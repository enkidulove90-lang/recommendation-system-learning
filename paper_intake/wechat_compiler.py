"""Compile a WeChat draft package from fact-pack/v2 ``wechat_draft``.

The WeChat template differs substantially from Xiaohongshu: long-form article
(200-2000 chars), emoji section markers (🔹/🔸/💡/📚), plain text only (UEditor
does not render Markdown), no PDF attachment, one cover image.  See
``.agents/skills/multi-platform-publishing/references/wechat-body-template.md``.

Pure backend: no agent, no vision model.  Figures come from the same paper-order
selection as the XHS compiler.
"""
from __future__ import annotations

import argparse
import html
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.note_compiler import _relative_to, build_body, load_fact_pack, select_figures

QUEUE_DIR = ROOT / "publish_queue"
DEFAULT_AUTHOR = "推荐系统研读"


def _plain(text: str) -> str:
    """WeChat-safe plain text: no Markdown markers."""
    cleaned = str(text).replace("**", "").replace("__", "").replace("`", "")
    cleaned = cleaned.replace("~~", "")
    cleaned = cleaned.replace("##", "").replace("![", "")
    return cleaned.strip()


def build_wechat_body(wechat_draft: dict[str, Any], facts: dict[str, Any],
                      *, paper_id: str, paper_url: str, code_url: str) -> str:
    """Render the WeChat-flavored long-form body from the model's draft.

    Uses the verified skeleton: 🔸 hook -> 🔹 background -> 🔹 method+evidence
    -> 💡 key result -> 🔸 limitations -> 🔹 takeaway -> 📚 links.
    """
    lead = _plain(wechat_draft.get("lead") or "")
    body = _plain(wechat_draft.get("body") or "")
    problem = _plain(facts.get("problem") or "")
    method = _plain(facts.get("method") or "")
    novelty = _plain(facts.get("novelty") or "")
    limitations = _plain(facts.get("limitations") or "")
    takeaway = _plain(facts.get("takeaway") or "")

    blocks: list[str] = []
    if lead:
        blocks.append("🔸 " + lead)
    if problem:
        blocks.append("但在此之前，" + problem + "长期是绕不开的痛点。")
    if novelty:
        blocks.append("🔹 新变化把旧方案吃进了模型\n\n" + novelty)
    if method:
        blocks.append("🔹 核心方法\n\n" + method)
    if body:
        # The model's full article is the substance; keep it intact.
        blocks.append(body)
    experiments = facts.get("experiments") or []
    if experiments:
        highlights = "\n".join(f"· {_plain(item)}" for item in experiments[:4])
        blocks.append("💡 关键结果\n\n" + highlights)
    if limitations:
        blocks.append("🔸 最先没必要的，是这几类\n\n· " + limitations)
    if takeaway:
        blocks.append("🔹 写在最后\n\n" + takeaway)
    links = f"📚 论文：{paper_url}"
    if code_url:
        links += f"\n代码：{code_url}"
    blocks.append(links)

    result = "\n\n".join(blocks)
    # WeChat editor is happiest with 200-2000 chars; truncate at a block boundary.
    if len(result) > 1950:
        result = result[:1950].rstrip() + "…"
    return result


