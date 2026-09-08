"""DTLE 双轨排版引擎 —— 公开 API。

一套配置，双轨输出：
  - track="wechat" → 微信安全内联 HTML（A 轨），附带发布前校验门结果。
  - track="xhs"    → 小红书 1242×1656 卡片 HTML（B 轨，可预览/可截图）。

主题每次渲染从 YAML 重读（配置驱动热更新，无需重启）。

快速开始
--------
    from wechat_design.dtle import render_source
    out = render_source(markdown_text, track="wechat", theme="recsys-blue")
    print(out["html"])
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Union

from .core.document import parse_markdown
from .core.types import Document, ThemeTokens
from .renderers.card import render_card_html
from .renderers.rich_text import render_document, wrap_preview
from .tokens import list_themes
from .validation.gate import GateResult, full_check

TRACKS = ("wechat", "xhs")


@dataclass
class RenderOutput:
    track: str
    theme: str
    html: str
    gate: Dict[str, Any] = None  # 仅 wechat 轨有校验结果
    preview_html: str = ""       # 仅 wechat 轨有预览页

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def _load_theme(name: str) -> ThemeTokens:
    if name not in list_themes():
        raise ValueError(f"未知主题 {name!r}（可选 {list_themes()}）")
    return ThemeTokens.load(name)


def render(doc: Document, track: str, theme: str = "recsys-blue") -> RenderOutput:
    if track not in TRACKS:
        raise ValueError(f"未知 track {track!r}（可选 {TRACKS}）")
    t = _load_theme(theme)
    if track == "wechat":
        html = render_document(doc, t)
        gate = full_check(html, name=f"<{theme}/wechat>")
        preview = wrap_preview(doc, t, html)
        return RenderOutput(track="wechat", theme=theme, html=html,
                             gate=asdict(gate), preview_html=preview)
    # xhs
    html = render_card_html(doc, t)
    return RenderOutput(track="xhs", theme=theme, html=html)


def render_dict(d: Dict[str, Any], track: str, theme: str = None) -> RenderOutput:
    theme = theme or d.get("theme", "recsys-blue")
    doc = Document.from_dict(d)
    doc.theme = theme
    return render(doc, track, theme)


def render_markdown(md: str, track: str, theme: str = "recsys-blue",
                    title: str = "") -> RenderOutput:
    doc = parse_markdown(md, title=title, theme=theme)
    return render(doc, track, theme)


def resolve_doc(source: Union[str, Dict[str, Any]],
                theme: str = "recsys-blue") -> tuple:
    """把 source 解析为 (Document, 实际 theme)。

    source 可为：① Markdown 文本；② .md 文件路径；③ .json 结构化文档路径；④ dict。
    供 render_source 与 B 轨 PNG（需 Document 实体）共用，避免重复解析逻辑。
    """
    if isinstance(source, dict):
        t = theme or source.get("theme", "recsys-blue")
        doc = Document.from_dict(source)
        doc.theme = t
        return doc, t
    if os.path.exists(source):
        if source.endswith(".json"):
            with open(source, encoding="utf-8") as f:
                d = json.load(f)
            t = theme or d.get("theme", "recsys-blue")
            doc = Document.from_dict(d)
            doc.theme = t
            return doc, t
        if source.endswith(".md"):
            with open(source, encoding="utf-8") as f:
                txt = f.read()
            t = theme or "recsys-blue"
            doc = parse_markdown(txt, title=os.path.splitext(
                os.path.basename(source))[0], theme=t)
            return doc, t
    # 视为 Markdown 文本
    t = theme or "recsys-blue"
    return parse_markdown(source, theme=t), t


def render_source(source: Union[str, Dict[str, Any]], track: str,
                  theme: str = "recsys-blue") -> RenderOutput:
    """source 可为：① Markdown 文本；② .md 文件路径；③ .json 结构化文档路径；④ dict。"""
    doc, t = resolve_doc(source, theme)
    return render(doc, track, t)


def list_available_themes() -> list:
    return list_themes()
