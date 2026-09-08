"""编排器（content_events/orchestrator.py）。

把队列处理与反馈采集组合为高阶动作，供 CLI / 自动化调用（设计 §7）。
- run_once：处理 publish_queue（intake→render→stage），返回 (摘要列表, RunSummary)
- collect_feedback：跑反馈采集窗口（守卫 OpenCLI）+ 自优化决策（O8 接通死代码）
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from . import queue_processor
from . import feedback_collector as fc
from .event_log import EventLog

logger = logging.getLogger(__name__)


def run_once(
    root: str,
    publisher: str = "dryrun",
    theme: str = "recsys-blue",
    *,
    dry_run: bool = True,
    retry_policy: Optional[queue_processor.RetryPolicy] = None,
) -> Tuple[List[Dict[str, Any]], queue_processor.RunSummary]:
    return queue_processor.process_queue(
        root, publisher_name=publisher, theme=theme,
        dry_run=dry_run, retry_policy=retry_policy,
    )


def collect_feedback(root: str, opencli_fn=None) -> Dict[str, Any]:
    db = os.path.join(root, "data", "feedback", "feedback.sqlite")
    elog = EventLog(os.path.join(root, "data", "content_events", "events.jsonl"))
    conn = fc.init_sqlite(db)
    try:
        res = fc.collect_once(conn, opencli_fn=opencli_fn, event_log=elog)
        # 自优化决策（O8）：在采集后基于既有快照做分组 lift / 时段选择
        decision = fc.decide_once(conn)
        res["decision"] = decision
        if decision.get("applied"):
            elog.append(__import__("content_events.schema", fromlist=["ContentEvent"]).ContentEvent(
                __import__("content_events.schema", fromlist=["EventType"]).EventType.DECISION_MADE,
                "feedback", __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                decision,
            ))
    finally:
        conn.close()
    return res
