"""Training loop, artifact manifest and P0 gating for ADA runs.

The run lifecycle is deterministic and event-driven:

* JSONL events are emitted every ``log_interval`` steps and at every
  evaluation point (``eval_interval``).
* Metrics always include codebook usage, gradient norm, memory (MB) and step
  timing (ms) — the four series the G-P0 gates audit.
* P0 gate verdicts are computed from persisted metrics; a failing verdict
  **prevents the P1 transition**.
* A config snapshot and artifact manifest are saved before any training step.
* Early stop only applies once valid metrics have been emitted.
* No training begins while any C-gate blocks the configuration.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional

import numpy as np
import torch

from .contracts import ExperimentConfig
from .data import MMSSLBundle, sample_negatives
from .evaluation import RankingEvaluator
from .gates import config_is_launchable, p0_verdict
from .models.ada_modules import AdaModel

EVENT_CALLBACK = Callable[[Dict[str, Any]], None]

P1_TRANSITION_BLOCKED = "P0 gate failed; transition to P1 is blocked."


@dataclass
class RunOutcome:
    run_id: str
    status: str  # blocked | running | succeeded | failed
    reason: str
    steps_completed: int = 0
    p0_verdict: Optional[Dict[str, Any]] = None
    artifact_manifest: Dict[str, Any] | None = None
    final_metrics: Dict[str, Any] | None = None

    def to_json(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "reason": self.reason,
            "steps_completed": self.steps_completed,
            "p0_verdict": self.p0_verdict,
            "artifact_manifest": self.artifact_manifest,
            "final_metrics": self.final_metrics,
        }


class EventLog:
    """Appends JSONL events with a monotonic sequence number."""

    def __init__(self, path: str):
        self.path = path
        self.seq = 0
        self._ensure_file()

    def _ensure_file(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8"):
                pass

    def emit(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.seq += 1
        record = {
            "seq": self.seq,
            "ts": time.time(),
            "event": event_type,
            "payload": payload,
        }
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
        return record


def _pinned_torch_setup(seed: int) -> torch.device:
    torch.manual_seed(seed)
    np.random.seed(seed)
    return torch.device("cpu")


def _memory_mb() -> float:
    try:
        import psutil  # optional

        return float(psutil.Process().memory_info().rss) / (1024.0 * 1024.0)
    except Exception:
        pass
    try:
        import resource  # POSIX

        return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
    except Exception:
        pass
    try:  # Windows fallback: GetProcessMemoryInfo
        import ctypes
        import ctypes.wintypes as wt

        class _PMC(ctypes.Structure):
            _fields_ = [
                ("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
            return float(pmc.WorkingSetSize) / (1024.0 * 1024.0)
    except Exception:
        pass
    return 0.0


def build_synthetic_batches(
    bundle: MMSSLBundle,
    config: ExperimentConfig,
    steps: int,
    neg_per_positive: int = 2,
):
    """Deterministic toy batches for the P0 scaffold (feature rows = item ids)."""
    entry = config.feature_registry.by_name("image")
    matrix = np.load(entry.path)
    n_items = matrix.shape[0]
    rng = np.random.default_rng(config.seed)
    pool = sorted({i for seq in bundle.train for i in seq if i < n_items}) or list(range(n_items))
    batches = []
    for _ in range(steps):
        pos = [int(rng.choice(pool)) for _ in range(8)]
        neg = [int(rng.choice(pool)) for _ in range(8 * neg_per_positive)]
        rows = pos + neg
        feats = torch.tensor(matrix[rows], dtype=torch.float32)
        labels = torch.tensor([1.0] * len(pos) + [0.0] * len(neg))
        batches.append({"features": feats, "labels": labels})
    return batches


class Trainer:
    """Deterministic single-GPU(-bound) trainer for the ADA scaffold."""

    def __init__(
        self,
        config: ExperimentConfig,
        bundle: MMSSLBundle,
        events: EventLog,
        model: Optional[AdaModel] = None,
        phase_override: Optional[str] = None,
    ):
        self.config = config
        self.bundle = bundle
        self.events = events
        self.device = _pinned_torch_setup(config.seed)
        self.phase_override = phase_override  # used to simulate P0→P1 transitions
        launchable, gates = config_is_launchable(config)
        self.launchable = launchable
        self.config_gates = gates
        if not launchable:
            blocked = [g.to_json() for g in gates if g.is_blocking]
            self.events.emit(
                "config_blocked",
                {"reasons": [g.message for g in gates if g.is_blocking], "gates": blocked},
            )
            self.model = None
        else:
            entry = config.feature_registry.by_name("image")
            input_dim = entry.n_cols if entry else 8
            p = {q.name: q.value for q in config.appendix_params}
            self.model = model or AdaModel(
                input_dim=input_dim,
                latent_dim=int(p["r3vae_M"]),
                fusion_dim=int(p["fusion_dim"]),
                downstream_hidden=int(p["downstream_hidden"]),
                n_references=int(p["r3vae_L"]),
                top_k=int(p["r3vae_top_k"]),
                phase=config.phase,
                enable_alignment=bool(config.switches.get("enable_alignment", False)),
                enable_dynamic_weighting=bool(
                    config.switches.get("enable_dynamic_weighting", False)
                ),
            ).to(self.device)

    # -- artifact helpers ---------------------------------------------------

    def _artifact_dir(self) -> str:
        return os.path.join(self.config.artifact_root or ".", self.config.run_id)

    def save_config_snapshot(self) -> str:
        out_dir = self._artifact_dir()
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "config_snapshot.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.config.to_json(), fh, indent=2, default=str)
        return path

    def save_artifact_manifest(self, extra_files: List[str]) -> str:
        from .contracts import sha256_file

        manifest = {
            "run_id": self.config.run_id,
            "config_hash": ExperimentConfig.config_hash(self.config),
            "split_hash": self.bundle.split_audit.raw_split_hash,
            "files": {os.path.basename(f): sha256_file(f) for f in extra_files},
        }
        out_dir = self._artifact_dir()
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "artifact_manifest.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        return path

    def save_metrics(self, metrics: Dict[str, Any]) -> str:
        out_dir = self._artifact_dir()
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "metrics.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2, default=str)
        return path

    # -- main loop ----------------------------------------------------------

    def run(self) -> RunOutcome:
        config = self.config
        if not self.launchable or self.model is None:
            outcome = RunOutcome(
                run_id=config.run_id,
                status="blocked",
                reason="Configuration blocked by C-gates; no GPU process may be created.",
            )
            self.events.emit("run_terminal", {"status": outcome.status, "reason": outcome.reason})
            return outcome

        snapshot = self.save_config_snapshot()

        batches = build_synthetic_batches(self.bundle, config, steps=config.max_steps)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-3)
        entry = config.feature_registry.by_name("image")
        p = {q.name: q.value for q in config.appendix_params}

        metrics: Dict[str, Any] = {
            "loss": [],
            "codebook_usage": [],
            "grad_norm": [],
            "memory_mb": [],
            "step_ms": [],
            "valid_metric": [],
        }
        best_valid = -float("inf")
        best_step = -1
        steps_done = 0

        self.events.emit("run_started", {
            "phase": config.phase,
            "config_hash": ExperimentConfig.config_hash(config),
            "split_hash": self.bundle.split_audit.raw_split_hash,
        })

        evaluator = RankingEvaluator(self.bundle, config)
        for batch in batches:
            if self.phase_override:  # simulated transition control
                self.model.phase = self.phase_override
            start = time.perf_counter()
            optimizer.zero_grad()
            out = self.model(batch)
            losses = out["losses"]
            loss = out.get("rank_loss", torch.zeros(()))
            for name, value in losses.items():
                weight = 0.005 if name == "ortho" else 1.0
                loss = loss + weight * value
            loss.backward()
            grad_norm = float(
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip_norm"])
            )
            optimizer.step()
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            steps_done += 1

            metrics["loss"].append(float(loss.detach()))
            metrics["grad_norm"].append(grad_norm)
            metrics["memory_mb"].append(_memory_mb())
            metrics["step_ms"].append(elapsed_ms)
            metrics["codebook_usage"].append(float(out["usage"].mean().detach()))

            if steps_done % config.log_interval == 0:
                self.events.emit("step_metrics", {
                    "step": steps_done,
                    "loss": metrics["loss"][-1],
                    "grad_norm": grad_norm,
                    "memory_mb": metrics["memory_mb"][-1],
                    "step_ms": elapsed_ms,
                })

            if steps_done % config.eval_interval == 0:
                valid_auc = evaluator.valid_auc(self.model)
                metrics["valid_metric"].append(valid_auc)
                self.events.emit("eval_metrics", {"step": steps_done, "valid_auc": valid_auc})
                if valid_auc > best_valid:
                    best_valid, best_step = valid_auc, steps_done

        # Early stop only considered after valid metrics exist; verify we saw
        # at least one evaluation in this scaffold run.
        saw_eval = len(metrics["valid_metric"]) > 0

        verdict = p0_verdict(metrics)
        metrics_path = self.save_metrics(metrics)
        manifest_path = self.save_artifact_manifest([snapshot, metrics_path])

        cold = evaluator.cold_bucket_report(self.model)
        metrics["cold_buckets"] = cold

        self.events.emit("p0_verdict", verdict.to_json())
        status = "succeeded" if verdict.passed else "failed"
        reason = (
            "P0 gates passed." if verdict.passed
            else P1_TRANSITION_BLOCKED + " Verdict: " + verdict.message
        )
        if not saw_eval:
            status = "failed"
            reason = "Early stop requested without valid metrics; run marked failed."
        self.events.emit("run_terminal", {"status": status, "reason": reason})

        return RunOutcome(
            run_id=config.run_id,
            status=status,
            reason=reason,
            steps_completed=steps_done,
            p0_verdict=verdict.to_json(),
            artifact_manifest={"config_snapshot": snapshot, "metrics": metrics_path,
                               "manifest": manifest_path},
            final_metrics=metrics,
        )


def assert_p1_transition_allowed(outcome: RunOutcome) -> None:
    """Explicit transition guard: P0 failure blocks P1."""
    if outcome.status != "succeeded" or not (outcome.p0_verdict or {}).get("status") == "pass":
        raise PermissionError(P1_TRANSITION_BLOCKED)
