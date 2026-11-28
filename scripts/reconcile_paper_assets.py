"""Inventory PDF/parsed assets against the identity master (papers table).

Task 1 of the content-level reconciliation: read-only scan that emits
``data/paper_catalog/reconcile_report.json``.  L1 = exact arXiv id extracted
from a filename/directory name; L2 = normalized title + first-author surname
from a parsed markdown file against ``papers.normalized_title``.  No database
write happens here (``--apply`` is reserved for later tasks).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog_identity import canonical_id_from_bare, normalize_title  # noqa: E402

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"
DEFAULT_PAPERS_DIR = ROOT / "data" / "papers"
DEFAULT_PARSED_DIR = ROOT / "data" / "parsed"
DEFAULT_REPORT = ROOT / "data" / "paper_catalog" / "reconcile_report.json"

_ARXIV_ID = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
_TITLE_LINE = re.compile(r"^#\s+(.+?)\s*$", re.M)


def extract_arxiv_id(name: str) -> str:
    match = _ARXIV_ID.search(name)
    return match.group(1) if match else ""


def _markdown_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    match = _TITLE_LINE.search(text[:4000])
    return match.group(1).strip() if match else ""


def build_report(*, database: Path = DEFAULT_DB, papers_dir: Path = DEFAULT_PAPERS_DIR,
                 parsed_dir: Path = DEFAULT_PARSED_DIR) -> dict[str, Any]:
    import sqlite3

    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        master = {
            row["canonical_id"]: {
                "arxiv_id": row["arxiv_id"], "title": row["title"],
                "normalized_title": row["normalized_title"],
                "authors": json.loads(row["authors_json"] or "[]"),
            }
            for row in connection.execute(
                "SELECT canonical_id, arxiv_id, title, normalized_title, authors_json FROM papers"
            )
        }
        try:
            job_rows = [
                {"job_id": row["job_id"], "canonical_id": row["canonical_id"],
                 "catalog_canonical_id": row["catalog_canonical_id"]}
                for row in connection.execute(
                    "SELECT job_id, canonical_id, catalog_canonical_id FROM jobs"
                )
            ]
        except sqlite3.OperationalError:
            job_rows = []
    finally:
        connection.close()

    by_arxiv = {value["arxiv_id"]: key for key, value in master.items() if value["arxiv_id"]}
    by_title: dict[str, list[str]] = {}
    for canonical, value in master.items():
        title = value["normalized_title"] or normalize_title(value["title"])
        if title:
            by_title.setdefault(title, []).append(canonical)

    assets: dict[str, dict[str, Any]] = {}
    for pdf in sorted(papers_dir.glob("*.pdf")):
        bare = extract_arxiv_id(pdf.stem)
        assets.setdefault(bare or f"file:{pdf.name}", {"pdf": pdf.name})["pdf"] = pdf.name
        if bare:
            assets[bare]["bare_id"] = bare
    for directory in sorted(parsed_dir.iterdir()):
        if not directory.is_dir():
            continue
        bare = extract_arxiv_id(directory.name)
        key = bare or f"dir:{directory.name}"
        entry = assets.setdefault(key, {})
        entry["parsed_dir"] = directory.name
        if bare:
            entry["bare_id"] = bare
        title = _markdown_title(directory / f"{bare}.md") if bare else ""
        if not title:
            candidates = list(directory.glob("*.md"))
            title = _markdown_title(candidates[0]) if candidates else ""
        if title:
            entry["title"] = title

    l1_hits: dict[str, str] = {}
    l2_hits: dict[str, str] = {}
    l2_ambiguous: list[dict[str, str]] = []
    unmatched: list[dict[str, str]] = []
    for key, asset in sorted(assets.items()):
        bare = asset.get("bare_id", "")
        canonical = canonical_id_from_bare(bare) if bare else ""
        if canonical and canonical in master:
            l1_hits[key] = canonical
            continue
        if canonical and bare in by_arxiv:
            l1_hits[key] = by_arxiv[bare]
            continue
        title = asset.get("title", "")
        if title:
            matches = by_title.get(normalize_title(title), [])
            if len(matches) == 1:
                l2_hits[key] = matches[0]
            elif len(matches) > 1:
                l2_ambiguous.append({"asset": key, "candidates": ",".join(matches)})
                continue
        unmatched.append({"asset": key, "pdf": asset.get("pdf", ""), "parsed_dir": asset.get("parsed_dir", "")})

    job_joins = [
        job for job in job_rows
        if job["canonical_id"] in master or job["catalog_canonical_id"] in master
    ]
    total = len(job_rows) or 1
    return {
        "summary": {
            "master_papers": len(master), "jobs": len(job_rows),
            "assets": len(assets), "l1_hits": len(l1_hits), "l2_hits": len(l2_hits),
            "l2_ambiguous": len(l2_ambiguous), "unmatched": len(unmatched),
            "job_master_join": len(job_joins),
            "job_master_join_rate": round(len(job_joins) / total, 4),
        },
        "l1_hits": l1_hits, "l2_hits": l2_hits,
        "l2_ambiguous": l2_ambiguous, "unmatched": unmatched,
        "jobs": job_rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory paper assets against the identity master.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--papers-dir", type=Path, default=DEFAULT_PAPERS_DIR)
    parser.add_argument("--parsed-dir", type=Path, default=DEFAULT_PARSED_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--stdout", action="store_true", help="Print the report without writing it.")
    args = parser.parse_args(argv)
    report = build_report(database=args.database, papers_dir=args.papers_dir, parsed_dir=args.parsed_dir)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if not args.stdout:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(json.dumps({"status": "dry_run", "report": str(args.report), **report["summary"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
