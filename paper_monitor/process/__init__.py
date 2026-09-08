"""处理层：去重 / 主题分类 / 打分 / 重排。"""
from .dedup import dedup, cross_source_overlap
from .classify import classify, matches_topic
from .score import score_paper, score_all
from .rerank import rerank

__all__ = [
    "dedup", "cross_source_overlap",
    "classify", "matches_topic",
    "score_paper", "score_all",
    "rerank",
]
