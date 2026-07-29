"""
skills/relevance_recommender.py — seed paper driven related-paper recommender.

The existing project already supports topic crawling. This skill adds a
recommendation layer that starts from one seed paper, expands focused arXiv
queries, ranks candidates with transparent heuristics, and writes a reusable
recommendation report for later parsing / summarization / merge steps.
"""

from __future__ import annotations

import json
import logging
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from config import settings
from skills.base_module import BaseSkill, register_skill
from skills.pdf_downloader import PDFDownloader

logger = logging.getLogger(__name__)

ATOM_NS = "http://www.w3.org/2005/Atom"


DEFAULT_RELATED_QUERIES: list[dict[str, str]] = [
    {
        "name": "agent-recommender-systems",
        "query": (
            'all:"agent" AND '
            '(all:"recommendation" OR all:"recommender system") AND '
            "(cat:cs.IR OR cat:cs.AI)"
        ),
        "description": "Agent 技术与推荐系统交叉",
    },
    {
        "name": "llm-recommendation-iteration",
        "query": (
            'all:"large language model" AND '
            '(all:"recommendation" OR all:"recommender system") AND '
            '(all:"ranking" OR all:"rerank" OR all:"evaluation" OR all:"feedback") '
            "AND (cat:cs.IR OR cat:cs.AI OR cat:cs.CL)"
        ),
        "description": "LLM 参与推荐排序、评估和反馈迭代",
    },
    {
        "name": "industrial-recommender-evaluation",
        "query": (
            '(all:"industrial recommender" OR all:"online experiment" OR all:"A/B test") '
            'AND (all:"recommendation" OR all:"recommender system") '
            "AND (cat:cs.IR OR cat:cs.AI)"
        ),
        "description": "工业推荐、在线实验与评估闭环",
    },
    {
        "name": "automated-recommender-research",
        "query": (
            '(all:"automated" OR all:"self-improving" OR all:"self-iteration") '
            'AND (all:"recommendation" OR all:"recommender system") '
            "AND (cat:cs.IR OR cat:cs.AI)"
        ),
        "description": "自动化推荐算法迭代",
    },
]


THEME_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "agent": [
        ("agent", 7.0),
        ("agentic", 7.0),
        ("multi-agent", 7.0),
        ("autonomous", 5.0),
        ("self-iteration", 8.0),
        ("self-improving", 8.0),
    ],
    "recommender": [
        ("recommendation", 8.0),
        ("recommender", 8.0),
        ("ranking", 5.0),
        ("rerank", 5.0),
        ("recall", 4.0),
        ("retrieval", 4.0),
        ("candidate generation", 4.0),
    ],
    "industrial_loop": [
        ("industrial", 6.0),
        ("production", 5.0),
        ("online", 4.0),
        ("a/b", 6.0),
        ("experiment", 5.0),
        ("evaluation", 5.0),
        ("feedback", 5.0),
        ("iteration", 6.0),
        ("launch", 4.0),
    ],
    "llm": [
        ("large language model", 6.0),
        ("llm", 6.0),
        ("language model", 4.0),
        ("deepseek", 2.0),
        ("reasoning", 3.0),
    ],
}


STOPWORDS = {
    "about", "after", "again", "against", "algorithm", "among", "based",
    "between", "could", "framework", "from", "have", "into", "large",
    "learning", "model", "paper", "recommendation", "recommender", "system",
    "systems", "their", "there", "these", "through", "towards", "using",
    "with", "without",
}


