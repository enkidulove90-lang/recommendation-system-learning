"""
skills/metadata_extractor.py — 论文元数据提取技能

对已经拉取到的原始论文数据进行清洗、增强与验证。
支持两种模式:
  1. refine  — 从已有 raw_dict 中标准化元数据
  2. validate — 验证单篇论文的字段完整性

设计为可在爬取流水线中作为独立阶段调用，也可单独使用。
"""

from __future__ import annotations

import logging
from typing import Any

from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

# 一篇"合格"论文必须拥有的字段
REQUIRED_FIELDS: list[str] = [
    "title",
    "authors",
    "abstract",
    "published",
    "pdf_url",
    "arxiv_url",
]


@register_skill("metadata-extract")
class MetadataExtractor(BaseSkill):
    """
    论文元数据提取 / 清洗技能。

    提供字段补全、作者格式统一、摘要截断生成短摘要、
    以及字段完整性校验功能。

    使用示例:
        extractor = MetadataExtractor()
        result = extractor.execute(
            mode="refine",
            papers=[{"title": "...", ...}, ...],
        )
        cleaned_papers = result["results"]
    """

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行元数据提取。

        参数:
            mode   (str) : "refine" | "validate" — 操作模式
            papers (list): 论文字典列表

        返回:
            {
                "results": [<cleaned paper dict>, ...],
                "total": int,
                "valid": int,
                "invalid": int,
            }
        """
        mode: str = kwargs.get("mode", "refine")
        papers: list[dict[str, Any]] = kwargs.get("papers", [])

        if mode == "refine":
            cleaned = [self._refine_one(p) for p in papers]
        elif mode == "validate":
            cleaned = papers  # 不做修改
        else:
            raise ValueError(f"Unknown mode '{mode}', expected 'refine' or 'validate'.")

        valid_count = sum(1 for p in cleaned if self._is_valid(p))
        invalid_count = len(cleaned) - valid_count

        logger.info(
            "Metadata extraction done | mode=%s total=%d valid=%d invalid=%d",
            mode, len(cleaned), valid_count, invalid_count,
        )

        return {
            "results": cleaned,
            "total": len(cleaned),
            "valid": valid_count,
            "invalid": invalid_count,
        }

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _refine_one(paper: dict[str, Any]) -> dict[str, Any]:
        """对单篇论文进行清洗与增强。"""
        # --- 标题 ---
        title = (paper.get("title") or "").strip()
        # 去除 arXiv 标题中常见的尾部换行
        title = title.replace("\n", " ").replace("  ", " ")

        # --- 作者 ---
        authors = paper.get("authors", [])
        if isinstance(authors, str):
            # 有些数据源作者以字符串形式返回
            authors = [a.strip() for a in authors.split(",") if a.strip()]

        # --- 摘要 ---
        abstract = (paper.get("abstract") or "").strip()
        abstract = abstract.replace("\n", " ").replace("  ", " ")

        # --- 短摘要（前 200 字符）---
        short_abstract = abstract[:200] + "..." if len(abstract) > 200 else abstract

        # --- 时间 ---
        published = paper.get("published", "")
        year = paper.get("year")

        # --- 链接 ---
        arxiv_id = paper.get("arxiv_id", "")
        pdf_url = paper.get("pdf_url") or (f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "")
        arxiv_url = paper.get("arxiv_url") or (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "")

        return {
            **paper,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "short_abstract": short_abstract,
            "published": published,
            "year": year,
            "pdf_url": pdf_url,
            "arxiv_url": arxiv_url,
            "arxiv_id": arxiv_id,
        }

    @staticmethod
    def _is_valid(paper: dict[str, Any]) -> bool:
        """校验论文字段完整性。"""
        for field in REQUIRED_FIELDS:
            value = paper.get(field)
            if not value:
                return False
            # authors 必须非空列表
            if field == "authors" and isinstance(value, list) and len(value) == 0:
                return False
        return True
