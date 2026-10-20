from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .article import PaperArticle, parse_article_payload


NOTION_API = "https://api.notion.com/v1"
NOTION_API_VERSION = "2026-03-11"
GITHUB_API = "https://api.github.com"
_IMAGE_LINE = re.compile(r"^!\[([^]]*)\]\(([^)]+)\)$")


class ExternalServiceError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


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
            result = self.parser.execute(
                pdf_path=str(path),
                arxiv_id=canonical_id,
                title=title,
            )
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


class DeepSeekArticleAdapter:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        client=None,
    ):
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url=base_url)
        self.client = client
        self.model = model

    def generate(
        self,
        *,
        markdown: str,
        metadata: dict[str, Any],
        figures: list[dict[str, str]],
    ) -> PaperArticle:
        trimmed = markdown[:80000]
        prompt = {
            "metadata": metadata,
            "available_figures": figures,
            "paper_markdown": trimmed,
            "requirements": {
                "language": "Chinese",
                "sections": ["introduction", "method", "experiments", "conclusion", "references"],
                "figure_rule": "Use only available figure paths and write an original Chinese explanation.",
                "output_schema": PaperArticle.model_json_schema(),
            },
        }
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是推荐系统论文编辑。只输出符合给定 Schema 的 JSON；"
                            "不得虚构实验数字、链接或图片路径。"
                        ),
                    },
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
            )
            raw = response.choices[0].message.content or ""
            return parse_article_payload(raw)
        except ExternalServiceError:
            raise
        except Exception as exc:
            if isinstance(exc, (ValueError, json.JSONDecodeError)):
                code = "deepseek_invalid_output"
                message = "DeepSeek returned an invalid article payload."
            else:
                code = "deepseek_request_failed"
                message = "DeepSeek request failed."
            raise ExternalServiceError(code, message) from exc


class _RequestsTransport:
    def __init__(self, *, base_url: str, headers: dict[str, str]):
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs):
        headers = dict(self.headers)
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
    ) -> dict:
        properties = {
            "title": {"title": self._rich_text(title)},
            "status": {"select": {"name": status}},
            "type": {"select": {"name": "Post"}},
            "slug": {"rich_text": self._rich_text(slug)},
            "summary": {"rich_text": self._rich_text(summary)},
            "arxiv_id": {"rich_text": self._rich_text(arxiv_id)},
        }
        if self._property_names is not None:
            properties = {key: value for key, value in properties.items() if key in self._property_names}
        return properties

    def _find_by_arxiv(self, arxiv_id: str) -> dict | None:
        result = self._request(
            "POST",
            f"/data_sources/{self._data_source()}/query",
            json={
                "filter": {"property": "arxiv_id", "rich_text": {"equals": arxiv_id}},
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
        existing = self._find_by_arxiv(draft.arxiv_id)
        properties = self._properties(
            title=draft.title,
            slug=draft.slug,
            summary=draft.summary,
            arxiv_id=draft.arxiv_id,
            status="Draft",
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
        existing = self._find_by_arxiv(draft.arxiv_id)
        properties = self._properties(
            title=draft.title,
            slug=draft.slug,
            summary=draft.summary,
            arxiv_id=draft.arxiv_id,
            status="Published",
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
