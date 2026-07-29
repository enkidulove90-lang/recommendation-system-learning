"""Read existing DeepSeek Markdown summaries without changing their format."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", flags=re.MULTILINE)


def parse_summary_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    english_match = re.search(
        r"^\*\*英文标题\*\*:[ \t]*([^\r\n]*)$",
        text,
        flags=re.MULTILINE,
    )
    id_match = re.search(
        r"^\*\*arXiv ID\*\*:[ \t]*([^\r\n]+)$",
        text,
        flags=re.MULTILINE,
    )
    generated_match = re.search(
        r"^\*\*生成时间\*\*:[ \t]*([^\r\n]+)$",
        text,
        flags=re.MULTILINE,
    )
    model_match = re.search(r"\*由 DeepSeek \((.+?)\) 自动生成\*", text)

    sections: dict[str, str] = {}
    matches = list(_HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        content = re.sub(
            r"\n+---\s*\n+\*由 DeepSeek .*?\*\s*$",
            "",
            content,
            flags=re.DOTALL,
        ).strip()
        sections[match.group(1).strip()] = content

    innovation_points = _numbered_items(sections.get("创新点", ""))
    datasets = _bullet_items(sections.get("Benchmark 与数据集", ""))
    conditions = _parse_experimental_conditions(sections.get("实验条件", ""))

    return {
        "paper_id": id_match.group(1).strip() if id_match else path.stem.removesuffix("_summary"),
        "chinese_title": title_match.group(1).strip() if title_match else "",
        "title": english_match.group(1).strip() if english_match else "",
        "generated_at": generated_match.group(1).strip() if generated_match else "",
        "summarizer_model": model_match.group(1).strip() if model_match else "",
        "main_contribution": sections.get("主要贡献", ""),
        "innovation_points": innovation_points,
        "methodology": sections.get("方法论", ""),
        "benchmark_datasets": datasets,
        "experimental_conditions": conditions,
        "experimental_results": sections.get("实验效果", ""),
        "agent_relevance": sections.get("对推荐系统 Agent 开发的借鉴", ""),
        "raw_text": text,
    }


def _numbered_items(text: str) -> list[str]:
    items = re.findall(r"^\s*\d+[.)、]\s*(.+?)(?=^\s*\d+[.)、]\s*|\Z)", text, flags=re.MULTILINE | re.DOTALL)
    return [re.sub(r"\s+", " ", item).strip() for item in items if item.strip()]


def _bullet_items(text: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", item).strip()
        for item in re.findall(r"^\s*[-*]\s+(.+?)\s*$", text, flags=re.MULTILINE)
        if item.strip()
    ]


def _parse_experimental_conditions(text: str) -> dict[str, str]:
    labels = {
        "数据与任务设置": "task_and_data",
        "基线与对照": "baselines",
        "评价指标": "metrics",
        "实现环境与关键参数": "implementation",
    }
    result = {value: "not_reported" for value in labels.values()}
    for line in text.splitlines():
        match = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*[：:]\s*(.*)$", line.strip())
        if not match:
            continue
        key = labels.get(match.group(1).strip())
        if key:
            value = match.group(2).strip()
            result[key] = value if value and value != "原文未披露" else "not_reported"
    return result
