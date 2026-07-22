"""
crawler/arxiv_crawler.py — arXiv 爬取编排器

协调各 skill 完成端到端的论文爬取流程:
  1. 按主题搜索论文 (ArxivSearcher)
  2. 元数据清洗增强 (MetadataExtractor)
  3. 保存结果到本地文件 (PaperStore)
  4. (可选) PDF 全文解析 (PDFParser)

所有 skill 均通过工厂函数注入，方便替换或 mock 测试。
"""

from __future__ import annotations

import logging
import time
from typing import Any

from tqdm import tqdm

from config import settings
from skills.base_module import get_skill, BaseSkill
from storage.paper_store import PaperStore

logger = logging.getLogger(__name__)


class ArxivCrawler:
    """
    arXiv 论文爬取编排器。

    使用示例:
        crawler = ArxivCrawler()
        crawler.run_all_topics()
        # 或按单个主题
        crawler.run_topic("agent-recommendation", max_results=30)
    """

    def __init__(self) -> None:
        self._searcher: BaseSkill = get_skill("arxiv-search")
        self._extractor: BaseSkill = get_skill("metadata-extract")
        self._store: PaperStore = PaperStore()

        # PDF 解析是可选步骤
        self._pdf_parser: BaseSkill | None = None
        try:
            parser = get_skill("pdf-parse")
            if parser.is_ready:
                self._pdf_parser = parser
                logger.info("MinerU PDF parser is ready.")
            else:
                logger.info("MinerU not configured; skipping PDF parse.")
        except Exception:
            logger.info("PDF parser not registered; skipping PDF parse.")

    # ------------------------------------------------------------------
    # 公共方法
    # ------------------------------------------------------------------

    def run_all_topics(self) -> dict[str, Any]:
        """
        遍历 settings.SEARCH_TOPICS 中的所有主题，
        逐一执行爬取，汇总结果。

        返回:
            {"topic_name": {"results": [...], "total": int}, ...}
        """
        all_results: dict[str, Any] = {}
        topics = settings.SEARCH_TOPICS

        for topic_name, query in topics.items():
            logger.info("=== Starting topic: %s ===", topic_name)
            try:
                result = self.run_topic(
                    topic_name=topic_name,
                    query=query,
                    max_results=settings.MAX_RESULTS_PER_QUERY,
                    start_year=settings.START_YEAR,
                    parse_pdf=False,  # 全量跑时不默认解析 PDF
                )
                all_results[topic_name] = result
            except Exception as exc:
                logger.error("Topic '%s' failed: %s", topic_name, exc)
                all_results[topic_name] = {"error": str(exc)}

        # 汇总统计
        total_papers = sum(
            v.get("total", 0) for v in all_results.values() if "error" not in v
        )
        logger.info(
            "All topics complete | topics=%d total_papers=%d",
            len(topics), total_papers,
        )

        # 保存汇总报告
        self._store.save_summary(all_results)

        return all_results

    def run_topic(
        self,
        topic_name: str,
        query: str | None = None,
        max_results: int | None = None,
        start_year: int | None = None,
        parse_pdf: bool = False,
    ) -> dict[str, Any]:
        """
        爬取单个主题。

        参数:
            topic_name: 主题标识符（用于命名输出文件）
            query:      arXiv 查询字符串；不传则从 SEARCH_TOPICS 获取
            max_results:单次搜索最大结果数
            start_year: 年份下限
            parse_pdf:  是否逐篇解析 PDF

        返回:
            {"results": [...], "total": int, "topic": str}
        """
        if query is None:
            query = settings.SEARCH_TOPICS.get(topic_name)
            if query is None:
                raise ValueError(f"Unknown topic '{topic_name}'.")

        if max_results is None:
            max_results = settings.MAX_RESULTS_PER_QUERY
        if start_year is None:
            start_year = settings.START_YEAR

        # ---------- Step 1: 搜索 ----------
        logger.info("[%s] Step 1/3: Searching arXiv ...", topic_name)
        search_result = self._searcher.execute(
            query=query,
            max_results=max_results,
            start_year=start_year,
        )
        papers: list[dict[str, Any]] = search_result.get("results", [])
        logger.info("[%s] Found %d papers.", topic_name, len(papers))

        if not papers:
            return {"results": [], "total": 0, "topic": topic_name}

        # ---------- Step 2: 元数据提取 ----------
        logger.info("[%s] Step 2/3: Extracting metadata ...", topic_name)
        extract_result = self._extractor.execute(
            mode="refine",
            papers=papers,
        )
        cleaned: list[dict[str, Any]] = extract_result.get("results", [])
        logger.info(
            "[%s] Metadata done | valid=%d invalid=%d",
            topic_name, extract_result["valid"], extract_result["invalid"],
        )

        # ---------- Step 3: 保存 ----------
        logger.info("[%s] Step 3/3: Saving results ...", topic_name)
        self._store.save_topic(topic_name, cleaned)

        # ---------- Step 4 (可选): PDF 解析 ----------
        if parse_pdf and self._pdf_parser:
            logger.info("[%s] Optional: Parsing PDFs ...", topic_name)
            for paper in tqdm(cleaned, desc=f"PDF [{topic_name}]"):
                pdf_url = paper.get("pdf_url", "")
                if not pdf_url:
                    continue
                parse_result = self._pdf_parser.execute(
                    pdf_url=pdf_url,
                    arxiv_id=paper.get("arxiv_id", ""),
                )
                paper["pdf_content"] = parse_result.get("content")
                time.sleep(1.0)  # 控制 API 速率

        return {"results": cleaned, "total": len(cleaned), "topic": topic_name}
