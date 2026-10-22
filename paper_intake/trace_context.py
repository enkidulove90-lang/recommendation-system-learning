from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator


_TRACE_ID: ContextVar[str] = ContextVar("paper_intake_trace_id", default="")


def current_trace_id() -> str:
    return _TRACE_ID.get()


@contextmanager
def trace_scope(trace_id: str | None) -> Iterator[None]:
    token = _TRACE_ID.set((trace_id or "").strip())
    try:
        yield
    finally:
        _TRACE_ID.reset(token)
