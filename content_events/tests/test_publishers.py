"""Publisher 适配器单测（content_events/tests/test_publishers.py）。

覆盖：make_publisher 工厂分派、DryRunPublisher 校验/本地包、_GuardedRedbookPublisher
dry_run 永远降级本地包（A3）、PlaceholderPublisher 未知平台显式占位（A4）。
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import publishers as pub  # noqa: E402

VALID_PKG = {
    "paper_id": "arxiv:3811001", "platform": "xhs",
    "canonical_url": "https://arxiv.org/abs/3811001",
    "title": "测试标题", "body_markdown": "# 标题\n\n正文内容。",
    "image_paths": [], "links": {"paper": "x"}, "review_status": "pending",
}


class TestMakePublisher(unittest.TestCase):
    def test_dryrun(self):
        self.assertIsInstance(pub.make_publisher("dryrun", "."), pub.DryRunPublisher)

    def test_known_platform_returns_guarded(self):
        p = pub.make_publisher("xhs", ".", dry_run=True)
        self.assertIsInstance(p, pub._GuardedRedbookPublisher)
        self.assertTrue(p.dry_run)

    def test_unknown_platform_returns_placeholder(self):
        p = pub.make_publisher("tiktok", ".", dry_run=True)
        self.assertIsInstance(p, pub.PlaceholderPublisher)
        self.assertEqual(p.platform_name, "tiktok")


class TestDryRun(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.p = pub.DryRunPublisher(self.d)

    def test_validate_ok(self):
        self.assertEqual(self.p.validate(VALID_PKG), [])

    def test_validate_missing_fields(self):
        bad = dict(VALID_PKG)
        bad["paper_id"] = ""
        errs = self.p.validate(bad)
        self.assertTrue(any("paper_id" in e for e in errs))

    def test_stage_writes_local_package(self):
        rcpt = self.p.stage(VALID_PKG)
        self.assertTrue(rcpt["path"].endswith(".json"))
        self.assertTrue(os.path.exists(rcpt["path"]))

    def test_stage_raises_on_bad(self):
        bad = dict(VALID_PKG)
        bad["title"] = ""
        with self.assertRaises(pub.PublishingError):
            self.p.stage(bad)

    def test_publish_noop(self):
        r = self.p.publish("x")
        self.assertFalse(r["published"])


class TestGuarded(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_dry_run_local_fallback(self):
        # dry_run=True 永远只写本地包，不触达真实平台（A3 修复：不再无条件抛）
        for plat in ("wechat", "xhs"):
            p = pub.make_publisher(plat, self.d, dry_run=True)
            rcpt = p.stage(VALID_PKG)
            self.assertEqual(rcpt["mode"], "local_fallback")
            self.assertTrue(os.path.exists(rcpt["path"]))


class TestPlaceholder(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_stage_writes_placeholder(self):
        p = pub.make_publisher("mastodon", self.d, dry_run=True)
        rcpt = p.stage(VALID_PKG)
        self.assertEqual(rcpt["mode"], "placeholder")
        self.assertTrue(os.path.exists(rcpt["path"]))

    def test_publish_unsupported(self):
        p = pub.make_publisher("mastodon", self.d)
        with self.assertRaises(pub.PublishingError):
            p.publish("x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
