"""Run the repository's MinerU parser for the four July-2026 draft papers."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.pdf_parser import PDFParser

OUTPUT_ROOT = ROOT / "data" / "parsed" / "mineru_july_2026"
PAPERS = [
    {
        "slug": "openai-gpt-red",
        "arxiv_id": "gpt-red",
        "title": "GPT-Red Automated Red Teaming via Self-Play at Scale",
        "pdf_url": "https://cdn.openai.com/pdf/gpt-red-automated-red-teaming-via-self-play-at-scale.pdf",
    },
    {
        "slug": "meta-ra-rft",
        "arxiv_id": "2606.13680",
        "title": "Learning to Reason by Analogy via Retrieval-Augmented Reinforcement Fine-Tuning",
        "pdf_url": "https://arxiv.org/pdf/2606.13680",
    },
    {
        "slug": "tencent-hils",
        "arxiv_id": "2607.02980",
        "title": "Hierarchical Sparse Attention Done Right Toward Infinite Context Modeling",
        "pdf_url": "https://arxiv.org/pdf/2607.02980",
    },
    {
        "slug": "mmeacr",
        "arxiv_id": "2607.07108",
        "title": "MMEACR Multimodal Memory Enhanced Agent Collaboration for Recommendation",
        "pdf_url": "https://arxiv.org/pdf/2607.07108",
    },
]


def main() -> None:
    parser = PDFParser()
    if not parser.is_ready:
        raise SystemExit("MINERU_API_KEY is not configured in .env")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    requested = set(sys.argv[1:])
    papers = [paper for paper in PAPERS if not requested or paper["slug"] in requested]
    if requested and not papers:
        raise SystemExit("No matching paper slug")
    report = []
    for paper in papers:
        print(f"Submitting MinerU parse: {paper['slug']}", flush=True)
        result = parser.execute(
            pdf_url=paper["pdf_url"],
            arxiv_id=paper["arxiv_id"],
            title=paper["title"],
            output_dir=str(OUTPUT_ROOT / paper["slug"]),
        )
        record = {
            "slug": paper["slug"],
            "ready": result.get("ready"),
            "markdown_path": result.get("markdown_path"),
            "json_path": result.get("json_path"),
            "error": result.get("error"),
        }
        report.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
    report_path = OUTPUT_ROOT / "parse_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if any(item["error"] for item in report):
        raise SystemExit("One or more MinerU parses failed")


if __name__ == "__main__":
    main()