@register_skill("related-paper-recommend")
class RelatedPaperRecommender(BaseSkill):
    """
    Find and rank papers related to a seed arXiv paper.

    Inputs:
        seed_arxiv_id: seed paper id, e.g. "2606.26859"
        max_results_per_query: candidates fetched per expanded query
        top_k: recommendations to keep in the report
        download_top_k: whether to download PDF files for top recommendations
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._output_dir = settings.DATA_DIR / "metadata" / "recommendations"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        seed_arxiv_id = str(kwargs.get("seed_arxiv_id", "")).strip()
        max_results_per_query = int(kwargs.get("max_results_per_query", 10))
        top_k = int(kwargs.get("top_k", 8))
        start_year = int(kwargs.get("start_year", settings.START_YEAR))
        download_top_k = bool(kwargs.get("download_top_k", False))
        queries = kwargs.get("queries") or DEFAULT_RELATED_QUERIES

        if not seed_arxiv_id:
            return {"error": "seed_arxiv_id is required.", "results": []}

        seed = self._fetch_by_id(seed_arxiv_id)
        if not seed:
            return {
                "error": f"Seed paper not found on arXiv: {seed_arxiv_id}",
                "results": [],
            }

        logger.info("[Recommend] Seed loaded: %s | %s", seed["arxiv_id"], seed["title"])

        candidates = self._collect_candidates(
            queries=queries,
            max_results_per_query=max_results_per_query,
            start_year=start_year,
        )
        seed_id = self._normalize_arxiv_id(seed_arxiv_id)
        candidates = [
            p for p in candidates
            if self._normalize_arxiv_id(p.get("arxiv_id", "")) != seed_id
        ]

        ranked = self._rank_candidates(seed, candidates)
        top = ranked[:top_k]

        downloaded: list[dict[str, Any]] = []
        if download_top_k:
            downloader = PDFDownloader()
            for paper in top:
                result = downloader.execute(
                    arxiv_id=paper["arxiv_id"],
                    pdf_url=paper.get("pdf_url", ""),
                )
                paper["local_pdf_path"] = result.get("pdf_path")
                downloaded.append(result)

        report_paths = self._save_report(
            seed=seed,
            recommendations=top,
            queries=queries,
            all_candidate_count=len(candidates),
            downloaded=downloaded,
        )

        return {
            "seed": seed,
            "results": top,
            "total_candidates": len(candidates),
            "queries": queries,
            "downloaded": downloaded,
            "report_json_path": str(report_paths["json"]),
            "report_md_path": str(report_paths["markdown"]),
            "error": None,
        }

    def _fetch_by_id(self, arxiv_id: str) -> dict[str, Any] | None:
        try:
            results = self._query_arxiv(
                id_list=[self._normalize_arxiv_id(arxiv_id)],
                max_results=1,
                max_attempts=4,
            )
        except Exception as exc:
            logger.error("[Recommend] Failed to fetch seed %s: %s", arxiv_id, exc)
            return None
        return results[0] if results else None

    def _collect_candidates(
        self,
        queries: list[dict[str, str]],
        max_results_per_query: int,
        start_year: int,
    ) -> list[dict[str, Any]]:
        by_id: dict[str, dict[str, Any]] = {}
        for query_def in queries:
            query = query_def["query"]
            try:
                results = self._query_arxiv(
                    query=query,
                    max_results=max(1, min(max_results_per_query, 20)),
                    max_attempts=3,
                )
            except Exception as exc:
                logger.warning("[Recommend] Query failed | %s | %s", query_def["name"], exc)
                continue

            for paper in results:
                if paper.get("year") and paper["year"] < start_year:
                    continue
                aid = self._normalize_arxiv_id(paper.get("arxiv_id", ""))
                if not aid:
                    continue

                existing = by_id.get(aid)
                if existing:
                    existing.setdefault("matched_queries", []).append(query_def["name"])
                else:
                    paper["matched_queries"] = [query_def["name"]]
                    by_id[aid] = paper

        return list(by_id.values())

    def _query_arxiv(
        self,
        max_attempts: int,
        query: str = "",
        id_list: list[str] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Query the arXiv Atom API with conservative retry behavior.

        Direct API access keeps request size and timeout under our control,
        which is important for interactive CLI usage.
        """
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                params = {
                    "start": "0",
                    "max_results": str(max_results),
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                }
                if id_list:
                    params["id_list"] = ",".join(id_list)
                    params["search_query"] = ""
                else:
                    params["search_query"] = query

                url = f"{settings.ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"
                logger.info("[Recommend] arXiv request: %s", url[:180])
                with httpx.Client(timeout=35.0, follow_redirects=True) as client:
                    resp = client.get(url, headers={"User-Agent": "recommendation-system-learning/1.0"})
                    if resp.status_code == 429:
                        raise RuntimeError(f"HTTP 429 from arXiv: {url}")
                    resp.raise_for_status()
                    return self._parse_atom(resp.text)
            except Exception as exc:
                last_error = exc
                message = str(exc)
                if "429" not in message or attempt == max_attempts:
                    break
                sleep_seconds = min(60, 8 * attempt)
                logger.warning(
                    "[Recommend] arXiv 429; retrying in %ds (attempt %d/%d)",
                    sleep_seconds,
                    attempt + 1,
                    max_attempts,
                )
                time.sleep(sleep_seconds)
        if last_error:
            raise last_error
        return []

    @staticmethod
    def _parse_atom(xml_text: str) -> list[dict[str, Any]]:
        root = ET.fromstring(xml_text)
        papers: list[dict[str, Any]] = []

        for entry in root.findall(f"{{{ATOM_NS}}}entry"):
            entry_id = entry.findtext(f"{{{ATOM_NS}}}id", "")
            if "/abs/" not in entry_id:
                continue

            arxiv_id = RelatedPaperRecommender._normalize_arxiv_id(entry_id.split("/abs/")[-1])
            title = (entry.findtext(f"{{{ATOM_NS}}}title", "") or "").strip()
            abstract = (entry.findtext(f"{{{ATOM_NS}}}summary", "") or "").strip()
            published_raw = (entry.findtext(f"{{{ATOM_NS}}}published", "") or "").strip()
            updated_raw = (entry.findtext(f"{{{ATOM_NS}}}updated", "") or "").strip()
            published = published_raw[:10]
            updated = updated_raw[:10]
            year = int(published[:4]) if published[:4].isdigit() else None
            authors = [
                a.findtext(f"{{{ATOM_NS}}}name", "") or ""
                for a in entry.findall(f"{{{ATOM_NS}}}author")
            ]
            categories = [
                c.attrib.get("term", "")
                for c in entry.findall(f"{{{ATOM_NS}}}category")
                if c.attrib.get("term")
            ]

            papers.append({
                "title": re.sub(r"\s+", " ", title),
                "authors": [a for a in authors if a],
                "abstract": re.sub(r"\s+", " ", abstract),
                "published": published,
                "updated": updated,
                "year": year,
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
                "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                "arxiv_id": arxiv_id,
                "categories": categories,
                "comment": "",
                "primary_category": categories[0] if categories else "",
            })

        return papers

    def _rank_candidates(
        self,
        seed: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        seed_terms = self._important_terms(seed)
        ranked: list[dict[str, Any]] = []

        for paper in candidates:
            score, factors = self._score_candidate(seed_terms, paper)
            if score <= 0:
                continue
            paper["relevance_score"] = round(score, 2)
            paper["relevance_factors"] = factors
            paper["recommendation_reason"] = self._build_reason(factors)
            ranked.append(paper)

        ranked.sort(
            key=lambda p: (
                p.get("relevance_score", 0),
                p.get("published", ""),
                len(p.get("matched_queries", [])),
            ),
            reverse=True,
        )
        return ranked

    @staticmethod
    def _score_candidate(
        seed_terms: set[str],
        paper: dict[str, Any],
    ) -> tuple[float, dict[str, Any]]:
        text = RelatedPaperRecommender._paper_text(paper)
        score = 0.0
        matched_themes: dict[str, list[str]] = {}

        for theme, keywords in THEME_KEYWORDS.items():
            theme_hits: list[str] = []
            for keyword, weight in keywords:
                if keyword in text:
                    score += weight
                    theme_hits.append(keyword)
            if theme_hits:
                matched_themes[theme] = theme_hits

        candidate_terms = RelatedPaperRecommender._important_terms(paper)
        overlap = sorted(seed_terms & candidate_terms)
        overlap_score = min(20.0, len(overlap) * 1.8)
        score += overlap_score

        year = paper.get("year") or 0
        recency_score = max(0.0, min(8.0, (year - 2023) * 2.0))
        score += recency_score

        categories = set(paper.get("categories", []))
        category_score = 0.0
        if "cs.IR" in categories:
            category_score += 8.0
        if "cs.AI" in categories:
            category_score += 4.0
        if "cs.CL" in categories:
            category_score += 2.0
        score += category_score

        matched_query_score = min(8.0, len(paper.get("matched_queries", [])) * 2.5)
        score += matched_query_score

        if "recommendation" not in text and "recommender" not in text:
            score *= 0.35
        if not matched_themes.get("agent") and not matched_themes.get("llm"):
            score *= 0.75

        factors = {
            "matched_themes": matched_themes,
            "seed_term_overlap": overlap[:12],
            "overlap_score": round(overlap_score, 2),
            "recency_score": round(recency_score, 2),
            "category_score": round(category_score, 2),
            "matched_query_score": round(matched_query_score, 2),
            "matched_queries": paper.get("matched_queries", []),
        }
        return score, factors

    @staticmethod
    def _build_reason(factors: dict[str, Any]) -> str:
        themes = factors.get("matched_themes", {})
        parts: list[str] = []
        if "agent" in themes:
            parts.append("覆盖 Agent / 自迭代方向")
        if "recommender" in themes:
            parts.append("与推荐召回/排序/重排直接相关")
        if "industrial_loop" in themes:
            parts.append("包含工业实验、反馈或评估闭环信号")
        if "llm" in themes:
            parts.append("包含 LLM 或推理增强推荐线索")

        overlap = factors.get("seed_term_overlap", [])
        if overlap:
            parts.append("与种子论文关键词重叠: " + ", ".join(overlap[:5]))
        return "；".join(parts) if parts else "与种子论文主题相近"

    @staticmethod
    def _important_terms(paper: dict[str, Any]) -> set[str]:
        text = RelatedPaperRecommender._paper_text(paper)
        words = re.findall(r"[a-z][a-z0-9\-]{3,}", text)
        counts = Counter(w for w in words if w not in STOPWORDS and len(w) > 3)
        return {word for word, freq in counts.items() if freq >= 1}

    @staticmethod
    def _paper_text(paper: dict[str, Any]) -> str:
        parts = [
            paper.get("title", ""),
            paper.get("abstract", ""),
            " ".join(paper.get("categories", [])),
            paper.get("primary_category", ""),
            paper.get("comment", ""),
        ]
        return " ".join(parts).lower()

    @staticmethod
    def _normalize_arxiv_id(arxiv_id: str) -> str:
        clean = arxiv_id.strip().rstrip("/")
        clean = clean.rsplit("/", 1)[-1]
        clean = clean[:-4] if clean.endswith(".pdf") else clean
        return re.sub(r"v\d+$", "", clean)

    def _save_report(
        self,
        seed: dict[str, Any],
        recommendations: list[dict[str, Any]],
        queries: list[dict[str, str]],
        all_candidate_count: int,
        downloaded: list[dict[str, Any]],
    ) -> dict[str, Path]:
        seed_id = seed["arxiv_id"]
        json_path = self._output_dir / f"{seed_id}_recommendations.json"
        md_path = self._output_dir / f"{seed_id}_recommendations.md"

        payload = {
            "generated_at": datetime.now().isoformat(),
            "seed": seed,
            "candidate_count": all_candidate_count,
            "recommendation_count": len(recommendations),
            "queries": queries,
            "recommendations": recommendations,
            "downloaded": downloaded,
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(
            self._build_markdown_report(payload),
            encoding="utf-8",
        )
        logger.info("[Recommend] Report saved: %s | %s", json_path, md_path)
        return {"json": json_path, "markdown": md_path}

    @staticmethod
    def _build_markdown_report(payload: dict[str, Any]) -> str:
        seed = payload["seed"]
        recommendations = payload["recommendations"]
        queries = payload["queries"]

        lines = [
            f"# Related Paper Recommendations for {seed['arxiv_id']}",
            "",
            "## Seed Paper",
            "",
            f"- **Title**: {seed['title']}",
            f"- **arXiv**: [{seed['arxiv_id']}]({seed['arxiv_url']})",
            f"- **Published**: {seed.get('published', '')}; **Updated**: {seed.get('updated', '')}",
            f"- **Categories**: {', '.join(seed.get('categories', []))}",
            f"- **Authors**: {', '.join(seed.get('authors', [])[:8])}",
            "",
            "## Expanded Queries",
            "",
        ]

        for query in queries:
            lines.append(f"- `{query['name']}`: {query['description']}")

        lines.extend([
            "",
            "## Top Recommendations",
            "",
            "| Rank | Score | arXiv | Published | Title | Reason |",
            "|---:|---:|---|---|---|---|",
        ])

        for i, paper in enumerate(recommendations, 1):
            title = paper.get("title", "").replace("|", "\\|")
            reason = paper.get("recommendation_reason", "").replace("|", "\\|")
            lines.append(
                f"| {i} | {paper.get('relevance_score', 0)} | "
                f"[{paper.get('arxiv_id')}]({paper.get('arxiv_url')}) | "
                f"{paper.get('published', '')} | {title} | {reason} |"
            )

        lines.extend([
            "",
            "## Architecture Implications",
            "",
            "1. 将原有固定主题爬取扩展为 `seed paper -> related queries -> candidate pool`，支持围绕某篇关键论文快速补齐上下游研究。",
            "2. 在搜索与下载之间加入可解释排序层，候选论文保留主题命中、关键词重叠、分类和时效性得分，便于后续替换为 DeepSeek rerank。",
            "3. 推荐报告写入 `data/metadata/recommendations/`，作为检索与排序过程的任务清单，不与 DeepSeek 论文摘要混放。",
            "4. 下载和解析解耦：Top-K PDF 可先落盘，MinerU Key 可用时再异步解析全文，避免单点 API 失败阻断推荐发现。",
            "",
            f"_Generated at {payload['generated_at']} from {payload['candidate_count']} unique candidates._",
            "",
        ])
        return "\n".join(lines)
