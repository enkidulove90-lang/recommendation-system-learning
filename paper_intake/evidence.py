from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


REPLACEMENT_CHARACTER = "\ufffd"
STABLE_ANCHOR_IDS = (
    "introduction.context",
    "introduction.problem",
    "method.overview",
    "method.details",
    "experiments.setup",
    "experiments.main-results",
    "experiments.ablation",
    "conclusion.summary",
    "conclusion.limitations",
)
_NUMBER = re.compile(r"(?<![\w.])(?:\d+(?:\.\d+)?%|\d+(?:\.\d+)?)(?![\w.])")
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_FIGURE_LABEL = re.compile(r"(?i)\b(?:figure|fig\.)\s*(\d+[a-z]?)\b")


class ContentIntegrityError(ValueError):
    pass


def ensure_clean_text(value: str, *, stage: str) -> str:
    if REPLACEMENT_CHARACTER in value:
        raise ContentIntegrityError(f"{stage}: replacement character U+FFFD is forbidden")
    return value


class EvidenceBlock(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    source_id: str
    text: str


class NumberFact(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    value: str
    source_id: str


class FigureFact(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    path: str
    sha256: str
    figure_label: str = ""
    original_caption: str = ""
    source_id: str


class FactPack(BaseModel):
    metadata: dict[str, Any]
    metadata_source: str = "authoritative_metadata"
    evidence_blocks: list[EvidenceBlock] = Field(default_factory=list)
    key_numbers: list[NumberFact] = Field(default_factory=list)
    figures: list[FigureFact] = Field(default_factory=list)
    anchor_ids: list[str] = Field(default_factory=lambda: list(STABLE_ANCHOR_IDS))


def _paragraphs(markdown: str) -> list[tuple[int, int, str]]:
    lines = markdown.splitlines()
    blocks: list[tuple[int, int, str]] = []
    start: int | None = None
    current: list[str] = []
    for line_number, line in enumerate(lines, 1):
        if line.strip() and not line.lstrip().startswith("#"):
            if start is None:
                start = line_number
            current.append(line)
            continue
        if current and start is not None:
            blocks.append((start, line_number - 1, "\n".join(current).strip()))
            start, current = None, []
    if current and start is not None:
        blocks.append((start, len(lines), "\n".join(current).strip()))
    return blocks


def build_fact_pack(
    *,
    markdown: str,
    metadata: dict[str, Any],
    figures: list[dict[str, str]],
) -> FactPack:
    clean = ensure_clean_text(markdown, stage="prompt_markdown")
    for key, value in metadata.items():
        if isinstance(value, str):
            ensure_clean_text(value, stage=f"metadata.{key}")
    blocks: list[EvidenceBlock] = []
    numbers: list[NumberFact] = []
    for index, (start, end, text) in enumerate(_paragraphs(clean), 1):
        source_id = f"mineru:l{start}-l{end}"
        block_id = f"evidence.{index:04d}"
        blocks.append(EvidenceBlock(id=block_id, source_id=source_id, text=text))
        for number_index, match in enumerate(_NUMBER.finditer(text), 1):
            numbers.append(
                NumberFact(
                    id=f"number.{index:04d}.{number_index}",
                    value=match.group(0),
                    source_id=source_id,
                )
            )

    captions_by_path: dict[str, str] = {}
    for match in _IMAGE.finditer(clean):
        captions_by_path[match.group(2).strip()] = match.group(1).strip()

    figure_facts: list[FigureFact] = []
    for index, item in enumerate(figures, 1):
        path = str(item.get("path", "")).strip()
        caption = captions_by_path.get(path, "")
        label_match = _FIGURE_LABEL.search(caption)
        figure_facts.append(
            FigureFact(
                id=f"fig{index}",
                path=path,
                sha256=str(item.get("sha256", "")).strip(),
                figure_label=f"Figure {label_match.group(1)}" if label_match else f"Figure {index}",
                original_caption=caption,
                source_id=f"mineru:figure:{index}",
            )
        )

    return FactPack(
        metadata=dict(metadata),
        evidence_blocks=blocks,
        key_numbers=numbers,
        figures=figure_facts,
    )
