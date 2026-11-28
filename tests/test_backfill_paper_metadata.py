from __future__ import annotations

import json
from pathlib import Path

from paper_intake.catalog_store import CatalogRepository
from scripts.backfill_paper_metadata import backfill_metadata


def test_backfill_creates_missing_papers_and_is_idempotent(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    CatalogRepository(database).close()
    report = tmp_path / "reconcile_report.json"
    report.write_text(json.dumps({
        "unmatched": [
            {"asset": "2302.08191"},
            {"asset": "2026.acl-short.10"},
            {"asset": "3792192_MSCA"},
        ]
    }), encoding="utf-8")

    class FakeResolver:
        def __call__(self, canonical_id: str, source_url: str):
            return {
                "title": f"Paper {canonical_id}", "authors": ["A. Author"],
                "paper_url": f"https://arxiv.org/abs/{canonical_id}",
                "published": "2023-02-01T00:00:00Z", "updated": "2023-02-02T00:00:00Z",
                "primary_category": "cs.IR", "arxiv_id": canonical_id,
            }

    dry = backfill_metadata(database=database, report_path=report, resolver_factory=FakeResolver)
    assert dry["apply"] is False and dry["candidates"] == 1
    assert dry["created"] == ["arxiv:2302.08191"]

    applied = backfill_metadata(database=database, report_path=report, resolver_factory=FakeResolver, apply=True)
    assert applied["created"] == ["arxiv:2302.08191"]
    again = backfill_metadata(database=database, report_path=report, resolver_factory=FakeResolver, apply=True)
    assert again["created"] == [] and again["skipped"] == ["arxiv:2302.08191"]

    repository = CatalogRepository(database)
    try:
        row = repository._connection.execute(
            "SELECT title, arxiv_id FROM papers WHERE canonical_id='arxiv:2302.08191'"
        ).fetchone()
        assert row is not None and row["arxiv_id"] == "2302.08191"
    finally:
        repository.close()
