"""arXiv 实时流适配器（设计文档#6/#8）。

直接调用 arXiv Atom API（export.arxiv.org/api/query，端点#8）——与 arxiv.py 包装的是
同一数据源，此处用 requests 解析 Atom 以保证零依赖可运行。sort_by=SubmittedDate 取最新。
"""
from __future__ import annotations

import re
import time
from datetime import date, timedelta

import requests
import xml.etree.ElementTree as ET

from ..config import log
from .base import IngestAdapter, build_paper

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


class ArxivAdapter(IngestAdapter):
    name = "arxiv"
    BASE = "https://export.arxiv.org/api/query"
    # 收口到 AI/RecSys 相关分类（设计文档§1 硬过滤）
    CATEGORIES = ["cs.IR", "cs.LG", "cs.AI", "cs.MM", "cs.CL"]

    def _fetch(self, limit: int, since_date: date | None) -> list:
        cat_q = " OR ".join(f"cat:{c}" for c in self.CATEGORIES)
        params = {
            "search_query": cat_q,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": min(limit, 200),
        }
        # arXiv API 对默认 python-requests User-Agent 会直接 429；设置规范 UA 可避开。
        headers = {"User-Agent": "paper-monitor/0.1 (research; mailto:research@example.com)"}
        resp = requests.get(self.BASE, params=params, timeout=30, headers=headers)
        if resp.status_code == 429:
            # 退避一次（arXiv 建议请求间 3s 间隔）
            time.sleep(3)
            resp = requests.get(self.BASE, params=params, timeout=30, headers=headers)
        resp.raise_for_status()
        return self._parse(resp.text, limit)

    def _parse(self, xml_text: str, limit: int) -> list:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            log.warning("[arxiv] XML parse error: %s", exc)
            return []
        papers = []
        for entry in root.findall(f"{ATOM}entry"):
            raw_id = entry.findtext(f"{ATOM}id", "") or ""
            m = re.search(r"abs/([^v]+)(v\d+)?$", raw_id)
            arxiv_id = m.group(1) if m else raw_id
            title = " ".join((entry.findtext(f"{ATOM}title", "") or "").split())
            summary = " ".join((entry.findtext(f"{ATOM}summary", "") or "").split())
            published = (entry.findtext(f"{ATOM}published", "") or "")[:10]
            authors = []
            for au in entry.findall(f"{ATOM}author"):
                nm = au.findtext(f"{ATOM}name", "") or ""
                if nm:
                    authors.append({"name": nm, "affiliations": []})
            prim = entry.find(f"{ARXIV_NS}primary_category")
            cats = [prim.get("term")] if prim is not None else []
            for c in entry.findall(f"{ATOM}category"):
                if c.get("term") and c.get("term") not in cats:
                    cats.append(c.get("term"))
            topics = [{"display_name": c, "level": None} for c in cats if c]
            papers.append(build_paper(
                source="arxiv",
                title=title, abstract=summary,
                publication_date=published,
                arxiv_id=arxiv_id,
                authors=authors,
                topics=topics,
                raw={"arxiv_url": raw_id, "categories": cats},
            ))
            if len(papers) >= limit:
                break
        return papers

    def _fixture(self, limit: int) -> list:
        base = date.today()
        return [
            build_paper(
                source="arxiv", title=f"Fixture arXiv: Graph RecSys {i}",
                abstract="Graph neural network for recommendation.",
                publication_date=(base - timedelta(days=i)).isoformat(),
                arxiv_id=f"2402.0000{i}",
                authors=[{"name": f"Arx Author {i}"}],
                topics=[{"display_name": "cs.IR"}, {"display_name": "cs.LG"}],
            )
            for i in range(min(limit, 3))
        ]
