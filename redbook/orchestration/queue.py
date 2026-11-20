"""Queue boundary: a backend-neutral Protocol plus the SQLite reference backend.

The method names map one-to-one onto Redis Streams so that swapping backends
later ("先语义，后中间件") requires no business-code change:

- ``enqueue``   -> XADD
- ``claim``     -> XREADGROUP (pending lease = PEML entry)
- ``heartbeat`` -> XCLAIM (extend idle)
- ``complete``/``fail`` -> XACK (+ state write)
- ``cancel``    -> per-job control flag read at step boundaries

The SQLite backend is the acceptance implementation for task 1; it keeps the
whole lifecycle in WAL transactions so crash recovery equals lease expiry.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
import hashlib
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Iterator, Protocol

from redbook.infrastructure.delivery_errors import (
    E_QUEUE_FULL, OrchestrationError,
)
from . import models
from .models import Job, Receipt


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.isoformat()


class QueueFullError(OrchestrationError):
    """Raised when a bounded queue refuses a new job (honest backpressure)."""

    def __init__(self, queue: str, max_depth: int) -> None:
        super().__init__(
            f"queue {queue} is full (max_depth={max_depth})",
            code=E_QUEUE_FULL,
            details={"queue": queue, "max_depth": max_depth},
        )


class QueueBackend(Protocol):
    """Minimal async-friendly surface shared by SQLite and future Redis."""

    def enqueue(self, queue: str, payload_ref: str, *, run_id: str = "",
                max_attempts: int = 3) -> Job: ...
    def claim(self, worker_id: str, *, lease_ttl_seconds: float = 60.0) -> Job | None: ...
    def heartbeat(self, job_id: str, worker_id: str, *,
                  lease_ttl_seconds: float = 60.0) -> bool: ...
    def complete(self, job_id: str, worker_id: str, state: str) -> Receipt: ...
    def fail(self, job_id: str, worker_id: str, error: OrchestrationError) -> Receipt: ...
    def cancel(self, job_id: str) -> bool: ...
    def depth(self, queue: str) -> int: ...
    def get_job(self, job_id: str) -> Job | None: ...
    def append_event(self, job_id: str, step: str, state: str, *,
                     code: str = "", detail: str = "") -> int: ...
    def events(self, job_id: str) -> list[dict[str, Any]]: ...


class SqliteQueueBackend:
    """WAL-backed queue sharing ``orchestration.sqlite`` with the registry."""

    def __init__(self, path: Path, *, max_depths: dict[str, int] | None = None,
                 default_max_depth: int = 1000,
                 backoff_seconds: float = 30.0) -> None:
        self.path = Path(path)
        self.max_depths = dict(max_depths or {})
        self.default_max_depth = default_max_depth
        self.backoff_seconds = backoff_seconds

    # -- connection ---------------------------------------------------------
    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA busy_timeout=5000")
            for attempt in range(50):
                try:
                    connection.execute("PRAGMA journal_mode=WAL")
                    break
                except sqlite3.OperationalError as error:
                    if "locked" not in str(error).lower() or attempt == 49:
                        raise
                    time.sleep(0.01)
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                  job_id TEXT PRIMARY KEY,
                  queue TEXT NOT NULL,
                  payload_ref TEXT NOT NULL,
                  payload_digest TEXT NOT NULL,
                  state TEXT NOT NULL,
                  attempt INTEGER NOT NULL DEFAULT 0,
                  max_attempts INTEGER NOT NULL DEFAULT 3,
                  cancel_requested INTEGER NOT NULL DEFAULT 0,
                  lease_owner TEXT NOT NULL DEFAULT '',
                  lease_expires_at TEXT NOT NULL DEFAULT '',
                  last_code TEXT,
                  run_id TEXT NOT NULL DEFAULT '',
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_jobs_queue_state
                  ON jobs(queue, state, created_at);
                CREATE TABLE IF NOT EXISTS job_events (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_id TEXT NOT NULL,
                  step TEXT NOT NULL,
                  state TEXT NOT NULL,
                  code TEXT NOT NULL DEFAULT '',
                  detail TEXT NOT NULL DEFAULT '',
                  created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_job_events_job
                  ON job_events(job_id, seq);
            """)
            yield connection
        finally:
            connection.close()

    # -- helpers ------------------------------------------------------------
    @staticmethod
    def _job(row: sqlite3.Row) -> Job:
        return Job(
            job_id=row["job_id"], queue=row["queue"],
            payload_ref=row["payload_ref"], payload_digest=row["payload_digest"],
            state=row["state"], attempt=row["attempt"],
            max_attempts=row["max_attempts"],
            cancel_requested=bool(row["cancel_requested"]),
            lease_owner=row["lease_owner"],
            lease_expires_at=row["lease_expires_at"],
            last_code=row["last_code"], run_id=row["run_id"],
            created_at=row["created_at"], updated_at=row["updated_at"],
        )

    def _set_state(self, connection: sqlite3.Connection, job_id: str, state: str, *,
                   worker_id: str = "", lease_ttl: float | None = None,
                   code: str | None = None) -> None:
        models.validate_transition(
            connection.execute("SELECT state FROM jobs WHERE job_id = ?", (job_id,)).fetchone()[0],
            state,
        )
        # lease_ttl=0.0 is meaningful ("expires immediately"): only None clears.
        expires = (_iso(_now() + timedelta(seconds=lease_ttl))
                   if lease_ttl is not None else "")
        connection.execute(
            "UPDATE jobs SET state = ?, lease_owner = ?, lease_expires_at = ?, "
            "last_code = COALESCE(?, last_code), updated_at = ? WHERE job_id = ?",
            (state, worker_id, expires, code, _iso(_now()), job_id),
        )

    # -- QueueBackend -------------------------------------------------------
    def enqueue(self, queue: str, payload_ref: str, *, run_id: str = "",
                max_attempts: int = 3,
                enqueue_step: str = "enqueue") -> Job:
        max_depth = self.max_depths.get(queue, self.default_max_depth)
        timestamp = _iso(_now())
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                depth = connection.execute(
                    "SELECT COUNT(*) FROM jobs WHERE queue = ? "
                    "AND state IN ('QUEUED', 'RUNNING')", (queue,)
                ).fetchone()[0]
                if depth >= max_depth:
                    raise QueueFullError(queue, max_depth)
                job_id = uuid.uuid4().hex
                digest = hashlib.sha256(payload_ref.encode("utf-8")).hexdigest()
                connection.execute(
                    "INSERT INTO jobs (job_id, queue, payload_ref, payload_digest, state, "
                    "attempt, max_attempts, created_at, updated_at, run_id) "
                    "VALUES (?, ?, ?, ?, 'QUEUED', 0, ?, ?, ?, ?)",
                    (job_id, queue, payload_ref, digest, max_attempts, timestamp, timestamp, run_id),
                )
                connection.execute(
                    "INSERT INTO job_events (job_id, step, state, created_at) "
                    "VALUES (?, ?, 'QUEUED', ?)", (job_id, enqueue_step, timestamp),
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return self.get_job(job_id)  # type: ignore[return-value]

    def claim(self, worker_id: str, *, lease_ttl_seconds: float = 60.0) -> Job | None:
        timestamp = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                # promote failed-retryable jobs whose backoff window has elapsed
                connection.execute(
                    "UPDATE jobs SET state = 'QUEUED', updated_at = ? "
                    "WHERE state = 'FAILED_RETRYABLE' AND lease_expires_at <= ?",
                    (_iso(timestamp), _iso(timestamp)),
                )
                # zombie takeover: a RUNNING job whose lease expired is requeued
                stale = connection.execute(
                    "SELECT job_id, cancel_requested FROM jobs "
                    "WHERE state = 'RUNNING' AND lease_expires_at != '' "
                    "AND lease_expires_at <= ?",
                    (_iso(timestamp),),
                ).fetchall()
                for row in stale:
                    target = models.CANCELLED if row["cancel_requested"] else models.QUEUED
                    self._set_state(connection, row["job_id"], target)
                    connection.execute(
                        "INSERT INTO job_events (job_id, step, state, created_at) "
                        "VALUES (?, 'lease_expired', ?, ?)",
                        (row["job_id"], target, _iso(timestamp)),
                    )
                rows = connection.execute(
                    "SELECT * FROM jobs WHERE state = 'QUEUED' "
                    "ORDER BY created_at LIMIT 1"
                ).fetchall()
                row = rows[0] if rows else None
                if row is None:
                    connection.execute("COMMIT")
                    return None
                if row["cancel_requested"]:
                    self._set_state(connection, row["job_id"], models.CANCELLED)
                    connection.execute(
                        "INSERT INTO job_events (job_id, step, state, created_at) "
                        "VALUES (?, 'claim', 'CANCELLED', ?)",
                        (row["job_id"], _iso(timestamp)),
                    )
                    connection.execute("COMMIT")
                    return None
                self._set_state(connection, row["job_id"], models.RUNNING,
                                worker_id=worker_id, lease_ttl=lease_ttl_seconds)
                connection.execute(
                    "UPDATE jobs SET attempt = attempt + 1 WHERE job_id = ?",
                    (row["job_id"],),
                )
                connection.execute(
                    "INSERT INTO job_events (job_id, step, state, detail, created_at) "
                    "VALUES (?, 'claim', 'RUNNING', ?, ?)",
                    (row["job_id"], worker_id, _iso(timestamp)),
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return self.get_job(row["job_id"])  # type: ignore[return-value]

    def heartbeat(self, job_id: str, worker_id: str, *,
                  lease_ttl_seconds: float = 60.0) -> bool:
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE jobs SET lease_owner = ?, lease_expires_at = ?, updated_at = ? "
                "WHERE job_id = ? AND lease_owner = ? AND state = 'RUNNING'",
                (worker_id, _iso(_now() + timedelta(seconds=lease_ttl_seconds)),
                 _iso(_now()), job_id, worker_id),
            )
        return cursor.rowcount == 1

    def complete(self, job_id: str, worker_id: str, state: str) -> Receipt:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                self._set_state(connection, job_id, state, worker_id=worker_id, code=None)
                connection.execute(
                    "INSERT INTO job_events (job_id, step, state, created_at) "
                    "VALUES (?, 'complete', ?, ?)", (job_id, state, _iso(_now())),
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return Receipt(job_id=job_id, state=state)

    def fail(self, job_id: str, worker_id: str, error: OrchestrationError) -> Receipt:
        retryable = _policy_retryable(error)
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT attempt, max_attempts FROM jobs WHERE job_id = ?",
                    (job_id,),
                ).fetchone()
                if row is None:
                    raise KeyError(job_id)
                exhausted = row["attempt"] >= row["max_attempts"]
                if retryable and not exhausted:
                    # back to the queue with an available-at backoff encoded in lease
                    self._set_state(connection, job_id, models.FAILED_RETRYABLE,
                                    code=error.code)
                    connection.execute(
                        "UPDATE jobs SET lease_expires_at = ? WHERE job_id = ?",
                        (_iso(_now() + timedelta(seconds=self.backoff_seconds)), job_id),
                    )
                elif retryable:
                    self._set_state(connection, job_id, models.FAILED_TERMINAL,
                                    code=error.code)
                else:
                    self._set_state(connection, job_id, models.FAILED_TERMINAL,
                                    code=error.code)
                connection.execute(
                    "INSERT INTO job_events (job_id, step, state, code, detail, created_at) "
                    "VALUES (?, 'fail', ?, ?, ?, ?)",
                    (job_id,
                     models.FAILED_RETRYABLE if (retryable and not exhausted)
                     else models.FAILED_TERMINAL,
                     error.code, error.message, _iso(_now())),
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        state = models.FAILED_RETRYABLE if (retryable and not exhausted) else models.FAILED_TERMINAL
        return Receipt(job_id=job_id, state=state, code=error.code,
                       retryable=retryable and not exhausted)

    def cancel(self, job_id: str) -> bool:
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE jobs SET cancel_requested = 1, updated_at = ? "
                "WHERE job_id = ? AND state IN ('QUEUED', 'RUNNING')",
                (_iso(_now()), job_id),
            )
        return cursor.rowcount == 1

    def requeue(self, job_id: str) -> bool:
        """Human reset path: MANUAL / FAILED_* / CANCELLED back to QUEUED."""
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                state = connection.execute(
                    "SELECT state FROM jobs WHERE job_id = ?", (job_id,)
                ).fetchone()[0]
                self._set_state(connection, job_id, models.QUEUED)
                connection.execute(
                    "INSERT INTO job_events (job_id, step, state, created_at) "
                    "VALUES (?, 'requeue', 'QUEUED', ?)", (job_id, _iso(_now())),
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return True

    def depth(self, queue: str) -> int:
        with self._connection() as connection:
            return int(connection.execute(
                "SELECT COUNT(*) FROM jobs WHERE queue = ? AND state IN ('QUEUED', 'RUNNING')",
                (queue,),
            ).fetchone()[0])

    def get_job(self, job_id: str) -> Job | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        return self._job(row) if row else None

    def append_event(self, job_id: str, step: str, state: str, *,
                     code: str = "", detail: str = "") -> int:
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO job_events (job_id, step, state, code, detail, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, step, state, code, detail, _iso(_now())),
            )
        return int(cursor.lastrowid or 0)

    def events(self, job_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT seq, job_id, step, state, code, detail, created_at "
                "FROM job_events WHERE job_id = ? ORDER BY seq", (job_id,),
            ).fetchall()
        return [dict(row) for row in rows]


def _policy_retryable(error: OrchestrationError) -> bool:
    from redbook.infrastructure.delivery_errors import policy_for
    return bool(policy_for(error.code).get("retryable"))
