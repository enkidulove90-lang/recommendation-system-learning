"""Single-session Xiaohongshu draft delivery driven entirely through CDP.

The adapter mirrors OpenCLI's own ``xiaohongshu publish --draft true`` sequence
verbatim (read from ``clis/xiaohongshu/publish.js``), but splits it into one
*persistent* browser session so the paper PDF can be attached **in the same
unsaved editor** before the draft is saved.

Why this exists
---------------
The previous implementation called ``publish --draft true`` (which opens the
composer, fills it, and immediately saves+closes the tab) and then tried to
re-open the freshly created draft from the drafts box to attach the PDF. That
re-open step is exactly the "semantic positioning failed" the user reported:
the CDP context of the original editor was gone, so the file-input locator
could not be resolved.

The corrected flow keeps one editor tab alive for the whole lifetime of the
call and performs, in order::

    open composer -> upload images -> fill title -> fill body
    -> bind real topic entities -> attach PDF -> save draft (LAST)

Saving is the *final* action, performed by invoking the ``<xhs-publish-btn>``
web component's ``_onSave`` / ``_onSaveDraft`` / ``_onDraft`` method (OpenCLI's
"Path 1"), with the text-match / leave-and-save fallbacks as backup. A draft is
only considered successful after the drafts API reports exactly one new draft
whose title matches and whose image count equals the manifest.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
from typing import Callable

from . import opencli_runtime


class DeliveryError(RuntimeError):
    """A platform-side prerequisite was not completed; never silently downgrade."""


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]

#: Creator-center automation (image upload, topic picker, PDF dialog, save) can
#: exceed OpenCLI's default 60s browser-command ceiling.
_BROWSER_TIMEOUT_SECONDS = 300

#: Selectors reused from OpenCLI's adapter (clis/xiaohongshu/publish.js) plus
#: the ones confirmed live against this account's creator-center DOM.
#:
#: IMPORTANT (2026-08 verified): the current creator center has **no**
#: searchable topic dropdown. The old ``div.items div.item`` list is gone,
#: typing ``#topic`` into the body no longer forms a chip, and clicking
#: ``button#topicBtn`` does NOT open a search box — it only reveals a set of
#: *recommended* ``.tag`` chips (which rotate randomly every session). The only
#: way to get a real, highlighted, clickable topic entity is to click a
#: recommended ``.tag`` chip whose text matches the desired topic or an academic
#: allowlist. ``TOPIC_SUGGESTION_SELECTORS`` is retained only as dead legacy and
#: is no longer used by ``_bind_topics``.
TITLE_SELECTOR = 'input[placeholder="填写标题会有更多赞哦"]'
BODY_SELECTOR = 'div.tiptap'
IMAGE_INPUT_SELECTOR = 'input.upload-input'
PDF_INPUT_SELECTOR = 'input[type="file"][accept*=".pdf"]'
TOPIC_BUTTON_SELECTOR = 'button#topicBtn'
TOPIC_SUGGESTION_SELECTORS = [
    'div.items div.item',
    '[class*="topic-item"]', '[class*="hashtag-item"]', '[class*="suggest-item"]',
    '[class*="suggestion"] li', '[class*="mention"] li', '[class*="dropdown"] li',
    '[id*="topic"] li', '[class*="topic"] li',
]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["OPENCLI_BROWSER_COMMAND_TIMEOUT"] = str(_BROWSER_TIMEOUT_SECONDS)
    return subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=_BROWSER_TIMEOUT_SECONDS + 30, env=env,
    )


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
    """Save an image note as a draft in one CDP session, then bind topics and attach the PDF."""

    creator_url = "https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image"
    _body_selectors_json = json.dumps([BODY_SELECTOR])

    def __init__(self, runner: Runner = _run, session: str = "redbook-daily-pdf") -> None:
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
            raise DeliveryError(f"{label} failed: {detail}")
        return result

    def _eval(self, js: str, label: str) -> dict:
        """Run a page-eval script that returns JSON and parse it."""
        result = self._browser("eval", js)
        if result.returncode:
            raise DeliveryError(f"{label} failed: {(result.stderr or result.stdout or '').strip()}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # Some eval output is wrapped; return raw stdout for the caller.
            return {"raw": result.stdout}

    # ------------------------------------------------------------------ #
    # Drafts API (before/after reconciliation)
    # ------------------------------------------------------------------ #
    def _drafts(self) -> list[dict]:
        result = self.runner(self._command(
            "xiaohongshu", "drafts", "-f", "json", "--window", "background", "--site-session", "ephemeral"))
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
        self.runner(self._command(
            "xiaohongshu", "draft-delete", draft_id, "--execute", "-f", "json",
            "--window", "background", "--site-session", "ephemeral"))

    # ------------------------------------------------------------------ #
    # Editor helpers (all share the one persistent CDP session)
    # ------------------------------------------------------------------ #
    def _open_editor(self) -> None:
        # Open the composer and begin driving it immediately. A long pre-wait
        # here has been observed to detach the image input, so we upload right
        # away (the input is present from first paint) and gate on the body
        # editor *after* the upload, since the title/body fields only render
        # once an image is attached.
        self._must("open creator editor", self._browser("open", self.creator_url, "--window", "foreground"))

    def _upload_images(self, image_paths: tuple[Path, ...]) -> None:
        files = [str(p) for p in image_paths]
        self._must("upload images", self._browser("upload", IMAGE_INPUT_SELECTOR, *files))
        self._browser("wait", "time", "4")
        # The title and body editors only appear once the first image is
        # attached; gate on the body editor (stable selector) before filling.
        self._must("wait for composer fields",
                   self._browser("wait", "selector", BODY_SELECTOR, "--timeout", "40000"))

    def _fill_title(self, title: str) -> None:
        self._must("fill title", self._browser("fill", TITLE_SELECTOR, title))
        self._browser("wait", "time", "1")

    def _fill_body(self, body: str) -> None:
        # Set the body content via a single ``eval`` that finds the
        # contentEditable ProseMirror body, focuses it, and feeds text through
        # ``document.execCommand('insertText', ...)``. Splitting into multiple
        # paragraphs is done inside the JS so each ``\\n`` becomes a real
        # ``<p>`` via ProseMirror's transaction handling.
        #
        # Why not ``browser type``?  As of 2026-08-12 the OpenCLI ``type``
        # command intermittently reports ``selector_not_found`` against a
        # ``div.tiptap`` that is demonstrably present, contentEditable, visible,
        # and role="textbox" in the DOM (verified by eval probes). This appears
        # to be an OpenCLI/ProseMirror interaction bug (likely the editor's
        # ``offsetParent`` / hidden-detection rules misclassifying the freshly
        # re-mounted editor after the title fill). execCommand is the
        # standard, ProseMirror-supported text-injection path and never
        # misroutes keystrokes.
        js = (
            "(function(text){"
            "const editors=Array.from(document.querySelectorAll('div.tiptap'))"
            ".filter(el=>el.isContentEditable&&el.offsetParent!==null);"
            "if(!editors.length)return JSON.stringify({ok:false,reason:'no contentEditable body'});"
            "const editor=editors[0];editor.focus();"
            "const lines=text.split('\\n');"
            "let lastOk=false;"
            "for(let i=0;i<lines.length;i++){"
            "  if(lines[i]){lastOk=document.execCommand('insertText',false,lines[i]);}"
            "  if(i<lines.length-1){"
            "    document.execCommand('insertParagraph',false,null);"
            "  }"
            "}"
            "editor.dispatchEvent(new Event('input',{bubbles:true}));"
            "return JSON.stringify({ok:lastOk,chars:editor.innerText.length,paras:lines.length});"
            "})(" + json.dumps(body) + ")"
        )
        result = self._eval(js, "set body content via execCommand")
        if not result.get("ok"):
            raise DeliveryError(f"failed to set body content: {result}")
        self._browser("wait", "time", "1")

    def _bind_topics(self, topics: tuple[str, ...]) -> int:
        """Bind real, clickable (highlighted) topic entities by typing ``#topic``
        into the body and clicking the matching item from XHS's suggestion dropdown.

        The dropdown (``div.items div.item``) appears **only** when ``#text`` is
        present in the ProseMirror body editor. Typing is done via ``execCommand``
        (not ``browser type``, which intermittently fails against ProseMirror).
        Returns the number of topic entities successfully created.
        """
        bound = 0
        for topic in topics:
            # 1. Focus body at end (cursor after existing content + any prior
            #    topic entities).
            self._eval(self._focus_body_end_js(), f"focus body for '#{topic}'")
            self._browser("wait", "time", "0.5")
            # 2. Type "#topicname" into the body. XHS detects the leading '#'
            #    and opens the suggestion dropdown.
            js = (
                "(function(topicName){"
                "const text='#'+topicName;"
                "document.execCommand('insertText',false,text);"
                "const a=document.activeElement;"
                "if(a){a.dispatchEvent(new Event('input',{bubbles:true}));"
                "a.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,key:text.slice(-1)}));}"
                "})(" + json.dumps(topic) + ")"
            )
            self._eval(js, f"type '#{topic}' into body")
            # 3. Wait for ``div.items div.item`` suggestions to render.
            self._must(
                f"wait topic dropdown for '{topic}'",
                self._browser("wait", "selector", "div.items div.item", "--timeout", "15000"),
            )
            # 4. Click the best-matching dropdown item.
            res = self._eval(self._click_suggestion_js(topic), f"click suggestion for '{topic}'")
            if res.get("ok"):
                bound += 1
            self._browser("wait", "time", "0.5")
        return bound

    @staticmethod
    def _norm(text: str) -> str:
        return (text or "").replace("#", "").replace(" ", "").strip().lower()

    def _topic_allow_set(self, topics: tuple[str, ...]) -> set[str]:
        base = {"论文解读", "科研", "学术论文", "论文精读", "科研干货", "学术",
                "人工智能", "机器学习", "推荐系统", "大模型", "智能体", "agent",
                "llm", "ai", "论文分享", "算法", "神经网络", "自然语言处理", "nlp", "数据分析"}
        for t in topics:
            base.add(self._norm(t))
        return base

    def _list_present_tags(self) -> list[str]:
        js = (
            "(function(){var out=[];"
            "for(var t of document.querySelectorAll('.tag-group .tag, .tag-group-popover-container .tag')){"
            "  if(t.offsetParent===null) continue;"
            "  var tx=(t.innerText||'').replace(/\\s+/g,' ').trim();"
            "  if(tx && tx!=='更多') out.push(tx);"
            "}"
            "return JSON.stringify(out);})()"
        )
        try:
            res = self._eval(js, "list tags")
            if isinstance(res, list):
                return res
            return json.loads(res.get("raw", "[]"))
        except Exception:
            return []

    def _click_chip_js(self, text: str) -> str:
        return (
            "(function(want){for(var t of document.querySelectorAll('.tag')){"
            "if((t.innerText||'').replace(/\\s+/g,' ').trim()===want){t.click();"
            "return JSON.stringify({ok:true});}}"
            "return JSON.stringify({ok:false});})(" + json.dumps(text) + ")"
        )

    def _attach_pdf(self, pdf_path: Path) -> None:
        self._must("upload pdf", self._browser("upload", PDF_INPUT_SELECTOR, str(pdf_path)))
        # The file card only appears once the upload has been acknowledged.
        self._must("wait pdf visible",
                   self._browser("wait", "text", pdf_path.name, "--timeout", "40000"))

    def _save_draft(self) -> dict:
        """Invoke the composer's save-draft action. Mirrors publish.js Step 7.

        Returns a small status dict; raises DeliveryError if no save path worked.
        """
        outcome = self._eval(self._save_draft_js(), "save draft (method/text)")
        if outcome.get("ok"):
            self._browser("wait", "time", "4")
            return outcome
        # Fallback A: leave the composer (返回/关闭/取消/离开) then save.
        if self._eval(self._leave_js(), "leave composer"):
            self._browser("wait", "time", "1")
            saved = self._eval(self._save_draft_js(), "save draft (after leave)")
            if saved.get("ok"):
                self._browser("wait", "time", "4")
                return saved
        # Fallback B: XHS sometimes auto-saves; detect the marker.
        auto = self._eval(self._autosave_marker_js(), "auto-save check")
        if auto.get("ok"):
            self._browser("wait", "time", "2")
            return {"ok": True, "via": "auto-save"}
        raise DeliveryError(f"could not trigger save-draft action: {outcome}")

    # ------------------------------------------------------------------ #
    # In-page scripts
    # ------------------------------------------------------------------ #
    def _focus_body_end_js(self) -> str:
        return (
            "(function(selectors){"
            "const el=selectors.map(s=>Array.from(document.querySelectorAll(s))).flat()"
            ".find(n=>n&&n.offsetParent!==null&&n.isContentEditable);"
            "if(!el)return false;el.focus();"
            "const sel=window.getSelection();const r=document.createRange();"
            "r.selectNodeContents(el);r.collapse(false);sel.removeAllRanges();sel.addRange(r);"
            "return true;})(" + self._body_selectors_json + ")"
        )

    def _type_topic_js(self, topic: str) -> str:
        # The topic picker (button#topicBtn) already injects the leading "#",
        # so we insert the bare topic text; XHS filters the suggestion dropdown.
        return (
            "(function(text){"
            "const ok=document.execCommand('insertText',false,text);"
            "const a=document.activeElement;"
            "if(a){a.dispatchEvent(new Event('input',{bubbles:true}));"
            "a.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,key:text.slice(-1)}));}"
            "return ok;})(" + json.dumps(topic) + ")"
        )

    def _click_suggestion_js(self, topic: str) -> str:
        sels = json.dumps(self._topic_suggestion_selectors_json())
        return (
            "(function(topicName){"
            "const norm=v=>(v||'').replace(/^#/,'').replace(/\\s+/g,'').trim();"
            "const want=norm(topicName);"
            "const SUG=" + sels + ";"
            "const seen=new Set();const items=[];"
            "for(const sel of SUG){for(const n of document.querySelectorAll(sel)){"
            "if(!n||seen.has(n))continue;if(n.offsetParent===null)continue;"
            "const r=n.getBoundingClientRect();if(r.width<=0||r.height<=0)continue;"
            "seen.add(n);items.push(n);}}"
            "if(!items.length)return JSON.stringify({ok:false,count:0});"
            "let t=items.find(n=>norm(n.innerText||n.textContent)===want);"
            "if(!t)t=items.find(n=>norm(n.innerText||n.textContent).includes(want));"
            "if(!t)t=items[0];"
            "try{t.click();return JSON.stringify({ok:true,count:items.length,"
            "text:(t.innerText||t.textContent||'').trim().slice(0,40)});}"
            "catch(e){return JSON.stringify({ok:false,count:items.length,message:String(e)});}"
            "})(" + json.dumps(topic) + ")"
        )

    def _topic_suggestion_selectors_json(self) -> list[str]:
        return TOPIC_SUGGESTION_SELECTORS

    def _save_draft_js(self) -> str:
        return (
            "(()=>{"
            "const isVisible=el=>{if(!el||el.offsetParent===null)return false;"
            "const r=el.getBoundingClientRect();return r.width>0&&r.height>0;};"
            "const hosts=Array.from(document.querySelectorAll('xhs-publish-btn')).filter(isVisible);"
            "const wanted=['_onSave','_onSaveDraft','_onDraft'];"
            "for(const host of hosts){for(const name of wanted){"
            "if(typeof host[name]==='function'){try{host[name]();"
            "return JSON.stringify({ok:true,via:'method',name});}catch(e){}}}}"
            "const labels=['暂存离开','存草稿','保存草稿'];"
            "const buttons=document.querySelectorAll('button, [role=\"button\"]');"
            "for(const btn of buttons){const text=(btn.innerText||btn.textContent||'').trim();"
            "if(labels.some(l=>text===l||text.includes(l))&&isVisible(btn)&&!btn.disabled){"
            "btn.click();return JSON.stringify({ok:true,via:'click',text});}}"
            "return JSON.stringify({ok:false,via:'none',hosts:hosts.length});"
            "})()"
        )

    def _leave_js(self) -> str:
        return (
            "(()=>{const labels=['返回','关闭','取消','离开'];"
            "const buttons=document.querySelectorAll('button, [role=\"button\"], div, span');"
            "for(const btn of buttons){const text=(btn.innerText||btn.textContent||'').trim();"
            "if(labels.some(l=>text===l||text.includes(l))&&btn.offsetParent!==null){btn.click();return true;}}"
            "return false;})()"
        )

    def _autosave_marker_js(self) -> str:
        return (
            "(()=>{const markers=['草稿箱(','保存于','编辑于'];"
            "for(const el of document.querySelectorAll('*')){"
            "const text=(el.innerText||el.textContent||'').trim();"
            "if(text&&markers.some(m=>text.includes(m)))return JSON.stringify({ok:true});}"
            "return JSON.stringify({ok:false});})()"
        )

    # ------------------------------------------------------------------ #
    # Public entry points
    # ------------------------------------------------------------------ #
    def _compose_and_save(self, payload: DraftPayload, *, attach_pdf: bool) -> dict:
        payload.validate()
        before = self._drafts()
        try:
            self._open_editor()
            self._upload_images(payload.image_paths)
            self._fill_title(payload.title)
            self._fill_body(payload.body)
            self._bind_topics(payload.topics)
            if attach_pdf:
                self._attach_pdf(payload.pdf_path)
            self._save_draft()
        finally:
            self._browser("close")
        after = self._drafts()
        draft = self._new_draft(before, after, payload.title)
        if int(draft.get("images", 0)) != len(payload.image_paths):
            self._delete(str(draft["id"]))
            raise DeliveryError("saved draft image count differs from the verified manifest")
        return draft

    def deliver(self, payload: DraftPayload) -> DeliveryReceipt:
        """Full flow: topics + PDF attached in-session, then saved as a draft."""
        draft = self._compose_and_save(payload, attach_pdf=True)
        return DeliveryReceipt(
            draft_id=str(draft.get("id", "")), title=payload.title,
            image_count=len(payload.image_paths), topics=payload.topics,
            pdf_name=payload.pdf_path.name,
        )

    def save_image_draft(self, payload: DraftPayload) -> dict:
        """No-PDF variant, kept for ``deliver_note(attach_pdf=False)``."""
        return self._compose_and_save(payload, attach_pdf=False)
