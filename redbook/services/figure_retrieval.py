"""High-DPI PDF extraction plus deterministic and multimodal figure ranking."""
from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import re
from typing import Iterable

import fitz
from PIL import Image, ImageStat

from redbook.domain.media import FigureCandidate, VisionReview
from redbook.infrastructure.modelscope_vision import ModelScopeVisionReviewer


CAPTION = re.compile(r"(?:Figure|Fig\.)\s*(\d+[\w.-]*)\s*[:.]?\s*(.+)", re.IGNORECASE)
IMAGE = re.compile(r"!\[.*?\]\(([^)]+)\)")
PDF_CAPTION = re.compile(r"(?:Figure|Fig\.)\s*(\d+[\w.-]*)\s*[:.]?\s*([^\n]+)", re.IGNORECASE)


def _role(caption: str, section: str) -> str:
    value = f"{caption} {section}".casefold()
    if any(word in value for word in ("overview", "framework", "architecture", "pipeline", "training", "unifies")):
        return "architecture"
    if any(word in value for word in ("main results", "results", "benchmark", "evaluation", "comparison", "ablation", "fidelity progress")):
        return "results"
    if any(word in value for word in ("case study", "case", "example", "analysis", "representative", "task")):
        return "case"
    return "other"


class MineruCaptionIndex:
    """Attach a caption to all image fragments preceding the same MinerU caption."""

    @staticmethod
    def build(markdown_path: Path) -> dict[str, dict[str, str]]:
        current_section = ""
        pending: list[str] = []
        metadata: dict[str, dict[str, str]] = {}
        for line in markdown_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                current_section = line.lstrip("# ").strip()
            image = IMAGE.search(line)
            if image:
                pending.append(Path(image.group(1)).name)
                continue
            caption = CAPTION.search(line)
            if not caption or not pending:
                continue
            value = {"figure_id": f"Figure {caption.group(1)}", "caption": caption.group(2).strip(), "section": current_section}
            for name in pending:
                metadata[name] = value
            pending = []
        return metadata


class PdfCaptionIndex:
    """Recover the paper's figure identifier and caption from rendered PDF pages."""

    @staticmethod
    def build(pdf_path: Path) -> dict[int, dict[str, str]]:
        captions: dict[int, dict[str, str]] = {}
        document = fitz.open(pdf_path)
        try:
            for page_number, page in enumerate(document, 1):
                match = PDF_CAPTION.search(page.get_text("text"))
                if not match:
                    continue
                captions[page_number] = {
                    "figure_id": f"Figure {match.group(1)}",
                    "caption": match.group(2).strip(),
                }
        finally:
            document.close()
        return captions


