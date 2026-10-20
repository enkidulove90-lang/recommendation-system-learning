from __future__ import annotations

import hashlib
import queue
import threading
from pathlib import Path
from typing import Callable

from .adapters import ExternalServiceError
from .inputs import PaperInputStore, canonicalize_url
from .models import JobRecord, JobStatus, StepName
from .repository import JobRepository


class ServiceError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class PaperIntakeService:
    def __init__(
        self,
        *,
        repository: JobRepository,
        input_store: PaperInputStore,
        pipeline,
        notion,
        github,
        workflow_root: str | Path,
        site_url: str,
        start_worker: bool = True,
    ):
        self.repository = repository
        self.input_store = input_store
        self.pipeline = pipeline
        self.notion = notion
        self.github = github
        self.workflow_root = Path(workflow_root)
        self.site_url = site_url.rstrip("/")
        self._queue: queue.Queue[str] = queue.Queue()
        self._stop = threading.Event()
        self._worker: threading.Thread | None = None
        self.repository.recover_interrupted_jobs()
        if start_worker:
            self._worker = threading.Thread(
                target=self._worker_loop,
                name="paper-intake-worker",
                daemon=True,
            )
            self._worker.start()

    def close(self) -> None:
        self._stop.set()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=2)

    def submit_url(self, url: str, *, title: str = "") -> JobRecord:
        source = canonicalize_url(url)
        duplicate = self.repository.find_duplicate(
            canonical_id=source.canonical_id,
            source_url=source.normalized_url,
        )
        if duplicate:
            raise ServiceError("duplicate_paper", f"Paper already exists in job {duplicate.job_id}.")
        job = self.repository.create_job(
            source_type="url",
            source_url=source.normalized_url,
        )
        if title or source.canonical_id:
            job = self.repository.update_job(
                job.job_id,
                title=title,
                canonical_id=source.canonical_id,
            )
        self._queue.put(job.job_id)
        return job

    def submit_upload(
        self,
        filename: str,
        content: bytes,
        *,
        paper_url: str = "",
        title: str = "",
    ) -> JobRecord:
        digest = hashlib.sha256(content).hexdigest()
        source = canonicalize_url(paper_url) if paper_url else None
        duplicate = self.repository.find_duplicate(
            canonical_id=source.canonical_id if source else "",
            source_sha256=digest,
            source_url=source.normalized_url if source else "",
        )
        if duplicate:
            raise ServiceError("duplicate_paper", f"Paper already exists in job {duplicate.job_id}.")
        job = self.repository.create_job(
            source_type="upload",
            source_url=source.normalized_url if source else "",
        )
        try:
            saved = self.input_store.store_upload(job.job_id, filename, content)
        except Exception:
            self.repository.update_job(
                job.job_id,
                status=JobStatus.FAILED,
                error_code="invalid_upload",
                error_message="The uploaded file could not be accepted.",
            )
            raise
        job = self.repository.update_job(
            job.job_id,
            upload_path=str(saved.path),
            source_sha256=saved.sha256,
            canonical_id=source.canonical_id if source else "",
            title=title,
        )
        self._queue.put(job.job_id)
        return job

    def run_pending_once(self) -> bool:
        try:
            job_id = self._queue.get_nowait()
        except queue.Empty:
            return False
        try:
            job = self.repository.get_job(job_id)
            if job and job.status != JobStatus.CANCELLED:
                self.pipeline.run(job_id)
        finally:
            self._queue.task_done()
        return True

    def _worker_loop(self) -> None:
        while not self._stop.is_set():
            try:
                job_id = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue
            try:
                job = self.repository.get_job(job_id)
                if job and job.status != JobStatus.CANCELLED:
                    self.pipeline.run(job_id)
            finally:
                self._queue.task_done()

    def retry_processing(
        self,
        job_id: str,
        *,
        restart_from: StepName | None = None,
    ) -> JobRecord:
        job = self._require_job(job_id)
        if job.status not in {JobStatus.FAILED, JobStatus.BLOCKED}:
            raise ServiceError("not_retryable", "Job is not in a retryable state.")
        if restart_from is not None:
            self.repository.reset_steps(
                job_id,
                restart_from=restart_from,
                ordered_steps=self.pipeline.PROCESSING_STEPS,
            )
        return self.pipeline.retry(job_id)

    def approve(self, job_id: str) -> JobRecord:
        job = self._require_job(job_id)
        if job.status != JobStatus.AWAITING_REVIEW:
            raise ServiceError("not_reviewable", "Job is not awaiting review.")
        quality = self.repository.get_step(job_id, StepName.QUALITY_CHECK)
        if not quality or not quality.output.get("publishable"):
            raise ServiceError("quality_gate_failed", "Article has not passed the quality gate.")
        if not job.notion_page_id:
            raise ServiceError("notion_page_missing", "Notion draft is missing.")

        self.repository.start_step(job_id, StepName.APPROVE)
        try:
            self.notion.publish(
                job.notion_page_id,
                title=job.title,
                slug=f"paper-{job.canonical_id}",
                arxiv_id=job.canonical_id,
            )
            self.repository.complete_step(
                job_id,
                StepName.APPROVE,
                output={"status": "Published"},
            )
        except Exception as exc:
            self.repository.fail_step(
                job_id,
                StepName.APPROVE,
                error_code="notion_publish_failed",
                error_message="Notion approval failed.",
            )
            return self._require_job(job_id)

        publication_url = f"{self.site_url}/article/paper-{job.canonical_id}/"
        self.repository.update_job(
            job_id,
            status=JobStatus.PUBLISHING,
            published_url=publication_url,
        )
        return self._dispatch(job_id)

    def _dispatch(self, job_id: str) -> JobRecord:
        self.repository.start_step(job_id, StepName.TRIGGER_PAGES)
        try:
            result = self.github.dispatch()
            self.repository.complete_step(
                job_id,
                StepName.TRIGGER_PAGES,
                output={
                    "triggered": result.triggered,
                    "run_id": result.run_id,
                    "message": result.message,
                },
            )
            return self.repository.update_job(
                job_id,
                status=JobStatus.PUBLISHING,
                github_run_id=result.run_id,
                error_code="",
                error_message="",
            )
        except Exception as exc:
            code = exc.code if isinstance(exc, ExternalServiceError) else "github_dispatch_failed"
            self.repository.fail_step(
                job_id,
                StepName.TRIGGER_PAGES,
                error_code=code,
                error_message="GitHub Pages deployment trigger failed.",
            )
            return self._require_job(job_id)

    def retry_deployment(self, job_id: str) -> JobRecord:
        job = self._require_job(job_id)
        trigger = self.repository.get_step(job_id, StepName.TRIGGER_PAGES)
        if not trigger or trigger.status.value not in {"failed", "interrupted"}:
            raise ServiceError("deployment_not_retryable", "Deployment is not retryable.")
        return self._dispatch(job_id)

    def cancel(self, job_id: str) -> JobRecord:
        job = self._require_job(job_id)
        if job.status == JobStatus.PUBLISHED:
            raise ServiceError("already_published", "Published jobs cannot be cancelled.")
        return self.repository.update_job(
            job_id,
            status=JobStatus.CANCELLED,
            error_code="",
            error_message="",
        )

    def restore_notion(self, job_id: str) -> JobRecord:
        job = self._require_job(job_id)
        snapshot = self.workflow_root / job_id / "notion-before.md"
        if not job.notion_page_id or not snapshot.is_file():
            raise ServiceError("notion_snapshot_missing", "Notion recovery snapshot is missing.")
        self.notion.restore_draft(
            job.notion_page_id,
            markdown=snapshot.read_text(encoding="utf-8"),
            title=job.title,
            slug=f"paper-{job.canonical_id}",
            arxiv_id=job.canonical_id,
        )
        return self.repository.update_job(
            job_id,
            status=JobStatus.AWAITING_REVIEW,
            error_code="",
            error_message="",
        )

    def verify_publication(
        self,
        job_id: str,
        *,
        checker: Callable[[str], bool],
    ) -> JobRecord:
        job = self._require_job(job_id)
        if not job.published_url or not checker(job.published_url):
            raise ServiceError("publication_not_ready", "Published article is not reachable yet.")
        self.repository.start_step(job_id, StepName.VERIFY_PUBLICATION)
        self.repository.complete_step(
            job_id,
            StepName.VERIFY_PUBLICATION,
            output={"url": job.published_url},
        )
        return self.repository.update_job(
            job_id,
            status=JobStatus.PUBLISHED,
            current_step="",
            error_code="",
            error_message="",
        )

    def _require_job(self, job_id: str) -> JobRecord:
        job = self.repository.get_job(job_id)
        if job is None:
            raise ServiceError("job_not_found", f"Unknown job: {job_id}")
        return job
