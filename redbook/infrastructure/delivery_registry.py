"""Durable per-paper record for draft-only delivery reconciliation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DeliveryRegistry:
    def __init__(self, data_root: Path, slug: str) -> None:
        self.path = data_root / "workflow_state" / slug / "delivery_registry.json"
        self.slug = slug

    def _read(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {"slug": self.slug, "runs": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, value: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.path)

    def _record(self, status: str, run_id: str, staged_id: str, draft_id: str, verification: dict[str, Any]) -> None:
        value = self._read()
        value["runs"].append({"run_id": run_id, "staged_id": staged_id, "draft_id": draft_id,
                              "status": status, "verification": verification})
        self._write(value)

    def record_verified(self, run_id: str, staged_id: str, draft_id: str, verification: dict[str, Any]) -> None:
        self._record("verify_passed", run_id, staged_id, draft_id, verification)

    def record_orphan(self, run_id: str, staged_id: str, draft_id: str, verification: dict[str, Any]) -> None:
        self._record("orphan", run_id, staged_id, draft_id, verification)

    def find_verified(self, staged_id: str) -> dict[str, Any] | None:
        for run in reversed(self._read()["runs"]):
            if run["staged_id"] == staged_id and run["status"] == "verify_passed":
                return run
        return None
