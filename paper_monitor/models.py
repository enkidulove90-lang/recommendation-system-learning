"""数据模型：Paper / Author / Topic，含 JSON 序列化与跨源归一主键。

口径（设计文档§3）：
  - 以 OpenAlex ID 为实体主键；arXiv ID / DOI / S2 CorpusId 均回链到统一 Work。
  - 去重主键 dedup_key: 优先 DOI -> arXiv ID -> OpenAlex ID。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


def _as_date(value: Any) -> str | None:
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
    s = str(value).strip()
    # 兼容 "2026-08-12T00:00:00" 或 "2026-08-12"
    return s[:10] if len(s) >= 10 else None


@dataclass
class Author:
    id: str | None = None
    name: str = ""
    affiliations: list[str] = field(default_factory=list)
    works_count: int | None = None

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "affiliations": self.affiliations, "works_count": self.works_count}

    @classmethod
    def from_dict(cls, d: dict) -> "Author":
        return cls(
            id=d.get("id"),
            name=d.get("name", ""),
            affiliations=list(d.get("affiliations", []) or []),
            works_count=d.get("works_count"),
        )


@dataclass
class Topic:
    id: str | None = None
    display_name: str = ""
    level: int | None = None
    parent_id: str | None = None
    parent_display_name: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "level": self.level,
            "parent_id": self.parent_id,
            "parent_display_name": self.parent_display_name,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Topic":
        return cls(
            id=d.get("id"),
            display_name=d.get("display_name", ""),
            level=d.get("level"),
            parent_id=d.get("parent_id"),
            parent_display_name=d.get("parent_display_name"),
        )


@dataclass
class Paper:
    id: str | None = None            # OpenAlex ID（权威主键）
    doi: str | None = None
    arxiv_id: str | None = None
    s2_corpus_id: str | None = None
    title: str = ""
    abstract: str = ""
    publication_date: str | None = None
    authors: list[Author] = field(default_factory=list)
    topics: list[Topic] = field(default_factory=list)
    cited_by_count: int = 0
    influential_citation_count: int | None = None
    upvotes: int | None = None
    github_stars: int | None = None
    github_repo: str | None = None   # 官方代码仓库链接（替换 PWC #13 的"代码链接"角色）
    code_count: int | None = None    # 关联 HF models+datasets+spaces 数量（= 有代码/实现）
    source: str = ""                 # openalex / arxiv / huggingface / s2 / hfcode
    score: float = 0.0
    raw: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # 归一主键
    # ------------------------------------------------------------------
    def dedup_key(self) -> str:
        """跨源去重主键：DOI > arXiv ID > OpenAlex ID > title-hash。"""
        if self.doi:
            return "doi:" + self.doi.lower().strip()
        if self.arxiv_id:
            return "arxiv:" + self.arxiv_id.lower().strip()
        if self.id:
            return "oa:" + self.id.lower().strip()
        # 极端兜底：标题归一
        import hashlib
        h = hashlib.md5(self.title.lower().strip().encode("utf-8")).hexdigest()[:12]
        return "title:" + h

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "s2_corpus_id": self.s2_corpus_id,
            "title": self.title,
            "abstract": self.abstract,
            "publication_date": self.publication_date,
            "authors": [a.to_dict() for a in self.authors],
            "topics": [t.to_dict() for t in self.topics],
            "cited_by_count": self.cited_by_count,
            "influential_citation_count": self.influential_citation_count,
            "upvotes": self.upvotes,
            "github_stars": self.github_stars,
            "github_repo": self.github_repo,
            "code_count": self.code_count,
            "source": self.source,
            "score": self.score,
            "raw": self.raw,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Paper":
        return cls(
            id=d.get("id"),
            doi=d.get("doi"),
            arxiv_id=d.get("arxiv_id"),
            s2_corpus_id=d.get("s2_corpus_id"),
            title=d.get("title", ""),
            abstract=d.get("abstract", ""),
            publication_date=_as_date(d.get("publication_date")),
            authors=[Author.from_dict(a) for a in d.get("authors", []) or []],
            topics=[Topic.from_dict(t) for t in d.get("topics", []) or []],
            cited_by_count=int(d.get("cited_by_count", 0) or 0),
            influential_citation_count=d.get("influential_citation_count"),
            upvotes=d.get("upvotes"),
            github_stars=d.get("github_stars"),
            github_repo=d.get("github_repo"),
            code_count=d.get("code_count"),
            source=d.get("source", ""),
            score=float(d.get("score", 0.0) or 0.0),
            raw=d.get("raw", {}) or {},
        )

    def merge(self, other: "Paper") -> "Paper":
        """将 other 的信号合并进 self（同 dedup_key 的跨源补全）。"""
        if not self.doi and other.doi:
            self.doi = other.doi
        if not self.arxiv_id and other.arxiv_id:
            self.arxiv_id = other.arxiv_id
        if not self.id and other.id:
            self.id = other.id
        if not self.s2_corpus_id and other.s2_corpus_id:
            self.s2_corpus_id = other.s2_corpus_id
        if not self.title and other.title:
            self.title = other.title
        if not self.abstract and other.abstract:
            self.abstract = other.abstract
        if not self.publication_date and other.publication_date:
            self.publication_date = other.publication_date
        if not self.authors and other.authors:
            self.authors = other.authors
        # 数值信号取较大者（多源互补，避免被空值覆盖）
        self.cited_by_count = max(self.cited_by_count, other.cited_by_count)
        if other.influential_citation_count is not None:
            self.influential_citation_count = max(
                self.influential_citation_count or 0, other.influential_citation_count
            )
        if other.upvotes is not None:
            self.upvotes = max(self.upvotes or 0, other.upvotes)
        if other.github_stars is not None:
            self.github_stars = max(self.github_stars or 0, other.github_stars)
        if other.code_count is not None:
            self.code_count = max(self.code_count or 0, other.code_count)
        if not self.github_repo and other.github_repo:
            self.github_repo = other.github_repo
        # topics 合并去重
        seen = {t.id or t.display_name for t in self.topics}
        for t in other.topics:
            key = t.id or t.display_name
            if key and key not in seen:
                self.topics.append(t)
                seen.add(key)
        # source 标记多源
        if other.source and other.source not in self.source:
            self.source = (self.source + "+" + other.source).strip("+")
        return self
