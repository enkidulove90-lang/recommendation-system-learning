from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog import load_catalog_config, refresh_from_config
from paper_intake.catalog_store import CatalogRepository
from paper_intake.catalog_snapshot import export_discovery_snapshot, export_snapshot
from paper_intake.repository import JobRepository
from paper_intake.catalog_identity import source_version


DEFAULT_CONFIG = ROOT / "config" / "paper_catalog_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "paper_catalog" / "papers.json"
DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_WATCH_INTERVAL_SECONDS = 1800


def _diagnostic_event(event: dict) -> None:
    destination = os.getenv("PAPER_CATALOG_DIAGNOSTIC_LOG", "").strip()
    if not destination:
        return
    try:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **event}, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except OSError:
        pass  # Diagnostics must not change refresh success or failure.


def refresh_once(
    *, config_path: Path, output_path: Path, db_path: Path = DEFAULT_DB,
    interval_seconds: int | None = None, bootstrap: bool = False, dry_run: bool = False,
    auto_enqueue: bool = False,
) -> int:
    config = load_catalog_config(config_path)
    interval = int(interval_seconds or DEFAULT_WATCH_INTERVAL_SECONDS)
    _diagnostic_event({"event": "refresh_start"})
    catalog = refresh_from_config(config, cache_dir=output_path.parent / "cache",
                                  on_source_event=_diagnostic_event if os.getenv("PAPER_CATALOG_DIAGNOSTIC_LOG") else None)
    _diagnostic_event({"event": "refresh_end", "candidates": len(catalog.raw_records)})
    if dry_run:
        print(json.dumps({"status": "dry_run", "candidate_count": len(catalog.papers), "auto_delivery": False}, ensure_ascii=False))
        return interval
    if not catalog.papers:
        raise RuntimeError("all catalog sources returned zero papers; previous catalog was preserved")
    # Search-pool snapshot is written from memory *before* any SQLite work.
    # A slow/failed upsert can no longer leave papers.json stale.
    discovery = export_discovery_snapshot(catalog, output_path, watch_interval_seconds=interval)
    _diagnostic_event({"event": "discovery_snapshot_written", "paper_count": discovery["paper_count"]})
    intake_schema = JobRepository(db_path)
    intake_schema.close()
    repository = CatalogRepository(db_path)
    try:
        repository.record_source_runs(catalog.source_runs)
        _diagnostic_event({"event": "source_runs_written", "count": len(catalog.source_runs)})
        existing = {
            row["canonical_id"]: (row["status"], row["source_version"])
            for row in repository._connection.execute("SELECT canonical_id, status, source_version FROM papers")
        }
        versions: dict[str, dict[tuple[str, str], str]] = {}
        # Explicit BEGIN is required: sqlite3's `with con:` does not open a
        # transaction until the first DML, so upsert_candidate's
        # `in_transaction` check reads False on every row and commits it
        # (301 Connection.__exit__ calls for 300 rows = 89% of runtime).
        # BEGIN IMMEDIATE keeps in_transaction=True for the whole loop, so
        # upsert_candidate uses nullcontext and no per-row commit happens.
        # Any failure rolls the entire batch back; no partial rows survive.
        repository._connection.execute("BEGIN IMMEDIATE")
        try:
            for index, paper in enumerate(catalog.raw_records, 1):
                canonical_id = repository.upsert_candidate(paper)
                versions.setdefault(canonical_id, {})[(paper.source, paper.source_id)] = source_version(paper)
                if index % 500 == 0:
                    _diagnostic_event({"event": "upsert_progress", "count": index})
        except Exception:
            repository._connection.rollback()
            raise
        else:
            repository._connection.commit()
        _diagnostic_event({"event": "upsert_end", "count": len(catalog.raw_records)})
        candidates: set[str] = set()
        with repository._connection:
            for canonical_id, source_versions in versions.items():
                ordered = [source_versions[key] for key in sorted(source_versions)]
                revision = ordered[0] if len(ordered) == 1 else hashlib.sha256(
                    json.dumps(ordered, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                repository._connection.execute(
                    "UPDATE papers SET source_version=? WHERE canonical_id=?", (revision, canonical_id)
                )
                prior = existing.get(canonical_id)
                if prior is None or (prior[0] == "metadata_only" and revision != prior[1]):
                    candidates.add(canonical_id)
        queued = 0
        if auto_enqueue and config.get("auto_delivery_enabled") and not bootstrap and existing:
            for canonical_id in sorted(candidates):
                repository.queue_candidate(canonical_id)
                queued += 1
        snapshot = export_snapshot(repository, output_path, watch_interval_seconds=interval)
        summary = repository.reconcile()
    finally:
        repository.close()
    print(json.dumps({"status": "ok", "paper_count": snapshot["paper_count"], "output": str(output_path), "bootstrap": bootstrap, "auto_enqueued": queued, "reconciliation": summary}, ensure_ascii=False))
    return interval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh the authoritative paper discovery catalog.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--bootstrap", action="store_true", help="Index discoveries without creating intake jobs.")
    parser.add_argument("--dry-run", action="store_true", help="Show candidate count without writing files or SQLite.")
    parser.add_argument("--auto-enqueue", action="store_true", help="Queue only newly discovered papers when config also enables it.")
    parser.add_argument("--interval", type=int, default=None, help="Refresh interval in seconds (default: config or 1800).")
    parser.add_argument("--watch", action="store_true", help="Keep running and refresh at the configured interval.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    while True:
        try:
            interval = refresh_once(
                config_path=args.config,
                output_path=args.output,
                db_path=args.db,
                interval_seconds=args.interval,
                bootstrap=args.bootstrap,
                dry_run=args.dry_run,
                auto_enqueue=args.auto_enqueue,
            )
        except Exception as exc:
            print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
            if not args.watch:
                return 1
            interval = int(args.interval or DEFAULT_WATCH_INTERVAL_SECONDS)
        if not args.watch:
            return 0
        time.sleep(max(interval, 60))


if __name__ == "__main__":
    raise SystemExit(main())
