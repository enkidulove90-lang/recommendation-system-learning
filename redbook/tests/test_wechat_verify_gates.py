"""Task 2 acceptance: WeChat draft-box reconciliation (TC11-TC14)."""
from __future__ import annotations

import pytest

from redbook.infrastructure.delivery_errors import (
    E_VERIFY_MISMATCH, E_VERIFY_UNCERTAIN, OrchestrationError,
)
from redbook.infrastructure.wechat_delivery import reconcile_draft_box


def test_reconcile_exactly_one_new_draft():  # TC11
    result = reconcile_draft_box(["a", "b"], ["a", "b", "c"])
    assert result == {"ok": True, "draft_id": "c",
                      "new_ids": ["c"], "verified": True}


def test_reconcile_multiple_new_drafts_is_mismatch():  # TC12
    with pytest.raises(OrchestrationError) as error:
        reconcile_draft_box(["a"], ["a", "b", "c"])
    assert error.value.code == E_VERIFY_MISMATCH
    assert error.value.details["new_ids"] == ["b", "c"]


def test_reconcile_zero_new_drafts_is_uncertain_not_delete():  # TC13
    with pytest.raises(OrchestrationError) as error:
        reconcile_draft_box(["a", "b"], ["a", "b"])
    assert error.value.code == E_VERIFY_UNCERTAIN
    # iron rule: the caller must NOT delete anything on uncertain
    assert error.value.details["before_count"] == error.value.details["after_count"]


def test_reconcile_tolerates_duplicate_and_type_noise():  # robustness
    result = reconcile_draft_box(["a", "a"], ["a", 1, 1])
    assert result["ok"] is True and result["draft_id"] == "1"
