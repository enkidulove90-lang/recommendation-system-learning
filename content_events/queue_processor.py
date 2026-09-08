"""队列处理器（content_events/queue_processor.py）。

对应设计 §4：把 publish_queue/<dir>/<platform>.json 驱动为内容生命周期事件流：
  intake → (RENDER_REQUEST→RENDERED) → (VALIDATED) → (STAGED) → [人工 publish]
沙箱无网络/未审核时：stage 降级本地待发布包（设计 04 §风控 1）。

本轮优化（详见 docs/content-event-optimization-design.md）：
- O1 幂等跨目录：新增全局幂等注册表（idem_registry.jsonl），同 idem_key 终态只处理一次
- O2 原子+韧性持久化：state.json 临时文件 + os.replace；事件日志 fsync（event_log 侧）
- O3 瞬时失败重试+退避：stage 调用套 retry_call（仅瞬时异常重试）
- O6 可观测性：RunSummary 聚合；每项错误计入摘要，不中断整轮
- O7 健壮性：坏 JSON / 无包目录 优雅跳过，不崩整轮
- O10 生命周期事件：render 前显式 emit RENDER_REQUEST
- D2 侧车容忍：resolve_sidecars 跨兄弟目录聚合 viz/interaction 等侧车
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional

from .event_log import EventLog
from .publishers import PublishingError, make_publisher
from .retry import RetryPolicy, retry_call
from .schema import (
    ContentEvent,
    ContentItem,
    ContentState,
    EventType,
    RunSummary,
    fs_safe,
)
from . import state_machine as sm

logger = logging.getLogger(__name__)

_SIDECAR_NAMES = ("viz.json", "interaction.json", "analytics.json", "distribution.json")
_PACKAGE_EXT = (".json",)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# 幂等注册表（O1）：跨 publish_queue 目录去重，防止同 idem_key 重复 stage/publish
# --------------------------------------------------------------------------- #
class IdempotencyRegistry:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._cache: Dict[str, str] = {}
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    def _scan(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except (json.JSONDecodeError, ValueError):
                        continue
                    k = d.get("idem_key")
                    s = d.get("state")
                    if k and s:
                        self._cache.setdefault(k, s)
        except FileNotFoundError:
            pass

    def terminal_state(self, key: str) -> Optional[str]:
        if key in self._cache:
            s = self._cache[key]
            return s if s in (ContentState.STAGED.value, ContentState.PUBLISHED.value) else None
        self._scan()
        s = self._cache.get(key)
        return s if s in (ContentState.STAGED.value, ContentState.PUBLISHED.value) else None

    def mark(self, key: str, state: str, paper_id: str = "", platform: str = "") -> None:
        self._cache[key] = state
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(
                    {"idem_key": key, "state": state, "ts": _now(),
                     "paper_id": paper_id, "platform": platform},
                    ensure_ascii=False,
                ) + "\n")
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass


def _default_registry_path(artifacts_root: str) -> str:
    # artifacts_root = <root>/data/publish_artifacts → <root>/data/content_events/idem_registry.jsonl
    return os.path.join(os.path.dirname(artifacts_root), "content_events", "idem_registry.jsonl")


# --------------------------------------------------------------------------- #
# 渲染（守卫 DTLE）
# --------------------------------------------------------------------------- #
def _render_html_and_png(item: ContentItem, theme: str, artifacts_dir: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        import importlib

        dtle = importlib.import_module("wechat_design.dtle")
        btrack = importlib.import_module("wechat_design.dtle.renderers.btrack")
        docmod = importlib.import_module("wechat_design.dtle.core.document")

        os.makedirs(artifacts_dir, exist_ok=True)
        md = item.body_markdown or item.title
        ro = dtle.render_markdown(md, track=item.platform, theme=theme, title=item.title)
        if ro.html:
            html_path = os.path.join(artifacts_dir, "index.html" if item.platform == "wechat" else "card.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(ro.html)
            out["html_path"] = html_path
            out["gate"] = ro.gate
        if item.platform in ("xhs", "wechat") and ro.html:
            try:
                doc = docmod.parse_markdown(md, title=item.title, theme=theme)
                from wechat_design.dtle.core.types import ThemeTokens

                png_path = os.path.join(artifacts_dir, "card.png")
                res = btrack.render_btrack(
                    doc, ThemeTokens.load(theme), backend="production",
                    out_path=png_path, png=True,
                )
                if os.path.exists(png_path):
                    out["png_path"] = png_path
                else:
                    out["note"] = res.get("note") or res.get("error")
            except Exception as e:  # noqa: BLE001
                out["note"] = f"PNG 跳过: {e}"
    except Exception as e:  # noqa: BLE001
        out["render_error"] = str(e)
    return out


# --------------------------------------------------------------------------- #
# 状态持久化（O2：原子写）
# --------------------------------------------------------------------------- #
def _load_state(queue_dir: str) -> Optional[Dict[str, Any]]:
    sp = os.path.join(queue_dir, "state.json")
    if os.path.exists(sp):
        try:
            with open(sp, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # 损坏的 state.json 不致命：视为无状态，重新处理（修复 B2 静默吞错）
            logger.warning("[queue_processor] state.json 损坏，按无状态处理: %s", sp)
            return None
    return None


def _save_state(queue_dir: str, item: ContentItem) -> None:
    sp = os.path.join(queue_dir, "state.json")
    tmp = sp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, sp)  # 原子替换，防止半截写入（修复 B2）


# --------------------------------------------------------------------------- #
# 侧车容忍解析（D2）：聚合同 paper_id 的 viz/interaction/analytics/distribution
# --------------------------------------------------------------------------- #
def resolve_sidecars(root: str, paper_id: str) -> Dict[str, str]:
    """扫描 publish_queue 下所有目录，收集与 paper_id 关联的侧车文件路径。

    设计 D2：content_factory 可能把侧车写到与平台包不同的目录。这里跨兄弟目录
    按 paper_id 关联，确保编排层能取到侧车（best-effort，不阻断主流程）。
    """
    found: Dict[str, str] = {}
    qroot = os.path.join(root, "publish_queue")
    if not os.path.isdir(qroot):
        return found
    for name in sorted(os.listdir(qroot)):
        d = os.path.join(qroot, name)
        if not os.path.isdir(d):
            continue
        # 找该目录里的平台包以确定 paper_id
        pkg_file = None
        for fn in os.listdir(d):
            if fn.endswith(".json") and fn not in ("state.json",) and fn not in _SIDECAR_NAMES:
                pkg_file = os.path.join(d, fn)
                break
        dir_paper = ""
        if pkg_file:
            try:
                with open(pkg_file, encoding="utf-8") as _pf:
                    dir_paper = str(json.loads(_pf.read()).get("paper_id", ""))
            except (json.JSONDecodeError, OSError):
                dir_paper = ""
        if dir_paper and dir_paper != paper_id:
            continue
        for sc in _SIDECAR_NAMES:
            scp = os.path.join(d, sc)
            if os.path.exists(scp):
                found[sc] = scp
    return found


# --------------------------------------------------------------------------- #
# 单条目处理
# --------------------------------------------------------------------------- #
def process_item(
    queue_dir: str,
    publisher_name: str,
    event_log: EventLog,
    artifacts_root: str,
    theme: str = "recsys-blue",
    *,
    dry_run: bool = True,
    idem_registry: Optional[IdempotencyRegistry] = None,
    run_summary: Optional[RunSummary] = None,
    retry_policy: Optional[RetryPolicy] = None,
    root: Optional[str] = None,
) -> Dict[str, Any]:
    """处理单个 publish_queue 子目录（应含 <platform>.json）。返回处理摘要。

    任何未预期异常都被捕获并计入 run_summary.errors，避免单条目崩掉整轮（O7）。
    """
    summary: Dict[str, Any] = {"queue_dir": os.path.basename(queue_dir)}
    if run_summary is not None:
        run_summary.scanned += 1

    reg = idem_registry or IdempotencyRegistry(_default_registry_path(artifacts_root))

    try:
        jsons = [
            f for f in os.listdir(queue_dir)
            if f.endswith(".json") and f != "state.json" and f not in _SIDECAR_NAMES
        ]
        if not jsons:
            summary["skipped"] = "no_package_json"
            if run_summary is not None:
                run_summary.skipped_other += 1
                run_summary.skipped_detail.append(queue_dir)
            return summary

        pkg_path = os.path.join(queue_dir, jsons[0])
        try:
            with open(pkg_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            summary["skipped"] = "bad_package_json"
            summary["error"] = str(e)
            if run_summary is not None:
                run_summary.errors += 1
            event_log.append(ContentEvent(EventType.NEEDS_REVIEW, queue_dir, _now(),
                                          {"why": "bad_json", "err": str(e)}))
            return summary

        item = ContentItem.from_queue_json(data)
        key = item.idem_key
        summary["key"] = key
        summary["platform"] = item.platform
        summary["state"] = item.state.value

        # ---- 幂等（O1）：全局注册表优先，再回退 per-dir state.json ----
        term = reg.terminal_state(key)
        if term:
            summary["skipped"] = f"already_{term}"
            if run_summary is not None:
                run_summary.skipped_idempotent += 1
            return summary
        st = _load_state(queue_dir)
        if st and st.get("state") in (ContentState.STAGED.value, ContentState.PUBLISHED.value):
            summary["skipped"] = f"already_{st['state']}"
            reg.mark(key, st["state"], item.paper_id, item.platform)
            if run_summary is not None:
                run_summary.skipped_idempotent += 1
            return summary

        event_log.append(ContentEvent(EventType.CONTENT_INTAKE, key, _now(),
                                      {"paper_id": item.paper_id, "platform": item.platform}))

        # ---- 1) 渲染（O10：先发 RENDER_REQUEST）----
        artifacts_dir = os.path.join(artifacts_root, fs_safe(key))
        event_log.append(ContentEvent(EventType.RENDER_REQUEST, key, _now(), {"theme": theme}))
        render = _render_html_and_png(item, theme, artifacts_dir)
        if render.get("render_error"):
            item.errors.append(render["render_error"])
            item.state = ContentState.NEEDS_REVIEW
            event_log.append(ContentEvent(EventType.NEEDS_REVIEW, key, _now(),
                                          {"why": "render", "err": render["render_error"]}))
            _save_state(queue_dir, item)
            summary.update(state=item.state.value, error=render["render_error"])
            if run_summary is not None:
                run_summary.needs_review += 1
            return summary
        event_log.append(ContentEvent(EventType.RENDERED, key, _now(),
                                      {k: v for k, v in render.items() if k in ("html_path", "png_path", "gate")}))
        item.state = sm.transition(item.state, EventType.RENDERED).to_state

        # ---- 2) 校验 ----
        is_real = publisher_name in ("wechat", "xhs") and item.review_status == "approved"
        eff_dry_run = dry_run or not is_real
        eff_name = publisher_name if not eff_dry_run else "dryrun"
        publisher = make_publisher(eff_name, os.path.join(artifacts_root, "..", "publish_results"),
                                   dry_run=eff_dry_run)
        verrs = publisher.validate(data)
        if verrs:
            item.errors.extend(verrs)
            item.state = ContentState.NEEDS_REVIEW
            event_log.append(ContentEvent(EventType.NEEDS_REVIEW, key, _now(),
                                          {"why": "validate", "errs": verrs}))
            _save_state(queue_dir, item)
            summary.update(state=item.state.value, errors=verrs)
            if run_summary is not None:
                run_summary.needs_review += 1
            return summary
        event_log.append(ContentEvent(EventType.VALIDATED, key, _now()))
        item.state = sm.transition(item.state, EventType.VALIDATED).to_state

        # ---- 3) stage（O3：瞬时失败重试；O7：统一 PublishingError→needs_review）----
        try:
            rcpt = retry_call(lambda: publisher.stage(data), retry_policy, logger)
            item.external_id = rcpt.get("external_id", "")
            item.state = sm.transition(item.state, EventType.STAGED).to_state
            event_log.append(ContentEvent(EventType.STAGED, key, _now(),
                                          {"external_id": item.external_id, "mode": rcpt.get("mode", eff_name)}))
            reg.mark(key, ContentState.STAGED.value, item.paper_id, item.platform)
        except PublishingError as e:
            item.errors.append(str(e))
            item.state = ContentState.NEEDS_REVIEW
            event_log.append(ContentEvent(EventType.NEEDS_REVIEW, key, _now(),
                                          {"why": "stage", "err": str(e)}))
            if run_summary is not None:
                run_summary.needs_review += 1

        _save_state(queue_dir, item)
        # 侧车容忍（D2）
        sidecars = resolve_sidecars(root or os.path.dirname(os.path.dirname(artifacts_root)), item.paper_id)
        summary.update(state=item.state.value, external_id=item.external_id,
                       artifacts=render, sidecars=list(sidecars.keys()))
        if run_summary is not None:
            run_summary.processed += 1
            if item.state == ContentState.PUBLISHED:
                run_summary.published += 1
        return summary

    except Exception as e:  # noqa: BLE001
        # 未预期错误：记录到摘要与事件，不中断整轮（O7）
        summary["error"] = str(e)
        summary["state"] = ContentState.NEEDS_REVIEW.value
        if run_summary is not None:
            run_summary.errors += 1
        logger.exception("[queue_processor] 未预期错误 %s: %s", queue_dir, e)
        try:
            event_log.append(ContentEvent(EventType.NEEDS_REVIEW, queue_dir, _now(),
                                          {"why": "unexpected", "err": str(e)}))
        except Exception:  # noqa: BLE001
            pass
        return summary


def process_queue(
    root: str,
    publisher_name: str = "dryrun",
    theme: str = "recsys-blue",
    *,
    dry_run: bool = True,
    retry_policy: Optional[RetryPolicy] = None,
) -> "tuple[List[Dict[str, Any]], RunSummary]":
    """扫描 root/publish_queue/ 全部子目录并驱动。返回 (摘要列表, RunSummary)。"""
    qroot = os.path.join(root, "publish_queue")
    aroot = os.path.join(root, "data", "publish_artifacts")
    os.makedirs(aroot, exist_ok=True)
    elog = EventLog(os.path.join(root, "data", "content_events", "events.jsonl"))
    reg = IdempotencyRegistry(_default_registry_path(aroot))
    run_summary = RunSummary()
    results: List[Dict[str, Any]] = []
    if not os.path.isdir(qroot):
        return results, run_summary
    for name in sorted(os.listdir(qroot)):
        qd = os.path.join(qroot, name)
        if os.path.isdir(qd):
            results.append(process_item(
                qd, publisher_name, elog, aroot, theme,
                dry_run=dry_run, idem_registry=reg, run_summary=run_summary,
                retry_policy=retry_policy, root=root,
            ))
    return results, run_summary
