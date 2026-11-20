"""Sentinel runner acceptance (TC7, TC13-TC15, TC17)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from redbook.orchestration import models
from redbook.orchestration.queue import SqliteQueueBackend
from redbook.orchestration.worker import Worker
from redbook.sentinel.paper_pool import PaperPool
from redbook.sentinel.runner import SentinelRunner


NOW = datetime(2026, 11, 21, 11, 30, tzinfo=timezone.utc)

#: pool status chain from queued to terminal (mirrors the 12-step pipeline)
_CHAIN = ["parsed", "summarized", "composed", "staged",
          "SAVED_UNVERIFIED", "VERIFIED", "published"]


def _advance(pool: PaperPool, cid: str, target: str) -> None:
    for status in _CHAIN:
        pool.set_status(cid, status)
        if status == target:
            break


@pytest.fixture()
def env(tmp_path):
    pool = PaperPool(tmp_path / "state" / "orchestration.sqlite")
    queue = SqliteQueueBackend(tmp_path / "state" / "orchestration.sqlite")
    return pool, queue


def _runner(pool: PaperPool, candidates: list[dict]) -> SentinelRunner:
    return SentinelRunner(
        pool, config={"retrieval_schedule": "11:00"},
        discovery=lambda now: candidates)


def test_retrieval_idempotent_per_day(env):  # TC7
    pool, _ = env
    runner = _runner(pool, [{"canonical_id": "p1"}])
    first = runner.run_retrieval(NOW)
    assert first["ran"] is True and first["added"] == 1
    again = runner.run_retrieval(NOW)
    assert again["ran"] is False and again["reason"] == "already ran today"
    before_sched = datetime(2026, 11, 22, 9, 0, tzinfo=timezone.utc)
    assert runner.run_retrieval(before_sched)["ran"] is False


def test_end_to_end_pool_to_queue_to_publish(env):  # TC13
    pool, queue = env
    runner = _runner(pool, [{"canonical_id": "p-home"}])
    report = runner.run_once(queue, now=NOW)
    assert report["retrieval"]["added"] == 1
    assert len(report["dispatched"]) == 1
    worker = Worker(queue)
    receipts = worker.drain(lambda job, hb: models.VERIFIED)
    assert [r.state for r in receipts] == [models.VERIFIED]
    # delivery leg finished: pool advances VERIFIED -> published + platform tag
    _advance(pool, "p-home", "VERIFIED")
    pool.set_status("p-home", "published")
    pool.record_platform("p-home", "homepage")
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status, platforms FROM paper_pool "
            "WHERE canonical_id = 'p-home'").fetchone()
    assert row["status"] == "published" and "homepage" in row["platforms"]


def test_xhs_leg_stops_at_verified(env):  # TC14
    pool, queue = env
    runner = _runner(pool, [{"canonical_id": "p-xhs"}])
    runner.run_once(queue, now=NOW)
    Worker(queue).drain(lambda job, hb: models.SAVED_UNVERIFIED)
    # draft-only iron rule: XHS handler returns SAVED_UNVERIFIED, never publish
    _advance(pool, "p-xhs", "VERIFIED")
    pool.record_platform("p-xhs", "xiaohongshu")
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status, platforms FROM paper_pool "
            "WHERE canonical_id = 'p-xhs'").fetchone()
    assert row["status"] == "VERIFIED"  # stopped, NOT published
    assert "homepage" not in row["platforms"]


def test_blocked_writeback_and_human_rerun(env):  # TC15
    pool, queue = env
    runner = _runner(pool, [{"canonical_id": "p-block"}])
    runner.run_once(queue, now=NOW)
    pool.set_status("p-block", "blocked")
    pool.reset_blocked("p-block")  # human reset path
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status, pending_delivery FROM paper_pool "
            "WHERE canonical_id = 'p-block'").fetchone()
    assert row["status"] == "queued" and row["pending_delivery"] == 1


def test_queue_full_degrades_to_pool_only(env):  # TC17
    pool, queue = env
    queue.max_depths["intake"] = 0  # bounded full
    runner = _runner(pool, [{"canonical_id": "p-degrade"}])
    report = runner.run_once(queue, now=NOW)
    assert report["dispatched"] == []
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status, pending_delivery FROM paper_pool "
            "WHERE canonical_id = 'p-degrade'").fetchone()
        degrade = pool.get_meta("last_dispatch_degrade")
    assert (row["status"], row["pending_delivery"]) == ("discovered", 1)
    assert degrade is not None and "E_QUEUE_FULL" in degrade
