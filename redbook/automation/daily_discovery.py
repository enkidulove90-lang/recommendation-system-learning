"""Configuration-driven, local-only paper candidate discovery.

This module is intentionally upstream of PDF, GitHub, MinerU, and delivery.
It discovers reproducible candidates and records why they matched; it never
creates a Xiaohongshu draft or a public post.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable

import yaml

from .common import append_jsonl, write_json
from .sources import ArxivSource, PaperRecord, SourceRunner, deduplicate_records


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized[:48] or "query"


def _contains(haystack: str, needle: str) -> bool:
    return needle.casefold() in haystack.casefold()


@dataclass(frozen=True)
class DailyDiscoveryConfig:
    companies: tuple[str, ...]
    universities: tuple[str, ...]
    domains: tuple[str, ...]
    allowed_venues: tuple[str, ...]
    allow_verified_preprint: bool
    max_results_per_query: int = 50
    max_candidate_age_days: int = 90

    @classmethod
    def load(cls, path: Path) -> "DailyDiscoveryConfig":
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        organizations = dict(value.get("candidate_organizations", {}))
        venue_gate = dict(value.get("venue_gate", {}))
        discovery = dict(value.get("discovery", {}))
        return cls(
            companies=tuple(str(item) for item in organizations.get("companies", []) if str(item).strip()),
            universities=tuple(str(item) for item in organizations.get("universities", []) if str(item).strip()),
            domains=tuple(str(item) for item in value.get("candidate_domains", []) if str(item).strip()),
            allowed_venues=tuple(str(item) for item in venue_gate.get("allowed", []) if str(item).strip()),
            allow_verified_preprint=bool(venue_gate.get("allow_verified_preprint", False)),
            max_results_per_query=int(discovery.get("arxiv_max_results_per_query", 50)),
            max_candidate_age_days=int(discovery.get("max_candidate_age_days", 90)),
        )

    def query_specs(self) -> list[dict[str, str | int]]:
        specs: list[dict[str, str | int]] = []
        for domain in self.domains:
            specs.append({"scope": "domain", "term": domain, "search_query": f'all:"{domain}"', "max_results": self.max_results_per_query})
        # Organization-name matches are discovery hints only. arXiv Atom metadata
        # lacks authoritative affiliation data, so qualification must verify the
        # affiliation from the paper/PDF before a candidate can be selected.
        for organization in (*self.companies, *self.universities):
            specs.append({"scope": "organization_hint", "term": organization, "search_query": f'all:"{organization}"', "max_results": self.max_results_per_query})
        return specs


def filter_candidates(records: list[PaperRecord], config: DailyDiscoveryConfig) -> list[PaperRecord]:
    """Keep configured discovery matches and attach transparent match evidence."""
    filtered: list[PaperRecord] = []
    organizations = (*config.companies, *config.universities)
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.max_candidate_age_days)
    for record in records:
        try:
            published = datetime.fromisoformat(str(record.published_at).replace("Z", "+00:00"))
        except ValueError:
            continue
        if published < cutoff:
            continue
        searchable = " ".join((record.title, record.abstract, *(str(author.get("name", "")) for author in record.authors)))
        query_scope = str(record.provenance.get("candidate_scope", ""))
        query_term = str(record.provenance.get("arxiv_query", ""))
        matched_domains = [domain for domain in config.domains if _contains(searchable, domain)]
        matched_organizations = [organization for organization in organizations if _contains(searchable, organization)]
        if query_scope == "domain" and query_term:
            matched_domains = list(dict.fromkeys([*matched_domains, query_term.removeprefix('all:"').removesuffix('"')]))
        if query_scope == "organization_hint" and query_term:
            matched_organizations = list(dict.fromkeys([*matched_organizations, query_term.removeprefix('all:"').removesuffix('"')]))
        if not matched_domains and not matched_organizations:
            continue
        venue_name = str(record.venue.get("name", ""))
        venue_match = any(_contains(venue_name, venue) for venue in config.allowed_venues)
        preprint_allowed = config.allow_verified_preprint and record.venue.get("status") == "preprint"
        if not venue_match and not preprint_allowed:
            continue
        record.provenance["daily_filter"] = {
            "matched_domains": matched_domains,
            "organization_hints": matched_organizations,
            "venue_match": venue_match,
            "requires_affiliation_verification": bool(matched_organizations),
            "requires_official_github_verification": True,
        }
        filtered.append(record)
    return filtered


def apply_daily_hard_gates(
    records: list[PaperRecord], config: DailyDiscoveryConfig, *,
    code_verifier: Callable[[str], dict[str, Any]] | None = None,
    text_fetcher: Callable[[str], str] | None = None,
    pdf_path_resolver: Callable[[PaperRecord], Path | None] | None = None,
) -> tuple[list[PaperRecord], list[dict[str, Any]]]:
    """Apply task-two affiliation/code evidence before a candidate enters a pool.

    Domain candidates do not claim an organization and therefore cannot be
    rejected for missing affiliation metadata.  Organization-hint candidates
    must have a verified match; every candidate needs a verified official-code
    URL.  The underlying gate records each verdict in ``provenance``.
    """
    qualified: list[PaperRecord] = []
    rejected: list[dict[str, Any]] = []
    organizations = (*config.companies, *config.universities)
    for record in records:
        daily_filter = dict(record.provenance.get("daily_filter", {}))
        require_affiliation = bool(daily_filter.get("requires_affiliation_verification"))
        kept, rejected_rows = apply_verification_gates(
            [record], candidate_orgs=organizations,
            require_affiliation=require_affiliation,
            require_code=True, code_verifier=code_verifier,
            text_fetcher=text_fetcher,
            pdf_path_resolver=pdf_path_resolver,
        )
        qualified.extend(kept)
        rejected.extend(rejected_rows)
    return qualified, rejected


def write_candidates_to_pool(
    records: list[PaperRecord], paper_pool: Any, *, exclusions: set[str] | None = None,
) -> dict[str, Any]:
    """Persist already-qualified records through the pool's single write API."""
    added: list[str] = []
    skipped: list[dict[str, Any]] = []
    for record in records:
        result = paper_pool.add_candidate(
            canonical_id=record.record_id,
            arxiv_id=str(record.identifiers.get("arxiv", "")),
            doi=str(record.identifiers.get("doi", "")),
            title=record.title,
            source="daily_discovery",
            exclusions=exclusions,
        )
        if result["added"]:
            added.append(str(result["canonical_id"]))
        else:
            skipped.append(dict(result))
    return {"added": len(added), "added_ids": added, "skipped": skipped}


