"""Task 1 queue acceptance: lifecycle, exclusion, takeover, cancel, backpressure."""
from __future__ import annotations

import threading

import pytest

from redbook.infrastructure.delivery_errors import (
    E_QUEUE_FULL, E_SAVE_UNVERIFIED, E_VERIFY_MISMATCH, OrchestrationError,
)
from redbook.orchestration import models
from redbook.orchestration.queue import QueueFullError, SqliteQueueBackend


@pytest.fixture()
def backend(tmp_path) -> SqliteQueueBackend:
    return SqliteQueueBackend(tmp_path / "state" / "orchestration.sqlite",
                              backoff_seconds=0.0)


def test_full_lifecycle_events_are_seq_monotonic(backend):  # TC1
    job = backend.enqueue("intake", "note:2611.17921")
    claimed = backend.claim("w1", lease_ttl_seconds=60)
    assert claimed is not None and claimed.job_id == job.job_id
    assert claimed.state == models.RUNNING and claimed.attempt == 1
    assert backend.heartbeat(job.job_id, "w1", lease_ttl_seconds=60)
    receipt = backend.complete(job.job_id, "w1", models.VERIFIED)
    assert receipt.state == models.VERIFIED
    events = backend.events(job.job_id)
    seqs = [event["seq"] for event in events]
    assert seqs == sorted(seqs) and len(seqs) == len(set(seqs))
    assert [event["step"] for event in events] == ["enqueue", "claim", "complete"]


def test_single_job_claimed_by_exactly_one_worker(backend):  # TC3
    backend.enqueue("intake", "note:a")
    first = backend.claim("w1")
    second = backend.claim("w2")
    assert first is not None and second is None


def test_claim_is_mutually_exclusive_under_concurrency(backend):  # TC3 concurrent
    for index in range(3):
        backend.enqueue("intake", f"note:{index}")
    barrier = threading.Barrier(4)
    winners: list[str] = []

    def try_claim(worker_id: str) -> None:
        barrier.wait()
        job = backend.claim(worker_id)
        if job is not None:
            winners.append(job.job_id)

    threads = [threading.Thread(target=try_claim, args=(f"w{index}",)) for index in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(winners) == 3  # exactly the three jobs, no double claim
    assert len(set(winners)) == 3  # and each job claimed by a distinct worker


def test_expired_lease_is_taken_over_by_second_worker(backend):  # TC4
    job = backend.enqueue("intake", "note:zombie")
    first = backend.claim("w1", lease_ttl_seconds=0.0)
    assert first is not None
    takeover = backend.claim("w2", lease_ttl_seconds=60.0)
    assert takeover is not None and takeover.job_id == job.job_id
    assert takeover.lease_owner == "w2"
    assert any(event["step"] == "lease_expired" for event in backend.events(job.job_id))


def test_cancel_before_claim_marks_job_cancelled(backend):  # TC5
    job = backend.enqueue("intake", "note:cancel")
    assert backend.cancel(job.job_id)
    assert backend.claim("w1") is None
    assert backend.get_job(job.job_id).state == models.CANCELLED


def test_cancel_requested_during_running_completes_as_cancelled(backend):  # TC5 mid-run
    from redbook.orchestration.worker import Worker

    def handler(job, heartbeat):
        backend.cancel(job.job_id)
        return models.VERIFIED  # worker must override with CANCELLED

    backend.enqueue("intake", "note:midcancel")
    worker = Worker(backend, heartbeat_interval_seconds=1000)
    receipt = worker.run_once(handler)
    assert receipt.state == models.CANCELLED


def test_retryable_failure_requeues_after_backoff(backend):  # disposition policy
    job = backend.enqueue("intake", "note:retry")
    backend.claim("w1")
    receipt = backend.fail(job.job_id, "w1", OrchestrationError("save failed", E_SAVE_UNVERIFIED))
    assert receipt.state == models.FAILED_RETRYABLE and receipt.retryable
    retried = backend.claim("w2", lease_ttl_seconds=60)
    assert retried is not None and retried.job_id == job.job_id and retried.attempt == 2


def test_non_retryable_failure_is_terminal(backend):
    job = backend.enqueue("intake", "note:terminal")
    backend.claim("w1")
    receipt = backend.fail(job.job_id, "w1", OrchestrationError("mismatch", E_VERIFY_MISMATCH))
    assert receipt.state == models.FAILED_TERMINAL and not receipt.retryable
    assert backend.claim("w2") is None


def test_bounded_queue_rejects_with_queue_full(backend):  # TC8
    backend.max_depths["intake"] = 1
    backend.enqueue("intake", "note:first")
    with pytest.raises(QueueFullError) as error:
        backend.enqueue("intake", "note:second")
    assert error.value.code == E_QUEUE_FULL


def test_requeue_is_allowed_from_human_reset_states(backend):
    job = backend.enqueue("intake", "note:manual")
    backend.claim("w1")
    backend.fail(job.job_id, "w1", OrchestrationError("unknown", "E_UNKNOWN_MANUAL"))
    assert backend.get_job(job.job_id).state == models.FAILED_TERMINAL
    assert backend.requeue(job.job_id)
    assert backend.get_job(job.job_id).state == models.QUEUED
