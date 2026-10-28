"""Render the public tau-Rec paper pages for evidence-asset inspection."""
from __future__ import annotations

from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "data" / "papers" / "2606.10156_tau_rec.pdf"
OUT = ROOT / "data" / "parsed" / "2606.10156_tau_rec" / "page_renders"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    document = fitz.open(PDF)
    try:
        for number, page in enumerate(document, 1):
            page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(OUT / f"page_{number:02d}.png")
    finally:
        document.close()


if __name__ == "__main__":
    main()
