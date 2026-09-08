"""摄入基类 + 归一化工具。"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from ..config import Config, get_config
from ..models import Author, Paper, Topic


def normalize_text(s: Any) -> str:
    if s is None:
        return ""
    return " ".join(str(s).split())


def build_paper(
    *,
    source: str,
    title: str,
    abstract: str = "",
    publication_date: str | None = None,
    openalex_id: str | None = None,
    doi: str | None = None,
    arxiv_id: str | None = None,
    s2_corpus_id: str | None = None,
    authors: list[dict] | None = None,
    topics: list[dict] | None = None,
    cited_by_count: int = 0,
    influential_citation_count: int | None = None,
    upvotes: int | None = None,
    github_stars: int | None = None,
    raw: dict | None = None,
) -> Paper:
    """统一构造 Paper（解决各源字段命名不一致）。"""
    return Paper(
        id=openalex_id,
        doi=doi,
        arxiv_id=arxiv_id,
        s2_corpus_id=s2_corpus_id,
        title=normalize_text(title),
        abstract=normalize_text(abstract),
        publication_date=_as_date(publication_date),
        authors=[Author.from_dict(a) for a in (authors or [])],
        topics=[Topic.from_dict(t) for t in (topics or [])],
        cited_by_count=int(cited_by_count or 0),
        influential_citation_count=influential_citation_count,
        upvotes=upvotes,
        github_stars=github_stars,
        source=source,
        raw=raw or {},
    )


def _as_date(value: Any) -> str | None:
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
    s = str(value).strip()
    return s[:10] if len(s) >= 10 else None


class IngestAdapter:
    """所有数据源 adapter 的抽象基类。

    子类实现 fetch(limit, since_date) -> List[Paper]。
    统一负责：离线 fixture 兜底、限流退避、异常隔离。
    """

    name = "base"

    def __init__(self, config: Config | None = None) -> None:
        self.cfg = config or get_config()

    def fetch(self, limit: int | None = None, since_date: date | None = None) -> list[Paper]:
        limit = limit or self.cfg.max_per_source
        if self.cfg.offline_fixture:
            return self._fixture(limit)
        try:
            return self._fetch(limit=limit, since_date=since_date)
        except Exception as exc:  # 单源失败不影响整体 DAG
            from ..config import log
            log.warning("[%s] fetch failed: %s", self.name, exc)
            return []

    def _fetch(self, limit: int, since_date: date | None) -> list[Paper]:  # pragma: no cover
        raise NotImplementedError

    def _fixture(self, limit: int) -> list[Paper]:  # pragma: no cover
        """离线样例，子类可覆盖。默认返回空。"""
        return []
