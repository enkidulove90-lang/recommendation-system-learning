"""One-off migration: prefix legacy bare canonical_ids in the unified index.

Backfilled local PDFs were registered with bare identifiers (``2302.08191``)
while the discovery catalog uses canonical prefixes (``arxiv:2302.08191``,
``source:acl_anthology:2026.acl-short.10``).  This script rewrites only bare
ids in place, is idempotent, and refuses to run unless ``--apply`` is given.

No PDF is moved, renamed or deleted.  A collision (two rows mapping to the
same canonical id) is reported and aborts the migration rather than being
silently merged.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_identity import canonical_id_from_bare

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"


def assert_unified_database(database: Path, *, expected_database: Path = DEFAULT_DB) -> Path:
    expected = expected_database.resolve()
    requested = Path(os.getenv("PAPER_INTAKE_DB_PATH", expected)).resolve()
    if requested != expected or database.resolve() != expected:
        raise RuntimeError(f"PAPER_INTAKE_DB_PATH must resolve to {expected}")
    return expected


def _bare_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT canonical_id FROM jobs WHERE canonical_id IS NOT NULL AND canonical_id != ''"
    ).fetchall()
    bare = []
    for row in rows:
        value = str(row["canonical_id"])
        if value.split(":", 1)[0] in {"arxiv", "doi", "source", "title"}:
            continue
        bare.append(value)
    return bare


def plan_migration(database: Path) -> dict[str, Any]:
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        bare = _bare_rows(connection)
        plan: dict[str, str] = {}
        unmapped: list[str] = []
        for value in bare:
            target = canonical_id_from_bare(value)
            if target:
                plan[value] = target
            else:
                unmapped.append(value)
        collisions = sorted({target for target in plan.values() if list(plan.values()).count(target) > 1})
        try:
            papers = {str(row[0]) for row in connection.execute("SELECT canonical_id FROM papers")}
        except sqlite3.OperationalError:
            papers = set()
        join_after = [target for target in plan.values() if target in papers]
        return {
            "bare_count": len(bare), "mapped": plan, "unmapped": unmapped,
            "collisions": collisions, "join_after_count": len(join_after),
        }
    finally:
        connection.close()


def apply_migration(database: Path, *, dry_run: bool = True,
                    expected_database: Path = DEFAULT_DB) -> dict[str, Any]:
    database = assert_unified_database(database, expected_database=expected_database)
    report = plan_migration(database)
    if dry_run or not report["mapped"]:
        return {**report, "applied": 0, "dry_run": dry_run}
    if report["collisions"]:
        raise RuntimeError(f"canonical id collision, migration aborted: {report['collisions']}")
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    changed = 0
    try:
        with connection:
            for bare, target in sorted(report["mapped"].items()):
                cursor = connection.execute(
                    "UPDATE jobs SET canonical_id=?, updated_at=datetime('now') WHERE canonical_id=?",
                    (target, bare),
                )
                changed += cursor.rowcount
    finally:
        connection.close()
    return {**report, "applied": changed, "dry_run": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy bare canonical ids to unified prefixed form.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--apply", action="store_true", help="Write changes (default is dry-run).")
    args = parser.parse_args(argv)
    try:
        report = apply_migration(args.db, dry_run=not args.apply)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
