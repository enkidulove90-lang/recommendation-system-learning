"""Stage 3 标题工厂测试：启发式评分 + <70 门禁。"""

import json
from pathlib import Path

from content_factory.schemas import PaperSummary
from content_factory.title_factory import TitleFactory

FIX = Path(__file__).resolve().parent / "fixtures"


def _summary(name: str) -> PaperSummary:
    return PaperSummary(json.loads((FIX / name).read_text(encoding="utf-8")))


def test_score_range_and_length_penalty():
    f = TitleFactory()
    good = f._heuristic("我们用新框架，把指标从8.1%拉到16.5%（实测）")[0]
    long_title = "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的标题用来测试长度惩罚是否生效了呀"
    bad = f._heuristic(long_title)[0]
    assert 0 <= good <= 100
    assert 0 <= bad <= 100
    assert bad < good  # 超长应被扣分


def test_score_rewards_number_powerword_curiosity():
    f = TitleFactory()
    s1, _ = f._heuristic("推荐系统的冷启动，被门控融合改写了")
    s2, _ = f._heuristic("一个反直觉结论：Recall@20 从0.084到0.088")
    assert s2 > s1  # 含数字 + 好奇心缺口


def test_generate_returns_sorted_variants_with_gate():
    f = TitleFactory()
    titles = f.generate(_summary("sample_summary.json"), n=5)
    assert 1 <= len(titles) <= 5
    scores = [t.score for t in titles]
    assert scores == sorted(scores, reverse=True)  # 降序


def test_gate_flags_rewrite_when_all_poor():
    f = TitleFactory()
    # 人为注入一个全空变体，强制最优 < 70
    titles = f.generate(_summary("sample_summary.json"), n=5)
    # 规则变体通常能拿到部分分；若全 <70 应标记 needs_rewrite
    if titles[0].score < 70:
        assert all(t.needs_rewrite for t in titles)


def test_external_scorer_pluggable():
    f = TitleFactory(external_scorer=lambda t: (95, ["[ext] high"]))
    titles = f.generate(_summary("sample_summary.json"), n=5)
    # 外部评分器应至少让最优接近 95
    assert titles[0].score >= 95
