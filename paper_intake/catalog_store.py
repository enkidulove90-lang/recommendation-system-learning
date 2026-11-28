from __future__ import annotations

import sqlite3
import json
import uuid
import hashlib
from contextlib import nullcontext
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .catalog import PaperRecord
from .catalog_admission import AdmissionDecision
from .catalog_events import published_idempotency_key, published_payload
from .catalog_identity import decide_identity, normalize_arxiv_id, normalize_doi, normalize_title, source_version


def _now() -> str:
    return datetime.now(UTC).isoformat()


class CatalogRepository:
    """SQLite ledger for discovered papers; never mutates intake job state."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.db_path, timeout=5)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA busy_timeout = 5000")
        self._create_schema()

    def close(self) -> None:
        self._connection.close()

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS papers (
                canonical_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                title TEXT NOT NULL,
                publication_year INTEGER,
                venue_type TEXT NOT NULL DEFAULT '',
                venue_name TEXT NOT NULL DEFAULT '',
                paper_url TEXT NOT NULL DEFAULT '',
                pdf_url TEXT NOT NULL DEFAULT '',
                doi TEXT NOT NULL DEFAULT '',
                arxiv_id TEXT NOT NULL DEFAULT '',
                authors_json TEXT NOT NULL DEFAULT '[]',
                last_upstream_updated_at TEXT NOT NULL DEFAULT '',
                source_version TEXT NOT NULL DEFAULT '',
                merged_into TEXT,
                status_changed_via TEXT NOT NULL DEFAULT 'scheduler',
                delivery_ref TEXT,
                delivery_result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS paper_sources (
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                canonical_id TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                last_upstream_updated_at TEXT NOT NULL DEFAULT '',
                discovery_query TEXT NOT NULL DEFAULT '',
                match_level TEXT NOT NULL DEFAULT '',
                source_snapshot_json TEXT NOT NULL DEFAULT '{}',
                PRIMARY KEY (source, source_id),
                FOREIGN KEY (canonical_id) REFERENCES papers(canonical_id)
            );
            CREATE INDEX IF NOT EXISTS paper_sources_canonical_idx ON paper_sources(canonical_id);
            CREATE TABLE IF NOT EXISTS paper_topics (
                canonical_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                value TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (canonical_id, signal_type, value, source),
                FOREIGN KEY (canonical_id) REFERENCES papers(canonical_id)
            );
            CREATE TABLE IF NOT EXISTS catalog_jobs (
                job_id TEXT PRIMARY KEY,
                canonical_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                idempotency_key TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL,
                lease_owner TEXT,
                lease_expires_at TEXT,
                heartbeat_at TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                max_attempts INTEGER NOT NULL DEFAULT 3,
                next_visible_at TEXT NOT NULL,
                failure_class TEXT,
                dead_letter_reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (canonical_id) REFERENCES papers(canonical_id)
            );
            CREATE INDEX IF NOT EXISTS catalog_jobs_ready_idx
                ON catalog_jobs(state, next_visible_at, created_at);
            CREATE TABLE IF NOT EXISTS budget_ledger (
                budget_week TEXT NOT NULL,
                domain TEXT NOT NULL,
                quota INTEGER NOT NULL,
                consumed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (budget_week, domain),
                CHECK (consumed >= 0 AND consumed <= quota)
            );
            CREATE TABLE IF NOT EXISTS budget_admissions (
                budget_week TEXT NOT NULL,
                domain TEXT NOT NULL,
                canonical_id TEXT NOT NULL,
                admitted_at TEXT NOT NULL,
                PRIMARY KEY (budget_week, domain, canonical_id),
                FOREIGN KEY (canonical_id) REFERENCES papers(canonical_id)
            );
            CREATE TABLE IF NOT EXISTS conflicts (
                conflict_id TEXT PRIMARY KEY,
                canonical_id TEXT NOT NULL,
                conflict_type TEXT NOT NULL,
                detail_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending_review',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (canonical_id) REFERENCES papers(canonical_id)
            );
            CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                event_type TEXT NOT NULL,
                event_version INTEGER NOT NULL CHECK (event_version > 0),
                producer_domain TEXT NOT NULL,
                target_domain TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                available_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error_code TEXT,
                consumed_at TEXT,
                dead_lettered_at TEXT,
                dead_letter_reason TEXT,
                archived_at TEXT
            );
            CREATE INDEX IF NOT EXISTS outbox_delivery_idx
                ON outbox(target_domain, consumed_at, dead_lettered_at, id);
            CREATE TABLE IF NOT EXISTS outbox_archive (
                id INTEGER PRIMARY KEY,
                event_id TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL,
                archived_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalog_transitions (
                transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_id TEXT NOT NULL,
                from_status TEXT,
                to_status TEXT NOT NULL,
                changed_via TEXT NOT NULL,
                outbox_event_id TEXT,
                occurred_at TEXT NOT NULL,
                FOREIGN KEY (canonical_id) REFERENCES papers(canonical_id)
            );
            CREATE TABLE IF NOT EXISTS source_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_key TEXT NOT NULL,
                status TEXT NOT NULL,
                error_code TEXT NOT NULL DEFAULT '',
                occurred_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS content_assets (
                canonical_id TEXT NOT NULL,
                asset_kind TEXT NOT NULL,
                asset_key TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                producer TEXT NOT NULL,
                prompt_version TEXT NOT NULL DEFAULT '',
                model_id TEXT NOT NULL DEFAULT '',
                source_hash TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (canonical_id, asset_kind, asset_key)
            );
            CREATE INDEX IF NOT EXISTS ix_content_assets_hash
                ON content_assets(canonical_id, asset_kind, source_hash);
            CREATE VIEW IF NOT EXISTS v_paper_lifecycle AS
            SELECT p.canonical_id, p.status AS catalog_status, p.created_at AS catalog_created_at,
                   (SELECT state FROM catalog_jobs cj WHERE cj.canonical_id=p.canonical_id
                    ORDER BY cj.created_at DESC, cj.job_id DESC LIMIT 1) AS latest_catalog_job_state,
                   (SELECT event_type FROM outbox o WHERE o.aggregate_id=p.canonical_id
                    ORDER BY o.id DESC LIMIT 1) AS latest_outbox_event,
                   (SELECT status FROM jobs j WHERE j.canonical_id=p.canonical_id
                    ORDER BY j.created_at DESC, j.job_id DESC LIMIT 1) AS latest_intake_status
            FROM papers p;
            """
        )
        columns = {row["name"] for row in self._connection.execute("PRAGMA table_info(papers)")}
        if "normalized_title" not in columns:
            self._connection.execute("ALTER TABLE papers ADD COLUMN normalized_title TEXT NOT NULL DEFAULT ''")
        archive_columns = {row["name"] for row in self._connection.execute("PRAGMA table_info(outbox_archive)")}
        for name in ("event_type", "aggregate_id"):
            if name not in archive_columns:
                self._connection.execute(f"ALTER TABLE outbox_archive ADD COLUMN {name} TEXT NOT NULL DEFAULT ''")
        self._connection.execute("CREATE INDEX IF NOT EXISTS papers_doi_idx ON papers(doi)")
        self._connection.execute("CREATE INDEX IF NOT EXISTS papers_arxiv_idx ON papers(arxiv_id)")
        self._connection.execute("CREATE INDEX IF NOT EXISTS papers_title_idx ON papers(normalized_title)")

    def upsert_candidate(self, record: PaperRecord, *, discovery_query: str = "") -> str:
        if not record.source or not record.source_id or not record.title.strip():
            raise ValueError("source, source_id, and title are required")
        now = _now()
        normalized_doi = normalize_doi(record.doi)
        normalized_arxiv = normalize_arxiv_id(record.arxiv_id)
        normalized_title = normalize_title(record.title)
        revision = source_version(record)
        with (nullcontext() if self._connection.in_transaction else self._connection):
            source_row = self._connection.execute(
                "SELECT canonical_id FROM paper_sources WHERE source=? AND source_id=?",
                (record.source, record.source_id),
            ).fetchone()
            if source_row:
                canonical_id = source_row["canonical_id"]
                match_level = "persistent_id"
                conflict_type = ""
            else:
                candidates = self._connection.execute(
                    "SELECT canonical_id, title, normalized_title, authors_json, doi, arxiv_id "
                    "FROM papers WHERE (doi=? AND doi!='') OR (arxiv_id=? AND arxiv_id!='') "
                    "OR normalized_title=?",
                    (normalized_doi, normalized_arxiv, normalized_title),
                ).fetchall()
                existing = [
                    {**dict(row), "authors": json.loads(row["authors_json"])} for row in candidates
                ]
                decision = decide_identity(
                    source=record.source, source_id=record.source_id, title=record.title,
                    authors=record.authors, doi=normalized_doi, arxiv_id=normalized_arxiv,
                    existing=existing,
                )
                canonical_id, match_level, conflict_type = (
                    decision.canonical_id, decision.match_level, decision.conflict_type
                )
            status = "identity_conflict" if conflict_type else "discovered"
            self._connection.execute(
                """INSERT INTO papers (
                    canonical_id, status, title, normalized_title, publication_year,
                    venue_type, venue_name, paper_url, doi, arxiv_id, authors_json,
                    last_upstream_updated_at, source_version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_id) DO UPDATE SET
                    updated_at=excluded.updated_at,
                    title=CASE WHEN papers.status='published_to_catalog' THEN papers.title ELSE excluded.title END,
                    normalized_title=CASE WHEN papers.status='published_to_catalog' THEN papers.normalized_title ELSE excluded.normalized_title END,
                    paper_url=CASE WHEN papers.status='published_to_catalog' THEN papers.paper_url ELSE excluded.paper_url END,
                    doi=CASE WHEN papers.status='published_to_catalog' OR excluded.doi='' THEN papers.doi ELSE excluded.doi END,
                    arxiv_id=CASE WHEN papers.status='published_to_catalog' OR excluded.arxiv_id='' THEN papers.arxiv_id ELSE excluded.arxiv_id END,
                    last_upstream_updated_at=CASE
                        WHEN excluded.last_upstream_updated_at!='' THEN excluded.last_upstream_updated_at
                        ELSE papers.last_upstream_updated_at END,
                    source_version=excluded.source_version""",
                (canonical_id, status, record.title, normalized_title, record.publication_year,
                 record.venue_type, record.venue_name, record.paper_url, normalized_doi,
                 normalized_arxiv, json.dumps(record.authors, ensure_ascii=False),
                 record.updated_at, revision, now, now),
            )
            self._connection.execute(
                """INSERT INTO paper_sources (
                    source, source_id, canonical_id, first_seen_at, last_seen_at,
                    last_upstream_updated_at, discovery_query, match_level, source_snapshot_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source, source_id) DO UPDATE SET
                    last_seen_at=excluded.last_seen_at,
                    last_upstream_updated_at=excluded.last_upstream_updated_at,
                    source_snapshot_json=excluded.source_snapshot_json""",
                (record.source, record.source_id, canonical_id, now, now, record.updated_at,
                 discovery_query, match_level, json.dumps(asdict(record), ensure_ascii=False)),
            )
            signal_type = {
                "arxiv_category": "author_category",
                "conference_track": "official_track",
                "conference_session": "official_session",
            }.get(record.topic_source, "inferred")
            for topic in record.topics:
                self._connection.execute(
                    """INSERT INTO paper_topics (
                        canonical_id, signal_type, value, source, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(canonical_id, signal_type, value, source)
                    DO UPDATE SET updated_at=excluded.updated_at""",
                    (canonical_id, signal_type, topic, record.source, now, now),
                )
            if conflict_type:
                self._connection.execute(
                    """INSERT INTO conflicts (
                        conflict_id, canonical_id, conflict_type, detail_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)""",
                    (str(uuid.uuid4()), canonical_id, conflict_type,
                     json.dumps({"source": record.source, "source_id": record.source_id}), now, now),
                )
            return canonical_id

    def reserve_budget(self, canonical_id: str, *, budget_week: str, domain: str, quota: int) -> bool:
        if not budget_week or not domain or quota < 0:
            raise ValueError("budget_week, domain, and nonnegative quota are required")
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            result = self._reserve_budget_tx(canonical_id, budget_week, domain, quota, _now())
            self._connection.commit()
            return result
        except Exception:
            self._connection.rollback()
            raise

    def _reserve_budget_tx(self, canonical_id: str, week: str, domain: str, quota: int, now: str) -> bool:
        existing = self._connection.execute(
            "SELECT 1 FROM budget_admissions WHERE budget_week=? AND domain=? AND canonical_id=?",
            (week, domain, canonical_id),
        ).fetchone()
        if existing:
            return True
        self._connection.execute(
            """INSERT INTO budget_ledger(budget_week, domain, quota, consumed, created_at, updated_at)
            VALUES (?, ?, ?, 0, ?, ?) ON CONFLICT(budget_week, domain) DO NOTHING""",
            (week, domain, quota, now, now),
        )
        changed = self._connection.execute(
            """UPDATE budget_ledger SET consumed=consumed+1, updated_at=?
            WHERE budget_week=? AND domain=? AND consumed < quota""",
            (now, week, domain),
        ).rowcount
        if not changed:
            return False
        self._connection.execute(
            "INSERT INTO budget_admissions(budget_week, domain, canonical_id, admitted_at) VALUES (?, ?, ?, ?)",
            (week, domain, canonical_id, now),
        )
        return True

    def queue_candidate(self, canonical_id: str, *, max_attempts: int = 3) -> str:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        now = _now()
        with self._connection:
            paper = self._connection.execute(
                "SELECT status, source_version FROM papers WHERE canonical_id=?", (canonical_id,)
            ).fetchone()
            if paper is None:
                raise KeyError(canonical_id)
            if paper["status"] in {"identity_conflict", "published_to_catalog"}:
                raise ValueError("paper is not eligible for automatic governance")
            key = hashlib.sha256(f"{canonical_id}|{paper['source_version']}|qualify-v1".encode()).hexdigest()
            job_id = str(uuid.uuid4())
            self._connection.execute(
                """INSERT INTO catalog_jobs(
                    job_id, canonical_id, task_type, idempotency_key, state,
                    max_attempts, next_visible_at, created_at, updated_at
                ) VALUES (?, ?, 'qualify', ?, 'ready', ?, ?, ?, ?)
                ON CONFLICT(idempotency_key) DO NOTHING""",
                (job_id, canonical_id, key, max_attempts, now, now, now),
            )
            stored_row = self._connection.execute(
                "SELECT job_id, state FROM catalog_jobs WHERE idempotency_key=?", (key,)
            ).fetchone()
            stored = stored_row["job_id"]
            if stored_row["state"] == "done":
                return stored
            self._connection.execute(
                "UPDATE papers SET status='queued', status_changed_via='scheduler', updated_at=? "
                "WHERE canonical_id=? AND status IN ('discovered', 'deferred_budget', 'metadata_only')",
                (now, canonical_id),
            )
            return stored

    def claim_job(self, worker_id: str, *, now: datetime | None = None, lease_seconds: int = 30) -> sqlite3.Row | None:
        current = now or datetime.now(UTC)
        timestamp = current.isoformat()
        expiry = (current + timedelta(seconds=lease_seconds)).isoformat()
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            while True:
                row = self._connection.execute(
                    """SELECT * FROM catalog_jobs
                    WHERE (state='ready' AND next_visible_at<=?)
                       OR (state='leased' AND lease_expires_at<=?)
                    ORDER BY created_at, job_id LIMIT 1""",
                    (timestamp, timestamp),
                ).fetchone()
                if row is None:
                    self._connection.commit()
                    return None
                if row["attempts"] >= row["max_attempts"]:
                    self._connection.execute(
                        "UPDATE catalog_jobs SET state='dead', dead_letter_reason='attempts_exhausted', updated_at=? WHERE job_id=?",
                        (timestamp, row["job_id"]),
                    )
                    continue
                self._connection.execute(
                    """UPDATE catalog_jobs SET state='leased', lease_owner=?, lease_expires_at=?,
                    heartbeat_at=?, attempts=attempts+1, updated_at=? WHERE job_id=?""",
                    (worker_id, expiry, timestamp, timestamp, row["job_id"]),
                )
                result = self._connection.execute(
                    "SELECT * FROM catalog_jobs WHERE job_id=?", (row["job_id"],)
                ).fetchone()
                self._connection.commit()
                return result
        except Exception:
            self._connection.rollback()
            raise

    def heartbeat(self, job_id: str, worker_id: str, *, now: datetime | None = None, lease_seconds: int = 30) -> bool:
        current = now or datetime.now(UTC)
        with self._connection:
            return self._connection.execute(
                """UPDATE catalog_jobs SET lease_expires_at=?, heartbeat_at=?, updated_at=?
                WHERE job_id=? AND state='leased' AND lease_owner=? AND lease_expires_at>?""",
                ((current + timedelta(seconds=lease_seconds)).isoformat(), current.isoformat(), current.isoformat(),
                 job_id, worker_id, current.isoformat()),
            ).rowcount == 1

    def fail_catalog_job(self, job_id: str, worker_id: str, *, error_code: str, retryable: bool) -> str:
        now = datetime.now(UTC)
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            row = self._connection.execute(
                "SELECT attempts, max_attempts FROM catalog_jobs WHERE job_id=? AND state='leased' AND lease_owner=?",
                (job_id, worker_id),
            ).fetchone()
            if row is None:
                raise ValueError("catalog job lease was lost")
            dead = not retryable or row["attempts"] >= row["max_attempts"]
            state = "dead" if dead else "ready"
            next_visible = (now + timedelta(seconds=min(2 ** row["attempts"], 60))).isoformat()
            self._connection.execute(
                """UPDATE catalog_jobs SET state=?, lease_owner=NULL, lease_expires_at=NULL,
                next_visible_at=?, failure_class=?, dead_letter_reason=?, updated_at=? WHERE job_id=?""",
                (state, next_visible, "discovery_failed" if retryable else "parse_failed",
                 error_code if dead else None, now.isoformat(), job_id),
            )
            self._connection.commit()
            return state
        except Exception:
            self._connection.rollback()
            raise

    def complete_governance(
        self, job_id: str, decision: AdmissionDecision, *, budget_week: str, domain: str, quota: int,
        domain_quota: int | None = None, worker_id: str | None = None,
    ) -> str:
        if decision.status not in {"admitted", "metadata_only", "deferred_budget", "identity_conflict"}:
            raise ValueError("unsupported governance decision")
        now = _now()
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            job = self._connection.execute("SELECT * FROM catalog_jobs WHERE job_id=?", (job_id,)).fetchone()
            if job is None:
                raise KeyError(job_id)
            if job["state"] == "done":
                self._connection.commit()
                return "already_done"
            if job["state"] == "leased" and (
                not worker_id or job["lease_owner"] != worker_id or job["lease_expires_at"] <= now
            ):
                raise ValueError("catalog governance lease is not owned by this worker")
            if job["state"] not in {"ready", "leased"}:
                raise ValueError("catalog governance job is not ready")
            paper = self._connection.execute("SELECT * FROM papers WHERE canonical_id=?", (job["canonical_id"],)).fetchone()
            if paper["status"] not in {"queued", "parsing"}:
                raise ValueError("paper is not in governance queue")
            status = decision.status
            event_id = None
            if status == "admitted":
                if not budget_week or not domain or quota < 0:
                    raise ValueError("budget parameters required")
                payload = published_payload(job["canonical_id"], paper["title"], decision.pdf_url)
                self._connection.execute("SAVEPOINT budget_bundle")
                total_ok = self._reserve_budget_tx(job["canonical_id"], budget_week, "all", quota, now)
                domain_ok = total_ok and (
                    domain == "all" or domain_quota is None or
                    self._reserve_budget_tx(job["canonical_id"], budget_week, domain, domain_quota, now)
                )
                if total_ok and domain_ok:
                    self._connection.execute("RELEASE SAVEPOINT budget_bundle")
                    status = "published_to_catalog"
                    key = published_idempotency_key(job["canonical_id"], paper["source_version"])
                    event_id = str(uuid.uuid4())
                    self._connection.execute(
                        """INSERT INTO outbox(
                            event_id, event_type, event_version, producer_domain, target_domain,
                            aggregate_id, idempotency_key, payload_json, occurred_at, available_at
                        ) VALUES (?, 'PaperPublishedToCatalog', 1, 'catalog', 'paper_intake', ?, ?, ?, ?, ?)
                        ON CONFLICT(idempotency_key) DO NOTHING""",
                        (event_id, job["canonical_id"], key, payload, now, now),
                    )
                    event_id = self._connection.execute(
                        "SELECT event_id FROM outbox WHERE idempotency_key=?", (key,)
                    ).fetchone()["event_id"]
                else:
                    self._connection.execute("ROLLBACK TO SAVEPOINT budget_bundle")
                    self._connection.execute("RELEASE SAVEPOINT budget_bundle")
                    status = "deferred_budget"
            self._connection.execute(
                """UPDATE papers SET status=?, pdf_url=?, status_changed_via='scheduler', updated_at=?
                WHERE canonical_id=?""",
                (status, decision.pdf_url if status == "published_to_catalog" else "", now, job["canonical_id"]),
            )
            self._connection.execute(
                """INSERT INTO catalog_transitions(canonical_id, from_status, to_status, changed_via, outbox_event_id, occurred_at)
                VALUES (?, ?, ?, 'scheduler', ?, ?)""",
                (job["canonical_id"], paper["status"], status, event_id, now),
            )
            self._connection.execute(
                "UPDATE catalog_jobs SET state='done', lease_owner=NULL, lease_expires_at=NULL, updated_at=? WHERE job_id=?",
                (now, job_id),
            )
            self._connection.commit()
            return status
        except Exception:
            self._connection.rollback()
            raise

    def merge_papers(self, old_canonical_id: str, new_canonical_id: str) -> str:
        if old_canonical_id == new_canonical_id:
            raise ValueError("cannot merge a paper into itself")
        now = _now()
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            old = self._connection.execute("SELECT * FROM papers WHERE canonical_id=?", (old_canonical_id,)).fetchone()
            if old is None or old["merged_into"]:
                raise ValueError("old canonical paper is missing or already merged")
            target = new_canonical_id
            seen = {old_canonical_id}
            chain_length = 0
            while True:
                if target in seen:
                    raise ValueError("merge cycle detected")
                seen.add(target)
                row = self._connection.execute("SELECT merged_into FROM papers WHERE canonical_id=?", (target,)).fetchone()
                if row is None:
                    raise ValueError("merge target does not exist")
                chain_length += 1
                if not row["merged_into"]:
                    break
                target = row["merged_into"]
            self._connection.execute(
                "UPDATE papers SET merged_into=?, updated_at=? WHERE canonical_id=?",
                (new_canonical_id, now, old_canonical_id),
            )
            key = hashlib.sha256(f"{old_canonical_id}|{target}|PaperMerged.v1".encode()).hexdigest()
            event_id = str(uuid.uuid4())
            self._connection.execute(
                """INSERT INTO outbox(event_id, event_type, event_version, producer_domain,
                    target_domain, aggregate_id, idempotency_key, payload_json, occurred_at, available_at)
                VALUES (?, 'PaperMerged', 1, 'catalog', 'paper_intake', ?, ?, ?, ?, ?)""",
                (event_id, old_canonical_id, key, json.dumps({
                    "old_canonical_id": old_canonical_id, "new_canonical_id": target,
                    "chain_length": chain_length,
                }), now, now),
            )
            self._connection.commit()
            return event_id
        except Exception:
            self._connection.rollback()
            raise

    def confirm_merge(self, old_canonical_id: str, final_canonical_id: str) -> str:
        now = _now()
        with self._connection:
            source = self._connection.execute(
                "SELECT merged_into FROM papers WHERE canonical_id=?", (old_canonical_id,)
            ).fetchone()
            target = self._connection.execute(
                "SELECT merged_into FROM papers WHERE canonical_id=?", (final_canonical_id,)
            ).fetchone()
            if source is None or not source["merged_into"] or target is None or target["merged_into"]:
                raise ValueError("confirmation must point from a merged paper to a terminal canonical paper")
            cursor = source["merged_into"]
            seen = {old_canonical_id}
            while cursor != final_canonical_id:
                if cursor in seen:
                    raise ValueError("merge chain contains a cycle")
                seen.add(cursor)
                next_row = self._connection.execute(
                    "SELECT merged_into FROM papers WHERE canonical_id=?", (cursor,)
                ).fetchone()
                if next_row is None or not next_row["merged_into"]:
                    raise ValueError("confirmed target is not on the merge chain")
                cursor = next_row["merged_into"]
            event_id = str(uuid.uuid4())
            key = hashlib.sha256(f"{old_canonical_id}|{final_canonical_id}|PaperMergeConfirmed.v1".encode()).hexdigest()
            self._connection.execute(
                """INSERT INTO outbox(event_id, event_type, event_version, producer_domain,
                    target_domain, aggregate_id, idempotency_key, payload_json, occurred_at, available_at)
                VALUES (?, 'PaperMergeConfirmed', 1, 'catalog', 'paper_intake', ?, ?, ?, ?, ?)
                ON CONFLICT(idempotency_key) DO NOTHING""",
                (event_id, old_canonical_id, key, json.dumps({
                    "old_canonical_id": old_canonical_id, "new_canonical_id": final_canonical_id,
                }), now, now),
            )
            return self._connection.execute(
                "SELECT event_id FROM outbox WHERE idempotency_key=?", (key,)
            ).fetchone()["event_id"]

    def reconcile(self) -> dict:
        missing = self._connection.execute(
            """SELECT p.canonical_id FROM papers p WHERE p.status='published_to_catalog'
            AND NOT EXISTS (SELECT 1 FROM outbox o WHERE o.event_type='PaperPublishedToCatalog'
              AND o.aggregate_id=p.canonical_id)
            AND NOT EXISTS (SELECT 1 FROM outbox_archive a WHERE a.event_type='PaperPublishedToCatalog'
              AND a.aggregate_id=p.canonical_id) ORDER BY p.canonical_id"""
        ).fetchall()
        status_counts = {name: 0 for name in (
            "discovered", "queued", "parsing", "metadata_only", "deferred_budget",
            "identity_conflict", "published_to_catalog",
        )}
        status_counts.update({row["status"]: row["count"] for row in self._connection.execute(
            "SELECT status, count(*) AS count FROM papers GROUP BY status"
        )})
        return {
            "paper_count": self._connection.execute("SELECT count(*) FROM papers").fetchone()[0],
            "status_counts": status_counts,
            "pending_outbox_count": self._connection.execute(
                "SELECT count(*) FROM outbox WHERE consumed_at IS NULL AND dead_lettered_at IS NULL"
            ).fetchone()[0],
            "consumed_outbox_count": self._connection.execute(
                "SELECT count(*) FROM outbox WHERE consumed_at IS NOT NULL"
            ).fetchone()[0],
            "dead_outbox_count": self._connection.execute(
                "SELECT count(*) FROM outbox WHERE dead_lettered_at IS NOT NULL"
            ).fetchone()[0],
            "missing_delivery_event_ids": [row["canonical_id"] for row in missing],
        }

    def record_source_runs(self, source_runs: dict[str, dict[str, str]]) -> None:
        now = _now()
        with self._connection:
            for key, result in source_runs.items():
                self._connection.execute(
                    "INSERT INTO source_runs(source_key, status, error_code, occurred_at) VALUES (?, ?, ?, ?)",
                    (key, result["status"], result.get("error_code", ""), now),
                )

    def archive_consumed_events(self, *, before: str) -> int:
        now = _now()
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            rows = self._connection.execute(
                """SELECT * FROM outbox WHERE consumed_at IS NOT NULL AND consumed_at<?
                AND dead_lettered_at IS NULL AND archived_at IS NULL ORDER BY id""",
                (before,),
            ).fetchall()
            archived = 0
            for row in rows:
                if row["event_type"] == "PaperPublishedToCatalog":
                    persisted = self._connection.execute(
                        "SELECT 1 FROM jobs WHERE source_event_id=?", (row["event_id"],)
                    ).fetchone()
                    if not persisted:
                        continue
                self._connection.execute(
                    """INSERT INTO outbox_archive(id, event_id, payload_json, archived_at, event_type, aggregate_id)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (row["id"], row["event_id"], json.dumps(dict(row), ensure_ascii=False), now,
                     row["event_type"], row["aggregate_id"]),
                )
                self._connection.execute("DELETE FROM outbox WHERE id=?", (row["id"],))
                archived += 1
            self._connection.commit()
            return archived
        except Exception:
            self._connection.rollback()
            raise


class CatalogProvenanceReader:
    """Narrow read-only capability exposed to the delivery domain."""

    def __init__(self, db_path: str | Path) -> None:
        self._connection = sqlite3.connect(f"file:{Path(db_path).resolve().as_posix()}?mode=ro", uri=True)
        self._connection.row_factory = sqlite3.Row

    def get_sources(self, canonical_id: str) -> list[dict[str, str]]:
        rows = self._connection.execute(
            """SELECT source, source_id, first_seen_at, last_seen_at,
                      last_upstream_updated_at, discovery_query, match_level
               FROM paper_sources WHERE canonical_id=? ORDER BY first_seen_at, source""",
            (canonical_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self._connection.close()
