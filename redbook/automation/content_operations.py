"""Canonical paper cards, platform renderers, and auditable review state.

This module is deliberately local-file first.  It cannot publish publicly;
the only platform write it coordinates is a Xiaohongshu ``draft_only`` receipt
created by :mod:`redbook.cli`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .common import stable_hash, utc_now, write_json


class ContentOperationError(RuntimeError):
    """The paper card or lifecycle record is not safe to advance."""


CARD_VERSION = 1
XHS_DEFAULT_ANGLE = "research_evidence"
REVIEW_TRANSITIONS = {
    "discovered": {"qualified", "rejected"},
    "qualified": {"evidence_ready", "rejected"},
    "evidence_ready": {"draft_ready", "rejected"},
    "draft_ready": {"staged", "needs_correction", "rejected"},
    "staged": {"approved", "needs_correction", "rejected"},
    "approved": {"published"},
    "needs_correction": {"evidence_ready", "draft_ready", "rejected"},
    "rejected": set(),
    "published": {"observed_2h"},
    "observed_2h": {"observed_24h"},
    "observed_24h": {"observed_7d"},
    "observed_7d": {"observed_30d"},
    "observed_30d": set(),
}


def _as_path(value: object) -> Path:
    return Path(str(value or ""))


def card_content_hash(card: dict[str, Any]) -> str:
    """Hash only facts and content-affecting assets, never mutable receipts."""
    stable = {
        "schema_version": card.get("schema_version"), "paper_id": card.get("paper_id"),
        "identity": card.get("identity"), "links": card.get("links"),
        "evidence": card.get("evidence"), "assets": card.get("assets"),
        "strategy": card.get("strategy"),
    }
    return stable_hash(json.dumps(stable, ensure_ascii=False, sort_keys=True))


class PaperCardStore:
    """Own one durable, validated fact card per paper."""

    @staticmethod
    def path_for(data_root: Path, paper_id: str) -> Path:
        return data_root / "workflow_state" / paper_id.removeprefix("arxiv:") / "paper_card.json"

    @staticmethod
    def validate(card: dict[str, Any], *, require_delivery_assets: bool = False) -> list[str]:
        errors: list[str] = []
        if card.get("schema_version") != CARD_VERSION:
            errors.append("unsupported paper_card schema_version")
        if not str(card.get("paper_id", "")).strip():
            errors.append("paper_id is required")
        identity = dict(card.get("identity", {}))
        if not str(identity.get("title", "")).strip():
            errors.append("identity.title is required")
        links = dict(card.get("links", {}))
        for key in ("landing", "pdf", "official_github"):
            if not str(links.get(key, "")).strip():
                errors.append(f"links.{key} is required")
        eligibility = dict(card.get("eligibility", {}))
        for key in ("official_github_verified", "venue_verified", "mineru_verified"):
            if eligibility.get(key) is not True:
                errors.append(f"eligibility.{key} must be true")
        figures = list(dict(card.get("assets", {})).get("figures", []))
        if int(eligibility.get("high_resolution_figure_count", 0)) < 4 or len(figures) < 4:
            errors.append("at least four qualified figures are required")
        if not eligibility.get("eligible", False):
            errors.append("eligibility.eligible must be true")
        strategy = dict(card.get("strategy", {}))
        if strategy.get("platform", "xiaohongshu") != "xiaohongshu":
            errors.append("only xiaohongshu is a supported production delivery platform")
        if strategy.get("angle", XHS_DEFAULT_ANGLE) not in {"research_evidence", "implementation", "industry", "learning"}:
            errors.append("unsupported strategy angle")
        if not list(strategy.get("topics", [])):
            errors.append("at least one real-topic candidate is required")
        evidence = dict(card.get("evidence", {}))
        if not any(list(evidence.get(key, [])) for key in ("problem", "contributions", "method", "results")):
            errors.append("evidence must contain at least one factual claim")
        if require_delivery_assets:
            assets = dict(card.get("assets", {}))
            for key in ("local_pdf", "mineru_markdown"):
                if not _as_path(assets.get(key)).is_file():
                    errors.append(f"assets.{key} must be an existing local file")
            for figure in figures:
                path = _as_path(figure.get("path") if isinstance(figure, dict) else figure)
                if not path.is_file():
                    errors.append(f"missing figure asset: {path}")
        return errors

    def create_from_manifest(self, manifest_path: Path, *, title: str | None = None,
                             topics: tuple[str, ...] = (), evidence: dict[str, list[str]] | None = None) -> dict[str, Any]:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifacts = dict(manifest.get("local_artifacts", {}))
        links = dict(manifest.get("links", {}))
        paper_id = str(manifest.get("paper_id", ""))
        card = {
            "schema_version": CARD_VERSION,
            "paper_id": paper_id,
            "identity": {"title": str(title or manifest.get("title") or paper_id), "authors": [], "organizations": [],
                         "venue": {"name": "", "year": 0, "status": str(manifest.get("venue_verification", "preprint"))}},
            "provenance": {"source_records": [{"type": "selection_manifest", "path": str(manifest_path)}],
                           "verified_at": utc_now(), "verifier": "selection_manifest_migration"},
            "links": {"landing": str(links.get("paper", "")), "pdf": str(links.get("pdf", "")),
                      "official_github": str(links.get("github", ""))},
            "evidence": evidence or {"problem": ["See the attached local MinerU evidence pack."], "contributions": [],
                                       "method": [], "benchmarks": [], "experimental_conditions": [], "results": [], "limitations": []},
            "assets": {"local_pdf": str(artifacts.get("pdf", "")), "mineru_markdown": str(artifacts.get("mineru_markdown", "")),
                       "figures": list(manifest.get("selected_figures", []))},
            "eligibility": {"official_github_verified": bool(links.get("github")), "venue_verified": bool(manifest.get("venue_verification")),
                            "mineru_verified": bool(artifacts.get("mineru_markdown")),
                            "high_resolution_figure_count": len(manifest.get("selected_figures", [])), "eligible": False, "reasons": []},
            "strategy": {"platform": "xiaohongshu", "angle": XHS_DEFAULT_ANGLE,
                         "topics": list(topics or tuple(manifest.get("topics", ())))},
            "delivery": {"mode": "draft_only", "state": "discovered"},
        }
        errors = self.validate(card)
        card["eligibility"]["eligible"] = not errors
        card["eligibility"]["reasons"] = errors
        card["content_hash"] = card_content_hash(card)
        return card

    def write(self, path: Path, card: dict[str, Any]) -> Path:
        errors = self.validate(card)
        if errors:
            raise ContentOperationError("invalid paper_card: " + "; ".join(errors))
        card = dict(card)
        card["content_hash"] = card_content_hash(card)
        write_json(path, card)
        return path

    @staticmethod
    def load(path: Path, *, require_delivery_assets: bool = False) -> dict[str, Any]:
        card = json.loads(path.read_text(encoding="utf-8"))
        errors = PaperCardStore.validate(card, require_delivery_assets=require_delivery_assets)
        if errors:
            raise ContentOperationError("invalid paper_card: " + "; ".join(errors))
        if card.get("content_hash") != card_content_hash(card):
            raise ContentOperationError("paper_card content_hash does not match its facts and assets")
        return card


class ReviewQueue:
    """Append-only state record; public publishing is intentionally absent."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, paper_id: str) -> Path:
        return self.root / "review_queue" / f"{paper_id.removeprefix('arxiv:')}_review.json"

    def create(self, card_path: Path, card: dict[str, Any]) -> dict[str, Any]:
        path = self.path_for(str(card["paper_id"]))
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("content_hash") != card["content_hash"]:
                raise ContentOperationError("paper content changed; create a new review record after correction")
            return existing
        record = {"paper_id": card["paper_id"], "paper_card": str(card_path), "content_hash": card["content_hash"],
                  "platform": "xiaohongshu", "state": "discovered", "history": [{"state": "discovered", "at": utc_now()}]}
        write_json(path, record)
        return record

    def transition(self, paper_id: str, state: str, **details: Any) -> dict[str, Any]:
        path = self.path_for(paper_id)
        if not path.is_file():
            raise ContentOperationError("review record does not exist")
        record = json.loads(path.read_text(encoding="utf-8"))
        current = str(record.get("state"))
        if state not in REVIEW_TRANSITIONS.get(current, set()):
            raise ContentOperationError(f"invalid review transition: {current} -> {state}")
        record["state"] = state
        record["history"].append({"state": state, "at": utc_now(), **details})
        write_json(path, record)
        return record


