from __future__ import annotations

import hashlib
from pathlib import Path


def test_backfill_registers_each_pdf_once_and_records_download_step(tmp_path: Path) -> None:
    from scripts.backfill_paper_index import backfill
    from paper_intake.repository import JobRepository
    from paper_intake.models import StepName, StepStatus

    papers = tmp_path / "papers"
    papers.mkdir()
    pdf = papers / "2611.17921_RecMem.pdf"
    pdf.write_bytes(b"%PDF-test")
    (papers / "2611.17921_duplicate.pdf").write_bytes(b"%PDF-test")
    database = tmp_path / "catalog.sqlite3"

    options = {"expected_database": database}
    canonical = "arxiv:2611.17921"
    assert backfill(papers, database, dry_run=True, **options)["created"] == [canonical]
    assert backfill(papers, database, dry_run=False, **options)["created"] == [canonical]
    assert backfill(papers, database, dry_run=False, **options)["created"] == []

    repository = JobRepository(database)
    try:
        job = repository.find_duplicate(canonical_id=canonical)
        assert job is not None
        assert job.source_sha256 == hashlib.sha256(pdf.read_bytes()).hexdigest()
        assert repository.get_step(job.job_id, StepName.DOWNLOAD_PDF).status == StepStatus.SUCCEEDED
    finally:
        repository.close()
