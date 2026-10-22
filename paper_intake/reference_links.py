from __future__ import annotations

import gzip
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence
from urllib.parse import quote

import requests

from .article import ReferenceChoice
from .reference_candidates import ReferenceCandidate, select_latest
from .retry import request_with_retry


class ReferenceClients(Protocol):
    def verified_arxiv_ids(self, arxiv_ids: list[str]) -> set[str]: ...

    def doi_exists(self, doi: str) -> bool: ...


class ArxivCrossrefClients:
    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.trust_env = False

    def verified_arxiv_ids(self, arxiv_ids: list[str]) -> set[str]:
        unique = list(dict.fromkeys(arxiv_ids))
        if not unique:
            return set()

        def fetch():
            response = self.session.get(
                "https://export.arxiv.org/api/query",
                params={"id_list": ",".join(unique)},
                timeout=(10, 30),
            )
            response.raise_for_status()
            return response

        response = request_with_retry(fetch)
        root = ET.fromstring(response.content)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        verified: set[str] = set()
        for entry in root.findall("atom:entry", namespace):
            identifier = entry.findtext("atom:id", default="", namespaces=namespace)
            match = re.search(r"/abs/([^v]+)(?:v\d+)?$", identifier)
            if match:
                verified.add(match.group(1))
        return verified & set(unique)

    def doi_exists(self, doi: str) -> bool:
        def fetch():
            response = self.session.get(
                f"https://api.crossref.org/works/{quote(doi, safe='')}",
                timeout=(10, 30),
            )
            response.raise_for_status()
            return response

        return request_with_retry(fetch).status_code == 200


@dataclass(frozen=True, slots=True)
class PwcSnapshot:
    by_arxiv: dict[str, str]
    by_doi: dict[str, str]

    def code_url_for(self, *, arxiv_id: str | None, doi: str | None) -> str | None:
        if arxiv_id and arxiv_id in self.by_arxiv:
            return self.by_arxiv[arxiv_id]
        if doi and doi.casefold() in self.by_doi:
            return self.by_doi[doi.casefold()]
        return None


def _github_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    url = value.strip()
    if re.match(r"^https://github\.com/[^/]+/[^/]+", url, flags=re.IGNORECASE):
        return url
    return None


def _snapshot_records(path: Path) -> object:
    raw = path.read_bytes()
    if path.suffix.casefold() == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def load_pwc_snapshot(path: Path, expected_sha256: str) -> PwcSnapshot | None:
    snapshot_path = Path(path)
    if not snapshot_path.is_file() or not re.fullmatch(r"[a-fA-F0-9]{64}", expected_sha256):
        return None
    if hashlib.sha256(snapshot_path.read_bytes()).hexdigest() != expected_sha256.casefold():
        return None
    try:
        records = _snapshot_records(snapshot_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, gzip.BadGzipFile):
        return None
    if not isinstance(records, list):
        return None

    ordered = sorted(
        (item for item in records if isinstance(item, dict)),
        key=lambda item: bool(item.get("is_official")),
        reverse=True,
    )
    by_arxiv: dict[str, str] = {}
    by_doi: dict[str, str] = {}
    for item in ordered:
        repo_url = _github_url(item.get("repo_url"))
        if not repo_url:
            continue
        arxiv_id = item.get("paper_arxiv_id") or item.get("arxiv_id")
        doi = item.get("paper_doi") or item.get("doi")
        if isinstance(arxiv_id, str):
            normalized = re.sub(r"v\d+$", "", arxiv_id.strip(), flags=re.IGNORECASE)
            by_arxiv.setdefault(normalized, repo_url)
        if isinstance(doi, str):
            by_doi.setdefault(doi.strip().casefold(), repo_url)
    return PwcSnapshot(by_arxiv=by_arxiv, by_doi=by_doi)


@dataclass(frozen=True, slots=True)
class ResolvedReference:
    candidate: ReferenceCandidate
    paper_url: str
    code_url: str | None
    link_source: str
    verification_status: str
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    mode: str
    references: list[ResolvedReference]


def resolve_selected_references(
    candidates: Sequence[ReferenceCandidate],
    choices: Sequence[ReferenceChoice] | None,
    clients: ReferenceClients,
    pwc_snapshot: PwcSnapshot | None,
) -> ResolutionResult:
    if not candidates:
        return ResolutionResult(mode="omitted", references=[])

    arxiv_ids = [candidate.arxiv_id for candidate in candidates if candidate.arxiv_id]
    try:
        verified_arxiv = clients.verified_arxiv_ids(arxiv_ids)
    except Exception:
        verified_arxiv = set()

    doi_verification: dict[str, bool] = {}
    for candidate in candidates:
        if not candidate.doi or candidate.doi in doi_verification:
            continue
        try:
            doi_verification[candidate.doi] = bool(clients.doi_exists(candidate.doi))
        except Exception:
            doi_verification[candidate.doi] = False

    by_id = {candidate.ref_id: candidate for candidate in candidates}
    reason_by_id = {choice.ref_id: choice.reason for choice in choices or []}
    chosen_ids = [choice.ref_id for choice in choices or [] if choice.ref_id in by_id]
    fallback = select_latest(candidates, count=len(candidates), excluded_ids=chosen_ids)
    ordered = [by_id[ref_id] for ref_id in chosen_ids] + fallback

    resolved: list[ResolvedReference] = []
    model_resolved = 0
    for candidate in ordered:
        if len(resolved) >= 2:
            break
        if candidate.arxiv_id and candidate.arxiv_id in verified_arxiv:
            paper_url = f"https://arxiv.org/abs/{candidate.arxiv_id}"
            source = "arxiv"
        elif candidate.doi and doi_verification.get(candidate.doi, False):
            paper_url = f"https://doi.org/{candidate.doi}"
            source = "doi"
        else:
            continue

        reason = reason_by_id.get(candidate.ref_id)
        if reason is not None:
            model_resolved += 1
        code_url = (
            pwc_snapshot.code_url_for(arxiv_id=candidate.arxiv_id, doi=candidate.doi)
            if pwc_snapshot
            else None
        )
        resolved.append(
            ResolvedReference(
                candidate=candidate,
                paper_url=paper_url,
                code_url=code_url,
                link_source=source,
                verification_status="verified",
                reason=reason,
            )
        )

    if not resolved:
        return ResolutionResult(mode="omitted", references=[])
    mode = "recommended" if len(resolved) == 2 and model_resolved == 2 else "supplemental"
    return ResolutionResult(mode=mode, references=resolved)
