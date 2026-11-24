"""Run the authoritative paper catalog-to-intake workflow once.

The operating system owns scheduling.  This script owns only one idempotent
run and records each stage in ``data/logs/runs.jsonl``.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import UTC, datetime
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "paper_ingest_schedule.yaml"
CATALOG_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("paper ingest schedule must be a YAML mapping")
    for key in ("enabled", "working_dir", "python", "entrypoint", "log_file"):
        if key not in payload:
            raise ValueError(f"paper ingest schedule is missing {key}")
    return payload


def append_run(log_path: Path, *, stage: str, status: str, detail: dict[str, Any], duration_ms: int) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = {"ts": _utc_now(), "stage": stage, "status": status,
            "detail": detail, "duration_ms": duration_ms}
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n")


def _commands(python: str, database: Path) -> dict[str, list[str]]:
    return {
        "s1": [python, "scripts/refresh_paper_catalog.py", "--auto-enqueue", "--db", str(database)],
        "s2": [python, "scripts/process_catalog_jobs.py", "--db", str(database), "--once"],
        "s3": [python, "scripts/consume_catalog_outbox.py", "--db", str(database), "--once"],
        # S4 is deliberately in-process so its database identity assertion is
        # evaluated before any PDF asset can be written.
        "s4": [python, "-c", "from scripts.backfill_paper_index import process_received_jobs; process_received_jobs()"],
    }


def _run_stage(stage: str, command: list[str], *, cwd: Path, dry_run: bool) -> tuple[bool, dict[str, Any]]:
    if dry_run:
        return True, {"dry_run": True, "command": command}
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=120)
    except subprocess.TimeoutExpired as exc:
        return False, {"command": command, "error": "timeout", "timeout_seconds": 120,
                       "stdout": (exc.stdout or "")[-2000:], "stderr": (exc.stderr or "")[-2000:]}
    detail = {"command": command, "returncode": completed.returncode,
              "stdout": completed.stdout[-2000:], "stderr": completed.stderr[-2000:]}
    return completed.returncode == 0, detail


def run_once(*, config_path: Path, dry_run: bool, selected_stage: str, fail_fast: bool, verbose: bool) -> int:
    config = load_config(config_path)
    if not bool(config["enabled"]):
        print(json.dumps({"status": "disabled", "reason": "enabled=false"}, ensure_ascii=False))
        return 0
    working_dir = Path(str(config["working_dir"])).resolve()
    if working_dir != ROOT.resolve():
        raise ValueError(f"schedule working_dir must be {ROOT}, got {working_dir}")
    log_path = ROOT / str(config["log_file"])
    commands = _commands(str(config["python"]), CATALOG_DB)
    stages = [selected_stage] if selected_stage != "all" else ["s1", "s2", "s3", "s4"]
    failures = 0
    for stage in stages:
        started = time.monotonic()
        ok, detail = _run_stage(stage, commands[stage], cwd=working_dir, dry_run=dry_run)
        duration_ms = int((time.monotonic() - started) * 1000)
        append_run(log_path, stage=stage, status="dry_run" if dry_run else ("ok" if ok else "failed"),
                   detail=detail, duration_ms=duration_ms)
        print(json.dumps({"stage": stage, "status": "dry_run" if dry_run else ("ok" if ok else "failed"),
                          "detail": detail}, ensure_ascii=False))
        if not ok:
            failures += 1
            if fail_fast:
                break
    summary = {"status": "failed" if failures else "ok", "stages": stages, "failures": failures}
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the daily paper ingestion workflow once.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage", choices=("all", "s1", "s2", "s3", "s4"), default="all")
    parser.add_argument("--fail-fast", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        return run_once(config_path=args.config, dry_run=args.dry_run, selected_stage=args.stage,
                        fail_fast=args.fail_fast, verbose=args.verbose)
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
