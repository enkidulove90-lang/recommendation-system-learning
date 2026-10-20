from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Callable

from .adapters import ExternalServiceError, NotionDraft
from .article import (
    PaperArticle,
    normalize_classification,
    render_article_markdown,
    validate_article,
)
from .inputs import InputValidationError, PaperInputStore, canonicalize_url, sha256_file
from .models import JobRecord, JobStatus, StepName, StepStatus
from .repository import JobRepository


class PipelineFailure(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class PaperPipeline:
    """Checkpointed single-paper pipeline publishing only after quality success."""

    PROCESSING_STEPS = (
        StepName.VALIDATE_INPUT,
        StepName.RESOLVE_METADATA,
        StepName.DOWNLOAD_PDF,
        StepName.MINERU_PARSE,
        StepName.DEEPSEEK_GENERATE,
        StepName.CLASSIFY,
        StepName.QUALITY_CHECK,
        StepName.WRITE_NOTION_PUBLISHED,
    )

    def __init__(
        self,
        *,
        repository: JobRepository,
        input_store: PaperInputStore,
        mineru,
        deepseek,
        notion,
        workflow_root: str | Path,
        metadata_resolver: Callable[[str, str], dict[str, Any]] | None = None,
    ):
        self.repository = repository
        self.input_store = input_store
        self.mineru = mineru
        self.deepseek = deepseek
        self.notion = notion
        self.workflow_root = Path(workflow_root)
        self.metadata_resolver = metadata_resolver or self._fallback_metadata

    def run(self, job_id: str) -> JobRecord:
        try:
            for step_name in self.PROCESSING_STEPS:
                if self._job(job_id).status == JobStatus.CANCELLED:
                    break
                output = self._run_step(job_id, step_name)
                if step_name == StepName.QUALITY_CHECK and output.get("issue_codes"):
                    self.repository.update_job(
                        job_id,
                        status=JobStatus.FAILED,
                        error_code="quality_gate_failed",
                        error_message="Article quality checks failed.",
                    )
                    break
            else:
                self.repository.update_job(
                    job_id,
                    status=JobStatus.PUBLISHING,
                    current_step="",
                    error_code="",
                    error_message="",
                )
        except Exception:
            # _run_step persists the safe failure state. Returning the job keeps the
            # web worker alive and lets the user retry from the same checkpoint.
            pass
        job = self.repository.get_job(job_id)
        if job is None:
            raise KeyError(f"Unknown job: {job_id}")
        return job

    def retry(self, job_id: str) -> JobRecord:
        job = self.repository.get_job(job_id)
        if job is None:
            raise KeyError(f"Unknown job: {job_id}")
        if job.status not in {JobStatus.FAILED, JobStatus.BLOCKED}:
            raise ValueError(f"Job {job_id} is not retryable from {job.status.value}")
        return self.run(job_id)

    def _run_step(self, job_id: str, step_name: StepName) -> dict[str, Any]:
        existing = self.repository.get_step(job_id, step_name)
        if existing and existing.status == StepStatus.SUCCEEDED:
            return existing.output
        handler = getattr(self, f"_step_{step_name.value}")
        self.repository.start_step(job_id, step_name)
        try:
            output = handler(job_id) or {}
        except Exception as exc:
            code, message = self._safe_error(exc)
            self.repository.fail_step(
                job_id,
                step_name,
                error_code=code,
                error_message=message,
            )
            raise
        self.repository.complete_step(job_id, step_name, output=output)
        return output

    def _bundle(self, job_id: str) -> Path:
        path = self.workflow_root / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _job(self, job_id: str) -> JobRecord:
        job = self.repository.get_job(job_id)
        if job is None:
            raise KeyError(f"Unknown job: {job_id}")
        return job

    def _step_validate_input(self, job_id: str) -> dict[str, Any]:
        job = self._job(job_id)
        canonical_id = job.canonical_id
        source_url = job.source_url
        if job.source_type == "url":
            source = canonicalize_url(job.source_url)
            canonical_id = source.canonical_id
            source_url = source.normalized_url
            duplicate = self.repository.find_duplicate(
                canonical_id=canonical_id,
                source_url=source_url,
                exclude_job_id=job_id,
            )
            if duplicate:
                raise PipelineFailure("duplicate_paper", f"Paper already exists in job {duplicate.job_id}.")
            self.repository.update_job(
                job_id,
                canonical_id=canonical_id,
                source_url=source_url,
            )
            return {"canonical_id": canonical_id, "source_url": source_url}

        pdf_path = Path(job.upload_path)
        if not pdf_path.is_file():
            raise InputValidationError("pdf_missing", "Uploaded PDF no longer exists.")
        digest = sha256_file(pdf_path)
        duplicate = self.repository.find_duplicate(
            canonical_id=canonical_id,
            source_sha256=digest,
            exclude_job_id=job_id,
        )
        if duplicate:
            raise PipelineFailure("duplicate_paper", f"Paper already exists in job {duplicate.job_id}.")
        canonical_id = canonical_id or f"pdf-{digest[:12]}"
        self.repository.update_job(
            job_id,
            canonical_id=canonical_id,
            source_sha256=digest,
        )
        return {
            "canonical_id": canonical_id,
            "pdf_path": str(pdf_path),
            "sha256": digest,
        }

    def _step_resolve_metadata(self, job_id: str) -> dict[str, Any]:
        job = self._job(job_id)
        metadata = self.metadata_resolver(job.canonical_id, job.source_url) or {}
        metadata.setdefault("canonical_id", job.canonical_id)
        metadata.setdefault("title", job.title or Path(job.upload_path or "paper.pdf").stem)
        metadata.setdefault("authors", [])
        metadata.setdefault("paper_url", job.source_url or f"local://{job.canonical_id}")
        metadata_path = self._bundle(job_id) / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        self.repository.update_job(job_id, title=str(metadata["title"]))
        return {"metadata_path": str(metadata_path)}

    def _step_download_pdf(self, job_id: str) -> dict[str, Any]:
        job = self._job(job_id)
        if job.source_type == "url":
            saved = self.input_store.download_url(job_id, job.source_url)
            pdf_path = saved.path
            digest = saved.sha256
        else:
            pdf_path = Path(job.upload_path)
            digest = job.source_sha256 or sha256_file(pdf_path)
        canonical_id = job.canonical_id or f"pdf-{digest[:12]}"
        duplicate = self.repository.find_duplicate(
            canonical_id=canonical_id,
            source_sha256=digest,
            source_url=job.source_url,
            exclude_job_id=job_id,
        )
        if duplicate:
            raise PipelineFailure("duplicate_paper", f"Paper already exists in job {duplicate.job_id}.")
        self.repository.update_job(
            job_id,
            upload_path=str(pdf_path),
            source_sha256=digest,
            canonical_id=canonical_id,
        )
        metadata_path = self._bundle(job_id) / "metadata.json"
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["canonical_id"] = canonical_id
            if str(metadata.get("paper_url", "")).startswith("local://") and job.source_url:
                metadata["paper_url"] = job.source_url
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"pdf_path": str(pdf_path), "sha256": digest, "canonical_id": canonical_id}

    def _step_mineru_parse(self, job_id: str) -> dict[str, Any]:
        job = self._job(job_id)
        result = self.mineru.parse(
            job.upload_path,
            canonical_id=job.canonical_id,
            title=job.title,
        )
        image_dir = self._bundle(job_id) / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        figures: list[dict[str, str]] = []
        used_names: set[str] = set()
        for index, source in enumerate(result.image_paths, 1):
            name = source.name
            if name in used_names:
                name = f"{source.stem}-{index}{source.suffix}"
            used_names.add(name)
            destination = image_dir / name
            shutil.copy2(source, destination)
            figures.append(
                {
                    "path": destination.relative_to(self._bundle(job_id)).as_posix(),
                    "sha256": sha256_file(destination),
                }
            )
        return {
            "markdown_path": str(result.markdown_path),
            "figures": figures,
        }

    def _step_deepseek_generate(self, job_id: str) -> dict[str, Any]:
        bundle = self._bundle(job_id)
        metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
        parse_step = self.repository.get_step(job_id, StepName.MINERU_PARSE)
        if parse_step is None or parse_step.status != StepStatus.SUCCEEDED:
            raise PipelineFailure("mineru_output_missing", "MinerU output is not available.")
        markdown = Path(parse_step.output["markdown_path"]).read_text(
            encoding="utf-8", errors="replace"
        )
        article = self.deepseek.generate(
            markdown=markdown,
            metadata=metadata,
            figures=list(parse_step.output.get("figures") or []),
        )
        article_path = bundle / "article.json"
        article_path.write_text(article.model_dump_json(indent=2), encoding="utf-8")
        return {"article_path": str(article_path)}

    def _load_article(self, job_id: str) -> PaperArticle:
        path = self._bundle(job_id) / "article.json"
        if not path.is_file():
            raise PipelineFailure("article_missing", "Generated article JSON is missing.")
        return PaperArticle.model_validate_json(path.read_text(encoding="utf-8"))

    def _step_classify(self, job_id: str) -> dict[str, Any]:
        article = self._load_article(job_id)
        normalized, warnings = normalize_classification(article.classification)
        article = article.model_copy(update={"classification": normalized})
        article_path = self._bundle(job_id) / "article.json"
        article_path.write_text(article.model_dump_json(indent=2), encoding="utf-8")
        return {"article_path": str(article_path), "warnings": warnings}

    def _step_quality_check(self, job_id: str) -> dict[str, Any]:
        bundle = self._bundle(job_id)
        article = self._load_article(job_id)
        result = validate_article(article, artifact_root=bundle)
        article_md = bundle / "article.md"
        article_md.write_text(render_article_markdown(article), encoding="utf-8")
        return {
            "publishable": result.publishable,
            "issue_codes": result.issue_codes,
            "issues": [issue.message for issue in result.issues],
            "article_path": str(article_md),
        }

    def _step_write_notion_published(self, job_id: str) -> dict[str, Any]:
        bundle = self._bundle(job_id)
        article = self._load_article(job_id)
        markdown = (bundle / "article.md").read_text(encoding="utf-8")
        figure_paths = tuple((bundle / figure.path).resolve() for figure in article.figures)
        page = self.notion.upsert_published(
            NotionDraft(
                arxiv_id=article.paper.canonical_id,
                title=article.paper.chinese_title or article.paper.title,
                slug=f"paper-{article.paper.canonical_id}",
                summary=article.article.introduction[:500],
                markdown=markdown,
                figure_paths=figure_paths,
            )
        )
        (bundle / "notion-before.md").write_text(page.before_markdown, encoding="utf-8")
        (bundle / "notion-after.md").write_text(markdown, encoding="utf-8")
        self.repository.update_job(
            job_id,
            notion_page_id=page.page_id,
            notion_url=page.url,
        )
        return {
            "page_id": page.page_id,
            "url": page.url,
            "status": page.status,
            "before_path": str(bundle / "notion-before.md"),
            "after_path": str(bundle / "notion-after.md"),
        }

    @staticmethod
    def _fallback_metadata(canonical_id: str, source_url: str) -> dict[str, Any]:
        return {
            "canonical_id": canonical_id,
            "title": canonical_id or "Uploaded paper",
            "authors": [],
            "paper_url": source_url or f"local://{canonical_id}",
        }

    @staticmethod
    def _safe_error(exc: Exception) -> tuple[str, str]:
        if isinstance(exc, (ExternalServiceError, InputValidationError, PipelineFailure)):
            return exc.code, str(exc)[:500]
        if isinstance(exc, FileNotFoundError):
            return "file_missing", "A required local artifact is missing."
        return "unexpected_error", "The paper pipeline failed unexpectedly."
