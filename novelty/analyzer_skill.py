"""
novelty/analyzer_skill.py — 注册为 novelty-analyze skill

接入既有 BaseSkill 工厂（skills/base_module.py），使创新性分析引擎可像
citation-collect / graph-build 一样被统一调度。execute(arxiv_id=...) 返回
报告 dict，并把 Markdown / JSON 落盘到 data/novelty_reports/。

LLM 增强: 若 .env 配置了 DEEPSEEK_API_KEY，则惰性加载 DeepSeekSummarizer
并包装为 Extractor 的可选 llm；否则纯启发式运行。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from skills.base_module import BaseSkill, register_skill

from .engine import NoveltyEngine, make_deepseek_llm
from .report import ReportGenerator

logger = logging.getLogger(__name__)


@register_skill("novelty-analyze")
class NoveltyAnalyzer(BaseSkill):
    """论文创新性辅助分析 skill。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._engine: NoveltyEngine | None = None

    def _build_engine(self, **kwargs) -> NoveltyEngine:
        from config import settings
        data_dir = kwargs.get("data_dir") or settings.DATA_DIR
        embedder = kwargs.get("embedder", "auto")
        use_online = kwargs.get("use_online", True)
        top_k = int(kwargs.get("top_k", 10))

        llm = None
        if use_online and settings.DEEPSEEK_API_KEY:
            try:
                from skills.deepseek_summarizer import DeepSeekSummarizer
                llm = make_deepseek_llm(DeepSeekSummarizer())
            except Exception as exc:
                logger.warning("[novelty-analyze] DeepSeek wrapper failed: %s", exc)

        return NoveltyEngine(
            data_dir=data_dir,
            embedder_kind=embedder,
            use_s2=use_online,
            use_openalex=use_online,
            top_k=top_k,
            llm=llm,
        )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        arxiv_id: str = kwargs.get("arxiv_id", "")
        if not arxiv_id:
            return {"error": "arxiv_id is required", "report": None}
        if self._engine is None:
            self._engine = self._build_engine(**kwargs)

        report = self._engine.analyze(arxiv_id)
        md, js = ReportGenerator().generate(report)

        out_dir = Path(kwargs.get("output_dir", "data/novelty_reports"))
        out_dir.mkdir(parents=True, exist_ok=True)
        md_path = out_dir / f"{arxiv_id}.md"
        json_path = out_dir / f"{arxiv_id}.json"
        md_path.write_text(md, encoding="utf-8")
        json_path.write_text(js, encoding="utf-8")

        return {
            "arxiv_id": arxiv_id,
            "report": report.model_dump(),
            "markdown_path": str(md_path),
            "json_path": str(json_path),
            "error": None,
        }
