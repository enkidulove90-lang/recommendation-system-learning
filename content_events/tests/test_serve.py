"""REST 服务测试（content_events/tests/test_serve.py）。

用 fastapi TestClient 覆盖 /health、/process-queue、/status、/collect-feedback。
安全断言：/process-queue 默认 dry_run=True（沙箱安全，只写本地包）。
真实语料验证：把仓库现有 publish_queue/ 复制到临时根，经 REST 实跑确认 errors=0。
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJ not in __import__("sys").path:
    __import__("sys").path.insert(0, PROJ)

from fastapi.testclient import TestClient  # noqa: E402

from content_events import serve  # noqa: E402


def _copy_real_queue() -> str:
    tmp = tempfile.mkdtemp(prefix="ce_serve_")
    src = os.path.join(PROJ, "publish_queue")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(tmp, "publish_queue"))
    return tmp


class ServeTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(serve.app)
        self.tmp = _copy_real_queue()

    def tearDown(self):
        try:
            shutil.rmtree(self.tmp)
        except OSError:
            pass

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_process_queue_dryrun_on_real_corpus(self):
        # 默认 dry_run=True（安全）
        r = self.client.post("/process-queue", json={"root": self.tmp, "publisher": "dryrun"})
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertTrue(body["dry_run"])
        self.assertGreaterEqual(body["processed"], 1)
        self.assertEqual(body["summary"]["errors"], 0, body["summary"])
        # 跨目录幂等：重复调用应跳过已终态项
        r2 = self.client.post("/process-queue", json={"root": self.tmp, "publisher": "dryrun"})
        self.assertEqual(r2.status_code, 200)
        self.assertGreaterEqual(r2.json()["summary"]["skipped_idempotent"], 1)

    def test_process_queue_requires_publish_queue(self):
        empty = tempfile.mkdtemp(prefix="ce_empty_")
        try:
            r = self.client.post("/process-queue", json={"root": empty})
            self.assertEqual(r.status_code, 400)
        finally:
            try:
                shutil.rmtree(empty)
            except OSError:
                pass

    def test_status(self):
        r = self.client.get("/status", params={"root": self.tmp})
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)
        self.assertGreaterEqual(len(r.json()), 1)

    def test_status_paper_id_filter(self):
        # 取一个真实 paper_id 过滤应返回子集或等长
        all_r = self.client.get("/status", params={"root": self.tmp}).json()
        if all_r:
            pid = all_r[0].get("paper_id")
            f = self.client.get("/status", params={"root": self.tmp, "paper_id": pid}).json()
            self.assertTrue(all(x.get("paper_id") == pid for x in f))

    def test_collect_feedback(self):
        # 沙箱无 OpenCLI 会话 → 返回 200 但 status=collection_failed（守卫），不崩
        r = self.client.post("/collect-feedback", json={"root": self.tmp})
        self.assertEqual(r.status_code, 200)
        self.assertIn("status", r.json())


if __name__ == "__main__":
    unittest.main()
