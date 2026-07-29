"""Recover completed MinerU archives via the parser's curl fallback."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.pdf_parser import PDFParser


OUTPUT_ROOT = ROOT / "data" / "parsed" / "mineru_july_2026"
ARCHIVES = [
    ("meta-ra-rft", "2606.13680", "https://cdn-mineru.openxlab.org.cn/pdf/2026-07-29/92959f61-fc93-41d7-a391-ff071d0dbe61.zip"),
    ("tencent-hils", "2607.02980", "https://cdn-mineru.openxlab.org.cn/pdf/2026-07-07/50bfdc26-48e9-4aa7-873e-ebbb231af9cb.zip"),
    ("mmeacr", "2607.07108", "https://cdn-mineru.openxlab.org.cn/pdf/2026-07-09/ca22fe28-0aa8-46d2-b7d5-ababb5bfe865.zip"),
]


def main() -> None:
    parser = PDFParser()
    failed = []
    for slug, arxiv_id, url in ARCHIVES:
        print(f"Recovering MinerU result: {slug}", flush=True)
        if not parser._download_and_extract(url, OUTPUT_ROOT / slug, arxiv_id):
            failed.append(slug)
    if failed:
        raise SystemExit(f"Could not recover: {', '.join(failed)}")


if __name__ == "__main__":
    main()
