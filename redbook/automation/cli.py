"""Single CLI for the six chapters. Commands are local-file first and safe by default."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .feedback import FeedbackStore
from .images import build_manifest, compose_group, group_figures, load_manifest
from .publishing import FilePublisher, render_package
from .scoring import QualityScorerV2
from .sources import JsonlSource, SourceRunner


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Redbook automation chapters 1-6")
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    commands = parser.add_subparsers(dest="command", required=True)
    source = commands.add_parser("source-jsonl")
    source.add_argument("--name", required=True); source.add_argument("--input", type=Path, required=True)
    normalize = commands.add_parser("normalize")
    normalize.add_argument("inputs", nargs="+", type=Path)
    score = commands.add_parser("score")
    score.add_argument("--evidence", type=Path, required=True)
    stage = commands.add_parser("stage")
    stage.add_argument("--platform", required=True); stage.add_argument("--paper", type=Path, required=True); stage.add_argument("--canonical-url", required=True)
    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--note-id", required=True); snapshot.add_argument("--age-hours", type=int, required=True); snapshot.add_argument("--metrics", type=Path, required=True)
    manifest = commands.add_parser("manifest")
    manifest.add_argument("--output", type=Path, required=True); manifest.add_argument("images", nargs="+", type=Path)
    compose = commands.add_parser("compose")
    compose.add_argument("--manifest", type=Path, required=True); compose.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "source-jsonl":
        print(json.dumps(SourceRunner(args.data_root).run(JsonlSource(args.name, args.input)), ensure_ascii=False, indent=2))
    elif args.command == "normalize":
        print(json.dumps(SourceRunner(args.data_root).normalize(args.inputs), ensure_ascii=False, indent=2))
    elif args.command == "score":
        result = QualityScorerV2().score(_json(args.evidence)); print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    elif args.command == "stage":
        package = render_package(_json(args.paper), args.platform, args.canonical_url); print(json.dumps(FilePublisher(args.platform, args.data_root).stage(package), ensure_ascii=False, indent=2))
    elif args.command == "snapshot":
        print(json.dumps(FeedbackStore(args.data_root).record_snapshot(args.note_id, args.age_hours, _json(args.metrics)), ensure_ascii=False, indent=2))
    elif args.command == "manifest":
        print(json.dumps([asset.__dict__ for asset in build_manifest(args.images, args.output)], ensure_ascii=False, indent=2))
    elif args.command == "compose":
        groups = group_figures(load_manifest(args.manifest)); results = []
        for index, group in enumerate(groups, 1):
            if len(group) > 1:
                results.append(compose_group(group, args.output_dir / f"group-{index:02d}.jpg"))
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
