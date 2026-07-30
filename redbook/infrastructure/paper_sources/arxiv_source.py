"""arXiv paper source via the official API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .base import Author, PaperMetadata, PaperSource, SourceType

logger = logging.getLogger(__name__)

ARXIV_SEARCH_URL = "http://export.arxiv.org/api/query"
ARXIV_PDF_TEMPLATE = "https://arxiv.org/pdf/{arxiv_id}"
ARXIV_ABS_TEMPLATE = "https://arxiv.org/abs/{arxiv_id}"


class ArxivSource(PaperSource):
    """Fetch papers from arXiv via the public API."""

    @property
    def source_type(self) -> SourceType:
        return SourceType.ARXIV

    @property
    def priority(self) -> int:
        return 0  # P0

    def fetch(self, query: str | None = None, max_results: int = 50) -> list[PaperMetadata]:
        """Search arXiv. If query is empty, fetch recent cs.IR papers."""
        import urllib.parse
        import urllib.request
        import xml.etree.ElementTree as ET

        if not query:
            query = "cat:cs.IR"

        params = {
            "search_query": query,
            "start": 0,
            "max_results": min(max_results, 100),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        qs = urllib.parse.urlencode(params)
        url = f"{ARXIV_SEARCH_URL}?{qs}"

        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as exc:
            logger.error("arXiv fetch failed: %s", exc)
            return []

        return self._parse_feed(raw)

    def fetch_by_id(self, paper_id: str) -> PaperMetadata | None:
        """Fetch a single arXiv paper by ID."""
        import urllib.request
        import xml.etree.ElementTree as ET

        clean_id = paper_id.replace("arxiv:", "").replace("arXiv:", "").strip()
        url = f"{ARXIV_ABS_TEMPLATE.format(arxiv_id=clean_id)}"
        api_url = f"{ARXIV_SEARCH_URL}?id_list={clean_id}&max_results=1"

        try:
            with urllib.request.urlopen(api_url, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as exc:
            logger.error("arXiv fetch_by_id failed for %s: %s", clean_id, exc)
            return None

        results = self._parse_feed(raw)
        return results[0] if results else None

    def _parse_feed(self, raw: str) -> list[PaperMetadata]:
        import xml.etree.ElementTree as ET
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return []

        papers = []
        for entry in root.findall("atom:entry", ns):
            arxiv_id = self._text(entry, "atom:id", ns).split("/")[-1]
            # Strip version suffix
            arxiv_id = arxiv_id.split("v")[0]

            title = self._text(entry, "atom:title", ns).strip().replace("\n", " ")
            summary = self._text(entry, "atom:summary", ns).strip().replace("\n", " ")

            authors = []
            for author_el in entry.findall("atom:author", ns):
                name = self._text(author_el, "atom:name", ns)
                aff = self._text(author_el, "arxiv:affiliation", ns)
                authors.append(Author(name=name, affiliation=aff))

            published = self._text(entry, "atom:published", ns)
            year = int(published[:4]) if published else 2026

            papers.append(PaperMetadata(
                paper_id=arxiv_id,
                source_type=SourceType.ARXIV,
                source_url=ARXIV_ABS_TEMPLATE.format(arxiv_id=arxiv_id),
                title=title,
                authors=authors,
                abstract=summary,
                pdf_url=ARXIV_PDF_TEMPLATE.format(arxiv_id=arxiv_id),
                year=year,
                fetched_at=datetime.now(timezone.utc).isoformat(),
            ))

        return papers

    @staticmethod
    def _text(element, tag: str, ns: dict) -> str:
        child = element.find(tag, ns)
        return child.text.strip() if child is not None and child.text else ""
