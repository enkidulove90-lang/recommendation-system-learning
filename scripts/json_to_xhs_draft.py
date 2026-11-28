"""RETIRED: use the S5 content bridge and the manual ``redbook.cli note`` entry.

Agent-free, vision-model-free.  Steps:
  1. generate fact-pack/v2 JSON (one DeepSeek call via idempotent gateway)
  2. compile it into a redbook note YAML (deterministic, figures in paper order)
  3. run `redbook.cli note --publish` (stage + CDP draft delivery + verification)

WeChat / homepage drafts are produced by step 1 into the same fact_pack JSON
(``wechat_draft`` / ``homepage_draft`` blocks) for their own compilers later.

Usage::

    python scripts/json_to_xhs_draft.py \
        --canonical-id arxiv:3774904.3792523 \
        --markdown data/parsed/3774904.3792523_RecCLIP/3774904.3792523.md \
        --parsed-dir data/parsed/recclip \
        --pdf data/papers/3774904.3792523.pdf
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.model_gateway import artifact_basename
from paper_intake.note_compiler import compile_note

DEFAULT_FACT_PACK = ROOT / "data" / "summaries"


def run(canonical_id: str, markdown: Path, parsed_dir: Path, pdf: Path | None,
        *, title_style: str = "literary", publish: bool = True,
        python: str | None = None) -> dict:
    raise RuntimeError("retired entrypoint: use S5 and manually run python -m redbook.cli note <slug>")
    from scripts.generate_fact_pack import generate

    fact_path = generate(canonical_id, markdown)
    payload = json.loads(fact_path.read_text(encoding="utf-8"))
    if not payload.get("xhs_draft"):
        raise RuntimeError(f"fact_pack has no xhs_draft: {fact_path}")

    note_path = compile_note(
        fact_path,
        canonical_id=canonical_id,
        parsed_dir=parsed_dir,
        pdf_path=pdf,
        title_style=title_style,
    )
    paper_id = canonical_id.rsplit(":", 1)[-1]
    result: dict = {
        "ok": True,
        "fact_pack": str(fact_path.relative_to(ROOT)),
        "note": str(note_path.relative_to(ROOT)),
        "title": payload["xhs_draft"].get(f"title_{title_style}", ""),
        "wechat_ready": bool(payload.get("wechat_draft")),
        "homepage_ready": bool(payload.get("homepage_draft")),
    }
    if not publish:
        result["delivery"] = "skipped"
        return result

    interpreter = python or sys.executable
    command = [interpreter, "-m", "redbook.cli", "note", paper_id, "--publish"]
    completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    try:
        result["delivery"] = json.loads(completed.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        result["delivery"] = {
            "ok": False,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-500:],
            "stderr": completed.stderr[-500:],
        }
    result["ok"] = bool(result["delivery"].get("ok"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="JSON -> Xiaohongshu draft, end to end")
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--parsed-dir", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--title-style", choices=("literary", "question"), default="literary")
    parser.add_argument("--no-publish", action="store_true",
                        help="only build the note YAML; do not write to the platform")
    parser.add_argument("--python", default=None, help="python interpreter for the CLI step")
    args = parser.parse_args()
    result = run(
        args.canonical_id, args.markdown, args.parsed_dir, args.pdf,
        title_style=args.title_style, publish=not args.no_publish, python=args.python)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
