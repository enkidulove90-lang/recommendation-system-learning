"""声明式配图加工：自制数字卡与位图放大。

此前每个 ``build_xhs_draft_*.py`` 都自带一份 ``draw_numbers_card`` /
``upscale``，图卡数据硬编码在 Python 里。现在数据由 note spec 声明，
绘制代码只有这一份；归档脚本里的实现仅作溯源（见 archive/xhs_drafts/README.md）。

新稿在 ``redbook/notes/<slug>.yaml`` 的 figure 上写 ``card: {...}`` 配方，
由人工或 CLI 生成 PNG 后再把文件名填进 ``figures[].file``；本模块**不在
stage 时偷偷写文件**，避免发布链路产生隐式副作用。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_CANDIDATES_BOLD = ("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc")
FONT_CANDIDATES_REGULAR = ("C:/Windows/Fonts/msyh.ttc",)

BLUE = (36, 88, 168)
DARK = (30, 34, 42)
GREY = (118, 126, 138)
ACCENT = (196, 74, 36)


def _font(size: int, bold: bool = False):
    for candidate in FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REGULAR:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return ImageFont.load_default()


@dataclass(frozen=True)
class CardRow:
    label: str
    cells: tuple[tuple[str, str], ...]
    hint: str = ""


@dataclass(frozen=True)
class NumberCardSpec:
    title: str
    subtitle: str
    columns: tuple[str, ...]
    rows: tuple[CardRow, ...]
    footnotes: tuple[str, ...] = ()
    width: int = 1840
    row_height: int = 168

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "NumberCardSpec":
        rows = tuple(
            CardRow(
                label=str(row["label"]),
                cells=tuple((str(cell[0]), str(cell[1])) for cell in row.get("cells", ())),
                hint=str(row.get("hint", "")),
            )
            for row in data.get("rows", ())
        )
        return cls(
            title=str(data.get("title", "")),
            subtitle=str(data.get("subtitle", "")),
            columns=tuple(str(item) for item in data.get("columns", ())),
            rows=rows,
            footnotes=tuple(str(item) for item in data.get("footnotes", ())),
            width=int(data.get("width", 1840)),
            row_height=int(data.get("row_height", 168)),
        )


def upscale_image(source: str | Path, target: str | Path, factor: float = 1.8) -> dict:
    """1024px 源图放大一档 + 轻锐化（手机全宽时文字边缘更顺）。"""
    src, dst = Path(source), Path(target)
    with Image.open(src) as image:
        width, height = image.size
        resized = image.convert("RGB").resize(
            (int(width * factor), int(height * factor)), Image.LANCZOS
        )
    sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=3))
    dst.parent.mkdir(parents=True, exist_ok=True)
    sharpened.save(dst, optimize=True)
    return {"ok": True, "path": str(dst), "size": list(sharpened.size), "bytes": dst.stat().st_size}


def render_number_card(spec: NumberCardSpec, output: str | Path) -> dict:
    """把论文表格重排成手机可读的大字号数字卡。"""
    if not spec.rows or not spec.columns:
        return {"ok": False, "error": "rows and columns are required"}
    if any(len(row.cells) != len(spec.columns) for row in spec.rows):
        return {"ok": False, "error": "every row must have one cell per column"}

    width = spec.width
    top = 236
    row_height = spec.row_height
    height = top + 76 + row_height * len(spec.rows) + 250
    image = Image.new("RGB", (width, height), (250, 251, 253))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width, 14], fill=BLUE)
    draw.text((70, 58), spec.title, font=_font(56, True), fill=DARK)
    draw.text((70, 144), spec.subtitle, font=_font(27), fill=GREY)

    x_label, x_end = 70, width - 70
    step = min(430.0, (x_end - 600) / max(len(spec.columns), 1))
    column_x = [int(560 + index * step) for index in range(len(spec.columns))]
    f_head, f_label, f_value, f_pct = _font(29, True), _font(33, True), _font(32), _font(40, True)
    draw.rounded_rectangle([x_label, top, x_end, top + 76], radius=12, fill=(232, 238, 248))
    draw.text((x_label + 26, top + 23), "指标", font=f_head, fill=BLUE)
    for column, name in zip(column_x, spec.columns):
        draw.text((column, top + 23), name, font=f_head, fill=BLUE)

    y = top + 76
    for index, row in enumerate(spec.rows):
        draw.rectangle([x_label, y, x_end, y + row_height],
                       fill=(255, 255, 255) if index % 2 == 0 else (245, 247, 250))
        draw.line([x_label, y, x_end, y], fill=(226, 230, 238), width=2)
        draw.text((x_label + 26, y + 36), row.label, font=f_label, fill=DARK)
        if row.hint:
            draw.text((x_label + 26, y + 88), row.hint, font=_font(24), fill=GREY)
        for column, (value, delta) in zip(column_x, row.cells):
            draw.text((column, y + 28), value, font=f_value, fill=(64, 70, 80))
            draw.text((column, y + 80), delta, font=f_pct, fill=ACCENT)
        y += row_height
    draw.line([x_label, y, x_end, y], fill=(200, 206, 216), width=3)
    for index, note in enumerate(spec.footnotes):
        draw.text((70, y + 40 + index * 50), note,
                  font=_font(29, True) if index == 0 else _font(27),
                  fill=BLUE if index == 0 else GREY)

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, optimize=True)
    return {
        "ok": True, "path": str(target), "size": [width, height],
        "bytes": target.stat().st_size, "rows": len(spec.rows), "columns": len(spec.columns),
    }


def render_card_from_mapping(data: Mapping[str, Any], output: str | Path) -> dict:
    return render_number_card(NumberCardSpec.from_mapping(data), output)
