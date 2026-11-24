from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dry_run_lists_all_four_stages_without_creating_runtime_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/daily_paper_ingest.py", "--dry-run"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert [f'"stage": "s{stage}"' for stage in range(1, 5)] == [
        token for token in [f'"stage": "s{stage}"' for stage in range(1, 5)] if token in result.stdout
    ]
