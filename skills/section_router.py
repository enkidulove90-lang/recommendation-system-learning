"""Route Markdown sections and create source evidence anchors."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from models.research_profile import EvidenceItem
from skills.base_module import BaseSkill, register_skill


SECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "abstract": ("abstract", "摘要"),
    "introduction": ("introduction", "motivation", "引言", "介绍", "动机"),
    "method": (
        "method", "approach", "framework", "architecture", "model",
        "methodology", "方法", "框架", "架构", "模型",
    ),
    "experiment": (
        "experiment", "experimental", "evaluation", "implementation",
        "dataset", "baseline", "result", "实验", "评估", "实现", "数据集", "结果",
    ),
    "related_work": ("related work", "background", "preliminary", "相关工作", "背景"),
    "conclusion": ("conclusion", "discussion", "limitation", "future work", "结论", "讨论", "局限"),
    "references": ("references", "bibliography", "参考文献"),
    "appendix": ("appendix", "supplement", "附录", "补充材料"),
}

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9@._+-]{2,}|[\u4e00-\u9fff]{2,}")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)


@dataclass(frozen=True)
class SectionSpan:
    heading: str
    section_type: str
    start_char: int
    end_char: int
    text: str


def source_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def route_sections(markdown_text: str) -> list[SectionSpan]:
    matches = list(_HEADING_RE.finditer(markdown_text))
    if not matches:
        return [
            SectionSpan(
                heading="_document",
                section_type="other",
                start_char=0,
                end_char=len(markdown_text),
                text=markdown_text,
            )
        ]

    sections: list[SectionSpan] = []
    if matches[0].start() > 0:
        sections.append(
            SectionSpan(
                heading="_preamble",
                section_type="other",
                start_char=0,
                end_char=matches[0].start(),
                text=markdown_text[:matches[0].start()],
            )
        )

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        heading = match.group(2).strip()
        sections.append(
            SectionSpan(
                heading=heading,
                section_type=classify_heading(heading),
                start_char=start,
                end_char=end,
                text=markdown_text[start:end],
            )
        )
    return sections


def classify_heading(heading: str) -> str:
    normalized = heading.casefold()
    for section_type, keywords in SECTION_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return section_type
    if re.match(r"page\s+\d+", normalized):
        return "page"
    return "other"


def select_evidence(
    *,
    sections: list[SectionSpan],
    query: str,
    claim_type: str,
    preferred_types: tuple[str, ...],
    source_path: Path,
    source_hash: str,
    ordinal: int = 1,
    max_chars: int = 1200,
) -> EvidenceItem | None:
    if not sections:
        return None

    query_tokens = {token.casefold() for token in _TOKEN_RE.findall(query)}
    ranked: list[tuple[float, SectionSpan]] = []
    for section in sections:
        section_lower = section.text.casefold()
        overlap = sum(1 for token in query_tokens if token in section_lower)
        preferred = 4.0 if section.section_type in preferred_types else 0.0
        content_bonus = min(len(section.text) / 4000.0, 1.0)
        ranked.append((preferred + overlap + content_bonus, section))

    score, selected = max(ranked, key=lambda item: item[0])
    quote_start = _best_quote_start(selected.text, query_tokens, max_chars)
    quote_end = min(quote_start + max_chars, len(selected.text))
    raw_quote = selected.text[quote_start:quote_end]
    left_trim = len(raw_quote) - len(raw_quote.lstrip())
    right_trim = len(raw_quote) - len(raw_quote.rstrip())
    quote_start += left_trim
    quote_end -= right_trim
    quote = selected.text[quote_start:quote_end]
    if not quote:
        return None

    absolute_start = selected.start_char + quote_start
    absolute_end = selected.start_char + quote_end
    overlap_count = sum(1 for token in query_tokens if token in quote.casefold())
    confidence = min(0.95, 0.35 + overlap_count * 0.08 + (0.15 if selected.section_type in preferred_types else 0.0))
    return EvidenceItem(
        evidence_id=f"ev-{claim_type}-{ordinal:02d}",
        claim_type=claim_type,
        section=selected.heading,
        start_char=absolute_start,
        end_char=absolute_end,
        quote=quote,
        source_path=str(source_path),
        source_hash=source_hash,
        confidence=round(confidence, 3),
    )


def _best_quote_start(text: str, query_tokens: set[str], max_chars: int) -> int:
    if len(text) <= max_chars:
        return 0
    lowered = text.casefold()
    positions = [lowered.find(token) for token in query_tokens]
    positions = [position for position in positions if position >= 0]
    if not positions:
        return 0
    center = min(positions)
    return max(0, min(center - max_chars // 4, len(text) - max_chars))


@register_skill("section-route")
class SectionRouterSkill(BaseSkill):
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        markdown_path = Path(str(kwargs.get("markdown_path", "")))
        if not markdown_path.exists():
            return {"sections": [], "source_hash": "", "error": f"Markdown not found: {markdown_path}"}
        text = markdown_path.read_text(encoding="utf-8", errors="replace")
        sections = route_sections(text)
        return {
            "sections": [
                {
                    "heading": section.heading,
                    "section_type": section.section_type,
                    "start_char": section.start_char,
                    "end_char": section.end_char,
                }
                for section in sections
            ],
            "source_hash": source_sha256(text),
            "error": None,
        }
