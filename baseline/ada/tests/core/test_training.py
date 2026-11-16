"""P0 lifecycle tests (Task 3)."""

from __future__ import annotations

import json
import os

import pytest
import torch

from ada_core.data import load_mmssl_bundle, make_config
from ada_core.evaluation import SplitHashMismatchError, RankingEvaluator
from ada_core.gates import config_is_launchable
from ada_core.training import (
    EventLog,
    RunOutcome,
    Trainer,
    assert_p1_transition_allowed,
)


def _resolved_config(tmp_path, mmssl_dir, feature_file, resolved_overrides, **kw):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    artifact_root = str(tmp_path / "artifacts")
    return make_config(
        kw.pop("run_id", "run-train"), "P0", bundle,
        appendix_overrides=resolved_overrides,
        artifact_root=artifact_root,
        max_steps=kw.pop("max_steps", 10),
        eval_interval=kw.pop("eval_interval", 5),
        log_interval=kw.pop("log_interval", 2),
        **kw,
    ), bundle


def test_p0_gate_failure_prevents_p1_transition(tmp_path, mmssl_dir, feature_file, resolved_overrides):
    config, bundle = _resolved_config(
        tmp_path, mmssl_dir, feature_file, resolved_overrides, run_id="failing-p0",
    )
    events = EventLog(str(tmp_path / "events.jsonl"))
    trainer = Trainer(config, bundle, events)
    assert trainer.launchable
    outcome = trainer.run()

    # Force a failing G-P0 verdict through an unhealthy metric series.
    failing_outcome = RunOutcome(
        run_id=config.run_id, status="failed", reason="simulated",
        p0_verdict={
            "gate_id": "G-P0", "status": "fail",
            "message": "P0 gate failed at: G-P0-1",
            "evidence": {"gates": [{"gate_id": "G-P0-1", "status": "fail"}]},
        },
    )
    with pytest.raises(PermissionError) as excinfo:
        assert_p1_transition_allowed(failing_outcome)
    assert "P1 is blocked" in str(excinfo.value) or "blocked" in str(excinfo.value)

    # A healthy outcome permits the transition.
    healthy = RunOutcome(
        run_id=config.run_id, status="succeeded", reason="ok",
        p0_verdict={"gate_id": "G-P0", "status": "pass", "message": "ok", "evidence": {}},
    )
    assert_p1_transition_allowed(healthy)  # must not raise


def test_metrics_include_usage_grad_loss_memory_and_step_timing(
    tmp_path, mmssl_dir, feature_file, resolved_overrides
):
    config, bundle = _resolved_config(
        tmp_path, mmssl_dir, feature_file, resolved_overrides, run_id="metrics-run",
    )
    events = EventLog(str(tmp_path / "events.jsonl"))
    outcome = Trainer(config, bundle, events).run()
    metrics = outcome.final_metrics
    for key in ("codebook_usage", "grad_norm", "memory_mb", "step_ms", "loss"):
        assert key in metrics and len(metrics[key]) == config.max_steps
    assert outcome.p0_verdict["status"] in ("pass", "fail")

    # JSONL events were emitted at log_interval and eval_interval.
    with open(events.path, encoding="utf-8") as fh:
        events_seen = [json.loads(line) for line in fh if line.strip()]
    kinds = [e["event"] for e in events_seen]
    assert "run_started" in kinds and "step_metrics" in kinds
    assert "eval_metrics" in kinds and "p0_verdict" in kinds and "run_terminal" in kinds
    seqs = [e["seq"] for e in events_seen]
    assert seqs == sorted(seqs) and len(set(seqs)) == len(seqs)


def test_evaluation_rejects_baseline_with_different_split_hash(
    tmp_path, mmssl_dir, feature_file, resolved_overrides
):
    config, bundle = _resolved_config(
        tmp_path, mmssl_dir, feature_file, resolved_overrides, run_id="eval-run",
    )
    evaluator = RankingEvaluator(bundle, config)
    good = evaluator.compare_to_baseline({"run_id": "b1", "split_hash": evaluator.split_hash})
    assert good["status"] == "accepted"

    with pytest.raises(SplitHashMismatchError) as excinfo:
        evaluator.compare_to_baseline({"run_id": "b2", "split_hash": "deadbeef" * 8})
    assert "rejected" in str(excinfo.value)


def test_blocked_config_never_reaches_training(
    tmp_path, mmssl_dir, feature_file
):
    bundle = load_mmssl_bundle(mmssl_dir, feature_paths={"image": feature_file})
    config = make_config("blocked-run", "P0", bundle, artifact_root=str(tmp_path / "a"))
    events = EventLog(str(tmp_path / "blocked-events.jsonl"))
    trainer = Trainer(config, bundle, events)
    outcome = trainer.run()
    assert outcome.status == "blocked"
    assert outcome.steps_completed == 0
    assert outcome.final_metrics is None
    # No artifact metrics file, no checkpoint metadata written.
    assert not os.path.exists(os.path.join(str(tmp_path / "a"), "blocked-run", "metrics.json"))
    kinds = [json.loads(l)["event"] for l in open(events.path, encoding="utf-8")]
    assert "config_blocked" in kinds and "run_terminal" in kinds


def test_early_stop_without_valid_metrics_fails(tmp_path, mmssl_dir, feature_file, resolved_overrides):
    config, bundle = _resolved_config(
        tmp_path, mmssl_dir, feature_file, resolved_overrides,
        run_id="no-eval", max_steps=10, eval_interval=100,  # no eval happens
    )
    events = EventLog(str(tmp_path / "no-eval.jsonl"))
    outcome = Trainer(config, bundle, events).run()
    assert outcome.status == "failed"
    assert "valid metrics" in outcome.reason


def test_artifact_manifest_and_snapshot_written(
    tmp_path, mmssl_dir, feature_file, resolved_overrides
):
    config, bundle = _resolved_config(
        tmp_path, mmssl_dir, feature_file, resolved_overrides, run_id="manifest-run",
    )
    artifact_dir = os.path.join(config.artifact_root, config.run_id)
    events = EventLog(os.path.join(artifact_dir, "events.jsonl"))
    outcome = Trainer(config, bundle, events).run()
    for name in ("config_snapshot.json", "artifact_manifest.json", "metrics.json", "events.jsonl"):
        assert os.path.exists(os.path.join(artifact_dir, name)), name
    manifest = json.load(open(os.path.join(artifact_dir, "artifact_manifest.json")))
    assert manifest["split_hash"] == bundle.split_audit.raw_split_hash
    assert manifest["config_hash"]
