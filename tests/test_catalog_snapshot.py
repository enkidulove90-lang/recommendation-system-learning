from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from paper_intake.catalog import PaperCatalog, PaperRecord
from paper_intake.catalog_snapshot import export_discovery_snapshot, export_snapshot
from paper_intake.catalog_store import CatalogRepository


def _record() -> PaperRecord:
    return PaperRecord(
        publication_year=2026, venue_type="preprint", venue_name="arXiv",
        title="Snapshot decoupling", paper_url="https://arxiv.org/abs/2601.09999",
        source="arxiv", source_id="2601.09999", arxiv_id="2601.09999", doi="",
        topics=["recommendation"], authors=["A. Author"],
    )


class SnapshotContractTest(unittest.TestCase):
    def test_discovery_snapshot_is_v2_with_canonical_id_and_checksum(self) -> None:
        with __import__("tempfile").TemporaryDirectory() as temporary:
            output = Path(temporary) / "papers.json"
            payload = export_discovery_snapshot(
                PaperCatalog([_record()]), output, watch_interval_seconds=1234,
            )
            written = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(written["schema_version"], 2)
        self.assertEqual(written["watch_interval_seconds"], 1234)
        self.assertEqual(written["paper_count"], 1)
        self.assertEqual(written["papers"][0]["canonical_id"], "arxiv:2601.09999")
        bare = {k: v for k, v in payload.items() if k != "checksum"}
        expected = hashlib.sha256(
            json.dumps(bare, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.assertEqual(payload["checksum"], expected)

    def test_discovery_snapshot_needs_no_database(self) -> None:
        with __import__("tempfile").TemporaryDirectory() as temporary:
            output = Path(temporary) / "papers.json"
            payload = export_discovery_snapshot(PaperCatalog([_record()]), output)
            self.assertEqual(payload["paper_count"], 1)
            self.assertFalse((Path(temporary) / "catalog.sqlite3").exists())

    def test_authoritative_snapshot_still_enriches_from_database(self) -> None:
        with __import__("tempfile").TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = CatalogRepository(root / "catalog.sqlite3")
            try:
                repository.upsert_candidate(_record())
                payload = export_snapshot(repository, root / "papers.json")
            finally:
                repository.close()
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["papers"][0]["status"], "discovered")
        self.assertEqual(payload["papers"][0]["sources"][0]["source"], "arxiv")


if __name__ == "__main__":
    unittest.main()
