"""Semantic Scholar 适配器（设计文档#9）。

取 influentialCitationCount / citationCount 作为"引用影响力"信号。
匿名易 429，故优先使用 S2_API_KEY，命中 429 即退避。
"""
from __future__ import annotations

import time
from datetime import date, timedelta

import requests

from ..config import log
from .base import IngestAdapter, build_paper

BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,abstract,authors,influentialCitationCount,citationCount,externalIds,publicationDate,year"


class SemanticScholarAdapter(IngestAdapter):
    name = "s2"

    def _fetch(self, limit: int, since_date: date | None) -> list:
        params = {
            "query": "recommendation system",
            "fields": FIELDS,
            "limit": min(limit, 100),
            "year": f"{date.today().year-1}-",  # 近一年
        }
        headers = {}
        if self.cfg.s2_api_key:
            headers["x-api-key"] = self.cfg.s2_api_key
        try:
            resp = requests.get(BASE, params=params, headers=headers, timeout=30)
        except requests.RequestException as exc:
            log.warning("[s2] request failed: %s", exc)
            return []
        if resp.status_code == 429:
            log.warning("[s2] 429 rate limit (匿名或超额), 跳过该源")
            return []
        if resp.status_code != 200:
            log.warning("[s2] status %s", resp.status_code)
            return []
        data = resp.json()
        out = []
        for d in data.get("data", []) or []:
            ext = d.get("externalIds", {}) or {}
            arxiv_id = ext.get("ArXiv")
            doi = ext.get("DOI")
            authors = [{"name": a.get("name", "")} for a in (d.get("authors", []) or []) if a.get("name")]
            out.append(build_paper(
                source="s2",
                title=d.get("title", ""),
                abstract=d.get("abstract", "") or "",
                publication_date=d.get("publicationDate"),
                doi=doi,
                arxiv_id=arxiv_id,
                s2_corpus_id=str(d.get("paperId")) if d.get("paperId") else None,
                authors=authors,
                influential_citation_count=d.get("influentialCitationCount"),
                cited_by_count=d.get("citationCount", 0) or 0,
                raw=d,
            ))
        return out[:limit]

    def _fixture(self, limit: int) -> list:
        base = date.today()
        return [
            build_paper(
                source="s2", title=f"Fixture S2: Knowledge Graph Rec {i}",
                abstract="Knowledge-aware recommendation with GNN.",
                publication_date=(base - timedelta(days=i)).isoformat(),
                doi=f"10.1145/fixs2.{i}",
                influential_citation_count=50 + i * 10,
                cited_by_count=120 + i * 15,
            )
            for i in range(min(limit, 3))
        ]
