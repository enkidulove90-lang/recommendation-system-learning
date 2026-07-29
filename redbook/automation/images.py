"""Chapter 6: figure manifests, conservative grouping, and uncropped Pillow composites."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable

from PIL import Image, ImageOps

from .common import append_jsonl, jaccard, normalize_text


CANVAS = (1440, 1920)
MARGIN, GAP = 48, 24


@dataclass(frozen=True)
class FigureAsset:
    path: str
    figure_id: str = ""
    caption: str = ""
    section: str = ""
    page: int | None = None
    source_order: int = 0
    width: int = 0
    height: int = 0
    sha256: str = ""
    is_table: bool = False
    is_equation_heavy: bool = False

    @property
    def readable(self) -> bool:
        return max(self.width, self.height) >= 1400 and not self.is_table and not self.is_equation_heavy


def build_manifest(paths: Iterable[Path], output: Path, metadata: dict[str, dict] | None = None) -> list[FigureAsset]:
    metadata = metadata or {}
    assets: list[FigureAsset] = []
    for order, path in enumerate(paths, 1):
        with Image.open(path) as image:
            width, height = image.size
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        extra = metadata.get(path.name, {})
        assets.append(FigureAsset(str(path), source_order=order, width=width, height=height, sha256=digest, **extra))
    append_jsonl(output, [asdict(asset) for asset in assets])
    return assets


def metadata_from_mineru_markdown(markdown_path: Path, images: Iterable[Path]) -> dict[str, dict]:
    """Associate MinerU image filenames with the nearest Figure caption and section heading."""
    text = markdown_path.read_text(encoding="utf-8")
    captions: dict[str, dict] = {}
    current_section = ""
    last_image = ""
    figure_pattern = re.compile(r"(?:Figure|Fig\.)\s*(\d+[\w.-]*)\s*[:.]?\s*(.+)", re.IGNORECASE)
    image_pattern = re.compile(r"!\[.*?\]\(([^)]+)\)")
    for line in text.splitlines():
        if line.startswith("#"):
            current_section = line.lstrip("# ").strip()
        image_match = image_pattern.search(line)
        if image_match:
            last_image = Path(image_match.group(1)).name
            continue
        caption_match = figure_pattern.search(line)
        if last_image and caption_match:
            captions[last_image] = {"figure_id": f"Figure {caption_match.group(1)}", "caption": caption_match.group(2).strip(), "section": current_section}
    by_name = {path.name: captions.get(path.name, {}) for path in images}
    return by_name


def _caption_link(left: FigureAsset, right: FigureAsset) -> float:
    return jaccard(set(normalize_text(left.caption).split()), set(normalize_text(right.caption).split()))


def group_figures(assets: list[FigureAsset], threshold: float = 0.80) -> list[list[FigureAsset]]:
    """Conservatively group only assets with explicit Figure/caption evidence."""
    unique: list[FigureAsset] = []
    hashes: set[str] = set()
    for asset in assets:
        if asset.sha256 in hashes or not asset.readable:
            continue
        hashes.add(asset.sha256)
        unique.append(asset)
    groups: list[list[FigureAsset]] = []
    used: set[str] = set()
    for asset in unique:
        if asset.path in used:
            continue
        group = [asset]
        for candidate in unique:
            if candidate.path in used or candidate.path == asset.path:
                continue
            same_figure = float(bool(asset.figure_id and asset.figure_id == candidate.figure_id))
            caption_link = _caption_link(asset, candidate)
            adjacent = float(asset.page is not None and candidate.page is not None and abs(asset.page - candidate.page) <= 1)
            score = 0.70 * same_figure + 0.20 * caption_link + 0.10 * adjacent
            if score >= threshold and len(group) < 4:
                group.append(candidate)
        for item in group:
            used.add(item.path)
        groups.append(sorted(group, key=lambda item: item.source_order))
    return groups


def _layout(count: int) -> tuple[list[tuple[int, int, int, int]], str]:
    width, height = CANVAS
    inner_w, inner_h = width - 2 * MARGIN, height - 2 * MARGIN
    if count == 2:
        cell_h = (inner_h - GAP) // 2
        return [(MARGIN, MARGIN, inner_w, cell_h), (MARGIN, MARGIN + cell_h + GAP, inner_w, cell_h)], "vertical"
    if count == 3:
        bottom_h = (inner_h * 2 // 5 - GAP) // 1
        top_h = inner_h - bottom_h - GAP
        bottom_w = (inner_w - GAP) // 2
        return [(MARGIN, MARGIN, inner_w, top_h), (MARGIN, MARGIN + top_h + GAP, bottom_w, bottom_h), (MARGIN + bottom_w + GAP, MARGIN + top_h + GAP, bottom_w, bottom_h)], "hero_plus_two"
    if count == 4:
        cell_w, cell_h = (inner_w - GAP) // 2, (inner_h - GAP) // 2
        return [(MARGIN + (index % 2) * (cell_w + GAP), MARGIN + (index // 2) * (cell_h + GAP), cell_w, cell_h) for index in range(4)], "grid_2x2"
    raise ValueError("only 2-4 figures may be composed")


def compose_group(group: list[FigureAsset], output: Path) -> dict[str, str | bool]:
    """Create an uncropped 3:4 composite or decline if source text would be too small."""
    if len(group) not in {2, 3, 4}:
        return {"composed": False, "reason": "group size must be 2-4"}
    cells, layout_name = _layout(len(group))
    images = [Image.open(asset.path).convert("RGB") for asset in group]
    try:
        for image, (_, _, cell_w, cell_h) in zip(images, cells):
            contained = ImageOps.contain(image, (cell_w, cell_h), Image.Resampling.LANCZOS)
            if min(contained.size) < 520:
                return {"composed": False, "reason": "panel would be unreadable"}
        canvas = Image.new("RGB", CANVAS, "white")
        for image, (x, y, cell_w, cell_h) in zip(images, cells):
            panel = ImageOps.contain(image, (cell_w, cell_h), Image.Resampling.LANCZOS)
            canvas.paste(panel, (x + (cell_w - panel.width) // 2, y + (cell_h - panel.height) // 2))
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output, quality=96, subsampling=0)
        return {"composed": True, "path": str(output), "layout": layout_name}
    finally:
        for image in images:
            image.close()


def load_manifest(path: Path) -> list[FigureAsset]:
    rows: list[FigureAsset] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(FigureAsset(**json.loads(line)))
    return rows
