from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from paper_intake.models import JobStatus, StepName, StepStatus
from paper_intake.repository import JobRepository
from paper_intake.catalog import PaperRecord
from paper_intake.catalog_admission import AdmissionDecision
from paper_intake.catalog_store import CatalogRepository
from scripts import consume_catalog_outbox
from scripts import daily_paper_ingest


ROOT = Path(__file__).resolve().parents[1]


def test_append_run_uses_unified_run_log_schema(tmp_path: Path) -> None:
    from redbook.infrastructure import run_log

    log_path = tmp_path / "runs.jsonl"
    daily_paper_ingest.append_run(
        log_path, stage="s1", status="ok", detail={"paper_count": 2}, duration_ms=12,
    )
    rows = run_log.read_events(log_path)
    assert len(rows) == 1
    assert rows[0]["event"] == "paper_ingest_stage"
    assert rows[0]["stage"] == "s1"
    assert rows[0]["status"] == "ok"
    assert "paper_ingest_stage" in run_log.summarize(rows)


def test_dry_run_lists_all_four_stages_without_creating_runtime_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/daily_paper_ingest.py", "--dry-run"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert [f'"stage": "s{stage}"' for stage in range(1, 5)] == [
        token for token in [f'"stage": "s{stage}"' for stage in range(1, 5)] if token in result.stdout
    ]


def test_s4_consumes_each_received_url_job_and_registers_the_local_pdf(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(daily_paper_ingest, "DEFAULT_RUN_LOG", tmp_path / "unexpected-default.jsonl")
    database = tmp_path / "catalog.sqlite3"
    from paper_intake.catalog_store import CatalogRepository
    CatalogRepository(database).close()
    repository = JobRepository(database)
    for index in (1, 2):
        repository._connection.execute(
            """INSERT INTO papers (canonical_id, status, title, normalized_title,
               publication_year, venue_type, venue_name, paper_url, doi, arxiv_id,
               authors_json, last_upstream_updated_at, source_version, created_at, updated_at)
               VALUES (?, 'discovered', ?, ?, 2026, 'preprint', 'arXiv', '', '', ?, '[]', '', 'v', '', '')""",
            (f"arxiv:2601.0000{index}", f"Paper {index}", f"paper {index}", f"2601.0000{index}"),
        )
    repository._connection.commit()
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

    assert result == {"processed": 2, "failed": 0, "blocked": 0, "jobs": job_ids}
    assert '"step": "mineru_parse"' in (tmp_path / "runs.jsonl").read_text(encoding="utf-8")
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


def test_s1_timeout_continues_through_remaining_stages_when_fail_fast_is_disabled(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "schedule.yaml"
    config_path.write_text(
        """enabled: true
time: \"11:00\"
timezone: \"Asia/Shanghai\"
working_dir: \"D:/recommendation-system-learning\"
python: \"python\"
entrypoint: \"scripts/daily_paper_ingest.py\"
log_file: \"data/logs/ingest.log\"
s1_timeout_seconds: 600
""",
        encoding="utf-8",
    )
    stages: list[str] = []
    monkeypatch.setattr(daily_paper_ingest, "_commands", lambda *_args: {stage: [stage] for stage in ("s1", "s2", "s3", "s4")})
    monkeypatch.setattr(daily_paper_ingest, "append_run", lambda *_args, **_kwargs: None)

    def fake_run_stage(stage: str, _command: list[str], **_kwargs):
        stages.append(stage)
        return (stage != "s1", {"error": "timeout"} if stage == "s1" else {})

    monkeypatch.setattr(daily_paper_ingest, "_run_stage", fake_run_stage)

    assert daily_paper_ingest.run_once(
        config_path=config_path,
        dry_run=False,
        selected_stage="all",
        fail_fast=False,
        verbose=False,
        s1_timeout_seconds=1,
    ) == 1
    assert stages == ["s1", "s2", "s3", "s4"]


def test_entry_resolves_relative_working_directory_and_passes_the_unified_database(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "schedule.yaml"
    config_path.write_text(
        """enabled: true
time: \"11:00\"
timezone: \"Asia/Shanghai\"
working_dir: \".\"
python: \"python\"
entrypoint: \"scripts/daily_paper_ingest.py\"
log_file: \"data/logs/runs.jsonl\"
s1_timeout_seconds: 600
""",
        encoding="utf-8",
    )
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(daily_paper_ingest, "_commands", lambda *_args: {"s2": ["s2"]})
    monkeypatch.setattr(daily_paper_ingest, "append_run", lambda *_args, **_kwargs: None)

    def fake_run_stage(_stage: str, _command: list[str], **kwargs):
        calls.append(kwargs)
        return True, {}

    monkeypatch.setattr(daily_paper_ingest, "_run_stage", fake_run_stage)

    assert daily_paper_ingest.run_once(
        config_path=config_path,
        dry_run=False,
        selected_stage="s2",
        fail_fast=False,
        verbose=False,
    ) == 0
    assert calls[0]["cwd"] == ROOT
    assert calls[0]["env"]["PAPER_INTAKE_DB_PATH"] == str(daily_paper_ingest.UNIFIED_CATALOG_DB)


def test_catalog_event_fixture_creates_a_received_url_job_through_s3(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    catalog = CatalogRepository(database)
    canonical_id = catalog.upsert_candidate(PaperRecord(
        publication_year=2026,
        venue_type="preprint",
        venue_name="arXiv",
        title="Catalog delivery fixture",
        paper_url="https://arxiv.org/abs/2601.00001",
        source="arxiv",
        source_id="2601.00001v1",
        arxiv_id="2601.00001",
    ))
    catalog_job_id = catalog.queue_candidate(canonical_id)
    assert catalog.complete_governance(
        catalog_job_id,
        AdmissionDecision(
            status="admitted",
            reason_code="fixture",
            pdf_url="https://arxiv.org/pdf/2601.00001.pdf",
        ),
        budget_week="2026-W01",
        domain="all",
        quota=1,
    ) == "published_to_catalog"
    catalog.close()

    assert consume_catalog_outbox.main(["--db", str(database), "--max", "1000"]) == 0
    repository = JobRepository(database)
    received = repository.list_received_jobs()
    assert len(received) == 1
    assert received[0].source_type == "url"
    assert received[0].source_url == "https://arxiv.org/pdf/2601.00001.pdf"
    repository.close()


def test_schedule_config_rejects_an_invalid_time(tmp_path: Path) -> None:
    config_path = tmp_path / "schedule.yaml"
    config_path.write_text(
        """enabled: true
time: \"25:00\"
timezone: \"Asia/Shanghai\"
working_dir: \".\"
python: \"python\"
entrypoint: \"scripts/daily_paper_ingest.py\"
log_file: \"data/logs/runs.jsonl\"
s1_timeout_seconds: 600
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="HH:MM"):
        daily_paper_ingest.load_config(config_path)
