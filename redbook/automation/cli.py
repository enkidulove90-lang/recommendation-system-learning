"""Single CLI for the six chapters. Commands are local-file first and safe by default."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .daily_discovery import DailyDiscoveryRunner
from .daily_runner import DailyDraftRunner, configured_interval_minutes
from .one_click import QualifiedPaperDraftDelivery
from .content_operations import PaperCardStore, ReviewQueue, XiaohongshuPaperRenderer
from .platform_adapters import adapter_for, package_from_paper_card, platform_doctor
from .feedback import FeedbackStore
from .images import build_manifest, compose_group, group_figures, load_manifest
from .publishing import FilePublisher, render_package
from .scoring import QualityScorerV2
from .sources import JsonlSource, SourceRunner


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _emit_json(value: object) -> None:
    """Keep automation results readable in Windows consoles with legacy encodings."""
    print(json.dumps(value, ensure_ascii=True, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Redbook automation chapters 1-6")
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    commands = parser.add_subparsers(dest="command", required=True)
    source = commands.add_parser("source-jsonl")
    source.add_argument("--name", required=True); source.add_argument("--input", type=Path, required=True)
    discover = commands.add_parser("discover-daily", help="discover local paper candidates from configured arXiv routes; never creates a draft")
    discover.add_argument("--config", type=Path, default=Path("redbook/config/daily_draft.yaml"))
    run_daily = commands.add_parser("run-daily", help="run the draft-only discovery and qualification queue for a bounded duration")
    run_daily.add_argument("--config", type=Path, default=Path("redbook/config/daily_draft.yaml"))
    run_daily.add_argument("--duration-hours", type=float, default=24)
    cadence = run_daily.add_mutually_exclusive_group()
    cadence.add_argument("--interval-hours", type=float, help="user-selected hours between discovery and qualification-queue runs")
    cadence.add_argument("--interval-minutes", type=int, help="user-selected minutes between discovery and qualification-queue runs")
    run_daily.add_argument("--once", action="store_true", help="run one discovery/queue cycle without sleeping")
    one_click = commands.add_parser("one-click-draft", help="save one fully qualified local paper bundle as a Xiaohongshu draft")
    one_click.add_argument("--manifest", type=Path, required=True, help="qualified selection_manifest.json")
    one_click.add_argument("--title", help="optional unique title override")
    one_click.add_argument("--topic", action="append", default=[], help="verified real topic candidate; repeat as needed")
    card_create = commands.add_parser("create-paper-card", help="create one canonical fact card from a qualified legacy manifest")
    card_create.add_argument("--manifest", type=Path, required=True)
    card_create.add_argument("--output", type=Path, required=True)
    card_create.add_argument("--title")
    card_create.add_argument("--topic", action="append", default=[])
    card_render = commands.add_parser("render-xhs-paper-card", help="render a draft-only Xiaohongshu JSON solely from paper_card.json")
    card_render.add_argument("--paper-card", type=Path, required=True)
    card_render.add_argument("--output", type=Path, required=True)
    card_deliver = commands.add_parser("draft-xhs-paper-card", help="render and save one complete Xiaohongshu private draft from paper_card.json")
    card_deliver.add_argument("--paper-card", type=Path, required=True)
    card_deliver.add_argument("--title", help="unique private-draft test title")
    card_validate = commands.add_parser("validate-paper-card", help="validate a canonical paper card; --write adds its deterministic content hash")
    card_validate.add_argument("--paper-card", type=Path, required=True)
    card_validate.add_argument("--write", action="store_true", help="canonicalize and write the validated card in place")
    platform_doctor_command = commands.add_parser("platform-doctor", help="inspect real platform-stage prerequisites without writing remotely")
    platform_stage = commands.add_parser("stage-platform", help="validate and stage one platform package from paper_card.json")
    platform_stage.add_argument("--platform", required=True, choices=("github_pages", "notion", "wechat", "zhihu", "x", "jike", "bilibili"))
    platform_stage.add_argument("--paper-card", type=Path, required=True)
    platform_stage.add_argument("--canonical-url", required=True)
    platform_stage.add_argument("--zhihu-query", help="optional read-only Zhihu question search query")
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
    elif args.command == "discover-daily":
        print(json.dumps(DailyDiscoveryRunner(args.data_root, args.config).run(), ensure_ascii=False, indent=2))
    elif args.command == "run-daily":
        runner = DailyDraftRunner(args.data_root, args.config)
        interval = (
            int(args.interval_hours * 60) if args.interval_hours is not None
            else args.interval_minutes if args.interval_minutes is not None
            else configured_interval_minutes(args.config)
        )
        result = [runner.run_once().as_dict()] if args.once else [item.as_dict() for item in runner.run_for(args.duration_hours, interval)]
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "one-click-draft":
        print(json.dumps(QualifiedPaperDraftDelivery().deliver(args.manifest, args.title, tuple(args.topic)), ensure_ascii=False, indent=2))
    elif args.command == "create-paper-card":
        card = PaperCardStore().create_from_manifest(args.manifest, title=args.title, topics=tuple(args.topic))
        PaperCardStore().write(args.output, card)
        _emit_json({"paper_card": str(args.output), "content_hash": card["content_hash"]})
    elif args.command == "render-xhs-paper-card":
        card = PaperCardStore.load(args.paper_card)
        draft = XiaohongshuPaperRenderer.render(card)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
        _emit_json({"draft": str(args.output), "content_hash": card["content_hash"]})
    elif args.command == "draft-xhs-paper-card":
        _emit_json(QualifiedPaperDraftDelivery().deliver_paper_card(args.paper_card, args.title))
    elif args.command == "validate-paper-card":
        store = PaperCardStore()
        if args.write:
            card = _json(args.paper_card)
            store.write(args.paper_card, card)
        card = store.load(args.paper_card)
        _emit_json({"paper_card": str(args.paper_card), "content_hash": card["content_hash"], "valid": True})
    elif args.command == "platform-doctor":
        _emit_json(platform_doctor(args.data_root))
    elif args.command == "stage-platform":
        package = package_from_paper_card(args.paper_card, args.platform, args.canonical_url)
        if args.zhihu_query:
            package.metadata["zhihu_query"] = args.zhihu_query
        _emit_json(adapter_for(args.platform, args.data_root).stage(package))
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
