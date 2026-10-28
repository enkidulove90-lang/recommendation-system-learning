from __future__ import annotations

import base64
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from redbook.infrastructure.xiaohongshu_delivery import (
    DraftPayload,
    DeliveryError,
    OpenCliXiaohongshuDelivery,
    TopicEntityUnavailable,
)


class FakeRunner:
    def __init__(self, drafts: list[str], publish_code: int = 0, publish_output: str = "") -> None:
        self.drafts, self.publish_code, self.publish_output, self.calls = drafts, publish_code, publish_output, []

    def __call__(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        app_index = command.index("xiaohongshu")
        app_command = command[app_index:app_index + 2]
        if app_command == ["xiaohongshu", "drafts"]:
            return subprocess.CompletedProcess(command, 0, self.drafts.pop(0), "")
        if app_command == ["xiaohongshu", "publish"]:
            output = self.publish_output or ("saved" if not self.publish_code else "topic failed")
            return subprocess.CompletedProcess(command, self.publish_code, output, "")
        return subprocess.CompletedProcess(command, 0, "{}", "")


class XiaohongshuDeliveryTests(unittest.TestCase):
    def test_default_browser_sessions_are_disposable_per_delivery(self) -> None:
        left = OpenCliXiaohongshuDelivery(runner=FakeRunner([]))
        right = OpenCliXiaohongshuDelivery(runner=FakeRunner([]))

        self.assertNotEqual(left.session, right.session)
        self.assertTrue(left.session.startswith("redbook-draft-"))

    def test_delivery_accepts_nine_images_and_rejects_ten_before_platform_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            nine = DraftPayload(payload.title, payload.body, payload.image_paths * 9, payload.topics, payload.pdf_path)
            nine.validate()
            ten = DraftPayload(payload.title, payload.body, payload.image_paths * 10, payload.topics, payload.pdf_path)
            with self.assertRaisesRegex(DeliveryError, "at most 9 images"):
                ten.validate()

    def _payload(self, root: Path) -> DraftPayload:
        image, pdf = root / "figure.png", root / "paper.pdf"
        image.write_bytes(b"png")
        pdf.write_bytes(b"%PDF-1.7")
        return DraftPayload("论文快报", "正文", (image,), ("AI论文",), pdf)

    def test_topic_binding_is_passed_to_opencli(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(['[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]'])
            delivery = OpenCliXiaohongshuDelivery(runner=runner)
            draft = delivery.save_image_draft(self._payload(Path(folder)))
        self.assertEqual(draft["id"], "draft-1")
        publish = next(call for call in runner.calls if call[call.index("xiaohongshu"):call.index("xiaohongshu") + 2] == ["xiaohongshu", "publish"])
        self.assertIn("--topics", publish)
        self.assertEqual(publish[publish.index("--topics") + 1], "AI论文")
        self.assertIn("--draft", publish)
        self.assertEqual(publish[publish.index("--site-session") + 1], "persistent")
        self.assertEqual(publish[publish.index("--keep-tab") + 1], "true")

    def test_drafts_accepts_opencli_v2_result_envelope(self) -> None:
        runner = FakeRunner(['{"ok":true,"data":[{"id":"draft-1","title":"论文快报","images":1}]}'])
        drafts = OpenCliXiaohongshuDelivery(runner=runner)._drafts()
        self.assertEqual(drafts, [{"id": "draft-1", "title": "论文快报", "images": 1}])

    def test_topic_failure_cleans_partial_draft(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(['[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]'], publish_code=1)
            delivery = OpenCliXiaohongshuDelivery(runner=runner)
            with self.assertRaises(DeliveryError):
                delivery.save_image_draft(self._payload(Path(folder)))
        delete = next(call for call in runner.calls if call[call.index("xiaohongshu"):call.index("xiaohongshu") + 2] == ["xiaohongshu", "draft-delete"])
        self.assertIn("--execute", delete)

    def test_unavailable_topic_entity_cleans_draft_and_skips_paper(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(
                ['[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]'],
                publish_code=1,
                publish_output='Could not attach topic "人工智能": no real topic entity appeared after selection',
            )
            delivery = OpenCliXiaohongshuDelivery(runner=runner)
            with self.assertRaises(TopicEntityUnavailable) as raised:
                delivery.save_image_draft(self._payload(Path(folder)))
        self.assertEqual(raised.exception.topics, ("人工智能",))
        self.assertIn("skip the current paper", str(raised.exception))
        delete = next(call for call in runner.calls if call[call.index("xiaohongshu"):call.index("xiaohongshu") + 2] == ["xiaohongshu", "draft-delete"])
        self.assertIn("--execute", delete)

    def test_missing_topics_fails_before_platform_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(payload.title, payload.body, payload.image_paths, (), payload.pdf_path)
            runner = FakeRunner([])
            with self.assertRaises(DeliveryError):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(payload)
        self.assertEqual(runner.calls, [])

    def test_explicit_pdf_waiver_allows_a_private_image_draft_without_attachment(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            waived = DraftPayload(
                payload.title, payload.body, payload.image_paths, payload.topics, None,
                require_pdf_attachment=False,
            )
            waived.validate()
            delivery = OpenCliXiaohongshuDelivery(runner=FakeRunner([]))
            delivery.attach_pdf_by_cdp = lambda *_: self.fail("waived draft must not upload a PDF")  # type: ignore[method-assign]
            prepared = DraftPayload(
                waived.title, waived.body, waived.image_paths, (), None,
                require_real_topics=False, resume_prepared_editor=True, require_pdf_attachment=False,
            )
            delivery._prepare_editor_before_draft_save(prepared)

        self.assertIsNone(waived.pdf_path)

    def test_plain_hashtag_mode_allows_empty_entities_and_omits_topics_option(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(
                payload.title, f"{payload.body}\n\n#论文解读", payload.image_paths, (), payload.pdf_path,
                require_real_topics=False,
            )
            runner = FakeRunner(['[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]'])
            OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(payload)
        publish = next(call for call in runner.calls if call[call.index("xiaohongshu"):call.index("xiaohongshu") + 2] == ["xiaohongshu", "publish"])
        self.assertNotIn("--topics", publish)
        self.assertEqual(publish[-1], "正文\n\n#论文解读")

    def test_draft_polling_handles_creator_list_lag_after_success(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner([
                '[]',
                '[]',
                '[{"id":"draft-1", "title":"论文快报", "images":1}]',
            ])
            delivery = OpenCliXiaohongshuDelivery(runner=runner, draft_poll_attempts=2, draft_poll_interval=0)
            draft = delivery.save_image_draft(self._payload(Path(folder)))
        self.assertEqual(draft["id"], "draft-1")

    def test_dom_click_waits_for_delayed_creator_control(self) -> None:
        states = iter(["", "[42]<div>论文快报</div>"])
        calls: list[list[str]] = []

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if "state" in command and command[-2:] == ["--source", "dom"]:
                return subprocess.CompletedProcess(command, 0, next(states), "")
            if "--text" in command:
                return subprocess.CompletedProcess(command, 1, "not found", "")
            if "eval" in command:
                return subprocess.CompletedProcess(command, 1, "not found", "")
            return subprocess.CompletedProcess(command, 0, "", "")

        delivery = OpenCliXiaohongshuDelivery(runner=runner, dom_poll_attempts=2, dom_poll_interval=0)
        delivery._click_dom_text("论文快报")
        self.assertEqual(len(calls), 5)
        self.assertEqual(calls[-1][-2:], ["click", "42"])

    def test_pdf_attachment_stays_in_existing_editor_session(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.7")
            states = iter(["[10]<button>添加组件</button>", "[11]<div>文件</div>"])
            calls: list[list[str]] = []

            def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
                calls.append(command)
                if "state" in command:
                    return subprocess.CompletedProcess(command, 0, next(states), "")
                return subprocess.CompletedProcess(command, 0, "", "")

            OpenCliXiaohongshuDelivery(runner=runner, dom_poll_interval=0).attach_pdf_by_cdp("论文快报", pdf)

        self.assertFalse(any("open" in call for call in calls))
        self.assertTrue(any("upload" in call for call in calls))
        self.assertFalse(any("click" in call for call in calls))

    def test_real_topic_delivery_attaches_pdf_before_clicking_save(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(payload.title, "正文\n\n#论文解读", payload.image_paths, (), payload.pdf_path, False)
            runner = FakeRunner(['[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]'])
            delivery = OpenCliXiaohongshuDelivery(runner=runner, draft_poll_interval=0)
            events: list[str] = []

            def prepare(value: DraftPayload) -> None:
                events.append("pdf_attached")

            def save(before: list[dict], value: DraftPayload) -> dict:
                events.append("draft_saved")
                return {"id": "draft-1", "title": value.title, "images": 1}

            delivery._prepare_editor_before_draft_save = prepare  # type: ignore[method-assign]
            delivery._save_editor_as_draft = save  # type: ignore[method-assign]
            receipt = delivery._deliver_with_pre_save_pdf(payload)

        self.assertEqual(events, ["pdf_attached", "draft_saved"])
        self.assertEqual(receipt.pdf_name, "paper.pdf")

    def test_deliver_rejects_plain_hashtag_fallback_before_platform_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(
                payload.title, payload.body, payload.image_paths, (), payload.pdf_path,
                require_real_topics=False,
            )
            runner = FakeRunner([])
            with self.assertRaisesRegex(DeliveryError, "plain body hashtags"):
                OpenCliXiaohongshuDelivery(runner=runner).deliver(payload)
        self.assertEqual(runner.calls, [])

    def test_strict_delivery_uses_the_presave_transaction_not_legacy_publish(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            delivery = OpenCliXiaohongshuDelivery(runner=FakeRunner(['[]']))
            events: list[str] = []

            def prepare(value: DraftPayload) -> None:
                events.append("topic_then_pdf")

            def save(before: list[dict], value: DraftPayload) -> dict:
                events.append("save")
                return {"id": "draft-1", "title": value.title, "images": len(value.image_paths)}

            delivery._prepare_editor_before_draft_save = prepare  # type: ignore[method-assign]
            delivery._save_editor_as_draft = save  # type: ignore[method-assign]
            delivery.save_image_draft = lambda _: self.fail("legacy publish route must not run")  # type: ignore[method-assign]
            receipt = delivery.deliver(payload)

        self.assertEqual(events, ["topic_then_pdf", "save"])
        self.assertEqual(receipt.draft_id, "draft-1")

    def test_delivery_refuses_same_title_draft_before_editing_the_creator(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            runner = FakeRunner(['[{"id":"prior", "title":"论文快报", "images":4}]'])
            delivery = OpenCliXiaohongshuDelivery(runner=runner)
            delivery._prepare_editor_before_draft_save = lambda _: self.fail("must not edit an existing draft")  # type: ignore[method-assign]
            with self.assertRaisesRegex(DeliveryError, "existing same-title draft"):
                delivery.deliver(payload)
        self.assertEqual(len(runner.calls), 1)

    def test_delivery_allows_only_explicit_id_matched_resume_of_auto_saved_draft(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(
                payload.title, payload.body, payload.image_paths, payload.topics, payload.pdf_path,
                resume_prepared_editor=True, resume_draft_id="prior",
            )
            runner = FakeRunner(['[{"id":"prior", "title":"论文快报", "images":1}]'])
            delivery = OpenCliXiaohongshuDelivery(runner=runner)
            events: list[str] = []
            delivery._prepare_editor_before_draft_save = lambda _: events.append("prepared")  # type: ignore[method-assign]
            delivery._save_editor_as_draft = lambda _, value: {  # type: ignore[method-assign]
                "id": value.resume_draft_id, "title": value.title, "images": 1
            }
            receipt = delivery.deliver(payload)
        self.assertEqual(events, ["prepared"])
        self.assertEqual(receipt.draft_id, "prior")

    def test_native_topic_picker_requires_a_real_tiptap_entity(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            calls: list[list[str]] = []

            def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
                calls.append(command)
                if "eval" in command and "tiptap-topic[data-topic]" in command[-1]:
                    return subprocess.CompletedProcess(command, 0, "true", "")
                return subprocess.CompletedProcess(command, 0, "", "")

            OpenCliXiaohongshuDelivery(runner=runner)._bind_real_topics_in_editor(payload)

        self.assertTrue(any("keys" in call and call[-1] == "Enter" for call in calls))
        topic_click = next(call for call in calls if "eval" in call and "[role=tooltip]" in call[-1])
        self.assertIn("exact topic suggestion", topic_click[-1])
        encoded_topic = base64.b64encode("\n#AI论文".encode("utf-8")).decode("ascii")
        native_insert = next(call for call in calls if call[-1] == encoded_topic)
        self.assertTrue(native_insert[1].endswith("opencli_native_input.mjs"))
        verification = next(call[-1] for call in calls if "eval" in call and "tiptap-topic[data-topic]" in call[-1])
        self.assertIn("data-topic", verification)

    def test_native_topic_picker_accepts_opencli_v2_true_eval_envelope(self) -> None:
        """OpenCLI 2 returns browser-eval results inside an ``ok/data`` envelope."""
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))

            def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
                if "eval" in command and "tiptap-topic[data-topic]" in command[-1]:
                    return subprocess.CompletedProcess(command, 0, '{"ok":true,"data":"true"}', "")
                return subprocess.CompletedProcess(command, 0, "", "")

            OpenCliXiaohongshuDelivery(runner=runner)._bind_real_topics_in_editor(payload)

    def test_rich_text_fill_accepts_written_content_when_line_break_verification_differs(self) -> None:
        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 1, '{"filled": true, "verified": false}', "")

        delivery = OpenCliXiaohongshuDelivery(runner=runner)
        delivery._fill_editor_field(("[contenteditable=true]",), "第一行\n第二行", "body")

    def test_rich_text_fill_accepts_creator_paragraph_normalization_only_for_body(self) -> None:
        response = (
            '{"ok":false,"error":{"code":"value_mismatch",'
            '"expected":"第一段\\n\\n第二段",'
            '"actual":"第一段\\n\\n\\n\\n\\n第二段"}}'
        )

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 1, response, "")

        delivery = OpenCliXiaohongshuDelivery(runner=runner)
        delivery._fill_editor_field(("[contenteditable=true]",), "第一段\n\n第二段", "body")
        with self.assertRaisesRegex(DeliveryError, "could not fill the title"):
            delivery._fill_editor_field(("[contenteditable=true]",), "第一段\n\n第二段", "title")

    def test_rich_text_fill_accepts_creator_conversion_of_each_line_to_a_paragraph(self) -> None:
        response = (
            '{"ok":false,"error":{"code":"value_mismatch",'
            '"expected":"标题\\n正文",'
            '"actual":"标题\\n\\n正文"}}'
        )

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 1, response, "")

        OpenCliXiaohongshuDelivery(runner=runner)._fill_editor_field(
            ("[contenteditable=true]",), "标题\n正文", "body"
        )

    def test_resume_prepared_editor_only_attaches_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(payload.title, payload.body, payload.image_paths, (), payload.pdf_path, False, True)
            delivery = OpenCliXiaohongshuDelivery(runner=FakeRunner([]))
            attached: list[Path] = []
            delivery.attach_pdf_by_cdp = lambda title, path: attached.append(path)  # type: ignore[method-assign]
            delivery._prepare_editor_before_draft_save(payload)
        self.assertEqual(attached, [payload.pdf_path])

    def test_dom_click_uses_visible_text_when_control_has_no_numeric_ref(self) -> None:
        calls: list[list[str]] = []

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if "state" in command:
                return subprocess.CompletedProcess(command, 0, "<div>添加组件</div>", "")
            return subprocess.CompletedProcess(command, 0, "", "")

        OpenCliXiaohongshuDelivery(runner=runner, dom_poll_attempts=1)._click_dom_text("添加组件")
        self.assertEqual(calls[-1][-2:], ["--text", "添加组件"])

    def test_dom_click_evaluates_visible_text_when_bridge_semantics_are_empty(self) -> None:
        calls: list[list[str]] = []

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if "state" in command:
                return subprocess.CompletedProcess(command, 0, "<div>添加组件</div>", "")
            if "--text" in command:
                return subprocess.CompletedProcess(command, 1, "not found", "")
            return subprocess.CompletedProcess(command, 0, "clicked:添加组件", "")

        OpenCliXiaohongshuDelivery(runner=runner, dom_poll_attempts=1)._click_dom_text("添加组件")
        self.assertIn("eval", calls[-1])

    def test_dom_click_refreshes_a_stale_numeric_ref(self) -> None:
        calls: list[list[str]] = []
        state_count = 0

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            nonlocal state_count
            calls.append(command)
            if "state" in command:
                state_count += 1
                ref = 125 if state_count == 1 else 126
                return subprocess.CompletedProcess(command, 0, f"[{ref}]<button>论文解读</button>", "")
            if "click" in command and command[-1] == "125":
                return subprocess.CompletedProcess(command, 1, "[not_found] ref=125", "")
            return subprocess.CompletedProcess(command, 0, "clicked", "")

        OpenCliXiaohongshuDelivery(runner=runner, dom_poll_attempts=2, dom_poll_interval=0)._click_dom_text("论文解读")
        self.assertTrue(any("click" in call and call[-1] == "126" for call in calls))

    def test_topic_suggestion_click_uses_live_exact_text_not_snapshot_ref(self) -> None:
        calls: list[list[str]] = []

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, "clicked", "")

        OpenCliXiaohongshuDelivery(runner=runner)._click_exact_topic_suggestion("论文解读")
        self.assertIn("[role=tooltip]", calls[-1][-1])
        self.assertIn("exact topic suggestion", calls[-1][-1])

    def test_creator_draft_save_uses_draft_method_not_publish(self) -> None:
        calls: list[list[str]] = []

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, "draft-save:_onSave", "")

        OpenCliXiaohongshuDelivery(runner=runner)._trigger_editor_draft_save()
        script = next(command[-1] for command in calls if "eval" in command)
        self.assertIn("_onSaveDraft", script)
        self.assertNotIn("_onPublish", script)

    def test_resume_attached_editor_skips_duplicate_pdf_upload(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(payload.title, payload.body, payload.image_paths, (), payload.pdf_path, False, True, True)
            delivery = OpenCliXiaohongshuDelivery(runner=FakeRunner([]))
            delivery.attach_pdf_by_cdp = lambda title, path: self.fail("PDF must not be uploaded twice")  # type: ignore[method-assign]
            delivery._prepare_editor_before_draft_save(payload)

    def test_recover_verified_draft_writes_receipt_without_ui_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(payload.title, payload.body, payload.image_paths, (), payload.pdf_path, False, True, True)
            runner = FakeRunner(['[{"id":"draft-1", "title":"论文快报", "images":1}]'])
            receipt = OpenCliXiaohongshuDelivery(runner=runner).recover_verified_draft(payload)
        self.assertEqual(receipt.draft_id, "draft-1")
        self.assertEqual(len(runner.calls), 1)

    def test_windows_invokes_node_entrypoint_without_cmd_url_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shim = root / "npm" / "opencli.cmd"
            entrypoint = root / "npm" / "node_modules" / "@jackwener" / "opencli" / "dist" / "src" / "main.js"
            node = root / "node.exe"
            shim.parent.mkdir(parents=True)
            entrypoint.parent.mkdir(parents=True)
            shim.write_text("shim", encoding="utf-8")
            entrypoint.write_text("entrypoint", encoding="utf-8")
            node.write_text("node", encoding="utf-8")

            def which(name: str) -> str | None:
                return str(shim) if name == "opencli.cmd" else str(node) if name == "node.exe" else None

            with patch("redbook.infrastructure.xiaohongshu_delivery.os.name", "nt"), patch(
                "redbook.infrastructure.xiaohongshu_delivery.shutil.which", side_effect=which
            ):
                command = OpenCliXiaohongshuDelivery(session="session")._command(
                    "browser", "session", "open", "https://example.test/publish?from=menu_left&target=image"
                )

        self.assertEqual(command[:2], [str(node), str(entrypoint)])
        self.assertEqual(command[2:6], ["browser", "--session", "session", "open"])
        self.assertEqual(command[-1], "https://example.test/publish?from=menu_left&target=image")

    def test_dom_ref_resolves_visible_control_text(self) -> None:
        state = "[95]<span>草稿箱(1)</span>\n[125]<button>添加组件</button>"
        self.assertEqual(OpenCliXiaohongshuDelivery._dom_ref_for_text(state, "草稿箱"), 95)
        self.assertEqual(OpenCliXiaohongshuDelivery._dom_ref_for_text(state, "添加组件"), 125)
