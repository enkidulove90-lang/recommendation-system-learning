"""
novelty/cli.py — 命令行入口

用法:
    python -m novelty.cli analyze --arxiv-id 2605.28175 --top-k 10
    python -m novelty.cli analyze --arxiv-id 2605.28175 --embedder tfidf --no-online
    python -m novelty.cli list-corpus        # 查看本地语料规模与样例

默认嵌入后端=tfidf（零下载、确定性强）；可用 --embedder minilm/specter2/pure。
默认联网（S2/OpenAlex）开启；离线用 --no-online。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 允许以脚本方式运行（确保项目根在 sys.path）
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import settings  # noqa: E402
from novelty.engine import NoveltyEngine  # noqa: E402
from novelty.report import ReportGenerator  # noqa: E402


def cmd_analyze(args: argparse.Namespace) -> int:
    embedder = args.embedder
    engine = NoveltyEngine(
        data_dir=settings.DATA_DIR,
        embedder_kind=embedder,
        use_s2=not args.no_online,
        use_openalex=not args.no_online,
        top_k=args.top_k,
    )
    report = engine.analyze(args.arxiv_id)
    md, js = ReportGenerator().generate(report)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{args.arxiv_id}.md").write_text(md, encoding="utf-8")
    (out_dir / f"{args.arxiv_id}.json").write_text(js, encoding="utf-8")

    if args.json:
        print(js)
    else:
        print(md)
    print(f"\n[done] report -> {out_dir / (args.arxiv_id + '.md')}", file=sys.stderr)
    return 0


def cmd_list_corpus(args: argparse.Namespace) -> int:
    from novelty.corpus import LocalCorpus
    corpus = LocalCorpus(settings.DATA_DIR).load(limit=args.limit)
    print(f"corpus size: {len(corpus.records)}")
    for r in corpus.records[:20]:
        print(f"  {r.arxiv_id:>14}  {r.year or '?'}  {r.title[:60]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="novelty", description="论文创新性分析引擎 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="分析单篇论文的新颖性辅助报告")
    a.add_argument("--arxiv-id", required=True)
    a.add_argument("--top-k", type=int, default=10)
    a.add_argument("--embedder", default="tfidf",
                   choices=["auto", "tfidf", "minilm", "specter2", "pure"])
    a.add_argument("--no-online", action="store_true", help="禁用 S2/OpenAlex 联网")
    a.add_argument("--out", default="data/novelty_reports")
    a.add_argument("--json", action="store_true", help="仅输出 JSON 报告")
    a.set_defaults(func=cmd_analyze)

    l = sub.add_parser("list-corpus", help="列出本地语料")
    l.add_argument("--limit", type=int, default=20)
    l.set_defaults(func=cmd_list_corpus)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
