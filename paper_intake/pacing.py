"""Process-local courtesy pacing for all official arXiv GET requests."""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from urllib.parse import urlsplit


OFFICIAL_ARXIV_HOSTS = frozenset({"arxiv.org", "www.arxiv.org", "export.arxiv.org"})


class ArxivPacer:
    _shared_lock = threading.Lock()
    _shared_custom: dict[object, "ArxivPacer"] = {}

    @classmethod
    def shared(cls, *, clock=None, sleep=None) -> "ArxivPacer":
        if clock is None and sleep is None:
            return GLOBAL_ARXIV_PACER
        key = clock or time.monotonic
        with cls._shared_lock:
            if key not in cls._shared_custom:
                cls._shared_custom[key] = cls(clock=clock, sleep=sleep)
            return cls._shared_custom[key]

    def __init__(self, *, clock=None, sleep=None, interval_seconds: float = 3.0):
        self.clock = clock or time.monotonic
        self.sleep = sleep or time.sleep
        self.interval_seconds = interval_seconds
        self._lock = threading.RLock()
        self._next_at = 0.0

    @contextmanager
    def request(self, url: str):
        if urlsplit(url).hostname not in OFFICIAL_ARXIV_HOSTS:
            yield 0.0
            return
        with self._lock:
            wait = max(0.0, self._next_at - self.clock())
            if wait:
                self.sleep(wait)
            try:
                yield wait
            finally:
                self._next_at = max(self._next_at, self.clock() + self.interval_seconds)

    def defer(self, seconds: float) -> None:
        with self._lock:
            self._next_at = max(self._next_at, self.clock() + seconds)


GLOBAL_ARXIV_PACER = ArxivPacer()
