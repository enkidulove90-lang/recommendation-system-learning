"""事件日志健壮性单测（content_events/tests/test_event_log.py）。

覆盖：损坏行（非法 JSON / 截断 JSON）被跳过不中断迭代（修复 B3）。
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events.event_log import EventLog  # noqa: E402
from content_events.schema import ContentEvent, EventType  # noqa: E402


class TestCorruptedLines(unittest.TestCase):
    def test_skips_bad_lines(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "events.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write("not json at all\n")
            f.write('{"type":"rendered","item_key":"k1","ts":"t","detail":{}}\n')
            f.write('{"type":"staged"\n')  # 截断 JSON
            f.write('{"type":"validated","item_key":"k2","ts":"t","detail":{}}\n')
        log = EventLog(path)
        evs = log.all()
        self.assertEqual(len(evs), 2)
        types = {e.type for e in evs}
        self.assertIn(EventType.RENDERED, types)
        self.assertIn(EventType.VALIDATED, types)

    def test_append_and_iter_roundtrip(self):
        d = tempfile.mkdtemp()
        log = EventLog(os.path.join(d, "events.jsonl"))
        log.append(ContentEvent(EventType.STAGED, "kx", "t", {"x": 1}))
        self.assertEqual(len(log.all("kx")), 1)
        self.assertEqual(log.all("kx")[0].type, EventType.STAGED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
