"""重排：按综合 score 降序（设计文档§1 推荐流）。"""
from __future__ import annotations

from ..models import Paper


def rerank(papers: list[Paper]) -> list[Paper]:
    return sorted(papers, key=lambda p: p.score, reverse=True)
