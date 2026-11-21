"""Dependency probes: eleven external dependencies, three-state verdicts.

Every probe implements ``check(now) -> ProbeResult`` with state in
``ok / degraded / down``; a probe must never raise (down + detail instead) so
one dead dependency cannot block the sweep (TC5). The OpenCLI and login probes
reuse ``opencli_runtime.doctor`` / ``probe_login``; HTTP probes take an
injectable ``fetcher`` so sandbox tests run against local mocks (TC1).
"""
from __future__ import annotations

import json
import time
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

Fetch = Callable[[str, float], tuple[int, float]]
"""fetcher(url, timeout) -> (status_code, latency_ms); injectable for tests."""


def _http_fetch(url: str, timeout: float,
                headers: dict[str, str] | None = None) -> tuple[int, float]:
    request = urllib.request.Request(
        url, method="GET",
        headers={"User-Agent": "redbook-sentinel/1", **(headers or {})},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(256)
            return int(response.status), (time.perf_counter() - started) * 1000.0
    except urllib.error.HTTPError as error:
        # 4xx/5xx reach the caller as a status so semantic mapping
        # (degraded_on / S2 429) can classify them; only transport-level
        # failures (DNS, TLS, timeout) still raise -> down.
        error.read(256)
        return int(error.code), (time.perf_counter() - started) * 1000.0


def _authenticated_get_status(url: str, key: str) -> tuple[int, str]:
    """Perform a bounded bearer-authenticated read without exposing the key."""
    request = urllib.request.Request(
        url, method="GET",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "redbook-sentinel/1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=8.0) as response:
            response.read(256)
        return int(response.status), f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        return int(error.code), f"HTTP {error.code}"


def _authenticated_health_call(url: str, env_var: str) -> Callable[[], tuple[bool, str]]:
    def check() -> tuple[bool, str]:
        import os
        status, detail = _authenticated_get_status(url, os.environ[env_var])
        return 200 <= status < 400, detail
    return check


def _configured_authenticated_health_call(
    name: str, url: str, env_var: str,
) -> Callable[[], tuple[bool, str]]:
    """Allow bearer-key probes only against the provider's pinned endpoint."""
    if name == "deepseek" and url == "https://api.deepseek.com/models":
        return _authenticated_health_call(url, env_var)
    return lambda: (False, f"E_CONFIG: unsupported authenticated health endpoint for {name}")


@dataclass
class ProbeResult:
    name: str
    state: str  # ok | degraded | down
    latency_ms: float
    detail: str = ""
    error_type: str = ""
    stack: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "state": self.state,
                "latency_ms": round(self.latency_ms, 1), "detail": self.detail,
                "error_type": self.error_type, "stack": self.stack}


class Probe(Protocol):
    name: str

    def check(self, now: datetime) -> ProbeResult: ...


class HttpProbe:
    """Generic endpoint probe: 2xx = ok, slow-but-successful = degraded.

    ``degraded_on`` lists statuses that mean *restricted access* rather than
    an outage (e.g. OpenReview's anonymous 403 bot-challenge): the endpoint
    answered, so the verdict is degraded with a sanitized detail, not down.
    """

    def __init__(self, name: str, url: str, *, timeout: float = 8.0,
                 slow_ms: float = 3000.0, fetch: Fetch | None = None,
                 degraded_on: tuple[int, ...] = ()) -> None:
        self.name = name
        self.url = url
        self.timeout = timeout
        self.slow_ms = slow_ms
        self._fetch = fetch or _http_fetch
        self._degraded_on = tuple(degraded_on)
        self._headers: dict[str, str] = {}

    def check(self, now: datetime) -> ProbeResult:
        try:
            if self._headers:
                status, latency = self._fetch(self.url, self.timeout, self._headers)
            else:
                status, latency = self._fetch(self.url, self.timeout)
        except Exception as error:  # probes never raise
            return ProbeResult(self.name, "down", 0.0,
                               f"{type(error).__name__}: {error}",
                               type(error).__name__, traceback.format_exc())
        if 200 <= status < 400:
            state = "degraded" if latency > self.slow_ms else "ok"
            return ProbeResult(self.name, state, latency, f"HTTP {status}")
        if status in self._degraded_on:
            return ProbeResult(self.name, "degraded", latency,
                               f"HTTP {status} (access-limited: challenge/auth gate, not outage)")
        return ProbeResult(self.name, "down", latency, f"HTTP {status}")


class SemanticScholarProbe(HttpProbe):
    """Semantic Scholar dedicated probe.

    The official auth header is the case-sensitive ``x-api-key`` — never
    ``Authorization: Bearer`` (that convention is DeepSeek-only). Without a
    key the request shares the anonymous pool, so a 429 means *rate-limited*,
    not an outage: it maps to degraded with a sanitized category detail that
    never exposes the key. With a key, 429 means the 1 rps entry tier was
    exceeded and is likewise degraded.
    """

    def __init__(self, name: str, url: str, *, env_var: str = "S2_API_KEY",
                 timeout: float = 8.0, slow_ms: float = 3000.0,
                 fetch: Fetch | None = None) -> None:
        super().__init__(name, url, timeout=timeout, slow_ms=slow_ms, fetch=fetch)
        self._env_var = env_var

    def check(self, now: datetime) -> ProbeResult:
        import os
        key = os.environ.get(self._env_var)
        if key:
            self._headers = {"x-api-key": key}
        result = super().check(now)
        if result.state == "down" and result.detail.startswith("HTTP 429"):
            result.state = "degraded"
            result.detail = (
                "authenticated rate-limited (x-api-key 1 rps entry tier)"
                if key else
                "anonymous rate-limited (shared pool; set S2_API_KEY for dedicated quota)"
            )
        elif result.state == "ok":
            result.detail = f"HTTP {result.detail.split()[-1]} (x-api-key)" if key \
                else f"HTTP {result.detail.split()[-1]} (anonymous)"
        return result


class ApiKeyProbe:
    """MinerU / DeepSeek: credential present + cheapest live call.

    The live call is injectable; the default no-op only verifies the key is
    configured, which keeps probe cost at zero while still catching the
    "key missing" failure mode that blocks the parse/summarize stages.
    """

    def __init__(self, name: str, env_var: str, *, slow_ms: float = 3000.0,
                 live_call: Callable[[], tuple[bool, str]] | None = None) -> None:
        import os
        self.name = name
        self._env_var = env_var
        self._slow_ms = slow_ms
        self._live = live_call
        self._os = os

    def check(self, now: datetime) -> ProbeResult:
        started = time.perf_counter()
        if not self._os.environ.get(self._env_var):
            return ProbeResult(self.name, "down", 0.0,
                               f"{self._env_var} not configured")
        if self._live is None:
            return ProbeResult(self.name, "ok", 0.0, "key present (no live call)")
        try:
            ok, detail = self._live()
        except Exception as error:
            return ProbeResult(self.name, "down", 0.0,
                               f"{type(error).__name__}: {error}",
                               type(error).__name__, traceback.format_exc())
        latency = (time.perf_counter() - started) * 1000.0
        if not ok:
            return ProbeResult(self.name, "down", latency, detail)
        state = "degraded" if latency > self._slow_ms else "ok"
        return ProbeResult(self.name, state, latency, detail)


class OpenCliProbe:
    """OpenCLI daemon/extension via ``opencli_runtime.doctor``; injectable."""

    def __init__(self, name: str = "opencli",
                 doctor: Callable[[], dict[str, Any]] | None = None) -> None:
        self.name = name
        self._doctor = doctor

    def check(self, now: datetime) -> ProbeResult:
        started = time.perf_counter()
        try:
            doctor = self._doctor
            if doctor is None:
                from redbook.infrastructure.opencli_runtime import OpenCliClient
                doctor = OpenCliClient().doctor
            report = doctor()
        except Exception as error:
            return ProbeResult(self.name, "down", 0.0,
                               f"{type(error).__name__}: {error}",
                               type(error).__name__, traceback.format_exc())
        latency = (time.perf_counter() - started) * 1000.0
        connected = bool(
            report.get("extension_connected")
            or report.get("extensionConnected")
            or report.get("connected")
        )
        if not connected:
            return ProbeResult(self.name, "down", latency,
                               json.dumps(report, ensure_ascii=False)[:200])
        return ProbeResult(self.name, "ok", latency,
                           json.dumps(report, ensure_ascii=False)[:200])


class LoginProbe:
    """Chrome login state via ``opencli_runtime.probe_login`` (read-only)."""

    def __init__(self, name: str, site: str,
                 probe: Callable[[str], dict[str, Any]] | None = None) -> None:
        self.name = name
        self._site = site
        self._probe = probe

    def check(self, now: datetime) -> ProbeResult:
        started = time.perf_counter()
        probe = self._probe
        if probe is None:
            from redbook.infrastructure.opencli_runtime import probe_login as real
            probe = real
        try:
            report = probe(self._site)
        except Exception as error:
            return ProbeResult(self.name, "down", 0.0,
                               f"{type(error).__name__}: {error}",
                               type(error).__name__, traceback.format_exc())
        latency = (time.perf_counter() - started) * 1000.0
        ok = bool(report.get("logged_in") or report.get("ok"))
        if ok:
            return ProbeResult(self.name, "ok", latency, "logged_in")
        # auth failure is E_AUTH semantics: retryable, human-owned
        return ProbeResult(self.name, "down", latency,
                           f"E_AUTH: {report.get('error', 'login state lost')}")


def build_default_probes(config: dict[str, Any] | None = None) -> list[Probe]:
    """Build the eleven-dependency sweep from ``config/sentinel.yaml``."""
    config = config or {}
    endpoints = config.get("http_endpoints", [])
    probes: list[Probe] = []
    for entry in endpoints:
        kind = entry.get("kind", "http")
        timeout = float(entry.get("timeout", 8.0))
        slow_ms = float(entry.get("slow_ms", 3000.0))
        if kind == "semantic_scholar":
            probes.append(SemanticScholarProbe(
                entry["name"], entry["url"],
                env_var=str(entry.get("env_var", "S2_API_KEY")),
                timeout=timeout, slow_ms=slow_ms,
            ))
        else:
            probes.append(HttpProbe(entry["name"], entry["url"],
                                    timeout=timeout, slow_ms=slow_ms,
                                    degraded_on=tuple(entry.get("degraded_on", ()))))
    for entry in config.get("api_key_probes", []):
        health_url = str(entry.get("health_url", "")).strip()
        live_call = _configured_authenticated_health_call(
            entry["name"], health_url, entry["env_var"],
        ) \
            if health_url else None
        probes.append(ApiKeyProbe(entry["name"], entry["env_var"], live_call=live_call))
    if bool(config.get("opencli_probe", True)):
        probes.append(OpenCliProbe())
    login = config.get("login_probe")
    if login:
        probes.append(LoginProbe(login.get("name", "chrome_login"),
                                 login.get("site", "xiaohongshu")))
    return probes


def run_sweep(probes: list[Probe], now: datetime) -> list[ProbeResult]:
    return [probe.check(now) for probe in probes]


def write_probe_log(log_dir: Path, results: list[ProbeResult], now: datetime) -> Path:
    """Append one JSONL line per probe, files split by day (run_log convention)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    day: date = now.date()
    path = log_dir / f"sentinel-probes-{day.isoformat()}.jsonl"
    moment = now.isoformat()
    with path.open("a", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps({"at": moment, **result.to_dict()},
                                    ensure_ascii=False) + "\n")
    return path
