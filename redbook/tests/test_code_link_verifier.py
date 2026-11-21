"""Task 2 acceptance: code link verifier + affiliation gates (TC5-TC10)."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.error import HTTPError
from unittest.mock import patch

from redbook.automation.code_link_verifier import parse_github_repo, verify_code_link
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
        urls={"landing": "https://arxiv.org/abs/2601.00001",
              "code": "https://github.com/org/repo"},
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


def test_git_suffix_uses_canonical_repository_name():
    assert parse_github_repo("https://github.com/org/repo.git") == ("org", "repo")


def test_real_http_404_is_classified_as_blocked(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fixture-token")
    error = HTTPError("https://api.github.com/repos/org/missing", 404,
                      "Not Found", {}, None)
    with patch("urllib.request.urlopen", side_effect=error):
        verdict = verify_code_link("https://github.com/org/missing")
    assert verdict["state"] == "blocked"


def test_network_error_does_not_export_exception_text_or_credentials():
    def failing_fetch(url: str, timeout: float) -> int:
        raise ConnectionError("https://user:pass@proxy.local/?token=secret")

    verdict = verify_code_link("https://github.com/org/repo", fetch=failing_fetch)
    assert verdict["state"] == "unverified"
    assert "ConnectionError" in verdict["detail"]
    assert "pass" not in verdict["detail"]
    assert "token=" not in verdict["detail"]


def test_default_fetch_never_uses_anonymous_github_api(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with patch("urllib.request.urlopen") as request:
        verdict = verify_code_link("https://github.com/org/repo")
    request.assert_not_called()
    assert verdict["state"] == "unverified"


def test_default_fetch_uses_preferred_token_without_exporting_it(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "preferred-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "other-secret")
    response = type("Response", (), {"status": 200, "__enter__": lambda self: self,
                                     "__exit__": lambda self, *args: None})()
    with patch("urllib.request.urlopen", return_value=response) as request:
        verdict = verify_code_link("https://github.com/org/repo.git?token=leak")
    sent = request.call_args.args[0]
    assert sent.get_header("Authorization") == "Bearer preferred-secret"
    assert sent.full_url == "https://api.github.com/repos/org/repo"
    assert verdict["url"] == "https://github.com/org/repo"
    assert "secret" not in str(verdict)
    assert "token=" not in str(verdict)


def test_invalid_credential_url_is_not_reflected():
    verdict = verify_code_link("https://user:pass@github.com/org/repo?token=secret",
                               fetch=lambda url, timeout: 200)
    assert verdict["state"] == "unverified"
    assert "pass" not in str(verdict)
    assert "secret" not in str(verdict)


def test_github_401_requires_token_repair_not_blind_retry():
    verdict = verify_code_link("https://github.com/org/repo",
                               fetch=lambda url, timeout: 401)
    assert verdict["state"] == "unverified"
    assert "credential" in verdict["detail"]
    assert "retry next run" not in verdict["detail"]


def test_gate_discovers_paper_declared_repository_before_api_check():
    paper_url = "https://arxiv.org/abs/2601.00001"
    repo_url = "https://github.com/org/repo"
    record = _record(title="Adaptive Sequential Recommendation",
                     authors=[{"name": "Ada Lovelace"}],
                     urls={"landing": paper_url})
    pages = {
        paper_url: f"Code: {repo_url}",
        repo_url: "Adaptive Sequential Recommendation by Lovelace",
    }
    kept, rejected = apply_verification_gates(
        [record], require_affiliation=False,
        code_verifier=lambda url: {"state": "verified", "url": url, "detail": "reachable"},
        text_fetcher=pages.__getitem__,
    )
    assert kept == [record] and rejected == []
    assert record.urls["github"] == repo_url
    assert record.provenance["official_github_verification"]["verified"] is True


def test_gate_rejects_reachable_repo_not_declared_by_paper():
    paper_url = "https://arxiv.org/abs/2601.00001"
    repo_url = "https://github.com/org/repo"
    record = _record(title="Adaptive Sequential Recommendation",
                     authors=[{"name": "Ada Lovelace"}],
                     urls={"landing": paper_url, "code": repo_url})
    pages = {
        paper_url: "No official code has been announced.",
        repo_url: "Adaptive Sequential Recommendation by Lovelace",
    }
    kept, rejected = apply_verification_gates(
        [record], require_affiliation=False,
        code_verifier=lambda url: {"state": "verified", "url": url, "detail": "reachable"},
        text_fetcher=pages.__getitem__,
    )
    assert kept == [] and rejected[0]["gate"] == "official_github"


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


def test_affiliation_generic_fragment_does_not_verify_named_institution():
    generic = _record(authors=[{"name": "A", "affiliation": "University"}])
    assert verify_affiliation(generic, ("Tsinghua University",))["state"] == "mismatch"


def test_affiliation_short_org_needs_token_boundary():
    unrelated = _record(authors=[{"name": "A", "affiliation": "Smith Research"}])
    assert verify_affiliation(unrelated, ("MIT",))["state"] == "mismatch"


def test_gates_keep_only_fully_verified_candidates():  # TC9 + TC10
    good = _record(record_id="good",
                   authors=[{"name": "A", "affiliation": "Tsinghua University"}])
    no_affil = _record(record_id="no-affil",
                       authors=[{"name": "B"}])
    dead_repo = _record(record_id="dead-repo",
                        authors=[{"name": "A", "affiliation": "Tsinghua University"}],
                       urls={"landing": "https://arxiv.org/abs/2601.00001",
                             "code": "https://github.com/org/gone"})
    kept, rejected = apply_verification_gates(
        [good, no_affil, dead_repo], candidate_orgs=ORGS,
        code_verifier=lambda url: {"state": "verified", "url": url, "detail": ""}
        if "repo" in url and "gone" not in url else
        {"state": "blocked", "url": url, "detail": "not found"},
        text_fetcher=lambda url: (
            "https://github.com/org/repo https://github.com/org/gone"
            if url.startswith("https://arxiv.org/") else "A Recommender Paper A"
        ))
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
