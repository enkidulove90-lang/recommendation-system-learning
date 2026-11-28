"""Tests for the Sentinel -> paper_intake candidate bridge."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.import_sentinel_candidates import (
    import_for_date,
    record_from_candidate,
)


def _candidate(arxiv_id: str = "2611.39999") -> dict:
    return {
        "record_id": f"arxiv:{arxiv_id}",
        "title": "A Test Paper on Recommender Systems",
        "abstract": "abstract",
        "authors": [{"name": "A. Author"}],
        "published_at": "2026-11-26T00:00:00Z",
        "venue": {"name": "", "status": "preprint", "year": "2026"},
        "topics": ["cs.IR"],
        "identifiers": {"arxiv": arxiv_id},
        "urls": {"landing": f"https://arxiv.org/abs/{arxiv_id}",
                 "pdf": f"https://arxiv.org/pdf/{arxiv_id}"},
        "source_records": [{"search_query": "test", "source": "arxiv-test"}],
    }


def test_record_from_candidate_maps_identifiers() -> None:
    record = record_from_candidate(_candidate())
    assert record is not None
    assert record.arxiv_id == "2611.39999"
    assert record.source == "sentinel_arxiv"
    assert record.publication_year == 2026
    assert record.authors == ["A. Author"]
    assert record.paper_url.startswith("https://arxiv.org/abs/")


def test_record_from_candidate_rejects_incomplete() -> None:
    assert record_from_candidate({"record_id": "arxiv:x"}) is None
    assert record_from_candidate({"title": "T"}) is None


def test_import_is_idempotent(tmp_path) -> None:
    state = tmp_path / "state"
    discovery = state / "discovery" / "2026-11-26"
    discovery.mkdir(parents=True)
    (discovery / "candidates.jsonl").write_text(
        json.dumps(_candidate()) + "\n", encoding="utf-8")
    db = tmp_path / "catalog.sqlite3"

    first = import_for_date(state, "2026-11-26", db_path=db)
    assert first["ok"] and first["seen"] == 1 and first["queued"] == 1
    second = import_for_date(state, "2026-11-26", db_path=db)
    assert second["ok"] and second["queued"] == 0  # idempotent


def test_import_missing_file_returns_error(tmp_path) -> None:
    result = import_for_date(tmp_path / "nope", "2026-01-01",
                             db_path=tmp_path / "c.sqlite3")
    assert result["ok"] is False
    assert "not found" in result["error"]
