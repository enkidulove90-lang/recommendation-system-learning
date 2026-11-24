from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def request_with_retry(
    operation: Callable[[], T],
    *,
    retryable: Callable[[Exception], bool] | None = None,
    delays: tuple[float, ...] = (1.0, 2.0, 4.0),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Run a remote operation with bounded exponential backoff."""
    predicate = retryable or (lambda _error: True)
    for attempt in range(len(delays) + 1):
        try:
            return operation()
        except Exception as exc:
            if attempt >= len(delays) or not predicate(exc):
                raise
            sleep(delays[attempt])
    raise RuntimeError("unreachable")
