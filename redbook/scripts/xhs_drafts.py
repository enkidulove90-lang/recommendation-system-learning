"""小红书草稿箱清点 / 详情导出 / 删除核验（合并两个根目录脚本）。

由 ``inspect_xhs_drafts.py`` + ``verify_xhs_drafts.py`` 合并而来，放在
``redbook/scripts/`` 与其它平台运维脚本同层。

中文可靠性铁律
--------------
PowerShell 5.1 捕获原生命令 stdout 时按系统 ANSI 代码页（简体中文为 GBK）解读，
Python 即使把 stdout 重配 UTF-8 也会被二次误解码，中文标题会变乱码。
因此结果**直接写 UTF-8 文件**，控制台只打印 ASCII 摘要。

删除是危险操作：默认 dry-run，必须显式 ``--yes``；``_delete`` 无回执，
执行后按 id 重新清点复核（脚本已自动做）。

CLI::

    python -m redbook.scripts.xhs_drafts dump
    python -m redbook.scripts.xhs_drafts inspect <draft_id> ...
    python -m redbook.scripts.xhs_drafts prune --keep-first 5 [--yes]
    python -m redbook.scripts.xhs_drafts prune --delete s:xxx [--yes]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
DUMP_JSON = ROOT / "xhs_drafts_dump.json"
DUMP_TXT = ROOT / "xhs_drafts_dump.txt"
DETAILS_JSON = ROOT / "xhs_draft_details.json"


def resolve_runtime():
    from redbook.infrastructure import opencli_runtime
    return opencli_runtime.resolve_runtime()


def fetch_drafts(runtime=None) -> list[dict[str, Any]]:
    rt = runtime or resolve_runtime()
    last_error = ""
    for attempt in range(3):
        result = rt.run(
            "xiaohongshu", "drafts", "-f", "json",
            "--window", "background", "--site-session", "ephemeral",
            timeout=120,
        )
        raw = (result.stdout or "").strip()
        if raw.startswith(("[", "{")):
            parsed = json.loads(raw)
            return sorted(parsed, key=lambda item: item.get("rank", 0))
        last_error = f"attempt {attempt + 1}: rc={result.returncode} stdout={raw[:120]!r}"
    raise RuntimeError("drafts 探针连续失败（可能瞬时窗口状态）：" + last_error)


def write_dump(drafts: list[dict[str, Any]]) -> dict[str, str]:
    DUMP_JSON.write_text(json.dumps(drafts, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"草稿箱共 {len(drafts)} 条", ""]
    for draft in drafts:
        lines.append("%2s | imgs=%s | %-45s | %s" % (
            draft.get("rank"), draft.get("images"), draft.get("id"), draft.get("title")
        ))
    DUMP_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(DUMP_JSON), "txt": str(DUMP_TXT), "count": str(len(drafts))}


def inspect_drafts(ids: Sequence[str], runtime=None) -> dict[str, Any]:
    rt = runtime or resolve_runtime()
    results: dict[str, Any] = {}
    for draft_id in ids:
        entry: dict[str, Any] = {"id": draft_id}
        try:
            result = rt.run(
                "xiaohongshu", "draft-open", draft_id, "-f", "json",
                "--window", "background", "--site-session", "ephemeral",
                timeout=150,
            )
            raw = (result.stdout or "").strip()
            entry["rc"] = result.returncode
            try:
                entry["data"] = json.loads(raw)
            except json.JSONDecodeError:
                entry["raw"] = raw[:1500]
                entry["stderr"] = (result.stderr or "")[:600]
            data = entry.get("data")
            if isinstance(data, dict):
                body = data.get("body") or data.get("content") or data.get("desc") or ""
                entry["summary"] = {
                    "title": data.get("title"),
                    "body_len": len(body) if isinstance(body, str) else None,
                    "images": data.get("images") or data.get("image_paths") or data.get("imagePaths"),
                    "topics": data.get("topics"),
                }
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        results[draft_id] = entry
    DETAILS_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(DETAILS_JSON), "details": results}


def delete_one(draft_id: str) -> str:
    from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery

    try:
        OpenCliXiaohongshuDelivery()._delete(draft_id)
        return "called (无回执，需按 id 复核)"
    except Exception as exc:  # noqa: BLE001
        return f"FAILED: {type(exc).__name__}: {str(exc)[:200]}"


def prune(targets: Sequence[str], *, yes: bool = False, runtime=None,
          drafts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    # 必须与 main 计算 keep-first 时用的是同一份快照，否则两次清点期间草稿箱
    # 变动会让删除目标与复核基线错位。
    drafts = drafts if drafts is not None else fetch_drafts(runtime)
    dump = write_dump(drafts)
    unique = list(dict.fromkeys(targets))
    if not yes:
        return {"ok": True, "dry_run": True, "targets": unique, "dump": dump}
    outcomes = {draft_id: delete_one(draft_id) for draft_id in unique}
    after = fetch_drafts(runtime)
    before_ids = {str(item["id"]) for item in drafts}
    after_ids = {str(item["id"]) for item in after}
    write_dump(after)
    return {
        "ok": True, "dry_run": False, "dump": dump, "count_before": len(drafts),
        "count_after": len(after), "outcomes": outcomes,
        "still_present": [item for item in unique if item in after_ids],
        "unexpectedly_lost": sorted(before_ids - after_ids - set(unique)),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="XHS draft box inventory helpers")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("dump")
    inspect = actions.add_parser("inspect")
    inspect.add_argument("ids", nargs="+")
    prune_parser = actions.add_parser("prune")
    prune_parser.add_argument("--delete", nargs="*", default=[])
    prune_parser.add_argument("--keep-first", type=int, default=None)
    prune_parser.add_argument("--yes", action="store_true", help="actually delete (otherwise dry-run)")
    args = parser.parse_args(argv)

    if args.action == "dump":
        result = write_dump(fetch_drafts())
    elif args.action == "inspect":
        result = inspect_drafts(args.ids)
    else:
        drafts = fetch_drafts()
        targets = list(args.delete)
        if args.keep_first is not None:
            targets += [str(item["id"]) for item in drafts[args.keep_first:]]
        result = prune(targets, yes=args.yes, drafts=drafts)
    print(json.dumps(result, ensure_ascii=False, indent=2)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
