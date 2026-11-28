"""One-shot end-to-end verification of the paper consumption middleware.

Checks, in order:
  1. data/parsed/<id>/ has a Markdown file
  2. content_bridge runs for the canonical id
  3. data/summaries/<safe id>_fact_pack.json exists and validates
  4. content_assets has an asset_kind='fact_pack' row
  5. paper_pool status is 'staged'
  6. publish_queue/<id>/ has xhs.json and wechat.json
  7. runs.jsonl tail has a content_bridge ok record

Prints PASS/FAIL per check and exits 1 if any fails.  Never calls a model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.fact_pack import FactPack
from paper_intake.model_gateway import artifact_basename

DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
RUNS = ROOT / "data" / "logs" / "runs.jsonl"


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    return ok


def find_parsed_markdown(canonical_id: str) -> Path | None:
    bare = canonical_id.split(":", 1)[-1]
    base = ROOT / "data" / "parsed"
    candidates = [
        base / bare,
        base / canonical_id.replace(":", "__"),
    ]
    # MinerU stores bundles as "<id>_<title>" (see resolve_paper_bundle);
    # include those directories via a bare-id prefix match.
    if base.is_dir():
        candidates.extend(
            folder for folder in sorted(base.iterdir())
            if folder.is_dir() and folder.name.startswith(f"{bare}_")
        )
    for folder in candidates:
        if folder.is_dir():
            matches = sorted(folder.rglob(f"{bare}.md"))
            if not matches:
                matches = sorted(folder.rglob("*.md"))
            if matches:
                return matches[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--skip-bridge", "--dry-run", dest="skip_bridge",
                        action="store_true",
                        help="only inspect existing artifacts; never call any model API")
    args = parser.parse_args()
    cid = args.canonical_id
    bare = cid.split(":", 1)[-1]
    results: list[bool] = []

    md = find_parsed_markdown(cid)
    results.append(check("1. parsed markdown exists", md is not None,
                         str(md.relative_to(ROOT)) if md else "not found"))

    if not args.skip_bridge:
        command = [sys.executable, str(ROOT / "scripts" / "content_bridge.py"),
                   "--canonical-id", cid]
        completed = subprocess.run(command, cwd=str(ROOT),
                                   capture_output=True, text=True)
        results.append(check("2. content_bridge ran", completed.returncode == 0,
                             (completed.stdout or completed.stderr).strip()[:200]))
    else:
        print("SKIP  2. content_bridge (--skip-bridge)")

    fact_path = ROOT / "data" / "summaries" / f"{artifact_basename(cid, 'fact_pack')}.json"
    fact_ok = fact_path.is_file()
    fact_detail = str(fact_path.relative_to(ROOT))
    if fact_ok:
        try:
            payload = json.loads(fact_path.read_text(encoding="utf-8"))
            FactPack(**payload)
        except Exception as error:
            fact_ok = False
            # Never put an exception string into a filename: it contains
            # newlines/colons that are illegal and crash the verifier.
            fact_detail = f"invalid schema: {str(error).splitlines()[0][:150]}"
    results.append(check("3. fact_pack valid", fact_ok, fact_detail))

    if DB.is_file():
        with sqlite3.connect(DB) as connection:
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")}
            if "content_assets" in tables:
                row = connection.execute(
                    "SELECT relative_path FROM content_assets "
                    "WHERE canonical_id=? AND asset_kind='fact_pack'",
                    (cid,)).fetchone()
                results.append(check("4. content_assets row", row is not None,
                                     row[0] if row else "no row"))
            else:
                results.append(check("4. content_assets row", False,
                                     "table missing (run refresh_once once)"))
            if "paper_pool" in tables:
                pool_row = connection.execute(
                    "SELECT status FROM paper_pool WHERE canonical_id=?", (cid,)).fetchone()
                results.append(check("5. paper_pool staged",
                                     pool_row is not None and pool_row[0] == "staged",
                                     pool_row[0] if pool_row else "no row"))
            else:
                results.append(check("5. paper_pool staged", False, "table missing"))
    else:
        results.extend([
            check("4. content_assets row", False, "db missing"),
            check("5. paper_pool staged", False, "db missing"),
        ])

    queue_dir = ROOT / "publish_queue" / bare
    xhs = queue_dir / "xhs.json"
    wechat = queue_dir / "wechat.json"
    results.append(check("6. platform packages",
                         xhs.is_file() and wechat.is_file(),
                         str(queue_dir.relative_to(ROOT))))

    if RUNS.is_file():
        import re

        all_lines = RUNS.read_text(encoding="utf-8", errors="replace").splitlines()
        # Match a JSONL record whose canonical_id is the target, whose stage is
        # fact_pack_generation/platform_render and whose status is ok.  Filter
        # the WHOLE log by canonical_id first: a busy log (or repeated retries)
        # can otherwise push an earlier ok out of the last-N window.  Keep the
        # latest ok per stage.
        pattern = re.compile(
            r'"stage":\s*"(fact_pack_generation|platform_render)"'
            r'.*?"status":\s*"ok"'
            r'.*?"canonical_id":\s*"' + re.escape(cid) + r'"',
        )
        found: dict[str, int] = {}
        for line in all_lines:
            if cid not in line:
                continue
            match = pattern.search(line)
            if not match:
                continue
            try:
                duration = json.loads(line).get("detail", {}).get("duration_ms", -1)
            except (json.JSONDecodeError, AttributeError):
                duration = -1
            found[match.group(1)] = int(duration)
        stages_ok = {"fact_pack_generation", "platform_render"} <= found.keys()
        detail = ", ".join(f"{name}={ms}ms" for name, ms in sorted(found.items())) or "none"
        results.append(check("7. runs.jsonl traced ok", stages_ok, detail))
    else:
        results.append(check("7. runs.jsonl traced ok", False, "log missing"))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
