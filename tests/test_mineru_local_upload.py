from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skills.pdf_parser import PDFParser


class _Response:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _Client:
    calls = []

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def post(self, url, *, headers, json):
        self.calls.append(("POST", url, json))
        return _Response(
            {
                "code": 0,
                "data": {
                    "batch_id": "batch-1",
                    "file_urls": ["https://upload.example/signed"],
                },
            }
        )

    def put(self, url, *, content):
        self.calls.append(("PUT", url, content.read()))
        return _Response({})

    def get(self, url, *, headers):
        self.calls.append(("GET", url, None))
        return _Response(
            {
                "code": 0,
                "data": {
                    "extract_result": [
                        {
                            "file_name": "paper.pdf",
                            "state": "done",
                            "full_zip_url": "https://cdn.example/result.zip",
                        }
                    ]
                },
            }
        )


class MinerULocalUploadTests(unittest.TestCase):
    def test_local_pdf_uses_signed_batch_upload_and_batch_polling(self):
        with tempfile.TemporaryDirectory() as temporary:
            pdf = Path(temporary) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.7\nbody")
            parser = PDFParser(api_key="mineru-test-token")
            _Client.calls = []

            with patch("skills.pdf_parser.httpx.Client", _Client):
                task_id = parser._submit_task("", str(pdf))
                result_url = parser._poll_task(task_id)

            self.assertEqual(task_id, "batch:batch-1")
            self.assertEqual(result_url, "https://cdn.example/result.zip")
            self.assertEqual(_Client.calls[0][1], "https://mineru.net/api/v4/file-urls/batch")
            self.assertEqual(_Client.calls[1], ("PUT", "https://upload.example/signed", b"%PDF-1.7\nbody"))
            self.assertIn("/api/v4/extract-results/batch/batch-1", _Client.calls[2][1])


if __name__ == "__main__":
    unittest.main()
