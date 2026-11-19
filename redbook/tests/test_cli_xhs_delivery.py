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
    assert "draft" in result.stdout.lower()
