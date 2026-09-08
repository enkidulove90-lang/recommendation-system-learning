"""
novelty/extractor.py — 抽取模块（四维度拆解 + 贡献句/声明抽取）

设计文档 §2/§5: 把论文拆为「背景 / 方法 / 实验 / 声明(claim)」四维度，
用 LLM + 解析结果抽取 1 个核心任务 + 若干贡献声明 + 关键主张。

实现策略（人机协同、可降级）:
  - 启发式: 基于章节标题与关键词，从 MinerU .md / 11 维摘要结构化抽取，零依赖、必可用。
  - LLM（可选）: 若提供 llm callable（如封装 DeepSeekSummarizer），以结构化 JSON 增强抽取，
    与启发式结果合并（LLM 优先，启发式兜底）。
"""

from __future__ import annotations

import json
import logging
import re
from typing import Callable, Optional, Sequence

from .schemas import Claim, ClaimType, ContributionExtraction

logger = logging.getLogger(__name__)


_SECTION_HEADER = re.compile(r"(?im)^(?:#{1,4})\s+(.+?)\s*$")
_SPLIT_SENT = re.compile(r"(?<=[.!?。！？])\s+")

# 维度 -> 章节标题关键词
_DIM_HEADERS = {
    "background": ["introduction", "background", "related work", "motivation", "problem", "引言", "背景", "相关工作"],
    "method": ["method", "approach", "model", "architecture", "framework", "our method",
               "methodology", "design", "system", "方法", "模型", "框架", "设计", "系统"],
    "experiments": ["experiment", "evaluation", "empirical", "result", "setup",
                    "implementation", "dataset", "实验", "评估", "结果", "数据集"],
}

_CONTRIB_KEYWORDS = [
    "contribut", "we propose", "we present", "we introduce", "we develop",
    "our main", "key insight", "贡献", "我们提出", "核心贡献",
]
_CLAIM_RULES = [
    (ClaimType.THEORETICAL, ["theoretically", "theorem", "prove", "first", "novel", "首次", "理论", "新颖"]),
    (ClaimType.EMPIRICAL, ["we show", "we demonstrate", "we find", "improves", "outperform",
                            "achieve", "better than", "superior", "实验表明", "优于", "提升"]),
    (ClaimType.METHODOLOGICAL, ["we propose", "we present", "we introduce", "we develop",
                                 "we design", "framework", "model", "method", "提出", "设计", "框架"]),
]


