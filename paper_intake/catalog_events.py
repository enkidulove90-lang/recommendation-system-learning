from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from urllib.parse import urlsplit
from typing import TYPE_CHECKING

from .repository import JobRepository

if TYPE_CHECKING:
    from .catalog_store import CatalogRepository


def published_idempotency_key(canonical_id: str, source_version: str) -> str:
    return hashlib.sha256(f"{canonical_id}|{source_version}|delivery-v1".encode("utf-8")).hexdigest()


def published_payload(canonical_id: str, title: str, pdf_url: str, admission_decision: str = "admitted") -> str:
    parsed = urlsplit(pdf_url)
    if not canonical_id or not title.strip():
        raise ValueError("canonical_id and title are required")
    if admission_decision not in {"admitted", "admitted_with_conflict_flag"}:
        raise ValueError("unsupported admission decision")
    # 允许 ACM DOI URL 和 PDF URL
    allowed_hosts = {"arxiv.org", "aclanthology.org", "dl.acm.org", "www.dl.acm.org"}
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts or not parsed.path.endswith(".pdf") and parsed.hostname == "dl.acm.org":
        # 对于 ACM DOI URL，允许 /doi/10.xxxx，路径不一定以 .pdf 结尾
        if not (parsed.path.endswith(".pdf") or parsed.hostname in {"dl.acm.org", "www.dl.acm.org"} and "doi" in parsed.path):
            raise ValueError("verified scholarly PDF URL required")
    return json.dumps({
        "canonical_id": canonical_id,
        "admission_decision": admission_decision,
        "source_type": "url",
        "pdf_url": pdf_url,
        "title": title,
    }, ensure_ascii=False, sort_keys=True)


def consume_next(repository: JobRepository, *, now: datetime | None = None) -> str | None:
    """Consume the oldest pending intake event atomically with job creation."""
    current = (now or datetime.now(UTC)).isoformat()
    with repository._lock:
        connection = repository._connection
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            # A competing SQLite writer owns the only write lock. Nothing was
            # changed, so leave the oldest event visible for the next poll.
            if exc.sqlite_errorcode in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}:
                return None
            raise
        try:
            row = connection.execute(
                """SELECT * FROM outbox WHERE target_domain='paper_intake'
                AND consumed_at IS NULL AND dead_lettered_at IS NULL
                ORDER BY id LIMIT 1"""
            ).fetchone()
            if row is None or row["available_at"] > current:
                connection.commit()
                return None
            try:
                if row["event_version"] != 1 or row["event_type"] not in {
                    "PaperPublishedToCatalog", "PaperMerged", "PaperMergeConfirmed"
                }:
                    raise ValueError("unsupported_event_version")
                payload = json.loads(row["payload_json"])
                if not isinstance(payload, dict):
                    raise ValueError("invalid_event_payload")
                if row["event_type"] == "PaperPublishedToCatalog":
                    if payload.get("source_type") != "url":
                        raise ValueError("invalid_event_payload")
                    published_payload(
                        payload["canonical_id"], payload["title"], payload["pdf_url"],
                        payload["admission_decision"],
                    )
                    if payload["canonical_id"] != row["aggregate_id"]:
                        raise ValueError("aggregate_identity_mismatch")
                else:
                    if payload["old_canonical_id"] != row["aggregate_id"] or not payload["new_canonical_id"]:
                        raise ValueError("aggregate_identity_mismatch")
                    if row["event_type"] == "PaperMerged" and not isinstance(payload["chain_length"], int):
                        raise ValueError("invalid_chain_length")
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                connection.execute(
                    """UPDATE outbox SET attempts=attempts+1, last_error_code='invalid_event',
                    dead_lettered_at=?, dead_letter_reason=? WHERE id=?""",
                    (current, type(exc).__name__, row["id"]),
                )
                connection.commit()
                return None
            if row["event_type"] == "PaperPublishedToCatalog":
                job_id = repository.create_from_catalog_event(
                    event_id=row["event_id"], idempotency_key=row["idempotency_key"], payload=payload,
                )
            else:
                job_id = _apply_merge_event(repository, row["event_type"], payload, current)
            connection.execute(
                "UPDATE outbox SET consumed_at=?, attempts=attempts+1 WHERE id=?",
                (current, row["id"]),
            )
            connection.commit()
            return job_id
        except Exception:
            connection.rollback()
            raise


