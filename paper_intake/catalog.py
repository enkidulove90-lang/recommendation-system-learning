from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable, Protocol
from urllib.parse import quote, urlencode, urljoin
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, Tag
import requests


_ATOM = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
_ARXIV_ID = re.compile(r"(?:abs/)?(\d{4}\.\d{4,5})(?:v\d+)?")
_ACL_PAPER_PATH = re.compile(r"^/(\d{4}\.[a-z0-9-]+\.\d+)/?$", re.IGNORECASE)
_DOI_URL = re.compile(r"^https?://doi\.org/(10\.\d{4,9}/\S+)$", re.IGNORECASE)
_SPACE = re.compile(r"\s+")
_TRACK_PREFIX = re.compile(r"^(RES|IND|REP|RPN|DEM|LBR|PPF|DOC)\s+", re.IGNORECASE)
_TRACK_NAMES = {
    "RES": "research",
    "IND": "industry",
    "REP": "reproducibility",
    "RPN": "research-and-practice-notes",
    "DEM": "demonstration",
    "LBR": "late-breaking-results",
    "PPF": "past-present-future",
    "DOC": "doctoral-symposium",
}


class CatalogTransport(Protocol):
    def get_text(self, url: str) -> str: ...

    def get_json(self, url: str) -> dict[str, Any]: ...


