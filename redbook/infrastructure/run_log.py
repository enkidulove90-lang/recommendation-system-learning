"""统一运行日志：结构化 JSONL，取代根目录的 ``logs_*.txt`` stdout 重定向。

设计约束（2026-11-10）：

* 只追加一行一个 JSON 对象到 ``data/logs/runs.jsonl``，不覆盖、不做日志轮转，
  也不在仓库根目录生成任何文件；换机器 / 换 IDE 落点一致（相对仓库根解析）。
* 正式入口显式调用 :func:`log_event`，或调用 :func:`install_jsonl_handler`
  把已有的 ``logging`` 记录镜像进同一份 JSONL；两者互不递归。
* 查看走本模块的 CLI（``python -m redbook.infrastructure.run_log``），
  不依赖 PowerShell 编码，也不需要再写一次性 dump 脚本。

用法::

    from redbook.infrastructure.run_log import log_event, install_jsonl_handler

    log_event("note", action="stage", paper_id="2601.21452", ok=True)
    install_jsonl_handler()   # 可选：把 logging.getLogger() 的 INFO+ 也写进来

    # 命令行
    # python -m redbook.infrastructure.run_log --summary --tail 20
    # python -m redbook.infrastructure.run_log --json --event note
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import threading
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG_PATH = PROJECT_ROOT / "data" / "logs" / "runs.jsonl"

_LOCK = threading.Lock()
_NOISY_LOGGERS = (
    "httpx", "httpcore", "urllib3", "chardet", "openai", "PIL",
    "matplotlib", "asyncio", "filelock",
)


def log_event(event: str, *, path: Path | str | None = None, **fields: Any) -> dict[str, Any]:
    """追加一条运行事件，返回实际写入的记录。字段一律可 JSON 序列化。"""
    record: dict[str, Any] = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "event": event,
    }
    record.update(fields)
    target = Path(path) if path is not None else DEFAULT_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, default=str) + "\n"
    with _LOCK, target.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return record


def read_events(
    path: Path | str | None = None,
    *,
    event: str | None = None,
    command: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """读取事件；坏行跳过而不是让查看器崩掉。``limit`` 取最后 N 条。"""
    target = Path(path) if path is not None else DEFAULT_LOG_PATH
    if not target.exists():
        return []
    events: list[dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            if event and row.get("event") != event:
                continue
            if command and row.get("command") != command:
                continue
            events.append(row)
    return events[-limit:] if limit else events


def summarize(events: Iterable[dict[str, Any]], *, tail: int = 10) -> str:
    """把事件列表压成一份人类可读摘要（stdout 友好，不含 ANSI）。"""
    rows = list(events)
    lines = [f"events: {len(rows)}"]
    if not rows:
        return "\n".join(lines)
    lines.append(f"first: {rows[0].get('ts', '-')}  last: {rows[-1].get('ts', '-')}")
    by_event = Counter(str(row.get("event", "-")) for row in rows)
    by_status = Counter(str(row.get("status", "-")) for row in rows if "status" in row)
    lines.append("by event: " + ", ".join(f"{k}={v}" for k, v in sorted(by_event.items())))
    if by_status:
        lines.append("by status: " + ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())))
    lines.append("--- tail ---")
    for row in rows[-tail:]:
        detail = {k: v for k, v in row.items() if k not in ("ts", "event")}
        lines.append(
            f"{row.get('ts', '-')} {row.get('event', '-')} "
            + json.dumps(detail, ensure_ascii=False, default=str)
        )
    return "\n".join(lines)


class _ProjectOnlyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.name.startswith(_NOISY_LOGGERS)


class JsonlHandler(logging.Handler):
    """把标准 logging 记录镜像进 JSONL，避免各入口各自重定向 stdout。"""

    def __init__(self, path: Path | str | None = None) -> None:
        super().__init__(level=logging.INFO)
        self.path = Path(path) if path is not None else DEFAULT_LOG_PATH

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_event(
                "log",
                path=self.path,
                level=record.levelname,
                logger=record.name,
                message=record.getMessage(),
            )
        except Exception:  # pragma: no cover - logging must never break the caller
            self.handleError(record)


def install_jsonl_handler(
    logger: logging.Logger | None = None, *, path: Path | str | None = None
) -> JsonlHandler:
    """幂等安装；重复调用不会写出重复记录。"""
    target = logger if logger is not None else logging.getLogger()
    wanted = Path(path) if path is not None else DEFAULT_LOG_PATH
    for handler in target.handlers:
        if isinstance(handler, JsonlHandler) and handler.path == wanted:
            return handler
    handler = JsonlHandler(wanted)
    handler.addFilter(_ProjectOnlyFilter())
    target.addHandler(handler)
    return handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect the structured run log")
    parser.add_argument("--path", type=Path, default=DEFAULT_LOG_PATH)
    parser.add_argument("--event", help="only events with this name")
    parser.add_argument("--command", help="only events with this command field")
    parser.add_argument("--tail", type=int, default=10, help="rows shown in the summary")
    parser.add_argument("--json", action="store_true", help="dump matching events as JSON instead")
    parser.add_argument("--limit", type=int, help="only read the last N matching events")
    args = parser.parse_args(argv)

    events = read_events(args.path, event=args.event, command=args.command, limit=args.limit)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover - non-CPython / redirected streams
        pass
    if args.json:
        print(json.dumps(events, ensure_ascii=False, indent=2))
    else:
        print(summarize(events, tail=args.tail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
