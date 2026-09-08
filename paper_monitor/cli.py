"""paper_monitor 命令行入口。

用法：
  python -m paper_monitor.cli ingest [--sources openalex,arxiv] [--limit 50] [--offline]
  python -m paper_monitor.cli digest            # 从 DB 重渲染并投递
  python -m paper_monitor.cli analyze            # 统计 / Top / 爆发
  python -m paper_monitor.cli serve [--port 8787]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

from .config import get_config, log
from .notify import deliver, render_digest
from .orchestrator import run_ingest
from .store import SQLiteStore


def _cmd_ingest(args) -> int:
    sources = [s.strip() for s in args.sources.split(",")] if args.sources else None
    summary = run_ingest(sources=sources, limit=args.limit, config=None)
    print("\n=== 摄入汇总 ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    return 0


def _cmd_digest(args) -> int:
    cfg = get_config()
    store = SQLiteStore(config=cfg)
    papers = store.query(limit=200)
    store.close()
    digest = render_digest(papers)
    if not digest:
        print("digest 为空，跳过投递（防静默空推）。")
        return 0
    res = deliver(digest, config=cfg)
    print("投递结果:", res)
    return 0


def _cmd_analyze(args) -> int:
    cfg = get_config()
    store = SQLiteStore(config=cfg)
    papers = store.query(limit=args.limit)
    bursts = store.detect_bursts()
    store.close()
    print(f"入库总数: {store.count() if False else len(papers)} (展示 Top {len(papers)})")
    print(f"引用爆发: {len(bursts)} 条")
    for i, p in enumerate(papers[:10], 1):
        topics = ", ".join(t.display_name for t in p.topics[:3] if t.display_name)
        print(f"  {i:2d}. [{p.score:.3f}] {p.title[:60]}  ({p.source}, {topics})")
    for b in bursts:
        print(f"  🔥 {b['title']}  +{b['delta']}")
    return 0


def _cmd_serve(args) -> int:
    from .api import serve
    try:
        serve(port=args.port)
    except ImportError:
        print("serve 需要可用的网络/socket；当前环境不支持。", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="paper_monitor", description="前沿论文自动发现·过滤·推送系统")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("ingest", help="运行摄入 DAG")
    pi.add_argument("--sources", help="逗号分隔: openalex,arxiv,huggingface,s2")
    pi.add_argument("--limit", type=int, default=50)
    pi.add_argument("--offline", action="store_true", help="使用内置 fixture（离线测试）")
    pi.set_defaults(func=_cmd_ingest)

    sub.add_parser("digest", help="从 DB 重渲染并投递 digest").set_defaults(func=_cmd_digest)

    pa = sub.add_parser("analyze", help="统计/Top/爆发")
    pa.add_argument("--limit", type=int, default=50)
    pa.set_defaults(func=_cmd_analyze)

    ps = sub.add_parser("serve", help="启动内部 REST API")
    ps.add_argument("--port", type=int, default=8787)
    ps.set_defaults(func=_cmd_serve)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "offline", False):
        import os
        os.environ["PM_OFFLINE_FIXTURE"] = "1"
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
