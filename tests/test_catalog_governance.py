"""Catalog governance acceptance tests: discovery never implies delivery."""

import json
import sqlite3

import pytest

from paper_intake.catalog_governance import CatalogGovernance, IdentityEvidence


BONSAI = {
    "source": "recsys_program", "source_id": "2026:bonsai", "title": "BONSAI Paper",
    "paper_url": "https://recsys.acm.org/recsys26/session-1/",
    "venue_name": "ACM RecSys 2026", "venue_type": "conference-paper",
    "publication_year": 2026, "topics": ["Semantic IDs"],
    "topic_source": "conference_session", "track": "research",
    "arxiv_id": "", "doi": "", "authors": ["Jingzhe Liu"], "published_at": "",
}


def test_full_catalog_import_is_idempotent_and_never_queues(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    snapshot = {"schema_version": 1, "papers": [BONSAI] * 5112}
    path = tmp_path / "papers.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    assert store.import_snapshot(path) == 1
    assert store.import_snapshot(path) == 0
    paper = store.get("recsys_program:2026:bonsai")
    assert paper["identity_state"] == "unresolved"
    assert paper["source_url"] == BONSAI["paper_url"]
    assert store.pending_events() == []


def test_bonsai_requires_verified_document_then_platform_admission(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([BONSAI])
    paper_id = "recsys_program:2026:bonsai"
    with pytest.raises(ValueError, match="identity_verified"):
        store.admit(paper_id, "homepage", topic_terms=("Semantic IDs",))
    with pytest.raises(ValueError, match="title mismatch"):
        store.verify_identity(paper_id, IdentityEvidence(
            title="Wrong Paper", authors=("Jingzhe Liu",),
            paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
            published_at="2026-07-01", authority="arxiv", evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    store.verify_identity(paper_id, IdentityEvidence(
        title="BONSAI Paper", authors=("Jingzhe Liu",),
        paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
        published_at="2026-07-01", authority="arxiv", evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    assert store.admit(paper_id, "homepage", topic_terms=("Unrelated Topic",)) == "deferred"
    assert store.pending_events() == []
    assert store.admit(paper_id, "homepage", topic_terms=("Semantic IDs",)) == "eligible"
    assert store.admit(paper_id, "wechat", topic_terms=("Semantic IDs",)) == "eligible"
    assert store.admit(paper_id, "xiaohongshu", topic_terms=("Semantic IDs",)) == "deferred"
    code_evidence = {"verified": True, "repository_url": "https://github.com/example/bonsai",
                     "paper_url": "https://arxiv.org/abs/2607.16633",
                     "paper_names_repository": True, "repository_reachable": True,
                     "repository_matches_title": True, "repository_mentions_author": True}
    assert store.admit(paper_id, "xiaohongshu", topic_terms=("Semantic IDs",),
                       code_evidence=code_evidence) == "eligible"
    assert store.admit(paper_id, "homepage", topic_terms=("Semantic IDs",)) == "eligible"
    events = store.pending_events()
    assert len(events) == 3
    assert {event["platform"] for event in events} == {"homepage", "wechat", "xiaohongshu"}


def test_bad_identity_url_never_becomes_eligible(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([BONSAI])
    with pytest.raises(ValueError, match="canonical paper URL"):
        store.verify_identity("recsys_program:2026:bonsai", IdentityEvidence(
            title="BONSAI Paper", authors=("Jingzhe Liu",),
            paper_url=BONSAI["paper_url"], published_at="2026-07-01",
            authority="arxiv", evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    assert store.pending_events() == []


def test_evidence_url_cannot_be_supplied_by_an_untrusted_host(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([BONSAI])
    with pytest.raises(ValueError, match="untrusted authority"):
        store.verify_identity("recsys_program:2026:bonsai", IdentityEvidence(
            title="BONSAI Paper", authors=("Jingzhe Liu",),
            paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
            published_at="2026-07-01", authority="arxiv",
            evidence_url="https://example.com/fake-arxiv-response"))
    assert store.pending_events() == []


def test_official_arxiv_response_resolves_suggested_id_only_on_title_match(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([BONSAI])
    feed = '''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
      <id>https://arxiv.org/abs/2607.16633v1</id>
      <published>2026-07-20T00:00:00Z</published><updated>2026-07-20T00:00:00Z</updated>
      <title>BONSAI Paper</title><author><name>Jingzhe Liu</name></author>
      </entry></feed>'''

    class Transport:
        def get_text(self, url):
            assert url == "https://export.arxiv.org/api/query?id_list=2607.16633"
            return feed

    store.verify_arxiv_id("recsys_program:2026:bonsai", "2607.16633", transport=Transport())
    assert store.get("recsys_program:2026:bonsai")["canonical_id"] == "arxiv:2607.16633"
    assert store.pending_events() == []

    other = CatalogGovernance(tmp_path / "other.sqlite")
    other.import_records([BONSAI])
    wrong_feed = feed.replace("BONSAI Paper", "Different Paper")
    with pytest.raises(ValueError, match="title mismatch"):
        other.verify_arxiv_id("recsys_program:2026:bonsai", "2607.16633",
                               transport=type("Wrong", (), {"get_text": lambda self, url: wrong_feed})())
    assert other.pending_events() == []


def test_old_recsys_snapshot_without_authors_stays_unresolved(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([{**BONSAI, "authors": []}])
    with pytest.raises(ValueError, match="source author evidence required"):
        store.verify_identity("recsys_program:2026:bonsai", IdentityEvidence(
            title="BONSAI Paper", authors=("Jingzhe Liu",),
            paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
            published_at="2026-07-20", authority="arxiv",
            evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    assert store.get("recsys_program:2026:bonsai")["identity_state"] == "unresolved"
    assert store.import_records([BONSAI]) == 0
    assert json.loads(store.get("recsys_program:2026:bonsai")["source_authors_json"]) == ["Jingzhe Liu"]


def test_revised_catalog_interfaces_are_auditable_and_restricted(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([BONSAI])
    paper_id = "recsys_program:2026:bonsai"
    assert store.get_by_identity("arxiv:missing") is None
    store.update_enrichment(paper_id, {"title_zh": "BONSAI 论文"})
    assert json.loads(store.get(paper_id)["enrichment_json"])["title_zh"] == "BONSAI 论文"
    with pytest.raises(ValueError, match="allowed fields"):
        store.update_enrichment(paper_id, {"canonical_id": "forged"})
    store.verify_identity(paper_id, IdentityEvidence(title="BONSAI Paper", authors=("Jingzhe Liu",),
        paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
        published_at="2026-07-01", authority="arxiv",
        evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    assert store.admit(paper_id, "wechat", topic_terms=("not-a-topic",)) == "deferred"
    store.block(paper_id, "wechat", "manual review", {"reviewer": "test"})
    assert store.governance_report()["deferred"] == []
    assert any(row["kind"] == "enrichment" for row in store.evidence_history(paper_id))
    unresolved_id = "recsys_program:2026:other"
    store.import_records([{**BONSAI, "source_id": "other", "title": "Other paper"}])
    unresolved_id = "recsys_program:other"
    store.mark_conflict(unresolved_id, "arxiv:2607.16633", {"reason": "collision"})
    assert len(store.governance_report()["conflicts"]) == 1
    assert store.get(unresolved_id)["identity_state"] == "conflict"


def test_missing_or_invalid_rules_fail_closed(tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError):
        CatalogGovernance(tmp_path / "x.sqlite", config_path=missing)
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("platforms: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid catalog governance"):
        CatalogGovernance(tmp_path / "y.sqlite", config_path=invalid)


def test_evidence_log_appends_identity_and_admission_decisions(tmp_path):
    store = CatalogGovernance(tmp_path / "catalog.sqlite")
    store.import_records([BONSAI])
    pid = "recsys_program:2026:bonsai"
    evidence = IdentityEvidence(title="BONSAI Paper", authors=("Jingzhe Liu",),
        paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
        published_at="2026-07-01", authority="arxiv",
        evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633")
    store.verify_identity(pid, evidence)
    store.verify_identity(pid, evidence)
    store.admit(pid, "homepage", topic_terms=("Semantic IDs",))
    history = store.evidence_history(pid)
    assert [row["kind"] for row in history] == ["identity", "identity", "admission"]
    with store._connect() as db:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute("UPDATE catalog_evidence_log SET verdict='rewritten' WHERE catalog_id=?", (pid,))
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute("DELETE FROM catalog_evidence_log WHERE catalog_id=?", (pid,))
