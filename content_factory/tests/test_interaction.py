"""Stage 5 交互组件测试：M9-M11 spec 产出 + 防幻觉绑定。"""

import json
from pathlib import Path

from content_factory.schemas import PaperSummary
from content_factory.interaction import InteractionFactory, build_all

FIX = Path(__file__).resolve().parent / "fixtures"


def _summary(name: str) -> PaperSummary:
    return PaperSummary(json.loads((FIX / name).read_text(encoding="utf-8")))


def test_code_playground_has_pseudocode_and_iframe():
    f = InteractionFactory()
    spec = f.code_playground(_summary("sample_summary.json"))
    assert spec.kind == "code_playground"
    assert "def propose_pipeline" in spec.payload["code"]
    assert "iframe" in spec.embed["html"]
    assert spec.payload["height"] == 600
    assert "method" in spec.bound_fields


def test_quiz_uses_key_result_as_correct():
    f = InteractionFactory()
    spec = f.quiz(_summary("sample_summary.json"))
    correct = [o for o in spec.payload["options"] if o["correct"]]
    assert len(correct) == 1
    # 正确选项文本应来自关键结果（Recall@200 16.5%）
    assert "16.5%" in correct[0]["text"]
    assert "key_result" in spec.bound_fields


def test_poll_derived_from_problem():
    f = InteractionFactory()
    spec = f.poll(_summary("sample_summary.json"))
    assert spec.kind == "poll"
    assert spec.payload["question"]
    assert "problem" in spec.bound_fields


def test_param_slider_declares_range():
    f = InteractionFactory()
    spec = f.param_slider(_summary("sample_summary.json"))
    sl = spec.payload["sliders"][0]
    assert sl["min"] <= sl["value"] <= sl["max"]
    assert "idyll" in spec.embed["html"]


def test_build_all_returns_four_interactions():
    specs = build_all(_summary("sample_summary.json"))
    assert len(specs) == 4
    assert {sp.kind for sp in specs} == {
        "code_playground", "quiz", "poll", "param_slider"
    }
