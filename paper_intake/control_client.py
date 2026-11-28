from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import requests


PROXY_ENV_NAMES = (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
)


def sanitize_proxy_environment() -> None:
    for name in PROXY_ENV_NAMES:
        os.environ.pop(name, None)


def build_control_session(*, mode: str = "direct", proxy_url: str = "") -> requests.Session:
    sanitize_proxy_environment()
    session = requests.Session()
    session.trust_env = False
    normalized = mode.strip().lower()
    if normalized == "direct":
        session.proxies.clear()
    elif normalized == "proxy":
        if not proxy_url.strip():
            raise ValueError("PAPER_INTAKE_PROXY_URL is required in proxy mode")
        session.proxies.update({"http": proxy_url.strip(), "https": proxy_url.strip()})
    else:
        raise ValueError("PAPER_INTAKE_NETWORK_MODE must be direct or proxy")
    return session


def load_or_create_operation_key(path: str | Path) -> str:
    target = Path(path)
    if target.is_file():
        return target.read_text(encoding="ascii").strip()
    target.parent.mkdir(parents=True, exist_ok=True)
    value = str(uuid.uuid4())
    try:
        with target.open("x", encoding="ascii") as handle:
            handle.write(value)
    except FileExistsError:
        return target.read_text(encoding="ascii").strip()
    return value


class ControlPlaneClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        session: requests.Session | Any | None = None,
        network_mode: str = "direct",
        proxy_url: str = "",
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session or build_control_session(mode=network_mode, proxy_url=proxy_url)
        self.headers = {"Authorization": f"Bearer {token}"}
        self.timeout = (8, 30)
        self.sleep = sleep

    def get_operation(self, idempotency_key: str) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/v1/worker/operations/{idempotency_key}",
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def retry_job(self, job_id: str, idempotency_key: str) -> dict[str, Any]:
        headers = {**self.headers, "Idempotency-Key": idempotency_key}
        try:
            response = self.session.post(
                f"{self.base_url}/v1/worker/jobs/{job_id}/retry",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as post_error:
            last_error: Exception = post_error
            for delay in (0, 1, 2, 4):
                if delay:
                    self.sleep(delay)
                try:
                    return self.get_operation(idempotency_key)
                except requests.RequestException as query_error:
                    last_error = query_error
            raise RuntimeError(
                "Retry outcome is unknown; POST was not repeated. Reuse the persisted idempotency key."
            ) from last_error
