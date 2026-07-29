#!/usr/bin/env python3
"""Backfill a consistent experiment-conditions section into paper summaries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from config import settings
from skills.deepseek_summarizer import DeepSeekSummarizer
from storage.paper_assets import find_parsed_markdown
from storage.profile_store import ProfileStore


SECTION_HEADING = "## 实验条件"
INSERT_BEFORE = "## 实验效果"


def _extract_title(summary_text: str, arxiv_id: str) -> str:
    match = re.search(r"^\*\*英文标题\*\*:\s*(.+)$", summary_text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()

    heading = re.search(r"^#\s+(.+)$", summary_text, flags=re.MULTILINE)
    return heading.group(1).strip() if heading else arxiv_id


def _render_section(conditions: dict[str, str], note: str = "") -> str:
    content = f"""## 实验条件

- **数据与任务设置**：{conditions['task_and_data']}
- **基线与对照**：{conditions['baselines']}
- **评价指标**：{conditions['metrics']}
- **实现环境与关键参数**：{conditions['implementation']}

"""
    if note:
        content += f"> {note}\n\n"
    return content


def _insert_or_replace_section(
    summary_text: str,
    section: str,
    *,
    force: bool,
) -> str:
    if SECTION_HEADING in summary_text:
        if not force:
            return summary_text
        pattern = re.compile(
            rf"{re.escape(SECTION_HEADING)}\s*\n.*?(?=^##\s+)",
            flags=re.MULTILINE | re.DOTALL,
        )
        return pattern.sub(section, summary_text, count=1)

    marker_index = summary_text.find(INSERT_BEFORE)
    if marker_index < 0:
        return summary_text.rstrip() + "\n\n" + section
    return summary_text[:marker_index] + section + summary_text[marker_index:]


def backfill(
    *,
    arxiv_id: str = "",
    force: bool = False,
    limit: int = 0,
    source: str = "deepseek",
) -> int:
    summarizer = DeepSeekSummarizer() if source == "deepseek" else None
    if source == "deepseek" and summarizer is not None and not summarizer.is_ready:
        print("ERROR: DEEPSEEK_API_KEY is not configured in the current project .env")
        return 1
    profile_store = ProfileStore()

    summaries_dir = settings.DATA_DIR / "summaries"
    candidates = sorted(summaries_dir.glob("*_summary.md"))
    if arxiv_id:
        candidates = [path for path in candidates if path.name == f"{arxiv_id}_summary.md"]
    if limit > 0:
        candidates = candidates[:limit]

    updated = 0
    skipped = 0
    failed = 0
    for index, summary_path in enumerate(candidates, 1):
        paper_id = summary_path.name.removesuffix("_summary.md")
        summary_text = summary_path.read_text(encoding="utf-8")
        if SECTION_HEADING in summary_text and not force:
            skipped += 1
            print(f"[{index}/{len(candidates)}] {paper_id}: already enriched")
            continue

        if source == "profile":
            profile = profile_store.load_profile(paper_id)
            if profile is None:
                failed += 1
                print(f"[{index}/{len(candidates)}] {paper_id}: profile not found")
                continue
            conditions, note = _profile_conditions(profile)
        else:
            parsed_md = find_parsed_markdown(paper_id)
            if parsed_md is None:
                failed += 1
                print(f"[{index}/{len(candidates)}] {paper_id}: parsed Markdown not found")
                continue

            title = _extract_title(summary_text, paper_id)
            full_text = parsed_md.read_text(encoding="utf-8", errors="replace")
            result = summarizer.extract_experimental_conditions(
                title=title,
                full_text=full_text,
            )
            if result.get("error"):
                failed += 1
                print(f"[{index}/{len(candidates)}] {paper_id}: {result['error']}")
                continue
            conditions = result["experimental_conditions"]
            note = "本节由 DeepSeek 根据论文原文补齐，未披露字段保持显式标记。"

        section = _render_section(conditions, note=note)
        enriched = _insert_or_replace_section(summary_text, section, force=force)
        summary_path.write_text(enriched, encoding="utf-8")
        updated += 1
        print(f"[{index}/{len(candidates)}] {paper_id}: updated")

    print(f"Completed: updated={updated}, skipped={skipped}, failed={failed}")
    return 0 if failed == 0 else 2


def _profile_conditions(profile: object) -> tuple[dict[str, str], str]:
    if profile.quality.grade == "D":
        blocked = "资产身份冲突，暂不写入实验事实，等待修复解析原文与摘要对应关系。"
        return {
            "task_and_data": blocked,
            "baselines": blocked,
            "metrics": blocked,
            "implementation": blocked,
        }, "Summary 2.0 质量闸门未通过；该论文当前不可作为实验事实来源。"

    experiment = profile.experiment
    datasets = "、".join(dataset.paper_name for dataset in experiment.datasets)
    task_parts = []
    if datasets:
        task_parts.append(f"数据集：{datasets}")
    if experiment.protocol.task and experiment.protocol.task != "not_reported":
        task_parts.append(f"任务：{experiment.protocol.task}")
    if experiment.protocol.split != "not_reported":
        task_parts.append(f"划分：{experiment.protocol.split}")

    baselines = "；".join(experiment.protocol.baselines) or "原文未披露"
    metrics = "、".join(experiment.protocol.metrics) or "原文未披露"
    implementation_parts = []
    if experiment.implementation.hardware:
        implementation_parts.append(
            "硬件："
            + "、".join(
                f"{item.count or ''}{'×' if item.count else ''}{item.model}"
                for item in experiment.implementation.hardware
            )
        )
    if experiment.implementation.framework:
        implementation_parts.append(f"框架：{experiment.implementation.framework}")
    if experiment.implementation.optimizer:
        implementation_parts.append(f"优化器：{experiment.implementation.optimizer}")
    if experiment.implementation.hyperparameters:
        implementation_parts.append(
            "超参数："
            + "、".join(
                f"{key}={value}"
                for key, value in experiment.implementation.hyperparameters.items()
            )
        )
    evidence_ids = experiment.protocol.evidence_ids or experiment.implementation.evidence_ids
    evidence_note = (
        "实验条件由 Summary 2.0 从解析原文提取；证据锚点："
        + ("、".join(evidence_ids) if evidence_ids else "未定位，需人工复核")
        + "。"
    )
    return {
        "task_and_data": "；".join(task_parts) or "原文未披露",
        "baselines": baselines,
        "metrics": metrics,
        "implementation": "；".join(implementation_parts) or "原文未披露",
    }, evidence_note


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arxiv-id", default="", help="Only process one arXiv ID")
    parser.add_argument("--force", action="store_true", help="Replace an existing section")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N summaries")
    parser.add_argument(
        "--source",
        choices=("deepseek", "profile"),
        default="deepseek",
        help="Use DeepSeek or an already validated Summary 2.0 profile",
    )
    args = parser.parse_args()
    raise SystemExit(
        backfill(
            arxiv_id=args.arxiv_id,
            force=args.force,
            limit=args.limit,
            source=args.source,
        )
    )


if __name__ == "__main__":
    main()
