"""Pydantic schemas for the ADA backend API."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AppendixParamIn(BaseModel):
    name: str
    value: Optional[float] = None
    resolved: bool = False
    rationale: str = ""
    source: str = ""


class ConfigIn(BaseModel):
    run_id: str = Field(min_length=1, max_length=64)
    phase: Literal["P0", "P1", "P2"]
    dataset_name: str
    seed: int = 42
    train_dir: str
    feature_paths: Dict[str, str] = Field(default_factory=dict)
    appendix_params: List[AppendixParamIn] = Field(default_factory=list)
    max_steps: int = 200
    eval_interval: int = 20
    log_interval: int = 5
    baseline_run_id: Optional[str] = None
    baseline_split_hash: Optional[str] = None
    is_synthetic_demo: bool = False
    switches: Dict[str, bool] = Field(default_factory=dict)
    negative_review: bool = False
    review_note: str = ""


class ConfigValidationOut(BaseModel):
    run_id: str
    blocked: bool
    reasons: List[str] = Field(default_factory=list)
    human_readable: str
    config_hash: Optional[str] = None
    split_hash: Optional[str] = None


class RunOut(BaseModel):
    run_id: str
    phase: str
    status: str
    blocked: bool
    blocking_reasons: List[str] = Field(default_factory=list)
    config_hash: Optional[str] = None
    split_hash: Optional[str] = None
    pid: Optional[int] = None
    return_code: Optional[int] = None
    baseline_run_id: Optional[str] = None
    is_synthetic_demo: bool = False
    created_at: float = 0.0
    updated_at: float = 0.0


class RunCreated(BaseModel):
    run: RunOut
    validation: ConfigValidationOut


class ArtifactOut(BaseModel):
    name: str
    path: str
    sha256: Optional[str] = None
    kind: str = "file"


class TerminalEvent(BaseModel):
    seq: int
    status: str
    reason: str
