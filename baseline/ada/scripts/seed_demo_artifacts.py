"""Seed explicit SYNTHETIC demo artifacts for UI verification only.

The artifacts produced here are labelled ``synthetic_demo`` end to end and
MUST NOT be used as, or confused with, real experimental results. The API
additionally refuses to ``start`` any run whose config carries the
``synthetic_demo`` marker (enforced in service layer via blocked protocol
decision injected at seed time).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

SYNTHETIC_TAG = "synthetic_demo"


def _series(n: int, start: float, drift: float, noise: float, gaps_at=()) -> list:
    """Deterministic series with explicit null gaps (never treated as zero)."""
    values: list = []
    v = start
    for i in range(n):
        v = max(0.0, v + drift + ((i % 3) - 1) * noise)
        values.append(None if i in gaps_at else round(v, 6))
    return values


def seed(artifact_root: str, run_id: str = "demo-synthetic-001") -> str:
    out_dir = os.path.join(artifact_root, run_id)
    os.makedirs(out_dir, exist_ok=True)

    config_snapshot = {
        "run_id": run_id,
        "tag": SYNTHETIC_TAG,
        "note": "UI demo only — NOT an experimental result",
        "phase": "p0",
        "split_hash": "0" * 64,
        "synthetic_demo": True,
    }
    metrics = {
        "run_id": run_id,
        "tag": SYNTHETIC_TAG,
        "synthetic_demo": True,
        "series": {
            "loss": _series(20, 2.4, -0.09, 0.01, gaps_at=(7, 13)),
            "codebook_usage": _series(20, 0.3, 0.005, 0.004),
            "grad_norm": _series(20, 1.1, -0.01, 0.02, gaps_at=(9,)),
            "memory_mb": _series(20, 2100.0, 2.0, 30.0),
            "step_ms": _series(20, 42.0, -0.2, 1.5),
            "valid_metric": _series(4, 0.55, 0.03, 0.0),
        },
        "p0_gates": [
            {"gate": "G-P0-1", "status": "passed", "evidence": "synthetic"},
            {"gate": "G-P0-2", "status": "passed", "evidence": "synthetic"},
        ],
    }
    manifest = {
        "run_id": run_id,
        "tag": SYNTHETIC_TAG,
        "files": ["config_snapshot.json", "metrics.json", "artifact_manifest.json"],
        "synthetic_demo": True,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    written = []
    for name, payload in (
        ("config_snapshot.json", config_snapshot),
        ("metrics.json", metrics),
        ("artifact_manifest.json", manifest),
    ):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        written.append(path)
    print(f"Seeded {len(written)} synthetic demo artifacts under {out_dir}")
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", default=os.path.join(os.path.dirname(__file__), "..", "artifacts"))
    parser.add_argument("--run-id", default="demo-synthetic-001")
    args = parser.parse_args()
    seed(args.artifact_root, args.run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
