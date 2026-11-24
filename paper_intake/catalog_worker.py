from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo
import httpx

from .catalog import PaperRecord
from .catalog_admission import admit_candidate, verify_pdf_url
from .catalog_store import CatalogRepository


def process_next(
    repository: CatalogRepository, *, pdf_probe: Callable[[str], bool] = verify_pdf_url,
    weekly_quota: int = 300, weekly_domain_quotas: dict[str, int] | None = None,
    worker_id: str = "catalog-worker",
) -> str | None:
    job = repository.claim_job(worker_id)
    if job is None:
        return None
    paper = repository._connection.execute(
        "SELECT * FROM papers WHERE canonical_id=?", (job["canonical_id"],)
    ).fetchone()
    source = repository._connection.execute(
        "SELECT source, source_id FROM paper_sources WHERE canonical_id=? ORDER BY first_seen_at LIMIT 1",
        (job["canonical_id"],),
    ).fetchone()
    topics = [row["value"] for row in repository._connection.execute(
        "SELECT value FROM paper_topics WHERE canonical_id=?", (job["canonical_id"],)
    ).fetchall()]
    record = PaperRecord(
        publication_year=paper["publication_year"] or 0,
        venue_type=paper["venue_type"], venue_name=paper["venue_name"],
        title=paper["title"], paper_url=paper["paper_url"],
        source=source["source"], source_id=source["source_id"],
        authors=json.loads(paper["authors_json"]), doi=paper["doi"], arxiv_id=paper["arxiv_id"],
        topics=topics,
    )
    try:
        decision = admit_candidate(record, pdf_probe=pdf_probe)
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        week = f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"
        domain = classify_domain(record)
        domain_quota = weekly_domain_quotas.get(domain) if weekly_domain_quotas else None
        return repository.complete_governance(
            job["job_id"], decision, budget_week=week, domain=domain, quota=weekly_quota,
            domain_quota=domain_quota, worker_id=worker_id,
        )
    except (TimeoutError, httpx.TransportError, sqlite3.OperationalError) as exc:
        return repository.fail_catalog_job(
            job["job_id"], worker_id, error_code=type(exc).__name__, retryable=True,
        )
    except Exception as exc:
        return repository.fail_catalog_job(
            job["job_id"], worker_id, error_code=type(exc).__name__, retryable=False,
        )


def classify_domain(record: PaperRecord) -> str:
    if record.venue_name.startswith("ACL") or "cs.CL" in record.topics:
        return "nlp"
    if record.venue_name.startswith("ACM RecSys") or "cs.IR" in record.topics:
        return "information_retrieval"
    if any(topic in record.topics for topic in ("cs.LG", "cs.AI", "stat.ML")):
        return "machine_learning"
    return "cross_domain"
