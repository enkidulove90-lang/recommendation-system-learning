"""Persist authoritative arXiv metadata used by summaries and profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import settings
from storage.paper_assets import normalize_arxiv_id


def paper_metadata_path(arxiv_id: str) -> Path:
    paper_id = normalize_arxiv_id(arxiv_id)
    return settings.DATA_DIR / "metadata" / "papers" / f"{paper_id}.json"


def save_paper_metadata(metadata: dict[str, Any]) -> Path:
    paper_id = normalize_arxiv_id(str(metadata.get("arxiv_id", "")))
    if not paper_id:
        raise ValueError("metadata.arxiv_id is required")
    path = paper_metadata_path(paper_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def load_paper_metadata(arxiv_id: str) -> dict[str, Any]:
    path = paper_metadata_path(arxiv_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}
