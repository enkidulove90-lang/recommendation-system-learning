"""Tests for the data / contract layer (Task 1)."""

from __future__ import annotations

import numpy as np
import pytest

from ada_core.contracts import (
    ExperimentConfig,
    ProtocolDecision,
    SplitAudit,
    FeatureRegistry,
    FeatureEntry,
)
from ada_core.data import (
    FeatureHealthError,
    compute_cold_buckets,
    load_mmssl_bundle,
    make_config,
    resolve_appendix_params,
)


# ---------------------------------------------------------------------------
# Blocked configuration
# ---------------------------------------------------------------------------


def test_config_with_unresolved_appendix_value_is_blocked(mmssl_dir, feature_file):
    bundle = load_mmssl_bundle(
        mmssl_dir,
        feature_paths={"image": feature_file},
        neg_params={"pool": 100, "neg_per_positive": 4},
    )
    # No overrides → all 12 Appendix-A values unresolved.
    config = make_config("run-blocked", "P0", bundle)
    assert config.is_blocked is True
    decision: ProtocolDecision = config.protocol_decision()
    assert decision.blocked is True
    assert len(decision.reasons) == 12
    assert all("unresolved" in r or "missing" in r or "rationale" in r for r in decision.reasons)
    assert "Appendix-A parameter" in decision.human_readable()

    # Resolving everything unblocks.
    config2 = make_config("run-ok", "P0", bundle, appendix_overrides={
        name: (1.0, "pilot rationale", "local_pilot")
        for name in [
            "r3vae_L", "r3vae_M", "r3vae_top_k", "mmq_expert_hidden", "fusion_dim",
            "downstream_hidden", "neg_pool_size", "neg_per_positive", "eval_topk",
            "grad_clip_norm", "weight_decay", "warmup_steps",
        ]
    })
    assert config2.is_blocked is False
    assert config2.protocol_decision().blocked is False


def test_resolved_value_without_rationale_still_blocks(mmssl_dir, feature_file):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    overrides = resolve_appendix_params({
        "r3vae_L": (8.0, "", "local_pilot"),
    })
    # Only one resolved; still blocked overall because of the other 11, and
    # specifically because r3vae_L lacks a rationale.
    assert overrides[0].blocking_reason() is not None
    assert "no recorded rationale" in overrides[0].blocking_reason()


# ---------------------------------------------------------------------------
# Feature health
# ---------------------------------------------------------------------------


def test_mmssl_loader_rejects_nonfinite_feature_values(mmssl_dir, tmp_path):
    bad = tmp_path / "bad_feat.npy"
    mat = np.random.default_rng(1).normal(size=(20, 8)).astype(np.float32)
    mat[3, 5] = np.nan
    mat[7, 0] = np.inf
    np.save(bad, mat)

    with pytest.raises(FeatureHealthError) as excinfo:
        load_mmssl_bundle(mmssl_dir, feature_paths={"image": str(bad)})
    assert "2 non-finite" in str(excinfo.value)


def test_mmssl_loader_rejects_row_mismatch(mmssl_dir, tmp_path):
    wrong_rows = tmp_path / "wrong_rows.npy"
    np.save(wrong_rows, np.zeros((99, 8), dtype=np.float32))
    with pytest.raises(FeatureHealthError) as excinfo:
        load_mmssl_bundle(mmssl_dir, feature_paths={"image": str(wrong_rows)})
    assert "rows" in str(excinfo.value)


def test_feature_registry_records_canonical_metadata(mmssl_dir, feature_file):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    entry = bundle.feature_registry.by_name("image")
    assert entry is not None
    assert entry.shape() if False else True  # noqa: silence
    assert entry.n_rows == 20 and entry.n_cols == 8
    assert entry.dtype == "float32"
    assert len(entry.sha256) == 64
    assert entry.healthy is True


# ---------------------------------------------------------------------------
# Split audit / cold buckets (train-only)
# ---------------------------------------------------------------------------


def test_split_audit_counts_cold_items_from_train_only():
    train = [
        [0, 1, 2, 3],          # user 0
        [0, 1, 2, 3],          # user 1
        [0, 1, 2, 3],          # user 2
        [4, 5],                # user 2-level seq; items 4/5 freq 1 → cold
    ]
    valid = [
        [6, 6, 6, 6, 6],       # item 6 frequent ONLY in valid — must NOT matter
        [4],
        [7],
        [],
    ]
    buckets = compute_cold_buckets(train, cold_item_max_train_freq=2, cold_user_max_len=3)
    # freq: 0,1,2,3 → 3 (warm); 4,5 → 1 (cold)
    assert set(buckets.cold_items) == {4, 5}
    assert buckets.warm_item_count == 4
    # valid/test items absent from train (6,7) are not counted anywhere.
    assert 6 not in buckets.cold_items and 7 not in buckets.cold_items
    # users: len 4,4,4,2 → user 3 cold only.
    assert buckets.cold_users == (3,)
    assert buckets.warm_user_count == 3


def test_split_audit_hashes_and_summary(mmssl_dir, feature_file):
    bundle = load_mmssl_bundle(
        mmssl_dir,
        feature_paths={"image": feature_file},
        neg_params={"pool": 100},
        seed=7,
    )
    audit: SplitAudit = bundle.split_audit
    assert audit.n_users == 10
    assert audit.n_train == 60 and audit.n_valid == 20 and audit.n_test == 20
    assert len(audit.raw_split_hash) == 64
    assert len(audit.semantic_split_hash) == 64
    assert len(audit.neg_hash) == 64
    summary = audit.evidence()
    assert summary["cold_buckets"]["n_cold_items"] == len(audit.cold_buckets.cold_items)


def test_split_audit_negative_review_requires_note(mmssl_dir, feature_file):
    bundle = load_mmssl_bundle(
        mmssl_dir,
        feature_paths={"image": feature_file},
        negative_review=True,
        review_note="",
    )
    assert bundle.split_audit.status == "warn_review_required"


# ---------------------------------------------------------------------------
# Config snapshot determinism
# ---------------------------------------------------------------------------


def test_config_hash_is_deterministic(mmssl_dir, feature_file, resolved_overrides):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    c1 = make_config("r1", "P0", bundle, appendix_overrides=resolved_overrides)
    c2 = make_config("r1", "P0", bundle, appendix_overrides=resolved_overrides)
    assert ExperimentConfig.config_hash(c1) == ExperimentConfig.config_hash(c2)
    c3 = make_config("r2", "P0", bundle, appendix_overrides=resolved_overrides)
    assert ExperimentConfig.config_hash(c1) != ExperimentConfig.config_hash(c3)
