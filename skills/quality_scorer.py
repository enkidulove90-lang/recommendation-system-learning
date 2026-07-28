"""
skills/quality_scorer.py — A3 论文质量评分技能

基于多维度指标对论文进行质量评分，决定是否触发完整分析（含图谱可视化）。

评分维度:
  1. 引用网络深度 (0-1) — 引用链是否清晰
  2. 引用数量      (0-1) — 被引次数归一化
  3. 合作网络广度  (0-1) — 多机构/多作者参与
  4. 主题新颖度    (0-1) — 与已发布论文主题重叠度（越低越新颖）
  5. 内容完整度    (0-1) — PDF 解析是否完整

阈值: >= 0.7 → full_analysis, < 0.7 → basic_only
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill("quality-score")
class QualityScorer(BaseSkill):
    """
    论文质量评分器。

    基于 AcademicGraph 和论文摘要，计算多维度质量评分，
    决定是否触发完整的分析增强流程（叙事生成 + 图谱可视化）。

    使用示例:
        scorer = QualityScorer()
        result = scorer.execute(
            arxiv_id="2605.28175",
            academic_graph={...},
            summary={"main_contribution": "...", ...},
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._threshold: float = kwargs.get("threshold", settings.QUALITY_THRESHOLD)

    @property
    def is_ready(self) -> bool:
        return True  # 纯计算，不需要外部依赖

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        计算论文质量评分。

        参数:
            arxiv_id       (str): arXiv ID
            academic_graph (dict): AcademicGraph 数据
            summary        (dict): 论文摘要
            output_dir     (str): 输出目录

        返回:
            {
                "score": float,
                "dimensions": {...},
                "threshold_pass": bool,
                "decision": "full_analysis" | "basic_only",
                "reason": str,
                "score_path": str,
                "error": None,
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        academic_graph: dict = kwargs.get("academic_graph", {})
        summary: dict = kwargs.get("summary", {})
        output_dir: str = kwargs.get("output_dir", "")

        if not arxiv_id or not academic_graph:
            return {
                "score": 0.0,
                "dimensions": {},
                "threshold_pass": False,
                "decision": "basic_only",
                "reason": "Missing arxiv_id or academic_graph",
                "error": "Missing required parameters",
            }

        if not output_dir:
            output_dir = str(settings.DATA_DIR / "graphs" / arxiv_id)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        try:
            # 计算各维度得分
            dims = {
                "citation_depth": self._score_citation_depth(academic_graph),
                "citation_count": self._score_citation_count(academic_graph),
                "collaboration_breadth": self._score_collaboration(academic_graph),
                "topic_novelty": self._score_topic_novelty(academic_graph),
                "content_completeness": self._score_content_completeness(summary),
            }

            # 加权综合得分
            weights = {
                "citation_depth": 0.25,
                "citation_count": 0.20,
                "collaboration_breadth": 0.15,
                "topic_novelty": 0.25,
                "content_completeness": 0.15,
            }
            overall = sum(dims[k] * weights[k] for k in dims)
            overall = round(min(overall, 1.0), 2)

            threshold_pass = overall >= self._threshold
            decision = "full_analysis" if threshold_pass else "basic_only"

            # 生成理由
            strengths = [k for k, v in dims.items() if v >= 0.7]
            weaknesses = [k for k, v in dims.items() if v < 0.4]
            reason_parts = []
            if strengths:
                reason_parts.append(f"High scores in: {', '.join(strengths)}")
            if weaknesses:
                reason_parts.append(f"Low scores in: {', '.join(weaknesses)}")
            reason = ". ".join(reason_parts) if reason_parts else "Average across all dimensions"

            result = {
                "score": overall,
                "dimensions": dims,
                "threshold_pass": threshold_pass,
                "decision": decision,
                "reason": reason,
                "scored_at": datetime.now().isoformat(),
                "arxiv_id": arxiv_id,
                "error": None,
            }

            # 保存
            score_path = out_path / "quality_score.json"
            score_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            result["score_path"] = str(score_path)

            logger.info(
                "[QualityScorer] %s → score=%.2f, decision=%s (%s)",
                arxiv_id, overall, decision, reason,
            )
            return result

        except Exception as exc:
            logger.error("[QualityScorer] Failed: %s", exc)
            return {
                "score": 0.5,
                "dimensions": {},
                "threshold_pass": False,
                "decision": "basic_only",
                "reason": f"Scoring error: {exc}",
                "error": str(exc),
            }

    # ------------------------------------------------------------------
    # 各维度评分实现
    # ------------------------------------------------------------------

    @staticmethod
    def _score_citation_depth(graph: dict) -> float:
        """
        引用网络深度评分。

        衡量引用链的完整性和层次结构：
          - 有引用 + 被引双向关系 → 高分
          - 引用年份跨度 > 5年 → 加分
          - 节点数量 > 10 → 加分
        """
        cg = graph.get("citation_graph", {})
        nodes = cg.get("nodes", [])
        edges = cg.get("edges", [])

        if not nodes or not edges:
            return 0.2

        score = 0.3

        # 节点数量
        if len(nodes) >= 30:
            score += 0.3
        elif len(nodes) >= 10:
            score += 0.2
        elif len(nodes) >= 3:
            score += 0.1

        # 边的多样性
        edge_types = set(e.get("relation", "") for e in edges)
        if len(edge_types) >= 3:
            score += 0.2
        elif len(edge_types) >= 2:
            score += 0.1

        # 年份跨度
        stats = graph.get("statistics", {})
        span = stats.get("reference_year_span", (2024, 2024))
        if span[1] - span[0] >= 10:
            score += 0.2
        elif span[1] - span[0] >= 5:
            score += 0.1

        return min(score, 1.0)

    @staticmethod
    def _score_citation_count(graph: dict) -> float:
        """
        引用数量评分。

        参考文献数量 + 被引次数归一化。
        """
        stats = graph.get("statistics", {})

        total_refs = stats.get("total_references", 0)
        total_cits = stats.get("total_citations", 0)

        # 参考文献数量归一化 (0-50 → 0-1)
        ref_score = min(total_refs / 40.0, 1.0) if total_refs > 0 else 0.1

        # 被引次数归一化 (0-100 → 0-1)
        cit_score = min(total_cits / 20.0, 1.0) if total_cits > 0 else 0.1

        return round(ref_score * 0.5 + cit_score * 0.5, 2)

    @staticmethod
    def _score_collaboration(graph: dict) -> float:
        """
        合作网络广度评分。

        多机构/多作者参与 → 高分。
        """
        cn = graph.get("collaboration_network", {})
        nodes = cn.get("nodes", [])

        if not nodes:
            return 0.3

        # 统计机构和作者数量
        institutions = set(
            n.get("label", "") for n in nodes if n.get("type") == "institution"
        )
        authors = set(
            n.get("label", "") for n in nodes if n.get("type") == "author"
        )

        score = 0.3
        if len(institutions) >= 3:
            score += 0.4
        elif len(institutions) >= 2:
            score += 0.2

        if len(authors) >= 5:
            score += 0.3
        elif len(authors) >= 3:
            score += 0.2

        return min(score, 1.0)

    @staticmethod
    def _score_topic_novelty(graph: dict) -> float:
        """
        主题新颖度评分。

        source_paper 中 keywords 数量和质量反映主题聚焦度。
        这里用启发式方法：关键词越具体/越少 → 可能越新颖。
        实际上需要与已发布论文对比，这里是简化实现。
        """
        sp = graph.get("source_paper", {})
        keywords = sp.get("keywords", [])

        if not keywords:
            return 0.5  # 中性

        # 较多具体关键词 → 中等偏上新颖度
        if len(keywords) >= 5:
            return 0.8
        elif len(keywords) >= 3:
            return 0.7
        else:
            return 0.5

    @staticmethod
    def _score_content_completeness(summary: dict) -> float:
        """
        内容完整度评分。

        检查摘要是否包含关键字段。
        """
        if not summary:
            return 0.2

        score = 0.2
        checks = [
            summary.get("main_contribution"),
            summary.get("innovation_points"),
            summary.get("experimental_results"),
            summary.get("methodology"),
        ]
        for check in checks:
            if check:
                if isinstance(check, list) and len(check) > 0:
                    score += 0.2
                elif isinstance(check, str) and len(check) > 20:
                    score += 0.2

        return min(score, 1.0)
