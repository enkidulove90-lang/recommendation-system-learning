"""Chapter 3: deterministic exploration, UCB time selection, and event-trigger gates."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import random
from typing import Any


DEFAULT_SLOTS = ("08:15", "12:20", "20:35")


@dataclass(frozen=True)
class ScheduleDecision:
    slot: str
    strategy: str
    reason: str
    event_triggered: bool = False


class PublishScheduler:
    def __init__(self, slots: tuple[str, ...] = DEFAULT_SLOTS, min_total_posts: int = 28, min_posts_per_slot: int = 7, exploration_rate: float = 0.30, seed: int = 7) -> None:
        self.slots = slots
        self.min_total_posts = min_total_posts
        self.min_posts_per_slot = min_posts_per_slot
        self.exploration_rate = exploration_rate
        self.random = random.Random(seed)

    def choose(self, observations: list[dict[str, Any]], now: datetime, event: dict[str, Any] | None = None) -> ScheduleDecision:
        today = now.date().isoformat()
        today_posts = [row for row in observations if str(row.get("published_at", "")).startswith(today)]
        if self._event_allowed(today_posts, now, event):
            return ScheduleDecision(slot=now.strftime("%H:%M"), strategy="event_trigger", reason="fresh verified high-value paper", event_triggered=True)
        counts = {slot: sum(1 for row in observations if row.get("time_slot") == slot and row.get("qs7") is not None) for slot in self.slots}
        if len(observations) < self.min_total_posts or min(counts.values()) < self.min_posts_per_slot:
            slot = min(self.slots, key=lambda key: (counts[key], self.slots.index(key)))
            return ScheduleDecision(slot=slot, strategy="balanced_explore", reason=f"insufficient observations: {counts}")
        if self.random.random() < self.exploration_rate:
            slot = min(self.slots, key=lambda key: counts[key])
            return ScheduleDecision(slot=slot, strategy="ucb_explore", reason="mandatory exploration")
        scores = {slot: self._ucb([float(row["qs7"]) for row in observations if row.get("time_slot") == slot and row.get("qs7") is not None], len(observations)) for slot in self.slots}
        slot = max(scores, key=scores.get)
        return ScheduleDecision(slot=slot, strategy="ucb_exploit", reason=f"ucb={scores[slot]:.3f}")

    def _event_allowed(self, today_posts: list[dict[str, Any]], now: datetime, event: dict[str, Any] | None) -> bool:
        if not event or len(today_posts) >= 2:
            return False
        discovered_at = event.get("first_seen_at")
        if not discovered_at or float(event.get("quality_score", 0.0)) < 0.85 or not event.get("verified", False):
            return False
        try:
            fresh = now - datetime.fromisoformat(str(discovered_at).replace("Z", "+00:00")) <= timedelta(hours=24)
        except ValueError:
            return False
        if not fresh:
            return False
        for row in today_posts:
            try:
                published = datetime.fromisoformat(str(row["published_at"]).replace("Z", "+00:00"))
                if abs(now - published) < timedelta(hours=6):
                    return False
            except (KeyError, ValueError):
                continue
        return True

    @staticmethod
    def _ucb(values: list[float], total: int) -> float:
        if not values:
            return float("inf")
        mean = sum(values) / len(values)
        uncertainty = math.sqrt(math.log(max(total, 2)) / len(values))
        return mean + 0.20 * uncertainty
