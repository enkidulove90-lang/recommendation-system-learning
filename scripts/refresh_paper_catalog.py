from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog import load_catalog_config, refresh_from_config
from paper_intake.catalog_store import CatalogRepository
from paper_intake.catalog_snapshot import export_snapshot
from paper_intake.repository import JobRepository
from paper_intake.catalog_identity import source_version


DEFAULT_CONFIG = ROOT / "config" / "paper_catalog_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "paper_catalog" / "papers.json"
DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_WATCH_INTERVAL_SECONDS = 1800


def refresh_once(
    *, config_path: Path, output_path: Path, db_path: Path = DEFAULT_DB,
    interval_seconds: int | None = None, bootstrap: bool = False, dry_run: bool = False,
    auto_enqueue: bool = False,
) -> int:
    config = load_catalog_config(config_path)
    interval = int(interval_seconds or DEFAULT_WATCH_INTERVAL_SECONDS)
    catalog = refresh_from_config(config, cache_dir=output_path.parent / "cache")
    if dry_run:
        print(json.dumps({"status": "dry_run", "candidate_count": len(catalog.papers), "auto_delivery": False}, ensure_ascii=False))
        return interval
    intake_schema = JobRepository(db_path)
    intake_schema.close()
    repository = CatalogRepository(db_path)
    try:
        repository.record_source_runs(catalog.source_runs)
        if not catalog.papers:
            raise RuntimeError("all catalog sources returned zero papers; previous catalog was preserved")
        existing = {
            row["canonical_id"]: (row["status"], row["source_version"])
            for row in repository._connection.execute("SELECT canonical_id, status, source_version FROM papers")
        }
        versions: dict[str, dict[tuple[str, str], str]] = {}
        for paper in catalog.raw_records:
            canonical_id = repository.upsert_candidate(paper)
            versions.setdefault(canonical_id, {})[(paper.source, paper.source_id)] = source_version(paper)
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
