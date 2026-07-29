"""Load controlled taxonomies and verified dataset aliases."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from config import settings


class KnowledgeRegistry:
    def __init__(self, registry_dir: Path | None = None) -> None:
        self.registry_dir = registry_dir or settings.DATA_DIR / "registry"
        self.taxonomies = self._load_yaml(self.registry_dir / "taxonomies.yaml")
        self.datasets = self._load_yaml(self.registry_dir / "datasets.yaml")

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}

    def allowed_tags(self, dimension: str) -> set[str]:
        values = self.taxonomies.get(dimension, {})
        return set(values) if isinstance(values, dict) else set()

    def classify(self, text: str, dimension: str) -> list[str]:
        normalized = text.casefold()
        values = self.taxonomies.get(dimension, {})
        if not isinstance(values, dict):
            return []

        matches: list[str] = []
        for canonical, config in values.items():
            aliases = config.get("aliases", []) if isinstance(config, dict) else []
            if any(self._contains_alias(normalized, str(alias).casefold()) for alias in aliases):
                matches.append(str(canonical))
        return matches

    @staticmethod
    def _contains_alias(text: str, alias: str) -> bool:
        if not alias:
            return False
        if len(alias) <= 3 and alias.isascii():
            return bool(re.search(rf"\b{re.escape(alias)}\b", text, flags=re.IGNORECASE))
        return alias in text

    def resolve_dataset(self, paper_name: str) -> str | None:
        normalized = paper_name.casefold().strip()
        entries = self.datasets.get("datasets", {})
        if not isinstance(entries, dict):
            return None
        for registry_id, config in entries.items():
            if not isinstance(config, dict):
                continue
            names = [config.get("canonical_name", ""), *config.get("aliases", [])]
            if any(normalized == str(name).casefold().strip() for name in names if name):
                return str(registry_id)
        return None