class XiaohongshuPaperRenderer:
    """Render one factual, angle-selected draft from a paper card only."""

    @staticmethod
    def render(card: dict[str, Any]) -> dict[str, Any]:
        identity, evidence, links, strategy = (dict(card[key]) for key in ("identity", "evidence", "links", "strategy"))
        def section(key: str, fallback: str) -> str:
            values = [str(value).strip() for value in evidence.get(key, []) if str(value).strip()]
            return "\n".join(f"• {value}" for value in values) if values else f"• {fallback}"
        title = str(identity["title"])[:20]
        body = "\n\n".join((
            "📌 这篇论文解决什么？\n" + section("problem", "原文未披露可直接转述的问题定义。"),
            "✨ 核心贡献\n" + section("contributions", "请结合论文原文与图表核对。"),
            "🧩 方法与实验\n" + section("method", "方法细节以原文为准。") + "\n" + section("results", "结果以论文报告为准。"),
            "⚠️ 阅读边界\n" + section("limitations", "不将论文内实验直接外推到所有真实场景。"),
            f"📎 论文：{links['landing']}\nPDF：{links['pdf']}\n官方 GitHub：{links['official_github']}",
        ))
        return {"title": title, "body": body, "topics": list(strategy["topics"]), "publication_state": "draft_only",
                "source": {"paper_card": card["paper_id"], "content_hash": card["content_hash"]}}
