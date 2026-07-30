"""OpenReview paper source for top-conference accepted papers.

Conferences supported (2026):
- ICML: ICML.cc/2026/Conference
- NeurIPS: NeurIPS.cc/2026/Conference
- ICLR: ICLR.cc/2026/Conference
"""

from __future__ import annotations

import json
import logging
import urllib.request
from datetime import datetime, timezone

from .base import Author, PaperMetadata, PaperSource, SourceType

logger = logging.getLogger(__name__)

OPENREVIEW_API = "https://api.openreview.net/notes"

# Top ML/AI conferences on OpenReview
CONFERENCES_2026 = [
    {"name": "ICML 2026", "invitation": "ICML.cc/2026/Conference/-/Blind_Submission"},
    {"name": "NeurIPS 2026", "invitation": "NeurIPS.cc/2026/Conference/-/Blind_Submission"},
    {"name": "ICLR 2026", "invitation": "ICLR.cc/2026/Conference/-/Blind_Submission"},
]

# Additional recommendation/IR conferences that may be on OpenReview
SEARCH_CONFERENCES = [
    "SIGIR", "KDD", "WWW", "RecSys", "WSDM", "CIKM",
]


class OpenReviewSource(PaperSource):
    """Fetch accepted papers from OpenReview for top conferences."""

    def __init__(self, conferences: list[dict] | None = None):
        self._conferences = conferences or CONFERENCES_2026

    @property
    def source_type(self) -> SourceType:
        return SourceType.OPENREVIEW

    @property
    def priority(self) -> int:
        return 0  # P0 — accepted papers are higher value than arXiv preprints

    def fetch(self, query: str | None = None, max_results: int = 50) -> list[PaperMetadata]:
        """Fetch accepted papers from all configured conferences."""
        all_papers: list[PaperMetadata] = []
        for conf in self._conferences:
            papers = self._fetch_conference(conf, max_results)
            logger.info("OpenReview %s: %d papers", conf["name"], len(papers))
            all_papers.extend(papers)
        return all_papers

    def fetch_by_id(self, paper_id: str) -> PaperMetadata | None:
        """Fetch a single OpenReview paper by note ID."""
        data = json.dumps({"ids": [paper_id]}).encode("utf-8")
        req = urllib.request.Request(
            f"{OPENREVIEW_API}?id={paper_id}",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
        except Exception as exc:
            logger.error("OpenReview fetch_by_id failed: %s", exc)
            return None

        notes = result.get("notes", [])
        if notes:
            return self._note_to_metadata(notes[0], "")
        return None

    def _fetch_conference(self, conf: dict, max_results: int) -> list[PaperMetadata]:
        """Fetch papers for one conference invitation.

        Note: OpenReview API requires the correct invitation ID format.
        2026 conferences use: <Venue>.cc/2026/Conference/-/Submission
        If API returns empty, the conference may not be publicly available yet.
        """
        invitations = [
            conf["invitation"],
            conf["invitation"].replace("Blind_Submission", "Submission"),
        ]
        all_notes = []

        for invitation in invitations:
            params = {
                "invitation": invitation,
                "limit": min(max_results, 100),
                "offset": 0,
            }
            try:
                data = json.dumps(params).encode("utf-8")
                req = urllib.request.Request(
                    OPENREVIEW_API,
                    data=data,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode())
                notes = result.get("notes", [])
                if notes:
                    all_notes.extend(notes)
                    logger.info("OpenReview %s: %d papers via %s", conf["name"], len(notes), invitation)
                    break
            except Exception as exc:
                logger.debug("OpenReview %s/%s: %s", conf["name"], invitation, exc)
                continue

        return [self._note_to_metadata(n, conf["name"]) for n in all_notes]

    def _note_to_metadata(self, note: dict, conference: str) -> PaperMetadata:
        """Convert an OpenReview note to PaperMetadata."""
        content = note.get("content", {})

        title = content.get("title", {}).get("value", "")
        abstract = content.get("abstract", {}).get("value", "")
        authors_list = content.get("authors", {}).get("value", [])
        author_ids = content.get("authorids", {}).get("value", [])

        # Parse keywords from content
        keywords = content.get("keywords", {}).get("value", [])

        # Extract PDF URL
        pdf_url = content.get("pdf", {}).get("value", "")

        authors = []
        for i, name in enumerate(authors_list):
            authors.append(Author(name=name))

        paper_id = note.get("id", "")
        # Try to find arXiv ID from the paper
        arxiv_id = ""
        if "arxiv" in abstract.lower():
            import re
            m = re.search(r"arxiv[:\s]*(\d{4}\.\d{4,5})", abstract.lower())
            if m:
                arxiv_id = m.group(1)

        return PaperMetadata(
            paper_id=paper_id,
            source_type=SourceType.OPENREVIEW,
            source_url=f"https://openreview.net/forum?id={paper_id}",
            title=title,
            authors=authors,
            abstract=abstract,
            pdf_url=pdf_url,
            conference=conference,
            year=2026,
            keywords=keywords,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def search_conference(name: str, year: int = 2026) -> dict | None:
        """Try to find a conference invitation by name."""
        patterns = [
            f"{name}.cc/{year}/Conference/-/Blind_Submission",
            f"{name}.cc/{year}/Conference/-/Submission",
        ]
        for invitation in patterns:
            return {"name": f"{name} {year}", "invitation": invitation}
        return None
