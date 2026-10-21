from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlencode

import requests

from .adapters import ExternalServiceError
from .retry import request_with_retry


_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")
_ATOM = {"atom": "http://www.w3.org/2005/Atom"}


class _ArxivTransport:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers["User-Agent"] = "EnkiduPaperIntake/1.0 (academic metadata resolver)"

    def get_text(self, url: str) -> str:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.text


class ArxivMetadataResolver:
    def __init__(self, *, transport: Any | None = None):
        self.transport = transport or _ArxivTransport()

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
        paper_id = canonical_id.removesuffix(".pdf")
        paper_id = re.sub(r"v\d+$", "", paper_id)
        if not _ARXIV_ID.fullmatch(canonical_id) and not _ARXIV_ID.fullmatch(paper_id):
            return self._fallback(canonical_id, source_url)
        url = "https://export.arxiv.org/api/query?" + urlencode({"id_list": paper_id})
        try:
            xml_text = request_with_retry(lambda: self.transport.get_text(url))
            root = ET.fromstring(xml_text)
            entry = root.find("atom:entry", _ATOM)
            if entry is None:
                raise ValueError("arXiv returned no entry")
            title = " ".join((entry.findtext("atom:title", default="", namespaces=_ATOM)).split())
            authors = [
                " ".join((node.findtext("atom:name", default="", namespaces=_ATOM)).split())
                for node in entry.findall("atom:author", _ATOM)
            ]
            authors = [name for name in authors if name]
            published = entry.findtext("atom:published", default="", namespaces=_ATOM)
            if not title:
                raise ValueError("arXiv title is empty")
        except Exception as exc:
            raise ExternalServiceError(
                "arxiv_metadata_failed",
                "arXiv metadata could not be resolved.",
                service="arxiv",
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
            "summary": " ".join((entry.findtext("atom:summary", default="", namespaces=_ATOM)).split()),
            "metadata_source": "arxiv",
        }
