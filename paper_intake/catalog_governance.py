"""SQLite catalog identity and per-platform admission; JSON is import-only.

The outbox is an event boundary. This module does not create delivery jobs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Iterable
from urllib.parse import urlparse

from .catalog import CatalogTransport, RequestsCatalogTransport, parse_arxiv_feed


_PLATFORMS = frozenset({"homepage", "xiaohongshu", "wechat"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _title(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


@dataclass(frozen=True)
class IdentityEvidence:
    title: str
    authors: tuple[str, ...]
    paper_url: str
    published_at: str
    authority: str
    evidence_url: str
    arxiv_id: str = ""
    doi: str = ""


class CatalogGovernance:
    """One SQLite truth source for discovery and admission decisions."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS catalog_papers (
                    catalog_id TEXT PRIMARY KEY, source TEXT NOT NULL,
                    source_id TEXT NOT NULL, title TEXT NOT NULL,
                    source_url TEXT NOT NULL, venue_name TEXT NOT NULL,
                    venue_type TEXT NOT NULL, publication_year INTEGER NOT NULL,
                    track TEXT NOT NULL, topic_signals_json TEXT NOT NULL,
                    identity_state TEXT NOT NULL DEFAULT 'unresolved',
                    canonical_id TEXT, paper_url TEXT, authors_json TEXT,
                    published_at TEXT, authority TEXT, evidence_url TEXT,
                    first_seen_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(source, source_id)
                );
                CREATE TABLE IF NOT EXISTS catalog_admissions (
                    catalog_id TEXT NOT NULL, platform TEXT NOT NULL,
                    state TEXT NOT NULL, reason TEXT NOT NULL,
                    decided_at TEXT NOT NULL,
                    PRIMARY KEY(catalog_id, platform)
                );
                CREATE TABLE IF NOT EXISTS catalog_outbox (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL, catalog_id TEXT NOT NULL,
                    platform TEXT NOT NULL, payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL, consumed_at TEXT
                );
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def import_snapshot(self, path: str | Path) -> int:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or not isinstance(payload.get("papers"), list):
            raise ValueError("unsupported catalog snapshot")
        return self.import_records(payload["papers"])

    def import_records(self, records: Iterable[dict[str, Any]]) -> int:
        added = 0
        with self._connect() as db:
            for row in records:
                source, source_id = str(row.get("source", "")).strip(), str(row.get("source_id", "")).strip()
                title = str(row.get("title", "")).strip()
                if not source or not source_id or not title:
                    continue
                signals = {"values": row.get("topics", []), "source": row.get("topic_source", "unavailable")}
                result = db.execute("""
                    INSERT INTO catalog_papers
                    (catalog_id, source, source_id, title, source_url, venue_name,
                     venue_type, publication_year, track, topic_signals_json,
                     first_seen_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, source_id) DO NOTHING
                """, (f"{source}:{source_id}", source, source_id, title,
                      str(row.get("paper_url", "")), str(row.get("venue_name", "")),
                      str(row.get("venue_type", "")), int(row.get("publication_year") or 0),
                      str(row.get("track", "")), json.dumps(signals, ensure_ascii=False),
                      _now(), _now()))
                added += result.rowcount
        return added

    def get(self, catalog_id: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM catalog_papers WHERE catalog_id=?", (catalog_id,)).fetchone()
        if row is None:
            raise KeyError(catalog_id)
        return dict(row)

    def verify_identity(self, catalog_id: str, evidence: IdentityEvidence) -> None:
        paper = self.get(catalog_id)
        if _title(evidence.title) != _title(paper["title"]):
            raise ValueError("title mismatch")
        if not evidence.authors or not evidence.published_at or not evidence.evidence_url:
            raise ValueError("incomplete authority evidence")
        evidence_host = urlparse(evidence.evidence_url)
        expected_host = {"arxiv": "export.arxiv.org", "crossref": "api.crossref.org",
                         "acl_anthology": "aclanthology.org"}.get(evidence.authority)
        if (expected_host is None or evidence_host.scheme != "https"
                or evidence_host.netloc != expected_host):
            raise ValueError("untrusted authority evidence URL")
        if paper["source"] == "arxiv" and paper["source_id"] != evidence.arxiv_id:
            raise ValueError("arxiv source identity mismatch")
        url = urlparse(evidence.paper_url)
        arxiv_ok = (evidence.authority == "arxiv" and evidence.arxiv_id
                    and url.scheme == "https" and url.netloc == "arxiv.org"
                    and url.path == f"/abs/{evidence.arxiv_id}"
                    and re.fullmatch(r"\d{4}\.\d{4,5}", evidence.arxiv_id))
        doi_ok = (evidence.authority == "crossref" and evidence.doi
                  and url.scheme == "https" and url.netloc == "doi.org"
                  and url.path == f"/{evidence.doi}")
        acl_ok = (evidence.authority == "acl_anthology"
                  and paper["source"] == "acl_anthology"
                  and url.scheme == "https" and url.netloc == "aclanthology.org"
                  and url.path.strip("/") == paper["source_id"])
        if not (arxiv_ok or doi_ok or acl_ok):
            raise ValueError("canonical paper URL is not verified")
        canonical_id = (f"doi:{evidence.doi.casefold()}" if evidence.doi else
                        f"arxiv:{evidence.arxiv_id}" if evidence.arxiv_id else
                        f"acl:{paper['source_id']}")
        with self._connect() as db:
            conflict = db.execute(
                "SELECT catalog_id FROM catalog_papers WHERE canonical_id=? AND catalog_id<>?",
                (canonical_id, catalog_id)).fetchone()
            if conflict:
                raise ValueError("canonical identity conflict")
            db.execute("""UPDATE catalog_papers SET identity_state='identity_verified',
                canonical_id=?, paper_url=?, authors_json=?, published_at=?, authority=?,
                evidence_url=?, updated_at=? WHERE catalog_id=?""",
                (canonical_id, evidence.paper_url, json.dumps(evidence.authors),
                 evidence.published_at, evidence.authority, evidence.evidence_url,
                 _now(), catalog_id))

    def verify_arxiv_id(self, catalog_id: str, arxiv_id: str, *,
                        transport: CatalogTransport | None = None) -> None:
        """Resolve one proposed arXiv ID against the official Atom record.

        A site article or meeting agenda may suggest an ID, but neither is
        treated as evidence until the official response matches the title.
        """
        if not re.fullmatch(r"\d{4}\.\d{4,5}", arxiv_id):
            raise ValueError("invalid arxiv id")
        client = transport or RequestsCatalogTransport()
        response_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        records = parse_arxiv_feed(client.get_text(response_url))
        matches = [item for item in records if item.arxiv_id == arxiv_id]
        if len(matches) != 1:
            raise ValueError("arxiv identity unresolved")
        record = matches[0]
        self.verify_identity(catalog_id, IdentityEvidence(
            title=record.title, authors=tuple(record.authors),
            paper_url=record.paper_url, published_at=record.published_at,
            authority="arxiv", evidence_url=response_url, arxiv_id=arxiv_id))

    def admit(self, catalog_id: str, platform: str, *, topic_match: bool,
              code_verified: bool = False) -> str:
        if platform not in _PLATFORMS:
            raise ValueError("unknown platform")
        paper = self.get(catalog_id)
        if paper["identity_state"] != "identity_verified":
            raise ValueError("identity_verified required before admission")
        reason = ("topic_out_of_scope" if not topic_match else
                  "official_code_unverified" if platform == "xiaohongshu" and not code_verified
                  else "verified")
        state = "eligible" if reason == "verified" else "deferred"
        with self._connect() as db:
            db.execute("""INSERT INTO catalog_admissions
                (catalog_id, platform, state, reason, decided_at) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(catalog_id, platform) DO UPDATE SET
                state=excluded.state, reason=excluded.reason, decided_at=excluded.decided_at""",
                (catalog_id, platform, state, reason, _now()))
            if state == "eligible":
                operation_id = f"catalog-admission-v1:{catalog_id}:{platform}"
                payload = {"event_version": 1, "catalog_id": catalog_id,
                           "canonical_id": paper["canonical_id"], "platform": platform,
                           "paper_url": paper["paper_url"],
                           "action": "publish" if platform == "homepage" else "save_draft"}
                db.execute("""INSERT INTO catalog_outbox
                    (operation_id, event_type, catalog_id, platform, payload_json, created_at)
                    VALUES (?, 'PaperEligible', ?, ?, ?, ?)
                    ON CONFLICT(operation_id) DO NOTHING""",
                    (operation_id, catalog_id, platform, json.dumps(payload), _now()))
        return state

    def pending_events(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM catalog_outbox WHERE consumed_at IS NULL ORDER BY id").fetchall()
        return [dict(row) for row in rows]
