"""内容事件日志（content_events/event_log.py）。

对应设计 §3：事件流追加到 data/content_events/events.jsonl（不可变审计日志）。
- EventLog.append(event)：写一行 JSONL（flush + fsync，强化持久性，修复 B3）
- EventLog.iter(item_key?)：读取（可按 item_key 过滤；损坏行跳过不中断，修复 B3）
单文件、进程内锁保护追加，线程安全足够本场景。
"""
from __future__ import annotations

import json
import os
import threading
from typing import Iterator, List, Optional

from .schema import ContentEvent, EventType

_LOCK = threading.Lock()


class EventLog:
    def __init__(self, path: str, fsync: bool = True):
        self.path = path
        self.fsync = fsync
        # 惰性建父目录 + 文件
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        try:
            with open(self.path, "a", encoding="utf-8"):
                pass
        except OSError:
            pass

    def append(self, event: ContentEvent) -> None:
        with _LOCK:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(event.to_line() + "\n")
                f.flush()
                if self.fsync:
                    try:
                        os.fsync(f.fileno())
                    except OSError:
                        pass

    def iter(self, item_key: Optional[str] = None) -> Iterator[ContentEvent]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = ContentEvent.from_line(line)
                    except (json.JSONDecodeError, ValueError, KeyError) as exc:
                        # 损坏行：告警并跳过，不中断整个迭代（修复 B3）
                        import logging
                        logging.getLogger(__name__).warning(
                            "[event_log] 跳过损坏行 L%d: %s", lineno, exc
                        )
                        continue
                    if item_key is None or ev.item_key == item_key:
                        yield ev
        except FileNotFoundError:
            return
        except OSError:
            return

    def all(self, item_key: Optional[str] = None) -> List[ContentEvent]:
        return list(self.iter(item_key))

    def last_type(self, item_key: str) -> Optional[EventType]:
        evs = self.all(item_key)
        return evs[-1].type if evs else None
