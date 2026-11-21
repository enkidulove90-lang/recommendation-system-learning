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

import yaml

from .catalog import CatalogTransport, RequestsCatalogTransport, parse_arxiv_feed


_DEFAULT_RULES = Path(__file__).resolve().parents[1] / "config" / "catalog_governance.yaml"


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

    def __init__(self, path: str | Path, *, config_path: str | Path | None = None) -> None:
        self.path = Path(path)
        self.config_path = Path(config_path) if config_path else _DEFAULT_RULES
        self.rules = self._load_rules()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS catalog_papers (
                    catalog_id TEXT PRIMARY KEY, source TEXT NOT NULL,
                    source_id TEXT NOT NULL, title TEXT NOT NULL,
                    source_url TEXT NOT NULL, venue_name TEXT NOT NULL,
                    venue_type TEXT NOT NULL, publication_year INTEGER NOT NULL,
                    track TEXT NOT NULL, topic_signals_json TEXT NOT NULL,
                    source_authors_json TEXT NOT NULL DEFAULT '[]',
                    identity_state TEXT NOT NULL DEFAULT 'unresolved',
                    canonical_id TEXT, paper_url TEXT, authors_json TEXT,
                    published_at TEXT, authority TEXT, evidence_url TEXT,
                    first_seen_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(source, source_id)
                );
                CREATE TABLE IF NOT EXISTS catalog_admissions (
                    catalog_id TEXT NOT NULL, platform TEXT NOT NULL,
                    state TEXT NOT NULL, reason TEXT NOT NULL,
                    evidence_json TEXT NOT NULL DEFAULT '{}',
                    decided_at TEXT NOT NULL,
                    PRIMARY KEY(catalog_id, platform)
                );
                CREATE TABLE IF NOT EXISTS catalog_outbox (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL, catalog_id TEXT NOT NULL,
                    platform TEXT NOT NULL, payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL, consumed_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_visible_at TEXT NOT NULL DEFAULT '',
                    dead_letter_reason TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS catalog_evidence_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    catalog_id TEXT NOT NULL, kind TEXT NOT NULL,
                    verdict TEXT NOT NULL, evidence_json TEXT NOT NULL,
                    decided_at TEXT NOT NULL
                );
            """)
            columns = {row[1] for row in db.execute("PRAGMA table_info(catalog_papers)")}
            if "source_authors_json" not in columns:
                db.execute("ALTER TABLE catalog_papers ADD COLUMN source_authors_json TEXT NOT NULL DEFAULT '[]'")
            admission_columns = {row[1] for row in db.execute("PRAGMA table_info(catalog_admissions)")}
            if "evidence_json" not in admission_columns:
                db.execute("ALTER TABLE catalog_admissions ADD COLUMN evidence_json TEXT NOT NULL DEFAULT '{}'")
            outbox_columns = {row[1] for row in db.execute("PRAGMA table_info(catalog_outbox)")}
            for name, ddl in (("attempts", "INTEGER NOT NULL DEFAULT 0"),
                              ("next_visible_at", "TEXT NOT NULL DEFAULT ''"),
                              ("dead_letter_reason", "TEXT NOT NULL DEFAULT ''")):
                if name not in outbox_columns:
                    db.execute(f"ALTER TABLE catalog_outbox ADD COLUMN {name} {ddl}")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=5000")
        return db

    def _load_rules(self) -> dict[str, Any]:
        if not self.config_path.is_file():
            raise FileNotFoundError(f"catalog governance config missing: {self.config_path}")
        rules = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
        required = {"authorities", "author_crosscheck", "per_platform_code_requirement", "platforms"}
        if not isinstance(rules, dict) or not required.issubset(rules):
            raise ValueError("invalid catalog governance configuration")
        return rules

    @staticmethod
    def _append_evidence(db: sqlite3.Connection, catalog_id: str, kind: str,
                         verdict: str, evidence: dict[str, Any]) -> None:
        db.execute("INSERT INTO catalog_evidence_log(catalog_id,kind,verdict,evidence_json,decided_at) VALUES(?,?,?,?,?)",
                   (catalog_id, kind, verdict, json.dumps(evidence, ensure_ascii=False), _now()))

    def get_by_identity(self, canonical_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM catalog_papers WHERE canonical_id=?", (canonical_id,)).fetchone()
        return dict(row) if row else None

    def update_enrichment(self, catalog_id: str, fields: dict[str, Any]) -> None:
        allowed = {"title_zh", "github_url", "project_url", "citation_count"}
        if not fields or set(fields) - allowed:
            raise ValueError("enrichment fields must be a non-empty subset of the allowed fields")
        # Store derived values in a separate JSON column, never mutate identity.
        with self._connect() as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(catalog_papers)")}
            if "enrichment_json" not in columns:
                db.execute("ALTER TABLE catalog_papers ADD COLUMN enrichment_json TEXT NOT NULL DEFAULT '{}'")
            row = db.execute("SELECT enrichment_json FROM catalog_papers WHERE catalog_id=?", (catalog_id,)).fetchone()
            if row is None:
                raise KeyError(catalog_id)
            merged = json.loads(row["enrichment_json"] or "{}") | fields
            db.execute("UPDATE catalog_papers SET enrichment_json=?,updated_at=? WHERE catalog_id=?",
                       (json.dumps(merged, ensure_ascii=False), _now(), catalog_id))
            self._append_evidence(db, catalog_id, "enrichment", "updated", fields)

    def block(self, catalog_id: str, platform: str, reason: str, evidence: dict[str, Any]) -> None:
        if platform not in self.rules["platforms"] or not reason.strip():
            raise ValueError("valid platform and reason required")
        with self._connect() as db:
            existing = db.execute("SELECT state FROM catalog_admissions WHERE catalog_id=? AND platform=?",
                                  (catalog_id, platform)).fetchone()
            if existing is None or existing["state"] != "deferred":
                raise ValueError("manual block is only allowed from deferred")
            db.execute("UPDATE catalog_admissions SET state='blocked',reason=?,evidence_json=?,decided_at=? WHERE catalog_id=? AND platform=?",
                       (reason, json.dumps(evidence, ensure_ascii=False), _now(), catalog_id, platform))
            self._append_evidence(db, catalog_id, "admission", "blocked", {"platform": platform, "reason": reason, **evidence})

    def mark_conflict(self, catalog_id: str, against: str, evidence: dict[str, Any]) -> None:
        with self._connect() as db:
            result = db.execute("UPDATE catalog_papers SET identity_state='conflict',updated_at=? WHERE catalog_id=? AND identity_state='unresolved'", (_now(), catalog_id))
            if result.rowcount == 0:
                exists = db.execute("SELECT 1 FROM catalog_papers WHERE catalog_id=?", (catalog_id,)).fetchone()
                if exists:
                    raise ValueError("identity is already resolved; conflict transition refused")
                raise KeyError(catalog_id)
            self._append_evidence(db, catalog_id, "identity", "conflict", {"against": against, **evidence})

    def mark_consumed(self, event_id: int, *, connection: sqlite3.Connection | None = None) -> None:
        if connection is not None:
            connection.execute("UPDATE catalog_outbox SET consumed_at=? WHERE id=? AND consumed_at IS NULL", (_now(), event_id))
            return
        with self._connect() as db:
            db.execute("UPDATE catalog_outbox SET consumed_at=? WHERE id=? AND consumed_at IS NULL", (_now(), event_id))

    def governance_report(self, *, unresolved_days: int = 7) -> dict[str, Any]:
        cutoff = (datetime.now(timezone.utc).timestamp() - unresolved_days * 86400)
        with self._connect() as db:
            unresolved = [dict(row) for row in db.execute("SELECT catalog_id,title,updated_at FROM catalog_papers WHERE identity_state='unresolved'")]
            deferred = [dict(row) for row in db.execute("SELECT catalog_id,platform,reason,decided_at FROM catalog_admissions WHERE state='deferred'")]
            conflicts = [dict(row) for row in db.execute("SELECT catalog_id,title,updated_at FROM catalog_papers WHERE identity_state='conflict'")]
        def old(row):
            try: return datetime.fromisoformat(row["updated_at"]).timestamp() <= cutoff
            except (ValueError, TypeError): return False
        return {"unresolved_count": len(unresolved), "unresolved_overdue": [row for row in unresolved if old(row)],
                "deferred": deferred, "conflicts": conflicts}

    def evidence_history(self, catalog_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM catalog_evidence_log WHERE catalog_id=? ORDER BY id", (catalog_id,))]

    def sync_pool(self, pool: Any) -> int:
        """Send catalog snapshots to a narrow pool adapter; never imports redbook."""
        with self._connect() as db:
            rows = [dict(row) for row in db.execute("SELECT * FROM catalog_papers ORDER BY updated_at,catalog_id")]
            admissions = [dict(row) for row in db.execute("SELECT * FROM catalog_admissions")]
        by_catalog: dict[str, dict[str, Any]] = {}
        for item in admissions:
            by_catalog.setdefault(item["catalog_id"], {})[item["platform"]] = {
                "state": item["state"], "reason": item["reason"]}
        for row in rows:
            if not row.get("canonical_id"):
                continue
            enrichment = json.loads(row.get("enrichment_json") or "{}")
            row["title_zh"] = enrichment.get("title_zh", "")
            row["github_url"] = enrichment.get("github_url", "")
            row["admission"] = by_catalog.get(row["catalog_id"], {})
        return int(pool.sync_catalog_snapshots(rows))

    def import_snapshot(self, path: str | Path) -> int:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") not in {1, 2} or not isinstance(payload.get("papers"), list):
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
                     venue_type, publication_year, track, topic_signals_json, source_authors_json,
                     first_seen_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, source_id) DO NOTHING
                """, (f"{source}:{source_id}", source, source_id, title,
                      str(row.get("paper_url", "")), str(row.get("venue_name", "")),
                      str(row.get("venue_type", "")), int(row.get("publication_year") or 0),
                      str(row.get("track", "")), json.dumps(signals, ensure_ascii=False),
                      json.dumps(row.get("authors", []), ensure_ascii=False),
                      _now(), _now()))
                added += result.rowcount
                if result.rowcount == 0 and row.get("authors"):
                    db.execute("""UPDATE catalog_papers SET source_authors_json=?, updated_at=?
                        WHERE source=? AND source_id=? AND source_authors_json='[]'""",
                        (json.dumps(row["authors"], ensure_ascii=False), _now(), source, source_id))
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
        crosscheck = self.rules["author_crosscheck"]
        require_source_authors = bool(crosscheck.get("require_source_authors", True))
        source_authors = json.loads(paper["source_authors_json"])
        if paper["source"] != "arxiv" and require_source_authors:
            if not source_authors:
                raise ValueError("source author evidence required")
            official_authors = {_title(name) for name in evidence.authors}
            if not any(_title(name) in official_authors for name in source_authors):
                raise ValueError("author mismatch")
        evidence_host = urlparse(evidence.evidence_url)
        authority_rule = self.rules["authorities"].get(evidence.authority, {})
        expected_host = authority_rule.get("evidence_host")
        if (expected_host is None or evidence_host.scheme != "https"
                or evidence_host.netloc != expected_host):
            raise ValueError("untrusted authority evidence URL")
        if paper["identity_state"] == "conflict":
            raise ValueError("identity conflict is terminal; manual resolution required")
        if paper["source"] == "arxiv" and paper["source_id"] != evidence.arxiv_id:
            raise ValueError("arxiv source identity mismatch")
        url = urlparse(evidence.paper_url)
        arxiv_pattern = authority_rule.get("paper_url_pattern", "")
        doi_pattern = authority_rule.get("paper_url_pattern", "")
        acl_rule = authority_rule
        arxiv_ok = (evidence.authority == "arxiv" and evidence.arxiv_id
                    and url.scheme == "https" and url.netloc == "arxiv.org"
                    and evidence.paper_url == arxiv_pattern.format(arxiv_id=evidence.arxiv_id)
                    and re.fullmatch(r"\d{4}\.\d{4,5}", evidence.arxiv_id))
        doi_ok = (evidence.authority == "crossref" and evidence.doi
                  and url.scheme == "https" and url.netloc == "doi.org"
                  and evidence.paper_url == doi_pattern.format(doi=evidence.doi))
        acl_ok = (evidence.authority == "acl_anthology"
                  and paper["source"] == "acl_anthology"
                  and url.scheme == "https" and url.netloc == "aclanthology.org"
                  and acl_rule.get("same_source_only") is True
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
            self._append_evidence(db, catalog_id, "identity", "identity_verified",
                                  {"title": evidence.title, "authors": evidence.authors,
                                   "paper_url": evidence.paper_url, "published_at": evidence.published_at,
                                   "authority": evidence.authority, "evidence_url": evidence.evidence_url,
                                   "arxiv_id": evidence.arxiv_id, "doi": evidence.doi})

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
        source = self.get(catalog_id)
        source_authors = json.loads(source["source_authors_json"])
        if source["source"] != "arxiv" and self.rules["author_crosscheck"].get("require_source_authors", True):
            if not source_authors:
                raise ValueError("source author evidence required")
            official = {_title(name) for name in record.authors}
            if not any(_title(name) in official for name in source_authors):
                raise ValueError("author mismatch")
        self.verify_identity(catalog_id, IdentityEvidence(
            title=record.title, authors=tuple(record.authors),
            paper_url=record.paper_url, published_at=record.published_at,
            authority="arxiv", evidence_url=response_url, arxiv_id=arxiv_id))

    def admit(self, catalog_id: str, platform: str, *, topic_terms: tuple[str, ...],
              code_evidence: dict[str, Any] | None = None) -> str:
        if platform not in self.rules["platforms"]:
            raise ValueError("unknown platform")
        paper = self.get(catalog_id)
        if paper["identity_state"] != "identity_verified":
            raise ValueError("identity_verified required before admission")
        signals = json.loads(paper["topic_signals_json"])
        fields = [("title", paper["title"])]
        fields.extend(("topic:" + str(signals.get("source", "unavailable")), str(value))
                      for value in signals.get("values", []))
        matches = [{"term": term, "field": field, "value": value}
                   for term in topic_terms if term.strip()
                   for field, value in fields if term.casefold() in value.casefold()]
        code = dict(code_evidence or {})
        required_code = self.rules["per_platform_code_requirement"].get(platform, [])
        code_valid = (code.get("verified") is True
                      and code.get("paper_url") == paper["paper_url"]
                      and all(code.get(key) is True for key in required_code)
                      and urlparse(str(code.get("repository_url", ""))).netloc == "github.com")
        reason = ("topic_out_of_scope" if not matches else
                  "official_code_unverified" if platform == "xiaohongshu" and not code_valid
                  else "verified")
        state = "eligible" if reason == "verified" else "deferred"
        evidence = {"topic_matches": matches, "topic_signal_source": signals.get("source", "unavailable"),
                    "code": code if platform == "xiaohongshu" else None}
        with self._connect() as db:
            db.execute("""INSERT INTO catalog_admissions
                (catalog_id, platform, state, reason, evidence_json, decided_at) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(catalog_id, platform) DO UPDATE SET
                state=excluded.state, reason=excluded.reason,
                evidence_json=excluded.evidence_json, decided_at=excluded.decided_at""",
                (catalog_id, platform, state, reason, json.dumps(evidence, ensure_ascii=False), _now()))
            self._append_evidence(db, catalog_id, "admission", state,
                                  {"platform": platform, "reason": reason, **evidence})
            if state == "eligible":
                operation_id = f"catalog-admission-v1:{catalog_id}:{platform}"
                payload = {"event_version": 1, "catalog_id": catalog_id,
                           "canonical_id": paper["canonical_id"], "platform": platform,
                           "paper_url": paper["paper_url"], "title": paper["title"],
                           "action": self.rules["platforms"][platform]["action"]}
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
