"""Dependency probes: eleven external dependencies, three-state verdicts.

Every probe implements ``check(now) -> ProbeResult`` with state in
``ok / degraded / down``; a probe must never raise (down + detail instead) so
one dead dependency cannot block the sweep (TC5). The OpenCLI and login probes
reuse ``opencli_runtime.doctor`` / ``probe_login``; HTTP probes take an
injectable ``fetcher`` so sandbox tests run against local mocks (TC1).
"""
from __future__ import annotations

import json
import errno
import socket
import ssl
import time
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

Fetch = Callable[[str, float], tuple[int, float]]
"""fetcher(url, timeout) -> (status_code, latency_ms); injectable for tests."""
ResponseFetch = Callable[[str, float], tuple[int, float, dict[str, str]]]

# ---------------------------------------------------------------------------
# Credential resolution: .env file first, system environment as fallback.
#
# Root cause this fixes (2026-11-22 11:00 run): the Task Scheduler launches
# ``cmd.exe /c ... -m redbook.sentinel run-once`` in a bare environment —
# no shell profile is sourced, redbook has no dotenv loading anywhere, and
# the run cwd is a *worktree* while the keys live in the main repo's .env —
# so ``os.environ``-only probes reported mineru/deepseek permanently down.
#
# Resolution order (user decision 2026-11-22): .env wins, os.environ is the
# fallback. We search cwd upward so a worktree run finds the main repo's
# .env without hardcoding paths.
# ---------------------------------------------------------------------------

_ENV_CACHE: dict[str, str] | None = None


def _load_env_file() -> dict[str, str]:
    """Parse the nearest ``.env`` walking up from cwd (cached once per run)."""
    global _ENV_CACHE
    if _ENV_CACHE is not None:
        return _ENV_CACHE
    loaded: dict[str, str] = {}
    current = Path.cwd()
    for candidate in (current, *current.parents[:4]):
        env_file = candidate / ".env"
        if not env_file.is_file():
            continue
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in loaded:
                    loaded[key] = value
        except OSError:
            continue  # unreadable .env must never crash a probe
        break  # nearest .env wins; do not merge further ancestors
    _ENV_CACHE = loaded
    return loaded


def _env_value(name: str, env: Mapping[str, str] | None = None) -> str | None:
    """Resolve explicit credentials, then nearest .env, then process env."""
    explicit = (env or {}).get(name, "").strip()
    if explicit:
        return explicit
    value = _load_env_file().get(name)
    if value:
        return value
    import os
    return os.environ.get(name, "").strip() or None


_NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
"""Opener that bypasses any configured proxy (direct connection)."""


def _proxy_opener(proxy_url: str | None) -> urllib.request.OpenerDirector | None:
    if not proxy_url:
        return None
    return urllib.request.build_opener(urllib.request.ProxyHandler({
        "http": proxy_url, "https": proxy_url,
    }))


def _http_fetch_response(url: str, timeout: float,
                         headers: dict[str, str] | None = None,
                         opener: urllib.request.OpenerDirector | None = None
                         ) -> tuple[int, float, dict[str, str]]:
    request = urllib.request.Request(
        url, method="GET",
        headers={"User-Agent": "redbook-sentinel/1", **(headers or {})},
    )
    started = time.perf_counter()
    try:
        open_fn = opener.open if opener is not None else urllib.request.urlopen
        with open_fn(request, timeout=timeout) as response:
            response.read(256)
            return (int(response.status), (time.perf_counter() - started) * 1000.0,
                    {str(k).casefold(): str(v) for k, v in response.headers.items()})
    except urllib.error.HTTPError as error:
        # 4xx/5xx reach the caller as a status so semantic mapping
        # (degraded_on / S2 429) can classify them; only transport-level
        # failures (DNS, TLS, timeout) still raise -> down.
        error.read(256)
        return (int(error.code), (time.perf_counter() - started) * 1000.0,
                {str(k).casefold(): str(v) for k, v in (error.headers or {}).items()})


def _http_fetch(url: str, timeout: float,
                headers: dict[str, str] | None = None,
                opener: urllib.request.OpenerDirector | None = None) -> tuple[int, float]:
    status, latency, _ = _http_fetch_response(url, timeout, headers, opener)
    return status, latency


