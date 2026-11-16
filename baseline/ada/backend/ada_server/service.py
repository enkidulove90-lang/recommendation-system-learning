"""Gate-aware service layer.

Enforces the review-focus invariants:

1. A blocked configuration produces a human-readable ``blocked`` state and
   never reaches the runner — no GPU process is created.
2. A P2 run whose ``split_hash`` differs from its baseline is *rejected*
   (HTTP 422 / ValueError), not warned.
3. Only one ``running`` GPU job exists at any time; a second start attempt is
   refused.
4. Cancellation terminates only the owning run's process and leaves a
   consistent terminal event + status.
5. Terminal events are idempotent, so SSE resume never duplicates them.
"""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

from .repository import Repository
from .runner import Runner
from .schemas import ConfigIn

import sys

BASELINE_ADA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (os.path.join(BASELINE_ADA, "core"), BASELINE_ADA):
    if p not in sys.path:
        sys.path.insert(0, p)

from ada_core.contracts import AppendixParam, ExperimentConfig  # noqa: E402
from ada_core.data import load_mmssl_bundle, make_config  # noqa: E402
from ada_core.gates import evaluate_config_gates  # noqa: E402


class ServiceError(ValueError):
    """Protocol violation that must reject the request."""


class Service:
    def __init__(
        self,
        repo: Repository,
        runner: Runner,
        artifact_root: str,
        python_executable: Optional[str] = None,
    ):
        self.repo = repo
        self.runner = runner
        self.artifact_root = artifact_root
        self._handles: Dict[str, Dict[str, Any]] = {}
        self._watchers: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    # -- validation ---------------------------------------------------------

    def build_config(self, body: ConfigIn) -> ExperimentConfig:
        resolved = {}
        for p in body.appendix_params:
            if p.resolved and p.value is not None and p.rationale.strip():
                resolved[p.name] = (p.value, p.rationale, p.source or "api")
        bundle = load_mmssl_bundle(
            body.train_dir,
            dataset_name=body.dataset_name,
            feature_paths=body.feature_paths,
            neg_params={"pool": 100},
            seed=body.seed,
            negative_review=body.negative_review,
            review_note=body.review_note,
        )
        return make_config(
            run_id=body.run_id,
            phase=body.phase,
            bundle=bundle,
            seed=body.seed,
            appendix_overrides=resolved,
            max_steps=body.max_steps,
            eval_interval=body.eval_interval,
            log_interval=body.log_interval,
            artifact_root=self.artifact_root,
            baseline_run_id=body.baseline_run_id,
            baseline_split_hash=body.baseline_split_hash,
            is_synthetic_demo=body.is_synthetic_demo,
            switches=body.switches,
        )

    def validate(self, body: ConfigIn) -> Dict[str, Any]:
        try:
            config = self.build_config(body)
        except FileNotFoundError as exc:
            return {
                "run_id": body.run_id,
                "blocked": True,
                "reasons": [f"dataset/feature file missing: {exc}"],
                "human_readable": f"Blocked: dataset/feature file missing: {exc}",
                "config_hash": None,
                "split_hash": None,
            }
        decision = config.protocol_decision()
        gates = evaluate_config_gates(config)
        extra = [
            gate.message for gate in gates
            if gate.is_blocking and gate.message not in decision.reasons
        ]
        all_reasons = tuple(decision.reasons) + tuple(extra)
        from ada_core.contracts import ProtocolDecision

        decision = ProtocolDecision(blocked=decision.blocked, reasons=all_reasons)
        return {
            "run_id": config.run_id,
            "blocked": decision.blocked,
            "reasons": list(decision.reasons),
            "human_readable": decision.human_readable(),
            "config_hash": ExperimentConfig.config_hash(config),
            "split_hash": config.split_audit.raw_split_hash if config.split_audit else None,
        }

    # -- run lifecycle ------------------------------------------------------

    def create_run(self, body: ConfigIn) -> Dict[str, Any]:
        validation = self.validate(body)
        now = time.time()
        try:
            config = self.build_config(body)
            split_hash = config.split_audit.raw_split_hash if config.split_audit else None
        except FileNotFoundError:
            config = None
            split_hash = None

        # Review-focus #2: P2 split-hash mismatch is a hard rejection.
        if config is not None and config.phase == "P2" and config.baseline_split_hash:
            if split_hash and config.baseline_split_hash != split_hash:
                self.repo.upsert_run(
                    run_id=body.run_id, phase=body.phase, status="blocked", blocked=True,
                    blocking_reasons=[f"baseline split_hash mismatch: {config.baseline_split_hash} != {split_hash}"],
                    split_hash=split_hash, baseline_run_id=body.baseline_run_id,
                    is_synthetic_demo=body.is_synthetic_demo, created_at=now, updated_at=now,
                )
                raise ServiceError(
                    f"Run rejected: baseline split_hash {config.baseline_split_hash[:12]}… "
                    f"differs from this dataset's split_hash {split_hash[:12]}…; "
                    "mismatched baselines are rejected, not warned."
                )

        self.repo.upsert_run(
            run_id=body.run_id, phase=body.phase,
            status="blocked" if validation["blocked"] else "queued",
            blocked=validation["blocked"],
            blocking_reasons=validation["reasons"],
            config_hash=validation["config_hash"], split_hash=split_hash,
            baseline_run_id=body.baseline_run_id,
            is_synthetic_demo=body.is_synthetic_demo,
            created_at=now, updated_at=now,
        )
        if config is not None:
            self.repo.save_config_snapshot(body.run_id, config.to_json())
            self.repo.add_artifact(
                body.run_id, "config_snapshot.json",
                os.path.join(self.artifact_root, body.run_id, "config_snapshot.json"),
                kind="config",
            )
        self.repo.append_event(
            body.run_id, "run_created",
            {"blocked": validation["blocked"], "reasons": validation["reasons"]},
            is_terminal=validation["blocked"],
        )
        run = self.repo.get_run(body.run_id)
        return {"run": run, "validation": validation}

    def start_run(self, run_id: str) -> Dict[str, Any]:
        run = self._require_run(run_id)
        if run["status"] == "running":
            raise ServiceError(f"Run '{run_id}' is already running.")
        if run["blocked"] or run["status"] == "blocked":
            raise ServiceError(
                "Run cannot start: configuration is blocked ("
                + "; ".join(run["blocking_reasons"][:3]) + ")."
            )
        if run["is_synthetic_demo"]:
            raise ServiceError("synthetic_demo artifacts are never launchable.")
        if run["status"] in ("succeeded", "failed", "cancelled"):
            raise ServiceError(f"Run '{run_id}' is already terminal ({run['status']}).")

        with self._lock:
            current = self.repo.running_run()
            if current is not None and current["run_id"] != run_id:
                raise ServiceError(
                    f"A GPU job is already running ('{current['run_id']}'); "
                    "only one running job is permitted."
                )

        snapshot = self.repo.get_config_snapshot(run_id)
        if snapshot is None:
            raise ServiceError(f"No config snapshot persisted for '{run_id}'.")

        config_path = os.path.join(self.artifact_root, run_id, "launch_config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        payload = dict(snapshot)
        payload["artifact_root"] = self.artifact_root
        train_dir = payload.get("_train_dir", "")
        with open(config_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, default=str)

        handle = self.runner.spawn(
            config_path=config_path,
            train_dir=train_dir,
            log_path=os.path.join(self.artifact_root, run_id, "stdout.log"),
        )
        self._handles[run_id] = handle
        self.repo.upsert_run(
            run_id=run_id, status="running", pid=handle["pid"], updated_at=time.time()
        )
        self.repo.append_event(run_id, "run_started", {"pid": handle["pid"]})

        watcher = threading.Thread(
            target=self._watch_process, args=(run_id, handle), daemon=True
        )
        self._watchers[run_id] = watcher
        watcher.start()
        return self.repo.get_run(run_id)

    def cancel_run(self, run_id: str) -> Dict[str, Any]:
        run = self._require_run(run_id)
        if run["status"] != "running":
            raise ServiceError(f"Run '{run_id}' is not running (status={run['status']}).")
        handle = self._handles.get(run_id)
        return_code: Optional[int] = run.get("return_code")
        if handle is not None:
            return_code = self.runner.cancel(handle["proc"])
            self.runner.cleanup(handle)
        else:
            return_code = -1
        with self._lock:
            self._handles.pop(run_id, None)
        self.repo.upsert_run(
            run_id=run_id, status="cancelled", return_code=return_code, pid=None,
            updated_at=time.time()
        )
        # Idempotent terminal event (repository dedups per kind).
        seq = self.repo.append_event(
            run_id, "run_terminal",
            {"status": "cancelled", "reason": "cancelled by operator",
             "return_code": return_code},
            is_terminal=True,
        )
        return {**self.repo.get_run(run_id), "terminal_seq": seq}

    # -- watcher ------------------------------------------------------------

    def _watch_process(self, run_id: str, handle: Dict[str, Any]) -> None:
        proc = handle["proc"]
        events_path = os.path.join(self.artifact_root, run_id, "events.jsonl")
        ingested = 0
        while True:
            # Ingest any new JSONL events the child emitted.
            if os.path.exists(events_path):
                try:
                    with open(events_path, "r", encoding="utf-8") as fh:
                        lines = fh.readlines()
                    while ingested < len(lines):
                        record = json.loads(lines[ingested])
                        ingested += 1
                        self.repo.append_event(
                            run_id, record.get("event", "unknown"),
                            record.get("payload", {}),
                            is_terminal=record.get("event") in ("run_terminal", "config_blocked"),
                        )
                except Exception:
                    pass
            code = self.runner.poll(proc)
            if code is not None:
                break
            time.sleep(0.1)
        self.runner.cleanup(handle)
        with self._lock:
            self._handles.pop(run_id, None)

        status_map = {0: "succeeded", 1: "failed", 2: "blocked"}
        terminal_status = status_map.get(code, "failed")
        current = self.repo.get_run(run_id)
        if current and current["status"] == "cancelled":
            # Operator already finalized this run; keep state consistent.
            self.repo.upsert_run(run_id=run_id, return_code=code, updated_at=time.time())
            return
        self.repo.upsert_run(
            run_id=run_id, status=terminal_status, return_code=code, pid=None,
            updated_at=time.time(),
        )
        self.repo.append_event(
            run_id, "run_terminal",
            {"status": terminal_status, "return_code": code},
            is_terminal=True,
        )

    # -- queries ------------------------------------------------------------

    def _require_run(self, run_id: str) -> Dict[str, Any]:
        run = self.repo.get_run(run_id)
        if run is None:
            raise KeyError(f"unknown run '{run_id}'")
        return run

    def list_runs(self) -> List[Dict[str, Any]]:
        return self.repo.list_runs()

    def run_detail(self, run_id: str) -> Dict[str, Any]:
        return self._require_run(run_id)

    def run_events(self, run_id: str, last_seq: int = 0) -> List[Dict[str, Any]]:
        self._require_run(run_id)
        return self.repo.events_since(run_id, last_seq)

    def run_artifacts(self, run_id: str) -> List[Dict[str, Any]]:
        self._require_run(run_id)
        return self.repo.list_artifacts(run_id)
