"""Govern active and quarantined research assets without deleting audit evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from config import settings


class AssetGovernance:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.DATA_DIR
        self.path = self.data_dir / "registry" / "quarantined_assets.yaml"
        self._payload = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"quarantined_ids": [], "repairs": []}
        payload = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        return payload if isinstance(payload, dict) else {}

    @property
    def quarantined_ids(self) -> set[str]:
        return {
            str(paper_id)
            for paper_id in self._payload.get("quarantined_ids", [])
            if paper_id
        }

    @property
    def repairs(self) -> list[dict[str, str]]:
        return [
            {str(key): str(value) for key, value in item.items()}
            for item in self._payload.get("repairs", [])
            if isinstance(item, dict)
        ]

    def is_quarantined(self, paper_id: str) -> bool:
        return str(paper_id) in self.quarantined_ids

    def filter_active(self, paper_ids: list[str]) -> list[str]:
        quarantined = self.quarantined_ids
        return [paper_id for paper_id in paper_ids if paper_id not in quarantined]
