"""幂等 / 跨目录去重单测（content_events/tests/test_idempotency.py）。

覆盖：IdempotencyRegistry.mark/terminal_state（O1）；同 idem_key 跨两个队列目录，
第一目录 stage 后，第二目录应幂等跳过（O1 跨目录去重）。
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import queue_processor as qp  # noqa: E402
from content_events.event_log import EventLog  # noqa: E402
from content_events.schema import ContentState, RunSummary  # noqa: E402


def _make_item_dir(root, sub, paper_id="arxiv:3811004", platform="xhs", body="# T\n\nB"):
    d = os.path.join(root, "publish_queue", sub)
    os.makedirs(d, exist_ok=True)
    pkg = {
        "paper_id": paper_id, "platform": platform,
        "canonical_url": "https://arxiv.org/abs/" + paper_id.split(":")[-1],
        "title": "标题", "body_markdown": body,
        "image_paths": [], "links": {"paper": "x"}, "review_status": "pending",
    }
    with open(os.path.join(d, platform + ".json"), "w", encoding="utf-8") as f:
        __import__("json").dump(pkg, f, ensure_ascii=False)
    return d


class TestRegistry(unittest.TestCase):
    def test_mark_and_terminal(self):
        reg = qp.IdempotencyRegistry(os.path.join(tempfile.mkdtemp(), "idem.jsonl"))
        reg.mark("k1", ContentState.STAGED.value, "p", "xhs")
        self.assertEqual(reg.terminal_state("k1"), ContentState.STAGED.value)

    def test_non_terminal_not_returned(self):
        reg = qp.IdempotencyRegistry(os.path.join(tempfile.mkdtemp(), "idem.jsonl"))
        reg.mark("k2", ContentState.DRAFT.value, "p", "xhs")
        self.assertIsNone(reg.terminal_state("k2"))

    def test_unknown_key(self):
        reg = qp.IdempotencyRegistry(os.path.join(tempfile.mkdtemp(), "idem.jsonl"))
        self.assertIsNone(reg.terminal_state("nope"))


class TestCrossDirIdempotency(unittest.TestCase):
    def test_same_key_two_dirs_second_skips(self):
        root = tempfile.mkdtemp()
        d1 = _make_item_dir(root, "a")
        d2 = _make_item_dir(root, "b")  # 同 paper_id/platform/body → 同 idem_key
        aroot = os.path.join(root, "data", "publish_artifacts")
        elog = EventLog(os.path.join(root, "data", "content_events", "events.jsonl"))
        reg = qp.IdempotencyRegistry(qp._default_registry_path(aroot))
        rs = RunSummary()
        r1 = qp.process_item(
            d1, "dryrun", elog, aroot, theme="recsys-blue",
            idem_registry=reg, run_summary=rs, root=root,
        )
        r2 = qp.process_item(
            d2, "dryrun", elog, aroot, theme="recsys-blue",
            idem_registry=reg, run_summary=rs, root=root,
        )
        self.assertIsNotNone(r1.get("key"))
        self.assertEqual(r2.get("skipped"), "already_staged")
        self.assertEqual(rs.skipped_idempotent, 1)
        self.assertEqual(rs.processed, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
