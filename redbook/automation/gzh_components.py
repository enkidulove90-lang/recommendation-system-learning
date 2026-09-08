"""Reusable recsys-blue component library for the automated WeChat pipeline.

Single source of truth
----------------------
``wechat_design/components/components.md`` — the *exact* component file the
hand-typeset (gzh-design) path uses.  This module loads those ``<section>``
templates and exposes parameterized render functions, so the automated
pipeline (``paper_to_wechat.py``) emits HTML that is visually identical to the
hand-typeset output and already satisfies the ``<span leaf="">`` requirement.

If the markdown file is missing for any reason, a built-in fallback copy of the
same 11 components keeps the pipeline functional (file always wins at runtime).

Why this matters
----------------
Before this module, ``render_wechat_html`` hardcoded inline styles without
``<span leaf>`` wrapping, so pasted drafts lost styling and failed the gzh-design
validation gate.  Reusing the component library closes that gap.
"""
from __future__ import annotations

import html as _html
import re
from pathlib import Path
from typing import Sequence

_COMPONENTS_MD = Path("wechat_design/components/components.md")


def _esc(text: str) -> str:
    """Escape text so it can never break an inline-styled tag."""
    return _html.escape(str(text), quote=False)


# --------------------------------------------------------------------------- #
# Load component templates from components.md (fallback = built-in copy)
# --------------------------------------------------------------------------- #
def _load_raw() -> dict[str, str]:
    """Parse ``wechat_design/components/components.md`` into ``{id: html}``.

    Each component lives under a ``## N. 中文名 component-id`` header and its
    HTML is fenced in a ````` ```html ```` block.  We walk the file line by line
    (robust against en-dash / full-width punctuation in labels) so every one of
    the 11 components is picked up from the file, not the fallback copy.
    """
    raw: dict[str, str] = {}
    if not _COMPONENTS_MD.is_file():
        return raw
    text = _COMPONENTS_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    cur_id: str | None = None
    buf: list[str] = []
    in_fence = False
    fence_buf: list[str] = []
    header_rx = re.compile(
        r"^##\s+\d+\.\s+.*?([a-z][a-z0-9-]+)"
        r"(?:\s*[（(][^）)]*[）)])?\s*$"
    )
    for line in lines:
        hm = header_rx.match(line)
        if hm:
            # flush previous component's fenced block
            if cur_id is not None and fence_buf:
                raw[cur_id] = "\n".join(fence_buf).strip()
            cur_id = hm.group(1)
            buf = []
            fence_buf = []
            in_fence = False
            continue
        if cur_id is not None:
            if line.strip().startswith("```"):
                if not in_fence:
                    in_fence = True
                    # drop the optional language tag (e.g. ```html)
                else:
                    in_fence = False
                    raw[cur_id] = "\n".join(fence_buf).strip()
                    fence_buf = []
                continue
            if in_fence:
                fence_buf.append(line)
    # flush trailing component (file may end without a closing header)
    if cur_id is not None and fence_buf and cur_id not in raw:
        raw[cur_id] = "\n".join(fence_buf).strip()
    return raw


_RAW = _load_raw()

