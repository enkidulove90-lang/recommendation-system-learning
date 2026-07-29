"""
models/ — 数据模型定义

使用 Pydantic 定义论文、解析结果、摘要等核心数据结构。
"""

from models.paper import Paper
from models.parsed_content import ParsedContent
from models.research_profile import (
    EvidenceBundle,
    EvidenceItem,
    ProfileReview,
    ResearchProfileV2,
    ValidationIssue,
)
from models.research_graph import (
    LearningPath,
    LearningStep,
    ProfileRecommendationReport,
    RankedRecommendation,
    RelationEdge,
    RelationGraph,
    ScoreBreakdown,
)
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
    "AcademicGraph",
    "Author",
    "Citation",
    "CitationGraph",
    "CollaborationNetwork",
    "EvidenceBundle",
    "EvidenceItem",
    "GraphEdge",
    "GraphNode",
    "LearningPath",
    "LearningStep",
    "Paper",
    "PaperSummary",
    "ParsedContent",
    "ProfileReview",
    "ProfileRecommendationReport",
    "QualityScore",
    "RankedRecommendation",
    "RelationEdge",
    "RelationGraph",
    "ResearchProfileV2",
    "ScoreBreakdown",
    "SourcePaper",
    "Timeline",
    "TimelineMilestone",
    "ValidationIssue",
]
