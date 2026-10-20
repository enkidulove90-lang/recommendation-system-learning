from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paper_intake.inputs import (
    InputValidationError,
    PaperInputStore,
    canonicalize_url,
    sanitize_filename,
    sha256_file,
)
from paper_intake.repository import JobRepository


class _FakeResponse:
    def __init__(self, chunks: list[bytes], content_type: str = "application/pdf"):
        self._chunks = chunks
        self.headers = {"content-type": content_type}

    def raise_for_status(self) -> None:
        return None

    def iter_bytes(self):
        yield from self._chunks

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _FakeClient:
    def __init__(self, response: _FakeResponse):
        self.response = response
        self.requested_url = ""

    def stream(self, method: str, url: str, **_kwargs):
        if method != "GET":
            raise AssertionError(method)
        self.requested_url = url
        return self.response


class PaperInputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.store = PaperInputStore(self.root / "inbox", max_file_bytes=64)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_arxiv_abs_and_pdf_urls_share_canonical_identity(self) -> None:
        abstract = canonicalize_url("https://arxiv.org/abs/2608.17316v2")
        pdf = canonicalize_url("https://ARXIV.org/pdf/2608.17316.pdf#page=2")

        self.assertEqual(abstract.canonical_id, "2608.17316")
        self.assertEqual(pdf.canonical_id, "2608.17316")
        self.assertEqual(abstract.normalized_url, "https://arxiv.org/pdf/2608.17316.pdf")
        self.assertEqual(pdf.normalized_url, abstract.normalized_url)

    def test_non_http_url_is_rejected(self) -> None:
        with self.assertRaisesRegex(InputValidationError, "http"):
            canonicalize_url("file:///tmp/paper.pdf")

    def test_generic_pdf_url_discards_fragment_but_preserves_query(self) -> None:
        source = canonicalize_url("https://EXAMPLE.org/papers/a.pdf?download=1#page=3")

        self.assertEqual(source.canonical_id, "")
        self.assertEqual(source.normalized_url, "https://example.org/papers/a.pdf?download=1")

    def test_upload_is_sanitized_validated_and_hashed(self) -> None:
        saved = self.store.store_upload(
            "job-1",
            "../../unsafe paper?.PDF",
            b"%PDF-1.7\nsmall paper",
        )

        self.assertEqual(saved.path.name, "unsafe_paper_.pdf")
        self.assertEqual(saved.path.parent, self.root / "inbox" / "job-1")
        self.assertEqual(saved.sha256, sha256_file(saved.path))
        self.assertEqual(saved.size, saved.path.stat().st_size)

    def test_non_pdf_upload_is_rejected_without_leaving_file(self) -> None:
        with self.assertRaisesRegex(InputValidationError, "PDF"):
            self.store.store_upload("job-2", "paper.pdf", b"not a pdf")

        self.assertFalse((self.root / "inbox" / "job-2").exists())

    def test_oversized_upload_is_rejected(self) -> None:
        with self.assertRaisesRegex(InputValidationError, "64 bytes"):
            self.store.store_upload("job-3", "paper.pdf", b"%PDF-" + b"x" * 80)

    def test_download_stream_is_limited_and_validated(self) -> None:
        client = _FakeClient(_FakeResponse([b"%PDF-1.7\n", b"body"]))

        saved = self.store.download_url(
            "job-4",
            "https://example.org/paper.pdf",
            client=client,
        )

        self.assertEqual(client.requested_url, "https://example.org/paper.pdf")
        self.assertEqual(saved.path.read_bytes(), b"%PDF-1.7\nbody")
        self.assertEqual(saved.path.name, "source.pdf")

    def test_repository_finds_duplicate_by_any_stable_identity(self) -> None:
        repo = JobRepository(self.root / "jobs.sqlite3")
        try:
            existing = repo.create_job(
                source_type="url",
                source_url="https://arxiv.org/pdf/2608.17316.pdf",
            )
            repo.update_job(
                existing.job_id,
                canonical_id="2608.17316",
                source_sha256="deadbeef",
            )

            self.assertEqual(repo.find_duplicate(canonical_id="2608.17316").job_id, existing.job_id)
            self.assertEqual(repo.find_duplicate(source_sha256="deadbeef").job_id, existing.job_id)
            self.assertEqual(
                repo.find_duplicate(source_url="https://arxiv.org/pdf/2608.17316.pdf").job_id,
                existing.job_id,
            )
            self.assertIsNone(repo.find_duplicate(canonical_id="9999.00001"))
        finally:
            repo.close()

    def test_filename_sanitizer_removes_path_components(self) -> None:
        self.assertEqual(sanitize_filename(r"C:\temp\paper name.pdf"), "paper_name.pdf")


if __name__ == "__main__":
    unittest.main()
