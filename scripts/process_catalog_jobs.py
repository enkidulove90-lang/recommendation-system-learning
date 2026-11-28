from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_worker import process_next
from paper_intake.catalog_store import CatalogRepository
from paper_intake.catalog import load_catalog_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Qualify locally queued catalog papers; does not publish articles.")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--weekly-quota", type=int, default=300)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "paper_catalog_sources.json")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    config = load_catalog_config(args.config)
    repository = CatalogRepository(args.db)
    try:
        while True:
            result = process_next(
                repository, weekly_quota=int(config.get("weekly_total_quota", args.weekly_quota)),
                weekly_domain_quotas=config.get("weekly_domain_quotas"),
            )
            if result:
                print(json.dumps({"status": result}))
            if args.once:
                return 0
            if result is None:
                time.sleep(1)
    finally:
        repository.close()


if __name__ == "__main__":
    raise SystemExit(main())
