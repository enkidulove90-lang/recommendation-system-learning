"""反馈自优化单测（content_events/tests/test_feedback_opt.py）。

覆盖：decide_once 样本不足→applied=False；两帖→applied 且写 decisions 表（O8 接通死代码）；
collect_once 成功采样后 emit FEEDBACK_SAMPLED（O8 生命周期事件）。
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import feedback_collector as fc  # noqa: E402
from content_events.event_log import EventLog  # noqa: E402


class TestDecideOnce(unittest.TestCase):
    def _seed(self, n):
        d = tempfile.mkdtemp()
        conn = fc.init_sqlite(os.path.join(d, "f.sqlite"))
        for i in range(n):
            conn.execute(
                "INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?,?,?)",
                (f"n{i}", f"p{i}", "xhs", "2026-01-01", "morning", "{}", "{}", f"h{i}"),
            )
            conn.execute(
                "INSERT INTO metric_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (f"n{i}", "2026-01-02", 24, 1000, 100 + i, 200, 10, 4, 20, 5, "{}", "{}", f"p{i}.json"),
            )
        conn.commit()
        return conn

    def test_insufficient_posts(self):
        conn = self._seed(1)
        res = fc.decide_once(conn)
        self.assertFalse(res["applied"])
        self.assertEqual(res["reason"], "insufficient_posts")

    def test_applied_with_two_posts(self):
        conn = self._seed(2)
        res = fc.decide_once(conn)
        self.assertTrue(res["applied"])
        self.assertIn("decision_id", res)
        row = conn.execute(
            "SELECT decision_id FROM decisions WHERE decision_id=?", (res["decision_id"],)
        ).fetchone()
        self.assertIsNotNone(row)

    def test_collect_once_emits_sampled(self):
        conn = fc.init_sqlite(os.path.join(tempfile.mkdtemp(), "f.sqlite"))
        elog = EventLog(os.path.join(tempfile.mkdtemp(), "events.jsonl"))
        res = fc.collect_once(
            conn, opencli_fn=lambda: [("n1", 24, {"views": 10}, "p.json")], event_log=elog
        )
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["sampled"], 1)
        types = [e.type for e in elog.all("feedback")]
        self.assertIn(fc.EventType.FEEDBACK_SAMPLED, types)


if __name__ == "__main__":
    unittest.main(verbosity=2)
