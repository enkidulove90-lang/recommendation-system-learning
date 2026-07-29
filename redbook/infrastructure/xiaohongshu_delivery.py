"""The only supported Xiaohongshu draft delivery adapter.

It deliberately uses OpenCLI's creator UI plus Browser Bridge CDP.  A run is
successful only after all three platform-side requirements have completed:
the image draft exists, real topic entities were selected by ``--topics``, and
the downloaded paper PDF is visible in the editor as an attached file.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import time
from typing import Callable


class DeliveryError(RuntimeError):
    """A platform-side prerequisite was not completed; never silently downgrade."""


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


@dataclass(frozen=True)
class DraftPayload:
    title: str
    body: str
    image_paths: tuple[Path, ...]
    topics: tuple[str, ...]
    pdf_path: Path

    def validate(self) -> None:
        if not self.title or len(self.title) > 20:
            raise DeliveryError("Xiaohongshu title is required and must contain at most 20 characters")
        if not self.body.strip() or not self.image_paths:
            raise DeliveryError("body and at least one image are required")
        if not self.topics:
            raise DeliveryError("real topic binding is mandatory; do not fall back to body hashtags")
        missing = [str(path) for path in (*self.image_paths, self.pdf_path) if not path.is_file()]
        if missing:
            raise DeliveryError(f"missing local delivery assets: {missing}")
        if self.pdf_path.suffix.casefold() != ".pdf":
            raise DeliveryError("the paper attachment must be a PDF")


@dataclass(frozen=True)
class DeliveryReceipt:
    draft_id: str
    title: str
    image_count: int
    topics: tuple[str, ...]
    pdf_name: str


class OpenCliXiaohongshuDelivery:
    """Save an image note as a draft, bind topics, then attach its local PDF by CDP."""

    creator_url = "https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image"

    def __init__(self, runner: Runner = _run, session: str = "redbook-daily-pdf") -> None:
        self.runner, self.session = runner, session

    def _command(self, *parts: str) -> list[str]:
        return ["opencli", *parts]

    def _drafts(self) -> list[dict]:
        result = self.runner(self._command("xiaohongshu", "drafts", "-f", "json", "--window", "background", "--site-session", "ephemeral"))
        if result.returncode:
            raise DeliveryError(result.stderr or result.stdout or "cannot read Xiaohongshu drafts")
        try:
            return list(json.loads(result.stdout))
        except json.JSONDecodeError as error:
            raise DeliveryError("Xiaohongshu drafts returned invalid JSON") from error

    @staticmethod
    def _new_draft(before: list[dict], after: list[dict], title: str) -> dict:
        known = {str(item.get("id")) for item in before}
        candidates = [item for item in after if str(item.get("id")) not in known and item.get("title") == title]
        if len(candidates) != 1:
            raise DeliveryError(f"expected exactly one newly saved draft for {title!r}, got {len(candidates)}")
        return candidates[0]

    def _delete(self, draft_id: str) -> None:
        self.runner(self._command("xiaohongshu", "draft-delete", draft_id, "--execute", "-f", "json", "--window", "background", "--site-session", "ephemeral"))

    def save_image_draft(self, payload: DraftPayload) -> dict:
        payload.validate()
        before = self._drafts()
        result = self.runner(self._command(
            "xiaohongshu", "publish", payload.body,
            "--title", payload.title,
            "--images", ",".join(str(path) for path in payload.image_paths),
            "--topics", ",".join(payload.topics),
            "--draft", "true", "--window", "foreground", "--site-session", "ephemeral", "--keep-tab", "false", "-f", "json",
        ))
        # OpenCLI may save an incomplete draft before reporting a topic-selection
        # failure.  Detect and delete that partial result instead of treating it
        # as successful or downgrading to plain #hashtags.
        after = self._drafts()
        try:
            draft = self._new_draft(before, after, payload.title)
        except DeliveryError:
            draft = None
        if result.returncode or not draft:
            if draft:
                self._delete(str(draft["id"]))
            raise DeliveryError(result.stderr or result.stdout or "topic entity binding did not complete")
        if int(draft.get("images", 0)) != len(payload.image_paths):
            self._delete(str(draft["id"]))
            raise DeliveryError("saved draft image count differs from the verified manifest")
        return draft

    def attach_pdf_by_cdp(self, title: str, pdf_path: Path) -> None:
        """Edit the just-created draft and assert the attachment filename becomes visible.

        The selectors intentionally use visible product text rather than legacy
        hashed CSS classes.  Browser Bridge implements CDP DOM.setFileInputFiles
        behind ``opencli browser upload``.
        """
        commands = [
            self._command("browser", self.session, "open", self.creator_url, "--window", "foreground"),
            self._command("browser", self.session, "click", "--text", "草稿箱"),
            self._command("browser", self.session, "click", "--text", title),
            self._command("browser", self.session, "click", "--text", "添加组件"),
            self._command("browser", self.session, "click", "--text", "文件"),
            self._command("browser", self.session, "upload", 'input[type="file"][accept*=".pdf"]', str(pdf_path)),
            self._command("browser", self.session, "wait", "text", pdf_path.name, "--timeout", "30000"),
        ]
        for command in commands:
            result = self.runner(command)
            if result.returncode:
                raise DeliveryError(result.stderr or result.stdout or f"CDP PDF attachment failed: {' '.join(command[:4])}")

    def deliver(self, payload: DraftPayload) -> DeliveryReceipt:
        draft = self.save_image_draft(payload)
        try:
            self.attach_pdf_by_cdp(payload.title, payload.pdf_path)
        except Exception:
            self._delete(str(draft["id"]))
            raise
        return DeliveryReceipt(
            draft_id=str(draft["id"]), title=payload.title, image_count=len(payload.image_paths),
            topics=payload.topics, pdf_name=payload.pdf_path.name,
        )
