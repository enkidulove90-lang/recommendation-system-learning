from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from redbook.infrastructure.xiaohongshu_delivery import DraftPayload, DeliveryError, OpenCliXiaohongshuDelivery


class FakeRunner:
    def __init__(self, drafts: list[str], publish_code: int = 0) -> None:
        self.drafts, self.publish_code, self.calls = drafts, publish_code, []

    def __call__(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        if command[1:3] == ["xiaohongshu", "drafts"]:
            return subprocess.CompletedProcess(command, 0, self.drafts.pop(0), "")
        if command[1:3] == ["xiaohongshu", "publish"]:
            return subprocess.CompletedProcess(command, self.publish_code, "saved" if not self.publish_code else "topic failed", "")
        return subprocess.CompletedProcess(command, 0, "{}", "")


class XiaohongshuDeliveryTests(unittest.TestCase):
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
        publish = next(call for call in runner.calls if call[1:3] == ["xiaohongshu", "publish"])
        self.assertIn("--topics", publish)
        self.assertEqual(publish[publish.index("--topics") + 1], "AI论文")
        self.assertIn("--draft", publish)

    def test_topic_failure_cleans_partial_draft(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            runner = FakeRunner(['[]', '[{"id":"draft-1", "title":"论文快报", "images":1}]'], publish_code=1)
            delivery = OpenCliXiaohongshuDelivery(runner=runner)
            with self.assertRaises(DeliveryError):
                delivery.save_image_draft(self._payload(Path(folder)))
        delete = next(call for call in runner.calls if call[1:3] == ["xiaohongshu", "draft-delete"])
        self.assertIn("--execute", delete)

    def test_missing_topics_fails_before_platform_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            payload = self._payload(Path(folder))
            payload = DraftPayload(payload.title, payload.body, payload.image_paths, (), payload.pdf_path)
            runner = FakeRunner([])
            with self.assertRaises(DeliveryError):
                OpenCliXiaohongshuDelivery(runner=runner).save_image_draft(payload)
        self.assertEqual(runner.calls, [])
