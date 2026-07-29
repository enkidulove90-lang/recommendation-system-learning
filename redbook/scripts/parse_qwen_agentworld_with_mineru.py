"""Parse the official Qwen-AgentWorld arXiv PDF with the configured MinerU API.

This is deliberately a one-paper entry point so the source URL, paper identity,
and output directory are auditable beside the resulting figures and Markdown.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.pdf_parser import PDFParser


PAPER = {
    "arxiv_id": "2606.24597",
    "title": "Qwen-AgentWorld: Language World Models for General Agents",
    "pdf_url": "https://arxiv.org/pdf/2606.24597",
    "paper_url": "https://arxiv.org/abs/2606.24597",
    "github_url": "https://github.com/QwenLM/Qwen-AgentWorld",
}
OUTPUT_DIR = ROOT / "data" / "parsed" / "2606.24597_qwen_agentworld"


def main() -> None:
    parser = PDFParser()
    if not parser.is_ready:
        raise SystemExit("MINERU_API_KEY is not configured in .env")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = parser.execute(
        pdf_url=PAPER["pdf_url"],
        arxiv_id=PAPER["arxiv_id"],
        title=PAPER["title"],
        output_dir=str(OUTPUT_DIR),
    )
    report = {**PAPER, **{key: result.get(key) for key in (
        "ready", "markdown_path", "json_path", "text_length", "error",
    )}}
    (OUTPUT_DIR / "parse_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if result.get("error"):
        raise SystemExit(result["error"])


if __name__ == "__main__":
    main()
