"""Tests for the three-layer progressive skill loader."""
from __future__ import annotations

from pathlib import Path

from redbook.services.skill_loader import (
    SkillIndex,
    SkillLoader,
    _parse_frontmatter,
    _split_sections,
    build_loader,
)

ROOT = Path(__file__).resolve().parents[1]


def test_parse_frontmatter_and_sections() -> None:
    text = ("---\nname: demo\ndescription: a test skill\n---\n"
            "preamble text\n\n## Phase 1\nfirst rules\n\n## Phase 2\nsecond rules\n")
    meta, body = _parse_frontmatter(text)
    assert meta["name"] == "demo"
    sections = _split_sections(body)
    assert sections["__preamble__"] == "preamble text"
    assert sections["Phase 1"] == "first rules"
    assert sections["Phase 2"] == "second rules"


def test_layer1_index_reads_only_frontmatter() -> None:
    index = SkillIndex.from_root(ROOT)
    stubs = index.all_stubs()
    assert stubs
    assert all(stub.description for stub in stubs)
    assert all(stub.path.name == "SKILL.md" for stub in stubs)
    assert "xhs-paper-draft" in {stub.skill_id for stub in stubs}


def test_layer1_index_text_is_compact() -> None:
    index = SkillIndex.from_root(ROOT)
    text = index.index_text()
    assert "- xhs-paper-draft:" in text
    assert len(text) < 3000  # tiny compared to full SKILL.md bodies


def test_layer1_match_relevant_skills() -> None:
    index = SkillIndex.from_root(ROOT)
    hits = index.match("把论文发到小红书草稿", limit=3)
    ids = {hit.skill_id for hit in hits}
    assert ids  # at least one match
    assert "xhs-paper-draft" in ids or "multi-platform-publishing" in ids


def test_layer2_and_layer3_load_and_section() -> None:
    index, loader = build_loader(ROOT)
    skill = loader.load("xhs-paper-draft")
    assert skill.name
    assert skill.sections  # full body split into sections
    assert any("硬约束" in title for title in skill.section_titles())
    # layer 3: one section only, substring match
    section = loader.section("xhs-paper-draft", "硬约束")
    assert "正文" in section
    assert len(section) < len(skill.raw)


def test_layer3_unknown_section_raises() -> None:
    _, loader = build_loader(ROOT)
    try:
        loader.section("xhs-paper-draft", "不存在的段落XYZ")
    except KeyError as exc:
        assert "available" in str(exc)
    else:
        raise AssertionError("expected KeyError")
