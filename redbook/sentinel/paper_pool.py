"""Paper pool: the single shared candidate store consumed by all platforms.

Decoupling contract (task 3): the pool is the ONLY shared artifact — each
platform takes candidates from the pool independently and records progress in
its own registry rows; platforms never call each other's adapters. Status
vocabulary is forward-only (same philosophy as the queue state machine);
``pending_delivery`` FIFO drives automatic delivery.
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

#: forward-only status vocabulary; blocked is recoverable via requeue
STATUSES = ("discovered", "queued", "parsed", "summarized", "composed",
            "staged", "SAVED_UNVERIFIED", "VERIFIED", "published", "blocked")

TRANSITIONS: dict[str, frozenset[str]] = {
    "discovered": frozenset({"queued", "blocked"}),
    "queued": frozenset({"parsed", "blocked"}),
    "parsed": frozenset({"summarized", "blocked"}),
    "summarized": frozenset({"composed", "blocked"}),
    "composed": frozenset({"staged", "blocked"}),
    "staged": frozenset({"SAVED_UNVERIFIED", "blocked"}),
    "SAVED_UNVERIFIED": frozenset({"VERIFIED", "blocked"}),
    "VERIFIED": frozenset({"published", "blocked"}),
    "published": frozenset(),
    "blocked": frozenset({"queued"}),  # human reset path
}

_PLATFORMS = ("xiaohongshu", "wechat", "homepage")

_DDL = """
CREATE TABLE IF NOT EXISTS paper_pool (
  canonical_id TEXT PRIMARY KEY,
  arxiv_id TEXT NOT NULL DEFAULT '',
  doi TEXT NOT NULL DEFAULT '',
  title TEXT NOT NULL DEFAULT '',
  source TEXT NOT NULL DEFAULT 'daily_discovery',
  status TEXT NOT NULL DEFAULT 'discovered',
  pending_delivery INTEGER NOT NULL DEFAULT 0,
  platforms TEXT NOT NULL DEFAULT '',
  discovered_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  reason TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS sentinel_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InvalidPoolTransition(Exception):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"illegal pool transition {current} -> {target}")
        self.current = current
        self.target = target


@dataclass
class PoolEntry:
    canonical_id: str
    arxiv_id: str
    doi: str
    title: str
    status: str
    pending_delivery: bool
    platforms: str
    discovered_at: str
    updated_at: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_id": self.canonical_id, "arxiv_id": self.arxiv_id,
            "doi": self.doi, "title": self.title, "status": self.status,
            "pending_delivery": self.pending_delivery,
            "platforms": self.platforms,
            "discovered_at": self.discovered_at, "updated_at": self.updated_at,
            "reason": self.reason,
        }


