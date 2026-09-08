"""内容工厂命令行入口。

用法：
    python -m content_factory --paper-id 2506.07261
    python -m content_factory --paper-id 2506.07261 --platforms xhs,wechat --llm
    python -m content_factory --paper-id 2506.07261 --dry-run     # 不写 publish_queue
    python -m content_factory --analyze-events events.jsonl      # 离线分析：漏斗/参与度/A-B（无需 GA4/Metabase）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .factory import ContentFactory
from .schemas import InsufficientSourceError
from .analytics import EventCollector, FunnelAnalyzer, report_ab

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="content_factory", description="科研故事化内容工厂")
    ap.add_argument("--paper-id", required=False, help="arXiv id，如 2506.07261（与 --analyze-events 二选一）")
    ap.add_argument("--platforms", default="xhs,wechat", help="逗号分隔，如 xhs,wechat,zhihu_answer")
    ap.add_argument("--llm", action="store_true", help="启用 LLM 润色（需 DEEPSEEK_API_KEY）")
    ap.add_argument("--viz", action="store_true", help="Stage 4/5：生成可视化 + 交互组件 spec")
    ap.add_argument("--distribute", action="store_true", help="Stage 7：生成分发 + canonical + A/B 作业")
    ap.add_argument("--analytics", action="store_true", help="Stage 8：生成 GA4/Metabase 看板 + 事件 Schema")
    ap.add_argument("--analyze-events", default=None, help="离线分析模式：读取 events JSONL 并输出漏斗/参与度/A-B 报告")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写 publish_queue")
    ap.add_argument("--root", default=str(ROOT), help="项目根（含 data/ 与 publish_queue/）")
    args = ap.parse_args(argv)

    if args.analyze_events:
        return run_analysis(args.analyze_events)

    if not args.paper_id:
        print("[内容工厂] 需要 --paper-id 或 --analyze-events", file=sys.stderr)
        return 2

    root = Path(args.root)
    summaries_dir = root / "data" / "summaries"
    parsed_dir = root / "data" / "parsed"
    platforms_yaml = Path(__file__).resolve().parent / "platforms.yaml"
    platforms = tuple(p.strip() for p in args.platforms.split(",") if p.strip())

    factory = ContentFactory(
        root=root, summaries_dir=summaries_dir, parsed_dir=parsed_dir,
        platforms_yaml=platforms_yaml, use_llm=args.llm,
    )
    try:
        result = factory.run(
            args.paper_id, platforms,
            viz=args.viz, interaction=args.viz,
            distribute=args.distribute, analytics=args.analytics,
        )
    except InsufficientSourceError as exc:
        print(f"[内容工厂] 阻断：{exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"[内容工厂] {exc}", file=sys.stderr)
        return 3

    print(f"[内容工厂] {args.paper_id} 故事化草稿 + 标题工厂完成")
    print(f"—— 选定标题：{result.chosen_title}")
    print(f"—— 标题候选（评分/门禁）：")
    for t in result.titles:
        flag = " ⚠需重写" if t.needs_rewrite else ""
        print(f"   • {t.text}  [{t.score}]{flag}")
    print(f"—— 故事四段式（防幻觉绑定字段：{result.story.bound_fields}）")
    print(result.story.full_text)

    if args.viz:
        print(f"—— Stage 4/5 可视化 {len(result.visuals)} 张 / 交互组件 {len(result.interactions)} 个")
    if args.distribute:
        print(f"—— Stage 7 分发作业 {len(result.distribution)} 个（Buffer/Dev.to/@appnest）")
    if args.analytics:
        evs = result.analytics.get("ga4_events", [])
        print(f"—— Stage 8 分析：GA4 事件 {len(evs)} 类 + Metabase 看板 + 埋点片段")

    if args.dry_run:
        print("[内容工厂] --dry-run：未写入 publish_queue")
        return 0

    receipts = factory.stage(result)
    for r in receipts:
        print(f"[内容工厂] 已暂存 {r.get('path')}")
    return 0


def run_analysis(events_path: str) -> int:
    """离线分析模式：载入 events JSONL → 本地漏斗/参与度/A-B 报告（无需 GA4/Metabase）。"""
    collector = EventCollector()
    n = collector.load(events_path)
    events = collector.events()
    if not events:
        print(f"[内容工厂] 未从 {events_path} 载入任何事件（文件不存在或为空）", file=sys.stderr)
        return 3
    print(f"[内容工厂] 已载入 {n} 条事件（校验错误 {collector.error_count()} 条）")

    fa = FunnelAnalyzer(events)
    print("—— 漏斗（按 session 去重）：impression → scroll_depth → cta_click")
    for row in fa.funnel(["impression", "scroll_depth", "cta_click"]):
        print(f"   • {row['stage']:<14} 会话数 {row['count']:>6}   步转化 {row['step_conv']}")

    print("—— 参与度指标")
    for k, v in fa.engagement().items():
        print(f"   • {k}: {v}")

    print("—— A/B 按 variant 归因（impression → cta_click）")
    for v, m in fa.ab_lift().items():
        print(f"   • {v}: 点击 {m['clicks']} / 曝光 {m['impressions']} = {m['rate']}")

    rec = report_ab(events)
    print(f"—— 多臂 A/B 判定：winner={rec.get('winner')}   注：{rec.get('note')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
