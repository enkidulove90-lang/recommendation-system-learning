from __future__ import annotations

import hashlib
import time
import uuid
from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from .control_client import sanitize_proxy_environment


class LeaseLost(RuntimeError):
    """Raised when Cloudflare no longer recognizes this worker's lease."""


class RemoteGatewayError(RuntimeError):
    def __init__(self, code: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class RemoteJob(BaseModel):
    job_id: str
    paper_id: str
    input_type: Literal["url", "pdf"]
    input_ref: str
    stage: str
    checkpoints: dict[str, dict[str, Any]] = Field(default_factory=dict)
    lease_owner: str
    lease_until: datetime
    artifact_storage_enabled: bool = True
    attempt: int = 0
    trace_id: str | None = None


class RemoteMetadataRefresh(BaseModel):
    idempotency_key: str
    job_id: str
    paper_id: str
    arxiv_id: str
    input_ref: str
    notion_page_id: str
    lease_owner: str
    lease_until: datetime


class RemoteGatewayClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        client: httpx.Client | None = None,
        max_attempts: int = 3,
        network_mode: str = "direct",
        proxy_url: str = "",
    ):
        self.base_url = base_url.rstrip("/")
        # The worker talks to one public Cloudflare endpoint directly. Ignoring
        # inherited proxy variables prevents stale desktop proxy settings from
        # terminating CONNECT tunnels during TLS negotiation.
        sanitize_proxy_environment()
        client_options: dict[str, Any] = {
            "base_url": self.base_url,
            "timeout": httpx.Timeout(connect=8, read=120, write=120, pool=8),
            "trust_env": False,
        }
        normalized_mode = network_mode.strip().lower()
        if normalized_mode == "proxy":
            if not proxy_url.strip():
                raise ValueError("PAPER_INTAKE_PROXY_URL is required in proxy mode")
            client_options["proxy"] = proxy_url.strip()
        elif normalized_mode != "direct":
            raise ValueError("PAPER_INTAKE_NETWORK_MODE must be direct or proxy")
        self.client = client or httpx.Client(**client_options)
        self.client.headers["Authorization"] = f"Bearer {token}"
        self.max_attempts = max(1, max_attempts)
        self.trace_id = ""

    def close(self) -> None:
        self.client.close()

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if self.trace_id:
            headers = dict(kwargs.pop("headers", {}) or {})
            headers.setdefault("X-Trace-Id", self.trace_id)
            kwargs["headers"] = headers
        response: httpx.Response | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.client.request(method, url, **kwargs)
            except httpx.RequestError as exc:
                if attempt == self.max_attempts:
                    raise RemoteGatewayError(
                        "gateway_unreachable",
                        "The paper intake gateway is unreachable.",
                        retryable=True,
                    ) from exc
                time.sleep(min(0.25 * 2 ** (attempt - 1), 2.0))
                continue
            if response.status_code != 429 and response.status_code < 500:
                return response
            if attempt == self.max_attempts:
                return response
            time.sleep(min(0.25 * 2 ** (attempt - 1), 2.0))
        if response is None:  # pragma: no cover - defensive guard
            raise RemoteGatewayError("gateway_unreachable", "Gateway request failed.", retryable=True)
        return response

    @staticmethod
    def _error(response: httpx.Response) -> RemoteGatewayError:
        try:
            body = response.json()
        except ValueError:
            body = {}
        code = str(body.get("code") or f"gateway_http_{response.status_code}")
        message = str(body.get("message") or "The paper intake gateway rejected the request.")
        if response.status_code == 409 and code == "lease_lost":
            return LeaseLost(code)
        return RemoteGatewayError(
            code,
            message[:500],
            retryable=bool(body.get("retryable") or response.status_code == 429 or response.status_code >= 500),
        )

    def _require_success(self, response: httpx.Response) -> httpx.Response:
        if response.is_success:
            return response
        raise self._error(response)

    def claim(self, worker_id: str) -> RemoteJob | None:
        response = self._request(
            "POST",
            "/v1/worker/jobs/claim",
            json={"worker_id": worker_id, "lease_seconds": 600},
        )
        if response.status_code == 204:
            return None
        self._require_success(response)
        payload = response.json()
        job = RemoteJob.model_validate(payload.get("job") or payload)
        self.trace_id = job.trace_id or ""
        return job

    def claim_metadata_refresh(self, worker_id: str) -> RemoteMetadataRefresh | None:
        response = self._request(
            "POST",
            "/v1/worker/metadata-refreshes/claim",
            json={"worker_id": worker_id, "lease_seconds": 600},
        )
        if response.status_code == 204:
            return None
        self._require_success(response)
        payload = response.json()
        return RemoteMetadataRefresh.model_validate(payload.get("operation") or payload)

    def enqueue_metadata_refresh(self, job_id: str, idempotency_key: str | None = None) -> dict[str, Any]:
        key = idempotency_key or str(uuid.uuid4())
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/refresh-metadata",
            headers={"Idempotency-Key": key},
        )
        payload = self._require_success(response).json()
        payload.setdefault("operation_key", key)
        return payload

    def get_metadata_refresh(self, operation_key: str) -> dict[str, Any]:
        response = self._request("GET", f"/v1/worker/metadata-refreshes/{operation_key}")
        return self._require_success(response).json()

    def complete_metadata_refresh(
        self,
        operation_key: str,
        worker_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/v1/worker/metadata-refreshes/{operation_key}/complete",
            json={"worker_id": worker_id, "result": result},
        )
        return self._require_success(response).json()

    def fail_metadata_refresh(
        self,
        operation_key: str,
        worker_id: str,
        code: str,
        message: str,
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/v1/worker/metadata-refreshes/{operation_key}/fail",
            json={
                "worker_id": worker_id,
                "error_code": code[:100],
                "error_message": message[:1000],
            },
        )
        return self._require_success(response).json()

    def heartbeat(self, job_id: str, worker_id: str, stage: str = "") -> bool:
        payload: dict[str, Any] = {"worker_id": worker_id, "lease_seconds": 600}
        if stage:
            payload["stage"] = stage
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/heartbeat",
            json=payload,
        )
        self._require_success(response)
        return True

    def download_input(self, job: RemoteJob) -> bytes:
        if job.input_type != "pdf":
            raise ValueError("download_input is only valid for hosted PDFs")
        return self._require_success(self._request("GET", job.input_ref)).content

    def download_artifact(self, job_id: str, worker_id: str, artifact_id: str) -> bytes:
        response = self._request(
            "GET",
            f"/v1/worker/jobs/{job_id}/artifacts/{artifact_id}",
            params={"worker_id": worker_id},
        )
        return self._require_success(response).content

    def checkpoint(
        self,
        job_id: str,
        worker_id: str,
        stage: str,
        output: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/checkpoint",
            json={"worker_id": worker_id, "stage": stage, "output": output},
        )
        return self._require_success(response).json()

    def upload_artifact(
        self,
        job_id: str,
        worker_id: str,
        *,
        kind: str,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> dict[str, Any]:
        digest = hashlib.sha256(content).hexdigest()
        response = self._request(
            "PUT",
            f"/v1/worker/jobs/{job_id}/artifacts/{kind}",
            params={"worker_id": worker_id},
            headers={
                "content-type": content_type,
                "x-content-sha256": digest,
                "x-artifact-name": filename,
            },
            content=content,
        )
        return self._require_success(response).json()

    def complete(
        self,
        job_id: str,
        worker_id: str,
        publication: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/complete",
            json={"worker_id": worker_id, "publication": publication},
        )
        return self._require_success(response).json()

    def fail(
        self,
        job_id: str,
        worker_id: str,
        code: str,
        message: str,
        failure: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/fail",
            json={
                "worker_id": worker_id,
                "error_code": code[:100],
                "error_message": message[:1000],
                "failure": failure or {},
            },
        )
        return self._require_success(response).json()
