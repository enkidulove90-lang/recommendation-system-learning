"""Backend API tests (Task 4).

These exercise the review-focus invariants end-to-end with real (tiny) runs:
blocked configs never spawn a process, single-GPU exclusivity, monotonic
events with SSE resume, and cancel isolating one run's process.
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

BASELINE_ADA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (os.path.join(BASELINE_ADA, "backend"), BASELINE_ADA):
    if p not in sys.path:
        sys.path.insert(0, p)

from ada_server.api import create_app  # noqa: E402

PYTHON = sys.executable

RESOLVED_PARAMS = [
    {"name": name, "value": 1.0 if name != "r3vae_top_k" else 2.0,
     "resolved": True, "rationale": "pilot rationale", "source": "local_pilot"}
    for name in [
        "r3vae_L", "r3vae_M", "r3vae_top_k", "mmq_expert_hidden", "fusion_dim",
        "downstream_hidden", "neg_pool_size", "neg_per_positive", "eval_topk",
        "grad_clip_norm", "weight_decay", "warmup_steps",
    ]
]


@pytest.fixture()
def tiny_dataset(tmp_path):
    d = tmp_path / "mmssl-tiny"
    d.mkdir()
    rng = np.random.default_rng(0)
    for name, seq_len in (("train", 5), ("valid", 2), ("test", 2)):
        lines = []
        for u in range(6):
            items = [(u * 3 + k) % 12 for k in range(seq_len)]
            lines.append(" ".join(str(x) for x in [u] + items))
        (d / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    feat = d / "image_feat.npy"
    np.save(feat, rng.normal(size=(12, 8)).astype(np.float32))
    return str(d), str(feat)


@pytest.fixture()
def client(tmp_path, tiny_dataset):
    train_dir, feat = tiny_dataset
    db = str(tmp_path / "runs.db")
    artifacts = str(tmp_path / "artifacts")
    os.makedirs(artifacts, exist_ok=True)
    app = create_app(db_path=db, artifact_root=artifacts, python_executable=PYTHON)
    with TestClient(app) as c:
        c.ada_ctx = {"train_dir": train_dir, "feat": feat, "artifacts": artifacts}
        yield c


def _resolved_body(run_id, train_dir, feat, phase="P0", **kw):
    return {
        "run_id": run_id,
        "phase": phase,
        "dataset_name": "mmssl_tiny",
        "seed": 42,
        "train_dir": train_dir,
        "feature_paths": {"image": feat},
        "appendix_params": RESOLVED_PARAMS,
        "max_steps": kw.pop("max_steps", 10),
        "eval_interval": 5,
        "log_interval": 2,
        **kw,
    }


def _blocked_body(run_id, train_dir, feat, phase="P0", **kw):
    body = _resolved_body(run_id, train_dir, feat, phase=phase, **kw)
    body["appendix_params"] = []  # nothing resolved → blocked
    return body


def test_blocked_config_cannot_start_run(client):
    train_dir, feat = client.ada_ctx["train_dir"], client.ada_ctx["feat"]
    body = _blocked_body("blocked-run", train_dir, feat)

    validation = client.post("/api/configs/validate", json=body).json()
    assert validation["blocked"] is True
    assert validation["reasons"], "human-readable reasons required"
    assert "unresolved" in validation["human_readable"]

    created = client.post("/api/runs", json=body).json()
    assert created["run"]["status"] == "blocked"
    assert created["run"]["blocked"] is True

    resp = client.post("/api/runs/blocked-run/start")
    assert resp.status_code == 409
    assert "blocked" in resp.json()["detail"]

    # No GPU process was created: no pid recorded anywhere.
    detail = client.get("/api/runs/blocked-run").json()
    assert detail["pid"] is None


def test_runner_refuses_second_gpu_job(client):
    train_dir, feat = client.ada_ctx["train_dir"], client.ada_ctx["feat"]
    # Large workload keeps the first run "running" deterministically long
    # enough for the mutual-exclusion assertion (de-flakes under load).
    client.post("/api/runs", json=_resolved_body("first-run", train_dir, feat, max_steps=100000, eval_interval=5))
    client.post("/api/runs", json=_resolved_body("second-run", train_dir, feat, max_steps=30, eval_interval=5))

    r1 = client.post("/api/runs/first-run/start")
    assert r1.status_code == 200
    assert r1.json()["status"] == "running"

    r2 = client.post("/api/runs/second-run/start")
    assert r2.status_code == 409
    assert "already running" in r2.json()["detail"]

    # Cancel the long-running first job to leave a clean terminal state.
    cancelled = client.post("/api/runs/first-run/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_events_stream_in_monotonic_sequence(client):
    train_dir, feat = client.ada_ctx["train_dir"], client.ada_ctx["feat"]
    client.post("/api/runs", json=_resolved_body("sse-run", train_dir, feat, max_steps=10, eval_interval=5))
    client.post("/api/runs/sse-run/start")
    for _ in range(300):
        if client.get("/api/runs/sse-run").json()["status"] != "running":
            break
        time.sleep(0.2)

    events = client.get("/api/runs/sse-run/events").json() if False else None
    # REST-style helper via repository is not exposed; verify via SSE stream.
    with client.stream("GET", "/api/runs/sse-run/events") as response:
        lines = list(response.iter_lines())
    seqs = []
    for i, line in enumerate(lines):
        if line.startswith("id: "):
            seqs.append(int(line[4:].strip()))
    assert seqs == sorted(seqs), "SSE ids must be monotonic"
    assert seqs[0] == 1

    # SSE resume from the last event id replays nothing new after terminal.
    last_id = seqs[-1]
    with client.stream(
        "GET", "/api/runs/sse-run/events", headers={"Last-Event-ID": str(last_id)}
    ) as response:
        resumed = list(response.iter_lines())
    resumed_ids = [int(l[4:]) for l in resumed if l.startswith("id: ")]
    assert all(i > last_id for i in resumed_ids)

    # Terminal transition appears exactly once in the stream.
    terminal_lines = [l for l in lines if l.startswith("event: run_terminal")]
    assert len(terminal_lines) == 1


def test_cancel_terminates_only_own_process(client):
    train_dir, feat = client.ada_ctx["train_dir"], client.ada_ctx["feat"]
    client.post("/api/runs", json=_resolved_body("cancel-run", train_dir, feat, max_steps=100000, eval_interval=500))
    started = client.post("/api/runs/cancel-run/start")
    assert started.status_code == 200
    pid = started.json()["pid"]
    assert pid

    # Another process that must survive the cancel.
    survivor = subprocess_alive_marker()

    cancelled = client.post("/api/runs/cancel-run/cancel")
    assert cancelled.status_code == 200
    data = cancelled.json()
    assert data["status"] == "cancelled"
    assert data["return_code"] is not None

    # The cancelled run's process is gone.
    time.sleep(0.5)
    assert not process_exists(pid), "cancelled run's process must terminate"
    assert process_exists(survivor), "unrelated process must survive"

    # Consistent terminal state: exactly one terminal event, status cancelled.
    with client.stream("GET", "/api/runs/cancel-run/events") as response:
        lines = list(response.iter_lines())
    terminal = [l for l in lines if l.startswith("event: run_terminal")]
    assert len(terminal) == 1
    detail = client.get("/api/runs/cancel-run").json()
    assert detail["status"] == "cancelled" and detail["pid"] is None


def test_p2_split_hash_mismatch_is_rejected(client):
    train_dir, feat = client.ada_ctx["train_dir"], client.ada_ctx["feat"]
    body = _resolved_body(
        "p2-bad", train_dir, feat, phase="P2",
        baseline_run_id="baseline-x", baseline_split_hash="deadbeef" * 8,
    )
    resp = client.post("/api/runs", json=body)
    assert resp.status_code == 422
    assert "rejected" in resp.json()["detail"]


def test_synthetic_demo_never_launchable(client):
    train_dir, feat = client.ada_ctx["train_dir"], client.ada_ctx["feat"]
    body = _resolved_body("demo-run", train_dir, feat, is_synthetic_demo=True)
    created = client.post("/api/runs", json=body).json()
    assert created["run"]["status"] == "blocked"
    assert created["validation"]["blocked"] is True
    assert "synthetic_demo" in created["validation"]["human_readable"]
    assert client.post("/api/runs/demo-run/start").status_code == 409


# -- helpers -----------------------------------------------------------------


def process_exists(pid: int) -> bool:
    if os.name == "nt":
        code = os.system(f'tasklist /FI "PID eq {pid}" /NH 2>nul | findstr /C:"{pid}" >nul 2>&1')
        return code == 0
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def subprocess_alive_marker() -> int:
    import subprocess

    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        creationflags=flags,
    )
    return proc.pid
