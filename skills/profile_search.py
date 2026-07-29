"""Search local ResearchProfileV2 records with controlled filters."""

from __future__ import annotations

import json
from typing import Any

from skills.base_module import BaseSkill, register_skill
from storage.profile_store import ProfileStore


_GRADE_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1}


@register_skill("research-profile-search")
class ProfileSearchSkill(BaseSkill):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.store = ProfileStore()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        stage = str(kwargs.get("stage", "")).strip()
        problem = str(kwargs.get("problem", "")).strip()
        paradigm = str(kwargs.get("paradigm", "")).strip()
        modality = str(kwargs.get("modality", "")).strip()
        query = str(kwargs.get("query", "")).strip().casefold()
        quality_values = {
            value.strip().upper()
            for value in str(kwargs.get("quality", "")).split(",")
            if value.strip()
        }
        limit = max(1, int(kwargs.get("limit", 20)))

        matches = []
        for profile in self.store.iter_profiles():
            classification = profile.classification
            if stage and stage not in classification.pipeline_stages:
                continue
            if problem and problem not in classification.problems:
                continue
            if paradigm and paradigm not in classification.technical_paradigms:
                continue
            if modality and modality not in classification.modalities:
                continue
            if quality_values and profile.quality.grade not in quality_values:
                continue
            if query:
                searchable = json.dumps(profile.model_dump(mode="json"), ensure_ascii=False).casefold()
                if query not in searchable:
                    continue
            matches.append(profile)

        matches.sort(
            key=lambda profile: (
                _GRADE_ORDER.get(profile.quality.grade, 0),
                profile.identity.published_date,
                profile.paper_id,
            ),
            reverse=True,
        )
        results = [
            {
                "paper_id": profile.paper_id,
                "title": profile.identity.title,
                "chinese_title": profile.identity.chinese_title,
                "paper_type": profile.identity.paper_type,
                "research_directions": profile.classification.research_directions,
                "pipeline_stages": profile.classification.pipeline_stages,
                "problems": profile.classification.problems,
                "technical_paradigms": profile.classification.technical_paradigms,
                "modalities": profile.classification.modalities,
                "datasets": [dataset.paper_name for dataset in profile.experiment.datasets],
                "metrics": profile.experiment.protocol.metrics,
                "quality": profile.quality.model_dump(mode="json"),
                "profile_path": str(self.store.profiles_dir / f"{profile.paper_id}.json"),
            }
            for profile in matches[:limit]
        ]
        return {"results": results, "total": len(matches), "error": None}
