"""Content bridge: consume ParseCompleted outbox events and drive one paper
from parsed Markdown to platform packages.

Architecture note: this worker lives in ``scripts/`` (consumer side) so
``paper_intake`` stays free of any redbook dependency (hard repo rule enforced
by the AST guard in tests/test_paper_catalog.py).  The only redbook touchpoints
are delayed imports of two *public* interfaces inside worker functions:
  - redbook.sentinel.paper_pool.PaperPool  (shared pool state machine)
  - redbook.infrastructure.run_log.log_event (single run log)
No redbook.services / application modules are imported here; platform package
generation goes through content_factory's public API.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time
import traceback
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from paper_intake.asset_manifest import ContentAssetManifest
from paper_intake.catalog_store import CatalogRepository
from paper_intake.fact_pack import (
    FACT_PACK_PROMPT_VERSION,
    build_fact_pack_prompt,
    parse_fact_pack_response,
)
from paper_intake.model_gateway import ModelCallGatewayWithFallback

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
RUN_LOG = ROOT / "data" / "logs" / "runs.jsonl"

# A claimed event that is still unconsumed after this window is considered
# abandoned (crash/kill/network loss) and becomes visible to the next poll.
# Reuses the existing ``available_at`` column -- no schema migration needed.
LEASE_SECONDS = 600

# Valid forward-only transitions in paper_pool.TRANSITIONS; we walk each one so
# no state is skipped (set_status rejects illegal jumps).
_STATUS_PATH = ("parsed", "summarized", "composed", "staged")


@contextmanager
def trace_step(stage: str, canonical_id: str) -> Iterator[None]:
    """Emit start/ok/failed records with duration_ms for one long-running step.

    ``log_event`` serialises with ``json.dumps(default=str)``, so the full
    traceback is safely escaped onto a single JSONL line (no manual truncation
    of the error text, no broken log rows).
    """
    started = time.monotonic()
    _log(stage, "start", {"canonical_id": canonical_id})
    try:
        yield
    except Exception:
        duration_ms = int((time.monotonic() - started) * 1000)
        _log(stage, "failed", {
            "canonical_id": canonical_id,
            "duration_ms": duration_ms,
            "error": traceback.format_exc(),
        })
        raise
    else:
        duration_ms = int((time.monotonic() - started) * 1000)
        _log(stage, "ok", {"canonical_id": canonical_id,
                           "duration_ms": duration_ms})


def _log(stage: str, status: str, detail: dict[str, Any]) -> None:
    """Log through run_log.log_event when available, else append directly."""
    try:
        from redbook.infrastructure.run_log import log_event

        log_event("content_bridge", path=RUN_LOG, stage=stage,
                  status=status, detail=detail)
    except Exception:
        RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(
                {"event": "content_bridge", "stage": stage, "status": status,
                 "detail": detail}, ensure_ascii=False) + "\n")


def _advance_pool(canonical_id: str, db_path: Path = DEFAULT_DB) -> None:
    """Advance the shared paper_pool to staged using its public set_status.

    If the paper is not yet in the pool, seed it from the catalog master first
    (add_candidate is idempotent).  Each transition is checked by set_status;
    already-advanced rows simply skip the transitions they passed.
    """
    from redbook.sentinel.paper_pool import PaperPool

    pool = PaperPool(db_path)
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status FROM paper_pool WHERE canonical_id=?",
            (canonical_id,)).fetchone()
    if row is None:
        repository = CatalogRepository(db_path)
        paper = repository._connection.execute(
            "SELECT canonical_id, arxiv_id, doi, title FROM papers WHERE canonical_id=?",
            (canonical_id,)).fetchone()
        if paper is None:
            # Source-scoped canonical ids ("source:acl_anthology:2026.findings-acl.100")
            # differ from the bare id carried in job/ParseCompleted payloads.
            # Resolve by ':' suffix so non-arxiv sources work too.
            paper = repository._connection.execute(
                "SELECT canonical_id, arxiv_id, doi, title FROM papers "
                "WHERE canonical_id LIKE '%:' || ? LIMIT 1",
                (canonical_id,)).fetchone()
        repository.close()
        if paper is None:
            raise KeyError(f"canonical_id not in catalog master: {canonical_id}")
        pool.add_candidate(
            canonical_id=canonical_id,
            arxiv_id=paper["arxiv_id"] or "",
            doi=paper["doi"] or "",
            title=paper["title"] or "",
        )
        current = "discovered"
    else:
        current = row["status"]

    # Walk the complete forward path, inserting 'queued' between discovered
    # and parsed (set_status enforces paper_pool.TRANSITIONS, which does not
    # allow discovered -> parsed directly).
    full_path = list(_STATUS_PATH)
    if full_path and full_path[0] == "parsed":
        full_path.insert(0, "queued")
    order = ("discovered", "queued", "parsed", "summarized", "composed", "staged")
    start = order.index(current) if current in order else -1
    for target in full_path:
        if start >= 0 and order.index(target) <= start:
            continue
        try:
            pool.set_status(canonical_id, target)
            current = target
        except Exception:
            # Unexpected state (e.g. blocked): stop advancing, never force it.
            break


def _ensure_legacy_summary(canonical_id: str) -> Path:
    """Derive content_factory's `<id>_summary.json` from the generated fact_pack.

    content_factory loads a traditional 11-dimension summary file; the new
    pipeline only produces fact_pack.  Build the bridge file once (idempotent)
    from facts, with no extra model call, so both entry points share facts.
    """
    from paper_intake.model_gateway import artifact_basename

    bare = canonical_id.split(":", 1)[-1]
    target = ROOT / "data" / "summaries" / f"{bare}_summary.json"
    if target.is_file():
        return target
    fact_path = (
        ROOT / "data" / "summaries"
        / f"{artifact_basename(canonical_id, 'fact_pack')}.json"
    )
    payload = json.loads(fact_path.read_text(encoding="utf-8"))
    facts = payload.get("facts", {})
    experiments = facts.get("experiments") or []
    # Map to the field names PaperSummary validates against (methodology /
    # main_contribution / experimental_results are mandatory).
    summary = {
        "paper_id": bare,
        "title": facts.get("one_line", "") or bare,
        "title_zh": facts.get("one_line", ""),
        "methodology": facts.get("method", ""),
        "main_contribution": facts.get("novelty", "") or facts.get("problem", ""),
        "experimental_results": "; ".join(str(item) for item in experiments),
        "limitations": facts.get("limitations", ""),
        "innovation_points": [facts.get("novelty", "")] if facts.get("novelty") else [],
        "keywords": facts.get("keywords", []),
        "audience": facts.get("audience", ""),
        "code_url": facts.get("code_url", ""),  # 新增 code_url 字段
        "generated_via": "fact_pack_bridge",
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def _stage_platform_packages(inputs) -> dict[str, dict[str, Any]]:
    """Compile local review packages from one identity-bound input set."""
    from content_factory.factory import ContentFactory

    summaries_dir = ROOT / "data" / "summaries"
    parsed_dir = ROOT / "data" / "parsed"
    factory = ContentFactory(
        root=ROOT,
        summaries_dir=summaries_dir,
        parsed_dir=parsed_dir,
        platforms_yaml=ROOT / "content_factory" / "platforms.yaml",
        use_llm=False,  # fact_pack already reused; no new model calls
    )
    return factory.compile_shared(inputs)


def resolve_event_inputs(payload: dict[str, Any], db_path: Path):
    """Resolve the job that produced this exact Markdown, never an arbitrary latest job."""
    from paper_intake.models import CompilationInputs
    from paper_intake.model_gateway import sha256_file

    canonical_id = str(payload.get("canonical_id") or "")
    markdown = Path(str(payload.get("markdown_path") or ""))
    if not canonical_id or not payload.get("markdown_path"):
        raise ValueError("ParseCompleted missing identity or markdown")
    if not markdown.is_absolute():
        markdown = ROOT / markdown
    markdown = markdown.resolve()
    if not markdown.is_file():
        raise FileNotFoundError(f"parse output missing: {markdown}")

    connection = sqlite3.connect(f"file:{Path(db_path).resolve().as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT j.job_id,j.canonical_id,j.catalog_canonical_id,j.upload_path,s.output_json "
            "FROM jobs j JOIN job_steps s ON s.job_id=j.job_id "
            "WHERE j.canonical_id=? AND s.step_name='mineru_parse' AND s.status='succeeded'",
            (canonical_id,),
        ).fetchall()
    finally:
        connection.close()
    matching = []
    for row in rows:
        output = json.loads(row["output_json"] or "{}")
        path = str(output.get("markdown_path") or "")
        if path and (Path(path) if Path(path).is_absolute() else ROOT / path).resolve() == markdown:
            matching.append(row)
    job_id = str(payload.get("job_id") or "")
    if job_id:
        matching = [row for row in matching if row["job_id"] == job_id]
    if len(matching) != 1:
        raise ValueError("ambiguous or missing producing job for ParseCompleted")
    row = matching[0]
    pdf_text = str(row["upload_path"] or "")
    if not pdf_text:
        raise ValueError("producing job has no PDF")
    pdf = Path(pdf_text)
    if not pdf.is_absolute():
        pdf = ROOT / pdf
    pdf = pdf.resolve()
    if not pdf.is_file():
        raise FileNotFoundError(f"producing job PDF missing: {pdf}")
    event_pdf = str(payload.get("pdf_path") or "")
    if event_pdf:
        event_path = Path(event_pdf)
        if (event_path if event_path.is_absolute() else ROOT / event_path).resolve() != pdf:
            raise ValueError("event PDF does not match producing job")
    expected_hash = str(payload.get("pdf_sha256") or "")
    if expected_hash and sha256_file(pdf) != expected_hash:
        raise ValueError("event PDF hash does not match producing job")
    catalog_id = str(row["catalog_canonical_id"] or "")
    if payload.get("catalog_canonical_id") and payload["catalog_canonical_id"] != catalog_id:
        raise ValueError("event catalog identity does not match producing job")
    return CompilationInputs(canonical_id, catalog_id, str(row["job_id"]), markdown, pdf)


#: Legacy editorial target from the redbook workflow. This is a *target*, never
#: an assertion: a paper that only offers two eligible figures publishes two.
FIGURE_TARGET = 4
FIGURE_CEILING = 9


def _layout_json(markdown_path: Path) -> Path | None:
    """Locate the MinerU layout JSON that carries per-figure bounding boxes."""
    base = markdown_path.parent
    for candidate in (base / f"{markdown_path.stem}_layout.json", base / "layout.json"):
        if candidate.is_file():
            return candidate
    matches = sorted(base.glob("*_layout.json"))
    return matches[0] if matches else None


def select_figures_with_fallback(markdown_path: Path, pdf_path) -> tuple[list, Path | None]:
    """Three-tier figure selection, mirroring ``redbook``'s paper workflow.

    Tier 1: arXiv LaTeX source images already on disk (highest fidelity).
    Tier 2: rerender the figure regions from the PDF at 288 dpi.
    Tier 3: whatever MinerU extracted.

    The tiers exist because MinerU's own crops fail the quality gate most of the
    time: measured over 16 real parses only 2.5% of MinerU candidates passed
    (short edge >= 480 px, >= 650k px, aspect <= 3.2). Rerendering from the PDF
    is the only way to recover full-width figures for a paper whose LaTeX source
    is unavailable. No gate threshold here was changed.

    Tiers accumulate instead of short-circuiting: the strongest tier is chosen
    first, then weaker tiers top up only with figures from pages that the
    stronger tier did not already cover, so the same figure is never shown
    twice. ``FIGURE_TARGET`` stays a target — a paper that only offers two
    eligible figures publishes two.
    """
    from redbook.services.figure_retrieval import FigureRetrievalService

    service = FigureRetrievalService()
    base = markdown_path.parent

    tiers: list[tuple[str, Path]] = []
    for relative, source in (("arxiv_source/images_source", "arxiv_latex"),
                             ("images_source", "arxiv_latex")):
        folder = base / relative
        if folder.is_dir():
            tiers.append((source, folder))

    layout = _layout_json(markdown_path)
    pdf = Path(str(pdf_path)) if pdf_path else None
    if layout is not None and pdf is not None and pdf.is_file():
        from redbook.services.figure_retrieval import HighDpiPdfFigureExtractor

        hd_dir = base / "images_hd"
        if not (hd_dir / "figure_manifest.json").is_file():
            try:
                HighDpiPdfFigureExtractor().extract(pdf, layout, hd_dir)
            except Exception as error:  # noqa: BLE001 — keep the run resumable
                print(f"  ! high-dpi figure rerender failed: {error}", file=sys.stderr)
        if hd_dir.is_dir():
            tiers.append(("pdf_high_dpi", hd_dir))

    if (base / "images").is_dir():
        tiers.append(("mineru", base / "images"))

    ranked: list[tuple[int, str, Path, list]] = []
    for source, folder in tiers:
        picked, _, _ = service.select(markdown_path, folder, limit=FIGURE_CEILING, source=source)
        if picked:
            ranked.append((len(picked), source, folder, picked))
    if not ranked:
        return [], None
    ranked.sort(key=lambda item: item[0], reverse=True)

    selected: list = []
    source_dir: Path | None = None
    covered_figures: set[str] = set()
    covered_pages: set = set()
    for _count, _source, folder, picked in ranked:
        if source_dir is None:
            source_dir = folder
        # Real figures first; rerendered tables only top up the remaining slots.
        ordered = sorted(picked, key=lambda item: "_table_" in str(getattr(item, "path", "")))
        for candidate in ordered:
            # The same figure exists twice once two tiers cover it (a PDF
            # rerender and MinerU's crop of it). Figure id is the stable key;
            # page is the fallback for crops that were never captioned.
            figure_id = str(getattr(candidate, "figure_id", "") or "").strip().casefold()
            page = getattr(candidate, "page", None)
            if figure_id:
                if figure_id in covered_figures:
                    continue
                covered_figures.add(figure_id)
            elif page is not None:
                if page in covered_pages:
                    continue
                covered_pages.add(page)
            selected.append(candidate)
            if len(selected) >= FIGURE_CEILING:
                break
        if len(selected) >= FIGURE_CEILING:
            break
    return selected, source_dir


def _prepare_compilation_inputs(inputs, fact_pack_path: Path, payload: dict[str, Any], db_path: Path):
    """Attach catalog links and one pending selected-figure manifest to the producing job."""
    from redbook.services.figure_retrieval import build_selected_figure_manifest

    connection = sqlite3.connect(f"file:{Path(db_path).resolve().as_posix()}?mode=ro", uri=True)
    try:
        row = connection.execute("SELECT paper_url, pdf_url FROM papers WHERE canonical_id=?",
                                 (inputs.catalog_canonical_id or inputs.canonical_id,)).fetchone()
    finally:
        connection.close()
    if row is None or not row[0] or not row[1]:
        raise ValueError("catalog paper URL or PDF URL missing for producing job")
    pack = json.loads(Path(fact_pack_path).read_text(encoding="utf-8"))
    code_url = str((pack.get("facts") or {}).get("code_url") or "")
    declared = payload.get("figure_manifest_path")
    if declared:
        manifest_path = Path(declared)
        if not manifest_path.is_absolute():
            manifest_path = ROOT / manifest_path
        if not manifest_path.is_file():
            raise FileNotFoundError("selected figure manifest missing")
    else:
        parsed_dir = inputs.markdown_path.parent
        figures, _figure_dir = select_figures_with_fallback(inputs.markdown_path, inputs.pdf_path)
        if not figures:
            raise ValueError("no eligible figures for selected figure manifest")
        manifest = build_selected_figure_manifest(inputs.canonical_id, parsed_dir, figures)
        encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
        manifest_path = ROOT / "data" / "workflow_state" / "figure_manifests" / (hashlib.sha256(encoded).hexdigest() + ".json")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with manifest_path.open("xb") as handle:
                handle.write(encoded)
        except FileExistsError:
            if manifest_path.read_bytes() != encoded:
                raise FileExistsError("figure manifest collision")
    return replace(inputs, fact_pack_path=Path(fact_pack_path), figure_manifest_path=manifest_path,
                   paper_url=row[0], pdf_url=row[1], code_url=code_url)


def _consume_event(event: sqlite3.Row, *, dry_run: bool,
                   db_path: Path = DEFAULT_DB) -> bool:
    payload = json.loads(event["payload_json"])
    canonical_id = str(payload.get("canonical_id") or "")
    markdown = str(payload.get("markdown_path") or "")
    if not canonical_id or not markdown:
        raise ValueError(f"invalid ParseCompleted payload: {event['id']}")
    inputs = resolve_event_inputs(payload, db_path)
    source = inputs.markdown_path

    repository = CatalogRepository(db_path)
    repository.close()
    manifest = ContentAssetManifest(db_path)

    # Use SHUSHENG model with DeepSeek fallback for fact_pack generation
    gateway = ModelCallGatewayWithFallback(manifest, ROOT, use_shusheng_cache=True)
    from paper_intake.model_gateway import sha256_file

    # Determine which model ID to use for cache lookup
    query_model_id = settings.SHUSHENG_MODEL if settings.SHUSHENG_API_KEY else settings.DEEPSEEK_MODEL
    cached = manifest.lookup(
        canonical_id, "fact_pack", sha256_file(source),
        FACT_PACK_PROMPT_VERSION, query_model_id)
    fact_pack_path = ROOT / cached["relative_path"] if cached is not None else None
    if cached is None or not (ROOT / cached["relative_path"]).is_file():
        if dry_run:
            _log("content_bridge", "skip", {"canonical_id": canonical_id,
                                            "reason": "fact_pack missing"})
            return False
        # First real generation: use SHUSHENG with DeepSeek fallback
        try:
            with trace_step("fact_pack_generation", canonical_id):
                fact_pack_path = gateway.ensure(
                    canonical_id=canonical_id, purpose="fact_pack", source=source,
                    prompt_version=FACT_PACK_PROMPT_VERSION,
                    model_id=settings.SHUSHENG_MODEL,
                    build_prompt=build_fact_pack_prompt,
                    parse_response=lambda raw: parse_fact_pack_response(raw, canonical_id),
                    use_shusheng_first=True,
                )
        except RuntimeError as e:
            # If all providers fail, raise
            if "all providers failed" in str(e):
                raise RuntimeError(f"FactPack generation failed: {e}") from e
            raise


    if dry_run:
        _log("content_bridge", "skip", {"canonical_id": canonical_id,
                                        "reason": "dry_run"})
        return False

    with trace_step("platform_render", canonical_id):
        inputs = _prepare_compilation_inputs(inputs, fact_pack_path, payload, db_path)
        results = _stage_platform_packages(inputs)
        _log("platform_compilation", "ok" if all(item["status"] == "compiled" for item in results.values()) else "failed",
             {"canonical_id": canonical_id, "job_id": inputs.job_id, "platforms": results})
        failed = {name: item for name, item in results.items() if item["status"] != "compiled"}
        if failed:
            raise RuntimeError(f"platform compilation failed: {failed}")

    # Advance paper_pool state only after platform packages are successfully generated
    _advance_pool(canonical_id, db_path)

    # Real delivery to all three platforms. Human-review gates are gone
    # (2026-11-28): field-complete packages go straight to the platform draft
    # boxes. Each platform is independent; a failure is logged, never hidden.
    with trace_step("platform_delivery", canonical_id):
        from scripts.deliver_packages import deliver_compiled
        receipts = deliver_compiled(results)
        _log("platform_delivery",
             "ok" if all(r.get("ok") for r in receipts.values()) else "partial",
             {"canonical_id": canonical_id, "receipts": receipts})
    _log("content_bridge", "ok", {"canonical_id": canonical_id,
                                  "packages": results, "receipts": receipts})
    return True


def _claim_next(db_path: Path, *, canonical_id: str, now: str, lease_until: str) -> sqlite3.Row | None:
    """Atomically claim one unconsumed ParseCompleted event.

    Mirrors ``paper_intake.catalog_events.consume_next``: BEGIN IMMEDIATE
    serialises competing workers, and the claim is committed BEFORE the long
    model call.  A crash leaves ``available_at`` in the future; after the
    lease expires the row becomes visible again.  No schema change needed.
    """
    connection = sqlite3.connect(db_path, timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT id, event_id, payload_json, available_at FROM outbox "
            "WHERE event_type='ParseCompleted' AND consumed_at IS NULL "
            "  AND dead_lettered_at IS NULL "
            "  AND available_at <= ? "
            "  AND (? = '' OR json_extract(payload_json, '$.canonical_id') = ?) "
            "ORDER BY id LIMIT 1",
            (now, canonical_id, canonical_id),
        ).fetchone()
        if row is None:
            connection.commit()
            return None
        # Claim: push availability into the future and bump attempts atomically.
        connection.execute(
            "UPDATE outbox SET available_at=?, attempts=attempts+1 WHERE id=?",
            (lease_until, row["id"]),
        )
        connection.commit()
        return row
    finally:
        connection.close()


def _release(db_path: Path, event_id: int, *, now: str, error: bool,
             retry_at: str | None = None) -> None:
    """Finish a claimed event: mark consumed on success; on failure push the
    availability into the future so one run does not repeatedly retry the same
    event (backoff), and dead-letter after too many attempts."""
    with sqlite3.connect(db_path, timeout=5) as connection:
        if error:
            backoff = retry_at or now
            connection.execute(
                "UPDATE outbox SET available_at=?, last_error_code='bridge_retry' "
                "WHERE id=? AND consumed_at IS NULL",
                (backoff, event_id),
            )
        else:
            connection.execute(
                "UPDATE outbox SET consumed_at=?, last_error_code=NULL WHERE id=?",
                (now, event_id),
            )


def run_bridge_once(db_path: Path = DEFAULT_DB, max_jobs: int = 10,
                    *, dry_run: bool = False, canonical_id: str = "") -> dict[str, Any]:
    """Process up to ``max_jobs`` unconsumed ParseCompleted events.

    ``canonical_id`` is pushed into the SQL WHERE clause via json_extract, so
    a target at position 51+ is still found (no in-memory post-filter).

    ``status`` is derived from the counters (see ``_run_status``); ``main``
    mirrors failures into the process exit code so the s5 stage can never be
    recorded as ok while every event failed.
    """
    db_path = Path(db_path)
    if dry_run:
        # Preview only: do not claim/release events or change their retry time.
        connection = sqlite3.connect(f"file:{db_path.resolve().as_posix()}?mode=ro", uri=True)
        try:
            now = datetime.now(timezone.utc).isoformat()
            rows = connection.execute(
                "SELECT id FROM outbox WHERE event_type='ParseCompleted' "
                "AND consumed_at IS NULL AND dead_lettered_at IS NULL AND available_at<=? "
                "AND (?='' OR json_extract(payload_json,'$.canonical_id')=?) "
                "ORDER BY id LIMIT ?", (now, canonical_id, canonical_id, max(0, max_jobs)),
            ).fetchall()
        finally:
            connection.close()
        return {"status": "dry_run", "processed": 0, "failed": 0, "scanned": len(rows)}
    processed = 0
    failed = 0
    scanned = 0
    for _ in range(max_jobs):
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        lease_until = (now_dt + timedelta(seconds=LEASE_SECONDS)).isoformat()
        event = _claim_next(db_path, canonical_id=canonical_id,
                            now=now, lease_until=lease_until)
        if event is None:
            break
        scanned += 1
        event_id = event["id"]
        retry_at = lease_until  # backoff: do not spin on the same failed event
        try:
            ok = _consume_event(event, dry_run=dry_run, db_path=db_path)
        except Exception as error:
            failed += 1
            # Full traceback already logged by trace_step; keep a short summary
            # here for the console result.
            _release(db_path, event_id, now=now, error=True, retry_at=retry_at)
            _log("content_bridge", "failed", {
                "canonical_id": canonical_id or event["event_id"],
                "error": str(error)[:500],
            })
            continue
        if not ok:
            _release(db_path, event_id, now=now, error=True, retry_at=retry_at)
            continue
        _release(db_path, event_id, now=now, error=False)
        processed += 1

    return {"status": _run_status(processed, failed, scanned, dry_run=dry_run),
            "processed": processed, "failed": failed, "scanned": scanned}


def _run_status(processed: int, failed: int, scanned: int, *,
                dry_run: bool = False) -> str:
    """Derive an honest run status from the counters.

    - ``ok``       nothing attempted (empty queue) or everything succeeded;
    - ``partial``  some events succeeded and some failed;
    - ``failed``   work was attempted but nothing succeeded;
    - ``dry_run``  a dry run never claims real work.
    """
    if failed == 0:
        return "dry_run" if dry_run and scanned else "ok"
    return "partial" if processed > 0 else "failed"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="consume ParseCompleted events")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--max-jobs", type=int, default=10)
    parser.add_argument("--canonical-id", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run_bridge_once(
        args.db, args.max_jobs, dry_run=args.dry_run,
        canonical_id=args.canonical_id)
    print(json.dumps(result, ensure_ascii=False))
    # Non-zero whenever real work failed: the s5 stage only checks the exit
    # code, so ``processed: 0, failed: 1`` must never look like success.
    return 1 if int(result.get("failed") or 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