class RequestsCatalogTransport:
    def __init__(self, *, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
        proxy = os.getenv("PAPER_CATALOG_HTTP_PROXY", "").strip()
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})
        self.session.headers.update(
            {"User-Agent": "EnkiduPaperCatalog/1.0 (authoritative scholarly metadata collector)"}
        )

    def get_text(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def get_json(self, url: str) -> dict[str, Any]:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("catalog provider returned a non-object JSON response")
        return payload


class CatalogCache:
    """TTL cache with stale-on-error fallback for upstream catalogue pages."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _paths(self, key: str) -> tuple[Path, Path]:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.txt", self.root / f"{digest}.json"

    def store(self, key: str, text: str) -> None:
        content_path, metadata_path = self._paths(key)
        temporary = content_path.with_suffix(".txt.tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(content_path)
        metadata_path.write_text(
            json.dumps({"fetched_at": datetime.now(timezone.utc).timestamp()}),
            encoding="utf-8",
        )

    def get_text(
        self,
        transport: CatalogTransport,
        url: str,
        *,
        key: str,
        ttl_seconds: int,
    ) -> str:
        content_path, metadata_path = self._paths(key)
        if content_path.is_file() and metadata_path.is_file():
            try:
                fetched_at = float(json.loads(metadata_path.read_text(encoding="utf-8"))["fetched_at"])
                age = datetime.now(timezone.utc).timestamp() - fetched_at
                if age < max(ttl_seconds, 0):
                    return content_path.read_text(encoding="utf-8")
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                pass
        try:
            text = transport.get_text(url)
        except Exception:
            if content_path.is_file():
                return content_path.read_text(encoding="utf-8")
            raise
        self.store(key, text)
        return text


@dataclass(slots=True)
class PaperRecord:
    publication_year: int
    venue_type: str
    venue_name: str
    title: str
    paper_url: str
    source: str
    source_id: str
    topics: list[str] = field(default_factory=list)
    topic_source: str = "unavailable"
    track: str = ""
    authors: list[str] = field(default_factory=list)
    published_at: str = ""
    updated_at: str = ""
    doi: str = ""
    arxiv_id: str = ""
    retrieved_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["topics"] = sorted({value for value in self.topics if value})
        return payload


def _text(value: str | None) -> str:
    return _SPACE.sub(" ", value or "").strip()


def _normalized_title(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def _canonical_arxiv_id(value: str) -> str:
    match = _ARXIV_ID.search(value)
    return match.group(1) if match else ""


def _clean_acl_track(value: str) -> str:
    return _text(
        re.sub(
            r"^(?:(?:pdf|bib|xml|mods|endnote)(?:\s*\(full\))?\s*)+",
            "",
            value,
            flags=re.IGNORECASE,
        )
    )


def parse_arxiv_feed(xml_text: str, *, retrieved_at: str = "") -> list[PaperRecord]:
    root = ET.fromstring(xml_text)
    records: list[PaperRecord] = []
    for entry in root.findall("atom:entry", _ATOM):
        entry_id = entry.findtext("atom:id", default="", namespaces=_ATOM)
        arxiv_id = _canonical_arxiv_id(entry_id)
        if not arxiv_id:
            continue
        title = _text(entry.findtext("atom:title", default="", namespaces=_ATOM))
        published = entry.findtext("atom:published", default="", namespaces=_ATOM)
        updated = entry.findtext("atom:updated", default="", namespaces=_ATOM)
        categories = [node.get("term", "") for node in entry.findall("atom:category", _ATOM)]
        primary = entry.find("arxiv:primary_category", _ATOM)
        if primary is not None and primary.get("term"):
            categories.insert(0, primary.get("term", ""))
        categories = list(dict.fromkeys(value for value in categories if value))
        authors = [
            _text(node.findtext("atom:name", default="", namespaces=_ATOM))
            for node in entry.findall("atom:author", _ATOM)
        ]
        records.append(
            PaperRecord(
                publication_year=int(published[:4]) if published[:4].isdigit() else int("20" + arxiv_id[:2]),
                venue_type="preprint",
                venue_name="arXiv",
                title=title,
                paper_url=f"https://arxiv.org/abs/{arxiv_id}",
                source="arxiv",
                source_id=arxiv_id,
                topics=categories,
                topic_source="arxiv_category" if categories else "unavailable",
                authors=[value for value in authors if value],
                published_at=published,
                updated_at=updated,
                arxiv_id=arxiv_id,
                retrieved_at=retrieved_at,
            )
        )
    return records


def parse_acl_event(
    html: str,
    *,
    event_url: str,
    venue_name: str,
    retrieved_at: str = "",
) -> list[PaperRecord]:
    soup = BeautifulSoup(html, "html.parser")
    current_track = ""
    records: list[PaperRecord] = []
    seen: set[str] = set()
    for node in soup.find_all(["h2", "h3", "h4", "a"]):
        if node.name in {"h2", "h3", "h4"}:
            heading = _clean_acl_track(node.get_text(" ", strip=True))
            if heading and not heading.casefold().startswith(("proceedings of", "acl 2026")):
                current_track = heading
            continue
        href = str(node.get("href") or "")
        match = _ACL_PAPER_PATH.match(href)
        if not match or match.group(1) in seen:
            continue
        title = _text(node.get_text(" ", strip=True))
        if not title:
            continue
        source_id = match.group(1)
        seen.add(source_id)
        year_text = source_id[:4]
        records.append(
            PaperRecord(
                publication_year=int(year_text),
                venue_type="conference-paper",
                venue_name=venue_name,
                title=title,
                paper_url=urljoin(event_url, href),
                source="acl_anthology",
                source_id=source_id,
                topics=[current_track] if current_track else [],
                topic_source="conference_track" if current_track else "unavailable",
                track=current_track,
                retrieved_at=retrieved_at,
            )
        )
    return records


def _recsys_topic(heading: str) -> str:
    return _text(re.sub(r"^\d+[A-Z]?\s*:\s*", "", heading, flags=re.IGNORECASE))


def _first_item_text(item: Tag) -> str:
    strong = item.find(["strong", "b"])
    if strong is not None:
        return _text(strong.get_text(" ", strip=True))
    link = item.find("a")
    if link is not None:
        return _text(link.get_text(" ", strip=True))
    strings = list(item.stripped_strings)
    return _text(strings[0] if strings else "")


def parse_recsys_program_page(
    html: str,
    *,
    page_url: str,
    publication_year: int,
    retrieved_at: str = "",
) -> list[PaperRecord]:
    soup = BeautifulSoup(html, "html.parser")
    current_topic = ""
    records: list[PaperRecord] = []
    for node in soup.find_all(["h2", "h3", "h4", "li"]):
        if node.name in {"h2", "h3", "h4"}:
            heading = _text(node.get_text(" ", strip=True))
            if re.match(r"^\d+[A-Z]?\s*:", heading, flags=re.IGNORECASE):
                current_topic = _recsys_topic(heading)
            continue
        raw_title = _first_item_text(node)
        prefix = _TRACK_PREFIX.match(raw_title)
        if prefix is None:
            continue
        track_code = prefix.group(1).upper()
        title = _TRACK_PREFIX.sub("", raw_title).strip()
        title = re.split(r"\s+by\s+(?=[A-ZÀ-ÖØ-Þ])", title, maxsplit=1)[0].strip()
        if not title:
            continue
        link = node.find("a", href=True)
        paper_url = page_url
        doi = ""
        if link is not None:
            candidate = urljoin(page_url, str(link.get("href")))
            doi_match = _DOI_URL.match(candidate)
            if doi_match:
                doi = doi_match.group(1).rstrip(".,;")
            if candidate.startswith("http"):
                paper_url = candidate
        records.append(
            PaperRecord(
                publication_year=publication_year,
                venue_type="conference-paper",
                venue_name=f"ACM RecSys {publication_year}",
                title=title,
                paper_url=paper_url,
                source="recsys_program",
                source_id=f"{publication_year}:{_normalized_title(title)}",
                topics=[current_topic] if current_topic else [],
                topic_source="conference_session" if current_topic else "unavailable",
                track=_TRACK_NAMES.get(track_code, track_code.casefold()),
                doi=doi,
                retrieved_at=retrieved_at,
            )
        )
    return records


class OpenAlexEnricher:
    """Add authoritative venue/topic metadata only after an exact title match."""

    def __init__(self, transport: CatalogTransport, *, mailto: str = "") -> None:
        self.transport = transport
        self.mailto = mailto

    def enrich(self, record: PaperRecord) -> PaperRecord:
        params = {
            "search": record.title,
            "per-page": 5,
            "select": "id,doi,title,publication_year,publication_date,type,primary_location,topics,primary_topic,ids",
        }
        if self.mailto:
            params["mailto"] = self.mailto
        url = "https://api.openalex.org/works?" + urlencode(params)
        results = self.transport.get_json(url).get("results") or []
        match = next(
            (item for item in results if _normalized_title(str(item.get("title") or "")) == _normalized_title(record.title)),
            None,
        )
        if not isinstance(match, dict):
            return record
        topics = [
            _text(str(item.get("display_name") or ""))
            for item in (match.get("topics") or [])
            if isinstance(item, dict)
        ]
        primary_location = match.get("primary_location") or {}
        source = primary_location.get("source") or {} if isinstance(primary_location, dict) else {}
        venue_name = _text(str(source.get("display_name") or "")) if isinstance(source, dict) else ""
        doi = str(match.get("doi") or "").removeprefix("https://doi.org/")
        ids = match.get("ids") or {}
        if venue_name:
            record.venue_name = venue_name
        if match.get("type"):
            record.venue_type = str(match["type"])
        if topics:
            record.topics = list(dict.fromkeys(topics))
            record.topic_source = "openalex_topic"
        if doi:
            record.doi = doi
            record.paper_url = f"https://doi.org/{doi}"
        if isinstance(ids, dict) and ids.get("arxiv"):
            record.arxiv_id = _canonical_arxiv_id(str(ids["arxiv"]))
        if match.get("publication_date"):
            record.published_at = str(match["publication_date"])
        return record


class PaperCatalog:
    def __init__(self, papers: Iterable[PaperRecord] = ()) -> None:
        self.papers: list[PaperRecord] = []
        self._index: dict[str, PaperRecord] = {}
        self.extend(papers)

    @staticmethod
    def _key(record: PaperRecord) -> str:
        if record.doi:
            return "doi:" + record.doi.casefold()
        if record.arxiv_id:
            return "arxiv:" + record.arxiv_id.casefold()
        return "title:" + _normalized_title(record.title)

    def add(self, record: PaperRecord) -> None:
        key = self._key(record)
        existing = self._index.get(key)
        if existing is None:
            self._index[key] = record
            self.papers.append(record)
            return
        existing.topics = list(dict.fromkeys([*existing.topics, *record.topics]))
        if existing.topic_source == "unavailable" and record.topic_source != "unavailable":
            existing.topic_source = record.topic_source
        for name in ("doi", "arxiv_id", "published_at", "updated_at", "track"):
            if not getattr(existing, name) and getattr(record, name):
                setattr(existing, name, getattr(record, name))

    def extend(self, papers: Iterable[PaperRecord]) -> None:
        for paper in papers:
            self.add(paper)

    def write_json(self, path: str | Path, *, refresh_interval_seconds: int) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        generated_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "schema_version": 1,
            "generated_at": generated_at,
            "refresh_interval_seconds": refresh_interval_seconds,
            "paper_count": len(self.papers),
            "papers": [
                item.to_dict()
                for item in sorted(self.papers, key=lambda value: (value.publication_year, value.title.casefold()), reverse=True)
            ],
        }
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(destination)


def refresh_from_config(
    config: dict[str, Any],
    *,
    transport: CatalogTransport | None = None,
    cache_dir: str | Path | None = None,
) -> PaperCatalog:
    client = transport or RequestsCatalogTransport()
    cache = CatalogCache(cache_dir) if cache_dir is not None else None
    now = datetime.now(timezone.utc).isoformat()
    catalog = PaperCatalog()
    for source in config.get("arxiv", []):
        params = {
            "search_query": source["query"],
            "start": 0,
            "max_results": int(source.get("max_results", 100)),
            "sortBy": source.get("sort_by", "submittedDate"),
            "sortOrder": source.get("sort_order", "descending"),
        }
        url = "https://export.arxiv.org/api/query?" + urlencode(params)
        xml_text = (
            cache.get_text(
                client,
                url,
                key="arxiv:" + str(source.get("name") or source["query"]),
                ttl_seconds=int(source.get("cache_ttl_seconds", 86400)),
            )
            if cache
            else client.get_text(url)
        )
        catalog.extend(parse_arxiv_feed(xml_text, retrieved_at=now))
    for source in config.get("acl_events", []):
        url = source["url"]
        html = (
            cache.get_text(
                client,
                url,
                key="acl:" + str(source["venue_name"]),
                ttl_seconds=int(source.get("cache_ttl_seconds", 1800)),
            )
            if cache
            else client.get_text(url)
        )
        records = parse_acl_event(
            html,
            event_url=url,
            venue_name=source["venue_name"],
            retrieved_at=now,
        )
        prefixes = [str(value) for value in source.get("include_id_prefixes", []) if value]
        if prefixes:
            records = [record for record in records if any(record.source_id.startswith(prefix) for prefix in prefixes)]
        catalog.extend(records)
    for source in config.get("recsys_pages", []):
        url = source["url"]
        html = (
            cache.get_text(
                client,
                url,
                key="recsys:" + url,
                ttl_seconds=int(source.get("cache_ttl_seconds", 1800)),
            )
            if cache
            else client.get_text(url)
        )
        catalog.extend(
            parse_recsys_program_page(
                html,
                page_url=url,
                publication_year=int(source["publication_year"]),
                retrieved_at=now,
            )
        )
    enrichment = config.get("openalex_enrichment") or {}
    if enrichment.get("enabled"):
        enricher = OpenAlexEnricher(client, mailto=str(enrichment.get("mailto") or ""))
        maximum = int(enrichment.get("max_records_per_run", 50))
        for record in catalog.papers[:maximum]:
            try:
                enricher.enrich(record)
            except Exception:
                continue
    return catalog


def load_catalog_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("paper catalog config must be a JSON object")
    return payload
