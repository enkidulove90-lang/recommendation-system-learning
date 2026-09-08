"""L2 共享图表轨道：纯 Python SVG 图表生成器（bar / line / pie）。

零外部依赖；主题色取自 ThemeTokens。A 轨用 ``to_img_tag`` 以 data-URI <img> 嵌入
（微信安全）；B 轨用 ``to_svg`` 直接合进卡片。生产可升级 ECharts(#17)/Chart.js(#15)。
"""
from __future__ import annotations

import base64
import html
from typing import Any, Dict, List

from ..core.types import ThemeTokens

_PALETTE = ["#3a5fcd", "#1a9e57", "#f0a020", "#8a94a6", "#e0567a", "#5b8def"]


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def render_svg(spec: Dict[str, Any], theme: ThemeTokens, width: int = 600, height: int = 360) -> str:
    """根据 spec 生成 SVG 字符串。spec.type ∈ {bar,line,pie}。"""
    ctype = spec.get("type", "bar")
    if ctype == "pie":
        return _pie(spec, theme, width, height)
    if ctype == "line":
        return _line(spec, theme, width, height)
    return _bar(spec, theme, width, height)


def _palette(theme: ThemeTokens) -> List[str]:
    return [_PALETTE[0], theme.color("ok"), theme.color("warn"),
            theme.color("mute")] + _PALETTE[4:]


def _bar(spec, theme, w, h) -> str:
    labels = spec.get("labels", [])
    series = spec.get("series", [{"name": "s", "data": spec.get("values", [])}])
    pal = _palette(theme)
    pad_l, pad_b, pad_t = 48, 40, 28
    plot_w, plot_h = w - pad_l - 16, h - pad_b - pad_t
    allv = [v for s in series for v in s.get("data", [])]
    vmax = max(allv) if allv else 1
    vmax = vmax * 1.1 or 1
    ngrp = max(len(labels), 1)
    gwidth = plot_w / ngrp
    ngroups_series = len(series)
    bw = gwidth * 0.7 / ngroups_series
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'font-family="-apple-system,PingFang SC,sans-serif">']
    # y 轴刻度
    for k in range(5):
        y = pad_t + plot_h * k / 4
        val = vmax * (4 - k) / 4
        svg.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-16}" y2="{y:.1f}" '
                   f'stroke="#e3e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{pad_l-6}" y="{y+4:.1f}" fill="{theme.color("mute")}" '
                   f'font-size="11" text-anchor="end">{val:.1f}</text>')
    for gi, lab in enumerate(labels):
        gx = pad_l + gwidth * gi + gwidth * 0.15
        for si, s in enumerate(series):
            data = s.get("data", [])
            if gi >= len(data):
                continue
            v = data[gi]
            bh = plot_h * v / vmax
            x = gx + si * bw
            y = pad_t + plot_h - bh
            col = s.get("color") or pal[si % len(pal)]
            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.92:.1f}" '
                       f'height="{bh:.1f}" rx="3" fill="{col}"/>')
            svg.append(f'<text x="{x+bw*0.46:.1f}" y="{y-4:.1f}" fill="{col}" '
                       f'font-size="11" text-anchor="middle" font-weight="700">{v}</text>')
        svg.append(f'<text x="{pad_l+gwidth*gi+gwidth/2:.1f}" y="{h-16:.1f}" '
                   f'fill="{theme.color("body")}" font-size="12" text-anchor="middle">'
                   f'{_esc(lab)}</text>')
    if spec.get("title"):
        svg.append(f'<text x="{pad_l}" y="16" fill="{theme.color("title")}" '
                   f'font-size="13" font-weight="700">{_esc(spec["title"])}</text>')
    svg.append("</svg>")
    return "".join(svg)


