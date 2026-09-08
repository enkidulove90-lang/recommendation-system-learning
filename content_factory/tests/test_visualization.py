"""Stage 4 可视化叙事测试：M3-M5 spec 产出 + 防幻觉绑定。"""

import json
from pathlib import Path

from content_factory.schemas import PaperSummary
from content_factory.narrative_engine import NarrativeEngine
from content_factory.visualization import VisualizationFactory, build_all

FIX = Path(__file__).resolve().parent / "fixtures"


def _summary(name: str) -> PaperSummary:
    return PaperSummary(json.loads((FIX / name).read_text(encoding="utf-8")))


def _story(s: PaperSummary):
    return NarrativeEngine().build(s, "2506.07261")


def test_metric_bars_extracts_gain_from_key_result():
    f = VisualizationFactory()
    spec = f.metric_bars(_summary("sample_summary.json"))
    assert spec.kind == "metric_bar"
    assert spec.data["baseline"] == "8.1%"   # Recall@200 基线
    assert spec.data["proposed"] == "16.5%"  # 本文
    assert "key_result" in spec.bound_fields
    assert "<svg" in spec.embed["html"]


def test_learning_curve_uses_reported_endpoints():
    f = VisualizationFactory()
    spec = f.learning_curve(_summary("sample_summary.json"))
    pts = spec.data["points"]
    assert pts[0]["y"] == "8.1%" and pts[1]["y"] == "16.5%"
    assert spec.data["interpolation"].startswith("linear-between-reported-endpoints")
    assert "<svg" in spec.embed["html"]


def test_infographic_binds_four_pillars():
    f = VisualizationFactory()
    spec = f.infographic(_summary("sample_summary.json"))
    d = spec.data
    assert d["problem"] and d["method"] and d["key_result"]
    assert "problem" in spec.bound_fields and "method" in spec.bound_fields


def test_scroll_story_sections_from_draft():
    s = _summary("sample_summary.json")
    spec = VisualizationFactory().scroll_story(_story(s))
    assert spec.kind == "scroll_story"
    assert len(spec.data["sections"]) == 4
    assert "scrollytelling" in spec.embed["html"]


def test_build_all_returns_four_specs_with_story():
    s = _summary("sample_summary.json")
    specs = build_all(s, _story(s))
    assert len(specs) == 4
    assert {sp.kind for sp in specs} == {
        "metric_bar", "learning_curve", "infographic", "scroll_story"
    }
