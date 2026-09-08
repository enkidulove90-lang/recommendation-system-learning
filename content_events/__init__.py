"""内容事件编排层（content_events）。

对应设计 docs/content-event-orchestration-design.md。
把 publish_queue/ 静态内容包驱动为可观测、可回滚、幂等的内容生命周期事件流：
  intake → render(DTLE) → validated → staged → published → feedback
"""
from .schema import (
    ContentEvent,
    ContentItem,
    ContentState,
    EventType,
    content_hash,
)
from . import state_machine as state_machine
from .event_log import EventLog
from . import publishers as publishers
from . import queue_processor as queue_processor
from . import feedback_collector as feedback_collector
from . import orchestrator as orchestrator

__all__ = [
    "ContentEvent", "ContentItem", "ContentState", "EventType", "content_hash",
    "state_machine", "EventLog", "publishers", "queue_processor",
    "feedback_collector", "orchestrator",
]