class PaperPool:
    """SQLite-backed pool sharing ``orchestration.sqlite`` with queue/registry."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.executescript(_DDL)

    # contextmanager import kept local to avoid module-level noise
    def _connection(self) -> Iterator[sqlite3.Connection]:
        from contextlib import contextmanager

        @contextmanager
        def manager():
            connection = sqlite3.connect(self.path, timeout=5,
                                         isolation_level=None)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA busy_timeout=5000")
            try:
                yield connection
            finally:
                connection.close()
        return manager()

    # -- meta (idempotent retrieval bookkeeping) -----------------------------
    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000")
        try:
            yield connection
        finally:
            connection.close()

    # -- meta (idempotent retrieval bookkeeping) -----------------------------
    def get_meta(self, key: str) -> str | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT value FROM sentinel_meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO sentinel_meta (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value))

    # -- candidates ----------------------------------------------------------
    def add_candidate(self, *, canonical_id: str, arxiv_id: str = "",
                      doi: str = "", title: str = "",
                      source: str = "daily_discovery",
                      exclusions: set[str] | None = None) -> dict[str, Any]:
        """Idempotent insert (TC10): existing canonical_id returns added=False."""
        if exclusions and (arxiv_id in exclusions or canonical_id in exclusions):
            return {"added": False, "reason": "excluded",
                    "canonical_id": canonical_id}
        moment = _now()
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT canonical_id FROM paper_pool WHERE canonical_id = ? "
                "OR (arxiv_id != '' AND arxiv_id = ?) OR (doi != '' AND doi = ?)",
                (canonical_id, arxiv_id, doi)).fetchone()
            if existing is not None:
                return {"added": False, "reason": "duplicate",
                        "canonical_id": existing["canonical_id"]}
            connection.execute(
                "INSERT INTO paper_pool (canonical_id, arxiv_id, doi, title, "
                "source, status, pending_delivery, platforms, discovered_at, "
                "updated_at, reason) VALUES (?, ?, ?, ?, ?, 'discovered', 1, "
                "'', ?, ?, 'hard-gate passed')",
                (canonical_id, arxiv_id, doi, title, source, moment, moment))
        return {"added": True, "reason": "", "canonical_id": canonical_id}

    def set_status(self, canonical_id: str, target: str) -> None:
        if target not in STATUSES:
            raise InvalidPoolTransition("unknown", target)
        with self._connection() as connection:
            current = connection.execute(
                "SELECT status FROM paper_pool WHERE canonical_id = ?",
                (canonical_id,)).fetchone()
            if current is None:
                raise KeyError(canonical_id)
            if target not in TRANSITIONS[current["status"]]:
                raise InvalidPoolTransition(current["status"], target)
            connection.execute(
                "UPDATE paper_pool SET status = ?, updated_at = ? "
                "WHERE canonical_id = ?", (target, _now(), canonical_id))

    def record_platform(self, canonical_id: str, platform: str) -> None:
        """One platform finished its leg; registry stays the per-platform truth."""
        if platform not in _PLATFORMS:
            raise ValueError(f"unknown platform {platform}")
        with self._connection() as connection:
            row = connection.execute(
                "SELECT platforms FROM paper_pool WHERE canonical_id = ?",
                (canonical_id,)).fetchone()
            if row is None:
                raise KeyError(canonical_id)
            done = set(json.loads(row["platforms"] or "[]"))
            done.add(platform)
            connection.execute(
                "UPDATE paper_pool SET platforms = ?, updated_at = ? "
                "WHERE canonical_id = ?",
                (json.dumps(sorted(done)), _now(), canonical_id))

    def take_pending(self, limit: int = 1) -> list[PoolEntry]:
        """FIFO claim of pending entries; atomic re-queue->queued prevents
        two consumers taking the same paper (TC16)."""
        claimed: list[PoolEntry] = []
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                rows = connection.execute(
                    "SELECT canonical_id FROM paper_pool "
                    "WHERE pending_delivery = 1 AND status = 'discovered' "
                    "ORDER BY discovered_at LIMIT ?", (limit,)).fetchall()
                for row in rows:
                    connection.execute(
                        "UPDATE paper_pool SET status = 'queued', "
                        "updated_at = ? WHERE canonical_id = ?",
                        (_now(), row["canonical_id"]))
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
            if rows:
                marks = ",".join("?" * len(rows))
                fetched = connection.execute(
                    f"SELECT * FROM paper_pool WHERE canonical_id IN ({marks})",
                    tuple(r["canonical_id"] for r in rows)).fetchall()
                claimed = [self._entry(r) for r in fetched]
        return claimed

    def reset_blocked(self, canonical_id: str) -> None:
        with self._connection() as connection:
            connection.execute(
                "UPDATE paper_pool SET status = 'queued', updated_at = ? "
                "WHERE canonical_id = ? AND status = 'blocked'",
                (_now(), canonical_id))

    def reset_to_discovered(self, canonical_id: str) -> None:
        """Dispatch fallback (queue full): keep pending, re-enter FIFO."""
        with self._connection() as connection:
            connection.execute(
                "UPDATE paper_pool SET status = 'discovered', updated_at = ? "
                "WHERE canonical_id = ? AND status = 'queued'",
                (_now(), canonical_id))

    @staticmethod
    def _entry(row: sqlite3.Row) -> PoolEntry:
        return PoolEntry(
            canonical_id=row["canonical_id"], arxiv_id=row["arxiv_id"],
            doi=row["doi"], title=row["title"], status=row["status"],
            pending_delivery=bool(row["pending_delivery"]),
            platforms=row["platforms"],
            discovered_at=row["discovered_at"], updated_at=row["updated_at"],
            reason=row["reason"])


def load_exclusions(path: Path) -> set[str]:
    """Hexo-side exclusion list (``tools/paper_exclusions.json`` shape)."""
    if not Path(path).exists():
        return set()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = data.get("excluded", data)
    else:
        items = data
    return {str(item) for item in items} if isinstance(items, list) else set()
