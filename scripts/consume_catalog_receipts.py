from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_events import consume_catalog_receipt
from paper_intake.catalog_store import CatalogRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consume terminal intake receipts into the local catalog.")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    repository = CatalogRepository(args.db)
    try:
        while True:
            job_id = consume_catalog_receipt(repository)
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
