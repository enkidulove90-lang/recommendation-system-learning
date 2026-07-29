"""Chapter 2: transparent quality scoring with impact, disruption, novelty, and team signals."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


WEIGHTS = {
    "academic_impact": 0.20,
    "disruption": 0.15,
    "absolute_novelty": 0.20,
    "knowledge_evolution": 0.15,
    "collaboration": 0.10,
    "content_completeness": 0.10,
    "reproducibility": 0.10,
}


def clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def disruption_index(citing_focal_only: int, citing_prior_only: int, citing_both: int) -> float:
    """Return the bounded disruption score (N_i - N_j)/(N_i + N_j + N_k)."""
    total = citing_focal_only + citing_prior_only + citing_both
    if total <= 0:
        return 0.5
    return clamp((citing_focal_only - citing_prior_only + total) / (2 * total))


@dataclass(frozen=True)
class ScoreResult:
    score: float
    dimensions: dict[str, float]
    decision: str
    reasons: list[str]


class QualityScorerV2:
    """Pure scorer; callers provide cached metadata so no scoring request needs a paid service."""

    def __init__(self, threshold: float = 0.72) -> None:
        self.threshold = threshold

    def score(self, evidence: dict[str, Any]) -> ScoreResult:
        citing_q1 = float(evidence.get("citing_q1_ratio", 0.0))
        citations = max(float(evidence.get("citation_count", 0.0)), 0.0)
        age_months = max(float(evidence.get("age_months", 1.0)), 1.0)
        academic_impact = clamp(0.65 * citing_q1 + 0.35 * min(math.log1p(citations) / math.log(101), 1.0) * min(12 / age_months, 1.0))
        disruption = disruption_index(int(evidence.get("citing_focal_only", 0)), int(evidence.get("citing_prior_only", 0)), int(evidence.get("citing_both", 0)))
        combination_frequency = max(float(evidence.get("problem_method_frequency", 0.0)), 0.0)
        absolute_novelty = clamp(1.0 / (1.0 + math.log1p(combination_frequency)))
        improvements = [float(evidence.get(key, 0.0)) for key in ("method_improvement", "application_improvement", "dataset_improvement")]
        knowledge_evolution = clamp(sum(clamp(item) for item in improvements) / len(improvements))
        institutions = max(int(evidence.get("institution_count", 0)), 0)
        regions = max(int(evidence.get("region_count", 0)), 0)
        authors = max(int(evidence.get("author_count", 0)), 0)
        collaboration = clamp(0.45 * min(institutions / 4, 1.0) + 0.30 * min(regions / 3, 1.0) + 0.25 * min(authors / 8, 1.0))
        content_completeness = clamp(float(evidence.get("content_completeness", 0.0)))
        reproducibility = clamp(0.7 if evidence.get("official_code") else 0.35 if evidence.get("reproduction_tool") else 0.0)
        dimensions = {
            "academic_impact": academic_impact,
            "disruption": disruption,
            "absolute_novelty": absolute_novelty,
            "knowledge_evolution": knowledge_evolution,
            "collaboration": collaboration,
            "content_completeness": content_completeness,
            "reproducibility": reproducibility,
        }
        score = round(sum(dimensions[key] * WEIGHTS[key] for key in WEIGHTS), 4)
        reasons = [key for key, value in dimensions.items() if value >= 0.7]
        decision = "full_analysis" if score >= self.threshold else "basic_only"
        return ScoreResult(score=score, dimensions=dimensions, decision=decision, reasons=reasons)
