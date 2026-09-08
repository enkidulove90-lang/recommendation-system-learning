"""去重：以 DOI / arXiv ID / OpenAlex ID 为归一主键（设计文档§3 口径铁律）。"""
from __future__ import annotations

from ..models import Paper


def dedup(papers: list[Paper]) -> list[Paper]:
    """按归一主键合并跨源记录（信号取较大者）。

    设计文档§3：OpenAlex ID 为实体主键，DOI/arXiv ID/S2 均回链到同一 Work。
    因此只要两条记录在任一标识符（DOI / arXiv / OpenAlex / 标题hash）上相同即合并，
    而非仅取单一优先级。
    """
    merged: list[Paper] = []
    index_of: dict[str, int] = {}  # 标识符 -> merged 下标

    for p in papers:
        keys = _keys_of(p)
        target = None
        for k in keys:
            if k in index_of:
                target = index_of[k]
                break
        if target is None:
            idx = len(merged)
            merged.append(p)
            for k in keys:
                index_of[k] = idx
        else:
            merged[target].merge(p)
            for k in keys:
                index_of.setdefault(k, target)
    return merged


def _keys_of(p: Paper) -> list[str]:
    keys: list[str] = []
    if p.doi:
        keys.append("doi:" + p.doi.lower().strip())
    if p.arxiv_id:
        keys.append("arxiv:" + p.arxiv_id.lower().strip())
    if p.id:
        keys.append("oa:" + p.id.lower().strip())
    if p.s2_corpus_id:
        keys.append("s2:" + p.s2_corpus_id.lower().strip())
    if not keys:
        import hashlib
        h = hashlib.md5(p.title.lower().strip().encode("utf-8")).hexdigest()[:12]
        keys.append("title:" + h)
    return keys


def cross_source_overlap(a: list[Paper], b: list[Paper]) -> float:
    """两源去重主键集合的 Jaccard 重叠率（设计测试：OpenAlex vs arXiv ≥ 95%）。"""
    set_a = {p.dedup_key() for p in a}
    set_b = {p.dedup_key() for p in b}
    if not set_a and not set_b:
        return 1.0
    inter = set_a & set_b
    union = set_a | set_b
    return len(inter) / len(union) if union else 0.0
