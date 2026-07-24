"""
models/summary.py — 论文摘要/深度解读数据模型

DeepSeek 生成的论文结构化解读。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaperSummary(BaseModel):
    """DeepSeek 生成的论文深度解读。"""

    paper_id: str = Field(..., description="arXiv ID")
    title: str = Field(default="", description="论文标题")
    main_contribution: str = Field(default="", description="主要贡献")
    innovation_points: list[str] = Field(default_factory=list, description="创新点列表")
    benchmark_datasets: list[str] = Field(default_factory=list, description="使用的 Benchmark 和数据集")
    experimental_results: str = Field(default="", description="关键实验效果")
    agent_relevance: str = Field(default="", description="对推荐系统 Agent 开发的借鉴之处")
    methodology: str = Field(default="", description="方法论简述")
    full_summary_text: str = Field(default="", description="完整解读（Markdown 格式）")
    generated_at: str = Field(default="", description="生成时间戳")

    def to_dict(self) -> dict:
        return self.model_dump()
