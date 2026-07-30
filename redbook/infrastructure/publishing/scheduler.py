"""Publishing scheduler — ties strategy to actual timing decisions."""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from .strategy import (
    DataDrivenStrategy,
    FixedTimeStrategy,
    PostMetrics,
    PublishingStrategy,
    StrategyPhase,
    TimeSlot,
    create_strategy,
)

logger = logging.getLogger(__name__)


class Scheduler:
    """Manages when to publish papers based on the active strategy.

    Usage:
        sched = Scheduler()
        sched.load()

        # Check if now is a good time (fixed/data-driven)
        if sched.should_publish_now():
            publish()

        # After publishing, record metrics
        sched.record(paper_id, datetime.now().isoformat())

        # Check if paper triggers immediate publish (event mode)
        if sched.should_trigger_immediately(paper_score=0.82):
            publish()
    """

    def __init__(self, db_path: str = "data/feedback/posts.db",
                 config_path: str = "data/feedback/scheduler.json"):
        self._db_path = Path(db_path)
        self._config_path = Path(config_path)
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._strategy: PublishingStrategy = create_strategy(str(db_path))
        self._last_published: dict[str, str] = {}  # date → time

    def load(self):
        """Load strategy state and select appropriate phase."""
        self._strategy = create_strategy(str(self._db_path))

        # Load last published times
        if self._config_path.exists():
            with open(self._config_path) as f:
                data = json.load(f)
            self._last_published = data.get("last_published", {})

        logger.info("Scheduler loaded. Phase: %s, posts: %d",
                      self._strategy.phase().value, self.post_count)

    def save(self):
        """Persist scheduler state."""
        with open(self._config_path, "w") as f:
            json.dump({
                "last_published": self._last_published,
                "phase": self._strategy.phase().value,
            }, f, indent=2)

    @property
    def post_count(self) -> int:
        if hasattr(self._strategy, "post_count"):
            return getattr(self._strategy, "post_count")  # type: ignore[union-attr]
        return 0

    @property
    def phase(self) -> StrategyPhase:
        return self._strategy.phase()

    @property
    def phase_description(self) -> str:
        descriptions = {
            StrategyPhase.FIXED: f"Fixed time (need {getattr(DataDrivenStrategy, 'MIN_POSTS', 30)} posts for data-driven)",
            StrategyPhase.DATA_DRIVEN: "Data-driven (historical engagement optimized)",
            StrategyPhase.HYBRID: "Hybrid (event trigger + data-driven)",
        }
        return descriptions.get(self.phase, "Unknown")

    def next_slot(self) -> TimeSlot:
        """Return the next recommended publish time slot."""
        return self._strategy.next_slot()

    def should_publish_now(self) -> bool:
        """Check if current time is within an optimal window (±30 min of a slot)."""
        now = datetime.now()
        slot = self._strategy.next_slot()
        next_time = slot.next_occurrence

        # If we're within 30min of the next slot, publish now
        delta = abs((now - next_time).total_seconds())
        if delta <= 1800:  # 30 minutes
            # Check we haven't already published today
            today = now.strftime("%Y-%m-%d")
            if today not in self._last_published:
                return True

        return False

    def should_trigger_immediately(self, paper_score: float) -> bool:
        """Check if a high-score paper should be published immediately."""
        return self._strategy.should_trigger(paper_score)

    def record(self, paper_id: str, posted_at: str, metrics: PostMetrics | None = None):
        """Record a published post."""
        self._strategy.record_post(paper_id, posted_at, metrics)
        today = datetime.fromisoformat(posted_at).strftime("%Y-%m-%d") if posted_at else datetime.now().strftime("%Y-%m-%d")
        self._last_published[today] = posted_at
        self.save()

    def status(self) -> dict:
        """Return human-readable status."""
        slot = self.next_slot()
        next_time = slot.next_occurrence
        return {
            "phase": self.phase.value,
            "phase_desc": self.phase_description,
            "total_posts": self.post_count,
            "next_publish_slot": slot.label,
            "next_publish_time": next_time.isoformat(),
            "minutes_until_next": round((next_time - datetime.now()).total_seconds() / 60, 1),
            "today_published": datetime.now().strftime("%Y-%m-%d") in self._last_published,
        }


