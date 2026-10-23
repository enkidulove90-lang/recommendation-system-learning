from __future__ import annotations

import hashlib
import inspect
import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .adapters import ExternalServiceError, NotionDraft
from .article import (
    GenerationEnvelope,
    PaperArticle,
    ReferenceChoice,
    normalize_classification,
    publication_year,
    render_article_markdown,
    validate_article,
)
from .generation_cache import GenerationCache
from .inputs import InputValidationError, PaperInputStore, canonicalize_url, sha256_file
from .models import JobRecord, JobStatus, StepName, StepStatus
from .metadata_refresh import refresh_metadata_file
from .repository import JobRepository
from .remote import LeaseLost
from .reference_candidates import (
    ReferenceCandidate,
    candidate_hash,
    extract_reference_candidates,
    source_hash,
)
from .reference_links import (
    ArxivCrossrefClients,
    PwcSnapshot,
    ResolutionResult,
    resolve_selected_references,
)


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
    ARTICLE_PROMPT_VERSION = "article-v3-plain-headings-formula-reference-selection"
    RANKING_RULE_VERSION = "latest-v1"

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
        reference_clients=None,
        pwc_snapshot: PwcSnapshot | None = None,
        generation_cache: GenerationCache | None = None,
    ):
        self.repository = repository
        self.input_store = input_store
        self.mineru = mineru
        self.deepseek = deepseek
        self.notion = notion
        self.workflow_root = Path(workflow_root)
        self.metadata_resolver = metadata_resolver or self._fallback_metadata
        self.reference_clients = reference_clients or ArxivCrossrefClients()
        self.pwc_snapshot = pwc_snapshot
        self.generation_cache = generation_cache or GenerationCache(
            self.workflow_root / ".generation-cache"
        )

    def run(
        self,
        job_id: str,
        *,
        before_step: Callable[[StepName], None] | None = None,
        on_step_completed: Callable[[StepName, dict[str, Any]], None] | None = None,
    ) -> JobRecord:
        try:
            for step_name in self.PROCESSING_STEPS:
                if self._job(job_id).status == JobStatus.CANCELLED:
                    break
                if before_step is not None:
                    before_step(step_name)
                output = self._run_step(job_id, step_name)
                if on_step_completed is not None:
                    on_step_completed(step_name, output)
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
        except LeaseLost:
            # Losing distributed ownership is not a paper-processing failure.
            # The remote ledger may already have assigned this job elsewhere.
            raise
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
        return {"metadata_path": str(metadata_path), "metadata": metadata}

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
        metadata_path = bundle / "metadata.json"
        job = self._job(job_id)
        refresh = refresh_metadata_file(
            metadata_path,
            canonical_id=job.canonical_id,
            source_url=job.source_url,
            resolver=self.metadata_resolver,
        )
        metadata = refresh.metadata
        if refresh.changed:
            self.repository.update_job(job_id, title=str(metadata["title"]))
        parse_step = self.repository.get_step(job_id, StepName.MINERU_PARSE)
        if parse_step is None or parse_step.status != StepStatus.SUCCEEDED:
            raise PipelineFailure("mineru_output_missing", "MinerU output is not available.")
        markdown = Path(parse_step.output["markdown_path"]).read_text(
            encoding="utf-8", errors="replace"
        )
        candidates = extract_reference_candidates(markdown)
        source_digest = source_hash(markdown)
        candidate_digest = candidate_hash(candidates)
        model = str(getattr(self.deepseek, "model", "unknown"))
        article = self.generation_cache.get_article(
            source_digest,
            model,
            self.ARTICLE_PROMPT_VERSION,
        )
        choices = self.generation_cache.get_ranking(
            source_digest,
            candidate_digest,
            model,
            self.ARTICLE_PROMPT_VERSION,
            self.RANKING_RULE_VERSION,
        )
        article_cache_hit = article is not None
        ranking_cache_hit = choices is not None
        ranking_diagnostic: str | None = None
        if article is None:
            generation_arguments = {
                "markdown": markdown,
                "metadata": metadata,
                "figures": list(parse_step.output.get("figures") or []),
                "failure_path": bundle / "diagnostics" / "deepseek-invalid-response.json",
            }
            parameters = inspect.signature(self.deepseek.generate).parameters.values()
            if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters) or any(
                parameter.name == "reference_candidates" for parameter in parameters
            ):
                generation_arguments["reference_candidates"] = [
                    asdict(candidate) for candidate in candidates
                ]
            generated = self.deepseek.generate(
                **generation_arguments,
            )
            if isinstance(generated, PaperArticle):
                envelope = GenerationEnvelope(
                    generated,
                    None,
                    "reference_selection_missing",
                )
            else:
                envelope = generated
            article = envelope.article
            ranking_diagnostic = envelope.ranking_diagnostic
            if choices is None:
                choices = envelope.reference_choices
            self.generation_cache.put_article(
                source_digest,
                model,
                self.ARTICLE_PROMPT_VERSION,
                article,
            )
            if choices:
                self.generation_cache.put_ranking(
                    source_digest,
                    candidate_digest,
                    model,
                    self.ARTICLE_PROMPT_VERSION,
                    self.RANKING_RULE_VERSION,
                    choices,
                )
        elif choices is None:
            ranking_diagnostic = "ranking_cache_miss"

        article_path = bundle / "article.json"
        article_path.write_text(article.model_dump_json(indent=2), encoding="utf-8")
        candidate_path = bundle / "reference-candidates.json"
        candidate_path.write_text(
            json.dumps(
                [asdict(candidate) for candidate in candidates],
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        diagnostics_dir = bundle / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)
        ranking_path = diagnostics_dir / "reference-selection.json"
        ranking_path.write_text(
            json.dumps(
                {
                    "article_cache_hit": article_cache_hit,
                    "candidate_hash": candidate_digest,
                    "choices": [choice.model_dump(mode="json") for choice in choices or []],
                    "model": model,
                    "prompt_version": self.ARTICLE_PROMPT_VERSION,
                    "ranking_cache_hit": ranking_cache_hit,
                    "ranking_diagnostic": ranking_diagnostic,
                    "rule_version": self.RANKING_RULE_VERSION,
                    "source_hash": source_digest,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return {
            "article_path": str(article_path),
            "metadata": metadata,
            "candidate_path": str(candidate_path),
            "ranking_path": str(ranking_path),
            "article_cache_hit": article_cache_hit,
            "ranking_cache_hit": ranking_cache_hit,
        }

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
        candidates: list[ReferenceCandidate] = []
        candidate_path = bundle / "reference-candidates.json"
        if candidate_path.is_file():
            try:
                candidates = [
                    ReferenceCandidate(**item)
                    for item in json.loads(candidate_path.read_text(encoding="utf-8"))
                ]
            except (OSError, TypeError, ValueError, json.JSONDecodeError):
                candidates = []
        ranking_path = bundle / "diagnostics" / "reference-selection.json"
        ranking_payload: dict[str, Any] = {}
        choices: list[ReferenceChoice] | None = None
        if ranking_path.is_file():
            try:
                ranking_payload = json.loads(ranking_path.read_text(encoding="utf-8"))
                raw_choices = ranking_payload.get("choices") or []
                choices = [ReferenceChoice.model_validate(item) for item in raw_choices] or None
            except (OSError, TypeError, ValueError, json.JSONDecodeError):
                choices = None
                ranking_payload = {"ranking_diagnostic": "reference_selection_unreadable"}
        try:
            resolved = resolve_selected_references(
                candidates,
                choices,
                self.reference_clients,
                self.pwc_snapshot,
            )
        except Exception:
            resolved = ResolutionResult(mode="omitted", references=[])
            ranking_payload["ranking_diagnostic"] = "reference_resolution_failed"
        ranking_payload.update(
            {
                "resolution_mode": resolved.mode,
                "resolved_ids": [item.candidate.ref_id for item in resolved.references],
                "verification_statuses": [
                    item.verification_status for item in resolved.references
                ],
            }
        )
        ranking_path.parent.mkdir(parents=True, exist_ok=True)
        ranking_path.write_text(
            json.dumps(ranking_payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        article_md = bundle / "article.md"
        article_md.write_text(
            render_article_markdown(article, resolved),
            encoding="utf-8",
        )
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
                categories=tuple(article.classification.categories),
                tags=tuple(article.classification.tags),
                year=publication_year(article),
                venue_type=article.classification.venue_type,
                venue_name=article.classification.venue_name,
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
