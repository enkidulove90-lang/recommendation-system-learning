"""CLI 单测（content_events/tests/test_cli.py）。

覆盖：process-queue 默认 dryrun 输出含 summary/summary_text、退出码约定；
status --paper-id 过滤（A6）；坏 JSON 队列不崩（O7）。
"""
import contextlib
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import cli  # noqa: E402


def _make_root():
    d = tempfile.mkdtemp()
    qd = os.path.join(d, "publish_queue", "item1")
    os.makedirs(qd, exist_ok=True)
    pkg = {
        "paper_id": "arxiv:3811003", "platform": "xhs",
        "canonical_url": "https://arxiv.org/abs/3811003",
        "title": "CLI 标题", "body_markdown": "# CLI 标题\n\n正文。",
        "image_paths": [], "links": {"paper": "x"}, "review_status": "pending",
    }
    with open(os.path.join(qd, "xhs.json"), "w", encoding="utf-8") as f:
        __import__("json").dump(pkg, f, ensure_ascii=False)
    return d


def _run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(argv)
    return rc, buf.getvalue()


class TestCliProcessQueue(unittest.TestCase):
    def test_process_queue_dryrun(self):
        root = _make_root()
        rc, out = _run(["process-queue", "--root", root, "--publisher", "dryrun"])
        self.assertEqual(rc, 0)
        self.assertIn("summary", out)
        self.assertIn("summary_text", out)

    def test_bad_queue_does_not_crash(self):
        root = _make_root()
        bad = os.path.join(root, "publish_queue", "bad")
        os.makedirs(bad, exist_ok=True)
        with open(os.path.join(bad, "xhs.json"), "w", encoding="utf-8") as f:
            f.write("{ this is not valid json ")
        rc, out = _run(["process-queue", "--root", root, "--publisher", "dryrun"])
        self.assertIn("summary", out)
        self.assertIn("errors", out)


class TestCliStatus(unittest.TestCase):
    def test_status_after_process(self):
        root = _make_root()
        _run(["process-queue", "--root", root, "--publisher", "dryrun"])
        rc, out = _run(["status", "--root", root, "--paper-id", "arxiv:3811003"])
        self.assertEqual(rc, 0)
        self.assertIn("arxiv:3811003", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
