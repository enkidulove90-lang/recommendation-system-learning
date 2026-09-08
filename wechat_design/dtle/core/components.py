"""L1 组件层 —— 11 个 recsys-blue 组件，每组件双 adapter：to_html(A 轨) + to_card(B 轨)。

A 轨 to_html：全部内联 style；含中文文字节点用 <span leaf=""> 包裹（公众号铁律）。
B 轨 to_card：产出 CardNode（React/camelCase 风格，Satori 就绪），由 card 渲染器落 HTML/SVG。
两 adapter 共享同一份 props 与 ThemeTokens，保证双轨视觉一致。
"""
from __future__ import annotations

import re
from typing import Any, Dict

from .types import CardNode, ThemeTokens, leaf

PRIMARY = "primary"
TITLE = "title"
BODY = "body"
MUTE = "mute"
WARN = "warn"
WARN_BG = "warn_bg"
OK = "ok"
BG_LIGHT = "bg_light"
CARD_BG = "card_bg"
BORDER = "border"
CODE_BG = "code_bg"


def _highlight(text: str, keywords, t: ThemeTokens) -> str:
    """正文关键词下划线（A 轨）。"""
    if not keywords:
        return leaf(text)
    pat = re.compile("(" + "|".join(re.escape(k) for k in keywords) + ")")
    segs = pat.split(text)
    out = []
    for i, s in enumerate(segs):
        if not s:
            continue
        if i % 2 == 1:
            out.append(
                f'<span leaf="" style="border-bottom:1px solid {t.color(PRIMARY)};'
                f'color:{t.color(PRIMARY)};font-weight:700;">{s}</span>'
            )
        else:
            out.append(leaf(s))
    return "".join(out)


class Component:
    name = ""

    def to_html(self, p: Dict[str, Any], t: ThemeTokens) -> str:
        raise NotImplementedError

    def to_card(self, p: Dict[str, Any], t: ThemeTokens) -> CardNode:
        raise NotImplementedError


class HookTitle(Component):
    name = "hook_title"

    def to_html(self, p, t):
        title = p.get("title", "")
        sub = p.get("subtitle", "")
        s = (f'<section style="text-align:center;margin:0 0 6px;">'
             f'<h1 style="font-size:{t.font("h1")}px;line-height:1.45;margin:0;'
             f'color:{t.color(TITLE)};font-weight:700;">{leaf(title)}</h1></section>')
        if sub:
            s += (f'<section style="text-align:center;margin:0 0 18px;">'
                  f'<p style="font-size:{t.font("caption")}px;color:{t.color(MUTE)};'
                  f'line-height:1.6;margin:0;">{leaf(sub)}</p></section>')
        return s

    def to_card(self, p, t):
        node = CardNode("div", {"display": "flex", "flexDirection": "column",
                                "alignItems": "center", "marginBottom": 18})
        node.add(CardNode("div", {"fontSize": t.font("h1") * 1.4, "fontWeight": 800,
                                  "color": t.color(TITLE), "textAlign": "center",
                                  "lineHeight": 1.3}, text=p.get("title", "")))
        if p.get("subtitle"):
            node.add(CardNode("div", {"fontSize": 18, "color": t.color(MUTE),
                                      "textAlign": "center", "marginTop": 8},
                              text=p.get("subtitle", "")))
        return node


class Cover(Component):
    name = "cover"

    def to_html(self, p, t):
        src = p.get("src", "")
        s = (f'<section style="margin:0 0 18px;">'
             f'<img src="{src}" style="width:100%;border-radius:{t.radius}px;display:block;"></section>')
        return s

    def to_card(self, p, t):
        return CardNode("img", {"width": "100%", "borderRadius": t.radius,
                                "marginBottom": 16, "src": p.get("src", "")})


class OneLiner(Component):
    name = "one_liner"

    def to_html(self, p, t):
        return (f'<section style="background:{t.color(BG_LIGHT)};'
                f'border-left:4px solid {t.color(PRIMARY)};padding:12px 16px;'
                f'border-radius:6px;margin:0 0 16px;">'
                f'<p style="margin:0;line-height:1.8;color:{t.color(BODY)};'
                f'font-size:{t.font("body")}px;">'
                f'<span leaf="">📌 一句话：</span>{leaf(p.get("text", ""))}</p></section>')

    def to_card(self, p, t):
        return CardNode("div", {"backgroundColor": t.color(BG_LIGHT),
                                "borderLeftWidth": 4, "borderLeftColor": t.color(PRIMARY),
                                "borderLeftStyle": "solid", "padding": "12px 16px",
                                "borderRadius": 6, "marginBottom": 16},
                        text="📌 " + p.get("text", ""))


