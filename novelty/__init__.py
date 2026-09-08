"""
novelty — 论文创新性分析引擎（论文创新性分析引擎）

设计依据: docs/novelty_analysis_engine_design.md + docs/innovation-tools-survey.md
定位: 增强人工对论文的深度理解（提取贡献点、与文献图谱对比、生成差异分析），
      **非全自动评判**。工具只输出"建议审视的差异点"与可追溯证据，不下终审结论。

数据流（与设计文档 §1 对齐）:
    PDF/解析结果 → 抽取模块 → 图谱查询模块 → 对比模块 → 报告生成模块 → 辅助分析报告

模块:
    schemas.py     数据模型（pydantic）
    extractor.py   抽取模块: 四维度拆解 + 贡献句/声明抽取（LLM + 启发式）
    corpus.py      本地快照知识图谱: 加载 data/parsed 与 summaries
    embedder.py    表示引擎: SPECTER2 / MiniLM / TF-IDF / 纯Python 后端（可降级）
    index.py       向量检索: faiss / numpy / linear 回退
    graph_query.py 图谱查询模块: 复用 CitationCollector(S2) + OpenAlex 适配器
    contrast.py    对比模块: FactReview 设计轴差异矩阵 + OpenNovelty 三态标签
    report.py      报告生成: 差异矩阵 + 证据片段 + 不下终审声明
    engine.py      编排: 串起上述模块产出 NoveltyReport
    analyzer_skill.py  注册为 novelty-analyze skill（接入 BaseSkill 工厂）
    cli.py         CLI 入口
    serve.py       FastAPI REST 服务（运维部署）
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["schemas", "engine"]

from . import schemas  # noqa: F401
