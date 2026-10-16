"""导出指定小红书草稿的详情（用于判断是否真重复）。

输出写到 xhs_draft_details.json（UTF-8），避免 PowerShell 控制台编码问题。
用法：python inspect_xhs_drafts.py <draft_id> [<draft_id> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "xhs_draft_details.json"


def main(ids: list[str]) -> int:
    from redbook.infrastructure import opencli_runtime

    rt = opencli_runtime.resolve_runtime()
    results: dict[str, object] = {}
    for did in ids:
        entry: dict[str, object] = {"id": did}
        try:
            r = rt.run(
                "xiaohongshu", "draft-open", did, "-f", "json",
                "--window", "background", "--site-session", "ephemeral",
                timeout=150,
            )
            raw = (r.stdout or "").strip()
            entry["rc"] = r.returncode
            try:
                entry["data"] = json.loads(raw)
            except json.JSONDecodeError:
                entry["raw"] = raw[:1500]
                entry["stderr"] = (r.stderr or "")[:600]
            d = entry.get("data")
            if isinstance(d, dict):
                body = d.get("body") or d.get("content") or d.get("desc") or ""
                entry["summary"] = {
                    "title": d.get("title"),
                    "body_len": len(body) if isinstance(body, str) else None,
                    "images": d.get("images") or d.get("image_paths") or d.get("imagePaths"),
                    "topics": d.get("topics"),
                }
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        results[did] = entry
        print("done", did, "->", entry.get("summary", entry.get("raw", entry.get("error"))))

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written ->", OUT.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
