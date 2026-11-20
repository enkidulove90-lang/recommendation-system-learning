"""Task 1 worker acceptance: crash resume, artifact reuse, drain, cancellation."""
from __future__ import annotations

from redbook.infrastructure.delivery_errors import E_SAVE_UNVERIFIED, OrchestrationError
from redbook.orchestration import models
from redbook.orchestration.artifacts import ArtifactStore
from redbook.orchestration.queue import SqliteQueueBackend
from redbook.orchestration.registry import SqliteDeliveryRegistry
from redbook.orchestration.worker import NoopHandler, Worker


def make_worker(tmp_path, **kwargs) -> tuple[Worker, SqliteQueueBackend]:
    backend = SqliteQueueBackend(tmp_path / "state" / "orchestration.sqlite",
                                 backoff_seconds=0.0)
    return Worker(backend, **kwargs), backend


def test_crash_resume_does_not_repeat_platform_save(tmp_path):  # TC2
    worker, backend = make_worker(tmp_path, heartbeat_interval_seconds=1000)
    registry = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite")
    platform_save_calls = []

    def flaky_handler(job, heartbeat):
        heartbeat()
        existing = registry.find_reusable(
            platform="xhs", account="default", staged_id="deadbeef" * 8,
        )
        if existing is None:
            platform_save_calls.append(job.attempt)
            registry.begin_save(run_id=job.job_id, content_hash="deadbeef" * 8,
                                platform="xhs", account="default",
                                staged_id="deadbeef" * 8)
            registry.mark_saved_unverified(platform="xhs", account="default",
                                           staged_id="deadbeef" * 8,
                                           draft_id="s:crash-mid-save")
            # simulate the worker dying right after the platform save
            raise OrchestrationError("worker crashed after save", E_SAVE_UNVERIFIED)
        registry.mark_verified(platform="xhs", account="default",
                               staged_id="deadbeef" * 8)
        return models.VERIFIED

    backend.enqueue("deliver", "note:crash", run_id="run-crash")
    first = worker.run_once(flaky_handler)
    assert first.state == models.FAILED_RETRYABLE
    resumed = worker.run_once(flaky_handler)
    assert resumed.state == models.VERIFIED
    assert len(platform_save_calls) == 1  # the platform save happened exactly once
    delivery = registry.find_delivery(platform="xhs", account="default",
                                      staged_id="deadbeef" * 8)
    assert delivery["state"] == models.VERIFIED and delivery["attempt"] == 1


def test_stage_artifact_reuse_calls_parser_once(tmp_path):  # TC6
    store = ArtifactStore(tmp_path / "artifacts.jsonl")
    parser_calls = []

    def fake_parse(pdf_path):
        parser_calls.append(pdf_path)
        return {"markdown_path": str(tmp_path / "out.md"), "json_path": ""}

    input_hash = "a" * 64
    hit = store.find("parse", input_hash)
    if hit is None:
        result = fake_parse(f"{tmp_path}/paper.pdf")
        store.register("parse", input_hash,
                       outputs={"markdown_path": result["markdown_path"]})
    hit = store.find("parse", input_hash)
    if hit is None:
        fake_parse(f"{tmp_path}/paper.pdf")

    assert len(parser_calls) == 1
    assert hit["outputs"]["markdown_path"].endswith("out.md")


def test_drain_processes_every_queued_job(tmp_path):  # TC7 (worker half)
    worker, backend = make_worker(tmp_path)
    for index in range(3):
        backend.enqueue("intake", f"note:{index}")
    receipts = worker.drain(NoopHandler())
    assert [receipt.state for receipt in receipts] == [models.VERIFIED] * 3
    assert backend.depth("intake") == 0
    assert backend.claim("w2") is None  # queue fully drained


def test_worker_heartbeat_extends_lease(tmp_path):
    worker, backend = make_worker(tmp_path, heartbeat_interval_seconds=1000)
    job = backend.enqueue("intake", "note:hb")
    claimed = backend.claim(worker.worker_id, lease_ttl_seconds=1.0)
    assert claimed is not None
    assert backend.heartbeat(job.job_id, worker.worker_id, lease_ttl_seconds=999.0)
    job_after = backend.get_job(job.job_id)
    assert "999" in job_after.lease_expires_at or job_after.lease_expires_at > claimed.lease_expires_at
