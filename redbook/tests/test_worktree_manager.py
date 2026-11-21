"""WorktreeManager tests: audit flags, safety gates, orphan archiving."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from redbook.services.worktree_manager import WorktreeManager


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=60)
    assert proc.returncode == 0, f"git {args} failed: {proc.stderr}"
    return proc


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.test")
    _git(root, "config", "user.name", "t")
    (root / "file.txt").write_text("hello", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "init")
    return root


def _add_worktree(root: Path, name: str, *extra: str) -> Path:
    path = root / ".worktrees" / name
    _git(root, "worktree", "add", str(path), *extra)
    _git(path, "config", "user.email", "t@example.test")
    _git(path, "config", "user.name", "t")
    return path


def _by_name(statuses, name):
    return next(s for s in statuses if s.name == name)


# ------------------------------------------------------------------ audit

def test_audit_reports_registered_worktrees(repo):
    _add_worktree(repo, "wt-clean", "-b", "feat")
    statuses = WorktreeManager(repo).audit()
    names = {s.name for s in statuses}
    assert "wt-clean" in names and "proj" in names
    clean = _by_name(statuses, "wt-clean")
    assert clean.kind == "registered" and clean.branch == "feat"
    assert clean.uncommitted == 0 and "DIRTY" not in clean.flags


def test_dirty_worktree_flagged_and_remove_refused(repo):
    wt = _add_worktree(repo, "wt-dirty", "-b", "feat-dirty")
    (wt / "file.txt").write_text("changed", encoding="utf-8")
    manager = WorktreeManager(repo)
    status = _by_name(manager.audit(), "wt-dirty")
    assert "DIRTY" in status.flags and not status.removable
    with pytest.raises(ValueError, match="DIRTY"):
        manager.remove("wt-dirty", confirm=True)


def test_duplicate_tip_flagged(repo):
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _add_worktree(repo, "wt-a", head)
    _add_worktree(repo, "wt-b", head)
    statuses = WorktreeManager(repo).audit()
    a, b = _by_name(statuses, "wt-a"), _by_name(statuses, "wt-b")
    assert a.detached and b.detached
    assert "DUPLICATE_TIP" in a.flags and "DUPLICATE_TIP" in b.flags


def test_head_contained_elsewhere_marks_removable(repo):
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _add_worktree(repo, "wt-same", head)  # detached at main tip -> contained
    status = _by_name(WorktreeManager(repo).audit(), "wt-same")
    assert status.contained_elsewhere and "REMOVABLE" in status.flags


def test_clean_worktree_remove_requires_confirm(repo):
    _add_worktree(repo, "wt-ok", "-b", "feat-ok")
    manager = WorktreeManager(repo)
    with pytest.raises(ValueError, match="confirmation"):
        manager.remove("wt-ok")
    result = manager.remove("wt-ok", confirm=True)
    assert result["removed"].endswith("wt-ok")
    assert not (repo / ".worktrees" / "wt-ok").exists()


# ----------------------------------------------------------------- orphans

def test_orphan_dir_detected_and_archived(repo):
    orphan = repo / ".worktrees" / "old-snapshot"
    (orphan / "data").mkdir(parents=True)
    (orphan / "data" / "x.txt").write_text("v", encoding="utf-8")
    (orphan / "README.md").write_text("snap", encoding="utf-8")
    manager = WorktreeManager(repo)
    status = _by_name(manager.audit(), "old-snapshot")
    assert status.kind == "orphan" and "ORPHAN_DIR" in status.flags
    with pytest.raises(ValueError, match="archive"):
        manager.remove("old-snapshot", confirm=True)
    result = manager.archive("old-snapshot")
    assert not orphan.exists()
    assert Path(result["archived_to"]).is_dir()
    assert (Path(result["archived_to"]) / "README.md").is_file()


def test_orphan_with_duplicated_pdfs_marked_redundant(repo):
    orphan = repo / ".worktrees" / "dup-snapshot"
    (orphan / "data" / "papers").mkdir(parents=True)
    (repo / "data" / "papers").mkdir(parents=True)
    (orphan / "data" / "papers" / "2607.16633.pdf").write_bytes(b"%PDF")
    (repo / "data" / "papers" / "2607.16633.pdf").write_bytes(b"%PDF")
    status = _by_name(WorktreeManager(repo).audit(), "dup-snapshot")
    assert "REDUNDANT_COPY" in status.flags and status.size_mb >= 0


def test_registered_worktree_under_worktree_root_not_orphan(repo):
    _add_worktree(repo, "wt-live", "-b", "feat-live")
    statuses = WorktreeManager(repo).audit()
    assert _by_name(statuses, "wt-live").kind == "registered"
    assert not any(s.name == "wt-live" and s.kind == "orphan" for s in statuses)


def test_audit_json_output_serializable(repo):
    import json
    _add_worktree(repo, "wt-j", "-b", "feat-j")
    statuses = WorktreeManager(repo).audit()
    payload = json.dumps([s.to_dict() for s in statuses])
    assert "wt-j" in payload
