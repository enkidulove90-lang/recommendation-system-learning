"""Chapter 1: pluggable source collection, normalization, and deterministic dedupe."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
import html
import re
from pathlib import Path
from typing import Any, Protocol

from .common import append_jsonl, jaccard, normalize_text, read_json, stable_hash, title_tokens, utc_now, write_json


SOURCE_PRIORITY = {
    "conference_announcement": 100,
    "proceedings": 90,
    "openreview": 80,
    "arxiv": 70,
    "institution": 60,
    "github": 50,
    "x_signal": 10,
}


@dataclass
class PaperRecord:
    """Normalized contract shared by all sources and stored as JSONL."""

    record_id: str
    title: str
    source_records: list[dict[str, Any]]
    identifiers: dict[str, str] = field(default_factory=dict)
    abstract: str = ""
    authors: list[dict[str, Any]] = field(default_factory=list)
    venue: dict[str, Any] = field(default_factory=dict)
    urls: dict[str, str] = field(default_factory=dict)
    announced_at: str | None = None
    published_at: str | None = None
    topics: list[str] = field(default_factory=list)
    provenance: dict[str, str] = field(default_factory=dict)
    revisions: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PaperRecord":
        source_records = list(value.get("source_records", []))
        now = utc_now()
        title = str(value.get("title", "")).strip()
        identifiers = {str(k): str(v) for k, v in dict(value.get("identifiers", {})).items() if v}
        record_id = str(value.get("record_id") or canonical_id(identifiers, title, value.get("authors", [])))
        return cls(
            record_id=record_id,
            title=title,
            source_records=source_records,
            identifiers=identifiers,
            abstract=str(value.get("abstract", "")),
            authors=list(value.get("authors", [])),
            venue=dict(value.get("venue", {})),
            urls={str(k): str(v) for k, v in dict(value.get("urls", {})).items() if v},
            announced_at=value.get("announced_at"),
            published_at=value.get("published_at"),
            topics=[str(topic) for topic in value.get("topics", []) if str(topic).strip()],
            provenance={"first_seen_at": now, "last_seen_at": now, **dict(value.get("provenance", {}))},
            revisions=list(value.get("revisions", [])),
        )


class PaperSource(Protocol):
    name: str

    def discover(self, cursor: dict[str, Any], query: dict[str, Any]) -> tuple[list[PaperRecord], dict[str, Any]]:
        """Return normalized candidates and a persistable next cursor without downstream writes."""


def canonical_id(identifiers: dict[str, str], title: str, authors: list[dict[str, Any]]) -> str:
    for key in ("doi", "arxiv", "openreview", "dblp"):
        if identifiers.get(key):
            return f"{key}:{identifiers[key].strip().lower()}"
    surname = ""
    if authors:
        surname = str(authors[0].get("name", "")).split()[-1:].pop() if str(authors[0].get("name", "")).split() else ""
    return "title:" + stable_hash(f"{normalize_text(title)}|{surname.casefold()}")[:20]


def _identifier_keys(record: PaperRecord) -> set[str]:
    return {f"{key}:{value.casefold()}" for key, value in record.identifiers.items() if value}


def _same_record(left: PaperRecord, right: PaperRecord) -> bool:
    if _identifier_keys(left) & _identifier_keys(right):
        return True
    left_authors = left.authors[0].get("name", "") if left.authors else ""
    right_authors = right.authors[0].get("name", "") if right.authors else ""
    years = {str(left.venue.get("year", "")), str(right.venue.get("year", ""))}
    return (
        bool(left_authors and right_authors)
        and normalize_text(left_authors).split()[-1:] == normalize_text(right_authors).split()[-1:]
        and len(years - {""}) <= 1
        and jaccard(title_tokens(left.title), title_tokens(right.title)) >= 0.92
    )


def _winner_source(records: list[dict[str, Any]]) -> dict[str, Any]:
    return max(records, key=lambda row: SOURCE_PRIORITY.get(str(row.get("source_type", "")), 0))


def _merge(left: PaperRecord, right: PaperRecord) -> PaperRecord:
    left_priority = max((SOURCE_PRIORITY.get(str(row.get("source_type", "")), 0) for row in left.source_records), default=0)
    right_priority = max((SOURCE_PRIORITY.get(str(row.get("source_type", "")), 0) for row in right.source_records), default=0)
    primary, secondary = (right, left) if right_priority > left_priority else (left, right)
    merged = PaperRecord.from_dict(primary.as_dict())
    merged.identifiers = {**secondary.identifiers, **primary.identifiers}
    merged.source_records = [*left.source_records, *right.source_records]
    merged.urls = {**secondary.urls, **primary.urls}
    merged.topics = list(dict.fromkeys([*left.topics, *right.topics]))
    merged.abstract = primary.abstract or secondary.abstract
    merged.authors = primary.authors or secondary.authors
    merged.venue = {**secondary.venue, **primary.venue}
    merged.announced_at = min(value for value in (left.announced_at, right.announced_at) if value) if left.announced_at and right.announced_at else left.announced_at or right.announced_at
    merged.published_at = max(value for value in (left.published_at, right.published_at) if value) if left.published_at and right.published_at else left.published_at or right.published_at
    merged.provenance["first_seen_at"] = min(left.provenance.get("first_seen_at", utc_now()), right.provenance.get("first_seen_at", utc_now()))
    merged.provenance["last_seen_at"] = utc_now()
    merged.record_id = canonical_id(merged.identifiers, merged.title, merged.authors)
    return merged


def deduplicate_records(records: list[PaperRecord]) -> list[PaperRecord]:
    merged: list[PaperRecord] = []
    for record in records:
        for index, prior in enumerate(merged):
            if _same_record(prior, record):
                merged[index] = _merge(prior, record)
                break
        else:
            merged.append(record)
    return merged


class JsonlSource:
    """Deterministic source adapter for saved source responses and test fixtures."""

    def __init__(self, name: str, path: Path, source_type: str = "institution") -> None:
        self.name, self.path, self.source_type = name, path, source_type

    def discover(self, cursor: dict[str, Any], query: dict[str, Any]) -> tuple[list[PaperRecord], dict[str, Any]]:
        offset = int(cursor.get("offset", 0))
        rows = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(PaperRecord.from_dict(__import__("json").loads(line)))
        for row in rows[offset:]:
            for source_record in row.source_records:
                source_record.setdefault("source", self.name)
                source_record.setdefault("source_type", self.source_type)
                source_record.setdefault("fetched_at", utc_now())
        return rows[offset:], {"offset": len(rows)}


class ConferenceAnnouncementSource:
    """Parse a configured official accepted-paper HTML page without venue-specific code."""

    def __init__(self, name: str, url: str, selector: str, source_type: str = "conference_announcement") -> None:
        self.name, self.url, self.selector, self.source_type = name, url, selector, source_type

    def discover(self, cursor: dict[str, Any], query: dict[str, Any]) -> tuple[list[PaperRecord], dict[str, Any]]:
        import httpx
        from bs4 import BeautifulSoup

        headers = {"User-Agent": "redbook-paper-monitor/1.0"}
        if cursor.get("etag"):
            headers["If-None-Match"] = str(cursor["etag"])
        response = httpx.get(self.url, headers=headers, timeout=20, follow_redirects=True)
        if response.status_code == 304:
            return [], cursor
        response.raise_for_status()
        body_hash = stable_hash(response.text)
        if body_hash == cursor.get("content_hash"):
            return [], {**cursor, "etag": response.headers.get("etag", ""), "content_hash": body_hash}
        soup = BeautifulSoup(response.text, "html.parser")
        records: list[PaperRecord] = []
        for item in soup.select(self.selector):
            title = html.unescape(item.get_text(" ", strip=True))
            if not title or len(title) < 6:
                continue
            href = item.get("href", "") if item.name == "a" else ""
            records.append(PaperRecord.from_dict({
                "title": title,
                "venue": {"name": query.get("venue", self.name), "year": query.get("year"), "status": "accepted"},
                "urls": {"landing": href or self.url},
                "source_records": [{"source": self.name, "source_type": self.source_type, "source_id": stable_hash(title)[:16], "url": self.url, "fetched_at": utc_now(), "content_hash": body_hash}],
                "announced_at": query.get("announced_at"),
            }))
        return records, {"etag": response.headers.get("etag", ""), "content_hash": body_hash, "checked_at": utc_now()}


class ProceedingsSource(ConferenceAnnouncementSource):
    """Generic PMLR/NeurIPS/ACM proceedings adapter using a per-venue link selector."""

    def __init__(self, name: str, url: str, selector: str = "a[href]", source_type: str = "proceedings") -> None:
        super().__init__(name, url, selector, source_type)

    def discover(self, cursor: dict[str, Any], query: dict[str, Any]) -> tuple[list[PaperRecord], dict[str, Any]]:
        records, state = super().discover(cursor, query)
        for record in records:
            record.venue["status"] = "published"
            record.published_at = query.get("published_at")
        return records, state


class OpenReviewSource:
    """OpenReview v2 public Notes adapter; invitation is supplied by the venue config."""

    def __init__(self, name: str, invitation: str, endpoint: str = "https://api2.openreview.net/notes") -> None:
        self.name, self.invitation, self.endpoint = name, invitation, endpoint

    def discover(self, cursor: dict[str, Any], query: dict[str, Any]) -> tuple[list[PaperRecord], dict[str, Any]]:
        import httpx

        params = {"invitation": self.invitation, "limit": 1000}
        if cursor.get("after"):
            params["after"] = cursor["after"]
        response = httpx.get(self.endpoint, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        notes = payload.get("notes", payload.get("data", []))
        records: list[PaperRecord] = []
        for note in notes:
            content = note.get("content", {})
            title = _openreview_value(content.get("title", ""))
            if not title:
                continue
            raw_authors = _openreview_value(content.get("authors", []))
            if isinstance(raw_authors, str):
                raw_authors = [raw_authors]
            authors = [{"name": str(name)} for name in (raw_authors or [])]
            identifiers = {"openreview": str(note.get("id", ""))}
            records.append(PaperRecord.from_dict({
                "title": title, "authors": authors, "abstract": _openreview_value(content.get("abstract", "")), "identifiers": identifiers,
                "venue": {"name": query.get("venue", self.name), "year": query.get("year"), "status": query.get("status", "preprint")},
                "urls": {"landing": f"https://openreview.net/forum?id={identifiers['openreview']}"},
                "source_records": [{"source": self.name, "source_type": "openreview", "source_id": identifiers["openreview"], "url": self.endpoint, "fetched_at": utc_now()}],
            }))
        return records, {"after": utc_now(), "checked_at": utc_now()}


def _openreview_value(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


class SourceRunner:
    """Run source adapters through JSONL/state files so sources remain independently replayable."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def run(self, source: PaperSource, query: dict[str, Any] | None = None) -> dict[str, Any]:
        query = query or {}
        state_path = self.root / "state" / "sources" / f"{source.name}.json"
        cursor = read_json(state_path, {})
        records, next_cursor = source.discover(cursor, query)
        now = date.today().isoformat()
        raw_path = self.root / "inbox" / now / f"{source.name}.jsonl"
        append_jsonl(raw_path, [record.as_dict() for record in records])
        write_json(state_path, {**next_cursor, "updated_at": utc_now()})
        return {"source": source.name, "count": len(records), "raw_path": str(raw_path), "state_path": str(state_path)}

    def normalize(self, inputs: list[Path]) -> dict[str, Any]:
        records: list[PaperRecord] = []
        for path in inputs:
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(PaperRecord.from_dict(__import__("json").loads(line)))
        deduped = deduplicate_records(records)
        output = self.root / "normalized" / "papers.jsonl"
        output.unlink(missing_ok=True)
        append_jsonl(output, [record.as_dict() for record in deduped])
        return {"input_records": len(records), "records": len(deduped), "path": str(output)}
