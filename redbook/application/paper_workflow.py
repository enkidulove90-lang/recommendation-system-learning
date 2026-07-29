"""Resumable paper-to-draft orchestration with explicit states and human gates."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from redbook.domain.media import WorkflowCheckpoint, WorkflowStage
from redbook.services.arxiv_source import ArxivSourceImageExtractor
from redbook.services.figure_retrieval import FigureRetrievalService, HighDpiPdfFigureExtractor
from redbook.automation.common import read_json, write_json


class PaperCreationWorkflow:
    def __init__(self, data_root: Path, figures: FigureRetrievalService | None = None) -> None:
        self.data_root = data_root
        self.figures = figures or FigureRetrievalService()

    def _checkpoint_path(self, paper_id: str) -> Path:
        return self.data_root / "workflow_state" / paper_id / "checkpoint.json"

    def load(self, paper_id: str) -> WorkflowCheckpoint:
        value = read_json(self._checkpoint_path(paper_id), {})
        return WorkflowCheckpoint.from_dict(value) if value else WorkflowCheckpoint(paper_id=paper_id)

    def _advance(self, checkpoint: WorkflowCheckpoint, stage: WorkflowStage, **artifacts: Any) -> WorkflowCheckpoint:
        order = list(WorkflowStage)
        if order.index(stage) < order.index(checkpoint.stage) and stage != WorkflowStage.BLOCKED:
            raise ValueError(f"Cannot move workflow backward: {checkpoint.stage} -> {stage}")
        checkpoint.stage = stage
        checkpoint.artifacts.update(artifacts)
        checkpoint.history.append({"stage": stage.value, "at": datetime.now(timezone.utc).isoformat(), "artifacts": sorted(artifacts)})
        write_json(self._checkpoint_path(checkpoint.paper_id), checkpoint.as_dict())
        return checkpoint

    def prepare_figures(self, paper_id: str, markdown_path: Path, image_dir: Path, pdf_path: Path | None = None,
                        layout_path: Path | None = None, use_vision: bool = False, arxiv_id: str | None = None) -> WorkflowCheckpoint:
        checkpoint = self.load(paper_id)
        selected = []
        candidates = []
        reviews = {}
        source_artifact: dict[str, Any] = {}

        # Priority 1: original author assets from the arXiv LaTeX source package.
        if arxiv_id:
            try:
                source_result = ArxivSourceImageExtractor().fetch(arxiv_id, image_dir.parent / "arxiv_source")
                source_artifact = source_result.as_dict()
                if source_result.images:
                    source_selected, source_candidates, source_reviews = self.figures.select(
                        markdown_path, Path(source_result.images[0]).parent, use_vision=use_vision, source="arxiv_latex"
                    )
                    selected.extend(source_selected)
                    candidates.extend(source_candidates)
                    reviews.update(source_reviews)
            except Exception as error:  # PDF fallback must keep a draft workflow resumable.
                source_artifact = {"arxiv_id": arxiv_id, "error": str(error)[:300]}

        # Priority 2: rerender MinerU-detected regions straight from the paper PDF.
        if len(selected) < 4 and pdf_path and layout_path:
            hd_dir = image_dir.parent / "images_hd"
            if not (hd_dir / "figure_manifest.json").is_file():
                HighDpiPdfFigureExtractor().extract(pdf_path, layout_path, hd_dir)
            fallback_selected, fallback_candidates, fallback_reviews = self.figures.select(
                markdown_path, hd_dir, limit=4 - len(selected), use_vision=use_vision, source="pdf_high_dpi"
            )
            selected.extend(fallback_selected)
            candidates.extend(fallback_candidates)
            reviews.update(fallback_reviews)
            source_dir = hd_dir
        elif selected:
            source_dir = Path(selected[0].path).parent
        else:
            # Last-resort compatibility path for older MinerU-only runs.
            selected, candidates, reviews = self.figures.select(markdown_path, image_dir, use_vision=use_vision, source="mineru")
            source_dir = image_dir
        if not selected:
            return self._advance(checkpoint, WorkflowStage.BLOCKED, figure_error="No figure passed quality gate", candidate_count=len(candidates))
        vision_error = ""
        if self.figures.reviewer:
            vision_error = self.figures.reviewer.last_error
        return self._advance(
            checkpoint, WorkflowStage.FIGURES_READY,
            figure_source=str(source_dir), arxiv_source=source_artifact,
            selected_figures=[candidate.as_dict() for candidate in selected],
            rejected_figures=[candidate.as_dict() for candidate in candidates if not candidate.eligible],
            vision_reviews={path: asdict(review) for path, review in reviews.items()},
            vision_warning=vision_error,
        )
