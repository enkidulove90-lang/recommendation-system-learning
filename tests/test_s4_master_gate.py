from __future__ import annotations

import json
from pathlib import Path

from paper_intake.catalog_store import CatalogRepository
from paper_intake.models import JobStatus
from paper_intake.repository import JobRepository
from scripts import daily_paper_ingest


def test_unmatched_job_is_blocked_not_silently_dropped(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    CatalogRepository(database).close()
    repository = JobRepository(database)
    job = repository.create_job(source_type="url", source_url="https://example.test/x.pdf")
    repository.update_job(job.job_id, canonical_id="9999.99999", title="Unknown")
    repository.close()

    result = daily_paper_ingest.consume_received_jobs(
        database=database,
        papers_dir=tmp_path / "papers",
        log_path=tmp_path / "runs.jsonl",
        pipeline_factory=lambda repo: None,
    )
    assert result["blocked"] == 1 and result["processed"] == 0

    repository = JobRepository(database)
    try:
        assert repository.get_job(job.job_id).status == JobStatus.BLOCKED
    finally:
        repository.close()

    rows = [json.loads(line) for line in (tmp_path / "runs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(row.get("status") == "blocked" and row.get("event") == "paper_ingest_stage" for row in rows)
