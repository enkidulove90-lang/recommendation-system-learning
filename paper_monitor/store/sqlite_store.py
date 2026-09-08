"""SQLite 存储：works 主表 + 倒排 topics/authors + snapshots（引用爆发检测）。

表结构（设计文档§6）：
  works(id PK, source, title, date, topics, score, raw_json) + 倒排 topics/authors
  扩展：counts_by_year / snapshots 用于引用爆发（> 均值+3σ）检测。
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from ..config import Config, get_config
from ..models import Paper


class SQLiteStore:
    def __init__(self, db_path: Path | None = None, config: Config | None = None) -> None:
        self.cfg = config or get_config()
        self.db_path = Path(db_path) if db_path else self.cfg.db_path
        self.cfg.ensure_dirs()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS works (
                id TEXT PRIMARY KEY,
                openalex_id TEXT, doi TEXT, arxiv_id TEXT,
                title TEXT, date TEXT, source TEXT,
                topics_json TEXT, score REAL DEFAULT 0,
                cited_by_count INTEGER DEFAULT 0,
                influential_citation_count INTEGER,
                upvotes INTEGER, github_stars INTEGER,
                raw_json TEXT, updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS topics_inv (
                paper_id TEXT, topic_name TEXT, parent_name TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_topics_inv_name ON topics_inv(topic_name);
            CREATE TABLE IF NOT EXISTS authors_inv (
                paper_id TEXT, author_name TEXT, affiliation TEXT
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                paper_id TEXT, snapshot_date TEXT, cited_by_count INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_snap_pid ON snapshots(paper_id);
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # 写
    # ------------------------------------------------------------------
    def upsert(self, paper: Paper) -> None:
        key = paper.dedup_key()
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO works (
                id, openalex_id, doi, arxiv_id, title, date, source,
                topics_json, score, cited_by_count, influential_citation_count,
                upvotes, github_stars, raw_json, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                openalex_id=excluded.openalex_id, doi=excluded.doi, arxiv_id=excluded.arxiv_id,
                title=excluded.title, date=excluded.date, source=excluded.source,
                topics_json=excluded.topics_json, score=excluded.score,
                cited_by_count=excluded.cited_by_count,
                influential_citation_count=excluded.influential_citation_count,
                upvotes=excluded.upvotes, github_stars=excluded.github_stars,
                raw_json=excluded.raw_json, updated_at=excluded.updated_at
            """,
            (
                key, paper.id, paper.doi, paper.arxiv_id, paper.title, paper.publication_date,
                paper.source, json.dumps([t.to_dict() for t in paper.topics], ensure_ascii=False),
                paper.score, paper.cited_by_count, paper.influential_citation_count,
                paper.upvotes, paper.github_stars, json.dumps(paper.raw, ensure_ascii=False),
                date.today().isoformat(),
            ),
        )
        # 倒排索引重建
        cur.execute("DELETE FROM topics_inv WHERE paper_id=?", (key,))
        cur.execute("DELETE FROM authors_inv WHERE paper_id=?", (key,))
        for t in paper.topics:
            cur.execute(
                "INSERT INTO topics_inv (paper_id, topic_name, parent_name) VALUES (?,?,?)",
                (key, t.display_name, t.parent_display_name),
            )
        for a in paper.authors:
            affs = ", ".join(a.affiliations) if a.affiliations else None
            cur.execute(
                "INSERT INTO authors_inv (paper_id, author_name, affiliation) VALUES (?,?,?)",
                (key, a.name, affs),
            )
        # 快照（用于引用爆发检测）
        cur.execute(
            "INSERT INTO snapshots (paper_id, snapshot_date, cited_by_count) VALUES (?,?,?)",
            (key, date.today().isoformat(), paper.cited_by_count),
        )
        self.conn.commit()

    def upsert_many(self, papers: list[Paper]) -> int:
        n = 0
        for p in papers:
            self.upsert(p)
            n += 1
        return n

    # ------------------------------------------------------------------
    # 读
    # ------------------------------------------------------------------
    def get_by_key(self, key: str) -> Paper | None:
        row = self.conn.execute("SELECT * FROM works WHERE id=?", (key,)).fetchone()
        return self._row_to_paper(row) if row else None

    def query(self, since: str | None = None, topic: str | None = None, limit: int = 100) -> list[Paper]:
        sql = "SELECT w.* FROM works w"
        args: list[Any] = []
        joins, wheres = [], []
        if topic:
            sql += " JOIN topics_inv t ON w.id=t.paper_id"
            wheres.append("t.topic_name LIKE ?")
            args.append(f"%{topic}%")
        if since:
            wheres.append("w.date >= ?")
            args.append(since)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY w.score DESC LIMIT ?"
        args.append(limit)
        rows = self.conn.execute(sql, args).fetchall()
        return [self._row_to_paper(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]

    def _row_to_paper(self, row: sqlite3.Row) -> Paper:
        d = dict(row)
        topics = json.loads(d.get("topics_json") or "[]")
        raw = json.loads(d.get("raw_json") or "{}")
        return Paper(
            id=d.get("openalex_id"), doi=d.get("doi"), arxiv_id=d.get("arxiv_id"),
            title=d.get("title") or "", publication_date=d.get("date"),
            topics=_topics_from(topics),
            cited_by_count=d.get("cited_by_count", 0) or 0,
            influential_citation_count=d.get("influential_citation_count"),
            upvotes=d.get("upvotes"), github_stars=d.get("github_stars"),
            source=d.get("source") or "", score=d.get("score", 0.0) or 0.0,
            raw=raw,
        )

    # ------------------------------------------------------------------
    # 引用爆发检测：snapshot 环比 > 均值 + 3σ 告警（设计文档§6）
    # ------------------------------------------------------------------
    def detect_bursts(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT paper_id, cited_by_count FROM snapshots ORDER BY paper_id, snapshot_date"
        ).fetchall()
        by_pid: dict[str, list[int]] = {}
        for r in rows:
            by_pid.setdefault(r["paper_id"], []).append(r["cited_by_count"])

        deltas: list[int] = []
        for series in by_pid.values():
            if len(series) >= 2:
                deltas.append(series[-1] - series[-2])
        if len(deltas) < 2:
            return []
        mean = sum(deltas) / len(deltas)
        var = sum((d - mean) ** 2 for d in deltas) / len(deltas)
        std = var ** 0.5
        threshold = mean + 3 * std

        flagged = []
        for pid, series in by_pid.items():
            if len(series) < 2:
                continue
            delta = series[-1] - series[-2]
            if delta > threshold:
                title = self.conn.execute(
                    "SELECT title FROM works WHERE id=?", (pid,)
                ).fetchone()
                flagged.append({
                    "paper_id": pid,
                    "title": title["title"] if title else pid,
                    "delta": delta,
                    "series": series,
                })
        return flagged

    def close(self) -> None:
        self.conn.close()


def _topics_from(topics: list[dict]):
    # 局部导入避免循环
    from ..models import Topic
    return [Topic.from_dict(t) for t in topics]
