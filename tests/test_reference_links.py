from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from paper_intake.article import ReferenceChoice
from paper_intake.reference_candidates import ReferenceCandidate
from paper_intake.reference_links import (
    PwcSnapshot,
    load_pwc_snapshot,
    resolve_selected_references,
)
from scripts.bootstrap_pwc_snapshot import bootstrap_snapshot


FIXTURES = Path(__file__).parent / "fixtures"


class FakeClients:
    def __init__(
        self,
        *,
        arxiv_valid: set[str] = frozenset(),
        doi_valid: set[str] = frozenset(),
        arxiv_error: Exception | None = None,
        doi_error: Exception | None = None,
    ):
        self.arxiv_valid = set(arxiv_valid)
        self.doi_valid = set(doi_valid)
        self.arxiv_error = arxiv_error
        self.doi_error = doi_error
        self.arxiv_calls: list[list[str]] = []
        self.doi_calls: list[str] = []

    def verified_arxiv_ids(self, arxiv_ids: list[str]) -> set[str]:
        self.arxiv_calls.append(arxiv_ids)
        if self.arxiv_error:
            raise self.arxiv_error
        return set(arxiv_ids) & self.arxiv_valid

    def doi_exists(self, doi: str) -> bool:
        self.doi_calls.append(doi)
        if self.doi_error:
            raise self.doi_error
        return doi in self.doi_valid


def _candidate(
    ref_id: str,
    *,
    year: int,
    arxiv_id: str | None = None,
    doi: str | None = None,
    original_index: int = 0,
) -> ReferenceCandidate:
    return ReferenceCandidate(
        ref_id=ref_id,
        raw_text=f"Citation {ref_id}",
        title=f"Title {ref_id}",
        year=year,
        arxiv_id=arxiv_id,
        doi=doi,
        original_index=original_index,
    )


def _valid_snapshot() -> PwcSnapshot:
    path = FIXTURES / "pwc" / "minimal-links.json"
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    snapshot = load_pwc_snapshot(path, expected)
    assert snapshot is not None
    return snapshot


def test_resolves_arxiv_and_doi_only_after_provider_verification() -> None:
    candidates = [
        _candidate("ref_001", year=2025, arxiv_id="2511.21631", original_index=0),
        _candidate(
            "ref_002",
            year=2024,
            doi="10.1145/1234567.8901234",
            original_index=1,
        ),
    ]
    choices = [
        ReferenceChoice(ref_id="ref_001", reason="方法相关"),
        ReferenceChoice(ref_id="ref_002", reason="实验相关"),
    ]
    clients = FakeClients(
        arxiv_valid={"2511.21631"}, doi_valid={"10.1145/1234567.8901234"}
    )

    result = resolve_selected_references(candidates, choices, clients, _valid_snapshot())

    assert result.mode == "recommended"
    assert [item.paper_url for item in result.references] == [
        "https://arxiv.org/abs/2511.21631",
        "https://doi.org/10.1145/1234567.8901234",
    ]
    assert result.references[0].code_url == "https://github.com/QwenLM/Qwen3-VL"
    assert result.references[1].code_url is None
    assert [item.link_source for item in result.references] == ["arxiv", "doi"]
    assert clients.arxiv_calls == [["2511.21631"]]


@pytest.mark.parametrize("failure", [TimeoutError("TLS"), RuntimeError("429")])
def test_provider_failure_never_synthesizes_a_paper_url(failure: Exception) -> None:
    candidate = _candidate("ref_001", year=2026, arxiv_id="2604.20937")

    result = resolve_selected_references(
        [candidate], None, FakeClients(arxiv_error=failure), None
    )

    assert result.mode == "omitted"
    assert result.references == []


def test_unverified_404_identifiers_are_omitted() -> None:
    candidates = [
        _candidate("ref_001", year=2026, arxiv_id="2601.00001"),
        _candidate("ref_002", year=2025, doi="10.1145/404", original_index=1),
    ]

    result = resolve_selected_references(candidates, None, FakeClients(), None)

    assert result.mode == "omitted"
    assert result.references == []


