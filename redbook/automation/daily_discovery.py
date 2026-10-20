"""Configuration-driven, local-only paper candidate discovery.

This module is intentionally upstream of PDF, GitHub, MinerU, and delivery.
It discovers reproducible candidates and records why they matched; it never
creates a Xiaohongshu draft or a public post.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
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


class DailyDiscoveryRunner:
    """Run the daily arXiv routes and write a reviewable local candidate pool."""

    def __init__(self, data_root: Path, config_path: Path, source_factory: Callable[..., ArxivSource] = ArxivSource) -> None:
        self.data_root, self.config_path, self.source_factory = data_root, config_path, source_factory

    def run(self) -> dict[str, Any]:
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
        candidates = filter_candidates(deduplicate_records(all_records), config)
        output_dir = self.data_root / "discovery" / date.today().isoformat()
        candidate_path = output_dir / "candidates.jsonl"
        candidate_path.unlink(missing_ok=True)
        append_jsonl(candidate_path, [record.as_dict() for record in candidates])
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "mode": "discovery_only", "config": str(self.config_path), "query_reports": reports,
            "candidate_count": len(candidates), "candidate_path": str(candidate_path),
            "next_step": "verify venue, author affiliation, official GitHub, PDF, MinerU, and figures before draft creation",
        }
        write_json(manifest_path, manifest)
        return {**manifest, "manifest_path": str(manifest_path)}
