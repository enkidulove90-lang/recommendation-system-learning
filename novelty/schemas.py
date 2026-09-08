"""
novelty/schemas.py — 创新性分析引擎数据模型

所有结构均基于 pydantic v2，便于序列化（JSON 报告）与下游消费。
设计约束: 工具只给证据，不下终审结论 —— 因此 NoveltyReport 不含 "novel/not novel" 字段。
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 抽取模块输出
# ---------------------------------------------------------------------------

class ClaimType(str, Enum):
    """声明/主张的类型（用于后续证据溯源）。"""
    METHODOLOGICAL = "methodological"   # 方法学主张（提出 X 方法/框架）
    EMPIRICAL = "empirical"             # 实证主张（在 Y 上取得提升）
    THEORETICAL = "theoretical"         # 理论主张
    POSITIONAL = "positional"           # 立场/观点主张


class Claim(BaseModel):
    """单条声明/主张。"""
    text: str = Field(..., description="声明原文片段")
    claim_type: ClaimType = Field(ClaimType.METHODOLOGICAL)
    section: str = Field(default="", description="所在章节（背景/方法/实验/声明）")


class ContributionExtraction(BaseModel):
    """四维度拆解 + 贡献句 + 关键主张。"""
    arxiv_id: str = Field(default="", description="arXiv ID（可为空，若仅给文本）")
    title: str = Field(default="", description="论文标题")
    core_task: str = Field(default="", description="核心任务（一句话）")
    background: str = Field(default="", description="背景/问题动机")
    method: str = Field(default="", description="方法/技术路线")
    experiments: str = Field(default="", description="实验/评估设置")
    contributions: list[str] = Field(default_factory=list, description="贡献点列表")
    claims: list[Claim] = Field(default_factory=list, description="关键主张列表")
    extraction_method: str = Field(default="heuristic", description="heuristic | llm | hybrid")
    source_chars: int = Field(default=0, description="抽取所用源文本长度")


# ---------------------------------------------------------------------------
# 图谱查询 / 邻域
# ---------------------------------------------------------------------------

class NeighborSource(str, Enum):
    CORPUS = "corpus"               # 本地快照语料（嵌入近邻）
    SEMANTIC_SCHOLAR = "semantic_scholar"
    OPENALEX = "openalex"
    PDF_REFS = "pdf_refs"


class NeighborPaper(BaseModel):
    """一篇邻域论文（与目标论文相关的候选对比对象）。"""
    arxiv_id: str = Field(default="", description="arXiv ID（可能为空）")
    title: str = Field(default="")
    year: Optional[int] = Field(default=None)
    relation: str = Field(default="similar", description="关系描述（cites/cited_by/similar/extends）")
    similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="与目标论文的语义相似度")
    source: NeighborSource = Field(default=NeighborSource.CORPUS)
    citation_count: int = Field(default=0)
    url: str = Field(default="")


# ---------------------------------------------------------------------------
# 对比模块输出（差异矩阵 + 三态标签）
# ---------------------------------------------------------------------------

class NoveltyLabel(str, Enum):
    """OpenNovelty 式三态标签 —— 替代二元"新颖/不新颖"判定。"""
    CAN_REFUTE = "can_refute"           # 有证据显示存在明确差异/可对照
    CANNOT_REFUTE = "cannot_refute"     # 有证据显示做法高度相似、难言差异
    UNCLEAR = "unclear"                 # 证据不足，无法判定


class DifferencePoint(BaseModel):
    """设计轴上的一个差异点（FactReview 设计轴定位矩阵的一格）。"""
    axis: str = Field(..., description="设计轴（如 对齐方式 / 损失项 / 评估协议）")
    target_value: str = Field(default="", description="目标论文在该轴的值")
    neighbor_value: str = Field(default="", description="邻域论文在该轴的值")
    difference: str = Field(default="", description="差异的自然语言描述")
    label: NoveltyLabel = Field(default=NoveltyLabel.UNCLEAR)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: str = Field(default="", description="证据片段（来自原文/摘要，禁止无引用断言）")
    neighbor_title: str = Field(default="", description="对比对象标题（便于溯源）")


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------

class NoveltyReport(BaseModel):
    """最终辅助分析报告。注意: 不含任何 'novel/not novel' 终审字段。"""
    arxiv_id: str = Field(default="")
    title: str = Field(default="")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    engine_version: str = Field(default="novelty-0.1.0")

    extraction: ContributionExtraction = Field(default_factory=ContributionExtraction)
    neighbors: list[NeighborPaper] = Field(default_factory=list)
    difference_matrix: list[DifferencePoint] = Field(default_factory=list)

    summary_note: str = Field(default="", description="机器生成的差异点速览（非结论）")
    disclaimer: str = Field(
        default=(
            "本工具仅辅助人工理解：输出为可追溯的差异点与证据片段，"
            "不做'新颖/不新颖'终审判定。最终判断由人工基于证据作出。"
        )
    )

    # 运维/调试字段
    meta: dict = Field(default_factory=dict, description="运行元数据（嵌入后端、在线源、耗时等）")
