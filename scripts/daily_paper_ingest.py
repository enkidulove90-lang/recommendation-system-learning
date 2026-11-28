"""Run the authoritative paper catalog-to-intake workflow once.

The operating system owns scheduling.  This script owns only one idempotent
run and records each stage in ``data/logs/runs.jsonl``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import uuid
import re
import shutil
import subprocess
import sys
import time
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from redbook.infrastructure.run_log import log_event

from paper_intake.adapters import MinerUAdapter
from paper_intake.inputs import PaperInputStore
from paper_intake.metadata import ArxivMetadataResolver
from paper_intake.models import JobStatus, StepName, StepStatus
from paper_intake.pipeline import PaperPipeline
from paper_intake.repository import JobRepository


DEFAULT_CONFIG = ROOT / "config" / "paper_ingest_schedule.yaml"
UNIFIED_CATALOG_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_PAPERS_DIR = ROOT / "data" / "papers"
DEFAULT_RUN_LOG = ROOT / "data" / "logs" / "runs.jsonl"


def load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("paper ingest schedule must be a YAML mapping")
    for key in ("enabled", "working_dir", "python", "entrypoint", "log_file", "s1_timeout_seconds"):
        if key not in payload:
            raise ValueError(f"paper ingest schedule is missing {key}")
    if int(payload["s1_timeout_seconds"]) < 1:
        raise ValueError("s1_timeout_seconds must be at least 1")
    if not isinstance(payload["time"], str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", payload["time"]):
        raise ValueError("paper ingest schedule time must use HH:MM (00:00-23:59)")
    if "stages" in payload:
        stages = payload["stages"]
        if not isinstance(stages, list) or not stages:
            raise ValueError("paper ingest schedule stages must be a non-empty list")
        unknown = [stage for stage in stages if stage not in ("s1", "s2", "s3", "s4", "s5")]
        if unknown:
            raise ValueError(f"paper ingest schedule has unknown stages: {unknown}")
    return payload


def append_run(log_path: Path, *, stage: str, status: str, detail: dict[str, Any], duration_ms: int) -> None:
    """Single run-log writer: delegates to run_log.log_event so every row has
    an ``event`` field and shares the module-level append lock."""
    log_event("paper_ingest_stage", path=log_path, stage=stage, status=status,
              detail=detail, duration_ms=duration_ms)


def _commands(python: str, database: Path) -> dict[str, list[str]]:
    return {
        "s1": [python, "scripts/refresh_paper_catalog.py", "--auto-enqueue", "--db", str(database)],
        "s2": [python, "scripts/process_catalog_jobs.py", "--db", str(database), "--once"],
        "s3": [python, "scripts/consume_catalog_outbox.py", "--db", str(database), "--max", "1000"],
        "s4": [python, "scripts/daily_paper_ingest.py", "--consume-received", "--db",
               str(database), "--max-jobs", "2"],
        # s5 consumes ParseCompleted events emitted by s4 and drives the shared
        # fact_pack -> platform package chain.  Must run AFTER s4 so the events
        # it consumes already exist in the outbox.
        "s5": [python, "scripts/content_bridge.py", "--db", str(database), "--max-jobs", "50"],
    }


def _resolve_working_dir(value: str, entrypoint: str) -> Path:
    configured = Path(value)
    working_dir = (ROOT / configured).resolve() if not configured.is_absolute() else configured.resolve()
    required_entrypoint = working_dir / entrypoint
    if not required_entrypoint.is_file() or not (working_dir / "scripts" / "daily_paper_ingest.py").is_file():
        raise ValueError(f"schedule working_dir must contain scripts/daily_paper_ingest.py: {working_dir}")
    return working_dir


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


def emit_parse_completed(repository: JobRepository, canonical_id: str, markdown_path: str, *,
                         job_id: str = "", catalog_canonical_id: str = "",
                         pdf_path: str = "", pdf_sha256: str = "") -> str | None:
    """Emit a ParseCompleted outbox event after S4 finished MinerU parsing.

    Idempotent on (canonical_id, markdown_path): re-running S4 for the same
    artifact never duplicates the event.  Returns the event_id, or None when
    an identical event already exists.
    """
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    key_parts = f"ParseCompleted|{canonical_id}|{markdown_path}"
    if job_id:
        key_parts += f"|{job_id}|{pdf_sha256}"
    idempotency_key = hashlib.sha256(key_parts.encode("utf-8")).hexdigest()
    payload = {"canonical_id": canonical_id, "markdown_path": markdown_path}
    if job_id:
        payload.update(job_id=job_id, catalog_canonical_id=catalog_canonical_id,
                       pdf_path=pdf_path, pdf_sha256=pdf_sha256)
    connection = repository._connection
    with connection:
        existing = connection.execute(
            "SELECT event_id FROM outbox WHERE idempotency_key=?",
            (idempotency_key,),
        ).fetchone()
        if existing is not None:
            return None
        event_id = str(uuid.uuid4())
        connection.execute(
            "INSERT INTO outbox(event_id, event_type, event_version, producer_domain, "
            "target_domain, aggregate_id, idempotency_key, payload_json, occurred_at, available_at) "
            "VALUES (?, 'ParseCompleted', ?, 'paper_intake', 'content_bridge', ?, ?, ?, ?, ?)",
            (
                event_id, 2 if job_id else 1, canonical_id, idempotency_key,
                json.dumps(payload),
                now, now,
            ),
        )
    return event_id


def _consume_received_job(repository: JobRepository, pipeline: Any, job_id: str, papers_dir: Path,
                          tracing_id: str | None = None, log_path: Path = DEFAULT_RUN_LOG) -> None:
    """消费一个已接收的论文作业，记录每一步的详细日志。"""
    current_job = repository.get_job(job_id)
    if current_job is None:
        raise KeyError(f"Unknown job: {job_id}")

    paper_id = current_job.canonical_id
    canonical_id = current_job.canonical_id

    # 记录每个步骤的开始和结束
    def log_step(step_name: StepName, status: str, detail: dict | None = None):
        append_run(
            log_path,
            stage="s4",
            status=status,
            detail={
                "job_id": job_id,
                "paper_id": paper_id,
                "canonical_id": canonical_id,
                "tracing_id": tracing_id,
                "step": step_name.value,
                **(detail or {}),
            },
            duration_ms=int((detail or {}).get("duration_ms", 0)),
        )

    # 1. Validate Input
    start = time.monotonic()
    log_step(StepName.VALIDATE_INPUT, "start")
    try:
        pipeline._run_step(job_id, StepName.VALIDATE_INPUT)
        log_step(StepName.VALIDATE_INPUT, "ok", {"duration_ms": int((time.monotonic() - start) * 1000)})
    except Exception as e:
        log_step(StepName.VALIDATE_INPUT, "failed", {"error": str(e)[:500]})
        raise

    # 2. Resolve Metadata
    start = time.monotonic()
    log_step(StepName.RESOLVE_METADATA, "start")
    try:
        pipeline._run_step(job_id, StepName.RESOLVE_METADATA)
        log_step(StepName.RESOLVE_METADATA, "ok", {"duration_ms": int((time.monotonic() - start) * 1000)})
    except Exception as e:
        log_step(StepName.RESOLVE_METADATA, "failed", {"error": str(e)[:500]})
        raise

    # 3. Download PDF
    start = time.monotonic()
    log_step(StepName.DOWNLOAD_PDF, "start")
    repository.start_step(job_id, StepName.DOWNLOAD_PDF)
    try:
        download_output = pipeline._step_download_pdf(job_id)
        log_step(StepName.DOWNLOAD_PDF, "ok", {
            "duration_ms": int((time.monotonic() - start) * 1000),
            "pdf_path": download_output.get("pdf_path"),
            "sha256": download_output.get("sha256"),
        })
    except Exception as e:
        log_step(StepName.DOWNLOAD_PDF, "failed", {"error": str(e)[:500]})
        repository.fail_step(
            job_id,
            StepName.DOWNLOAD_PDF,
            error_code="download_failed",
            error_message=str(e)[:500],
        )
        raise

    source_path = Path(download_output["pdf_path"])
    if current_job is None:
        raise KeyError(f"Unknown job: {job_id}")

    # 4. Move PDF to papers directory
    target_path = _target_pdf_path(papers_dir, current_job.canonical_id, source_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    try:
        shutil.copy2(source_path, target_path)
        repository.update_job(job_id, upload_path=str(target_path))
        log_step(StepName.DOWNLOAD_PDF, "pdf_copied", {
            "source_size": source_path.stat().st_size,
            "target_size": target_path.stat().st_size,
            "duration_ms": int((time.monotonic() - start) * 1000),
        })
    except Exception as e:
        log_step(StepName.DOWNLOAD_PDF, "pdf_copy_failed", {"error": str(e)[:500]})
        raise

    download_output = {**download_output, "pdf_path": str(target_path)}

    # 5. MinerU Parse
    start = time.monotonic()
    log_step(StepName.MINERU_PARSE, "start")
    repository.start_step(job_id, StepName.MINERU_PARSE)
    try:
        parse_output = pipeline._step_mineru_parse(job_id)
        log_step(StepName.MINERU_PARSE, "ok", {
            "duration_ms": int((time.monotonic() - start) * 1000),
            "markdown_path": parse_output.get("markdown_path"),
            "figure_count": len(parse_output.get("figures", [])),
        })
    except Exception as e:
        log_step(StepName.MINERU_PARSE, "failed", {"error": str(e)[:500]})
        repository.fail_step(
            job_id,
            StepName.MINERU_PARSE,
            error_code="mineru_parse_failed",
            error_message=str(e)[:500],
        )
        raise

    repository.complete_received_ingest(
        job_id,
        download_output=download_output,
        parse_output=parse_output,
    )

    # 6. Emit ParseCompleted event
    markdown = str(parse_output.get("markdown_path") or "")
    if markdown and current_job.canonical_id:
        start = time.monotonic()
        row = repository._connection.execute(
            "SELECT catalog_canonical_id FROM jobs WHERE job_id=?", (job_id,)
        ).fetchone()
        catalog_id = str(row[0] or "") if row else ""
        event_id = emit_parse_completed(
            repository, current_job.canonical_id, markdown, job_id=job_id,
            catalog_canonical_id=catalog_id, pdf_path=str(target_path),
            pdf_sha256=str(download_output.get("sha256") or ""),
        )
        if event_id:
            log_step(StepName.MINERU_PARSE, "parse_completed", {
                "event_id": event_id,
                "duration_ms": int((time.monotonic() - start) * 1000),
            })
        else:
            log_step(StepName.MINERU_PARSE, "parse_completed_duplicate", {})


def _default_master_check(repository: JobRepository, job: Any) -> bool:
    """A received job is consumable only if it joins the identity master."""
    from paper_intake.catalog_identity import canonical_id_from_bare

    for raw in (getattr(job, "catalog_canonical_id", ""), getattr(job, "canonical_id", "")):
        if not raw:
            continue
        candidate = raw if ":" in raw else canonical_id_from_bare(raw)
        for value in {raw, candidate}:
            if not value:
                continue
            row = repository._connection.execute(
                "SELECT 1 FROM papers WHERE canonical_id=? LIMIT 1", (value,)
            ).fetchone()
            if row is not None:
                return True
    return False


def consume_received_jobs(
    *,
    database: Path,
    papers_dir: Path = DEFAULT_PAPERS_DIR,
    log_path: Path = DEFAULT_RUN_LOG,
    pipeline_factory=_received_pipeline,
    master_check=_default_master_check,
    max_jobs: int = 5,
) -> dict[str, Any]:
    """Consume at most ``max_jobs`` received jobs that join the identity master.

    Bounded on purpose: each job downloads a PDF + runs MinerU (30-60s), and
    the scheduler gives s4 a 120s budget.  Unbounded consumption used to hit
    that timeout and get killed mid-batch.
    """
    repository = JobRepository(database)
    processed = 0
    failed = 0
    blocked = 0
    job_ids: list[str] = []
    try:
        pipeline = pipeline_factory(repository)
        while (processed + failed + blocked) < max_jobs and (
                received_jobs := repository.list_received_jobs()):
            for job in received_jobs:
                if processed + failed + blocked >= max_jobs:
                    break
                started = time.monotonic()
                if not master_check(repository, job):
                    blocked += 1
                    repository.update_job(job.job_id, status=JobStatus.BLOCKED)
                    append_run(
                        log_path, stage="s4", status="blocked",
                        detail={"job_id": job.job_id, "reason": "no_identity_master_join",
                                "canonical_id": getattr(job, "canonical_id", "")},
                        duration_ms=int((time.monotonic() - started) * 1000),
                    )
                    continue
                try:
                    _consume_received_job(repository, pipeline, job.job_id, papers_dir, log_path=log_path)
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
    result = {"processed": processed, "failed": failed, "blocked": blocked, "jobs": job_ids}
    print(json.dumps(result, ensure_ascii=False))
    return result


def _run_stage(
    stage: str,
    command: list[str],
    *,
    cwd: Path,
    dry_run: bool,
    env: dict[str, str],
    timeout_seconds: int,
) -> tuple[bool, dict[str, Any]]:
    if dry_run:
        return True, {"dry_run": True, "command": command}
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
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
    working_dir = _resolve_working_dir(str(config["working_dir"]), str(config["entrypoint"]))
    log_path = ROOT / str(config["log_file"])
    commands = _commands(str(config["python"]), UNIFIED_CATALOG_DB)
    child_env = os.environ.copy()
    child_env["PAPER_INTAKE_DB_PATH"] = str(UNIFIED_CATALOG_DB)
    s1_timeout = s1_timeout_seconds or int(config["s1_timeout_seconds"])
    # Backward compatible: configs without an explicit `stages` list keep the
    # historical s1-s4 set (and any injected command map in tests stays valid).
    # s5 is opt-in via config, or runnable directly with `--stage s5`.
    configured_stages = config.get("stages") or ["s1", "s2", "s3", "s4"]
    stages = [selected_stage] if selected_stage != "all" else list(configured_stages)
    failures = 0
    for stage in stages:
        started = time.monotonic()
        ok, detail = _run_stage(
            stage,
            commands[stage],
            cwd=working_dir,
            dry_run=dry_run,
            env=child_env,
            # s5 may generate the first fact_pack via DeepSeek, which is a
            # network-bound model call; give it the same generous window as s1
            # instead of the 120s default used for fast local stages.
            timeout_seconds=s1_timeout if stage in ("s1", "s5") else 120,
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
    parser.add_argument("--stage", choices=("all", "s1", "s2", "s3", "s4", "s5"), default="all")
    parser.add_argument("--fail-fast", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--s1-timeout-seconds", type=int)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--consume-received", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--db", type=Path, default=UNIFIED_CATALOG_DB, help=argparse.SUPPRESS)
    parser.add_argument("--max-jobs", type=int, default=5, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.s1_timeout_seconds is not None and args.s1_timeout_seconds < 1:
            parser.error("--s1-timeout-seconds must be at least 1")
        if args.consume_received:
            result = consume_received_jobs(database=args.db, max_jobs=args.max_jobs)
            return 1 if result["failed"] else 0
        return run_once(config_path=args.config, dry_run=args.dry_run, selected_stage=args.stage,
                        fail_fast=args.fail_fast, verbose=args.verbose,
                        s1_timeout_seconds=args.s1_timeout_seconds)
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
