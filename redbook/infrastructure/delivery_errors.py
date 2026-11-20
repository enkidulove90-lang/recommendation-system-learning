"""Stable, serializable failures and disposition policy for draft-only delivery."""
from __future__ import annotations

import re
from typing import Any


ERROR_CODE_TABLE_VERSION = 1

E_PREFLIGHT_BLOCKED = "E_PREFLIGHT_BLOCKED"
E_OPENCLI_UNAVAILABLE = "E_OPENCLI_UNAVAILABLE"
E_RESPONSE_SHAPE = "E_RESPONSE_SHAPE"
E_TOPIC_UNAVAILABLE = "E_TOPIC_UNAVAILABLE"
E_SAVE_UNVERIFIED = "E_SAVE_UNVERIFIED"
E_VERIFY_MISMATCH = "E_VERIFY_MISMATCH"
E_REGISTRY_CONFLICT = "E_REGISTRY_CONFLICT"
E_AUTH = "E_AUTH"
E_VERIFY_UNCERTAIN = "E_VERIFY_UNCERTAIN"
E_ROLLBACK_FAILED = "E_ROLLBACK_FAILED"
E_QUEUE_FULL = "E_QUEUE_FULL"
E_UNKNOWN_MANUAL = "E_UNKNOWN_MANUAL"


_POLICIES: dict[str, dict[str, object]] = {
    E_PREFLIGHT_BLOCKED: {"retryable": False, "next_step": "修复 Bridge 预检后重试", "owner": "human"},
    E_OPENCLI_UNAVAILABLE: {"retryable": True, "next_step": "恢复 OpenCLI 后重试", "owner": "system"},
    E_RESPONSE_SHAPE: {"retryable": False, "next_step": "人工检查 OpenCLI 响应契约", "owner": "human"},
    E_TOPIC_UNAVAILABLE: {"retryable": False, "next_step": "人工改话题后重跑", "owner": "author"},
    E_SAVE_UNVERIFIED: {"retryable": True, "next_step": "读取草稿箱后重试", "owner": "system"},
    E_VERIFY_MISMATCH: {"retryable": False, "next_step": "确认不匹配后回滚", "owner": "system"},
    E_REGISTRY_CONFLICT: {"retryable": False, "next_step": "返回已有回执", "owner": "system"},
    E_AUTH: {"retryable": True, "next_step": "运行 scripts/login_qr.py 扫码后重试", "owner": "human"},
    E_VERIFY_UNCERTAIN: {"retryable": True, "next_step": "进对账 job，不删除", "owner": "system"},
    E_ROLLBACK_FAILED: {"retryable": True, "next_step": "进人工收件箱，附 draft_id", "owner": "human"},
    E_QUEUE_FULL: {"retryable": True, "next_step": "队列已满，稍后重新入队", "owner": "system"},
    E_UNKNOWN_MANUAL: {"retryable": False, "next_step": "人工排查未知异常后重跑", "owner": "human"},
}


def policy_for(code: str | None) -> dict[str, object]:
    """Return the versioned disposition policy without exposing mutable globals."""
    normalized = code if code in _POLICIES else E_SAVE_UNVERIFIED
    return {"code": normalized, **_POLICIES[normalized]}


def exit_code_for(code: str | None) -> int:
    """Keep manual/terminal failures at 2 and retryable failures at 3."""
    if code not in _POLICIES:
        return 2
    return 3 if bool(policy_for(code)["retryable"]) else 2


def _redact_message(message: str) -> str:
    return re.sub(r"(?:[A-Za-z]:\\|/)[^\s]+", "<path>", str(message))


class OrchestrationError(RuntimeError):
    """Base error whose code can always be rendered as a safe receipt."""

    def __init__(self, message: str, code: str = E_SAVE_UNVERIFIED,
                 details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = dict(details or {})

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class DeliveryError(OrchestrationError):
    """Delivery-bound specialization retained for existing adapter callers."""


def receipt_envelope(error: OrchestrationError, *, job_id: str = "", state: str = "failed",
                     evidence_ref: str = "") -> dict[str, object]:
    """Render the stable, path-redacted receipt contract used by CLI callers."""
    policy = policy_for(error.code)
    return {
        "ok": False, "job_id": job_id, "state": state, "code": policy["code"],
        "message": _redact_message(error.message), "retryable": policy["retryable"],
        "next_step": policy["next_step"], "owner": policy["owner"],
        "evidence_ref": evidence_ref,
    }
