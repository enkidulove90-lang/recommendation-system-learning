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

    # ── note spec 编排：复用上面同一套 checkpoint 状态机，不另建编排层 ──
    def _xhs_publisher(self):
        from redbook.automation.publishing import XhsPublisher
        return XhsPublisher(self.data_root)

    def build_note_package(self, paper_id: str, *, notes_dir: Path | None = None,
                           repo_root: Path | None = None):
        """读 redbook/notes/<paper_id>.yaml，产出唯一一份 PublicationPackage。

        人工定稿正文经 render_post 的 body 分支进入，跳过 persona 模板；
        出口仍是 XhsPublisher，与旧脚本完全一致。
        """
        from redbook.services.note_spec import REPO_ROOT, load_note
        from redbook.services.render_post import render_package, render_post

        root = Path(repo_root) if repo_root else REPO_ROOT
        spec = load_note(paper_id, notes_dir)
        post = render_post("xhs", **spec.as_post_kwargs(root))
        package = render_package(
            post, canonical_url=spec.canonical_url, links=spec.links,
            pdf_path=spec.resolved_pdf_path(root), review_status=spec.review_status,
        )
        return spec, package

    def validate_note(self, paper_id: str, *, notes_dir: Path | None = None,
                      repo_root: Path | None = None) -> dict[str, Any]:
        """只跑内容闸门，不检查图片文件（另一台机器 clone 后天然没有图）。"""
        from redbook.services.note_spec import NoteSpecError
        from redbook.services.xhs_content_gate import ContentSpecError

        try:
            spec, package = self.build_note_package(paper_id, notes_dir=notes_dir, repo_root=repo_root)
        except (ContentSpecError, NoteSpecError) as error:
            return {"ok": False, "paper_id": paper_id, "errors": [str(error)]}
        errors = self._xhs_publisher().validate(package)
        return {
            "ok": not errors, "paper_id": paper_id, "title": package.title,
            "body_chars": len(package.body_markdown), "figures": len(package.image_paths),
            "status": spec.status, "errors": errors,
        }

    def stage_note(self, paper_id: str, *, notes_dir: Path | None = None,
                   repo_root: Path | None = None, require_files: bool = True) -> dict[str, Any]:
        """落盘不可变 review 包；成功后把 checkpoint 推进到 PACKAGED。"""
        from redbook.services.note_spec import NoteSpecError
        from redbook.services.xhs_content_gate import ContentSpecError

        try:
            spec, package = self.build_note_package(paper_id, notes_dir=notes_dir, repo_root=repo_root)
        except (ContentSpecError, NoteSpecError) as error:
            return {"ok": False, "paper_id": paper_id, "errors": [str(error)]}
        # 历史已发布稿只作归档，回溯目检标记不能让它们被误重发。
        if spec.status == "published":
            return {"ok": False, "paper_id": paper_id, "errors": [
                "published note is archived; set status to 'validated' and record a fresh "
                "per-image visual review before staging again"
            ]}
        if require_files:
            missing = [path for path in package.image_paths if not Path(path).is_file()]
            pdf = str(package.metadata.get("pdf_path", ""))
            if pdf and not Path(pdf).is_file():
                missing.append(pdf)
            if missing:
                return {"ok": False, "paper_id": paper_id,
                        "errors": [f"missing asset: {path}" for path in missing]}
        publisher = self._xhs_publisher()
        errors = publisher.validate(package)
        if errors:
            return {"ok": False, "paper_id": paper_id, "errors": errors}
        receipt = publisher.stage(package)
        if receipt.get("ok"):
            self._advance(self.load(paper_id), WorkflowStage.PACKAGED,
                          note_spec=str(spec.path), staged_id=str(receipt["staged_id"]))
        return receipt

    def publish_note(self, paper_id: str, *, notes_dir: Path | None = None,
                     repo_root: Path | None = None) -> dict[str, Any]:
        """先 stage 再投递草稿箱；成功后把 checkpoint 推进到 DRAFT_SAVED。"""
        staged = self.stage_note(paper_id, notes_dir=notes_dir, repo_root=repo_root)
        if not staged.get("ok"):
            return staged
        receipt = self._xhs_publisher().publish(str(staged["staged_id"]))
        if receipt.get("ok"):
            self._advance(self.load(paper_id), WorkflowStage.DRAFT_SAVED,
                          draft_id=str(receipt.get("draft_id", "")))
        return receipt
