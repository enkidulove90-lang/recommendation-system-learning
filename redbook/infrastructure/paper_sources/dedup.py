"""Deduplication and merging logic for multi-source paper discovery."""

from __future__ import annotations

import logging
import re

from .base import PaperMetadata

logger = logging.getLogger(__name__)

# Regex to extract arXiv ID from various formats
ARXIV_ID_PATTERN = re.compile(r"(?:arxiv[:\s]*)?(\d{4}\.\d{4,5})", re.IGNORECASE)


class DedupManager:
    """Merge duplicate papers from multiple sources and remove noise."""

    def __init__(self, title_threshold: float = 0.85, author_overlap: float = 0.5):
        self._title_threshold = title_threshold
        self._author_overlap = author_overlap
        self._seen_ids: set[str] = set()

    def merge(self, papers: list[PaperMetadata]) -> list[PaperMetadata]:
        """Merge duplicate papers and return deduplicated list.

        Priority in merging: OpenReview > arXiv > others (highest confidence first).
        """
        merged: list[PaperMetadata] = []

        for paper in papers:
            if self._is_duplicate(paper, merged):
                self._merge_into(paper, merged)
            else:
                self._seen_ids.add(paper.paper_id)
                merged.append(paper)

        return merged

    def _is_duplicate(self, paper: PaperMetadata, existing: list[PaperMetadata]) -> bool:
        """Check if paper is a duplicate of any existing entry."""
        # Exact ID match
        if paper.paper_id in self._seen_ids:
            return True

        # arXiv ID cross-matching (arxiv source vs OpenReview abstract)
        paper_arxiv = self._extract_arxiv_id(paper)
        for ex in existing:
            ex_arxiv = self._extract_arxiv_id(ex)
            if paper_arxiv and ex_arxiv and paper_arxiv == ex_arxiv:
                return True

            # Title + author overlap
            if self._title_similarity(paper.title, ex.title) >= self._title_threshold:
                if self._author_overlap_ratio(paper, ex) >= self._author_overlap:
                    return True

        return False

    def _merge_into(self, paper: PaperMetadata, existing: list[PaperMetadata]) -> None:
        """Merge incremental fields from new paper into existing entry."""
        for i, ex in enumerate(existing):
            if not self._is_duplicate(paper, [ex]):
                continue

            # Keep higher-priority source
            if paper.source_type.value < ex.source_type.value:
                # New paper has higher priority, replace
                existing[i] = self._merge_fields(paper, ex)
            else:
                # Existing has higher or equal priority, update only missing fields
                existing[i] = self._merge_fields(ex, paper)
            return

    @staticmethod
    def _merge_fields(primary: PaperMetadata, secondary: PaperMetadata) -> PaperMetadata:
        """Merge fields: keep primary, fill gaps from secondary."""
        # Conference from OpenReview is gold
        if not primary.conference and secondary.conference:
            primary.conference = secondary.conference
        if not primary.github_url and secondary.github_url:
            primary.github_url = secondary.github_url
        if primary.citation_count == 0 and secondary.citation_count > 0:
            primary.citation_count = secondary.citation_count
        if not primary.pdf_url and secondary.pdf_url:
            primary.pdf_url = secondary.pdf_url
        if not primary.keywords and secondary.keywords:
            primary.keywords = secondary.keywords
        return primary

    @staticmethod
    def _extract_arxiv_id(paper: PaperMetadata) -> str:
        """Extract arXiv ID from paper metadata."""
        # Direct match on paper_id
        m = ARXIV_ID_PATTERN.match(paper.paper_id)
        if m:
            return m.group(1)
        # Search in abstract
        m = ARXIV_ID_PATTERN.search(paper.abstract)
        if m:
            return m.group(1)
        return ""

    def _title_similarity(self, title1: str, title2: str) -> float:
        """Compute normalized title similarity."""
        t1 = self._normalize(title1)
        t2 = self._normalize(title2)
        if not t1 or not t2:
            return 0.0

        # Jaccard similarity on word sets
        words1 = set(t1.split())
        words2 = set(t2.split())
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0

    def _author_overlap_ratio(self, p1: PaperMetadata, p2: PaperMetadata) -> float:
        """Compute author overlap ratio between two papers."""
        names1 = {a.name.lower() for a in p1.authors}
        names2 = {a.name.lower() for a in p2.authors}
        if not names1 or not names2:
            return 0.0
        intersection = names1 & names2
        return len(intersection) / min(len(names1), len(names2))

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
