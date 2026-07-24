"""
models/paper.py — 论文数据模型

定义论文的核心元数据结构。
"""

from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class Paper(BaseModel):
    """一篇 arXiv 论文的完整元数据。"""

    arxiv_id: str = Field(..., description="arXiv ID，如 '2602.21756'")
    title: str = Field(..., description="论文标题")
    authors: list[str] = Field(default_factory=list, description="作者列表")
    abstract: str = Field(default="", description="摘要全文")
    short_abstract: str = Field(default="", description="短摘要（前200字符）")
    published_date: str = Field(default="", description="发布日期 YYYY-MM-DD")
    year: Optional[int] = Field(default=None, description="发表年份")
    categories: list[str] = Field(default_factory=list, description="arXiv 分类标签")
    primary_category: str = Field(default="", description="主分类")
    comment: str = Field(default="", description="备注信息")
    pdf_url: str = Field(default="", description="PDF 下载链接")
    arxiv_url: str = Field(default="", description="arXiv 页面链接")
    research_direction: str = Field(default="", description="研究方向标签")

    # 本地文件路径（下载/解析后填充）
    local_pdf_path: Optional[str] = Field(default=None, description="本地 PDF 文件路径")
    local_md_path: Optional[str] = Field(default=None, description="本地 Markdown 解析文件路径")
    local_json_path: Optional[str] = Field(default=None, description="本地 JSON 解析文件路径")
    local_summary_path: Optional[str] = Field(default=None, description="本地摘要文件路径")

    @property
    def chinese_title(self) -> str:
        """尝试从 comment 中提取中文标题，否则返回英文标题。"""
        return self.title

    def to_dict(self) -> dict:
        """转换为字典（兼容旧版 dict 接口）。"""
        return self.model_dump()
