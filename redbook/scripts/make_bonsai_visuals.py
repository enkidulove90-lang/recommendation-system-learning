"""Render BONSAI's author-provided vector figures as high-DPI editorial images."""
from __future__ import annotations

import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "workflow_state" / "2607.16633" / "arxiv_source" / "figs"
OUTPUT = ROOT / "data" / "parsed" / "2607.16633_bonsai" / "editorial_visuals"


def render(source_name: str, target_name: str, clip: fitz.Rect | None = None) -> dict[str, object]:
    document = fitz.open(SOURCE / source_name)
    try:
        page = document[0]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(5, 5), clip=clip, alpha=False)
        target = OUTPUT / target_name
        pixmap.save(target)
        return {"path": str(target), "source": source_name, "width": pixmap.width, "height": pixmap.height}
    finally:
        document.close()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    architecture = fitz.open(SOURCE / "BONSAI_frame.pdf")
    try:
        rect = architecture[0].rect
    finally:
        architecture.close()
    # The overview is retained whole; the two crops make the four-stage pipeline
    # legible in a phone carousel without redrawing or altering the source figure.
    visuals = [
        render("BONSAI_frame.pdf", "01_architecture_overview.png"),
        render("BONSAI_frame.pdf", "02_architecture_filter_and_trie.png", fitz.Rect(rect.x0, rect.y0, rect.x0 + rect.width * 0.52, rect.y1)),
        render("BONSAI_frame.pdf", "03_architecture_llm_and_rl.png", fitz.Rect(rect.x0 + rect.width * 0.48, rect.y0, rect.x1, rect.y1)),
        render("impr_bar.pdf", "04_main_results.png"),
        render("ablation_branch.pdf", "05_branching_ablation.png"),
        render("ablation_depth.pdf", "06_depth_ablation.png"),
    ]
    (OUTPUT / "visual_manifest.json").write_text(
        json.dumps(visuals, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(visuals, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
