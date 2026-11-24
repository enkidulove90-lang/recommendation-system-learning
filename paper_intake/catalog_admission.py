from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlsplit

import httpx

from .catalog import PaperRecord
from .catalog_identity import normalize_arxiv_id


_ACL_PATH = re.compile(r"^/(\d{4}\.[a-z0-9-]+\.\d+)/?$", re.I)
_ALLOWED_PDF_HOSTS = {"arxiv.org", "www.arxiv.org", "aclanthology.org"}


@dataclass(frozen=True)
class AdmissionDecision:
    status: str
    reason_code: str
    pdf_url: str = ""
    budget_week: str = ""
    budget_domain: str = ""


def candidate_pdf_url(paper: PaperRecord) -> str:
    parsed = urlsplit(paper.paper_url)
    if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_PDF_HOSTS:
        return ""
    arxiv_id = normalize_arxiv_id(paper.arxiv_id)
    if paper.source == "arxiv" and arxiv_id:
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    if paper.source == "acl_anthology" and parsed.hostname == "aclanthology.org":
        match = _ACL_PATH.fullmatch(parsed.path)
        if match:
            return f"https://aclanthology.org/{match.group(1)}.pdf"
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
        return AdmissionDecision("metadata_only", "pdf_url_unavailable")
    if not pdf_probe(pdf_url):
        return AdmissionDecision("metadata_only", "pdf_unverified")
    if not budget_available:
        return AdmissionDecision("deferred_budget", "weekly_quota_exhausted", pdf_url, budget_week, budget_domain)
    return AdmissionDecision("admitted", "verified_pdf", pdf_url, budget_week, budget_domain)
