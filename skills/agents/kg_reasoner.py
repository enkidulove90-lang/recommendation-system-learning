"""
skills/agents/kg_reasoner.py — Agent D: 知识图谱推理 Agent

基于 knowledge_subgraph 做跨论文实体路径推理。
权重: relation_graph(0.10) + profile_quality(0.05) = 0.15

匹配策略:
  1. 跨论文知识子图实体匹配（共享模块/创新点/基线方法）
  2. 路径推理：种子论文的 innovation → 候选论文的 module/baseline
  3. 引用关联：通过 related_papers 构建引用网络
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

# Agent D 权重
WEIGHT_RELATION = 0.10
WEIGHT_QUALITY = 0.05
AGENT_WEIGHT = WEIGHT_RELATION + WEIGHT_QUALITY  # 0.15


@register_skill("agent-kg-reason")
class KGReasoner(BaseSkill):
    """
    Agent D: 知识图谱推理 Agent。

    基于知识子图做跨论文实体路径推理。

    使用示例:
        agent = KGReasoner()
        result = agent.execute(
            seed_arxiv_id="2505.19525",
            top_k=10,
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._summaries: dict[str, dict] = {}
        self._entity_index: dict[str, set[str]] = {}  # entity -> set of arxiv_ids
        self._load_data()

    def _load_data(self) -> None:
        """加载摘要数据并构建实体索引。"""
        if SUMMARIES_DIR.exists():
            for json_file in SUMMARIES_DIR.glob("*_summary.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    aid = data.get("paper_id") or data.get("arxiv_id", "")
                    if not aid:
                        aid = json_file.stem.split("_")[0]
                    if aid:
                        self._summaries[aid] = data
                        self._index_entities(aid, data)
                except (json.JSONDecodeError, OSError):
                    continue

        logger.info("[AgentD] Loaded %d summaries, %d entities indexed",
                     len(self._summaries), len(self._entity_index))

    def _index_entities(self, arxiv_id: str, summary: dict) -> None:
        """为论文的实体构建倒排索引。"""
        # 模块名称
        modules = summary.get("modules", [])
        if isinstance(modules, list):
            for mod in modules:
                if isinstance(mod, dict):
                    name = str(mod.get("name", "")).strip().lower()
                    if name and len(name) > 2:
                        self._entity_index.setdefault(name, set()).add(arxiv_id)

        # 基线方法
        benchmark = summary.get("benchmark", {})
        if isinstance(benchmark, dict):
            baselines = benchmark.get("baselines", [])
            if isinstance(baselines, list):
                for bl in baselines:
                    bl_name = str(bl).strip().lower()
                    if bl_name and len(bl_name) > 2:
                        self._entity_index.setdefault(bl_name, set()).add(arxiv_id)

        # 创新点关键词
        innovations = summary.get("innovations", [])
        if isinstance(innovations, list):
            for inv in innovations:
                if isinstance(inv, dict):
                    point = str(inv.get("point", "")).strip().lower()
                    # 提取创新点中的方法名（简单启发式：大写开头的词组）
                    method_names = re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", point)
                    for mn in method_names:
                        self._entity_index.setdefault(mn.lower(), set()).add(arxiv_id)

        # 关联论文引用
        related = summary.get("related_papers", [])
        if isinstance(related, list):
            for rp in related:
                if isinstance(rp, dict):
                    ref_id = str(rp.get("ref_id", "")).strip()
                    # 提取引文编号 [12] 中的数字
                    ref_match = re.search(r"\[(\d+)\]", ref_id)
                    if ref_match:
                        ref_key = f"ref_{ref_match.group(1)}"
                        self._entity_index.setdefault(ref_key, set()).add(arxiv_id)

    @property
    def is_ready(self) -> bool:
        return len(self._summaries) > 0

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行 KG 推理推荐。

        参数:
            seed_arxiv_id (str): 种子论文 arXiv ID
            top_k        (int): 返回数量
            candidates   (list): 可选候选 ID 列表

        返回:
            {
                "agent": "D",
                "seed": str,
                "results": [{"arxiv_id": str, "score": float, "reason": str, "path": str}],
                "error": str | None,
            }
        """
        seed_id: str = kwargs.get("seed_arxiv_id", "")
        top_k: int = kwargs.get("top_k", 10)
        candidate_ids: list[str] | None = kwargs.get("candidates")

        if not seed_id:
            return {"agent": "D", "seed": "", "results": [], "error": "seed_arxiv_id required"}

        seed_summary = self._summaries.get(seed_id, {})
        if not seed_summary:
            return {"agent": "D", "seed": seed_id, "results": [], "error": "Seed summary not found"}

        if candidate_ids is None:
            candidate_ids = [aid for aid in self._summaries if aid != seed_id]

        # 提取种子论文的实体
        seed_entities = self._get_paper_entities(seed_id, seed_summary)

        results = []
        for cand_id in candidate_ids:
            if cand_id == seed_id:
                continue

            cand_summary = self._summaries.get(cand_id, {})
            if not cand_summary:
                continue

            cand_entities = self._get_paper_entities(cand_id, cand_summary)

            # 1. 共享实体（模块/基线/方法名）
            shared_entities = seed_entities & cand_entities
            entity_score = len(shared_entities) / max(len(seed_entities | cand_entities), 1)

            # 2. 路径推理：种子创新点 → 候选模块/基线
            path_score = self._path_reasoning(seed_summary, cand_summary, shared_entities)

            # 3. 引用网络关联
            citation_score = self._citation_proximity(seed_summary, cand_summary)

            # 4. 摘要质量分（profile_quality 维度）
            quality_score = self._quality_score(cand_summary)

            # 综合得分
            relation_score = entity_score * 0.4 + path_score * 0.3 + citation_score * 0.3
            total_score = (relation_score * WEIGHT_RELATION + quality_score * WEIGHT_QUALITY) / AGENT_WEIGHT

            if total_score > 0 and shared_entities:
                path_desc = self._describe_path(seed_id, cand_id, shared_entities)
                reason = self._build_reason(shared_entities, path_desc, citation_score)
                results.append({
                    "arxiv_id": cand_id,
                    "score": round(total_score, 4),
                    "reason": reason,
                    "path": path_desc,
                    "shared_entities": list(shared_entities)[:5],
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]

        return {
            "agent": "D",
            "seed": seed_id,
            "results": results,
            "error": None,
        }

    @staticmethod
    def _get_paper_entities(arxiv_id: str, summary: dict) -> set[str]:
        """提取论文的所有实体。"""
        entities: set[str] = set()

        # 模块
        modules = summary.get("modules", [])
        if isinstance(modules, list):
            for mod in modules:
                if isinstance(mod, dict):
                    name = str(mod.get("name", "")).strip().lower()
                    if name:
                        entities.add(name)

        # 基线
        benchmark = summary.get("benchmark", {})
        if isinstance(benchmark, dict):
            baselines = benchmark.get("baselines", [])
            if isinstance(baselines, list):
                for bl in baselines:
                    entities.add(str(bl).strip().lower())

        # 创新点中的方法名
        innovations = summary.get("innovations", [])
        if isinstance(innovations, list):
            for inv in innovations:
                if isinstance(inv, dict):
                    point = str(inv.get("point", ""))
                    method_names = re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", point)
                    entities.update(mn.lower() for mn in method_names)

        # 数据集
        datasets = summary.get("datasets", [])
        if isinstance(datasets, list):
            for ds in datasets:
                if isinstance(ds, dict):
                    entities.add(str(ds.get("name", "")).strip().lower())

        return {e for e in entities if e and len(e) > 2}

    @staticmethod
    def _path_reasoning(seed: dict, cand: dict, shared: set) -> float:
        """
        路径推理：种子创新点是否引用了候选论文的模块/基线。

        简化版：检查共享实体是否出现在种子的 innovations 中。
        """
        if not shared:
            return 0.0

        seed_innovations_text = ""
        innovations = seed.get("innovations", [])
        if isinstance(innovations, list):
            for inv in innovations:
                if isinstance(inv, dict):
                    seed_innovations_text += " " + str(inv.get("point", "")).lower()

        # 检查共享实体是否在种子创新点中被提及
        mentioned = sum(1 for e in shared if e in seed_innovations_text)
        return min(1.0, mentioned / max(len(shared), 1))

    @staticmethod
    def _citation_proximity(seed: dict, cand: dict) -> float:
        """引用网络邻近度。"""
        # 检查种子的 related_papers 中是否间接关联到候选
        seed_related = seed.get("related_papers", [])
        cand_related = cand.get("related_papers", [])

        if not isinstance(seed_related, list) or not isinstance(cand_related, list):
            return 0.0

        # 简化版：共享引文编号
        seed_refs = set()
        for rp in seed_related:
            if isinstance(rp, dict):
                ref = str(rp.get("ref_id", ""))
                seed_refs.add(ref)

        cand_refs = set()
        for rp in cand_related:
            if isinstance(rp, dict):
                ref = str(rp.get("ref_id", ""))
                cand_refs.add(ref)

        shared_refs = seed_refs & cand_refs
        if not seed_refs or not cand_refs:
            return 0.0

        return len(shared_refs) / max(len(seed_refs | cand_refs), 1)

    @staticmethod
    def _quality_score(summary: dict) -> float:
        """论文画像质量分。"""
        score = 0.0

        # 字段完整度
        key_fields = ["title_zh", "problem_definition", "innovations", "modules",
                      "training", "datasets", "benchmark", "related_papers",
                      "reproducibility", "limitations"]
        filled = sum(1 for f in key_fields if summary.get(f))
        score += filled / len(key_fields) * 0.6

        # 复现性
        repro = summary.get("reproducibility", {})
        if isinstance(repro, dict):
            if repro.get("code_open"):
                score += 0.2
            if repro.get("data_open"):
                score += 0.1
            if repro.get("hyperparams_complete"):
                score += 0.1

        return min(1.0, score)

    @staticmethod
    def _describe_path(seed_id: str, cand_id: str, shared: set) -> str:
        """描述知识子图路径。"""
        entities_str = ", ".join(list(shared)[:3])
        return f"{seed_id} --[{entities_str}]--> {cand_id}"

    @staticmethod
    def _build_reason(shared: set, path: str, citation: float) -> str:
        parts = []
        if shared:
            parts.append(f"共享实体: {', '.join(list(shared)[:3])}")
        if path:
            parts.append(f"KG路径: {path}")
        if citation > 0:
            parts.append(f"引用邻近: {citation:.2f}")
        return "; ".join(parts) if parts else "KG弱关联"
