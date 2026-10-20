"""One-command delivery for an already qualified paper bundle, draft-only."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Callable

from .common import write_json
from .content_operations import ContentOperationError, PaperCardStore, ReviewQueue, XiaohongshuPaperRenderer


class OneClickEligibilityError(RuntimeError):
    """A paper must be fully qualified before the platform is touched."""


Executor = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _execute(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


class QualifiedPaperDraftDelivery:
    """Deliver exactly one verified local paper bundle through save-xhs-draft."""

    def __init__(self, executor: Executor = _execute) -> None:
        self.executor = executor

    @staticmethod
    def _required(manifest: dict, manifest_path: Path) -> tuple[Path, Path, list[Path], Path]:
        artifacts = dict(manifest.get("local_artifacts", {}))
        links = dict(manifest.get("links", {}))
        pdf = Path(str(artifacts.get("pdf", "")))
        markdown = Path(str(artifacts.get("mineru_markdown", "")))
        draft = Path(str(artifacts.get("structured_draft", "")))
        figures = [Path(str(row.get("path", ""))) for row in manifest.get("selected_figures", [])]
        missing = [str(path) for path in (pdf, markdown, draft, *figures) if not path.is_file()]
        if not links.get("github"):
            missing.append("official GitHub link")
        if len(figures) < 4:
            missing.append("four qualified figures")
        if missing:
            raise OneClickEligibilityError(f"qualified delivery blocked: {', '.join(missing)}")
        return pdf, markdown, figures, draft

    def deliver(self, manifest_path: Path, title: str | None = None, topics: tuple[str, ...] = ()) -> dict:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("mode") != "draft_only":
            raise OneClickEligibilityError("one-click delivery only supports draft_only")
        if manifest.get("status") == "saved_draft_only":
            raise OneClickEligibilityError("paper already has a saved draft; refuse duplicate delivery")
        pdf, _markdown, figures, draft = self._required(manifest, manifest_path)
        selected_topics = topics or tuple(str(topic) for topic in manifest.get("topics", []) if str(topic).strip())
        if selected_topics:
            draft_payload = json.loads(draft.read_text(encoding="utf-8"))
            draft_payload["topics"] = list(selected_topics)
            overridden_draft = manifest_path.parent / "one_click_payload.json"
            write_json(overridden_draft, draft_payload)
            draft = overridden_draft
        paper_id = str(manifest.get("paper_id", "paper"))
        receipt_path = manifest_path.parent / "one_click_delivery_receipt.json"
        command = [sys.executable, "-m", "redbook.cli", "save-xhs-draft", "--draft", str(draft)]
        if title:
            command.extend(["--title", title])
        for figure in figures:
            command.extend(["--image", str(figure)])
        command.extend(["--pdf", str(pdf), "--output", str(receipt_path)])
        result = self.executor(command)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout or f"one-click delivery failed for {paper_id}")
        # The nested CLI writes this receipt as UTF-8.  Read that authoritative
        # file instead of reparsing captured Windows console output, whose
        # inherited GBK code page can replace Chinese topic names after the
        # platform delivery has already succeeded.
        if not receipt_path.is_file():
            raise RuntimeError("one-click delivery returned without a local receipt")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("state") != "saved_draft_only" or not receipt.get("draft_id"):
            raise RuntimeError("one-click delivery returned no saved draft receipt")
        manifest.update({
            "status": "saved_draft_only", "draft_id": receipt["draft_id"],
            "topics_entity_bound": True, "pdf_attachment_verified": True,
            "delivery_receipt": str(receipt_path),
        })
        write_json(manifest_path, manifest)
        return receipt

    def deliver_paper_card(self, card_path: Path, title: str | None = None) -> dict:
        """Production route: render and deliver strictly from one paper card."""
        card = PaperCardStore.load(card_path, require_delivery_assets=True)
        if dict(card.get("delivery", {})).get("state") == "staged":
            raise OneClickEligibilityError("paper_card already has a staged Xiaohongshu draft; refuse duplicate delivery")
        queue = ReviewQueue(card_path.parents[2])
        record = queue.create(card_path, card)
        preparation_states = ("discovered", "qualified", "evidence_ready", "draft_ready")
        current = str(record["state"])
        if current not in preparation_states:
            raise OneClickEligibilityError(f"paper review record is not retryable from state: {current}")
        for state in preparation_states[preparation_states.index(current) + 1:]:
            try:
                record = queue.transition(str(card["paper_id"]), state, content_hash=card["content_hash"])
            except ContentOperationError as error:
                raise OneClickEligibilityError(str(error)) from error
        draft = XiaohongshuPaperRenderer.render(card)
        draft_path = card_path.parent / "xiaohongshu_research_evidence_draft.json"
        write_json(draft_path, draft)
        assets = dict(card["assets"])
        figures = [Path(str(row.get("path", ""))) for row in assets["figures"]]
        receipt_path = card_path.parent / "delivery_receipt.json"
        command = [sys.executable, "-m", "redbook.cli", "save-xhs-draft", "--draft", str(draft_path)]
        if title:
            command.extend(["--title", title])
        for figure in figures:
            command.extend(["--image", str(figure)])
        command.extend(["--pdf", str(assets["local_pdf"]), "--output", str(receipt_path)])
        result = self.executor(command)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout or f"paper-card delivery failed for {card['paper_id']}")
        if not receipt_path.is_file():
            raise RuntimeError("paper-card delivery returned without a local receipt")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("state") != "saved_draft_only" or not receipt.get("draft_id"):
            raise RuntimeError("paper-card delivery returned no saved draft receipt")
        card = dict(card)
        card["delivery"] = {"mode": "draft_only", "state": "staged", "draft_id": receipt["draft_id"],
                            "receipt": str(receipt_path), "rendered_draft": str(draft_path),
                            "topics_entity_bound": True, "pdf_attachment_verified": True}
        PaperCardStore().write(card_path, card)
        queue.transition(str(card["paper_id"]), "staged", draft_id=receipt["draft_id"], receipt=str(receipt_path))
        return receipt
