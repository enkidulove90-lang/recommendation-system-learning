from __future__ import annotations

import sys

from redbook import cli
from redbook.orchestration.registry import SqliteDeliveryRegistry
from redbook.sentinel.paper_pool import PaperPool


def test_sentinel_run_once_wires_daily_discovery_adapter(monkeypatch, tmp_path, capsys):
    captured = {}

    class Runner:
        def __init__(self, pool, *, config, probes, log_dir, discovery, platform="homepage"):
            captured["discovery"] = discovery

        def run_once(self, queue, *, dispatch):
            return {"ok": True, "has_discovery": callable(captured["discovery"]), "dispatch": dispatch}

    monkeypatch.setattr("redbook.sentinel.runner.SentinelRunner", Runner)
    monkeypatch.setattr(
        sys, "argv",
        ["redbook.cli", "sentinel", "run-once", "--no-dispatch", "--data-root", str(tmp_path)],
    )

    cli.main()

    assert '"has_discovery": true' in capsys.readouterr().out


def test_sentinel_platform_flag_overrides_configured_consumer(monkeypatch, tmp_path, capsys):
    captured = {}

    class Runner:
        def __init__(self, pool, *, config, probes, log_dir, discovery, platform="homepage"):
            captured["platform"] = platform

        def run_once(self, queue, *, dispatch):
            return {"ok": True, "platform": captured["platform"]}

    monkeypatch.setattr("redbook.sentinel.runner.SentinelRunner", Runner)
    monkeypatch.setattr(
        sys, "argv",
        [
            "redbook.cli", "sentinel", "run-once", "--platform", "xiaohongshu",
            "--no-dispatch", "--data-root", str(tmp_path),
        ],
    )

    cli.main()

    assert '"platform": "xiaohongshu"' in capsys.readouterr().out


def test_sentinel_pool_export_pending_is_read_only(monkeypatch, tmp_path, capsys):
    pool = PaperPool(tmp_path / "state" / "orchestration.sqlite")
    pool.add_candidate(canonical_id="arxiv:2601.00003", arxiv_id="2601.00003")
    monkeypatch.setattr(
        sys, "argv",
        ["redbook.cli", "sentinel", "pool", "--export-pending", "--data-root", str(tmp_path)],
    )

    cli.main()

    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload == {
        "ok": True,
        "schema_version": "paper-pool-export/v1",
        "entries": [{
            "canonical_id": "arxiv:2601.00003", "arxiv_id": "2601.00003",
            "doi": "", "title": "",
        }],
    }


def test_sentinel_pool_reconcile_reports_registry_progress(monkeypatch, tmp_path, capsys):
    database = tmp_path / "state" / "orchestration.sqlite"
    pool = PaperPool(database)
    pool.add_candidate(canonical_id="arxiv:2601.00004", arxiv_id="2601.00004")
    registry = SqliteDeliveryRegistry(database)
    registry.begin_save(
        run_id="run-4", content_hash="4" * 64, platform="xhs", account="default",
        staged_id="4" * 64, canonical_id="arxiv:2601.00004",
    )
    registry.mark_saved_unverified(
        platform="xhs", account="default", staged_id="4" * 64, draft_id="s:4",
    )
    monkeypatch.setattr(
        sys, "argv",
        ["redbook.cli", "sentinel", "pool", "--reconcile", "--data-root", str(tmp_path)],
    )

    cli.main()

    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["entries"][0]["canonical_id"] == "arxiv:2601.00004"
    assert payload["entries"][0]["delivery_state"] == "SAVED_UNVERIFIED"
