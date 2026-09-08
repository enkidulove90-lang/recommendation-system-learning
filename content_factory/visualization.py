"""Stage 4 可视化叙事（M3 交互可视化图 / M4 自动信息图 / M5 滚动叙事线）。

选型对齐 docs/content-factory-engineering.md：
  M3  Idyll / Observable / Vizzu(ipyvizzu)        报告 6 / 10 / 7
  M4  AntV Infographic / Narrative Chart(纳图)    报告 9 / 8
  M5  NarroViz / litvis                          报告 12 / 11

防幻觉铁律：所有图表数据仅来自 PaperSummary / StoryDraft 的事实字段
（bound_fields 可追溯）。外部服务（Idyll/Observable/AntV）需要前端或 API key，
本模块只产出「结构化 spec + 可离线渲染的内联 SVG/HTML 片段」，真正挂载到平台
时由 redbook 渲染层注入 iframe。无网络 / 无 key 环境即可跑通全部单测。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .schemas import PaperSummary, StoryDraft
from .title_factory import TitleFactory


@dataclass
class VizSpec:
    """一张可视化图的产出契约（工具无关，平台按需转译）。"""

    id: str
    kind: str            # metric_bar | learning_curve | infographic | scroll_story
    tool: str            # Idyll | Observable | Vizzu | AntV | NarroViz
    title: str
    data: dict[str, Any] = field(default_factory=dict)
    embed: dict[str, Any] = field(default_factory=dict)   # {type, html, note}
    bound_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VisualizationFactory:
    """从论文事实事实构建可视化 spec。"""

    # ── M3：指标对比柱状图（Observable / Vizzu）──
    def metric_bars(self, s: PaperSummary, tool: str = "Observable") -> VizSpec:
        metric, x, y = TitleFactory._extract_gain(s.key_result or s.method)
        data = {
            "metric": metric,
            "baseline": x,
            "proposed": y,
            "comparison": [
                {"label": "基线", "value": x, "group": "baseline"},
                {"label": "本文方法", "value": y, "group": "proposed"},
            ],
        }
        html = self._bars_svg([("基线", x), ("本文方法", y)], title=f"{metric} 对比")
        return VizSpec(
            id="viz_metric_bar", kind="metric_bar", tool=tool,
            title=f"{metric}：{x} → {y}",
            data=data, embed={"type": "svg", "html": html,
                              "note": "内联 SVG，可离线渲染；挂载平台时替换为 Observable/Vizzu iframe"},
            bound_fields=["key_result", "method"],
        )

    # ── M3：学习/提升曲线（Idyll / Observable Inputs）──
    def learning_curve(self, s: PaperSummary, tool: str = "Idyll") -> VizSpec:
        _, x, y = TitleFactory._extract_gain(s.key_result or s.method)
        # 仅有两个报告端点，曲线为「报告端点的线性插值」，明确标注非真实逐点数据
        data = {
            "x_label": "阶段（基线 → 本文）",
            "y_label": "指标",
            "points": [
                {"x": 0, "y": x, "note": "报告基线值"},
                {"x": 1, "y": y, "note": "报告本文值"},
            ],
            "interpolation": "linear-between-reported-endpoints",
        }
        html = self._line_svg([(0, x), (1, y)], title="提升曲线（端点来自报告）")
        return VizSpec(
            id="viz_learning_curve", kind="learning_curve", tool=tool,
            title="报告端点的提升曲线",
            data=data, embed={"type": "svg", "html": html,
                              "note": "仅两端点为论文报告值，中间为插值示意"},
            bound_fields=["key_result"],
        )

    # ── M4：自动信息图（AntV Infographic / Narrative Chart）──
    def infographic(self, s: PaperSummary, tool: str = "AntV") -> VizSpec:
        data = {
            "title": s.title_zh or s.title_en,
            "problem": s.problem,
            "method": s.method,
            "key_result": s.key_result,
            "limitations": s.limitations,
        }
        return VizSpec(
            id="viz_infographic", kind="infographic", tool=tool,
            title=f"信息图：{s.title_zh or s.title_en}",
            data=data,
            embed={"type": "markdown-infographic", "html": self._infographic_md(data),
                   "note": "结构化事实卡，可由 AntV/Narrative Chart 转译为图形信息图"},
            bound_fields=["problem", "method", "key_result", "limitations"],
        )

    # ── M5：滚动叙事线（NarroViz / litvis）──
    def scroll_story(self, story: StoryDraft, tool: str = "NarroViz") -> VizSpec:
        sections = [
            {"id": "hook", "heading": "为什么现在重要", "body": story.hook},
            {"id": "method", "heading": "我们怎么打", "body": story.method_section},
            {"id": "climax", "heading": "最反直觉的 1 个数", "body": story.climax_section},
            {"id": "ending", "heading": "它在哪会失效？", "body": story.ending_section},
        ]
        return VizSpec(
            id="viz_scroll_story", kind="scroll_story", tool=tool,
            title=f"滚动叙事：{story.title_zh}",
            data={"sections": sections},
            embed={"type": "scrollytelling", "html": self._scrollytell_html(sections),
                   "note": "每节一屏，可由 NarroViz/litvis 转译为滚动叙事"},
            bound_fields=list({f for v in story.bound_fields.values() for f in v}),
        )

    # ── 内联 SVG / HTML 辅助（离线可渲染，零依赖）──
    @staticmethod
    def _bars_svg(pairs: list[tuple[str, str]], title: str = "") -> str:
        try:
            vals = [float(str(v).rstrip("%")) for _, v in pairs]
        except Exception:
            vals = [1.0] * len(pairs)
        maxv = max(vals) or 1.0
        w, h, bw = 520, 240, 150
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
               f'viewBox="0 0 {w} {h}" role="img" aria-label="{title}">']
        if title:
            svg.append(f'<text x="20" y="28" font-size="16" font-weight="bold">{title}</text>')
        for i, (lab, v) in enumerate(pairs):
            bh = int((float(str(v).rstrip("%")) / maxv) * 160) + 4
            x = 60 + i * (bw + 40)
            svg.append(f'<rect x="{x}" y="{200 - bh}" width="{bw}" height="{bh}" '
                       f'fill="#3b6fd4" rx="4"/>')
            svg.append(f'<text x="{x + bw / 2}" y="{196 - bh}" font-size="13" '
                       f'text-anchor="middle">{v}</text>')
            svg.append(f'<text x="{x + bw / 2}" y="220" font-size="13" '
                       f'text-anchor="middle">{lab}</text>')
        svg.append("</svg>")
        return "".join(svg)

    @staticmethod
    def _line_svg(points: list[tuple[float, str]], title: str = "") -> str:
        w, h = 520, 240
        xs = [p[0] for p in points]
        try:
            ys = [float(str(p[1]).rstrip("%")) for p in points]
        except Exception:
            ys = [0.0] * len(points)
        maxy = max(ys) or 1.0
        miny = min(ys)
        rng = (maxy - miny) or 1.0
        def tx(x: float) -> int:
            return 60 + int((x - min(xs)) / (max(xs) - min(xs) or 1) * 400)
        def ty(y: float) -> int:
            return 200 - int((y - miny) / rng * 160)
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
               f'viewBox="0 0 {w} {h}" role="img" aria-label="{title}">']
        if title:
            svg.append(f'<text x="20" y="28" font-size="16" font-weight="bold">{title}</text>')
        pts = " ".join(f"{tx(x)},{ty(y)}" for x, y in zip(xs, ys))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="#3b6fd4" stroke-width="3"/>')
        for (x, y), (ox, oy) in zip(zip(xs, ys), points):
            svg.append(f'<circle cx="{tx(x)}" cy="{ty(y)}" r="5" fill="#3b6fd4"/>')
            svg.append(f'<text x="{tx(x)}" y="{ty(y) - 12}" font-size="12" '
                       f'text-anchor="middle">{oy}</text>')
        svg.append("</svg>")
        return "".join(svg)

    @staticmethod
    def _infographic_md(data: dict[str, Any]) -> str:
        lines = [f"# {data.get('title', '')}", ""]
        for head, key in [("问题", "problem"), ("方法", "method"),
                          ("关键结果", "key_result"), ("边界", "limitations")]:
            val = data.get(key) or "（原文未给出）"
            lines.append(f"**{head}**：{val}")
        return "\n".join(lines)

    @staticmethod
    def _scrollytell_html(sections: list[dict[str, str]]) -> str:
        items = "".join(
            f'<section style="min-height:80vh;padding:8vh 6vw;">'
            f'<h2>{s["heading"]}</h2><p>{s["body"]}</p></section>'
            for s in sections
        )
        return f'<div class="scrollytelling">{items}</div>'


def build_all(s: PaperSummary, story: StoryDraft | None = None) -> list[VizSpec]:
    """一键产出 Stage 4 全部可视化 spec。"""
    vf = VisualizationFactory()
    specs = [vf.metric_bars(s), vf.learning_curve(s), vf.infographic(s)]
    if story is not None:
        specs.append(vf.scroll_story(story))
    return specs
