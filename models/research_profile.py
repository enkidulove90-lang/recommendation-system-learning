"""Pydantic contracts for the machine-readable research knowledge layer."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceReference(StrictModel):
    type: str = "arxiv"
    url: str = ""


class PaperIdentity(StrictModel):
    title: str = ""
    chinese_title: str = ""
    authors: list[str] = Field(default_factory=list)
    published_date: str = ""
    source: SourceReference = Field(default_factory=SourceReference)
    paper_type: str = "experiment"


class PaperClassification(StrictModel):
    research_directions: list[str] = Field(default_factory=list)
    pipeline_stages: list[str] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    technical_paradigms: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=list)
    maturity: str = "research_prototype"
    proposed_tags: list[str] = Field(default_factory=list)


class MethodComponent(StrictModel):
    name: str
    role: str = ""
    mechanism: str = ""
    evidence_ids: list[str] = Field(default_factory=list)


class ResearchClaim(StrictModel):
    problem: str = ""
    one_sentence_contribution: str = ""
    method_overview: str = ""
    method_components: list[MethodComponent] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class DatasetReference(StrictModel):
    registry_id: str | None = None
    paper_name: str


class ExperimentProtocol(StrictModel):
    task: str = "not_reported"
    split: str = "not_reported"
    metrics: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class HardwareSpec(StrictModel):
    model: str
    count: int | None = None


class ExperimentImplementation(StrictModel):
    hardware: list[HardwareSpec] = Field(default_factory=list)
    framework: str | None = None
    optimizer: str | None = None
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    unreported_fields: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class ExperimentResult(StrictModel):
    dataset: str | None = None
    metric: str
    value: float | None = None
    setting: str = ""
    comparison: str = ""
    delta: float | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class AblationFinding(StrictModel):
    component: str
    finding: str
    evidence_ids: list[str] = Field(default_factory=list)


class ReproducibilityInfo(StrictModel):
    code_url: str | None = None
    data_access: str = "not_reported"
    reproducibility_grade: Literal["A", "B", "C", "D"] = "C"


class ExperimentProfile(StrictModel):
    datasets: list[DatasetReference] = Field(default_factory=list)
    protocol: ExperimentProtocol = Field(default_factory=ExperimentProtocol)
    implementation: ExperimentImplementation = Field(default_factory=ExperimentImplementation)
    results: list[ExperimentResult] = Field(default_factory=list)
    results_summary: str = ""
    ablations: list[AblationFinding] = Field(default_factory=list)
    reproducibility: ReproducibilityInfo = Field(default_factory=ReproducibilityInfo)


class AgentDesignProfile(StrictModel):
    applicability: str = ""
    design_lessons: list[str] = Field(default_factory=list)
    source_type: Literal["paper_fact", "project_analysis", "mixed"] = "project_analysis"
    evidence_ids: list[str] = Field(default_factory=list)


class ProfileQuality(StrictModel):
    status: Literal["validated", "needs_review", "stale", "failed"] = "needs_review"
    grade: Literal["A", "B", "C", "D"] = "C"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    validated_at: str | None = None


class ProfileProvenance(StrictModel):
    parser: str = "unknown"
    summarizer_model: str = ""
    generated_at: str = ""
    source_path: str = ""
    source_hash: str = ""
    summary_path: str = ""
    summary_hash: str = ""


class ResearchProfileV2(StrictModel):
    schema_version: Literal["2.0"] = "2.0"
    paper_id: str
    identity: PaperIdentity = Field(default_factory=PaperIdentity)
    classification: PaperClassification = Field(default_factory=PaperClassification)
    research_claim: ResearchClaim = Field(default_factory=ResearchClaim)
    experiment: ExperimentProfile = Field(default_factory=ExperimentProfile)
    agent_design: AgentDesignProfile | None = None
    quality: ProfileQuality = Field(default_factory=ProfileQuality)
    provenance: ProfileProvenance = Field(default_factory=ProfileProvenance)


class EvidenceItem(StrictModel):
    evidence_id: str
    claim_type: str
    section: str
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    quote: str
    source_path: str
    source_hash: str
    extraction_method: str = "section_router"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class EvidenceBundle(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    paper_id: str
    source_path: str
    source_hash: str
    parser: str = "unknown"
    items: list[EvidenceItem] = Field(default_factory=list)


class ValidationIssue(StrictModel):
    severity: Literal["error", "warning", "info"]
    code: str
    path: str
    message: str


class ProfileReview(StrictModel):
    paper_id: str
    profile_path: str
    status: Literal["validated", "needs_review", "failed"]
    grade: Literal["A", "B", "C", "D"]
    issues: list[ValidationIssue] = Field(default_factory=list)
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    generated_at: str
