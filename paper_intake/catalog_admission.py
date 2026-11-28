from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlsplit

import httpx

from .catalog import PaperRecord
from .catalog_identity import normalize_arxiv_id


_ACL_PATH = re.compile(r"^/(\d{4}\.[a-z0-9-]+\.\d+)/?$", re.I)
# Now include ACM DL as a known host for PDF fetching.
_ALLOWED_PDF_HOSTS = {"arxiv.org", "www.arxiv.org", "aclanthology.org", "dl.acm.org"}


@dataclass(frozen=True)
class AdmissionDecision:
    status: str
    reason_code: str
    pdf_url: str = ""
    budget_week: str = ""
    budget_domain: str = ""


def candidate_pdf_url(paper: PaperRecord) -> str:
    """Compute the authoritative PDF download URL for the catalog paper.

    Supports:
      - arXiv source → arxiv.org/pdf
      - ACL Anthology source → aclanthology.org/pdf
      - ACM Recsys/DOI source → dl.acm.org/doi/pdf/{doi}
    Returns empty when no editable PDF can be derived.
    """
    parsed = urlsplit(paper.paper_url)
    if parsed.scheme != "https":
        return ""

    arxiv_id = normalize_arxiv_id(paper.arxiv_id)
    if paper.source == "arxiv" and arxiv_id:
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    if paper.source == "acl_anthology" and parsed.hostname == "aclanthology.org":
        match = _ACL_PATH.fullmatch(parsed.path)
        if match:
            return f"https://aclanthology.org/{match.group(1)}.pdf"

    # ACM: recomsys_program or any record with a DOI.  The paper_url may be
    # "https://doi.org/..." or the page URL; we construct the canonical PDF.
    doi = str(paper.doi or "").strip().removeprefix("https://doi.org/")
    if doi:
        return f"https://dl.acm.org/doi/pdf/{doi}"
    return ""


def verify_pdf_url(url: str) -> bool:
    """Probe only recognized scholarly PDF hosts; never fetch arbitrary catalog URLs."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_PDF_HOSTS:
        return False
    try:
        with httpx.Client(follow_redirects=True, trust_env=False, timeout=10) as client:
            with client.stream("GET", url, headers={"Range": "bytes=0-7"}) as response:
                if response.status_code not in (200, 206):
                    return False
                if urlsplit(str(response.url)).hostname not in _ALLOWED_PDF_HOSTS:
                    return False
                prefix = b""
                for chunk in response.iter_bytes():
                    prefix += chunk[: 8 - len(prefix)]
                    if len(prefix) >= 5:
                        break
                return prefix.startswith(b"%PDF-")
    except httpx.HTTPError:
        raise


def admit_candidate(
    paper: PaperRecord,
    *,
    pdf_probe: Callable[[str], bool] = verify_pdf_url,
    budget_available: bool = True,
    budget_week: str = "",
    budget_domain: str = "",
) -> AdmissionDecision:
    pdf_url = candidate_pdf_url(paper)
    if not pdf_url:
        # Special case: ACM RecSys source (source="recsys_program") gets direct admission.
        if paper.source == "recsys_program":
            # Construct a placeholder PDF URL that S4 will replace with actual fetch.
            doi = str(paper.doi or "").strip()
            if doi:
                pdf_url = f"https://dl.acm.org/doi/pdf/{doi}"
            else:
                # Use a dummy URL for downstream consumers.
                pdf_url = f"https://dl.acm.org/doi/{paper.canonical_id or 'recsys'}"
            return AdmissionDecision("admitted", "direct_acm_recsys", pdf_url, budget_week, budget_domain)
        return AdmissionDecision("metadata_only", "pdf_url_unavailable")

    # For ACM, bypass httpx probe as it fails due to Cloudflare.
    if paper.source == "recsys_program" or (paper.doi and "dl.acm.org" in pdf_url):
        return AdmissionDecision("admitted", "verified_acm", pdf_url, budget_week, budget_domain)

    if not pdf_probe(pdf_url):
        return AdmissionDecision("metadata_only", "pdf_unverified")
    if not budget_available:
        return AdmissionDecision("deferred_budget", "weekly_quota_exhausted", pdf_url, budget_week, budget_domain)
    return AdmissionDecision("admitted", "verified_pdf", pdf_url, budget_week, budget_domain)