def _apply_merge_event(repository: JobRepository, event_type: str, payload: dict, now: str) -> str | None:
    connection = repository._connection
    old_id = payload["old_canonical_id"]
    new_id = payload["new_canonical_id"]
    rows = connection.execute(
        """SELECT job_id, status, catalog_canonical_id FROM jobs
           WHERE catalog_canonical_id=? OR (catalog_canonical_id IS NULL AND canonical_id=?)""",
        (old_id, old_id),
    ).fetchall()
    migrated: str | None = None
    for job in rows:
        if job["status"] in {"published", "cancelled"}:
            continue
        if event_type == "PaperMerged" and payload["chain_length"] > 2:
            connection.execute(
                "UPDATE jobs SET merge_review_status='pending_manual_confirmation', updated_at=? WHERE job_id=?",
                (now, job["job_id"]),
            )
            continue
        if job["catalog_canonical_id"]:
            connection.execute(
                "UPDATE jobs SET catalog_canonical_id=?, merge_review_status=NULL, updated_at=? WHERE job_id=?",
                (new_id, now, job["job_id"]),
            )
        else:
            connection.execute(
                "UPDATE jobs SET canonical_id=?, merge_review_status=NULL, updated_at=? WHERE job_id=?",
                (new_id, now, job["job_id"]),
            )
        repository._add_event(job["job_id"], "job.migrated", "Canonical paper identity migrated", {
            "old_canonical_id": old_id, "new_canonical_id": new_id,
        })
        key = hashlib.sha256(f"{job['job_id']}|{old_id}|{new_id}|JobMigrated.v1".encode()).hexdigest()
        connection.execute(
            """INSERT INTO outbox(event_id, event_type, event_version, producer_domain,
                target_domain, aggregate_id, idempotency_key, payload_json, occurred_at, available_at)
            VALUES (?, 'JobMigrated', 1, 'paper_intake', 'catalog', ?, ?, ?, ?, ?)
            ON CONFLICT(idempotency_key) DO NOTHING""",
            (str(uuid.uuid4()), new_id, key, json.dumps({
                "job_id": job["job_id"], "old_canonical_id": old_id,
                "new_canonical_id": new_id,
            }), now, now),
        )
        migrated = job["job_id"]
    return migrated


def consume_catalog_receipt(repository: CatalogRepository) -> str | None:
    now = datetime.now(UTC).isoformat()
    connection = repository._connection
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            """SELECT * FROM outbox WHERE target_domain='catalog'
            AND consumed_at IS NULL AND dead_lettered_at IS NULL ORDER BY id LIMIT 1"""
        ).fetchone()
        if row is None or row["available_at"] > now:
            connection.commit()
            return None
        try:
            if row["event_version"] != 1 or row["event_type"] not in {
                "DeliveryCompleted", "DeliveryFailed", "JobMigrated"
            }:
                raise ValueError("unsupported_receipt")
            payload = json.loads(row["payload_json"])
            job_id = payload["job_id"]
            if row["event_type"] in {"DeliveryCompleted", "DeliveryFailed"}:
                if payload["canonical_id"] != row["aggregate_id"]:
                    raise ValueError("aggregate_identity_mismatch")
                result = "completed" if row["event_type"] == "DeliveryCompleted" else "failed"
                connection.execute(
                    "UPDATE papers SET delivery_ref=?, delivery_result=?, updated_at=? WHERE canonical_id=?",
                    (job_id, result, now, row["aggregate_id"]),
                )
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            connection.execute(
                "UPDATE outbox SET dead_lettered_at=?, dead_letter_reason=? WHERE id=?",
                (now, type(exc).__name__, row["id"]),
            )
            connection.commit()
            return None
        connection.execute("UPDATE outbox SET consumed_at=? WHERE id=?", (now, row["id"]))
        connection.commit()
        return job_id
    except Exception:
        connection.rollback()
        raise
