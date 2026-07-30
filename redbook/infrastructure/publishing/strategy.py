"""Publishing time optimization — fixed → data-driven → event-triggered.

Phase 0 (Fixed Time):  Publish at predefined optimal slots. Accumulate data.
Phase 1 (Data-Driven): After ≥30 posts, switch to per-account best time.
Phase 2 (Hybrid):      Event-triggered for high-score papers + data-driven for rest.

Usage:
    strategy = HybridStrategy(db_path="data/feedback/posts.db")
    slot = strategy.next_slot()
    strategy.record_post(paper_id, posted_at, metrics)
"""

from __future__ import annotations

import json
import logging
import random
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ── Data Types ────────────────────────────────────────────


class StrategyPhase(str, Enum):
    FIXED = "fixed"
    DATA_DRIVEN = "data_driven"
    HYBRID = "hybrid"


@dataclass
class TimeSlot:
    """A publishable time window."""
    day_of_week: int          # 0=Mon, 6=Sun
    hour: int                 # 0-23
    minute: int = 0
    weight: float = 1.0       # higher = preferred
    label: str = ""

    @property
    def next_occurrence(self) -> datetime:
        """Return the next datetime this slot occurs."""
        now = datetime.now()
        target = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        days_ahead = self.day_of_week - now.weekday()
        if days_ahead < 0 or (days_ahead == 0 and target <= now):
            days_ahead += 7
        return target + timedelta(days=days_ahead)

    def as_dict(self) -> dict:
        return {
            "day_of_week": self.day_of_week,
            "hour": self.hour,
            "minute": self.minute,
            "weight": self.weight,
            "label": self.label,
        }


@dataclass
class PostMetrics:
    """Engagement metrics for a published post."""
    paper_id: str
    posted_at: str          # ISO 8601
    views: int = 0
    likes: int = 0
    collects: int = 0
    comments: int = 0
    new_followers: int = 0

    @property
    def collection_rate(self) -> float:
        return self.collects / max(self.views, 1)

    @property
    def engagement_rate(self) -> float:
        return (self.likes + self.collects + self.comments) / max(self.views, 1)

    @property
    def quality_score(self) -> float:
        """Composite quality: collection_rate weighted 0.6, engagement 0.4."""
        return self.collection_rate * 0.6 + self.engagement_rate * 0.4

    @property
    def hour(self) -> int:
        try:
            return datetime.fromisoformat(self.posted_at).hour
        except (ValueError, TypeError):
            return 0

    @property
    def weekday(self) -> int:
        try:
            return datetime.fromisoformat(self.posted_at).weekday()
        except (ValueError, TypeError):
            return 0


# ── Base Strategy ─────────────────────────────────────────


class PublishingStrategy(ABC):
    """Abstract publishing time strategy."""

    @abstractmethod
    def next_slot(self) -> TimeSlot:
        """Return the next recommended publish time."""
        ...

    @abstractmethod
    def phase(self) -> StrategyPhase:
        ...

    def record_post(self, paper_id: str, posted_at: str, metrics: PostMetrics | None = None) -> None:
        """Record a published post for future analysis. Default no-op."""
        pass

    def should_trigger(self, paper_score: float) -> bool:
        """Check if a paper should trigger immediate publish (event mode)."""
        return False


# ── Phase 0: Fixed Time ───────────────────────────────────


class FixedTimeStrategy(PublishingStrategy):
    """Publish at industry-optimal fixed times.

    Weekdays: 12:30 (lunch) and 21:00 (evening)
    Weekends: 10:30 (morning) and 16:00 (afternoon)
    """

    DEFAULT_SLOTS = [
        TimeSlot(0, 12, 30, 1.0, "Mon lunch"),
        TimeSlot(0, 21, 0, 1.0, "Mon evening"),
        TimeSlot(1, 12, 30, 1.0, "Tue lunch"),
        TimeSlot(1, 21, 0, 1.0, "Tue evening"),
        TimeSlot(2, 12, 30, 1.0, "Wed lunch"),
        TimeSlot(2, 21, 0, 1.0, "Wed evening"),
        TimeSlot(3, 12, 30, 1.0, "Thu lunch"),
        TimeSlot(3, 21, 0, 1.0, "Thu evening"),
        TimeSlot(4, 12, 30, 1.0, "Fri lunch"),
        TimeSlot(4, 21, 0, 1.0, "Fri evening"),
        TimeSlot(5, 10, 30, 0.8, "Sat morning"),
        TimeSlot(5, 16, 0, 0.8, "Sat afternoon"),
        TimeSlot(6, 10, 30, 0.8, "Sun morning"),
        TimeSlot(6, 16, 0, 0.8, "Sun afternoon"),
    ]

    def __init__(self, slots: list[TimeSlot] | None = None):
        self._slots = slots or self.DEFAULT_SLOTS

    def next_slot(self) -> TimeSlot:
        """Return the next fixed time slot."""
        now = datetime.now()
        # Filter to slots after now
        upcoming = []
        for slot in self._slots:
            next_time = slot.next_occurrence
            upcoming.append((next_time, slot))

        upcoming.sort(key=lambda x: x[0])
        _, slot = upcoming[0]
        return slot

    def phase(self) -> StrategyPhase:
        return StrategyPhase.FIXED


# ── Phase 1: Data-Driven ──────────────────────────────────


