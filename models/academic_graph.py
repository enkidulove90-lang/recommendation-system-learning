"""
models/academic_graph.py — 学术知识图谱数据模型

定义分析增强层的核心数据结构：引用关系、合作网络、时间线、质量评分。
所有分析工具的输出统一转换为此格式，所有下游消费者从此格式读取。

参考: docs/ANALYSIS_LAYER_DESIGN.md §4 数据模型定义
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ======================================================================
# 辅助模型
# ======================================================================

class Author(BaseModel):
    """论文作者信息。"""
    name: str = Field(..., description="作者姓名")
    institution: str = Field(default="", description="所属机构")
    is_corresponding: bool = Field(default=False, description="是否为通讯作者")


class GraphNode(BaseModel):
    """图谱节点（论文 / 机构 / 作者）。"""
    id: str = Field(..., description="节点唯一标识")
    label: str = Field(..., description="节点显示标签")
    type: str = Field(
        default="reference",
        description="节点类型: target | reference | citation | related | institution | author",
    )
    year: Optional[int] = Field(default=None, description="发表年份")
    authors: list[str] = Field(default_factory=list, description="作者列表")
    institution: str = Field(default="", description="所属机构")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="重要度 0-1")
    # 机构/作者节点特有
    paper_count: int = Field(default=1, description="相关论文数")
    research_focus: list[str] = Field(default_factory=list, description="研究方向")
    h_index_estimate: Optional[int] = Field(default=None, description="估算 h-index")


class GraphEdge(BaseModel):
    """图谱边（引用 / 合作 / 从属关系）。"""
    source: str = Field(..., description="源节点 ID")
    target: str = Field(..., description="目标节点 ID")
    relation: str = Field(
        default="cites",
        description="关系类型: cites | cited_by | extends | contrasts | uses_dataset | affiliated_with | co_author",
    )
    weight: float = Field(default=0.5, ge=0.0, le=1.0, description="边权重")
    description: str = Field(default="", description="关系简短说明")


class CitationGraph(BaseModel):
    """引用关系图。"""
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class CollaborationNetwork(BaseModel):
    """合作网络。"""
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class TimelineMilestone(BaseModel):
    """时间线里程碑。"""
    year: int = Field(..., description="年份")
    event: str = Field(..., description="事件描述")
    paper_ids: list[str] = Field(default_factory=list, description="关联论文 ID")
    type: str = Field(
        default="incremental",
        description="里程碑类型: foundation | breakthrough | incremental | application",
    )
    impact_description: str = Field(default="", description="影响力描述")


class Timeline(BaseModel):
    """论文时间线。"""
    target_paper_id: str = Field(..., description="目标论文 ID")
    milestones: list[TimelineMilestone] = Field(default_factory=list)
    span_years: tuple[int, int] = Field(default=(2020, 2026), description="时间跨度 (起始年, 终止年)")
    narrative: str = Field(default="", description="时间线叙述文本")


class TopicAnnotation(BaseModel):
    """主题标签。"""
    paper_id: str = Field(..., description="论文 ID")
    topics: list[dict] = Field(
        default_factory=list,
        description="主题列表，每项含 label (str) 和 confidence (float)",
    )


class Citation(BaseModel):
    """单条引用条目。"""
    title: str = Field(..., description="论文标题")
    title_normalized: str = Field(default="", description="归一化标题（小写+去标点，用于去重）")
    authors: list[str] = Field(default_factory=list)
    first_author_surname: str = Field(default="", description="第一作者姓氏")
    year: Optional[int] = Field(default=None, description="发表年份")
    arxiv_id: str = Field(default="", description="arXiv ID")
    doi: str = Field(default="", description="DOI")
    venue: str = Field(default="", description="发表会议/期刊")
    citation_count: int = Field(default=0, description="被引次数")
    relation_type: str = Field(
        default="cites",
        description="关系: cites | cited_by | extends | uses_dataset",
    )
    relation_description: str = Field(default="", description="引用关系说明")


class QualityScore(BaseModel):
    """论文质量评分。"""
    arxiv_id: str = Field(..., description="arXiv ID")
    overall_score: float = Field(default=0.5, ge=0.0, le=1.0, description="综合评分")
    dimensions: dict = Field(
        default_factory=lambda: {
            "citation_depth": 0.5,
            "citation_count": 0.5,
            "collaboration_breadth": 0.5,
            "topic_novelty": 0.5,
            "content_completeness": 0.5,
        },
        description="各维度评分",
    )
    threshold_pass: bool = Field(default=False, description="是否通过阈值")
    decision: str = Field(default="basic_only", description="决策: full_analysis | basic_only")
    reason: str = Field(default="", description="决策理由")
    scored_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="评分时间戳",
    )


# ======================================================================
# 核心模型 — AcademicGraph
# ======================================================================

class SourcePaper(BaseModel):
    """源论文元信息。"""
    arxiv_id: str = Field(..., description="arXiv ID")
    title: str = Field(default="", description="论文标题")
    year: Optional[int] = Field(default=None, description="发表年份")
    venue: str = Field(default="", description="发表会议/期刊")
    authors: list[Author] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list, description="关键词")
    research_area: str = Field(default="", description="研究领域")


class GraphStatistics(BaseModel):
    """图谱统计摘要。"""
    total_references: int = Field(default=0, description="参考文献总数")
    total_citations: int = Field(default=0, description="被引总数")
    total_related: int = Field(default=0, description="相关论文数")
    reference_year_span: tuple[int, int] = Field(
        default=(2020, 2026), description="引用年份跨度"
    )
    top_institutions: list[str] = Field(default_factory=list, description="Top 机构")
    avg_citation_year: float = Field(default=2024.0, description="平均引用年份")


class AcademicGraph(BaseModel):
    """
    学术知识图谱 — 分析增强层的核心数据结构。

    所有分析工具（A1-A5）的输出都转换为此格式，
    所有下游消费者（叙事生成、可视化、配图）都从此格式读取。
    """

    schema_version: str = Field(default="1.0", description="数据格式版本")
    generated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="生成时间 ISO 时间戳",
    )
    source_paper: SourcePaper = Field(default_factory=SourcePaper, description="源论文信息")

    # 图谱子结构
    citation_graph: CitationGraph = Field(default_factory=CitationGraph, description="引用关系图")
    collaboration_network: CollaborationNetwork = Field(
        default_factory=CollaborationNetwork, description="合作网络"
    )
    timeline: Timeline = Field(default_factory=Timeline, description="时间线")

    # 主题与统计
    topic_annotations: list[TopicAnnotation] = Field(default_factory=list, description="主题标签")
    statistics: GraphStatistics = Field(default_factory=GraphStatistics, description="统计摘要")

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "AcademicGraph":
        return cls(**data)
