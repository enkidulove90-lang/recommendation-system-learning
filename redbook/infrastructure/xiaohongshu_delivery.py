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


def build_deliver_payload(args) -> "DraftPayload":
    """Build a DraftPayload from ``save-xhs-draft`` CLI args with mutual-exclusion checks.

    Kept beside :class:`DraftPayload` (stdlib-only) so CLI flag rules are
    testable without importing the heavyweight CLI module. Raises ValueError
    on ambiguous flags.
    """
    if args.skip_pdf_attachment and args.pdf is not None:
        raise ValueError("use either --pdf or --skip-pdf-attachment, not both")
    if not args.skip_pdf_attachment and args.pdf is None:
        raise ValueError("--pdf is required unless --skip-pdf-attachment is explicitly provided")
    draft = json.loads(args.draft.read_text(encoding="utf-8"))
    topics = tuple(str(item).lstrip("#") for item in draft.get("topics", []) if str(item).strip())
    return DraftPayload(
        title=str(draft["title"]), body=str(draft["body"]),
        image_paths=tuple(args.image), topics=topics,
        pdf_path=args.pdf,
        require_pdf_attachment=not args.skip_pdf_attachment,
        require_real_topics=not args.skip_topic_binding,
    )


class TopicEntityUnavailable(DeliveryError):
    """A requested Xiaohongshu topic has no selectable platform entity.

    Terminal eligibility result for the current paper: skip it (and record the
    candidates for the manual queue) instead of retrying or silently binding a
    wrong suggestion. Never falls back to body hashtags.
    """

    def __init__(self, topics: tuple[str, ...], detail: str = "") -> None:
        self.topics = topics
        rendered = ", ".join(repr(topic) for topic in topics)
        super().__init__(
            f"real Xiaohongshu topic entity unavailable for {rendered}"
            + (f"; {detail}" if detail else "")
            + "; skip the current paper (no body-hashtag fallback)"
        )


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
    pdf_path: Path | None
    require_real_topics: bool = True
    require_pdf_attachment: bool = True

    def validate(self) -> None:
        if not self.title or len(self.title) > 20:
            raise DeliveryError("Xiaohongshu title is required and must contain at most 20 characters")
        if not self.body.strip() or not self.image_paths:
            raise DeliveryError("body and at least one image are required")
        if self.require_real_topics and not self.topics:
            raise DeliveryError("real topic binding is mandatory; do not fall back to body hashtags")
        assets: tuple[Path, ...] = self.image_paths + ((self.pdf_path,) if self.pdf_path else ())
        missing = [str(path) for path in assets if not path.is_file()]
        if missing:
            raise DeliveryError(f"missing local delivery assets: {missing}")
        if self.require_pdf_attachment and self.pdf_path is None:
            raise DeliveryError("a PDF is required unless the explicit per-run waiver is enabled")
        if self.pdf_path is not None and self.pdf_path.suffix.casefold() != ".pdf":
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
        self._step_no = 0
        # PDF-attachment readiness polling (used by _wait_for_pdf_ready).
        self._pdf_poll_interval_seconds = 0.5
        self._pdf_ready_timeout_seconds = 60.0

    def _step(self, step: str, fn, *args, **kwargs):
        """Run one delivery step with structured JSONL logging (start/ok/fail).

        Every step writes to ``data/logs/runs.jsonl`` via ``log_event`` so a
        later failure (e.g. a changed topic selector) can be diagnosed from
        logs instead of a bare exception.  The step's return value is passed
        through unchanged; exceptions are logged and re-raised.
        """
        from redbook.infrastructure.run_log import log_event

        self._step_no += 1
        index = self._step_no
        started = __import__("time").monotonic()
        log_event("xhs_delivery_step", session=self.session, step_index=index,
                  step=step, status="start")
        try:
            result = fn(*args, **kwargs)
        except Exception as error:  # noqa: BLE001 - log every failure, then re-raise
            log_event("xhs_delivery_step", session=self.session, step_index=index,
                      step=step, status="failed",
                      error=f"{type(error).__name__}: {str(error)[:300]}",
                      duration_ms=int((__import__("time").monotonic() - started) * 1000))
            raise
        detail = ""
        if isinstance(result, dict):
            detail = {k: result[k] for k in ("id", "images", "draft_id", "topics")
                      if k in result}
        log_event("xhs_delivery_step", session=self.session, step_index=index,
                  step=step, status="ok", detail=detail,
                  duration_ms=int((__import__("time").monotonic() - started) * 1000))
        return result

    # ------------------------------------------------------------------ #
    # Command plumbing
    # ------------------------------------------------------------------ #
    def _command(self, *parts: str) -> list[str]:
        if self.runner is _run and len(parts) >= 3 and parts[0] == "browser" and parts[1] == self.session:
            parts = ("browser", "--session", self.session, *parts[2:])
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
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Some eval output is wrapped; return raw stdout for the caller.
            return {"raw": result.stdout}
        # OpenCLI v2 wraps page results as {"ok": true, "data": ...}; the
        # data itself is commonly a JSON string returned by our in-page script.
        if isinstance(payload, dict) and payload.get("ok") is True and "data" in payload:
            payload = payload["data"]
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    return {"raw": payload}
        if isinstance(payload, dict):
            return payload
        return {"data": payload}

    # ------------------------------------------------------------------ #
    # Drafts API (before/after reconciliation)
    # ------------------------------------------------------------------ #
    def _drafts(self) -> list[dict]:
        result = self.runner(self._command(
            "xiaohongshu", "drafts", "-f", "json", "--window", "background", "--site-session", "ephemeral"))
        if result.returncode:
            raise DeliveryError(result.stderr or result.stdout or "cannot read Xiaohongshu drafts")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise DeliveryError("Xiaohongshu drafts returned invalid JSON") from error
        if isinstance(payload, dict):
            payload = payload.get("data", [])
        if not isinstance(payload, list):
            raise DeliveryError("Xiaohongshu drafts returned an unexpected payload")
        return payload

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

    def _bind_topics_by_chip(self, topics: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
        """Try the recommended-``.tag``-chip path first.

        Returns (bound_count, topics_still_unbound).  Opens ``button#topicBtn``,
        lists visible ``.tag`` chips, clicks exact-normalized matches.  Chips
        rotate per session, so an unmatched topic is passed back to the legacy
        dropdown branch rather than treated as a terminal failure.
        """
        if not topics:
            return 0, topics
        from redbook.infrastructure.run_log import log_event
        cfg = self._topic_config().get("strategies", [{}])[0]
        buttons = cfg.get("panel_buttons") or [TOPIC_BUTTON_SELECTOR]

        clicked = ""
        for selector in buttons:
            open_js = ("(function(s){var el=document.querySelector(s);"
                       "if(!el)return JSON.stringify({ok:false});"
                       "el.click();return JSON.stringify({ok:true});})("
                       + json.dumps(selector) + ")")
            try:
                opened = self._eval(open_js, f"open topic panel via {selector}")
            except Exception:  # noqa: BLE001 - try next candidate
                continue
            if opened.get("ok"):
                clicked = selector
                break
        self._browser("wait", "time", "0.5")
        try:
            present = self._list_present_tags(cfg.get("chip_selectors"))
        except Exception as error:  # noqa: BLE001 - diagnostic, fall back
            log_event("xhs_topic_probe", session=self.session,
                      status="chip_probe_error", error=str(error)[:300])
            return 0, topics
        # Log what the live DOM actually offered so a later selector change is
        # diagnosable offline (instead of a bare "dropdown not found").
        probe = {"button_clicked": bool(opened.get("ok")),
                 "present_tags": [str(tag)[:30] for tag in present[:20]],
                 "wanted": [str(t)[:30] for t in topics]}
        if not present:
            # Dump candidate topic-ish elements with their classes so the next
            # selector fix can be made from data instead of guesswork.
            dom_js = (
                "(function(){var out=[];"
                "for(var n of document.querySelectorAll('*')){"
                "var tx=(n.innerText||'').replace(/\\s+/g,' ').trim();"
                "if(tx && tx.length<20 && /话题|论文|AI|人工智能|推荐|标签|topic/i.test(tx)"
                " && n.children.length===0){"
                "out.push({tag:n.tagName,cls:String(n.className||'').slice(0,80),text:tx.slice(0,20)});}}"
                "return JSON.stringify(out.slice(0,25));})()"
            )
            try:
                dom_res = self._eval(dom_js, "dump topic-ish DOM")
                probe["dom_candidates"] = dom_res if isinstance(dom_res, list) else []
            except Exception:  # noqa: BLE001 - diagnostic only
                probe["dom_candidates"] = []
        log_event("xhs_topic_probe", session=self.session,
                  status="chip_path", **probe)
        if not present:
            return 0, topics

        wanted = {self._norm(topic): topic for topic in topics}
        bound = 0
        unbound: list[str] = []
        for topic in topics:
            match = next((tag for tag in present if self._norm(tag) == self._norm(topic)), None)
            if match is None:
                unbound.append(topic)
                continue
            res = self._eval(self._click_chip_js(match), f"click topic chip '{match}'")
            if res.get("ok"):
                bound += 1
                self._browser("wait", "time", "0.3")
            else:
                unbound.append(topic)
        return bound, tuple(unbound)

    def _bind_topics(self, topics: tuple[str, ...]) -> int:
        """Bind real topic entities, preferring recommended chips.

        Two platform shapes exist (both seen on this account):
          A. recommended ``.tag`` chips behind ``button#topicBtn`` (current);
          B. a searchable dropdown opened by typing ``#text`` into the
             ProseMirror body — typing '#' is only the trigger prefix: the
             draft must end up storing topic ENTITIES (keyword + hyperlink),
             never literal ``#topic`` text.  Exact match is mandatory in both
             branches — no ``items[0]`` fallback.
        """
        bound = 0
        remaining = self._bind_topics_by_chip(topics)
        bound += remaining[0]
        topics = remaining[1]
        if not topics:
            return bound
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
            # 3. Wait for a suggestion dropdown from the configured selectors.
            # No dropdown means the platform offers no entity for this topic:
            # terminal ineligibility, never a silent skip.
            dropdown_cfg = next(
                (s for s in self._topic_config().get("strategies", [])
                 if s.get("name") == "search_dropdown"), {})
            dropdown_selectors = dropdown_cfg.get("dropdown_selectors") or ["div.items div.item"]
            appeared = False
            for selector in dropdown_selectors:
                wait = self._browser("wait", "selector", selector, "--timeout", "5000")
                if not wait.returncode:
                    appeared = True
                    break
            if not appeared:
                raise TopicEntityUnavailable(
                    (topic,), detail=f"no dropdown among {dropdown_selectors}")
            # 4. Click the exactly-matching dropdown item. Exact match only:
            # no ``items[0]`` fallback, wrong-entity binding is a failure.
            try:
                res = self._eval(self._click_suggestion_js(topic), f"click suggestion for '{topic}'")
            except DeliveryError as error:
                raise TopicEntityUnavailable((topic,), detail=str(error)) from error
            if not res.get("ok"):
                raise TopicEntityUnavailable((topic,), detail=f"no exact suggestion match: {res}")
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

    def _topic_config(self) -> dict:
        """Load topic selector strategies from config (single source of truth)."""
        path = Path(__file__).resolve().parents[2] / "config" / "xhs_topic_selectors.yaml"
        if not path.is_file():
            return {}
        try:
            import yaml
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}

    def _list_present_tags(self, selectors: list[str] | None = None) -> list[str]:
        selectors = selectors or ['.tag-group .tag', '.tag-group-popover-container .tag']
        js = ("(function(sels){var out=[];var seen=new Set();"
              "for(var sel of sels){for(var t of document.querySelectorAll(sel)){"
              "  if(!t||seen.has(t)||t.offsetParent===null) continue;"
              "  seen.add(t);"
              "  var tx=(t.innerText||'').replace(/\\s+/g,' ').trim();"
              "  if(tx && tx!=='更多') out.push(tx);"
              "}}"
              "return JSON.stringify(out);})(" + json.dumps(selectors) + ")")
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

    def _install_pdf_upload_probe(self, pdf_path: Path) -> None:
        """Observe the PDF request itself; selecting a local file is not success."""
        name = json.dumps(pdf_path.name)
        js = (
            "(()=>{const fileName=" + name + ";"
            "const fresh=()=>({name:fileName,startedAt:Date.now(),seen:0,pending:0,"
            "success:0,failed:0,lastStatus:0,error:''});"
            "window.__redbookPdfUploadProbe=fresh();"
            "if(window.__redbookPdfUploadHooks)return JSON.stringify({ok:true,reused:true});"
            "window.__redbookPdfUploadHooks=true;"
            "const isPdfBody=body=>{if(!(body instanceof FormData))return false;"
            "for(const pair of body.entries()){const value=pair[1];"
            "if(value instanceof File&&(value.name===fileName||value.type==='application/pdf'))return true;}"
            "return false;};"
            "const finish=(probe,status,error)=>{probe.pending=Math.max(0,probe.pending-1);"
            "probe.lastStatus=Number(status)||0;if(status>=200&&status<300){probe.success++;}"
            "else{probe.failed++;probe.error=error||('HTTP '+status);}};"
            "const originalFetch=window.fetch;window.fetch=async function(input,init){"
            "const probe=window.__redbookPdfUploadProbe;const matched=probe&&isPdfBody(init&&init.body);"
            "if(matched){probe.seen++;probe.pending++;}try{const response=await originalFetch.apply(this,arguments);"
            "if(matched)finish(probe,response.status,response.ok?'':'HTTP '+response.status);return response;}"
            "catch(error){if(matched)finish(probe,0,String(error));throw error;}};"
            "const originalOpen=XMLHttpRequest.prototype.open;const originalSend=XMLHttpRequest.prototype.send;"
            "XMLHttpRequest.prototype.open=function(method,url){this.__redbookUploadUrl=String(url||'');"
            "return originalOpen.apply(this,arguments);};"
            "XMLHttpRequest.prototype.send=function(body){const probe=window.__redbookPdfUploadProbe;"
            "const matched=probe&&isPdfBody(body);if(matched){probe.seen++;probe.pending++;"
            "this.addEventListener('loadend',()=>finish(probe,this.status,this.statusText||''),{once:true});}"
            "return originalSend.apply(this,arguments);};"
            "return JSON.stringify({ok:true,reused:false});})()"
        )
        result = self._eval(js, "install PDF upload response probe")
        if not result.get("ok"):
            raise DeliveryError(f"could not install PDF upload response probe: {result}")

    def _read_pdf_upload_state(self, pdf_path: Path) -> dict:
        name = json.dumps(pdf_path.name)
        js = (
            "(()=>{const fileName=" + name + ";const probe=window.__redbookPdfUploadProbe||{};"
            "const visible=e=>{if(!e||e.offsetParent===null)return false;"
            "const r=e.getBoundingClientRect();return r.width>0&&r.height>0;};"
            "const roots=Array.from(document.querySelectorAll('.file-relation-container,.setting-card-wrapper,.setting-card'))"
            ".filter(visible);const card=roots.find(e=>(e.innerText||e.textContent||'').includes(fileName));"
            "const text=card?(card.innerText||card.textContent||''):'';"
            "const loading=!!(card&&Array.from(card.querySelectorAll('[class*=loading],[class*=progress],[aria-busy=true]'))"
            ".some(visible))||/上传中|处理中|正在上传/.test(text);"
            "const domError=(text.match(/上传失败|网络异常|文件过大|格式不支持|请重试/)||[])[0]||'';"
            "const networkError=probe.failed>0?(probe.error||'PDF upload request failed'):'';"
            "const error=domError||networkError;const networkSeen=(probe.seen||0)>0;"
            "const networkOk=(probe.success||0)>0&&(probe.pending||0)===0&&(probe.failed||0)===0;"
            "const age=Date.now()-(probe.startedAt||Date.now());"
            "let state='pending';if(error)state='error';"
            "else if(card&&!loading&&(networkOk||(!networkSeen&&age>=3000)))state='complete';"
            "return JSON.stringify({state,card_visible:!!card,loading,network_seen:networkSeen,"
            "network_ok:networkOk,pending:probe.pending||0,status:probe.lastStatus||0,error});})()"
        )
        return self._eval(js, "read PDF upload completion state")

    def _attach_pdf(self, pdf_path: Path) -> None:
        self._install_pdf_upload_probe(pdf_path)
        self._must("upload pdf", self._browser("upload", PDF_INPUT_SELECTOR, str(pdf_path)))
        deadline = time.monotonic() + self._pdf_ready_timeout_seconds
        stable_dom_samples = 0
        last_state: dict = {}
        while True:
            last_state = self._read_pdf_upload_state(pdf_path)
            error = str(last_state.get("error") or "")
            if last_state.get("state") == "error" or error:
                raise DeliveryError(f"PDF upload failed before draft save: {error or last_state}")
            complete = (
                last_state.get("state") == "complete"
                and last_state.get("card_visible") is True
                and last_state.get("loading") is False
            )
            if complete and last_state.get("network_ok") is True:
                return
            if complete and last_state.get("network_seen") is False:
                stable_dom_samples += 1
                if stable_dom_samples >= 2:
                    return
            else:
                stable_dom_samples = 0
            if time.monotonic() >= deadline:
                raise DeliveryError(f"PDF upload did not reach a completed state: {last_state}")
            time.sleep(self._pdf_poll_interval_seconds)

    def _verify_saved_draft(self, draft_id: str, payload: DraftPayload) -> dict:
        """Reopen one draft and prove its body, topics, and PDF persisted together."""
        verifier = OpenCliXiaohongshuDelivery(
            runner=self.runner, session=f"{self.session}-verify-{int(time.time() * 1000)}"
        )
        verifier._must(
            "open creator for saved-draft verification",
            verifier._browser("open", self.creator_url, "--window", "background"),
        )
        try:
            return verifier._eval(
                self._saved_draft_verification_js(draft_id, payload),
                "reopen saved draft and verify body, topics, and PDF",
            )
        finally:
            verifier._browser("close")

    def _saved_draft_verification_js(self, draft_id: str, payload: DraftPayload) -> str:
        draft_key = draft_id[2:] if draft_id.startswith("s:") else draft_id
        expected_name = json.dumps(payload.pdf_path.name)
        expected_size = payload.pdf_path.stat().st_size
        expected_body = json.dumps(payload.body)
        expected_topics = json.dumps(list(payload.topics))
        return (
            "(async()=>{const draftKey=" + json.dumps(draft_key) + ";"
            "const expectedName=" + expected_name + ";const expectedSize=" + str(expected_size) + ";"
            "const expectedBody=" + expected_body + ";const expectedTopics=" + expected_topics + ";"
            "const norm=value=>String(value||'').replace(/\\s+/g,'').trim();"
            "const containsExpected=(actual,expected)=>norm(actual).includes(norm(expected));"
            "const visible=e=>{if(!e||e.offsetParent===null)return false;"
            "const r=e.getBoundingClientRect();return r.width>0&&r.height>0;};"
            "const waitFor=async(fn,label,timeout=30000)=>{const start=Date.now();while(Date.now()-start<timeout){"
            "const value=fn();if(value)return value;await new Promise(r=>setTimeout(r,100));}"
            "throw new Error('timeout waiting for '+label);};"
            "try{const draftButton=await waitFor(()=>document.querySelector('.draft-title-box'),'draft box');"
            "draftButton.click();const tabs=await waitFor(()=>Array.from(document.querySelectorAll('.draft-tabs .tab-item'))"
            ".find(e=>(e.innerText||'').includes('图文笔记')),'image draft tab');tabs.click();"
            "const item=await waitFor(()=>Array.from(document.querySelectorAll('.draft-item'))"
            ".find(e=>e.dataset.draftId===draftKey),'saved draft card');"
            "const edit=item.querySelector('.draft-actions .btn');if(!edit)throw new Error('draft edit action missing');"
            "edit.click();await waitFor(()=>Array.from(document.querySelectorAll('input'))"
            ".find(e=>(e.placeholder||'').includes('标题')),'draft editor');"
            "await new Promise(r=>setTimeout(r,300));"
            "const roots=Array.from(document.querySelectorAll('.file-relation-container,.setting-card-wrapper,.setting-card'))"
            ".filter(visible);const card=roots.find(e=>(e.innerText||e.textContent||'').includes(expectedName));"
            "const cardText=card?(card.innerText||card.textContent||''):'';"
            "const loading=!!(card&&Array.from(card.querySelectorAll('[class*=loading],[class*=progress],[aria-busy=true]'))"
            ".some(visible))||/上传中|处理中|正在上传/.test(cardText);"
            "const domError=(cardText.match(/上传失败|网络异常|文件过大|格式不支持|请重试/)||[])[0]||'';"
            "const db=await new Promise((ok,bad)=>{const r=indexedDB.open('draft-database-v1');"
            "r.onsuccess=()=>ok(r.result);r.onerror=()=>bad(r.error);});"
            "const tx=db.transaction('image-draft','readonly');const store=tx.objectStore('image-draft');"
            "const row=await new Promise((ok,bad)=>{const r=store.get(draftKey);"
            "r.onsuccess=()=>ok(r.result);r.onerror=()=>bad(r.error);});db.close();"
            "const draftStore=row&&row.content&&row.content.draftStore||{};"
            "const relation=row&&row.content&&row.content.settingStore&&row.content.settingStore.fileRelate||{};"
            "const documentId=String(relation.docId||relation.fileId||'');"
            "const storedName=String(relation.docName||relation.docShowName||'');"
            "const storedSize=Number(relation.docSize||0);"
            "const recordOk=!!documentId&&storedName===expectedName&&storedSize===expectedSize;"
            "const cardVisible=!!card&&!loading&&!domError;const ok=recordOk&&cardVisible;"
            "const editor=Array.from(document.querySelectorAll('div[contenteditable=true]')).find(visible);"
            "const persistedBody=draftStore.desc||draftStore.descInnerHTML||'';"
            "const visibleBody=editor?(editor.innerText||editor.textContent||''):'';"
            "const bodyOk=containsExpected(persistedBody,expectedBody)&&containsExpected(visibleBody,expectedBody);"
            "const storedTopics=Array.isArray(draftStore.hashTag)?draftStore.hashTag:[];"
            "const storedNames=storedTopics.map(t=>String(t&&t.name||''));"
            "const visibleText=editor?(editor.innerText||editor.textContent||''):'';"
            "const topicsOk=expectedTopics.every(t=>storedNames.includes(t)&&visibleText.includes('#'+t+'[话题]'));"
            "const allOk=recordOk&&cardVisible&&bodyOk&&topicsOk;"
            "return JSON.stringify({ok:allOk,card_visible:cardVisible,document_id:documentId,name:storedName,"
            "size:storedSize,body_ok:bodyOk,topics_ok:topicsOk,error:allOk?'':(domError||(!card?'attachment card missing after reopen':"
            "!bodyOk?'saved body does not match expected text':!topicsOk?'saved topic entities do not match expected topics':"
            "!documentId?'saved attachment has no server document id':'saved attachment metadata mismatch'))});"
            "}catch(error){return JSON.stringify({ok:false,card_visible:false,document_id:'',"
            "name:expectedName,size:0,error:String(error&&error.message||error)});}})()"
        )

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
            "const norm=v=>((v||'').split('\\n')[0]).replace(/^#/,'').replace(/\\s+/g,'').trim();"
            "const want=norm(topicName);"
            "const SUG=" + sels + ";"
            "const seen=new Set();const items=[];"
            "for(const sel of SUG){for(const n of document.querySelectorAll(sel)){"
            "if(!n||seen.has(n))continue;if(n.offsetParent===null)continue;"
            "const r=n.getBoundingClientRect();if(r.width<=0||r.height<=0)continue;"
            "seen.add(n);items.push(n);}}"
            "if(!items.length)return JSON.stringify({ok:false,count:0});"
            "let t=items.find(n=>norm(n.innerText||n.textContent)===want);"
            "if(!t)return JSON.stringify({ok:false,count:items.length,reason:'no exact match',"
            "candidates:items.slice(0,10).map(n=>((n.innerText||n.textContent||'').trim().slice(0,20)))});"
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
        before = self._step("list_drafts_before", self._drafts)
        try:
            self._step("open_editor", self._open_editor)
            self._step("upload_images", self._upload_images, payload.image_paths)
            self._step("fill_title", self._fill_title, payload.title)
            self._step("fill_body", self._fill_body, payload.body)
            self._step("bind_topics", self._bind_topics, payload.topics)
            if attach_pdf:
                self._step("attach_pdf", self._attach_pdf, payload.pdf_path)
            self._step("save_draft", self._save_draft)
            after = self._step("list_drafts_after", self._drafts)
            draft = self._step("new_draft", self._new_draft, before, after, payload.title)
            if int(draft.get("images", 0)) != len(payload.image_paths):
                self._delete(str(draft["id"]))
                raise DeliveryError("saved draft image count differs from the verified manifest")
            if attach_pdf:
                verification = self._step("verify_saved_draft", self._verify_saved_draft,
                                          str(draft["id"]), payload)
                if not verification.get("ok"):
                    self._delete(str(draft["id"]))
                    detail = verification.get("error") or verification
                    raise DeliveryError(f"saved draft verification failed: {detail}")
            return draft
        finally:
            self._browser("close")

    def deliver(self, payload: DraftPayload) -> DeliveryReceipt:
        """Full flow: topics (+PDF when provided) attached in-session, then saved as a draft."""
        draft = self._compose_and_save(payload, attach_pdf=payload.pdf_path is not None)
        return DeliveryReceipt(
            draft_id=str(draft.get("id", "")), title=payload.title,
            image_count=len(payload.image_paths), topics=payload.topics,
            pdf_name=payload.pdf_path.name if payload.pdf_path else "",
        )

    def save_image_draft(self, payload: DraftPayload) -> dict:
        """No-PDF variant, kept for ``deliver_note(attach_pdf=False)``."""
        return self._compose_and_save(payload, attach_pdf=False)
