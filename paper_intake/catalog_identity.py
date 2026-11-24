from __future__ import annotations

import re
import hashlib
import json
import unicodedata
from dataclasses import dataclass
from urllib.parse import unquote, urlsplit


_ARXIV_ID = re.compile(r"(?:abs/|pdf/)?(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
_DOI = re.compile(r"10\.\d{4,9}/\S+", re.I)
_NUMERAL = re.compile(r"\b\d+(?:\.\d+)?\b|\b(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\b", re.I)


def normalize_doi(value: str) -> str:
    value = unquote(value.strip())
    if value.lower().startswith(("http://", "https://")):
        value = urlsplit(value).path.lstrip("/")
    value = re.sub(r"^doi:\s*", "", value, flags=re.I).rstrip(".,;)")
    match = _DOI.fullmatch(value)
    return value.casefold() if match else ""


def normalize_arxiv_id(value: str) -> str:
    match = _ARXIV_ID.search(value.strip())
    return match.group(1) if match else ""


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(character for character in value if not unicodedata.combining(character))
    return " ".join(re.findall(r"[\w]+", value, flags=re.UNICODE))


def numeral_signature(value: str) -> tuple[str, ...]:
    tokens = normalize_title(value)
    return tuple(sorted(token.casefold() for token in _NUMERAL.findall(tokens)))


def first_author_surname(authors: list[str]) -> str:
    return normalize_title(authors[0]).split(" ")[-1] if authors else ""


def source_version(record) -> str:
    """Stable upstream revision; excludes local retrieval time."""
    evidence = {
        "updated_at": record.updated_at, "title": record.title,
        "paper_url": record.paper_url, "doi": normalize_doi(record.doi),
        "arxiv_id": normalize_arxiv_id(record.arxiv_id),
        "authors": record.authors, "topics": sorted(record.topics), "track": record.track,
    }
    return hashlib.sha256(json.dumps(evidence, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class IdentityDecision:
    canonical_id: str
    match_level: str
    conflict_type: str = ""


def decide_identity(
    *, source: str, source_id: str, title: str, authors: list[str], doi: str, arxiv_id: str,
    existing: list[dict],
) -> IdentityDecision:
    normalized_doi = normalize_doi(doi)
    normalized_arxiv = normalize_arxiv_id(arxiv_id)
    normalized_title = normalize_title(title)
    surname = first_author_surname(authors)
    fallback = f"source:{source}:{source_id}"
    candidate_id = f"doi:{normalized_doi}" if normalized_doi else (f"arxiv:{normalized_arxiv}" if normalized_arxiv else fallback)
    for item in existing:
        if normalized_doi and item["doi"] == normalized_doi:
            if item["normalized_title"] != normalized_title and item["normalized_title"]:
                return IdentityDecision(fallback, "conflict", "identifier_title_conflict")
            return IdentityDecision(item["canonical_id"], "doi")
        if normalized_arxiv and item["arxiv_id"] == normalized_arxiv:
            if normalized_doi and item["doi"] and item["doi"] != normalized_doi:
                return IdentityDecision(candidate_id, "conflict", "identifier_conflict")
            return IdentityDecision(item["canonical_id"], "persistent_id")
    for item in existing:
        if item["normalized_title"] != normalized_title:
            continue
        if numeral_signature(item["title"]) != numeral_signature(title):
            continue
        existing_surname = first_author_surname(item["authors"])
        if not surname or not existing_surname or surname != existing_surname:
            continue
        if normalized_doi and item["doi"] and item["doi"] != normalized_doi:
            return IdentityDecision(candidate_id, "conflict", "identifier_conflict")
        if normalized_arxiv and item["arxiv_id"] and item["arxiv_id"] != normalized_arxiv:
            return IdentityDecision(candidate_id, "conflict", "identifier_conflict")
        if len(normalized_title.split()) >= 3:
            return IdentityDecision(item["canonical_id"], "title_author")
    return IdentityDecision(candidate_id, "new")
