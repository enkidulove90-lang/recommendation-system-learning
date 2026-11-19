from __future__ import annotations

from redbook.infrastructure.delivery_errors import (
    ERROR_CODE_TABLE_VERSION,
    E_AUTH,
    E_ROLLBACK_FAILED,
    E_TOPIC_UNAVAILABLE,
    E_VERIFY_UNCERTAIN,
    DeliveryError,
    OrchestrationError,
    exit_code_for,
    policy_for,
    receipt_envelope,
)


def test_error_table_keeps_existing_codes_and_adds_t7_codes() -> None:
    expected = {
        "E_PREFLIGHT_BLOCKED", "E_OPENCLI_UNAVAILABLE", "E_RESPONSE_SHAPE",
        "E_TOPIC_UNAVAILABLE", "E_SAVE_UNVERIFIED", "E_VERIFY_MISMATCH",
        "E_REGISTRY_CONFLICT", E_AUTH, E_VERIFY_UNCERTAIN, E_ROLLBACK_FAILED,
    }
    assert ERROR_CODE_TABLE_VERSION == 1
    assert set(policy_for(code)["code"] for code in expected) == expected


def test_delivery_error_is_an_orchestration_error_with_policy_envelope() -> None:
    error = DeliveryError("failed at C:\\private\\note.txt", E_AUTH)

    assert isinstance(error, OrchestrationError)
    receipt = receipt_envelope(error, job_id="job-7", state="failed", evidence_ref="acceptance/e.json")

    assert receipt == {
        "ok": False, "job_id": "job-7", "state": "failed", "code": E_AUTH,
        "message": "failed at <path>", "retryable": True,
        "next_step": "运行 scripts/login_qr.py 扫码后重试", "owner": "human",
        "evidence_ref": "acceptance/e.json",
    }


def test_exit_codes_preserve_manual_and_retryable_contract() -> None:
    assert exit_code_for(E_TOPIC_UNAVAILABLE) == 2
    assert exit_code_for(E_AUTH) == 3
    assert exit_code_for(E_VERIFY_UNCERTAIN) == 3
    assert exit_code_for(E_ROLLBACK_FAILED) == 3
    assert exit_code_for(None) == 2
