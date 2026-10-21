from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import requests

from scripts.paper_intake_diagnose import http_check, make_http_session, process_alive


class DiagnoseTests(unittest.TestCase):
    def test_current_process_is_reported_alive(self):
        self.assertTrue(process_alive(os.getpid()))

    def test_diagnostics_ignore_stale_desktop_proxy_environment(self):
        session = make_http_session()
        try:
            self.assertFalse(session.trust_env)
        finally:
            session.close()

    def test_http_check_retries_one_transient_connection_failure(self):
        class Response:
            status_code = 200

        class Session:
            def __init__(self):
                self.calls = 0

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def request(self, *_args, **_kwargs):
                self.calls += 1
                if self.calls == 1:
                    raise requests.ConnectionError("transient TLS reset")
                return Response()

        session = Session()
        with patch("scripts.paper_intake_diagnose.make_http_session", return_value=session):
            result = http_check("Notion", "GET", "https://api.notion.com/v1/users/me")

        self.assertEqual(result.status, "OK")
        self.assertEqual(session.calls, 2)


if __name__ == "__main__":
    unittest.main()
