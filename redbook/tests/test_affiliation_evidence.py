"""Local PDF first-page evidence for daily discovery admission."""

from pathlib import Path
import hashlib
import json

import fitz

from redbook.automation.affiliation_evidence import inspect_first_page
from redbook.automation.daily_discovery import DailyDiscoveryRunner, apply_verification_gates
from redbook.automation.sources import PaperRecord


def _pdf(path: Path, lines: list[str]) -> Path:
    document = fitz.open()
    page = document.new_page()
    for index, line in enumerate(lines):
        page.insert_text((72, 72 + index * 24), line)
    document.save(path)
    document.close()
    return path


def test_first_page_requires_title_author_and_organization(tmp_path):
    path = _pdf(tmp_path / "paper.pdf", [
        "Evidence-Based Recommendations", "Alice Example", "Tsinghua University",
        "Abstract", "This paper studies recommendations.",
    ])
    verdict = inspect_first_page(path, title="Evidence-Based Recommendations",
                                 authors=[{"name": "Alice Example"}],
                                 candidate_orgs=("Tsinghua University",))
    assert verdict["state"] == "verified"
    assert verdict["source"] == "pdf_first_page"
    assert verdict["matched"] == ["Tsinghua University"]


def test_first_page_rejects_identity_mismatch(tmp_path):
    path = _pdf(tmp_path / "wrong.pdf", [
        "Different Paper", "Alice Example", "Tsinghua University",
    ])
    verdict = inspect_first_page(path, title="Evidence-Based Recommendations",
                                 authors=[{"name": "Alice Example"}],
                                 candidate_orgs=("Tsinghua University",))
    assert verdict["state"] == "unverified"


def test_first_page_does_not_use_abstract_organization_mention(tmp_path):
    path = _pdf(tmp_path / "mention.pdf", [
        "Evidence-Based Recommendations", "Alice Example", "Abstract",
        "A prior study from Tsinghua University is cited here.",
    ])
    verdict = inspect_first_page(path, title="Evidence-Based Recommendations",
                                 authors=[{"name": "Alice Example"}],
                                 candidate_orgs=("Tsinghua University",))
    assert verdict["state"] == "unverified"


def test_missing_or_invalid_pdf_is_unverified(tmp_path):
    for path in (tmp_path / "missing.pdf", tmp_path / "invalid.pdf"):
        if path.name == "invalid.pdf":
            path.write_text("not a PDF", encoding="utf-8")
        verdict = inspect_first_page(path, title="Paper", authors=[{"name": "Alice"}],
                                     candidate_orgs=("Tsinghua University",))
        assert verdict["state"] == "unverified"


def test_gate_uses_cached_pdf_only_when_author_metadata_has_no_affiliation(tmp_path):
    path = _pdf(tmp_path / "paper.pdf", [
        "Evidence-Based Recommendations", "Alice Example", "Tsinghua University",
        "Abstract", "A paper.",
    ])
    record = PaperRecord(
        record_id="arxiv:2601.00001", title="Evidence-Based Recommendations",
        source_records=[], identifiers={"arxiv": "2601.00001"},
        authors=[{"name": "Alice Example"}],
    )
    kept, rejected = apply_verification_gates(
        [record], candidate_orgs=("Tsinghua University",), require_code=False,
        pdf_path_resolver=lambda _record: path,
    )
    assert kept == [record] and rejected == []
    assert record.provenance["affiliation_verification"]["source"] == "pdf_first_page"


def test_gate_keeps_missing_pdf_unverified(tmp_path):
    record = PaperRecord(
        record_id="arxiv:2601.00001", title="Evidence-Based Recommendations",
        source_records=[], identifiers={"arxiv": "2601.00001"},
        authors=[{"name": "Alice Example"}],
    )
    kept, rejected = apply_verification_gates(
        [record], candidate_orgs=("Tsinghua University",), require_code=False,
        pdf_path_resolver=lambda _record: tmp_path / "missing.pdf",
    )
    assert kept == [] and rejected[0]["gate"] == "affiliation"


def test_runner_rejects_cached_pdf_without_matching_manifest(tmp_path):
    paper_id = "2601.00001"
    papers = tmp_path / "papers"
    papers.mkdir()
    pdf = _pdf(papers / f"{paper_id}.pdf", ["Paper", "Alice", "Abstract"])
    record = PaperRecord(record_id=f"arxiv:{paper_id}", title="Paper",
                         source_records=[], identifiers={"arxiv": paper_id})
    runner = DailyDiscoveryRunner(tmp_path, tmp_path / "config.yaml")
    assert runner._cached_pdf_path(record) is None

    data = pdf.read_bytes()
    manifest = {"arxiv_id": paper_id, "sha256": hashlib.sha256(data).hexdigest(),
                "byte_size": len(data)}
    (papers / f"{paper_id}.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert runner._cached_pdf_path(record) == pdf

    pdf.write_bytes(data + b"tampered")
    assert runner._cached_pdf_path(record) is None


def test_runner_rejects_wrong_cached_pdf_identity(tmp_path):
    paper_id = "2601.00001"
    papers = tmp_path / "papers"
    papers.mkdir()
    pdf = _pdf(papers / f"{paper_id}.pdf", ["Paper", "Alice", "Abstract"])
    data = pdf.read_bytes()
    (papers / f"{paper_id}.manifest.json").write_text(json.dumps({
        "arxiv_id": "2601.00002", "sha256": hashlib.sha256(data).hexdigest(),
        "byte_size": len(data),
    }), encoding="utf-8")
    record = PaperRecord(record_id=f"arxiv:{paper_id}", title="Paper",
                         source_records=[], identifiers={"arxiv": paper_id})
    assert DailyDiscoveryRunner(tmp_path, tmp_path / "config.yaml")._cached_pdf_path(record) is None
