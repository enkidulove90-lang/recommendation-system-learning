"""Long-running, draft-only daily paper discovery runner.

This runner deliberately stops at a local qualification queue.  The current
project has no unattended verifier for official GitHub, MinerU, or source
figures, so creating a Xiaohongshu draft here would weaken the configured hard
gates.  A qualified workflow may consume this queue and invoke the one
supported ``save-xhs-draft`` entry point later.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

import yaml

from .common import write_json
from .daily_discovery import DailyDiscoveryRunner


def configured_interval_minutes(config_path: Path) -> int:
    """Read a human-friendly discovery cadence, defaulting to 18 hours."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    runner = dict(config.get("continuous_runner", {}))
    if runner.get("discovery_interval_minutes") is not None:
        return int(runner["discovery_interval_minutes"])
    return int(float(runner.get("discovery_interval_hours", 18)) * 60)


@dataclass(frozen=True)
class DailyRunResult:
    started_at: str
    state: str
    candidate_count: int
    queue_path: str
    discovery_manifest: str | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class DailyDraftRunner:
    """Poll new arXiv candidates and persist a reviewable, fail-closed queue."""

    def __init__(
        self,
        data_root: Path,
        config_path: Path,
        discovery_factory: Callable[[Path, Path], DailyDiscoveryRunner] = DailyDiscoveryRunner,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.data_root, self.config_path = data_root, config_path
        self.discovery_factory, self.sleep, self.now = discovery_factory, sleep, now

    def run_once(self) -> DailyRunResult:
        started = self.now().isoformat()
        queue_dir = self.data_root / "review_queue"
        stamp = self.now().strftime("%Y%m%dT%H%M%SZ")
        queue_path = queue_dir / f"paper_qualification_{stamp}.json"
        try:
            report = self.discovery_factory(self.data_root, self.config_path).run()
            candidate_path = Path(str(report["candidate_path"]))
            candidates = [json.loads(line) for line in candidate_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            queue = {
                "mode": "draft_only",
                "state": "awaiting_qualification",
                "created_at": started,
                "discovery_manifest": report["manifest_path"],
                "hard_gates_before_delivery": [
                    "verified venue or trusted preprint", "public PDF", "official GitHub",
                    "local MinerU parse", "at least four qualified figures", "real topic entities",
                    "same-editor PDF attachment",
                ],
                "candidates": candidates,
                "delivery": "disabled_until_every_hard_gate_is_verified",
            }
            write_json(queue_path, queue)
            return DailyRunResult(started, "awaiting_qualification", len(candidates), str(queue_path), str(report["manifest_path"]))
        except Exception as error:  # preserve the loop and a local diagnosis
            write_json(queue_path, {
                "mode": "draft_only", "state": "discovery_failed", "created_at": started,
                "error": f"{type(error).__name__}: {error}",
            })
            return DailyRunResult(started, "discovery_failed", 0, str(queue_path), error=f"{type(error).__name__}: {error}")

    def run_for(self, duration_hours: float = 24, interval_minutes: int = 180) -> list[DailyRunResult]:
        if duration_hours <= 0:
            raise ValueError("duration_hours must be positive")
        if interval_minutes <= 0:
            raise ValueError("interval_minutes must be positive")
        deadline = time.monotonic() + duration_hours * 3600
        results: list[DailyRunResult] = []
        while True:
            result = self.run_once()
            results.append(result)
            # A background runner otherwise has no visible progress until its
            # bounded duration ends.  Flush each heartbeat to its redirected
            # log so an operator can distinguish a live queue worker from a
            # process that never reached its first discovery cycle.
            print(json.dumps(result.as_dict(), ensure_ascii=False), flush=True)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return results
            self.sleep(min(interval_minutes * 60, remaining))
