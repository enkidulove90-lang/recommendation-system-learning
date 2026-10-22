from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from pydantic import ValidationError

from .article import PaperArticle, ReferenceChoice


def _key(kind: str, dimensions: dict[str, str]) -> str:
    payload = json.dumps(
        {"kind": kind, **dimensions},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class GenerationCache:
    def __init__(self, root: Path):
        self.root = Path(root)
        (self.root / "article").mkdir(parents=True, exist_ok=True)
        (self.root / "ranking").mkdir(parents=True, exist_ok=True)

    def _path(self, kind: str, dimensions: dict[str, str]) -> Path:
        return self.root / kind / f"{_key(kind, dimensions)}.json"

    @staticmethod
    def _read(path: Path) -> Any | None:
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _write(path: Path, payload: Any) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)

    def get_article(
        self, source_hash: str, model: str, prompt_version: str
    ) -> PaperArticle | None:
        dimensions = {
            "source_hash": source_hash,
            "model": model,
            "prompt_version": prompt_version,
        }
        payload = self._read(self._path("article", dimensions))
        if payload is None:
            return None
        try:
            return PaperArticle.model_validate(payload)
        except ValidationError:
            return None

    def put_article(
        self,
        source_hash: str,
        model: str,
        prompt_version: str,
        article: PaperArticle,
    ) -> None:
        dimensions = {
            "source_hash": source_hash,
            "model": model,
            "prompt_version": prompt_version,
        }
        self._write(self._path("article", dimensions), article.model_dump(mode="json"))

    def get_ranking(
        self,
        source_hash: str,
        candidate_hash: str,
        model: str,
        prompt_version: str,
        rule_version: str,
    ) -> list[ReferenceChoice] | None:
        dimensions = {
            "source_hash": source_hash,
            "candidate_hash": candidate_hash,
            "model": model,
            "prompt_version": prompt_version,
            "rule_version": rule_version,
        }
        payload = self._read(self._path("ranking", dimensions))
        if payload is None:
            return None
        try:
            return [ReferenceChoice.model_validate(item) for item in payload]
        except (ValidationError, TypeError):
            return None

    def put_ranking(
        self,
        source_hash: str,
        candidate_hash: str,
        model: str,
        prompt_version: str,
        rule_version: str,
        choices: Sequence[ReferenceChoice],
    ) -> None:
        dimensions = {
            "source_hash": source_hash,
            "candidate_hash": candidate_hash,
            "model": model,
            "prompt_version": prompt_version,
            "rule_version": rule_version,
        }
        self._write(
            self._path("ranking", dimensions),
            [choice.model_dump(mode="json") for choice in choices],
        )
