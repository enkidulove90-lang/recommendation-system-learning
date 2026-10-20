from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from paper_intake.models import JobStatus
from paper_intake.repository import JobRepository
from paper_intake.service import ServiceError
from paper_intake.web import create_app


class _FakeService:
    def __init__(self, repo: JobRepository):
        self.repository = repo
        self.uploads = []
        self.raise_duplicate = False

    def submit_url(self, url: str, *, title: str = ""):
        if self.raise_duplicate:
            raise ServiceError("duplicate_paper", "Paper already exists in job existing.")
        job = self.repository.create_job(source_type="url", source_url=url)
        return self.repository.update_job(job.job_id, title=title)

    def submit_upload(self, filename: str, content: bytes, *, paper_url: str = "", title: str = ""):
        self.uploads.append((filename, content, paper_url, title))
        job = self.repository.create_job(source_type="upload", upload_path="hidden/source.pdf")
        return self.repository.update_job(job.job_id, title=title, source_url=paper_url)

    def retry_processing(self, job_id: str, *, restart_from=None):
        return self.repository.update_job(job_id, status=JobStatus.PROCESSING)

    def approve(self, job_id: str):
        job = self.repository.get_job(job_id)
        if job.status != JobStatus.AWAITING_REVIEW:
            raise ServiceError("not_reviewable", "Job is not awaiting review.")
        return self.repository.update_job(job_id, status=JobStatus.PUBLISHING)

    def cancel(self, job_id: str):
        return self.repository.update_job(job_id, status=JobStatus.CANCELLED)

    def retry_deployment(self, job_id: str):
        return self.repository.update_job(job_id, status=JobStatus.PUBLISHING)

    def restore_notion(self, job_id: str):
        return self.repository.update_job(job_id, status=JobStatus.AWAITING_REVIEW)


class WebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = JobRepository(Path(self.temp_dir.name) / "jobs.sqlite3")
        self.service = _FakeService(self.repo)
        self.client = TestClient(create_app(self.service, max_upload_bytes=32))

    def tearDown(self) -> None:
        self.repo.close()
        self.temp_dir.cleanup()

    def test_homepage_is_a_local_paper_control_desk(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("论文入库控制台", response.text)
        self.assertIn("PDF", response.text)
        self.assertIn("Notion Draft", response.text)

    def test_url_submission_returns_accepted_job(self) -> None:
        response = self.client.post(
            "/api/jobs/url",
            json={"url": "https://arxiv.org/abs/2608.17316", "title": "A Paper"},
        )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["status"], "received")
        self.assertEqual(response.json()["title"], "A Paper")

    def test_upload_returns_job_without_exposing_local_paths_or_secrets(self) -> None:
        response = self.client.post(
            "/api/jobs/upload",
            data={"paper_url": "https://arxiv.org/abs/2608.17316", "title": "A Paper"},
            files={"file": ("paper.pdf", b"%PDF-1.7\nbody", "application/pdf")},
        )

        self.assertEqual(response.status_code, 202)
        body = response.text.lower()
        self.assertNotIn("hidden/source.pdf", body)
        self.assertNotIn("token", body)
        self.assertEqual(self.service.uploads[0][0], "paper.pdf")

    def test_oversized_upload_is_rejected_before_service_call(self) -> None:
        response = self.client.post(
            "/api/jobs/upload",
            files={"file": ("paper.pdf", b"%PDF-" + b"x" * 40, "application/pdf")},
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.service.uploads, [])

    def test_list_and_detail_include_safe_step_and_event_data(self) -> None:
        job = self.repo.create_job(source_type="url", source_url="https://example.org/paper.pdf")

        listing = self.client.get("/api/jobs")
        detail = self.client.get(f"/api/jobs/{job.job_id}")

        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()[0]["job_id"], job.job_id)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["steps"], [])
        self.assertEqual(detail.json()["events"][0]["event_type"], "job.created")
        self.assertNotIn("upload_path", detail.json())

    def test_duplicate_submission_returns_conflict_with_existing_job_hint(self) -> None:
        self.service.raise_duplicate = True

        response = self.client.post(
            "/api/jobs/url",
            json={"url": "https://arxiv.org/abs/2608.17316"},
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error_code"], "duplicate_paper")
        self.assertIn("existing", response.json()["message"])

    def test_unreviewed_job_approval_returns_conflict(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="paper.pdf")

        response = self.client.post(f"/api/jobs/{job.job_id}/approve")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error_code"], "not_reviewable")

    def test_cancel_action_updates_job(self) -> None:
        job = self.repo.create_job(source_type="upload", upload_path="paper.pdf")

        response = self.client.post(f"/api/jobs/{job.job_id}/cancel")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "cancelled")


if __name__ == "__main__":
    unittest.main()
