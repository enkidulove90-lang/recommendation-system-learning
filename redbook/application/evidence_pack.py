"""Parse an auditable, open-access evidence pack into a separate data bundle."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from skills.pdf_parser import PDFParser


class EvidencePackParser:
    def __init__(self, data_root: Path = Path("data"), parser: PDFParser | None = None) -> None:
        self.data_root = data_root
        self.parser = parser or PDFParser()

    def parse(self, manifest_path: Path) -> dict[str, Any]:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        pack_id = str(manifest["id"])
        root = self.data_root / "evidence" / pack_id
        parsed_root = root / "parsed"
        root.mkdir(parents=True, exist_ok=True)
        reports: list[dict[str, Any]] = []
        if not self.parser.is_ready:
            raise RuntimeError("MINERU_API_KEY is not configured")
        for paper in manifest.get("papers", []):
            paper_id = str(paper["id"])
            output_dir = parsed_root / paper_id
            markdown_path = output_dir / f"{paper_id}.md"
            existing_markdown = markdown_path if markdown_path.is_file() else next(iter(sorted(output_dir.glob("*.md"))), None)
            if existing_markdown:
                reports.append({**paper, "markdown_path": str(existing_markdown), "status": "cached"})
                continue
            result = self.parser.execute(
                pdf_url=str(paper["pdf_url"]), arxiv_id=paper_id,
                title=str(paper.get("title", "")), output_dir=str(output_dir),
            )
            reports.append({
                **paper, "status": "parsed" if result.get("markdown_path") else "failed",
                "markdown_path": result.get("markdown_path"), "json_path": result.get("json_path"), "error": result.get("error"),
            })
        report = {"pack_id": pack_id, "manifest": str(manifest_path), "papers": reports}
        (root / "parse_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report
