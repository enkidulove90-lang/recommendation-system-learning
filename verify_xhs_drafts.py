"""小红书草稿箱清点/核验工具（中文可靠）。

为什么不用 stdout 回传结果
--------------------------
PowerShell 5.1 捕获原生命令 stdout 时按系统 ANSI 代码页（简体中文为 GBK）解读，
Python 即使把 stdout 重配成 UTF-8 也会被二次误解码 → 中文标题变 `鎺ㄨ崘` 之类乱码。
因此本脚本**把结果直接写成 UTF-8 文件**，再用读取工具看文件（控制台只看 ASCII 摘要）。

用法：
    powershell & "C:\\Program Files\\Python311\\python.exe" verify_xhs_drafts.py
        [--dump]              导出草稿箱全量到 xhs_drafts_dump.json / .txt
        [--keep-first N]      按 rank 保留前 N 条，删除其余（危险，需 --yes）
        [--delete s:xxx ...]  删除指定草稿 id
        [--yes]               确认执行删除
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DUMP_JSON = ROOT / "xhs_drafts_dump.json"
DUMP_TXT = ROOT / "xhs_drafts_dump.txt"


def fetch_drafts() -> list[dict]:
    from redbook.infrastructure import opencli_runtime

    rt = opencli_runtime.resolve_runtime()
    last_err = None
    for attempt in range(3):
        r = rt.run(
            "xiaohongshu", "drafts", "-f", "json",
            "--window", "background", "--site-session", "ephemeral",
            timeout=120,
        )
        raw = (r.stdout or "").strip()
        if raw.startswith(("[", "{")):
            return sorted(json.loads(raw), key=lambda x: x.get("rank", 0))
        last_err = f"attempt {attempt + 1}: rc={r.returncode} stdout={raw[:120]!r}"
    raise SystemExit("drafts 探针连续失败（可能瞬时窗口状态，稍后重试）：" + str(last_err))


def write_dump(drafts: list[dict]) -> None:
    DUMP_JSON.write_text(
        json.dumps(drafts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [f"草稿箱共 {len(drafts)} 条", ""]
    for d in drafts:
        lines.append(
            "%2s | imgs=%s | %-45s | %s"
            % (d.get("rank"), d.get("images"), d.get("id"), d.get("title"))
        )
    DUMP_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("dumped ->", DUMP_JSON.name, "/", DUMP_TXT.name, "(", len(drafts), "drafts )")


def delete_one(draft_id: str) -> str:
    from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery

    try:
        OpenCliXiaohongshuDelivery()._delete(draft_id)
        return "called (无回执，需按 id 复核)"
    except Exception as exc:  # noqa: BLE001
        return f"FAILED: {type(exc).__name__}: {str(exc)[:200]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--delete", nargs="*", default=[])
    ap.add_argument("--keep-first", type=int, default=None)
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    drafts = fetch_drafts()
    write_dump(drafts)

    targets: list[str] = list(args.delete)
    if args.keep_first is not None:
        targets += [d["id"] for d in drafts[args.keep_first:]]
    targets = list(dict.fromkeys(targets))

    if not targets:
        print("no delete targets")
        return 0

    if not args.yes:
        print("DRY-RUN，将删除以下", len(targets), "条：")
        for t in targets:
            print("   ", t)
        print("加 --yes 才真正执行")
        return 0

    for t in targets:
        print("delete", t, "->", delete_one(t))

    after = fetch_drafts()
    before_ids = {d["id"] for d in drafts}
    after_ids = {d["id"] for d in after}
    print("count:", len(drafts), "->", len(after))
    for t in targets:
        print("  verify", t, "removed" if t not in after_ids else "STILL PRESENT")
    print("unexpectedly lost:", sorted(before_ids - after_ids - set(targets)) or "none")
    write_dump(after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
