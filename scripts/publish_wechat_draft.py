"""Compile a WeChat draft package from fact_pack JSON and deliver it.

This is the consumer-side entry point (scripts/ may import redbook; the
paper_intake compiler may not).  One command does compile + browser-bridge
delivery to the WeChat draft box.

Usage::

    python scripts/publish_wechat_draft.py \
        --fact-pack data/summaries/arxiv__3774904.3792523_fact_pack.json \
        --canonical-id arxiv:3774904.3792523 \
        --parsed-dir data/parsed/recclip
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.wechat_compiler import (
    DEFAULT_AUTHOR,
    compile_wechat_package,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="compile + deliver a WeChat draft")
    parser.add_argument("--fact-pack", type=Path, required=True)
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--parsed-dir", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--author", default=DEFAULT_AUTHOR)
    parser.add_argument("--no-publish", action="store_true",
                        help="only compile the package; do not write to WeChat")
    args = parser.parse_args()

    path, staged_id = compile_wechat_package(
        args.fact_pack, canonical_id=args.canonical_id, parsed_dir=args.parsed_dir,
        pdf_path=args.pdf, author=args.author)
    result: dict = {
        "ok": True,
        "package": str(path.relative_to(ROOT)),
        "staged_id": staged_id[:32],
    }
    if not args.no_publish:
        from redbook.automation.publishing import WeChatPublisher
        result["delivery"] = WeChatPublisher(ROOT).publish(staged_id)
        result["ok"] = bool(result["delivery"].get("ok"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
