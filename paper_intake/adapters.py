from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .article import (
    ArticlePayloadError,
    GenerationEnvelope,
    generation_output_schema,
    parse_generation_envelope,
)
from .retry import request_with_retry
from .trace_context import current_trace_id


NOTION_API = "https://api.notion.com/v1"
NOTION_API_VERSION = "2026-03-11"
GITHUB_API = "https://api.github.com"
_IMAGE_LINE = re.compile(r"^!\[([^]]*)\]\(([^)]+)\)$")


class ExternalServiceError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        service: str = "",
        http_status: int | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.service = service
        self.http_status = http_status
        self.retryable = retryable


@dataclass(frozen=True, slots=True)
class ParseResult:
    markdown_path: Path
    image_paths: tuple[Path, ...]
    text: str


@dataclass(frozen=True, slots=True)
class NotionDraft:
    arxiv_id: str
    title: str
    slug: str
    summary: str
    markdown: str
    figure_paths: tuple[Path, ...] = ()
    categories: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    year: str = ""
    venue_type: str = ""
    venue_name: str = ""


@dataclass(frozen=True, slots=True)
class NotionPage:
    page_id: str
    url: str
    status: str
    before_markdown: str = ""


@dataclass(frozen=True, slots=True)
class DispatchResult:
    triggered: bool
    run_id: str = ""
    message: str = ""


class MinerUAdapter:
    def __init__(self, *, parser=None):
        if parser is None:
            from skills.pdf_parser import PDFParser

            parser = PDFParser()
        self.parser = parser

    def parse(self, pdf_path: str | Path, *, canonical_id: str, title: str = "") -> ParseResult:
        path = Path(pdf_path)
        try:
            result = request_with_retry(lambda: self.parser.execute(
                pdf_path=str(path), arxiv_id=canonical_id, title=title,
                trace_id=current_trace_id(),
            ))
        except Exception as exc:
            raise ExternalServiceError("mineru_request_failed", "MinerU request failed.") from exc
        if result.get("error"):
            raise ExternalServiceError("mineru_parse_failed", str(result["error"])[:500])
        markdown_path = Path(result.get("markdown_path") or "")
        if not markdown_path.is_file():
            raise ExternalServiceError("mineru_output_missing", "MinerU did not return Markdown.")
        image_dir = markdown_path.parent / "images"
        allowed = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        images = (
            tuple(sorted(p for p in image_dir.rglob("*") if p.is_file() and p.suffix.lower() in allowed))
            if image_dir.is_dir()
            else ()
        )
        text = markdown_path.read_text(encoding="utf-8", errors="replace")
        return ParseResult(markdown_path=markdown_path, image_paths=images, text=text)


DEEPSEEK_ARTICLE_SYSTEM_PROMPT = (
    "你是推荐系统论文编辑。只输出符合给定 Schema 的 JSON；"
    "不得虚构实验数字、链接或图片路径。"
)


