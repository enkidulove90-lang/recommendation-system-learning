"""Prune stale LoopsBench drafts, keeping only the latest good one.

Keep : s:69d5cb6a-4b24-49d0-9cdc-b8f460149898  ('首个loop engineer基准来了', just published)
Delete:
  - any draft whose title contains '循环工程评估'  (the pre-title-change curated version)
  - any other draft titled '首个loop engineer基准来了' that is NOT the kept id (auto-saved partial from the failed first attempt)
"""
import sys
sys.path.insert(0, "redbook")
from infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery

KEEP = "s:69d5cb6a-4b24-49d0-9cdc-b8f460149898"
NEW_TITLE = "首个loop engineer基准来了"

delivery = OpenCliXiaohongshuDelivery()
drafts = delivery._drafts()
print(f"=== {len(drafts)} drafts in box ===")
for d in drafts:
    print(" -", repr(d.get("title")), "| id=", d.get("id"))

def should_delete(d):
    tid = d.get("id")
    title = d.get("title") or ""
    if "循环工程评估" in title:
        return True, "old curated version (pre-title-change)"
    if title == NEW_TITLE and tid != KEEP:
        return True, "duplicate new-title draft (auto-saved partial)"
    return False, ""

targets = [(d, should_delete(d)[1]) for d in drafts if should_delete(d)[0]]
print(f"\n=== deleting {len(targets)} stale draft(s) ===")
for d, reason in targets:
    tid = d.get("id")
    print(f"deleting {tid}  [{reason}]  title={d.get('title')!r}")
    delivery._delete(tid)
print("done")

# re-list to confirm
remaining = delivery._drafts()
print(f"\n=== {len(remaining)} drafts remain ===")
for d in remaining:
    print(" -", repr(d.get("title")), "| id=", d.get("id"))
