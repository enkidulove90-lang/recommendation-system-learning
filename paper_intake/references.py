from __future__ import annotations

import re
from urllib.parse import quote_plus


_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")
_ARXIV_ID = re.compile(r"(?i)arxiv(?:\s+preprint)?(?:\s+arxiv)?\s*:\s*(\d{4}\.\d{4,5})(?:v\d+)?")
_DOI = re.compile(r"(?i)(?:doi\s*:\s*|https?://doi\.org/)(10\.\d{4,9}/[^\s<>]+)")
_WORD = re.compile(r"[a-z0-9]+")


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


def _source_url(title: str, candidates: list[str]) -> str:
    wanted = _tokens(title)
    best = ""
    best_score = 0.0
    for candidate in candidates:
        available = _tokens(candidate)
        score = len(wanted & available) / max(len(wanted), 1)
        if score > best_score:
            best, best_score = candidate, score
    if best_score >= 0.75:
        arxiv = _ARXIV_ID.search(best)
        if arxiv:
            return f"https://arxiv.org/abs/{arxiv.group(1)}"
        doi = _DOI.search(best)
        if doi:
            return "https://doi.org/" + doi.group(1).rstrip(".,;)")
    return ""


def _title_parts(reference: str) -> tuple[str, str]:
    clean = reference.strip().rstrip(".")
    if ". " not in clean:
        return "", clean
    author, title = clean.split(". ", 1)
    return author.strip(), title.strip()


def link_reference_titles(references: list[str], source_markdown: str) -> list[str]:
    """Link model-selected citations without asking the model to invent URLs."""
    candidates = _reference_candidates(source_markdown)
    linked: list[str] = []
    for reference in references:
        if _MARKDOWN_LINK.search(reference):
            linked.append(reference)
            continue
        author, title = _title_parts(reference)
        url = _source_url(title, candidates)
        if not url:
            url = "https://scholar.google.com/scholar?q=" + quote_plus(title)
        prefix = f"{author}. " if author else ""
        linked.append(f"{prefix}[{title}]({url}).")
    return linked
