"""
skills/arxiv_searcher.py — arXiv 论文搜索技能

使用官方 arxiv Python API 搜索论文。
支持按主题、年份、分类等条件过滤。

接口设计（动态可扩展）:
  - execute(query, max_results, start_year) -> {"results": [...], "total": int}
  - 新增搜索后端（如 Semantic Scholar）时，只需实现相同接口。
"""

from __future__ import annotations

import time
import logging
from typing import Any
from datetime import datetime, timezone

import arxiv
from arxiv import Search, SortCriterion, Result

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill("arxiv-search")
class ArxivSearcher(BaseSkill):
    """
    arXiv 论文搜索技能。

    封装 arxiv.Search API，提供分页、重试、速率限制等功能。
    搜索结果统一格式化为字典列表。

    使用示例:
        searcher = ArxivSearcher()
        result = searcher.execute(
            query='all:"recommendation system"',
            max_results=30,
            start_year=2024,
        )
        papers = result["results"]
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = arxiv.Client(
            page_size=min(settings.MAX_RESULTS_PER_QUERY, 100),
            delay_seconds=settings.REQUEST_INTERVAL,
        )

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行 arXiv 搜索。

        参数:
            query       (str): arXiv 搜索查询字符串。
            max_results (int): 最大返回数量，默认 50。
            start_year  (int): 发表年份下限，默认 2024。

        返回:
            {
                "results": [<paper dict>, ...],
                "total": int,
                "query": str,
            }
        """
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", settings.MAX_RESULTS_PER_QUERY)
        start_year = kwargs.get("start_year", settings.START_YEAR)

        if not query:
            raise ValueError("Search query must not be empty.")

        logger.info(
            "Searching arXiv | query='%s' max=%d year>=%d",
            query, max_results, start_year,
        )

        search = Search(
            query=query,
            max_results=max_results,
            sort_by=SortCriterion.SubmittedDate,
        )

        papers: list[dict[str, Any]] = []
        try:
            results: list[Result] = list(self._client.results(search))
        except Exception as exc:
            logger.error("arXiv API error: %s", exc)
            return {"results": [], "total": 0, "query": query, "error": str(exc)}

        for result in results:
            paper = self._result_to_dict(result)
            # 按年份过滤
            if paper["year"] is not None and paper["year"] < start_year:
                continue
            papers.append(paper)

        logger.info("arXiv search complete | returned=%d papers", len(papers))
        return {"results": papers, "total": len(papers), "query": query}

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _result_to_dict(result: Result) -> dict[str, Any]:
        """将 arxiv.Result 对象转换为标准化字典。

        最终包含的字段（对标参考论文 https://arxiv.org/abs/2503.21460）:
          - title        : 论文标题
          - authors      : 作者列表 (list[str])
          - abstract     : 摘要全文
          - published    : 发布日期 (YYYY-MM-DD 格式)
          - year         : 发表年份 (int)
          - pdf_url      : PDF 下载链接
          - arxiv_url    : arXiv 页面链接
          - arxiv_id     : arXiv ID (如 "2503.21460")
          - categories   : arXiv 分类标签
          - comment      : 备注信息
          - primary_category : 主分类
        """
        # 提取发表时间
        published: datetime | None = result.published
        pub_date: str = ""
        pub_year: int | None = None
        if published is not None:
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            pub_date = published.strftime("%Y-%m-%d")
            pub_year = published.year

        # 提取 arXiv ID（如 "2503.21460v2" -> "2503.21460"）
        arxiv_id_raw: str = result.get_short_id()
        arxiv_id: str = arxiv_id_raw.split("v")[0] if "v" in arxiv_id_raw else arxiv_id_raw

        return {
            "title": result.title.strip() if result.title else "",
            "authors": [str(a) for a in result.authors],
            "abstract": result.summary.strip().replace("\n", " ") if result.summary else "",
            "published": pub_date,
            "year": pub_year,
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
            "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
            "arxiv_id": arxiv_id,
            "categories": list(result.categories) if result.categories else [],
            "comment": (result.comment or "").strip(),
            "primary_category": result.primary_category or "",
        }
