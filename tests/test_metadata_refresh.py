from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from paper_intake.metadata_refresh import (
    MetadataRefreshError,
    needs_metadata_refresh,
    refresh_metadata_file,
)


class MetadataRefreshTests(unittest.TestCase):
    def test_any_legacy_arxiv_feature_requires_refresh(self):
        complete = {
            "metadata_source": "arxiv_xml",
            "title": "A real paper title",
            "authors": ["Alice"],
        }
        cases = (
            {"title": "A real paper title", "authors": ["Alice"]},
            {**complete, "title": "2606.17628"},
            {**complete, "authors": []},
            {**complete, "authors": None},
        )
        for metadata in cases:
            with self.subTest(metadata=metadata):
                self.assertTrue(needs_metadata_refresh(metadata, "2606.17628"))

        self.assertFalse(needs_metadata_refresh(complete, "2606.17628"))
        self.assertFalse(needs_metadata_refresh({}, "pdf-deadbeef"))

    def test_refresh_atomically_replaces_incomplete_metadata_and_marks_source(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "metadata.json"
            path.write_text(
                json.dumps({"canonical_id": "2606.17628", "title": "2606.17628", "custom": "keep"}),
                encoding="utf-8",
            )
            calls = []

            def resolver(canonical_id, source_url):
                calls.append((canonical_id, source_url))
                return {
                    "canonical_id": canonical_id,
                    "title": "OPD-Evolver",
                    "authors": ["Guibin Zhang", "Xun Xu"],
                    "paper_url": "https://arxiv.org/abs/2606.17628",
                    "published": "2026-06-19T12:00:00Z",
                    "updated": "2026-06-20T12:00:00Z",
                    "metadata_source": "arxiv",
                }

            result = refresh_metadata_file(
                path,
                canonical_id="2606.17628",
                source_url="https://arxiv.org/pdf/2606.17628.pdf",
                resolver=resolver,
            )

            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(result.changed)
            self.assertEqual(calls, [("2606.17628", "https://arxiv.org/pdf/2606.17628.pdf")])
            self.assertEqual(stored["title"], "OPD-Evolver")
            self.assertEqual(stored["authors"], ["Guibin Zhang", "Xun Xu"])
            self.assertEqual(stored["metadata_source"], "arxiv_api_refresh")
            self.assertEqual(stored["custom"], "keep")
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_complete_metadata_skips_resolver_and_file_write(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "metadata.json"
            original = json.dumps(
                {"metadata_source": "arxiv_xml", "title": "Complete", "authors": ["Alice"]},
                separators=(",", ":"),
            )
            path.write_text(original, encoding="utf-8")

            result = refresh_metadata_file(
                path,
                canonical_id="2606.17628",
                source_url="https://arxiv.org/abs/2606.17628",
                resolver=lambda *_args: self.fail("resolver must not run"),
            )

            self.assertFalse(result.changed)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_invalid_refresh_never_overwrites_original_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "metadata.json"
            original = '{"canonical_id":"2606.17628","title":"2606.17628","authors":[]}'
            path.write_text(original, encoding="utf-8")

            with self.assertRaises(MetadataRefreshError):
                refresh_metadata_file(
                    path,
                    canonical_id="2606.17628",
                    source_url="https://arxiv.org/abs/2606.17628",
                    resolver=lambda *_args: {
                        "title": "2606.17628",
                        "authors": [],
                        "metadata_source": "fallback",
                    },
                )

            self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
