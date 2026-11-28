from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts import migrate_canonical_ids


def _seed(database: Path, values: list[str]) -> None:
    from paper_intake.repository import JobRepository

    repository = JobRepository(database)
    try:
        for value in values:
            job = repository.create_job(source_type="upload", upload_path=f"/tmp/{value}.pdf")
            repository.update_job(job.job_id, canonical_id=value)
    finally:
        repository.close()


def test_migration_is_dry_run_by_default_and_prefixes_bare_ids(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "catalog.sqlite3"
    _seed(database, ["2302.08191", "2026.acl-short.10"])
    monkeypatch.setenv("PAPER_INTAKE_DB_PATH", str(database))

    options = {"expected_database": database}
    report = migrate_canonical_ids.apply_migration(database, dry_run=True, **options)
    assert report["applied"] == 0
    assert report["mapped"]["2302.08191"] == "arxiv:2302.08191"
    assert report["mapped"]["2026.acl-short.10"] == "source:acl_anthology:2026.acl-short.10"

    applied = migrate_canonical_ids.apply_migration(database, dry_run=False, **options)
    assert applied["applied"] == 2
    again = migrate_canonical_ids.apply_migration(database, dry_run=False, **options)
    assert again["bare_count"] == 0
    assert again["applied"] == 0


def test_migration_aborts_on_collision(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "catalog.sqlite3"
    _seed(database, ["2302.08191", "2302.08191v2"])
    monkeypatch.setenv("PAPER_INTAKE_DB_PATH", str(database))

    with pytest.raises(RuntimeError, match="collision"):
        migrate_canonical_ids.apply_migration(database, dry_run=False, expected_database=database)
