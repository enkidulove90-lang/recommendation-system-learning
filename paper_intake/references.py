from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Protocol
from urllib.parse import quote, urlencode
import xml.etree.ElementTree as ET

import requests


_ARXIV_ID = re.compile(
    r"(?i)(?:arxiv(?:\s+preprint)?(?:\s+arxiv)?\s*:\s*|arxiv\.org/(?:abs|pdf)/)"
    r"(\d{4}\.\d{4,5})(?:v\d+)?"
)
_DOI = re.compile(r"(?i)(?:doi\s*:\s*|https?://doi\.org/)(10\.\d{4,9}/[^\s<>\])]+)")
_MARKDOWN_LINK = re.compile(r"\[([^]]+)\]\(https?://[^)]+\)")
_WORD = re.compile(r"[a-z0-9]+")
_ATOM = {"atom": "http://www.w3.org/2005/Atom"}


class ReferenceTransport(Protocol):
    def get_text(self, url: str) -> str: ...

    def get_json(self, url: str) -> dict[str, Any]: ...


class RequestsReferenceTransport:
    def __init__(self, *, timeout: float = 15.0) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({"User-Agent": "paper-intake/1.0 (verified-reference-resolver)"})

    def get_text(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def get_json(self, url: str) -> dict[str, Any]:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("reference provider returned a non-object response")
        return payload


@dataclass(frozen=True, slots=True)
class VerifiedReference:
    url: str
    provider: str


def _reference_candidates(markdown: str) -> list[str]:
    match = re.search(r"(?im)^##\s+references\s*$", markdown)
    body = markdown[match.end() :] if match else ""
    return [
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n", body)
        if re.match(r"^\s*\[\d+\]", paragraph)
    ]


def _tokens(value: str) -> set[str]:
    return {token for token in _WORD.findall(value.casefold()) if len(token) > 2}


def _title_matches(expected: str, authoritative: str) -> bool:
    wanted = _tokens(expected)
    actual = _tokens(authoritative)
    if not wanted or not actual:
        return False
    return len(wanted & actual) / max(len(wanted), len(actual)) >= 0.85


def _best_candidate(title: str, candidates: list[str]) -> str:
    wanted = _tokens(title)
    best = ""
    best_score = 0.0
    for candidate in candidates:
        available = _tokens(candidate)
        score = len(wanted & available) / max(len(wanted), 1)
        if score > best_score:
            best, best_score = candidate, score
    return best if best_score >= 0.75 else ""


def _identity(reference: str) -> tuple[str, str]:
    arxiv = _ARXIV_ID.search(reference)
    if arxiv:
        return "arxiv", arxiv.group(1)
    doi = _DOI.search(reference)
    if doi:
        return "doi", doi.group(1).rstrip(".,;)")
    return "", ""


class VerifiedReferenceResolver:
    """Resolve only identities confirmed by an authoritative scholarly API."""

    def __init__(self, *, transport: ReferenceTransport | None = None) -> None:
        self.transport = transport or RequestsReferenceTransport()

    def resolve(self, *, title: str, citation: str) -> VerifiedReference | None:
        identity_type, identity = _identity(citation)
        if identity_type == "arxiv":
            return self._resolve_arxiv(identity, title)
        if identity_type == "doi":
            return self._resolve_doi(identity, title)
        return None

    def _resolve_arxiv(self, arxiv_id: str, title: str) -> VerifiedReference | None:
        url = "https://export.arxiv.org/api/query?" + urlencode({"id_list": arxiv_id})
        try:
            root = ET.fromstring(self.transport.get_text(url))
            entry = root.find("atom:entry", _ATOM)
            authoritative = "" if entry is None else " ".join(
                (entry.findtext("atom:title", default="", namespaces=_ATOM)).split()
            )
        except Exception:
            return None
        if not _title_matches(title, authoritative):
            return None
        return VerifiedReference(url=f"https://arxiv.org/abs/{arxiv_id}", provider="arxiv")

    def _resolve_doi(self, doi: str, title: str) -> VerifiedReference | None:
        crossref_url = "https://api.crossref.org/works/" + quote(doi, safe="")
        try:
            message = self.transport.get_json(crossref_url).get("message") or {}
            titles = message.get("title") or []
            authoritative = str(titles[0]) if titles else ""
            returned_doi = str(message.get("DOI") or "").casefold()
            if returned_doi == doi.casefold() and _title_matches(title, authoritative):
                return VerifiedReference(url=f"https://doi.org/{doi}", provider="crossref")
        except Exception:
            pass

        openalex_url = "https://api.openalex.org/works?" + urlencode(
            {"filter": f"doi:https://doi.org/{doi}", "select": "doi,title"}
        )
        try:
            results = self.transport.get_json(openalex_url).get("results") or []
        except Exception:
            return None
        for work in results:
            returned_doi = str(work.get("doi") or "").removeprefix("https://doi.org/")
            authoritative = str(work.get("title") or "")
            if returned_doi.casefold() == doi.casefold() and _title_matches(title, authoritative):
                return VerifiedReference(url=f"https://doi.org/{doi}", provider="openalex")
        return None


def _title_parts(reference: str) -> tuple[str, str]:
    clean = _MARKDOWN_LINK.sub(r"\1", reference.strip()).rstrip(".")
    clean = re.sub(
        r"(?i)\.?\s*(?:arxiv(?:\s+preprint)?(?:\s+arxiv)?\s*:\s*\d{4}\.\d{4,5}(?:v\d+)?"
        r"|doi\s*:\s*10\.\d{4,9}/\S+)\.?$",
        "",
        clean,
    ).strip().rstrip(".")
    if ". " not in clean:
        return "", clean
    author, title = clean.split(". ", 1)
    return author.strip(), title.strip()


def link_reference_titles(
    references: list[str],
    source_markdown: str,
    *,
    resolver: VerifiedReferenceResolver | None = None,
) -> list[str]:
    """Link citations only after an authoritative provider confirms their identity."""
    verifier = resolver or VerifiedReferenceResolver()
    candidates = _reference_candidates(source_markdown)
    linked: list[str] = []
    for reference in references:
        author, title = _title_parts(reference)
        candidate = _best_candidate(title, candidates)
        citation_with_identity = reference if _identity(reference)[0] else candidate
        verified = verifier.resolve(title=title, citation=citation_with_identity)
        prefix = f"{author}. " if author else ""
        if verified is None:
            linked.append(f"{prefix}{title}.（未解析）")
            continue
        linked.append(f"{prefix}[{title}]({verified.url}).")
    return linked
