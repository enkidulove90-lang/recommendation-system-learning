"""ADA protocol contracts.

Immutable, typed records describing the experiment configuration, feature
registry, split audit and gate outcomes.  The contract layer is the single
source of truth for the *blocked / unblocked* protocol decision: a
configuration with any unresolved Appendix-A parameter is ``blocked`` and no
GPU process may ever be created for it (enforced again in the backend).

Design rules enforced here
--------------------------
* ``split_hash`` is the canonical hash of the raw split files and is part of
  every downstream comparison; mismatching baselines are *rejected*, never
  warned (see ``evaluation.py`` / backend service).
* Cold buckets (``cold_item`` / ``cold_user``) are computed from the *train*
  split only.
* Every gate outcome carries explicit pass/fail evidence fields so the UI can
  render a gate rail without re-deriving logic.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Small value objects
# ---------------------------------------------------------------------------

RUN_PHASES = ("P0", "P1", "P2")
TERMINAL_RUN_STATES = ("succeeded", "failed", "cancelled", "blocked")

GATE_STATUSES = ("pass", "fail", "warn", "blocked")


@dataclass(frozen=True)
class AppendixParam:
    """One of the 12 Appendix-A protocol values.

    A parameter with ``resolved=False`` (value ``None`` or missing rationale)
    blocks the whole configuration.
    """

    name: str
    value: Optional[float] = None
    resolved: bool = False
    rationale: str = ""
    source: str = ""  # e.g. "paper_appendix_A", "local_pilot"

    def blocking_reason(self) -> Optional[str]:
        if not self.resolved or self.value is None:
            return (
                f"Appendix-A parameter '{self.name}' is unresolved "
                f"(value={self.value!r}, resolved={self.resolved}); "
                f"resolve it with an explicit rationale before launching a run."
            )
        if not self.rationale.strip():
            return (
                f"Appendix-A parameter '{self.name}' has a value but no "
                f"recorded rationale; protocol requires an explicit rationale."
            )
        return None


@dataclass(frozen=True)
class FeatureEntry:
    """Canonical metadata for one registered feature matrix."""

    name: str
    path: str
    n_rows: int
    n_cols: int
    dtype: str
    sha256: str
    n_nonfinite: int = 0
    healthy: bool = True

    def evidence(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "shape": [self.n_rows, self.n_cols],
            "dtype": self.dtype,
            "sha256": self.sha256,
            "n_nonfinite": self.n_nonfinite,
            "healthy": self.healthy,
        }


@dataclass(frozen=True)
class FeatureRegistry:
    entries: Tuple[FeatureEntry, ...] = ()

    def by_name(self, name: str) -> Optional[FeatureEntry]:
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None

    def shapes(self) -> Dict[str, List[int]]:
        return {e.name: [e.n_rows, e.n_cols] for e in self.entries}

    def unhealthy(self) -> Tuple[FeatureEntry, ...]:
        return tuple(e for e in self.entries if not e.healthy)

    def to_json(self) -> Dict[str, Any]:
        return {"features": [e.evidence() for e in self.entries]}


@dataclass(frozen=True)
class DeviationEntry:
    """A registered deviation between paper protocol and local reality."""

    code: str
    level: str  # "high" | "mid" | "low" | "conditional"
    description: str
    handling: str


@dataclass(frozen=True)
class ColdBuckets:
    """Cold-start buckets computed **from the train split only**."""

    cold_item_max_train_freq: int
    cold_user_max_len: int
    cold_items: Tuple[int, ...] = ()
    cold_users: Tuple[int, ...] = ()
    warm_item_count: int = 0
    warm_user_count: int = 0

    def summary(self) -> Dict[str, Any]:
        return {
            "cold_item_rule": f"train_freq <= {self.cold_item_max_train_freq}",
            "cold_user_rule": f"train_seq_len <= {self.cold_user_max_len}",
            "n_cold_items": len(self.cold_items),
            "n_cold_users": len(self.cold_users),
            "n_warm_items": self.warm_item_count,
            "n_warm_users": self.warm_user_count,
        }


@dataclass(frozen=True)
class SplitAudit:
    """Audit record for a dataset bundle.

    ``raw_split_hash``  – sha256 over the ordered raw bytes of the split files.
    ``semantic_split_hash`` – sha256 over the order-independent interaction
    multiset, so two audits of the *same* content re-serialized differently can
    be compared.
    ``neg_hash`` – sha256 over (train pool + negative-sampling parameters).
    """

    dataset_name: str
    n_users: int
    n_items: int
    n_train: int
    n_valid: int
    n_test: int
    raw_split_hash: str
    semantic_split_hash: str
    neg_hash: str
    cold_buckets: ColdBuckets
    deviations: Tuple[DeviationEntry, ...] = ()
    review_note: str = ""
    status: str = "pass"  # pass | warn_review_required

    def evidence(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "n_users": self.n_users,
            "n_items": self.n_items,
            "n_train": self.n_train,
            "n_valid": self.n_valid,
            "n_test": self.n_test,
            "raw_split_hash": self.raw_split_hash,
            "semantic_split_hash": self.semantic_split_hash,
            "neg_hash": self.neg_hash,
            "cold_buckets": self.cold_buckets.summary(),
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# Gate outcome
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GateOutcome:
    """One gate verdict with explicit evidence fields."""

    gate_id: str  # "C1".."C5", "G-P0-1".."G-P0-4"
    status: str  # pass | fail | warn | blocked
    message: str
    evidence: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    @property
    def is_blocking(self) -> bool:
        return self.status in ("fail", "blocked")

    def to_json(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "message": self.message,
            "evidence": dict(self.evidence),
        }


# ---------------------------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------------------------

APPENDIX_A_PARAM_NAMES: Tuple[str, ...] = (
    "r3vae_L",            # number of quantizer references
    "r3vae_M",            # reference dimensionality
    "r3vae_top_k",        # top-K dot-product quantization
    "mmq_expert_hidden",  # hidden width of each MMQ expert
    "fusion_dim",         # fused representation width
    "downstream_hidden",  # downstream scorer hidden width
    "neg_pool_size",      # negative candidate pool size
    "neg_per_positive",   # negatives sampled per positive
    "eval_topk",          # ranking cutoff for reported metrics
    "grad_clip_norm",     # gradient clipping norm
    "weight_decay",       # optimizer weight decay
    "warmup_steps",       # LR warmup steps
)


@dataclass(frozen=True)
class ExperimentConfig:
    """Immutable experiment configuration.

    ``appendix_params`` must cover all 12 Appendix-A names.  ``is_blocked`` is
    derived, never stored, so a blocked config can never masquerade as ready.
    """

    run_id: str
    phase: str  # P0 | P1 | P2
    dataset_name: str
    seed: int
    appendix_params: Tuple[AppendixParam, ...]
    feature_registry: FeatureRegistry = field(default_factory=FeatureRegistry)
    split_audit: Optional[SplitAudit] = None
    max_steps: int = 200
    eval_interval: int = 20
    log_interval: int = 5
    artifact_root: str = ""
    baseline_run_id: Optional[str] = None  # P2 comparisons
    baseline_split_hash: Optional[str] = None
    is_synthetic_demo: bool = False
    switches: Mapping[str, bool] = field(default_factory=dict)

    def appendix_by_name(self, name: str) -> Optional[AppendixParam]:
        for p in self.appendix_params:
            if p.name == name:
                return p
        return None

    def blocking_issues(self) -> Tuple[str, ...]:
        issues: List[str] = []
        for param in self.appendix_params:
            reason = param.blocking_reason()
            if reason:
                issues.append(reason)
        missing = [n for n in APPENDIX_A_PARAM_NAMES if self.appendix_by_name(n) is None]
        for name in missing:
            issues.append(f"Appendix-A parameter '{name}' is missing from the configuration.")
        if self.phase not in RUN_PHASES:
            issues.append(f"Unknown protocol phase '{self.phase}'.")
        return tuple(issues)

    @property
    def is_blocked(self) -> bool:
        return bool(self.blocking_issues())

    def protocol_decision(self) -> "ProtocolDecision":
        if self.is_synthetic_demo:
            return ProtocolDecision(
                blocked=True,
                reasons=(
                    "Configuration references synthetic_demo artifacts; "
                    "demo data is never launchable.",
                ),
            )
        if self.is_blocked:
            return ProtocolDecision(blocked=True, reasons=self.blocking_issues())
        return ProtocolDecision(blocked=False, reasons=())

    def to_json(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "phase": self.phase,
            "dataset_name": self.dataset_name,
            "seed": self.seed,
            "appendix_params": [
                {
                    "name": p.name,
                    "value": p.value,
                    "resolved": p.resolved,
                    "rationale": p.rationale,
                }
                for p in self.appendix_params
            ],
            "features": self.feature_registry.to_json(),
            "split_audit": self.split_audit.evidence() if self.split_audit else None,
            "max_steps": self.max_steps,
            "eval_interval": self.eval_interval,
            "log_interval": self.log_interval,
            "baseline_run_id": self.baseline_run_id,
            "baseline_split_hash": self.baseline_split_hash,
            "is_synthetic_demo": self.is_synthetic_demo,
            "switches": dict(self.switches),
            "blocked": self.is_blocked,
            "blocking_issues": list(self.blocking_issues()),
        }

    @staticmethod
    def config_hash(config: "ExperimentConfig") -> str:
        payload = json.dumps(config.to_json(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProtocolDecision:
    blocked: bool
    reasons: Tuple[str, ...]

    def human_readable(self) -> str:
        if not self.blocked:
            return "Protocol checks passed; run may be launched."
        return "Blocked: " + " | ".join(self.reasons)


# ---------------------------------------------------------------------------
# Hash helpers shared with data.py
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def semantic_hash_interactions(interactions: Sequence[Tuple[int, int]]) -> str:
    """Order-independent hash over the (user, item) interaction multiset."""
    canonical = "\n".join(f"{u}\t{i}" for u, i in sorted(interactions))
    return sha256_bytes(canonical.encode("utf-8"))


def neg_hash_for(train_pairs: Sequence[Tuple[int, int]], seed: int, params: Mapping[str, Any]) -> str:
    payload = json.dumps(
        {"n_pairs": len(train_pairs), "seed": seed, "params": dict(params)},
        sort_keys=True,
    )
    return sha256_bytes(payload.encode("utf-8"))


def assert_finite(matrix: Any, name: str) -> int:
    """Return the number of non-finite cells in ``matrix`` (numpy-like)."""
    import numpy as np

    arr = np.asarray(matrix)
    if arr.dtype.kind not in "fc":
        return 0
    return int((~np.isfinite(arr)).sum())


def require_finite(matrix: Any, name: str) -> None:
    n_bad = assert_finite(matrix, name)
    if n_bad > 0:
        raise ValueError(
            f"Feature '{name}' contains {n_bad} non-finite value(s) "
            f"(NaN/Inf); refusing to register unhealthy features."
        )
