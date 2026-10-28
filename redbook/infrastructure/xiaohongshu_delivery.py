"""The only supported Xiaohongshu draft delivery adapter.

It deliberately uses OpenCLI's creator UI plus Browser Bridge CDP.  A run is
successful only after all three platform-side requirements have completed in
one persistent creator editor: real topic entities were selected, the
downloaded paper PDF is visible as an attached file, and the editor was then
saved as a draft.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Callable
from uuid import uuid4


class DeliveryError(RuntimeError):
    """A platform-side prerequisite was not completed; never silently downgrade."""


MAX_DRAFT_IMAGES = 9


class TopicEntityUnavailable(DeliveryError):
    """A requested Xiaohongshu topic has no selectable platform entity.

    This is a terminal eligibility result for the current paper.  It is kept
    distinct from a transient OpenCLI/CDP failure so callers can skip the
    paper instead of retrying it or replacing the entity with body hashtags.
    """

    def __init__(self, topics: tuple[str, ...]) -> None:
        self.topics = topics
        rendered = ", ".join(repr(topic) for topic in topics)
        super().__init__(
            f"real Xiaohongshu topic entity unavailable for {rendered}; "
            "skip the current paper (no body-hashtag fallback)"
        )


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    # The desktop host can expose a non-writable inherited TEMP (for example
    # ``D:\\tmp``).  Browser Bridge needs a writable directory for traces and
    # uploads, so keep its transient data inside the checked-out workspace.
    temp_dir = Path.cwd() / ".redbook_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update({"TEMP": str(temp_dir), "TMP": str(temp_dir)})
    return subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, env=environment
    )


@dataclass(frozen=True)
class DraftPayload:
    title: str
    body: str
    image_paths: tuple[Path, ...]
    topics: tuple[str, ...]
    pdf_path: Path | None
    require_real_topics: bool = True
    resume_prepared_editor: bool = False
    pdf_already_verified: bool = False
    resume_draft_id: str | None = None
    require_pdf_attachment: bool = True

    def validate(self) -> None:
        if not self.title or len(self.title) > 20:
            raise DeliveryError("Xiaohongshu title is required and must contain at most 20 characters")
        if not self.body.strip() or not self.image_paths:
            raise DeliveryError("body and at least one image are required")
        if len(self.image_paths) > MAX_DRAFT_IMAGES:
            raise DeliveryError(f"at most {MAX_DRAFT_IMAGES} images are supported by the current creator upload flow")
        if self.require_real_topics and not self.topics:
            raise DeliveryError("real topic binding is mandatory; do not fall back to body hashtags")
        required_assets = list(self.image_paths)
        if self.require_pdf_attachment:
            if self.pdf_path is None:
                raise DeliveryError("a PDF is required unless the explicit per-run waiver is enabled")
            required_assets.append(self.pdf_path)
        missing = [str(path) for path in required_assets if not path.is_file()]
        if missing:
            raise DeliveryError(f"missing local delivery assets: {missing}")
        if self.require_pdf_attachment and self.pdf_path and self.pdf_path.suffix.casefold() != ".pdf":
            raise DeliveryError("the paper attachment must be a PDF")


@dataclass(frozen=True)
class DeliveryReceipt:
    draft_id: str
    title: str
    image_count: int
    topics: tuple[str, ...]
    pdf_name: str | None


class OpenCliXiaohongshuDelivery:
    """Deliver one complete, draft-only creator-editor transaction.

    The former ``publish --topics --draft`` route saved first and attached the
    PDF afterwards.  It must not be used by :meth:`deliver`: a saved image-only
    draft is an incomplete publication artifact.
    """

    creator_url = "https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image"
    title_selectors = (
        '[contenteditable="true"][placeholder*="标题"]',
        'input[placeholder*="标题"]',
        '[contenteditable="true"][class*="title"]',
        'input[maxlength="20"]',
    )
    body_selectors = (
        '[contenteditable="true"][class*="content"]',
        '[contenteditable="true"][class*="editor"]',
        '[contenteditable="true"][placeholder*="描述"]',
        '[contenteditable="true"][placeholder*="正文"]',
        '[contenteditable="true"]:not([placeholder*="标题"])',
    )

    def __init__(
        self,
        runner: Runner = _run,
        session: str | None = None,
        draft_poll_attempts: int = 12,
        draft_poll_interval: float = 1.0,
        dom_poll_attempts: int = 10,
        dom_poll_interval: float = 1.0,
    ) -> None:
        self.runner = runner
        # Browser Bridge sessions own a selected creator tab.  Reusing a
        # fixed session lets a failed, unsaved editor leak its uploaded images
        # into the next delivery even after its auto-saved draft is deleted.
        # Keep one session for the whole transaction, but make it disposable
        # for each delivery object.  This is intentionally separate from the
        # OpenCLI ``--site-session persistent`` login/cookie session.
        self.session = session or f"redbook-draft-{uuid4().hex}"
        self.draft_poll_attempts = draft_poll_attempts
        self.draft_poll_interval = draft_poll_interval
        self.dom_poll_attempts = dom_poll_attempts
        self.dom_poll_interval = dom_poll_interval

    def _command(self, *parts: str) -> list[str]:
        # OpenCLI 2.0 changed the Browser Bridge grammar from
        # ``browser <session> <command>`` to
        # ``browser --session <session> <command>``. Keep callers expressed
        # in the adapter's session-first form and normalize at this one
        # boundary, including every CDP upload and verification operation.
        if len(parts) >= 3 and parts[0] == "browser" and parts[1] == self.session:
            parts = ("browser", "--session", self.session, *parts[2:])
        # On Windows, executing npm's ``.cmd`` shim through CreateProcess
        # routes arguments through cmd.exe.  That breaks creator URLs because
        # an unquoted ``&target=...`` query fragment is interpreted as a second
        # shell command.  Invoke the installed Node entrypoint directly instead.
        executable = "opencli"
        if os.name == "nt":
            shim = shutil.which("opencli.cmd")
            if shim:
                entrypoint = Path(shim).parent / "node_modules" / "@jackwener" / "opencli" / "dist" / "src" / "main.js"
                node = shutil.which("node.exe") or "node.exe"
                if entrypoint.is_file():
                    return [node, str(entrypoint), *parts]
            executable = shim or "opencli.cmd"
        return [executable, *parts]

    def _drafts(self) -> list[dict]:
        result = self.runner(self._command(
            "xiaohongshu", "drafts", "-f", "json", "--window", "background",
            "--site-session", "persistent", "--keep-tab", "true",
        ))
        if result.returncode:
            raise DeliveryError(result.stderr or result.stdout or "cannot read Xiaohongshu drafts")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise DeliveryError("Xiaohongshu drafts returned invalid JSON") from error
        # OpenCLI 2.0 wraps machine-readable command results in
        # ``{"ok": true, "data": [...]}``, while earlier releases returned
        # the list directly.  Normalize both formats before any lifecycle
        # checks so a version upgrade cannot bypass partial-draft cleanup.
        if isinstance(payload, dict):
            if payload.get("ok") is not True or not isinstance(payload.get("data"), list):
                raise DeliveryError("Xiaohongshu drafts returned an unexpected result envelope")
            payload = payload["data"]
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise DeliveryError("Xiaohongshu drafts returned invalid draft records")
        return payload

    @staticmethod
    def _new_draft(before: list[dict], after: list[dict], title: str) -> dict:
        known = {str(item.get("id")) for item in before}
        candidates = [item for item in after if str(item.get("id")) not in known and item.get("title") == title]
        if len(candidates) != 1:
            raise DeliveryError(f"expected exactly one newly saved draft for {title!r}, got {len(candidates)}")
        return candidates[0]

    def _delete(self, draft_id: str) -> None:
        # Use the same persistent Creator session as ``_drafts``.  Deleting
        # through an ephemeral session can report success while the actual
        # creator draft remains visible to the persistent session.
        result = self.runner(self._command(
            "xiaohongshu", "draft-delete", draft_id, "--execute", "-f", "json", "--window", "background",
            "--site-session", "persistent", "--keep-tab", "false",
        ))
        if result.returncode:
            raise DeliveryError(result.stderr or result.stdout or f"could not delete incomplete draft {draft_id}")

    def _await_new_draft(self, before: list[dict], title: str) -> dict | None:
        """Wait briefly for the creator's eventually consistent draft list."""
        for attempt in range(self.draft_poll_attempts):
            after = self._drafts()
            try:
                return self._new_draft(before, after, title)
            except DeliveryError:
                if attempt + 1 < self.draft_poll_attempts:
                    time.sleep(self.draft_poll_interval)
        return None

    @staticmethod
    def _unavailable_topics(output: str) -> tuple[str, ...]:
        """Extract the platform-selected entities that could not be bound.

        OpenCLI emits this when its topic picker cannot select a real entity,
        for example ``Could not attach topic \"人工智能\": no real topic entity
        appeared after selection``.  Match the stable English API portion so
        the classification remains correct even when the host's console has a
        different code page.
        """
        pattern = re.compile(
            r'Could not attach topic\s+["“](.+?)["”]\s*:\s*'
            r'no real topic entity appeared after selection',
            re.IGNORECASE,
        )
        return tuple(dict.fromkeys(match.group(1).strip() for match in pattern.finditer(output) if match.group(1).strip()))

    def save_image_draft(self, payload: DraftPayload) -> dict:
        payload.validate()
        before = self._drafts()
        publish_parts = [
            "xiaohongshu", "publish",
            "--title", payload.title,
            "--images", ",".join(str(path) for path in payload.image_paths),
        ]
        if payload.topics:
            publish_parts.extend(("--topics", ",".join(payload.topics)))
        publish_parts.extend((
            "--draft", "true", "--window", "foreground", "--site-session", "persistent", "--keep-tab", "true", "-f", "json",
            payload.body,
        ))
        result = self.runner(self._command(*publish_parts))
        # OpenCLI may save an incomplete draft before reporting a topic-selection
        # failure.  Detect and delete that partial result instead of treating it
        # as successful or downgrading to plain #hashtags.
        if result.returncode:
            after = self._drafts()
            try:
                draft = self._new_draft(before, after, payload.title)
            except DeliveryError:
                draft = None
        else:
            draft = self._await_new_draft(before, payload.title)
        if result.returncode or not draft:
            if draft:
                self._delete(str(draft["id"]))
            output = "\n".join(part for part in (result.stderr, result.stdout) if part)
            unavailable = self._unavailable_topics(output)
            if unavailable:
                raise TopicEntityUnavailable(unavailable)
            raise DeliveryError(output or "topic entity binding did not complete")
        if int(draft.get("images", 0)) != len(payload.image_paths):
            self._delete(str(draft["id"]))
            raise DeliveryError("saved draft image count differs from the verified manifest")
        return draft

    def attach_pdf_by_cdp(self, title: str, pdf_path: Path) -> None:
        """Attach a PDF in the same editor session that saved the draft.

        The selectors intentionally use visible product text rather than legacy
        hashed CSS classes.  Browser Bridge implements CDP DOM.setFileInputFiles
        behind ``opencli browser upload``.
        """
        # The editor pre-renders a PDF input even when the component menu is
        # closed. Prefer that stable input; clicking the menu can rerender and
        # invalidate a short-lived "文件" control ref.
        if self._upload_pdf_and_verify(pdf_path):
            return
        for label in ("添加组件", "文件"):
            self._click_dom_text(label)
        if not self._upload_pdf_and_verify(pdf_path):
            raise DeliveryError("CDP PDF attachment failed: no PDF file input became available")

    def _upload_pdf_and_verify(self, pdf_path: Path) -> bool:
        upload = self.runner(self._command(
            "browser", self.session, "upload", 'input[type="file"][accept*=".pdf"]', str(pdf_path),
        ))
        if upload.returncode:
            # Creator's component picker uses the same hidden-input pattern as
            # the image uploader.  Reuse the OpenCLI page-side fallback; the
            # following visible-filename assertion is still mandatory.
            try:
                self._set_file_input_with_native_cdp(
                    (pdf_path,), 'input[type="file"][accept*=".pdf"]',
                )
            except DeliveryError:
                return False
        visible = self.runner(self._command(
            "browser", self.session, "wait", "text", pdf_path.name, "--timeout", "30000",
        ))
        if visible.returncode:
            raise DeliveryError(visible.stderr or visible.stdout or "CDP PDF attachment did not show the local filename")
        return True

    def _click_dom_text(self, label: str) -> None:
        """Click a visible creator control after its asynchronous DOM render."""
        for attempt in range(self.dom_poll_attempts):
            state = self.runner(self._command("browser", self.session, "state", "--source", "dom"))
            if state.returncode:
                raise DeliveryError(state.stderr or state.stdout or "CDP could not inspect the creator DOM")
            ref = self._dom_ref_for_text(state.stdout, label)
            if ref is not None:
                result = self.runner(self._command("browser", self.session, "click", str(ref)))
                if not result.returncode:
                    return
                # Creator suggestion rows are frequently replaced between the
                # snapshot and the click.  A missing numeric ref is a stale
                # observation, not evidence that the requested real topic is
                # absent; re-snapshot and resolve the exact visible row.
                output = "\n".join(part for part in (result.stderr, result.stdout) if part).casefold()
                if "not found" in output or "not_found" in output or "not in dom" in output or "removed" in output:
                    if attempt + 1 < self.dom_poll_attempts:
                        time.sleep(self.dom_poll_interval)
                        continue
                raise DeliveryError(result.stderr or result.stdout or f"CDP could not click creator control: {label}")
            # Some creator controls are visible but intentionally omitted from
            # the numbered DOM snapshot. Browser Bridge can still resolve
            # their rendered text without a numeric ref.
            semantic = self.runner(self._command("browser", self.session, "click", "--text", label))
            if not semantic.returncode:
                return
            # Last-resort CDP path for creator containers which render visible
            # text but expose neither a numeric ref nor an accessibility node.
            # The script throws when no visible exact text exists, so a zero
            # return code still means the click was actually dispatched.
            script = (
                "(() => {"
                f"const label = {json.dumps(label)};"
                "const visible = el => !!el && el.offsetParent !== null;"
                "const text = el => (el.innerText || el.textContent || '').trim();"
                "const target = Array.from(document.querySelectorAll('button, [role=button], div, span'))"
                ".find(el => visible(el) && text(el) === label);"
                "if (!target) throw new Error('visible creator text not found: ' + label);"
                "target.click(); return 'clicked:' + label;"
                "})()"
            )
            evaluated = self.runner(self._command("browser", self.session, "eval", script))
            if not evaluated.returncode:
                return
            if attempt + 1 < self.dom_poll_attempts:
                time.sleep(self.dom_poll_interval)
        raise DeliveryError(f"CDP creator DOM did not expose the required control: {label}")

    def _click_exact_topic_suggestion(self, topic: str) -> None:
        """Click the live picker suggestion without retaining a stale DOM ref.

        Xiaohongshu replaces suggestion rows while a query is resolving, so a
        ref captured by ``browser state`` can be invalid by the next CDP call.
        The picker itself is a visible tooltip. Querying only that tooltip at
        click time avoids the body editor, which also contains the query text.
        This is the required exact-suggestion action and is not a body-hashtag
        fallback.
        """
        last_error = ""
        for attempt in range(self.dom_poll_attempts):
            script = (
                "(() => {"
                f"const topic = {json.dumps(topic)};"
                "const visible = el => !!el && el.offsetParent !== null;"
                "const normalize = value => (value || '').replace(/\\s+/g, '').replace(/^#/, '');"
                "const tooltips = Array.from(document.querySelectorAll('[role=tooltip], .tippy-box')).filter(visible);"
                "const nodes = tooltips.flatMap(box => [box, ...Array.from(box.querySelectorAll('*'))]).filter(visible);"
                "const target = nodes.find(node => normalize(node.innerText || node.textContent) === normalize(topic));"
                "if (!target) throw new Error('exact topic suggestion not visible: ' + topic);"
                "target.click(); return 'clicked-topic:' + topic;"
                "})()"
            )
            result = self.runner(self._command("browser", self.session, "eval", script))
            if not result.returncode:
                return
            last_error = result.stderr or result.stdout or last_error
            if attempt + 1 < self.dom_poll_attempts:
                time.sleep(self.dom_poll_interval)
        raise DeliveryError(last_error or f"CDP creator did not expose the exact topic suggestion: {topic}")

    def _click_any_dom_text(self, labels: tuple[str, ...]) -> None:
        last_error: DeliveryError | None = None
        for label in labels:
            try:
                self._click_dom_text(label)
                return
            except DeliveryError as error:
                last_error = error
        raise last_error or DeliveryError("CDP creator DOM did not expose a save-draft control")

    def _fill_editor_field(self, selectors: tuple[str, ...], value: str, name: str) -> None:
        errors: list[str] = []
        for selector in selectors:
            result = self.runner(self._command("browser", self.session, "fill", selector, value))
            if not result.returncode:
                return
            # Rich-text editors can normalize line breaks into paragraph nodes.
            # Browser Bridge then reports ``filled: true`` but ``verified:
            # false`` because its literal text comparison sees extra blank
            # lines.  The write itself is still successful and must not reset
            # this pre-save editor session.
            for output in (result.stdout, result.stderr):
                try:
                    response = json.loads(output)
                    if response.get("filled") is True:
                        return
                    # Creator represents blank lines as multiple paragraph
                    # separators.  OpenCLI's literal verifier consequently
                    # returns value_mismatch even when every non-whitespace
                    # character was written.  This tolerance is deliberately
                    # limited to the rich-text body and only to runs of three
                    # or more newlines; titles retain exact verification.
                    error = response.get("error") if isinstance(response, dict) else None
                    if (
                        name == "body"
                        and isinstance(error, dict)
                        and error.get("code") == "value_mismatch"
                        and self._normalize_creator_body(str(error.get("expected", "")))
                        == self._normalize_creator_body(str(error.get("actual", "")))
                    ):
                        return
                except (json.JSONDecodeError, AttributeError):
                    pass
            errors.append(result.stderr or result.stdout or selector)
        raise DeliveryError(f"CDP could not fill the {name} field: {' | '.join(errors[-2:])}")

    @staticmethod
    def _normalize_creator_body(value: str) -> str:
        # Creator serializes each visible line as an independent paragraph,
        # so textContent may gain blank-only lines without changing any
        # author-provided characters.  Compare the non-empty line sequence,
        # not the DOM paragraph spacing.
        return "\n".join(line.strip() for line in value.replace("\r\n", "\n").split("\n") if line.strip())

    @staticmethod
    def _browser_eval_is_true(output: str) -> bool:
        """Accept both legacy browser-eval output and OpenCLI 2's JSON envelope."""
        value = output.strip().casefold()
        if value in {"true", '"true"'}:
            return True
        try:
            envelope = json.loads(output)
        except json.JSONDecodeError:
            return False
        if not isinstance(envelope, dict) or envelope.get("ok") is not True:
            return False
        result = envelope.get("data")
        return result is True or (isinstance(result, str) and result.strip().casefold() == "true")

    def _bind_real_topics_in_editor(self, payload: DraftPayload) -> None:
        """Select each topic through the creator's native inline picker.

        The picker is closed-shadow-DOM UI and cannot be selected by a stable
        CSS locator.  We append the query in the live contenteditable, let the
        platform show its inline suggestion, accept it with a real Browser
        Bridge key event, and require its resulting ``tiptap-topic`` entity.
        A literal ``#topic`` is deliberately not accepted as a substitute.
        """
        for topic in payload.topics:
            query = f"#{topic}"
            focus = (
                "(() => {"
                f"const selectors = {json.dumps(self.body_selectors)};"
                "const editor = selectors.flatMap(selector => Array.from(document.querySelectorAll(selector)))"
                ".find(node => node && node.offsetParent !== null && node.isContentEditable);"
                "if (!editor) throw new Error('creator body editor not found');"
                "editor.focus();"
                "const selection = window.getSelection(); const range = document.createRange();"
                "range.selectNodeContents(editor); range.collapse(false);"
                "selection.removeAllRanges(); selection.addRange(range);"
                "return 'topic-caret-ready';"
                "})()"
            )
            separated = self.runner(self._command("browser", self.session, "eval", focus))
            if separated.returncode:
                raise DeliveryError(separated.stderr or separated.stdout or f"could not focus real topic query: {topic}")
            # Keep the paragraph break and query in the same native CDP input
            # transaction.  A standalone bridge ``keys Enter`` can lose the
            # contenteditable focus between commands on the Creator page.
            self._insert_text_at_creator_caret(focus, "\n" + query)
            shown = self.runner(self._command("browser", self.session, "wait", "time", "1.2"))
            if shown.returncode:
                raise DeliveryError(shown.stderr or shown.stdout or f"creator topic picker did not render: {topic}")
            # The inline picker is rendered asynchronously and is often in a
            # closed shadow root.  Do not rely on an assumed auto-highlight:
            # the workflow requires selecting the exact rendered suggestion
            # before Enter.  Browser Bridge's visible-text route reaches the
            # picker even when it lacks a stable light-DOM selector.
            self._click_exact_topic_suggestion(topic)
            committed = self.runner(self._command("browser", self.session, "keys", "Enter"))
            if committed.returncode:
                raise DeliveryError(committed.stderr or committed.stdout or f"could not commit real topic entity: {topic}")
            settled = self.runner(self._command("browser", self.session, "wait", "time", "0.8"))
            if settled.returncode:
                raise DeliveryError(settled.stderr or settled.stdout or f"creator topic selection did not settle: {topic}")
            verify = (
                "(() => {"
                f"const topic = {json.dumps(topic)};"
                "const normalize = value => (value || '').replace(/\\s+/g, '').replace(/^#/, '');"
                "const linked = Array.from(document.querySelectorAll('a.tiptap-topic[data-topic]')).some(node => {"
                "  const raw = node.getAttribute('data-topic');"
                "  try { if (normalize(JSON.parse(raw || '{}').name) === normalize(topic)) return true; } catch (_) {}"
                "  return normalize(node.innerText || node.textContent) === normalize(topic);"
                "});"
                "const editor = " + json.dumps(self.body_selectors) + ".flatMap(selector => Array.from(document.querySelectorAll(selector)))"
                ".find(node => node && node.offsetParent !== null && node.isContentEditable);"
                "const marker = '#' + topic + '[\\u8bdd\\u9898]';"
                "const marked = !!editor && (editor.innerText || editor.textContent || '').replace(/\\s+/g, '').includes(marker);"
                "return linked || marked;"
                "})()"
            )
            verified = self.runner(self._command("browser", self.session, "eval", verify))
            if verified.returncode or not self._browser_eval_is_true(verified.stdout):
                raise TopicEntityUnavailable((topic,))

    def _insert_text_at_creator_caret(self, focus_script: str, text: str) -> None:
        """Append Unicode text via OpenCLI's native CDP ``Input.insertText`` path."""
        if os.name != "nt":
            raise DeliveryError("OpenCLI native CDP text insertion is unavailable on this host")
        shim = shutil.which("opencli.cmd")
        if not shim:
            raise DeliveryError("OpenCLI native CDP text insertion requires the installed opencli.cmd shim")
        package_root = Path(shim).parent / "node_modules" / "@jackwener" / "opencli" / "dist" / "src"
        bridge_module = package_root / "browser" / "bridge.js"
        node = shutil.which("node.exe") or "node.exe"
        helper = Path(__file__).with_name("opencli_native_input.mjs")
        if not bridge_module.is_file() or not helper.is_file():
            raise DeliveryError("OpenCLI native CDP text insertion support is not installed")
        # Node on this Windows host receives non-ASCII argv through the active
        # ANSI code page (turning Chinese topic names into ``?``).  Keep the
        # process boundary ASCII-only and recover the exact UTF-8 text in the
        # narrow native-input helper.
        encoded_text = base64.b64encode(text.encode("utf-8")).decode("ascii")
        inserted = self.runner([node, str(helper), str(bridge_module), self.session, focus_script, encoded_text])
        if inserted.returncode:
            raise DeliveryError(inserted.stderr or inserted.stdout or "OpenCLI native CDP text insertion failed")

    def _set_file_input_with_native_cdp(self, files: tuple[Path, ...], selector: str) -> None:
        """Set local input files through OpenCLI inside this editor session.

        Creator's custom image and PDF controls do not always open a browser
        chooser, which makes the generic command-line upload adapter
        unavailable even while the matching ``input[type=file]`` exists in the
        DOM. This remains part of the same ``save-xhs-draft`` transaction: it
        only puts files into the already-open Creator editor and does not save
        or publish.
        """
        if os.name != "nt":
            raise DeliveryError("OpenCLI native CDP file upload is unavailable on this host")
        shim = shutil.which("opencli.cmd")
        if not shim:
            raise DeliveryError("OpenCLI native CDP file upload requires the installed opencli.cmd shim")
        package_root = Path(shim).parent / "node_modules" / "@jackwener" / "opencli" / "dist" / "src"
        bridge_module = package_root / "browser" / "bridge.js"
        helper = Path(__file__).with_name("opencli_native_file_input.mjs")
        node = shutil.which("node.exe") or "node.exe"
        if not bridge_module.is_file() or not helper.is_file():
            raise DeliveryError("OpenCLI native CDP file upload support is not installed")
        encoded_files = base64.b64encode(json.dumps([str(path) for path in files]).encode("utf-8")).decode("ascii")
        uploaded = self.runner([node, str(helper), str(bridge_module), self.session, selector, encoded_files])
        if uploaded.returncode:
            raise DeliveryError(uploaded.stderr or uploaded.stdout or "OpenCLI native CDP image upload failed")

    def _prepare_editor_before_draft_save(self, payload: DraftPayload) -> None:
        """Populate, attach, and verify a note before its first save action."""
        if payload.resume_prepared_editor:
            for topic in payload.topics:
                verify = (
                    "(() => {"
                    f"const topic = {json.dumps(topic)};"
                    "const normalize = value => (value || '').replace(/\\s+/g, '').replace(/^#/, '');"
                "const linked = Array.from(document.querySelectorAll('a.tiptap-topic[data-topic]')).some(node => {"
                "  const raw = node.getAttribute('data-topic');"
                "  try { if (normalize(JSON.parse(raw || '{}').name) === normalize(topic)) return true; } catch (_) {}"
                "  return normalize(node.innerText || node.textContent) === normalize(topic);"
                "});"
                "const editor = " + json.dumps(self.body_selectors) + ".flatMap(selector => Array.from(document.querySelectorAll(selector)))"
                ".find(node => node && node.offsetParent !== null && node.isContentEditable);"
                "const marker = '#' + topic + '[\\u8bdd\\u9898]';"
                "const marked = !!editor && (editor.innerText || editor.textContent || '').replace(/\\s+/g, '').includes(marker);"
                "return linked || marked;"
                "})()"
            )
                verified = self.runner(self._command("browser", self.session, "eval", verify))
                if verified.returncode or not self._browser_eval_is_true(verified.stdout):
                    # A failed run may leave a complete, unsaved editor.  Bind
                    # only its missing topics in that same editor rather than
                    # discarding verified images/text or using a hashtag.
                    self._bind_real_topics_in_editor(DraftPayload(
                        payload.title, payload.body, payload.image_paths, (topic,), payload.pdf_path,
                        require_real_topics=True, resume_prepared_editor=True,
                        require_pdf_attachment=payload.require_pdf_attachment,
                    ))
            if payload.require_pdf_attachment and not payload.pdf_already_verified:
                if payload.pdf_path is None:
                    raise DeliveryError("PDF attachment was required but no local PDF was provided")
                self.attach_pdf_by_cdp(payload.title, payload.pdf_path)
            return
        open_result = self.runner(self._command("browser", self.session, "open", self.creator_url, "--window", "foreground"))
        if open_result.returncode:
            raise DeliveryError(open_result.stderr or open_result.stdout or "CDP could not open the creator page")
        # Creator's accepted-image MIME list changes over time (for example,
        # from a literal ``.jpg`` extension to MIME types).  Keep the precise
        # selector first, then fall back only to visible file inputs in the
        # same fresh editor; the next verification still rejects an incorrect
        # image count before any draft is retained.
        image_result = None
        upload_errors: list[str] = []
        for image_selector in (
            'input[type="file"][multiple][accept*=".jpg"]',
            'input[type="file"][multiple]',
            'input[type="file"]',
        ):
            candidate = self.runner(self._command(
                "browser", self.session, "upload", image_selector,
                *(str(path) for path in payload.image_paths),
            ))
            if not candidate.returncode:
                image_result = candidate
                break
            upload_errors.append(candidate.stderr or candidate.stdout or image_selector)
        if image_result is None:
            # Some Browser Bridge builds cannot resolve a CSS selector to a
            # chooser-backed input, although their freshly captured state has
            # a valid numeric DOM ref.  Retry those refs before failing the
            # transaction; the normal post-upload verification remains the
            # authority on whether the expected images actually arrived.
            state = self.runner(self._command("browser", self.session, "state"))
            file_refs = re.findall(r"\\[(\\d+)\\]<input type=file[^>]*>", state.stdout)
            for ref in file_refs:
                candidate = self.runner(self._command(
                    "browser", self.session, "upload", ref,
                    *(str(path) for path in payload.image_paths),
                ))
                if not candidate.returncode:
                    image_result = candidate
                    break
                upload_errors.append(candidate.stderr or candidate.stdout or f"ref={ref}")
        if image_result is None:
            # Browser Bridge's generic `upload` command first waits for an OS
            # file chooser. Creator's hidden input can accept CDP file paths
            # without opening that chooser, so use the installed bridge API as
            # the final in-transaction fallback.
            try:
                self._set_file_input_with_native_cdp(
                    payload.image_paths,
                    'input[type="file"][multiple][accept*=".jpg"], input[type="file"][multiple], input[type="file"]',
                )
                image_result = subprocess.CompletedProcess([], 0, "", "")
            except DeliveryError as error:
                upload_errors.append(str(error))
        if image_result is None:
            raise DeliveryError("CDP image upload failed: " + " | ".join(upload_errors))
        ready = self.runner(self._command("browser", self.session, "wait", "time", "2"))
        if ready.returncode:
            raise DeliveryError(ready.stderr or ready.stdout or "CDP editor did not become ready after image upload")
        self._fill_editor_field(self.title_selectors, payload.title, "title")
        self._fill_editor_field(self.body_selectors, payload.body, "body")
        self._bind_real_topics_in_editor(payload)
        if payload.require_pdf_attachment:
            if payload.pdf_path is None:
                raise DeliveryError("PDF attachment was required but no local PDF was provided")
            self.attach_pdf_by_cdp(payload.title, payload.pdf_path)

    def _save_editor_as_draft(self, before: list[dict], payload: DraftPayload) -> dict:
        self._trigger_editor_draft_save()
        draft = self._await_new_draft(before, payload.title)
        if not draft:
            if payload.resume_draft_id:
                draft = next((item for item in self._drafts() if str(item.get("id")) == payload.resume_draft_id), None)
            if not draft:
                raise DeliveryError("editor reported draft save, but no matching Xiaohongshu draft was found")
        if int(draft.get("images", 0)) != len(payload.image_paths):
            self._delete(str(draft["id"]))
            raise DeliveryError("saved draft image count differs from the verified manifest")
        return draft

    def _trigger_editor_draft_save(self) -> None:
        """Invoke the creator's draft-save action without touching publish."""
        script = (
            "(() => {"
            "const names = ['_onSave', '_onSaveDraft', '_onDraft'];"
            "const visible = el => !!el && el.offsetParent !== null;"
            "for (const host of Array.from(document.querySelectorAll('xhs-publish-btn')).filter(visible)) {"
            "  for (const name of names) {"
            "    if (typeof host[name] !== 'function') continue;"
            "    try { host[name](); return 'draft-save:' + name; } catch (_) {}"
            "  }"
            "}"
            "const labels = ['暂存离开', '存草稿', '保存草稿'];"
            "const button = Array.from(document.querySelectorAll('button, [role=button]'))"
            ".find(el => visible(el) && labels.some(label => (el.innerText || el.textContent || '').trim().includes(label)));"
            "if (!button) throw new Error('creator draft-save action not found');"
            "button.click(); return 'draft-save:button';"
            "})()"
        )
        result = self.runner(self._command("browser", self.session, "eval", script))
        if result.returncode:
            raise DeliveryError(result.stderr or result.stdout or "CDP could not trigger the creator draft-save action")
        settled = self.runner(self._command("browser", self.session, "wait", "time", "4"))
        if settled.returncode:
            raise DeliveryError(settled.stderr or settled.stdout or "creator draft-save action did not settle")

    def _deliver_with_pre_save_pdf(self, payload: DraftPayload) -> DeliveryReceipt:
        before = self._drafts()
        title_conflicts = [draft for draft in before if draft.get("title") == payload.title]
        allowed_resume = (
            payload.resume_prepared_editor
            and payload.resume_draft_id
            and len(title_conflicts) == 1
            and str(title_conflicts[0].get("id")) == payload.resume_draft_id
        )
        if title_conflicts and not allowed_resume:
            ids = ", ".join(str(draft.get("id", "unknown")) for draft in title_conflicts)
            raise DeliveryError(
                f"refusing to edit an existing same-title draft for {payload.title!r} ({ids}); "
                "use a unique title or explicitly resume that verified draft by ID"
            )
        draft: dict | None = None
        try:
            self._prepare_editor_before_draft_save(payload)
            draft = self._save_editor_as_draft(before, payload)
        except Exception:
            if draft:
                self._delete(str(draft["id"]))
            else:
                # The creator may auto-save while a component is being added.
                # Clean only a uniquely identifiable new draft; never touch
                # an existing user draft with the same title.
                try:
                    new_draft = self._await_new_draft(before, payload.title)
                except DeliveryError:
                    new_draft = None
                if new_draft:
                    self._delete(str(new_draft["id"]))
            raise
        return DeliveryReceipt(
            draft_id=str(draft["id"]), title=payload.title, image_count=len(payload.image_paths),
            topics=payload.topics, pdf_name=payload.pdf_path.name if payload.pdf_path else None,
        )

    def recover_verified_draft(self, payload: DraftPayload) -> DeliveryReceipt:
        """Recover a just-saved, already PDF-verified draft without new UI writes."""
        payload.validate()
        if payload.require_pdf_attachment and not payload.pdf_already_verified:
            raise DeliveryError("recovery requires a PDF filename verified in the current editor session")
        matches = [
            draft for draft in self._drafts()
            if draft.get("title") == payload.title and int(draft.get("images", 0)) == len(payload.image_paths)
        ]
        if len(matches) != 1:
            raise DeliveryError(f"expected exactly one recovered draft for {payload.title!r}, got {len(matches)}")
        draft = matches[0]
        return DeliveryReceipt(
            draft_id=str(draft["id"]), title=payload.title, image_count=len(payload.image_paths),
            topics=payload.topics, pdf_name=payload.pdf_path.name if payload.pdf_path else None,
        )

    @staticmethod
    def _dom_ref_for_text(state: str, text: str) -> int | None:
        """Return a Browser Bridge DOM ref for visible text in the latest state."""
        candidates = re.findall(r"\[(\d+)\]<[^>\n]*>([^\n]*)", state)
        for ref, rendered in candidates:
            if text in rendered:
                return int(ref)
        return None

    def deliver(self, payload: DraftPayload) -> DeliveryReceipt:
        payload.validate()
        if not payload.require_real_topics:
            raise DeliveryError("plain body hashtags are not a supported production delivery path")
        return self._deliver_with_pre_save_pdf(payload)
