"""Sentinel probes acceptance (TC1-TC6)."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from redbook.sentinel.paper_pool import PaperPool
from redbook.sentinel.probes import (
    ApiKeyProbe, HttpProbe, LoginProbe, OpenCliProbe, build_default_probes, write_probe_log,
)


NOW = datetime(2026, 11, 21, 10, 0, tzinfo=timezone.utc)


def _probe(status: int, latency_ms: float, fail: Exception | None = None) -> HttpProbe:
    def fetch(url: str, timeout: float) -> tuple[int, float]:
        if fail is not None:
            raise fail
        return status, latency_ms
    return HttpProbe("dep", "https://example.test", fetch=fetch)


def test_table_driven_three_states():  # TC1
    assert _probe(200, 50.0).check(NOW).state == "ok"
    assert _probe(200, 9000.0).check(NOW).state == "degraded"
    assert _probe(500, 10.0).check(NOW).state == "down"
    assert _probe(0, 0.0, fail=TimeoutError("boom")).check(NOW).state == "down"


def test_down_never_raises_and_carries_detail():  # TC2
    result = _probe(0, 0.0, fail=ConnectionError("refused")).check(NOW)
    assert result.state == "down" and result.latency_ms == 0.0
    assert "refused" in result.detail and result.name == "dep"


def test_probe_log_jsonl_split_by_day(tmp_path):  # TC3
    results = [_probe(200, 1.0).check(NOW), _probe(500, 2.0).check(NOW)]
    path = write_probe_log(tmp_path, results, NOW)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2 and "sentinel-probes-2026-11-21" in path.name
    assert json.loads(lines[0])["state"] == "ok"
    assert json.loads(lines[1])["state"] == "down"


def test_probe_rate_limit_via_meta(tmp_path):  # TC4
    pool = PaperPool(tmp_path / "state" / "orchestration.sqlite")
    from redbook.sentinel.runner import SentinelRunner
    probe = _probe(200, 1.0)
    runner = SentinelRunner(pool, probes=[probe],
                            config={"probe_min_interval_seconds": 900})
    first = runner.probe_all(NOW)
    assert [r.state for r in first] == ["ok"]
    soon = datetime(2026, 11, 21, 10, 5, tzinfo=timezone.utc)
    assert runner.probe_all(soon) == []  # within 15 min floor
    later = datetime(2026, 11, 21, 10, 20, tzinfo=timezone.utc)
    assert [r.state for r in runner.probe_all(later)] == ["ok"]


def test_opencli_probe_down_does_not_block_sweep():  # TC5
    def broken_doctor() -> dict:
        raise RuntimeError("daemon not running")
    opencli = OpenCliProbe(doctor=broken_doctor)
    healthy = _probe(200, 1.0)
    results = [opencli.check(NOW), healthy.check(NOW)]
    assert results[0].state == "down" and "daemon" in results[0].detail
    assert results[1].state == "ok"  # sweep survived the dead probe


def test_opencli_probe_default_path_uses_runtime_client(monkeypatch):
    class Client:
        def doctor(self):
            return {"daemon_running": True, "extension_connected": True}

    monkeypatch.setattr("redbook.infrastructure.opencli_runtime.OpenCliClient", Client)

    assert OpenCliProbe().check(NOW).state == "ok"


def test_opencli_probe_runtime_initialization_failure_is_down(monkeypatch):
    class UnavailableClient:
        def __init__(self):
            raise RuntimeError("runtime unavailable")

    monkeypatch.setattr("redbook.infrastructure.opencli_runtime.OpenCliClient", UnavailableClient)

    result = OpenCliProbe().check(NOW)

    assert result.state == "down" and "runtime unavailable" in result.detail


def test_login_probe_maps_e_auth_semantics():  # TC6
    lost = LoginProbe("chrome_login", "xiaohongshu",
                      probe=lambda site: {"ok": False, "error": "expired"})
    result = lost.check(NOW)
    assert result.state == "down" and result.detail.startswith("E_AUTH")
    alive = LoginProbe("chrome_login", "xiaohongshu",
                       probe=lambda site: {"ok": True})
    assert alive.check(NOW).state == "ok"


def test_login_probe_default_path_accepts_probe_login_contract(monkeypatch):
    monkeypatch.setattr(
        "redbook.infrastructure.opencli_runtime.probe_login",
        lambda site: {"logged_in": True, "site": site},
    )

    assert LoginProbe("chrome_login", "xiaohongshu").check(NOW).state == "ok"


def test_api_key_probe_missing_config_is_down():  # covers MinerU/DeepSeek branch
    probe = ApiKeyProbe("deepseek", "DEEPSEEK_API_KEY_TEST_MISSING")
    assert probe.check(NOW).state == "down"


def test_default_probes_respect_disabled_opencli_probe():
    probes = build_default_probes({"opencli_probe": False})

    assert not any(probe.name == "opencli" for probe in probes)


def test_default_deepseek_probe_uses_configured_authenticated_health_endpoint(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_TEST_KEY", "test-key")
    captured = {}

    def fake_authenticated_get(url, key):
        captured.update(url=url, key=key)
        return 200, "HTTP 200"

    monkeypatch.setattr("redbook.sentinel.probes._authenticated_get_status", fake_authenticated_get)
    probe = build_default_probes({"api_key_probes": [{
        "name": "deepseek", "env_var": "DEEPSEEK_TEST_KEY",
        "health_url": "https://api.deepseek.com/models",
    }]})[0]

    result = probe.check(NOW)

    assert result.state == "ok" and result.detail == "HTTP 200"
    assert captured == {"url": "https://api.deepseek.com/models", "key": "test-key"}


def test_default_probe_rejects_untrusted_authenticated_health_url(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_TEST_KEY", "test-key")
    monkeypatch.setattr(
        "redbook.sentinel.probes._authenticated_get_status",
        lambda *_: (_ for _ in ()).throw(AssertionError("untrusted URL must not be called")),
    )
    probe = build_default_probes({"api_key_probes": [{
        "name": "deepseek", "env_var": "DEEPSEEK_TEST_KEY",
        "health_url": "https://example.invalid/models",
    }]})[0]

    result = probe.check(NOW)

    assert result.state == "down" and result.detail.startswith("E_CONFIG")
