from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .catalog_store import CatalogRepository
from .catalog_identity import canonical_id


def export_discovery_snapshot(catalog, path: str | Path, *, watch_interval_seconds: int = 1800) -> dict:
    """Write the search-pool snapshot directly from the in-memory catalog.

    Deliberately independent of SQLite: the snapshot lands before the slow
    candidate upsert, so a timeout can never leave ``papers.json`` stale.
    Schema mirrors :func:`export_snapshot` (v2 + checksum); ledger-only fields
    (``status``/``sources`` detail) are filled by the authoritative export
    after the database write completes.
    """
    papers = []
    ordered = sorted(catalog.papers, key=lambda value: (value.publication_year, value.title.casefold()), reverse=True)
    for item in ordered:
        papers.append({
            "canonical_id": canonical_id(item), "status": "discovered",
            "publication_year": item.publication_year, "venue_type": item.venue_type,
            "venue_name": item.venue_name, "title": item.title,
            "paper_url": item.paper_url, "pdf_url": "",
            "doi": item.doi, "arxiv_id": item.arxiv_id,
            "authors": list(item.authors), "source": item.source,
            "source_id": item.source_id, "topics": sorted(set(item.topics)),
            "topic_signals": [], "sources": [],
        })
    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "watch_interval_seconds": watch_interval_seconds,
        "paper_count": len(papers),
        "papers": papers,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    payload["checksum"] = hashlib.sha256(canonical).hexdigest()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return payload


def export_snapshot(repository: CatalogRepository, path: str | Path, *, watch_interval_seconds: int = 1800) -> dict:
    papers = []
    rows = repository._connection.execute(
        "SELECT * FROM papers ORDER BY publication_year DESC, title COLLATE NOCASE DESC"
    ).fetchall()
    for row in rows:
        sources = repository._connection.execute(
            "SELECT source, source_id, discovery_query, match_level FROM paper_sources "
            "WHERE canonical_id=? ORDER BY source, source_id",
            (row["canonical_id"],),
        ).fetchall()
        topics = repository._connection.execute(
            "SELECT signal_type, value, source FROM paper_topics WHERE canonical_id=? ORDER BY signal_type, value",
            (row["canonical_id"],),
        ).fetchall()
        primary = sources[0] if sources else None
        papers.append({
            "canonical_id": row["canonical_id"], "status": row["status"],
            "publication_year": row["publication_year"], "venue_type": row["venue_type"],
            "venue_name": row["venue_name"], "title": row["title"],
            "paper_url": row["paper_url"], "pdf_url": row["pdf_url"],
            "doi": row["doi"], "arxiv_id": row["arxiv_id"],
            "authors": json.loads(row["authors_json"]),
            "source": primary["source"] if primary else "",
            "source_id": primary["source_id"] if primary else "",
            "topics": [topic["value"] for topic in topics],
            "topic_signals": [dict(topic) for topic in topics],
            "sources": [dict(source) for source in sources],
        })
    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "watch_interval_seconds": watch_interval_seconds,
        "paper_count": len(papers),
        "papers": papers,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    payload["checksum"] = hashlib.sha256(canonical).hexdigest()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return payload
