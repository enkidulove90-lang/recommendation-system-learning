from __future__ import annotations

from pathlib import Path

from paper_intake.reference_candidates import (
    candidate_hash,
    extract_reference_candidates,
    select_latest,
    source_hash,
    strip_generated_related_reading,
)


FIXTURE = Path(__file__).parent / "fixtures" / "references" / "2610.05432-excerpt.md"


def test_extracts_only_normalized_arxiv_or_doi_candidates_in_original_order() -> None:
    markdown = FIXTURE.read_text(encoding="utf-8")

    candidates = extract_reference_candidates(markdown)

    assert [item.ref_id for item in candidates] == [
        "ref_001",
        "ref_002",
        "ref_003",
        "ref_004",
    ]
    assert [item.original_index for item in candidates] == [0, 1, 3, 4]
    assert [item.arxiv_id for item in candidates] == [
        "2511.21631",
        None,
        "hep-th/9901001",
        "2604.20937",
    ]
    assert [item.doi for item in candidates] == [
        None,
        "10.1145/1234567.8901234",
        None,
        None,
    ]
    assert [item.year for item in candidates] == [2025, 2024, 1999, 2026]
    assert candidates[0].raw_text.endswith("arXiv:2511.21631v2.")
    assert "Qwen3-vl technical report" in candidates[0].title
    assert "fine-grained video understanding" in candidates[3].title
    assert all("2609.99999" not in item.raw_text for item in candidates)


def test_unrelated_numbers_outside_or_inside_references_are_not_candidates() -> None:
    markdown = """# Paper\n\n2026 10.1145\n\n## References\n\nA. Author. 2024. No identifier, pages 10-20.\n"""

    assert extract_reference_candidates(markdown) == []


def test_latest_selection_sorts_year_then_arxiv_yymm_then_original_order() -> None:
    candidates = extract_reference_candidates(FIXTURE.read_text(encoding="utf-8"))

    latest = select_latest(candidates, count=3)
    excluding_newest = select_latest(candidates, count=2, excluded_ids={"ref_004"})

    assert [item.ref_id for item in latest] == ["ref_004", "ref_001", "ref_002"]
    assert [item.ref_id for item in excluding_newest] == ["ref_001", "ref_002"]


def test_candidate_hash_is_stable_and_changes_with_candidate_metadata() -> None:
    markdown = FIXTURE.read_text(encoding="utf-8")
    candidates = extract_reference_candidates(markdown)

    first = candidate_hash(candidates)
    second = candidate_hash(extract_reference_candidates(markdown.replace("\r\n", "\n")))
    changed = candidate_hash(
        extract_reference_candidates(markdown.replace("Qwen3-vl", "Qwen3-vl updated"))
    )

    assert first == second
    assert first != changed
    assert len(first) == 64


def test_source_hash_ignores_replaced_generated_related_reading_block() -> None:
    base = "# Article\n\n正文。\n"
    first = (
        base
        + "\n<!-- related-reading:start -->\n## 延伸阅读\n旧内容\n"
        + "<!-- related-reading:end -->\n"
    )
    second = (
        base
        + "\n<!-- related-reading:start -->\n## 补充阅读\n新内容\n"
        + "<!-- related-reading:end -->\n"
    )

    assert strip_generated_related_reading(first).strip() == base.strip()
    assert source_hash(first) == source_hash(second) == source_hash(base)


def test_source_hash_normalizes_line_endings_and_trailing_whitespace() -> None:
    assert source_hash("A  \r\nB\r\n") == source_hash("A\nB\n")