def build_wechat_html(facts: dict[str, Any], figure_paths: list[str],
                      *, paper_url: str, code_url: str, title: str) -> str:
    """Render WeChat-safe inline-styled HTML with figures inserted in paper order.

    Follows the verified 代码随想录 skeleton (H2/H3 ladder, bold punchlines,
    data callout, category table, per-audience advice) rather than emoji
    markers.  ``<img src>`` uses LOCAL paths: WeChatDraftDelivery uploads each
    one and rewrites src to a mmbiz.qpic.cn CDN url before saving.
    """
    def esc(value: str) -> str:
        return (str(value).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))

    def p(text: str, *, style: str = "") -> str:
        attr = f' style="{style}"' if style else ""
        return f"<p{attr}>{esc(text)}</p>"

    def h2(text: str) -> str:
        return (f'<p style="font-size:18px;font-weight:bold;color:#1a1a1a;'
                f'margin:28px 0 12px 0;border-left:4px solid #576b95;'
                f'padding-left:10px;">{esc(text)}</p>')

    def callout(text: str) -> str:
        return (f'<p style="background:#f7f7f9;padding:12px 14px;margin:14px 0;'
                f'border-radius:6px;font-weight:bold;color:#576b95;">{esc(text)}</p>')

    def img(path: str, caption: str = "") -> str:
        parts = [f'<p style="margin:16px 0;text-align:center;">'
                 f'<img src="{esc(path)}" style="max-width:100%;height:auto;"/></p>']
        if caption:
            parts.append(p(caption, style="font-size:12px;color:#888;text-align:center;"))
        return "".join(parts)

    one_line = _plain(facts.get("one_line") or "")
    problem = _plain(facts.get("problem") or "")
    method = _plain(facts.get("method") or "")
    novelty = _plain(facts.get("novelty") or "")
    limitations = _plain(facts.get("limitations") or "")
    takeaway = _plain(facts.get("takeaway") or "")
    experiments = [_plain(str(x)) for x in (facts.get("experiments") or [])]

    parts: list[str] = []
    # Opening hook: reverse-conclusion first, bold punchline.
    if one_line:
        parts.append(callout(one_line))
    if problem:
        parts.append(p(f"但在此之前，{problem}长期是绕不开的痛点。"))
    # §1 background (figure 1 = overview)
    parts.append(h2("1. 它过去解决了什么"))
    if problem:
        parts.append(p(problem))
    if figure_paths:
        parts.append(img(figure_paths[0], "图1：论文概览与问题背景"))
    # §2 new change + evidence (figure 2 = architecture)
    parts.append(h2("2. 新变化把旧方案吃进了模型"))
    if novelty:
        parts.append(callout(novelty))
    if method:
        parts.append(p(method))
    if len(figure_paths) > 1:
        parts.append(img(figure_paths[1], "图2：方法整体架构"))
    # §3 key results + data callout (figure 3 = result)
    parts.append(h2("3. 关键结果"))
    if experiments:
        parts.append(callout(" · ".join(experiments[:3])))
    if len(figure_paths) > 2:
        parts.append(img(figure_paths[2], "图3：核心实验结果"))
    # §4 not a full replacement (figure 4 if present)
    parts.append(h2("4. 但这不等于全部都该换"))
    if limitations:
        parts.append(p(limitations))
    if len(figure_paths) > 3:
        parts.append(img(figure_paths[3], "图4：补充实验与对比"))
    # §5 takeaway + per-audience advice
    parts.append(h2("5. 写在最后"))
    if takeaway:
        parts.append(callout(takeaway))
    parts.append(p("对学生：先理解问题设定，再判断方法是否可迁移。"
                   "对工业界：核对数据切分与线上成本，再决定是否落地。"))
    links = f"论文：{paper_url}"
    if code_url:
        links += f"　代码：{code_url}"
    parts.append(p(links, style="font-size:12px;color:#888;margin-top:24px;"))
    return "".join(parts)


