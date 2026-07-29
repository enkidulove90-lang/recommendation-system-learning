"""Generate explainable reading orders from profiles and their relation graph."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from models.research_graph import LearningPath, LearningStep
from skills.base_module import BaseSkill, get_skill, register_skill
from storage.profile_store import ProfileStore
from storage.research_graph_store import ResearchGraphStore


DEFAULT_PATHS = (
    ("multimodal", "beginner"),
    ("agent", "intermediate"),
    ("generative", "intermediate"),
    ("ranking", "advanced"),
    ("long-tail", "advanced"),
)

TOPIC_ALIASES = {
    "multimodal": ("multimodal", "multi-modal", "vision", "image", "多模态"),
    "agent": ("agent", "agentic", "multi-agent", "智能体"),
    "generative": ("generative", "generation", "llm", "生成式"),
    "ranking": ("ranking", "rerank", "re-ranking", "排序", "重排"),
    "long-tail": ("long-tail", "cold_start", "cold start", "popularity", "长尾", "冷启动"),
}


@register_skill("research-learning-path")
class LearningPathBuilderSkill(BaseSkill):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.profiles = ProfileStore()
        self.graphs = ResearchGraphStore()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        topic = str(kwargs.get("topic", "")).strip().casefold()
        level = str(kwargs.get("level", "intermediate")).strip().casefold()
        max_papers = int(kwargs.get("max_papers", 0))
        if not topic:
            return {"error": "topic is required.", "steps": []}
        if level not in {"beginner", "intermediate", "advanced"}:
            return {"error": f"Unsupported level: {level}", "steps": []}

        graph = self.graphs.load_graph()
        if graph is None:
            relation_result = get_skill("research-relations-build").execute()
            if relation_result.get("error"):
                return {"error": relation_result["error"], "steps": []}
            graph = self.graphs.load_graph()
        if graph is None:
            return {"error": "Relation graph is unavailable.", "steps": []}

        candidates = [
            profile
            for profile in self.profiles.iter_profiles()
            if profile.quality.grade in {"A", "B", "C"}
        ]
        scored = [
            (self._topic_score(profile, topic), profile)
            for profile in candidates
        ]
        scored = [item for item in scored if item[0] > 0]
        if not scored:
            return {"error": f"No active profiles match topic: {topic}", "steps": []}

        default_count = {"beginner": 5, "intermediate": 6, "advanced": 7}[level]
        limit = max_papers if max_papers > 0 else default_count
        selected = self._select_and_order(scored, level, limit)
        edge_lookup = self._edge_lookup(graph.edges)
        steps: list[LearningStep] = []
        completed_ids: list[str] = []
        for order, profile in enumerate(selected, 1):
            related_edges = self._best_prior_edges(
                profile.paper_id,
                completed_ids,
                edge_lookup,
            )
            prerequisites = []
            relation_ids = []
            if related_edges:
                prerequisites = [related_edges[0][0]]
                relation_ids = [related_edges[0][1].edge_id]
            elif completed_ids and order > 2:
                prerequisites = [completed_ids[-1]]

            role = self._role(profile, order, level)
            steps.append(
                LearningStep(
                    order=order,
                    paper_id=profile.paper_id,
                    title=profile.identity.title or profile.identity.chinese_title,
                    role=role,
                    rationale=self._rationale(profile, topic, role),
                    prerequisites=prerequisites,
                    relation_edge_ids=relation_ids,
                    profile_quality=profile.quality.grade,
                )
            )
            completed_ids.append(profile.paper_id)

        path_id = f"{self._slug(topic)}_{level}"
        path_model = LearningPath(
            path_id=path_id,
            topic=topic,
            level=level,
            objective=self._objective(topic, level),
            generated_at=datetime.now(timezone.utc).isoformat(),
            steps=steps,
        )
        json_path, md_path = self.graphs.save_learning_path(path_model)
        return {
            "error": None,
            "path_id": path_id,
            "topic": topic,
            "level": level,
            "steps": [step.model_dump(mode="json") for step in steps],
            "json_path": str(json_path),
            "markdown_path": str(md_path),
        }

    @staticmethod
    def _topic_score(profile: Any, topic: str) -> float:
        aliases = TOPIC_ALIASES.get(topic, (topic,))
        payload = json.dumps(profile.model_dump(mode="json"), ensure_ascii=False).casefold()
        hits = sum(alias.casefold() in payload for alias in aliases)
        classification = profile.classification
        exact_values = {
            *classification.research_directions,
            *classification.pipeline_stages,
            *classification.problems,
            *classification.technical_paradigms,
            *classification.modalities,
        }
        exact_bonus = 2.0 if topic in exact_values else 0.0
        quality_bonus = {"A": 1.0, "B": 0.8, "C": 0.3, "D": 0.0}[profile.quality.grade]
        return hits + exact_bonus + quality_bonus

    @staticmethod
    def _select_and_order(
        scored: list[tuple[float, Any]],
        level: str,
        limit: int,
    ) -> list[Any]:
        def difficulty(profile: Any) -> float:
            if profile.identity.paper_type == "survey":
                return 0.0
            if profile.identity.paper_type in {"dataset", "benchmark"}:
                return 0.25
            value = 0.5
            if "agentic" in profile.classification.technical_paradigms:
                value += 0.2
            if "online_learning" in profile.classification.pipeline_stages:
                value += 0.2
            return value

        top = sorted(
            scored,
            key=lambda item: (
                item[0],
                item[1].quality.confidence,
                item[1].paper_id,
            ),
            reverse=True,
        )[: max(limit * 2, limit)]
        if level == "advanced":
            ordered = sorted(
                top,
                key=lambda item: (
                    item[1].identity.paper_type != "survey",
                    difficulty(item[1]),
                    item[1].paper_id,
                ),
            )
        else:
            ordered = sorted(
                top,
                key=lambda item: (
                    difficulty(item[1]),
                    item[1].paper_id,
                ),
            )
        return [profile for _, profile in ordered[:limit]]

    @staticmethod
    def _edge_lookup(edges: list[Any]) -> dict[str, list[Any]]:
        lookup: dict[str, list[Any]] = {}
        for edge in edges:
            lookup.setdefault(edge.source_id, []).append(edge)
            lookup.setdefault(edge.target_id, []).append(edge)
        return lookup

    @staticmethod
    def _best_prior_edges(
        paper_id: str,
        completed_ids: list[str],
        lookup: dict[str, list[Any]],
    ) -> list[tuple[str, Any]]:
        completed = set(completed_ids)
        matches = []
        for edge in lookup.get(paper_id, []):
            other_id = edge.target_id if edge.source_id == paper_id else edge.source_id
            if other_id in completed:
                matches.append((other_id, edge))
        return sorted(
            matches,
            key=lambda item: (item[1].confidence, item[1].score),
            reverse=True,
        )

    @staticmethod
    def _role(profile: Any, order: int, level: str) -> str:
        if profile.identity.paper_type == "survey":
            return "survey"
        if profile.identity.paper_type in {"dataset", "benchmark"}:
            return "benchmark"
        if order == 1:
            return "foundation"
        if level == "advanced" and order >= 4:
            return "advanced"
        if "agentic" in profile.classification.technical_paradigms:
            return "application"
        return "method"

    @staticmethod
    def _rationale(profile: Any, topic: str, role: str) -> str:
        signals = [
            *profile.classification.pipeline_stages[:2],
            *profile.classification.problems[:2],
            *profile.classification.technical_paradigms[:2],
        ]
        signal_text = ", ".join(dict.fromkeys(signals)) or "core concepts"
        return f"Use this {role} paper to learn {topic} through {signal_text}."

    @staticmethod
    def _objective(topic: str, level: str) -> str:
        return (
            f"Build a {level} understanding of {topic}, progressing from framing "
            "and evidence standards to methods and implementation implications."
        )

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "topic"
