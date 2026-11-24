from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from paper_intake.models import JobStatus, StepName, StepStatus
from paper_intake.repository import JobRepository
from scripts import consume_catalog_outbox
from scripts import daily_paper_ingest


ROOT = Path(__file__).resolve().parents[1]


def test_dry_run_lists_all_four_stages_without_creating_runtime_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/daily_paper_ingest.py", "--dry-run"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert [f'"stage": "s{stage}"' for stage in range(1, 5)] == [
        token for token in [f'"stage": "s{stage}"' for stage in range(1, 5)] if token in result.stdout
    ]


def test_s4_consumes_each_received_url_job_and_registers_the_local_pdf(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    repository = JobRepository(database)
    job_ids = []
    for index in (1, 2):
        job = repository.create_job(
            source_type="url",
            source_url=f"https://example.test/paper-{index}.pdf",
        )
        repository.update_job(job.job_id, canonical_id=f"2601.0000{index}", title=f"Paper {index}")
        job_ids.append(job.job_id)

    class FakePipeline:
        def __init__(self, repo: JobRepository, source_dir: Path) -> None:
            self.repo = repo
            self.source_dir = source_dir

        def _run_step(self, job_id: str, step_name: StepName) -> dict[str, str]:
            self.repo.start_step(job_id, step_name)
            output = {"step": step_name.value}
            self.repo.complete_step(job_id, step_name, output=output)
            return output

        def _step_download_pdf(self, job_id: str) -> dict[str, str]:
            self.source_dir.mkdir(parents=True, exist_ok=True)
            source = self.source_dir / f"{job_id}.pdf"
            source.write_bytes(b"%PDF-1.7\nfixture")
            self.repo.update_job(job_id, upload_path=str(source), source_sha256="fixture-sha")
            return {"pdf_path": str(source), "sha256": "fixture-sha", "canonical_id": self.repo.get_job(job_id).canonical_id}

        def _step_mineru_parse(self, job_id: str) -> dict[str, str]:
            return {"markdown_path": str(self.source_dir / f"{job_id}.md")}

        @staticmethod
        def _safe_error(exc: Exception) -> tuple[str, str]:
            return "fixture_failure", str(exc)

    result = daily_paper_ingest.consume_received_jobs(
        database=database,
        papers_dir=tmp_path / "papers",
        log_path=tmp_path / "runs.jsonl",
        pipeline_factory=lambda repo: FakePipeline(repo, tmp_path / "source"),
    )

    assert result == {"processed": 2, "failed": 0, "jobs": job_ids}
    for job_id in job_ids:
        job = repository.get_job(job_id)
        assert job is not None
        assert job.status == JobStatus.AWAITING_REVIEW
        assert job.source_url.startswith("https://example.test/")
        assert Path(job.upload_path).is_file()
        assert Path(job.upload_path).parent == tmp_path / "papers"
        assert repository.get_step(job_id, StepName.DOWNLOAD_PDF).status == StepStatus.SUCCEEDED
        assert repository.get_step(job_id, StepName.MINERU_PARSE).status == StepStatus.SUCCEEDED
    repository.close()


def test_outbox_consumer_processes_up_to_max_events(monkeypatch, tmp_path: Path) -> None:
    consumed = iter(["job-1", "job-2", "job-3"])
    monkeypatch.setattr(consume_catalog_outbox, "consume_next", lambda _repo: next(consumed, None))

    assert consume_catalog_outbox.main(["--db", str(tmp_path / "catalog.sqlite3"), "--max", "2"]) == 0