def _proxy_endpoint_unreachable(url: str, proxy_url: str | None) -> bool:
    """Check whether the selected proxy TCP endpoint itself is unreachable.

    A request timeout alone does not reveal whether the proxy connect, tunnel,
    or upstream response timed out. Only fall back when a second, bounded TCP
    connect to the configured proxy also fails by refusal/timeout.
    """
    target = urlsplit(url)
    proxies = urllib.request.getproxies()
    selected_proxy = proxy_url or proxies.get(target.scheme)
    if not selected_proxy or urllib.request.proxy_bypass(target.hostname or ""):
        return False
    parsed = urlsplit(selected_proxy if "://" in selected_proxy else f"//{selected_proxy}")
    if not parsed.hostname:
        return False
    port = parsed.port or (443 if parsed.scheme.casefold() == "https" else 80)
    try:
        connection = socket.create_connection((parsed.hostname, port), timeout=0.5)
    except (ConnectionRefusedError, TimeoutError, socket.timeout):
        return True
    except OSError:
        return False
    else:
        connection.close()
        return False


def _proxy_connection_failure(error: Exception, *, url: str,
                              proxy_url: str | None = None) -> bool:
    """Return true for proxy refusal or a confirmed proxy TCP timeout only."""
    target = urlsplit(url)
    proxies = urllib.request.getproxies()
    selected_proxy = proxy_url or proxies.get(target.scheme)
    if (not selected_proxy
            or urllib.request.proxy_bypass(target.hostname or "")):
        return False
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    if isinstance(reason, ssl.SSLCertVerificationError):
        return False
    if isinstance(reason, (ConnectionRefusedError,)):
        return True
    if isinstance(reason, (TimeoutError, socket.timeout)) or (
            isinstance(reason, OSError) and reason.errno == errno.ETIMEDOUT):
        return _proxy_endpoint_unreachable(url, proxy_url)
    return isinstance(reason, OSError) and reason.errno == errno.ECONNREFUSED


def _authenticated_get_status(
        url: str, key: str,
        opener: urllib.request.OpenerDirector | None = None,
) -> tuple[int, str]:
    """Perform a bounded bearer-authenticated read without exposing the key."""
    request = urllib.request.Request(
        url, method="GET",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "redbook-sentinel/1"},
    )
    try:
        open_fn = opener.open if opener is not None else urllib.request.urlopen
        with open_fn(request, timeout=8.0) as response:
            response.read(256)
        return int(response.status), f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        return int(error.code), f"HTTP {error.code}"


def _authenticated_health_call(url: str, env_var: str,
                               env: Mapping[str, str] | None = None,
                               proxy_url: str | None = None,
                               ) -> Callable[[], tuple[bool, str]]:
    proxy_opener = _proxy_opener(proxy_url)
    def check() -> tuple[bool, str]:
        key = _env_value(env_var, env)
        if not key:
            return False, f"{env_var} not configured (.env or environment)"
        status, detail = (_authenticated_get_status(url, key, proxy_opener)
                          if proxy_opener else _authenticated_get_status(url, key))
        return 200 <= status < 400, detail
    return check


