from redbook.infrastructure.delivery_registry import DeliveryRegistry
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
    assert result == {"ok": True, "method": "registry", "draft_id": "s:draft-1", "reused": True}


def test_successful_platform_delivery_is_registered(tmp_path, monkeypatch):
    staged_id, slug = "b" * 64, "paper-2"
    package = tmp_path / "publish_queue" / staged_id[:32]
    package.mkdir(parents=True)
    (package / "xhs.json").write_text(json.dumps({"paper_id": slug}), encoding="utf-8")
    publisher = XhsPublisher(tmp_path)
    monkeypatch.setattr(publisher, "_publish_opencli", lambda _: {"ok": True, "draft_id": "s:new"})
    assert publisher.publish(staged_id)["draft_id"] == "s:new"
    assert DeliveryRegistry(tmp_path, slug).find_verified(staged_id)["draft_id"] == "s:new"