class Extractor:
    def __init__(self, llm: Optional[Callable[[str], str]] = None) -> None:
        self.llm = llm

    # ------------------------------------------------------------------
    def extract(self, text: str, arxiv_id: str = "", title: str = "",
                summary: Optional[dict] = None) -> ContributionExtraction:
        text = text or ""
        title = title or self._extract_title(text)
        sections = self._split_sections(text)
        background = self._collect(sections, "background")
        method = self._collect(sections, "method")
        experiments = self._collect(sections, "experiments")
        contributions = self._collect_contributions(text, sections)
        claims = self._collect_claims(text)

        core_task = title
        abs_sec = self._section_named(text, "abstract")
        if abs_sec:
            first_sent = _SPLIT_SENT.split(abs_sec.strip())[0]
            if len(first_sent) > 20:
                core_task = f"{title} — {first_sent}"

        method_name = "heuristic"
        # 可选 LLM 增强
        if self.llm is not None:
            try:
                llm_out = self._llm_extract(text, title)
                if llm_out:
                    method_name = "hybrid"
                    core_task = llm_out.get("core_task") or core_task
                    background = llm_out.get("background") or background
                    method = llm_out.get("method") or method
                    experiments = llm_out.get("experiments") or experiments
                    if llm_out.get("contributions"):
                        contributions = llm_out["contributions"]
                    if llm_out.get("claims"):
                        claims = [self._to_claim(c) for c in llm_out["claims"]]
            except Exception as exc:
                logger.warning("[Extractor] LLM extraction failed, keep heuristic: %s", exc)

        return ContributionExtraction(
            arxiv_id=arxiv_id,
            title=title,
            core_task=core_task.strip(),
            background=background.strip()[:4000],
            method=method.strip()[:4000],
            experiments=experiments.strip()[:4000],
            contributions=contributions[:20],
            claims=claims[:30],
            extraction_method=method_name,
            source_chars=len(text),
        )

    # ------------------------------------------------------------------
    # 启发式实现
    # ------------------------------------------------------------------
    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        out = []
        matches = list(_SECTION_HEADER.finditer(text))
        for i, m in enumerate(matches):
            header = m.group(1).strip().lower()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            out.append((header, text[start:end].strip()))
        return out

    def _collect(self, sections: list[tuple[str, str]], dim: str) -> str:
        kws = _DIM_HEADERS[dim]
        chunks = []
        for header, body in sections:
            if any(k in header for k in kws):
                chunks.append(body)
        return "\n\n".join(chunks)[:4000]

    @staticmethod
    def _section_named(text: str, name: str) -> str:
        m = re.search(r"(?im)^#{1,4}\s*" + re.escape(name) + r"\b\s*$\n", text)
        if not m:
            return ""
        start = m.end()
        nxt = re.search(r"(?im)^#{1,4}\s+\S", text[start:])
        end = start + nxt.start() if nxt else len(text)
        return text[start:end].strip()

    def _collect_contributions(self, text: str, sections) -> list[str]:
        # 1) 显式 Contribution 章节
        for header, body in sections:
            if "contribut" in header or "贡献" in header:
                items = re.findall(r"(?m)^\s*[-*]\s+(.+)$", body)
                if items:
                    return [i.strip() for i in items if len(i.strip()) > 10][:15]
        # 2) 关键词扫描（intro / method 段落）
        found = []
        for sent in _SPLIT_SENT.split(text):
            s = sent.strip()
            if 15 < len(s) < 300 and any(k in s.lower() for k in _CONTRIB_KEYWORDS):
                found.append(s)
        return found[:15]

    def _collect_claims(self, text: str) -> list[Claim]:
        claims = []
        for sent in _SPLIT_SENT.split(text):
            s = sent.strip()
            if len(s) < 15 or len(s) > 400:
                continue
            low = s.lower()
            if not any(k in low for k in sum((r[1] for r in _CLAIM_RULES), [])):
                continue
            ctype = ClaimType.POSITIONAL
            for typ, kws in _CLAIM_RULES:
                if any(k in low for k in kws):
                    ctype = typ
                    break
            section = self._claim_section(text, s)
            claims.append(Claim(text=s, claim_type=ctype, section=section))
        return claims[:30]

    @staticmethod
    def _claim_section(text: str, sentence: str) -> str:
        idx = text.find(sentence[:30])
        if idx < 0:
            return ""
        head = text[:idx].rfind("\n#")
        if head < 0:
            return ""
        m = re.match(r"(?im)^#{1,4}\s+(.+)$", text[head:].splitlines()[0])
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_title(text: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# ") and len(line) > 2:
                return line[2:].strip()
        return ""

    # ------------------------------------------------------------------
    # LLM 增强
    # ------------------------------------------------------------------
    def _llm_extract(self, text: str, title: str) -> Optional[dict]:
        prompt = (
            "你是一名严谨的论文分析助手。请基于以下论文内容，抽取结构化信息，"
            "仅输出 JSON（不要解释），字段: "
            "core_task(str), background(str), method(str), experiments(str), "
            "contributions(list[str]), claims(list[str])。\n\n"
            f"标题: {title}\n\n内容:\n{text[:6000]}"
        )
        raw = self.llm(prompt)
        if not raw:
            return None
        # 容错: 去 ```json 包裹
        raw = re.sub(r"^```(?:json)?", "", raw.strip(), flags=re.I)
        raw = re.sub(r"```$", "", raw.strip())
        try:
            return json.loads(raw)
        except Exception:
            # 尝试抽取第一个 { ... }
            m = re.search(r"\{.*\}", raw, re.S)
            return json.loads(m.group(0)) if m else None

    @staticmethod
    def _to_claim(c) -> Claim:
        if isinstance(c, dict):
            return Claim(text=c.get("text", ""), claim_type=ClaimType(c.get("claim_type", "positional")))
        return Claim(text=str(c))
