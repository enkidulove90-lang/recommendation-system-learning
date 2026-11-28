"""End-to-End Content Bridge: drive one paper through three platform pipelines.

This is a complete rewrite of content_bridge.py that:
- Uses the same fact_pack and parsed assets for all three platforms
- Calls each platform's dedicated compiler
- Collects and reports independent receipts from each platform
- Does not merge state - each platform reports its own status
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]


class E2EResult:
    """End-to-end result for a single paper across three platforms."""

    def __init__(self, canonical_id: str):
        self.canonical_id = canonical_id
        self.webkit: Optional[Path] = None
        self.platforms: dict[str, E2EResult.PlatformResult] = {}

    class PlatformResult:
        """Result for one platform."""

        def __init__(self):
            self.compiled: bool = False
            self.compiled_path: Optional[Path] = None
            self.staged: bool = False
            self.staged_id: Optional[str] = None
            self.drafted: bool = False
            self.draft_id: Optional[str] = None
            self.reopened_verified: bool = False
            self.reopened_url: Optional[str] = None
            self.title_verified: bool = False
            self.body_verified: bool = False
            self.cover_verified: bool = False
            self.reason: str = ""

        def all_ok(self) -> bool:
            # compiled + drafted + reopened_verified for minimal delivery
            return self.compiled and self.drafted and self.reopened_verified

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_id": self.canonical_id,
            "platforms": {
                name: {
                    "compiled": res.compiled,
                    "compiled_path": str(res.compiled_path) if res.compiled_path else None,
                    "staged": res.staged,
                    "staged_id": res.staged_id,
                    "drafted": res.drafted,
                    "draft_id": res.draft_id,
                    "reopened_verified": res.reopened_verified,
                    "reopened_url": res.reopened_url,
                    "title_verified": res.title_verified,
                    "body_verified": res.body_verified,
                    "cover_verified": res.cover_verified,
                    "reason": res.reason,
                }
                for name, res in self.platforms.items()
            },
            "summary": {
                "all_platforms_ok": all(res.all_ok() for res in self.platforms.values()),
                "xhs": "ready" if self.platforms["xhs"].all_ok() else "blocked",
                "wechat": "ready" if self.platforms["wechat"].all_ok() else "blocked",
                "notion": "ready" if self.platforms["notion"].all_ok() else "blocked",
            }
        }


def _load_fact_pack(path: Path) -> dict:
    """Simple load_fact_pack using note_compiler's function."""
    from paper_intake.note_compiler import load_fact_pack as _lfp
    fp = _lfp(path)
    if not fp.get("facts") or not fp.get("xhs_draft") or not fp.get("wechat_draft"):
        raise ValueError(f"fact_pack missing required blocks: {path}")
    return fp


def _compile_xhs(
    fact_pack_path: Path,
    canonical_id: str,
    parsed_dir: Path,
    pdf_path: Path | None,
) -> E2EResult.PlatformResult:
    """Compile Xiaohongshu note."""
    result = E2EResult.PlatformResult()

    try:
        from paper_intake.note_compiler import compile_note
        note_path = compile_note(
            fact_pack_path=fact_pack_path,
            canonical_id=canonical_id,
            parsed_dir=parsed_dir,
            pdf_path=pdf_path,
        )
        result.compiled = True
        result.compiled_path = note_path
        # compile_note does NOT set staged; we leave it as False
    except Exception as e:
        result.reason = f"XHS compile error: {e}"
        return result

    return result


def _compile_wechat(
    fact_pack_path: Path,
    canonical_id: str,
    parsed_dir: Path,
    pdf_path: Path | None,
) -> E2EResult.PlatformResult:
    """Compile WeChat package."""
    result = E2EResult.PlatformResult()

    try:
        from paper_intake.wechat_compiler import compile_wechat_package
        wechat_path, staged_id = compile_wechat_package(
            fact_pack_path=fact_pack_path,
            canonical_id=canonical_id,
            parsed_dir=parsed_dir,
            pdf_path=pdf_path,
        )
        result.compiled = True
        result.compiled_path = wechat_path
        result.staged = True
        result.staged_id = staged_id
    except Exception as e:
        result.reason = f"WeChat compile error: {e}"
        return result

    return result


def _compile_notion(
    canonical_id: str,
) -> E2EResult.PlatformResult:
    """Compile Notion / personal homepage content."""
    result = E2EResult.PlatformResult()
    # Notion integration README says this is not implemented
    result.reason = "Notion integration blocked: requires explicit NOTION_WRITE_AUTH setting and target database schema"
    return result


def run_end_to_end(
    canonical_id: str,
    fact_pack_path: Path,
    parsed_dir: Path,
    pdf_path: Path | None,
) -> E2EResult:
    """Execute full end-to-end pipeline for one paper."""
    # Load shared assets
    fact_pack = _load_fact_pack(fact_pack_path)

    result = E2EResult(canonical_id)
    result.platforms["xhs"] = _compile_xhs(fact_pack_path, canonical_id, parsed_dir, pdf_path)
    result.platforms["wechat"] = _compile_wechat(fact_pack_path, canonical_id, parsed_dir, pdf_path)
    result.platforms["notion"] = _compile_notion(canonical_id)

    return result


def main():
    """Example usage - for testing only."""
    import argparse
    parser = argparse.ArgumentParser(description="End-to-end pipeline for one paper")
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--fact-pack", required=True)
    parser.add_argument("--parsed-dir", required=True)
    parser.add_argument("--pdf-path", type=Path, default=None)
    args = parser.parse_args()

    result = run_end_to_end(
        canonical_id=args.canonical_id,
        fact_pack_path=Path(args.fact_pack),
        parsed_dir=Path(args.parsed_dir),
        pdf_path=args.pdf_path,
    )

    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
