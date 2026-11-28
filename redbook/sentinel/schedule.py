"""Windows Task Scheduler registration for the redbook sentinel.

Low-ops contract (task 3 devplan): no resident service. The sentinel runs as
a daily scheduled task invoking the idempotent ``python -m redbook.sentinel
run-once`` entry point in the repository working directory.

Pure helpers (``build_task_name`` / ``build_task_command`` / ``build_register_args``)
are testable without touching the OS; ``install_task`` / ``remove_task`` shell
out to ``schtasks.exe``.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import yaml

DEFAULT_TASK_NAME = "RedbookSentinelDaily"
DEFAULT_PYTHON = Path(sys.executable)
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEDULE_CONFIG = ROOT / "config" / "paper_ingest_schedule.yaml"


def configured_time(config_path: Path = DEFAULT_SCHEDULE_CONFIG) -> str:
    """Read the single schedule authority used by all daily paper tasks."""
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    value = str(payload.get("time") or "").strip()
    if not value:
        raise ValueError(f"schedule time is required in {config_path}")
    return value


def build_task_name(repo_hint: str = "") -> str:
    """Stable task name; repo_hint disambiguates worktrees if provided."""
    return f"{DEFAULT_TASK_NAME}({repo_hint})" if repo_hint else DEFAULT_TASK_NAME


def build_task_command(python: Path, repo_dir: Path) -> str:
    """cmd wrapper because schtasks /TR has no working-directory option."""
    python_path = str(python).replace("/", "\\")
    repo_path = str(repo_dir).replace("/", "\\")
    return f'cmd.exe /c "cd /d {repo_path} && {python_path} -m redbook.sentinel run-once"'


def build_register_args(task_name: str, python: Path, repo_dir: Path,
                        *, time: str | None = None) -> List[str]:
    return [
        "/Create", "/F",
        "/TN", task_name,
        "/SC", "DAILY",
        "/ST", time or configured_time(),
        "/TR", build_task_command(python, repo_dir),
    ]


def _run(args: List[str]) -> Dict[str, object]:
    # schtasks emits the OEM/ANSI codepage on zh-CN Windows (GBK); utf-8 would
    # raise UnicodeDecodeError inside the reader thread.
    completed = subprocess.run(
        ["schtasks", *args], capture_output=True, check=False,
        encoding="mbcs", errors="replace")
    return {"ok": completed.returncode == 0,
            "stdout": (completed.stdout or "").strip(),
            "stderr": (completed.stderr or "").strip()}


def install_task(task_name: str, python: Path, repo_dir: Path,
                 *, time: str | None = None) -> Dict[str, object]:
    return _run(build_register_args(task_name, python, repo_dir, time=time))


def remove_task(task_name: str) -> Dict[str, object]:
    return _run(["/Delete", "/F", "/TN", task_name])


def query_task(task_name: str) -> Dict[str, object]:
    result = _run(["/Query", "/TN", task_name])
    result["exists"] = bool(result["ok"])
    return result


def main(argv: List[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="register/uninstall the sentinel scheduled task")
    parser.add_argument("action", choices=["install", "remove", "query"])
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--repo-dir", type=Path, default=Path.cwd())
    parser.add_argument("--name", default=DEFAULT_TASK_NAME)
    parser.add_argument("--time", default=None)
    args = parser.parse_args(argv)

    if args.action == "install":
        result = install_task(args.name, args.python, args.repo_dir, time=args.time)
    elif args.action == "remove":
        result = remove_task(args.name)
    else:
        result = query_task(args.name)
    print(result["stdout"] or result["stderr"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
