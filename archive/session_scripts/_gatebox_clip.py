# -*- coding: utf-8 -*-
"""Clip a figure by unioning drawings + text blocks in the band above its caption."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz

PDF = r"C:/Users/xu.yan1/Downloads/3773078.3831765.pdf"
doc = fitz.open(PDF)


def clip_by_caption(page, caption_prefix: str, out: str, zoom: float = 6, margin: float = 6) -> None:
    hits = page.search_for(caption_prefix)
    if not hits:
        raise SystemExit(f"caption not found: {caption_prefix}")
    cap = hits[0]
    # band: from the text block above the caption (exclusive) down to caption top
    band_top = 72.0  # below running head
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
        if y1 < cap.y0 - 1 and y0 > 72 and not text.startswith("Figure"):
            band_top = max(band_top, y1) if False else band_top  # keep simple: use drawings only below
    rects = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.y1 <= cap.y0 + 1 and r.y0 >= 60:
            rects.append(r)
    if not rects:
        raise SystemExit("no drawings in band")
    union = rects[0]
    for r in rects[1:]:
        union |= r
    # include text blocks that intersect the drawing band (axis labels, legends)
    for b in page.get_text("blocks"):
        r = fitz.Rect(b[:4])
        if r.y1 <= cap.y0 + 1 and r.y0 >= 60 and r.intersects(union + (-20, -20, 20, 20)):
            union |= r
    union = union + (-margin, -margin, margin, margin)
    pix = page.get_pixmap(clip=union, matrix=fitz.Matrix(zoom, zoom))
    pix.save(out)
    print(f"p{page.number + 1} {caption_prefix[:20]!r} clip={union.width:.0f}x{union.height:.0f}pt -> {pix.width}x{pix.height}px -> {out}")


clip_by_caption(doc[4], "Figure 4: Box Preference", "data/parsed/gateboxgcn/images/fig4_scoring.png")
clip_by_caption(doc[7], "Figure 5: Effect of the Number", "data/parsed/gateboxgcn/images/fig5_layers.png")