def _configured_authenticated_health_call(
    name: str, url: str, env_var: str,
    env: Mapping[str, str] | None = None,
    proxy_url: str | None = None,
) -> Callable[[], tuple[bool, str]]:
    """Allow bearer-key probes only against the provider's pinned endpoint."""
    if name == "deepseek" and url == "https://api.deepseek.com/models":
        return _authenticated_health_call(url, env_var, env, proxy_url)
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
                 degraded_on: tuple[int, ...] = (),
                 direct_fallback: bool = False,
                 proxy_url: str | None = None) -> None:
        self.name = name
        self.url = url
        self.timeout = timeout
        self.slow_ms = slow_ms
        self._fetch = fetch or _http_fetch
        self._degraded_on = tuple(degraded_on)
        self._direct_fallback = bool(direct_fallback)
        self._proxy_url = proxy_url
        self._proxy_opener = _proxy_opener(proxy_url)
        self._headers: dict[str, str] = {}

    def check(self, now: datetime) -> ProbeResult:
        started = time.perf_counter()
        try:
            headers = self._headers or None
            if self._fetch is _http_fetch and self._proxy_opener is not None:
                status, latency = _http_fetch(
                    self.url, self.timeout, headers,
                    opener=self._proxy_opener)
            elif headers:
                status, latency = self._fetch(self.url, self.timeout, headers)
            else:
                status, latency = self._fetch(self.url, self.timeout)
            suffix = ""
        except Exception as error:  # probes never raise
            if not (self._direct_fallback and self._fetch is _http_fetch
                    and _proxy_connection_failure(
                        error, url=self.url, proxy_url=self._proxy_url)):
                return ProbeResult(self.name, "down", 0.0,
                                   f"{type(error).__name__}: {error}",
                                   type(error).__name__, traceback.format_exc())
            # Proxy management: the sweep runs on a dev machine where a
            # system proxy (e.g. 127.0.0.1:7897) may MITM TLS or be dead.
            # First attempt goes through the ambient proxy; on a transport
            # connection refusal/timeout retry once direct. TLS certificate
            # failures are deliberately not bypassed; configure a trusted CA.
            try:
                status, latency = _http_fetch(self.url, self.timeout,
                                              self._headers or None,
                                              opener=_NO_PROXY_OPENER)
                suffix = " (direct-fallback)"
            except Exception as retry_error:
                latency = (time.perf_counter() - started) * 1000.0
                return ProbeResult(
                    self.name, "down", latency,
                    f"{type(error).__name__}: {error} | direct retry: "
                    f"{type(retry_error).__name__}: {retry_error}",
                    type(retry_error).__name__, traceback.format_exc())
        if 200 <= status < 400:
            state = "degraded" if latency > self.slow_ms else "ok"
            return ProbeResult(self.name, state, latency, f"HTTP {status}{suffix}")
        if status in self._degraded_on:
            return ProbeResult(self.name, "degraded", latency,
                               f"HTTP {status} (access-limited: challenge/auth gate, not outage)")
        return ProbeResult(self.name, "down", latency, f"HTTP {status}{suffix}")


class CrossrefProbe(HttpProbe):
    """Crossref health probe with polite-pool identity and bounded 429 retry."""

    def __init__(self, name: str, url: str, *,
                 mailto_env_var: str = "CROSSREF_MAILTO",
                 env: Mapping[str, str] | None = None,
                 proxy_url: str | None = None,
                 timeout: float = 8.0, slow_ms: float = 3000.0,
                 fetch_response: ResponseFetch | None = None,
                 sleep: Callable[[float], None] = time.sleep,
                 max_retries: int = 2, retry_backoff_seconds: float = 1.0,
                 max_retry_after_seconds: float = 30.0) -> None:
        super().__init__(name, url, timeout=timeout, slow_ms=slow_ms,
                         degraded_on=(429,), proxy_url=proxy_url)
        self._mailto_env_var = mailto_env_var
        self._env = env
        self._fetch_response = fetch_response or _http_fetch_response
        self._sleep = sleep
        self._max_retries = max(0, int(max_retries))
        self._retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        self._max_retry_after_seconds = max(0.0, float(max_retry_after_seconds))

    def _request_url(self) -> str:
        mailto = _env_value(self._mailto_env_var, self._env)
        if not mailto:
            return self.url
        parsed = urlsplit(self.url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["mailto"] = mailto
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path,
                           urlencode(query), parsed.fragment))

    @staticmethod
    def _retry_after_seconds(value: str | None) -> float | None:
        if not value:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(value)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                return None

    def check(self, now: datetime) -> ProbeResult:
        url = self._request_url()
        started = time.perf_counter()
        retries = 0
        rate_headers: dict[str, str] = {}
        retry_after_deferred: float | None = None
        while True:
            try:
                if self._fetch_response is _http_fetch_response:
                    status, latency, headers = _http_fetch_response(
                        url, self.timeout, opener=self._proxy_opener)
                else:
                    status, latency, headers = self._fetch_response(url, self.timeout)
            except Exception as error:
                return ProbeResult(self.name, "down",
                                   (time.perf_counter() - started) * 1000.0,
                                   f"{type(error).__name__}: {error}",
                                   type(error).__name__, traceback.format_exc())
            rate_headers.update({key: value for key, value in headers.items()
                                 if key.casefold() in {
                                     "x-rate-limit-limit", "x-rate-limit-interval",
                                     "retry-after",
                                 }})
            if status != 429:
                break
            if retries >= self._max_retries:
                break
            retry_after = self._retry_after_seconds(
                next((v for k, v in headers.items()
                      if k.casefold() == "retry-after"), None))
            delay = retry_after if retry_after is not None else (
                self._retry_backoff_seconds * (2 ** retries))
            if delay > self._max_retry_after_seconds:
                retry_after_deferred = delay
                break
            retries += 1
            self._sleep(delay)
        evidence = " ".join(f"{key}={value}" for key, value in sorted(rate_headers.items()))
        if status == 429:
            deferred = (f" retry_after_deferred={retry_after_deferred:g}s"
                        if retry_after_deferred is not None else "")
            return ProbeResult(self.name, "degraded", latency,
                               f"HTTP 429 rate-limited retries={retries}"
                               f"{deferred}" + (f" {evidence}" if evidence else ""))
        if 200 <= status < 400:
            state = "degraded" if latency > self.slow_ms else "ok"
            retry_detail = f" 429 retries={retries}" if retries else ""
            return ProbeResult(self.name, state, latency,
                               f"HTTP {status}{retry_detail}"
                               + (f" {evidence}" if evidence else ""))
        return ProbeResult(self.name, "down", latency,
                           f"HTTP {status}" + (f" {evidence}" if evidence else ""))


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
                 fetch: Fetch | None = None,
                 env: Mapping[str, str] | None = None,
                 proxy_url: str | None = None) -> None:
        super().__init__(name, url, timeout=timeout, slow_ms=slow_ms, fetch=fetch,
                         proxy_url=proxy_url)
        self._env_var = env_var
        self._env = env

    def check(self, now: datetime) -> ProbeResult:
        key = _env_value(self._env_var, self._env)
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
                 live_call: Callable[[], tuple[bool, str]] | None = None,
                 env: Mapping[str, str] | None = None) -> None:
        self.name = name
        self._env_var = env_var
        self._slow_ms = slow_ms
        self._live = live_call
        self._env = env

    def check(self, now: datetime) -> ProbeResult:
        started = time.perf_counter()
        if not _env_value(self._env_var, self._env):
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


