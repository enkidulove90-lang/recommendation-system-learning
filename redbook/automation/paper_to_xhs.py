"""Turn a parsed paper into a Xiaohongshu draft: topics -> PDF -> draft.

Pipeline
--------
1. Load the 11-dimension summary JSON produced by ``skills/deepseek_summarizer.py``.
2. Pick cover + body figures using the vision descriptions in ``*_figures.json``.
3. Render a 300-1000 character note that reads like a person, not a changelog.
4. Deliver through OpenCLI in the order the platform enforces:
   bind real topic entities, attach the paper PDF, then save as a draft.

The delivery order is not cosmetic.  Topics must be selected from the composer's
picker to become real, clickable entities -- writing ``#foo`` into the body only
produces inert text.  The PDF can only be attached once a note entity exists.
Saving the draft last is what makes both survive.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any

from ..infrastructure import opencli_runtime
from ..infrastructure.xiaohongshu_delivery import (
    DeliveryError,
    DeliveryReceipt,
    DraftPayload,
    OpenCliXiaohongshuDelivery,
)

#: Platform hard limits, verified against `opencli xiaohongshu publish --help`.
#: The body budget is relaxed to 1000 chars so single-paper deep reads can use
#: the structured template (🧠/✨/🔧/🧪/⚙️/📊) without being truncated.
TITLE_MAX = 20
IMAGES_MAX = 9
BODY_MIN, BODY_MAX = 300, 1000

#: Figure types worth showing, in descending order of reader value.
_FIGURE_PRIORITY = ("architecture", "framework", "model", "result", "table", "chart", "other")

#: Always-on topics for this account's paper-sharing niche.
#: Domain-specific tags are derived per paper below — we no longer force
#: "推荐系统" on every note, since the account also covers coding-agent /
#: LLM-system papers that would otherwise be mislabeled.
_BASE_TOPICS = ("论文分享", "人工智能")

_TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "推荐系统": ("推荐", "协同过滤", "召回", "排序", "点击率", "ctr", "ranking",
                "recommend", "recsys", "推荐系统", "协同"),
    "图神经网络": ("graph", "gnn", "图神经", "图卷积", "gcn"),
    "对比学习": ("contrastive", "对比学习"),
    "大模型": ("llm", "large language", "大模型", "语言模型", "gpt", "opus",
               "claude", "codex", "deepseek", "qwen"),
    "智能体": ("agent", "智能体", "多智能体", "coding agent", "autonomous"),
    "AI编程": ("coding", "代码", "编程", "code", "software engineering",
               "软件工程", "程序员", "repository"),
    "多模态": ("multimodal", "多模态", "modality"),
    "强化学习": ("reinforcement", "强化学习", "policy"),
    "序列推荐": ("sequential", "序列推荐", "session"),
    "机器学习": (),  # generic fallback
}


class RenderError(RuntimeError):
    """The paper does not carry enough material to build a publishable note."""


@dataclass
class PaperAssets:
    """Everything on disk that a note needs, resolved and validated."""

    paper_id: str
    summary: dict[str, Any]
    parsed_dir: Path
    pdf_path: Path
    figures: list[dict[str, Any]] = field(default_factory=list)

    @property
    def title_zh(self) -> str:
        return str(self.summary.get("title_zh") or self.summary.get("title") or self.paper_id)


@dataclass
class XhsNote:
    """A rendered, platform-ready note."""

    paper_id: str
    title: str
    body: str
    image_paths: list[Path]
    topics: list[str]
    pdf_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "body": self.body,
            "body_length": len(self.body),
            "image_paths": [str(p) for p in self.image_paths],
            "topics": self.topics,
            "pdf_path": str(self.pdf_path),
        }


# --------------------------------------------------------------------------- #
# Asset loading
# --------------------------------------------------------------------------- #

def load_assets(paper_id: str, project_root: Path) -> PaperAssets:
    """Collect the summary, parsed directory, figures and PDF for one paper."""
    summary_path = project_root / "data" / "summaries" / f"{paper_id}_summary.json"
    if not summary_path.is_file():
        raise RenderError(f"missing 11-dimension summary: {summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    parsed_dir = _find_parsed_dir(paper_id, project_root)
    if parsed_dir is None:
        raise RenderError(f"no parsed directory found for {paper_id}")

    figures: list[dict[str, Any]] = []
    figures_path = parsed_dir / f"{paper_id}_figures.json"
    if figures_path.is_file():
        payload = json.loads(figures_path.read_text(encoding="utf-8"))
        figures = list(payload.get("figures", []) if isinstance(payload, dict) else payload)

    pdf_path = _find_pdf(paper_id, parsed_dir, project_root)
    if pdf_path is None:
        raise RenderError(f"no PDF found for {paper_id}")

    return PaperAssets(
        paper_id=paper_id, summary=summary, parsed_dir=parsed_dir,
        pdf_path=pdf_path, figures=figures,
    )


def _find_parsed_dir(paper_id: str, project_root: Path) -> Path | None:
    """Prefer the标准化 (renamed) directory, which carries the richest figures."""
    base = project_root / "data" / "parsed"
    if not base.is_dir():
        return None
    candidates = [d for d in base.iterdir() if d.is_dir() and d.name.startswith(paper_id)]
    if not candidates:
        return None
    # A descriptive suffix means the folder went through folder_standardizer.
    candidates.sort(key=lambda d: (len(d.name) == len(paper_id), -len(d.name)))
    return candidates[0]


def _find_pdf(paper_id: str, parsed_dir: Path, project_root: Path) -> Path | None:
    for candidate in (
        parsed_dir / f"{paper_id}_origin.pdf",
        project_root / "data" / "papers" / f"{paper_id}.pdf",
    ):
        if candidate.is_file():
            return candidate
    return None


# --------------------------------------------------------------------------- #
# Figure selection
# --------------------------------------------------------------------------- #

def select_images(assets: PaperAssets, limit: int = 5) -> list[Path]:
    """Pick the most explanatory figures, falling back to raw page images.

    Figures carrying a vision-model description are ranked by ``figure_type``;
    ties are broken by description length, which correlates with how much the
    model actually found to say about the panel.
    """
    ranked: list[tuple[int, int, Path]] = []
    for figure in assets.figures:
        rel = str(figure.get("image_file", "")).strip()
        if not rel:
            continue
        path = (assets.parsed_dir / rel).resolve()
        if not path.is_file():
            continue
        ftype = str(figure.get("figure_type", "other")).lower()
        rank = _FIGURE_PRIORITY.index(ftype) if ftype in _FIGURE_PRIORITY else len(_FIGURE_PRIORITY)
        ranked.append((rank, -len(str(figure.get("description", ""))), path))

    ranked.sort()
    chosen = [path for _, _, path in ranked][:limit]

    if len(chosen) < limit:
        images_dir = assets.parsed_dir / "images"
        if images_dir.is_dir():
            seen = {p.name for p in chosen}
            extras = sorted(
                (p for p in images_dir.iterdir()
                 if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and p.name not in seen),
                key=lambda p: p.stat().st_size, reverse=True,
            )
            chosen.extend(extras[: limit - len(chosen)])

    if not chosen:
        raise RenderError(f"{assets.paper_id}: no usable images for a Xiaohongshu note")
    return chosen[:IMAGES_MAX]


# --------------------------------------------------------------------------- #
# Topic derivation
# --------------------------------------------------------------------------- #

def derive_topics(assets: PaperAssets, limit: int = 5) -> list[str]:
    """Map paper content onto topic entities that actually exist on the platform.

    Only well-populated, human-used tags are emitted.  Inventing a niche tag
    ("#SVD增强图对比") produces a picker miss, which the delivery adapter treats
    as a hard failure rather than silently degrading to plain text.
    """
    summary = assets.summary
    benchmark = summary.get("benchmark", {}) or {}
    one_liner = str(summary.get("one_liner") or summary.get("one_line_summary", ""))
    haystack = " ".join(
        str(part).lower() for part in (
            summary.get("title_zh", ""),
            summary.get("title_en", ""),
            one_liner,
            json.dumps(summary.get("innovations", []), ensure_ascii=False),
            json.dumps(summary.get("main_contributions", []), ensure_ascii=False),
            json.dumps(summary.get("problem_definition", {}), ensure_ascii=False),
            str(benchmark.get("main_results", "")),
            str(benchmark.get("significance", "")),
            str(summary.get("limitations", "")),
            str(summary.get("limitations_reader_judged", "")),
        )
    )
    topics = list(_BASE_TOPICS)
    for topic, keywords in _TOPIC_KEYWORDS.items():
        if len(topics) >= limit:
            break
        if topic in topics:
            continue
        if any(keyword in haystack for keyword in keywords):
            topics.append(topic)
    return topics[:limit]


# --------------------------------------------------------------------------- #
# Body rendering
# --------------------------------------------------------------------------- #

def _clean(text: str) -> str:
    """Strip citation scaffolding that reads as noise outside a paper."""
    text = re.sub(r"\[[^\]]*(?:阅读者判断|来源)[^\]]*\]", "", str(text))
    text = re.sub(r"[（(]\s*第[^）)]*节\s*[）)]", "", text)
    text = re.sub(r"\s+", " ", text)
    # Removing an inline marker can strand its punctuation ("。：" / "，、").
    text = re.sub(r"([。；;])\s*[：:、，,]+", r"\1", text)
    text = re.sub(r"[：:]\s*(?=[。；;]|$)", "", text)
    return text.strip(" ，。;；:：、")


def _title(assets: PaperAssets) -> str:
    """Fill the 20-character budget: short name plus as much hook as fits."""
    raw = assets.title_zh.split("：")[0].split(":")[0].strip()
    if len(raw) > TITLE_MAX:
        return raw[: TITLE_MAX - 1] + "…"

    one_liner = _clean(assets.summary.get("one_liner") or assets.summary.get("one_line_summary", ""))
    if not one_liner:
        return raw

    budget = TITLE_MAX - len(raw) - 1  # one char for the separator
    if budget < 4:
        return raw
    hook = one_liner if len(one_liner) <= budget else one_liner[: budget - 1] + "…"
    return f"{raw}｜{hook}"


_CN_TERMS: tuple[tuple[str, str], ...] = (
    ("Multi-view Semantic Pattern Encoder", "多视图语义模式编码器"),
    ("Semantic Contrastive Alignment", "语义对比对齐"),
    ("Multi-view Adaptive Fusion (MAF)", "多视图自适应融合(MAF)"),
    ("Multi-view Adaptive Fusion", "多视图自适应融合"),
    ("User-Item Collaborative View", "用户-物品协同视图"),
    ("Item-Item Structural View", "物品-物品结构视图"),
    ("Item-Item Intra-Modal View", "物品-物品模态内视图"),
    ("Collaborative View", "协同视图"),
    ("Structural View", "结构视图"),
    ("Intra-Modal View", "模态内视图"),
    ("layer-0 excluded from aggregation", "不含layer-0"),
    ("visual, textual", "视/文"),
    ("user-item interaction graph", "用户-物品交互图"),
    ("item multimodal features", "item多模态特征"),
    ("all-ranking Top-K list", "全量Top-K排序"),
    ("augmented representations offer limited information gain", "模态增强表征增益有限"),
    ("introduce noise", "甚至引入噪声"),
    ("interactive prediction in the collaborative view", "对协同视图的交互预测"),
    ("semantic discrepancy between collaborative view and modality-augmented features", "协同视图与模态增强特征间存在语义鸿沟"),
    ("remains inadequately addressed", "仍未充分解决"),
    ("textual modality consistently more important than visual", "文本模态重要性>视觉"),
    (" (w/o T drop > w/o V drop on all datasets)", "（去文本掉点>去视觉）"),
    ("No Limitations section in the paper", "论文无Limitations章节"),
    ("Eq.12-13 ", "Eq.12-13"),
    ("formulation is mathematically degenerate; the real algorithm is only recoverable from source code", "公式数学退化；真实算法只能从源码还原"),
    ("collaborative-anchored InfoNCE", "协同锚定InfoNCE"),
    ("InfoNCE", "InfoNCE"),
    ("LightGCN", "LightGCN"),
    ("L_BPR", "BPR"),
    ("Top-K ranking", "Top-K 排序"),
    ("multimodal collaborative filtering", "多模态协同过滤"),
    ("co-occurrence graph", "共现图"),
    ("sparse GCN", "稀疏 GCN"),
    ("kNN graph", "kNN 图"),
    ("ID-gated modal projection", "ID 门控模态投影"),
    # Full-sentence polish for common challenge phrasing so the 🧠 section reads
    # like a person rather than a translated abstract.
    (
        "augmented representations offer limited information gain (or introduce noise) for interactive prediction in the collaborative view；semantic discrepancy between collaborative view and modality-augmented features remains inadequately addressed",
        "把视觉/文本特征加进协同过滤，增益常常有限，甚至还引入噪声；协同视图和模态增强特征之间始终有条语义鸿沟没填平",
    ),
    # Method module function one-liners: keep methodology bullets in Chinese.
    (
        "L-layer symmetric-normalized propagation + layer average (Eq.1-3), intentionally excluding layer 0",
        "L层对称归一化传播 + 层平均聚合（不含layer-0）",
    ),
    (
        "co-occurrence graph (count > 1, top-k=10, self-loop, binary) + 1-layer sparse GCN, then back-project to users via normalized R (Eq.4-6)",
        "共现图（共现次数>1, top-k=10）+ 1层稀疏GCN，再回投影到用户",
    ),
    (
        "cosine kNN graph per modality + ID-gated modal projection (Eq.9, MGCN-style gate) + 1-layer sparse GCN + back-project to users (Eq.7-11)",
        "每个模态建cos kNN图 + ID门控投影 + 1层稀疏GCN回投影",
    ),
    (
        "shared attention g(x) scores each view; redundant part E_r subtracted from view sum (Eq.12-14). NOTE: Eq.12-13 mathematically degenerate; code uses cross-view softmax over concatenated (N,3) scores",
        "共享注意力给三视图打分，减去冗余表征后再融合",
    ),
    (
        "E* = E_bar + alpha * E_hat, inner product (Eq.17)",
        "E* = 协同表征 + α·去冗余增强表征，内积预测",
    ),
)


def _cn(text: str) -> str:
    """Translate known English RecSys vocabulary to concise Chinese.

    Longest phrases are replaced first so full-sentence polish entries win over
    shorter sub-term entries that would otherwise fragment the translation.
    """
    t = str(text)
    for en, zh in sorted(_CN_TERMS, key=lambda pair: len(pair[0]), reverse=True):
        if en in t:
            t = t.replace(en, zh)
    return t


def _section_problem(summary: dict[str, Any]) -> list[str]:
    """🧠 解决什么问题 — colloquial conflict + concrete pain point."""
    problem = summary.get("problem_definition", {}) or {}
    if not isinstance(problem, dict):
        return []

    task = _cn(_clean(problem.get("task_type", "")))
    challenges = problem.get("challenges") or []
    if isinstance(challenges, list) and challenges:
        chal_text = _cn("；".join(str(c) for c in challenges))
        chal_text = re.sub(r"\(or[^)]*\)", "", chal_text)
        chal_text = re.sub(r"\s+for\s+", "", chal_text)
        chal_text = re.sub(r"\s+", " ", chal_text).strip()
        chal_text = chal_text.replace("；", "，")
    else:
        chal_text = ""

    if not task and not chal_text:
        return []

    is_mm = "多模态" in task or "multimodal" in str(problem.get("task_type", "")).lower()
    opener = "多模态推荐有个经典尴尬：" if is_mm else "这个方向有个真实痛点："
    if task and chal_text:
        line = f"{opener}{chal_text}。"
    elif chal_text:
        line = f"{opener}{chal_text}。"
    elif task:
        line = f"{task}场景下，怎么把模态信息真正用好，而不是加了反而掉点？" if is_mm else f"{task}场景下，现有方法还缺一把火候。"
    else:
        return []
    return ["🧠 解决什么问题", line, ""]


def _section_contributions(summary: dict[str, Any]) -> list[str]:
    """✨ 主要贡献 / 创新点 — numbered, punchy."""
    contribs = summary.get("main_contributions") or summary.get("innovations") or []
    if not isinstance(contribs, list) or not contribs:
        return []

    items: list[str] = []
    for c in contribs[:3]:
        raw = c.get("point") if isinstance(c, dict) else c
        text = _cn(_clean(raw))
        text = re.sub(r",\s*reader-highlighted", "", text)
        # Keep only the lead clause so bullets stay short; preserve parenthetical acronyms.
        lead = re.split(r"[:;；,，]", text)[0].strip()
        if lead:
            items.append(lead)
    if not items:
        return []

    lines = ["✨ 主要贡献 / 创新点"]
    for i, item in enumerate(items, start=1):
        lines.append(f"{i}. {item}")
    return lines + [""]


def _section_method(summary: dict[str, Any]) -> list[str]:
    """🔧 方法论 — bulletized pipeline."""
    arch = summary.get("architecture", {}) or {}
    if not isinstance(arch, dict):
        return []
    modules = arch.get("modules", [])
    if not isinstance(modules, list) or not modules:
        return []

    bullets: list[str] = []
    for m in modules[:5]:
        if not isinstance(m, dict):
            continue
        name = _cn(_clean(m.get("name", "")))
        func = _cn(_clean(m.get("function", "")))
        # Compress function to one clause.
        func_lead = re.split(r"[;；]", func)[0].strip() if func else ""
        if name and func_lead:
            snippet = func_lead[:68]
            if len(func_lead) > 68:
                snippet = snippet.rstrip() + "…"
            bullets.append(f"• {name}：{snippet}")
        elif name:
            bullets.append(f"• {name}")
    if not bullets:
        return []
    return ["🔧 方法论"] + bullets[:4] + [""]


def _section_benchmark(summary: dict[str, Any]) -> list[str]:
    """🧪 Benchmark 与数据集 — task / data / baselines / metrics."""
    problem = summary.get("problem_definition", {}) or {}
    task = _cn(_clean(problem.get("task_type", ""))) if isinstance(problem, dict) else ""
    datasets = summary.get("datasets", []) or []
    ds_names = [str(d.get("name", "")).replace("Amazon ", "") for d in datasets if isinstance(d, dict) and d.get("name")]
    baselines = summary.get("baselines", {}) or {}
    n_bases = sum(len(v) for v in baselines.values() if isinstance(v, list)) if isinstance(baselines, dict) else 0
    metrics = summary.get("metrics", []) or []

    lines = ["🧪 Benchmark 与数据集"]
    if task:
        lines.append(f"• 任务：{task}")
    if ds_names:
        lines.append(f"• 数据集：{'、'.join(ds_names)}")
    if n_bases:
        lines.append(f"• 对比方法：{n_bases} 个基线")
    if metrics:
        lines.append(f"• 指标：{'、'.join(str(m) for m in metrics)}")
    return lines + [""] if len(lines) > 1 else []


def _section_conditions(summary: dict[str, Any]) -> list[str]:
    """⚙️ 实验条件 — implementation & key settings."""
    tr = summary.get("training", {}) or {}
    if not isinstance(tr, dict):
        return []

    bits: list[str] = []
    env = summary.get("reproducibility", {}).get("env", "")
    if not env and tr.get("hardware"):
        env = str(tr.get("hardware"))
    if env:
        bits.append(f"环境：{env}")
    if tr.get("optimizer"):
        opt = str(tr["optimizer"]).split("(")[0].strip()
        bits.append(f"优化：{opt} lr={tr.get('lr')}, bs={tr.get('batch_size')}")
    if tr.get("epochs"):
        bits.append(f"训练：{tr.get('epochs')} epoch, early stop patience={tr.get('early_stop_patience', '?')}")
    if tr.get("valid_metric"):
        bits.append(f"选优指标：{tr.get('valid_metric')}")

    if not bits:
        return []
    return ["⚙️ 实验条件"] + [f"• {b}" for b in bits] + [""]


def _section_results(summary: dict[str, Any]) -> list[str]:
    """📊 实验效果 — only the brightest numbers + one ablation insight."""
    main = summary.get("main_results", {}) or {}
    imp = summary.get("improvement_over_best_baseline", {}) or {}
    if not isinstance(main, dict):
        return []

    bits: list[str] = []
    for ds_name, vals in main.items():
        if not isinstance(vals, dict) or "MSCA" not in vals:
            continue
        r20 = vals["MSCA"].get("R@20")
        if r20 is None:
            continue
        up = (imp.get(ds_name, {}) or {}).get("R@20") if isinstance(imp, dict) else None
        short = str(ds_name).replace("Amazon ", "").split()[0]
        bits.append(f"{short} R@20={r20:.4f}" + (f"(+{up})" if up else ""))

    if not bits:
        return []

    # Add one ablation takeaway if available.
    ab = summary.get("ablation", {}) or {}
    ab_note = ""
    if isinstance(ab, dict) and isinstance(ab.get("conclusions"), list) and ab["conclusions"]:
        ab_note = "。" + _cn(_clean(ab["conclusions"][0]))

    return ["📊 实验效果", "；".join(bits) + ab_note, ""]


def render_body(assets: PaperAssets) -> str:
    """Compose a structured deep-read note in the account's established voice.

    The format follows the single-paper XHS template:
    🧠 problem -> ✨ contributions -> 🔧 method -> 🧪 benchmark -> ⚙️ conditions
    -> 📊 results, then the follow line.  Links are appended by ``build_package``.
    """
    summary = assets.summary
    sections: list[list[str]] = [
        _section_problem(summary),
        _section_contributions(summary),
        _section_method(summary),
        _section_benchmark(summary),
        _section_conditions(summary),
        _section_results(summary),
    ]

    lines: list[str] = []
    for sec in sections:
        lines.extend(sec)
    lines.append("关注我，持续拆解推荐系统与多模态方向的新论文 📚")

    body = "\n".join(lines).strip()
    if len(body) > BODY_MAX:
        body = body[: BODY_MAX - 1].rstrip() + "…"
    if len(body) < BODY_MIN:
        # Fallback: if a sparse paper cannot fill the template, surface the
        # one-liner and a generic closing so the note is still publishable.
        one_liner = _clean(summary.get("one_liner") or summary.get("one_line_summary", ""))
        body = f"🎓 一句话精读\n{one_liner}\n\n{body}"
    return body


# --------------------------------------------------------------------------- #
# Note assembly & validation
# --------------------------------------------------------------------------- #

def render_note(assets: PaperAssets, image_limit: int = 5) -> XhsNote:
    """Build a complete, validated note from parsed paper assets."""
    note = XhsNote(
        paper_id=assets.paper_id,
        title=_title(assets),
        body=render_body(assets),
        image_paths=select_images(assets, limit=image_limit),
        topics=derive_topics(assets),
        pdf_path=assets.pdf_path,
    )
    problems = validate_note(note)
    if problems:
        raise RenderError("; ".join(problems))
    return note


def validate_note(note: XhsNote) -> list[str]:
    """Check a note against platform limits before touching the browser."""
    problems: list[str] = []
    if not note.title or len(note.title) > TITLE_MAX:
        problems.append(f"title must be 1-{TITLE_MAX} chars, got {len(note.title)}")
    if not note.body.strip():
        problems.append("body is empty")
    if len(note.body) > BODY_MAX:
        problems.append(f"body exceeds {BODY_MAX} chars: {len(note.body)}")
    if len(note.body) < BODY_MIN:
        problems.append(f"body below {BODY_MIN} chars: {len(note.body)}")
    if not note.image_paths:
        problems.append("at least one image is required")
    if len(note.image_paths) > IMAGES_MAX:
        problems.append(f"at most {IMAGES_MAX} images, got {len(note.image_paths)}")
    if not note.topics:
        problems.append("at least one topic is required")
    if not note.pdf_path.is_file():
        problems.append(f"PDF not found: {note.pdf_path}")
    return problems


# --------------------------------------------------------------------------- #
# Delivery
# --------------------------------------------------------------------------- #

def deliver_note(note: XhsNote, *, attach_pdf: bool = True) -> DeliveryReceipt:
    """Send the note to Xiaohongshu as a draft: topics -> PDF -> draft.

    Raises :class:`DeliveryError` rather than degrading: a draft without real
    topic entities or without the PDF is worse than no draft, because it looks
    finished and would be published by hand.
    """
    if not opencli_runtime.is_available():
        raise DeliveryError("OpenCLI not found; set OPENCLI_NODE and OPENCLI_MAIN")

    login = opencli_runtime.probe_login("xiaohongshu", timeout=240)
    if not login.get("logged_in"):
        raise DeliveryError(
            f"xiaohongshu session is not authenticated: {login.get('error', login)}"
        )

    payload = DraftPayload(
        title=note.title,
        body=note.body,
        image_paths=tuple(note.image_paths),
        topics=tuple(note.topics),
        pdf_path=note.pdf_path,
    )
    delivery = OpenCliXiaohongshuDelivery()
    if attach_pdf:
        return delivery.deliver(payload)

    draft = delivery.save_image_draft(payload)
    return DeliveryReceipt(
        draft_id=str(draft.get("id", "")), title=note.title,
        image_count=len(note.image_paths), topics=tuple(note.topics),
        pdf_name="(skipped)",
    )
