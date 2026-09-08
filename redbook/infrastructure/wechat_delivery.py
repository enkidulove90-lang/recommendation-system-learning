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
        return self.runner(self._command("browser", self.session, *parts))

    def _must(self, label: str, result: subprocess.CompletedProcess[str]) -> subprocess.CompletedProcess[str]:
        if result.returncode:
            detail = (result.stderr or result.stdout or "").strip()
            raise DeliveryError(f"{label} failed: {detail[:400]}")
        return result

    def _eval(self, js: str, label: str) -> dict:
        """Run page-eval JS and parse its JSON envelope."""
        result = self._browser("eval", js)
        if result.returncode:
            raise DeliveryError(f"{label} failed: {(result.stderr or result.stdout or '').strip()[:400]}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout.strip()}

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
        self._browser("wait", "time", "3")
        token = self._eval(_EXTRACT_TOKEN_JS, "extract token").get("value", "")
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
        try:
            envelope = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise DeliveryError(f"fill title returned non-JSON: {result.stdout[:200]}") from exc
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

        Returns True when the cover area ends up with a WeChat-CDN background,
        matching ``selectCoverFromContent`` in create-draft.js.  Non-fatal: a
        draft without a cover is still savable.
        """
        # 1. Click the image-menu trigger
        trigger_result = self._eval(_CLICK_JS(COVER_IMAGE_TRIGGER), "open image menu")
        if not trigger_result.get("ok"):
            return False
        self._browser("wait", "time", "1")

        # 2. Click the first dropdown item (the "从电脑选择" entry)
        first_item = self._eval(_CLICK_FIRST_DROPDOWN_JS, "click first dropdown item")
        if not first_item.get("ok"):
            return False
        self._browser("wait", "time", "1")

        # 3. Upload the file via the file input that just appeared
        upload = self._browser("upload", COVER_FILE_INPUT, str(cover_path))
        if upload.returncode:
            return False
        # Wait for CDN — the image src flips to mmbiz.qpic.cn
        for _ in range(8):
            self._browser("wait", "time", "1")
            if self._eval(_WAIT_CDN_JS, "wait CDN upload").get("ok"):
                break

        # 4. Open the cover picker, pick "从正文选择", select first image, confirm
        if not self._eval(_CLICK_JS(".js_cover_btn_area"), "open cover picker").get("ok"):
            return False
        self._browser("wait", "time", "1")
        if not self._eval(_CLICK_PICK_FROM_CONTENT_JS, "click 从正文选择").get("ok"):
            return False
        self._browser("wait", "time", "2")
        self._eval(_CLICK_FIRST_PICKER_IMG_JS, "click first content image")

        # Click 下一步, wait for 确认 to become enabled, then click 确认
        self._click_by_label("下一步")
        for _ in range(8):
            self._browser("wait", "time", "2")
            if self._eval(_CONFIRM_READY_JS, "wait 确认 enabled").get("ok"):
                break
        self._click_by_label("确认")
        self._browser("wait", "time", "2")
        return bool(self._eval(_COVER_PRESENT_JS, "verify cover").get("ok"))

    def _upload_inline_image(self, img_path: Path) -> str | None:
        """Upload one image through the editor's image menu and return its CDN url.

        The image-insert flow is identical to the cover flow up to the upload
        step: open the image menu → "从电脑选择" → upload via the file input.
        WeChat pushes the file to its CDN and rewrites the ``<img>`` ``src`` to
        ``mmbiz.qpic.cn``; we read that url back so the final body HTML can point
        at the public CDN instead of the local disk path (which WeChat blocks).
        """
        if not self._eval(_CLICK_JS(COVER_IMAGE_TRIGGER), "open image menu").get("ok"):
            return None
        self._browser("wait", "time", "1")
        if not self._eval(_CLICK_FIRST_DROPDOWN_JS, "click first dropdown item").get("ok"):
            return None
        self._browser("wait", "time", "1")
        upload = self._browser("upload", COVER_FILE_INPUT, str(img_path))
        if upload.returncode:
            return None
        for _ in range(12):
            self._browser("wait", "time", "1")
            src = self._eval(_GET_LAST_BODY_IMG_SRC_JS, "read uploaded img src").get("src")
            if src:
                return src
        return None

    def _fill_summary(self, summary: str) -> None:
        if not summary:
            return
        summary = summary[:120]
        result = self._browser("fill", SUMMARY_SELECTOR, summary)
        if result.returncode:
            # Non-fatal: summary is optional.
            return

    def _save_draft(self) -> bool:
        """Click 保存为草稿 and verify the success marker."""
        if not self._click_by_label(SAVE_DRAFT_LABEL).get("ok"):
            raise DeliveryError(f"could not find '{SAVE_DRAFT_LABEL}' button")
        for _ in range(8):
            self._browser("wait", "time", "2")
            if self._eval(_SAVE_SUCCESS_JS, "verify save").get("ok"):
                return True
        return False

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
                            continue
                        url = self._upload_inline_image(disk)
                        if url:
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
        finally:
            self._close()
        return DeliveryReceipt(
            title=payload.title,
            cover_applied=cover_applied,
            body_chars=len(payload.body_text),
            saved=saved,
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
    "if((document.body.innerText||'').indexOf('已保存')>=0)"
    "return JSON.stringify({ok:true,via:'text'});"
    "return JSON.stringify({ok:false});"
    "})()"
)


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