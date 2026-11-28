from __future__ import annotations

import json
from pathlib import Path

from paper_intake.repository import JobRepository
from scripts.backfill_catalog_links import backfill_links


def _seed(tmp: Path) -> Path:
    database = tmp / "catalog.sqlite3"
    from paper_intake.catalog_store import CatalogRepository
    CatalogRepository(database).close()
    repository = JobRepository(database)
    try:
        repository._connection.executescript(
            """INSERT INTO papers (canonical_id, status, title, normalized_title,
               publication_year, venue_type, venue_name, paper_url, doi, arxiv_id,
               authors_json, last_upstream_updated_at, source_version, created_at, updated_at)
               VALUES ('arxiv:2302.08191','discovered','A','a',2026,'preprint','arXiv','','', '2302.08191','[]','','v','','');"""
        )
        repository._connection.commit()
        for bare in ("arxiv:2302.08191", "arxiv:2402.01135"):
            job = repository.create_job(source_type="upload", upload_path=f"/tmp/{bare}.pdf")
            repository.update_job(job.job_id, canonical_id=bare)
    finally:
        repository.close()
    return database


def test_backfill_links_and_aliases(tmp_path: Path) -> None:
    database = _seed(tmp_path)
    report = tmp_path / "reconcile_report.json"
    report.write_text(json.dumps({"l2_hits": {"arxiv:2402.01135": "arxiv:2302.08191"}}), encoding="utf-8")

    dry = backfill_links(database=database, report_path=report)
    assert dry["apply"] is False and dry["planned_links"] == 2
    assert dry["projected_linked"] == 2

    applied = backfill_links(database=database, report_path=report, apply=True)
    assert applied["already_linked"] == 2

    import sqlite3
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute("SELECT old_canonical,new_canonical,strategy FROM id_alias").fetchall()
        assert len(rows) == 2
        assert any(row[2] == "title_l2" for row in rows)
        assert connection.execute(
            "SELECT count(*) FROM jobs WHERE catalog_canonical_id='arxiv:2302.08191'"
        ).fetchone()[0] == 2
    finally:
        connection.close()
