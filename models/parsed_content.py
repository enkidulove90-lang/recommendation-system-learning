"""
models/parsed_content.py — 论文解析结果数据模型

MinerU 解析后的结构化数据。
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ParsedContent(BaseModel):
    """MinerU 解析一篇论文后的结构化结果。"""

    paper_id: str = Field(..., description="arXiv ID")
    markdown_path: str = Field(default="", description="本地 .md 文件路径")
    json_path: str = Field(default="", description="本地 .json 文件路径（结构化元数据）")
    parse_status: str = Field(default="pending", description="解析状态: pending|processing|success|failed")
    page_count: Optional[int] = Field(default=None, description="PDF 页数")
    parse_timestamp: str = Field(default="", description="解析完成时间戳")
    error_message: Optional[str] = Field(default=None, description="错误信息")

    # 解析统计
    text_length: int = Field(default=0, description="Markdown 文本总字符数")
    section_count: int = Field(default=0, description="章节数量")
    table_count: int = Field(default=0, description="表格数量")
    figure_count: int = Field(default=0, description="图片数量")

    def to_dict(self) -> dict:
        return self.model_dump()
