"""PaperSummary 抽取层测试：双 schema 兼容 + 防幻觉阻断。"""

import json
from pathlib import Path

import pytest

from content_factory.schemas import (
    InsufficientSourceError,
    PaperSummary,
    find_summary_path,
    load_summary,
)

FIX = Path(__file__).resolve().parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def test_simpler_schema_extracts_four_pillars():
    s = PaperSummary(_load("sample_summary.json"))
    assert s.title_zh == "延迟异步检索增强召回"
    assert "RADAR" in s.method
    assert "16.5%" in s.key_result
    assert s.problem  # 钩子动机来自 methodology/main_contribution


def test_11dim_schema_extracts_four_pillars():
    s = PaperSummary(_load("sample_11dim.json"))
    assert "门控融合" in s.method
    assert "0.088" in s.key_result
    assert "稀疏" in s.limitations


def test_missing_method_blocks_generation():
    raw = {"title": "X", "main_contribution": "y", "experimental_results": "z"}
    with pytest.raises(InsufficientSourceError) as exc:
        PaperSummary(raw)
    assert "method" in str(exc.value)


def test_missing_result_blocks_generation():
    raw = {"title": "X", "methodology": "m"}
    with pytest.raises(InsufficientSourceError):
        PaperSummary(raw)


def test_find_summary_path_globs_chinese_name(tmp_path):
    # 模拟 data/summaries/<id>_中文_title_summary.json 命名
    d = tmp_path / "data" / "summaries"
    d.mkdir(parents=True)
    p = d / "2506.07261_延迟异步检索增强召回_summary.json"
    p.write_text(json.dumps({"paper_id": "2506.07261"}), encoding="utf-8")
    found = find_summary_path("2506.07261", d)
    assert found == p


def test_load_summary_end_to_end(tmp_path):
    d = tmp_path / "data" / "summaries"
    d.mkdir(parents=True)
    (d / "2506.07261_X_summary.json").write_text(
        (FIX / "sample_summary.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    s, path = load_summary("2506.07261", d)
    assert isinstance(s, PaperSummary)
    assert path.name.startswith("2506.07261")
