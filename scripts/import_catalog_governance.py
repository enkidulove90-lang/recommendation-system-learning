"""Import a read-only discovery snapshot into the SQLite governance catalog.

The database path is explicit so runtime state is never hidden in a worktree.
This command never admits papers or creates delivery jobs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_governance import CatalogGovernance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import paper catalog into SQLite governance")
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args(argv)
    store = CatalogGovernance(args.db)
    added = store.import_snapshot(args.snapshot)
    with store._connect() as db:
        total = db.execute("SELECT COUNT(*) FROM catalog_papers").fetchone()[0]
        pending = db.execute("SELECT COUNT(*) FROM catalog_outbox WHERE consumed_at IS NULL").fetchone()[0]
    print(json.dumps({"added": added, "total": total, "pending_events": pending}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
