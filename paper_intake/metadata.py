from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

import requests

from .adapters import ExternalServiceError
from .inputs import canonicalize_url, parse_retry_after
from .pacing import GLOBAL_ARXIV_PACER, ArxivPacer


_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")
_ATOM = {"atom": "http://www.w3.org/2005/Atom"}
_ARXIV_NS = {"arxiv": "http://arxiv.org/schemas/atom"}
_LATEX_TITLE = re.compile(r"\\title(?:\[[^]]*\])?\{([^{}]+)\}")
_LATEX_AUTHOR = re.compile(r"\\author\{([^{}]+)\}")


class _ArxivTransport:
    def __init__(self, *, session=None, clock=None, sleep=None) -> None:
        self.session = session or requests.Session()
        if session is None:
            self.session.trust_env = False
            self.session.headers["User-Agent"] = "EnkiduPaperIntake/1.0 (academic metadata resolver)"
        self.pacer = ArxivPacer.shared(clock=clock, sleep=sleep)
        self.last_status_code: int | None = None

    def get_text(self, url: str) -> str:
        for attempt in range(3):
            try:
                with self.pacer.request(url):
                    response = self.session.get(url, timeout=30)
            except requests.RequestException:
                if attempt == 2:
                    raise
                continue
            self.last_status_code = response.status_code
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "")
                delay = max(3, parse_retry_after(retry_after) or 3)
                if delay > 30:
                    raise ExternalServiceError(
                        "arxiv_rate_limited_manual_retry",
                        "arXiv requested a longer cooldown; manual retry required.",
                        service="arxiv", http_status=429, retryable=False,
                        retry_after_seconds=delay,
                    )
                if attempt == 2:
                    response.raise_for_status()
                self.pacer.defer(delay)
                continue
            if response.status_code >= 500 and attempt < 2:
                continue
            response.raise_for_status()
            return response.text
        raise RuntimeError("arXiv API retry exhausted")


