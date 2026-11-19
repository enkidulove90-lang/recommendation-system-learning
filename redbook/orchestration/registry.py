"""Single-source SQLite delivery registry introduced by M3."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Iterator


_MIGRATION_KEY = "json_registry_migration_v1"
_REUSABLE_STATES = ("SAVING", "SAVED_UNVERIFIED", "VERIFIED")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SqliteDeliveryRegistry:
    """Registry whose uniqueness boundary is ``(platform, account, staged_id)``.

    Legacy JSON is read exactly once by :meth:`migrate_json_once`; every later
    online read and write uses this database, so migration never dual-writes.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

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
            connection.execute("""
                CREATE TABLE IF NOT EXISTS deliveries (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  run_id TEXT NOT NULL,
                  staged_id TEXT NOT NULL,
                  content_hash TEXT NOT NULL,
                  platform TEXT NOT NULL,
                  account TEXT NOT NULL,
                  draft_id TEXT,
                  state TEXT NOT NULL,
                  attempt INTEGER NOT NULL DEFAULT 1,
                  last_code TEXT,
                  evidence TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                )
            """)
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_delivery "
                "ON deliveries(platform, account, staged_id)"
            )
            connection.execute("""
                CREATE TABLE IF NOT EXISTS registry_meta (
                  key TEXT PRIMARY KEY,
                  value TEXT NOT NULL
                )
            """)
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _row(value: sqlite3.Row) -> dict[str, Any]:
        return {
            "run_id": value["run_id"], "staged_id": value["staged_id"],
            "content_hash": value["content_hash"], "platform": value["platform"],
            "account": value["account"], "draft_id": value["draft_id"],
            "state": value["state"], "attempt": value["attempt"],
            "last_code": value["last_code"],
        }

    def migrate_json_once(self, workflow_state: Path, *, platform: str = "xhs",
                          account: str = "default") -> int:
        """Import legacy JSON records atomically, then permanently mark the cutover."""
        imported = 0
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                if connection.execute(
                    "SELECT 1 FROM registry_meta WHERE key = ?", (_MIGRATION_KEY,)
                ).fetchone():
                    connection.execute("COMMIT")
                    return 0
                for source in sorted(workflow_state.glob("*/delivery_registry.json")):
                    raw = json.loads(source.read_text(encoding="utf-8"))
                    for run in raw.get("runs", []):
                        staged_id = str(run.get("staged_id", ""))
                        if not staged_id:
                            continue
                        state = "VERIFIED" if run.get("status") == "verify_passed" else "ROLLED_BACK"
                        timestamp = _now()
                        cursor = connection.execute("""
                            INSERT OR IGNORE INTO deliveries (
                              run_id, staged_id, content_hash, platform, account, draft_id,
                              state, attempt, last_code, evidence, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, NULL, ?, ?, ?)
                        """, (
                            str(run.get("run_id", "legacy")), staged_id, staged_id,
                            platform, account, str(run.get("draft_id", "")) or None, state,
                            json.dumps({"source": "legacy_json"}, ensure_ascii=False), timestamp, timestamp,
                        ))
                        imported += cursor.rowcount
                connection.execute(
                    "INSERT INTO registry_meta(key, value) VALUES (?, ?)", (_MIGRATION_KEY, _now())
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return imported

    def begin_save(self, *, run_id: str, content_hash: str, platform: str, account: str,
                   staged_id: str) -> dict[str, Any] | None:
        """Return an existing reusable delivery or atomically create a SAVING intent."""
        timestamp = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                existing = connection.execute("""
                    SELECT * FROM deliveries
                    WHERE platform = ? AND account = ? AND staged_id = ?
                      AND state IN (?, ?, ?)
                """, (platform, account, staged_id, *_REUSABLE_STATES)).fetchone()
                if existing:
                    connection.execute("COMMIT")
                    return self._row(existing)
                connection.execute("""
                    INSERT INTO deliveries (
                      run_id, staged_id, content_hash, platform, account, draft_id,
                      state, attempt, last_code, evidence, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, NULL, 'SAVING', 1, NULL, NULL, ?, ?)
                """, (run_id, staged_id, content_hash, platform, account, timestamp, timestamp))
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return None

    def delivery_count(self) -> int:
        with self._connection() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0])

    def find_delivery(self, *, platform: str, account: str, staged_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("""
                SELECT * FROM deliveries WHERE platform = ? AND account = ? AND staged_id = ?
            """, (platform, account, staged_id)).fetchone()
        return self._row(row) if row else None

    def find_reusable(self, *, platform: str, account: str, staged_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("""
                SELECT * FROM deliveries
                WHERE platform = ? AND account = ? AND staged_id = ?
                  AND state IN (?, ?, ?)
            """, (platform, account, staged_id, *_REUSABLE_STATES)).fetchone()
        return self._row(row) if row else None

    def stale_saving(self, stale_after_seconds: float) -> list[dict[str, Any]]:
        threshold = datetime.now(timezone.utc).timestamp() - stale_after_seconds
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM deliveries WHERE state = 'SAVING'").fetchall()
        return [
            self._row(row) for row in rows
            if datetime.fromisoformat(row["updated_at"]).timestamp() <= threshold
        ]

    def mark_saved_unverified(self, *, platform: str, account: str, staged_id: str,
                              draft_id: str | None) -> None:
        self._set_state(
            platform=platform, account=account, staged_id=staged_id,
            state="SAVED_UNVERIFIED", draft_id=draft_id, last_code=None,
        )

    def mark_manual(self, *, platform: str, account: str, staged_id: str,
                    code: str = "E_VERIFY_UNCERTAIN") -> None:
        self._set_state(
            platform=platform, account=account, staged_id=staged_id,
            state="MANUAL", draft_id=None, last_code=code,
        )

    def mark_verified(self, *, platform: str, account: str, staged_id: str) -> None:
        self._set_state(
            platform=platform, account=account, staged_id=staged_id,
            state="VERIFIED", draft_id=None, last_code=None,
        )

    def mark_missing(self, *, platform: str, account: str, staged_id: str) -> None:
        self._set_state(
            platform=platform, account=account, staged_id=staged_id,
            state="MISSING", draft_id=None, last_code="E_VERIFY_UNCERTAIN",
        )

    def mark_verify_uncertain(self, *, platform: str, account: str, staged_id: str) -> None:
        self._set_state(
            platform=platform, account=account, staged_id=staged_id,
            state="SAVED_UNVERIFIED", draft_id=None, last_code="E_VERIFY_UNCERTAIN",
        )

    def mark_rolled_back(self, *, platform: str, account: str, staged_id: str) -> None:
        self._set_state(
            platform=platform, account=account, staged_id=staged_id,
            state="ROLLED_BACK", draft_id=None, last_code=None,
        )

    def deliveries_in_state(self, state: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM deliveries WHERE state = ?", (state,)).fetchall()
        return [self._row(row) for row in rows]

    def deliveries_with_code(self, code: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM deliveries WHERE last_code = ?", (code,)).fetchall()
        return [self._row(row) for row in rows]

    def _set_state(self, *, platform: str, account: str, staged_id: str, state: str,
                   draft_id: str | None, last_code: str | None) -> None:
        with self._connection() as connection:
            cursor = connection.execute("""
                UPDATE deliveries
                SET state = ?, draft_id = COALESCE(?, draft_id), last_code = ?, updated_at = ?
                WHERE platform = ? AND account = ? AND staged_id = ?
            """, (state, draft_id, last_code, _now(), platform, account, staged_id))
        if cursor.rowcount != 1:
            raise KeyError(f"delivery not found for {platform}/{account}/{staged_id}")
