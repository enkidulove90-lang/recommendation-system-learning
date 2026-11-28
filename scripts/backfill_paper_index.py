"""Idempotently register locally stored PDF assets in the unified intake DB."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_identity import canonical_id_from_bare
from paper_intake.models import JobStatus, StepName
from paper_intake.repository import JobRepository


DEFAULT_PAPERS = ROOT / "data" / "papers"
DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
ARXIV_ID = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def paper_id_from_path(path: Path) -> str:
    """Return the canonical (prefixed) identity for a locally stored PDF."""
    match = ARXIV_ID.search(path.stem)
    if match:
        return canonical_id_from_bare(match.group(1))
    return canonical_id_from_bare(path.stem)


def assert_unified_database(database: Path, *, expected_database: Path = DEFAULT_DB) -> Path:
    expected = expected_database.resolve()
    requested = Path(os.getenv("PAPER_INTAKE_DB_PATH", expected)).resolve()
    if requested != expected or database.resolve() != expected:
        raise RuntimeError(f"PAPER_INTAKE_DB_PATH must resolve to {expected}")
    return expected


def _register_pdf(repository: JobRepository, pdf: Path, canonical_id: str) -> str:
    digest = sha256_file(pdf)
    duplicate = repository.find_duplicate(canonical_id=canonical_id, source_sha256=digest)
    if duplicate:
        return "skipped"
    job = repository.create_job(source_type="upload", upload_path=str(pdf))
    repository.update_job(job.job_id, canonical_id=canonical_id, source_sha256=digest)
    repository.start_step(job.job_id, StepName.DOWNLOAD_PDF, input_hash=digest)
    repository.complete_step(job.job_id, StepName.DOWNLOAD_PDF,
                             output={"pdf_path": str(pdf), "sha256": digest})
    repository.update_job(job.job_id, status=JobStatus.AWAITING_REVIEW, current_step="")
    return "created"


def backfill(papers_dir: Path = DEFAULT_PAPERS, database: Path = DEFAULT_DB, *, dry_run: bool = False,
             expected_database: Path = DEFAULT_DB) -> dict[str, list[str]]:
    database = assert_unified_database(database, expected_database=expected_database)
    result: dict[str, list[str]] = {"created": [], "skipped": [], "warnings": []}
    if dry_run:
        existing: set[tuple[str, str]] = set()
        planned_ids: set[str] = set()
        if database.exists():
            connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
            try:
                existing = {(str(row[0]), str(row[1])) for row in connection.execute(
                    "SELECT canonical_id, source_sha256 FROM jobs"
                )}
            finally:
                connection.close()
        for pdf in sorted(papers_dir.glob("*.pdf")):
            canonical_id = paper_id_from_path(pdf)
            if not canonical_id:
                result["warnings"].append(pdf.name)
            elif canonical_id in planned_ids or (canonical_id, sha256_file(pdf)) in existing:
                result["skipped"].append(canonical_id)
            else:
                result["created"].append(canonical_id)
                planned_ids.add(canonical_id)
        return result
    repository = JobRepository(database)
    try:
        for pdf in sorted(papers_dir.glob("*.pdf")):
            canonical_id = paper_id_from_path(pdf)
            if not canonical_id:
                result["warnings"].append(pdf.name)
                continue
            if repository.find_duplicate(canonical_id=canonical_id, source_sha256=sha256_file(pdf)):
                result["skipped"].append(canonical_id)
                continue
            if _register_pdf(repository, pdf, canonical_id) == "created":
                result["created"].append(canonical_id)
            else:
                result["skipped"].append(canonical_id)
    finally:
        repository.close()
    return result


def process_received_jobs() -> None:
    """S4's local-asset pass; URL downloading remains an explicit worker concern."""
    report = backfill()
    print(json.dumps({"status": "ok", **report}, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backfill PDF assets into the unified paper intake index.")
    parser.add_argument("--papers-dir", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(backfill(args.papers_dir, args.db, dry_run=args.dry_run), ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
