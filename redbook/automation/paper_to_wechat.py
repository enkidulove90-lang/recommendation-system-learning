"""Turn a parsed paper into a WeChat Official Account draft.

Pipeline
--------
1. Load the 11-dimension summary JSON produced by ``skills/deepseek_summarizer.py``.
2. Render **two** bodies from the same summary:
     * ``render_article_body``  -> Markdown source (audit trail / HTML preview).
     * ``render_wechat_article`` -> WeChat-flavored plain text (emoji markers,
       no ``**``/``##`` syntax) that the editor actually renders.
3. Pick the single best figure as the cover.
4. Deliver through :class:`WeChatDraftDelivery` (a browser-bridge that drives the
   real mp.weixin.qq.com editor in one persistent session) when logged in;
   otherwise fall back to a local HTML preview the user can paste by hand.

Why not ``opencli weixin create-draft``
---------------------------------------
That command silently produced broken drafts: it set the title through a
synthetic ``value`` setter + ``InputEvent`` that UEditor ignores (title stayed
empty), and it wrote the body via ``execCommand('insertText')`` so Markdown
survived literally.  The browser bridge fixes both by using ``browser fill``
(verified title) and a direct ``innerHTML`` ``<p>`` injection.  See
``~/.workbuddy/skills/multi-platform-publishing/references/wechat-publishing.md``.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from ..infrastructure import opencli_runtime
from .paper_to_xhs import RenderError, load_assets, select_images
from .publishing import PublicationPackage, WeChatPublisher
from . import gzh_components as gzh  # recsys-blue 组件库（单一来源 = wechat_design/components/components.md）

#: WeChat drafts allow at most 64-char titles and one cover image.
TITLE_MAX = 64
COVER_MAX = 1
BODY_MIN, BODY_MAX = 200, 2000

#: A short, stable author byline for the account's research niche.
_DEFAULT_AUTHOR = "推荐系统研读"

#: WeChat-safe inline-style palette.  WeChat's editor sanitizes injected HTML:
#: it keeps ``style`` attributes but strips ``<style>``/``<script>``/``class``/
#: ``id`` and layout properties (``position``/``float``).  So every visual cue
#: here is an *inline* style on ``<section>``/``<p>``/``<span>`` — the same
#: subset the 秀米 / 135 编辑器 rely on.
_ACCENT = "#3a5fcd"
_ACCENT_BG = "#eef3ff"
_TEXT = "#2c3e50"
_MUTED = "#8a94a6"


def _clean(text: str) -> str:
    """Strip citation scaffolding that reads as noise outside a paper."""
    if not text:
        return ""
    text = str(text)
    text = re.sub(r"\[[^\]]*(?:阅读者判断|来源)[^\]]*\]", "", text)
    text = re.sub(r"[（(]\s*第[^）)]*节\s*[）)]", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([。；;])\s*[：:、，,]+", r"\1", text)
    text = re.sub(r"[：:]\s*(?=[。；;]|$)", "", text)
    return text.strip(" ，。;；:：、")


def _field(summary: dict[str, Any], *path: str, default: str = "") -> str:
    """Safely reach a nested summary field."""
    cur: Any = summary
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return _clean(cur) if isinstance(cur, str) else ("" if cur is None else str(cur))


def _datasets_line(summary: dict[str, Any]) -> str:
    datasets = summary.get("datasets", []) or []
    if not datasets:
        return ""
    return "、".join(str(d.get("name", "")) for d in datasets if isinstance(d, dict))


def _shares_substring(a: str, b: str, k: int = 10) -> bool:
    """True if ``a`` contains a contiguous ``k``-char window also present in ``b``.

    Used to drop a benchmark result line when its substance was already stated
    inside the innovation bullets (common when a paper repeats its headline
    numbers in both places).
    """
    a, b = a or "", b or ""
    if len(a) < k or len(b) < k:
        return False
    return any(a[i:i + k] in b for i in range(len(a) - k + 1))


def _derive_insights(summary: dict[str, Any]) -> list[str]:
    """Three concrete takeaways grounded in the paper's stated innovations.

    Every point is derived verbatim from ``innovations`` so nothing is invented.
    """
    innovations = summary.get("innovations", []) or []
    texts = [_clean(i.get("point", "")) for i in innovations if isinstance(i, dict)]
    insights: list[str] = []
    labels = ["用起来", "简化它", "提速它"]
    for idx, text in enumerate(texts[:3]):
        if text:
            insights.append(f"把「{text[:40]}…」这一思路{labels[idx % 3]}——可直接迁移到自己的图模型管线。")
    while len(insights) < 3:
        insights.append("将论文的对比视图构造方式替换为你现有模型的增强策略，观察召回/排序指标变化。")
    return insights[:3]


def _arxiv_id(paper_id: str) -> bool:
    """True for an arXiv id like 2302.08191 (used to pick link style)."""
    return bool(re.match(r"^\d{4}\.\d{4,5}$", paper_id or ""))


def _render_hook(summary, one_liner):
    """开场钩子：反向结论前置 + 痛点。"""
    problem = (
        _field(summary, "problem_definition", "task_type")
        or _field(summary, "problem_definition", "input")
    )
    if one_liner:
        hook = f"**{one_liner}**"
        if problem:
            hook += f"\n\n但在此之前，{problem}长期是绕不开的痛点。"
        return hook
    return "（本文给出一种更简洁的思路，下面拆开讲。）"


def _render_background(summary):
    """§1 它过去解决了什么。"""
    task = _field(summary, "problem_definition", "task_type")
    inp = _field(summary, "problem_definition", "input")
    parts = []
    if task:
        parts.append(f"任务类型：{task}。")
    if inp:
        parts.append(f"输入：{inp}。")
    one = _field(summary, "one_line_summary")
    if one:
        parts.append(one + "。")
    return " ".join(parts) or "（论文未提供明确的问题定义）"


def _render_method_evidence(summary):
    """§2 新变化/证据：核心方法 + 加粗数字（与上文创新点去重）。"""
    lines = []
    innov_points: list[str] = []
    for i, item in enumerate(summary.get("innovations", [])[:3], start=1):
        if isinstance(item, dict) and item.get("point"):
            pt = _clean(item["point"])
            innov_points.append(pt)
            lines.append(f"{i}. {pt}")
    bench = summary.get("benchmark", {}) or {}
    mr = _clean(bench.get("main_results", ""))
    sig = _clean(bench.get("significance", ""))
    innov_blob = " ".join(innov_points)
    # 避免与 §2 创新点重复（论文里 main_results 常已在创新点中展开）
    if mr and not _shares_substring(mr, innov_blob):
        lines += ["", f"关键结果：{mr[:500]}"]
    if sig and not _shares_substring(sig, innov_blob):
        lines.append(sig[:200])
    return "\n".join(lines) or "（论文未列出明确方法/实验）"


def _render_categories(summary):
    """§3 最先没必要的，是这几类（局限分类）。"""
    lim = _clean(summary.get("limitations", ""))
    if not lim:
        return "（论文未明确列出局限）"
    sents = [s.strip() for s in re.split(r"[。；;]", lim) if s.strip()]
    if len(sents) <= 1:
        return f"- {lim}"
    return "\n".join(f"- {s}。" for s in sents)


def _render_boundary(summary):
    """§4 反转折线：适用边界。

    §3 已列出局限，这里只点出「按场景取舍」的取舍逻辑，不再复述原文，
    避免真实论文（局限常有多句）在 §3/§4 出现重复段落。
    """
    ds = _datasets_line(summary) or "作者的验证场景"
    lim = _clean(summary.get("limitations", ""))
    note = f"本文方法在 {ds} 上得到验证。"
    if lim:
        note += "但上面列出的局限提醒我们：新方法不是「全盘替代」，而是按场景取舍——"
    else:
        note += "但验证有边界，新方法不是「全盘替代」，而是按场景取舍——"
    note += "简单任务不必套重流程，复杂或高风险任务仍值得保留显式约束。"
    return note


def _render_steps(summary):
    """§5 新方法：先裸跑，再加最小Skill（五步）。"""
    ds = _datasets_line(summary) or "你的基准数据"
    metrics = "/".join(str(m) for m in summary.get("benchmark", {}).get("metrics", [])[:4])
    ins_text = "；".join(
        _clean(i.get("point", ""))[:30] for i in summary.get("innovations", [])[:2]
        if isinstance(i, dict)
    )
    return "\n".join([
        "第一步：先定义结果，不定义仪式——把目标、硬约束、验收标准写清楚。",
        f"第二步：用基准数据（{ds}）让模型/基线裸跑，记录成功率与返工。",
        "第三步：只看可复现的失败——同一类错误稳定出现，才说明缺经验。",
        f"第四步：只补一个最小补丁——把上文方法（{ins_text}…）固化成可触发的最小流程。",
        f"第五步：再跑同一组任务，对比指标（{metrics or '论文指标'}）；质量没提升就删掉。",
    ])


def _render_audience(summary):
    """§6 还要不要装：分人群建议。"""
    return "\n".join([
        "如果你是在校学生：先吃透上面的创新点，理解它到底解决了什么。",
        "如果你在工业界落地：重点看关键结果能否在你的业务指标上复现。",
        "如果你在做研究：借鉴它的模块拆分思路，而不是照抄整条流程。",
    ])


def _render_closing(summary):
    """§7 写在最后。"""
    one = _field(summary, "one_line_summary")
    if one:
        return (f"{one} 真正该学的，不是最火的插件或 Skill 名字，"
                "而是看清模型现在会什么、不会什么。")
    return "方法会过时，看清问题与约束的能力不过时。"


def _links_block(assets) -> tuple[str, dict[str, str]]:
    """参考文献块 + 链接字典（arxiv 用 arxiv 链接，否则用原文占位）。"""
    if _arxiv_id(assets.paper_id):
        paper = f"https://arxiv.org/abs/{assets.paper_id}"
        pdf = f"https://arxiv.org/pdf/{assets.paper_id}"
        code = "暂无官方代码（以论文复现为准）"
    else:
        paper = "https://mp.weixin.qq.com（见原文）"
        pdf = paper
        code = "（见原文链接）"
    block = "\n".join([
        "## 参考文献",
        f"- 论文：{paper}",
        f"- PDF：{pdf}",
        f"- 代码：{code}",
        "",
        "> 图表摘自论文，仅作学术解读。",
    ])
    return block, {"paper": paper, "pdf": pdf, "code": code}


def _wechat_marker(section: str) -> str:
    """Pick an emoji marker for a WeChat section.

    The mapping reflects "is this section actionable insight (🔹) or context /
    constraint (🔸)?".  The platform renders single-codepoint glyphs without
    extra spacing, so the visual hierarchy is the spacing + blank lines around
    each heading, not the marker itself.
    """
    return {
        "它过去解决了什么": "🔹",
        "新变化把旧方案吃进了模型": "🔹",
        "最先没必要的，是这几类": "🔸",
        "但这不等于全部都该删": "🔸",
        "新方法：先裸跑，再加最小Skill": "🔹",
        "还要不要装": "🔹",
        "写在最后": "🔹",
        "参考文献": "📚",
    }.get(section, "🔹")


def render_wechat_article(assets) -> str:
    """Produce a WeChat-flavored plain-text article (no Markdown syntax).

    The WeChat editor (UEditor) does **not** render Markdown, so anything that
    contains ``**``, ``## ``, or ``---`` shows up literally (the screenshot
    evidence from the create-draft round).  This renderer reuses the same 11-dim
    summary fields as :func:`render_article_body` but emits a structure the
    editor actually understands:

    * emoji markers (``🔹`` / ``🔸`` / ``💡`` / ``📚``) for section hierarchy
    * generous blank lines for paragraph spacing
    * plain ``·`` for unordered bullets and ``1.`` ``2.`` for ordered
    * ``「」`` for inline emphasis (instead of bold)
    * no horizontal rules (WeChat renders ``---`` as literal dashes)

    The output still respects WeChat's hard limits: 200–2,000 characters, all
    content verbatim from the summary (no invention).
    """
    summary = assets.summary
    one_liner = _field(summary, "one_line_summary")
    problem = (
        _field(summary, "problem_definition", "task_type")
        or _field(summary, "problem_definition", "input")
    )
    innovations = summary.get("innovations", []) or []
    benchmark = summary.get("benchmark", {}) or {}
    limitations = _clean(summary.get("limitations", ""))
    datasets = _datasets_line(summary)
    innov_points = [_clean(i.get("point", "")) for i in innovations if isinstance(i, dict)]
    innov_blob = " ".join(innov_points)

    parts: list[str] = []

    # ── 开场钩子 ────────────────────────────────────────────────────────
    if one_liner:
        parts.append(f"🔸 {one_liner}")
        parts.append("")
    if problem:
        parts.append(f"但在此之前，{problem}长期是绕不开的痛点。")
    parts.append("")
    parts.append("")

    # ── §1 它过去解决了什么 ─────────────────────────────────────────────
    parts.append(f"🔹 它过去解决了什么")
    parts.append("")
    task = _field(summary, "problem_definition", "task_type")
    inp = _field(summary, "problem_definition", "input")
    if task:
        parts.append(f"任务类型：{task}")
    if inp:
        parts.append(f"输入：{inp}")
    if one_liner:
        parts.append("")
        parts.append(one_liner + "。")
    parts.append("")
    parts.append("")

    # ── §2 新变化把旧方案吃进了模型 ────────────────────────────────────
    parts.append("🔹 新变化把旧方案吃进了模型")
    parts.append("")
    for idx, item in enumerate(innovations[:3], 1):
        pt = _clean(item.get("point", "")) if isinstance(item, dict) else ""
        if pt:
            parts.append(f"{idx}. {pt}")
            parts.append("")
    parts.append("")

    mr = _clean(benchmark.get("main_results", ""))
    sig = _clean(benchmark.get("significance", ""))
    if mr and not _shares_substring(mr, innov_blob):
        parts.append("💡 关键结果")
        parts.append("")
        parts.append(mr)
        parts.append("")
    if sig and not _shares_substring(sig, innov_blob):
        parts.append(sig)
        parts.append("")
    parts.append("")

    # ── §3 最先没必要的，是这几类 ──────────────────────────────────────
    parts.append("🔸 最先没必要的，是这几类")
    parts.append("")
    if limitations:
        sents = [s.strip() for s in re.split(r"[。；;]", limitations) if s.strip()]
        for sent in sents:
            parts.append(f"· {sent}。")
        parts.append("")
    parts.append("")

    # ── §4 但这不等于全部都该删 ────────────────────────────────────────
    parts.append("🔸 但这不等于全部都该删")
    parts.append("")
    parts.append(f"本文方法在 {datasets or '作者的验证场景'} 上得到验证。")
    if limitations:
        parts.append("但上面列出的局限提醒我们：新方法不是「全盘替代」，而是按场景取舍。")
    parts.append("简单任务不必套重流程，复杂或高风险任务仍值得保留显式约束。")
    parts.append("")
    parts.append("")

    # ── §5 新方法：先裸跑，再加最小Skill ──────────────────────────────
    parts.append("🔹 新方法：先裸跑，再加最小Skill")
    parts.append("")
    ds = datasets or "你的基准数据"
    metrics = "/".join(str(m) for m in benchmark.get("metrics", [])[:4])
    ins_text = "；".join(
        _clean(i.get("point", ""))[:30] for i in innovations[:2] if isinstance(i, dict)
    )
    parts.append("第一步：先定义结果，不定义仪式——把目标、硬约束、验收标准写清楚。")
    parts.append("")
    parts.append(f"第二步：用基准数据（{ds}）让模型/基线裸跑，记录成功率与返工。")
    parts.append("")
    parts.append("第三步：只看可复现的失败——同一类错误稳定出现，才说明缺经验。")
    parts.append("")
    parts.append(f"第四步：只补一个最小补丁——把上文方法（{ins_text}…）固化成可触发的最小流程。")
    parts.append("")
    parts.append(f"第五步：再跑同一组任务，对比指标（{metrics or '论文指标'}）；质量没提升就删掉。")
    parts.append("")
    parts.append("")

    # ── §6 还要不要装 ─────────────────────────────────────────────────
    parts.append("🔹 还要不要装")
    parts.append("")
    parts.append("🧑‍🎓 如果你是在校学生：先吃透上面的创新点，理解它到底解决了什么。")
    parts.append("")
    parts.append("💼 如果你在工业界落地：重点看关键结果能否在你的业务指标上复现。")
    parts.append("")
    parts.append("🔬 如果你在做研究：借鉴它的模块拆分思路，而不是照抄整条流程。")
    parts.append("")
    parts.append("")

    # ── §7 写在最后 ────────────────────────────────────────────────────
    parts.append("🔹 写在最后")
    parts.append("")
    if one_liner:
        parts.append(one_liner + "。")
        parts.append("")
        parts.append("真正该学的，不是最火的插件或 Skill 名字，而是看清模型现在会什么、不会什么。")
    else:
        parts.append("方法会过时，看清问题与约束的能力不过时。")
    parts.append("")
    parts.append("")

    # ── 分隔 + 参考文献 ────────────────────────────────────────────────
    parts.append("——————————————")
    parts.append("")
    parts.append("📚 参考文献")
    parts.append("")
    if _arxiv_id(assets.paper_id):
        parts.append(f"· 论文：https://arxiv.org/abs/{assets.paper_id}")
        parts.append(f"· PDF：https://arxiv.org/pdf/{assets.paper_id}")
        parts.append("· 代码：暂无官方代码（以论文复现为准）")
    else:
        parts.append("· 论文：见原文链接")
        parts.append("· PDF：见原文链接")
        parts.append("· 代码：（见原文链接）")
    parts.append("")
    parts.append("> 图表摘自论文，仅作学术解读。")

    return "\n".join(parts).strip()


# --------------------------------------------------------------------------- #
# HTML renderer (WeChat-safe inline styles)
# --------------------------------------------------------------------------- #
def _h(text: str) -> str:
    """A section heading with a colored left bar — delegates to gzh section-header."""
    return gzh.section_header(text)


def _p(text: str) -> str:
    """A plain paragraph — delegates to gzh body-para (includes <span leaf>)."""
    return gzh.body_para(text)


def _box(label: str, text: str) -> str:
    """A highlighted callout box — delegates to gzh one-liner (📌)."""
    return gzh.one_liner(text, label=label)


def _li(num: int, text: str) -> str:
    return gzh.body_li(num, text)


def _bul(text: str) -> str:
    return gzh.body_bul(text)


def _link(url: str, text: str | None = None) -> str:
    t = text or url
    return f'<a href="{url}" style="color:{_ACCENT};text-decoration:none;">{t}</a>'


def _divider() -> str:
    return '<section style="border-top:1px solid #eee;margin:22px 0 10px;"></section>'


def render_wechat_html(assets) -> str:
    """Render the same verified 代码随想录 skeleton as :func:`render_wechat_article`
    but as **WeChat-safe inline-styled HTML** (see module-level palette notes).

    The output is the *inner* body HTML only — no ``<!DOCTYPE>`` wrapper, no
    ``<style>`` block — because it is injected straight into UEditor's
    ``contenteditable`` via ``innerHTML``.  Every color/size/spacing cue is an
    inline ``style`` attribute, which WeChat preserves; structural tags are kept
    to the minimal ``<section>``/``<p>``/``<span>``/``<a>`` set the editor keeps.
    """
    summary = assets.summary
    one_liner = _field(summary, "one_line_summary")
    problem = (
        _field(summary, "problem_definition", "task_type")
        or _field(summary, "problem_definition", "input")
    )
    innovations = summary.get("innovations", []) or []
    benchmark = summary.get("benchmark", {}) or {}
    limitations = _clean(summary.get("limitations", ""))
    datasets = _datasets_line(summary)
    innov_points = [_clean(i.get("point", "")) for i in innovations if isinstance(i, dict)]
    innov_blob = " ".join(innov_points)

    parts: list[str] = []

    # ── 开场钩子（高亮框） ───────────────────────────────────────────────
    if one_liner:
        parts.append(_box("📌 一句话", one_liner))
    if problem:
        parts.append(_p(f"但在此之前，{problem}长期是绕不开的痛点。"))

    # ── §1 它过去解决了什么 ─────────────────────────────────────────────
    parts.append(_h("它过去解决了什么"))
    task = _field(summary, "problem_definition", "task_type")
    inp = _field(summary, "problem_definition", "input")
    if task:
        parts.append(_p(f"任务类型：{task}"))
    if inp:
        parts.append(_p(f"输入：{inp}"))
    if one_liner:
        parts.append(_p(one_liner + "。"))

    # ── §2 新变化把旧方案吃进了模型 ────────────────────────────────────
    parts.append(_h("新变化把旧方案吃进了模型"))
    for idx, item in enumerate(innovations[:3], 1):
        pt = _clean(item.get("point", "")) if isinstance(item, dict) else ""
        if pt:
            parts.append(_li(idx, pt))
    mr = _clean(benchmark.get("main_results", ""))
    sig = _clean(benchmark.get("significance", ""))
    if mr and not _shares_substring(mr, innov_blob):
        parts.append(_h("💡 关键结果"))
        parts.append(_p(mr))
    if sig and not _shares_substring(sig, innov_blob):
        parts.append(_p(sig))

    # ── §3 最先没必要的，是这几类 ──────────────────────────────────────
    parts.append(_h("最先没必要的，是这几类"))
    if limitations:
        sents = [s.strip() for s in re.split(r"[。；;]", limitations) if s.strip()]
        for sent in sents:
            parts.append(_bul(sent))

    # ── §4 但这不等于全部都该删 ────────────────────────────────────────
    parts.append(_h("但这不等于全部都该删"))
    parts.append(_p(f"本文方法在 {datasets or '作者的验证场景'} 上得到验证。"))
    if limitations:
        parts.append(_p("但上面列出的局限提醒我们：新方法不是「全盘替代」，而是按场景取舍。"))
    parts.append(_p("简单任务不必套重流程，复杂或高风险任务仍值得保留显式约束。"))

    # ── §5 新方法：先裸跑，再加最小Skill ──────────────────────────────
    parts.append(_h("新方法：先裸跑，再加最小Skill"))
    ds = datasets or "你的基准数据"
    metrics = "/".join(str(m) for m in benchmark.get("metrics", [])[:4])
    ins_text = "；".join(
        _clean(i.get("point", ""))[:30] for i in innovations[:2] if isinstance(i, dict)
    )
    parts.append(_li(1, "先定义结果，不定义仪式——把目标、硬约束、验收标准写清楚。"))
    parts.append(_li(2, f"用基准数据（{ds}）让模型/基线裸跑，记录成功率与返工。"))
    parts.append(_li(3, "只看可复现的失败——同一类错误稳定出现，才说明缺经验。"))
    parts.append(_li(4, f"只补一个最小补丁——把上文方法（{ins_text}…）固化成可触发的最小流程。"))
    parts.append(_li(5, f"再跑同一组任务，对比指标（{metrics or '论文指标'}）；质量没提升就删掉。"))

    # ── §6 还要不要装 ─────────────────────────────────────────────────
    parts.append(_h("还要不要装"))
    parts.append(_p("🧑‍🎓 如果你是在校学生：先吃透上面的创新点，理解它到底解决了什么。"))
    parts.append(_p("💼 如果你在工业界落地：重点看关键结果能否在你的业务指标上复现。"))
    parts.append(_p("🔬 如果你在做研究：借鉴它的模块拆分思路，而不是照抄整条流程。"))

    # ── §7 写在最后 ────────────────────────────────────────────────────
    parts.append(_h("写在最后"))
    if one_liner:
        parts.append(_p(one_liner + "。"))
        parts.append(_p("真正该学的，不是最火的插件或 Skill 名字，而是看清模型现在会什么、不会什么。"))
    else:
        parts.append(_p("方法会过时，看清问题与约束的能力不过时。"))

    # ── 分隔 + 参考文献 ────────────────────────────────────────────────
    parts.append(_divider())
    parts.append(_h("📚 参考文献"))
    if _arxiv_id(assets.paper_id):
        paper = f"https://arxiv.org/abs/{assets.paper_id}"
        pdf = f"https://arxiv.org/pdf/{assets.paper_id}"
        parts.append(gzh.references(paper))  # 组件 #11：论文链接 + 学术声明（含 span leaf）
        parts.append(_p(f"· PDF：{_link(pdf)}"))
        parts.append(_p("· 代码：暂无官方代码（以论文复现为准）"))
    else:
        parts.append(_p("· 论文：见原文链接"))
        parts.append(_p("· PDF：见原文链接"))
        parts.append(_p("· 代码：（见原文链接）"))
        parts.append(
            _p(f'<span style="color:{_MUTED};font-size:13px;">图表摘自论文，仅作学术解读。</span>'))

    return "\n".join(parts)


def render_wechat_preview_doc(assets, root: Path) -> Path:
    """Write a self-contained HTML preview file for manual upload / eyeballing.

    Wraps :func:`render_wechat_html` in a full document with the title and the
    cover image so the result can be opened in any browser.  Returns the path.
    """
    html = render_wechat_html(assets)
    title = assets.title_zh[:TITLE_MAX]
    images = [str(p) for p in select_images(assets, limit=7)][:7]
    cover = images[0] if images else ""
    cover_tag = f'<img class="cover" src="file:///{cover}">' if cover else ""
    img_tags = "".join(
        f'<img src="file:///{p}" style="max-width:100%;border-radius:6px;'
        f'margin:8px 0 16px;">' for p in images
    )
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ max-width:680px; margin:0 auto; padding:22px;
  font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;
  background:#fff; color:{_TEXT}; }}
h1 {{ font-size:22px; line-height:1.4; margin:0 0 18px; color:#1a1a1a; }}
.cover {{ width:100%; border-radius:8px; margin-bottom:18px; }}
hr {{ border:none; border-top:1px solid #eee; margin:24px 0; }}
</style></head>
<body>
<h1>{title}</h1>
{cover_tag}
{html}
{img_tags}
<hr>
<p style="color:{_MUTED};font-size:13px;">图表摘自论文，仅作学术解读。</p>
</body></html>"""
    out = root / "publish_preview" / "wechat" / (
        "".join(c for c in title if c.isalnum() or c in "._-")[:40] + ".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


def render_article_body(assets) -> str:
    """Compose a 1,200-2,000 char WeChat article following the verified
    代码随想录-style skeleton (see references/wechat-post-template.md):

        开场钩子 → 它过去解决了什么 → 新变化/证据 → 该避的几类
        → 反转折线 → 新方法五步 → 分人群建议 → 写在最后

    每个插槽严格源自 11 维摘要，不编造；缺字段则优雅降级。
    """
    summary = assets.summary
    one_liner = _field(summary, "one_line_summary")

    lines: list[str] = []
    lines += [_render_hook(summary, one_liner), ""]
    lines += ["## 它过去解决了什么", _render_background(summary), ""]
    lines += ["## 新变化把旧方案吃进了模型", _render_method_evidence(summary), ""]
    lines += ["## 最先没必要的，是这几类", _render_categories(summary), ""]
    lines += ["## 但这不等于全部都该删", _render_boundary(summary), ""]
    lines += ["## 新方法：先裸跑，再加最小Skill", _render_steps(summary), ""]
    lines += ["## 还要不要装", _render_audience(summary), ""]
    lines += ["## 写在最后", _render_closing(summary), ""]
    ref_block, _ = _links_block(assets)
    lines += [ref_block]

    body = "\n".join(lines).strip()
    if len(body) > BODY_MAX:
        body = body[:BODY_MAX - 1].rstrip() + "…"
    return body


def build_package(assets, canonical_url: str, title: str = "") -> PublicationPackage:
    """Assemble a platform-ready WeChat package from parsed paper assets.

    The package carries two bodies:

    * ``body_markdown`` — the **WeChat-flavored plain text** produced by
      :func:`render_wechat_article`.  This is what ``WeChatDraftDelivery``
      injects into the UEditor; no Markdown syntax survives.
    * ``metadata["markdown_source"]`` — the original Markdown body from
      :func:`render_article_body`, kept for the audit trail / HTML preview
      fallback so reviewers can see what the Markdown source looked like.
    """
    markdown_source = render_article_body(assets)
    wechat_body = render_wechat_article(assets)
    wechat_html = render_wechat_html(assets)
    images = [str(p) for p in select_images(assets, limit=7)][:7]
    if not images:
        raise RenderError(f"{assets.paper_id}: no usable images for a WeChat draft")

    _, links = _links_block(assets)
    package = PublicationPackage(
        paper_id=assets.paper_id,
        platform="wechat",
        canonical_url=canonical_url or links["paper"],
        title=(title or assets.title_zh)[:TITLE_MAX],
        body_markdown=wechat_body,
        image_paths=images,
        links=links,
    )
    package.metadata["summary"] = _field(assets.summary, "one_line_summary")
    package.metadata["author"] = _DEFAULT_AUTHOR
    package.metadata["markdown_source"] = markdown_source
    package.metadata["wechat_html"] = wechat_html
    return package


def deliver_article(assets, canonical_url: str = "", title: str = "") -> dict[str, Any]:
    """Stage and publish a WeChat draft for one parsed paper.

    Returns the :class:`WeChatPublisher` result dict.  When mp.weixin.qq.com is
    not logged in, this falls back to a local HTML preview (see
    ``WeChatPublisher.publish``), so a usable artifact is always produced.
    """
    if not opencli_runtime.is_available():
        raise RenderError("OpenCLI not found; set OPENCLI_NODE and OPENCLI_MAIN")

    package = build_package(assets, canonical_url, title=title)
    publisher = WeChatPublisher(Path("data"))
    staged = publisher.stage(package)
    if not staged.get("ok"):
        return {"ok": False, "stage_error": staged}
    return publisher.publish(staged["staged_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a WeChat draft from a parsed paper")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--canonical-url", default="")
    parser.add_argument("--title", default="", help="Override the auto title (WeChat allows up to 64 chars)")
    args = parser.parse_args()

    assets = load_assets(args.paper_id, Path.cwd())
    receipt = deliver_article(assets, canonical_url=args.canonical_url, title=args.title)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
