"""
skills/agent_router.py — 多 Agent 推荐路由器

根据用户查询意图选择 Agent 组合，汇总各 Agent 结果，应用多样性约束。

架构:
  用户查询 → 意图分类 → Agent 选择 → 并行执行 → 候选合并 → 多样性约束 → 排序输出

路由规则:
  - direction_match (Agent A): 方向/领域/topic/相似 → 权重 0.45
  - pipeline_complement (Agent B): 流程/管线/pipeline/召回/排序 → 权重 0.20
  - dataset_comparison (Agent C): 数据集/dataset/对比/benchmark → 权重 0.10
  - kg_reasoning (Agent D): 关联/关系/知识图谱/graph → 权重 0.15
  - recency (全局): 时效性因子 0.10
"""

from __future__ import annotations

import json
import logging
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill
from skills.agents.direction_matcher import DirectionMatcher
from skills.agents.pipeline_complementer import PipelineComplementer
from skills.agents.dataset_comparator import DatasetComparator
from skills.agents.kg_reasoner import KGReasoner

logger = logging.getLogger(__name__)

ROUTES_CONFIG_PATH = settings.DATA_DIR.parent / "config" / "agent_routes.yaml"
SUMMARIES_DIR = settings.DATA_DIR / "summaries"


@register_skill("agent-router")
class AgentRouter(BaseSkill):
    """
    多 Agent 推荐路由器。

    根据用户查询意图选择 Agent 组合，汇总结果，应用多样性约束。

    使用示例:
        router = AgentRouter()
        result = router.execute(
            seed_arxiv_id="2505.19525",
            user_query="找方向相似的论文",
            top_k=20,
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._routes_config: dict = {}
        self._agents: dict[str, BaseSkill] = {}
        self._load_config()
        self._init_agents()

    def _load_config(self) -> None:
        """加载路由配置。"""
        if ROUTES_CONFIG_PATH.exists():
            try:
                self._routes_config = yaml.safe_load(
                    ROUTES_CONFIG_PATH.read_text(encoding="utf-8")
                )
                logger.info("[Router] Loaded routes config from %s", ROUTES_CONFIG_PATH.name)
            except Exception as e:
                logger.error("[Router] Failed to load config: %s", e)
                self._routes_config = {}
        else:
            logger.warning("[Router] Config not found: %s", ROUTES_CONFIG_PATH)
            self._routes_config = {}

    def _init_agents(self) -> None:
        """初始化 4 个 Agent。"""
        try:
            self._agents = {
                "A": DirectionMatcher(),
                "B": PipelineComplementer(),
                "C": DatasetComparator(),
                "D": KGReasoner(),
            }
            ready_count = sum(1 for a in self._agents.values() if a.is_ready)
            logger.info("[Router] Initialized %d agents (%d ready)", len(self._agents), ready_count)
        except Exception as e:
            logger.error("[Router] Agent init error: %s", e)

    @property
    def is_ready(self) -> bool:
        return len(self._agents) > 0 and any(a.is_ready for a in self._agents.values())

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行多 Agent 推荐。

        参数:
            seed_arxiv_id (str): 种子论文 arXiv ID
            user_query    (str): 用户查询意图（可选）
            top_k         (int): 最终返回数量，默认 20
            agents        (list): 指定使用的 Agent 列表（如 ["A", "B"]），默认自动选择

        返回:
            {
                "seed": str,
                "selected_agents": list[str],
                "results": [{"arxiv_id": str, "score": float, "reason": str, "agents": list}],
                "agent_results": dict,  # 各 Agent 的独立结果
                "error": str | None,
            }
        """
        seed_id: str = kwargs.get("seed_arxiv_id", "")
        user_query: str = kwargs.get("user_query", "")
        top_k: int = kwargs.get("top_k", 20)
        specified_agents: list[str] | None = kwargs.get("agents")

        if not seed_id:
            return {"seed": "", "results": [], "error": "seed_arxiv_id required"}

        # 1. 意图分类 → Agent 选择
        if specified_agents:
            selected = specified_agents
        else:
            selected = self._classify_intent(user_query)

        logger.info("[Router] Seed=%s, Query='%s', Agents=%s", seed_id, user_query[:50], selected)

        # 2. 并行执行各 Agent（串行实现，API 调用无并行需求）
        agent_results: dict[str, dict] = {}
        all_candidates: dict[str, dict] = {}  # arxiv_id -> merged data

        for agent_key in selected:
            agent = self._agents.get(agent_key)
            if not agent or not agent.is_ready:
                logger.warning("[Router] Agent %s not ready, skipping", agent_key)
                continue

            result = agent.execute(seed_arxiv_id=seed_id, top_k=10)
            agent_results[agent_key] = result

            if result.get("error"):
                logger.warning("[Router] Agent %s error: %s", agent_key, result["error"])
                continue

            # 合并候选
            agent_weight = self._get_agent_weight(agent_key)
            for item in result.get("results", []):
                aid = item.get("arxiv_id", "")
                if not aid:
                    continue

                weighted_score = item["score"] * agent_weight

                if aid in all_candidates:
                    all_candidates[aid]["score"] += weighted_score
                    all_candidates[aid]["agents"].append(agent_key)
                    all_candidates[aid]["reasons"].append(f"[{agent_key}] {item.get('reason', '')}")
                else:
                    all_candidates[aid] = {
                        "arxiv_id": aid,
                        "score": weighted_score,
                        "agents": [agent_key],
                        "reasons": [f"[{agent_key}] {item.get('reason', '')}"],
                    }

        # 3. 应用全局 recency 因子
        recency_weight = self._get_global_weight("recency")
        if recency_weight > 0:
            for aid, data in all_candidates.items():
                recency = self._compute_recency(aid)
                data["score"] += recency * recency_weight

        # 4. 多样性约束
        diversity_config = self._routes_config.get("diversity", {})
        max_same_family = diversity_config.get("max_same_method_family", 2)
        merged = self._apply_diversity(
            list(all_candidates.values()), max_same_family
        )

        # 5. 排序并截断
        merged.sort(key=lambda x: x["score"], reverse=True)
        merged = merged[:top_k]

        # 格式化输出
        for item in merged:
            item["score"] = round(item["score"], 4)
            item["reason"] = " | ".join(item.pop("reasons"))

        return {
            "seed": seed_id,
            "selected_agents": selected,
            "results": merged,
            "agent_results": {
                k: {"result_count": len(v.get("results", [])), "error": v.get("error")}
                for k, v in agent_results.items()
            },
            "error": None,
        }

    # ------------------------------------------------------------------
    # 意图分类
    # ------------------------------------------------------------------

    def _classify_intent(self, query: str) -> list[str]:
        """根据用户查询意图选择 Agent 组合。"""
        if not query:
            # 默认策略
            default_cfg = self._routes_config.get("default", {})
            return default_cfg.get("agents", ["A", "B"])

        query_lower = query.lower()
        scores: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0}

        routes = self._routes_config.get("routes", [])
        for route_cfg in routes:
            agent_key = route_cfg.get("agent", "")
            keywords = route_cfg.get("trigger_keywords", [])
            for kw in keywords:
                if kw.lower() in query_lower:
                    scores[agent_key] = scores.get(agent_key, 0) + 1

        # 选择得分 > 0 的 Agent，如果全部为 0 则用默认
        selected = [k for k, v in scores.items() if v > 0]
        if not selected:
            default_cfg = self._routes_config.get("default", {})
            selected = default_cfg.get("agents", ["A", "B"])

        return selected

    # ------------------------------------------------------------------
    # 权重获取
    # ------------------------------------------------------------------

    def _get_agent_weight(self, agent_key: str) -> float:
        """获取 Agent 权重。"""
        routes = self._routes_config.get("routes", [])
        for route_cfg in routes:
            if route_cfg.get("agent") == agent_key:
                return float(route_cfg.get("weight", 0.0))

        # 默认权重
        defaults = {"A": 0.45, "B": 0.20, "C": 0.10, "D": 0.15}
        return defaults.get(agent_key, 0.0)

    def _get_global_weight(self, factor: str) -> float:
        """获取全局排序因子权重。"""
        default_cfg = self._routes_config.get("default", {})
        if factor == "recency":
            return float(default_cfg.get("recency_weight", 0.10))
        elif factor == "profile_quality":
            return float(default_cfg.get("profile_quality_weight", 0.05))
        return 0.0

    # ------------------------------------------------------------------
    # 时效性计算
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_recency(arxiv_id: str) -> float:
        """根据 arXiv ID 计算时效性分数。"""
        # arXiv ID 格式: YYMM.NNNNN
        match = re.match(r"(\d{2})(\d{2})\.", arxiv_id)
        if not match:
            return 0.0

        year = 2000 + int(match.group(1))
        month = int(match.group(2))
        now = datetime.now()

        # 距今年月差
        months_ago = (now.year - year) * 12 + (now.month - month)
        if months_ago < 0:
            months_ago = 0

        # 6 个月内 = 1.0, 12 个月 = 0.7, 24 个月 = 0.4, 36+ = 0.1
        if months_ago <= 6:
            return 1.0
        elif months_ago <= 12:
            return 0.7
        elif months_ago <= 24:
            return 0.4
        elif months_ago <= 36:
            return 0.2
        return 0.1

    # ------------------------------------------------------------------
    # 多样性约束
    # ------------------------------------------------------------------

    def _apply_diversity(self, candidates: list[dict], max_same_family: int) -> list[dict]:
        """
        应用多样性约束。

        确保同一方法族（同一 research_direction）的论文不超过 max_same_family 篇。
        """
        if not candidates:
            return []

        # 加载分类信息用于方法族判断
        jsonl_path = settings.DATA_DIR / "registry" / "papers.jsonl"
        classifications: dict[str, dict] = {}
        if jsonl_path.exists():
            for line in jsonl_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    aid = record.get("arxiv_id", "")
                    if aid:
                        classifications[aid] = record.get("classification", {})
                except json.JSONDecodeError:
                    continue

        # 按分数排序
        candidates.sort(key=lambda x: x["score"], reverse=True)

        family_counts: dict[str, int] = {}
        result = []

        for cand in candidates:
            aid = cand["arxiv_id"]
            cls = classifications.get(aid, {})
            directions = cls.get("research_directions", ["unknown"])
            primary_dir = directions[0] if directions else "unknown"

            if family_counts.get(primary_dir, 0) < max_same_family:
                result.append(cand)
                family_counts[primary_dir] = family_counts.get(primary_dir, 0) + 1

        return result
