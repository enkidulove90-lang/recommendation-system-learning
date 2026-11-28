"""Delivery ledger: overwrite-not-skip semantics for XHS drafts."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import delivery_ledger as L  # noqa: E402


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = Path(self.dir) / "ledger.json"

    def test_record_and_get_roundtrip(self):
        L.record("xhs", "2026.acl.1", path=self.path, draft_id="s:1")
        self.assertEqual(L.get("xhs", "2026.acl.1", path=self.path)["draft_id"], "s:1")

    def test_missing_returns_empty(self):
        self.assertEqual(L.get("xhs", "nope", path=self.path), {})

    def test_refresh_creates_and_retires_previous(self):
        L.record("xhs", "p1", path=self.path, draft_id="s:old")
        deleted: list[str] = []
        out = L.refresh_xhs_draft(
            "p1", path=self.path,
            create=lambda: "s:new",
            delete=lambda did: deleted.append(did),
        )
        self.assertTrue(out["ok"])
        self.assertEqual(out["draft_id"], "s:new")
        self.assertTrue(out["retired_previous"])
        self.assertEqual(deleted, ["s:old"])
        self.assertEqual(L.get("xhs", "p1", path=self.path)["draft_id"], "s:new")

    def test_refresh_first_time_has_no_previous(self):
        deleted: list[str] = []
        out = L.refresh_xhs_draft(
            "p2", path=self.path, create=lambda: "s:fresh",
            delete=lambda did: deleted.append(did))
        self.assertTrue(out["ok"])
        self.assertFalse(out["retired_previous"])
        self.assertEqual(deleted, [])

    def test_create_failure_keeps_previous_draft(self):
        L.record("xhs", "p3", path=self.path, draft_id="s:keep")
        deleted: list[str] = []
        out = L.refresh_xhs_draft(
            "p3", path=self.path, create=lambda: None,
            delete=lambda did: deleted.append(did))
        self.assertFalse(out["ok"])
        self.assertEqual(deleted, [], "must not delete old draft when create fails")
        self.assertEqual(L.get("xhs", "p3", path=self.path)["draft_id"], "s:keep")

    def test_delete_failure_still_records_new(self):
        L.record("xhs", "p4", path=self.path, draft_id="s:old")
        def boom(_): raise RuntimeError("delete failed")
        out = L.refresh_xhs_draft("p4", path=self.path, create=lambda: "s:new2", delete=boom)
        self.assertTrue(out["ok"])
        self.assertFalse(out["retired_previous"])
        self.assertEqual(L.get("xhs", "p4", path=self.path)["draft_id"], "s:new2")


if __name__ == "__main__":
    unittest.main()
