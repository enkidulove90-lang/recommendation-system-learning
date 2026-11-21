from __future__ import annotations

import json
import sys

import pytest

import redbook.cli as cli
from redbook.infrastructure.delivery_errors import DeliveryError, E_TOPIC_UNAVAILABLE
from redbook.orchestration.registry import SqliteDeliveryRegistry


class _ReadOnlyDelivery:
    def __init__(self, drafts: list[dict[str, object]]) -> None:
        self._items = drafts
        self.opencli = type("Ready", (), {"preflight": lambda self: {}})()

    def _drafts(self) -> list[dict[str, object]]:
        return self._items


def test_note_reconcile_empty_registry_emits_success(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setattr(cli, "OpenCliXiaohongshuDelivery", lambda: _ReadOnlyDelivery([]))
    monkeypatch.setattr(sys, "argv", ["redbook.cli", "note", "--reconcile", "--data-root", str(tmp_path)])

    cli.main()

    result = json.loads(capsys.readouterr().out)
    assert result == {
        "ok": True,
        "results": [
            {"stale_saves": {"manual": 0, "recovered": 0}},
            {"verified_deliveries": {"missing": 0}},
            {"uncertain_deliveries": {
                "rollback_failed": 0, "rolled_back": 0, "uncertain": 0, "verified": 0,
            }},
        ],
        "orphans": [],
    }


def test_note_reconcile_reports_uncertain_draft_without_platform_deletion(monkeypatch, tmp_path, capsys) -> None:
    registry = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite")
    registry.begin_save(
        run_id="run-1", content_hash="j" * 64, platform="xhs", account="default", staged_id="j" * 64,
    )
    registry.mark_saved_unverified(
        platform="xhs", account="default", staged_id="j" * 64, draft_id="s:uncertain",
    )
    registry.mark_verify_uncertain(platform="xhs", account="default", staged_id="j" * 64)
    monkeypatch.setattr(
        cli, "OpenCliXiaohongshuDelivery", lambda: _ReadOnlyDelivery([{"id": "s:uncertain"}]),
    )
    monkeypatch.setattr(sys, "argv", ["redbook.cli", "note", "--reconcile", "--data-root", str(tmp_path)])

    cli.main()

    result = json.loads(capsys.readouterr().out)
    assert result["ok"] is True
    assert result["results"][2]["uncertain_deliveries"]["uncertain"] == 1
    stored = registry.find_delivery(platform="xhs", account="default", staged_id="j" * 64)
    assert stored["state"] == "SAVED_UNVERIFIED"
    assert stored["last_code"] == "E_VERIFY_UNCERTAIN"


def test_note_reconcile_maps_manual_preflight_error_to_exit_two(monkeypatch, tmp_path, capsys) -> None:
    class _BlockedDelivery:
        opencli = type("Blocked", (), {
            "preflight": lambda self: (_ for _ in ()).throw(
                DeliveryError("topic needs attention", E_TOPIC_UNAVAILABLE),
            ),
        })()

    monkeypatch.setattr(cli, "OpenCliXiaohongshuDelivery", _BlockedDelivery)
    monkeypatch.setattr(sys, "argv", ["redbook.cli", "note", "--reconcile", "--data-root", str(tmp_path)])

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2
    assert json.loads(capsys.readouterr().out)["code"] == E_TOPIC_UNAVAILABLE
