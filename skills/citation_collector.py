"""
skills/citation_collector.py — A1 引用数据采集技能

从 MinerU 解析结果和 Semantic Scholar API 采集目标论文的引用关系、
相关论文、作者/机构信息。

数据源优先级:
  1. MinerU 解析的 References 段落（PDF 内提取）
  2. Semantic Scholar API（免费，无需 Key）— 被引列表 + 相关论文
  3. arXiv API — 补充元数据

降级策略: SemSch 不可用时仅使用 PDF 内解析的参考文献。
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill("citation-collect")
class CitationCollector(BaseSkill):
    """
    引用数据采集器。

    从多个数据源采集论文的引用关系：
      - PDF 内 References 段落 → references.json
      - Semantic Scholar API → citations.json + related_works.json

    使用示例:
        collector = CitationCollector()
        result = collector.execute(
            arxiv_id="2605.28175",
            parsed_dir="data/parsed/2605.28175/",
            metadata={"title": "...", "authors": [...]},
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._sem_sch_base: str = settings.SEMANTIC_SCHOLAR_API_BASE
        self._cache_days: int = settings.CITATION_CACHE_DAYS
        # 超时配置（秒）
        self._timeout: int = kwargs.get("timeout", 180)

    @property
    def is_ready(self) -> bool:
        """检查数据源可用性。始终就绪（至少可解析 PDF References）。"""
        return True

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        采集引用数据。

        参数:
            arxiv_id  (str): arXiv ID
            parsed_dir (str): MinerU 解析结果目录
            metadata   (dict): 论文元数据 {title, authors, year, ...}
            sources    (list): 数据源列表，默认 ["pdf_refs", "semantic_scholar"]
            output_dir (str): 输出目录，默认 data/citations/{arxiv_id}/

        返回:
            {
                "references": [Citation, ...],
                "citations":  [Citation, ...],
                "related":    [Citation, ...],
                "collected_at": "ISO timestamp",
                "sources_used": ["pdf_refs", ...],
                "output_dir": "data/citations/{id}/",
                "error": None | "error message",
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        parsed_dir: str = kwargs.get("parsed_dir", "")
        metadata: dict = kwargs.get("metadata", {})
        sources: list[str] = kwargs.get("sources", ["pdf_refs", "semantic_scholar"])
        output_dir: str = kwargs.get("output_dir", "")

        if not arxiv_id:
            return {"error": "arxiv_id is required", "references": [], "citations": [], "related": []}

        # 确定输出目录
        if not output_dir:
            output_dir = str(settings.DATA_DIR / "citations" / arxiv_id)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # 检查缓存
        cached = self._load_cache(out_path)
        if cached:
            logger.info("[CitationCollector] Using cached data for %s", arxiv_id)
            return cached

        references: list[dict] = []
        citations: list[dict] = []
        related: list[dict] = []
        sources_used: list[str] = []
        errors: list[str] = []

        # ---- 数据源 1: PDF References 段落 ----
        if "pdf_refs" in sources:
            try:
                refs = self._extract_from_pdf_refs(arxiv_id, parsed_dir, metadata)
                references = refs
                sources_used.append("pdf_refs")
                logger.info("[CitationCollector] Extracted %d references from PDF", len(refs))
            except Exception as exc:
                errors.append(f"pdf_refs: {exc}")
                logger.warning("[CitationCollector] PDF refs extraction failed: %s", exc)

        # ---- 数据源 2: Semantic Scholar API ----
        if "semantic_scholar" in sources:
            try:
                sem_result = self._fetch_from_semantic_scholar(arxiv_id, metadata)
                if sem_result.get("citations"):
                    citations = sem_result["citations"]
                    sources_used.append("semantic_scholar_citations")
                if sem_result.get("related"):
                    related = sem_result["related"]
                    sources_used.append("semantic_scholar_related")
                # 补充 references（如果 PDF 解析为空）
                if not references and sem_result.get("references"):
                    references = sem_result["references"]
                    sources_used.append("semantic_scholar_references")
            except Exception as exc:
                errors.append(f"semantic_scholar: {exc}")
                logger.warning("[CitationCollector] Semantic Scholar fetch failed: %s", exc)

        # ---- 组装结果 ----
        result = {
            "arxiv_id": arxiv_id,
            "references": references,
            "citations": citations,
            "related": related,
            "collected_at": datetime.now().isoformat(),
            "sources_used": sources_used,
            "output_dir": str(out_path),
            "error": "; ".join(errors) if errors else None,
        }

        # 保存到文件
        self._save_results(out_path, result)

        return result

    # ------------------------------------------------------------------
    # PDF References 提取
    # ------------------------------------------------------------------

    def _extract_from_pdf_refs(
        self, arxiv_id: str, parsed_dir: str, metadata: dict
    ) -> list[dict]:
        """从 MinerU 解析结果中提取参考文献列表。"""
        references: list[dict] = []

        # 尝试多个路径
        possible_paths = [
            Path(parsed_dir) / f"{arxiv_id}_content.json",
            Path(parsed_dir) / f"{arxiv_id}.md",
            settings.DATA_DIR / "parsed" / arxiv_id / f"{arxiv_id}_content.json",
            settings.DATA_DIR / "parsed" / arxiv_id / f"{arxiv_id}.md",
        ]

        full_text = ""
        for p in possible_paths:
            if p.exists():
                if p.suffix == ".json":
                    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
                    # 尝试从 content.json 提取文本
                    if isinstance(data, dict):
                        full_text = data.get("content", {}).get("text", "")
                        if not full_text:
                            # 尝试递归查找所有 text 字段
                            full_text = self._extract_text_from_json(data)
                else:
                    full_text = p.read_text(encoding="utf-8", errors="replace")
                if full_text:
                    break

        if not full_text:
            logger.warning("No parsed content found for %s", arxiv_id)
            return references

        # 查找 References 章节
        ref_section = self._find_references_section(full_text)
        if not ref_section:
            return references

        # 解析每一条引用
        references = self._parse_reference_entries(ref_section)
        return references

    @staticmethod
    def _find_references_section(text: str) -> str:
        """定位 References/Bibliography 章节。"""
        # 匹配常见的 References 章节标题
        patterns = [
            r'(?:^|\n)#{1,3}\s*(?:References|Bibliography|REFERENCES|BIBLIOGRAPHY)\s*\n',
            r'(?:^|\n)REFERENCES\s*\n',
            r'(?:^|\n)References\s*\n',
            r'(?:^|\n)##\s*References?\s*\n',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                start = match.start()
                # 从匹配位置取到文档末尾（或 Appendix 之前）
                remaining = text[start:]
                # 截断在 Appendix 之前
                appendix_match = re.search(
                    r'\n#{1,3}\s*(?:Appendix|Appendices|A\s|Acknowledgments?)',
                    remaining[10:],  # 跳过标题行本身
                )
                if appendix_match:
                    remaining = remaining[: 10 + appendix_match.start()]
                return remaining

        return ""

    @staticmethod
    def _parse_reference_entries(ref_text: str) -> list[dict]:
        """解析参考文献段落的每一条引用。"""
        references: list[dict] = []

        # 按编号拆分: [1] ... [2] ... 或 1. ... 2. ...
        entries = re.split(r'\n\s*(?:\[\d+\]|\d+\.)\s*', ref_text)
        # 过滤掉标题行、空白行
        entries = [e.strip() for e in entries if len(e.strip()) > 20]

        # MinerU sometimes preserves bibliography entries as blank-line-separated
        # paragraphs without numeric labels. Treating the complete section as
        # one entry would discard the paper's real reference network.
        if len(entries) <= 1:
            entries = [
                entry.strip()
                for entry in re.split(r'\n\s*\n+', ref_text)
                if len(entry.strip()) > 20
                and entry.strip().lower() not in {"references", "bibliography"}
            ]

        for entry in entries:
            ref = CitationCollector._parse_single_ref(entry)
            if ref.get("title"):
                references.append(ref)

        return references

    @staticmethod
    def _parse_single_ref(entry: str) -> dict:
        """解析单条引用条目，提取 title, authors, year, venue。"""
        ref: dict = {
            "title": "",
            "title_normalized": "",
            "authors": [],
            "first_author_surname": "",
            "year": None,
            "arxiv_id": "",
            "doi": "",
            "venue": "",
            "citation_count": 0,
            "relation_type": "cites",
            "relation_description": "",
        }

        # 提取年份
        year_match = re.search(r'\b(19|20)\d{2}\b', entry)
        if year_match:
            ref["year"] = int(year_match.group())

        # 提取 arXiv ID
        arxiv_match = re.search(r'arxiv[:.\s]*(\d{4}\.\d{4,5})', entry, re.IGNORECASE)
        if arxiv_match:
            ref["arxiv_id"] = arxiv_match.group(1)

        # 提取 DOI
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', entry)
        if doi_match:
            ref["doi"] = doi_match.group()

        # 标题：通常在第一句，直到第一个句号或 "In" / "Proc" / "arXiv"
        # 简化处理：取前面的主要文本
        title_end_patterns = [
            r'\.\s+(?:In\s|Proc\.|Proceedings|arXiv|https?://|[A-Z][a-z]+\s+\d{4})',
            r'\.\s*(?:pp?\.?\s*\d|vol\.?\s*\d)',
        ]
        title_end = len(entry)
        for pat in title_end_patterns:
            m = re.search(pat, entry)
            if m and m.start() < title_end:
                title_end = m.start()

        # 跳过开头的作者名部分（通常含逗号和大写字母缩写）
        # 简单策略：找第一个句号后的内容作为标题候选
        first_period = entry.find(".")
        if first_period > 0:
            # 如果第一个句号前有很多逗号，可能是作者列表
            before_first = entry[:first_period]
            if before_first.count(",") >= 1 and len(before_first) < 150:
                # 跳过作者部分，从第一个句号后开始
                title_start = first_period + 1
            else:
                title_start = 0
        else:
            title_start = 0

        # 提取标题
        candidate = entry[title_start:title_end].strip().lstrip('"').lstrip("'")
        # 去开头的标点
        candidate = re.sub(r'^[.,;:：；，\s]+', '', candidate)
        if len(candidate) > 15:
            ref["title"] = candidate[:300]

        # 归一化标题（去重用）
        ref["title_normalized"] = re.sub(
            r'[^a-z0-9\s]', '', candidate.lower()
        ).strip()[:200]

        # 提取第一作者姓氏
        first_author_match = re.match(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', entry)
        if first_author_match:
            ref["first_author_surname"] = first_author_match.group(1).split()[-1]

        # 提取作者列表（简化：取开头的逗号分隔部分）
        author_section = entry[: first_period] if first_period > 0 else entry[:200]
        if "," in author_section:
            ref["authors"] = [
                a.strip() for a in author_section.split(",")
                if len(a.strip()) > 2 and not any(kw in a.lower() for kw in ["proc", "conf", "arxiv", "http"])
            ][:10]

        return ref

    @staticmethod
    def _extract_text_from_json(data: dict, depth: int = 0) -> str:
        """递归提取 JSON 中所有文本字段。"""
        if depth > 5:
            return ""
        texts = []
        if isinstance(data, dict):
            for key, val in data.items():
                if key in ("text", "content", "md", "markdown") and isinstance(val, str):
                    texts.append(val)
                elif isinstance(val, (dict, list)):
                    texts.append(CitationCollector._extract_text_from_json(val, depth + 1))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    texts.append(CitationCollector._extract_text_from_json(item, depth + 1))
        return "\n".join(t for t in texts if t)

    # ------------------------------------------------------------------
    # Semantic Scholar API
    # ------------------------------------------------------------------

    def _fetch_from_semantic_scholar(self, arxiv_id: str, metadata: dict) -> dict:
        """从 Semantic Scholar API 获取引用数据。"""
        result: dict = {"references": [], "citations": [], "related": []}

        # 用 arXiv ID 搜索论文
        paper_id = self._resolve_sem_sch_id(arxiv_id)
        if not paper_id:
            logger.warning("Paper %s not found on Semantic Scholar", arxiv_id)
            return result

        # 获取参考文献
        refs = self._sem_sch_get(paper_id, "references")
        if refs:
            result["references"] = [
                {
                    "title": r.get("title", ""),
                    "title_normalized": re.sub(r'[^a-z0-9\s]', '', r.get("title", "").lower()).strip(),
                    "authors": [a.get("name", "") for a in r.get("authors", [])],
                    "first_author_surname": (r.get("authors", [{}])[0].get("name", "").split()[-1] if r.get("authors") else ""),
                    "year": r.get("year"),
                    "arxiv_id": r.get("externalIds", {}).get("ArXiv", ""),
                    "doi": r.get("externalIds", {}).get("DOI", ""),
                    "venue": r.get("venue", ""),
                    "citation_count": r.get("citationCount", 0),
                    "relation_type": "cites",
                    "relation_description": "",
                }
                for r in refs
                if r.get("title")
            ]

        # 获取被引列表
        cits = self._sem_sch_get(paper_id, "citations")
        if cits:
            result["citations"] = [
                {
                    "title": c.get("citingPaper", {}).get("title", ""),
                    "title_normalized": re.sub(
                        r'[^a-z0-9\s]', '',
                        c.get("citingPaper", {}).get("title", "").lower()
                    ).strip(),
                    "authors": [a.get("name", "") for a in c.get("citingPaper", {}).get("authors", [])],
                    "first_author_surname": (
                        c.get("citingPaper", {}).get("authors", [{}])[0].get("name", "").split()[-1]
                        if c.get("citingPaper", {}).get("authors") else ""
                    ),
                    "year": c.get("citingPaper", {}).get("year"),
                    "arxiv_id": c.get("citingPaper", {}).get("externalIds", {}).get("ArXiv", ""),
                    "doi": "",
                    "venue": c.get("citingPaper", {}).get("venue", ""),
                    "citation_count": c.get("citingPaper", {}).get("citationCount", 0),
                    "relation_type": "cited_by",
                    "relation_description": "",
                }
                for c in cits
                if c.get("citingPaper", {}).get("title")
            ]

        return result

    def _resolve_sem_sch_id(self, arxiv_id: str) -> str:
        """通过 arXiv ID 查找 Semantic Scholar paper ID。"""
        url = f"{self._sem_sch_base}/paper/ArXiv:{arxiv_id}"
        try:
            resp = requests.get(
                url,
                params={"fields": "paperId"},
                timeout=15,
                headers={"User-Agent": "RS-Paper-Pipeline/1.0"},
            )
            if resp.status_code == 200:
                return resp.json().get("paperId", "")
        except Exception as exc:
            logger.warning("Semantic Scholar resolve failed: %s", exc)
        return ""

    def _sem_sch_get(self, paper_id: str, endpoint: str, limit: int = 50) -> list[dict]:
        """调用 Semantic Scholar API 获取引用/被引数据。"""
        url = f"{self._sem_sch_base}/paper/{paper_id}/{endpoint}"
        all_data: list[dict] = []
        offset = 0

        try:
            while offset < limit:
                resp = requests.get(
                    url,
                    params={
                        "fields": "title,authors,year,venue,citationCount,externalIds",
                        "limit": min(50, limit - offset),
                        "offset": offset,
                    },
                    timeout=20,
                    headers={"User-Agent": "RS-Paper-Pipeline/1.0"},
                )
                if resp.status_code != 200:
                    break
                data = resp.json().get("data", [])
                if not data:
                    break
                all_data.extend(data)
                offset += len(data)
                time.sleep(1.0)  # 限流
        except Exception as exc:
            logger.warning("Semantic Scholar %s fetch failed: %s", endpoint, exc)

        return all_data

    # ------------------------------------------------------------------
    # 缓存管理
    # ------------------------------------------------------------------

    def _load_cache(self, output_dir: Path) -> dict | None:
        """检查并加载缓存。"""
        cache_file = output_dir / "references.json"
        if not cache_file.exists():
            return None

        # 检查缓存时效
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_days = (datetime.now() - mtime).days
        if age_days > self._cache_days:
            logger.info("Cache expired (%d days > %d days max)", age_days, self._cache_days)
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            # 确保格式正确
            if "references" in data:
                return data
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    @staticmethod
    def _save_results(output_dir: Path, result: dict) -> None:
        """保存采集结果到 JSON 文件。"""
        files = {
            "references.json": result.get("references", []),
            "citations.json": result.get("citations", []),
            "related_works.json": result.get("related", []),
        }
        for filename, data in files.items():
            filepath = output_dir / filename
            filepath.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        # 同时保存完整结果快照
        snapshot_path = output_dir / "collection_result.json"
        snapshot_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("[CitationCollector] Saved to %s", output_dir)
