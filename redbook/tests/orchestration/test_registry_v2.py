from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from redbook.orchestration.reconcile import (
    reconcile_stale_saves,
    reconcile_uncertain_deliveries,
    reconcile_verified_deliveries,
)
from redbook.orchestration.registry import SqliteDeliveryRegistry


def test_json_migration_is_single_source_then_reuses_existing_delivery(tmp_path) -> None:
    slug = "paper-1"
    source = tmp_path / "workflow_state" / slug / "delivery_registry.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({
        "slug": slug,
        "runs": [{
            "run_id": "run-1", "staged_id": "a" * 64, "draft_id": "s:draft-1",
            "status": "verify_passed", "verification": {"ok": True},
        }],
    }), encoding="utf-8")
    registry = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite")

    assert registry.migrate_json_once(tmp_path / "workflow_state") == 1
    assert registry.migrate_json_once(tmp_path / "workflow_state") == 0

    existing = registry.begin_save(
        run_id="run-2", content_hash="a" * 64, platform="xhs", account="default", staged_id="a" * 64,
    )

    assert existing["draft_id"] == "s:draft-1"
    assert existing["state"] == "VERIFIED"
    assert registry.delivery_count() == 1
    assert "body" not in existing
    assert "path" not in existing


def test_reconcile_recovers_crashed_saving_without_repeating_platform_save(tmp_path) -> None:
    registry = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite")
    assert registry.begin_save(
        run_id="run-1", content_hash="b" * 64, platform="xhs", account="default", staged_id="b" * 64,
    ) is None

    result = reconcile_stale_saves(
        registry, stale_after_seconds=0, find_draft=lambda entry: "s:recovered",
    )

    assert result == {"recovered": 1, "manual": 0}
    recovered = registry.find_delivery(platform="xhs", account="default", staged_id="b" * 64)
    assert recovered["state"] == "SAVED_UNVERIFIED"
    assert recovered["draft_id"] == "s:recovered"
    assert registry.begin_save(
        run_id="run-2", content_hash="b" * 64, platform="xhs", account="default", staged_id="b" * 64,
    )["draft_id"] == "s:recovered"


def test_reconcile_marks_missing_when_verified_platform_draft_disappears(tmp_path) -> None:
    registry = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite")
    registry.begin_save(
        run_id="run-1", content_hash="c" * 64, platform="xhs", account="default", staged_id="c" * 64,
    )
    registry.mark_saved_unverified(
        platform="xhs", account="default", staged_id="c" * 64, draft_id="s:gone",
    )
    registry.mark_verified(platform="xhs", account="default", staged_id="c" * 64)

    assert reconcile_verified_deliveries(registry, draft_exists=lambda _: False) == {"missing": 1}
    assert registry.find_delivery(platform="xhs", account="default", staged_id="c" * 64)["state"] == "MISSING"


def test_uncertain_verification_rolls_back_only_after_confirmed_mismatch(tmp_path) -> None:
    registry = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite")
    registry.begin_save(
        run_id="run-1", content_hash="d" * 64, platform="xhs", account="default", staged_id="d" * 64,
    )
    registry.mark_saved_unverified(
        platform="xhs", account="default", staged_id="d" * 64, draft_id="s:uncertain",
    )
    registry.mark_verify_uncertain(platform="xhs", account="default", staged_id="d" * 64)
    rollback_calls: list[str] = []

    result = reconcile_uncertain_deliveries(
        registry,
        verify=lambda _: "mismatch",
        rollback=lambda delivery: rollback_calls.append(str(delivery["draft_id"])) or True,
    )

    assert result == {"verified": 0, "rolled_back": 1, "uncertain": 0, "rollback_failed": 0}
    assert rollback_calls == ["s:uncertain"]
    assert registry.find_delivery(platform="xhs", account="default", staged_id="d" * 64)["state"] == "ROLLED_BACK"


def test_concurrent_saves_share_one_wal_delivery_row(tmp_path) -> None:
    database = tmp_path / "state" / "orchestration.sqlite"

    def begin(run_id: str):
        return SqliteDeliveryRegistry(database).begin_save(
            run_id=run_id, content_hash="e" * 64, platform="xhs", account="default", staged_id="e" * 64,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = tuple(pool.map(begin, ("run-1", "run-2")))

    assert (first is None) != (second is None)
    assert SqliteDeliveryRegistry(database).delivery_count() == 1