def build_wechat_html_with_captions(
    facts: dict[str, Any],
    figures: list[dict],  # [{file, figure_id, caption, type}]
    *,
    paper_url: str,
    code_url: str,
    title: str
) -> str:
    """Render WeChat HTML using figure intents from fact_pack and real captions.

    Each figure's caption must come from its table caption, not hard-coded.
    """
    def esc(value: str) -> str:
        return (str(value).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))

    def p(text: str, *, style: str = "") -> str:
        attr = f' style="{style}"' if style else ""
        return f"<p{attr}>{esc(text)}</p>"

    def h2(text: str) -> str:
        return (f'<p style="font-size:18px;font-weight:bold;color:#1a1a1a;'
                f'margin:28px 0 12px 0;border-left:4px solid #576b95;'
                f'padding-left:10px;">{esc(text)}</p>')

    def callout(text: str) -> str:
        return (f'<p style="background:#f7f7f9;padding:12px 14px;margin:14px 0;'
                f'border-radius:6px;font-weight:bold;color:#576b95;">{esc(text)}</p>')

    def img(path: str, caption: str = "") -> str:
        parts = [f'<p style="margin:16px 0;text-align:center;">'
                 f'<img src="{esc(path)}" style="max-width:100%;height:auto;"/></p>']
        if caption:
            parts.append(p(caption, style="font-size:12px;color:#888;text-align:center;"))
        return "".join(parts)

    one_line = _plain(facts.get("one_line") or "")
    problem = _plain(facts.get("problem") or "")
    method = _plain(facts.get("method") or "")
    novelty = _plain(facts.get("novelty") or "")
    limitations = _plain(facts.get("limitations") or "")
    takeaway = _plain(facts.get("takeaway") or "")
    experiments = [_plain(str(x)) for x in (facts.get("experiments") or [])]

    parts: list[str] = []
    # Opening hook: reverse-conclusion first, bold punchline.
    if one_line:
        parts.append(callout(one_line))
    if problem:
        parts.append(p(f"但在此之前，{problem}长期是绕不开的痛点。"))
    # §1 background (figure 1 = overview)
    parts.append(h2("1. 它过去解决了什么"))
    if problem:
        parts.append(p(problem))
    if figures:
        fig = figures[0]
        caption = fig.get("caption") or fig.get("description") or ""
        parts.append(img(str(fig["file"]), caption))
    # §2 new change + evidence (figure 2 = architecture)
    parts.append(h2("2. 新变化把旧方案吃进了模型"))
    if novelty:
        parts.append(callout(novelty))
    if method:
        parts.append(p(method))
    if len(figures) > 1:
        fig = figures[1]
        caption = fig.get("caption") or fig.get("description") or ""
        parts.append(img(str(fig["file"]), caption))
    # §3 key results + data callout (figure 3 = result)
    parts.append(h2("3. 关键结果"))
    if experiments:
        parts.append(callout(" · ".join(experiments[:3])))
    if len(figures) > 2:
        fig = figures[2]
        caption = fig.get("caption") or fig.get("description") or ""
        parts.append(img(str(fig["file"]), caption))
    # §4 not a full replacement (figure 4 if present)
    parts.append(h2("4. 但这不等于全部都该换"))
    if limitations:
        parts.append(p(limitations))
    if len(figures) > 3:
        fig = figures[3]
        caption = fig.get("caption") or fig.get("description") or ""
        parts.append(img(str(fig["file"]), caption))
    for fig in figures[4:]:
        caption = fig.get("caption") or fig.get("description") or ""
        parts.append(img(str(fig["file"]), caption))
    # §5 takeaway + per-audience advice
    parts.append(h2("5. 写在最后"))
    if takeaway:
        parts.append(callout(takeaway))
    parts.append(p("对学生：先理解问题设定，再判断方法是否可迁移。"
                   "对工业界：核对数据切分与线上成本，再决定是否落地。"))
    links = f"论文：{paper_url}"
    if code_url:
        links += f"　代码：{code_url}"
    parts.append(p(links, style="font-size:12px;color:#888;margin-top:24px;"))
    return "".join(parts)


def _shared_body_html(body: str, figures: list[dict]) -> str:
    """Preserve the reviewed XHS text and embed the same selected figures."""
    parts = [f"<p>{html.escape(line)}</p>" for line in body.splitlines() if line.strip()]
    for figure in figures:
        parts.append(f'<p><img src="{html.escape(str(figure["file"]), quote=True)}" '
                     'style="max-width:100%;height:auto;"/></p>')
        caption = str(figure.get("caption") or figure.get("description") or "")
        if caption:
            parts.append(f"<p>{html.escape(caption)}</p>")
    return "".join(parts)


