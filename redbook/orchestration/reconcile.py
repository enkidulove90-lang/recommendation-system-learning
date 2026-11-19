"""Read-only platform reconciliation for interrupted draft saves."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .registry import SqliteDeliveryRegistry


DraftFinder = Callable[[dict[str, Any]], str | None]


def reconcile_stale_saves(registry: SqliteDeliveryRegistry, *, stale_after_seconds: float,
                          find_draft: DraftFinder) -> dict[str, int]:
    """Recover stale save intents without issuing another platform save request."""
    recovered = manual = 0
    for delivery in registry.stale_saving(stale_after_seconds):
        draft_id = find_draft(delivery)
        if draft_id:
            registry.mark_saved_unverified(
                platform=str(delivery["platform"]), account=str(delivery["account"]),
                staged_id=str(delivery["staged_id"]), draft_id=draft_id,
            )
            recovered += 1
        else:
            registry.mark_manual(
                platform=str(delivery["platform"]), account=str(delivery["account"]),
                staged_id=str(delivery["staged_id"]),
            )
            manual += 1
    return {"recovered": recovered, "manual": manual}


def reconcile_verified_deliveries(registry: SqliteDeliveryRegistry, *,
                                  draft_exists: Callable[[dict[str, Any]], bool]) -> dict[str, int]:
    """Mark only confirmed platform disappearances as MISSING for human follow-up."""
    missing = 0
    for delivery in registry.deliveries_in_state("VERIFIED"):
        if not draft_exists(delivery):
            registry.mark_missing(
                platform=str(delivery["platform"]), account=str(delivery["account"]),
                staged_id=str(delivery["staged_id"]),
            )
            missing += 1
    return {"missing": missing}


def reconcile_uncertain_deliveries(
    registry: SqliteDeliveryRegistry, *, verify: Callable[[dict[str, Any]], str],
    rollback: Callable[[dict[str, Any]], bool],
) -> dict[str, int]:
    """Retry uncertain reads; only a confirmed mismatch may invoke rollback."""
    result = {"verified": 0, "rolled_back": 0, "uncertain": 0, "rollback_failed": 0}
    for delivery in registry.deliveries_with_code("E_VERIFY_UNCERTAIN"):
        outcome = verify(delivery)
        key = {
            "platform": str(delivery["platform"]), "account": str(delivery["account"]),
            "staged_id": str(delivery["staged_id"]),
        }
        if outcome == "verified":
            registry.mark_verified(**key)
            result["verified"] += 1
        elif outcome == "mismatch":
            if rollback(delivery):
                registry.mark_rolled_back(**key)
                result["rolled_back"] += 1
            else:
                registry.mark_manual(**key, code="E_ROLLBACK_FAILED")
                result["rollback_failed"] += 1
        else:
            result["uncertain"] += 1
    return result
