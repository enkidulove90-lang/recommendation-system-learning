"""Import Paper Sentinel candidates into the paper_intake catalog.

The scheduled Sentinel task runs with `--no-dispatch`, so its discoveries only
land in its own state directory and never reach this repository.  This importer
bridges that gap: it reads ``discovery/<date>/candidates.jsonl``, upserts each
record into ``papers`` via the public CatalogRepository API, and queues eligible
papers for the normal s2 -> s3 -> s4 -> s5 chain.

Idempotent: re-running skips papers already present.

Usage::

    python scripts/import_sentinel_candidates.py \
        --state-dir "C:/Users/lkshpc/AppData/Local/PaperSentinel/state" \
        --date 2026-11-26
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog import PaperRecord
from paper_intake.catalog_store import CatalogRepository

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_STATE = Path.home() / "AppData" / "Local" / "PaperSentinel" / "state"


def _as_year(value: str) -> int:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) >= 4:
        try:
            return int(digits[:4])
        except ValueError:
            pass
    return date.today().year


def record_from_candidate(row: dict) -> PaperRecord | None:
    rid = str(row.get("record_id") or "")
    title = str(row.get("title") or "").strip()
    identifiers = row.get("identifiers") or {}
    arxiv_id = str(identifiers.get("arxiv") or (rid.split(":", 1)[1] if ":" in rid else ""))
    doi = str(identifiers.get("doi") or "")
    if not title or not (arxiv_id or doi):
        return None
    urls = row.get("urls") or {}
    source_query = ""
    source_records = row.get("source_records") or []
    if source_records and isinstance(source_records[0], dict):
        source_query = str(source_records[0].get("search_query") or "")
    source = "sentinel_arxiv" if arxiv_id else "sentinel_doi"
    source_id = arxiv_id or doi
    venue = row.get("venue") or {}
    authors = [str(a.get("name") or "") for a in (row.get("authors") or []) if isinstance(a, dict)]
    return PaperRecord(
        publication_year=_as_year(venue.get("year") or row.get("published_at") or ""),
        venue_type=str(venue.get("status") or "preprint"),
        venue_name=str(venue.get("name") or ""),
        title=title,
        paper_url=str(urls.get("landing") or (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else f"https://doi.org/{doi}")),
        source=source,
        source_id=source_id,
        topics=[str(t) for t in (row.get("topics") or [])],
        authors=[a for a in authors if a],
        published_at=str(row.get("published_at") or ""),
        doi=doi,
        arxiv_id=arxiv_id,
    )


def import_for_date(state_dir: Path, target_date: str, *, db_path: Path = DEFAULT_DB) -> dict:
    candidates_path = (
        Path(state_dir) / "discovery" / target_date / "candidates.jsonl")
    if not candidates_path.is_file():
        return {"ok": False, "error": f"not found: {candidates_path}"}

    repository = CatalogRepository(db_path)
    seen = 0
    upserted = 0
    queued = 0
    skipped = 0
    try:
        for line in candidates_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            seen += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            record = record_from_candidate(row)
            if record is None:
                skipped += 1
                continue
            canonical_id = repository.upsert_candidate(record, discovery_query="")
            upserted += 1
            # queue_candidate is itself idempotent (ON CONFLICT DO NOTHING), but
            # it returns the existing job_id on a repeat call.  Count only the
            # first queue so the report reflects real new work.
            already = repository._connection.execute(
                "SELECT 1 FROM catalog_jobs WHERE canonical_id=? LIMIT 1",
                (canonical_id,)).fetchone()
            if already is not None:
                continue
            try:
                repository.queue_candidate(canonical_id)
                queued += 1
            except (ValueError, KeyError):
                pass  # identity_conflict / published_to_catalog are not eligible
    finally:
        repository.close()
    return {
        "ok": True,
        "source": str(candidates_path),
        "seen": seen,
        "upserted": upserted,
        "queued": queued,
        "skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="import Sentinel candidates into paper_intake")
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    result = import_for_date(args.state_dir, args.date, db_path=args.db)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