class SectionHeader(Component):
    name = "section_header"

    def to_html(self, p, t):
        return (f'<section style="border-left:4px solid {t.color(PRIMARY)};'
                f'padding-left:10px;margin:24px 0 12px;">'
                f'<h2 style="font-size:{t.font("h2")}px;font-weight:700;'
                f'color:{t.color(TITLE)};line-height:1.45;margin:0;">'
                f'{leaf(p.get("text", ""))}</h2></section>')

    def to_card(self, p, t):
        return CardNode("div", {"borderLeftWidth": 4, "borderLeftColor": t.color(PRIMARY),
                                "borderLeftStyle": "solid", "paddingLeft": 10,
                                "marginTop": 24, "marginBottom": 12,
                                "fontSize": t.font("h2") + 4, "fontWeight": 700,
                                "color": t.color(TITLE)}, text=p.get("text", ""))


class BodyPara(Component):
    name = "body_para"

    def to_html(self, p, t):
        text = p.get("text", "")
        keywords = p.get("keywords")
        inner = _highlight(text, keywords, t)
        return (f'<section style="margin:0 0 14px;">'
                f'<p style="margin:0;line-height:1.8;color:{t.color(BODY)};'
                f'font-size:{t.font("body")}px;">{inner}</p></section>')

    def to_card(self, p, t):
        return CardNode("div", {"marginBottom": 14, "fontSize": 17,
                                "lineHeight": 1.8, "color": t.color(BODY)},
                        text=p.get("text", ""))


class RrTable(Component):
    name = "rr_table"

    def to_html(self, p, t):
        headers = p.get("headers", [])
        rows = p.get("rows", [])
        th = "".join(
            f'<th style="border:1px solid {t.color(BORDER)};padding:9px 8px;'
            f'text-align:left;"><span leaf="">{h}</span></th>' for h in headers)
        trs = []
        for r in rows:
            cells = []
            for c in r:
                cells.append(f'<td style="border:1px solid {t.color(BORDER)};'
                             f'padding:9px 8px;"><span leaf="">{c}</span></td>')
            trs.append("<tr>" + "".join(cells) + "</tr>")
        return (f'<section style="margin:6px 0 16px;">'
                f'<table style="width:100%;border-collapse:collapse;'
                f'font-size:14px;">'
                f'<thead><tr style="background:{t.color(PRIMARY)};'
                f'color:#ffffff;">{th}</tr></thead>'
                f'<tbody>{"".join(trs)}</tbody></table></section>')

    def to_card(self, p, t):
        node = CardNode("div", {"marginBottom": 16, "width": "100%"})
        tbl = CardNode("div", {"display": "flex", "flexDirection": "column",
                               "borderWidth": 1, "borderColor": t.color(BORDER),
                               "borderStyle": "solid", "borderRadius": 6})
        head = CardNode("div", {"display": "flex", "backgroundColor": t.color(PRIMARY)})
        for h in p.get("headers", []):
            head.add(CardNode("div", {"flex": 1, "padding": "9px 8px",
                                      "color": "#fff", "fontWeight": 700}, text=h))
        tbl.add(head)
        for r in p.get("rows", []):
            row = CardNode("div", {"display": "flex",
                                   "borderTopWidth": 1, "borderTopColor": t.color(BORDER),
                                   "borderTopStyle": "solid"})
            for c in r:
                row.add(CardNode("div", {"flex": 1, "padding": "9px 8px",
                                         "color": t.color(BODY)}, text=c))
            tbl.add(row)
        node.add(tbl)
        return node


class KpiCards(Component):
    name = "kpi_cards"

    def to_html(self, p, t):
        items = p.get("items", [])
        cells = []
        for it in items:
            cells.append(
                f'<section style="flex:1;min-width:90px;background:{t.color(CARD_BG)};'
                f'border:1px solid {t.color(BORDER)};border-radius:{t.radius}px;'
                f'padding:10px 8px;text-align:center;">'
                f'<p style="margin:0;font-size:{t.font("kpi")}px;font-weight:700;'
                f'color:{t.color(PRIMARY)};line-height:1.2;">'
                f'<span leaf="">{it.get("value","")}</span></p>'
                f'<p style="margin:2px 0 0;font-size:12px;color:{t.color(MUTE)};">'
                f'<span leaf="">{it.get("label","")}</span></p></section>')
        return f'<section style="display:flex;gap:10px;margin:0 0 16px;flex-wrap:wrap;">{"".join(cells)}</section>'

    def to_card(self, p, t):
        node = CardNode("div", {"display": "flex", "gap": 12, "marginBottom": 16,
                                "flexWrap": "wrap"})
        for it in p.get("items", []):
            node.add(CardNode("div", {"flex": 1, "minWidth": 90,
                                      "backgroundColor": t.color(CARD_BG),
                                      "borderWidth": 1, "borderColor": t.color(BORDER),
                                      "borderStyle": "solid", "borderRadius": t.radius,
                                      "padding": "12px 8px", "alignItems": "center",
                                      "textAlign": "center"},
                             children=[
                                 CardNode("div", {"fontSize": t.font("kpi") + 6,
                                                  "fontWeight": 800, "color": t.color(PRIMARY)},
                                          text=it.get("value", "")),
                                 CardNode("div", {"fontSize": 13, "color": t.color(MUTE),
                                                  "marginTop": 4}, text=it.get("label", "")),
                             ]))
        return node


