from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil


def test_sentinel_task_runner_dry_run_uses_module_entrypoint():
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_sentinel_task.ps1"
    result = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
            "-Platform", "homepage", "-NoDispatch", "-PythonPath", sys.executable, "-WhatIf",
        ],
        text=True, capture_output=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "WorkingDirectory": str(script.parents[2]),
        "PythonPath": sys.executable,
        "Arguments": [
            "-m", "redbook.sentinel", "run-once", "--platform", "homepage", "--no-dispatch",
        ],
    }


def test_sentinel_registration_preview_is_discovery_only():
    script = Path(__file__).resolve().parents[2] / "scripts" / "register_sentinel_task.ps1"
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
         "-TaskName", "Paper Sentinel Test", "-Platform", "homepage", "-NoDispatch",
         "-PythonPath", sys.executable, "-WhatIf"],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    preview = json.loads(result.stdout)
    assert preview["TaskName"] == "Paper Sentinel Test"
    assert preview["Schedule"] == "11:00"
    assert preview["NoDispatch"] is True
    assert preview["WorkingDirectory"] == str(script.parents[1])
    assert "run_sentinel_task.ps1" in preview["ActionArguments"]


def test_stable_install_preview_uses_external_code_state_and_exclusions():
    script = Path(__file__).resolve().parents[2] / "scripts" / "register_sentinel_task.ps1"
    runner_source = script.parent / "run_sentinel_task.ps1"
    with tempfile.TemporaryDirectory(prefix="sentinel-release-") as temporary:
        root = Path(temporary)
        app = root / "release"
        state = root / "state"
        (app / "scripts").mkdir(parents=True)
        state.mkdir()
        shutil.copy2(runner_source, app / "scripts" / runner_source.name)
        config = app / "sentinel.yaml"
        config.write_text("platform: homepage\n", encoding="utf-8")
        exclusions = state / "exclusions.json"
        exclusions.write_text('{"excluded_ids": []}', encoding="utf-8")
        result = subprocess.run([
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
            "-InstallRoot", str(app), "-DataRoot", str(state), "-ConfigPath", str(config),
            "-ExclusionsPath", str(exclusions), "-PythonPath", sys.executable,
            "-NoDispatch", "-WhatIf"], text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr
        preview = json.loads(result.stdout)
        assert preview["WorkingDirectory"] == str(app)
        assert str(app / "scripts" / "run_sentinel_task.ps1") in preview["ActionArguments"]
        assert "-DataRoot" in preview["ActionArguments"]
        assert "-ExclusionsPath" in preview["ActionArguments"]
