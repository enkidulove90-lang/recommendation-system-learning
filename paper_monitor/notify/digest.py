"""每日 digest Markdown 渲染。防静默空推：空列表返回 None。"""
from __future__ import annotations

from datetime import date

from ..models import Paper


def _link(p: Paper) -> str:
    if p.arxiv_id:
        return f"https://arxiv.org/abs/{p.arxiv_id}"
    if p.doi:
        return f"https://doi.org/{p.doi}"
    if p.id:
        return p.id
    return ""


def _signals(p: Paper) -> str:
    parts = []
    if p.upvotes is not None:
        parts.append(f"👍{p.upvotes}")
    if p.github_stars is not None:
        parts.append(f"⭐{p.github_stars}")
    if p.code_count is not None and p.code_count > 0:
        parts.append(f"💻code={p.code_count}")
    if p.influential_citation_count is not None:
        parts.append(f"infCite={p.influential_citation_count}")
    if p.cited_by_count:
        parts.append(f"cite={p.cited_by_count}")
    return " | ".join(parts) if parts else "—"


def render_digest(
    papers: list[Paper],
    bursts: list[dict] | None = None,
    top_n: int = 15,
    day: str | None = None,
) -> str | None:
    """渲染 digest。papers 为空返回 None（防静默空推）。"""
    if not papers:
        return None
    day = day or date.today().isoformat()
    kept = papers[:top_n]
    lines = [
        f"# 📡 前沿论文 Daily Digest — {day}",
        "",
        f"> 共 {len(papers)} 篇进入推荐流（按综合 score 排序，展示 Top {len(kept)}）。",
        "",
    ]
    if bursts:
        lines.append("## 🔥 引用爆发预警")
        for b in bursts:
            lines.append(f"- **{b['title']}** — 引用环比 +{b['delta']} (历史: {b['series']})")
        lines.append("")
    lines.append("## 📄 推荐论文")
    lines.append("")
    for i, p in enumerate(kept, 1):
        topics = ", ".join(t.display_name for t in p.topics[:5] if t.display_name) or "—"
        authors = ", ".join(a.name for a in p.authors[:3] if a.name)
        if len(p.authors) > 3:
            authors += " et al."
        link = _link(p)
        lines.append(f"### {i}. {p.title}")
        lines.append(f"- **score**: {p.score:.3f}  |  **source**: {p.source}")
        lines.append(f"- **topics**: {topics}")
        if authors:
            lines.append(f"- **authors**: {authors}")
        lines.append(f"- **signals**: {_signals(p)}")
        if link:
            lines.append(f"- **link**: {link}")
        lines.append("")
    return "\n".join(lines)