class HighDpiPdfFigureExtractor:
    """Use MinerU layout bboxes to rerender figure/chart regions directly from the PDF."""

    def extract(self, pdf_path: Path, layout_path: Path, output_dir: Path, dpi: int = 288) -> list[Path]:
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        pages = layout.get("pdf_info", [])
        scale = dpi / 72
        output_dir.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []
        manifest: list[dict[str, object]] = []
        captions = PdfCaptionIndex.build(pdf_path)
        document = fitz.open(pdf_path)
        try:
            for page_index, page_info in enumerate(pages):
                page = document[page_index]
                for block in page_info.get("preproc_blocks", []):
                    if block.get("type") not in {"image", "chart"}:
                        continue
                    left, top, right, bottom = block.get("bbox", [0, 0, 0, 0])
                    if right <= left or bottom <= top:
                        continue
                    # MinerU boxes are in a 600-ish rendered coordinate system.
                    width_scale = page.rect.width / 600
                    height_scale = page.rect.height / 840
                    clip = fitz.Rect(left * width_scale, top * height_scale, right * width_scale, bottom * height_scale)
                    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
                    target = output_dir / f"p{page_index + 1:02d}_{block.get('type')}_{block.get('index', 0):02d}.png"
                    pixmap.save(target)
                    created.append(target)
                    page_number = page_index + 1
                    manifest.append({
                        "path": target.name,
                        "page": page_number,
                        "block_type": block.get("type"),
                        "bbox": [left, top, right, bottom],
                        **captions.get(page_number, {}),
                    })
        finally:
            document.close()
        (output_dir / "figure_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return created


class FigureQualityGate:
    """Reject weak source figures before an optional Qwen multimodal final review."""

    def __init__(self, min_pixels: int = 650_000, min_short_edge: int = 480) -> None:
        self.min_pixels, self.min_short_edge = min_pixels, min_short_edge

    @staticmethod
    def _sharpness_proxy(image: Image.Image) -> float:
        gray = image.convert("L").resize((96, 96))
        stat = ImageStat.Stat(gray)
        return min(1.0, stat.var[0] / 1400.0)

    def candidate(self, path: Path, order: int, metadata: dict[str, object] | None = None, source: str = "mineru") -> FigureCandidate:
        metadata = metadata or {}
        with Image.open(path) as image:
            width, height = image.size
            sharpness = self._sharpness_proxy(image)
        pixels = width * height
        short_edge = min(width, height)
        aspect = max(width, height) / max(short_edge, 1)
        eligible = pixels >= self.min_pixels and short_edge >= self.min_short_edge and aspect <= 3.2
        reason = "" if eligible else (
            f"needs high-DPI rerender: pixels={pixels}, short_edge={short_edge}, aspect={aspect:.2f}"
        )
        caption = str(metadata.get("caption", ""))
        section = str(metadata.get("section", ""))
        role = _role(caption, section)
        role_score = {"architecture": 0.20, "results": 0.17, "case": 0.14, "other": 0.05}[role]
        structural_score = min(0.55, pixels / 3_000_000 * 0.55) + min(0.25, short_edge / 1200 * 0.25) + sharpness * 0.20 + role_score
        return FigureCandidate(
            path=str(path), source=source, order=order, width=width, height=height, bytes=path.stat().st_size,
            page=int(metadata["page"]) if metadata.get("page") is not None else None,
            figure_id=str(metadata.get("figure_id", "")), caption=caption, section=section,
            role=role, structural_score=round(min(1.0, structural_score), 4), eligible=eligible, rejection_reason=reason,
        )

    def rank(self, candidates: Iterable[FigureCandidate], reviews: dict[str, VisionReview] | None = None, limit: int = 4) -> list[FigureCandidate]:
        reviews = reviews or {}
        scored: list[tuple[float, FigureCandidate]] = []
        for candidate in sorted(candidates, key=lambda value: value.order):
            if not candidate.eligible:
                continue
            review = reviews.get(candidate.path)
            if review and review.verdict != "keep":
                continue
            score = candidate.structural_score * 0.55 + (review.score * 0.45 if review else 0.25)
            scored.append((score, candidate))
        def editorial_order(pair: tuple[float, FigureCandidate]) -> tuple[float, int, int]:
            figure = re.search(r"(\d+)", pair[1].figure_id)
            # When scores tie, a paper's earlier overview figure is generally
            # the clearest editorial opener, rather than an alphabetically
            # earlier source filename.
            figure_number = int(figure.group(1)) if figure else 10_000
            return pair[0], -figure_number, -pair[1].order

        ranked = sorted(scored, key=editorial_order, reverse=True)
        chosen: list[FigureCandidate] = []
        # The post sequence must explain the paper, not merely display its four
        # largest assets: architecture -> evidence/results -> concrete case.
        for role in ("architecture", "results", "case"):
            match = next((candidate for _, candidate in ranked if candidate.role == role), None)
            if match and match not in chosen:
                chosen.append(match)
        for _, candidate in ranked:
            if candidate not in chosen:
                chosen.append(candidate)
            if len(chosen) >= limit:
                break
        return chosen[:limit]


class FigureRetrievalService:
    """One service owns captioning, high-DPI fallback, deterministic ranking and Qwen review."""

    def __init__(self, gate: FigureQualityGate | None = None, reviewer: ModelScopeVisionReviewer | None = None) -> None:
        self.gate = gate or FigureQualityGate()
        self.reviewer = reviewer

    @staticmethod
    def _manifest_metadata(image_dir: Path) -> dict[str, dict[str, object]]:
        manifest_path = image_dir / "figure_manifest.json"
        if not manifest_path.is_file():
            return {}
        try:
            rows = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return {
            Path(str(row["path"])).name: dict(row)
            for row in rows if isinstance(row, dict) and row.get("path")
        }

    def select(self, markdown_path: Path, image_dir: Path, limit: int = 4, use_vision: bool = False,
               source: str = "mineru") -> tuple[list[FigureCandidate], list[FigureCandidate], dict[str, VisionReview]]:
        metadata = MineruCaptionIndex.build(markdown_path)
        manifest_metadata = self._manifest_metadata(image_dir)
        candidates = [
            self.gate.candidate(path, order, {**metadata.get(path.name, {}), **manifest_metadata.get(path.name, {})}, source)
            for order, path in enumerate(sorted(image_dir.glob("*")), 1)
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ]
        eligible = [candidate for candidate in candidates if candidate.eligible]
        reviews = self.reviewer.review(eligible) if use_vision and self.reviewer and self.reviewer.is_ready else {}
        return self.gate.rank(candidates, reviews, limit), candidates, reviews
