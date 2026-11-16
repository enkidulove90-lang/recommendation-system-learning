"""End-to-end smoke: demo artifacts are labelled synthetic and never launchable."""

import json
import os
import sys

import pytest

BASELINE_ADA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (BASELINE_ADA, os.path.join(BASELINE_ADA, "backend"), os.path.join(BASELINE_ADA, "core")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ada_server.service import Service, ServiceError  # noqa: E402
from ada_server.repository import Repository  # noqa: E402
from ada_server.runner import Runner  # noqa: E402
from ada_server.schemas import ConfigIn  # noqa: E402
from scripts.seed_demo_artifacts import seed, SYNTHETIC_TAG  # noqa: E402


def test_demo_artifacts_are_labeled_synthetic_and_never_launchable(tmp_path):
    # Seed demo artifacts (never-training UI demo data).
    out_dir = seed(str(tmp_path))
    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, encoding="utf-8") as fh:
        metrics = json.load(fh)
    assert metrics.get("synthetic_demo") is True
    assert metrics.get("tag") == SYNTHETIC_TAG

    # Register the demo run in the service and try to start it.
    # Split files must exist so C1 does not block the config; only then is the
    # synthetic_demo launch refusal (not the blocked refusal) exercised.
    for name in ("train.txt", "valid.txt", "test.txt"):
        with open(os.path.join(str(tmp_path), name), "w", encoding="utf-8") as fh:
            fh.write("0 1 2 3\n")
    db_path = os.path.join(tmp_path, "demo.db")
    repo = Repository(db_path)
    service = Service(repo, Runner(str(BASELINE_ADA)), artifact_root=str(tmp_path))
    body = ConfigIn(
        run_id="demo-synthetic-001",
        phase="P0",
        dataset_name="synthetic-demo",
        train_dir=str(tmp_path),
        is_synthetic_demo=True,
    )
    created = service.create_run(body)
    assert created["run"]["is_synthetic_demo"] in (True, 1)

    with pytest.raises(ServiceError, match="synthetic_demo"):
        service.start_run("demo-synthetic-001")
