"""重试/退避工具（content_events/retry.py）。

解决运维弱点 B1：瞬时失败（网络抖动/超时）可重试+指数退避，
但永久错误（如 PublishingError 校验失败）直接抛出不重试。
- RetryPolicy：最大次数、基础退避、退避上限、可重试的瞬时异常类型。
- retry_call：包裹任意可调用；仅瞬时异常重试；达到上限后抛出原异常。
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional, Tuple, Type

# 默认瞬时异常：网络/超时/系统 IO（不含 PublishingError 等语义错误）
_DEFAULT_TRANSIENT: Tuple[Type[BaseException], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
)


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_base: float = 1.0
    backoff_cap: float = 30.0
    transient: Tuple[Type[BaseException], ...] = _DEFAULT_TRANSIENT


def retry_call(
    fn: Callable[[], object],
    policy: Optional[RetryPolicy] = None,
    logger=None,
) -> object:
    """执行 fn，对瞬时异常按 policy 重试；非瞬时异常立即上抛。

    - policy 为 None → 直接执行一次（无重试）。
    - 达到 max_attempts 仍瞬时失败 → 抛出最后一次异常。
    - 非瞬时异常（如 PublishingError）→ 不重试，立即上抛。
    """
    if policy is None:
        return fn()
    attempt = 0
    while True:
        attempt += 1
        try:
            return fn()
        except policy.transient as exc:  # 仅瞬时异常重试
            if attempt >= policy.max_attempts:
                raise
            wait = min(policy.backoff_cap, policy.backoff_base * (2 ** (attempt - 1)))
            if logger is not None:
                logger.warning(
                    "[retry] 第 %d/%d 次瞬时失败，%.1fs 后重试: %s",
                    attempt, policy.max_attempts, wait, exc,
                )
            time.sleep(wait)
