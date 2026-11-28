"""P2 write-convergence: NotionGateway read-only by default + overwrite guard.

Uses unittest (pytest lacks pluggy in this environment). No network: the
Gateway's I/O helpers are monkeypatched to record calls.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from paper_intake.adapters import NotionDraft, NotionGateway  # noqa: E402


def make_gateway(*, allow_write: bool | None = None) -> tuple[NotionGateway, list[str]]:
    kwargs = {"allow_write": allow_write} if allow_write is not None else {}
    gw = NotionGateway("token", "db", **kwargs)
    calls: list[str] = []
    gw.preflight_schema = lambda: set()  # type: ignore[method-assign]
    gw._find_by_arxiv = lambda arxiv_id: None  # type: ignore[method-assign]
    gw._create_page = lambda properties: {"id": "new-page", "url": ""}  # type: ignore[method-assign]
    gw._update_page = lambda page_id, properties: calls.append("update")  # type: ignore[method-assign]
    gw._upload_file = lambda path: "upload-id"  # type: ignore[method-assign]
    gw._blocks = lambda markdown, uploads: []  # type: ignore[method-assign]
    gw._clear_children = lambda page_id: calls.append("clear")  # type: ignore[method-assign]
    def fake_request(method, path, **kw):
        calls.append(f"{method} {path}")
        if path.endswith("/markdown"):
            return {"markdown": ""}
        if "data_sources" in path and method == "GET":
            return {"properties": {}}
        return {}
    gw._request = fake_request  # type: ignore[method-assign]
    return gw, calls


def draft() -> NotionDraft:
    return NotionDraft(arxiv_id="2601.00001", title="T", slug="s", summary="", markdown="# T")


class GatewayReadOnlyTest(unittest.TestCase):
    def test_default_upsert_published_is_blocked(self):
        gw, calls = make_gateway()
        with self.assertRaisesRegex(RuntimeError, "read.only"):
            gw.upsert_published(draft())
        self.assertEqual(calls, [], "no writes should happen in read-only mode")

    def test_explicit_allow_write_enables_upsert(self):
        gw, calls = make_gateway(allow_write=True)
        page = gw.upsert_published(draft())
        self.assertEqual(page.page_id, "new-page")
        self.assertIn("clear", calls)

    def test_default_publish_is_blocked(self):
        gw, calls = make_gateway()
        with self.assertRaisesRegex(RuntimeError, "read.only"):
            gw.publish("page-1", title="T", slug="s", arxiv_id="2601.00001")
        self.assertEqual(calls, [])

    def test_read_methods_still_work_when_read_only(self):
        gw, _ = make_gateway()
        # snapshot / schema are read operations and must remain available.
        self.assertEqual(gw._snapshot_markdown("page-1"), "")
        self.assertIsInstance(gw._data_source(), str)


class GatewayOverwriteGuardTest(unittest.TestCase):
    def setUp(self):
        self.gw, self.calls = make_gateway(allow_write=True)
        self.gw._find_by_arxiv = lambda arxiv_id: {"id": "existing", "url": ""}  # type: ignore[method-assign]
        self.gw._snapshot_markdown = lambda page_id: "existing body"  # type: ignore[method-assign]

    def test_overwrite_existing_page_blocked_by_default(self):
        with self.assertRaisesRegex(RuntimeError, "overwrite"):
            self.gw.upsert_published(draft())
        self.assertNotIn("clear", self.calls, "must not clear children when blocked")

    def test_explicit_overwrite_marker_allows_and_snapshots(self):
        snapshots: list[str] = []
        self.gw._snapshot_markdown = lambda page_id: (snapshots.append("existing body") or "existing body")  # type: ignore[method-assign]
        self.gw.upsert_published(draft(), allow_overwrite=True)
        self.assertIn("clear", self.calls)
        self.assertEqual(snapshots, ["existing body"])
        self.assertEqual(self.gw.last_overwrite_snapshot, "existing body")

    def test_empty_existing_body_does_not_block(self):
        self.gw._snapshot_markdown = lambda page_id: ""  # type: ignore[method-assign]
        self.gw.upsert_published(draft())
        self.assertIn("clear", self.calls)


if __name__ == "__main__":
    unittest.main()