class ArxivMetadataResolver:
    def __init__(
        self,
        *,
        transport: Any | None = None,
        local_source_root: str | Path | None = None,
    ):
        self.transport = transport or _ArxivTransport()
        self.local_source_root = Path(local_source_root or (
            Path(__file__).resolve().parent.parent / "data" / "workflow_state"
        ))

    @staticmethod
    def _plain_latex_title(value: str) -> str:
        return " ".join(
            value.replace("$\\tau$", "τ")
            .replace("{", "")
            .replace("}", "")
            .split()
        )

    def _local_authoritative_metadata(self, paper_id: str, source_url: str) -> dict[str, Any] | None:
        source_root = self.local_source_root / paper_id / "arxiv_source"
        main = next(
            (source_root / name for name in ("main.tex", "main_arxiv.tex") if (source_root / name).is_file()),
            None,
        )
        if main is None:
            return None
        try:
            text = main.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeDecodeError):
            return None
        if "\ufffd" in text:
            return None
        title_match = _LATEX_TITLE.search(text)
        title = self._plain_latex_title(title_match.group(1)) if title_match else ""
        authors = [" ".join(value.split()) for value in _LATEX_AUTHOR.findall(text)]
        authors = [value for value in authors if value]
        if not title or not authors:
            return None
        return {
            "canonical_id": paper_id,
            "title": title,
            "authors": authors,
            "paper_url": f"https://arxiv.org/abs/{paper_id}",
            "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf",
            "year": "20" + paper_id[:2],
            "published": "",
            "updated": "",
            "summary": "",
            "metadata_source": "local_arxiv_source",
        }

    @staticmethod
    def _fallback(canonical_id: str, source_url: str) -> dict[str, Any]:
        return {
            "canonical_id": canonical_id,
            "title": canonical_id or "Uploaded paper",
            "authors": [],
            "paper_url": source_url or f"local://{canonical_id}",
            "metadata_source": "fallback",
        }

    def __call__(self, canonical_id: str, source_url: str) -> dict[str, Any]:
        if not source_url and not _ARXIV_ID.fullmatch(canonical_id):
            return self._fallback(canonical_id, source_url)
        source = canonicalize_url(source_url or canonical_id)
        is_arxiv_host = urlsplit(source_url).hostname in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}
        if is_arxiv_host and not source.canonical_id:
            raise ExternalServiceError("arxiv_id_invalid", "arXiv input ID is invalid.", service="arxiv", retryable=False)
        if not _ARXIV_ID.fullmatch(canonical_id) and not _ARXIV_ID.fullmatch(source.canonical_id):
            return self._fallback(canonical_id, source_url)
        paper_id = source.canonical_id or re.sub(r"v\d+$", "", canonical_id.removesuffix(".pdf"))
        query_id = f"{paper_id}v{source.version}" if source.version else paper_id
        url = "https://export.arxiv.org/api/query?" + urlencode({"id_list": query_id})
        try:
            xml_text = self.transport.get_text(url)
            root = ET.fromstring(xml_text)
            entry = root.find("atom:entry", _ATOM)
            if entry is None:
                raise ValueError("arXiv returned no entry")
            entry_source = canonicalize_url(entry.findtext("atom:id", default="", namespaces=_ATOM))
            if entry_source.canonical_id != paper_id or entry_source.version is None:
                raise ValueError("arXiv returned the wrong paper ID or no version")
            if source.version and source.version != entry_source.version:
                raise ExternalServiceError(
                    "arxiv_version_mismatch", "arXiv metadata version does not match the requested PDF version.",
                    service="arxiv", retryable=False,
                )
            title = " ".join((entry.findtext("atom:title", default="", namespaces=_ATOM)).split())
            comment = entry.findtext("arxiv:comment", default="", namespaces=_ARXIV_NS).strip()
            summary = entry.findtext("atom:summary", default="", namespaces=_ATOM)
            if (title.lower().startswith("withdrawn:")
                    or re.search(r"\b(withdrawn by|paper has been withdrawn|this paper is withdrawn)\b", comment.lower())
                    or re.search(r"\b(withdrawn by|paper has been withdrawn|this paper is withdrawn)\b", summary.lower())):
                raise ExternalServiceError("arxiv_withdrawn", "arXiv entry is withdrawn.", service="arxiv", retryable=False)
            authors = [
                " ".join((node.findtext("atom:name", default="", namespaces=_ATOM)).split())
                for node in entry.findall("atom:author", _ATOM)
            ]
            authors = [name for name in authors if name]
            published = entry.findtext("atom:published", default="", namespaces=_ATOM)
            updated = entry.findtext("atom:updated", default="", namespaces=_ATOM)
            primary = entry.find("arxiv:primary_category", _ARXIV_NS)
            primary_category = primary.get("term", "") if primary is not None else ""
            if not title or not authors or not published or not updated or not primary_category:
                raise ValueError("arXiv metadata is incomplete")
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(
                "arxiv_metadata_failed",
                "arXiv metadata could not be resolved.",
                service="arxiv",
                http_status=getattr(self.transport, "last_status_code", None),
                retryable=True,
            ) from exc
        return {
            "canonical_id": paper_id,
            "title": title,
            "authors": authors,
            "paper_url": f"https://arxiv.org/abs/{paper_id}",
            "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf",
            "year": published[:4] if len(published) >= 4 else "",
            "published": published,
            "updated": updated,
            "arxiv_id": paper_id,
            "version": entry_source.version,
            "primary_category": primary_category,
            "canonical_pdf_url": f"https://arxiv.org/pdf/{paper_id}v{entry_source.version}",
            "metadata_source_domain": "export.arxiv.org",
            "api_status_code": int(getattr(self.transport, "last_status_code", 200)),
            "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "summary": " ".join((entry.findtext("atom:summary", default="", namespaces=_ATOM)).split()),
            "metadata_source": "arxiv",
        }
