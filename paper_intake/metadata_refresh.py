from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")


class MetadataRefreshError(RuntimeError):
    """Raised when refreshed metadata is not safe to persist."""


@dataclass(frozen=True)
class MetadataRefreshResult:
    changed: bool
    metadata: dict[str, Any]


def needs_metadata_refresh(metadata: dict[str, Any], canonical_id: str) -> bool:
    paper_id = str(canonical_id or "").removesuffix(".pdf")
    if not _ARXIV_ID.fullmatch(paper_id):
        return False
    title = str(metadata.get("title") or "").strip()
    authors = metadata.get("authors")
    return (
        not str(metadata.get("metadata_source") or "").strip()
        or title == paper_id
        or not isinstance(authors, list)
        or not any(str(author).strip() for author in authors)
    )


def _validated_refresh(metadata: dict[str, Any], canonical_id: str) -> dict[str, Any]:
    title = str(metadata.get("title") or "").strip()
    authors = [str(author).strip() for author in metadata.get("authors") or [] if str(author).strip()]
    paper_id = str(canonical_id or "").removesuffix(".pdf")
    if not title or title == paper_id or not authors:
        raise MetadataRefreshError("arXiv metadata refresh returned an incomplete title or author list")
    refreshed = dict(metadata)
    refreshed["canonical_id"] = paper_id
    refreshed["title"] = title
    refreshed["authors"] = authors
    refreshed["metadata_source"] = "arxiv_api_refresh"
    return refreshed


def refresh_metadata_file(
    path: str | Path,
    *,
    canonical_id: str,
    source_url: str,
    resolver: Callable[[str, str], dict[str, Any]],
) -> MetadataRefreshResult:
    metadata_path = Path(path)
    current = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not needs_metadata_refresh(current, canonical_id):
        return MetadataRefreshResult(False, current)

    resolved = _validated_refresh(resolver(canonical_id, source_url) or {}, canonical_id)
    merged = {**current, **resolved}
    if merged == current:
        return MetadataRefreshResult(False, current)

    temporary = metadata_path.with_suffix(metadata_path.suffix + ".tmp")
    temporary.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(metadata_path)
    return MetadataRefreshResult(True, merged)
