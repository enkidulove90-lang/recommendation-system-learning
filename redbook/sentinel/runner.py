"""Sentinel runner: probe sweep + 11:00 retrieval + FIFO dispatch.

Three entry points, all idempotent and scheduler-friendly:
- ``probe_all``      : sweep all dependencies, log JSONL (rate-limited).
- ``run_retrieval``  : once per day after the configured time (default 11:00),
  filtered candidates go into the pool (TC7/TC8/TC9).
- ``dispatch_pending``: FIFO claim from the pool into the orchestration queue;
  when the queue is bounded-full the sentinel degrades to pool-only mode and
  records the reason (TC17) instead of crashing the sweep.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from redbook.orchestration.queue import QueueBackend, QueueFullError
from .paper_pool import PaperPool, load_exclusions
from .probes import Probe, ProbeResult, run_sweep, write_probe_log


class SentinelRunner:
    def __init__(self, pool: PaperPool, *, config: dict[str, Any] | None = None,
                 probes: list[Probe] | None = None,
                 log_dir: Path | None = None,
                 discovery: Callable[[datetime], list[dict[str, Any]]] | None = None,
                 platform: str = "homepage") -> None:
        config = config or {}
        self.pool = pool
        self.probes = probes or []
        self.log_dir = Path(log_dir or (config.get("log_dir") or "data/logs"))
        self.probe_min_interval_seconds = float(config.get("probe_min_interval_seconds", 900))
        self.retrieval_time = str(config.get("retrieval_schedule", "11:00"))
        self.discovery = discovery  # injectable: returns filtered candidate dicts
        self.platform = platform  # this runner's own delivery leg

    # -- probes ---------------------------------------------------------------
    def probe_all(self, now: datetime | None = None) -> list[ProbeResult]:
        now = now or datetime.now(timezone.utc)
        last_key = "last_probe_at"
        last = self.pool.get_meta(last_key)
        if last:
            from datetime import datetime as dt
            elapsed = (now - dt.fromisoformat(last)).total_seconds()
            if elapsed < self.probe_min_interval_seconds:
                return []
        results = run_sweep(self.probes, now)
        write_probe_log(self.log_dir, results, now)
        self.pool.set_meta(last_key, now.isoformat())
        return results

    # -- retrieval ------------------------------------------------------------
    def run_retrieval(self, now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        day = now.date().isoformat()
        scheduled = self._retrieval_moment(now)
        if now < scheduled:
            return {"ran": False, "reason": "before schedule",
                    "schedule": self.retrieval_time}
        if self.pool.get_meta("last_retrieval_date") == day:
            return {"ran": False, "reason": "already ran today", "date": day}
        exclusions = set()
        excl_path = self.pool.path.parent.parent / "workflow_state" / "sentinel" \
            / "exclusions.json"
        exclusions = load_exclusions(excl_path)
        candidates = self.discovery(now) if self.discovery else []
        added, skipped = [], []
        for candidate in candidates:
            result = self.pool.add_candidate(
                canonical_id=candidate["canonical_id"],
                arxiv_id=candidate.get("arxiv_id", ""),
                doi=candidate.get("doi", ""),
                title=candidate.get("title", ""),
                exclusions=exclusions)
            (added if result["added"] else skipped).append(
                {**result, "reason": result["reason"] or "hard-gate passed"})
        self.pool.set_meta("last_retrieval_date", day)
        return {"ran": True, "date": day, "added": len(added),
                "skipped": skipped, "added_ids": [a["canonical_id"] for a in added]}

    def _retrieval_moment(self, now: datetime) -> datetime:
        hour, minute = (int(part) for part in self.retrieval_time.split(":"))
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # -- dispatch -------------------------------------------------------------
    def dispatch_pending(self, queue: QueueBackend, *, limit: int = 3) -> list[dict[str, Any]]:
        dispatched = []
        while True:
            entries = self.pool.take_pending(limit=1)
            if not entries:
                break
            entry = entries[0]
            try:
                job = queue.enqueue(
                    "intake", f"note:{entry.canonical_id}",
                    run_id=f"sentinel:{entry.canonical_id}",
                    enqueue_step="sentinel_dispatch")
            except QueueFullError as error:
                # degrade to pool-only: re-enter FIFO, pending stays set (TC17)
                self.pool.reset_to_discovered(entry.canonical_id)
                self.pool.set_meta("last_dispatch_degrade",
                                   json.dumps({"canonical_id": entry.canonical_id,
                                               "code": error.code}))
                break
            dispatched.append({"canonical_id": entry.canonical_id,
                               "job_id": job.job_id})
        return dispatched

    def run_once(self, queue: QueueBackend | None = None,
                 now: datetime | None = None, *,
                 dispatch: bool = True) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        report: dict[str, Any] = {
            "probes": [r.to_dict() for r in self.probe_all(now)],
            "retrieval": self.run_retrieval(now),
        }
        if dispatch and queue is not None:
            report["dispatched"] = self.dispatch_pending(queue)
        return report
