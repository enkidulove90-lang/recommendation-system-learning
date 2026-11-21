"""Conservative affiliation evidence from an already downloaded PDF first page.

This module does not download PDFs. The discovery caller supplies a local file;
unreadable or ambiguous first pages remain unverified.
"""

from __future__ import annotations

from pathlib import Path
import re
import unicodedata
from typing import Any

import fitz


def _identity_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return "".join(char for char in value if char.isalnum())


def _contains_named_org(text: str, organization: str) -> bool:
    organization = organization.strip()
    if not organization:
        return False
    return bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(organization)
                          + r"(?![A-Za-z0-9])", text, re.IGNORECASE))


def inspect_first_page(
    pdf_path: Path, *, title: str, authors: list[dict[str, Any]],
    candidate_orgs: tuple[str, ...],
) -> dict[str, Any]:
    """Verify title, an author, and a named institution before the abstract.

    A title mismatch or a PDF with no recognizable abstract boundary cannot
    establish an author-affiliation relationship and stays unverified.
    """
    verdict: dict[str, Any] = {
        "state": "unverified", "source": "pdf_first_page", "matched": [],
        "detail": "first-page affiliation evidence unavailable",
    }
    try:
        with fitz.open(pdf_path) as document:
            if not document.page_count:
                return verdict
            lines = [line.strip() for line in document[0].get_text("text", sort=True).splitlines()]
    except (OSError, ValueError, RuntimeError, fitz.FileDataError):
        return verdict

    boundary = next((index for index, line in enumerate(lines)
                     if re.match(r"^abstract\b", line, re.IGNORECASE)), None)
    if boundary is None:
        return verdict
    front_matter = " ".join(lines[:boundary])
    compact_front = _identity_text(front_matter)
    title_key = _identity_text(title)
    author_keys = [_identity_text(str(author.get("name", "")))
                   for author in authors if isinstance(author, dict)]
    if not title_key or title_key not in compact_front:
        verdict["detail"] = "first-page title mismatch"
        return verdict
    if not any(key and key in compact_front for key in author_keys):
        verdict["detail"] = "first-page author mismatch"
        return verdict
    matched = [org for org in candidate_orgs if _contains_named_org(front_matter, org)]
    if matched:
        verdict.update(state="verified", matched=matched, detail="title, author and organization matched")
    return verdict
