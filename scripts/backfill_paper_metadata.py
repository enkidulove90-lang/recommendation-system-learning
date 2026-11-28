"""Task 2: resolve metadata for L1 arXiv assets missing from the identity master.

Reads ``reconcile_report.json`` (or re-scans), calls ``ArxivMetadataResolver``
for each arXiv-shaped asset whose canonical id is absent from ``papers``, and
writes a ``PaperRecord`` via ``upsert_candidate``.  Idempotent on canonical id.
Default is dry-run; ``--apply`` performs writes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog import PaperRecord  # noqa: E402
from paper_intake.catalog_identity import canonical_id_from_bare  # noqa: E402
from paper_intake.catalog_store import CatalogRepository  # noqa: E402
from paper_intake.metadata import ArxivMetadataResolver  # noqa: E402

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_REPORT = ROOT / "data" / "paper_catalog" / "reconcile_report.json"


def _record_from_metadata(meta: dict[str, Any], bare: str) -> PaperRecord:
    year = str(meta.get("year") or meta.get("published", "")[:4] or "0")
    return PaperRecord(
        publication_year=int(year) if year.isdigit() and int(year) else 0,
        venue_type="preprint", venue_name=str(meta.get("venue_name") or "arXiv"),
        title=str(meta.get("title") or bare),
        paper_url=str(meta.get("paper_url") or f"https://arxiv.org/abs/{bare}"),
        source="arxiv", source_id=bare,
        topics=[meta["primary_category"]] if meta.get("primary_category") else [],
        topic_source="arxiv_category" if meta.get("primary_category") else "unavailable",
        authors=[str(a) for a in meta.get("authors", [])],
        published_at=str(meta.get("published") or ""),
        updated_at=str(meta.get("updated") or ""),
        doi=str(meta.get("doi") or ""), arxiv_id=bare,
        retrieved_at=str(meta.get("retrieved_at") or ""),
    )


def backfill_metadata(*, database: Path, report_path: Path = DEFAULT_REPORT,
                      resolver_factory: Callable[[], Any] = ArxivMetadataResolver,
                      apply: bool = False, max_items: int | None = None) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    candidates: dict[str, str] = {}
    for item in report.get("unmatched", []):
        bare = str(item.get("asset", ""))
        canonical = canonical_id_from_bare(bare)
        if canonical.startswith("arxiv:"):
            candidates[canonical] = bare
    if max_items is not None:
        candidates = dict(list(candidates.items())[:max_items])

    repository = CatalogRepository(database)
    resolver = resolver_factory() if candidates else None
    created: list[str] = []
    skipped: list[str] = []
    failed: list[dict[str, str]] = []
    try:
        existing = {row[0] for row in repository._connection.execute("SELECT canonical_id FROM papers")}
        for canonical, bare in sorted(candidates.items()):
            if canonical in existing:
                skipped.append(canonical)
                continue
            if not apply:
                created.append(canonical)
                continue
            try:
                meta = resolver(bare, "")
                record = _record_from_metadata(meta, bare)
                stored = repository.upsert_candidate(record)
                created.append(stored)
                existing.add(stored)
            except Exception as exc:
                failed.append({"canonical_id": canonical, "error": f"{type(exc).__name__}: {exc}"[:300]})
    finally:
        repository.close()
    return {"apply": apply, "candidates": len(candidates), "created": created,
            "skipped": skipped, "failed": failed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backfill missing identity-master rows from arXiv metadata.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--max", type=int, default=None)
    args = parser.parse_args(argv)
    result = backfill_metadata(database=args.database, report_path=args.report,
                               apply=args.apply, max_items=args.max)
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
