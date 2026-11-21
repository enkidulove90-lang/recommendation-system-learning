"""Skill routing registry regression + counterexamples.

Integration gate: ``SkillManager.validate`` must be green against the real
repository (not just tmp-tree helper tests), and every failure mode has a
counterexample proving the validator actually fires.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from redbook.services.skill_manager import SkillManager

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_IDS = {"xhs-paper-draft", "multi-platform-publishing", "paper-summarize"}


# --- real-repository integration ---------------------------------------------

def test_real_repo_registry_routes_are_valid_and_green():
    issues = SkillManager(ROOT).validate()
    assert issues == [], "\n".join(str(i) for i in issues)


def test_real_repo_registry_has_expected_active_routes():
    registry = yaml.safe_load((ROOT / "config/skill_registry.yaml").read_text(encoding="utf-8"))
    active = [item for item in registry["skills"] if item["status"] == "active"]
    assert {item["id"] for item in active} == ACTIVE_IDS
    for item in active:
        assert item["entrypoint"] and item["verification_command"]


def test_real_repo_agents_md_has_no_broken_repo_links():
    manager = SkillManager(ROOT)
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    broken = manager.sweep_markdown_links(text)
    assert broken == [], f"broken repo-relative links in AGENTS.md: {broken}"


# --- legacy pointer / archive invariants --------------------------------------

def test_deprecated_claude_xhs_skill_is_pointer_only():
    pointer = (ROOT / ".claude/skills/redbook-publish/SKILL.md").read_text(encoding="utf-8")
    assert "status: deprecated" in pointer
    assert ".agents/skills/xhs-paper-draft/SKILL.md" in pointer
    assert "python -m redbook.cli note" in pointer
    assert "opencli xiaohongshu publish" not in pointer
    assert "curl -L -o" not in pointer


def test_claude_paper_summarize_is_pointer_to_canonical_body():
    pointer = (ROOT / ".claude/skills/paper-summarize/SKILL.md").read_text(encoding="utf-8")
    assert "status: deprecated" in pointer
    assert ".agents/skills/paper-summarize/SKILL.md" in pointer
    canonical = (ROOT / ".agents/skills/paper-summarize/SKILL.md").read_text(encoding="utf-8")
    assert "8 个必填区块" in canonical  # body survived the consolidation


def test_legacy_skill_is_archived_as_non_executable_history():
    history = ROOT / "archive/skill_history/redbook-publish-legacy.md"
    assert history.is_file()
    assert "opencli xiaohongshu publish" in history.read_text(encoding="utf-8")
    notice = (ROOT / "archive/skill_history/README.md").read_text(encoding="utf-8")
    assert "勿执行" in notice


def test_removed_placeholder_skill_is_gone_from_disk():
    assert not (ROOT / ".claude/skills/evil-read-arxiv").exists()


# --- counterexamples: validator must fire on each failure mode -----------------

def _tmp_repo(tmp_path: Path) -> tuple[SkillManager, Path]:
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)
    (root / "archive" / "skill_history").mkdir(parents=True)
    (root / "archive" / "skill_history" / "README.md").write_text("历史归档，勿执行。", encoding="utf-8")
    (root / ".agents" / "skills" / "alpha").mkdir(parents=True)
    return SkillManager(root), root


def _write_registry(root: Path, payload: dict) -> None:
    (root / "config" / "skill_registry.yaml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _good_registry(root: Path) -> dict:
    (root / ".agents" / "skills" / "alpha" / "SKILL.md").write_text(
        "---\nname: alpha\n---\nalpha body", encoding="utf-8")
    return {
        "schema_version": 2,
        "forbidden_executable_patterns": ["opencli xiaohongshu publish"],
        "skills": [{
            "id": "alpha", "status": "active", "owner": "redbook",
            "canonical_path": ".agents/skills/alpha/SKILL.md",
            "entrypoint": "python -m alpha", "verification_command": "python -m alpha --help",
        }],
    }


def test_counterexample_route_missing_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    registry = _good_registry(root)
    (root / ".agents" / "skills" / "alpha" / "SKILL.md").unlink()
    _write_registry(root, registry)
    codes = {i.code for i in manager.validate()}
    assert "ROUTE_MISSING" in codes


def test_counterexample_duplicate_active_id_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    registry = _good_registry(root)
    (root / ".agents" / "skills" / "beta").mkdir()
    (root / ".agents" / "skills" / "beta" / "SKILL.md").write_text("b", encoding="utf-8")
    registry["skills"].append(dict(registry["skills"][0], id="alpha"))  # same id twice
    _write_registry(root, registry)
    codes = {i.code for i in manager.validate()}
    assert "DUPLICATE_ID" in codes


def test_counterexample_bad_superseded_by_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    registry = _good_registry(root)
    registry["skills"].append({
        "id": "old", "status": "deprecated", "owner": "redbook",
        "canonical_path": ".agents/skills/old/SKILL.md", "superseded_by": "ghost",
    })
    (root / ".agents" / "skills" / "old").mkdir()
    (root / ".agents" / "skills" / "old" / "SKILL.md").write_text(
        "status: deprecated\nlegacy", encoding="utf-8")
    _write_registry(root, registry)
    codes = {i.code for i in manager.validate()}
    assert "BAD_SUPERSEDED_BY" in codes


def test_counterexample_executable_deprecated_skill_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    registry = _good_registry(root)
    registry["skills"].append({
        "id": "old", "status": "deprecated", "owner": "redbook",
        "canonical_path": ".agents/skills/old/SKILL.md", "superseded_by": "alpha",
    })
    old = root / ".agents" / "skills" / "old"
    old.mkdir()
    (old / "SKILL.md").write_text(
        "status: deprecated\nrun: opencli xiaohongshu publish", encoding="utf-8")
    _write_registry(root, registry)
    codes = {i.code for i in manager.validate()}
    assert "EXECUTABLE_DEPRECATED" in codes


def test_counterexample_orphan_disk_skill_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    _write_registry(root, _good_registry(root))
    (root / ".agents" / "skills" / "rogue").mkdir()
    (root / ".agents" / "skills" / "rogue" / "SKILL.md").write_text("r", encoding="utf-8")
    codes = {i.code for i in manager.validate()}
    assert "ORPHAN_SKILL" in codes


def test_counterexample_removed_skill_still_on_disk_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    registry = _good_registry(root)
    registry["skills"].append({
        "id": "gone", "status": "removed", "owner": "redbook",
        "canonical_path": ".agents/skills/gone", "note": "placeholder deleted",
    })
    (root / ".agents" / "skills" / "gone").mkdir()
    _write_registry(root, registry)
    codes = {i.code for i in manager.validate()}
    assert "REMOVED_STILL_PRESENT" in codes


def test_counterexample_user_level_duplicate_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    home = tmp_path / "home"
    user_skill = home / ".claude" / "skills" / "alpha"
    user_skill.mkdir(parents=True)
    (user_skill / "SKILL.md").write_text("user-level copy", encoding="utf-8")
    manager.home_override = home
    _write_registry(root, _good_registry(root))
    codes = {i.code for i in manager.validate()}
    assert "USER_LEVEL_DUPLICATE" in codes


def test_counterexample_missing_archive_notice_fires(tmp_path):
    manager, root = _tmp_repo(tmp_path)
    registry = _good_registry(root)
    (root / "archive" / "skill_history" / "README.md").unlink()
    _write_registry(root, registry)
    codes = {i.code for i in manager.validate()}
    assert "ARCHIVE_NOTICE" in codes


# --- integration: deprecate() end-to-end ---------------------------------------

def test_deprecate_end_to_end_archives_pointer_and_registry(tmp_path):
    """Full-chain proof (not a helper unit test): deprecate -> archive exists,
    pointer is clean, registry updated, validator green afterwards."""
    manager, root = _tmp_repo(tmp_path)
    _write_registry(root, _good_registry(root))
    # realistic two-skill repo: alpha retired in favour of beta
    (root / ".agents" / "skills" / "beta").mkdir()
    (root / ".agents" / "skills" / "beta" / "SKILL.md").write_text("beta body", encoding="utf-8")
    registry = _good_registry(root)
    registry["skills"].append({
        "id": "beta", "status": "active", "owner": "redbook",
        "canonical_path": ".agents/skills/beta/SKILL.md",
        "entrypoint": "python -m beta", "verification_command": "python -m beta --help",
    })
    _write_registry(root, registry)

    artifacts = manager.deprecate("alpha", "beta", pointer_note="先读 AGENTS.md，再用 beta 技能。")

    history = Path(artifacts["history"])
    pointer = Path(artifacts["pointer"])
    assert history.is_file() and "alpha body" in history.read_text(encoding="utf-8")
    pointer_text = pointer.read_text(encoding="utf-8")
    assert "status: deprecated" in pointer_text and "beta 技能" in pointer_text
    assert "opencli xiaohongshu publish" not in pointer_text

    registry_after = manager.load_registry()
    entry = next(s for s in registry_after["skills"] if s["id"] == "alpha")
    assert entry["status"] == "deprecated" and entry["superseded_by"] == "beta"

    leftover = SkillManager(root).validate()
    assert leftover == [], "\n".join(str(i) for i in leftover)
