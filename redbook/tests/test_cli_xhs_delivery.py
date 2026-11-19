from __future__ import annotations

import subprocess
import sys


def test_note_help_exposes_draft_only_save_alias() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "redbook.cli", "note", "--help"],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert "--save-draft" in result.stdout
    assert "--publish" in result.stdout
    assert "deprecated alias of --save-draft" in result.stdout
    assert "never publishes publicly" in result.stdout


def test_note_help_exposes_read_only_verify() -> None:
    result = subprocess.run([sys.executable, "-m", "redbook.cli", "note", "--help"], text=True, capture_output=True)
    assert result.returncode == 0
    assert "--verify" in result.stdout
    assert "--draft-id" in result.stdout
