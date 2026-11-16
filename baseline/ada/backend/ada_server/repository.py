"""SQLite-backed repository: runs, events (monotonic seq), config snapshots."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    phase TEXT NOT NULL,
    status TEXT NOT NULL,             -- draft|blocked|queued|running|succeeded|failed|cancelled
    blocked INTEGER NOT NULL DEFAULT 0,
    blocking_reasons TEXT NOT NULL DEFAULT '[]',
    config_hash TEXT,
    split_hash TEXT,
    baseline_run_id TEXT,
    is_synthetic_demo INTEGER NOT NULL DEFAULT 0,
    pid INTEGER,
    return_code INTEGER,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    event TEXT NOT NULL,
    payload TEXT NOT NULL,
    is_terminal INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    UNIQUE (run_id, seq)
);
CREATE TABLE IF NOT EXISTS config_snapshots (
    run_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT,
    kind TEXT NOT NULL DEFAULT 'file',
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_run ON events (run_id, seq);
"""


class Repository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- runs ---------------------------------------------------------------

    def upsert_run(self, **fields: Any) -> None:
        fields.setdefault("updated_at", time.time())
        for key, value in fields.items():
            if isinstance(value, (list, dict)):
                fields[key] = json.dumps(value)
            elif isinstance(value, bool):
                fields[key] = int(value)
        with self._lock:
            run_id = fields.get("run_id")
            existing = self._conn.execute(
                "SELECT 1 FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if existing:
                columns = [c for c in fields if c != "run_id"]
                self._conn.execute(
                    f"UPDATE runs SET {', '.join(f'{c}=?' for c in columns)} WHERE run_id=?",
                    [fields[c] for c in columns] + [run_id],
                )
            else:
                defaults = {
                    "phase": "P0", "status": "draft", "blocked": 0,
                    "blocking_reasons": "[]", "is_synthetic_demo": 0,
                }
                merged = {**defaults, **fields}
                merged.setdefault("created_at", time.time())
                columns = list(merged.keys())
                self._conn.execute(
                    f"INSERT INTO runs ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
                    [merged[c] for c in columns],
                )
            self._conn.commit()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return self._run_from_row(row)

    def list_runs(self) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM runs ORDER BY created_at DESC").fetchall()
        return [self._run_from_row(r) for r in rows]

    @staticmethod
    def _run_from_row(row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        data["blocked"] = bool(data["blocked"])
        data["is_synthetic_demo"] = bool(data["is_synthetic_demo"])
        data["blocking_reasons"] = json.loads(data["blocking_reasons"])
        return data

    def running_run(self) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT * FROM runs WHERE status = 'running' LIMIT 1"
        ).fetchone()
        return self._run_from_row(row) if row else None

    # -- events -------------------------------------------------------------

    def append_event(
        self, run_id: str, event: str, payload: Dict[str, Any], *, is_terminal: bool = False
    ) -> int:
        """Append with a per-run monotonic seq; returns the seq.

        Terminal transitions are unique per (run_id, kind): a duplicate
        terminal event is ignored (idempotent), so SSE resume never
        re-delivers a second terminal transition.
        """
        with self._lock:
            if is_terminal:
                existing = self._conn.execute(
                    "SELECT seq FROM events WHERE run_id = ? AND is_terminal = 1 AND event = ?",
                    (run_id, event),
                ).fetchone()
                if existing:
                    return int(existing["seq"])
            row = self._conn.execute(
                "SELECT COALESCE(MAX(seq), 0) AS m FROM events WHERE run_id = ?", (run_id,)
            ).fetchone()
            seq = int(row["m"]) + 1
            self._conn.execute(
                "INSERT INTO events (run_id, seq, event, payload, is_terminal, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, seq, event, json.dumps(payload, default=str), int(is_terminal), time.time()),
            )
            self._conn.commit()
            return seq

    def events_since(self, run_id: str, last_seq: int = 0) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE run_id = ? AND seq > ? ORDER BY seq ASC",
            (run_id, last_seq),
        ).fetchall()
        return [self._event_from_row(r) for r in rows]

    def all_events(self, run_id: str) -> List[Dict[str, Any]]:
        return self.events_since(run_id, 0)

    def last_event_seq(self, run_id: str) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(MAX(seq), 0) AS m FROM events WHERE run_id = ?", (run_id,)
        ).fetchone()
        return int(row["m"])

    @staticmethod
    def _event_from_row(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "seq": int(row["seq"]),
            "event": row["event"],
            "payload": json.loads(row["payload"]),
            "is_terminal": bool(row["is_terminal"]),
            "created_at": row["created_at"],
        }

    # -- config snapshot ----------------------------------------------------

    def save_config_snapshot(self, run_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO config_snapshots (run_id, payload, created_at) VALUES (?, ?, ?) "
                "ON CONFLICT(run_id) DO UPDATE SET payload=excluded.payload",
                (run_id, json.dumps(payload, default=str), time.time()),
            )
            self._conn.commit()

    def get_config_snapshot(self, run_id: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT payload FROM config_snapshots WHERE run_id = ?", (run_id,)
        ).fetchone()
        return json.loads(row["payload"]) if row else None

    # -- artifacts ----------------------------------------------------------

    def add_artifact(self, run_id: str, name: str, path: str, sha256: str = "", kind: str = "file") -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO artifacts (run_id, name, path, sha256, kind, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, name, path, sha256, kind, time.time()),
            )
            self._conn.commit()

    def list_artifacts(self, run_id: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM artifacts WHERE run_id = ? ORDER BY id ASC", (run_id,)
        ).fetchall()
        return [dict(r) for r in rows]