class DeepSeekArticleAdapter:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        client=None,
        preflight_transport=None,
    ):
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url=base_url)
        self.client = client
        self.model = model
        self.preflight_transport = preflight_transport or _RequestsTransport(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def preflight(self) -> dict[str, Any]:
        """Verify credential reachability and usable account balance."""
        try:
            payload = self.preflight_transport.request("GET", "/user/balance")
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in {401, 403}:
                code, retryable = "deepseek_auth_rejected", False
            elif status == 402:
                code, retryable = "deepseek_balance_low", False
            elif status == 429:
                code, retryable = "deepseek_rate_limited", True
            else:
                code, retryable = "deepseek_unreachable", True
            raise ExternalServiceError(
                code,
                "DeepSeek preflight failed.",
                service="deepseek",
                http_status=status,
                retryable=retryable,
            ) from exc
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(
                "deepseek_unreachable",
                "DeepSeek preflight failed.",
                service="deepseek",
                retryable=True,
            ) from exc
        if payload.get("is_available") is not True:
            raise ExternalServiceError(
                "deepseek_balance_low",
                "DeepSeek balance is unavailable.",
                service="deepseek",
            )
        return payload

    def generate(
        self,
        *,
        markdown: str,
        metadata: dict[str, Any],
        figures: list[dict[str, str]],
        reference_candidates: list[dict[str, Any]] | None = None,
        failure_path: str | Path | None = None,
    ) -> GenerationEnvelope:
        trimmed = markdown[:80000]
        safe_candidates = [
            {
                "ref_id": str(item.get("ref_id", "")),
                "title": str(item.get("title", "")),
                "year": item.get("year"),
            }
            for item in (reference_candidates or [])
        ]
        prompt = {
            "metadata": metadata,
            "available_figures": figures,
            "paper_markdown": trimmed,
            "requirements": {
                "language": "Chinese",
                "sections": ["introduction", "method", "experiments", "conclusion", "references"],
                "figure_rule": "Use only available figure paths and write an original Chinese explanation.",
                "output_schema": generation_output_schema(),
                "formula_format": (
                    "Use $...$ for inline formulas and $$...$$ for block formulas."
                ),
                "reference_selection": {
                    "instruction": (
                        "Choose exactly two eligible ref_id values most relevant to the article "
                        "and provide one short reason for each. Do not create identifiers or links."
                    ),
                    "candidates": safe_candidates,
                },
            },
        }
        try:
            response = request_with_retry(lambda: self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": DEEPSEEK_ARTICLE_SYSTEM_PROMPT,
                    },
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
                extra_headers={"X-Trace-Id": current_trace_id()} if current_trace_id() else None,
            ))
            raw = response.choices[0].message.content or ""
            try:
                return parse_generation_envelope(
                    raw,
                    {item["ref_id"] for item in safe_candidates if item["ref_id"]},
                )
            except ArticlePayloadError as exc:
                if failure_path:
                    self._write_failure(Path(failure_path), raw, exc.details)
                raise
        except ExternalServiceError:
            raise
        except Exception as exc:
            if isinstance(exc, (ValueError, json.JSONDecodeError)):
                code = "deepseek_invalid_output"
                message = str(exc)
            else:
                code = "deepseek_request_failed"
                message = "DeepSeek request failed."
            raise ExternalServiceError(code, message) from exc

    @staticmethod
    def _write_failure(path: Path, raw: str, details: list[dict[str, str]]) -> None:
        redacted = raw
        for name in (
            "DEEPSEEK_API_KEY", "NOTION_TOKEN", "GITHUB_TOKEN",
            "PAPER_INTAKE_WORKER_TOKEN", "MINERU_API_KEY",
        ):
            value = os.getenv(name, "")
            if value:
                redacted = redacted.replace(value, "[REDACTED]")
        redacted = re.sub(
            r"(?i)(?:bearer\s+)?(?:sk[-_]|ntn_|ghp_|github_pat_)[A-Za-z0-9_-]{8,}",
            "[REDACTED]",
            redacted,
        )
        limit = 256 * 1024
        payload = {
            "response_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "response_chars": len(raw),
            "truncated": len(redacted) > limit,
            "response": redacted[:limit],
            "validation_errors": details,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        temporary.replace(path)


class _RequestsTransport:
    def __init__(self, *, base_url: str, headers: dict[str, str]):
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()
        self.session.trust_env = False

    def request(self, method: str, path: str, **kwargs):
        headers = dict(self.headers)
        if current_trace_id():
            headers["X-Trace-Id"] = current_trace_id()
        if "files" not in kwargs:
            headers.setdefault("Content-Type", "application/json")
        response = self.session.request(
            method,
            self.base_url + path,
            headers=headers,
            timeout=120,
            **kwargs,
        )
        response.raise_for_status()
        return response.json() if response.content else {}


class NotionGateway:
    def __init__(
        self,
        token: str,
        database_id: str,
        *,
        transport=None,
        max_retries: int = 4,
    ):
        if not token or not database_id:
            raise ValueError("Notion token and database ID are required")
        self.database_id = database_id
        self.transport = transport or _RequestsTransport(
            base_url=NOTION_API,
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": NOTION_API_VERSION,
            },
        )
        self.max_retries = max_retries
        self._source_id = ""
        self._property_names: set[str] | None = None
        self._upload_cache: dict[str, str] = {}

    def _request(self, method: str, path: str, **kwargs):
        positions: list[tuple[Any, int]] = []
        for value in (kwargs.get("files") or {}).values():
            payload = value[1] if isinstance(value, tuple) else value
            if hasattr(payload, "tell") and hasattr(payload, "seek"):
                positions.append((payload, payload.tell()))
        for attempt in range(self.max_retries + 1):
            for handle, position in positions:
                handle.seek(position)
            try:
                return self.transport.request(method, path, **kwargs)
            except requests.RequestException as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                transient = status is None or status == 429 or (status is not None and status >= 500)
                if not transient or attempt >= self.max_retries:
                    raise ExternalServiceError("notion_request_failed", "Notion request failed.") from exc
                time.sleep(min(2**attempt, 8))
            except ExternalServiceError:
                raise
            except Exception as exc:
                raise ExternalServiceError("notion_request_failed", "Notion request failed.") from exc
        raise ExternalServiceError("notion_request_failed", "Notion request failed.")

    def _data_source(self) -> str:
        if self._source_id:
            return self._source_id
        database = self._request("GET", f"/databases/{self.database_id}")
        sources = database.get("data_sources") or []
        self._source_id = sources[0]["id"] if sources else self.database_id
        if sources:
            source = self._request("GET", f"/data_sources/{self._source_id}")
            self._property_names = set((source.get("properties") or {}).keys())
        return self._source_id

    def preflight_schema(self) -> set[str]:
        """Fail before mutation when the publication schema is incompatible."""
        self._data_source()
        names = self._property_names or set()
        # Summary and arXiv ID improve discovery, but existing databases may
        # omit them; slug remains the stable idempotency fallback.
        required = {"title", "status", "type", "slug"}
        missing = sorted(required - names)
        if missing:
            raise ExternalServiceError(
                "notion_schema_mismatch",
                "Notion database is missing required properties: " + ", ".join(missing),
                service="notion",
            )
        return names

    @staticmethod
    def _rich_text(value: str) -> list[dict]:
        return [{"type": "text", "text": {"content": value[:2000]}}] if value else []

    def _properties(
        self,
        *,
        title: str,
        slug: str,
        summary: str,
        arxiv_id: str,
        status: str,
        categories: tuple[str, ...] = (),
        tags: tuple[str, ...] = (),
        year: str = "",
        venue_type: str = "",
        venue_name: str = "",
    ) -> dict:
        properties = {
            "title": {"title": self._rich_text(title)},
            "status": {"select": {"name": status}},
            "type": {"select": {"name": "Post"}},
            "slug": {"rich_text": self._rich_text(slug)},
            "summary": {"rich_text": self._rich_text(summary)},
            "arxiv_id": {"rich_text": self._rich_text(arxiv_id)},
            "category": {
                "select": {"name": " / ".join(category for category in categories if category)}
            },
            "tags": {
                "multi_select": [{"name": tag[:100]} for tag in tags if tag]
            },
            "year": {"select": {"name": year}},
            "venue_type": {"select": {"name": venue_type}},
            "venue_name": {"rich_text": self._rich_text(venue_name)},
        }
        properties = {
            key: value
            for key, value in properties.items()
            if not (
                (key in {"category", "year", "venue_type"} and not value["select"]["name"])
                or (key == "tags" and not value["multi_select"])
                or (key == "venue_name" and not value["rich_text"])
            )
        }
        if self._property_names is not None:
            properties = {key: value for key, value in properties.items() if key in self._property_names}
        return properties

    def _find_by_arxiv(self, arxiv_id: str) -> dict | None:
        source_id = self._data_source()
        property_name = "arxiv_id"
        property_type = "rich_text"
        property_value = arxiv_id
        if self._property_names is not None and property_name not in self._property_names:
            if "slug" not in self._property_names:
                return None
            property_name = "slug"
            property_value = f"paper-{arxiv_id}"
        result = self._request(
            "POST",
            f"/data_sources/{source_id}/query",
            json={
                "filter": {
                    "property": property_name,
                    property_type: {"equals": property_value},
                },
                "page_size": 2,
            },
        )
        pages = result.get("results") or []
        return pages[0] if pages else None

    def _create_page(self, properties: dict) -> dict:
        return self._request(
            "POST",
            "/pages",
            json={
                "parent": {"type": "data_source_id", "data_source_id": self._data_source()},
                "properties": properties,
            },
        )

    def _update_page(self, page_id: str, properties: dict) -> None:
        self._request("PATCH", f"/pages/{page_id}", json={"properties": properties})

    def update_metadata_properties(self, page_id: str, metadata: dict) -> None:
        """Update verified bibliographic properties without reading or replacing page blocks."""
        self._data_source()
        canonical_id = str(metadata.get("canonical_id") or metadata.get("arxiv_id") or "").strip()
        published = str(metadata.get("published") or "").strip()
        authors = metadata.get("authors") or []
        if not isinstance(authors, (list, tuple)):
            authors = []
        properties = {
            "title": {"title": self._rich_text(str(metadata.get("title") or "").strip())},
            "arxiv_id": {"rich_text": self._rich_text(canonical_id)},
            "year": {"select": {"name": published[:4] if len(published) >= 4 else ""}},
            "authors": {
                "rich_text": self._rich_text(", ".join(str(author).strip() for author in authors if str(author).strip()))
            },
            "published": {"rich_text": self._rich_text(published)},
            "updated": {"rich_text": self._rich_text(str(metadata.get("updated") or "").strip())},
        }
        properties = {
            key: value
            for key, value in properties.items()
            if key in (self._property_names or set())
            and not (
                (key == "year" and not value["select"]["name"])
                or (key != "year" and not next(iter(value.values())))
            )
        }
        if not properties:
            raise ExternalServiceError(
                "notion_schema_mismatch",
                "Notion database has no supported metadata properties.",
                service="notion",
            )
        self._update_page(page_id, properties)

    def _snapshot_markdown(self, page_id: str) -> str:
        result = self._request("GET", f"/pages/{page_id}/markdown")
        return str(result.get("markdown") or result.get("content") or "")

    def _clear_children(self, page_id: str) -> None:
        cursor = None
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            result = self._request("GET", f"/blocks/{page_id}/children", params=params)
            for block in result.get("results") or []:
                self._request("DELETE", f"/blocks/{block['id']}")
            if not result.get("has_more"):
                return
            cursor = result.get("next_cursor")

    def _upload_file(self, path: Path) -> str:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in self._upload_cache:
            return self._upload_cache[digest]
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        created = self._request(
            "POST",
            "/file_uploads",
            json={"mode": "single_part", "filename": path.name, "content_type": content_type},
        )
        upload_id = created["id"]
        with path.open("rb") as handle:
            self._request(
                "POST",
                f"/file_uploads/{upload_id}/send",
                files={"file": (path.name, handle, content_type)},
            )
        self._upload_cache[digest] = upload_id
        return upload_id

    def _blocks(self, markdown: str, uploads: dict[str, str]) -> list[dict]:
        blocks: list[dict] = []
        in_frontmatter = False
        for raw_line in markdown.splitlines():
            line = raw_line.strip()
            if line == "---" and not blocks:
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter or not line:
                continue
            image = _IMAGE_LINE.fullmatch(line)
            if image and Path(image.group(2)).name in uploads:
                blocks.append(
                    {
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "file_upload",
                            "file_upload": {"id": uploads[Path(image.group(2)).name]},
                            "caption": self._rich_text(image.group(1)),
                        },
                    }
                )
                continue
            block_type = "paragraph"
            text = line
            for prefix, candidate in (("### ", "heading_3"), ("## ", "heading_2"), ("# ", "heading_1")):
                if line.startswith(prefix):
                    block_type = candidate
                    text = line[len(prefix) :]
                    break
            blocks.append(
                {
                    "object": "block",
                    "type": block_type,
                    block_type: {"rich_text": self._rich_text(text)},
                }
            )
        return blocks

    def upsert_draft(self, draft: NotionDraft) -> NotionPage:
        self.preflight_schema()
        existing = self._find_by_arxiv(draft.arxiv_id)
        properties = self._properties(
            title=draft.title,
            slug=draft.slug,
            summary=draft.summary,
            arxiv_id=draft.arxiv_id,
            status="Draft",
            categories=draft.categories,
            tags=draft.tags,
            year=draft.year,
            venue_type=draft.venue_type,
            venue_name=draft.venue_name,
        )
        before = ""
        if existing:
            page_id = existing["id"]
            page_url = existing.get("url", "")
            before = self._snapshot_markdown(page_id)
            self._update_page(page_id, properties)
        else:
            created = self._create_page(properties)
            page_id = created["id"]
            page_url = created.get("url", "")
        uploads = {path.name: self._upload_file(path) for path in draft.figure_paths}
        blocks = self._blocks(draft.markdown, uploads)
        self._clear_children(page_id)
        for index in range(0, len(blocks), 100):
            self._request(
                "PATCH",
                f"/blocks/{page_id}/children",
                json={"children": blocks[index : index + 100]},
            )
        return NotionPage(page_id, page_url, "Draft", before)

    def upsert_published(self, draft: NotionDraft) -> NotionPage:
        self.preflight_schema()
        existing = self._find_by_arxiv(draft.arxiv_id)
        properties = self._properties(
            title=draft.title,
            slug=draft.slug,
            summary=draft.summary,
            arxiv_id=draft.arxiv_id,
            status="Published",
            categories=draft.categories,
            tags=draft.tags,
            year=draft.year,
            venue_type=draft.venue_type,
            venue_name=draft.venue_name,
        )
        before = ""
        if existing:
            page_id = existing["id"]
            page_url = existing.get("url", "")
            before = self._snapshot_markdown(page_id)
            self._update_page(page_id, properties)
        else:
            created = self._create_page(properties)
            page_id = created["id"]
            page_url = created.get("url", "")
        uploads = {path.name: self._upload_file(path) for path in draft.figure_paths}
        blocks = self._blocks(draft.markdown, uploads)
        self._clear_children(page_id)
        for index in range(0, len(blocks), 100):
            self._request(
                "PATCH",
                f"/blocks/{page_id}/children",
                json={"children": blocks[index : index + 100]},
            )
        return NotionPage(page_id, page_url, "Published", before)

    def publish(self, page_id: str, *, title: str, slug: str, arxiv_id: str) -> NotionPage:
        properties = self._properties(
            title=title,
            slug=slug,
            summary="",
            arxiv_id=arxiv_id,
            status="Published",
        )
        self._update_page(page_id, properties)
        return NotionPage(page_id, "", "Published")

    def restore_draft(
        self,
        page_id: str,
        *,
        markdown: str,
        title: str,
        slug: str,
        arxiv_id: str,
    ) -> NotionPage:
        properties = self._properties(
            title=title,
            slug=slug,
            summary="",
            arxiv_id=arxiv_id,
            status="Draft",
        )
        self._update_page(page_id, properties)
        self._clear_children(page_id)
        blocks = self._blocks(markdown, {})
        for index in range(0, len(blocks), 100):
            self._request(
                "PATCH",
                f"/blocks/{page_id}/children",
                json={"children": blocks[index : index + 100]},
            )
        return NotionPage(page_id, "", "Draft")

class GitHubPagesGateway:
    def __init__(
        self,
        *,
        token: str,
        repository: str,
        workflow: str = "publish.yml",
        ref: str = "source",
        transport=None,
    ):
        self.configured = bool(token)
        self.repository = repository
        self.workflow = workflow
        self.ref = ref
        self.transport = transport or (
            _RequestsTransport(
                base_url=GITHUB_API,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2026-03-10",
                },
            )
            if token
            else None
        )

    def dispatch(self) -> DispatchResult:
        if not self.configured:
            return DispatchResult(
                False,
                message="GitHub token is not configured; the scheduled build remains available.",
            )
        try:
            result = self.transport.request(
                "POST",
                f"/repos/{self.repository}/actions/workflows/{self.workflow}/dispatches",
                json={"ref": self.ref},
            )
        except Exception as exc:
            raise ExternalServiceError(
                "github_dispatch_failed",
                "GitHub workflow dispatch failed.",
            ) from exc
        return DispatchResult(True, run_id=str((result or {}).get("run_id", "")))
