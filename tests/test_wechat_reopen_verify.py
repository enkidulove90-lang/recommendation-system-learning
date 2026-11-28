"""WeChat draft reopen verification must check title, body, and image count.

Uses a stub that replaces _browser/_eval so no real browser is driven.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from redbook.infrastructure.wechat_delivery import (  # noqa: E402
    DeliveryReceipt, WeChatDraftDelivery, WeChatDraftPayload,
)


def make_delivery(reopened_dom: dict) -> WeChatDraftDelivery:
    delivery = WeChatDraftDelivery(runner=lambda *a, **k: None)
    # navigate() calls: open/wait/close -> no-op
    delivery._browser = lambda *parts: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    # _eval returns our canned DOM snapshot for the verify step
    delivery._eval = lambda js, label: dict(reopened_dom)
    return delivery


def payload() -> WeChatDraftPayload:
    return WeChatDraftPayload(
        title="EchoMLLM：心超视频关键帧定位",
        body_text="正文第一段。" * 40,
        cover_image=None,
        body_html="<p>本文提出EchoMLLM用于心超视频关键帧定位与报告生成。</p>",
    )


class ReopenVerificationTest(unittest.TestCase):
    def _snapshot(self, *, title="EchoMLLM：心超视频关键帧定位",
                 body="本文提出EchoMLLM用于心超视频关键帧定位与报告生成。",
                 images=2) -> dict:
        return {"title": title, "body_text": body, "image_count": images,
                "ok": True}

    def test_verified_when_title_body_and_image_count_all_match(self):
        d = make_delivery(self._snapshot(images=2))
        p = payload()
        # payload body_html has 1 <img>? we pass expected image count explicitly
        self.assertTrue(d._verify_draft_reopened("draft-1", p, expected_images=2))

    def test_fails_when_title_differs(self):
        d = make_delivery(self._snapshot(title="别的标题"))
        self.assertFalse(d._verify_draft_reopened("draft-1", payload(), expected_images=2))

    def test_fails_when_body_not_present(self):
        d = make_delivery(self._snapshot(body="完全不同的正文"))
        self.assertFalse(d._verify_draft_reopened("draft-1", payload(), expected_images=2))

    def test_fails_when_image_count_mismatches(self):
        d = make_delivery(self._snapshot(images=0))
        self.assertFalse(d._verify_draft_reopened("draft-1", payload(), expected_images=2))

    def test_fails_without_draft_id(self):
        d = make_delivery(self._snapshot())
        self.assertFalse(d._verify_draft_reopened(None, payload(), expected_images=2))


class SaveDraftDetectionTest(unittest.TestCase):
    def _delivery(self, *, marker_ok: bool, draft_id):
        d = WeChatDraftDelivery(runner=lambda *a, **k: None)
        d._browser = lambda *p: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        d._click_by_label = lambda label: {"ok": True}
        d._eval = lambda js, label: {"ok": marker_ok}
        d._extract_draft_id = lambda: draft_id
        return d

    def test_marker_success_returns_true(self):
        d = self._delivery(marker_ok=True, draft_id=None)
        self.assertTrue(d._save_draft())

    def test_url_draft_id_is_sufficient_when_marker_missing(self):
        # Real case: toast never appears, but the saved draft id is in the URL.
        d = self._delivery(marker_ok=False, draft_id="123456")
        self.assertTrue(d._save_draft())

    def test_no_signal_returns_false(self):
        d = self._delivery(marker_ok=False, draft_id=None)
        self.assertFalse(d._save_draft())


if __name__ == "__main__":
    unittest.main()
