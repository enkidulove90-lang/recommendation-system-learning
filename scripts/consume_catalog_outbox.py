from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_events import consume_next
from paper_intake.repository import JobRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consume catalog outbox into local paper-intake jobs.")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    repository = JobRepository(args.db)
    try:
        while True:
            if args.dry_run:
                row = repository._connection.execute(
                    """SELECT id, event_type FROM outbox WHERE target_domain='paper_intake'
                    AND consumed_at IS NULL AND dead_lettered_at IS NULL ORDER BY id LIMIT 1"""
                ).fetchone()
                print(json.dumps({"dry_run": True, "next_event_id": row["id"] if row else None}))
                return 0
            job_id = consume_next(repository)
            if job_id:
                print(json.dumps({"status": "consumed", "job_id": job_id}))
            if args.once:
                return 0
            if not job_id:
                time.sleep(1)
    finally:
        repository.close()


if __name__ == "__main__":
    raise SystemExit(main())
