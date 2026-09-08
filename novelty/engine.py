"""
novelty/engine.py — 编排器（串联全部模块产出 NoveltyReport）

数据流（对齐设计文档 §1）:
    解析/文本 → Extractor（四维度拆解）→ GraphQuery（图谱邻域）
             → VectorIndex（嵌入近邻）→ ContrastEngine（差异矩阵）
             → ReportGenerator（报告）

设计约束: 全程 evidence-only，报告不含"新颖/不新颖"终审判定。

可选 LLM: 通过 make_deepseek_llm() 把已配置的 DeepSeekSummarizer 包装为
Callable[[str], str]，供 Extractor 做结构化增强抽取（无 Key 时自动跳过）。
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, Optional

from .corpus import LocalCorpus
from .embedder import EmbeddingBackend
from .extractor import Extractor
from .graph_query import GraphQuery
from .index import VectorIndex
from .contrast import ContrastEngine
from .report import ReportGenerator
from .schemas import NeighborPaper, NeighborSource, NoveltyReport, NoveltyLabel

logger = logging.getLogger(__name__)


def make_deepseek_llm(summarizer) -> Optional[Callable[[str], str]]:
    """把 DeepSeekSummarizer 包装成 Extractor 需要的 `Callable[[str], str]`。

    仅当 summarizer.is_ready 时返回可用 callable；否则返回 None（启发式兜底）。
    复用 summarizer 既有的 OpenAI client，不重复建连。
    """
    if summarizer is None or not getattr(summarizer, "is_ready", False):
        return None
    client = getattr(summarizer, "_client", None)
    model = getattr(summarizer, "_model", "deepseek-chat")
    if client is None:
        return None

    def _call(prompt: str) -> str:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500,
        )
        return (resp.choices[0].message.content or "")

    return _call


class NoveltyEngine:
    def __init__(
        self,
        data_dir: str | Path,
        embedder_kind: str = "auto",
        use_s2: bool = True,
        use_openalex: bool = True,
        top_k: int = 10,
        contrast_top_k: int = 8,
        llm: Optional[Callable[[str], str]] = None,
        cache_dir: Optional[str | Path] = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.embedder_kind = embedder_kind
        self.use_s2 = use_s2
        self.use_openalex = use_openalex
        self.top_k = top_k
        self.contrast_top_k = contrast_top_k
        self.llm = llm
        self.cache_dir = Path(cache_dir) if cache_dir else None

        self.extractor = Extractor(llm=llm)
        self.embedder = EmbeddingBackend(kind=embedder_kind)
        self.report_gen = ReportGenerator()
        self._corpus: Optional[LocalCorpus] = None
        self._index: Optional[VectorIndex] = None

    # ------------------------------------------------------------------
    def _ensure_corpus(self) -> LocalCorpus:
        if self._corpus is None:
            self._corpus = LocalCorpus(self.data_dir).load()
        return self._corpus

    def _ensure_index(self) -> VectorIndex:
        if self._index is not None:
            return self._index
        corpus = self._ensure_corpus()
        idx = VectorIndex(self.embedder)
        idx.build(corpus.records, text_accessor=lambda r: r.text or r.raw_text or "")
        self._index = idx
        if self.cache_dir:
            try:
                idx.save(self.cache_dir / "novelty_index")
            except Exception as exc:
                logger.warning("[Engine] index cache save failed: %s", exc)
        return idx

    # ------------------------------------------------------------------
    def analyze(self, arxiv_id: str) -> NoveltyReport:
        t0 = time.time()
        corpus = self._ensure_corpus()
        target = corpus.get(arxiv_id)
        online_sources: list[str] = []

        if target is None:
            return NoveltyReport(
                arxiv_id=arxiv_id,
                title="",
                summary_note=f"目标论文 {arxiv_id} 不在本地语料（data/parsed）中，无法分析。",
                meta={"error": "target_not_in_corpus", "embedder": self.embedder.kind,
                      "elapsed_sec": round(time.time() - t0, 2)},
            )

        # 1) 抽取
        extraction = self.extractor.extract(
            target.raw_text or target.text or "",
            arxiv_id=arxiv_id, title=target.title,
        )

        # 2) 嵌入近邻（本地语料）
        neighbors: list[NeighborPaper] = []
        try:
            index = self._ensure_index()
            for aid, sim in index.search(target.text or target.raw_text or "",
                                        top_k=self.top_k, exclude=arxiv_id):
                rec = corpus.get(aid)
                neighbors.append(NeighborPaper(
                    arxiv_id=aid,
                    title=rec.title if rec else aid,
                    year=rec.year if rec else None,
                    relation="similar",
                    similarity=round(float(sim), 4),
                    source=NeighborSource.CORPUS,
                    url=f"https://arxiv.org/abs/{aid}" if aid else "",
                ))
        except Exception as exc:
            logger.warning("[Engine] corpus neighbor search failed: %s", exc)

        # 3) 外部图谱邻域（S2 / OpenAlex）
        external: list[NeighborPaper] = []
        if self.use_s2 or self.use_openalex:
            try:
                gq = GraphQuery(use_s2=self.use_s2, use_openalex=self.use_openalex)
                external = gq.query(
                    arxiv_id,
                    parsed_dir=target.parsed_path,
                    metadata={"title": target.title, "year": target.year},
                )
                if self.use_s2:
                    online_sources.append("semantic_scholar")
                if self.use_openalex:
                    online_sources.append("openalex")
            except Exception as exc:
                logger.warning("[Engine] graph query failed: %s", exc)

        # 合并（去重 by title），corpus 近邻优先（有相似度）
        merged = self._merge_neighbors(neighbors, external)
        contrast_set = merged[: self.contrast_top_k]

        # 4) 对比（设计轴差异矩阵）
        engine_c = ContrastEngine()
        diff_matrix = []
        for nb in contrast_set:
            nb_text = ""
            if nb.arxiv_id and (rec := corpus.get(nb.arxiv_id)):
                nb_text = rec.raw_text or rec.text or ""
            diff_matrix.extend(engine_c.build_matrix(extraction, nb, nb_text))

        # 5) 报告
        report = NoveltyReport(
            arxiv_id=arxiv_id,
            title=target.title,
            extraction=extraction,
            neighbors=merged,
            difference_matrix=diff_matrix,
            meta={
                "embedder": self.embedder.kind,
                "embedder_dim": self.embedder.dim,
                "online_sources": online_sources,
                "corpus_size": len(corpus.records),
                "n_corpus_neighbors": len(neighbors),
                "n_external_neighbors": len(external),
                "n_diff_points": len(diff_matrix),
                "elapsed_sec": round(time.time() - t0, 2),
            },
        )
        report.summary_note = self.report_gen.build_summary_note(report)
        return report

    # ------------------------------------------------------------------
    @staticmethod
    def _merge_neighbors(corpus_n: list[NeighborPaper],
                         external: list[NeighborPaper]) -> list[NeighborPaper]:
        seen = set()
        out: list[NeighborPaper] = []
        for n in corpus_n:  # 有相似度，优先
            k = (n.title or n.arxiv_id or "").strip().lower()[:120]
            if k in seen:
                continue
            seen.add(k)
            out.append(n)
        for n in external:
            k = (n.title or n.arxiv_id or "").strip().lower()[:120]
            if not k or k in seen:
                continue
            seen.add(k)
            out.append(n)
        return out
