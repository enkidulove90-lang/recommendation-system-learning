"""Deliver compiled platform packages to their real destinations.

This is the S5 delivery stage: ``ContentFactory.compile_shared`` produces
local packages (XHS note YAML, WeChat staged package, Notion review package);
this module pushes each to the real platform using the same publishers the CLI
uses. Human-review gates were removed by user decision (2026-11-28): as long as
field completeness passes the publishers' own ``validate``, delivery proceeds.

Design notes
------------
- Each platform is delivered independently; one failure never aborts the rest.
- Returns a structured per-platform receipt: ``{ok, method, ...}``.
- XHS: YAML -> PaperCreationWorkflow.publish_note(slug) (rebuilds package then
  stages + CDP-publishes).
- WeChat: WeChatPublisher.publish(staged_id) consumes the staged package.
- Notion: shell out to the blog repo's publish_review_package.py CLI with
  ``--write-notion`` (idempotent: skip_if_exists by default).

Nothing here fabricates a receipt: if opencli/browser/login is unavailable the
publisher returns ``ok=False`` and we pass that through verbatim.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLOG_REPO = Path("D:/enkidulove90-lang.github.io")


def _delete_xhs_draft(draft_id: str) -> dict[str, Any]:
    """Best-effort delete of an old XHS draft via opencli (used for overwrite)."""
    from redbook.infrastructure import opencli_runtime

    try:
        runtime = opencli_runtime.resolve_runtime()
        result = runtime.run(
            "xiaohongshu", "draft-delete", str(draft_id),
            "--type", "image", "--execute", "true", "-f", "json", timeout=120)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"ok": result.returncode == 0,
            "stdout": (result.stdout or "")[:300]}


def deliver_xhs(note_path: str) -> dict[str, Any]:
    """Publish the XHS note to the draft box, refreshing any prior draft.

    Overwrite semantics (user decision): each run creates a fresh draft and,
    only on success, deletes the previously-ledgered draft so exactly one
    current draft exists per note. A failed create never deletes the old one.
    """
    from redbook.application.paper_workflow import PaperCreationWorkflow
    from scripts import delivery_ledger

    note = Path(note_path)
    if not note.is_file():
        return {"ok": False, "platform": "xhs", "error": f"note yaml missing: {note}"}
    slug = note.stem
    paper_key = _note_paper_key(note) or slug

    def _create() -> str | None:
        workflow = PaperCreationWorkflow(ROOT / "data")
        receipt = workflow.publish_note(slug, notes_dir=note.parent)
        if not receipt.get("ok"):
            return None
        return str(receipt.get("draft_id") or "")

    try:
        outcome = delivery_ledger.refresh_xhs_draft(
            paper_key, create=_create, delete=_delete_xhs_draft)
    except Exception as exc:  # noqa: BLE001 — surface real cause verbatim.
        return {"ok": False, "platform": "xhs", "error": f"{type(exc).__name__}: {exc}"}
    if not outcome.get("ok"):
        return {"platform": "xhs", "ok": False, "error": outcome.get("reason", "create_failed"),
                "previous_draft_id": outcome.get("previous_draft_id", "")}
    return {"platform": "xhs", "ok": True, "method": "opencli-cdp",
            "draft_id": outcome["draft_id"],
            "previous_draft_id": outcome.get("previous_draft_id", ""),
            "retired_previous": outcome.get("retired_previous", False)}


def _note_paper_key(note: Path) -> str:
    """Read paper_id from a note YAML (stable ledger key); fall back to ''."""
    try:
        import yaml
        data = yaml.safe_load(note.read_text(encoding="utf-8")) or {}
        return str(data.get("paper_id") or "")
    except Exception:  # noqa: BLE001
        return ""


def deliver_wechat(staged_id: str) -> dict[str, Any]:
    """Publish the staged WeChat package to the 公众号 草稿箱."""
    from redbook.automation.publishing import WeChatPublisher

    try:
        receipt = WeChatPublisher(ROOT).publish(staged_id)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "platform": "wechat", "error": f"{type(exc).__name__}: {exc}"}
    return {"platform": "wechat", **receipt}


def deliver_notion(notion_package_path: str, *, timeout: int = 300) -> dict[str, Any]:
    """Push the review package to Notion via the blog repo CLI (idempotent write)."""
    pkg = Path(notion_package_path)
    if not pkg.is_file():
        return {"ok": False, "platform": "notion", "error": f"package missing: {pkg}"}
    cli = BLOG_REPO / "tools" / "publish_review_package.py"
    if not cli.is_file():
        return {"ok": False, "platform": "notion", "error": f"blog CLI missing: {cli}"}
    env = {**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONIOENCODING": "utf-8"}
    try:
        process = subprocess.run(
            [sys.executable, str(cli), "--review-json", str(pkg), "--write-notion"],
            capture_output=True, text=True, encoding="utf-8", env=env,
            cwd=str(BLOG_REPO), timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "platform": "notion", "error": f"{type(exc).__name__}: {exc}"}
    # The CLI prints the report JSON on success, and exits 1 when gate errors exist.
    try:
        report = json.loads(process.stdout) if process.stdout.strip() else {}
    except json.JSONDecodeError:
        report = {"raw_stdout": process.stdout[:500]}
    delivery = report.get("delivery") or {}
    ok = process.returncode == 0 and bool(delivery)
    return {
        "ok": ok, "platform": "notion",
        "action": delivery.get("action"), "page_id": delivery.get("page_id"),
        "identity_key": delivery.get("identity_key"),
        "returncode": process.returncode,
        "error": (process.stderr or "")[:500] if not ok else "",
    }


def _load_package_body(platform: str, item: dict[str, Any]) -> dict[str, Any] | None:
    """Load the package body so the preflight can validate fields + materials."""
    try:
        if platform == "xhs" and item.get("path"):
            import yaml
            return yaml.safe_load(Path(item["path"]).read_text(encoding="utf-8")) or {}
        if platform == "wechat" and item.get("staged_id"):
            p = ROOT / "publish_queue" / str(item["staged_id"])[:32] / "wechat.json"
            if p.is_file():
                return json.loads(p.read_text(encoding="utf-8"))
        if platform == "notion" and item.get("path"):
            return json.loads(Path(item["path"]).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    return None


def deliver_compiled(results: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Preflight then deliver every compiled platform package.

    ``results`` is ``ContentFactory.compile_shared`` output:
      - results["xhs"]["path"]         -> note YAML path
      - results["wechat"]["staged_id"] -> staged package id
      - results["notion"]["path"]      -> review package json path

    Before delivery, each package is checked against
    ``paper_intake.platform_requirements`` (required fields + material
    validity). A failed preflight returns a ``needs_regeneration`` report and
    SKIPS that platform — we never silently re-run the model. A human/upstream
    step decides to regenerate the fact_pack, then re-delivers.
    """
    from paper_intake.platform_requirements import check_package

    receipts: dict[str, dict[str, Any]] = {}

    def _deliver(platform: str, item: dict[str, Any], ready: bool, run):
        if not ready:
            receipts[platform] = {"ok": False, "platform": platform,
                                  "error": f"not compiled: {item.get('status')}"}
            return
        body = _load_package_body(platform, item)
        if body is None:
            receipts[platform] = {"ok": False, "platform": platform,
                                  "error": "package body unreadable"}
            return
        report = check_package(platform, body)
        if not report["ok"]:
            receipts[platform] = {
                "ok": False, "platform": platform, "preflight_failed": True,
                "missing_fields": report["missing_fields"],
                "invalid_fields": report["invalid_fields"],
                "invalid_materials": report["invalid_materials"],
                "needs_regeneration": report["needs_regeneration"],
                "error": "preflight failed; regenerate fact_pack for the listed fields",
            }
            return
        receipts[platform] = run()

    xhs = results.get("xhs") or {}
    _deliver("xhs", xhs, bool(xhs.get("status") == "compiled" and xhs.get("path")),
             lambda: deliver_xhs(xhs["path"]))

    wechat = results.get("wechat") or {}
    _deliver("wechat", wechat,
             bool(wechat.get("status") == "compiled" and wechat.get("staged_id")),
             lambda: deliver_wechat(str(wechat["staged_id"])))

    notion = results.get("notion") or {}
    _deliver("notion", notion, bool(notion.get("status") == "compiled" and notion.get("path")),
             lambda: deliver_notion(notion["path"]))

    return receipts