class DataDrivenStrategy(PublishingStrategy):
    """Analyze historical post data to find optimal publish times."""

    MIN_POSTS = 30  # posts needed before switching

    def __init__(self, db_path: str = "data/feedback/posts.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT NOT NULL,
                    posted_at TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    collects INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    new_followers INTEGER DEFAULT 0,
                    fetched_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hourly_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weekday INTEGER NOT NULL,
                    hour INTEGER NOT NULL,
                    post_count INTEGER DEFAULT 0,
                    avg_collection_rate REAL DEFAULT 0.0,
                    avg_engagement_rate REAL DEFAULT 0.0,
                    composite_score REAL DEFAULT 0.0,
                    updated_at TEXT DEFAULT (datetime('now')),
                    UNIQUE(weekday, hour)
                )
            """)
            conn.commit()

    @property
    def post_count(self) -> int:
        with sqlite3.connect(str(self._db_path)) as conn:
            row = conn.execute("SELECT COUNT(*) FROM posts").fetchone()
            return row[0] if row else 0

    def is_ready(self) -> bool:
        return self.post_count >= self.MIN_POSTS

    def record_post(self, paper_id: str, posted_at: str, metrics: PostMetrics | None = None) -> None:
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute(
                "INSERT INTO posts (paper_id, posted_at, views, likes, collects, comments, new_followers) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (paper_id, posted_at,
                 metrics.views if metrics else 0,
                 metrics.likes if metrics else 0,
                 metrics.collects if metrics else 0,
                 metrics.comments if metrics else 0,
                 metrics.new_followers if metrics else 0),
            )
            conn.commit()
        self._recompute_hourly_stats()

    def _recompute_hourly_stats(self):
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO hourly_stats (weekday, hour, post_count, avg_collection_rate, avg_engagement_rate, composite_score)
                SELECT
                    CAST(strftime('%w', posted_at) AS INTEGER) AS weekday,
                    CAST(strftime('%H', posted_at) AS INTEGER) AS hour,
                    COUNT(*) AS post_count,
                    AVG(CAST(collects AS REAL) / MAX(views, 1)) AS avg_collection_rate,
                    AVG(CAST(likes + collects + comments AS REAL) / MAX(views, 1)) AS avg_engagement_rate,
                    (AVG(CAST(collects AS REAL) / MAX(views, 1)) * 0.6 + AVG(CAST(likes + collects + comments AS REAL) / MAX(views, 1)) * 0.4) AS composite_score
                FROM posts
                WHERE views > 0
                GROUP BY weekday, hour
            """)
            conn.commit()

    def _load_slots(self) -> list[TimeSlot]:
        slots = []
        with sqlite3.connect(str(self._db_path)) as conn:
            rows = conn.execute(
                "SELECT weekday, hour, post_count, composite_score FROM hourly_stats ORDER BY composite_score DESC"
            ).fetchall()

        if not rows:
            # Fallback to fixed
            return FixedTimeStrategy.DEFAULT_SLOTS

        for weekday, hour, count, score in rows[:20]:
            if count >= 1:
                slots.append(TimeSlot(
                    day_of_week=weekday,
                    hour=hour,
                    weight=round(score, 4) if score else 0.01,
                    label=f"w{weekday}h{hour}(n={count})",
                ))
        return slots or FixedTimeStrategy.DEFAULT_SLOTS

    def next_slot(self) -> TimeSlot:
        slots = self._load_slots()
        # Weighted random selection among top slots
        weights = [s.weight for s in slots]
        total = sum(weights)
        if total <= 0:
            return slots[0]
        # Roulette-wheel selection
        r = random.random() * total
        cumulative = 0.0
        for slot in slots:
            cumulative += slot.weight
            if r <= cumulative:
                return slot
        return slots[0]

    def phase(self) -> StrategyPhase:
        return StrategyPhase.DATA_DRIVEN


# ── Phase 2: Hybrid (Event + Data-Driven) ─────────────────


class EventTriggerStrategy(PublishingStrategy):
    """Event trigger for high-score papers + data-driven for the rest."""

    EVENT_THRESHOLD = 0.75  # score ≥0.75 triggers immediate publish

    def __init__(self, db_path: str = "data/feedback/posts.db"):
        self._data_driven = DataDrivenStrategy(db_path)

    def next_slot(self) -> TimeSlot:
        return self._data_driven.next_slot()

    def should_trigger(self, paper_score: float) -> bool:
        return paper_score >= self.EVENT_THRESHOLD

    def record_post(self, paper_id: str, posted_at: str, metrics: PostMetrics | None = None) -> None:
        self._data_driven.record_post(paper_id, posted_at, metrics)

    def phase(self) -> StrategyPhase:
        return StrategyPhase.HYBRID

    @property
    def post_count(self) -> int:
        return self._data_driven.post_count


# ── Factory ───────────────────────────────────────────────


def create_strategy(db_path: str = "data/feedback/posts.db") -> PublishingStrategy:
    """Auto-select the best strategy based on accumulated data."""
    ds = DataDrivenStrategy(db_path)
    if ds.is_ready():
        logger.info("Phase 2: Hybrid (data-driven + event trigger), %d posts", ds.post_count)
        return EventTriggerStrategy(db_path)
    else:
        logger.info("Phase 0: Fixed time, %d posts (need %d)", ds.post_count, DataDrivenStrategy.MIN_POSTS)
        return FixedTimeStrategy()
