"""
novelty/report.py — 报告生成模块

把 NoveltyReport 渲染为人类可读的 Markdown 报告 + 机器可读 JSON。
报告包含: 四维度剖析、邻域论文表、设计轴差异矩阵（三态标签 + 证据）、
明确的"本工具只给证据、不下终审结论"声明。

速览 summary_note 由差异矩阵自动汇总，仍是"建议审视的差异点"而非结论。
"""

from __future__ import annotations

import json
import logging
from typing import Tuple

from .schemas import NoveltyLabel, NoveltyReport

logger = logging.getLogger(__name__)


class ReportGenerator:
    def generate(self, report: NoveltyReport) -> Tuple[str, str]:
        md = self._render_markdown(report)
        js = json.dumps(report.model_dump(), ensure_ascii=False, indent=2)
        return md, js

    # ------------------------------------------------------------------
    def _render_markdown(self, r: NoveltyReport) -> str:
        L = []
        L.append(f"# 论文创新性辅助分析报告 · {r.title or r.arxiv_id}")
        L.append("")
        L.append(f"- arXiv: `{r.arxiv_id}`  ")
        L.append(f"- 生成时间: {r.generated_at}  ")
        L.append(f"- 引擎: {r.engine_version}  ")
        L.append(f"- 嵌入后端: {r.meta.get('embedder', 'n/a')} · 在线源: {', '.join(r.meta.get('online_sources', [])) or '无'}")
        L.append("")

        # 四维度
        L.append("## 一、四维度剖析（结构化抽取）")
        L.append("")
        e = r.extraction
        L.append(f"**核心任务**: {e.core_task or '—'}")
        L.append("")
        L.append(f"**背景/问题**: {e.background[:600] or '—'}")
        L.append("")
        L.append(f"**方法/路线**: {e.method[:600] or '—'}")
        L.append("")
        L.append(f"**实验/评估**: {e.experiments[:600] or '—'}")
        L.append("")
        if e.contributions:
            L.append("**贡献点**:")
            for c in e.contributions[:10]:
                L.append(f"- {c}")
            L.append("")
        if e.claims:
            L.append(f"**关键主张（{len(e.claims)} 条，节选）**:")
            for c in e.claims[:6]:
                L.append(f"- [{c.claim_type.value}] {c.text[:200]}")
            L.append("")

        # 邻域
        L.append("## 二、邻域论文（对比对象）")
        L.append("")
        if r.neighbors:
            L.append("| # | 标题 | 年份 | 相似度 | 关系 | 来源 |")
            L.append("|---|------|------|--------|------|------|")
            for i, n in enumerate(r.neighbors[:15], 1):
                sim = f"{n.similarity:.3f}" if n.similarity else "—"
                L.append(f"| {i} | {n.title[:60] or '—'} | {n.year or '—'} | {sim} | {n.relation} | {n.source.value} |")
        else:
            L.append("（未检索到邻域论文；可联网补全 Semantic Scholar / OpenAlex）")
        L.append("")

        # 差异矩阵
        L.append("## 三、设计轴差异矩阵（证据导向 · 三态标签）")
        L.append("")
        if r.difference_matrix:
            L.append("| 设计轴 | 目标取值 | 邻域取值 | 差异 | 标签 | 置信 |")
            L.append("|--------|----------|----------|------|------|------|")
            for d in r.difference_matrix:
                L.append(
                    f"| {d.axis} | {d.target_value[:30]} | {d.neighbor_value[:30]} "
                    f"| {d.difference[:40]} | {d.label.value} | {d.confidence:.2f} |"
                )
            L.append("")
            # 证据明细
            L.append("**证据明细**")
            for d in r.difference_matrix:
                if d.label != NoveltyLabel.UNCLEAR:
                    L.append(f"- **[{d.axis}] {d.label.value}** — {d.evidence}")
        else:
            L.append("（差异矩阵为空：邻域论文文本不可得或尚未对比）")
        L.append("")

        # 速览
        L.append("## 四、差异点速览（非结论）")
        L.append("")
        L.append(r.summary_note or "—")
        L.append("")

        # 声明
        L.append("> ⚠️ " + r.disclaimer)
        return "\n".join(L)

    # ------------------------------------------------------------------
    @staticmethod
    def build_summary_note(r: NoveltyReport) -> str:
        from collections import Counter
        cnt = Counter(d.label for d in r.difference_matrix)
        can_ref = cnt.get(NoveltyLabel.CAN_REFUTE, 0)
        cannot = cnt.get(NoveltyLabel.CANNOT_REFUTE, 0)
        unclear = cnt.get(NoveltyLabel.UNCLEAR, 0)
        axes = [d.axis for d in r.difference_matrix if d.label != NoveltyLabel.UNCLEAR]
        note = (
            f"共识别 {len(r.difference_matrix)} 个设计轴差异点："
            f"其中 {can_ref} 项显示与邻域做法高度相似（建议审视）、"
            f"{cannot} 项存在明确差异（潜在区分点）、{unclear} 项证据不足。"
        )
        if axes:
            note += " 重点审视轴：" + "、".join(axes[:5]) + "。"
        note += " 最终新颖性判断请结合证据由人工作出。"
        return note
