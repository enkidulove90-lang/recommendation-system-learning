"""Worktree lifecycle management: audit, gate-guarded removal, archiving.

Repo-wide ops tool. Read-only by default; destructive operations are
gate-guarded (dirty trees and unpushed work are always refused unless the
caller passes ``force``; orphan directories are archived (moved), never
deleted, by this module).

CLI::

    python -m redbook.services.worktree_manager audit [--json]
    python -m redbook.services.worktree_manager remove <name> --confirm
    python -m redbook.services.worktree_manager archive <name> [--dest DIR]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from redbook.infrastructure.run_log import log_event

ARCHIVE_ROOT = "archive/worktree_history"


@dataclass
class WorktreeStatus:
    """One worktree (or orphan directory) and its lifecycle flags."""

    name: str
    path: str
    kind: str  # "registered" | "orphan"
    branch: str | None = None
    head: str | None = None
    detached: bool = False
    uncommitted: int = 0
    unpushed: int | None = None  # None = no upstream branch
    upstream: str | None = None
    size_mb: float | None = None
    flags: list[str] = field(default_factory=list)
    contained_elsewhere: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name, "path": self.path, "kind": self.kind,
            "branch": self.branch, "head": self.head, "detached": self.detached,
            "uncommitted": self.uncommitted, "unpushed": self.unpushed,
            "upstream": self.upstream, "size_mb": self.size_mb,
            "flags": self.flags,
            "contained_elsewhere": self.contained_elsewhere,
        }

    @property
    def removable(self) -> bool:
        """True when nothing would be lost by removing the worktree directory.

        For registered trees: clean AND every commit already on its upstream
        (or the head is contained in some other branch).  Orphans never count
        as removable here — they go through :meth:`archive` instead.
        """
        if self.kind == "orphan":
            return False
        no_loss = self.uncommitted == 0 and (
            (self.unpushed is not None and self.unpushed == 0)
            or self.contained_elsewhere
        )
        return no_loss


def _git(repo: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=str(cwd or repo), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    )


class WorktreeManager:
    """Audit and manage git worktrees plus orphan snapshot directories."""

    def __init__(self, repo_root: Path, *, worktree_root: Path | None = None,
                 external_roots: list[Path] | None = None) -> None:
        self.root = Path(repo_root).resolve()
        self.worktree_root = worktree_root or self.root / ".worktrees"
        self.external_roots = external_roots or []

    # ---------------------------------------------------------------- audit

    def audit(self) -> list[WorktreeStatus]:
        registered = self._registered()
        statuses: list[WorktreeStatus] = []
        tips: dict[str, list[str]] = {}
        for entry in registered:
            status = self._inspect(entry)
            if status.head:
                tips.setdefault(status.head, []).append(status.name)
            statuses.append(status)
        for status in statuses:
            if len(tips.get(status.head or "", [])) > 1:
                status.flags.append("DUPLICATE_TIP")
            if status.removable:
                status.flags.append("REMOVABLE")
        for orphan_dir in self._orphan_dirs(registered):
            statuses.append(self._inspect_orphan(orphan_dir))
        return statuses

    def _registered(self) -> list[dict[str, str]]:
        proc = _git(self.root, "worktree", "list", "--porcelain")
        if proc.returncode != 0:
            raise RuntimeError(f"git worktree list failed: {proc.stderr.strip()}")
        entries: list[dict[str, str]] = []
        current: dict[str, str] = {}
        for line in proc.stdout.splitlines():
            if not line.strip():
                if current:
                    entries.append(current)
                current = {}
                continue
            key, _, value = line.partition(" ")
            if key == "worktree":
                current = {"path": value}
            else:
                current[key] = value
        if current:
            entries.append(current)
        return entries

    def _inspect(self, entry: dict[str, str]) -> WorktreeStatus:
        path = Path(entry["path"])
        name = path.name if path.parent != self.root else self.root.name
        branch = entry.get("branch", "").removeprefix("refs/heads/") or None
        head = entry.get("HEAD") or None
        detached = "detached" in entry
        status = WorktreeStatus(name=name, path=str(path), kind="registered",
                                branch=branch, head=head, detached=detached)
        if branch:
            proc = _git(self.root, "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}")
            if proc.returncode == 0:
                status.upstream = proc.stdout.strip() or None
                ahead = _git(self.root, "rev-list", "--count", f"{status.upstream}..{branch}")
                status.unpushed = int(ahead.stdout.strip() or 0)
            else:
                status.unpushed = None
                # unpushed commits may still exist if the branch is contained
                # in another local branch; audit() marks those REMOVABLE only
                # when containment is proven below.
                status.flags.append("NO_UPSTREAM")
                if head and self._head_contained(head, branch):
                    status.contained_elsewhere = True
        elif head:
            status.contained_elsewhere = self._head_contained(head, "")
        dirty = _git(self.root, "status", "--porcelain", cwd=path)
        status.uncommitted = sum(
            1 for line in dirty.stdout.splitlines() if line.strip()
        )
        if status.uncommitted:
            status.flags.append("DIRTY")
        if detached:
            status.flags.append("DETACHED")
        if status.unpushed:
            status.flags.append("UNPUSHED")
        return status

    def _head_contained(self, head: str, exclude_branch: str) -> bool:
        proc = _git(self.root, "branch", "--contains", head, "--format=%(refname:short)")
        if proc.returncode != 0:
            return False
        return any(
            line.strip() and line.strip() != exclude_branch
            for line in proc.stdout.splitlines()
        )

    def _orphan_dirs(self, registered: list[dict[str, str]]) -> list[Path]:
        known = {Path(e["path"]).resolve() for e in registered}
        known.add(self.root)
        orphans: list[Path] = []
        for root in [self.worktree_root, *self.external_roots]:
            if not root.is_dir():
                continue
            for child in sorted(root.iterdir()):
                if child.is_dir() and child.resolve() not in known \
                        and not (child / ".git").exists():
                    orphans.append(child)
        return orphans

    def _inspect_orphan(self, path: Path) -> WorktreeStatus:
        name = path.name
        status = WorktreeStatus(name=name, path=str(path), kind="orphan")
        status.flags.append("ORPHAN_DIR")
        file_count = sum(1 for _ in path.rglob("*") if _.is_file())
        status.size_mb = round(
            sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1_048_576, 1,
        ) if file_count else 0.0
        status.uncommitted = file_count
        if self._orphan_is_redundant(path):
            status.flags.append("REDUNDANT_COPY")
        return status

    def _orphan_is_redundant(self, path: Path) -> bool:
        """Heuristic: every data PDF basename in the orphan also exists in the
        main repo data tree (bounded check — code files are assumed git-tracked
        lineage snapshots, which the audit report states explicitly)."""
        main_data = self.root / "data"
        if not main_data.is_dir():
            return False
        main_pdfs = {f.name for f in main_data.rglob("*.pdf")}
        orphan_pdfs = list(path.glob("data/**/*.pdf"))
        if not orphan_pdfs:
            return False
        return all(f.name in main_pdfs for f in orphan_pdfs)

    # --------------------------------------------------------------- mutate

    def remove(self, name: str, *, confirm: bool = False, force: bool = False) -> dict[str, object]:
        """``git worktree remove`` with explicit safety gates.

        Refuses when the tree is dirty or has unpushed work unless ``force``;
        requires ``confirm`` regardless.  Orphans are refused — use
        :meth:`archive` (move) instead of deleting an unregistered snapshot.
        """
        statuses = {s.name: s for s in self.audit()}
        status = statuses.get(name)
        if status is None:
            raise ValueError(f"unknown worktree: {name}")
        if status.kind == "orphan":
            raise ValueError("orphan directory: use archive(), never delete")
        if not confirm:
            raise ValueError("confirmation required: pass confirm=True / --confirm")
        blockers = [f for f in ("DIRTY", "UNPUSHED") if f in status.flags]
        if blockers and not force:
            raise ValueError(f"refused: {name} has {blockers}; pass force=True only "
                             "after the work has been committed or pushed")
        proc = _git(self.root, "worktree", "remove", status.path)
        log_event("worktree.remove", component="worktree_manager", state="ok" if proc.returncode == 0 else "failed",
                  detail={"name": name, "stderr": proc.stderr.strip()})
        if proc.returncode != 0:
            raise RuntimeError(f"git worktree remove failed: {proc.stderr.strip()}")
        return {"removed": status.path, "flags_before": status.flags}

    def archive(self, name: str, *, dest: Path | None = None) -> dict[str, object]:
        """Move an orphan snapshot directory into ``archive/worktree_history``.

        Archiving is a rename on the same volume — no data is deleted, so no
        confirmation prompt is needed beyond invoking the method itself.
        """
        statuses = {s.name: s for s in self.audit()}
        status = statuses.get(name)
        if status is None or status.kind != "orphan":
            raise ValueError(f"not an orphan directory: {name!r}")
        dest_dir = Path(dest) if dest else self.root / ARCHIVE_ROOT
        dest_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        target = dest_dir / f"{status.name}-{stamp}"
        if target.exists():
            raise FileExistsError(f"archive target already exists: {target}")
        shutil.move(status.path, str(target))
        log_event("worktree.archive", component="worktree_manager", state="ok",
                  detail={"from": status.path, "to": str(target),
                          "size_mb": status.size_mb, "flags": status.flags})
        return {"archived_to": str(target), "size_mb": status.size_mb,
                "flags": status.flags}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser("worktree_manager")
    parser.add_argument("--repo", default=".", help="repository root")
    sub = parser.add_subparsers(dest="command", required=True)
    audit_p = sub.add_parser("audit")
    audit_p.add_argument("--json", action="store_true")
    rm = sub.add_parser("remove")
    rm.add_argument("name")
    rm.add_argument("--confirm", action="store_true")
    rm.add_argument("--force", action="store_true")
    arch = sub.add_parser("archive")
    arch.add_argument("name")
    arch.add_argument("--dest", default=None)
    args = parser.parse_args(argv)

    manager = WorktreeManager(Path(args.repo).resolve())
    if args.command == "audit":
        statuses = manager.audit()
        if args.json:
            print(json.dumps([s.to_dict() for s in statuses], ensure_ascii=False, indent=2))
        else:
            for s in statuses:
                branch = s.branch or ("(detached)" if s.detached else "-")
                print(f"{s.name:34s} [{branch}] kind={s.kind} uncommitted={s.uncommitted} "
                      f"unpushed={s.unpushed} flags={','.join(s.flags) or '-'}")
        return 0
    if args.command == "remove":
        result = manager.remove(args.name, confirm=args.confirm, force=args.force)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    result = manager.archive(args.name, dest=Path(args.dest) if args.dest else None)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
