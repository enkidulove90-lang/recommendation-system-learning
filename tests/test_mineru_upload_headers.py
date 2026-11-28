from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skills.pdf_parser import PDFParser


class _Response:
    status_code = 200
    text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return {"code": 0, "data": {"batch_id": "batch-1", "file_urls": ["https://upload.example/signed"]}}


class _Client:
    """Records the kwargs passed to put() so we can assert no None-valued headers."""

    put_kwargs: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def post(self, url, *, headers, json):
        return _Response()

    def put(self, url, *, content, headers=None):
        # Emulate httpx's real validation: None header values are illegal.
        for key, value in (headers or {}).items():
            if value is None:
                raise TypeError(f"Header value must be str or bytes, not {type(value)}")
        type(self).put_kwargs.append({"content": content, "headers": headers})
        return _Response()


class MinerUUploadHeaderTests(unittest.TestCase):
    def test_upload_put_sends_no_none_valued_headers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pdf = Path(temporary) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.7\nbody")
            parser = PDFParser(api_key="test-token")
            _Client.put_kwargs = []

            with patch("skills.pdf_parser.httpx.Client", _Client):
                batch_id = parser._submit_task_upload(str(pdf), "2601.00001")

            self.assertEqual(batch_id, "batch-1")
            self.assertEqual(len(_Client.put_kwargs), 1)
            put = _Client.put_kwargs[0]
            self.assertEqual(put["content"], b"%PDF-1.7\nbody")
            self.assertIsNone(put["headers"])


if __name__ == "__main__":
    unittest.main()
