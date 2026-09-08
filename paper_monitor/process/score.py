"""打分排序：influentialCitationCount + upvotes + githubStars + cited_by_count + 兴趣匹配。

各信号 log1p 归一化到 0..1（按软上限 cap），加权求和（权重见 config.score_weights，和为 1）。
"""
from __future__ import annotations

import math

from ..config import Config, get_config
from ..models import Paper

# 各信号的软上限（用于 log1p 归一化）
_CAPS = {
    "influential_citation": 100.0,
    "upvotes": 100.0,
    "github_stars": 1000.0,
    "cited_by_count": 500.0,
}


def _norm(value: float | None, cap: float) -> float:
    if value is None or value <= 0:
        return 0.0
    return min(1.0, math.log1p(value) / math.log1p(cap))


def _interest_match(paper: Paper, profile: list[str]) -> float:
    if not profile:
        return 0.0
    text = (paper.title + " " + paper.abstract).lower()
    hits = sum(1 for kw in profile if kw and kw in text)
    return hits / len(profile)


def score_paper(
    paper: Paper,
    weights: dict | None = None,
    interest_profile: list[str] | None = None,
    config: Config | None = None,
) -> float:
    cfg = config or get_config()
    w = weights or cfg.score_weights
    profile = interest_profile if interest_profile is not None else cfg.interest_profile

    s_inf = _norm(paper.influential_citation_count, _CAPS["influential_citation"])
    s_up = _norm(paper.upvotes, _CAPS["upvotes"])
    s_star = _norm(paper.github_stars, _CAPS["github_stars"])
    s_cite = _norm(paper.cited_by_count, _CAPS["cited_by_count"])
    s_int = _interest_match(paper, profile)

    score = (
        w.get("influential_citation", 0) * s_inf
        + w.get("upvotes", 0) * s_up
        + w.get("github_stars", 0) * s_star
        + w.get("cited_by_count", 0) * s_cite
        + w.get("interest_match", 0) * s_int
    )
    return round(score, 6)


def score_all(papers: list[Paper], config: Config | None = None) -> list[Paper]:
    cfg = config or get_config()
    for p in papers:
        p.score = score_paper(p, config=cfg)
    return papers