def build_default_probes(config: dict[str, Any] | None = None, *,
                         env: Mapping[str, str] | None = None) -> list[Probe]:
    """Build the eleven-dependency sweep from ``config/sentinel.yaml``."""
    config = config or {}
    endpoints = config.get("http_endpoints", [])
    proxy_env_var = str(config.get("proxy_env_var", "PAPER_INTAKE_PROXY_URL"))
    probes: list[Probe] = []
    for entry in endpoints:
        kind = entry.get("kind", "http")
        timeout = float(entry.get("timeout", 8.0))
        slow_ms = float(entry.get("slow_ms", 3000.0))
        proxy_url = _env_value(str(entry.get("proxy_env_var", proxy_env_var)), env)
        if kind == "crossref":
            probes.append(CrossrefProbe(
                entry["name"], entry["url"],
                mailto_env_var=str(entry.get("mailto_env_var", "CROSSREF_MAILTO")),
                env=env, proxy_url=proxy_url,
                timeout=timeout, slow_ms=slow_ms,
                max_retries=int(entry.get("max_retries", 2)),
                retry_backoff_seconds=float(entry.get("retry_backoff_seconds", 1.0)),
                max_retry_after_seconds=float(entry.get("max_retry_after_seconds", 30.0)),
            ))
        elif kind == "semantic_scholar":
            probes.append(SemanticScholarProbe(
                entry["name"], entry["url"],
                env_var=str(entry.get("env_var", "S2_API_KEY")),
                timeout=timeout, slow_ms=slow_ms, env=env,
                proxy_url=proxy_url,
            ))
        else:
            probes.append(HttpProbe(entry["name"], entry["url"],
                                    timeout=timeout, slow_ms=slow_ms,
                                    degraded_on=tuple(entry.get("degraded_on", ())),
                                    direct_fallback=bool(entry.get("direct_fallback", False)),
                                    proxy_url=proxy_url))
    for entry in config.get("api_key_probes", []):
        health_url = str(entry.get("health_url", "")).strip()
        live_call = _configured_authenticated_health_call(
            entry["name"], health_url, entry["env_var"], env,
            _env_value(str(entry.get("proxy_env_var", proxy_env_var)), env),
        ) \
            if health_url else None
        probes.append(ApiKeyProbe(entry["name"], entry["env_var"],
                                  live_call=live_call, env=env))
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
