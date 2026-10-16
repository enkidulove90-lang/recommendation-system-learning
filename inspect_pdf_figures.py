# -*- coding: utf-8 -*-
"""检查 PDF 的图与图注分布（用于挑小红书配图）。

输出写到图注/图片清单文件（UTF-8），避免控制台编码问题。
用法：python inspect_pdf_figures.py <pdf> [输出txt]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz


def main() -> int:
    pdf = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("pdf_figures_report.txt")
    doc = fitz.open(pdf)
    lines: list[str] = []
    lines.append(f"PDF: {pdf}")
    lines.append(f"pages: {doc.page_count}")
    lines.append("")

    lines.append("=== 每页嵌入位图（xref, w x h, 颜色空间, 压缩后大小） ===")
    for i, page in enumerate(doc):
        imgs = page.get_images(full=True)
        if not imgs:
            continue
        lines.append(f"p{i + 1}:")
        for im in imgs:
            xref = im[0]
            w, h = im[2], im[3]
            cs = im[5]
            try:
                raw = doc.extract_image(xref)
                size = len(raw["image"])
                ext = raw["ext"]
            except Exception:
                size, ext = -1, "?"
            draw = page.get_image_rects(xref)
            area = ""
            if draw:
                r = draw[0]
                area = f" 占页 {r.width:.0f}x{r.height:.0f}pt"
            lines.append(f"   xref={xref} {w}x{h} {cs} {ext} {size // 1024}KB{area}")

    lines.append("")
    lines.append("=== 图注（Figure N / Table N 所在页） ===")
    fig_re = re.compile(r"\b(Figure|Fig\.)\s*(\d{1,2})\b", re.I)
    tab_re = re.compile(r"\bTable\s*(\d{1,2})\b", re.I)
    for i, page in enumerate(doc):
        text = page.get_text()
        for m in fig_re.finditer(text):
            seg = " ".join(text[m.start(): m.start() + 320].split())
            lines.append(f"p{i + 1} FIG {m.group(2)}: {seg[:300]}")
        for m in tab_re.finditer(text):
            seg = " ".join(text[m.start(): m.start() + 240].split())
            lines.append(f"p{i + 1} TAB {m.group(1)}: {seg[:220]}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("pages:", doc.page_count, "-> written", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