def test_partial_model_selection_keeps_valid_choice_and_fills_latest_verified() -> None:
    candidates = [
        _candidate("ref_001", year=2025, arxiv_id="2511.21631", original_index=0),
        _candidate("ref_002", year=2026, arxiv_id="2601.00001", original_index=1),
        _candidate("ref_003", year=2026, arxiv_id="2604.20937", original_index=2),
    ]
    choices = [
        ReferenceChoice(ref_id="ref_001", reason="模型给出的有效理由"),
        ReferenceChoice(ref_id="ref_002", reason="但链接不存在"),
    ]

    result = resolve_selected_references(
        candidates,
        choices,
        FakeClients(arxiv_valid={"2511.21631", "2604.20937"}),
        _valid_snapshot(),
    )

    assert result.mode == "supplemental"
    assert [item.candidate.ref_id for item in result.references] == ["ref_001", "ref_003"]
    assert result.references[0].reason == "模型给出的有效理由"
    assert result.references[1].reason is None
    assert result.references[1].code_url is None


def test_invalid_or_missing_snapshot_never_supplies_code_url(tmp_path: Path) -> None:
    snapshot_path = FIXTURES / "pwc" / "minimal-links.json"
    assert load_pwc_snapshot(snapshot_path, "0" * 64) is None
    assert load_pwc_snapshot(tmp_path / "missing.json", "0" * 64) is None
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("not json", encoding="utf-8")
    digest = hashlib.sha256(corrupt.read_bytes()).hexdigest()
    assert load_pwc_snapshot(corrupt, digest) is None


def test_snapshot_accepts_only_github_repo_urls() -> None:
    snapshot = _valid_snapshot()

    assert snapshot.code_url_for(arxiv_id="2511.21631", doi=None) == (
        "https://github.com/QwenLM/Qwen3-VL"
    )
    assert snapshot.code_url_for(arxiv_id="2604.20937", doi=None) is None


def test_curated_verified_link_supplies_stop_official_repository() -> None:
    snapshot = load_pwc_snapshot(
        Path("config/reference-code-links.json"),
        hashlib.sha256(Path("config/reference-code-links.json").read_bytes()).hexdigest(),
    )

    assert snapshot is not None
    assert snapshot.code_url_for(arxiv_id="2604.20937", doi=None) == (
        "https://github.com/rlqja1107/SToP"
    )


def test_empty_candidates_omit_section_without_provider_calls() -> None:
    clients = FakeClients()

    result = resolve_selected_references([], None, clients, None)

    assert result.mode == "omitted"
    assert clients.arxiv_calls == []
    assert clients.doi_calls == []


def test_bootstrap_requires_pinned_revision_and_checksum(tmp_path: Path) -> None:
    payload = b'[{"paper_arxiv_id":"2511.21631"}]'
    expected = hashlib.sha256(payload).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "source_url": "https://example.invalid/snapshot.json",
                "revision": "abc123",
                "sha256": expected,
                "filename": "snapshot.json",
            }
        ),
        encoding="utf-8",
    )

    output = bootstrap_snapshot(manifest, tmp_path / "cache", downloader=lambda _url: payload)

    assert output.read_bytes() == payload
    manifest.write_text(
        json.dumps(
            {
                "source_url": "https://example.invalid/snapshot.json",
                "revision": "abc123",
                "sha256": "0" * 64,
                "filename": "snapshot.json",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="checksum"):
        bootstrap_snapshot(manifest, tmp_path / "cache-2", downloader=lambda _url: payload)


def test_production_reference_modules_do_not_contain_bm25() -> None:
    production = Path("paper_intake")
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in production.rglob("*.py")
    ).lower()

    assert "bm25" not in text
    assert "rank_bm25" not in text
