"""
utils/helpers.py — 通用工具函数

提供日志配置、文本清理、函数重试装饰器等。
"""

from __future__ import annotations

import logging
import sys
import time
from functools import wraps
from typing import Any, Callable

from config import settings


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------

def setup_logging(level: str | None = None) -> None:
    """
    初始化全局日志配置。

    参数:
        level: "DEBUG" | "INFO" | "WARNING" | "ERROR"，默认读取 .env
    """
    log_level = (level or settings.LOG_LEVEL).upper()
    fmt = (
        "%(asctime)s [%(levelname)-7s] %(name)s | %(message)s"
        if log_level == "DEBUG"
        else "[%(levelname)-7s] %(name)s | %(message)s"
    )

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # 降低第三方库日志噪音
    for noisy in ("httpx", "httpcore", "urllib3", "chardet"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# 文本清理
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    清理文本：去除多余空白、统一换行为空格。

    参数:
        text: 原始文本

    返回:
        清理后的单行文本
    """
    if not text:
        return ""
    return " ".join(text.strip().split())


# ---------------------------------------------------------------------------
# 重试装饰器
# ---------------------------------------------------------------------------

def retry(
    max_attempts: int = 3,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """
    函数执行重试装饰器。

    参数:
        max_attempts: 最大尝试次数（含首次）
        backoff:      退避系数（延迟 = backoff ** attempt 秒）
        exceptions:   需要重试的异常类型

    使用示例:
        @retry(max_attempts=5, exceptions=(ConnectionError, TimeoutError))
        def fetch_url(url):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        delay = backoff ** attempt
                        logger.warning(
                            "Retry %d/%d for %s after %.1fs: %s",
                            attempt, max_attempts, func.__name__, delay, exc,
                        )
                        time.sleep(delay)
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator
