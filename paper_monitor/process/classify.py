"""主题分类（硬过滤）：OpenAlex 三级 topics 命中 RecSys/AI 才入推荐流。

设计文档§1/§5：叶子 topic 精确匹配、父 topic 保召回。
allowlist 为小写子串关键词；任一 topic 的 display_name 或 parent_display_name 命中即过。
"""
from __future__ import annotations

from ..config import Config, get_config
from ..models import Paper


def _topic_hits(paper: Paper, allowlist: list[str]) -> list[str]:
    hits: list[str] = []
    for t in paper.topics:
        name = (t.display_name or "").lower()
        parent = (t.parent_display_name or "").lower()
        for term in allowlist:
            if (term in name) or (term in parent) or (name and name in term):
                hits.append(term)
                break
    return hits


def matches_topic(paper: Paper, allowlist: list[str] | None = None) -> bool:
    if not allowlist:
        cfg = get_config()
        allowlist = cfg.topic_allowlist
    return len(_topic_hits(paper, allowlist)) > 0


def classify(
    papers: list[Paper],
    allowlist: list[str] | None = None,
    enable: bool = True,
    config: Config | None = None,
) -> tuple[list[Paper], list[Paper]]:
    """返回 (kept, dropped)。enable=False 时全部保留（仅标记）。"""
    cfg = config or get_config()
    terms = allowlist or cfg.topic_allowlist
    kept, dropped = [], []
    for p in papers:
        if enable and not matches_topic(p, terms):
            dropped.append(p)
        else:
            kept.append(p)
    return kept, dropped
