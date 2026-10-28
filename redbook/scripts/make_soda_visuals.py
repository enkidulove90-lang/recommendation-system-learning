"""Create high-DPI, unmodified evidence views from the public SODA paper."""
from __future__ import annotations

from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "data" / "papers" / "2603.00700_soda.pdf"
METHOD = ROOT / "data" / "workflow_state" / "2603.00700" / "arxiv_source" / "figure" / "method.pdf"
OUT = ROOT / "data" / "parsed" / "2603.00700_soda" / "editorial_visuals"


def render(document_path: Path, destination: str, page_no: int, crop: tuple[float, float, float, float]) -> None:
    document = fitz.open(document_path)
    try:
        page = document[page_no]
        rect = page.rect
        left, top, right, bottom = crop
        clip = fitz.Rect(rect.width * left, rect.height * top, rect.width * right, rect.height * bottom)
        page.get_pixmap(matrix=fitz.Matrix(5, 5), clip=clip, alpha=False).save(OUT / destination)
    finally:
        document.close()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Figure 1 is the author-supplied method diagram.  The two detail views
    # retain the original diagram without editorial redraws.
    render(METHOD, "architecture_overview.png", 0, (0.0, 0.0, 1.0, 1.0))
    render(METHOD, "architecture_tokenizer.png", 0, (0.0, 0.0, 0.53, 1.0))
    render(METHOD, "architecture_alignment.png", 0, (0.45, 0.0, 1.0, 1.0))
    # These remain verbatim high-DPI crops from the published paper tables.
    render(PAPER, "table1_datasets.png", 2, (0.05, 0.07, 0.95, 0.31))
    render(PAPER, "table2_performance.png", 3, (0.05, 0.06, 0.95, 0.55))
    render(PAPER, "table3_ablation.png", 3, (0.05, 0.47, 0.95, 0.78))


if __name__ == "__main__":
    main()
