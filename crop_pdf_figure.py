# -*- coding: utf-8 -*-
"""通用：从 PDF 里按"图注定位"裁出一张图（含内联 tikz/pgfplots 生成的矢量图）。

为什么需要：排版论文的图多为矢量，`page.get_images()` 拿不到（只会返回每页重复的模板底图），
必须靠文本层定位图注，再在"图注上方"收集矢量绘图求并集 bbox，最后高倍 clip 渲染。

关键细节：**上界要卡在本页"上一个图注的下边"**，否则同页两张图会被一起裁进来。

用法：
    python crop_pdf_figure.py <pdf> <页码1-based> <图注定位短语> <输出png> [最大高度pt] [zoom]
"""
from __future__ import annotations

import sys
from pathlib import Path

import fitz

CAPTION_PREFIXES = ("Fig.", "Fig ", "Figure", "Table", "TABLE")


def caption_lines(page: fitz.Page) -> list[fitz.Rect]:
    """本页所有以 Fig./Figure/Table 开头的行的矩形（用于取"上一个图注"的下边界）。"""
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
    prev_bottom = 0.0
    for r in caption_lines(page):
        if r.y1 <= caption.y0 - 2:
            prev_bottom = max(prev_bottom, r.y1)
    top_limit = max(caption.y0 - max_h, prev_bottom + 2)

    xs0, xs1 = caption.x0 - 34, caption.x1 + 34
    boxes: list[fitz.Rect] = []
    for d in page.get_drawings():
        r = d["rect"]
        if not r.is_empty and r.y1 <= caption.y0 + 4 and r.y0 >= top_limit and r.x1 > xs0 and r.x0 < xs1:
            boxes.append(r)
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if r.y1 <= caption.y0 + 4 and r.y0 >= top_limit and r.x1 > xs0 and r.x0 < xs1:
            boxes.append(r)
    if not boxes:
        return None
    out = boxes[0]
    for b in boxes[1:]:
        out |= b
    return out


def main() -> int:
    if len(sys.argv) < 5:
        print(__doc__)
        return 2
    pdf, pno, needle, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    max_h = float(sys.argv[5]) if len(sys.argv) > 5 else 340.0
    zoom = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0

    doc = fitz.open(pdf)
    page = doc[pno - 1]
    hits = page.search_for(needle)
    if not hits:
        print("!! 未找到图注短语:", needle)
        return 1
    cap = hits[-1]
    bbox = union_bbox(page, cap, max_h)
    note = ""
    if bbox is None or bbox.height < 40 or bbox.width < 60:
        bbox = fitz.Rect(page.rect.x0 + 30, max(page.rect.y0, cap.y0 - max_h), page.rect.x1 - 30, cap.y0 - 6)
        note = " (fallback 整栏)"
    else:
        # 横向扩到"整栏"：坐标轴刻度/label 是文本、不属于 drawings，
        # 只用矢量 bbox 会把 y 轴刻度裁掉（实测图框左沿 94pt、刻度起点 ~70pt）。
        x0 = max(page.rect.x0 + 28, min(bbox.x0, cap.x0) - 48)
        x1 = min(page.rect.x1 - 28, max(bbox.x1, cap.x1) + 14)
        bbox = fitz.Rect(x0, bbox.y0 - 8, x1, bbox.y1 + 6)
    clip = fitz.Rect(bbox) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(out)
    print("p%d clip=%dx%dpt -> %dx%dpx %dKB -> %s%s"
          % (pno, clip.width, clip.height, pix.width, pix.height, out.stat().st_size // 1024, out, note))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
