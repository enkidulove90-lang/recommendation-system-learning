"""内容事件编排层单元测试（content_events/tests/test_content_events.py）。

运行：python -m unittest content_events.tests.test_content_events -v
覆盖：schema 幂等、状态机、事件日志、队列处理器（DTLE 渲染接入 + 幂等）、反馈指标。
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events.schema import ContentItem, ContentState, EventType, content_hash  # noqa: E402
from content_events import state_machine as sm  # noqa: E402
from content_events.event_log import EventLog  # noqa: E402
from content_events import queue_processor as qp  # noqa: E402
from content_events import feedback_collector as fc  # noqa: E402


class TestSchema(unittest.TestCase):
    def test_hash_deterministic_and_idem_key(self):
        a = ContentItem.from_queue_json({"paper_id": "P1", "platform": "xhs", "title": "T", "body_markdown": "B"})
        b = ContentItem.from_queue_json({"paper_id": "P1", "platform": "xhs", "title": "T", "body_markdown": "B"})
        self.assertEqual(a.content_hash, b.content_hash)
        self.assertEqual(a.idem_key, "P1::xhs::" + a.content_hash)
        # 正文不同 → hash 不同
        c = ContentItem.from_queue_json({"paper_id": "P1", "platform": "xhs", "title": "T", "body_markdown": "B2"})
        self.assertNotEqual(a.content_hash, c.content_hash)

    def test_runstate_ignored_in_hash(self):
        a = ContentItem.from_queue_json({"paper_id": "P1", "platform": "xhs", "title": "T", "body_markdown": "B", "state": "draft"})
        b = ContentItem.from_queue_json({"paper_id": "P1", "platform": "xhs", "title": "T", "body_markdown": "B", "state": "staged"})
        self.assertEqual(a.content_hash, b.content_hash)


class TestStateMachine(unittest.TestCase):
    def test_linear_happy_path(self):
        s = ContentState.DRAFT
        for ev in (EventType.RENDERED, EventType.VALIDATED, EventType.STAGED, EventType.PUBLISHED):
            r = sm.transition(s, ev)
            self.assertTrue(r.ok, f"{s}->{ev}")
            s = r.to_state
        self.assertEqual(s, ContentState.PUBLISHED)

    def test_invalid_transition_rejected(self):
        r = sm.transition(ContentState.DRAFT, EventType.STAGED)
        self.assertFalse(r.ok)
        self.assertIn("非法转移", r.reason)

    def test_failure_goes_needs_review(self):
        r = sm.transition(ContentState.VALIDATED, EventType.NEEDS_REVIEW)
        self.assertTrue(r.ok)
        self.assertEqual(r.to_state, ContentState.NEEDS_REVIEW)

    def test_review_reentry(self):
        r = sm.transition(ContentState.NEEDS_REVIEW, EventType.VALIDATED)
        self.assertTrue(r.ok)
        self.assertEqual(r.to_state, ContentState.VALIDATED)


class TestEventLog(unittest.TestCase):
    def test_append_and_read(self):
        with tempfile.TemporaryDirectory() as d:
            log = EventLog(os.path.join(d, "events.jsonl"))
            from content_events.schema import ContentEvent
            log.append(ContentEvent(EventType.CONTENT_INTAKE, "k1", "t1", {"x": 1}))
            log.append(ContentEvent(EventType.RENDERED, "k1", "t2"))
            log.append(ContentEvent(EventType.STAGED, "k2", "t3"))
            all_ev = log.all()
            self.assertEqual(len(all_ev), 3)
            self.assertEqual(len(log.all("k1")), 2)
            self.assertEqual(log.last_type("k1"), EventType.RENDERED)


class TestQueueProcessor(unittest.TestCase):
    def _make_root(self):
        d = tempfile.mkdtemp()
        qd = os.path.join(d, "publish_queue", "item1")
        os.makedirs(qd, exist_ok=True)
        pkg = {
            "paper_id": "arxiv:3806231", "platform": "xhs",
            "canonical_url": "https://arxiv.org/abs/3806231",
            "title": "测试标题", "body_markdown": "# 测试标题\n\n一段正文用于渲染。",
            "image_paths": [], "links": {"paper": "x"}, "review_status": "pending",
        }
        with open(os.path.join(qd, "xhs.json"), "w", encoding="utf-8") as f:
            __import__("json").dump(pkg, f, ensure_ascii=False)
        return d

    def test_process_item_renders_and_stages(self):
        root = self._make_root()
        aroot = os.path.join(root, "data", "publish_artifacts")
        elog = EventLog(os.path.join(root, "data", "content_events", "events.jsonl"))
        qd = os.path.join(root, "publish_queue", "item1")
        res = qp.process_item(qd, "dryrun", elog, aroot, theme="recsys-blue")
        self.assertIn(res["state"], (ContentState.STAGED.value, ContentState.NEEDS_REVIEW.value))
        # 渲染产物应存在（DTLE 可用时）
        art = os.path.join(aroot, res["key"])
        if os.path.isdir(art):
            files = os.listdir(art)
            self.assertTrue(any(f.endswith(".html") for f in files), f"html 未生成: {files}")
        # 事件应含 intake/rendered/validated/staged 之一
        types = [e.type for e in elog.all(res["key"])]
        self.assertIn(EventType.CONTENT_INTAKE, types)
        self.assertIn(EventType.RENDERED, types)

    def test_idempotency_skip(self):
        root = self._make_root()
        aroot = os.path.join(root, "data", "publish_artifacts")
        elog = EventLog(os.path.join(root, "data", "content_events", "events.jsonl"))
        qd = os.path.join(root, "publish_queue", "item1")
        r1 = qp.process_item(qd, "dryrun", elog, aroot, theme="recsys-blue")
        r2 = qp.process_item(qd, "dryrun", elog, aroot, theme="recsys-blue")
        self.assertNotEqual(r1.get("skipped"), "already_staged")
        self.assertEqual(r2.get("skipped"), "already_staged")


class TestFeedbackCollector(unittest.TestCase):
    def test_compute_metrics(self):
        m = fc.compute_metrics(views=1000, likes=100, collects=200, comments=10, replies=4, shares=20, follows=5)
        self.assertAlmostEqual(m["SR"], 200 / 1000)
        self.assertAlmostEqual(m["ER"], (100 + 200 + 10 + 20) / 1000)
        self.assertAlmostEqual(m["FLR"], 200 / 100)  # F/L（L≥20 照常计算，仅决策时受限）
        m2 = fc.compute_metrics(views=1000, likes=300, collects=200, comments=10, replies=4, shares=20, follows=5)
        self.assertAlmostEqual(m2["FLR"], 200 / 300)

    def test_qs7_needs_peers(self):
        self.assertEqual(fc.qs7_for_posts([{"SR": 1, "ER": 1, "DDR": 1, "FR": 1}]), [0.0])

    def test_bayes_group_lift_guards(self):
        lift, dec = fc.bayes_group_lift([0.1, 0.2], account_qs7_mean=0.0)
        self.assertEqual(dec, "样本不足")
        # 高 lift 组
        big = [0.8] * 8
        lift, dec = fc.bayes_group_lift(big, account_qs7_mean=0.0)
        self.assertIn(dec, ("priority_up", "stable"))

    def test_ucb_slot(self):
        best = fc.ucb_slot({"morning": 0.5, "evening": 0.9}, {"morning": 0.1, "evening": 0.1})
        self.assertEqual(best, "evening")

    def test_sqlite_schema(self):
        with tempfile.TemporaryDirectory() as d:
            conn = fc.init_sqlite(os.path.join(d, "f.sqlite"))
            conn.execute("INSERT INTO posts VALUES ('n1','p1','xhs','2026-01-01','morning','{}','{}','h1')")
            conn.commit()
            row = conn.execute("SELECT note_id FROM posts").fetchone()
            self.assertEqual(row[0], "n1")
            conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
