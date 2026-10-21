from __future__ import annotations

import mimetypes
import logging
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any

from .models import JobStatus, StepName, StepStatus
from .remote import LeaseLost, RemoteGatewayClient, RemoteJob


logger = logging.getLogger(__name__)

# Background workers must not inherit an interactive shell proxy accidentally.
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)


class RemoteProcessingError(RuntimeError):
    """A pipeline failure whose code and message are safe for the owner UI."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class RemoteWorker:
    def __init__(
        self,
        *,
        gateway,
        processor,
        worker_id: str | None = None,
        poll_seconds: float = 10,
        heartbeat_seconds: float = 30,
        preflight=None,
        preflight_interval_seconds: float = 60,
    ):
        self.gateway = gateway
        self.processor = processor
        self.worker_id = worker_id or f"{socket.gethostname()}-{os.getpid()}"
        self.poll_seconds = max(0, poll_seconds)
        self.heartbeat_seconds = max(0.05, heartbeat_seconds)
        self.preflight = preflight
        self.preflight_interval_seconds = max(0.0, preflight_interval_seconds)
        self._last_preflight = 0.0
        self._preflight_error: Exception | None = None
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run_claimed(self, job: RemoteJob) -> None:
        worker_id = job.lease_owner or self.worker_id
        self.gateway.heartbeat(job.job_id, worker_id)
        heartbeat_stop = threading.Event()
        lost_lease = threading.Event()

        def heartbeat_loop() -> None:
            while not heartbeat_stop.wait(self.heartbeat_seconds):
                try:
                    self.gateway.heartbeat(job.job_id, worker_id)
                except LeaseLost:
                    lost_lease.set()
                    return
                except Exception:
                    # A transient client retry may still recover on the next heartbeat.
                    continue

        thread = threading.Thread(target=heartbeat_loop, name=f"heartbeat-{job.job_id}", daemon=True)
        thread.start()
        try:
            try:
                publication = self.processor.process(job, self.gateway)
            except LeaseLost:
                raise
            except Exception as exc:
                code = "processing_failed"
                message = "The local paper processor failed. Inspect local logs for details."
                if isinstance(exc, RemoteProcessingError):
                    code = exc.code
                    message = str(exc)
                self.gateway.fail(
                    job.job_id,
                    worker_id,
                    code,
                    message,
                )
                raise
            if lost_lease.is_set():
                raise LeaseLost(job.job_id)
            # Completion transfers ownership to the publishing state. If dispatch
            # fails, do not send a second failure request using the expired lease.
            self.gateway.complete(job.job_id, worker_id, publication)
        finally:
            heartbeat_stop.set()
            thread.join(timeout=2)

    def run_once(self) -> bool:
        now = time.monotonic()
        if self.preflight is not None:
            due = (
                self._last_preflight == 0.0
                or now - self._last_preflight >= self.preflight_interval_seconds
            )
            if due:
                self._last_preflight = now
                try:
                    self.preflight()
                except Exception as exc:
                    self._preflight_error = exc
                    raise
                self._preflight_error = None
            elif self._preflight_error is not None:
                raise self._preflight_error
        job = self.gateway.claim(self.worker_id)
        if job is None:
            return False
        self.run_claimed(job)
        return True

    def run_forever(self) -> None:
        while not self._stop.is_set():
            try:
                handled = self.run_once()
            except LeaseLost as exc:
                logger.warning("Worker lease was lost; continuing polling: %s", exc)
                handled = False
            except Exception:
                logger.exception("Worker iteration failed; continuing polling")
                handled = False
            if not handled:
                self._stop.wait(self.poll_seconds)


class RemotePipelineProcessor:
    """Runs the existing local pipeline and mirrors safe checkpoints remotely."""

    def __init__(
        self,
        *,
        repository,
        input_store,
        pipeline,
        workflow_root: str | Path,
        site_url: str,
    ):
        self.repository = repository
        self.input_store = input_store
        self.pipeline = pipeline
        self.workflow_root = Path(workflow_root)
        self.site_url = site_url.rstrip("/")

    def _ensure_local_job(self, job: RemoteJob, gateway) -> None:
        if self.repository.get_job(job.job_id) is not None:
            return
        if job.input_type == "url":
            self.repository.create_job(
                job_id=job.job_id,
                source_type="url",
                source_url=job.input_ref,
            )
            return
        local = self.repository.create_job(job_id=job.job_id, source_type="upload")
        try:
            saved = self.input_store.store_upload(job.job_id, "paper.pdf", gateway.download_input(job))
            self.repository.update_job(
                local.job_id,
                upload_path=str(saved.path),
                source_sha256=saved.sha256,
            )
        except Exception:
            self.repository.update_job(
                local.job_id,
                status=JobStatus.FAILED,
                error_code="remote_input_failed",
                error_message="The remote PDF could not be restored locally.",
            )
            raise

    @staticmethod
    def _artifact_id(value: Any) -> str:
        if isinstance(value, dict):
            return str(value.get("artifact_id") or "")
        return str(value or "")

    def _restore_remote_checkpoints(self, job: RemoteJob, gateway) -> None:
        if not job.artifact_storage_enabled:
            return
        parsed = job.checkpoints.get(StepName.MINERU_PARSE.value) or job.checkpoints.get("parsed")
        existing = self.repository.get_step(job.job_id, StepName.MINERU_PARSE)
        if not parsed or (existing and existing.status == StepStatus.SUCCEEDED):
            return

        for initial_step in (
            StepName.VALIDATE_INPUT,
            StepName.RESOLVE_METADATA,
            StepName.DOWNLOAD_PDF,
        ):
            self.pipeline._run_step(job.job_id, initial_step)

        bundle = self.workflow_root / job.job_id
        restore_root = bundle / "restored"
        restore_root.mkdir(parents=True, exist_ok=True)
        markdown_id = self._artifact_id(parsed.get("markdown_artifact"))
        if not markdown_id:
            return
        markdown_path = restore_root / "paper.md"
        markdown_path.write_bytes(gateway.download_artifact(job.job_id, job.lease_owner, markdown_id))
        figures = []
        for index, item in enumerate(parsed.get("figure_artifacts") or [], 1):
            artifact_id = self._artifact_id(item)
            if not artifact_id:
                continue
            figure_path = bundle / "images" / f"restored-{index}.png"
            figure_path.parent.mkdir(parents=True, exist_ok=True)
            content = gateway.download_artifact(job.job_id, job.lease_owner, artifact_id)
            figure_path.write_bytes(content)
            import hashlib

            figures.append(
                {
                    "path": figure_path.relative_to(bundle).as_posix(),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
        self.repository.start_step(job.job_id, StepName.MINERU_PARSE)
        self.repository.complete_step(
            job.job_id,
            StepName.MINERU_PARSE,
            output={"markdown_path": str(markdown_path), "figures": figures},
        )

    def _sync_step(self, job: RemoteJob, gateway, step: StepName, output: dict[str, Any]) -> None:
        if step.value in job.checkpoints or (
            step == StepName.MINERU_PARSE and "parsed" in job.checkpoints
        ):
            return
        remote_output: dict[str, Any] = {
            key: value
            for key, value in output.items()
            if not key.endswith("_path") and key not in {"figures"}
        }
        if step == StepName.MINERU_PARSE and job.artifact_storage_enabled:
            markdown_path = Path(output["markdown_path"])
            remote_output["markdown_artifact"] = gateway.upload_artifact(
                job.job_id,
                job.lease_owner,
                kind="parsed_markdown",
                filename=markdown_path.name,
                content=markdown_path.read_bytes(),
                content_type="text/markdown",
            )
            figure_artifacts = []
            bundle = self.workflow_root / job.job_id
            for figure in output.get("figures") or []:
                path = bundle / figure["path"]
                figure_artifacts.append(
                    gateway.upload_artifact(
                        job.job_id,
                        job.lease_owner,
                        kind="figure",
                        filename=path.name,
                        content=path.read_bytes(),
                        content_type=mimetypes.guess_type(path.name)[0] or "image/png",
                    )
                )
            remote_output["figure_artifacts"] = figure_artifacts
        elif step in {StepName.DEEPSEEK_GENERATE, StepName.CLASSIFY} and job.artifact_storage_enabled:
            article_path = Path(output["article_path"])
            remote_output["article_artifact"] = gateway.upload_artifact(
                job.job_id,
                job.lease_owner,
                kind="article_json",
                filename=article_path.name,
                content=article_path.read_bytes(),
                content_type="application/json",
            )
        elif step == StepName.QUALITY_CHECK and job.artifact_storage_enabled:
            article_path = Path(output["article_path"])
            remote_output["article_artifact"] = gateway.upload_artifact(
                job.job_id,
                job.lease_owner,
                kind="generated_article",
                filename=article_path.name,
                content=article_path.read_bytes(),
                content_type="text/markdown",
            )
        gateway.checkpoint(job.job_id, job.lease_owner, step.value, remote_output)

    def process(self, job: RemoteJob, gateway) -> dict[str, Any]:
        self._ensure_local_job(job, gateway)
        self._restore_remote_checkpoints(job, gateway)
        result = self.pipeline.run(
            job.job_id,
            before_step=lambda step: gateway.heartbeat(
                job.job_id,
                job.lease_owner,
                step.value,
            ),
            on_step_completed=lambda step, output: self._sync_step(job, gateway, step, output),
        )
        if result.status != JobStatus.PUBLISHING or not result.notion_page_id:
            raise RemoteProcessingError(
                result.error_code or "processing_failed",
                result.error_message or "The local paper processor did not produce a publishable Notion page.",
            )
        slug = f"paper-{result.canonical_id}"
        return {
            "notion_page_id": result.notion_page_id,
            "slug": slug,
            "site_url": f"{self.site_url}/article/{slug}/",
        }


def build_remote_worker(gateway: RemoteGatewayClient) -> RemoteWorker:
    from dotenv import load_dotenv

    from .adapters import DeepSeekArticleAdapter, MinerUAdapter, NotionGateway
    from .inputs import PaperInputStore
    from .metadata import ArxivMetadataResolver
    from .pipeline import PaperPipeline
    from .repository import JobRepository

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env", override=False)
    required = {
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN", ""),
        "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID", ""),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError("Missing local configuration: " + ", ".join(missing) + ".")

    runtime_root = project_root / "data" / "paper_intake" / "remote"
    workflow_root = project_root / "data" / "workflow_state" / "paper_intake" / "remote"
    repository = JobRepository(runtime_root / "jobs.sqlite3")
    input_store = PaperInputStore(
        runtime_root / "inbox",
        max_file_bytes=int(os.getenv("PAPER_INTAKE_MAX_FILE_MB", "100")) * 1024 * 1024,
    )
    notion = NotionGateway(required["NOTION_TOKEN"], required["NOTION_DATABASE_ID"])
    deepseek = DeepSeekArticleAdapter(
        api_key=required["DEEPSEEK_API_KEY"],
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    )
    pipeline = PaperPipeline(
        repository=repository,
        input_store=input_store,
        mineru=MinerUAdapter(),
        deepseek=deepseek,
        notion=notion,
        workflow_root=workflow_root,
        metadata_resolver=ArxivMetadataResolver(),
    )
    processor = RemotePipelineProcessor(
        repository=repository,
        input_store=input_store,
        pipeline=pipeline,
        workflow_root=workflow_root,
        site_url=os.getenv(
            "PAPER_INTAKE_SITE_URL",
            "https://enkidulove90-lang.github.io",
        ),
    )
    worker = RemoteWorker(
        gateway=gateway,
        processor=processor,
        worker_id=os.getenv("PAPER_INTAKE_WORKER_ID") or None,
        poll_seconds=float(os.getenv("PAPER_INTAKE_POLL_SECONDS", "10")),
        heartbeat_seconds=float(os.getenv("PAPER_INTAKE_HEARTBEAT_SECONDS", "30")),
        preflight=lambda: (deepseek.preflight(), notion.preflight_schema()),
        preflight_interval_seconds=float(os.getenv("PAPER_INTAKE_PREFLIGHT_SECONDS", "60")),
    )
    worker.repository = repository
    return worker
