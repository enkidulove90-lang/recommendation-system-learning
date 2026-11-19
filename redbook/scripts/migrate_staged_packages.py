"""Migrate legacy 32-hex publish-queue directories to full staged IDs."""
from __future__ import annotations

import json
from pathlib import Path


def migrate(queue_root: Path, *, apply: bool = False) -> dict[str, int]:
    migrated = skipped = 0
    for entry in queue_root.iterdir() if queue_root.is_dir() else ():
        if not entry.is_dir() or len(entry.name) != 32:
            continue
        packages = list(entry.glob("*.json"))
        if not packages:
            skipped += 1
            continue
        data = json.loads(packages[0].read_text(encoding="utf-8"))
        staged_id = str(data.get("content_hash", ""))
        if len(staged_id) != 64 or not staged_id.startswith(entry.name):
            skipped += 1
            continue
        target = queue_root / staged_id
        if target.exists():
            skipped += 1
        elif apply:
            entry.replace(target)
            migrated += 1
    return {"migrated": migrated, "skipped": skipped}
