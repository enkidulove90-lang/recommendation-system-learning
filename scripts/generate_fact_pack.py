"""Generate a publish-ready fact_pack JSON from a parsed paper Markdown.

Pure backend entry point using SHUSHENG with DeepSeek fallback (idempotent
on source hash + prompt version + model id), producing fact-pack/v2 with the
``xhs_draft`` / ``wechat_draft`` / ``homepage_draft`` manuscript blocks.

Usage::

    python scripts/generate_fact_pack.py \
        --canonical-id arxiv:2605.14853 \
        --markdown data/parsed/2605.14853_2605.14853/2605.14853.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from paper_intake.asset_manifest import ContentAssetManifest
from paper_intake.catalog_store import CatalogRepository
from paper_intake.fact_pack import (
    FACT_PACK_PROMPT_VERSION,
    build_fact_pack_prompt,
    parse_fact_pack_response,
)
from paper_intake.model_gateway import ModelCallGatewayWithFallback

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"


def generate(canonical_id: str, markdown: Path, db_path: Path = DEFAULT_DB) -> Path:
    markdown = Path(markdown)
    if not markdown.is_file():
        raise FileNotFoundError(f"markdown missing: {markdown}")
    if not (settings.SHUSHENG_API_KEY or settings.DEEPSEEK_API_KEY):
        raise RuntimeError("Either SHUSHENG_API_KEY or DEEPSEEK_API_KEY must be configured")

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    repository = CatalogRepository(db_path)
    repository.close()

    gateway = ModelCallGatewayWithFallback(
        ContentAssetManifest(db_path), ROOT, use_shusheng_cache=True)
    return gateway.ensure(
        canonical_id=canonical_id,
        purpose="fact_pack",
        source=markdown,
        prompt_version=FACT_PACK_PROMPT_VERSION,
        model_id=settings.SHUSHENG_MODEL,
        build_prompt=build_fact_pack_prompt,
        parse_response=lambda raw: parse_fact_pack_response(raw, canonical_id),
        use_shusheng_first=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="generate fact-pack/v2 JSON")
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    path = generate(args.canonical_id, args.markdown, args.db)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps({
        "ok": True,
        "path": str(path.relative_to(ROOT)),
        "schema_version": payload.get("schema_version"),
        "has_xhs_draft": bool(payload.get("xhs_draft")),
        "title": (payload.get("xhs_draft") or {}).get("title_literary", ""),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
