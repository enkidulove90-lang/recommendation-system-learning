from __future__ import annotations

import hashlib
import time
from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field


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


class RemoteGatewayClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        client: httpx.Client | None = None,
        max_attempts: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(base_url=self.base_url, timeout=120)
        self.client.headers["Authorization"] = f"Bearer {token}"
        self.max_attempts = max(1, max_attempts)

    def close(self) -> None:
        self.client.close()

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
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
        return RemoteJob.model_validate(payload.get("job") or payload)

    def heartbeat(self, job_id: str, worker_id: str) -> bool:
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/heartbeat",
            json={"worker_id": worker_id, "lease_seconds": 600},
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
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/v1/worker/jobs/{job_id}/fail",
            json={
                "worker_id": worker_id,
                "error_code": code[:100],
                "error_message": message[:1000],
            },
        )
        return self._require_success(response).json()
