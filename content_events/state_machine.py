"""内容事件状态机（content_events/state_machine.py）。

对应设计 §3：draft → rendered → validated → staged → published -> archived，
任意校验/发布失败 → needs_review（不自动重试，设计 04 §风控 3 / 设计 05 §实施 3）。
仅强制合法转移；非法转移抛 StateMachineError，由调用方记录 NEEDS_REVIEW。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .schema import ContentState, EventType


class StateMachineError(Exception):
    pass


# 合法转移表：(from, event) -> to
_TRANSITIONS: Dict[Tuple[ContentState, EventType], ContentState] = {
    (ContentState.DRAFT, EventType.RENDERED): ContentState.RENDERED,
    (ContentState.RENDERED, EventType.VALIDATED): ContentState.VALIDATED,
    (ContentState.VALIDATED, EventType.STAGED): ContentState.STAGED,
    (ContentState.STAGED, EventType.PUBLISHED): ContentState.PUBLISHED,
    (ContentState.PUBLISHED, EventType.FEEDBACK_SAMPLED): ContentState.PUBLISHED,
    (ContentState.PUBLISHED, EventType.DECISION_MADE): ContentState.PUBLISHED,
    (ContentState.PUBLISHED, EventType.ARCHIVED): ContentState.ARCHIVED,
    # 任意态失败 → 人工
    (ContentState.DRAFT, EventType.NEEDS_REVIEW): ContentState.NEEDS_REVIEW,
    (ContentState.RENDERED, EventType.NEEDS_REVIEW): ContentState.NEEDS_REVIEW,
    (ContentState.VALIDATED, EventType.NEEDS_REVIEW): ContentState.NEEDS_REVIEW,
    (ContentState.STAGED, EventType.NEEDS_REVIEW): ContentState.NEEDS_REVIEW,
    # 人工修订后重入
    (ContentState.NEEDS_REVIEW, EventType.RENDERED): ContentState.RENDERED,
    (ContentState.NEEDS_REVIEW, EventType.VALIDATED): ContentState.VALIDATED,
}


@dataclass
class TransitionResult:
    ok: bool
    from_state: ContentState
    to_state: ContentState
    reason: str = ""


def transition(state: ContentState, event: EventType) -> TransitionResult:
    """尝试推进状态机；返回结果（不抛异常，便于编排层记录）。"""
    key = (state, event)
    if key in _TRANSITIONS:
        to = _TRANSITIONS[key]
        return TransitionResult(ok=True, from_state=state, to_state=to)
    # 同一态的反馈采样等中性事件允许
    if event in (EventType.FEEDBACK_SAMPLED, EventType.DECISION_MADE) and state in (
        ContentState.PUBLISHED,
        ContentState.STAGED,
    ):
        return TransitionResult(ok=True, from_state=state, to_state=state)
    return TransitionResult(
        ok=False,
        from_state=state,
        to_state=state,
        reason=f"非法转移: {state.value} --{event.value}--> ?",
    )
