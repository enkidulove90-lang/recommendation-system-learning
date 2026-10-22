from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence


RELATED_READING_START = "<!-- related-reading:start -->"
RELATED_READING_END = "<!-- related-reading:end -->"

_REFERENCE_HEADING = re.compile(
    r"(?im)^#{1,6}\s*(?:references|参考文献)\s*$"
)
_NEXT_HEADING = re.compile(r"(?m)^#{1,6}\s+.+$")
_GENERATED_BLOCK = re.compile(
    rf"(?ms)^\s*{re.escape(RELATED_READING_START)}.*?"
    rf"{re.escape(RELATED_READING_END)}\s*$"
)
_MODERN_ARXIV = re.compile(
    r"(?i)(?:arxiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})(?:v\d+)?"
)
_LEGACY_ARXIV = re.compile(
    r"(?i)(?:arxiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)"
    r"([a-z][a-z0-9.-]+/\d{7})(?:v\d+)?"
)
_DOI = re.compile(r"(?i)(?:doi\s*:\s*|https?://(?:dx\.)?doi\.org/)(10\.\d{4,9}/\S+)")
_YEAR = re.compile(r"\b((?:19|20)\d{2})[a-z]?\b", re.IGNORECASE)


@dataclass(frozen=True)
class ReferenceCandidate:
    ref_id: str
    raw_text: str
    title: str
    year: int | None
    arxiv_id: str | None
    doi: str | None
    original_index: int


def strip_generated_related_reading(markdown: str) -> str:
    return _GENERATED_BLOCK.sub("", markdown).rstrip() + ("\n" if markdown else "")


def _normalize_markdown(markdown: str) -> str:
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip() for line in normalized.split("\n"))
    return normalized.strip() + "\n"


def source_hash(markdown: str) -> str:
    normalized = _normalize_markdown(strip_generated_related_reading(markdown))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _reference_body(markdown: str) -> str:
    heading = _REFERENCE_HEADING.search(markdown)
    if not heading:
        return ""
    body = markdown[heading.end() :]
    next_heading = _NEXT_HEADING.search(body)
    return body[: next_heading.start()] if next_heading else body


def _normalize_entry(block: str) -> str:
    text = re.sub(r"\s+", " ", block).strip()
    return re.sub(r"^(?:[-*+]\s+|\[?\d+\]?\s*[.)]\s*)", "", text)


def _extract_title(raw_text: str, year_match: re.Match[str] | None) -> str:
    remainder = raw_text[year_match.end() :] if year_match else raw_text
    remainder = remainder.lstrip(" .:-")
    boundary = re.search(
        r"(?i)\.\s+(?:preprint\b|arxiv\b|in\s+proceedings\b|proceedings\b|"
        r"journal\b|https?://|doi\b)",
        remainder,
    )
    title = remainder[: boundary.start()] if boundary else remainder
    title = _MODERN_ARXIV.sub("", title)
    title = _LEGACY_ARXIV.sub("", title)
    title = _DOI.sub("", title)
    return title.strip(" .;:-") or raw_text


def extract_reference_candidates(markdown: str) -> list[ReferenceCandidate]:
    body = _reference_body(markdown)
    if not body:
        return []

    entries = [
        _normalize_entry(block)
        for block in re.split(r"\n\s*\n+", body.strip())
        if block.strip()
    ]
    candidates: list[ReferenceCandidate] = []
    for original_index, raw_text in enumerate(entries):
        modern = _MODERN_ARXIV.search(raw_text)
        legacy = _LEGACY_ARXIV.search(raw_text)
        doi_match = _DOI.search(raw_text)
        arxiv_id = modern.group(1) if modern else legacy.group(1) if legacy else None
        doi = doi_match.group(1).rstrip(".,;:)]}") if doi_match else None
        if not arxiv_id and not doi:
            continue

        year_match = _YEAR.search(raw_text)
        candidates.append(
            ReferenceCandidate(
                ref_id=f"ref_{len(candidates) + 1:03d}",
                raw_text=raw_text,
                title=_extract_title(raw_text, year_match),
                year=int(year_match.group(1)) if year_match else None,
                arxiv_id=arxiv_id,
                doi=doi,
                original_index=original_index,
            )
        )
    return candidates


def candidate_hash(candidates: Sequence[ReferenceCandidate]) -> str:
    payload = json.dumps(
        [asdict(candidate) for candidate in candidates],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _arxiv_yymm(arxiv_id: str | None) -> int:
    if not arxiv_id or not re.fullmatch(r"\d{4}\.\d{4,5}", arxiv_id):
        return -1
    return int(arxiv_id[:4])


def select_latest(
    candidates: Sequence[ReferenceCandidate],
    count: int = 2,
    excluded_ids: Iterable[str] = frozenset(),
) -> list[ReferenceCandidate]:
    excluded = set(excluded_ids)
    eligible = [candidate for candidate in candidates if candidate.ref_id not in excluded]
    ordered = sorted(
        eligible,
        key=lambda candidate: (
            -(candidate.year if candidate.year is not None else -1),
            -_arxiv_yymm(candidate.arxiv_id),
            candidate.original_index,
        ),
    )
    return ordered[: max(count, 0)]
