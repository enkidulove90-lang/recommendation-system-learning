from redbook.infrastructure.delivery_registry import DeliveryRegistry
from redbook.orchestration.registry import SqliteDeliveryRegistry
from redbook.automation.publishing import XhsPublisher
import json


def test_verified_record_is_reused_for_same_slug_and_staged_id(tmp_path):
    registry = DeliveryRegistry(tmp_path, "paper-1")
    registry.record_verified("run-1", "staged-1", "s:draft-1", {"ok": True})
    found = registry.find_verified("staged-1")
    assert found["draft_id"] == "s:draft-1"


def test_orphan_does_not_count_as_verified(tmp_path):
    registry = DeliveryRegistry(tmp_path, "paper-1")
    registry.record_orphan("run-1", "staged-1", "s:bad", {"ok": False})
    assert registry.find_verified("staged-1") is None


def test_verified_staged_id_is_idempotent_without_platform_write(tmp_path, monkeypatch):
    staged_id, slug = "a" * 64, "paper-1"
    package = tmp_path / "publish_queue" / staged_id[:32]
    package.mkdir(parents=True)
    (package / "xhs.json").write_text(json.dumps({"paper_id": slug}), encoding="utf-8")
    DeliveryRegistry(tmp_path, slug).record_verified("run-1", staged_id, "s:draft-1", {"ok": True})
    publisher = XhsPublisher(tmp_path)
    monkeypatch.setattr(publisher, "_publish_opencli", lambda _: (_ for _ in ()).throw(AssertionError("must not write")))
    result = publisher.publish(staged_id)
    assert result == {
        "ok": True, "method": "registry", "draft_id": "s:draft-1",
        "state": "VERIFIED", "reused": True,
    }


def test_successful_platform_delivery_is_registered(tmp_path, monkeypatch):
    staged_id, slug = "b" * 64, "paper-2"
    package = tmp_path / "publish_queue" / staged_id[:32]
    package.mkdir(parents=True)
    (package / "xhs.json").write_text(json.dumps({"paper_id": slug}), encoding="utf-8")
    publisher = XhsPublisher(tmp_path)
    monkeypatch.setattr("redbook.automation.publishing.opencli_runtime.is_available", lambda: True)
    monkeypatch.setattr("redbook.automation.publishing.opencli_runtime.OpenCliClient", lambda: type("Ready", (), {"preflight": lambda self: {}})())
    monkeypatch.setattr(publisher, "_publish_opencli", lambda _: {"ok": True, "draft_id": "s:new"})
    assert publisher.publish(staged_id)["draft_id"] == "s:new"
    stored = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite").find_delivery(
        platform="xhs", account="default", staged_id=staged_id,
    )
    assert stored["draft_id"] == "s:new"
    assert stored["state"] == "VERIFIED"


def test_failed_delivery_with_known_draft_is_registered_as_orphan(tmp_path, monkeypatch):
    staged_id, slug = "d" * 64, "paper-4"
    package = tmp_path / "publish_queue" / staged_id
    package.mkdir(parents=True)
    (package / "xhs.json").write_text(json.dumps({"paper_id": slug}), encoding="utf-8")
    publisher = XhsPublisher(tmp_path)
    monkeypatch.setattr("redbook.automation.publishing.opencli_runtime.is_available", lambda: True)
    monkeypatch.setattr("redbook.automation.publishing.opencli_runtime.OpenCliClient", lambda: type("Ready", (), {"preflight": lambda self: {}})())
    monkeypatch.setattr(publisher, "_publish_opencli", lambda _: {"ok": False, "draft_id": "s:deleted", "error_code": "E_VERIFY_MISMATCH"})

    result = publisher.publish(staged_id)

    assert result["ok"] is False
    stored = SqliteDeliveryRegistry(tmp_path / "state" / "orchestration.sqlite").find_delivery(
        platform="xhs", account="default", staged_id=staged_id,
    )
    assert stored["state"] == "ROLLED_BACK"
    assert stored["draft_id"] == "s:deleted"


def test_preflight_failure_never_calls_platform_write(tmp_path, monkeypatch):
    staged_id, slug = "c" * 64, "paper-3"
    package = tmp_path / "publish_queue" / staged_id[:32]
    package.mkdir(parents=True)
    (package / "xhs.json").write_text(json.dumps({"paper_id": slug}), encoding="utf-8")
    publisher = XhsPublisher(tmp_path)
    monkeypatch.setattr("redbook.automation.publishing.opencli_runtime.is_available", lambda: True)
    class Blocked:
        def preflight(self):
            from redbook.infrastructure.delivery_errors import DeliveryError
            raise DeliveryError("stale", "E_PREFLIGHT_BLOCKED")
    monkeypatch.setattr("redbook.automation.publishing.opencli_runtime.OpenCliClient", Blocked)
    monkeypatch.setattr(publisher, "_publish_opencli", lambda _: (_ for _ in ()).throw(AssertionError("must not write")))
    assert publisher.publish(staged_id)["error_code"] == "E_PREFLIGHT_BLOCKED"
