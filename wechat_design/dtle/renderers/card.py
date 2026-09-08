"""L2 B 轨：小红书卡片渲染器（Document → 1242×1656 自包含卡片 HTML）。

- 输出完整 <html> 页面，所有样式内联，浏览器直接打开即所见即所得（可预览/可截图）。
- CardNode（camelCase React 风格）→ HTML 内联 style，Satori 就绪。
- ``card_to_png``：可选后端（Playwright/Chromium），未安装时抛清晰错误并提示安装路径。
"""
from __future__ import annotations

import re
from typing import Any, Dict, Union

from ..core.components import render_block_card
from ..core.types import CardNode, Document, ThemeTokens

# camelCase → kebab；数值除这些单位less 属性外自动补 px
_UNITLESS = {"lineHeight", "flex", "opacity", "zIndex", "fontWeight",
             "flexGrow", "flexShrink", "order", "zoom"}


def _style_to_css(style: Dict[str, Any]) -> str:
    out = []
    for k, v in style.items():
        if v is None:
            continue
        kb = re.sub(r"(?<!^)(?=[A-Z])", "-", k).lower()  # borderLeft→border-left
        if isinstance(v, (int, float)) and kb not in _UNITLESS:
            v = f"{v}px"
        out.append(f"{kb}:{v}")
    return ";".join(out)


def _render_node(node: Union[CardNode, str]) -> str:
    if isinstance(node, str):
        return node
    tag = node.type
    style = _style_to_css(node.style)
    attrs = f' style="{style}"' if style else ""
    # img / br 自闭合
    if tag in ("img", "br"):
        src = node.style.get("src") or node.style.get("Src")
        extra = f' src="{src}"' if src else ""
        return f"<img{attrs}{extra}/>"
    inner = "".join(_render_node(c) for c in node.children)
    if node.text:
        inner = node.text + inner
    return f"<{tag}{attrs}>{inner}</{tag}>"


def build_card_root(doc: Document, theme: ThemeTokens, W: int = 1242, H: int = 1656) -> CardNode:
    """构建 B 轨卡片的 CardNode 根（Satori 就绪 camelCase 风格），HTML 与 Satori 共用。"""
    root = CardNode("div", {
        "width": W, "minHeight": H, "backgroundColor": "#ffffff",
        "boxSizing": "border-box", "padding": 64, "margin": "0 auto",
        "fontFamily": '-apple-system,"PingFang SC","Microsoft YaHei",sans-serif',
        "display": "flex", "flexDirection": "column",
    })
    # 封面标题区
    if doc.title:
        root.add(CardNode("div", {"fontSize": 52, "fontWeight": 800,
                                  "color": theme.color("title"), "lineHeight": 1.3,
                                  "marginBottom": 8}, text=doc.title))
    if doc.subtitle:
        root.add(CardNode("div", {"fontSize": 26, "color": theme.color("mute"),
                                  "marginBottom": 20}, text=doc.subtitle))
    # 内容区
    body = CardNode("div", {"flex": 1, "display": "flex", "flexDirection": "column"})
    for b in doc.blocks:
        body.add(render_block_card(b.type, b.props, theme))
    root.add(body)
    # 品牌签名区
    sig = theme.brand.get("signature", "@RecSysLab")
    if sig:
        root.add(CardNode("div", {"textAlign": "center", "color": theme.color("mute"),
                                  "fontSize": 22, "marginTop": 24,
                                  "borderTopWidth": 1, "borderTopColor": theme.color("border"),
                                  "borderTopStyle": "solid", "paddingTop": 16}, text=sig))
    return root


def render_card_html(doc: Document, theme: ThemeTokens) -> str:
    """B 轨：1242×1656 小红书长图卡片（自包含 HTML，可预览/可截图）。"""
    W, H = 1242, 1656
    root = build_card_root(doc, theme, W, H)
    inner = _render_node(root)
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{doc.title or 'DTLE 卡片'} · {theme.name}</title>
<style>body{{margin:0;background:#e9edf2;}}</style>
</head>
<body>
{inner}
</body></html>"""


def card_to_png(html: str, out_path: str) -> str:
    """可选：用 Playwright/Chromium 把卡片 HTML 截成 PNG。

    未安装 playwright 时抛 RuntimeError 并提示安装命令（生产建议 Satori+resvg）。
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        raise RuntimeError(
            "B 轨 PNG 导出需要 Playwright：pip install playwright && playwright install chromium。"
            "生产环境推荐 Satori(#9)+@resvg/resvg-js 做确定性无浏览器渲染。"
        )
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1242, "height": 1656},
                                device_scale_factor=2)
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path=out_path, full_page=True)
        browser.close()
    return out_path


def build(theme_name: str, doc: Document) -> str:
    t = ThemeTokens.load(theme_name)
    return render_card_html(doc, t)
