"""Resolve the on-disk asset bundle for one arXiv paper."""

from __future__ import annotations

import re
from pathlib import Path

from config import settings


_ARXIV_ID_RE = re.compile(r"^(?P<arxiv_id>\d{4}\.\d{4,5})(?:v\d+)?")


def normalize_arxiv_id(value: str) -> str:
    """Return a version-free arXiv ID from an ID, URL, or folder name."""
    clean = str(value).strip().rstrip("/").rsplit("/", 1)[-1]
    if clean.endswith(".pdf"):
        clean = clean[:-4]
    match = _ARXIV_ID_RE.match(clean)
    return match.group("arxiv_id") if match else clean.split("_", 1)[0]


def paper_id_from_folder(folder_name: str) -> str:
    """Extract the arXiv ID from ``{id}`` or ``{id}_{chinese_title}``."""
    return normalize_arxiv_id(folder_name)


def sanitize_folder_title(title: str, max_len: int = 80) -> str:
    """Make a title safe for a Windows folder while preserving Chinese text."""
    safe = re.sub(r'[/\\:*?"<>|]', "", str(title))
    safe = re.sub(r"\s+", "_", safe).strip("._-")
    return safe[:max_len].rstrip("._-")


def find_paper_bundle(arxiv_id: str) -> Path | None:
    """Find an existing parsed asset directory for the paper."""
    paper_id = normalize_arxiv_id(arxiv_id)
    parsed_root = settings.DATA_DIR / "parsed"
    exact = parsed_root / paper_id
    if exact.is_dir():
        return exact

    titled = sorted(path for path in parsed_root.glob(f"{paper_id}_*") if path.is_dir())
    return titled[0] if titled else None


def resolve_paper_bundle(
    arxiv_id: str,
    title: str = "",
    *,
    create: bool = False,
) -> Path:
    """Return the existing bundle or the canonical path for a new bundle."""
    existing = find_paper_bundle(arxiv_id)
    if existing is not None:
        return existing

    paper_id = normalize_arxiv_id(arxiv_id)
    safe_title = sanitize_folder_title(title)
    folder_name = f"{paper_id}_{safe_title}" if safe_title else paper_id
    bundle = settings.DATA_DIR / "parsed" / folder_name
    if create:
        bundle.mkdir(parents=True, exist_ok=True)
    return bundle


def find_parsed_markdown(arxiv_id: str) -> Path | None:
    """Find the primary Markdown produced for a paper asset bundle."""
    paper_id = normalize_arxiv_id(arxiv_id)
    bundle = find_paper_bundle(paper_id)
    if bundle is None:
        return None

    canonical = bundle / f"{paper_id}.md"
    if canonical.is_file():
        return canonical

    markdown_files = sorted(bundle.glob("*.md"))
    return markdown_files[0] if markdown_files else None


def find_bundle_pdf(arxiv_id: str) -> Path | None:
    """Find either the canonical PDF or MinerU's ``*_origin.pdf`` file."""
    paper_id = normalize_arxiv_id(arxiv_id)
    bundle = find_paper_bundle(paper_id)
    if bundle is None:
        return None

    canonical = bundle / f"{paper_id}.pdf"
    if canonical.is_file():
        return canonical

    origin_files = sorted(bundle.glob("*_origin.pdf"))
    if origin_files:
        return origin_files[0]

    pdf_files = sorted(bundle.glob("*.pdf"))
    return pdf_files[0] if pdf_files else None


def summary_path(arxiv_id: str) -> Path:
    """Return the canonical DeepSeek Markdown summary path."""
    paper_id = normalize_arxiv_id(arxiv_id)
    return settings.DATA_DIR / "summaries" / f"{paper_id}_summary.md"
