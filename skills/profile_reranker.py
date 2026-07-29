"""Rerank the local candidate pool with ResearchProfileV2 and graph signals."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from config import settings
from models.research_graph import (
    ProfileRecommendationReport,
    RankedRecommendation,
    ScoreBreakdown,
)
from skills.base_module import BaseSkill, get_skill, register_skill
from storage.profile_store import ProfileStore
from storage.research_graph_store import ResearchGraphStore


@register_skill("research-profile-rerank")
class ProfileRerankerSkill(BaseSkill):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.profiles = ProfileStore()
        self.graphs = ResearchGraphStore()
        self.config = self._load_config()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        seed_id = str(kwargs.get("seed_id", "")).strip()
        top_k = max(1, int(kwargs.get("top_k", 8)))
        seed = self.profiles.load_profile(seed_id)
        if seed is None or seed.quality.grade == "D":
            return {
                "error": f"Validated seed profile not found for {seed_id}",
                "results": [],
            }

        graph = self.graphs.load_graph()
        if graph is None:
            relation_result = get_skill("research-relations-build").execute()
            if relation_result.get("error"):
                return {"error": relation_result["error"], "results": []}
            graph = self.graphs.load_graph()
        if graph is None:
            return {"error": "Relation graph is unavailable.", "results": []}

        relation_lookup = self._relation_lookup(seed_id, graph.edges)
        scored = []
        for candidate in self.profiles.iter_profiles():
            if candidate.paper_id == seed_id or candidate.quality.grade == "D":
                continue
            scored.append(
                self._score_candidate(seed, candidate, relation_lookup.get(candidate.paper_id))
            )
        scored.sort(key=lambda item: (item["score"], item["paper_id"]), reverse=True)
        selected = self._apply_diversity(scored, top_k)

        recommendations = []
        for rank, item in enumerate(selected, 1):
            recommendations.append(
                RankedRecommendation(
                    rank=rank,
                    paper_id=item["paper_id"],
                    title=item["title"],
                    score=item["score"],
                    score_breakdown=ScoreBreakdown(**item["score_breakdown"]),
                    why_this_paper=item["why_this_paper"],
                    comparison_role=item["comparison_role"],
                    evidence_refs=item["evidence_refs"],
                    profile_quality=item["profile_quality"],
                )
            )

        weights = {
            key: float(value)
            for key, value in self.config.get("weights", {}).items()
        }
        report = ProfileRecommendationReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            seed_id=seed_id,
            weights=weights,
            candidate_count=len(scored),
            recommendations=recommendations,
        )
        json_path, md_path = self.graphs.save_recommendations(report)
        return {
            "error": None,
            "seed_id": seed_id,
            "candidate_count": len(scored),
            "results": [item.model_dump(mode="json") for item in recommendations],
            "report_json_path": str(json_path),
            "report_md_path": str(md_path),
        }

    def _score_candidate(
        self,
        seed: Any,
        candidate: Any,
        relation: Any | None,
    ) -> dict[str, Any]:
        weights = self.config["weights"]
        topic_problem = self._mean(
            self._jaccard(
                seed.classification.research_directions,
                candidate.classification.research_directions,
            ),
            self._jaccard(
                seed.classification.problems,
                candidate.classification.problems,
            ),
        )
        stage = self._jaccard(
            seed.classification.pipeline_stages,
            candidate.classification.pipeline_stages,
        )
        paradigm_modality = self._mean(
            self._jaccard(
                seed.classification.technical_paradigms,
                candidate.classification.technical_paradigms,
            ),
            self._jaccard(
                seed.classification.modalities,
                candidate.classification.modalities,
            ),
        )
        shared_dataset = self._jaccard(
            self._datasets(seed),
            self._datasets(candidate),
        )
        relation_score = float(relation.score * relation.confidence) if relation else 0.0
        year = self._paper_year(candidate.paper_id, candidate.identity.published_date)
        recency = min(1.0, max(0.0, (year - 2022) / 4.0))
        quality = {"A": 1.0, "B": 0.85, "C": 0.55, "D": 0.0}[
            candidate.quality.grade
        ]
        raw = {
            "topic_and_problem": topic_problem,
            "pipeline_stage": stage,
            "paradigm_and_modality": paradigm_modality,
            "shared_dataset": shared_dataset,
            "relation_graph": relation_score,
            "recency": recency,
            "profile_quality": quality,
        }
        points = {
            key: round(raw[key] * float(weights[key]) * 100.0, 4)
            for key in raw
        }
        total = round(sum(points.values()), 2)
        reasons = self._reasons(seed, candidate, raw, relation)
        return {
            "paper_id": candidate.paper_id,
            "title": candidate.identity.title or candidate.identity.chinese_title,
            "score": total,
            "score_breakdown": points,
            "why_this_paper": reasons,
            "comparison_role": self._comparison_role(candidate, shared_dataset, relation),
            "evidence_refs": self._evidence_refs(candidate, relation),
            "profile_quality": candidate.quality.grade,
            "method_family": self._method_family(candidate),
        }

    def _apply_diversity(
        self,
        scored: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        max_same = int(
            self.config.get("diversity", {}).get("max_same_method_family", 2)
        )
        family_counts: dict[str, int] = {}
        selected = []
        deferred = []
        for item in scored:
            family = item["method_family"]
            if family_counts.get(family, 0) >= max_same:
                deferred.append(item)
                continue
            selected.append(item)
            family_counts[family] = family_counts.get(family, 0) + 1
            if len(selected) == top_k:
                return sorted(
                    selected,
                    key=lambda candidate: (candidate["score"], candidate["paper_id"]),
                    reverse=True,
                )
        for item in deferred:
            if len(selected) == top_k:
                break
            selected.append(item)
        return sorted(
            selected,
            key=lambda candidate: (candidate["score"], candidate["paper_id"]),
            reverse=True,
        )

    @staticmethod
    def _relation_lookup(seed_id: str, edges: list[Any]) -> dict[str, Any]:
        matches: dict[str, Any] = {}
        for edge in edges:
            if edge.source_id == seed_id:
                other_id = edge.target_id
            elif edge.target_id == seed_id:
                other_id = edge.source_id
            else:
                continue
            existing = matches.get(other_id)
            if existing is None or edge.confidence * edge.score > existing.confidence * existing.score:
                matches[other_id] = edge
        return matches

    @staticmethod
    def _reasons(
        seed: Any,
        candidate: Any,
        raw: dict[str, float],
        relation: Any | None,
    ) -> list[str]:
        reasons = []
        if raw["topic_and_problem"] > 0:
            shared = sorted(
                set(seed.classification.problems)
                & set(candidate.classification.problems)
            )
            reasons.append(
                "profile.classification matches research problem"
                + (f": {', '.join(shared)}" if shared else "")
            )
        if raw["pipeline_stage"] > 0:
            shared = sorted(
                set(seed.classification.pipeline_stages)
                & set(candidate.classification.pipeline_stages)
            )
            reasons.append(f"profile.pipeline_stages overlap: {', '.join(shared)}")
        if raw["shared_dataset"] > 0:
            reasons.append("profile.experiment contains comparable datasets")
        if relation is not None:
            reasons.append(
                f"relation_graph contains {relation.relation_type} "
                f"(confidence={relation.confidence:.2f})"
            )
        if candidate.experiment.reproducibility.code_url:
            reasons.append("profile.reproducibility reports public code")
        if not reasons:
            reasons.append("profile quality and recency provide supporting signals")
        return reasons

    @staticmethod
    def _comparison_role(candidate: Any, shared_dataset: float, relation: Any | None) -> str:
        if candidate.identity.paper_type == "survey":
            return "foundation"
        if candidate.identity.paper_type in {"benchmark", "dataset"}:
            return "evaluation_benchmark"
        if relation and relation.relation_type in {"method_extension", "cites"}:
            return "method_extension"
        if shared_dataset > 0 or (
            relation and relation.relation_type in {"direct_comparison", "evaluation_comparable"}
        ):
            return "direct_comparison"
        return "method_extension"

    @staticmethod
    def _evidence_refs(candidate: Any, relation: Any | None) -> list[str]:
        refs = [
            *candidate.research_claim.evidence_ids[:2],
            *candidate.experiment.protocol.evidence_ids[:1],
        ]
        if relation:
            refs.extend(relation.evidence_refs[:2])
        return list(dict.fromkeys(refs))

    @staticmethod
    def _method_family(profile: Any) -> str:
        values = (
            profile.classification.technical_paradigms
            or profile.classification.research_directions
            or [profile.identity.paper_type]
        )
        return str(values[0])

    @staticmethod
    def _datasets(profile: Any) -> list[str]:
        return [
            dataset.registry_id or dataset.paper_name.casefold()
            for dataset in profile.experiment.datasets
        ]

    @staticmethod
    def _jaccard(left: list[str], right: list[str]) -> float:
        left_set, right_set = set(left), set(right)
        if not left_set or not right_set:
            return 0.0
        return len(left_set & right_set) / len(left_set | right_set)

    @staticmethod
    def _mean(*values: float) -> float:
        nonzero = [value for value in values if value > 0]
        return sum(nonzero) / len(nonzero) if nonzero else 0.0

    @staticmethod
    def _paper_year(paper_id: str, published_date: str) -> int:
        if published_date[:4].isdigit():
            return int(published_date[:4])
        if paper_id[:2].isdigit():
            return 2000 + int(paper_id[:2])
        return 2022

    @staticmethod
    def _load_config() -> dict[str, Any]:
        path = Path(settings.PROJECT_ROOT if hasattr(settings, "PROJECT_ROOT") else Path(__file__).parents[1])
        config_path = path / "config" / "recommendation_weights.yaml"
        if not config_path.exists():
            config_path = Path(__file__).parents[1] / "config" / "recommendation_weights.yaml"
        return yaml.safe_load(config_path.read_text(encoding="utf-8"))
