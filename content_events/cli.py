"""内容事件编排 CLI（content_events/cli.py）。

用法：
  python content_events/cli.py process-queue [--root .] [--publisher dryrun] [--theme recsys-blue] [--no-dry-run] [--retry]
  python content_events/cli.py collect-feedback [--root .]
  python content_events/cli.py status [--root .] [--paper-id X]

process-queue 默认 dryrun（沙箱安全，只写本地待发布包，不触达真实平台）。
--no-dry-run 仅在 review_status=approved 的真实平台项才尝试真实 stage（沙箱无会话→needs_review）。
退出码：errors>0 → 1（部分失败，便于自动化识别）；否则 0。
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import orchestrator  # noqa: E402
from content_events.retry import RetryPolicy  # noqa: E402


def cmd_process_queue(args):
    retry_policy = RetryPolicy(max_attempts=args.retry_attempts) if args.retry else None
    results, summary = orchestrator.run_once(
        args.root, publisher=args.publisher, theme=args.theme,
        dry_run=not args.no_dry_run, retry_policy=retry_policy,
    )
    out = {
        "processed": len(results),
        "summary": summary.as_dict(),
        "summary_text": summary.render(),
        "results": results,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1 if summary.errors > 0 else 0


def cmd_collect_feedback(args):
    res = orchestrator.collect_feedback(args.root)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def cmd_status(args):
    qroot = os.path.join(args.root, "publish_queue")
    out = []
    if os.path.isdir(qroot):
        for name in sorted(os.listdir(qroot)):
            sp = os.path.join(qroot, name, "state.json")
            if not os.path.exists(sp):
                continue
            try:
                with open(sp, encoding="utf-8") as _sf:
                    d = json.load(_sf)
            except (json.JSONDecodeError, OSError):
                continue
            if args.paper_id and d.get("paper_id") != args.paper_id:
                continue
            out.append(d)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="内容事件编排层 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    pq = sub.add_parser("process-queue", help="处理发布队列")
    pq.add_argument("--root", default=ROOT)
    pq.add_argument("--publisher", default="dryrun", choices=["dryrun", "wechat", "xhs"])
    pq.add_argument("--theme", default="recsys-blue")
    pq.add_argument("--no-dry-run", action="store_true",
                    help="允许 approved 真实平台项尝试真实 stage（沙箱无会话→needs_review）")
    pq.add_argument("--retry", action="store_true", help="对 stage 瞬时失败启用重试+退避")
    pq.add_argument("--retry-attempts", type=int, default=3, help="最大重试次数（配合 --retry）")
    pq.set_defaults(func=cmd_process_queue)

    cf = sub.add_parser("collect-feedback", help="采集反馈观察窗口 + 自优化决策")
    cf.add_argument("--root", default=ROOT)
    cf.set_defaults(func=cmd_collect_feedback)

    st = sub.add_parser("status", help="查看队列状态")
    st.add_argument("--root", default=ROOT)
    st.add_argument("--paper-id", default=None, help="仅显示该 paper_id 的状态（A6）")
    st.set_defaults(func=cmd_status)
    return p


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
