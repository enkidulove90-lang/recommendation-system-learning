"""Per-platform required-field manifest + material validity."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from paper_intake.platform_requirements import (  # noqa: E402
    PLATFORM_FIELDS, check_image_file, check_package, check_pdf_file,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def make_file(dir: Path, name: str, content: bytes) -> Path:
    p = dir / name
    p.write_bytes(content)
    return p


class MaterialValidityTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def test_valid_png_passes(self):
        p = make_file(self.dir, "ok.png", PNG_MAGIC + b"0" * 2000)
        self.assertEqual(check_image_file(p), "")

    def test_zero_byte_image_is_invalid(self):
        p = make_file(self.dir, "empty.png", b"")
        self.assertIn("invalid image", check_image_file(p))

    def test_missing_image_is_invalid(self):
        self.assertIn("missing image", check_image_file(self.dir / "nope.png"))

    def test_bad_header_is_invalid(self):
        p = make_file(self.dir, "fake.png", b"not-an-image" * 200)
        self.assertIn("invalid image header", check_image_file(p))

    def test_pdf_header(self):
        good = make_file(self.dir, "a.pdf", b"%PDF-1.4\n" + b"0" * 2000)
        bad = make_file(self.dir, "b.pdf", b"notpdf" + b"0" * 2000)
        self.assertEqual(check_pdf_file(good), "")
        self.assertIn("invalid pdf header", check_pdf_file(bad))


class CheckPackageTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.png = make_file(self.dir, "f.png", PNG_MAGIC + b"0" * 2000)

    def _xhs(self, **over):
        base = {
            "paper_id": "2026.acl.1004", "title": "标题", "body": "正文内容",
            "topics": ["推荐系统"], "slug": "paper-x",
            "parsed_dir": str(self.dir),
            "figures": [{"file": "f.png"}],
        }
        base.update(over)
        return base

    def test_all_present_and_valid_ok(self):
        rc = check_package("xhs", self._xhs())
        self.assertTrue(rc["ok"], rc)

    def test_missing_field_reported_and_needs_regeneration(self):
        data = self._xhs()
        del data["body"]
        rc = check_package("xhs", data)
        self.assertFalse(rc["ok"])
        self.assertIn("body", rc["missing_fields"])
        self.assertIn("body", rc["needs_regeneration"])

    def test_title_too_long_is_invalid(self):
        rc = check_package("xhs", self._xhs(title="x" * 25))
        self.assertFalse(rc["ok"])
        self.assertTrue(any("title too long" in r for r in rc["invalid_fields"]))

    def test_zero_byte_figure_is_caught(self):
        make_file(self.dir, "bad.png", b"")
        rc = check_package("xhs", self._xhs(figures=[{"file": "bad.png"}]))
        self.assertFalse(rc["ok"])
        self.assertTrue(any("invalid image" in m for m in rc["invalid_materials"]))

    def test_wechat_body_too_short(self):
        data = {"paper_id": "p", "title": "t", "body_markdown": "短",
                "image_paths": [str(self.png)],
                "links": {"paper": "http://a", "pdf": "http://b"}}
        rc = check_package("wechat", data)
        self.assertTrue(any("body too short" in r for r in rc["invalid_fields"]))

    def test_notion_requires_article_input(self):
        rc = check_package("notion", {})
        self.assertFalse(rc["ok"])
        self.assertIn("canonical_id", rc["missing_fields"])

    def test_all_platforms_have_manifest(self):
        self.assertEqual(set(PLATFORM_FIELDS), {"xhs", "wechat", "notion"})


if __name__ == "__main__":
    unittest.main()
