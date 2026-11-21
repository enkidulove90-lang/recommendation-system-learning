"""Evidence-first verification for an official paper GitHub repository.

The verifier is deliberately independent of delivery.  It operates on the
normalized resource-layer ``PaperRecord`` and receives its fetch function from
the caller so tests and scheduled discovery can control network access.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Callable
from urllib.parse import urlparse

from .sources import PaperRecord


TextFetcher = Callable[[str], str]
_GITHUB_REPOSITORY_PATTERN = re.compile(
    r"https?://github\.com/([^\s/#?\"'<>]+)/([^\s/#?\"'<>]+)", re.IGNORECASE
)


def fetch_public_text(url: str) -> str:
    """Fetch only the public landing text needed for repository identity checks."""
    import requests

    response = requests.get(url, headers={"User-Agent": "redbook-paper-monitor/1.0"}, timeout=10)
    response.raise_for_status()
    return response.text[:1_000_000]


def normalize_github_repository(url: str) -> str:
    """Return the canonical repository URL, rejecting paths below a repository."""
    parsed = urlparse(str(url).strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc.casefold() != "github.com":
        return ""
    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) != 2:
        return ""
    owner, repository = segments
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+", repository):
        return ""
    return f"https://github.com/{owner}/{repository.removesuffix('.git')}"


def _paper_names_repository(text: str, repository_url: str) -> bool:
    canonical = normalize_github_repository(repository_url)
    for match in _GITHUB_REPOSITORY_PATTERN.finditer(text):
        linked = normalize_github_repository(match.group(0).rstrip(".,;:)]}\"'"))
        if linked and linked.casefold() == canonical.casefold():
            return True
    return False


def _repositories_in_text(text: str) -> list[str]:
    repositories: list[str] = []
    for match in _GITHUB_REPOSITORY_PATTERN.finditer(text):
        repository = normalize_github_repository(match.group(0).rstrip(".,;:)]}\"'"))
        if repository and repository.casefold() not in {item.casefold() for item in repositories}:
            repositories.append(repository)
    return repositories


def _title_tokens(title: str) -> list[str]:
    ignored = {"a", "an", "and", "for", "of", "the", "to", "with"}
    return [token.casefold() for token in re.findall(r"[A-Za-z0-9]+", title) if len(token) >= 4 and token.casefold() not in ignored]


@dataclass(frozen=True)
class OfficialGithubVerification:
    repository_url: str
    paper_url: str
    paper_names_repository: bool
    repository_reachable: bool
    repository_matches_title: bool
    repository_mentions_author: bool
    verified: bool
    reason: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def verify_official_github(
    record: PaperRecord, github_url: str, fetch_text: TextFetcher,
) -> OfficialGithubVerification:
    """Verify paper-declared ownership, availability, and repository identity.

    A supplied URL alone never passes: the paper landing page must identify the
    same canonical repository and its public landing page must contain both a
    title signal and the first author's surname.  The result is embedded in
    ``record.provenance`` so a candidate queue can retain the evidence without
    ever invoking the publishing adapter.
    """
    repository_url = normalize_github_repository(github_url)
    paper_url = str(record.urls.get("landing", "")).strip()
    if not repository_url:
        result = OfficialGithubVerification("", paper_url, False, False, False, False, False, "invalid GitHub repository URL")
    elif not paper_url:
        result = OfficialGithubVerification(repository_url, "", False, False, False, False, False, "paper landing URL is missing")
    else:
        try:
            paper_text = fetch_text(paper_url)
        except Exception as error:
            result = OfficialGithubVerification(repository_url, paper_url, False, False, False, False, False, f"paper landing fetch failed: {type(error).__name__}")
        else:
            named = _paper_names_repository(paper_text, repository_url)
            try:
                repository_text = fetch_text(repository_url)
            except Exception as error:
                result = OfficialGithubVerification(repository_url, paper_url, named, False, False, False, False, f"repository fetch failed: {type(error).__name__}")
            else:
                lowered = repository_text.casefold()
                title_tokens = _title_tokens(record.title)
                title_match = bool(title_tokens) and sum(token in lowered for token in title_tokens) >= min(3, len(title_tokens))
                first_author = str(record.authors[0].get("name", "")).split()[-1:] if record.authors else []
                author_match = bool(first_author and first_author[0].casefold() in lowered)
                verified = named and title_match and author_match
                reason = "verified" if verified else "paper/repository identity evidence is incomplete"
                result = OfficialGithubVerification(repository_url, paper_url, named, True, title_match, author_match, verified, reason)
    record.provenance["official_github_verification"] = result.as_dict()  # type: ignore[assignment]
    return result


def discover_and_verify_official_github(
    record: PaperRecord, fetch_text: TextFetcher,
) -> OfficialGithubVerification:
    """Discover paper-declared GitHub links then verify one against the record.

    This is the resource-layer entry point for daily candidates: callers only
    provide a ``PaperRecord`` with its paper landing URL, rather than a
    hand-copied repository URL.  A link is promoted to ``urls['github']`` only
    when the full verifier accepts it.
    """
    paper_url = str(record.urls.get("landing", "")).strip()
    if not paper_url:
        return verify_official_github(record, "", fetch_text)
    try:
        paper_text = fetch_text(paper_url)
    except Exception as error:
        result = OfficialGithubVerification("", paper_url, False, False, False, False, False, f"paper landing fetch failed: {type(error).__name__}")
        record.provenance["official_github_verification"] = result.as_dict()  # type: ignore[assignment]
        return result
    repositories = _repositories_in_text(paper_text)
    record.provenance["official_github_candidates"] = repositories  # type: ignore[assignment]
    if not repositories:
        return verify_official_github(record, "", lambda url: paper_text if url == paper_url else fetch_text(url))
    cached_fetcher = lambda url: paper_text if url == paper_url else fetch_text(url)
    results = [verify_official_github(record, repository, cached_fetcher) for repository in repositories]
    verified = next((result for result in results if result.verified), results[0])
    if verified.verified:
        record.urls["github"] = verified.repository_url
    return verified
