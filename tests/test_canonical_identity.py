from __future__ import annotations

from pathlib import Path

from paper_intake.catalog import PaperCatalog, PaperRecord
from paper_intake.catalog_identity import canonical_id, canonical_id_from_bare, decide_identity
from paper_intake.catalog_store import CatalogRepository


def _record(**overrides: object) -> PaperRecord:
    values: dict[str, object] = dict(
        publication_year=2026, venue_type="preprint", venue_name="arXiv",
        title="Unified identity test", paper_url="https://arxiv.org/abs/2601.00001",
        source="arxiv", source_id="2601.00001", arxiv_id="2601.00001", doi="",
    )
    values.update(overrides)
    return PaperRecord(**values)  # type: ignore[arg-type]


def test_canonical_id_priority_matches_persisted_identity() -> None:
    assert canonical_id(_record(arxiv_id="2601.00001")) == "arxiv:2601.00001"
    assert canonical_id(_record(doi="https://doi.org/10.1234/AbC", arxiv_id="2601.00001")) == "doi:10.1234/abc"
    assert canonical_id(_record(doi="", arxiv_id="", source="acl_anthology", source_id="2026.acl-long.1")) == (
        "source:acl_anthology:2026.acl-long.1"
    )


def test_catalog_key_delegates_to_unified_identity() -> None:
    record = _record(doi="", arxiv_id="", source="recsys_program", source_id="2026:some title")
    assert PaperCatalog._key(record) == canonical_id(record)
    catalog = PaperCatalog([record, _record(source_id="2601.00002", arxiv_id="2601.00002")])
    assert len(catalog.papers) == 2


def test_decide_identity_new_record_agrees_with_canonical_id() -> None:
    record = _record(arxiv_id="2601.00001")
    decision = decide_identity(
        source=record.source, source_id=record.source_id, title=record.title,
        authors=record.authors, doi=record.doi, arxiv_id=record.arxiv_id, existing=[],
    )
    assert decision.canonical_id == canonical_id(record)


def test_persisted_paper_uses_canonical_prefix(tmp_path: Path) -> None:
    repository = CatalogRepository(tmp_path / "catalog.sqlite3")
    try:
        canonical = repository.upsert_candidate(_record())
        row = repository._connection.execute(
            "SELECT canonical_id FROM papers WHERE canonical_id=?", (canonical,)
        ).fetchone()
        assert row is not None
        assert canonical == "arxiv:2601.00001"
    finally:
        repository.close()


def test_canonical_id_from_bare_handles_arxiv_acl_and_rejects_garbage() -> None:
    assert canonical_id_from_bare("2302.08191") == "arxiv:2302.08191"
    assert canonical_id_from_bare("2302.08191v2") == "arxiv:2302.08191"
    assert canonical_id_from_bare("2026.acl-short.10") == "source:acl_anthology:2026.acl-short.10"
    assert canonical_id_from_bare("arxiv:2302.08191") == "arxiv:2302.08191"
    assert canonical_id_from_bare("3792192_MSCA") == ""
    assert canonical_id_from_bare("") == ""
