"""Catalog admission uses persisted topic and fetched official-code evidence."""
import json

import pytest

from paper_intake.catalog_governance import CatalogGovernance, IdentityEvidence
from redbook.automation.sources import PaperRecord
from redbook.orchestration.catalog_admission import admit_candidate


def _ready(path):
    catalog = CatalogGovernance(path)
    catalog.import_records([{
        "source": "arxiv", "source_id": "2607.16633", "title": "BONSAI Paper",
        "paper_url": "https://arxiv.org/abs/2607.16633", "authors": ["Jingzhe Liu"],
        "topics": ["Semantic IDs"], "topic_source": "arxiv_author_category",
        "publication_year": 2026,
    }])
    catalog.verify_identity("arxiv:2607.16633", IdentityEvidence(
        title="BONSAI Paper", authors=("Jingzhe Liu",),
        paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
        published_at="2026-07-20", authority="arxiv",
        evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    return catalog


def _record():
    return PaperRecord(
        record_id="arxiv:2607.16633", title="BONSAI Paper", source_records=[],
        authors=[{"name": "Jingzhe Liu"}],
        urls={"landing": "https://arxiv.org/abs/2607.16633"},
    )


def test_verified_paper_and_repository_evidence_admits_xhs(tmp_path):
    catalog = _ready(tmp_path / "state.sqlite")
    pages = {
        "https://arxiv.org/abs/2607.16633": "Official code: https://github.com/lab/bonsai",
        "https://github.com/lab/bonsai": "BONSAI Paper by Jingzhe Liu",
    }
    assert admit_candidate(catalog, "arxiv:2607.16633", "xiaohongshu",
                           topic_terms=("Semantic IDs",), record=_record(),
                           fetch_text=pages.__getitem__) == "eligible"
    with catalog._connect() as db:
        evidence = json.loads(db.execute("SELECT evidence_json FROM catalog_admissions").fetchone()[0])
    assert evidence["topic_matches"][0]["field"] == "topic:arxiv_author_category"
    assert evidence["code"]["repository_url"] == "https://github.com/lab/bonsai"
    assert evidence["code"]["evidence_source"] == "paper_landing_and_github_repository"
    assert evidence["code"]["checked_at"]


def test_missing_code_and_identity_mismatch_fail_closed(tmp_path):
    catalog = _ready(tmp_path / "state.sqlite")
    assert admit_candidate(catalog, "arxiv:2607.16633", "xiaohongshu",
                           topic_terms=("Semantic IDs",)) == "deferred"
    wrong = _record()
    wrong.urls["landing"] = "https://arxiv.org/abs/2607.16634"
    with pytest.raises(ValueError, match="candidate identity"):
        admit_candidate(catalog, "arxiv:2607.16633", "xiaohongshu",
                        topic_terms=("Semantic IDs",), record=wrong,
                        fetch_text=lambda _: "https://github.com/lab/bonsai")
    wrong_author = _record()
    wrong_author.authors = [{"name": "Other Author"}]
    with pytest.raises(ValueError, match="candidate author"):
        admit_candidate(catalog, "arxiv:2607.16633", "xiaohongshu",
                        topic_terms=("Semantic IDs",), record=wrong_author,
                        fetch_text=lambda _: "https://github.com/lab/bonsai")
    with catalog._connect() as db:
        assert db.execute("SELECT COUNT(*) FROM catalog_outbox").fetchone()[0] == 0


def test_unreachable_repository_does_not_admit_xhs(tmp_path):
    catalog = _ready(tmp_path / "state.sqlite")
    def fetch(url):
        if url.startswith("https://arxiv.org/"):
            return "Code https://github.com/lab/bonsai"
        raise OSError("offline")
    assert admit_candidate(catalog, "arxiv:2607.16633", "xiaohongshu",
                           topic_terms=("Semantic IDs",), record=_record(),
                           fetch_text=fetch) == "deferred"
