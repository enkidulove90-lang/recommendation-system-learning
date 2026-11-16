"""Tests for gate logic (Task 1)."""

from __future__ import annotations

import pytest

from ada_core.contracts import GateOutcome
from ada_core.data import load_mmssl_bundle, make_config
from ada_core.gates import (
    config_is_launchable,
    evaluate_config_gates,
    evaluate_p0_gates,
    gate_c3_split_audit,
    gate_c4_protocol_phase,
    gate_c5_configuration_completeness,
    p0_verdict,
)


def _resolved_config(mmssl_dir, feature_file, resolved_overrides, **kw):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    return make_config("run-gates", "P0", bundle, appendix_overrides=resolved_overrides, **kw)


def test_blocked_config_fails_c5_and_is_not_launchable(mmssl_dir, feature_file):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    config = make_config("blocked-run", "P0", bundle)  # unresolved appendix
    gates = evaluate_config_gates(config)
    by_id = {g.gate_id: g for g in gates}
    assert by_id["C5"].status == "blocked"
    assert "unresolved" in by_id["C5"].message
    launchable, _ = config_is_launchable(config)
    assert launchable is False


def test_resolved_config_passes_c1_to_c5(mmssl_dir, feature_file, resolved_overrides):
    config = _resolved_config(mmssl_dir, feature_file, resolved_overrides)
    gates = evaluate_config_gates(config)
    assert {g.gate_id for g in gates} == {"C1", "C2", "C3", "C4", "C5"}
    assert all(g.passed for g in gates), [g.to_json() for g in gates]
    launchable, _ = config_is_launchable(config)
    assert launchable is True


def test_c3_blocked_when_negative_review_unsigned(mmssl_dir, feature_file, resolved_overrides):
    bundle = load_mmssl_bundle(
        mmssl_dir, feature_paths={"image": feature_file},
        negative_review=True, review_note="",
    )
    config = make_config("unsigned", "P0", bundle, appendix_overrides=resolved_overrides)
    outcome = gate_c3_split_audit(config)
    assert outcome.status == "blocked"
    assert "review_note" in outcome.message

    # Signed note → C3 passes.
    bundle2 = load_mmssl_bundle(
        mmssl_dir, feature_paths={"image": feature_file},
        negative_review=True, review_note="audited by operator, 2026-11-16",
    )
    config2 = make_config("signed", "P0", bundle2, appendix_overrides=resolved_overrides)
    assert gate_c3_split_audit(config2).status == "pass"


def test_c4_p2_rejects_split_hash_mismatch(mmssl_dir, feature_file, resolved_overrides):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    config = make_config(
        "p2-run", "P2", bundle,
        appendix_overrides=resolved_overrides,
        baseline_run_id="baseline-1",
        baseline_split_hash="deadbeef" * 8,
    )
    outcome = gate_c4_protocol_phase(config)
    assert outcome.status == "fail"
    assert "rejected" in outcome.message

    # Matching hash passes.
    config2 = make_config(
        "p2-run", "P2", bundle,
        appendix_overrides=resolved_overrides,
        baseline_run_id="baseline-1",
        baseline_split_hash=bundle.split_audit.raw_split_hash,
    )
    assert gate_c4_protocol_phase(config2).status == "pass"


def test_p0_gate_failure_blocks_p1_transition():
    healthy = {
        "codebook_usage": [0.3, 0.4, 0.5],
        "grad_norm": [1.0, 0.9, 0.8],
        "memory_mb": [512, 640, 700],
        "step_ms": [10, 11, 12],
    }
    verdict = p0_verdict(healthy)
    assert verdict.status == "pass"
    assert "P1 transition permitted" in verdict.message

    collapsed = dict(healthy, codebook_usage=[0.3, 0.2, 0.005])
    verdict2 = p0_verdict(collapsed)
    assert verdict2.status == "fail"
    assert "G-P0-1" in verdict2.message

    individual = {g.gate_id: g for g in evaluate_p0_gates(collapsed)}
    assert individual["G-P0-1"].is_blocking
    assert individual["G-P0-2"].passed


def test_p0_gates_require_metric_series():
    verdict = p0_verdict({})
    assert verdict.status == "fail"
    for gate in evaluate_p0_gates({}):
        assert gate.status == "fail"
        assert gate.message


def test_gate_outcome_json_shape():
    outcome = GateOutcome("C2", "fail", "boom", {"n_unhealthy": 1})
    as_json = outcome.to_json()
    assert as_json == {
        "gate_id": "C2",
        "status": "fail",
        "message": "boom",
        "evidence": {"n_unhealthy": 1},
    }
