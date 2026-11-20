"""Task 2 acceptance: code link verifier + affiliation gates (TC5-TC10)."""
from __future__ import annotations

from datetime import datetime, timezone

from redbook.automation.code_link_verifier import verify_code_link
from redbook.automation.daily_discovery import (
    apply_verification_gates, verify_affiliation,
)
from redbook.automation.sources import PaperRecord

ORGS = ("Tsinghua University", "Alibaba", "ByteDance")


def _record(**kwargs) -> PaperRecord:
    base = dict(
        record_id="r1", title="A Recommender Paper",
        source_records=[], published_at=datetime.now(timezone.utc).isoformat(),
        identifiers={"arxiv": "2601.00001"},
        venue={"name": "SIGIR", "status": "published"},
        urls={"code": "https://github.com/org/repo"},
    )
    base.update(kwargs)
    record = PaperRecord(**base)
    record.provenance["candidate_scope"] = "domain"
    record.provenance["arxiv_query"] = 'all:"recommender"'
    return record


def test_code_link_verified_on_200():  # TC6
    verdict = verify_code_link("https://github.com/org/repo",
                               fetch=lambda url, t: 200)
    assert verdict["state"] == "verified" and "org/repo" in verdict["detail"]


def test_code_link_404_parks_not_drops():  # TC7
    verdict = verify_code_link("https://github.com/org/missing",
                               fetch=lambda url, t: 404)
    assert verdict["state"] == "blocked" and "human review" in verdict["detail"]


def test_code_link_timeout_is_retryable_unverified():  # TC8
    def timeout_fetch(url: str, t: float) -> int:
        raise TimeoutError("read timed out")
    verdict = verify_code_link("https://github.com/org/repo", fetch=timeout_fetch)
    assert verdict["state"] == "unverified" and "retry" in verdict["detail"]


def test_code_link_non_github_url_requires_manual():  # covers edge
    verdict = verify_code_link("https://gitlab.com/org/repo", fetch=lambda u, t: 200)
    assert verdict["state"] == "unverified" and "manual" in verdict["detail"]


def test_affiliation_three_states_table_driven():  # TC5
    verified = _record(authors=[{"name": "A", "affiliation": "Tsinghua University, Beijing"}])
    assert verify_affiliation(verified, ORGS)["state"] == "verified"
    mismatch = _record(authors=[{"name": "B", "affiliation": "Some Unknown Institute"}])
    assert verify_affiliation(mismatch, ORGS)["state"] == "mismatch"
    no_meta = _record(authors=[{"name": "C"}])
    assert verify_affiliation(no_meta, ORGS)["state"] == "unverified"
    partial_list = _record(authors=[{"name": "D",
                                     "affiliation": ["Alibaba Group", "HKUST"]}])
    assert verify_affiliation(partial_list, ORGS)["state"] == "verified"


def test_gates_keep_only_fully_verified_candidates():  # TC9 + TC10
    good = _record(record_id="good",
                   authors=[{"name": "A", "affiliation": "Tsinghua University"}])
    no_affil = _record(record_id="no-affil",
                       authors=[{"name": "B"}])
    dead_repo = _record(record_id="dead-repo",
                        authors=[{"name": "A", "affiliation": "Tsinghua University"}],
                        urls={"code": "https://github.com/org/gone"})
    kept, rejected = apply_verification_gates(
        [good, no_affil, dead_repo], candidate_orgs=ORGS,
        code_verifier=lambda url: {"state": "verified", "url": url, "detail": ""}
        if "repo" in url and "gone" not in url else
        {"state": "blocked", "url": url, "detail": "not found"})
    assert [r.record_id for r in kept] == ["good"]
    gates = {entry["record_id"]: entry["gate"] for entry in rejected}
    assert gates["no-affil"] == "affiliation"
    assert gates["dead-repo"] == "code"


def test_gates_record_evidence_in_provenance():  # audit trail
    record = _record(authors=[{"name": "A", "affiliation": "Tsinghua University"}])
    apply_verification_gates(
        [record], candidate_orgs=ORGS, require_code=False)
    assert record.provenance["affiliation_verification"]["state"] == "verified"
    assert record.provenance["affiliation_verification"]["matched"]
