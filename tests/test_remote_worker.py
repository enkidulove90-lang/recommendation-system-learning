from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_intake.remote import LeaseLost, RemoteJob, RemoteMetadataRefresh
from paper_intake.models import StepName
from paper_intake.remote_worker import (
    FailureDescriptor,
    PublishedMetadataRefresher,
    RemotePipelineProcessor,
    RemoteProcessingError,
    RemoteWorker,
)


class _FakeGateway:
    def __init__(self, *, heartbeat_result=True, checkpoints=None):
        self.heartbeat_result = heartbeat_result
        self.checkpoints = checkpoints or {}
        self.completed = []
        self.failed = []
        self.claim_calls = 0

    def claim(self, worker_id="test-worker"):
        self.claim_calls += 1
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

    def heartbeat(self, job_id, worker_id, stage=""):
        if not self.heartbeat_result:
            raise LeaseLost(job_id)
        return True

    def complete(self, job_id, worker_id, publication):
        self.completed.append((job_id, worker_id, publication))

    def fail(self, job_id, worker_id, code, message, failure=None):
        self.failed.append((job_id, worker_id, code, message, failure))


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
    def test_published_refresh_updates_only_metadata_and_completes_operation(self):
        class Gateway:
            def __init__(self):
                self.completed = []
                self.failed = []

            def complete_metadata_refresh(self, key, worker_id, result):
                self.completed.append((key, worker_id, result))

            def fail_metadata_refresh(self, key, worker_id, code, message):
                self.failed.append((key, worker_id, code, message))

        class Notion:
            def __init__(self):
                self.calls = []

            def update_metadata_properties(self, page_id, metadata):
                self.calls.append((page_id, metadata))

        operation = RemoteMetadataRefresh(
            idempotency_key="11111111-1111-4111-8111-111111111111",
            job_id="published-job",
            paper_id="paper-1",
            arxiv_id="2606.17628",
            input_ref="https://arxiv.org/abs/2606.17628",
            notion_page_id="notion-page",
            lease_owner="metadata-worker",
            lease_until=datetime.now(UTC) + timedelta(minutes=10),
        )
        gateway = Gateway()
        notion = Notion()
        with TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "published-job" / "metadata.json"
            metadata_path.parent.mkdir()
            metadata_path.write_text(
                '{"canonical_id":"2606.17628","title":"2606.17628","authors":[]}',
                encoding="utf-8",
            )
            refresher = PublishedMetadataRefresher(
                workflow_root=directory,
                notion=notion,
                metadata_resolver=lambda _paper_id, _url: {
                    "title": "OPD-Evolver",
                    "authors": ["Author One"],
                    "published": "2026-06-18T00:00:00Z",
                },
            )

            refresher.process(operation, gateway)

        self.assertEqual(notion.calls[0][0], "notion-page")
        self.assertEqual(gateway.completed[0][2]["metadata"]["title"], "OPD-Evolver")
        self.assertTrue(gateway.completed[0][2]["changed"])
        self.assertEqual(gateway.failed, [])

    def test_published_refresh_restores_local_metadata_when_notion_rejects_update(self):
        class Gateway:
            def __init__(self):
                self.failed = []

            def complete_metadata_refresh(self, *_args):
                raise AssertionError("completion must not run")

            def fail_metadata_refresh(self, *args):
                self.failed.append(args)

        class Notion:
            def update_metadata_properties(self, _page_id, _metadata):
                raise RuntimeError("notion unavailable")

        operation = RemoteMetadataRefresh(
            idempotency_key="11111111-1111-4111-8111-111111111111",
            job_id="published-job",
            paper_id="paper-1",
            arxiv_id="2606.17628",
            input_ref="https://arxiv.org/abs/2606.17628",
            notion_page_id="notion-page",
            lease_owner="metadata-worker",
            lease_until=datetime.now(UTC) + timedelta(minutes=10),
        )
        with TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "published-job" / "metadata.json"
            metadata_path.parent.mkdir()
            old = b'{"canonical_id":"2606.17628","title":"2606.17628","authors":[]}'
            metadata_path.write_bytes(old)
            refresher = PublishedMetadataRefresher(
                workflow_root=directory,
                notion=Notion(),
                metadata_resolver=lambda *_args: {
                    "title": "OPD-Evolver",
                    "authors": ["Author One"],
                },
            )
            gateway = Gateway()

            with self.assertRaisesRegex(RuntimeError, "notion unavailable"):
                refresher.process(operation, gateway)

            self.assertEqual(metadata_path.read_bytes(), old)
            self.assertEqual(gateway.failed[0][2], "metadata_refresh_failed")

    def test_published_metadata_refresh_is_claimed_before_pipeline_job(self):
        class Gateway(_FakeGateway):
            def __init__(self):
                super().__init__()
                self.refresh_claims = 0

            def claim_metadata_refresh(self, worker_id):
                self.refresh_claims += 1
                return RemoteMetadataRefresh(
                    idempotency_key="11111111-1111-4111-8111-111111111111",
                    job_id="published-job",
                    paper_id="paper-1",
                    arxiv_id="2606.17628",
                    input_ref="https://arxiv.org/abs/2606.17628",
                    notion_page_id="notion-page",
                    lease_owner=worker_id,
                    lease_until=datetime.now(UTC) + timedelta(minutes=10),
                )

        class Refresher:
            def __init__(self):
                self.calls = []

            def process(self, operation, gateway):
                self.calls.append((operation, gateway))

        gateway = Gateway()
        processor = _CheckpointAwareProcessor()
        refresher = Refresher()
        runner = RemoteWorker(
            gateway=gateway,
            processor=processor,
            metadata_refresher=refresher,
            poll_seconds=0,
        )

        self.assertTrue(runner.run_once())
        self.assertEqual(len(refresher.calls), 1)
        self.assertEqual(gateway.claim_calls, 0)
        self.assertEqual(processor.deepseek_calls, 0)

    def test_preflight_failure_prevents_claiming_a_job(self):
        gateway = _FakeGateway()
        calls = 0

        def unavailable():
            nonlocal calls
            calls += 1
            raise RuntimeError("deepseek balance unavailable")

        runner = RemoteWorker(
            gateway=gateway,
            processor=_CheckpointAwareProcessor(),
            poll_seconds=0,
            preflight=unavailable,
        )

        with self.assertRaisesRegex(RuntimeError, "balance unavailable"):
            runner.run_once()
        with self.assertRaisesRegex(RuntimeError, "balance unavailable"):
            runner.run_once()

        self.assertEqual(gateway.claim_calls, 0)
        self.assertEqual(calls, 1)

    def test_url_only_job_checkpoints_without_uploading_artifacts(self):
        class Gateway:
            def __init__(self):
                self.uploads = []
                self.checkpoints = []

            def upload_artifact(self, *args, **kwargs):
                self.uploads.append((args, kwargs))
                raise AssertionError("artifact upload must stay disabled")

            def checkpoint(self, job_id, worker_id, stage, output):
                self.checkpoints.append((job_id, worker_id, stage, output))

        job = RemoteJob(
            job_id="job-url-only",
            paper_id="paper-url-only",
            input_type="url",
            input_ref="https://arxiv.org/abs/2608.17316",
            stage="received",
            checkpoints={},
            lease_owner="worker-a",
            lease_until=datetime.now(UTC) + timedelta(minutes=10),
            artifact_storage_enabled=False,
        )
        gateway = Gateway()
        with TemporaryDirectory() as directory:
            article_path = Path(directory) / "article.json"
            article_path.write_text("{}", encoding="utf-8")
            processor = RemotePipelineProcessor(
                repository=None,
                input_store=None,
                pipeline=None,
                workflow_root=directory,
                site_url="https://example.github.io",
            )
            processor._sync_step(
                job,
                gateway,
                StepName.DEEPSEEK_GENERATE,
                {"article_path": str(article_path), "title": "URL paper"},
            )

        self.assertEqual(gateway.uploads, [])
        self.assertEqual(gateway.checkpoints[0][2], StepName.DEEPSEEK_GENERATE.value)
        self.assertEqual(gateway.checkpoints[0][3], {"title": "URL paper"})

    def test_worker_stops_when_initial_heartbeat_loses_lease(self):
        gateway = _FakeGateway(heartbeat_result=False)
        runner = RemoteWorker(gateway=gateway, processor=_CheckpointAwareProcessor(), poll_seconds=0)

        with self.assertRaises(LeaseLost):
            runner.run_claimed(gateway.claim())

        self.assertEqual(gateway.completed, [])
        self.assertEqual(gateway.failed, [])

    def test_pipeline_updates_job_stage_before_a_step_can_fail(self):
        class Repository:
            def get_job(self, _job_id):
                return object()

        class Pipeline:
            def run(self, _job_id, *, before_step, on_step_completed):
                before_step(StepName.MINERU_PARSE)
                raise RuntimeError("parse exploded")

        class Gateway:
            def heartbeat(self, *_args):
                return True

        job = _FakeGateway().claim()
        job.artifact_storage_enabled = False
        processor = RemotePipelineProcessor(
            repository=Repository(), input_store=None, pipeline=Pipeline(),
            workflow_root=".", site_url="https://example.github.io",
        )
        with self.assertRaisesRegex(RuntimeError, "parse exploded"):
            processor.process(job, Gateway())
        self.assertEqual(job.stage, StepName.MINERU_PARSE.value)

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
        failure = gateway.failed[0][4]
        self.assertIsInstance(failure, dict)
        self.assertEqual(failure["category"], "internal")
        self.assertEqual(failure["exception_type"], "RuntimeError")
        self.assertFalse(failure["retryable"])
        self.assertNotIn("secret", str(failure))
        self.assertRegex(failure["error_fingerprint"], r"^[0-9a-f]{40}$")

    def test_failure_descriptor_rejects_unsafe_diagnostic_fields(self):
        with self.assertRaises(ValueError):
            FailureDescriptor(
                stage="download_pdf",
                code="download_failed",
                category="network",
                retryable=True,
                attempt=1,
                safe_message="Authorization: Bearer secret-token",
                diagnostic_hint="Retry the download.",
                error_fingerprint="abc",
            )

    def test_known_processing_failure_keeps_its_safe_stage_error(self):
        class KnownFailureProcessor:
            def process(self, _job, _gateway):
                raise RemoteProcessingError("notion_request_failed", "Notion request failed.")

        gateway = _FakeGateway()
        runner = RemoteWorker(gateway=gateway, processor=KnownFailureProcessor(), poll_seconds=0)

        with self.assertRaises(RemoteProcessingError):
            runner.run_once()

        self.assertEqual(gateway.failed[0][2], "notion_request_failed")
        self.assertEqual(gateway.failed[0][3], "Notion request failed.")


if __name__ == "__main__":
    unittest.main()
