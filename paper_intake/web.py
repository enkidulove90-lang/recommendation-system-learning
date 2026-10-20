from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

from .inputs import InputValidationError
from .models import JobRecord, StepName
from .service import ServiceError


PACKAGE_ROOT = Path(__file__).resolve().parent
_PRIVATE_KEYS = ("path", "sha", "token", "secret", "api_key", "markdown")


class UrlSubmission(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    url: str
    title: str = ""


class RetrySubmission(BaseModel):
    restart_from: StepName | None = None


def _safe_nested(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _safe_nested(item)
            for key, item in value.items()
            if not any(private in key.lower() for private in _PRIVATE_KEYS)
        }
    if isinstance(value, list):
        return [_safe_nested(item) for item in value]
    return value


def _serialize_job(job: JobRecord) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "source_type": job.source_type,
        "source_url": job.source_url,
        "canonical_id": job.canonical_id,
        "title": job.title,
        "status": job.status.value,
        "current_step": job.current_step,
        "notion_url": job.notion_url,
        "github_run_id": job.github_run_id,
        "published_url": job.published_url,
        "error_code": job.error_code,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


def _serialize_detail(service, job: JobRecord) -> dict[str, Any]:
    payload = _serialize_job(job)
    payload["steps"] = [
        {
            "step_name": step.step_name.value,
            "status": step.status.value,
            "attempts": step.attempts,
            "output": _safe_nested(step.output),
            "error_code": step.error_code,
            "error_message": step.error_message,
            "started_at": step.started_at,
            "completed_at": step.completed_at,
        }
        for step in service.repository.list_steps(job.job_id)
    ]
    payload["events"] = [
        {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "message": event.message,
            "details": _safe_nested(event.details),
            "created_at": event.created_at,
        }
        for event in service.repository.list_events(job.job_id)
    ]
    return payload


def _default_publication_checker(url: str) -> bool:
    import httpx

    try:
        response = httpx.get(url, follow_redirects=True, timeout=20.0)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


def create_app(
    service,
    *,
    max_upload_bytes: int = 100 * 1024 * 1024,
    publication_checker=None,
) -> FastAPI:
    app = FastAPI(title="Paper Intake Control Desk", docs_url=None, redoc_url=None)
    app.state.service = service
    app.state.max_upload_bytes = max_upload_bytes
    app.state.publication_checker = publication_checker or _default_publication_checker
    app.mount("/static", StaticFiles(directory=PACKAGE_ROOT / "static"), name="static")

    @app.exception_handler(ServiceError)
    async def handle_service_error(_request, exc: ServiceError):
        status = 404 if exc.code == "job_not_found" else 409
        return JSONResponse(
            status_code=status,
            content={"error_code": exc.code, "message": str(exc)},
        )

    @app.exception_handler(InputValidationError)
    async def handle_input_error(_request, exc: InputValidationError):
        status = 413 if exc.code == "file_too_large" else 400
        return JSONResponse(
            status_code=status,
            content={"error_code": exc.code, "message": str(exc)},
        )

    @app.get("/", response_class=HTMLResponse)
    async def homepage():
        return (PACKAGE_ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    @app.post("/api/jobs/url", status_code=202)
    async def submit_url(payload: UrlSubmission):
        return _serialize_job(service.submit_url(payload.url, title=payload.title))

    @app.post("/api/jobs/upload", status_code=202)
    async def submit_upload(
        file: UploadFile = File(...),
        paper_url: str = Form(""),
        title: str = Form(""),
    ):
        content = await file.read(max_upload_bytes + 1)
        if len(content) > max_upload_bytes:
            raise InputValidationError(
                "file_too_large",
                f"PDF exceeds the {max_upload_bytes} bytes upload limit.",
            )
        job = service.submit_upload(
            file.filename or "source.pdf",
            content,
            paper_url=paper_url,
            title=title,
        )
        return _serialize_job(job)

    @app.get("/api/jobs")
    async def list_jobs():
        return [_serialize_job(job) for job in service.repository.list_jobs()]

    @app.get("/api/jobs/{job_id}")
    async def get_job(job_id: str):
        job = service.repository.get_job(job_id)
        if job is None:
            raise ServiceError("job_not_found", f"Unknown job: {job_id}")
        return _serialize_detail(service, job)

    @app.post("/api/jobs/{job_id}/retry")
    async def retry_job(job_id: str, payload: RetrySubmission | None = None):
        restart_from = payload.restart_from if payload else None
        return _serialize_job(service.retry_processing(job_id, restart_from=restart_from))

    @app.post("/api/jobs/{job_id}/approve")
    async def approve_job(job_id: str):
        return _serialize_job(service.approve(job_id))

    @app.post("/api/jobs/{job_id}/cancel")
    async def cancel_job(job_id: str):
        return _serialize_job(service.cancel(job_id))

    @app.post("/api/jobs/{job_id}/retry-deployment")
    async def retry_deployment(job_id: str):
        return _serialize_job(service.retry_deployment(job_id))

    @app.post("/api/jobs/{job_id}/restore-notion")
    async def restore_notion(job_id: str):
        return _serialize_job(service.restore_notion(job_id))

    @app.post("/api/jobs/{job_id}/verify-publication")
    async def verify_publication(job_id: str):
        return _serialize_job(
            service.verify_publication(job_id, checker=app.state.publication_checker)
        )

    return app


def build_default_app() -> FastAPI:
    """Build the local application without performing external requests at startup."""
    import os

    from dotenv import load_dotenv

    from .adapters import DeepSeekArticleAdapter, GitHubPagesGateway, MinerUAdapter, NotionGateway
    from .inputs import PaperInputStore
    from .pipeline import PaperPipeline
    from .repository import JobRepository
    from .service import PaperIntakeService

    project_root = PACKAGE_ROOT.parent
    load_dotenv(project_root / ".env", override=False)

    required = {
        "MINERU_API_KEY": os.getenv("MINERU_API_KEY", ""),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN", ""),
        "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID", ""),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing local configuration: " + ", ".join(missing) + ". Add them to .env."
        )

    runtime_root = project_root / "data" / "paper_intake"
    workflow_root = project_root / "data" / "workflow_state" / "paper_intake"
    max_bytes = int(os.getenv("PAPER_INTAKE_MAX_FILE_MB", "100")) * 1024 * 1024
    repository = JobRepository(runtime_root / "jobs.sqlite3")
    input_store = PaperInputStore(runtime_root / "inbox", max_file_bytes=max_bytes)
    notion = NotionGateway(required["NOTION_TOKEN"], required["NOTION_DATABASE_ID"])
    github = GitHubPagesGateway(
        token=os.getenv("GITHUB_TOKEN", ""),
        repository=os.getenv(
            "GITHUB_REPOSITORY", "enkidulove90-lang/enkidulove90-lang.github.io"
        ),
        workflow=os.getenv("GITHUB_WORKFLOW", "publish.yml"),
        ref=os.getenv("GITHUB_REF", "source"),
    )
    pipeline = PaperPipeline(
        repository=repository,
        input_store=input_store,
        mineru=MinerUAdapter(),
        deepseek=DeepSeekArticleAdapter(
            api_key=required["DEEPSEEK_API_KEY"],
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        ),
        notion=notion,
        workflow_root=workflow_root,
    )
    service = PaperIntakeService(
        repository=repository,
        input_store=input_store,
        pipeline=pipeline,
        notion=notion,
        github=github,
        workflow_root=workflow_root,
        site_url=os.getenv(
            "PAPER_INTAKE_SITE_URL", "https://enkidulove90-lang.github.io"
        ),
    )
    return create_app(service, max_upload_bytes=max_bytes)
