"""Chapter 5: append-only creator metrics, normalized SQLite, and bounded adjustments."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any

from .common import append_jsonl, utc_now


SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
 note_id TEXT PRIMARY KEY, paper_id TEXT NOT NULL, platform TEXT NOT NULL,
 published_at TEXT NOT NULL, time_slot TEXT NOT NULL, topics_json TEXT NOT NULL,
 features_json TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metric_snapshots (
 note_id TEXT NOT NULL, observed_at TEXT NOT NULL, age_hours INTEGER NOT NULL,
 views INTEGER, likes INTEGER, collects INTEGER, comments INTEGER, replies INTEGER,
 shares INTEGER, follows INTEGER, traffic_json TEXT, audience_json TEXT, raw_path TEXT NOT NULL,
 PRIMARY KEY (note_id, age_hours)
);
CREATE TABLE IF NOT EXISTS decisions (
 decision_id TEXT PRIMARY KEY, made_at TEXT NOT NULL, target_type TEXT NOT NULL,
 target_key TEXT NOT NULL, previous_value REAL, next_value REAL, evidence_json TEXT NOT NULL,
 rollback_at TEXT
);
"""


class FeedbackStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / "feedback" / "feedback.sqlite"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = self.connect()
        try:
            connection.executescript(SCHEMA)
            connection.commit()
        finally:
            connection.close()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def register_post(self, post: dict[str, Any]) -> None:
        required = ("note_id", "paper_id", "published_at", "time_slot", "content_hash")
        missing = [key for key in required if not post.get(key)]
        if missing:
            raise ValueError(f"missing post fields: {', '.join(missing)}")
        connection = self.connect()
        try:
            connection.execute("""INSERT OR REPLACE INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                post["note_id"], post["paper_id"], post.get("platform", "xiaohongshu"), post["published_at"], post["time_slot"],
                json.dumps(post.get("topics", []), ensure_ascii=False), json.dumps(post.get("features", {}), ensure_ascii=False), post["content_hash"],
            ))
            connection.commit()
        finally:
            connection.close()

    def record_snapshot(self, note_id: str, age_hours: int, metrics: dict[str, Any]) -> dict[str, Any]:
        raw_path = self.root / "feedback" / "raw" / f"{datetime.now().date().isoformat()}.jsonl"
        payload = {"note_id": note_id, "age_hours": age_hours, "metrics": metrics, "observed_at": utc_now()}
        append_jsonl(raw_path, [payload])
        connection = self.connect()
        try:
            connection.execute("""INSERT OR REPLACE INTO metric_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                note_id, payload["observed_at"], age_hours, metrics.get("views"), metrics.get("likes"), metrics.get("collects"),
                metrics.get("comments"), metrics.get("replies", 0), metrics.get("shares", 0), metrics.get("follows", 0),
                json.dumps(metrics.get("traffic", {}), ensure_ascii=False), json.dumps(metrics.get("audience", {}), ensure_ascii=False), str(raw_path),
            ))
            connection.commit()
        finally:
            connection.close()
        return self.metrics(note_id, age_hours)

    def import_creator_note(self, note: dict[str, Any], paper_id: str, time_slot: str, content_hash: str, age_hours: int = 168) -> dict[str, Any]:
        """Import one `opencli ... creator-notes -f json` row without using a third-party API."""
        note_id = str(note.get("id") or note.get("note_id") or note.get("noteId") or "")
        if not note_id:
            raise ValueError("creator note row does not include an id")
        self.register_post({
            "note_id": note_id, "paper_id": paper_id, "published_at": str(note.get("date") or note.get("published_at") or utc_now()),
            "time_slot": time_slot, "content_hash": content_hash, "topics": note.get("topics", []), "features": {"title": note.get("title", "")},
        })
        aliases = {"views": ("views", "view_count"), "likes": ("likes", "like_count"), "collects": ("collects", "collect_count", "favorites"), "comments": ("comments", "comment_count")}
        metrics = {target: next((note[key] for key in keys if key in note), 0) for target, keys in aliases.items()}
        return self.record_snapshot(note_id, age_hours, metrics)

    def write_decision(self, decision_id: str, target_type: str, target_key: str, previous_value: float, next_value: float, evidence: dict[str, Any], rollback_at: str | None = None) -> None:
        connection = self.connect()
        try:
            connection.execute("INSERT OR REPLACE INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                decision_id, utc_now(), target_type, target_key, previous_value, next_value, json.dumps(evidence, ensure_ascii=False), rollback_at,
            ))
            connection.commit()
        finally:
            connection.close()

    def metrics(self, note_id: str, age_hours: int = 168) -> dict[str, Any]:
        connection = self.connect()
        try:
            row = connection.execute("SELECT * FROM metric_snapshots WHERE note_id=? AND age_hours=?", (note_id, age_hours)).fetchone()
        finally:
            connection.close()
        if not row:
            return {"note_id": note_id, "available": False}
        views = row["views"]
        if views is None:
            return {"note_id": note_id, "available": True, "exposure_available": False}
        denominator = max(int(views), 100)
        likes, collects, comments, replies, shares, follows = (int(row[key] or 0) for key in ("likes", "collects", "comments", "replies", "shares", "follows"))
        return {
            "note_id": note_id, "available": True, "exposure_available": True,
            "er": (likes + collects + comments + shares) / denominator,
            "sr": collects / denominator, "flr": collects / max(likes, 1),
            "ddr": (comments + 0.5 * replies) / denominator, "fr": follows / denominator,
        }

    @staticmethod
    def group_adjustment(values: list[float], account_mean: float) -> float:
        if len(values) < 6:
            return 0.0
        posterior = (sum(values) + account_mean * 12) / (len(values) + 12)
        lift = posterior - account_mean
        return 0.05 if lift > 0.15 else -0.05 if lift < -0.15 else 0.0