class Figure(Component):
    name = "figure"

    def to_html(self, p, t):
        s = (f'<section style="margin:0 0 18px;">'
             f'<img src="{p.get("src","")}" style="width:100%;border-radius:6px;'
             f'border:1px solid #f0f0f0;display:block;">')
        if p.get("caption"):
            s += (f'<p style="font-size:{t.font("caption")}px;color:{t.color(MUTE)};'
                  f'line-height:1.6;margin:6px 0 0;text-align:center;">'
                  f'<span leaf="">{p.get("caption")}</span></p>')
        s += "</section>"
        return s

    def to_card(self, p, t):
        node = CardNode("div", {"marginBottom": 16})
        node.add(CardNode("img", {"width": "100%", "borderRadius": 6,
                                  "borderWidth": 1, "borderColor": "#f0f0f0",
                                  "borderStyle": "solid", "src": p.get("src", "")}))
        if p.get("caption"):
            node.add(CardNode("div", {"fontSize": 13, "color": t.color(MUTE),
                                      "textAlign": "center", "marginTop": 6},
                              text=p.get("caption", "")))
        return node


class Limitation(Component):
    name = "limitation"

    def to_html(self, p, t):
        return (f'<section style="background:{t.color(WARN_BG)};'
                f'border-left:4px solid {t.color(WARN)};padding:12px 16px;'
                f'border-radius:6px;margin:0 0 16px;">'
                f'<p style="margin:0;line-height:1.8;color:{t.color(BODY)};'
                f'font-size:14px;"><span leaf="">⚠️ 备注：</span>'
                f'{leaf(p.get("text",""))}</p></section>')

    def to_card(self, p, t):
        return CardNode("div", {"backgroundColor": t.color(WARN_BG),
                                "borderLeftWidth": 4, "borderLeftColor": t.color(WARN),
                                "borderLeftStyle": "solid", "padding": "12px 16px",
                                "borderRadius": 6, "marginBottom": 16},
                        text="⚠️ " + p.get("text", ""))


class Cta(Component):
    name = "cta"

    def to_html(self, p, t):
        return (f'<section style="background:{t.color(BG_LIGHT)};border-radius:8px;'
                f'padding:14px 16px;margin:18px 0;">'
                f'<p style="margin:0;font-size:14px;color:{t.color(BODY)};line-height:1.7;">'
                f'<span leaf="">💬 互动一下：</span>{leaf(p.get("text",""))}</p></section>')

    def to_card(self, p, t):
        return CardNode("div", {"backgroundColor": t.color(BG_LIGHT), "borderRadius": 8,
                                "padding": "14px 16px", "marginTop": 18, "marginBottom": 18},
                        text="💬 " + p.get("text", ""))


class References(Component):
    name = "references"

    def to_html(self, p, t):
        items = p.get("items", [])
        paras = []
        for it in items:
            url = it.get("url", "")
            label = it.get("label", url)
            paras.append(
                f'<p style="margin:0 0 14px;line-height:1.8;color:{t.color(BODY)};'
                f'font-size:{t.font("body")}px;"><span leaf="">· {label}：</span>'
                f'<a href="{url}" style="color:{t.color(PRIMARY)};text-decoration:none;">'
                f'<span leaf="">{url}</span></a></p>')
        note = ""
        if p.get("note"):
            note = (f'<p style="margin:0;font-size:{t.font("caption")}px;'
                    f'color:{t.color(MUTE)};line-height:1.7;">'
                    f'<span leaf="">{p.get("note")}</span></p>')
        return f'<section style="margin:0 0 12px;">{"".join(paras)}{note}</section>'

    def to_card(self, p, t):
        node = CardNode("div", {"marginBottom": 12})
        for it in p.get("items", []):
            node.add(CardNode("div", {"fontSize": 14, "color": t.color(BODY),
                                      "marginBottom": 6},
                              text=f"· {it.get('label', it.get('url',''))}: {it.get('url','')}"))
        if p.get("note"):
            node.add(CardNode("div", {"fontSize": 13, "color": t.color(MUTE),
                                      "marginTop": 4}, text=p.get("note", "")))
        return node


REGISTRY: Dict[str, Component] = {
    c().name: c() for c in [
        HookTitle, Cover, OneLiner, SectionHeader, BodyPara,
        RrTable, KpiCards, Figure, Limitation, Cta, References,
    ]
}


def render_block_html(block_type: str, props: Dict[str, Any], t: ThemeTokens) -> str:
    comp = REGISTRY.get(block_type)
    if not comp:
        # 未知组件降级为纯文本段
        return (f'<section style="margin:0 0 14px;"><p style="margin:0;'
                f'line-height:1.8;color:{t.color(BODY)};">'
                f'{leaf(str(props.get("text", block_type)))}</p></section>')
    return comp.to_html(props, t)


def render_block_card(block_type: str, props: Dict[str, Any], t: ThemeTokens) -> CardNode:
    comp = REGISTRY.get(block_type)
    if not comp:
        return CardNode("div", {"marginBottom": 14, "color": t.color(BODY)},
                        text=str(props.get("text", block_type)))
    return comp.to_card(props, t)
