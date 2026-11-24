from __future__ import annotations

import json
import hashlib
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import EventRecord, JobRecord, JobStatus, StepName, StepRecord, StepStatus
from .inputs import canonicalize_url


def _now() -> str:
    return datetime.now(UTC).isoformat()


class JobRepository:
    """Transactional SQLite ledger for paper jobs and resumable steps."""

    _UPDATABLE_JOB_FIELDS = {
        "source_url",
        "upload_path",
        "source_sha256",
        "canonical_id",
        "title",
        "status",
        "current_step",
        "notion_page_id",
        "notion_url",
        "github_run_id",
        "published_url",
        "error_code",
        "error_message",
    }

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA busy_timeout = 5000")
        self._create_schema()

    def close(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

    def _create_schema(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    source_type TEXT NOT NULL,
                    source_url TEXT NOT NULL DEFAULT '',
                    upload_path TEXT NOT NULL DEFAULT '',
                    source_sha256 TEXT NOT NULL DEFAULT '',
                    canonical_id TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    current_step TEXT NOT NULL DEFAULT '',
                    notion_page_id TEXT NOT NULL DEFAULT '',
                    notion_url TEXT NOT NULL DEFAULT '',
                    github_run_id TEXT NOT NULL DEFAULT '',
                    published_url TEXT NOT NULL DEFAULT '',
                    error_code TEXT NOT NULL DEFAULT '',
                    error_message TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS jobs_canonical_id_idx ON jobs(canonical_id);
                CREATE INDEX IF NOT EXISTS jobs_source_sha256_idx ON jobs(source_sha256);
                CREATE INDEX IF NOT EXISTS jobs_source_url_idx ON jobs(source_url);

                CREATE TABLE IF NOT EXISTS job_steps (
                    job_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    input_hash TEXT NOT NULL DEFAULT '',
                    output_json TEXT NOT NULL DEFAULT '{}',
                    error_code TEXT NOT NULL DEFAULT '',
                    error_message TEXT NOT NULL DEFAULT '',
                    started_at TEXT NOT NULL DEFAULT '',
                    completed_at TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (job_id, step_name),
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS job_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL DEFAULT '',
                    details_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                );
                """
            )
            columns = {row["name"] for row in self._connection.execute("PRAGMA table_info(jobs)")}
            for name in ("source_event_id", "source_idempotency_key", "merge_review_status", "catalog_canonical_id"):
                if name not in columns:
                    self._connection.execute(f"ALTER TABLE jobs ADD COLUMN {name} TEXT")
            self._connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS jobs_source_event_id_uq "
                "ON jobs(source_event_id) WHERE source_event_id IS NOT NULL"
            )
            self._connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS jobs_source_idempotency_key_uq "
                "ON jobs(source_idempotency_key) WHERE source_idempotency_key IS NOT NULL"
            )

    def create_job(
        self,
        *,
        source_type: str,
        source_url: str = "",
        upload_path: str = "",
        job_id: str | None = None,
    ) -> JobRecord:
        if source_type not in {"url", "upload"}:
            raise ValueError("source_type must be 'url' or 'upload'")
        identifier = job_id or str(uuid.uuid4())
        timestamp = _now()
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO jobs (
                    job_id, source_type, source_url, upload_path, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    source_type,
                    source_url,
                    upload_path,
                    JobStatus.RECEIVED.value,
                    timestamp,
                    timestamp,
                ),
            )
            self._add_event(identifier, "job.created", "Paper intake job created")
        return self._require_job(identifier)

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        return self._job_from_row(row) if row else None

    def _require_job(self, job_id: str) -> JobRecord:
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(f"Unknown job: {job_id}")
        return job

    def list_jobs(self, *, limit: int = 100) -> list[JobRecord]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._job_from_row(row) for row in rows]

    def list_received_jobs(self) -> list[JobRecord]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM jobs WHERE status=? ORDER BY created_at, job_id",
                (JobStatus.RECEIVED.value,),
            ).fetchall()
        return [self._job_from_row(row) for row in rows]

    def create_from_catalog_event(self, *, event_id: str, idempotency_key: str, payload: dict[str, str]) -> str:
        """Insert an intake job inside the caller's active SQLite transaction."""
        if not self._connection.in_transaction:
            raise RuntimeError("catalog event insertion requires an active transaction")
        existing = self._connection.execute(
            "SELECT job_id FROM jobs WHERE source_event_id=? OR source_idempotency_key=?",
            (event_id, idempotency_key),
        ).fetchone()
        if existing:
            return existing["job_id"]
        job_id = str(uuid.uuid4())
        timestamp = _now()
        intake_id = canonicalize_url(payload["pdf_url"]).canonical_id
        if not intake_id:
            raise ValueError("catalog PDF must have an intake paper ID")
        self._connection.execute(
            """INSERT INTO jobs (
                job_id, source_type, source_url, canonical_id, title, status,
                source_event_id, source_idempotency_key, catalog_canonical_id, created_at, updated_at
            ) VALUES (?, 'url', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING""",
            (job_id, payload["pdf_url"], intake_id, payload["title"],
             JobStatus.RECEIVED.value, event_id, idempotency_key, payload["canonical_id"], timestamp, timestamp),
        )
        saved = self._connection.execute(
            "SELECT job_id FROM jobs WHERE source_event_id=? OR source_idempotency_key=?",
            (event_id, idempotency_key),
        ).fetchone()
        if saved is None:
            raise sqlite3.IntegrityError("catalog job could not be inserted")
        if saved["job_id"] == job_id:
            self._add_event(job_id, "job.created", "Paper intake job created from catalog", {"source_event_id": event_id})
        return saved["job_id"]

    def record_delivery_terminal(self, job_id: str, *, success: bool) -> str:
        with self._lock, self._connection:
            job = self._connection.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if job is None:
                raise KeyError(job_id)
            expected = JobStatus.PUBLISHED.value if success else JobStatus.FAILED.value
            if job["status"] != expected:
                raise ValueError("delivery receipt requires a terminal job state")
            return self._record_terminal_tx(job, success=success)

    def complete_verified_publication(self, job_id: str) -> JobRecord:
        """Finalize a verified URL and its catalog receipt in one transaction."""
        now = _now()
        with self._lock, self._connection:
            row = self._connection.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            if not row["published_url"]:
                raise ValueError("published URL is required")
            self._connection.execute(
                """UPDATE jobs SET status=?, current_step='', error_code='', error_message='', updated_at=?
                WHERE job_id=?""",
                (JobStatus.PUBLISHED.value, now, job_id),
            )
            if row["source_event_id"]:
                self._record_terminal_tx(row, success=True)
        return self._require_job(job_id)

    def _record_terminal_tx(self, job: sqlite3.Row, *, success: bool) -> str:
        job_id = job["job_id"]
        event_type = "DeliveryCompleted" if success else "DeliveryFailed"
        key = hashlib.sha256(f"{job_id}|{event_type}|v1".encode()).hexdigest()
        event_id = str(uuid.uuid4())
        now = _now()
        self._connection.execute(
            """INSERT INTO outbox(event_id, event_type, event_version, producer_domain,
                target_domain, aggregate_id, idempotency_key, payload_json, occurred_at, available_at)
            VALUES (?, ?, 1, 'paper_intake', 'catalog', ?, ?, ?, ?, ?)
            ON CONFLICT(idempotency_key) DO NOTHING""",
            (event_id, event_type, job["catalog_canonical_id"] or job["canonical_id"], key,
             json.dumps({"canonical_id": job["catalog_canonical_id"] or job["canonical_id"], "job_id": job_id,
                         "result": "completed" if success else "failed"}), now, now),
        )
        return self._connection.execute(
            "SELECT event_id FROM outbox WHERE idempotency_key=?", (key,)
        ).fetchone()["event_id"]

    def find_duplicate(
        self,
        *,
        canonical_id: str = "",
        source_sha256: str = "",
        source_url: str = "",
        exclude_job_id: str = "",
    ) -> JobRecord | None:
        conditions: list[str] = []
        parameters: list[str] = []
        for column, value in (
            ("canonical_id", canonical_id),
            ("source_sha256", source_sha256),
            ("source_url", source_url),
        ):
            if value:
                conditions.append(f"{column} = ?")
                parameters.append(value)
        if not conditions:
            return None
        query = "SELECT * FROM jobs WHERE (" + " OR ".join(conditions) + ")"
        if exclude_job_id:
            query += " AND job_id != ?"
            parameters.append(exclude_job_id)
        query += " ORDER BY created_at LIMIT 1"
        with self._lock:
            row = self._connection.execute(query, parameters).fetchone()
        return self._job_from_row(row) if row else None

    def update_job(self, job_id: str, **values: Any) -> JobRecord:
        unknown = set(values) - self._UPDATABLE_JOB_FIELDS
        if unknown:
            raise ValueError(f"Unsupported job fields: {', '.join(sorted(unknown))}")
        if not values:
            return self._require_job(job_id)
        normalized = {
            key: value.value if isinstance(value, JobStatus) else value
            for key, value in values.items()
        }
        normalized["updated_at"] = _now()
        assignments = ", ".join(f"{key} = ?" for key in normalized)
        with self._lock, self._connection:
            cursor = self._connection.execute(
                f"UPDATE jobs SET {assignments} WHERE job_id = ?",
                (*normalized.values(), job_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Unknown job: {job_id}")
        return self._require_job(job_id)

    def start_step(
        self,
        job_id: str,
        step_name: StepName,
        *,
        input_hash: str = "",
    ) -> StepRecord:
        self._require_job(job_id)
        timestamp = _now()
        with self._lock, self._connection:
            existing = self._connection.execute(
                "SELECT attempts FROM job_steps WHERE job_id = ? AND step_name = ?",
                (job_id, step_name.value),
            ).fetchone()
            attempts = int(existing["attempts"]) + 1 if existing else 1
            self._connection.execute(
                """
                INSERT INTO job_steps (
                    job_id, step_name, status, attempts, input_hash, output_json,
                    error_code, error_message, started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, '{}', '', '', ?, '')
                ON CONFLICT(job_id, step_name) DO UPDATE SET
                    status = excluded.status,
                    attempts = excluded.attempts,
                    input_hash = excluded.input_hash,
                    output_json = '{}',
                    error_code = '',
                    error_message = '',
                    started_at = excluded.started_at,
                    completed_at = ''
                """,
                (
                    job_id,
                    step_name.value,
                    StepStatus.RUNNING.value,
                    attempts,
                    input_hash,
                    timestamp,
                ),
            )
            self._connection.execute(
                """
                UPDATE jobs
                SET status = ?, current_step = ?, error_code = '', error_message = '', updated_at = ?
                WHERE job_id = ?
                """,
                (JobStatus.PROCESSING.value, step_name.value, timestamp, job_id),
            )
            self._add_event(job_id, "step.started", step_name.value, {"attempt": attempts})
        return self._require_step(job_id, step_name)

    def complete_step(
        self,
        job_id: str,
        step_name: StepName,
        *,
        output: dict[str, Any] | None = None,
    ) -> StepRecord:
        timestamp = _now()
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE job_steps
                SET status = ?, output_json = ?, error_code = '', error_message = '', completed_at = ?
                WHERE job_id = ? AND step_name = ?
                """,
                (
                    StepStatus.SUCCEEDED.value,
                    json.dumps(output or {}, ensure_ascii=False),
                    timestamp,
                    job_id,
                    step_name.value,
                ),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Step has not started: {step_name.value}")
            self._connection.execute(
                "UPDATE jobs SET updated_at = ? WHERE job_id = ?", (timestamp, job_id)
            )
            self._add_event(job_id, "step.succeeded", step_name.value, output or {})
        return self._require_step(job_id, step_name)

    def fail_step(
        self,
        job_id: str,
        step_name: StepName,
        *,
        error_code: str,
        error_message: str,
    ) -> StepRecord:
        timestamp = _now()
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE job_steps
                SET status = ?, error_code = ?, error_message = ?, completed_at = ?
                WHERE job_id = ? AND step_name = ?
                """,
                (
                    StepStatus.FAILED.value,
                    error_code,
                    error_message,
                    timestamp,
                    job_id,
                    step_name.value,
                ),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Step has not started: {step_name.value}")
            self._connection.execute(
                """
                UPDATE jobs
                SET status = ?, error_code = ?, error_message = ?, updated_at = ?
                WHERE job_id = ?
                """,
                (
                    (JobStatus.RATE_LIMITED_MANUAL_RETRY.value
                    if error_code in {"pdf_rate_limited_manual_retry", "arxiv_rate_limited_manual_retry"}
                    else JobStatus.FAILED.value),
                    error_code,
                    error_message,
                    timestamp,
                    job_id,
                ),
            )
            self._add_event(
                job_id,
                "step.failed",
                step_name.value,
                {"error_code": error_code, "error_message": error_message},
            )
        return self._require_step(job_id, step_name)

    def get_step(self, job_id: str, step_name: StepName) -> StepRecord | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM job_steps WHERE job_id = ? AND step_name = ?",
                (job_id, step_name.value),
            ).fetchone()
        return self._step_from_row(row) if row else None

    def _require_step(self, job_id: str, step_name: StepName) -> StepRecord:
        step = self.get_step(job_id, step_name)
        if step is None:
            raise KeyError(f"Unknown step: {job_id}/{step_name.value}")
        return step

    def list_steps(self, job_id: str) -> list[StepRecord]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM job_steps WHERE job_id = ? ORDER BY rowid", (job_id,)
            ).fetchall()
        return [self._step_from_row(row) for row in rows]

    def reset_steps(
        self,
        job_id: str,
        *,
        restart_from: StepName,
        ordered_steps: tuple[StepName, ...],
    ) -> int:
        if restart_from not in ordered_steps:
            raise ValueError(f"Step is not restartable: {restart_from.value}")
        names = [step.value for step in ordered_steps[ordered_steps.index(restart_from) :]]
        placeholders = ", ".join("?" for _ in names)
        with self._lock, self._connection:
            cursor = self._connection.execute(
                f"DELETE FROM job_steps WHERE job_id = ? AND step_name IN ({placeholders})",
                (job_id, *names),
            )
            self._connection.execute(
                """
                UPDATE jobs
                SET status = ?, current_step = '', error_code = '', error_message = '', updated_at = ?
                WHERE job_id = ?
                """,
                (JobStatus.RECEIVED.value, _now(), job_id),
            )
            self._add_event(
                job_id,
                "job.reset",
                restart_from.value,
                {"cleared_steps": names},
            )
        return cursor.rowcount

    def recover_interrupted_jobs(self) -> int:
        timestamp = _now()
        with self._lock, self._connection:
            rows = self._connection.execute(
                "SELECT job_id, step_name FROM job_steps WHERE status = ?",
                (StepStatus.RUNNING.value,),
            ).fetchall()
            for row in rows:
                self._connection.execute(
                    """
                    UPDATE job_steps
                    SET status = ?, error_code = ?, error_message = ?, completed_at = ?
                    WHERE job_id = ? AND step_name = ?
                    """,
                    (
                        StepStatus.INTERRUPTED.value,
                        "interrupted",
                        "The local service stopped while this step was running.",
                        timestamp,
                        row["job_id"],
                        row["step_name"],
                    ),
                )
                self._connection.execute(
                    """
                    UPDATE jobs
                    SET status = ?, error_code = ?, error_message = ?, updated_at = ?
                    WHERE job_id = ?
                    """,
                    (
                        JobStatus.FAILED.value,
                        "interrupted",
                        "The local service stopped while this step was running.",
                        timestamp,
                        row["job_id"],
                    ),
                )
                self._add_event(
                    row["job_id"],
                    "step.interrupted",
                    row["step_name"],
                )
        return len(rows)

    def list_events(self, job_id: str) -> list[EventRecord]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM job_events WHERE job_id = ? ORDER BY event_id", (job_id,)
            ).fetchall()
        return [self._event_from_row(row) for row in rows]

    def record_manual_retry(self, job_id: str, operator: str) -> None:
        with self._lock, self._connection:
            self._add_event(job_id, "job.manual_retry_requested", "Manual retry requested",
                            {"operator": operator, "requested_at": _now()})

    def _add_event(
        self,
        job_id: str,
        event_type: str,
        message: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO job_events (job_id, event_type, message, details_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                job_id,
                event_type,
                message,
                json.dumps(details or {}, ensure_ascii=False),
                _now(),
            ),
        )

    @staticmethod
    def _job_from_row(row: sqlite3.Row) -> JobRecord:
        return JobRecord(
            job_id=row["job_id"],
            source_type=row["source_type"],
            source_url=row["source_url"],
            upload_path=row["upload_path"],
            source_sha256=row["source_sha256"],
            canonical_id=row["canonical_id"],
            title=row["title"],
            status=JobStatus(row["status"]),
            current_step=row["current_step"],
            notion_page_id=row["notion_page_id"],
            notion_url=row["notion_url"],
            github_run_id=row["github_run_id"],
            published_url=row["published_url"],
            error_code=row["error_code"],
            error_message=row["error_message"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _step_from_row(row: sqlite3.Row) -> StepRecord:
        return StepRecord(
            job_id=row["job_id"],
            step_name=StepName(row["step_name"]),
            status=StepStatus(row["status"]),
            attempts=int(row["attempts"]),
            input_hash=row["input_hash"],
            output=json.loads(row["output_json"] or "{}"),
            error_code=row["error_code"],
            error_message=row["error_message"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
        )

    @staticmethod
    def _event_from_row(row: sqlite3.Row) -> EventRecord:
        return EventRecord(
            event_id=int(row["event_id"]),
            job_id=row["job_id"],
            event_type=row["event_type"],
            message=row["message"],
            details=json.loads(row["details_json"] or "{}"),
            created_at=row["created_at"],
        )
