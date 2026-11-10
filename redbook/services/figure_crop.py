"""按图注定位从 PDF 裁出矢量图 / 表（内联 tikz / pgfplots 专用）。

从根目录 ``crop_pdf_figure.py`` 提升为 service。后端既有的
``figure_retrieval.HighDpiPdfFigureExtractor`` 依赖 MinerU layout bbox，
对没有独立图片文件的矢量图无能为力；本模块补的是这条缺口。

两条实测踩坑，改动时不要"优化"掉
--------------------------------
1. 上界必须卡在**本页上一个图注的下边**（``prev_bottom``），否则同页两张图
   会被一起裁进来。
2. 横向必须扩到整栏。坐标轴刻度 / label 是文本，不属于 ``get_drawings()``，
   只用矢量 bbox 会把 y 轴刻度切掉（实测图框左沿 94pt、刻度起点约 70pt）。

CLI：``python -m redbook.services.figure_crop <pdf> <页码> <图注短语> <输出png> [max_h] [zoom]``
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Sequence

import fitz

CAPTION_PREFIXES = ("Fig.", "Fig ", "Figure", "Table", "TABLE")


def caption_lines(page: fitz.Page) -> list[fitz.Rect]:
    """本页所有以 Fig./Figure/Table 开头的行的矩形。"""
    out: list[fitz.Rect] = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if spans and spans[0]["text"].strip().startswith(CAPTION_PREFIXES):
                out.append(fitz.Rect(line["bbox"]))
    return out


def union_bbox(page: fitz.Page, caption: fitz.Rect, max_h: float) -> fitz.Rect | None:
    """求图注上方、上一图注下方的矢量绘图与位图并集 bbox。"""
    prev_bottom = 0.0
    for rect in caption_lines(page):
        if rect.y1 <= caption.y0 - 2:
            prev_bottom = max(prev_bottom, rect.y1)
    top_limit = max(caption.y0 - max_h, prev_bottom + 2)

    xs0, xs1 = caption.x0 - 34, caption.x1 + 34
    boxes: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        rect = drawing["rect"]
        if not rect.is_empty and rect.y1 <= caption.y0 + 4 and rect.y0 >= top_limit \
                and rect.x1 > xs0 and rect.x0 < xs1:
            boxes.append(rect)
    for info in page.get_image_info():
        rect = fitz.Rect(info["bbox"])
        if rect.y1 <= caption.y0 + 4 and rect.y0 >= top_limit and rect.x1 > xs0 and rect.x0 < xs1:
            boxes.append(rect)
    if not boxes:
        return None
    result = boxes[0]
    for box in boxes[1:]:
        result |= box
    return result


def crop_figure_by_caption(
    pdf_path: str | Path,
    page_number: int,
    needle: str,
    output: str | Path,
    *,
    max_height: float = 340.0,
    zoom: float = 4.0,
) -> dict:
    """裁出单张图，返回结构化回执（供 workflow / MCP 复用，不靠 stdout）。"""
    target = Path(output)
    document = fitz.open(str(pdf_path))
    try:
        if not 1 <= page_number <= document.page_count:
            return {"ok": False, "error": f"page {page_number} outside 1..{document.page_count}"}
        page = document[page_number - 1]
        hits = page.search_for(needle)
        if not hits:
            return {"ok": False, "error": f"caption phrase not found: {needle!r}"}
        caption = hits[-1]
        bbox = union_bbox(page, caption, max_height)
        fallback = False
        if bbox is None or bbox.height < 40 or bbox.width < 60:
            bbox = fitz.Rect(
                page.rect.x0 + 30, max(page.rect.y0, caption.y0 - max_height),
                page.rect.x1 - 30, caption.y0 - 6,
            )
            fallback = True
        else:
            x0 = max(page.rect.x0 + 28, min(bbox.x0, caption.x0) - 48)
            x1 = min(page.rect.x1 - 28, max(bbox.x1, caption.x1) + 14)
            bbox = fitz.Rect(x0, bbox.y0 - 8, x1, bbox.y1 + 6)
        clip = fitz.Rect(bbox) & page.rect
        pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(str(target))
        return {
            "ok": True, "path": str(target), "page": page_number,
            "clip": [round(v, 1) for v in clip], "pixels": [pixmap.width, pixmap.height],
            "bytes": target.stat().st_size, "fallback_full_column": fallback,
        }
    finally:
        document.close()


def crop_targets(
    pdf_path: str | Path,
    output_dir: str | Path,
    targets: Iterable[Sequence],
) -> list[dict]:
    """批量裁剪，替代根脚本 ``extract_sihg_assets.py`` 的手写循环。

    targets 每项为 ``(输出名, 页码1-based, 图注定位短语, 最大高度pt)``。
    """
    folder = Path(output_dir)
    results = []
    for item in targets:
        name, page, needle, *rest = item
        max_h = float(rest[0]) if rest else 340.0
        result = crop_figure_by_caption(
            pdf_path, int(page), str(needle), folder / f"{name}.png", max_height=max_h
        )
        results.append({"name": name, **result})
    return results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crop a vector figure from a PDF by its caption")
    parser.add_argument("pdf")
    parser.add_argument("page", type=int, help="1-based page number")
    parser.add_argument("needle", help="caption phrase to locate the figure")
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-height", type=float, default=340.0)
    parser.add_argument("--zoom", type=float, default=4.0)
    args = parser.parse_args(argv)
    result = crop_figure_by_caption(
        args.pdf, args.page, args.needle, args.output,
        max_height=args.max_height, zoom=args.zoom,
    )
    print(result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
