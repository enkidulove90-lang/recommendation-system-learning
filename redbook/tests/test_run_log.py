"""统一运行日志与会话查看器的回归测试（不触碰真实 data/logs）。"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from redbook.infrastructure import run_log
from redbook.scripts import session_inspect


def test_log_event_appends_jsonl_and_reads_back(tmp_path: Path) -> None:
    path = tmp_path / "runs.jsonl"
    run_log.log_event("note", path=path, action="stage", paper_id="2601.21452", ok=True)
    run_log.log_event("note", path=path, action="publish", paper_id="2601.21452", ok=False)
    run_log.log_event("cli_start", path=path, command="list", argv=["list"])

    rows = run_log.read_events(path)
    assert len(rows) == 3
    assert all("ts" in row for row in rows)
    assert rows[0]["event"] == "note" and rows[0]["ok"] is True
    assert rows[1]["ok"] is False
    assert [row["action"] for row in run_log.read_events(path, event="note")] == ["stage", "publish"]
    assert run_log.read_events(path, command="list")[0]["event"] == "cli_start"
    assert run_log.read_events(path, limit=1)[0]["event"] == "cli_start"
    assert run_log.read_events(tmp_path / "missing.jsonl") == []


def test_read_events_skips_corrupt_lines(tmp_path: Path) -> None:
    path = tmp_path / "runs.jsonl"
    path.write_text('{"event": "ok"}\nNOT JSON\n\n[]\n', encoding="utf-8")
    assert run_log.read_events(path) == [{"event": "ok"}]


def test_summarize_reports_counts_and_tail() -> None:
    text = run_log.summarize(
        [
            {"ts": "2026-11-10T10:00:00", "event": "note", "status": "ok", "action": "stage"},
            {"ts": "2026-11-10T10:01:00", "event": "note", "status": "failed", "action": "publish"},
        ],
        tail=1,
    )
    assert "events: 2" in text
    assert "by event: note=2" in text
    assert "failed=1" in text
    assert "stage" not in text  # tail=1 只保留最后一条
    assert "publish" in text


def test_install_jsonl_handler_is_idempotent(tmp_path: Path) -> None:
    logger = logging.getLogger("test.run_log")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    path = tmp_path / "runs.jsonl"
    try:
        first = run_log.install_jsonl_handler(logger, path=path)
        second = run_log.install_jsonl_handler(logger, path=path)
        assert first is second
        logger.info("batch done")
        rows = run_log.read_events(path)
        assert len(rows) == 1
        assert rows[0]["event"] == "log" and rows[0]["message"] == "batch done"
    finally:
        logger.handlers.clear()


def test_logging_handler_filters_third_party_noise(tmp_path: Path) -> None:
    logger = logging.getLogger("test.run_log.noise")
    logger.handlers.clear()
    path = tmp_path / "runs.jsonl"
    try:
        handler = run_log.install_jsonl_handler(logger, path=path)
        noisy = logging.LogRecord("httpx", logging.INFO, __file__, 1, "external", (), None)
        project = logging.LogRecord("redbook.cli", logging.INFO, __file__, 1, "local", (), None)
        assert handler.filter(noisy) is False
        assert handler.filter(project) is True
        assert run_log.read_events(path) == []
    finally:
        logger.handlers.clear()


def test_session_inspect_parses_queries_and_calls(tmp_path: Path) -> None:
    session = tmp_path / "session.jsonl"
    rows = [
        {
            "type": "message",
            "role": "user",
            "timestamp": "1787138416737",
            "content": [{"type": "text", "text": "<user_query>把 30 个 txt 归档</user_query>"}],
        },
        {
            "type": "function_call",
            "name": "Bash",
            "timestamp": "1787138416738",
            "arguments": json.dumps({"description": "检查状态", "command": "git status --short"}),
        },
    ]
    session.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\nBROKEN\n", encoding="utf-8")

    loaded = session_inspect.load_rows(session)
    assert len(loaded) == 2
    assert session_inspect.user_queries(loaded)[0][1] == "把 30 个 txt 归档"
    calls = session_inspect.tool_calls(loaded)
    assert calls[0]["name"] == "Bash" and calls[0]["args"]["command"] == "git status --short"
    assert "--- tool calls ---" in session_inspect.render(loaded)
    out = tmp_path / "readable.txt"
    assert session_inspect.main([str(session), "--output", str(out)]) == 0
    assert "把 30 个 txt 归档" in out.read_text(encoding="utf-8")


def test_run_log_cli_on_empty_path(tmp_path: Path, capsys) -> None:
    path = tmp_path / "runs.jsonl"
    assert run_log.main(["--path", str(path), "--json"]) == 0
    assert "[]" in capsys.readouterr().out
    assert run_log.main(["--path", str(path)]) == 0
    assert "events: 0" in capsys.readouterr().out
