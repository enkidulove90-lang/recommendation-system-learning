"""Content asset manifest: authoritative index of derived artifacts.

Storage contract (hard rule): SQLite stores ONLY relative paths, content
hashes and metadata.  Markdown bodies and large JSON never enter the DB.
Every path handed to :meth:`record` is converted with ``relative_to(ROOT)``.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ContentAssetManifest:
    """Idempotent lookup/record over the ``content_assets`` table."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def lookup(
        self,
        canonical_id: str,
        purpose: str,
        source_hash: str,
        prompt_version: str,
        model_id: str,
    ) -> dict[str, Any] | None:
        """Return the matching asset only when the full idempotency key matches.

        The key is (canonical_id, purpose/asset_kind, source_hash,
        prompt_version, model_id).  A changed source hash, prompt version or
        model id intentionally misses so a fresh generation is produced.
        """
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT canonical_id, asset_kind, asset_key, relative_path, "
                "       content_hash, producer, prompt_version, model_id, "
                "       source_hash, created_at, updated_at "
                "FROM content_assets "
                "WHERE canonical_id=? AND asset_kind=? AND source_hash=? "
                "  AND prompt_version=? AND model_id=?",
                (canonical_id, purpose, source_hash, prompt_version, model_id),
            ).fetchone()
        return dict(row) if row is not None else None

    def record(
        self,
        canonical_id: str,
        purpose: str,
        relative_path: Path,
        source_hash: str,
        prompt_version: str,
        model_id: str,
        producer: str,
    ) -> None:
        """Upsert an asset row.  ``relative_path`` is normalised to a ROOT-relative
        POSIX string before it touches SQLite."""
        path = Path(relative_path)
        if path.is_absolute():
            relative = path.resolve().relative_to(ROOT)
        else:
            # Already relative: normalise and re-verify it stays inside ROOT.
            relative = (ROOT / path).resolve().relative_to(ROOT)
        relative_str = relative.as_posix()

        target = ROOT / relative
        if not target.is_file():
            raise FileNotFoundError(f"asset file does not exist: {target}")
        content_hash = _file_sha256(target)
        timestamp = _now()
        statement = (
            "INSERT INTO content_assets ("
            "  canonical_id, asset_kind, asset_key, relative_path, content_hash, "
            "  producer, prompt_version, model_id, source_hash, created_at, updated_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(canonical_id, asset_kind, asset_key) DO UPDATE SET "
            "  relative_path=excluded.relative_path, "
            "  content_hash=excluded.content_hash, "
            "  producer=excluded.producer, "
            "  prompt_version=excluded.prompt_version, "
            "  model_id=excluded.model_id, "
            "  source_hash=excluded.source_hash, "
            "  updated_at=excluded.updated_at"
        )
        parameters = (
            canonical_id, purpose, purpose, relative_str, content_hash,
            producer, prompt_version, model_id, source_hash,
            timestamp, timestamp,
        )
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(statement, parameters)


def _file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