def compile_wechat_package(
    fact_pack_path: Path,
    *,
    canonical_id: str,
    parsed_dir: Path,
    pdf_path: Path | None = None,
    author: str = DEFAULT_AUTHOR,
    figure_manifest_path: Path | None = None,
    paper_url: str | None = None,
    pdf_url: str | None = None,
    code_url: str | None = None,
    queue_dir: Path | None = None,
    html_renderer: Callable[[str, list[dict]], str] | None = None,
) -> tuple[Path, str]:
    """Write a publish_queue wechat.json and return (path, staged_id)."""
    payload = load_fact_pack(fact_pack_path)
    draft = payload.get("wechat_draft") or {}
    if figure_manifest_path is None and (not isinstance(draft, dict) or not draft.get("body")):
        raise ValueError("fact_pack has no wechat_draft.body")
    if not isinstance(draft, dict):
        draft = {}

    paper_id = canonical_id.rsplit(":", 1)[-1]
    facts = payload.get("facts") or {}

    # === 使用与小红书同源的审核图集 ===
    xhs_draft = payload.get("xhs_draft")
    if xhs_draft and isinstance(xhs_draft, dict):
        figure_intents = xhs_draft.get("figure_intents") or []
    else:
        figure_intents = []

    figures = select_figures(parsed_dir, figure_intents=figure_intents,
                             manifest_path=figure_manifest_path, canonical_id=canonical_id)

    # === 使用已审核的图集 ===
    image_paths = [str((ROOT / parsed_dir / fig["file"]).resolve()) for fig in figures[:9]]

    # === 从 FactFacts 中获取已核验的链接 ===
    if paper_url is None:
        paper_url = facts.get("paper_link")
    if not paper_url:
        paper_url = f"https://arxiv.org/abs/{paper_id}" if paper_id.replace(".", "").isdigit() else f"https://doi.org/{paper_id}"
    pdf_link = pdf_url if pdf_url is not None else facts.get("pdf_link")
    code_url = code_url if code_url is not None else str(facts.get("code_url") or "")

    if figure_manifest_path is not None:
        body = build_body(xhs_draft, paper_url=paper_url, code_url=code_url)
    else:
        body = build_wechat_body(
            draft, facts, paper_id=paper_id, paper_url=paper_url, code_url=code_url)
    title = _plain(draft.get("title") or facts.get("one_line") or paper_id)
    if len(title) > 64:
        title = title[:64]

    # === 使用已审核的图集，确保与图注对应 ===
    html_figures = []
    for fig in figures:
        image_path = (parsed_dir / fig["file"]).resolve()
        try:
            image_src = image_path.relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            image_src = image_path.as_posix()
        html_figures.append({**fig, "file": image_src})
    if figure_manifest_path is not None:
        wechat_html = (html_renderer or _shared_body_html)(body, html_figures)
    else:
        wechat_html = build_wechat_html_with_captions(
            facts, html_figures, paper_url=paper_url, code_url=code_url, title=title)

    package = {
        "paper_id": paper_id,
        "platform": "wechat",
        "canonical_url": paper_url,
        "title": title,
        "body_markdown": body,
        "image_paths": image_paths,
        "links": {"paper": paper_url, "pdf": pdf_link or "", "code": code_url},
        "review_status": "pending",  # 初始状态为 pending，需要人工目检后再改为 reviewed
        "source_attribution": "图片按论文图序取自原文解析产物，仅作学术解读。",
        "metadata": {
            "platform": "wechat",
            "status": "draft",
            "author": author,
            "summary": str(draft.get("lead") or "")[:120],
            "cover_image": figures[0]["file"] if figures else "",
            "wechat_html": wechat_html,
            "generated_by": "paper_intake.wechat_compiler",
            "fact_pack_schema": payload.get("schema_version", "fact-pack/v2"),
            "figure_manifest": figures,  # 保存审核图集元数据
        },
    }
    digest = hashlib.sha256(json.dumps(
        {k: v for k, v in package.items() if k not in ("content_hash", "staged_at")},
        ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    package["content_hash"] = digest
    target_dir = (queue_dir or QUEUE_DIR) / digest[:32]
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "wechat.json"
    target.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    return target, digest


def main() -> int:
    parser = argparse.ArgumentParser(description="compile a WeChat package from fact_pack JSON")
    parser.add_argument("--fact-pack", type=Path, required=True)
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--parsed-dir", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--author", default=DEFAULT_AUTHOR)
    args = parser.parse_args()

    path, staged_id = compile_wechat_package(
        args.fact_pack, canonical_id=args.canonical_id, parsed_dir=args.parsed_dir,
        pdf_path=args.pdf, author=args.author)
    result: dict[str, Any] = {
        "ok": True,
        "package": str(path.relative_to(ROOT)),
        "staged_id": staged_id[:32],
    }
    # Publishing is intentionally NOT here: paper_intake must not import
    # redbook (AST guard).  Use scripts/publish_wechat_draft.py --publish.
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
