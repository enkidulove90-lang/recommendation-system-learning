"""Abstract base classes for pluggable paper data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class SourceType(str, Enum):
    ARXIV = "arxiv"
    OPENREVIEW = "openreview"
    CVF = "cvf"
    ACL_ANTHOLOGY = "acl_anthology"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    PAPERS_WITH_CODE = "papers_with_code"
    RSS = "rss"


@dataclass(frozen=True)
class Author:
    name: str
    affiliation: str = ""


@dataclass
class PaperMetadata:
    """Unified paper metadata across all sources."""

    paper_id: str                    # arXiv ID or OpenReview note ID
    source_type: SourceType
    source_url: str                  # canonical URL
    title: str
    authors: list[Author] = field(default_factory=list)
    abstract: str = ""
    pdf_url: str = ""
    conference: str = ""             # e.g., "ICML 2026", "NeurIPS 2026"
    year: int = 2026
    keywords: list[str] = field(default_factory=list)
    github_url: str = ""
    citation_count: int = 0
    influential_citations: int = 0
    fetched_at: str = ""             # ISO 8601

    @property
    def primary_affiliations(self) -> list[str]:
        """Return unique primary affiliations (first listed per author)."""
        seen = set()
        result = []
        for author in self.authors:
            if author.affiliation and author.affiliation not in seen:
                seen.add(author.affiliation)
                result.append(author.affiliation)
        return result

    @property
    def author_names(self) -> list[str]:
        return [a.name for a in self.authors]

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["source_type"] = self.source_type.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PaperMetadata":
        authors = [Author(**a) if isinstance(a, dict) else Author(name=str(a))
                   for a in data.get("authors", [])]
        source_type = data.get("source_type", "arxiv")
        if isinstance(source_type, str):
            source_type = SourceType(source_type)
        return cls(
            paper_id=str(data["paper_id"]),
            source_type=source_type,
            source_url=str(data.get("source_url", "")),
            title=str(data.get("title", "")),
            authors=authors,
            abstract=str(data.get("abstract", "")),
            pdf_url=str(data.get("pdf_url", "")),
            conference=str(data.get("conference", "")),
            year=int(data.get("year", 2026)),
            keywords=list(data.get("keywords", [])),
            github_url=str(data.get("github_url", "")),
            citation_count=int(data.get("citation_count", 0)),
            influential_citations=int(data.get("influential_citations", 0)),
            fetched_at=str(data.get("fetched_at", "")),
        )


class PaperSource(ABC):
    """Abstract base for a paper data source.

    Each subclass implements `fetch()`, `fetch_by_id()`, and `priority()`.
    """

    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        ...

    @property
    @abstractmethod
    def priority(self) -> int:
        """Lower = higher priority (0 = P0, 1 = P1, 2 = P2)."""
        ...

    @abstractmethod
    def fetch(self, query: str | None = None, max_results: int = 50) -> list[PaperMetadata]:
        """Search/fetch papers. query=None returns recent papers."""
        ...

    @abstractmethod
    def fetch_by_id(self, paper_id: str) -> PaperMetadata | None:
        """Fetch a single paper by its canonical ID."""
        ...

    def is_available(self) -> bool:
        """Check if the source is reachable. Default True."""
        return True
