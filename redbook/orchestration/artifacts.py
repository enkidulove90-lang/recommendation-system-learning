"""Content-hash artifact registry: the reuse layer for pipeline stages.

Each stage (crawl/parse/summarize/compose) records ``input digest -> product
paths`` once. Re-running the same stage on the same input hits the registry
instead of calling MinerU/DeepSeek again -- the C-2 computation-reuse
semantics that later maps 1:1 onto a cache backend (the digest becomes the
cache key, the registry becomes a cache-aside store).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: str | Path) -> str:
    sha = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            sha.update(chunk)
    return sha.hexdigest()


class ArtifactStore:
    """Append-only JSONL registry; last row per (stage, input_hash) wins."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def find(self, stage: str, input_hash: str) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        hit = None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("stage") == stage and record.get("input_hash") == input_hash:
                hit = record
        return hit

    def register(self, stage: str, input_hash: str, *,
                 outputs: dict[str, str], source: str = "") -> dict[str, Any]:
        record = {
            "stage": stage, "input_hash": input_hash,
            "outputs": dict(outputs), "source": source,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record
