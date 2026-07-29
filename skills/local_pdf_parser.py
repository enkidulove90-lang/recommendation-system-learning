"""
skills/local_pdf_parser.py — local PDF text fallback parser.

MinerU remains the preferred structured parser. This skill is a lightweight
fallback used when MinerU is not configured or when the user needs a fast local
text extraction pass for downloaded arXiv PDFs.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill
from storage.paper_assets import normalize_arxiv_id, resolve_paper_bundle

logger = logging.getLogger(__name__)


@register_skill("pdf-parse-local")
class LocalPDFParser(BaseSkill):
    """Extract plain text from a local PDF and save it as Markdown."""

    @property
    def is_ready(self) -> bool:
        try:
            import pypdf  # noqa: F401
        except Exception:
            return False
        return True

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        arxiv_id = normalize_arxiv_id(str(kwargs.get("arxiv_id", "")).strip())
        pdf_path_raw = str(kwargs.get("pdf_path", "")).strip()
        pdf_path = Path(pdf_path_raw).expanduser() if pdf_path_raw else None
        title = str(kwargs.get("title", "")).strip()
        output_dir = str(kwargs.get("output_dir", ""))

        if not arxiv_id:
            return self._error("", "arxiv_id is required.")
        if not pdf_path:
            pdf_path = settings.DATA_DIR / "papers" / f"{arxiv_id}.pdf"
        if not pdf_path.exists():
            return self._error(arxiv_id, f"PDF not found: {pdf_path}")
        if not self.is_ready:
            return self._error(arxiv_id, "pypdf is not installed.")

        if output_dir:
            out_dir = Path(output_dir)
        else:
            out_dir = resolve_paper_bundle(arxiv_id, title=title, create=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        md_path = out_dir / f"{arxiv_id}.md"
        bundled_pdf_path = out_dir / f"{arxiv_id}.pdf"

        try:
            if pdf_path.resolve() != bundled_pdf_path.resolve() and not bundled_pdf_path.exists():
                shutil.copy2(pdf_path, bundled_pdf_path)

            from pypdf import PdfReader

            reader = PdfReader(str(pdf_path))
            page_count = len(reader.pages)
            chunks: list[str] = [
                f"# {arxiv_id}",
                "",
                f"**Source PDF**: {pdf_path}",
                f"**Parser**: local pypdf fallback",
                f"**Pages**: {page_count}",
                "",
            ]
            total_chars = 0
            for index, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                text = text.strip()
                if not text:
                    continue
                total_chars += len(text)
                chunks.extend([
                    f"## Page {index}",
                    "",
                    text,
                    "",
                ])

            md_path.write_text("\n".join(chunks), encoding="utf-8")
            logger.info(
                "[Local PDF Parse] Parsed %s | pages=%d chars=%d -> %s",
                arxiv_id,
                page_count,
                total_chars,
                md_path,
            )
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "markdown_path": str(md_path),
                "pdf_path": str(bundled_pdf_path),
                "json_path": None,
                "content": {"text": "\n".join(chunks), "page_count": page_count},
                "error": None,
            }
        except Exception as exc:
            logger.error("[Local PDF Parse] Error for %s: %s", arxiv_id, exc)
            return self._error(arxiv_id, str(exc))

    @staticmethod
    def _error(arxiv_id: str, message: str) -> dict[str, Any]:
        return {
            "ready": False,
            "arxiv_id": arxiv_id,
            "markdown_path": None,
            "pdf_path": None,
            "json_path": None,
            "content": None,
            "error": message,
        }
