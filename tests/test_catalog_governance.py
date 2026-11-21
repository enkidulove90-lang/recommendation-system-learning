"""Catalog governance acceptance tests: discovery never implies delivery."""

import json

import pytest

from paper_intake.catalog_governance import CatalogGovernance, IdentityEvidence


BONSAI = {
    "source": "recsys_program", "source_id": "2026:bonsai", "title": "BONSAI Paper",
    "paper_url": "https://recsys.acm.org/recsys26/session-1/",
    "venue_name": "ACM RecSys 2026", "venue_type": "conference-paper",
    "publication_year": 2026, "topics": ["Semantic IDs"],
    "topic_source": "conference_session", "track": "research",
    "arxiv_id": "", "doi": "", "authors": [], "published_at": "",
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
        store.admit(paper_id, "homepage", topic_match=True)
    with pytest.raises(ValueError, match="title mismatch"):
        store.verify_identity(paper_id, IdentityEvidence(
            title="Wrong Paper", authors=("Jingzhe Liu",),
            paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
            published_at="2026-07-01", authority="arxiv", evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    store.verify_identity(paper_id, IdentityEvidence(
        title="BONSAI Paper", authors=("Jingzhe Liu",),
        paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
        published_at="2026-07-01", authority="arxiv", evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    assert store.admit(paper_id, "homepage", topic_match=False) == "deferred"
    assert store.pending_events() == []
    assert store.admit(paper_id, "homepage", topic_match=True) == "eligible"
    assert store.admit(paper_id, "wechat", topic_match=True) == "eligible"
    assert store.admit(paper_id, "xiaohongshu", topic_match=True) == "deferred"
    assert store.admit(paper_id, "xiaohongshu", topic_match=True, code_verified=True) == "eligible"
    assert store.admit(paper_id, "homepage", topic_match=True) == "eligible"
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
