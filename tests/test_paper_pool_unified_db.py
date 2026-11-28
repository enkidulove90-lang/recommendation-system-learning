from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile

from redbook.sentinel.paper_pool import DEFAULT_PAPER_POOL_DB, PaperPool


def test_paper_pool_defaults_to_unified_catalog_database() -> None:
    assert DEFAULT_PAPER_POOL_DB.name == "catalog.sqlite3"
    assert "paper_catalog" in DEFAULT_PAPER_POOL_DB.parts


def test_paper_pool_default_resolves_inside_the_repository() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    assert DEFAULT_PAPER_POOL_DB == repo_root / "data" / "paper_catalog" / "catalog.sqlite3"


def test_paper_pool_keeps_explicit_path_for_isolated_tests() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "pool.sqlite3"
        pool = PaperPool(path)
        assert pool.path == path
        assert path.exists()


def test_cli_sentinel_command_triggers_pool_ddl(monkeypatch, tmp_path) -> None:
    """Production instantiation point: `redbook.cli sentinel` builds PaperPool(),
    which must create the three pool tables in the unified catalog database."""
    from redbook.cli import main as cli_main
    from redbook.sentinel import paper_pool as pool_module

    target = tmp_path / "catalog.sqlite3"
    monkeypatch.setattr(pool_module, "DEFAULT_PAPER_POOL_DB", target)
    monkeypatch.setattr(
        sys, "argv",
        ["redbook.cli", "sentinel", "pool", "--data-root", str(tmp_path / "data")])

    cli_main()

    with sqlite3.connect(target) as connection:
        names = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"paper_pool", "sentinel_meta", "paper_pool_platform_delivery"} <= names
