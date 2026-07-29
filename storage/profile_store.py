"""Persistence for profiles, evidence, reviews, and the paper registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import settings
from models.research_profile import EvidenceBundle, ProfileReview, ResearchProfileV2
from storage.asset_governance import AssetGovernance


class ProfileStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.DATA_DIR
        self.profiles_dir = self.data_dir / "profiles"
        self.evidence_dir = self.data_dir / "evidence"
        self.reviews_dir = self.data_dir / "reviews"
        self.registry_dir = self.data_dir / "registry"
        for directory in (
            self.profiles_dir,
            self.evidence_dir,
            self.reviews_dir,
            self.registry_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def save_profile(self, profile: ResearchProfileV2) -> Path:
        path = self.profiles_dir / f"{profile.paper_id}.json"
        self._write_json(path, profile.model_dump(mode="json"))
        self._upsert_registry(profile)
        return path

    def save_evidence(self, bundle: EvidenceBundle) -> Path:
        path = self.evidence_dir / f"{bundle.paper_id}.json"
        self._write_json(path, bundle.model_dump(mode="json"))
        return path

    def save_review(self, review: ProfileReview) -> Path:
        path = self.reviews_dir / f"{review.paper_id}.json"
        self._write_json(path, review.model_dump(mode="json"))
        return path

    def load_profile(self, arxiv_id: str) -> ResearchProfileV2 | None:
        path = self.profiles_dir / f"{arxiv_id}.json"
        if not path.exists():
            return None
        return ResearchProfileV2.model_validate_json(path.read_text(encoding="utf-8"))

    def load_evidence(self, arxiv_id: str) -> EvidenceBundle | None:
        path = self.evidence_dir / f"{arxiv_id}.json"
        if not path.exists():
            return None
        return EvidenceBundle.model_validate_json(path.read_text(encoding="utf-8"))

    def iter_profiles(self, *, include_quarantined: bool = False) -> list[ResearchProfileV2]:
        profiles: list[ResearchProfileV2] = []
        governance = AssetGovernance(self.data_dir)
        for path in sorted(self.profiles_dir.glob("*.json")):
            if not include_quarantined and governance.is_quarantined(path.stem):
                continue
            try:
                profiles.append(ResearchProfileV2.model_validate_json(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return profiles

    def export_schema(self) -> Path:
        path = self.registry_dir / "research_profile_v2.schema.json"
        self._write_json(path, ResearchProfileV2.model_json_schema())
        return path

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(path)

    def _upsert_registry(self, profile: ResearchProfileV2) -> None:
        path = self.registry_dir / "papers.jsonl"
        records: dict[str, dict[str, Any]] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                paper_id = str(item.get("paper_id", ""))
                if paper_id:
                    records[paper_id] = item

        records[profile.paper_id] = {
            "paper_id": profile.paper_id,
            "title": profile.identity.title,
            "chinese_title": profile.identity.chinese_title,
            "paper_type": profile.identity.paper_type,
            "classification": profile.classification.model_dump(mode="json"),
            "quality": profile.quality.model_dump(mode="json"),
            "profile_path": str(self.profiles_dir / f"{profile.paper_id}.json"),
            "evidence_path": str(self.evidence_dir / f"{profile.paper_id}.json"),
            "summary_path": profile.provenance.summary_path,
            "source_path": profile.provenance.source_path,
            "source_hash": profile.provenance.source_hash,
        }
        content = "\n".join(
            json.dumps(records[key], ensure_ascii=False, sort_keys=True)
            for key in sorted(records)
        )
        temporary = path.with_suffix(".jsonl.tmp")
        temporary.write_text(content + ("\n" if content else ""), encoding="utf-8")
        temporary.replace(path)
