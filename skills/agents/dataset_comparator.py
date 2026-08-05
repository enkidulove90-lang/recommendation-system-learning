"""
skills/agents/dataset_comparator.py — Agent C: 数据集共享 Agent

基于相同数据集找可比论文。
权重: shared_dataset(0.10)

匹配策略:
  1. 共享数据集名称精确匹配
  2. 数据集规模相似度（用户数/物品数/交互数在同一量级）
  3. 相同评测指标的对比价值
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

SUMMARIES_DIR = settings.DATA_DIR / "summaries"

# Agent C 权重
WEIGHT_DATASET = 0.10
AGENT_WEIGHT = WEIGHT_DATASET  # 0.10


@register_skill("agent-dataset-compare")
class DatasetComparator(BaseSkill):
    """
    Agent C: 数据集共享 Agent。

    基于相同数据集找可比论文。

    使用示例:
        agent = DatasetComparator()
        result = agent.execute(
            seed_arxiv_id="2505.19525",
            top_k=10,
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._summaries: dict[str, dict] = {}
        self._load_data()

    def _load_data(self) -> None:
        """加载摘要数据。"""
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

        logger.info("[AgentC] Loaded %d summaries", len(self._summaries))

    @property
    def is_ready(self) -> bool:
        return len(self._summaries) > 0

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行数据集共享推荐。

        参数:
            seed_arxiv_id (str): 种子论文 arXiv ID
            top_k        (int): 返回数量
            candidates   (list): 可选候选 ID 列表

        返回:
            {
                "agent": "C",
                "seed": str,
                "results": [{"arxiv_id": str, "score": float, "reason": str}],
                "error": str | None,
            }
        """
        seed_id: str = kwargs.get("seed_arxiv_id", "")
        top_k: int = kwargs.get("top_k", 10)
        candidate_ids: list[str] | None = kwargs.get("candidates")

        if not seed_id:
            return {"agent": "C", "seed": "", "results": [], "error": "seed_arxiv_id required"}

        seed_summary = self._summaries.get(seed_id, {})
        if not seed_summary:
            return {"agent": "C", "seed": seed_id, "results": [], "error": "Seed summary not found"}

        seed_datasets = self._extract_datasets(seed_summary)
        seed_metrics = self._extract_metrics(seed_summary)

        if not seed_datasets:
            return {"agent": "C", "seed": seed_id, "results": [], "error": "Seed has no dataset info"}

        if candidate_ids is None:
            candidate_ids = [aid for aid in self._summaries if aid != seed_id]

        results = []
        for cand_id in candidate_ids:
            if cand_id == seed_id:
                continue

            cand_summary = self._summaries.get(cand_id, {})
            if not cand_summary:
                continue

            cand_datasets = self._extract_datasets(cand_summary)
            cand_metrics = self._extract_metrics(cand_summary)

            # 1. 共享数据集
            shared_datasets = seed_datasets & cand_datasets
            shared_score = len(shared_datasets) / max(len(seed_datasets | cand_datasets), 1)

            # 2. 规模相似度
            scale_sim = self._scale_similarity(seed_summary, cand_summary)

            # 3. 共享评测指标
            shared_metrics = seed_metrics & cand_metrics
            metric_score = len(shared_metrics) / max(len(seed_metrics | cand_metrics), 1) if seed_metrics or cand_metrics else 0

            # 综合得分
            total_score = shared_score * 0.6 + scale_sim * 0.2 + metric_score * 0.2

            if total_score > 0 and shared_datasets:
                reason = self._build_reason(shared_datasets, shared_metrics, scale_sim)
                results.append({
                    "arxiv_id": cand_id,
                    "score": round(total_score, 4),
                    "reason": reason,
                    "shared_datasets": list(shared_datasets),
                    "shared_metrics": list(shared_metrics),
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]

        return {
            "agent": "C",
            "seed": seed_id,
            "results": results,
            "error": None,
        }

    @staticmethod
    def _extract_datasets(summary: dict) -> set[str]:
        """从摘要中提取数据集名称。"""
        datasets: set[str] = set()
        ds_list = summary.get("datasets", [])
        if isinstance(ds_list, list):
            for ds in ds_list:
                if isinstance(ds, dict):
                    name = str(ds.get("name", "")).strip()
                    if name:
                        datasets.add(name.lower())
                elif isinstance(ds, str) and ds.strip():
                    datasets.add(ds.strip().lower())
        return datasets

    @staticmethod
    def _extract_metrics(summary: dict) -> set[str]:
        """从摘要中提取评测指标。"""
        metrics: set[str] = set()
        benchmark = summary.get("benchmark", {})
        if isinstance(benchmark, dict):
            metric_list = benchmark.get("metrics", [])
            if isinstance(metric_list, list):
                for m in metric_list:
                    metrics.add(str(m).strip().lower())
        return metrics

    @staticmethod
    def _scale_similarity(seed: dict, cand: dict) -> float:
        """计算数据集规模相似度。"""
        def get_scale(summary: dict) -> tuple[int, int, int]:
            ds_list = summary.get("datasets", [])
            if not isinstance(ds_list, list) or not ds_list:
                return (0, 0, 0)
            ds = ds_list[0] if ds_list else {}
            if not isinstance(ds, dict):
                return (0, 0, 0)

            def parse_num(s: str) -> int:
                s = str(s).replace(",", "").replace(" ", "")
                m = re.match(r"[\d.]+", s)
                if not m:
                    return 0
                val = float(m.group())
                if "k" in s.lower():
                    val *= 1_000
                elif "m" in s.lower():
                    val *= 1_000_000
                return int(val)

            users = parse_num(str(ds.get("users", "0")))
            items = parse_num(str(ds.get("items", "0")))
            inter = parse_num(str(ds.get("interactions", "0")))
            return (users, items, inter)

        s_users, s_items, s_inter = get_scale(seed)
        c_users, c_items, c_inter = get_scale(cand)

        if s_users == 0 or c_users == 0:
            return 0.0

        # 对数尺度比较
        def log_sim(a: int, b: int) -> float:
            if a == 0 and b == 0:
                return 1.0
            if a == 0 or b == 0:
                return 0.0
            import math
            ratio = abs(math.log10(a) - math.log10(b))
            return max(0.0, 1.0 - ratio / 3.0)  # 3个数量级内有一定相似度

        return (log_sim(s_users, c_users) + log_sim(s_items, c_items) + log_sim(s_inter, c_inter)) / 3.0

    @staticmethod
    def _build_reason(shared_ds: set, shared_metrics: set, scale_sim: float) -> str:
        parts = []
        if shared_ds:
            parts.append(f"共享数据集: {', '.join(list(shared_ds)[:3])}")
        if shared_metrics:
            parts.append(f"共享指标: {', '.join(list(shared_metrics)[:3])}")
        if scale_sim > 0.5:
            parts.append(f"数据规模相似: {scale_sim:.2f}")
        return "; ".join(parts) if parts else "数据集弱关联"
