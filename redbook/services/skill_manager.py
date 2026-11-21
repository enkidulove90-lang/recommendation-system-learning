"""Centralized skill registry manager.

One truth source (``config/skill_registry.yaml``) routes every agent skill in
the repository. Canonical bodies live under ``.agents/skills/``; IDE-local
directories (``.claude/skills/`` 等) may only hold pointer stubs; deprecated
bodies are archived under ``archive/skill_history/`` as non-executable history.

``validate`` is the routing gate used by regression tests and CI: it checks
registry integrity (unique ids, existing canonical paths, entrypoints), that
deprecated on-disk skills are pointer-only (no executable commands), that no
on-disk skill is unregistered, and that user-level skill directories do not
duplicate a repo-local active id. ``deprecate`` performs the full archive +
pointer + registry rewrite so a skill can be retired in one auditable step.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path("config/skill_registry.yaml")
ARCHIVE_DIR = Path("archive/skill_history")
CANONICAL_DIRS = (Path(".agents/skills"), Path(".claude/skills"))
POINTER_DIRS = (Path(".claude/skills"),)  # IDE-local: stubs only
USER_SKILL_DIRS = (Path.home() / ".claude" / "skills",
                   Path.home() / ".workbuddy" / "skills",
                   Path.home() / ".codex" / "skills")
ACTIVE_STATUSES = frozenset({"active"})
DISK_STATUSES = frozenset({"active", "deprecated"})  # removed = must be absent


@dataclass
class SkillIssue:
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.path}: {self.message}"


@dataclass
class SkillManager:
    root: Path
    home_override: Path | None = None  # injectable for duplicate-routing tests
    _issues: list[SkillIssue] = field(default_factory=list, repr=False)

    # -- loading --------------------------------------------------------------
    @property
    def registry_path(self) -> Path:
        return self.root / REGISTRY_PATH

    def load_registry(self) -> dict[str, Any]:
        return yaml.safe_load(self.registry_path.read_text(encoding="utf-8"))

    def _skills(self, registry: dict[str, Any]) -> list[dict[str, Any]]:
        return list(registry.get("skills", []))

    def _active_ids(self, registry: dict[str, Any]) -> set[str]:
        return {s["id"] for s in self._skills(registry) if s.get("status") == "active"}

    def _user_skill_dirs(self) -> list[Path]:
        if self.home_override is not None:
            home = self.home_override
            return [home / ".claude" / "skills", home / ".workbuddy" / "skills",
                    home / ".codex" / "skills"]
        return list(USER_SKILL_DIRS)

    # -- validation -----------------------------------------------------------
    def validate(self) -> list[SkillIssue]:
        self._issues = []
        registry = self.load_registry()
        self._check_schema(registry)
        self._check_entries(registry)
        self._check_orphan_disk_skills(registry)
        self._check_archive_notice()
        self._check_user_level_duplicates(registry)
        return self._issues

    def _check_schema(self, registry: dict[str, Any]) -> None:
        if registry.get("schema_version") != 2:
            self._add("SCHEMA", str(REGISTRY_PATH),
                      f"schema_version must be 2, got {registry.get('schema_version')}")

    def _check_entries(self, registry: dict[str, Any]) -> None:
        skills = self._skills(registry)
        active_ids = self._active_ids(registry)
        seen: set[str] = set()
        for skill in skills:
            sid = str(skill.get("id", ""))
            path = str(skill.get("canonical_path", ""))
            status = str(skill.get("status", ""))
            if not sid or sid in seen:
                self._add("DUPLICATE_ID", path, f"missing or duplicate id {sid!r}")
            seen.add(sid)
            target = self.root / path
            if status == "removed":
                if target.exists():
                    self._add("REMOVED_STILL_PRESENT", path,
                              "removed skill must not exist on disk")
                if not str(skill.get("note", "")).strip():
                    self._add("REMOVED_NO_NOTE", path, "removed entry needs a note")
                continue
            if not target.is_file():
                self._add("ROUTE_MISSING", path, "canonical_path is not a file")
            if status == "active":
                if not str(skill.get("entrypoint", "")).strip():
                    self._add("NO_ENTRYPOINT", path, "active skill needs an entrypoint")
                if not str(skill.get("verification_command", "")).strip():
                    self._add("NO_VERIFICATION", path,
                              "active skill needs a verification_command")
            elif status == "deprecated":
                if skill.get("superseded_by") not in active_ids:
                    self._add("BAD_SUPERSEDED_BY", path,
                              f"superseded_by {skill.get('superseded_by')!r} is not an active id")
                self._check_deprecated_disk_state(skill, path, registry, target)
            else:
                self._add("BAD_STATUS", path, f"unknown status {status!r}")

    def _check_deprecated_disk_state(self, skill: dict[str, Any], path: str,
                                     registry: dict[str, Any], target: Path) -> None:
        if target.is_file():
            text = target.read_text(encoding="utf-8")
            if "status: deprecated" not in text and "status: pointer" not in text:
                self._add("DEPRECATED_NOT_MARKED", path,
                          "on-disk deprecated skill must declare status: deprecated/pointer")
            for pattern in registry.get("forbidden_executable_patterns", []):
                if str(pattern) in text:
                    self._add("EXECUTABLE_DEPRECATED", path,
                              f"deprecated skill contains forbidden command {pattern!r}")
        # Body must survive somewhere: an archived history file, or the
        # superseding active skill that absorbed the canonical body.
        history = str(skill.get("history_path", "")).strip()
        body_preserved = bool(history) and (self.root / history).is_file()
        if not body_preserved:
            successor = str(skill.get("superseded_by", ""))
            successor_paths = {
                s["canonical_path"] for s in self._skills(registry)
                if s.get("id") == successor and s.get("status") == "active"
            }
            body_preserved = any((self.root / p).is_file() for p in successor_paths)
        if not body_preserved:
            self._add("HISTORY_MISSING", path,
                      "deprecated skill needs an archived body or an active successor "
                      "that preserves the canonical body")

    def _check_orphan_disk_skills(self, registry: dict[str, Any]) -> None:
        registered = {str(s.get("canonical_path", "")) for s in self._skills(registry)}
        for base in CANONICAL_DIRS:
            base_dir = self.root / base
            if not base_dir.is_dir():
                continue
            for skill_dir in sorted(base_dir.iterdir()):
                marker = skill_dir / "SKILL.md"
                if marker.is_file():
                    rel = marker.relative_to(self.root).as_posix()
                    if rel not in registered:
                        self._add("ORPHAN_SKILL", rel,
                                  "on-disk skill is not registered in skill_registry.yaml")

    def _check_archive_notice(self) -> None:
        readme = self.root / ARCHIVE_DIR / "README.md"
        if not readme.is_file() or "勿执行" not in readme.read_text(encoding="utf-8"):
            self._add("ARCHIVE_NOTICE", str(ARCHIVE_DIR / "README.md"),
                      "archive dir must carry the non-executable notice")

    def _check_user_level_duplicates(self, registry: dict[str, Any]) -> None:
        active_ids = self._active_ids(registry)
        for user_dir in self._user_skill_dirs():
            if not user_dir.is_dir():
                continue  # absent on CI / other machines: advisory only
            for skill_dir in sorted(user_dir.iterdir()):
                marker = skill_dir / "SKILL.md"
                if marker.is_file() and skill_dir.name in active_ids:
                    self._add("USER_LEVEL_DUPLICATE", str(marker),
                              f"user-level skill id {skill_dir.name!r} duplicates a "
                              "repo-local active skill; keep only a pointer")

    def _add(self, code: str, path: str, message: str) -> None:
        self._issues.append(SkillIssue(code, path, message))

    # -- operations -----------------------------------------------------------
    def inventory(self) -> dict[str, list[str]]:
        """On-disk skill ids grouped by location (repo canonical vs IDE stubs)."""
        found: dict[str, list[str]] = {"canonical": [], "pointer": [], "user": []}
        for base in CANONICAL_DIRS:
            found["canonical" if base == Path(".agents/skills") else "pointer"].extend(
                d.name for d in sorted((self.root / base).glob("*/SKILL.md")))
        for user_dir in self._user_skill_dirs():
            if user_dir.is_dir():
                found["user"].extend(d.name for d in sorted(user_dir.glob("*/SKILL.md")))
        return found

    def deprecate(self, skill_id: str, superseded_by: str, *, pointer_note: str) -> dict[str, str]:
        """Retire one skill: archive body -> pointer stub -> registry update.

        Returns the artifact paths for the audit trail. Raises KeyError when
        the id is unknown or already deprecated.
        """
        registry = self.load_registry()
        entry = next((s for s in self._skills(registry) if s["id"] == skill_id), None)
        if entry is None or entry.get("status") != "active":
            raise KeyError(f"unknown or non-active skill: {skill_id}")
        body = self.root / entry["canonical_path"]
        archive_dir = self.root / ARCHIVE_DIR
        archive_dir.mkdir(parents=True, exist_ok=True)
        history = archive_dir / f"{skill_id}-legacy.md"
        shutil.copyfile(body, history)

        stub = (
            "---\n"
            f"name: {skill_id}\n"
            f"description: Deprecated compatibility pointer. Route to {superseded_by}.\n"
            "status: deprecated\n"
            "---\n\n"
            "# 已废弃：仅作路由指针\n\n"
            f"{pointer_note}\n\n"
            f"原文完整保存在 `{history.as_posix()}`，仅供故障溯源，勿执行。\n"
        )
        body.write_text(stub, encoding="utf-8")

        entry["status"] = "deprecated"
        entry["superseded_by"] = superseded_by
        entry["history_path"] = history.relative_to(self.root).as_posix()
        self.registry_path.write_text(
            yaml.safe_dump(registry, allow_unicode=True, sort_keys=False),
            encoding="utf-8")
        return {"history": str(history), "pointer": str(body)}

    def sweep_markdown_links(self, text: str) -> list[str]:
        """Return markdown link targets that reference repo files gone missing."""
        targets = re.findall(r"\]\(([^)#\s]+)\)", text)
        broken = []
        for raw in targets:
            if re.match(r"^[a-z]+://", raw) or raw.startswith("<"):
                continue
            candidate = (self.root / raw.split("#")[0]).resolve()
            if not candidate.exists():
                broken.append(raw)
        return broken
