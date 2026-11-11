"""把 WorkBuddy 会话 ``*.jsonl`` 转成可读文本或事件摘要。

替代已归档的 ``archive/session_scripts/_dump_calls.py``、``_extract2..5.py``、
``_extract_session.py``、``_scan2.py``、``_scan_session.py``：那 7 个脚本各自把
同一份会话转储读一遍再写到根目录，路径全是硬编码的绝对路径。

::

    python -m redbook.scripts.session_inspect <session.jsonl> --output <readable.txt>
    python -m redbook.scripts.session_inspect <session.jsonl> --queries-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

_USER_QUERY = re.compile(r"<user_query>(.*?)</user_query>", re.S)
_INTERESTING_ARGS = ("description", "command", "url", "prompt", "q", "skill", "file_path", "pattern")


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _text_blocks(row: dict[str, Any]) -> str:
    content = row.get("content") or []
    if not isinstance(content, list):
        return ""
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") in ("text", "input_text")
    )


def _timestamp(row: dict[str, Any]) -> str:
    raw = row.get("timestamp")
    if isinstance(raw, (int, float)) or (isinstance(raw, str) and raw.isdigit()):
        return datetime.fromtimestamp(int(raw) / 1000).strftime("%m-%d %H:%M:%S")
    return str(raw or "-")


def user_queries(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for row in rows:
        if row.get("type") != "message" or row.get("role") != "user":
            continue
        text = _text_blocks(row)
        for match in _USER_QUERY.findall(text):
            query = match.strip()
            if query:
                found.append((_timestamp(row), query))
        if not _USER_QUERY.search(text) and text.strip() and not text.lstrip().startswith("<"):
            found.append((_timestamp(row), text.strip()))
    return found


def tool_calls(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for row in rows:
        if row.get("type") != "function_call":
            continue
        raw_args = row.get("arguments") or {}
        if isinstance(raw_args, str):
            try:
                raw_args = json.loads(raw_args)
            except json.JSONDecodeError:
                raw_args = {"raw": raw_args}
        if not isinstance(raw_args, dict):
            raw_args = {"raw": raw_args}
        calls.append({
            "ts": _timestamp(row),
            "name": row.get("name", "-"),
            "args": {key: raw_args[key] for key in _INTERESTING_ARGS if raw_args.get(key)},
        })
    return calls


def render(rows: list[dict[str, Any]], *, limit: int = 0) -> str:
    types = Counter(str(row.get("type", "-")) for row in rows)
    lines = [
        f"rows: {len(rows)}",
        "types: " + ", ".join(f"{key}={value}" for key, value in sorted(types.items())),
        "",
        "--- user queries ---",
    ]
    queries = user_queries(rows)
    for ts, query in queries[-limit:] if limit else queries:
        lines.append(f"{ts}  {' '.join(query.split())[:300]}")
    lines.extend(["", "--- tool calls ---"])
    calls = tool_calls(rows)
    for index, call in enumerate(calls[-limit:] if limit else calls, start=1):
        lines.append(f"#{index} {call['ts']} {call['name']}")
        for key, value in call["args"].items():
            lines.append(f"  {key}: {' '.join(str(value).split())[:400]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a WorkBuddy session JSONL")
    parser.add_argument("session", type=Path, help="path to the .jsonl transcript")
    parser.add_argument("--output", type=Path, help="write UTF-8 readable text here")
    parser.add_argument("--limit", type=int, default=0, help="only keep the last N queries / calls")
    parser.add_argument("--queries-only", action="store_true")
    args = parser.parse_args(argv)

    rows = load_rows(args.session)
    if args.queries_only:
        text = "\n".join(f"{ts}  {' '.join(query.split())}" for ts, query in user_queries(rows))
    else:
        text = render(rows, limit=args.limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output} ({len(rows)} rows)")
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:  # pragma: no cover
            pass
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
