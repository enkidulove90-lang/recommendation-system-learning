"""Single-session WeChat Official Account draft delivery driven through CDP.

Why this exists
---------------
The previous implementation routed through ``opencli weixin create-draft``, which
silently produced unusable drafts:

1. **Title dropped.** ``create-draft`` sets ``textarea#title`` via the
   ``HTMLTextAreaElement.prototype.value`` setter + ``InputEvent('input')``.
   The WeChat editor (UEditor front-end) does not subscribe to that synthetic
   event sequence, so the React state stays empty.  The screenshot of the
   saved draft shows ``请在这里输入标题`` (0/64) even though OpenCLI reported
   ``"draft saved"``.

2. **Body unformatted.** ``create-draft`` writes the body with
   ``document.execCommand('insertText', ...)``.  WeChat's rich editor accepts
   the text as plain content, so Markdown syntax (``**``, ``##``) survives
   literally — the resulting draft looks like a raw changelog, not an article.

The corrected pipeline keeps one editor tab alive for the whole lifetime of
the call and performs, in order::

    open home → extract token → open editor URL
        → fill title (verified via ``browser fill``'s actual/verified fields)
        → inject body via ``innerHTML`` so UEdit sees real <p>/<br> structure
        → upload cover image → promote to cover via the official picker
        → fill summary → click "保存为草稿" → verify save marker → close

Why not the lower-level ``create-draft`` at all
----------------------------------------------
The two failure modes above are inside OpenCLI itself, not in our wrapper.
Wrapping ``create-draft`` cannot recover the title or the formatting.  The new
pipeline bypasses ``create-draft`` and calls the same browser bridge
``create-draft`` uses internally (``opencli browser <session> ...``), but with
the right commands: ``fill`` (real native event sequence) and ``eval``
(direct ``innerHTML`` manipulation).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import opencli_runtime


class DeliveryError(RuntimeError):
    """A WeChat prerequisite failed; the caller should not silently downgrade."""


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


#: Creator-center automation routinely exceeds OpenCLI's 60s default ceiling.
_BROWSER_TIMEOUT_SECONDS = 270

#: Selectors lifted from clis/weixin/create-draft.js (proven to resolve against
#: the editor DOM) and refined for the new pipeline.
TITLE_SELECTOR = "textarea#title"
AUTHOR_SELECTOR = "input#author"
SUMMARY_SELECTOR = "textarea#js_description"
#: UEditor's contenteditable body. There may be multiple on the page (search
#: inputs, etc.) — the body editor is the last one in document order.
BODY_SELECTORS = ('div[contenteditable="true"]',)
COVER_IMAGE_TRIGGER = "#js_editor_insertimage"
COVER_DROPDOWN_ITEM = ".js_img_dropdown_menu .tpl_dropdown_menu_item"
COVER_FILE_INPUT = 'input[type="file"][name="file"]'
SAVE_DRAFT_LABEL = "保存为草稿"
SAVE_SUCCESS_SELECTOR = "#js_save_success"

#: A short, stable author byline surfaced into OpenCLI's metadata.
_DEFAULT_AUTHOR = "推荐系统研读"

#: Project root used to resolve relative image paths embedded in body_html.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

#: Matches ``<img ... src="...">`` / ``<img ... src='...'>`` so we can find the
#: local image references that must be uploaded to WeChat's CDN before the draft
#: will render.  ``data:`` and ``http(s)://`` sources are already public and are
#: skipped.
_LOCAL_IMG_RE = re.compile(r"<img\b[^>]*?\ssrc=([\"'])(.*?)\1", re.I | re.S)
#: Any <img ...> tag, regardless of src, for counting body images.
_IMG_TAG_RE = re.compile(r"<img\b", re.I)


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["OPENCLI_BROWSER_COMMAND_TIMEOUT"] = str(_BROWSER_TIMEOUT_SECONDS)
    return subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=_BROWSER_TIMEOUT_SECONDS + 60, env=env,
    )


@dataclass(frozen=True)
class WeChatDraftPayload:
    """All the inputs the editor needs, validated up front."""

    title: str
    body_text: str
    cover_image: Path | None
    summary: str = ""
    author: str = _DEFAULT_AUTHOR
    body_html: str = ""

    def validate(self) -> None:
        if not self.title or len(self.title) > 64:
            raise DeliveryError("WeChat title is required and must be at most 64 characters")
        # Either the plain body_text or the rich body_html satisfies the body.
        body = self.body_html or self.body_text
        if not body.strip():
            raise DeliveryError("body text is required")
        if len(body) < 200:
            raise DeliveryError("body must be at least 200 characters (公众号 prefers depth)")
        if self.cover_image is not None and not self.cover_image.is_file():
            raise DeliveryError(f"cover image missing on disk: {self.cover_image}")
        if self.author and len(self.author) > 8:
            raise DeliveryError("WeChat author must be at most 8 characters")


@dataclass(frozen=True)
class DeliveryReceipt:
    """Confirmation that the draft saved (or the failure that prevented it)."""

    title: str
    cover_applied: bool
    body_chars: int
    saved: bool
    draft_id: str | None = None
    reopened_verified: bool = False


class WeChatDraftDelivery:
    """Drive the WeChat editor in one persistent browser session."""

    home_url = "https://mp.weixin.qq.com/"
    editor_path = (
        "/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1"
        "&type=77&lang=zh_CN&token={token}"
    )

    def __init__(
        self, runner: Runner = _run, session: str = "redbook-wechat-draft"
    ) -> None:
        self.runner, self.session = runner, session

    # ------------------------------------------------------------------ #
    # Command plumbing
    # ------------------------------------------------------------------ #
    def _command(self, *parts: str) -> list[str]:
        return opencli_runtime.resolve_runtime().command(*parts)

    def _browser(self, *parts: str) -> subprocess.CompletedProcess[str]:
        # OpenCLI CLI expects `--session <name>` as a flag; the older
        # `browser <session> <command>` positional form now fails with
        # "unknown command '<session>'".
        return self.runner(
            self._command("browser", *parts, "--session", self.session))

    def _must(self, label: str, result: subprocess.CompletedProcess[str]) -> subprocess.CompletedProcess[str]:
        if result.returncode:
            detail = (result.stderr or result.stdout or "").strip()
            raise DeliveryError(f"{label} failed: {detail[:400]}")
        return result

    @staticmethod
    def _unpack(raw: str) -> dict:
        """Unwrap OpenCLI's `{"ok":true,"data":...}` envelope.

        Newer CLI versions wrap every command result in `data` (a dict or a
        JSON string).  Older ones returned the payload at top level.  Callers
        always receive the inner payload dict.
        """
        try:
            envelope = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"raw": str(raw).strip()}
        if not isinstance(envelope, dict):
            return {"raw": str(envelope)}
        data = envelope.get("data")
        if isinstance(data, str):
            try:
                decoded = json.loads(data)
                if isinstance(decoded, dict):
                    return decoded
            except json.JSONDecodeError:
                pass
        elif isinstance(data, dict):
            return data
        return envelope

    def _eval(self, js: str, label: str) -> dict:
        """Run page-eval JS and parse its JSON envelope."""
        result = self._browser("eval", js)
        if result.returncode:
            raise DeliveryError(f"{label} failed: {(result.stderr or result.stdout or '').strip()[:400]}")
        return self._unpack(result.stdout)

    def _click_by_label(self, label: str) -> dict:
        """Click the first visible element whose text matches ``label``."""
        js = _CLICK_BY_LABEL_JS.replace("__LABEL__", json.dumps(label))
        return self._eval(js, f"click {label}")

    # ------------------------------------------------------------------ #
    # Editor session
    # ------------------------------------------------------------------ #
    def _open_editor(self) -> None:
        """Navigate to the WeChat editor in this session's tab.

        Mirrors ``navigateToEditor`` in clis/weixin/create-draft.js so we end up
        on the same DOM, but every subsequent step is owned by this module.
        """
        self._must("open mp.weixin.qq.com",
                   self._browser("open", self.home_url, "--window", "foreground"))
        # Poll for the token instead of a fixed sleep: the redirect from
        # mp.weixin.qq.com to /cgi-bin/home?...token=... can take 3-8s on a
        # cold tab, and a single 3s wait used to fail spuriously.
        token = ""
        for _ in range(6):
            self._browser("wait", "time", "2")
            token = self._eval(_EXTRACT_TOKEN_JS, "extract token").get("value", "")
            if token:
                break
        if not token:
            raise DeliveryError(
                "could not extract session token — Chrome is not logged in to mp.weixin.qq.com")
        editor_url = f"https://mp.weixin.qq.com{self.editor_path.format(token=token)}"
        self._must("open editor URL", self._browser("open", editor_url))
        self._browser("wait", "time", "4")
        # Title textarea is the stable gate — if it isn't there, the editor
        # didn't actually load (session expired mid-call).
        self._must("wait for title textarea",
                   self._browser("wait", "selector", TITLE_SELECTOR, "--timeout", "20000"))

    def _fill_title(self, title: str) -> None:
        """Set the title and verify the value actually landed.

        ``browser fill`` returns ``{filled, verified, text, actual}``.  ``actual``
        is what UEditor actually sees in the DOM; it must match the title we sent,
        not just echo our request.
        """
        result = self._browser("fill", TITLE_SELECTOR, title)
        if result.returncode:
            raise DeliveryError(f"fill title failed: {(result.stderr or result.stdout or '').strip()[:400]}")
        envelope = self._unpack(result.stdout)
        if not envelope.get("filled") or not envelope.get("verified"):
            raise DeliveryError(
                f"title fill not verified: actual={envelope.get('actual')!r}, "
                f"requested={title!r}")
        if envelope.get("actual") != title:
            raise DeliveryError(
                f"title applied value differs from requested: "
                f"actual={envelope.get('actual')!r} vs requested={title!r}")

    def _fill_author(self, author: str) -> None:
        if not author:
            return
        if len(author) > 8:
            author = author[:8]
        result = self._browser("fill", AUTHOR_SELECTOR, author)
        if result.returncode:
            raise DeliveryError(f"fill author failed: {(result.stderr or result.stdout or '').strip()[:400]}")

    def _fill_body(self, body_text: str) -> None:
        """Inject WeChat-flavored plain text into UEditor's contenteditable.

        Plain ``insertText`` would leave ``\\n`` as literal newlines and produce
        the raw-text look from create-draft.  Instead, we split the body on
        blank lines into paragraphs and assign ``innerHTML`` with ``<p>...</p>``.
        UEditor notices the new DOM and keeps its toolbar in sync.
        """
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", body_text) if p.strip()]
        js = _BODY_INNERHTML_JS.replace("__PAYLOAD__", json.dumps(paragraphs, ensure_ascii=False))
        outcome = self._eval(js, "set body innerHTML")
        if not outcome.get("ok"):
            raise DeliveryError(f"set body innerHTML failed: {outcome}")
        self._browser("wait", "time", "1")

    def _fill_body_html(self, body_html: str) -> None:
        """Inject pre-built WeChat-safe HTML into UEditor's contenteditable.

        Unlike :meth:`_fill_body`, this does **not** escape or wrap the content:
        ``body_html`` is already a complete, trusted HTML string (inline styles
        only, produced by ``paper_to_wechat.render_wechat_html``) that WeChat's
        editor preserves.  We set ``innerHTML`` directly.
        """
        js = _BODY_HTML_JS.replace("__HTML__", json.dumps(body_html, ensure_ascii=False))
        outcome = self._eval(js, "set body innerHTML (html)")
        if not outcome.get("ok"):
            raise DeliveryError(f"set body innerHTML (html) failed: {outcome}")
        self._browser("wait", "time", "1")

    def _upload_cover(self, cover_path: Path) -> bool:
        """Insert the cover image into the body, then promote it to cover.

        Throws DeliveryError on any failure; returns True when the cover area
        ends up with a WeChat-CDN background, matching ``selectCoverFromContent``
        in create-draft.js.
        """
        # 1. Click the image-menu trigger
        trigger_result = self._eval(_CLICK_JS(COVER_IMAGE_TRIGGER), "open image menu")
        if not trigger_result.get("ok"):
            raise DeliveryError("failed to open image menu for cover")
        self._browser("wait", "time", "1")

        # 2. Click the first dropdown item (the "从电脑选择" entry)
        first_item = self._eval(_CLICK_FIRST_DROPDOWN_JS, "click first dropdown item")
        if not first_item.get("ok"):
            raise DeliveryError("failed to click '从电脑选择' for cover")
        self._browser("wait", "time", "1")

        # 3. Upload the file via the file input that just appeared
        upload = self._browser("upload", COVER_FILE_INPUT, str(cover_path))
        if upload.returncode:
            raise DeliveryError(f"cover file upload failed: {upload.stderr[:400]}")
        # Wait for CDN — the image src flips to mmbiz.qpic.cn
        for _ in range(8):
            self._browser("wait", "time", "1")
            if self._eval(_WAIT_CDN_JS, "wait CDN upload").get("ok"):
                break
        else:
            raise DeliveryError("cover CDN upload timed out")

        # 4. Open the cover picker, pick "从正文选择", select first image, confirm
        if not self._eval(_CLICK_JS(".js_cover_btn_area"), "open cover picker").get("ok"):
            raise DeliveryError("failed to open cover picker")
        self._browser("wait", "time", "1")
        if not self._eval(_CLICK_PICK_FROM_CONTENT_JS, "click 从正文选择").get("ok"):
            raise DeliveryError("failed to click '从正文选择' in cover picker")
        self._browser("wait", "time", "2")
        self._eval(_CLICK_FIRST_PICKER_IMG_JS, "click first content image")

        # Click 下一步, wait for 确认 to become enabled, then click 确认
        self._click_by_label("下一步")
        for _ in range(8):
            self._browser("wait", "time", "2")
            if self._eval(_CONFIRM_READY_JS, "wait 确认 enabled").get("ok"):
                break
        else:
            raise DeliveryError("cover 确认 button did not enable in time")
        self._click_by_label("确认")
        self._browser("wait", "time", "2")
        if not self._eval(_COVER_PRESENT_JS, "verify cover").get("ok"):
            raise DeliveryError("cover verification failed: no CDN background in cover area")
        return True

    def _upload_inline_image(self, img_path: Path) -> str:
        """Upload one image through the editor's image menu and return its CDN url.

        The image-insert flow is identical to the cover flow up to the upload
        step: open the image menu → "从电脑选择" → upload via the file input.
        WeChat pushes the file to its CDN and rewrites the ``<img>`` ``src`` to
        ``mmbiz.qpic.cn``; we read that url back so the final body HTML can point
        at the public CDN instead of the local disk path (which WeChat blocks).

        Throws DeliveryError on any failure.
        """
        if not self._eval(_CLICK_JS(COVER_IMAGE_TRIGGER), "open image menu").get("ok"):
            raise DeliveryError(f"failed to open image menu for {img_path}")
        self._browser("wait", "time", "1")
        if not self._eval(_CLICK_FIRST_DROPDOWN_JS, "click first dropdown item").get("ok"):
            raise DeliveryError(f"failed to click '从电脑选择' for {img_path}")
        self._browser("wait", "time", "1")
        upload = self._browser("upload", COVER_FILE_INPUT, str(img_path))
        if upload.returncode:
            raise DeliveryError(f"image file upload failed for {img_path}: {upload.stderr[:400]}")
        for _ in range(12):
            self._browser("wait", "time", "1")
            src = self._eval(_GET_LAST_BODY_IMG_SRC_JS, "read uploaded img src").get("src")
            if src:
                return src
        raise DeliveryError(f"image CDN upload timed out for {img_path}")

    def _fill_summary(self, summary: str) -> None:
        if not summary:
            return
        summary = summary[:120]
        result = self._browser("fill", SUMMARY_SELECTOR, summary)
        if result.returncode:
            # Non-fatal: summary is optional.
            return

    def _save_draft(self) -> bool:
        """Click 保存为草稿 and verify the save actually happened.

        WeChat's "已保存" toast is inconsistent across editor builds (a real
        draft was observed in the draft box while the marker never showed).
        So a save counts as confirmed if ANY of these hold within the poll
        window: the success element/text appears, OR the editor URL now carries
        a ``draft_id`` (proof the draft entity exists).
        """
        if not self._click_by_label(SAVE_DRAFT_LABEL).get("ok"):
            raise DeliveryError(f"could not find '{SAVE_DRAFT_LABEL}' button")
        for _ in range(8):
            self._browser("wait", "time", "2")
            if self._eval(_SAVE_SUCCESS_JS, "verify save").get("ok"):
                return True
            # URL draft_id is a reliable positive signal the draft persisted.
            if self._extract_draft_id():
                return True
        return False

    def _extract_draft_id(self) -> str | None:
        """Extract draft ID from current page URL or success message after saving."""
        try:
            # Check URL pattern: /cgi-bin/appmsg?t=...</各地
            result = self._eval(
                "(function(){"
                "var value = new URL(window.location.href).searchParams.get('draft_id');"
                "return JSON.stringify({value:value || null});"
                "})()",
                "extract draft ID from URL"
            )
            if result.get("value"):
                return result["value"]
        except Exception:
            pass
        # Fallback: look for draft_id in success message
        try:
            result = self._eval(
                "(function(){"
                "var text = document.body.innerText || '';"
                "var match = text.match(/草稿 ID:?(\\d+)/);"
                "if(match && match[1])return JSON.stringify({value:match[1]});"
                "return JSON.stringify({value:null});"
                "})()",
                "extract draft ID from success message"
            )
            if result.get("value"):
                return result["value"]
        except Exception:
            pass
        return None

    def _verify_draft_reopened(
        self,
        draft_id: str | None,
        payload: "WeChatDraftPayload | None" = None,
        *,
        expected_images: int | None = None,
    ) -> bool:
        """Reopen the saved draft and confirm it holds the intended content.

        The old check only proved "a title textarea exists". This version reads
        the reopened editor and verifies three things match what we filled:
          1. the title text contains the payload title (first 12 chars anchor),
          2. the body editor text contains an anchor phrase from the payload,
          3. the body's <img> count equals ``expected_images`` (body images only,
             cover copy already stripped by the delivery flow).

        With no payload (legacy callers) it degrades to "title control present
        and non-empty" so it never regresses to always-false.
        """
        if not draft_id:
            return False
        try:
            editor_url = (
                "https://mp.weixin.qq.com/cgi-bin/appmsg?"
                f"t=media/appmsg_edit&draft_id={draft_id}"
            )
            self._browser("open", editor_url, "--window", "foreground")
            self._browser("wait", "time", "3")
            result = self._eval(_REOPEN_SNAPSHOT_JS, "snapshot reopened draft")
            self._browser("close")
        except Exception:
            return False

        if not result.get("ok"):
            return False
        if payload is None:
            return bool(str(result.get("title", "")).strip())

        title_dom = str(result.get("title", ""))
        body_dom = str(result.get("body_text", ""))
        image_count = int(result.get("image_count", -1))

        title_anchor = payload.title.strip()[:12]
        body_source = payload.body_html or payload.body_text
        body_anchor = _body_anchor_text(body_source)
        if title_anchor and title_anchor not in title_dom:
            return False
        if body_anchor and body_anchor not in body_dom:
            return False
        if expected_images is not None and image_count != expected_images:
            return False
        return True

    def _close(self) -> None:
        # Close is best-effort — even if it fails we don't want to fail delivery.
        try:
            self._browser("close")
        except Exception:  # noqa: BLE001 — close must never block cleanup.
            pass

    # ------------------------------------------------------------------ #
    # Public entry
    # ------------------------------------------------------------------ #
    def deliver(self, payload: WeChatDraftPayload) -> DeliveryReceipt:
        payload.validate()
        cover_applied = False
        saved = False
        draft_id = None
        reopened_verified = False
        try:
            self._open_editor()
            self._fill_title(payload.title)
            self._fill_author(payload.author)
            body_html = payload.body_html
            if body_html:
                local_imgs = _collect_local_images(body_html)
                if local_imgs:
                    src_to_url: dict[str, str] = {}
                    for src in local_imgs:
                        disk = _resolve_image_path(src)
                        if disk is None:
                            raise DeliveryError(f"local image not found: {src}")
                        url = self._upload_inline_image(disk)
                        src_to_url[src] = url
                    if src_to_url:
                        # The uploads above left placeholder <img>s in the body;
                        # clear them, then inject the rewritten HTML that points
                        # at the public CDN urls so WeChat renders the images.
                        self._eval(_CLEAR_BODY_JS, "clear placeholder images")
                        body_html = _rewrite_local_images(body_html, src_to_url)
                self._fill_body_html(body_html)
            else:
                self._fill_body(payload.body_text)
            if payload.cover_image is not None:
                cover_applied = self._upload_cover(payload.cover_image)
                # The cover upload leaves a copy of the image in the body; drop
                # it so the body only contains the intended illustrations.
                self._eval(_REMOVE_LAST_BODY_IMG_JS, "drop cover copy from body")
            self._fill_summary(payload.summary)
            saved = self._save_draft()
            if saved:
                draft_id = self._extract_draft_id()
                # Body images as rendered: count <img> in the final body html
                # (cover copy was removed above, so this is illustrations only).
                expected_images = len(_IMG_TAG_RE.findall(body_html)) if body_html else 0
                reopened_verified = self._verify_draft_reopened(
                    draft_id, payload, expected_images=expected_images)
        except DeliveryError:
            raise
        finally:
            self._close()
        return DeliveryReceipt(
            title=payload.title,
            cover_applied=cover_applied,
            body_chars=len(payload.body_text),
            saved=saved,
            draft_id=draft_id,
            reopened_verified=reopened_verified,
        )


# ---------------------------------------------------------------------- #
# Body image collection / rewrite (local disk -> WeChat CDN)
# ---------------------------------------------------------------------- #
def _collect_local_images(body_html: str) -> list[str]:
    """Return local (non-public) ``src`` values found in ``body_html`` order."""
    out: list[str] = []
    for match in _LOCAL_IMG_RE.finditer(body_html):
        src = match.group(2).strip()
        if src.startswith(("http://", "https://", "data:")):
            continue
        out.append(src)
    return out


def _resolve_image_path(src: str) -> Path | None:
    """Resolve a body_html image ``src`` to a real file on disk, if it exists."""
    candidate = Path(src)
    if not candidate.is_absolute():
        candidate = _PROJECT_ROOT / src
    return candidate if candidate.is_file() else None


def _rewrite_local_images(body_html: str, src_to_url: dict[str, str]) -> str:
    """Replace each local ``src`` in ``body_html`` with its uploaded CDN url."""

    def _repl(match: "re.Match[str]") -> str:
        quote, src = match.group(1), match.group(2).strip()
        url = src_to_url.get(src)
        if not url:
            return match.group(0)
        return match.group(0).replace(
            f"src={quote}{src}{quote}", f"src={quote}{url}{quote}"
        )

    return _LOCAL_IMG_RE.sub(_repl, body_html)


# ---------------------------------------------------------------------- #
# In-page scripts (mirror xiaohongshu_delivery.py's JS-string approach)
# ---------------------------------------------------------------------- #
_EXTRACT_TOKEN_JS = (
    "(function(){"
    "var m=(window.location.href||'').match(/token=(\\d+)/);"
    "if(m&&m[1])return JSON.stringify({value:m[1]});"
    "var c=(document.cookie||'').match(/[?&]token=(\\d+)/);"
    "return JSON.stringify({value:c?c[1]:''});"
    "})()"
)


#: Inject paragraphs as <p> blocks.  The editor body lives inside the
#: ``#ueditor_0`` iframe in the v2 editor, so resolve ``ctx`` from the iframe
#: when present (mirrors ``_EDITOR_CTX_JS``) — querying ``document`` at top
#: level silently targets the wrong element and the body stays empty.
_BODY_INNERHTML_JS = (
    "(function(paragraphs){"
    "var ifr=document.querySelector('#ueditor_0');"
    "var ctx=(ifr&&ifr.contentDocument)?ifr.contentDocument:document;"
    "var editors=ctx.querySelectorAll('div[contenteditable=\"true\"]');"
    "var editor=editors[editors.length-1];"
    "if(!editor)return JSON.stringify({ok:false,reason:'no editor'});"
    "editor.focus();"
    "var html=paragraphs.map(function(p){"
    "return '<p>'+p.split('\\n').map(function(line){"
    "return line.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');"
    "}).join('<br/>')+'</p>';"
    "}).join('');"
    "editor.innerHTML=html;"
    "editor.dispatchEvent(new InputEvent('input',{bubbles:true,data:paragraphs.join('\\n\\n')}));"
    "return JSON.stringify({ok:true,paragraphs:paragraphs.length,"
    "chars:paragraphs.join('').length});"
    "})(__PAYLOAD__)"
)


#: Inject already-built, WeChat-safe HTML verbatim (no escaping).  ``__HTML__``
#: is replaced with the JSON-encoded HTML string so quotes/brackets survive.
#: Like ``_BODY_INNERHTML_JS``, this must resolve the editor body inside the
#: ``#ueditor_0`` iframe, otherwise the body is injected into the wrong node
#: and WeChat refuses to save ("正文不能为空").
_BODY_HTML_JS = (
    "(function(html){"
    "var ifr=document.querySelector('#ueditor_0');"
    "var ctx=(ifr&&ifr.contentDocument)?ifr.contentDocument:document;"
    "var editors=ctx.querySelectorAll('div[contenteditable=\"true\"]');"
    "var editor=editors[editors.length-1];"
    "if(!editor)return JSON.stringify({ok:false,reason:'no editor'});"
    "editor.focus();"
    "editor.innerHTML=html;"
    "editor.dispatchEvent(new InputEvent('input',{bubbles:true}));"
    "return JSON.stringify({ok:true,chars:html.length});"
    "})(__HTML__)"
)


def _CLICK_JS(selector: str) -> str:
    return (
        "(function(){"
        f"var el=document.querySelector({json.dumps(selector)});"
        "if(!el)return JSON.stringify({ok:false,reason:'not found'});"
        "el.click();"
        "return JSON.stringify({ok:true});"
        "})()"
    )


_CLICK_FIRST_DROPDOWN_JS = (
    "(function(){"
    f"var items=document.querySelectorAll({json.dumps(COVER_DROPDOWN_ITEM)});"
    "if(!items.length)return JSON.stringify({ok:false,reason:'no items'});"
    "items[0].click();"
    "return JSON.stringify({ok:true,count:items.length});"
    "})()"
)


_WAIT_CDN_JS = (
    "(function(){"
    "var editor=document.querySelector('#ueditor_0');"
    "if(!editor)return JSON.stringify({ok:false});"
    "var imgs=editor.querySelectorAll('img[src*=\"mmbiz\"]');"
    "return JSON.stringify({ok:imgs.length>0,count:imgs.length});"
    "})()"
)


_CLICK_PICK_FROM_CONTENT_JS = (
    "(function(){"
    "var links=document.querySelectorAll('a.pop-opr__button');"
    "for(var i=0;i<links.length;i++){"
    "if((links[i].textContent||'').trim()==='从正文选择'){links[i].click();return JSON.stringify({ok:true});}"
    "}"
    "return JSON.stringify({ok:false,reason:'从正文选择 button not found'});"
    "})()"
)


_CLICK_FIRST_PICKER_IMG_JS = (
    "(function(){"
    "var img=document.querySelector('.weui-desktop-dialog_img-picker .appmsg_content_img');"
    "if(!img)return JSON.stringify({ok:false});"
    "img.click();"
    "return JSON.stringify({ok:true});"
    "})()"
)


_CLICK_BY_LABEL_JS = (
    "(function(label){"
    "var btns=document.querySelectorAll('button, span, a');"
    "for(var i=0;i<btns.length;i++){"
    "var t=(btns[i].textContent||'').trim();"
    "if((t===label||t.indexOf(label)>=0)&&btns[i].offsetParent!==null&&!btns[i].disabled){"
    "btns[i].click();return JSON.stringify({ok:true,label:label});"
    "}"
    "}"
    "return JSON.stringify({ok:false,label:label});"
    "})(__LABEL__)"
)


_CONFIRM_READY_JS = (
    "(function(){"
    "var btns=document.querySelectorAll('button');"
    "for(var i=0;i<btns.length;i++){"
    "if((btns[i].textContent||'').trim()==='确认'&&btns[i].offsetHeight>0&&!btns[i].disabled){"
    "return JSON.stringify({ok:true});"
    "}"
    "}"
    "return JSON.stringify({ok:false});"
    "})()"
)


_COVER_PRESENT_JS = (
    "(function(){"
    "var area=document.querySelector('#js_cover_area');"
    "if(!area)return JSON.stringify({ok:false});"
    "var found=false;"
    "area.querySelectorAll('*').forEach(function(el){"
    "var bg=window.getComputedStyle(el).backgroundImage||'';"
    "if(bg.indexOf('mmbiz')>=0)found=true;"
    "});"
    "return JSON.stringify({ok:found});"
    "})()"
)


_SAVE_SUCCESS_JS = (
    "(function(){"
    "var el=document.querySelector('#js_save_success');"
    "if(el&&window.getComputedStyle(el).display!=='none')return JSON.stringify({ok:true,via:'element'});"
    "var t=(document.body.innerText||'');"
    "if(t.indexOf('已保存')>=0||t.indexOf('保存成功')>=0||t.indexOf('已保存到草稿箱')>=0)"
    "return JSON.stringify({ok:true,via:'text'});"
    "return JSON.stringify({ok:false});"
    "})()"
)


#: Snapshot a reopened draft's editable fields so delivery can prove the draft
#: it reopened is the one it filled: title text, body text, body image count.
#: Reads the body from the UEditor iframe when present, else the top document.
_REOPEN_SNAPSHOT_JS = (
    "(function(){"
    "var titleEl=document.querySelector('textarea#title');"
    "var ifr=document.querySelector('#ueditor_0');"
    "var ctx=(ifr&&ifr.contentDocument)?ifr.contentDocument:document;"
    "var body=ctx.querySelector('div[contenteditable=\"true\"]')||ctx.body;"
    "var title=titleEl?titleEl.value:'';"
    "var bodyText=body?(body.innerText||''):'';"
    "var imgs=body?body.querySelectorAll('img').length:0;"
    "var ok=!!titleEl;"
    "return JSON.stringify({ok:ok,title:title,body_text:bodyText,image_count:imgs});"
    "})()"
)


def _body_anchor_text(body_source: str) -> str:
    """Pick a stable anchor phrase from the payload body for reopen matching.

    Strips tags to plain text, then takes the first run of ~20 contiguous
    non-space characters after leading punctuation. Returns "" when the body
    is too short to anchor on (so verification skips the body check).
    """
    import re as _re

    text = _re.sub(r"<[^>]+>", "", body_source or "")
    text = _re.sub(r"\s+", "", text)
    text = text.lstrip("　#*>-·•　")
    if len(text) < 12:
        return ""
    return text[:20]


#: Resolve the live editing context: WeChat's body rich-editor lives inside the
#: ``#ueditor_0`` iframe in the v2 editor, but some builds render it as a
#: top-level ``div[contenteditable]`` — check both and use whichever exists.
def _EDITOR_CTX_JS(inner: str) -> str:
    return (
        "(function(){"
        "var ifr=document.querySelector('#ueditor_0');"
        "var ctx=(ifr&&ifr.contentDocument)?ifr.contentDocument:document;"
        + inner
        + "})()"
    )


_GET_LAST_BODY_IMG_SRC_JS = _EDITOR_CTX_JS(
    "var imgs=ctx.querySelectorAll('img[src*=\"mmbiz\"]');"
    "if(!imgs.length)imgs=ctx.querySelectorAll('img');"
    "return JSON.stringify({src:imgs.length?imgs[imgs.length-1].getAttribute('src'):''});"
)


_CLEAR_BODY_JS = _EDITOR_CTX_JS(
    "var ed=ctx.querySelector('div[contenteditable=\"true\"]')||ctx.body;"
    "ed.innerHTML='';return JSON.stringify({ok:true});"
)


_REMOVE_LAST_BODY_IMG_JS = _EDITOR_CTX_JS(
    "var imgs=ctx.querySelectorAll('img');"
    "if(imgs.length){imgs[imgs.length-1].parentNode.removeChild(imgs[imgs.length-1]);"
    "return JSON.stringify({ok:true,removed:true});}"
    "return JSON.stringify({ok:false});"
)
