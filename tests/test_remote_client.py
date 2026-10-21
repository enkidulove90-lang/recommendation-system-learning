from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

import httpx

from paper_intake.remote import LeaseLost, RemoteGatewayClient


class RemoteGatewayClientTests(unittest.TestCase):
    def test_default_client_ignores_inherited_proxy_environment(self):
        client = MagicMock()
        client.headers = {}
        inherited = {
            "HTTP_PROXY": "http://stale:7890",
            "https_proxy": "http://stale:7890",
            "ALL_PROXY": "http://stale:7890",
        }
        with patch.dict("os.environ", inherited, clear=False), patch(
            "paper_intake.remote.httpx.Client", return_value=client
        ) as factory:
            RemoteGatewayClient("https://gateway.test", "machine-secret")
            self.assertTrue(all(name not in __import__("os").environ for name in inherited))

        factory.assert_called_once_with(
            base_url="https://gateway.test",
            timeout=httpx.Timeout(connect=8, read=120, write=120, pool=8),
            trust_env=False,
        )

    def test_proxy_mode_is_explicit(self):
        client = MagicMock()
        client.headers = {}
        with patch("paper_intake.remote.httpx.Client", return_value=client) as factory:
            RemoteGatewayClient(
                "https://gateway.test",
                "machine-secret",
                network_mode="proxy",
                proxy_url="http://127.0.0.1:7890",
            )
        factory.assert_called_once_with(
            base_url="https://gateway.test",
            timeout=httpx.Timeout(connect=8, read=120, write=120, pool=8),
            trust_env=False,
            proxy="http://127.0.0.1:7890",
        )

    def test_claim_parses_nested_job_and_uses_machine_token(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(
                200,
                json={
                    "job": {
                        "job_id": "job-1",
                        "paper_id": "paper-1",
                        "input_type": "pdf",
                        "input_ref": "https://gateway.test/v1/worker/jobs/job-1/input?worker_id=w",
                        "stage": "received",
                        "checkpoints": {},
                        "lease_owner": "worker-a",
                        "lease_until": "2026-10-20T12:00:00Z",
                    }
                },
            )

        client = httpx.Client(
            base_url="https://gateway.test",
            transport=httpx.MockTransport(handler),
        )
        gateway = RemoteGatewayClient("https://gateway.test", "machine-secret", client=client)

        job = gateway.claim("worker-a")

        self.assertEqual(job.job_id, "job-1")
        self.assertEqual(requests[0].url.path, "/v1/worker/jobs/claim")
        self.assertEqual(requests[0].headers["authorization"], "Bearer machine-secret")

    def test_claim_returns_none_for_no_content(self):
        client = httpx.Client(
            base_url="https://gateway.test",
            transport=httpx.MockTransport(lambda _request: httpx.Response(204)),
        )
        gateway = RemoteGatewayClient("https://gateway.test", "token", client=client)

        self.assertIsNone(gateway.claim("worker-a"))

    def test_heartbeat_raises_lease_lost_on_conflict(self):
        client = httpx.Client(
            base_url="https://gateway.test",
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(409, json={"code": "lease_lost"})
            ),
        )
        gateway = RemoteGatewayClient("https://gateway.test", "token", client=client)

        with self.assertRaises(LeaseLost):
            gateway.heartbeat("job-1", "worker-a")

    def test_artifact_upload_sends_digest_and_filename(self):
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["headers"] = request.headers
            captured["body"] = request.content
            return httpx.Response(201, json={"artifact_id": "artifact-1"})

        client = httpx.Client(
            base_url="https://gateway.test",
            transport=httpx.MockTransport(handler),
        )
        gateway = RemoteGatewayClient("https://gateway.test", "token", client=client)

        artifact = gateway.upload_artifact(
            "job-1",
            "worker-a",
            kind="parsed_markdown",
            filename="paper.md",
            content=b"# paper",
            content_type="text/markdown",
        )

        self.assertEqual(artifact["artifact_id"], "artifact-1")
        self.assertEqual(captured["headers"]["x-artifact-name"], "paper.md")
        self.assertEqual(len(captured["headers"]["x-content-sha256"]), 64)
        self.assertEqual(captured["body"], b"# paper")


if __name__ == "__main__":
    unittest.main()
