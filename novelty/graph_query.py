"""
novelty/graph_query.py — 图谱查询模块

设计文档 §1/§3: 以论文 ID 调 Semantic Scholar Graph API 与 OpenAlex 获取
引用/被引邻域及作者/概念标签。本模块:
  - 复用既有 CitationCollector（S2 API，免费无需 Key）采集 references/citations/related；
  - 新增 OpenAlex 适配器（CC0 全开放）补全邻域作品；
  - 统一输出 NeighborPaper 列表，供对比模块使用。

降级: S2/OpenAlex 任一不可用时跳过，绝不阻塞主流程（设计文档 §7 容错）。
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

from .schemas import NeighborPaper, NeighborSource

logger = logging.getLogger(__name__)

OPENALEX_API = "https://api.openalex.org/works"


class GraphQuery:
    def __init__(self, use_s2: bool = True, use_openalex: bool = True,
                 timeout: int = 20) -> None:
        self.use_s2 = use_s2
        self.use_openalex = use_openalex
        self.timeout = timeout

    # ------------------------------------------------------------------
    def query(self, arxiv_id: str, parsed_dir: str = "", metadata: Optional[dict] = None
              ) -> list[NeighborPaper]:
        """返回外部图谱邻域论文（S2 + OpenAlex）。"""
        neighbors: list[NeighborPaper] = []
        if self.use_s2:
            neighbors += self._from_semantic_scholar(arxiv_id, parsed_dir, metadata)
        if self.use_openalex:
            neighbors += self._from_openalex(arxiv_id, metadata)
        # 去重（按 title 归一化）
        seen = set()
        out = []
        for n in neighbors:
            key = n.title.strip().lower()[:120]
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(n)
        logger.info("[GraphQuery] collected %d external neighbors", len(out))
        return out

    # ------------------------------------------------------------------
    def _from_semantic_scholar(self, arxiv_id: str, parsed_dir: str, metadata) -> list[NeighborPaper]:
        try:
            from skills.citation_collector import CitationCollector
        except Exception as exc:
            logger.warning("[GraphQuery] CitationCollector unavailable: %s", exc)
            return []
        try:
            res = CitationCollector().execute(
                arxiv_id=arxiv_id, parsed_dir=parsed_dir, metadata=metadata or {},
                sources=["semantic_scholar"],
            )
        except Exception as exc:
            logger.warning("[GraphQuery] S2 fetch failed: %s", exc)
            return []

        out = []
        for item in (res.get("citations") or [])[:30]:
            out.append(self._mk(item, NeighborSource.SEMANTIC_SCHOLAR, "cited_by"))
        for item in (res.get("references") or [])[:30]:
            out.append(self._mk(item, NeighborSource.SEMANTIC_SCHOLAR, "cites"))
        return out

    @staticmethod
    def _mk(item: dict, src: NeighborSource, relation: str) -> NeighborPaper:
        return NeighborPaper(
            arxiv_id=item.get("arxiv_id", "") or "",
            title=item.get("title", "") or "",
            year=item.get("year"),
            relation=relation,
            similarity=0.0,
            source=src,
            citation_count=item.get("citation_count", 0) or 0,
            url=f"https://arxiv.org/abs/{item['arxiv_id']}" if item.get("arxiv_id") else "",
        )

    # ------------------------------------------------------------------
    def _from_openalex(self, arxiv_id: str, metadata) -> list[NeighborPaper]:
        title = (metadata or {}).get("title", "") if metadata else ""
        if not title:
            return []
        try:
            resp = requests.get(
                OPENALEX_API,
                params={"search": title, "per-page": 15, "select": "title,publication_year,cited_by_count,doi,id"},
                timeout=self.timeout,
                headers={"User-Agent": "RS-NoveltyEngine/0.1"},
            )
            if resp.status_code != 200:
                return []
            data = resp.json().get("results", [])
        except Exception as exc:
            logger.warning("[GraphQuery] OpenAlex fetch failed: %s", exc)
            return []
        out = []
        for w in data[:10]:
            out.append(NeighborPaper(
                arxiv_id="",
                title=w.get("title", "") or "",
                year=w.get("publication_year"),
                relation="similar",
                similarity=0.0,
                source=NeighborSource.OPENALEX,
                citation_count=w.get("cited_by_count", 0) or 0,
                url=w.get("doi") or w.get("id", ""),
            ))
        return out
