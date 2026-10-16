# -*- coding: utf-8 -*-
"""从 SIHG-Rec 的 ACM PDF 里裁出图/表（矢量内容用高倍渲染得到高清 PNG），并导出指定页文本。

裁剪原理：矢量图不是"嵌入位图"，无法 extract_image 拿到。做法是——
1. 文本层定位图注（caption）矩形的坐标；
2. 在"图注上方"的区域内收集矢量绘图(get_drawings)与嵌入位图(get_image_info)，
   求并集 bbox（正文文本不属于 drawings，因此不会混入）；
3. 用 4 倍 zoom（≈288 DPI）按该 bbox clip 渲染。

用法：python extract_sihg_assets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "data" / "parsed" / "sihg_rec" / "10.1145_3847662.pdf"
IMG_DIR = ROOT / "data" / "parsed" / "sihg_rec" / "images"
TXT_OUT = ROOT / "data" / "parsed" / "sihg_rec" / "sihg_text_excerpt.txt"

# (输出名, 页码(1-based), 图注定位短语, 裁剪区域最大高度pt)
TARGETS = [
    ("fig1_overview", 5, "overview structure of SIHG-Rec", 460),
    ("fig2_ablation", 19, "Ablation study for SIHG-Rec", 400),
    ("fig3_sparsity", 22, "Sparsity analysis for SIHG-Rec", 400),
    ("fig4_convergence", 24, "Convergence analysis for SIHG-Rec", 320),
    ("fig5_hyper_lr", 24, "Hyper-parameter analysis for SIHG-Rec across all datasets in terms of Recall", 320),
    ("fig6_hyper_k", 25, "Hyper-parameter analysis for SIHG-Rec across all datasets for", 340),
    ("fig11_adaptive", 28, "Analysis for adaptive weighting mechanism", 300),
    ("fig13_cos", 30, "Analysis for cross-modality cosine similarity", 280),
    ("tab6_coldstart", 22, "User cold-start analysis across all datasets", 300),
    ("tab3_main", 18, "Performance comparison of baselines and SIHG-Rec in terms of Recall", 420),
]

TEXT_PAGES = [1, 2, 4, 5, 6, 18, 19, 20, 21, 22]


CAPTION_PREFIXES = ("Fig.", "Figure", "Table", "TABLE")


def page_caption_rects(page: fitz.Page) -> list[fitz.Rect]:
    """页面上所有"图/表注"所在行的矩形（用于确定上一个图注的下边界）。"""
    rects: list[fitz.Rect] = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            head = spans[0]["text"].strip()
            if head.startswith(CAPTION_PREFIXES):
                rects.append(fitz.Rect(line["bbox"]))
    return rects


def union_bbox(page: fitz.Page, caption: fitz.Rect, max_h: float) -> fitz.Rect | None:
    # 上界：优先取"上一个图注的下边"，避免把上一张图的内容一起裁进来
    prev_bottom = 0.0
    for r in page_caption_rects(page):
        if r.y1 <= caption.y0 - 2:
            prev_bottom = max(prev_bottom, r.y1)
    top_limit = max(caption.y0 - max_h, prev_bottom + 2)

    xs0, xs1 = caption.x0 - 34, caption.x1 + 34
    boxes: list[fitz.Rect] = []

    for d in page.get_drawings():
        r = d["rect"]
        if r.is_empty:
            continue
        if r.y1 <= caption.y0 + 4 and r.y0 >= top_limit and r.x1 > xs0 and r.x0 < xs1:
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


def crop(target: tuple) -> str:
    name, pno, needle, max_h = target
    doc = fitz.open(PDF)
    page = doc[pno - 1]
    hits = page.search_for(needle)
    if not hits:
        return f"{name}: !! 未找到图注 '{needle}'"
    cap = hits[-1]
    bbox = union_bbox(page, cap, max_h)
    if bbox is None or bbox.height < 40 or bbox.width < 60:
        bbox = fitz.Rect(page.rect.x0 + 30, cap.y0 - min(max_h, 260), page.rect.x1 - 30, cap.y0 - 6)
        note = " (fallback 整栏裁剪)"
    else:
        bbox = fitz.Rect(bbox.x0 - 6, bbox.y0 - 8, bbox.x1 + 6, bbox.y1 + 6)
        note = ""
    clip = fitz.Rect(bbox) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=clip, alpha=False)
    out = IMG_DIR / f"{name}.png"
    pix.save(out)
    return f"{name}: p{pno} clip={clip.width:.0f}x{clip.height:.0f}pt -> {pix.width}x{pix.height}px {out.stat().st_size // 1024}KB{note}"


def dump_text() -> str:
    doc = fitz.open(PDF)
    chunks = []
    for pno in TEXT_PAGES:
        chunks.append("\n" + "=" * 30 + f" PAGE {pno} " + "=" * 30)
        chunks.append(doc[pno - 1].get_text())
    TXT_OUT.write_text("\n".join(chunks), encoding="utf-8")
    return f"text -> {TXT_OUT.name} ({len(''.join(chunks))} chars, pages {TEXT_PAGES})"


def main() -> int:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    print(dump_text())
    for t in TARGETS:
        print(crop(t), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
