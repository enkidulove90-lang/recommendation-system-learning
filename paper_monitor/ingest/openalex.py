"""OpenAlex 摄入适配器（设计文档#1/#3/#5）。

主客户端设计推荐 pyalex，此处直接调用 OpenAlex REST API（#5，同一端点），
零额外依赖、便于限额/退避控制。免费 key 走 from_publication_date 退化路径 +
本地去重（设计文档§1/§6 已说明 freemium 现状）。
"""
from __future__ import annotations

import time
from datetime import date, timedelta

import requests

from ..config import log
from .base import IngestAdapter, build_paper


class OpenAlexAdapter(IngestAdapter):
    name = "openalex"
    BASE = "https://api.openalex.org/works"

    def _build_filters(self, since_date: date | None) -> dict:
        if since_date is None:
            since_date = date.today() - timedelta(days=self.cfg.time_window_days)
        since = since_date.isoformat()
        flt = [
            f"from_publication_date:{since}",
            "has_abstract:true",
            "type:article",
            "title_and_abstract.search:recommend",  # 收窄到推荐系统相关性
        ]
        return {"filter": ",".join(flt)}

    def _fetch(self, limit: int, since_date: date | None) -> list:
        params = {
            "search": "recommendation system",
            "sort": "publication_date:desc",
            "per_page": min(self.cfg.per_page, 200),
            "select": "id,doi,ids,title,display_name,abstract_inverted_index,publication_date,authorships,topics,primary_topic,cited_by_count",
            "cursor": "*",
            "mailto": self.cfg.openalex_mailto or "",
        }
        params.update(self._build_filters(since_date))
        headers = {}
        if self.cfg.openalex_api_key:
            headers["Authorization"] = f"Bearer {self.cfg.openalex_api_key}"

        results: list = []
        pages = 0
        while len(results) < limit and pages < 20:
            pages += 1
            resp = requests.get(self.BASE, params=params, headers=headers, timeout=30)
            if resp.status_code == 429:
                log.warning("[openalex] 429 rate limit, backing off 5s")
                time.sleep(5)
                continue
            resp.raise_for_status()
            data = resp.json()
            for w in data.get("results", []):
                results.append(self._map(w))
                if len(results) >= limit:
                    break
            meta = data.get("meta", {})
            next_cursor = meta.get("next_cursor")
            if not next_cursor:
                break
            params["cursor"] = next_cursor
            time.sleep(0.2)  # polite pool 礼貌间隔
        return results[:limit]

    @staticmethod
    def _reconstruct_abstract(inv_idx: dict | None) -> str:
        if not inv_idx:
            return ""
        slots: dict = {}
        for word, positions in inv_idx.items():
            for p in positions:
                slots[p] = word
        return " ".join(slots[i] for i in sorted(slots))

    def _map(self, w: dict) -> object:
        ids = w.get("ids", {}) or {}
        arxiv_raw = ids.get("arxiv")
        arxiv_id = arxiv_raw.split(":")[-1] if arxiv_raw else None

        authors = []
        for a in w.get("authorships", []) or []:
            au = a.get("author", {}) or {}
            affs = [i.get("display_name") for i in (a.get("institutions", []) or []) if i.get("display_name")]
            authors.append({"id": au.get("id"), "name": au.get("display_name"), "affiliations": affs})

        topics = []
        for t in w.get("topics", []) or []:
            sub = t.get("subfield", {}) or {}
            fld = t.get("field", {}) or {}
            dom = t.get("domain", {}) or {}
            topics.append({
                "id": t.get("id"), "display_name": t.get("display_name"), "level": 3,
                "parent_id": sub.get("id"), "parent_display_name": sub.get("display_name"),
            })
            if sub.get("display_name"):
                topics.append({"id": sub.get("id"), "display_name": sub.get("display_name"), "level": 2,
                               "parent_id": fld.get("id"), "parent_display_name": fld.get("display_name")})
            if fld.get("display_name"):
                topics.append({"id": fld.get("id"), "display_name": fld.get("display_name"), "level": 1,
                               "parent_id": dom.get("id"), "parent_display_name": dom.get("display_name")})

        return build_paper(
            source="openalex",
            title=w.get("title") or w.get("display_name", ""),
            abstract=self._reconstruct_abstract(w.get("abstract_inverted_index")),
            publication_date=w.get("publication_date"),
            openalex_id=w.get("id"),
            doi=w.get("doi"),
            arxiv_id=arxiv_id,
            authors=authors,
            topics=topics,
            cited_by_count=w.get("cited_by_count", 0),
            raw=w,
        )

    # ---- 离线 fixture ----
    def _fixture(self, limit: int) -> list:
        base = date.today()
        return [
            build_paper(
                source="openalex", title="Fixture: LLM-based Sequential Recommendation",
                abstract="A large language model approach to sequential recommendation.",
                publication_date=(base - timedelta(days=i)).isoformat(),
                openalex_id=f"https://openalex.org/W100{i}", doi=f"10.1000/fix{i}.doi",
                arxiv_id=f"2401.0000{i}",
                authors=[{"name": f"Author {i}", "affiliations": ["MIT"]}],
                topics=[{"display_name": "recommender systems", "level": 3, "parent_display_name": "information retrieval"}],
                cited_by_count=10 + i,
            )
            for i in range(min(limit, 3))
        ]