class DailyDiscoveryRunner:
    """Run the daily arXiv routes and write a reviewable local candidate pool."""

    def __init__(self, data_root: Path, config_path: Path,
                 source_factory: Callable[..., ArxivSource] = ArxivSource,
                 code_verifier: Callable[[str], dict[str, Any]] | None = None,
                 text_fetcher: Callable[[str], str] | None = None,
                 pdf_path_resolver: Callable[[PaperRecord], Path | None] | None = None) -> None:
        self.data_root, self.config_path = data_root, config_path
        self.source_factory, self.code_verifier = source_factory, code_verifier
        self.text_fetcher = text_fetcher
        self.pdf_path_resolver = pdf_path_resolver or self._cached_pdf_path

    def _cached_pdf_path(self, record: PaperRecord) -> Path | None:
        paper_id = str(record.identifiers.get("arxiv", ""))
        if not re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", paper_id):
            return None
        path = self.data_root / "papers" / f"{paper_id}.pdf"
        manifest_path = self.data_root / "papers" / f"{paper_id}.manifest.json"
        if not path.is_file() or not manifest_path.is_file():
            return None
        try:
            if manifest_path.stat().st_size > 16_384:
                return None
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("arxiv_id") != paper_id:
                return None
            if manifest.get("byte_size") != path.stat().st_size:
                return None
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                if handle.read(5) != b"%PDF-":
                    return None
                handle.seek(0)
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != manifest.get("sha256"):
                return None
        except (OSError, UnicodeError, ValueError, TypeError, AttributeError):
            return None
        return path

    def run(self, *, paper_pool: Any | None = None,
            exclusions: set[str] | None = None) -> dict[str, Any]:
        config = DailyDiscoveryConfig.load(self.config_path)
        runner = SourceRunner(self.data_root)
        reports: list[dict[str, Any]] = []
        inputs: list[Path] = []
        for spec in config.query_specs():
            name = f"arxiv-{spec['scope']}-{_slug(str(spec['term']))}"
            report = runner.run(self.source_factory(name=name, max_results=config.max_results_per_query), dict(spec))
            reports.append(report)
            inputs.append(Path(report["raw_path"]))
        all_records: list[PaperRecord] = []
        for path in inputs:
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    all_records.append(PaperRecord.from_dict(json.loads(line)))
        filtered = filter_candidates(deduplicate_records(all_records), config)
        candidates, rejected = apply_daily_hard_gates(
            filtered, config, code_verifier=self.code_verifier,
            text_fetcher=self.text_fetcher,
            pdf_path_resolver=self.pdf_path_resolver,
        )
        output_dir = self.data_root / "discovery" / date.today().isoformat()
        candidate_path = output_dir / "candidates.jsonl"
        candidate_path.unlink(missing_ok=True)
        append_jsonl(candidate_path, [record.as_dict() for record in candidates])
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "mode": "qualified_discovery", "config": str(self.config_path), "query_reports": reports,
            "candidate_count": len(candidates), "candidate_path": str(candidate_path),
            "rejected_candidates": rejected,
            "next_step": "verify public PDF, MinerU, and figures before draft creation",
        }
        if paper_pool is not None:
            manifest["paper_pool"] = write_candidates_to_pool(
                candidates, paper_pool, exclusions=exclusions,
            )
        write_json(manifest_path, manifest)
        return {**manifest, "manifest_path": str(manifest_path)}


