"""Task 3: link intake jobs to the identity master and record id aliases.

Creates ``id_alias`` (idempotent DDL), then for each job resolves the target
canonical id by (1) job.canonical_id in papers, (2) L2 title match recorded in
``reconcile_report.json``, and writes ``jobs.catalog_canonical_id``.  Default
is dry-run; ``--apply`` performs writes.  No PDF is touched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_REPORT = ROOT / "data" / "paper_catalog" / "reconcile_report.json"

_DDL = """
CREATE TABLE IF NOT EXISTS id_alias (
  old_canonical TEXT PRIMARY KEY,
  new_canonical TEXT NOT NULL,
  strategy TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 1.0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def backfill_links(*, database: Path, report_path: Path = DEFAULT_REPORT,
                   apply: bool = False) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    l2 = report.get("l2_hits", {})
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            connection.executescript(_DDL) if apply else None
        master = {row[0] for row in connection.execute("SELECT canonical_id FROM papers")}
        jobs = [dict(row) for row in connection.execute(
            "SELECT job_id, canonical_id, catalog_canonical_id FROM jobs"
        )]
        plan: list[dict[str, str]] = []
        for job in jobs:
            current = job.get("catalog_canonical_id") or ""
            if current in master:
                continue
            bare = str(job.get("canonical_id") or "")
            target = ""
            strategy = ""
            if bare in master:
                target, strategy = bare, "exact"
            elif bare in l2 and l2[bare] in master:
                target, strategy = l2[bare], "title_l2"
            if target:
                plan.append({"job_id": job["job_id"], "old": bare,
                             "new": target, "strategy": strategy})
        if apply:
            with connection:
                for item in plan:
                    connection.execute(
                        "UPDATE jobs SET catalog_canonical_id=?, updated_at=datetime('now') WHERE job_id=?",
                        (item["new"], item["job_id"]),
                    )
                    connection.execute(
                        """INSERT INTO id_alias(old_canonical,new_canonical,strategy,confidence)
                           VALUES(?,?,?,?) ON CONFLICT(old_canonical) DO UPDATE SET
                           new_canonical=excluded.new_canonical, strategy=excluded.strategy""",
                        (item["old"], item["new"], item["strategy"],
                         1.0 if item["strategy"] == "exact" else 0.7),
                    )
        total = len(jobs) or 1
        linked = sum(1 for job in jobs if (job.get("catalog_canonical_id") or "") in master)
        if apply and plan:
            linked = sum(1 for row in connection.execute(
                "SELECT catalog_canonical_id FROM jobs"
            ) if (row[0] or "") in master)
        projected = linked + (0 if apply else len(plan))
        return {
            "apply": apply, "jobs": len(jobs), "master": len(master),
            "already_linked": linked, "planned_links": len(plan),
            "projected_linked": projected, "projected_rate": round(projected / total, 4),
            "aliases": plan,
        }
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Link intake jobs to the identity master.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    result = backfill_links(database=args.database, report_path=args.report, apply=args.apply)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
