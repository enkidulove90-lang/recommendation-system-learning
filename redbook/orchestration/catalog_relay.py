"""Delivery-domain consumer for catalog PaperEligible outbox events.

The catalog never writes jobs. The relay consumes one event and creates its
platform job, idempotency marker, pool projection, and receipt atomically in
the same SQLite database. No platform adapter or long-running parser runs here.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Callable
from urllib.parse import urlparse
from uuid import uuid4

from paper_intake.catalog_governance import CatalogGovernance
from redbook.orchestration.queue import SqliteQueueBackend
from redbook.sentinel.paper_pool import PaperPool


class InvalidEvent(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CatalogOutboxRelay:
    def __init__(self, path: str | Path, *, max_attempts: int = 3,
                 retry_delay_seconds: float = 30.0,
                 after_job_insert: Callable[[], None] | None = None) -> None:
        self.path = Path(path)
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.after_job_insert = after_job_insert
        CatalogGovernance(self.path)
        PaperPool(self.path)
        self.queue = SqliteQueueBackend(self.path)
        with self.queue._connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS catalog_event_deliveries (
                operation_id TEXT PRIMARY KEY, job_id TEXT NOT NULL UNIQUE,
                delivered_at TEXT NOT NULL)""")

    @staticmethod
    def _payload(event: sqlite3.Row) -> dict:
        try:
            payload = json.loads(event["payload_json"])
        except (ValueError, TypeError) as error:
            raise InvalidEvent("invalid_event_payload") from error
        platform = event["platform"]
        expected_action = "publish" if platform == "homepage" else "save_draft"
        url = urlparse(str(payload.get("paper_url", "")))
        if (event["event_type"] != "PaperEligible" or payload.get("event_version") != 1
                or platform not in {"homepage", "xiaohongshu", "wechat"}
                or payload.get("platform") != platform
                or payload.get("catalog_id") != event["catalog_id"]
                or payload.get("action") != expected_action
                or not str(payload.get("canonical_id", ""))
                or not str(payload.get("title", ""))
                or url.scheme != "https" or url.netloc not in
                {"arxiv.org", "doi.org", "aclanthology.org"}):
            raise InvalidEvent("invalid_event_payload")
        return payload

    def _deliver(self, event: sqlite3.Row) -> str:
        with self.queue._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                duplicate = db.execute("SELECT job_id FROM catalog_event_deliveries WHERE operation_id=?",
                                       (event["operation_id"],)).fetchone()
                if duplicate:
                    db.execute("UPDATE catalog_outbox SET consumed_at=? WHERE id=?",
                               (_now().isoformat(), event["id"]))
                    db.execute("COMMIT")
                    return "duplicates"
                payload = self._payload(event)
                canonical_id = payload["canonical_id"]
                platform = event["platform"]
                existing = db.execute("SELECT pending_delivery FROM paper_pool WHERE canonical_id=?",
                                      (canonical_id,)).fetchone()
                if existing and existing["pending_delivery"]:
                    raise InvalidEvent("legacy_pool_conflict")
                stamp = _now().isoformat()
                db.execute("""INSERT OR IGNORE INTO paper_pool
                    (canonical_id, arxiv_id, doi, title, source, status,
                     pending_delivery, platforms, discovered_at, updated_at, reason)
                    VALUES (?, ?, ?, ?, 'catalog_outbox', 'discovered', 0, '', ?, ?, 'admitted')""",
                    (canonical_id, canonical_id.removeprefix("arxiv:") if canonical_id.startswith("arxiv:") else "",
                     canonical_id.removeprefix("doi:") if canonical_id.startswith("doi:") else "",
                     payload["title"], stamp, stamp))
                platform_row = db.execute("""SELECT status FROM paper_pool_platform_delivery
                    WHERE canonical_id=? AND platform=?""", (canonical_id, platform)).fetchone()
                if platform_row:
                    raise InvalidEvent("platform_job_conflict")
                depth = db.execute("""SELECT COUNT(*) FROM jobs WHERE queue='intake'
                    AND state IN ('QUEUED','RUNNING')""").fetchone()[0]
                if depth >= self.queue.default_max_depth:
                    raise RuntimeError("queue_full")
                db.execute("""INSERT INTO paper_pool_platform_delivery
                    (canonical_id, platform, status, pending_delivery, updated_at, reason)
                    VALUES (?, ?, 'queued', 1, ?, 'catalog admission')""",
                    (canonical_id, platform, stamp))
                job_id = uuid4().hex
                payload_ref = f"sentinel:{platform}:{canonical_id}"
                db.execute("""INSERT INTO jobs
                    (job_id, queue, payload_ref, payload_digest, state, attempt,
                     max_attempts, created_at, updated_at, run_id)
                    VALUES (?, 'intake', ?, ?, 'QUEUED', 0, 3, ?, ?, ?)""",
                    (job_id, payload_ref, hashlib.sha256(payload_ref.encode()).hexdigest(),
                     stamp, stamp, event["operation_id"]))
                db.execute("""INSERT INTO job_events (job_id, step, state, created_at)
                    VALUES (?, 'catalog_outbox', 'QUEUED', ?)""", (job_id, stamp))
                if self.after_job_insert:
                    self.after_job_insert()
                db.execute("""INSERT INTO catalog_event_deliveries
                    (operation_id, job_id, delivered_at) VALUES (?, ?, ?)""",
                    (event["operation_id"], job_id, stamp))
                db.execute("UPDATE catalog_outbox SET consumed_at=? WHERE id=?", (stamp, event["id"]))
                db.execute("COMMIT")
                return "sent"
            except Exception:
                db.execute("ROLLBACK")
                raise

    def _record_failure(self, event: sqlite3.Row, *, permanent: bool, reason: str) -> str:
        attempts = event["attempts"] + 1
        dead = permanent or attempts >= self.max_attempts
        visible = "" if dead else (_now() + timedelta(seconds=self.retry_delay_seconds)).isoformat()
        with self.queue._connection() as db:
            db.execute("""UPDATE catalog_outbox SET attempts=?, next_visible_at=?, dead_letter_reason=?
                WHERE id=? AND consumed_at IS NULL""",
                (attempts, visible, reason if dead else "", event["id"]))
        return "dead" if dead else "deferred"

    def run_once(self, *, limit: int = 50) -> dict[str, int]:
        report = {"sent": 0, "duplicates": 0, "deferred": 0, "dead": 0}
        with self.queue._connection() as db:
            events = db.execute("""SELECT * FROM catalog_outbox
                WHERE consumed_at IS NULL AND dead_letter_reason=''
                ORDER BY id LIMIT ?""", (max(0, limit),)).fetchall()
        for event in events:
            if event["next_visible_at"] and event["next_visible_at"] > _now().isoformat():
                break
            try:
                outcome = self._deliver(event)
            except InvalidEvent as error:
                outcome = self._record_failure(event, permanent=True, reason=str(error))
            except Exception as error:
                outcome = self._record_failure(event, permanent=False,
                                               reason=type(error).__name__)
            report[outcome] += 1
            if outcome == "deferred":
                break
        return report
