"""Evidence-producing adapter between normalized candidates and catalog admission.

The catalog owns identity and topic decisions. This adapter only obtains the
official-code evidence required by the Xiaohongshu gate; it never publishes.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from typing import Callable

from paper_intake.catalog_governance import CatalogGovernance
from redbook.automation.github_verification import discover_and_verify_official_github
from redbook.automation.sources import PaperRecord


def _normalized(value: str) -> str:
    return "".join(re.findall(r"\w", value.casefold()))


def admit_candidate(
    governance: CatalogGovernance,
    catalog_id: str,
    platform: str,
    *,
    topic_terms: tuple[str, ...],
    record: PaperRecord | None = None,
    fetch_text: Callable[[str], str] | None = None,
) -> str:
    """Admit from persisted identity/topic facts and verified code evidence.

    XHS requires a normalized source record matching the verified catalog
    identity. Network fetches are injected so tests can prove both positive and
    fail-closed paths without sending requests.
    """
    if platform != "xiaohongshu":
        return governance.admit(catalog_id, platform, topic_terms=topic_terms)
    paper = governance.get(catalog_id)
    if paper["identity_state"] != "identity_verified":
        raise ValueError("identity_verified required before admission")
    if record is None or fetch_text is None:
        return governance.admit(catalog_id, platform, topic_terms=topic_terms)
    if (_normalized(record.title) != _normalized(paper["title"])
            or record.urls.get("landing") != paper["paper_url"]):
        raise ValueError("candidate identity does not match catalog")
    verified_authors = {_normalized(name) for name in json.loads(paper["authors_json"] or "[]")}
    candidate_authors = {_normalized(str(item.get("name", ""))) for item in record.authors}
    if not verified_authors.intersection(candidate_authors):
        raise ValueError("candidate author does not match verified identity")
    verification = discover_and_verify_official_github(record, fetch_text)
    evidence = verification.as_dict()
    evidence["evidence_source"] = "paper_landing_and_github_repository"
    evidence["checked_at"] = datetime.now(timezone.utc).isoformat()
    return governance.admit(catalog_id, platform, topic_terms=topic_terms,
                            code_evidence=evidence)
