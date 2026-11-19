import json

from redbook.scripts.migrate_staged_packages import migrate


def test_migration_renames_legacy_directory_once(tmp_path):
    staged_id = "d" * 64
    legacy = tmp_path / staged_id[:32]
    legacy.mkdir()
    (legacy / "xhs.json").write_text(json.dumps({"content_hash": staged_id}), encoding="utf-8")
    assert migrate(tmp_path, apply=True)["migrated"] == 1
    assert (tmp_path / staged_id).is_dir()
    assert migrate(tmp_path, apply=True)["migrated"] == 0
