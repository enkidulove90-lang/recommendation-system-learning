"""MMSSL bundle loading, feature registry, split audit and negatives.

``load_mmssl_bundle`` is the only sanctioned way to turn on-disk data into
contract objects.  It enforces:

* feature health — non-finite (NaN/Inf) feature values abort registration;
* canonical feature metadata (shape, dtype, sha256);
* cold buckets computed **from the train split only**;
* raw + semantic split hashes and a deterministic ``neg_hash``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .contracts import (
    AppendixParam,
    ColdBuckets,
    DeviationEntry,
    ExperimentConfig,
    FeatureEntry,
    FeatureRegistry,
    SplitAudit,
    assert_finite,
    neg_hash_for,
    require_finite,
    semantic_hash_interactions,
    sha256_file,
)

MMSSL_SPLIT_NAMES = ("train", "valid", "test")


class FeatureHealthError(ValueError):
    """Raised when a feature matrix contains non-finite values."""


class SplitFormatError(ValueError):
    """Raised when split files do not follow the MMSSL id-sequence format."""


@dataclass
class MMSSLBundle:
    dataset_name: str
    train: List[List[int]]
    valid: List[List[int]]
    test: List[List[int]]
    feature_registry: FeatureRegistry
    split_audit: SplitAudit

    @property
    def n_users(self) -> int:
        return len(self.train)

    def interactions(self, split: str = "train") -> List[Tuple[int, int]]:
        seqs = getattr(self, split)
        return [(u, i) for u, seq in enumerate(seqs) for i in seq]


def _read_split(path: str) -> List[List[int]]:
    seqs: List[List[int]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            try:
                values = [int(x) for x in parts]
            except ValueError as exc:
                raise SplitFormatError(
                    f"{path}: expected integer id sequence, got malformed line"
                ) from exc
            if len(values) < 1:
                raise SplitFormatError(f"{path}: empty sequence line")
            if len(values) >= 2 and values[0] != len(seqs):
                raise SplitFormatError(
                    f"{path}: first column must be the 0-based user index; "
                    f"expected {len(seqs)}, got {values[0]}"
                )
            seqs.append(values[1:] if len(values) > 1 else [])
    return seqs


def _register_feature(path: str, name: str, expected_rows: Optional[int]) -> FeatureEntry:
    if not os.path.exists(path):
        raise FileNotFoundError(f"feature file for '{name}' not found: {path}")
    matrix = np.load(path)
    if matrix.ndim != 2:
        raise FeatureHealthError(
            f"feature '{name}' must be a 2-D matrix, got shape {matrix.shape}"
        )
    if expected_rows is not None and matrix.shape[0] != expected_rows:
        raise FeatureHealthError(
            f"feature '{name}' has {matrix.shape[0]} rows, expected {expected_rows} "
            f"(row order must equal item id); refusing to register a misaligned feature."
        )
    n_nonfinite = assert_finite(matrix, name)
    if n_nonfinite > 0:
        raise FeatureHealthError(
            f"feature '{name}' contains {n_nonfinite} non-finite value(s); "
            f"run feature cleanup or regenerate before launching."
        )
    return FeatureEntry(
        name=name,
        path=os.path.abspath(path),
        n_rows=int(matrix.shape[0]),
        n_cols=int(matrix.shape[1]),
        dtype=str(matrix.dtype),
        sha256=sha256_file(path),
        n_nonfinite=0,
        healthy=True,
    )


def compute_cold_buckets(
    train: Sequence[Sequence[int]],
    cold_item_max_train_freq: int = 5,
    cold_user_max_len: int = 3,
) -> ColdBuckets:
    """Cold buckets from the train split ONLY.

    Items that appear in valid/test but never/rarely in train do not move the
    cold-item set; user lengths are train-sequence lengths, never augmented by
    later splits.
    """
    freq: Dict[int, int] = {}
    for seq in train:
        for item in seq:
            freq[item] = freq.get(item, 0) + 1

    cold_items = tuple(sorted(i for i, c in freq.items() if c <= cold_item_max_train_freq))
    warm_items = len(freq) - len(cold_items)

    cold_users = tuple(u for u, seq in enumerate(train) if len(seq) <= cold_user_max_len)
    warm_users = len(train) - len(cold_users)

    return ColdBuckets(
        cold_item_max_train_freq=cold_item_max_train_freq,
        cold_user_max_len=cold_user_max_len,
        cold_items=cold_items,
        cold_users=cold_users,
        warm_item_count=warm_items,
        warm_user_count=warm_users,
    )


def audit_split(
    bundle_train: Sequence[Sequence[int]],
    bundle_valid: Sequence[Sequence[int]],
    bundle_test: Sequence[Sequence[int]],
    dataset_name: str,
    split_paths: Mapping[str, str],
    neg_params: Mapping[str, Any],
    seed: int,
    deviations: Sequence[DeviationEntry] = (),
    negative_review: bool = False,
    review_note: str = "",
) -> SplitAudit:
    train_pairs = [(u, i) for u, seq in enumerate(bundle_train) for i in seq]
    all_pairs = train_pairs + [
        (u, i) for u, seq in enumerate(bundle_valid) for i in seq
    ] + [(u, i) for u, seq in enumerate(bundle_test) for i in seq]

    raw_hash_parts = [sha256_file(split_paths[name]) for name in ("train", "valid", "test")]
    canonical_raw = "\n".join(raw_hash_parts)
    from .contracts import sha256_bytes

    raw_split_hash = sha256_bytes(canonical_raw.encode("utf-8"))
    semantic = semantic_hash_interactions(all_pairs)
    neg_hash = neg_hash_for(train_pairs, seed, neg_params)

    n_items = 1 + max(
        [i for seq in bundle_train for i in seq]
        + [i for seq in bundle_valid for i in seq]
        + [i for seq in bundle_test for i in seq]
        + [0]
    )

    status = "warn_review_required" if negative_review else "pass"

    return SplitAudit(
        dataset_name=dataset_name,
        n_users=len(bundle_train),
        n_items=n_items,
        n_train=len(train_pairs),
        n_valid=sum(len(s) for s in bundle_valid),
        n_test=sum(len(s) for s in bundle_test),
        raw_split_hash=raw_split_hash,
        semantic_split_hash=semantic,
        neg_hash=neg_hash,
        cold_buckets=compute_cold_buckets(bundle_train),
        deviations=tuple(deviations),
        status=status,
        review_note=review_note,
    )


def load_mmssl_bundle(
    dataset_dir: str,
    dataset_name: str = "mmssl_baby",
    feature_paths: Optional[Mapping[str, str]] = None,
    neg_params: Optional[Mapping[str, Any]] = None,
    seed: int = 42,
    deviations: Sequence[DeviationEntry] = (),
    negative_review: bool = False,
    review_note: str = "",
) -> MMSSLBundle:
    """Load split files (+ optional features) into a fully audited bundle."""
    split_paths = {
        name: os.path.join(dataset_dir, f"{name}.txt") for name in MMSSL_SPLIT_NAMES
    }
    for name, path in split_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"missing split file: {path}")

    train = _read_split(split_paths["train"])
    valid = _read_split(split_paths["valid"])
    test = _read_split(split_paths["test"])

    n_items = 1 + max(
        [i for seq in train for i in seq]
        + [i for seq in valid for i in seq]
        + [i for seq in test for i in seq]
        + [0]
    )

    entries: List[FeatureEntry] = []
    for name, path in (feature_paths or {}).items():
        entries.append(_register_feature(path, name, expected_rows=n_items))
    registry = FeatureRegistry(entries=tuple(entries))

    split_audit = audit_split(
        train,
        valid,
        test,
        dataset_name=dataset_name,
        split_paths=split_paths,
        neg_params=neg_params or {},
        seed=seed,
        deviations=deviations,
        negative_review=negative_review,
        review_note=review_note,
    )

    return MMSSLBundle(
        dataset_name=dataset_name,
        train=train,
        valid=valid,
        test=test,
        feature_registry=registry,
        split_audit=split_audit,
    )


# ---------------------------------------------------------------------------
# Negative sampling (train-only pool, deterministic)
# ---------------------------------------------------------------------------


def build_negative_pool(train: Sequence[Sequence[int]], seed: int) -> Tuple[int, ...]:
    rng = np.random.default_rng(seed)
    items = sorted({i for seq in train for i in seq})
    return tuple(int(x) for x in rng.permutation(items))


def sample_negatives(
    pool: Sequence[int],
    n_positive: int,
    neg_per_positive: int,
    seed: int,
    epoch: int = 0,
) -> List[int]:
    """Deterministic negatives derived from (seed, epoch) — no shared state."""
    rng = np.random.default_rng((seed, epoch))
    draws = rng.integers(0, len(pool), size=n_positive * neg_per_positive)
    return [pool[int(x)] for x in draws]


# ---------------------------------------------------------------------------
# Config assembly helpers
# ---------------------------------------------------------------------------


def resolve_appendix_params(
    overrides: Optional[Mapping[str, Tuple[float, str, str]]] = None,
) -> Tuple[AppendixParam, ...]:
    """Build the 12 Appendix-A parameter records.

    By default every parameter is **unresolved** (blocked configuration).
    Pass ``overrides={name: (value, rationale, source)}`` to resolve entries.
    """
    from .contracts import APPENDIX_A_PARAM_NAMES

    overrides = overrides or {}
    params: List[AppendixParam] = []
    for name in APPENDIX_A_PARAM_NAMES:
        if name in overrides:
            value, rationale, source = overrides[name]
            params.append(
                AppendixParam(
                    name=name,
                    value=float(value),
                    resolved=True,
                    rationale=rationale,
                    source=source,
                )
            )
        else:
            params.append(AppendixParam(name=name, value=None, resolved=False, rationale=""))
    return tuple(params)


def make_config(
    run_id: str,
    phase: str,
    bundle: MMSSLBundle,
    seed: int = 42,
    appendix_overrides: Optional[Mapping[str, Tuple[float, str, str]]] = None,
    max_steps: int = 200,
    eval_interval: int = 20,
    log_interval: int = 5,
    artifact_root: str = "",
    baseline_run_id: Optional[str] = None,
    baseline_split_hash: Optional[str] = None,
    is_synthetic_demo: bool = False,
    switches: Optional[Mapping[str, bool]] = None,
) -> ExperimentConfig:
    return ExperimentConfig(
        run_id=run_id,
        phase=phase,
        dataset_name=bundle.dataset_name,
        seed=seed,
        appendix_params=resolve_appendix_params(appendix_overrides),
        feature_registry=bundle.feature_registry,
        split_audit=bundle.split_audit,
        max_steps=max_steps,
        eval_interval=eval_interval,
        log_interval=log_interval,
        artifact_root=artifact_root,
        baseline_run_id=baseline_run_id,
        baseline_split_hash=baseline_split_hash,
        is_synthetic_demo=is_synthetic_demo,
        switches=switches or {},
    )
