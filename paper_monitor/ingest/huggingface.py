"""Hugging Face Daily Papers 适配器（设计文档#10/#11/#12）。

免鉴权：https://huggingface.co/api/daily_papers?date=YYYY-MM-DD
返回 paper.id(arXiv号)/title/upvotes/githubStars/summary/topic_tags，作为"社区热度"信号。
"""
from __future__ import annotations

from datetime import date, timedelta

import requests

from ..config import log
from .base import IngestAdapter, build_paper


class HuggingFaceAdapter(IngestAdapter):
    name = "huggingface"
    BASE = "https://huggingface.co/api/daily_papers"

    def _fetch(self, limit: int, since_date: date | None) -> list:
        # 拉取最近 time_window_days 天的每日精选（社区热度信号）
        out: list = []
        for d in range(self.cfg.time_window_days):
            day = date.today() - timedelta(days=d)
            url = f"{self.BASE}?date={day.isoformat()}"
            try:
                resp = requests.get(url, timeout=30)
            except requests.RequestException as exc:
                log.warning("[hf] request failed %s: %s", day, exc)
                continue
            if resp.status_code != 200:
                # 当天可能无 daily papers
                continue
            try:
                items = resp.json()
            except ValueError:
                continue
            for it in items:
                p = self._map(it)
                if p is not None:
                    out.append(p)
                if len(out) >= limit:
                    return out
        return out[:limit]

    def _map(self, it: dict):
        paper = it.get("paper", {}) or {}
        pid = paper.get("id")
        if not pid:
            return None
        authors = [{"name": a.get("name", "")} for a in (paper.get("authors", []) or [])]
        topics = [{"display_name": t} for t in (paper.get("topic_tags", []) or [])]
        return build_paper(
            source="huggingface",
            title=paper.get("title", ""),
            abstract=paper.get("summary", ""),
            publication_date=it.get("publishedAt", "")[:10] or None,
            arxiv_id=pid,
            authors=authors,
            topics=topics,
            upvotes=paper.get("upvotes"),
            github_stars=paper.get("githubStars"),
            raw=it,
        )

    def _fixture(self, limit: int) -> list:
        base = date.today()
        return [
            build_paper(
                source="huggingface", title=f"Fixture HF: Multimodal LLM Agent {i}",
                abstract="Community hot paper on multimodal agents.",
                publication_date=(base - timedelta(days=i)).isoformat(),
                arxiv_id=f"2403.0000{i}",
                topics=[{"display_name": "cs.AI"}, {"display_name": "cs.CL"}],
                upvotes=20 + i * 5, github_stars=10 + i,
            )
            for i in range(min(limit, 3))
        ]
