"""Deterministic validation and quality grading for ResearchProfileV2."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models.research_profile import (
    ProfileQuality,
    ProfileReview,
    ValidationIssue,
)
from skills.base_module import BaseSkill, register_skill
from skills.section_router import source_sha256
from storage.knowledge_registry import KnowledgeRegistry
from storage.paper_assets import normalize_arxiv_id
from storage.profile_store import ProfileStore
from storage.summary_compat import parse_summary_markdown


@register_skill("research-profile-validate")
class ProfileValidatorSkill(BaseSkill):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.registry = KnowledgeRegistry()
        self.store = ProfileStore()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        arxiv_id = normalize_arxiv_id(str(kwargs.get("arxiv_id", "")))
        profile = self.store.load_profile(arxiv_id)
        if profile is None:
            return {"error": f"Profile not found for {arxiv_id}", "issues": []}

        evidence = self.store.load_evidence(arxiv_id)
        issues: list[ValidationIssue] = []
        self._validate_asset_state(profile, issues)
        evidence_ids = {item.evidence_id for item in evidence.items} if evidence else set()
        referenced_ids = self._referenced_evidence_ids(profile)

        if evidence is None:
            issues.append(self._issue("error", "evidence_missing", "evidence", "Evidence bundle is missing."))
        for evidence_id in sorted(referenced_ids - evidence_ids):
            issues.append(
                self._issue(
                    "error",
                    "evidence_reference_missing",
                    "evidence_ids",
                    f"Referenced evidence does not exist: {evidence_id}",
                )
            )

        self._validate_taxonomy(profile, issues)
        self._validate_content(profile, issues)
        self._validate_source_hash(profile, issues)

        errors = sum(issue.severity == "error" for issue in issues)
        warnings = sum(issue.severity == "warning" for issue in issues)
        evidence_coverage = (
            len(referenced_ids & evidence_ids) / len(referenced_ids)
            if referenced_ids else 0.0
        )
        if errors:
            grade, status, confidence = "D", "failed", 0.2
        elif warnings >= 3 or evidence_coverage < 0.5:
            grade, status, confidence = "C", "needs_review", 0.55
        else:
            grade, status, confidence = "B", "validated", 0.82

        validated_at = datetime.now(timezone.utc).isoformat()
        profile.quality = ProfileQuality(
            status=status,
            grade=grade,
            confidence=confidence,
            issues=[issue.message for issue in issues],
            validated_at=validated_at,
        )
        profile_path = self.store.save_profile(profile)
        review = ProfileReview(
            paper_id=arxiv_id,
            profile_path=str(profile_path),
            status=status,
            grade=grade,
            issues=issues,
            generated_at=validated_at,
        )
        review_path = self.store.save_review(review)
        return {
            "error": None,
            "paper_id": arxiv_id,
            "grade": grade,
            "status": status,
            "confidence": confidence,
            "evidence_coverage": round(evidence_coverage, 3),
            "issues": [issue.model_dump(mode="json") for issue in issues],
            "profile_path": str(profile_path),
            "review_path": str(review_path),
        }

    def _validate_taxonomy(self, profile: Any, issues: list[ValidationIssue]) -> None:
        dimensions = (
            "research_directions",
            "pipeline_stages",
            "problems",
            "technical_paradigms",
            "modalities",
        )
        for dimension in dimensions:
            allowed = self.registry.allowed_tags(dimension)
            values = getattr(profile.classification, dimension)
            for value in values:
                if value not in allowed:
                    issues.append(
                        self._issue(
                            "error",
                            "unknown_controlled_tag",
                            f"classification.{dimension}",
                            f"Unknown controlled tag: {value}",
                        )
                    )

        if profile.identity.paper_type not in self.registry.allowed_tags("paper_type"):
            issues.append(
                self._issue(
                    "error",
                    "unknown_paper_type",
                    "identity.paper_type",
                    f"Unknown paper type: {profile.identity.paper_type}",
                )
            )

    @staticmethod
    def _validate_asset_state(profile: Any, issues: list[ValidationIssue]) -> None:
        summary_path = Path(profile.provenance.summary_path)
        if not profile.provenance.summary_path or not summary_path.exists():
            issues.append(
                ProfileValidatorSkill._issue(
                    "warning",
                    "summary_missing",
                    "provenance.summary_path",
                    "DeepSeek summary is missing.",
                )
            )
        else:
            summary = parse_summary_markdown(summary_path)
            summary_title = str(summary.get("title", ""))
            if (
                summary_title
                and profile.identity.title
                and not ProfileValidatorSkill._titles_are_compatible(
                    summary_title,
                    profile.identity.title,
                )
            ):
                issues.append(
                    ProfileValidatorSkill._issue(
                        "error",
                        "asset_identity_conflict",
                        "identity.title",
                        "Summary English title conflicts with the parsed paper title.",
                    )
                )
            conditions = summary.get("experimental_conditions", {})
            if conditions and all(
                value == "not_reported" for value in conditions.values()
            ):
                issues.append(
                    ProfileValidatorSkill._issue(
                        "warning",
                        "experimental_conditions_missing",
                        "experiment",
                        "Experimental conditions have not been extracted.",
                    )
                )

        if profile.provenance.parser == "local_pypdf":
            issues.append(
                ProfileValidatorSkill._issue(
                    "warning",
                    "lower_confidence_parser",
                    "provenance.parser",
                    "Local PDF fallback has lower structural confidence than MinerU.",
                )
            )

    @staticmethod
    def _titles_are_compatible(left: str, right: str) -> bool:
        import re

        left_words = set(re.findall(r"[a-z0-9]{3,}", left.casefold()))
        right_words = set(re.findall(r"[a-z0-9]{3,}", right.casefold()))
        if not left_words or not right_words:
            return True
        return (
            len(left_words & right_words) / min(len(left_words), len(right_words))
            >= 0.35
        )

    @staticmethod
    def _validate_content(profile: Any, issues: list[ValidationIssue]) -> None:
        if not profile.identity.title:
            issues.append(ProfileValidatorSkill._issue("warning", "title_missing", "identity.title", "English title is missing."))
        if not profile.research_claim.one_sentence_contribution:
            issues.append(
                ProfileValidatorSkill._issue(
                    "warning",
                    "contribution_missing",
                    "research_claim.one_sentence_contribution",
                    "Contribution is missing.",
                )
            )
        if profile.identity.paper_type == "experiment":
            if not profile.experiment.datasets:
                issues.append(
                    ProfileValidatorSkill._issue(
                        "warning",
                        "datasets_missing",
                        "experiment.datasets",
                        "Experiment paper has no registered datasets.",
                    )
                )
            if not profile.experiment.protocol.metrics:
                issues.append(
                    ProfileValidatorSkill._issue(
                        "warning",
                        "metrics_missing",
                        "experiment.protocol.metrics",
                        "Experiment paper has no extracted metrics.",
                    )
                )
        for index, result in enumerate(profile.experiment.results):
            if result.value is not None and not result.evidence_ids:
                issues.append(
                    ProfileValidatorSkill._issue(
                        "error",
                        "numeric_result_without_evidence",
                        f"experiment.results.{index}",
                        f"Numeric result for {result.metric} has no evidence.",
                    )
                )
        if profile.experiment.implementation.unreported_fields:
            issues.append(
                ProfileValidatorSkill._issue(
                    "info",
                    "implementation_incomplete",
                    "experiment.implementation",
                    "Unreported implementation fields: "
                    + ", ".join(profile.experiment.implementation.unreported_fields),
                )
            )

    @staticmethod
    def _validate_source_hash(profile: Any, issues: list[ValidationIssue]) -> None:
        source_path = Path(profile.provenance.source_path)
        if not source_path.exists():
            issues.append(
                ProfileValidatorSkill._issue(
                    "error",
                    "source_missing",
                    "provenance.source_path",
                    f"Parsed source does not exist: {source_path}",
                )
            )
            return
        current_hash = source_sha256(
            source_path.read_text(encoding="utf-8", errors="replace")
        )
        if current_hash != profile.provenance.source_hash:
            issues.append(
                ProfileValidatorSkill._issue(
                    "error",
                    "source_hash_changed",
                    "provenance.source_hash",
                    "Parsed source changed after profile generation.",
                )
            )

    @staticmethod
    def _referenced_evidence_ids(profile: Any) -> set[str]:
        values = set(profile.research_claim.evidence_ids)
        for component in profile.research_claim.method_components:
            values.update(component.evidence_ids)
        values.update(profile.experiment.protocol.evidence_ids)
        values.update(profile.experiment.implementation.evidence_ids)
        for result in profile.experiment.results:
            values.update(result.evidence_ids)
        for ablation in profile.experiment.ablations:
            values.update(ablation.evidence_ids)
        if profile.agent_design:
            values.update(profile.agent_design.evidence_ids)
        return values

    @staticmethod
    def _issue(severity: str, code: str, path: str, message: str) -> ValidationIssue:
        return ValidationIssue(
            severity=severity,
            code=code,
            path=path,
            message=message,
        )