# Built-in fallback (identical to components.md) so import never crashes.
_FALLBACK: dict[str, str] = {
    "hook-title": (
        '<section style="text-align:center;margin:0 0 6px;">\n'
        '  <h1 style="font-size:20px;line-height:1.45;margin:0;color:#1a1a1a;'
        'font-weight:700;"><span leaf="">标题放这里</span></h1>\n'
        '</section>\n'
        '<section style="text-align:center;margin:0 0 18px;">\n'
        '  <p style="font-size:13px;color:#8a94a6;line-height:1.6;margin:0;">'
        '<span leaf="">副标题一句话钩子放这里</span></p>\n'
        '</section>'
    ),
    "cover": (
        '<section style="margin:0 0 18px;">\n'
        '  <img src="图片URL或本地路径" style="width:100%;border-radius:8px;'
        'display:block;">\n'
        '</section>'
    ),
    "one-liner": (
        '<section style="background:#eef3ff;border-left:4px solid #3a5fcd;'
        'padding:12px 16px;border-radius:6px;margin:0 0 16px;">\n'
        '  <p style="margin:0;line-height:1.8;color:#2c3e50;font-size:15px;">'
        '<span leaf="">📌 一句话：</span>'
        '<span leaf="">核心结论放这里，一句话讲清价值。</span></p>\n'
        '</section>'
    ),
    "section-header": (
        '<section style="border-left:4px solid #3a5fcd;padding-left:10px;'
        'margin:24px 0 12px;">\n'
        '  <h2 style="font-size:17px;font-weight:700;color:#1a1a1a;line-height:1.45;'
        'margin:0;"><span leaf="">小标题文字</span></h2>\n'
        '</section>'
    ),
    "body-para": (
        '<section style="margin:0 0 14px;">\n'
        '  <p style="margin:0;line-height:1.8;color:#3f3f3f;font-size:15px;">'
        '<span leaf="">普通叙述句。把</span>'
        '<span leaf="" style="border-bottom:1px solid #3a5fcd;color:#3a5fcd;'
        'font-weight:700;">关键短语</span>'
        '<span leaf="">用主色下划线标记，每段 1–3 处。</span></p>\n'
        '</section>'
    ),
    "rr-table": (
        '<section style="margin:6px 0 16px;">\n'
        '  <table style="width:100%;border-collapse:collapse;font-size:14px;">\n'
        '    <thead><tr style="background:#3a5fcd;color:#ffffff;">\n'
        '      <th style="border:1px solid #e3e8f0;padding:9px 8px;text-align:left;">'
        '<span leaf="">列1</span></th>\n'
        '      <th style="border:1px solid #e3e8f0;padding:9px 8px;">'
        '<span leaf="">列2</span></th>\n'
        '      <th style="border:1px solid #e3e8f0;padding:9px 8px;">'
        '<span leaf="">列3</span></th>\n'
        '    </tr></thead>\n'
        '    <tbody>\n'
        '      <tr><td style="border:1px solid #e3e8f0;padding:9px 8px;">'
        '<span leaf="">单元格</span></td>'
        '<td style="border:1px solid #e3e8f0;padding:9px 8px;text-align:center;">'
        '<span leaf="">12.3%</span></td>'
        '<td style="border:1px solid #e3e8f0;padding:9px 8px;text-align:center;'
        'color:#1a9e57;font-weight:700;"><span leaf="">+1.2</span></td></tr>\n'
        '    </tbody>\n'
        '  </table>\n'
        '</section>'
    ),
    "kpi-cards": (
        '<section style="flex:1;min-width:90px;background:#f5f8ff;'
        'border:1px solid #dce6ff;border-radius:8px;padding:10px 8px;text-align:center;">\n'
        '    <p style="margin:0;font-size:18px;font-weight:700;color:#3a5fcd;'
        'line-height:1.2;"><span leaf="">+8.04</span></p>\n'
        '    <p style="margin:2px 0 0;font-size:12px;color:#6b7280;">'
        '<span leaf="">指标说明</span></p>\n'
        '  </section>'
    ),
    "figure": (
        '<section style="margin:0 0 18px;">\n'
        '  <img src="图片URL" style="width:100%;border-radius:6px;'
        'border:1px solid #f0f0f0;display:block;">\n'
        '  <p style="font-size:13px;color:#999;line-height:1.6;margin:6px 0 0;'
        'text-align:center;"><span leaf="">图 N｜说明文字（只有真有说明才写）</span></p>\n'
        '</section>'
    ),
    "limitation": (
        '<section style="background:#fff7ec;border-left:4px solid #f0a020;'
        'padding:12px 16px;border-radius:6px;margin:0 0 16px;">\n'
        '  <p style="margin:0;line-height:1.8;color:#5a4a2a;font-size:14px;">'
        '<span leaf="">⚠️ 备注：</span>'
        '<span leaf="">局限或需要诚实说明的点放这里。</span></p>\n'
        '</section>'
    ),
    "cta": (
        '<section style="background:#f0f7ff;border-radius:8px;padding:14px 16px;'
        'margin:18px 0;">\n'
        '  <p style="margin:0;font-size:14px;color:#2c3e3a;line-height:1.7;">'
        '<span leaf="">💬 互动一下：</span>'
        '<span leaf="">抛一个让读者想评论的问题。</span></p>\n'
        '</section>'
    ),
    "references": (
        '<section style="margin:0 0 12px;">\n'
        '  <p style="margin:0 0 14px;line-height:1.8;color:#3f3f3f;font-size:15px;">'
        '<span leaf="">· 论文：</span>'
        '<a href="https://arxiv.org/abs/XXXX" style="color:#3a5fcd;'
        'text-decoration:none;"><span leaf="">https://arxiv.org/abs/XXXX</span></a></p>\n'
        '  <p style="margin:0;font-size:13px;color:#8a94a6;line-height:1.7;">'
        '<span leaf="">图表摘自论文，仅作学术解读。</span></p>\n'
        '</section>'
    ),
}