# ---- verification gates (task 2: affiliation + official code link) ----------

def extract_affiliations(record: PaperRecord) -> list[str]:
    """Collect affiliation strings from arxiv-source author metadata."""
    affiliations: list[str] = []
    for author in record.authors:
        value = author.get("affiliation") if isinstance(author, dict) else None
        if isinstance(value, str) and value.strip():
            affiliations.append(value.strip())
        elif isinstance(value, list):
            affiliations.extend(str(item).strip() for item in value if str(item).strip())
    return list(dict.fromkeys(affiliations))


def verify_affiliation(record: PaperRecord,
                       candidate_orgs: tuple[str, ...]) -> dict[str, Any]:
    """Three-state affiliation verdict: verified / unverified / mismatch."""
    affiliations = extract_affiliations(record)
    matched = [org for org in candidate_orgs
               if org.strip() and any(
                   re.search(r"(?<![A-Za-z0-9])" + re.escape(org.strip())
                             + r"(?![A-Za-z0-9])", aff, re.IGNORECASE)
                   for aff in affiliations
               )]
    if matched:
        return {"state": "verified", "matched": matched,
                "affiliations": affiliations}
    if not affiliations:
        return {"state": "unverified", "matched": [], "affiliations": [],
                "detail": "no affiliation metadata in source"}
    return {"state": "mismatch", "matched": [],
            "affiliations": affiliations,
            "detail": "affiliations present but none in candidate list"}


def apply_verification_gates(
        records: list[PaperRecord], *,
        candidate_orgs: tuple[str, ...] = (),
        require_affiliation: bool = True,
        require_code: bool = True,
        code_verifier: Callable[[str], dict[str, Any]] | None = None,
        text_fetcher: Callable[[str], str] | None = None,
        pdf_path_resolver: Callable[[PaperRecord], Path | None] | None = None,
) -> tuple[list[PaperRecord], list[dict[str, Any]]]:
    """Hard-gate kept candidates on verified affiliation and code link.

    Rejected candidates are returned with reasons (parked for human review,
    never silently dropped); a ``blocked`` code link parks the candidate, an
    ``unverified`` one simply fails this run and may pass on a retry.
    """
    if code_verifier is None:
        from .code_link_verifier import verify_code_link
        code_verifier = verify_code_link
    from .github_verification import (
        discover_and_verify_official_github, fetch_public_text,
        verify_official_github,
    )
    fetcher = text_fetcher or fetch_public_text
    kept: list[PaperRecord] = []
    rejected: list[dict[str, Any]] = []

    def reject(record: PaperRecord, gate: str, state: str, detail: str) -> None:
        rejected.append({"record_id": record.record_id, "title": record.title,
                         "gate": gate, "state": state, "detail": detail})

    for record in records:
        if require_affiliation:
            verdict = verify_affiliation(record, candidate_orgs)
            if verdict["state"] == "unverified" and pdf_path_resolver is not None:
                from .affiliation_evidence import inspect_first_page

                pdf_path = pdf_path_resolver(record)
                if pdf_path is not None:
                    verdict = inspect_first_page(
                        pdf_path, title=record.title, authors=record.authors,
                        candidate_orgs=candidate_orgs,
                    )
            record.provenance["affiliation_verification"] = verdict
            record.provenance.setdefault("evidence", {}).setdefault("affiliation", []).append(
                {"checked_at": datetime.now(timezone.utc).isoformat(), "source": "author_affiliation_metadata", **verdict})
            if verdict["state"] != "verified":
                reject(record, "affiliation", verdict["state"],
                       verdict.get("detail", ""))
                continue
        if require_code:
            code_url = str(record.urls.get("code") or record.urls.get("github") or "")
            official = (
                verify_official_github(record, code_url, fetcher)
                if code_url else discover_and_verify_official_github(record, fetcher)
            )
            if not official.verified:
                reject(record, "official_github", "unverified", official.reason)
                continue
            code_url = official.repository_url
            record.urls["github"] = code_url
            verdict = code_verifier(code_url)
            record.provenance["code_verification"] = verdict
            record.provenance.setdefault("evidence", {}).setdefault("code", []).append(
                {"checked_at": datetime.now(timezone.utc).isoformat(), "source": "code_link_verifier", **verdict})
            if verdict["state"] == "blocked":
                reject(record, "code", "blocked", verdict["detail"])
                continue
            if verdict["state"] != "verified":
                reject(record, "code", "unverified", verdict["detail"])
                continue
        kept.append(record)
    return kept, rejected
