"""Build citation and high-confidence semantic relations between active profiles."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models.research_graph import RelationEdge, RelationGraph
from skills.base_module import BaseSkill, register_skill
from storage.profile_store import ProfileStore
from storage.research_graph_store import ResearchGraphStore


_ARXIV_REFERENCE_RE = re.compile(
    r"(?:arXiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})",
    flags=re.IGNORECASE,
)


@register_skill("research-relations-build")
class RelationBuilderSkill(BaseSkill):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.profiles = ProfileStore()
        self.graphs = ResearchGraphStore()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        requested_id = str(kwargs.get("arxiv_id", "")).strip()
        max_semantic_edges = max(1, int(kwargs.get("max_semantic_edges", 6)))
        profiles = [
            profile
            for profile in self.profiles.iter_profiles()
            if profile.quality.grade in {"A", "B", "C"}
        ]
        by_id = {profile.paper_id: profile for profile in profiles}
        if requested_id and requested_id not in by_id:
            return {
                "error": f"Active profile not found for {requested_id}",
                "edge_count": 0,
            }

        citation_targets = {
            profile.paper_id: self._citation_targets(profile.provenance.source_path, set(by_id))
            for profile in profiles
        }
        edges: list[RelationEdge] = []
        for source_id, targets in citation_targets.items():
            source = by_id[source_id]
            for target_id in sorted(targets):
                if target_id == source_id:
                    continue
                target = by_id[target_id]
                shared = self._shared_features(source, target)
                relation_type = self._citation_relation_type(shared)
                edges.append(
                    self._edge(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type=relation_type,
                        directed=True,
                        confidence=0.98,
                        score=max(0.65, self._semantic_score(shared)),
                        reasons=[
                            f"{source_id} explicitly references {target_id}",
                            *self._shared_reasons(shared),
                        ],
                        shared=shared,
                        evidence_refs=[f"source:{source_id}:citation:{target_id}"],
                    )
                )

        semantic_candidates: dict[str, list[tuple[float, RelationEdge]]] = {
            paper_id: [] for paper_id in by_id
        }
        profile_list = list(by_id.values())
        for index, source in enumerate(profile_list):
            for target in profile_list[index + 1 :]:
                shared = self._shared_features(source, target)
                score = self._semantic_score(shared)
                if score < 0.34:
                    continue
                relation_type = self._semantic_relation_type(shared)
                confidence = min(0.95, 0.55 + score * 0.4)
                edge = self._edge(
                    source_id=source.paper_id,
                    target_id=target.paper_id,
                    relation_type=relation_type,
                    directed=False,
                    confidence=confidence,
                    score=score,
                    reasons=self._shared_reasons(shared),
                    shared=shared,
                    evidence_refs=self._profile_evidence_refs(source, target),
                )
                semantic_candidates[source.paper_id].append((score, edge))
                semantic_candidates[target.paper_id].append((score, edge))

        selected_edge_ids: set[str] = set()
        for candidates in semantic_candidates.values():
            for _, edge in sorted(candidates, key=lambda item: item[0], reverse=True)[
                :max_semantic_edges
            ]:
                if edge.edge_id not in selected_edge_ids:
                    selected_edge_ids.add(edge.edge_id)
                    edges.append(edge)

        edges.sort(
            key=lambda edge: (
                edge.source_id,
                edge.target_id,
                edge.relation_type,
                edge.edge_id,
            )
        )
        graph = RelationGraph(
            generated_at=datetime.now(timezone.utc).isoformat(),
            profile_count=len(profiles),
            edges=edges,
        )
        graph_path, jsonl_path = self.graphs.save_graph(graph)
        selected = [
            edge.model_dump(mode="json")
            for edge in edges
            if not requested_id
            or edge.source_id == requested_id
            or edge.target_id == requested_id
        ]
        return {
            "error": None,
            "profile_count": len(profiles),
            "edge_count": len(edges),
            "selected_edge_count": len(selected),
            "edges": selected,
            "graph_path": str(graph_path),
            "jsonl_path": str(jsonl_path),
        }

    @staticmethod
    def _citation_targets(source_path: str, local_ids: set[str]) -> set[str]:
        path = Path(source_path)
        if not path.exists():
            return set()
        text = path.read_text(encoding="utf-8", errors="replace")
        return {
            match.group(1)
            for match in _ARXIV_REFERENCE_RE.finditer(text)
            if match.group(1) in local_ids
        }

    @staticmethod
    def _shared_features(source: Any, target: Any) -> dict[str, list[str]]:
        source_datasets = {
            dataset.registry_id or dataset.paper_name.casefold()
            for dataset in source.experiment.datasets
        }
        target_datasets = {
            dataset.registry_id or dataset.paper_name.casefold()
            for dataset in target.experiment.datasets
        }
        dimensions = {
            "research_directions": (
                source.classification.research_directions,
                target.classification.research_directions,
            ),
            "pipeline_stages": (
                source.classification.pipeline_stages,
                target.classification.pipeline_stages,
            ),
            "problems": (
                source.classification.problems,
                target.classification.problems,
            ),
            "technical_paradigms": (
                source.classification.technical_paradigms,
                target.classification.technical_paradigms,
            ),
            "modalities": (
                source.classification.modalities,
                target.classification.modalities,
            ),
            "datasets": (source_datasets, target_datasets),
            "metrics": (
                source.experiment.protocol.metrics,
                target.experiment.protocol.metrics,
            ),
        }
        return {
            name: sorted(set(left) & set(right))
            for name, (left, right) in dimensions.items()
            if set(left) & set(right)
        }

    @staticmethod
    def _semantic_score(shared: dict[str, list[str]]) -> float:
        weights = {
            "research_directions": 0.20,
            "pipeline_stages": 0.15,
            "problems": 0.20,
            "technical_paradigms": 0.15,
            "modalities": 0.10,
            "datasets": 0.15,
            "metrics": 0.05,
        }
        score = 0.0
        for dimension, values in shared.items():
            score += weights.get(dimension, 0.0) * min(1.0, 0.5 + 0.25 * len(values))
        return round(min(1.0, score), 4)

    @staticmethod
    def _citation_relation_type(shared: dict[str, list[str]]) -> str:
        if shared.get("datasets") and shared.get("metrics"):
            return "direct_comparison"
        if shared.get("technical_paradigms") or shared.get("pipeline_stages"):
            return "method_extension"
        return "cites"

    @staticmethod
    def _semantic_relation_type(shared: dict[str, list[str]]) -> str:
        if shared.get("datasets") and shared.get("metrics"):
            return "evaluation_comparable"
        if shared.get("datasets"):
            return "shared_dataset"
        if shared.get("problems"):
            return "shared_problem"
        return "shared_topic"

    @staticmethod
    def _shared_reasons(shared: dict[str, list[str]]) -> list[str]:
        labels = {
            "research_directions": "research direction",
            "pipeline_stages": "pipeline stage",
            "problems": "research problem",
            "technical_paradigms": "technical paradigm",
            "modalities": "modality",
            "datasets": "dataset",
            "metrics": "metric",
        }
        return [
            f"Shared {labels.get(name, name)}: {', '.join(values)}"
            for name, values in shared.items()
        ]

    @staticmethod
    def _profile_evidence_refs(source: Any, target: Any) -> list[str]:
        refs = [
            *source.research_claim.evidence_ids[:2],
            *target.research_claim.evidence_ids[:2],
        ]
        return list(dict.fromkeys(refs))

    @staticmethod
    def _edge(
        *,
        source_id: str,
        target_id: str,
        relation_type: str,
        directed: bool,
        confidence: float,
        score: float,
        reasons: list[str],
        shared: dict[str, list[str]],
        evidence_refs: list[str],
    ) -> RelationEdge:
        pair = f"{source_id}|{target_id}" if directed else "|".join(sorted((source_id, target_id)))
        edge_id = "rel_" + hashlib.sha1(
            f"{pair}|{relation_type}".encode("utf-8")
        ).hexdigest()[:16]
        return RelationEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            directed=directed,
            confidence=round(confidence, 4),
            score=round(score, 4),
            reasons=reasons,
            shared_features=shared,
            evidence_refs=evidence_refs,
        )
