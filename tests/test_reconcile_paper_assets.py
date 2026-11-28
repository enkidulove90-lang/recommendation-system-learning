from __future__ import annotations

import json
from pathlib import Path

from paper_intake.catalog_store import CatalogRepository
from scripts import reconcile_paper_assets


def test_build_report_is_read_only_and_reports_l1_l2(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    repository = CatalogRepository(database)
    try:
        repository._connection.execute(
            """INSERT INTO papers (canonical_id, status, title, normalized_title,
               publication_year, venue_type, venue_name, paper_url, doi, arxiv_id,
               authors_json, last_upstream_updated_at, source_version, created_at, updated_at)
               VALUES (?, 'discovered', ?, ?, 2026, 'preprint', 'arXiv', ?, '', ?, '[]', '', 'v1', '', '')""",
            ("arxiv:2302.08191", "Older paper", "older paper", "https://arxiv.org/abs/2302.08191", "2302.08191"),
        )
        repository._connection.commit()
    finally:
        repository.close()

    papers = tmp_path / "papers"
    papers.mkdir()
    (papers / "2302.08191.pdf").write_bytes(b"%PDF")
    parsed = tmp_path / "parsed"
    parsed.mkdir()
    (parsed / "2402.01135").mkdir()

    before = database.read_bytes()
    report = reconcile_paper_assets.build_report(
        database=database, papers_dir=papers, parsed_dir=parsed,
    )
    assert database.read_bytes() == before
    assert report["l1_hits"]["2302.08191"] == "arxiv:2302.08191"
    assert "2402.01135" in [item["asset"] for item in report["unmatched"]]
