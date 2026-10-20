from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paper_intake.adapters import DispatchResult, ExternalServiceError, NotionPage
from paper_intake.inputs import PaperInputStore
from paper_intake.models import JobStatus, StepName
from paper_intake.repository import JobRepository
from paper_intake.service import PaperIntakeService, ServiceError


class _FakePipeline:
    PROCESSING_STEPS = (
        StepName.VALIDATE_INPUT,
        StepName.RESOLVE_METADATA,
        StepName.DOWNLOAD_PDF,
        StepName.MINERU_PARSE,
        StepName.DEEPSEEK_GENERATE,
        StepName.CLASSIFY,
        StepName.QUALITY_CHECK,
        StepName.WRITE_NOTION_DRAFT,
    )

    def __init__(self, repo: JobRepository):
        self.repo = repo
        self.calls = []

    def run(self, job_id: str):
        self.calls.append(job_id)
        return self.repo.update_job(job_id, status=JobStatus.AWAITING_REVIEW)

    def retry(self, job_id: str):
        return self.run(job_id)


class _FakeNotion:
    def __init__(self):
        self.publish_calls = 0
        self.restore_calls = []

    def publish(self, page_id: str, *, title: str, slug: str, arxiv_id: str):
        self.publish_calls += 1
        return NotionPage(page_id, "https://notion.so/page", "Published")

    def restore_draft(self, page_id: str, *, markdown: str, title: str, slug: str, arxiv_id: str):
        self.restore_calls.append((page_id, markdown, title, slug, arxiv_id))
        return NotionPage(page_id, "https://notion.so/page", "Draft")


