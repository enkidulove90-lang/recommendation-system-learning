"""
skills/agents/pipeline_complementer.py — Agent B: 管线互补 Agent

基于 pipeline_stage 标签找上下游论文（如 召回→排序→重排 学习路径）。
权重: pipeline_stage(0.20)

匹配策略:
  1. pipeline_stage 上下游关系（召回→排序→重排 的相邻阶段）
  2. 同阶段不同方法的对比
  3. 完整管线覆盖度计算
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

SUMMARIES_DIR = settings.DATA_DIR / "summaries"
JSONL_PATH = settings.DATA_DIR / "registry" / "papers.jsonl"

# Agent B 权重
WEIGHT_PIPELINE = 0.20
AGENT_WEIGHT = WEIGHT_PIPELINE  # 0.20

# 管线阶段上下游关系定义
PIPELINE_ORDER = [
    "data_preprocessing",
    "candidate_generation",
    "recall_retrieval",
    "pre_ranking",
    "ranking",
    "re_ranking",
    "fusion",
    "serving",
]


@register_skill("agent-pipeline-complement")
class PipelineComplementer(BaseSkill):
    """
    Agent B: 管线互补 Agent。

    基于 pipeline_stage 标签找上下游论文，构建学习路径。

    使用示例:
        agent = PipelineComplementer()
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
        """加载分类和摘要数据。"""
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

        if SUMMARIES_DIR.exists():
            for json_file in SUMMARIES_DIR.glob("*_summary.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    aid = data.get("paper_id") or data.get("arxiv_id", "")
                    if not aid:
                        aid = json_file.stem.split("_")[0]
                    if aid:
                        self._summaries[aid] = data
                except (json.JSONDecodeError, OSError):
                    continue

        logger.info("[AgentB] Loaded %d classifications, %d summaries",
                     len(self._classifications), len(self._summaries))

    @property
    def is_ready(self) -> bool:
        return len(self._summaries) > 0

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行管线互补推荐。

        参数:
            seed_arxiv_id (str): 种子论文 arXiv ID
            top_k        (int): 返回数量
            candidates   (list): 可选候选 ID 列表

        返回:
            {
                "agent": "B",
                "seed": str,
                "results": [{"arxiv_id": str, "score": float, "reason": str, "relation": str}],
                "error": str | None,
            }
        """
        seed_id: str = kwargs.get("seed_arxiv_id", "")
        top_k: int = kwargs.get("top_k", 10)
        candidate_ids: list[str] | None = kwargs.get("candidates")

        if not seed_id:
            return {"agent": "B", "seed": "", "results": [], "error": "seed_arxiv_id required"}

        seed_cls = self._classifications.get(seed_id, {})

        if not seed_cls:
            return {"agent": "B", "seed": seed_id, "results": [], "error": "Seed classification not found"}

        if candidate_ids is None:
            candidate_ids = [aid for aid in self._summaries if aid != seed_id]

        seed_stages = seed_cls.get("pipeline_stages", [])
        seed_stage_set = set(seed_stages)

        results = []
        for cand_id in candidate_ids:
            if cand_id == seed_id:
                continue

            cand_cls = self._classifications.get(cand_id, {})
            cand_stages = set(cand_cls.get("pipeline_stages", []))

            if not cand_stages:
                continue

            # 1. 上下游关系: 种子阶段与候选阶段是否在管线中相邻
            upstream, downstream = self._find_pipeline_relation(seed_stage_set, cand_stages)

            # 2. 同阶段不同方法
            same_stage = seed_stage_set & cand_stages

            # 3. 互补阶段（种子没有但候选有的阶段）
            complementary = cand_stages - seed_stage_set

            # 计算得分
            score = 0.0
            relation = ""

            if upstream:
                score += 0.5
                relation = f"上游管线: {', '.join(upstream)}"
            elif downstream:
                score += 0.5
                relation = f"下游管线: {', '.join(downstream)}"
            elif same_stage:
                score += 0.3
                relation = f"同阶段对比: {', '.join(same_stage)}"
            elif complementary:
                score += 0.2
                relation = f"管线互补: {', '.join(complementary)}"

            if score > 0:
                results.append({
                    "arxiv_id": cand_id,
                    "score": round(score, 4),
                    "reason": relation,
                    "relation": relation.split(":")[0].strip() if ":" in relation else relation,
                    "seed_stages": list(seed_stage_set),
                    "candidate_stages": list(cand_stages),
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]

        return {
            "agent": "B",
            "seed": seed_id,
            "results": results,
            "error": None,
        }

    @staticmethod
    def _find_pipeline_relation(seed_stages: set, cand_stages: set) -> tuple[list, list]:
        """
        找出候选论文相对种子论文的上下游关系。

        返回 (upstream_stages, downstream_stages)。
        """
        upstream = []
        downstream = []

        for seed_stage in seed_stages:
            if seed_stage not in PIPELINE_ORDER:
                continue
            seed_idx = PIPELINE_ORDER.index(seed_stage)

            for cand_stage in cand_stages:
                if cand_stage not in PIPELINE_ORDER or cand_stage in seed_stages:
                    continue
                cand_idx = PIPELINE_ORDER.index(cand_stage)

                if cand_idx < seed_idx:
                    if cand_stage not in upstream:
                        upstream.append(cand_stage)
                elif cand_idx > seed_idx:
                    if cand_stage not in downstream:
                        downstream.append(cand_stage)

        return upstream, downstream
