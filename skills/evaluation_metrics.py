"""
skills/evaluation_metrics.py — 6 维推荐评价指标体系

对推荐结果进行多维度质量评估。

6 维指标:
  R1: 摘要准确度 (Summary Accuracy) — 摘要与原文的一致性
  R2: 图文一致性 (Figure-Text Consistency) — 图表描述与摘要的交叉校验
  R3: 分类覆盖度 (Classification Coverage) — 受控词表分类的完整度
  R4: 推荐多样性 (Recommendation Diversity) — 推荐结果的方法族多样性
  R5: 知识连通度 (Knowledge Connectivity) — 论文间 KG 路径连通性
  R6: Agent 路由准确度 (Router Accuracy) — 意图分类与 Agent 选择的匹配度
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

SUMMARIES_DIR = settings.DATA_DIR / "summaries"
PARSED_DIR = settings.DATA_DIR / "parsed"
JSONL_PATH = settings.DATA_DIR / "registry" / "papers.jsonl"
TAXONOMIES_PATH = settings.DATA_DIR / "registry" / "taxonomies.yaml"
LOG_DIR = settings.DATA_DIR / "logs"


@register_skill("evaluation-metrics")
class EvaluationMetrics(BaseSkill):
    """
    6 维推荐评价指标体系。

    使用示例:
        evaluator = EvaluationMetrics()
        result = evaluator.execute(
            recommendation_results=[...],  # AgentRouter 输出
            evaluate_all=True,              # 是否评估所有摘要
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._taxonomies: dict = {}
        self._classifications: dict[str, dict] = {}
        self._load_taxonomies()
        self._load_classifications()

    def _load_taxonomies(self) -> None:
        if TAXONOMIES_PATH.exists():
            try:
                self._taxonomies = yaml.safe_load(
                    TAXONOMIES_PATH.read_text(encoding="utf-8")
                )
            except Exception as e:
                logger.error("[Metrics] Failed to load taxonomies: %s", e)

    def _load_classifications(self) -> None:
        if JSONL_PATH.exists():
            for line in JSONL_PATH.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    aid = record.get("arxiv_id") or record.get("paper_id", "")
                    if aid:
                        self._classifications[aid] = record.get("classification", {})
                except json.JSONDecodeError:
                    continue

    @property
    def is_ready(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行 6 维评价指标计算。

        参数:
            recommendation_results (list): AgentRouter 的推荐结果列表
            evaluate_all           (bool): 是否评估所有摘要（R1/R2/R3），默认 True
            router_query           (str): 用户原始查询（用于 R6）

        返回:
            {
                "R1_summary_accuracy": float,
                "R2_figure_text_consistency": float,
                "R3_classification_coverage": float,
                "R4_recommendation_diversity": float,
                "R5_knowledge_connectivity": float,
                "R6_router_accuracy": float,
                "overall_score": float,
                "details": dict,
            }
        """
        rec_results: list = kwargs.get("recommendation_results", [])
        evaluate_all: bool = kwargs.get("evaluate_all", True)
        router_query: str = kwargs.get("router_query", "")

        metrics: dict[str, Any] = {}

        # R1: 摘要准确度
        if evaluate_all:
            metrics["R1_summary_accuracy"] = self._r1_summary_accuracy()
            metrics["R2_figure_text_consistency"] = self._r2_figure_text_consistency()
            metrics["R3_classification_coverage"] = self._r3_classification_coverage()

        # R4: 推荐多样性
        if rec_results:
            metrics["R4_recommendation_diversity"] = self._r4_recommendation_diversity(rec_results)
            metrics["R5_knowledge_connectivity"] = self._r5_knowledge_connectivity(rec_results)
        else:
            metrics["R4_recommendation_diversity"] = 0.0
            metrics["R5_knowledge_connectivity"] = 0.0

        # R6: Agent 路由准确度
        metrics["R6_router_accuracy"] = self._r6_router_accuracy(router_query, rec_results)

        # 综合得分
        valid_scores = [v for v in metrics.values() if isinstance(v, (int, float)) and v >= 0]
        metrics["overall_score"] = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        metrics["overall_score"] = round(metrics["overall_score"], 4)

        # 四舍五入
        for key in metrics:
            if isinstance(metrics[key], float):
                metrics[key] = round(metrics[key], 4)

        return metrics

    # ------------------------------------------------------------------
    # R1: 摘要准确度
    # ------------------------------------------------------------------

    def _r1_summary_accuracy(self) -> float:
        """
        评估摘要的字段完整度和 source 标注率。

        完整度 = 已填写字段数 / 总字段数
        Source 标注率 = 有 source 标注的维度数 / 总维度数
        """
        summary_files = list(SUMMARIES_DIR.glob("*_summary.json"))
        if not summary_files:
            return 0.0

        required_fields = [
            "title_zh", "title_en", "paper_type", "venue", "year",
            "one_line_summary", "problem_definition", "innovations",
            "modules", "training", "datasets", "benchmark",
            "related_papers", "reproducibility", "limitations",
        ]

        source_fields = ["problem_definition", "innovations", "modules", "training", "datasets", "benchmark"]

        total_completeness = 0.0
        total_source_rate = 0.0

        for sf in summary_files:
            try:
                data = json.loads(sf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            # 字段完整度
            filled = sum(1 for f in required_fields if data.get(f))
            completeness = filled / len(required_fields)

            # Source 标注率
            source_count = 0
            for sf_key in source_fields:
                field_val = data.get(sf_key, {})
                if isinstance(field_val, dict):
                    if field_val.get("source"):
                        source_count += 1
                elif isinstance(field_val, list):
                    for item in field_val:
                        if isinstance(item, dict) and item.get("source"):
                            source_count += 1
                            break

            source_rate = source_count / len(source_fields)

            total_completeness += completeness
            total_source_rate += source_rate

        n = len(summary_files)
        avg_completeness = total_completeness / n
        avg_source_rate = total_source_rate / n

        # R1 = 完整度 * 0.6 + source标注率 * 0.4
        return round(avg_completeness * 0.6 + avg_source_rate * 0.4, 4)

    # ------------------------------------------------------------------
    # R2: 图文一致性
    # ------------------------------------------------------------------

    def _r2_figure_text_consistency(self) -> float:
        """
        评估 _figures.json 与摘要的一致性。

        检查图表描述中的关键术语是否在摘要中出现。
        """
        from skills.vision_enhancer import VisionEnhancer
        enhancer = VisionEnhancer()

        consistency_scores = []
        folders = [d for d in PARSED_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")]

        for folder in folders:
            arxiv_id = folder.name.split("_")[0]
            figures_path = folder / f"{arxiv_id}_figures.json"
            summary_path = SUMMARIES_DIR / f"{arxiv_id}_summary.md"

            if not figures_path.exists() or not summary_path.exists():
                continue

            result = enhancer.cross_validate(str(summary_path), str(figures_path))
            if result.get("checked_figures", 0) > 0:
                # 一致性 = 1 - 问题数/检查数
                consistency = 1.0 - len(result.get("issues", [])) / result["checked_figures"]
                consistency_scores.append(max(0.0, consistency))

        if not consistency_scores:
            return 0.0

        return round(sum(consistency_scores) / len(consistency_scores), 4)

    # ------------------------------------------------------------------
    # R3: 分类覆盖度
    # ------------------------------------------------------------------

    def _r3_classification_coverage(self) -> float:
        """
        评估受控词表分类的覆盖度。

        覆盖度 = 有分类的论文数 / 总论文数 × 平均分类维度数 / 期望维度数
        """
        total_papers = 0
        classified_count = 0
        dimension_counts: list[int] = []

        expected_dimensions = 6  # research_directions, pipeline_stages, etc.

        # 统计有摘要的论文
        summary_files = list(SUMMARIES_DIR.glob("*_summary.json"))
        for sf in summary_files:
            try:
                data = json.loads(sf.read_text(encoding="utf-8"))
                aid = data.get("paper_id") or data.get("arxiv_id", "")
                if not aid:
                    aid = sf.stem.split("_")[0]
                if not aid:
                    continue
                total_papers += 1

                cls = self._classifications.get(aid, {})
                if cls:
                    classified_count += 1
                    # 计算非空维度数
                    non_empty = sum(1 for v in cls.values() if v)
                    dimension_counts.append(non_empty)
            except (json.JSONDecodeError, OSError):
                continue

        if total_papers == 0:
            return 0.0

        coverage_rate = classified_count / total_papers
        avg_dimensions = sum(dimension_counts) / len(dimension_counts) if dimension_counts else 0
        dimension_completeness = avg_dimensions / expected_dimensions

        return round(coverage_rate * 0.5 + dimension_completeness * 0.5, 4)

    # ------------------------------------------------------------------
    # R4: 推荐多样性
    # ------------------------------------------------------------------

    def _r4_recommendation_diversity(self, results: list) -> float:
        """
        评估推荐结果的方法族多样性。

        多样性 = Shannon 熵 / log2(N)
        """
        if not results:
            return 0.0

        # 收集所有推荐论文的方向
        directions = []
        for item in results:
            aid = item.get("arxiv_id", "")
            cls = self._classifications.get(aid, {})
            dirs = cls.get("research_directions", ["unknown"])
            directions.extend(dirs)

        if not directions:
            return 0.0

        # Shannon 熵
        counter = Counter(directions)
        n = len(directions)
        entropy = 0.0
        for count in counter.values():
            p = count / n
            entropy -= p * math.log2(p)

        # 归一化
        max_entropy = math.log2(len(counter)) if len(counter) > 1 else 1.0
        diversity = entropy / max_entropy if max_entropy > 0 else 0.0

        return round(diversity, 4)

    # ------------------------------------------------------------------
    # R5: 知识连通度
    # ------------------------------------------------------------------

    def _r5_knowledge_connectivity(self, results: list) -> float:
        """
        评估推荐结果中论文间的知识连通度。

        连通度 = 有共享实体的论文对数 / 总论文对数
        """
        if len(results) < 2:
            return 0.0

        # 加载所有摘要
        summaries: dict[str, dict] = {}
        for sf in SUMMARIES_DIR.glob("*_summary.json"):
            try:
                data = json.loads(sf.read_text(encoding="utf-8"))
                aid = data.get("paper_id", "")
                if aid:
                    summaries[aid] = data
            except (json.JSONDecodeError, OSError):
                continue

        # 提取每篇论文的实体集
        from skills.agents.kg_reasoner import KGReasoner
        entity_sets: dict[str, set] = {}
        for item in results:
            aid = item.get("arxiv_id", "")
            summary = summaries.get(aid, {})
            if summary:
                entity_sets[aid] = KGReasoner._get_paper_entities(aid, summary)

        # 计算连通对数
        connected_pairs = 0
        total_pairs = 0
        ids = list(entity_sets.keys())

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                total_pairs += 1
                if entity_sets[ids[i]] & entity_sets[ids[j]]:
                    connected_pairs += 1

        if total_pairs == 0:
            return 0.0

        return round(connected_pairs / total_pairs, 4)

    # ------------------------------------------------------------------
    # R6: Agent 路由准确度
    # ------------------------------------------------------------------

    def _r6_router_accuracy(self, query: str, results: list) -> float:
        """
        评估 Agent 路由的准确度。

        检查推荐结果中论文的 reason 是否与用户查询意图一致。
        """
        if not query or not results:
            return 0.5  # 无查询时给中性分

        query_lower = query.lower()
        query_terms = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-z]{3,}", query_lower))

        if not query_terms:
            return 0.5

        # 检查推荐理由中是否包含查询关键词
        match_count = 0
        for item in results:
            reason = item.get("reason", "").lower()
            if any(term in reason for term in query_terms):
                match_count += 1

        return round(match_count / len(results), 4) if results else 0.0

    # ------------------------------------------------------------------
    # 批量评估并生成报告
    # ------------------------------------------------------------------

    def evaluate_all(self) -> dict[str, Any]:
        """评估全部指标并生成报告。"""
        metrics = self.execute(evaluate_all=True)

        # 保存报告
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = LOG_DIR / f"evaluation_metrics_{timestamp}.json"

        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "summary_files_count": len(list(SUMMARIES_DIR.glob("*_summary.json"))),
            "classified_papers_count": len(self._classifications),
        }

        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("[Metrics] Report saved -> %s", report_path)

        return report
