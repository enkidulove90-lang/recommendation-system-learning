from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path
from unittest.mock import patch

from paper_intake.catalog_store import CatalogRepository
from scripts.refresh_paper_catalog import refresh_once


def _snapshot(db: Path) -> int:
    con = sqlite3.connect(db)
    total = con.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    con.close()
    return total


class _FakeCatalog:
    """Minimal catalog stand-in; only fields refresh_once touches."""

    def __init__(self, records):
        self.raw_records = records
        self.papers = records
        self.source_runs = {}


def test_upsert_failure_rolls_back_entire_batch(tmp_path) -> None:
    """方案 A 的 BEGIN IMMEDIATE + try/except rollback：batch 中途失败时
    整批回滚，不留下半写入的 papers 行。"""
    root = Path(__file__).resolve().parents[1]
    src = root / "data" / "paper_catalog" / "catalog.sqlite3"
    db = tmp_path / "catalog.sqlite3"
    shutil.copy2(src, db)
    before = _snapshot(db)

    # 构造 3 条合法记录（source/source_id/title 必填）
    from paper_intake.catalog import PaperRecord
    records = [
        PaperRecord(publication_year=2026, venue_type="c", venue_name="B",
                    title=f"Rollback Probe {i}", paper_url="", source="rollback_probe",
                    source_id=f"rb-{i}", authors=["A"], updated_at="2026-01-01")
        for i in range(3)
    ]
    fake = _FakeCatalog(records)

    original = CatalogRepository.upsert_candidate
    call_count = {"n": 0}

    def failing_upsert(self, record, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise RuntimeError("injected failure")
        return original(self, record, **kwargs)

    with patch("scripts.refresh_paper_catalog.refresh_from_config", return_value=fake), \
         patch("scripts.refresh_paper_catalog.export_discovery_snapshot", return_value={"paper_count": 3}), \
         patch("scripts.refresh_paper_catalog.export_snapshot", return_value={"paper_count": 3}), \
         patch.object(CatalogRepository, "upsert_candidate", failing_upsert):
        try:
            refresh_once(
                config_path=root / "config" / "paper_catalog_sources.json",
                output_path=db.parent / "papers.json",
                db_path=db,
                auto_enqueue=False,
            )
        except RuntimeError as exc:
            assert "injected failure" in str(exc)
        else:
            raise AssertionError("expected RuntimeError from injected failure")

    assert call_count["n"] == 2, "failure must be injected mid-batch"
    after = _snapshot(db)
    assert after == before, f"rollback failed: before={before}, after={after}"


def test_successful_batch_is_committed(tmp_path) -> None:
    """成功路径：整批提交后新行可见。"""
    root = Path(__file__).resolve().parents[1]
    src = root / "data" / "paper_catalog" / "catalog.sqlite3"
    db = tmp_path / "catalog.sqlite3"
    shutil.copy2(src, db)
    before = _snapshot(db)

    from paper_intake.catalog import PaperRecord
    records = [
        PaperRecord(publication_year=2026, venue_type="c", venue_name="B",
                    title=f"Commit Probe {i}", paper_url="", source="commit_probe",
                    source_id=f"cp-{i}", authors=["A"], updated_at="2026-01-01")
        for i in range(3)
    ]
    fake = _FakeCatalog(records)

    with patch("scripts.refresh_paper_catalog.refresh_from_config", return_value=fake), \
         patch("scripts.refresh_paper_catalog.export_discovery_snapshot", return_value={"paper_count": 3}), \
         patch("scripts.refresh_paper_catalog.export_snapshot", return_value={"paper_count": 3}):
        refresh_once(
            config_path=root / "config" / "paper_catalog_sources.json",
            output_path=db.parent / "papers.json",
            db_path=db,
            auto_enqueue=False,
        )

    after = _snapshot(db)
    assert after == before + 3, f"commit failed: before={before}, after={after}"
