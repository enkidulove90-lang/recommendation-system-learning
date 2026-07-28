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

# 项目根目录（即 recommendation-system-learning/）
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

    @property
    def MINERU_MODEL_VERSION(self) -> str:
        return os.getenv("MINERU_MODEL_VERSION", "vlm")

    @property
    def MINERU_POLL_INTERVAL(self) -> float:
        return float(os.getenv("MINERU_POLL_INTERVAL", "3.0"))

    @property
    def MINERU_POLL_MAX_RETRIES(self) -> int:
        return int(os.getenv("MINERU_POLL_MAX_RETRIES", "100"))

    # ---- DeepSeek ----
    @property
    def DEEPSEEK_API_KEY(self) -> str:
        return os.getenv("DEEPSEEK_API_KEY", "")

    @property
    def DEEPSEEK_MODEL(self) -> str:
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

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

    @property
    def START_YEAR(self) -> int:
        """只爬取该年份及之后发表的论文。"""
        return int(os.getenv("START_YEAR", "2024"))

    # ---- 输出 ----
    @property
    def OUTPUT_DIR(self) -> Path:
        raw = os.getenv("OUTPUT_DIR", "./output")
        path = Path(raw)
        if not path.is_absolute():
            path = PROJECT_ROOT / raw
        return path

    @property
    def DATA_DIR(self) -> Path:
        raw = os.getenv("DATA_DIR", "./data")
        path = Path(raw)
        if not path.is_absolute():
            path = PROJECT_ROOT / raw
        return path

    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    # ---- 搜索主题（扩展至 6 大方向，覆盖推荐系统前沿） ----
    @property
    def SEARCH_TOPICS(self) -> dict[str, str]:
        """
        返回 {主题名称: arXiv 搜索查询字符串} 的映射。

        六大核心方向，覆盖推荐系统前沿研究:
        1. LLM Agent 推荐 — Agent 技术与推荐系统的交叉
        2. 多模态推荐 — 融合图像/文本/视频等多模态信号
        3. 大模型召回/排序 — LLM 参与候选生成与精排
        4. 序列/会话推荐 — 用户行为序列建模
        5. 图神经网络推荐 — GNN 在推荐中的应用
        6. 可解释/公平推荐 — 推荐系统的可解释性与公平性
        """
        return {
            "agent-recommendation": (
                'all:"agent" AND all:"recommendation" '
                "AND (cat:cs.IR OR cat:cs.AI)"
            ),
            "multimodal-recommendation": (
                'all:"multimodal" AND all:"recommendation" '
                "AND cat:cs.IR"
            ),
            "llm-ranking-recall": (
                'all:"large language model" AND '
                'all:"recommendation" AND '
                '(all:"ranking" OR all:"recall" OR all:"rerank" OR all:"candidate") '
                "AND cat:cs.IR"
            ),
            "sequential-session": (
                'all:"sequential recommendation" OR all:"session-based recommendation" '
                "AND cat:cs.IR"
            ),
            "gnn-recommendation": (
                'all:"graph neural network" AND all:"recommendation" '
                "AND cat:cs.IR"
            ),
            "explainable-fair": (
                'all:"explainable recommendation" OR all:"fairness recommendation" '
                "AND cat:cs.IR"
            ),
        }

    # ---- 分析增强层 (Analysis Enhancement Layer) ----
    @property
    def ENABLE_ANALYSIS_LAYER(self) -> bool:
        """是否启用分析增强层。默认 True，可通过环境变量关闭。"""
        return os.getenv("ENABLE_ANALYSIS_LAYER", "true").lower() == "true"

    @property
    def ANALYSIS_TIME_BUDGET_MINUTES(self) -> int:
        """分析层总时间预算（分钟），超时则剩余论文降级处理。默认 45"""
        return int(os.getenv("ANALYSIS_TIME_BUDGET_MINUTES", "45"))

    @property
    def QUALITY_THRESHOLD(self) -> float:
        """质量评分阈值。>= 此值触发完整分析（含图谱可视化）。默认 0.7"""
        return float(os.getenv("QUALITY_THRESHOLD", "0.7"))

    @property
    def SEMANTIC_SCHOLAR_API_BASE(self) -> str:
        """Semantic Scholar API 端点。免费无需 Key。"""
        return os.getenv(
            "SEMANTIC_SCHOLAR_API_BASE",
            "https://api.semanticscholar.org/graph/v1",
        )

    @property
    def CITATION_CACHE_DAYS(self) -> int:
        """引用数据缓存天数。超过后重新采集。默认 7"""
        return int(os.getenv("CITATION_CACHE_DAYS", "7"))

    @property
    def GRAPH_CACHE_DAYS(self) -> int:
        """图谱数据缓存天数。超过后重建。默认 30"""
        return int(os.getenv("GRAPH_CACHE_DAYS", "30"))

    @property
    def MAX_ANALYSIS_PAPERS_PER_RUN(self) -> int:
        """每次运行最多触发完整分析的论文数。默认 5"""
        return int(os.getenv("MAX_ANALYSIS_PAPERS_PER_RUN", "5"))

    @property
    def GRAPH_VIZ_DPI(self) -> int:
        """图谱可视化 DPI。默认 150"""
        return int(os.getenv("GRAPH_VIZ_DPI", "150"))

    @property
    def GRAPH_VIZ_SIZE(self) -> tuple[int, int]:
        """图谱可视化尺寸 (width, height)。默认 (1200, 800)"""
        raw = os.getenv("GRAPH_VIZ_SIZE", "1200,800")
        parts = raw.split(",")
        return (int(parts[0].strip()), int(parts[1].strip()))

    # ---- 论文检索增强关键词 ----
    @property
    def EXTRA_SEARCH_QUERIES(self) -> list[dict[str, str]]:
        """
        额外的专项检索查询，用于补充前沿方向。
        每个查询获取 3-5 篇，确保总量 20-30 篇。
        """
        return [
            {
                "name": "llm-recommendation-survey",
                "query": (
                    'all:"survey" AND all:"recommendation" AND '
                    'all:"large language model" AND cat:cs.IR'
                ),
                "description": "大模型推荐综述",
            },
            {
                "name": "diffusion-recommendation",
                "query": (
                    'all:"diffusion" AND all:"recommendation" AND '
                    "cat:cs.IR"
                ),
                "description": "扩散模型推荐",
            },
            {
                "name": "contrastive-recommendation",
                "query": (
                    'all:"contrastive learning" AND all:"recommendation" '
                    "AND cat:cs.IR"
                ),
                "description": "对比学习推荐",
            },
            {
                "name": "reinforcement-recommendation",
                "query": (
                    'all:"reinforcement learning" AND all:"recommendation" '
                    "AND cat:cs.IR"
                ),
                "description": "强化学习推荐",
            },
        ]


# 全局单例
settings = Settings()
