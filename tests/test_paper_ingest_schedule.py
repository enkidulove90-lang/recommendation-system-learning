from __future__ import annotations

from pathlib import Path
import tempfile

from redbook.sentinel.paper_pool import PaperPool
from redbook.sentinel.runner import SentinelRunner


def test_sentinel_uses_the_central_ingest_schedule_when_no_legacy_time_is_given(monkeypatch) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        pool = PaperPool(Path(temporary) / "pool.sqlite3")
        monkeypatch.setattr("redbook.sentinel.runner.configured_time", lambda: "13:17")
        runner = SentinelRunner(pool, config={"timezone": "Asia/Shanghai"})
        assert runner.retrieval_time == "13:17"
