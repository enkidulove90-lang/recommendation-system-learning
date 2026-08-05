"""
skills/agents/direction_matcher.py — Agent A: 方向匹配 Agent

基于 research_direction + technical_paradigm 计算论文间方向相似度。
权重: topic_and_problem(0.30) + paradigm_and_modality(0.15) = 0.45

匹配策略:
  1. research_direction 标签交集（Jaccard 相似度）
  2. technical_paradigm 标签交集
  3. 标题/摘要关键词重叠（TF-IDF 简化版）
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

SUMMARIES_DIR = settings.DATA_DIR / "summaries"
JSONL_PATH = settings.DATA_DIR / "registry" / "papers.jsonl"

# Agent A 权重（来自 recommendation_weights.yaml + integration_design.md）
WEIGHT_TOPIC = 0.30
WEIGHT_PARADIGM = 0.15
AGENT_WEIGHT = WEIGHT_TOPIC + WEIGHT_PARADIGM  # 0.45


@register_skill("agent-direction-match")
class DirectionMatcher(BaseSkill):
    """
    Agent A: 方向匹配 Agent。

    基于 research_direction 和 technical_paradigm 标签计算论文间方向相似度。

    使用示例:
        agent = DirectionMatcher()
        result = agent.execute(
            seed_arxiv_id="2505.19525",
            top_k=10,
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._classifications: dict[str, dict] = {}
        self._summaries: dict[str, dict] = {}
        self._load_data()

    def _load_data(self) -> None:
        """加载 papers.jsonl 分类数据和 summaries JSON。"""
        # 加载分类（papers.jsonl 使用 paper_id 字段）
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

        # 加载摘要（文件名格式: {arxiv_id}_{title}_summary.json 或 {arxiv_id}_summary.json）
        if SUMMARIES_DIR.exists():
            for json_file in SUMMARIES_DIR.glob("*_summary.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    aid = data.get("paper_id") or data.get("arxiv_id", "")
                    if not aid:
                        # 从文件名提取 arXiv ID
                        aid = json_file.stem.split("_")[0]
                    if aid:
                        self._summaries[aid] = data
                except (json.JSONDecodeError, OSError):
                    continue

        logger.info("[AgentA] Loaded %d classifications, %d summaries",
                     len(self._classifications), len(self._summaries))

    @property
    def is_ready(self) -> bool:
        return len(self._summaries) > 0

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行方向匹配推荐。

        参数:
            seed_arxiv_id (str): 种子论文 arXiv ID
            top_k        (int): 返回数量，默认 10
            candidates   (list): 可选的候选论文 ID 列表（如果 None 则用全部）

        返回:
            {
                "agent": "A",
                "seed": str,
                "results": [{"arxiv_id": str, "score": float, "reason": str}],
                "error": str | None,
            }
        """
        seed_id: str = kwargs.get("seed_arxiv_id", "")
        top_k: int = kwargs.get("top_k", 10)
        candidate_ids: list[str] | None = kwargs.get("candidates")

        if not seed_id:
            return {"agent": "A", "seed": "", "results": [], "error": "seed_arxiv_id required"}

        seed_cls = self._classifications.get(seed_id, {})
        seed_summary = self._summaries.get(seed_id, {})

        if not seed_cls and not seed_summary:
            return {"agent": "A", "seed": seed_id, "results": [], "error": "Seed paper not found"}

        # 确定候选池
        if candidate_ids is None:
            candidate_ids = [aid for aid in self._summaries if aid != seed_id]

        seed_directions = set(seed_cls.get("research_directions", []))
        seed_paradigms = set(seed_cls.get("technical_paradigms", []))
        seed_terms = self._extract_terms(seed_summary)

        results = []
        for cand_id in candidate_ids:
            if cand_id == seed_id:
                continue

            cand_cls = self._classifications.get(cand_id, {})
            cand_summary = self._summaries.get(cand_id, {})

            # 1. 方向标签 Jaccard 相似度
            cand_directions = set(cand_cls.get("research_directions", []))
            direction_sim = self._jaccard(seed_directions, cand_directions)

            # 2. 范式标签 Jaccard 相似度
            cand_paradigms = set(cand_cls.get("technical_paradigms", []))
            paradigm_sim = self._jaccard(seed_paradigms, cand_paradigms)

            # 3. 关键词重叠
            cand_terms = self._extract_terms(cand_summary)
            term_overlap = len(seed_terms & cand_terms)
            term_sim = term_overlap / max(len(seed_terms | cand_terms), 1)

            # 加权得分
            topic_score = direction_sim * 0.6 + term_sim * 0.4
            paradigm_score = paradigm_sim

            total_score = (topic_score * WEIGHT_TOPIC + paradigm_score * WEIGHT_PARADIGM) / AGENT_WEIGHT

            # 归一化到 0-1
            total_score = min(1.0, total_score)

            if total_score > 0:
                reason = self._build_reason(
                    direction_sim, paradigm_sim, term_sim,
                    seed_directions & cand_directions,
                    seed_paradigms & cand_paradigms,
                )
                results.append({
                    "arxiv_id": cand_id,
                    "score": round(total_score, 4),
                    "reason": reason,
                    "matched_directions": list(seed_directions & cand_directions),
                    "matched_paradigms": list(seed_paradigms & cand_paradigms),
                })

        # 排序并截断
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]

        return {
            "agent": "A",
            "seed": seed_id,
            "results": results,
            "error": None,
        }

    @staticmethod
    def _jaccard(a: set, b: set) -> float:
        """Jaccard 相似度。"""
        if not a and not b:
            return 0.0
        intersection = len(a & b)
        union = len(a | b)
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _extract_terms(summary: dict) -> set[str]:
        """从摘要中提取关键术语。"""
        terms: set[str] = set()
        title = str(summary.get("title_en", "")) + " " + str(summary.get("title_zh", ""))
        one_line = str(summary.get("one_line_summary", ""))

        # 从问题定义提取
        prob = summary.get("problem_definition", {})
        if isinstance(prob, dict):
            terms.add(str(prob.get("task_type", "")).lower())

        # 从创新点提取
        innovations = summary.get("innovations", [])
        if isinstance(innovations, list):
            for inv in innovations:
                if isinstance(inv, dict):
                    terms.add(str(inv.get("point", "")).lower()[:50])

        # 从模块名称提取
        modules = summary.get("modules", [])
        if isinstance(modules, list):
            for mod in modules:
                if isinstance(mod, dict):
                    terms.add(str(mod.get("name", "")).lower())

        # 标题关键词
        for word in title.lower().split():
            if len(word) > 3:
                terms.add(word)

        return {t for t in terms if t and len(t) > 2}

    @staticmethod
    def _build_reason(
        dir_sim: float, parad_sim: float, term_sim: float,
        matched_dirs: set, matched_paradigms: set,
    ) -> str:
        """生成推荐理由。"""
        parts = []
        if matched_dirs:
            parts.append(f"研究方向匹配: {', '.join(matched_dirs)}")
        if matched_paradigms:
            parts.append(f"技术范式匹配: {', '.join(matched_paradigms)}")
        if term_sim > 0.2:
            parts.append(f"关键词相似度: {term_sim:.2f}")
        if not parts:
            parts.append("方向弱关联")
        return "; ".join(parts)
