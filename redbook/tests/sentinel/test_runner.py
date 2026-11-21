"""Sentinel runner acceptance (TC7, TC13-TC15, TC17)."""
from __future__ import annotations

from datetime import datetime, timezone
import json

import pytest

from redbook.orchestration import models
from redbook.orchestration.queue import SqliteQueueBackend
from redbook.orchestration.worker import Worker
from redbook.sentinel.delivery import PoolDeliveryHandler
from redbook.sentinel.paper_pool import PaperPool
from redbook.sentinel.runner import DailyDiscoveryAdapter, SentinelRunner


NOW = datetime(2026, 11, 21, 11, 30, tzinfo=timezone.utc)


@pytest.fixture()
def env(tmp_path):
    pool = PaperPool(tmp_path / "state" / "orchestration.sqlite")
    queue = SqliteQueueBackend(tmp_path / "state" / "orchestration.sqlite")
    return pool, queue


def _runner(pool: PaperPool, candidates: list[dict], *, platform: str = "homepage") -> SentinelRunner:
    return SentinelRunner(
        pool, config={"retrieval_schedule": "11:00"},
        discovery=lambda now: candidates, platform=platform)


def test_retrieval_idempotent_per_day(env):  # TC7
    pool, _ = env
    runner = _runner(pool, [{"canonical_id": "p1"}])
    first = runner.run_retrieval(NOW)
    assert first["ran"] is True and first["added"] == 1
    again = runner.run_retrieval(NOW)
    assert again["ran"] is False and again["reason"] == "already ran today"
    before_sched = datetime(2026, 11, 22, 9, 0, tzinfo=timezone.utc)
    assert runner.run_retrieval(before_sched)["ran"] is False


def test_retrieval_uses_configured_hexo_exclusion_list(env, tmp_path):  # TC9
    pool, _ = env
    exclusions = tmp_path / "paper_exclusions.json"
    exclusions.write_text(json.dumps(["2601.00001"]), encoding="utf-8")
    runner = SentinelRunner(
        pool,
        config={"retrieval_schedule": "11:00", "exclusions_path": str(exclusions)},
        discovery=lambda now: [{"canonical_id": "arxiv:2601.00001", "arxiv_id": "2601.00001"}],
    )

    result = runner.run_retrieval(NOW)

    assert result["added"] == 0
    assert result["skipped"] == [{
        "added": False, "reason": "excluded", "canonical_id": "arxiv:2601.00001",
    }]


def test_daily_discovery_adapter_translates_replayable_jsonl_to_pool_candidates(tmp_path):
    candidate_path = tmp_path / "candidates.jsonl"
    candidate_path.write_text(json.dumps({
        "record_id": "arxiv:2601.00001",
        "identifiers": {"arxiv": "2601.00001", "doi": "10.1/example"},
        "title": "A qualified paper",
    }) + "\n", encoding="utf-8")

    class Discovery:
        def __init__(self, data_root, config_path) -> None:
            self.data_root, self.config_path = data_root, config_path

        def run(self):
            return {"candidate_path": str(candidate_path)}

    result = DailyDiscoveryAdapter(
        tmp_path / "data", tmp_path / "daily.yaml", runner_factory=Discovery,
    )(NOW)

    assert result == [{
        "canonical_id": "arxiv:2601.00001", "arxiv_id": "2601.00001",
        "doi": "10.1/example", "title": "A qualified paper",
    }]


def test_platform_runners_enqueue_distinct_platform_addressed_jobs(env):
    pool, queue = env
    pool.add_candidate(canonical_id="arxiv:2601.00005", arxiv_id="2601.00005")

    homepage = _runner(pool, [], platform="homepage").dispatch_pending(queue)
    xiaohongshu = _runner(pool, [], platform="xiaohongshu").dispatch_pending(queue)

    assert len(homepage) == len(xiaohongshu) == 1
    first = queue.get_job(homepage[0]["job_id"])
    second = queue.get_job(xiaohongshu[0]["job_id"])
    assert {first.payload_ref, second.payload_ref} == {
        "sentinel:homepage:arxiv:2601.00005",
        "sentinel:xiaohongshu:arxiv:2601.00005",
    }


def test_platform_dispatch_respects_requested_batch_limit(env):
    pool, queue = env
    pool.add_candidate(canonical_id="arxiv:2601.00006", arxiv_id="2601.00006")
    pool.add_candidate(canonical_id="arxiv:2601.00007", arxiv_id="2601.00007")

    dispatched = _runner(pool, [], platform="homepage").dispatch_pending(queue, limit=1)

    assert len(dispatched) == 1
    queued = [
        pool.platform_delivery_status(canonical_id, "homepage")
        for canonical_id in ("arxiv:2601.00006", "arxiv:2601.00007")
    ]
    assert sorted(queued) == ["discovered", "queued"]


def test_end_to_end_pool_to_queue_to_publish(env):  # TC13
    pool, queue = env
    runner = _runner(pool, [{"canonical_id": "p-home"}])
    report = runner.run_once(queue, now=NOW)
    assert report["retrieval"]["added"] == 1
    assert len(report["dispatched"]) == 1
    class Homepage:
        def __init__(self) -> None:
            self.published: list[str] = []

        def publish(self, canonical_id, heartbeat):
            heartbeat()
            self.published.append(canonical_id)
            return models.PUBLISHED

        def save_draft(self, canonical_id, heartbeat):
            raise AssertionError("homepage delivery must use publish")

    homepage = Homepage()
    receipts = Worker(queue).drain(PoolDeliveryHandler(pool, "homepage", homepage))
    assert [r.state for r in receipts] == [models.PUBLISHED]
    assert homepage.published == ["p-home"]
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status, platforms FROM paper_pool "
            "WHERE canonical_id = 'p-home'").fetchone()
    assert row["status"] == "discovered" and "homepage" in row["platforms"]
    assert pool.platform_delivery_status("p-home", "homepage") == "published"


def test_xhs_leg_stops_at_verified(env):  # TC14
    pool, queue = env
    runner = _runner(pool, [{"canonical_id": "p-xhs"}], platform="xiaohongshu")
    runner.run_once(queue, now=NOW)
    class Xhs:
        def save_draft(self, canonical_id, heartbeat):
            heartbeat()
            return models.VERIFIED

        def publish(self, canonical_id, heartbeat):
            raise AssertionError("XHS publish must never be called")

    receipts = Worker(queue).drain(PoolDeliveryHandler(pool, "xiaohongshu", Xhs()))
    assert [r.state for r in receipts] == [models.VERIFIED]
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT status, platforms FROM paper_pool "
            "WHERE canonical_id = 'p-xhs'").fetchone()
    assert row["status"] == "discovered"  # platform progress is independent
    assert "homepage" not in row["platforms"]
    assert pool.platform_delivery_status("p-xhs", "xiaohongshu") == "VERIFIED"


def test_blocked_writeback_and_human_rerun(env):  # TC15
    pool, queue = env
    runner = _runner(pool, [{"canonical_id": "p-block"}])
    runner.run_once(queue, now=NOW)

    class FailedHomepage:
        def publish(self, canonical_id, heartbeat):
            raise RuntimeError("delivery unavailable")

        def save_draft(self, canonical_id, heartbeat):
            raise AssertionError("homepage delivery must use publish")

    receipts = Worker(queue).drain(PoolDeliveryHandler(pool, "homepage", FailedHomepage()))
    assert [receipt.state for receipt in receipts] == [models.FAILED_TERMINAL]
    pool.reset_platform_blocked("p-block", "homepage")  # human reset path
    assert pool.platform_delivery_status("p-block", "homepage") == "queued"


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
