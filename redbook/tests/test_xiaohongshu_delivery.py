"""xiaohongshu_delivery 单元测试（对齐 CDP save-last 重写 + 2026-10-28 冻结口径）。

覆盖：save-last 全流程与 PDF 附件；话题精确匹配（无 items[0] 兜底）；
话题下拉缺失 → TopicEntityUnavailable；PDF 豁免规则；CLI 互斥校验。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from redbook.infrastructure.xiaohongshu_delivery import (
    DeliveryError,
    DraftPayload,
    OpenCliXiaohongshuDelivery,
    TopicEntityUnavailable,
    build_deliver_payload,
)


class FakeRunner:
    """Emulate OpenCLI for the CDP save-last flow.

    ``eval_rules``: (js_substring, stdout_json) pairs served by ``browser eval``.
    ``fail_rules``: commands whose joined text contains the substring fail (rc 1).
    """

    def __init__(self, drafts: tuple[str, ...] = ("[]",), eval_rules: dict[str, str] | None = None,
                 fail_rules: tuple[str, ...] = ()) -> None:
        self.drafts, self.eval_rules, self.fail_rules = list(drafts), dict(eval_rules or {}), fail_rules
        self.calls: list[list[str]] = []

    def __call__(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        joined = "\x1f".join(command)
        if any(rule in joined for rule in self.fail_rules):
            return subprocess.CompletedProcess(command, 1, "", "simulated failure")
        if "xiaohongshu\x1fdrafts" in joined:
            return subprocess.CompletedProcess(command, 0, self.drafts.pop(0) if self.drafts else "[]", "")
        if "browser" in command:
            sub = command[command.index("browser") + 2]
            if sub == "eval":
                js = command[-1]
                for needle, response in self.eval_rules.items():
                    if needle in js:
                        return subprocess.CompletedProcess(command, 0, response, "")
                return subprocess.CompletedProcess(command, 0, '{"ok": true}', "")
        return subprocess.CompletedProcess(command, 0, "{}", "")


class XiaohongshuDeliveryTests(unittest.TestCase):
    def _payload(self, root: Path, **overrides) -> DraftPayload:
        image, pdf = root / "figure.png", root / "paper.pdf"
        image.write_bytes(b"png")
        pdf.write_bytes(b"%PDF-1.7")
        fields = dict(title="论文快报", body="正文", image_paths=(image,),
                      topics=("AI论文",), pdf_path=pdf)
        fields.update(overrides)
        return DraftPayload(**fields)

    def test_deliver_attaches_pdf_then_saves(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            drafts = ('[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]')
            runner = FakeRunner(drafts=drafts)
            receipt = OpenCliXiaohongshuDelivery(runner=runner).deliver(self._payload(Path(folder)))
        self.assertEqual(receipt.draft_id, "draft-1")
        self.assertEqual(receipt.pdf_name, "paper.pdf")
        upload = next(call for call in runner.calls if any("paper.pdf" in part for part in call))
        self.assertTrue(any("paper.pdf" in part for part in upload))

    def test_topic_without_exact_match_raises_and_skips(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(
                eval_rules={"no exact match": '{"ok": false, "count": 3, "reason": "no exact match"}'})
            with self.assertRaises(TopicEntityUnavailable):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(self._payload(Path(folder)))
        deletes = [call for call in runner.calls if "draft-delete" in call]
        self.assertEqual(deletes, [], "nothing was saved, so nothing may be deleted")

    def test_missing_topic_dropdown_raises_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(fail_rules=("div.items div.item",))
            with self.assertRaises(TopicEntityUnavailable):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(self._payload(Path(folder)))

    def test_missing_topics_fails_before_platform_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder), topics=())
            runner = FakeRunner()
            with self.assertRaises(DeliveryError):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(payload)
        self.assertEqual(runner.calls, [])

    def test_skip_topic_binding_allows_empty_topics(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            self._payload(Path(folder), topics=(), require_real_topics=False).validate()

    def test_pdf_required_unless_waived(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder) / "figure.png"
            image.write_bytes(b"png")
            with self.assertRaises(DeliveryError):
                DraftPayload("论文快报", "正文", (image,), ("AI",), None).validate()
            DraftPayload("论文快报", "正文", (image,), ("AI",), None, require_pdf_attachment=False).validate()

    def test_non_pdf_attachment_rejected_even_with_waiver(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            text = Path(folder) / "notes.txt"
            text.write_bytes(b"txt")
            with self.assertRaises(DeliveryError):
                DraftPayload("论文快报", "正文", (text,), (), text,
                             require_real_topics=False, require_pdf_attachment=False).validate()


class DeliverCliFlagTests(unittest.TestCase):
    """CLI 互斥校验（build_deliver_payload 与 main 共用同一路径）。"""

    def _args(self, tmp: Path, **overrides):
        draft_file = tmp / "draft.json"
        draft_file.write_text(json.dumps({"title": "论文快报", "body": "正文", "topics": ["AI论文"]}),
                              encoding="utf-8")
        fields = dict(draft=draft_file, image=(tmp / "figure.png",), pdf=None,
                      skip_pdf_attachment=False, skip_topic_binding=False)
        fields.update(overrides)
        return argparse.Namespace(**fields)

    def test_pdf_and_waiver_are_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.7")
            with self.assertRaises(ValueError):
                build_deliver_payload(self._args(Path(folder), pdf=pdf, skip_pdf_attachment=True))

    def test_waiver_without_pdf_builds_payload(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = build_deliver_payload(self._args(Path(folder), skip_pdf_attachment=True))
        self.assertIsNone(payload.pdf_path)
        self.assertFalse(payload.require_pdf_attachment)
        self.assertTrue(payload.require_real_topics)


if __name__ == "__main__":
    unittest.main()
