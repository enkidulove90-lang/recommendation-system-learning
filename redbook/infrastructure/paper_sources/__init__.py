"""Pluggable paper data sources with unified metadata and deduplication."""

from .base import PaperMetadata, PaperSource
from .arxiv_source import ArxivSource
from .openreview_source import OpenReviewSource
from .dedup import DedupManager
from .discovery import discover_papers

__all__ = [
    "PaperMetadata",
    "PaperSource",
    "ArxivSource",
    "OpenReviewSource",
    "DedupManager",
    "discover_papers",
]
