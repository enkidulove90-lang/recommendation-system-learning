"""GitHub API code-link verification for the daily hard gate.

Three-state output mirrors the affiliation verifier: ``verified`` means only
that the repository is reachable, not that it belongs to the paper. The
paper-declared identity check lives in ``github_verification``. ``blocked``
means confirmed absent; ``unverified`` means missing credentials or a transient
failure. All API requests use GH_TOKEN or GITHUB_TOKEN, never anonymous access.
"""
from __future__ import annotations

import os
from typing import Any, Callable
from urllib.parse import urlparse

from .github_verification import normalize_github_repository

Fetch = Callable[[str, float], int]
"""fetcher(url, timeout) -> HTTP status; injectable for sandbox tests."""

def parse_github_repo(url: str) -> tuple[str, str] | None:
    canonical = normalize_github_repository(url)
    if not canonical:
        return None
    owner, repo = urlparse(canonical).path.strip("/").split("/")
    return owner, repo


class MissingGitHubTokenError(RuntimeError):
    """GitHub verification cannot make an anonymous API request."""


def resolve_github_token() -> str:
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        token = os.environ.get(name, "").strip()
        if token:
            return token
    raise MissingGitHubTokenError("GitHub token is not configured")


def verify_code_link(url: str, *, timeout: float = 8.0,
                     fetch: Fetch | None = None) -> dict[str, Any]:
    """Return ``{"state", "detail", "url"}``; never raises."""
    parsed = parse_github_repo(url)
    if parsed is None:
        return {"state": "unverified", "url": "",
                "detail": "not a GitHub repository URL; manual check required"}
    owner, repo = parsed
    canonical_url = f"https://github.com/{owner}/{repo}"
    api = f"https://api.github.com/repos/{owner}/{repo}"
    if fetch is None:
        fetch = _default_fetch
    try:
        status = fetch(api, timeout)
    except Exception as error:  # timeout / network: retryable, not blocking
        return {"state": "unverified", "url": canonical_url,
                "detail": f"{type(error).__name__}; retry next run"}
    if status == 200:
        return {"state": "verified", "url": canonical_url, "detail": f"repos/{owner}/{repo} exists"}
    if status == 404:
        return {"state": "blocked", "url": canonical_url,
                "detail": f"repos/{owner}/{repo} not found; human review"}
    if status == 401:
        return {"state": "unverified", "url": canonical_url,
                "detail": "GitHub credential rejected; repair token before retry"}
    return {"state": "unverified", "url": canonical_url,
            "detail": f"HTTP {status}; retry next run"}


def _default_fetch(url: str, timeout: float) -> int:
    import urllib.request
    from urllib.error import HTTPError

    token = resolve_github_token()
    request = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "redbook-sentinel/1",
                                              "Accept": "application/vnd.github+json",
                                              "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except HTTPError as error:
        return int(error.code)
