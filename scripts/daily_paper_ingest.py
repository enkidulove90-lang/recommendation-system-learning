"""Run the authoritative paper catalog-to-intake workflow once.

The operating system owns scheduling.  This script owns only one idempotent
run and records each stage in ``data/logs/runs.jsonl``.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.adapters import MinerUAdapter
from paper_intake.inputs import PaperInputStore
from paper_intake.metadata import ArxivMetadataResolver
from paper_intake.models import StepName, StepStatus
from paper_intake.pipeline import PaperPipeline
from paper_intake.repository import JobRepository


DEFAULT_CONFIG = ROOT / "config" / "paper_ingest_schedule.yaml"
UNIFIED_CATALOG_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_PAPERS_DIR = ROOT / "data" / "papers"
DEFAULT_RUN_LOG = ROOT / "data" / "logs" / "runs.jsonl"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("paper ingest schedule must be a YAML mapping")
    for key in ("enabled", "working_dir", "python", "entrypoint", "log_file", "s1_timeout_seconds"):
        if key not in payload:
            raise ValueError(f"paper ingest schedule is missing {key}")
    if int(payload["s1_timeout_seconds"]) < 1:
        raise ValueError("s1_timeout_seconds must be at least 1")
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
        "s3": [python, "scripts/consume_catalog_outbox.py", "--db", str(database), "--max", "1000"],
        "s4": [python, "scripts/daily_paper_ingest.py", "--consume-received", "--db", str(database)],
    }


def _received_pipeline(repository: JobRepository) -> PaperPipeline:
    input_store = PaperInputStore(ROOT / "data" / "paper_intake" / "inbox")
    return PaperPipeline(
        repository=repository,
        input_store=input_store,
        mineru=MinerUAdapter(),
        deepseek=None,
        notion=None,
        workflow_root=ROOT / "data" / "workflow_state" / "paper_intake",
        metadata_resolver=ArxivMetadataResolver(),
    )


def _target_pdf_path(papers_dir: Path, canonical_id: str, source_path: Path) -> Path:
    safe_name = Path(canonical_id).name or source_path.stem
    return papers_dir / f"{safe_name}.pdf"


def _consume_received_job(repository: JobRepository, pipeline: Any, job_id: str, papers_dir: Path) -> None:
    pipeline._run_step(job_id, StepName.VALIDATE_INPUT)
    pipeline._run_step(job_id, StepName.RESOLVE_METADATA)
    repository.start_step(job_id, StepName.DOWNLOAD_PDF)
    download_output = pipeline._step_download_pdf(job_id)
    source_path = Path(download_output["pdf_path"])
    current_job = repository.get_job(job_id)
    if current_job is None:
        raise KeyError(f"Unknown job: {job_id}")
    target_path = _target_pdf_path(papers_dir, current_job.canonical_id, source_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    repository.update_job(job_id, upload_path=str(target_path))
    download_output = {**download_output, "pdf_path": str(target_path)}
    repository.start_step(job_id, StepName.MINERU_PARSE)
    parse_output = pipeline._step_mineru_parse(job_id)
    repository.complete_received_ingest(
        job_id,
        download_output=download_output,
        parse_output=parse_output,
    )


def consume_received_jobs(
    *,
    database: Path,
    papers_dir: Path = DEFAULT_PAPERS_DIR,
    log_path: Path = DEFAULT_RUN_LOG,
    pipeline_factory=_received_pipeline,
) -> dict[str, Any]:
    """Consume every catalog-created received job through download and MinerU."""
    repository = JobRepository(database)
    processed = 0
    failed = 0
    job_ids: list[str] = []
    try:
        pipeline = pipeline_factory(repository)
        while received_jobs := repository.list_received_jobs():
            for job in received_jobs:
                started = time.monotonic()
                try:
                    _consume_received_job(repository, pipeline, job.job_id, papers_dir)
                except Exception as exc:
                    failed += 1
                    current = repository.get_job(job.job_id)
                    if current is not None and current.current_step:
                        step = repository.get_step(job.job_id, StepName(current.current_step))
                        if step is not None and step.status == StepStatus.RUNNING:
                            code, message = pipeline._safe_error(exc)
                            repository.fail_step(
                                job.job_id,
                                StepName(current.current_step),
                                error_code=code,
                                error_message=message,
                            )
                    append_run(
                        log_path,
                        stage="s4",
                        status="failed",
                        detail={"job_id": job.job_id, "error": type(exc).__name__, "message": str(exc)[:500]},
                        duration_ms=int((time.monotonic() - started) * 1000),
                    )
                    continue
                processed += 1
                job_ids.append(job.job_id)
                append_run(
                    log_path,
                    stage="s4",
                    status="ok",
                    detail={"job_id": job.job_id, "source_url": job.source_url},
                    duration_ms=int((time.monotonic() - started) * 1000),
                )
    finally:
        repository.close()
    result = {"processed": processed, "failed": failed, "jobs": job_ids}
    print(json.dumps(result, ensure_ascii=False))
    return result


def _run_stage(
    stage: str,
    command: list[str],
    *,
    cwd: Path,
    dry_run: bool,
    timeout_seconds: int,
) -> tuple[bool, dict[str, Any]]:
    if dry_run:
        return True, {"dry_run": True, "command": command}
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        return False, {"command": command, "error": "timeout", "timeout_seconds": timeout_seconds,
                       "stdout": (exc.stdout or "")[-2000:], "stderr": (exc.stderr or "")[-2000:]}
    detail = {"command": command, "returncode": completed.returncode,
              "stdout": completed.stdout[-2000:], "stderr": completed.stderr[-2000:]}
    return completed.returncode == 0, detail


def run_once(
    *,
    config_path: Path,
    dry_run: bool,
    selected_stage: str,
    fail_fast: bool,
    verbose: bool,
    s1_timeout_seconds: int | None = None,
) -> int:
    config = load_config(config_path)
    if not bool(config["enabled"]):
        print(json.dumps({"status": "disabled", "reason": "enabled=false"}, ensure_ascii=False))
        return 0
    working_dir = Path(str(config["working_dir"])).resolve()
    if working_dir != ROOT.resolve():
        raise ValueError(f"schedule working_dir must be {ROOT}, got {working_dir}")
    log_path = ROOT / str(config["log_file"])
    commands = _commands(str(config["python"]), UNIFIED_CATALOG_DB)
    s1_timeout = s1_timeout_seconds or int(config["s1_timeout_seconds"])
    stages = [selected_stage] if selected_stage != "all" else ["s1", "s2", "s3", "s4"]
    failures = 0
    for stage in stages:
        started = time.monotonic()
        ok, detail = _run_stage(
            stage,
            commands[stage],
            cwd=working_dir,
            dry_run=dry_run,
            timeout_seconds=s1_timeout if stage == "s1" else 120,
        )
        duration_ms = int((time.monotonic() - started) * 1000)
        status = "dry_run" if dry_run else ("ok" if ok else ("timeout" if detail.get("error") == "timeout" else "failed"))
        append_run(log_path, stage=stage, status=status,
                   detail=detail, duration_ms=duration_ms)
        print(json.dumps({"stage": stage, "status": status,
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
    parser.add_argument("--fail-fast", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--s1-timeout-seconds", type=int)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--consume-received", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--db", type=Path, default=UNIFIED_CATALOG_DB, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.s1_timeout_seconds is not None and args.s1_timeout_seconds < 1:
            parser.error("--s1-timeout-seconds must be at least 1")
        if args.consume_received:
            result = consume_received_jobs(database=args.db)
            return 1 if result["failed"] else 0
        return run_once(config_path=args.config, dry_run=args.dry_run, selected_stage=args.stage,
                        fail_fast=args.fail_fast, verbose=args.verbose,
                        s1_timeout_seconds=args.s1_timeout_seconds)
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
