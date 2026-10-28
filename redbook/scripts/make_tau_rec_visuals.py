"""Create high-DPI, unmodified evidence crops from the public tau-Rec PDF."""
from __future__ import annotations

from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "data" / "papers" / "2606.10156_tau_rec.pdf"
OUT = ROOT / "data" / "parsed" / "2606.10156_tau_rec" / "editorial_visuals"

# (filename, zero-based page number, normalized left, top, right, bottom)
CROPS = [
    ("table1_benchmark_capabilities.png", 1, 0.08, 0.08, 0.49, 0.36),
    ("table2_reliability.png", 3, 0.08, 0.10, 0.92, 0.35),
    ("table3_reveal_difficulty.png", 3, 0.13, 0.33, 0.92, 0.54),
    ("figure1_capability_latency.png", 3, 0.12, 0.43, 0.51, 0.75),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    document = fitz.open(PDF)
    try:
        for name, page_no, left, top, right, bottom in CROPS:
            page = document[page_no]
            rect = page.rect
            clip = fitz.Rect(rect.width * left, rect.height * top, rect.width * right, rect.height * bottom)
            page.get_pixmap(matrix=fitz.Matrix(5, 5), clip=clip, alpha=False).save(OUT / name)
    finally:
        document.close()


if __name__ == "__main__":
    main()
