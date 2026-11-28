"""Local delivery ledger: one record per paper per platform.

Purpose (user decision 2026-11-28): XHS/WeChat have no server-side "does this
paper already have a draft" query, so we track what we delivered locally. The
ledger records the platform's id (XHS draft_id, WeChat draft_id, Notion page_id)
keyed by the paper's canonical id.

Overwrite policy (XHS): the user wants each note's draft to be *continuously
updated*, not skipped. Since opencli's publish always creates a NEW draft, the
"overwrite" is realised as: create the fresh draft, then delete the previously
ledgered draft so exactly one current draft exists per note. Deletion is
best-effort and only after the new draft is confirmed.

The file lives under ``data/delivery_ledger.json`` (data dir, not versioned).
It is a plain dict so a human can inspect/repair it.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "delivery_ledger.json"

#: Platform id field names this ledger stores.
_FIELD = {"xhs": "draft_id", "wechat": "draft_id", "notion": "page_id"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path = DEFAULT_PATH) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save(ledger: dict[str, dict[str, Any]], path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")


def get(platform: str, paper_key: str, *, path: Path = DEFAULT_PATH) -> dict[str, Any]:
    return ((load(path).get(paper_key) or {}).get(platform)) or {}


def record(platform: str, paper_key: str, *, path: Path = DEFAULT_PATH,
           **fields: Any) -> dict[str, Any]:
    """Upsert one platform record for a paper. Merges into any existing record."""
    ledger = load(path)
    entry = ledger.setdefault(paper_key, {})
    platform_entry = entry.setdefault(platform, {})
    platform_entry.update(fields)
    platform_entry.setdefault("recorded_at", _now())
    platform_entry["updated_at"] = _now()
    save(ledger, path)
    return platform_entry


def refresh_xhs_draft(
    paper_key: str,
    *,
    create: Callable[[], str | None],
    delete: Callable[[str], Any],
    path: Path = DEFAULT_PATH,
) -> dict[str, Any]:
    """Create a fresh XHS draft and, on success, delete the previously-ledgered one.

    "Overwrite, not skip" (user decision): each run refreshes the note's draft
    so there is exactly one current draft. The old draft is deleted ONLY after
    the new draft id is confirmed, so a failed create never destroys the old
    draft.

    ``create()`` returns the new draft_id (or None/"" on failure).
    ``delete(draft_id)`` performs the platform delete (best-effort).
    Returns the parsed new draft_id and whether the old one was retired.
    """
    previous = (get("xhs", paper_key, path=path) or {}).get("draft_id", "")
    new_id = create()
    if not new_id:
        return {"ok": False, "reason": "create_failed", "previous_draft_id": previous}
    record("xhs", paper_key, path=path, draft_id=new_id, content_hash="", state="draft")
    retired = False
    if previous and previous != new_id:
        try:
            delete(previous)
            retired = True
        except Exception:  # noqa: BLE001 — retiring the old draft is best-effort.
            retired = False
    return {"ok": True, "draft_id": new_id, "previous_draft_id": previous,
            "retired_previous": retired}
