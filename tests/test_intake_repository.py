from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paper_intake.models import JobStatus, StepName, StepStatus
from paper_intake.repository import JobRepository


class JobRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "jobs.sqlite3"
        self.repo = JobRepository(self.db_path)

    def tearDown(self) -> None:
        self.repo.close()
        self.temp_dir.cleanup()

    def test_create_job_persists_across_reopen(self) -> None:
        created = self.repo.create_job(
            source_type="url",
            source_url="https://arxiv.org/pdf/2608.17316",
        )
        self.repo.close()

        self.repo = JobRepository(self.db_path)
        loaded = self.repo.get_job(created.job_id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.status, JobStatus.RECEIVED)
        self.assertEqual(loaded.source_type, "url")
        self.assertEqual(loaded.source_url, "https://arxiv.org/pdf/2608.17316")

    def test_step_transition_records_attempt_output_and_event(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="source.pdf")

        started = self.repo.start_step(
            job.job_id,
            StepName.MINERU_PARSE,
            input_hash="pdf-sha256",
        )
        completed = self.repo.complete_step(
            job.job_id,
            StepName.MINERU_PARSE,
            output={"markdown_path": "paper.md"},
        )

        self.assertEqual(started.status, StepStatus.RUNNING)
        self.assertEqual(started.attempts, 1)
        self.assertEqual(completed.status, StepStatus.SUCCEEDED)
        self.assertEqual(completed.output["markdown_path"], "paper.md")
        events = self.repo.list_events(job.job_id)
        self.assertEqual([event.event_type for event in events], ["job.created", "step.started", "step.succeeded"])

    def test_running_step_becomes_interrupted_after_restart(self) -> None:
        job = self.repo.create_job(
            source_type="url",
            source_url="https://arxiv.org/pdf/2608.17316",
        )
        self.repo.start_step(job.job_id, StepName.MINERU_PARSE)
        self.repo.close()

        self.repo = JobRepository(self.db_path)
        recovered = self.repo.recover_interrupted_jobs()

        step = self.repo.get_step(job.job_id, StepName.MINERU_PARSE)
        loaded = self.repo.get_job(job.job_id)
        self.assertEqual(recovered, 1)
        self.assertEqual(step.status, StepStatus.INTERRUPTED)
        self.assertEqual(loaded.status, JobStatus.FAILED)
        self.assertEqual(loaded.error_code, "interrupted")

    def test_external_identifiers_are_retained(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="source.pdf")

        updated = self.repo.update_job(
            job.job_id,
            canonical_id="2608.17316",
            source_sha256="abc123",
            title="A Paper",
            notion_page_id="notion-page",
            notion_url="https://notion.so/notion-page",
            github_run_id="12345",
            published_url="https://example.github.io/article/a-paper/",
        )

        self.assertEqual(updated.canonical_id, "2608.17316")
        self.assertEqual(updated.source_sha256, "abc123")
        self.assertEqual(updated.notion_page_id, "notion-page")
        self.assertEqual(updated.github_run_id, "12345")
        self.assertTrue(updated.published_url.endswith("/a-paper/"))

    def test_failed_step_keeps_safe_error_and_attempt_count(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="source.pdf")
        self.repo.start_step(job.job_id, StepName.DEEPSEEK_GENERATE)

        failed = self.repo.fail_step(
            job.job_id,
            StepName.DEEPSEEK_GENERATE,
            error_code="deepseek_timeout",
            error_message="The summary request timed out.",
        )

        loaded = self.repo.get_job(job.job_id)
        self.assertEqual(failed.status, StepStatus.FAILED)
        self.assertEqual(failed.attempts, 1)
        self.assertEqual(loaded.status, JobStatus.FAILED)
        self.assertEqual(loaded.error_code, "deepseek_timeout")
        self.assertNotIn("token", loaded.error_message.lower())


if __name__ == "__main__":
    unittest.main()