def _tpl(cid: str) -> str:
    return _RAW.get(cid) or _FALLBACK[cid]


# --------------------------------------------------------------------------- #
# Parameterized render functions (each maps to one component)
# --------------------------------------------------------------------------- #
def section_header(text: str) -> str:
    """组件 #4 section-header：色条小标题。"""
    return _tpl("section-header").replace("小标题文字", _esc(text))


def one_liner(text: str, label: str = "📌 一句话：") -> str:
    """组件 #3 one-liner：📌 高亮框。label 默认保留「📌 一句话：」品牌前缀。"""
    t = _tpl("one-liner")
    t = t.replace("📌 一句话：", _esc(label))
    t = t.replace("核心结论放这里，一句话讲清价值。", _esc(text))
    return t


def body_para(text: str, keyword: str | None = None) -> str:
    """组件 #5 body-para：正文段落，可选关键词主色下划线（每段 1–3 处）。"""
    safe = _esc(text)
    if keyword:
        k = _esc(keyword)
        # 只替换首个命中，避免重复下划线
        safe = safe.replace(
            k,
            '<span leaf="" style="border-bottom:1px solid #3a5fcd;'
            'color:#3a5fcd;font-weight:700;">' + k + "</span>",
            1,
        )
    return (
        '<section style="margin:0 0 14px;">'
        '<p style="margin:0;line-height:1.8;color:#3f3f3f;font-size:15px;">'
        f'<span leaf="">{safe}</span></p></section>'
    )


def body_li(num: int, text: str) -> str:
    """有序列表项（编号 + 正文），复用 body-para 的合规结构。"""
    return body_para(f"{num}. {text}")


def body_bul(text: str) -> str:
    """无序列表项（· 前缀），复用 body-para 的合规结构。"""
    return body_para(f"· {text}")


def kpi_cards(cards: Sequence[tuple[str, str]]) -> str:
    """组件 #7 kpi-cards：一组 (数值, 说明) 卡片，横向 flex 排列。"""
    items = []
    for value, label in cards:
        item = _tpl("kpi-cards").replace("+8.04", _esc(value)).replace("指标说明", _esc(label))
        items.append(item)
    return (
        '<section style="display:flex;gap:10px;margin:0 0 16px;flex-wrap:wrap;">'
        + "".join(items)
        + "</section>"
    )


def limitation(text: str) -> str:
    """组件 #9 limitation：⚠️ 诚实备注框。"""
    return _tpl("limitation").replace("局限或需要诚实说明的点放这里。", _esc(text))


def cta(text: str, label: str = "💬 互动一下：") -> str:
    """组件 #10 cta：互动引导框。"""
    t = _tpl("cta").replace("💬 互动一下：", _esc(label))
    t = t.replace("抛一个让读者想评论的问题。", _esc(text))
    return t


def references(paper: str = "", pdf: str = "", note: str = "图表摘自论文，仅作学术解读。") -> str:
    """组件 #11 references：论文/PDF 链接 + 学术声明。"""
    url = paper or "https://arxiv.org/abs/XXXX"
    t = _tpl("references")
    t = t.replace("https://arxiv.org/abs/XXXX", _esc(url))
    t = t.replace("图表摘自论文，仅作学术解读。", _esc(note))
    return t


def cover(img: str) -> str:
    """组件 #2 cover：封面图（100% 宽居中）。"""
    return _tpl("cover").replace("图片URL或本地路径", _esc(img))


def figure(img: str, caption: str = "") -> str:
    """组件 #8 figure：带图注图（caption 为空则不写图注）。"""
    t = _tpl("figure").replace("图片URL", _esc(img))
    t = t.replace("图 N｜说明文字（只有真有说明才写）", _esc(caption) if caption else "")
    return t


def hook_title(title: str, subtitle: str = "") -> str:
    """组件 #1 hook-title：居中大标题 + 副标题钩子。"""
    t = _tpl("hook-title").replace("标题放这里", _esc(title))
    t = t.replace("副标题一句话钩子放这里", _esc(subtitle))
    return t


# Exported component id list (for callers / tests).
COMPONENT_IDS = (
    "hook-title", "cover", "one-liner", "section-header", "body-para",
    "rr-table", "kpi-cards", "figure", "limitation", "cta", "references",
)
