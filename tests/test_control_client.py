from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from paper_intake.control_client import (
    ControlPlaneClient,
    build_control_session,
    load_or_create_operation_key,
    sanitize_proxy_environment,
)


class _Response:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    @property
    def is_success(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not self.is_success:
            raise requests.HTTPError(str(self.status_code))


class _Session:
    def __init__(self, *, post_result=None, get_results=()):
        self.post_result = post_result
        self.get_results = iter(get_results)
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        if isinstance(self.post_result, Exception):
            raise self.post_result
        return self.post_result

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        result = next(self.get_results)
        if isinstance(result, Exception):
            raise result
        return result


class ControlClientTests(unittest.TestCase):
    def test_sanitizes_upper_and_lower_proxy_environment(self):
        names = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")
        with patch.dict(os.environ, {name: "http://stale:7890" for name in names}, clear=False):
            sanitize_proxy_environment()
            self.assertTrue(all(name not in os.environ for name in names))

    def test_network_mode_is_explicit_and_timeouts_are_split(self):
        direct = build_control_session(mode="direct")
        proxied = build_control_session(mode="proxy", proxy_url="http://127.0.0.1:7890")
        self.assertFalse(direct.trust_env)
        self.assertEqual(direct.proxies, {})
        self.assertEqual(proxied.proxies["https"], "http://127.0.0.1:7890")
        with self.assertRaises(ValueError):
            build_control_session(mode="proxy", proxy_url="")

    def test_timeout_queries_operation_without_reposting(self):
        session = _Session(
            post_result=requests.ConnectTimeout("tls timeout"),
            get_results=[_Response(200, {"job_id": "job-1", "status": "queued", "code": "retry_accepted"})],
        )
        client = ControlPlaneClient("https://paper-intake.example", "token", session=session, sleep=lambda _n: None)

        result = client.retry_job("job-1", "55555555-5555-4555-8555-555555555555")

        self.assertEqual(result["code"], "retry_accepted")
        self.assertEqual(len(session.post_calls), 1)
        self.assertEqual(len(session.get_calls), 1)
        self.assertEqual(session.post_calls[0][1]["timeout"], (8, 30))
        self.assertEqual(session.get_calls[0][1]["timeout"], (8, 30))

    def test_operation_key_is_persisted_and_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "retry-key"
            first = load_or_create_operation_key(path)
            second = load_or_create_operation_key(path)
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f-]{36}$")


if __name__ == "__main__":
    unittest.main()
