"""Backend-launched experiment entrypoint.

Usage:
    python scripts/run_experiment.py --config-path <config.json> --phase P0

Reads a serialized ExperimentConfig JSON (as produced by
``ExperimentConfig.to_json``), rebuilds the objects, runs the trainer and
exits with a status code the backend runner persists:

    0  succeeded (P0 gates passed)
    2  blocked (C-gates) — no GPU work was performed
    1  failed (P0 gate failure or runtime error)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

BASELINE_ADA = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(BASELINE_ADA, "core"), BASELINE_ADA):
    if p not in sys.path:
        sys.path.insert(0, p)


def rebuild_config(payload: dict):
    from ada_core.contracts import (
        AppendixParam,
        ExperimentConfig,
        FeatureEntry,
        FeatureRegistry,
    )
    from ada_core.data import MMSSLBundle, audit_split

    params = tuple(
        AppendixParam(
            name=p["name"],
            value=p["value"],
            resolved=p["resolved"],
            rationale=p.get("rationale", ""),
        )
        for p in payload["appendix_params"]
    )
    features = tuple(
        FeatureEntry(
            name=f["name"],
            path=f.get("path", ""),
            n_rows=f["shape"][0],
            n_cols=f["shape"][1],
            dtype=f["dtype"],
            sha256=f["sha256"],
        )
        for f in payload["features"]["features"]
    )
    audit_payload = payload["split_audit"] or {}
    split_audit = None
    if audit_payload:
        from ada_core.contracts import ColdBuckets

        cb = audit_payload["cold_buckets"]
        split_audit = audit_split(
            bundle_train=[[]], bundle_valid=[[]], bundle_test=[[]],
            dataset_name=audit_payload["dataset_name"],
            split_paths={"train": payload["_split_paths"]["train"],
                         "valid": payload["_split_paths"]["valid"],
                         "test": payload["_split_paths"]["test"]},
            neg_params={},
            seed=payload["seed"],
        )
        # Preserve the audited numbers from the parent process verbatim.
        from dataclasses import replace
        from ada_core.contracts import SplitAudit

        cold = ColdBuckets(
            cold_item_max_train_freq=5, cold_user_max_len=3,
            cold_items=(), cold_users=(),
            warm_item_count=cb["n_warm_items"], warm_user_count=cb["n_warm_users"],
        )
        split_audit = SplitAudit(
            dataset_name=audit_payload["dataset_name"],
            n_users=audit_payload["n_users"], n_items=audit_payload["n_items"],
            n_train=audit_payload["n_train"], n_valid=audit_payload["n_valid"],
            n_test=audit_payload["n_test"],
            raw_split_hash=audit_payload["raw_split_hash"],
            semantic_split_hash=audit_payload["semantic_split_hash"],
            neg_hash=audit_payload["neg_hash"],
            cold_buckets=cold,
            status=audit_payload["status"],
            review_note=audit_payload.get("review_note", ""),
        )

    config = ExperimentConfig(
        run_id=payload["run_id"],
        phase=payload["phase"],
        dataset_name=payload["dataset_name"],
        seed=payload["seed"],
        appendix_params=params,
        feature_registry=FeatureRegistry(entries=features),
        split_audit=split_audit,
        max_steps=payload["max_steps"],
        eval_interval=payload["eval_interval"],
        log_interval=payload["log_interval"],
        artifact_root=payload.get("artifact_root", ""),
        baseline_run_id=payload.get("baseline_run_id"),
        baseline_split_hash=payload.get("baseline_split_hash"),
        is_synthetic_demo=payload.get("is_synthetic_demo", False),
        switches=payload.get("switches", {}),
    )
    return config


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ADA experiment entrypoint")
    parser.add_argument("--config-path", required=True)
    parser.add_argument("--train-dir", default="", help="MMSSL dataset directory")
    args = parser.parse_args(argv)

    with open(args.config_path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    config = rebuild_config(payload)

    from ada_core.contracts import sha256_bytes
    from ada_core.data import load_mmssl_bundle
    from ada_core.gates import config_is_launchable
    from ada_core.training import EventLog, Trainer

    events_path = os.path.join(config.artifact_root or ".", config.run_id, "events.jsonl")
    events = EventLog(events_path)

    launchable, gates = config_is_launchable(config)
    if not launchable:
        events.emit("config_blocked", {
            "reasons": [g.message for g in gates if g.is_blocking],
        })
        events.emit("run_terminal", {"status": "blocked",
                                     "reason": "C-gates blocked; no GPU process created."})
        return 2

    if config.is_synthetic_demo:
        events.emit("run_terminal", {"status": "blocked",
                                     "reason": "synthetic_demo artifacts are never launchable."})
        return 2

    feature_paths = {
        f["name"]: f.get("path") for f in payload["features"]["features"] if f.get("path")
    }
    bundle = load_mmssl_bundle(
        args.train_dir or payload.get("_train_dir", "."),
        dataset_name=config.dataset_name,
        feature_paths=feature_paths,
        seed=config.seed,
    )
    # The reloaded audit must agree with the serialized one (hash equality).
    if bundle.split_audit.raw_split_hash != (config.split_audit.raw_split_hash if config.split_audit else ""):
        events.emit("run_terminal", {"status": "failed",
                                     "reason": "split_hash drift between snapshot and reload."})
        return 1

    outcome = Trainer(config, bundle, events).run()
    return {"succeeded": 0, "failed": 1, "blocked": 2}[outcome.status]


if __name__ == "__main__":
    sys.exit(main())
