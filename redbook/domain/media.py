"""Domain models for figure selection and resumable creation workflow state."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class WorkflowStage(str, Enum):
    DISCOVERED = "discovered"
    PARSED = "parsed"
    FIGURES_READY = "figures_ready"
    REVIEWED = "reviewed"
    PACKAGED = "packaged"
    DRAFT_SAVED = "draft_saved"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class FigureCandidate:
    path: str
    source: str
    order: int
    width: int
    height: int
    bytes: int
    page: int | None = None
    figure_id: str = ""
    caption: str = ""
    section: str = ""
    role: str = "other"
    structural_score: float = 0.0
    eligible: bool = False
    rejection_reason: str = ""

    @property
    def pixels(self) -> int:
        return self.width * self.height

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VisionReview:
    path: str
    readability: float
    relevance: float
    text_legibility: float
    verdict: str
    reason: str

    @property
    def score(self) -> float:
        return round((self.readability * 0.45 + self.relevance * 0.35 + self.text_legibility * 0.20), 4)


@dataclass
class WorkflowCheckpoint:
    paper_id: str
    stage: WorkflowStage = WorkflowStage.DISCOVERED
    artifacts: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["stage"] = self.stage.value
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WorkflowCheckpoint":
        return cls(
            paper_id=str(value["paper_id"]),
            stage=WorkflowStage(value.get("stage", WorkflowStage.DISCOVERED.value)),
            artifacts=dict(value.get("artifacts", {})),
            history=list(value.get("history", [])),
        )


def existing_paths(paths: list[str]) -> list[Path]:
    return [Path(path) for path in paths if Path(path).is_file()]
