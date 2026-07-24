"""
storage/paper_store.py — 论文数据持久化

将爬取结果按主题分别保存为 JSON 文件，
并提供去重、增量更新和汇总报告功能。

输出目录结构:
  output/
  ├── agent-recommendation/
  │   └── papers_2026-07-22.json
  ├── multimodal-recommendation/
  │   └── papers_2026-07-22.json
  ├── llm-recall/
  │   └── papers_2026-07-22.json
  ├── llm-ranking/
  │   └── papers_2026-07-22.json
  └── summary_2026-07-22.json
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import settings

logger = logging.getLogger(__name__)


class PaperStore:
    """
    论文存储管理器。

    提供按主题保存、去重、增量更新和汇总功能。
    所有输出写入 settings.OUTPUT_DIR 指定的目录。
    """

    def __init__(self) -> None:
        self._output_dir: Path = settings.OUTPUT_DIR
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 保存方法
    # ------------------------------------------------------------------

    def save_topic(self, topic_name: str, papers: list[dict[str, Any]]) -> Path:
        """
        将单个主题的论文列表保存为带时间戳的 JSON 文件。

        参数:
            topic_name: 主题标识符（如 "agent-recommendation"）
            papers:     论文字典列表

        返回:
            Path: 输出文件路径
        """
        topic_dir = self._output_dir / topic_name
        topic_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_path = topic_dir / f"papers_{timestamp}.json"

        output_data = {
            "topic": topic_name,
            "crawled_at": datetime.now().isoformat(),
            "total": len(papers),
            "papers": papers,
        }

        with open(file_path, "w", encoding="utf-8") as fh:
            json.dump(output_data, fh, ensure_ascii=False, indent=2)

        logger.info("Saved %d papers -> %s", len(papers), file_path)
        return file_path

    def save_summary(self, all_results: dict[str, Any]) -> Path:
        """
        保存跨主题汇总报告。

        参数:
            all_results: {topic_name: {"total": int, ...}, ...}

        返回:
            Path: 汇总文件路径
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_path = self._output_dir / f"summary_{timestamp}.json"

        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_topics": len(all_results),
            "total_papers": sum(
                v.get("total", 0) for v in all_results.values() if "error" not in v
            ),
            "topics": {
                name: {
                    "total": info.get("total", 0),
                    "error": info.get("error"),
                }
                for name, info in all_results.items()
            },
        }

        with open(file_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)

        logger.info("Saved summary -> %s", file_path)
        return file_path

    # ------------------------------------------------------------------
    # 去重 & 增量
    # ------------------------------------------------------------------

    @staticmethod
    def deduplicate(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        按 arxiv_id 去重，保留首次出现的记录。

        返回去重后的列表，顺序不变。
        """
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for paper in papers:
            aid = paper.get("arxiv_id", "")
            if aid and aid not in seen:
                seen.add(aid)
                unique.append(paper)
            elif not aid:
                # 没有 arxiv_id 的记录也保留（可能是元数据不完整）
                unique.append(paper)
        removed = len(papers) - len(unique)
        if removed:
            logger.info("Deduplication removed %d duplicate(s).", removed)
        return unique

    @staticmethod
    def merge_results(
        existing: list[dict[str, Any]],
        new: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        合并已有结果与新结果，按 arxiv_id 去重。

        新结果中的记录会覆盖已有记录中相同 arxiv_id 的条目。
        """
        merged: dict[str, dict[str, Any]] = {}
        for paper in existing:
            aid = paper.get("arxiv_id", "")
            if aid:
                merged[aid] = paper
        for paper in new:
            aid = paper.get("arxiv_id", "")
            if aid:
                merged[aid] = paper  # 新覆盖旧
        return list(merged.values())
