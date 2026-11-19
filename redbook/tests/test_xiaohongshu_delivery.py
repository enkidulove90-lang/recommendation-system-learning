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
        self.marker_calls = 0

    def __call__(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        joined = "\x1f".join(command)
        if any(rule in joined for rule in self.fail_rules):
            return subprocess.CompletedProcess(command, 1, "", "simulated failure")
        if "xiaohongshu\x1fdrafts" in joined:
            return subprocess.CompletedProcess(command, 0, self.drafts.pop(0) if self.drafts else "[]", "")
        if "browser" in command:
            sub = command[command.index("browser") + 1]
            if sub == "eval":
                js = command[command.index("eval") + 1]
                for needle, response in self.eval_rules.items():
                    if needle in js:
                        return subprocess.CompletedProcess(command, 0, response, "")
                if "const marker='#'+topicName+'[话题]'" in js:
                    self.marker_calls += 1
                    return subprocess.CompletedProcess(
                        command, 0,
                        '{"ok":true,"count":' + ("0" if self.marker_calls == 1 else "1") + "}", "",
                    )
                if "for(var t of document.querySelectorAll('.tag-group" in js:
                    return subprocess.CompletedProcess(command, 0, '["AI论文"]', "")
                if "if((t.innerText||'').replace(/\\s+/g,' ').trim()===want)" in js:
                    return subprocess.CompletedProcess(command, 0, '{"ok": true}', "")
                return subprocess.CompletedProcess(command, 0, '{"ok": true}', "")
        return subprocess.CompletedProcess(command, 0, "{}", "")


class ScriptedVerificationDelivery(OpenCliXiaohongshuDelivery):
    """Exercise the real save flow while supplying the post-save platform readback."""

    def __init__(self, runner: FakeRunner, verification: dict) -> None:
        super().__init__(runner=runner)
        self.verification = verification
        self.checks: list[tuple[str, str, tuple[str, ...], str]] = []

    def _verify_saved_draft(self, draft_id: str, payload: DraftPayload) -> dict:
        self.checks.append((draft_id, payload.body, payload.topics, payload.pdf_path.name))
        return self.verification


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

    def test_incomplete_saved_draft_is_removed_after_readback(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            drafts = ('[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]')
            runner = FakeRunner(drafts=drafts)
            delivery = ScriptedVerificationDelivery(
                runner, {"ok": False, "error": "saved body does not match expected text"}
            )
            with self.assertRaisesRegex(DeliveryError, "saved body does not match"):
                delivery.deliver(self._payload(Path(folder)))
        self.assertEqual(delivery.checks, [("draft-1", "正文", ("AI论文",), "paper.pdf")])
        self.assertTrue(any("draft-delete" in call for call in runner.calls))

    def test_open_editor_releases_stale_session_before_navigating(self) -> None:
        runner = FakeRunner()
        OpenCliXiaohongshuDelivery(runner=runner)._open_editor()
        browser_calls = [call for call in runner.calls if "browser" in call]
        first = browser_calls[0]
        second = browser_calls[1]
        self.assertEqual(first[first.index("browser") + 1], "close")
        self.assertEqual(second[second.index("browser") + 1], "open")

    def test_drafts_accepts_opencli_v2_data_envelope(self) -> None:
        runner = FakeRunner(drafts=['{"ok":true,"data":[{"id":"s:new","title":"draft"}]}'])
        drafts = OpenCliXiaohongshuDelivery(runner=runner)._drafts()
        self.assertEqual(drafts, [{"id": "s:new", "title": "draft"}])

    def test_topic_without_exact_match_raises_and_skips(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(
                eval_rules={"const marker='#'+topicName+'[话题]'": '{"ok": true, "count": 0}'})
            with self.assertRaises(TopicEntityUnavailable):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(self._payload(Path(folder)))
        deletes = [call for call in runner.calls if "draft-delete" in call]
        self.assertEqual(deletes, [], "nothing was saved, so nothing may be deleted")

    def test_topic_binding_clicks_real_creator_chip_without_native_typing(self) -> None:
        runner = FakeRunner(eval_rules={
            "for(var t of document.querySelectorAll('.tag-group": '["AI论文"]',
            "if((t.innerText||'').replace(/\\s+/g,' ').trim()===want)": '{"ok": true}',
        })
        delivery = OpenCliXiaohongshuDelivery(runner=runner)
        self.assertEqual(delivery._bind_topics(("AI论文",)), 1)
        self.assertFalse(any("browser\\x1ftype" in "\\x1f".join(call) for call in runner.calls))
        click_eval = next(call for call in runner.calls if "click real topic chip" not in call
                          and "browser" in call and "eval" in call
                          and "document.querySelectorAll('.tag')" in "\\n".join(call))
        self.assertIn("replace(/^#/,''", "\\n".join(click_eval))

    def test_missing_creator_chip_raises_unavailable_without_native_typing(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(eval_rules={
                "for(var t of document.querySelectorAll('.tag-group": '[]',
            })
            with self.assertRaises(TopicEntityUnavailable):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(self._payload(Path(folder)))
        self.assertFalse(any("browser\x1ftype" in "\x1f".join(call) for call in runner.calls))

    def test_missing_creator_chip_has_stable_error_code(self) -> None:
        runner = FakeRunner(eval_rules={"for(var t of document.querySelectorAll('.tag-group": '[]'})
        with self.assertRaises(TopicEntityUnavailable) as error:
            OpenCliXiaohongshuDelivery(runner=runner)._bind_topics(("AI论文",))
        self.assertEqual(error.exception.code, "E_TOPIC_UNAVAILABLE")

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
