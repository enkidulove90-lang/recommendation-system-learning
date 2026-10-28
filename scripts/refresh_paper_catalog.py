from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.catalog import load_catalog_config, refresh_from_config


DEFAULT_CONFIG = ROOT / "config" / "paper_catalog_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "paper_catalog" / "papers.json"


def refresh_once(*, config_path: Path, output_path: Path, interval_seconds: int | None = None) -> int:
    config = load_catalog_config(config_path)
    interval = int(interval_seconds or config.get("refresh_interval_seconds", 1800))
    catalog = refresh_from_config(config, cache_dir=output_path.parent / "cache")
    if not catalog.papers:
        raise RuntimeError("all catalog sources returned zero papers; previous catalog was preserved")
    catalog.write_json(output_path, refresh_interval_seconds=interval)
    print(json.dumps({"status": "ok", "paper_count": len(catalog.papers), "output": str(output_path)}, ensure_ascii=False))
    return interval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh the authoritative paper discovery catalog.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--interval", type=int, default=None, help="Refresh interval in seconds (default: config or 1800).")
    parser.add_argument("--watch", action="store_true", help="Keep running and refresh at the configured interval.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    while True:
        try:
            interval = refresh_once(
                config_path=args.config,
                output_path=args.output,
                interval_seconds=args.interval,
            )
        except Exception as exc:
            print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
            if not args.watch:
                return 1
            interval = int(args.interval or 1800)
        if not args.watch:
            return 0
        time.sleep(max(interval, 60))


if __name__ == "__main__":
    raise SystemExit(main())
