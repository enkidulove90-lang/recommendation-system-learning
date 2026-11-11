# -*- coding: utf-8 -*-
"""UniPinRec 换稿：发布 v2（文案更清晰版），成功后删除旧草稿，并按 id 复核。

顺序不能反：先发新稿 → 确认成功 → 再删旧稿（否则新稿失败+旧稿已删=两头空）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
NEW_STAGED = "a896caa7ac8bc6fe941b5f0500eadfed6f7284a18a8feb9147b670116b372035"
OLD_DRAFT = "s:69f6c71a-1094-4be3-8e2a-eb957036e7f5"

from redbook.automation.publishing import XhsPublisher

result = XhsPublisher(root=ROOT).publish(NEW_STAGED)
print("PUBLISH NEW:", result)

new_ok = isinstance(result, dict) and result.get("ok")
new_id = (result or {}).get("draft_id", "") if isinstance(result, dict) else ""
print("NEW_DRAFT_ID:", new_id)

if new_ok and new_id and new_id != OLD_DRAFT:
    try:
        from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery

        r = OpenCliXiaohongshuDelivery()._delete(OLD_DRAFT)
        print("DELETE OLD called (无回执):", r)
    except Exception as exc:  # noqa: BLE001
        print("DELETE OLD FAILED:", type(exc).__name__, str(exc)[:200])
else:
    print("新稿未成功或 id 异常 -> 保留旧稿")

# 按 id 复核（_delete 静默成功，必须回读列表）
from redbook.infrastructure import opencli_runtime

rt = opencli_runtime.resolve_runtime()
for attempt in range(3):
    rr = rt.run("xiaohongshu", "drafts", "-f", "json", "--window", "background",
                "--site-session", "ephemeral", timeout=120)
    raw = (rr.stdout or "").strip()
    if raw.startswith(("[", "{")):
        drafts = json.loads(raw)
        ref = new_id.split(":")[-1][:8]
        oldref = OLD_DRAFT.split(":")[-1][:8]
        print("total:", len(drafts))
        print("new present:", any(ref in str(d.get("id", "")) for d in drafts))
        print("old removed:", not any(oldref in str(d.get("id", "")) for d in drafts))
        break
    print("retry probe", attempt + 1, repr(raw[:100]))
