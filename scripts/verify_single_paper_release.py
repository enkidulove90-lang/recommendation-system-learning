from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.reprocess_single_paper import ReleasePlan


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_allowed_changes(
    before: dict[str, str], after: dict[str, str], allowed_paths: list[str]
) -> list[str]:
    allowed = {str(Path(path).resolve()) for path in allowed_paths}
    unexpected: list[str] = []
    for path in sorted(set(before) | set(after)):
        comparable = str(Path(path).resolve()) if Path(path).is_absolute() else path
        if before.get(path) != after.get(path) and comparable not in allowed:
            unexpected.append(path)
    return unexpected


def restore_release(plan: ReleasePlan, *, notion) -> dict[str, str]:
    source_backup = Path(plan.site_backup_path).read_bytes()
    notion_backup = Path(plan.notion_backup_path).read_bytes()
    if _sha256(source_backup) != plan.site_source_sha256:
        raise ValueError("site backup hash does not match release plan")
    if _sha256(notion_backup) != plan.notion_backup_sha256:
        raise ValueError("Notion backup hash does not match release plan")
    Path(plan.site_source_path).write_bytes(source_backup)
    notion.restore(plan.notion_page_id, notion_backup)
    return {
        "site_source_sha256": _sha256(Path(plan.site_source_path).read_bytes()),
        "notion_backup_sha256": _sha256(notion_backup),
    }