class _FakeGitHub:
    def __init__(self, *, fail_once: bool = False, triggered: bool = True):
        self.calls = 0
        self.fail_once = fail_once
        self.triggered = triggered

    def dispatch(self):
        self.calls += 1
        if self.fail_once and self.calls == 1:
            raise ExternalServiceError("github_dispatch_failed", "GitHub workflow dispatch failed.")
        return DispatchResult(self.triggered, run_id="run-1" if self.triggered else "")


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.repo = JobRepository(self.root / "jobs.sqlite3")
        self.store = PaperInputStore(self.root / "inbox")
        self.pipeline = _FakePipeline(self.repo)
        self.notion = _FakeNotion()
        self.github = _FakeGitHub()
        self.service = PaperIntakeService(
            repository=self.repo,
            input_store=self.store,
            pipeline=self.pipeline,
            notion=self.notion,
            github=self.github,
            workflow_root=self.root / "workflow",
            site_url="https://example.github.io",
            start_worker=False,
        )

    def tearDown(self) -> None:
        self.service.close()
        self.repo.close()
        self.temp_dir.cleanup()

    def _reviewable_job(self):
        saved = self.store.store_upload("review", "paper.pdf", b"%PDF-1.7\nbody")
        job = self.repo.create_job(source_type="upload", upload_path=str(saved.path))
        self.repo.update_job(
            job.job_id,
            canonical_id="2608.17316",
            title="测试论文",
            notion_page_id="page",
            notion_url="https://notion.so/page",
            status=JobStatus.AWAITING_REVIEW,
        )
        self.repo.start_step(job.job_id, StepName.QUALITY_CHECK)
        self.repo.complete_step(
            job.job_id,
            StepName.QUALITY_CHECK,
            output={"publishable": True, "issue_codes": []},
        )
        bundle = self.root / "workflow" / job.job_id
        bundle.mkdir(parents=True)
        (bundle / "notion-before.md").write_text("old body", encoding="utf-8")
        return self.repo.update_job(job.job_id, status=JobStatus.AWAITING_REVIEW)

    def test_queue_processes_only_one_job_per_tick(self) -> None:
        first = self.service.submit_upload("one.pdf", b"%PDF-1.7\none")
        second = self.service.submit_upload("two.pdf", b"%PDF-1.7\ntwo")

        self.assertTrue(self.service.run_pending_once())
        self.assertEqual(self.pipeline.calls, [first.job_id])
        self.assertEqual(self.repo.get_job(second.job_id).status, JobStatus.RECEIVED)
        self.assertTrue(self.service.run_pending_once())
        self.assertEqual(self.pipeline.calls, [first.job_id, second.job_id])

    def test_approval_publishes_notion_then_dispatches_pages(self) -> None:
        job = self._reviewable_job()

        approved = self.service.approve(job.job_id)

        self.assertEqual(self.notion.publish_calls, 1)
        self.assertEqual(self.github.calls, 1)
        self.assertEqual(approved.status, JobStatus.PUBLISHING)
        self.assertEqual(approved.github_run_id, "run-1")
        self.assertEqual(approved.published_url, "https://example.github.io/article/paper-2608.17316/")

    def test_blocked_or_unreviewed_job_cannot_be_approved(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="missing.pdf")
        self.repo.update_job(job.job_id, status=JobStatus.BLOCKED)

        with self.assertRaisesRegex(ServiceError, "awaiting review"):
            self.service.approve(job.job_id)

        self.assertEqual(self.notion.publish_calls, 0)
        self.assertEqual(self.github.calls, 0)

    def test_deployment_retry_does_not_publish_notion_twice(self) -> None:
        job = self._reviewable_job()
        self.github = _FakeGitHub(fail_once=True)
        self.service.github = self.github

        failed = self.service.approve(job.job_id)
        retried = self.service.retry_deployment(job.job_id)

        self.assertEqual(failed.status, JobStatus.FAILED)
        self.assertEqual(retried.status, JobStatus.PUBLISHING)
        self.assertEqual(self.notion.publish_calls, 1)
        self.assertEqual(self.github.calls, 2)

    def test_cancel_does_not_delete_uploaded_pdf(self) -> None:
        job = self.service.submit_upload("paper.pdf", b"%PDF-1.7\nbody")
        pdf = Path(job.upload_path)

        cancelled = self.service.cancel(job.job_id)

        self.assertEqual(cancelled.status, JobStatus.CANCELLED)
        self.assertTrue(pdf.is_file())

    def test_restore_notion_uses_saved_snapshot_and_returns_to_review(self) -> None:
        job = self._reviewable_job()

        restored = self.service.restore_notion(job.job_id)

        self.assertEqual(self.notion.restore_calls[0][1], "old body")
        self.assertEqual(restored.status, JobStatus.AWAITING_REVIEW)

    def test_blocked_job_can_restart_from_deepseek_without_resetting_mineru(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="paper.pdf")
        for step_name in (
            StepName.MINERU_PARSE,
            StepName.DEEPSEEK_GENERATE,
            StepName.CLASSIFY,
            StepName.QUALITY_CHECK,
        ):
            self.repo.start_step(job.job_id, step_name)
            self.repo.complete_step(job.job_id, step_name, output={})
        self.repo.update_job(job.job_id, status=JobStatus.BLOCKED)

        retried = self.service.retry_processing(
            job.job_id,
            restart_from=StepName.DEEPSEEK_GENERATE,
        )

        self.assertEqual(retried.status, JobStatus.AWAITING_REVIEW)
        self.assertEqual(
            self.repo.get_step(job.job_id, StepName.MINERU_PARSE).status.value,
            "succeeded",
        )
        self.assertIsNone(self.repo.get_step(job.job_id, StepName.DEEPSEEK_GENERATE))

    def test_mark_published_requires_successful_publication_check(self) -> None:
        job = self._reviewable_job()
        approved = self.service.approve(job.job_id)

        with self.assertRaisesRegex(ServiceError, "not reachable"):
            self.service.verify_publication(approved.job_id, checker=lambda _url: False)
        published = self.service.verify_publication(approved.job_id, checker=lambda _url: True)

        self.assertEqual(published.status, JobStatus.PUBLISHED)


if __name__ == "__main__":
    unittest.main()