def _line(spec, theme, w, h) -> str:
    labels = spec.get("labels", [])
    series = spec.get("series", [{"name": "s", "data": spec.get("values", [])}])
    pal = _palette(theme)
    pad_l, pad_b, pad_t = 48, 40, 28
    plot_w, plot_h = w - pad_l - 16, h - pad_b - pad_t
    allv = [v for s in series for v in s.get("data", [])]
    vmax = max(allv) if allv else 1
    vmin = min(allv) if allv else 0
    rng = (vmax - vmin) or 1
    vmax, vmin = vmax + rng * 0.1, vmin - rng * 0.1
    rng = (vmax - vmin) or 1
    n = max(len(labels), 1)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'font-family="-apple-system,PingFang SC,sans-serif">']
    for k in range(5):
        y = pad_t + plot_h * k / 4
        val = vmax + (vmin - vmax) * k / 4
        svg.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-16}" y2="{y:.1f}" '
                   f'stroke="#e3e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{pad_l-6}" y="{y+4:.1f}" fill="{theme.color("mute")}" '
                   f'font-size="11" text-anchor="end">{val:.1f}</text>')
    for si, s in enumerate(series):
        data = s.get("data", [])
        pts = []
        for xi, v in enumerate(data):
            x = pad_l + (plot_w * xi / max(n - 1, 1))
            y = pad_t + plot_h * (vmax - v) / rng
            pts.append((x, y))
        col = s.get("color") or pal[si % len(pal)]
        d = " ".join(f"L{x:.1f},{y:.1f}" if i else f"M{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(pts))
        svg.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        for x, y in pts:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{col}"/>')
    for xi, lab in enumerate(labels):
        x = pad_l + (plot_w * xi / max(n - 1, 1))
        svg.append(f'<text x="{x:.1f}" y="{h-16:.1f}" fill="{theme.color("body")}" '
                   f'font-size="12" text-anchor="middle">{_esc(lab)}</text>')
    if spec.get("title"):
        svg.append(f'<text x="{pad_l}" y="16" fill="{theme.color("title")}" '
                   f'font-size="13" font-weight="700">{_esc(spec["title"])}</text>')
    svg.append("</svg>")
    return "".join(svg)


def _pie(spec, theme, w, h) -> str:
    labels = spec.get("labels", [])
    values = spec.get("values", [])
    pal = _palette(theme)
    total = sum(values) or 1
    cx, cy, r = w / 2, h / 2 + 6, min(w, h) / 2 - 30
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'font-family="-apple-system,PingFang SC,sans-serif">']
    ang = 0.0
    for i, v in enumerate(values):
        frac = v / total
        a2 = ang + frac * 360
        import math
        x1, y1 = cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))
        x2, y2 = cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2))
        large = 1 if frac > 0.5 else 0
        col = pal[i % len(pal)]
        svg.append(f'<path d="M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} '
                   f'A{r},{r} 0 {large} 1 {x2:.1f},{y2:.1f} Z" fill="{col}"/>')
        ang = a2
    # 图例
    lx = cx + r + 16
    for i, lab in enumerate(labels):
        col = pal[i % len(pal)]
        svg.append(f'<rect x="{lx}" y="{cy - r + i*22}" width="12" height="12" '
                   f'rx="2" fill="{col}"/>')
        svg.append(f'<text x="{lx+18}" y="{cy - r + i*22 + 11}" fill="{theme.color("body")}" '
                   f'font-size="12">{_esc(lab)}</text>')
    if spec.get("title"):
        svg.append(f'<text x="{cx}" y="16" fill="{theme.color("title")}" '
                   f'font-size="13" font-weight="700" text-anchor="middle">'
                   f'{_esc(spec["title"])}</text>')
    svg.append("</svg>")
    return "".join(svg)


def to_img_tag(spec: Dict[str, Any], theme: ThemeTokens, width: int = 600) -> str:
    """A 轨：SVG 包成 data-URI <img>（微信安全嵌入）。"""
    svg = render_svg(spec, theme, width=width)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width:100%;display:block;margin:0 0 16px;">'


def to_svg(spec: Dict[str, Any], theme: ThemeTokens, width: int = 600) -> str:
    """B 轨：直接返回 SVG 字符串（合进卡片 HTML）。"""
    return render_svg(spec, theme, width=width)
