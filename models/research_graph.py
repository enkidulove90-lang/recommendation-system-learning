"""Contracts for paper relations, learning paths, and profile reranking."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from models.research_profile import StrictModel


RelationType = Literal[
    "cites",
    "method_extension",
    "direct_comparison",
    "evaluation_comparable",
    "shared_dataset",
    "shared_problem",
    "shared_topic",
]


class RelationEdge(StrictModel):
    edge_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    directed: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    shared_features: dict[str, list[str]] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)


class RelationGraph(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    generated_at: str
    profile_count: int
    edges: list[RelationEdge] = Field(default_factory=list)


class LearningStep(StrictModel):
    order: int = Field(ge=1)
    paper_id: str
    title: str
    role: Literal[
        "foundation",
        "survey",
        "method",
        "benchmark",
        "application",
        "advanced",
    ]
    rationale: str
    prerequisites: list[str] = Field(default_factory=list)
    relation_edge_ids: list[str] = Field(default_factory=list)
    profile_quality: Literal["A", "B", "C", "D"]


class LearningPath(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    path_id: str
    topic: str
    level: Literal["beginner", "intermediate", "advanced"]
    objective: str
    generated_at: str
    steps: list[LearningStep] = Field(default_factory=list)


class ScoreBreakdown(StrictModel):
    topic_and_problem: float = 0.0
    pipeline_stage: float = 0.0
    paradigm_and_modality: float = 0.0
    shared_dataset: float = 0.0
    relation_graph: float = 0.0
    recency: float = 0.0
    profile_quality: float = 0.0


class RankedRecommendation(StrictModel):
    rank: int = Field(ge=1)
    paper_id: str
    title: str
    score: float = Field(ge=0.0, le=100.0)
    score_breakdown: ScoreBreakdown
    why_this_paper: list[str] = Field(default_factory=list)
    comparison_role: Literal[
        "foundation",
        "direct_comparison",
        "method_extension",
        "evaluation_benchmark",
    ]
    evidence_refs: list[str] = Field(default_factory=list)
    profile_quality: Literal["A", "B", "C", "D"]


class ProfileRecommendationReport(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    generated_at: str
    seed_id: str
    weights: dict[str, float]
    candidate_count: int
    recommendations: list[RankedRecommendation] = Field(default_factory=list)
