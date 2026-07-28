"""
models/ — 数据模型定义

使用 Pydantic 定义论文、解析结果、摘要等核心数据结构。
"""

from models.paper import Paper
from models.parsed_content import ParsedContent
from models.summary import PaperSummary
from models.academic_graph import (
    AcademicGraph,
    Citation,
    CitationGraph,
    GraphNode,
    GraphEdge,
    Timeline,
    TimelineMilestone,
    QualityScore,
    CollaborationNetwork,
    SourcePaper,
    Author,
)

__all__ = [
    "Paper",
    "ParsedContent",
    "PaperSummary",
    "AcademicGraph",
    "Citation",
    "CitationGraph",
    "GraphNode",
    "GraphEdge",
    "Timeline",
    "TimelineMilestone",
    "QualityScore",
    "CollaborationNetwork",
    "SourcePaper",
    "Author",
]
