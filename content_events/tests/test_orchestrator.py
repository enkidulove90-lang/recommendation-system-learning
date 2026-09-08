"""编排器单测（content_events/tests/test_orchestrator.py）。

覆盖：run_once 返回 (摘要列表, RunSummary) 元组；collect_feedback 在无 opencli 时
安全返回 collection_failed（O8 接通死代码、守卫 OpenCLI）。
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import orchestrator  # noqa: E402
from content_events import feedback_collector as fc  # noqa: E402


def _make_root():
    d = tempfile.mkdtemp()
    qd = os.path.join(d, "publish_queue", "item1")
    os.makedirs(qd, exist_ok=True)
    pkg = {
        "paper_id": "arxiv:3811002", "platform": "xhs",
        "canonical_url": "https://arxiv.org/abs/3811002",
        "title": "测试标题", "body_markdown": "# 测试标题\n\n正文。",
        "image_paths": [], "links": {"paper": "x"}, "review_status": "pending",
    }
    with open(os.path.join(qd, "xhs.json"), "w", encoding="utf-8") as f:
        __import__("json").dump(pkg, f, ensure_ascii=False)
    return d


class TestRunOnce(unittest.TestCase):
    def test_returns_tuple(self):
        root = _make_root()
        results, summary = orchestrator.run_once(root, publisher="dryrun", theme="recsys-blue")
        self.assertIsInstance(results, list)
        self.assertIsInstance(summary, orchestrator.queue_processor.RunSummary)
        self.assertEqual(summary.scanned, 1)


class TestCollectFeedback(unittest.TestCase):
    def test_no_opencli_fails_safe(self):
        root = _make_root()
        res = orchestrator.collect_feedback(root, opencli_fn=None)
        self.assertEqual(res["status"], "collection_failed")

    def test_with_opencli_and_seeded_posts(self):
        root = _make_root()
        db = os.path.join(root, "data", "feedback", "feedback.sqlite")
        conn = fc.init_sqlite(db)
        conn.execute("INSERT OR REPLACE INTO posts VALUES ('n1','p1','xhs','2026-01-01','morning','{}','{}','h1')")
        conn.execute("INSERT OR REPLACE INTO posts VALUES ('n2','p2','xhs','2026-01-01','evening','{}','{}','h2')")
        conn.execute("INSERT INTO metric_snapshots VALUES ('n1','2026-01-02',24,1000,100,200,10,4,20,5,'{}','{}','p1.json')")
        conn.execute("INSERT INTO metric_snapshots VALUES ('n2','2026-01-02',24,1000,120,180,12,5,25,6,'{}','{}','p2.json')")
        conn.commit()
        conn.close()
        res = orchestrator.collect_feedback(root, opencli_fn=lambda: [])
        self.assertIn("decision", res)
        self.assertTrue(res["decision"]["applied"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
