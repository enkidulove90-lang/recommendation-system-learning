"""
config/settings.py — 全局配置管理

基于 python-dotenv 从 .env 文件加载配置项，
通过 `Settings` 单例统一暴露给项目内各模块使用。

使用方式:
    from config import settings
    api_key = settings.MINERU_API_KEY
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录（即 recommendation-system/）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 加载 .env 文件（若不存在则静默跳过）
_dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_dotenv_path, override=False)


class Settings:
    """
    应用配置单例。

    所有配置项均从环境变量读取，若未设置则回退到默认值。
    新增配置项时只需添加一个 @property，保持调用方无感知。
    """

    # ---- MinerU ----
    @property
    def MINERU_API_KEY(self) -> str:
        return os.getenv("MINERU_API_KEY", "")

    # ---- arXiv API ----
    @property
    def ARXIV_API_BASE(self) -> str:
        return os.getenv("ARXIV_API_BASE", "https://export.arxiv.org/api/query")

    # ---- 爬取控制 ----
    @property
    def REQUEST_INTERVAL(self) -> float:
        return float(os.getenv("REQUEST_INTERVAL", "3.0"))

    @property
    def MAX_RESULTS_PER_QUERY(self) -> int:
        return int(os.getenv("MAX_RESULTS_PER_QUERY", "50"))

    # ---- 输出 ----
    @property
    def OUTPUT_DIR(self) -> Path:
        raw = os.getenv("OUTPUT_DIR", "./output")
        path = Path(raw)
        if not path.is_absolute():
            path = PROJECT_ROOT / raw
        return path

    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    # ---- 搜索主题 2024+ ----
    @property
    def SEARCH_TOPICS(self) -> dict[str, str]:
        """
        返回 {主题名称: arXiv 搜索查询字符串} 的映射。

        四个核心主题:
        1. Agent 推荐 — Agent 技术与推荐系统的交叉研究
        2. 多模态推荐 — 利用图像/文本/视频等多模态信号的推荐
        3. 大模型召回 — LLM 参与候选生成 / 召回阶段
        4. 大模型排序 — LLM 参与预排序 / 排序 / 重排序阶段
        """
        return {
            "agent-recommendation": (
                'all:"agent" AND all:"recommendation system" '
                "AND cat:cs.IR"
            ),
            "multimodal-recommendation": (
                'all:"multimodal" AND all:"recommendation" '
                "AND cat:cs.IR"
            ),
            "llm-recall": (
                'all:"large language model" AND (all:"recall" OR all:"candidate generation") '
                'AND all:"recommendation" AND cat:cs.IR'
            ),
            "llm-ranking": (
                'all:"large language model" AND '
                '(all:"ranking" OR all:"re-ranking" OR all:"pre-ranking" OR all:"rerank") '
                'AND all:"recommendation" AND cat:cs.IR'
            ),
        }

    @property
    def START_YEAR(self) -> int:
        """只爬取该年份及之后发表的论文。"""
        return int(os.getenv("START_YEAR", "2024"))


# 全局单例
settings = Settings()
