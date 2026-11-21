import json

import pytest

from paper_intake.catalog import PaperCatalog, PaperRecord


def test_v1_snapshot_reads_as_v2_and_ignores_unknown_fields():
    record = PaperRecord.from_dict({"publication_year": 2026, "venue_type": "preprint",
        "venue_name": "arXiv", "title": "Example", "paper_url": "https://arxiv.org/abs/2601.00001",
        "source": "arxiv", "source_id": "2601.00001", "arxiv_id": "2601.00001",
        "unexpected_future_field": True})
    assert record.schema_version == 2
    assert record.canonical_id == "arxiv:2601.00001"
    assert record.identity_status == "discovered"
    assert "unexpected_future_field" not in record.to_dict()


def test_catalog_get_uses_canonical_identifier():
    record = PaperRecord(2026, "preprint", "arXiv", "Example", "https://arxiv.org/abs/2601.00001",
                         "arxiv", "2601.00001", arxiv_id="2601.00001")
    catalog = PaperCatalog([record])
    assert catalog.get("arxiv:2601.00001") is record
    with pytest.raises(KeyError):
        catalog.get("arxiv:missing")


def test_exported_catalog_is_schema_v2(tmp_path):
    catalog = PaperCatalog([PaperRecord(2026, "preprint", "arXiv", "Example",
        "https://arxiv.org/abs/2601.00001", "arxiv", "2601.00001", arxiv_id="2601.00001")])
    target = tmp_path / "papers.json"
    catalog.write_json(target, refresh_interval_seconds=1800)
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["papers"][0]["canonical_id"] == "arxiv:2601.00001"
