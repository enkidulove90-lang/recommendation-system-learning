"""Stage 1 叙事引擎测试：四段式 + 防幻觉字段绑定。"""

import json
from pathlib import Path

from content_factory.narrative_engine import NarrativeEngine
from content_factory.schemas import PaperSummary

FIX = Path(__file__).resolve().parent / "fixtures"


def _summary(name: str) -> PaperSummary:
    return PaperSummary(json.loads((FIX / name).read_text(encoding="utf-8")))


def test_four_sections_non_empty():
    story = NarrativeEngine().build(_summary("sample_summary.json"), "2506.07261")
    assert story.hook
    assert story.method_section
    assert story.climax_section
    assert story.ending_section


def test_antihallucination_bound_fields_present():
    story = NarrativeEngine().build(_summary("sample_summary.json"), "2506.07261")
    # 每节都须绑定至少一个来源字段，否则即「编造」
    for sec in ("hook", "method_section", "climax_section", "ending_section"):
        assert story.bound_fields.get(sec), f"{sec} 未绑定任何来源字段"


def test_full_text_contains_title_and_key_number():
    story = NarrativeEngine().build(_summary("sample_summary.json"), "2506.07261")
    assert "延迟异步检索增强召回" in story.full_text
    assert "16.5%" in story.full_text


def test_11dim_schema_also_builds():
    story = NarrativeEngine().build(_summary("sample_11dim.json"), "2302.08191")
    assert "门控融合" in story.method_section
    assert story.bound_fields["climax_section"]


def test_polish_disabled_without_key_is_noop():
    # 无 DEEPSEEK_API_KEY 时 polish=True 也应安全返回（不联网、不改变事实）
    import os
    os.environ.pop("DEEPSEEK_API_KEY", None)
    base = NarrativeEngine().build(_summary("sample_summary.json"), "x")
    polished = NarrativeEngine(polish=True).build(_summary("sample_summary.json"), "x")
    # 关键数字必须保留（防幻觉）
    assert "16.5%" in polished.full_text
    assert "16.5%" in base.full_text
