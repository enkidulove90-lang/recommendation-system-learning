"""
skills/agents/__init__.py — 多 Agent 推荐模块

4 个专业化推荐 Agent:
  - DirectionMatcher (Agent A): 方向匹配
  - PipelineComplementer (Agent B): 管线互补
  - DatasetComparator (Agent C): 数据集共享
  - KGReasoner (Agent D): KG 推理
"""

from skills.agents.direction_matcher import DirectionMatcher
from skills.agents.pipeline_complementer import PipelineComplementer
from skills.agents.dataset_comparator import DatasetComparator
from skills.agents.kg_reasoner import KGReasoner

__all__ = [
    "DirectionMatcher",
    "PipelineComplementer",
    "DatasetComparator",
    "KGReasoner",
]
