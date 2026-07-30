"""Multi-source paper discovery orchestrator."""

from __future__ import annotations

import logging

from .arxiv_source import ArxivSource
from .base import PaperMetadata, PaperSource
from .dedup import DedupManager
from .openreview_source import OpenReviewSource

logger = logging.getLogger(__name__)


def discover_papers(
    query: str | None = None,
    max_per_source: int = 50,
    sources: list[PaperSource] | None = None,
) -> list[PaperMetadata]:
    """Discover papers from all configured sources, merge and deduplicate.

    Args:
        query: Search query. If None, uses source defaults (recent papers).
        max_per_source: Maximum papers per source.
        sources: Custom source list. Defaults to [ArxivSource(), OpenReviewSource()].

    Returns:
        Deduplicated list of PaperMetadata, sorted by: OpenReview (conf) first,
        then by citation_count desc.
    """
    if sources is None:
        sources = [
            ArxivSource(),
            OpenReviewSource(),
        ]

    all_papers: list[PaperMetadata] = []
    for source in sources:
        if not source.is_available():
            logger.warning("Source %s unavailable, skipping", source.source_type)
            continue
        try:
            papers = source.fetch(query=query, max_results=max_per_source)
            logger.info("%s: %d papers fetched", source.source_type.value, len(papers))
            all_papers.extend(papers)
        except Exception as exc:
            logger.error("%s fetch failed: %s", source.source_type.value, exc)

    if not all_papers:
        return []

    # Deduplicate
    dedup = DedupManager()
    merged = dedup.merge(all_papers)

    # Sort: conference papers first, then by recency
    merged.sort(key=lambda p: (
        0 if p.conference else 1,       # conference papers first
        -p.year,                         # newest first
        -(p.citation_count or 0),       # high citation first
    ))

    logger.info("Total: %d papers (%d duplicates removed)", len(merged),
                 len(all_papers) - len(merged))
    return merged
