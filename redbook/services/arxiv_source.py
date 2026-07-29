"""Source-first, high-fidelity figure acquisition for arXiv papers.

The original LaTeX source is preferred because it contains the author supplied
assets.  A PDF crop is only a fallback and is intentionally owned by the
workflow, not by ad-hoc scripts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
from typing import Iterable

import fitz
import httpx


RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VECTOR_EXTENSIONS = {".pdf", ".eps", ".svg"}
PREFERRED_DIRECTORIES = {"pics", "figures", "figure", "fig", "images", "image", "img"}
FIGURE_ENV = re.compile(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", re.DOTALL)
INCLUDE_GRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


@dataclass(frozen=True)
class SourceImageResult:
    images: list[str]
    source_root: str
    manifest_path: str
    tikz_detected: bool
    warnings: list[str]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class ArxivSourceImageExtractor:
    """Download an arXiv e-print safely and normalize its reusable figures."""

    def __init__(self, timeout: float = 45.0) -> None:
        self.timeout = timeout

    @staticmethod
    def _safe_members(archive: tarfile.TarFile) -> Iterable[tarfile.TarInfo]:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                continue
            yield member

    def download_and_extract(self, arxiv_id: str, destination: Path) -> Path:
        url = f"https://arxiv.org/e-print/{arxiv_id}"
        with httpx.Client(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": "redbook-paper-workflow/1.0"}) as client:
            response = client.get(url)
            response.raise_for_status()
        root = destination / "source"
        root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=BytesIO(response.content), mode="r:*") as archive:
            archive.extractall(root, members=self._safe_members(archive), filter="data")
        return root

    @staticmethod
    def _is_preferred(path: Path) -> bool:
        return any(part.casefold() in PREFERRED_DIRECTORIES for part in path.parts[:-1])

    @staticmethod
    def _has_tikz(source_root: Path) -> bool:
        for tex_path in source_root.rglob("*.tex"):
            try:
                if "\\begin{tikzpicture}" in tex_path.read_text(encoding="utf-8", errors="ignore"):
                    return True
            except OSError:
                continue
        return False

    @staticmethod
    def _command_argument(text: str, command: str) -> str:
        """Read a balanced TeX command argument (captions commonly nest braces)."""
        match = re.search(rf"\\{command}(?:\[[^\]]*\])?\{{", text)
        if not match:
            return ""
        start = match.end()
        depth = 1
        for offset, char in enumerate(text[start:], start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start:offset]
        return ""

    @staticmethod
    def _latex_caption_metadata(source_root: Path) -> dict[str, dict[str, str]]:
        """Map source asset stems to the author-written figure caption."""
        metadata: dict[str, dict[str, str]] = {}
        figure_number = 0
        for tex_path in source_root.rglob("*.tex"):
            text = tex_path.read_text(encoding="utf-8", errors="ignore")
            for environment in FIGURE_ENV.finditer(text):
                body = environment.group(1)
                caption = ArxivSourceImageExtractor._command_argument(body, "caption")
                images = INCLUDE_GRAPHICS.findall(body)
                if not caption or not images:
                    continue
                figure_number += 1
                caption_text = " ".join(caption.replace("~", " ").split())
                for image in images:
                    metadata[Path(image).stem] = {
                        "figure_id": f"Figure {figure_number}", "caption": caption_text,
                    }
        return metadata

    @staticmethod
    def _dedupe_name(path: Path, output_dir: Path) -> Path:
        digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:8]
        return output_dir / f"{path.stem}_{digest}{path.suffix.lower()}"

    @staticmethod
    def _render_vector_pdf(path: Path, target: Path) -> bool:
        try:
            document = fitz.open(path)
            try:
                if not document.page_count:
                    return False
                document[0].get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False).save(target)
                return True
            finally:
                document.close()
        except (fitz.FileDataError, RuntimeError, OSError):
            return False

    def collect(self, source_root: Path, output_dir: Path) -> SourceImageResult:
        """Collect local source assets; public for offline tests and cache reuse."""
        output_dir.mkdir(parents=True, exist_ok=True)
        selected: list[tuple[Path, bool, dict[str, str]]] = []
        warnings: list[str] = []
        caption_metadata = self._latex_caption_metadata(source_root)
        all_assets = [path for path in source_root.rglob("*") if path.is_file() and path.suffix.lower() in RASTER_EXTENSIONS | VECTOR_EXTENSIONS]
        ordered = sorted(all_assets, key=lambda path: (not self._is_preferred(path.relative_to(source_root)), str(path)))
        for path in ordered:
            preferred = self._is_preferred(path.relative_to(source_root))
            target = self._dedupe_name(path.relative_to(source_root), output_dir)
            suffix = path.suffix.lower()
            if suffix in RASTER_EXTENSIONS:
                shutil.copy2(path, target)
                selected.append((target, preferred, caption_metadata.get(path.stem, {})))
            elif suffix == ".pdf":
                rendered = target.with_suffix(".png")
                if self._render_vector_pdf(path, rendered):
                    selected.append((rendered, preferred, caption_metadata.get(path.stem, {})))
                else:
                    warnings.append(f"Could not render vector PDF: {path.name}")
            else:
                warnings.append(f"Vector asset needs external conversion and was skipped: {path.name}")
        manifest = output_dir / "figure_manifest.json"
        manifest.write_text(json.dumps([
            {"path": path.name, "source_asset": "arxiv_latex", "preferred_directory": preferred, **metadata}
            for path, preferred, metadata in selected
        ], ensure_ascii=False, indent=2), encoding="utf-8")
        return SourceImageResult(
            images=[str(path) for path, _, _ in selected], source_root=str(source_root), manifest_path=str(manifest),
            tikz_detected=self._has_tikz(source_root), warnings=warnings,
        )

    def fetch(self, arxiv_id: str, output_dir: Path) -> SourceImageResult:
        source_root = output_dir / "source"
        # The source package is immutable for a specific arXiv version in a
        # single workflow run. Reuse it so retries, vision rechecks and draft
        # rebuilds do not repeatedly hit arXiv.
        if not source_root.is_dir() or not any(source_root.rglob("*")):
            source_root = self.download_and_extract(arxiv_id, output_dir)
        return self.collect(source_root, output_dir / "images_source")
