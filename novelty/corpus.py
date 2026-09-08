"""
novelty/corpus.py — 本地快照知识图谱（语料加载）

把项目已有的解析结果（data/parsed/* 的 MinerU .md）与 11 维摘要
（data/summaries/*_summary.json）加载为统一的 PaperRecord 列表，
作为"本地快照"知识图谱（设计文档 §3）。无需联网即可支撑嵌入近邻检索。

设计要点:
  - 以 arXiv ID 去重（parsed 文本优先作检索语料，summary 补全元数据）。
  - 索引文本优先取 Abstract/Introduction 片段，贴合"找相似论文"语义。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


_ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})")


@dataclass
class PaperRecord:
    arxiv_id: str
    title: str = ""
    text: str = ""            # 用于嵌入/检索的主体文本（abstract+intro 等）
    raw_text: str = ""        # 完整解析文本
    year: Optional[int] = None
    authors: list[str] = field(default_factory=list)
    parsed_path: str = ""
    summary_path: str = ""
    url: str = ""


class LocalCorpus:
    """加载并索引本地论文语料。"""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.records: list[PaperRecord] = []
        self._by_id: dict[str, PaperRecord] = {}

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------
    def load(self, limit: int | None = None) -> "LocalCorpus":
        parsed_dir = self.data_dir / "parsed"
        summary_dir = self.data_dir / "summaries"
        tmp: dict[str, PaperRecord] = {}

        # 1) parsed .md（主检索语料）
        if parsed_dir.exists():
            for md in parsed_dir.rglob("*.md"):
                aid = self._extract_arxiv_id(md.parent.name) or self._extract_arxiv_id(md.name)
                if not aid:
                    continue
                text = md.read_text(encoding="utf-8", errors="replace")
                rec = tmp.setdefault(aid, PaperRecord(arxiv_id=aid))
                rec.raw_text = text
                rec.text = self._index_text(text)
                rec.parsed_path = str(md)
                if not rec.title:
                    rec.title = self._extract_title(text)

        # 2) summaries（补元数据 + 兜底文本）
        if summary_dir.exists():
            for sj in summary_dir.glob("*_summary.json"):
                self._merge_summary(tmp, sj)
            for smd in summary_dir.glob("*_summary.md"):
                aid = self._extract_arxiv_id(smd.name)
                if not aid:
                    continue
                rec = tmp.setdefault(aid, PaperRecord(arxiv_id=aid))
                if not rec.text:
                    t = smd.read_text(encoding="utf-8", errors="replace")
                    rec.text = self._index_text(t)

        self.records = list(tmp.values())
        if limit:
            self.records = self.records[:limit]
        self._by_id = {r.arxiv_id: r for r in self.records}
        logger.info("[LocalCorpus] loaded %d papers from %s", len(self.records), self.data_dir)
        return self

    def _merge_summary(self, tmp: dict[str, PaperRecord], sj: Path) -> None:
        try:
            d = json.loads(sj.read_text(encoding="utf-8"))
        except Exception:
            return
        aid = d.get("arxiv_id") or self._extract_arxiv_id(sj.name)
        if not aid:
            return
        rec = tmp.setdefault(aid, PaperRecord(arxiv_id=aid))
        rec.summary_path = str(sj)
        rec.title = d.get("title") or rec.title
        rec.year = self._coerce_year(d.get("year")) or rec.year
        if isinstance(d.get("authors"), list):
            rec.authors = [str(a) for a in d["authors"][:10]]
        # 若 parsed 缺失，用 summary 文本兜底
        if not rec.text:
            blob = " ".join(str(v) for v in d.values() if isinstance(v, str))
            rec.text = self._index_text(blob)

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    def get(self, arxiv_id: str) -> PaperRecord | None:
        return self._by_id.get(arxiv_id)

    def ids(self) -> list[str]:
        return [r.arxiv_id for r in self.records]

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------
    @staticmethod
    def _coerce_year(value) -> Optional[int]:
        """把摘要 JSON 里的 year 字段安全地转成 int 或 None。

        语料中的 *_summary.json 偶尔写入 '论文未提及' / '未知' 等中文占位符，
        直接赋值会破坏下游 NeighborPaper(Optional[int]) 的校验。这里统一拦截。
        """
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return None
            # 取前 4 位数字（如 '2024' / '2024.' / '2024年'）
            m = re.search(r"(\d{4})", s)
            return int(m.group(1)) if m else None
        return None

    @staticmethod
    def _extract_arxiv_id(name: str) -> str:
        m = _ARXIV_RE.search(name)
        return m.group(1) if m else ""

    @staticmethod
    def _extract_title(text: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# ") and len(line) > 2:
                return line[2:].strip()
        return ""

    @staticmethod
    def _index_text(text: str) -> str:
        """抽取用于嵌入检索的文本: 优先 Abstract + Introduction 片段。"""
        abs_sec = LocalCorpus._section(text, "abstract")
        intro_sec = LocalCorpus._section(text, "introduction")
        if abs_sec or intro_sec:
            return (abs_sec + "\n" + intro_sec)[:3500].strip()
        # 兜底: 前 2000 字符
        return text[:2000].strip()

    @staticmethod
    def _section(text: str, header: str) -> str:
        """抓 '## Header' 到下一个 '## ' 之间的内容。"""
        pat = re.compile(r"(?im)^#{1,3}\s*" + re.escape(header) + r"\b\s*$\n")
        m = pat.search(text)
        if not m:
            return ""
        start = m.end()
        nxt = re.search(r"(?im)^#{1,3}\s+\S", text[start:])
        end = start + nxt.start() if nxt else len(text)
        return text[start:end].strip()
