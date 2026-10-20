from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from paper_intake.remote import LeaseLost, RemoteJob
from paper_intake.remote_worker import RemoteWorker


class _FakeGateway:
    def __init__(self, *, heartbeat_result=True, checkpoints=None):
        self.heartbeat_result = heartbeat_result
        self.checkpoints = checkpoints or {}
        self.completed = []
        self.failed = []

    def claim(self, worker_id="test-worker"):
        return RemoteJob(
            job_id="job-1",
            paper_id="paper-1",
            input_type="pdf",
            input_ref="https://gateway.test/input",
            stage="received",
            checkpoints=self.checkpoints,
            lease_owner=worker_id,
            lease_until=datetime.now(UTC) + timedelta(minutes=10),
        )

    def heartbeat(self, job_id, worker_id):
        if not self.heartbeat_result:
            raise LeaseLost(job_id)
        return True

    def complete(self, job_id, worker_id, publication):
        self.completed.append((job_id, worker_id, publication))

    def fail(self, job_id, worker_id, code, message):
        self.failed.append((job_id, worker_id, code, message))


class _CheckpointAwareProcessor:
    def __init__(self, *, fail=False):
        self.mineru_calls = 0
        self.deepseek_calls = 0
        self.fail = fail

    def process(self, job, _gateway):
        if "parsed" not in job.checkpoints:
            self.mineru_calls += 1
        self.deepseek_calls += 1
        if self.fail:
            raise RuntimeError("secret upstream failure")
        return {
            "notion_page_id": "page-1",
            "slug": "paper-1",
            "site_url": "https://example.github.io/article/paper-1/",
        }


class RemoteWorkerTests(unittest.TestCase):
    def test_worker_stops_when_initial_heartbeat_loses_lease(self):
        gateway = _FakeGateway(heartbeat_result=False)
        runner = RemoteWorker(gateway=gateway, processor=_CheckpointAwareProcessor(), poll_seconds=0)

        with self.assertRaises(LeaseLost):
            runner.run_claimed(gateway.claim())

        self.assertEqual(gateway.completed, [])
        self.assertEqual(gateway.failed, [])

    def test_retry_reuses_parsed_checkpoint(self):
        gateway = _FakeGateway(checkpoints={"parsed": {"artifact_id": "parsed-1"}})
        processor = _CheckpointAwareProcessor()
        runner = RemoteWorker(gateway=gateway, processor=processor, poll_seconds=0)

        self.assertTrue(runner.run_once())

        self.assertEqual(processor.mineru_calls, 0)
        self.assertEqual(processor.deepseek_calls, 1)
        self.assertEqual(len(gateway.completed), 1)

    def test_processing_failure_is_reported_without_leaking_exception_text(self):
        gateway = _FakeGateway()
        runner = RemoteWorker(
            gateway=gateway,
            processor=_CheckpointAwareProcessor(fail=True),
            poll_seconds=0,
        )

        with self.assertRaises(RuntimeError):
            runner.run_once()

        self.assertEqual(gateway.failed[0][2], "processing_failed")
        self.assertNotIn("secret", gateway.failed[0][3])


if __name__ == "__main__":
    unittest.main()
