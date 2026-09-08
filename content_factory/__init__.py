"""科研故事化内容工厂 — 端到端流水线（Stage 1–8 本地可工程化部分）。

设计来源：docs/content-factory-engineering.md（19 模块 / Stage 0–8）
           docs/content-strategy-research.md（27 个已验证工具）

本包负责「论文 11 维摘要 → 故事化草稿 → 标题工厂 → 多平台适配 →
可视化/交互 → 分发/A-B → 分析回收 → 发布审核包」，
对齐既有 redbook 发布体系（publish_queue 同构 JSON + content_hash[:32] 路径）。

防幻觉铁律：
- 规则层（narrative_engine / visualization / interaction）只用摘要原文事实填空，
  缺失必要字段即阻断（InsufficientSourceError）。
- LLM 层（可选 polish / 标题生成）只基于摘要事实润色或扩写，不得引入原文外数字。
- 依赖仅为标准库 + PyYAML；无需外部 API key 即可跑通规则层与全部单测。
"""

from .schemas import (
    FactoryResult,
    InsufficientSourceError,
    PaperSummary,
    StoryDraft,
    TitleVariant,
)
from .narrative_engine import NarrativeEngine
from .title_factory import TitleFactory
from .platforms import PlatformAdapter, load_platforms
from .visualization import VisualizationFactory, VizSpec, build_all as build_viz
from .interaction import InteractionFactory, InteractionSpec, build_all as build_ix
from .distribution import Distributor, DistributionJob, BufferAdapter, DevToAdapter, AppnestABAdapter
from .analytics import AnalyticsSpec, TitleABTest, EventSpec, EVENT_SCHEMA
from .factory import ContentFactory, write_package

__all__ = [
    "FactoryResult",
    "InsufficientSourceError",
    "PaperSummary",
    "StoryDraft",
    "TitleVariant",
    "NarrativeEngine",
    "TitleFactory",
    "PlatformAdapter",
    "load_platforms",
    "VisualizationFactory",
    "VizSpec",
    "build_viz",
    "InteractionFactory",
    "InteractionSpec",
    "build_ix",
    "Distributor",
    "DistributionJob",
    "BufferAdapter",
    "DevToAdapter",
    "AppnestABAdapter",
    "AnalyticsSpec",
    "TitleABTest",
    "EventSpec",
    "EVENT_SCHEMA",
    "ContentFactory",
    "write_package",
]
