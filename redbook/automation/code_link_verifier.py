"""GitHub API code-link verification for the daily hard gate.

Three-state output mirrors the affiliation verifier: ``verified`` (repo
exists), ``blocked`` (repo confirmed absent -- candidate parked, NOT dropped,
human review path stays open), ``unverified`` (network/timeout -- retryable,
candidate not qualified this run). Uses unauthenticated ``repos/{owner}/{repo}``
which fits the 60 req/h budget of a once-per-day gate.
"""
from __future__ import annotations

import re
from typing import Any, Callable

Fetch = Callable[[str, float], int]
"""fetcher(url, timeout) -> HTTP status; injectable for sandbox tests."""

_GITHUB_REPO = re.compile(
    r"^https?://github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)/?(?:\.git)?$")


def parse_github_repo(url: str) -> tuple[str, str] | None:
    match = _GITHUB_REPO.match(url.strip())
    if match is None:
        return None
    return match.group("owner"), match.group("repo")


def verify_code_link(url: str, *, timeout: float = 8.0,
                     fetch: Fetch | None = None) -> dict[str, Any]:
    """Return ``{"state", "detail", "url"}``; never raises."""
    parsed = parse_github_repo(url)
    if parsed is None:
        return {"state": "unverified", "url": url,
                "detail": "not a GitHub repository URL; manual check required"}
    owner, repo = parsed
    api = f"https://api.github.com/repos/{owner}/{repo}"
    if fetch is None:
        fetch = _default_fetch
    try:
        status = fetch(api, timeout)
    except Exception as error:  # timeout / network: retryable, not blocking
        return {"state": "unverified", "url": url,
                "detail": f"{type(error).__name__}: {error}; retry next run"}
    if status == 200:
        return {"state": "verified", "url": url, "detail": f"repos/{owner}/{repo} exists"}
    if status == 404:
        return {"state": "blocked", "url": url,
                "detail": f"repos/{owner}/{repo} not found; human review"}
    return {"state": "unverified", "url": url,
            "detail": f"HTTP {status}; retry next run"}


def _default_fetch(url: str, timeout: float) -> int:
    import urllib.request

    request = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "redbook-sentinel/1",
                                              "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return int(response.status)
