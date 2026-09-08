"""内容工厂自动调度器（本地 cron / GitHub Action 共用）。

扫描 data/summaries/ 中最新、且尚未在 publish_queue 生成过审核包的论文，
对其运行内容工厂并暂存（review_status=pending，不自动发布）。
幂等：已存在 cf_<paper_id> 实验标记则跳过。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _staged_ids(root: Path) -> set[str]:
    q = root / "publish_queue"
    if not q.is_dir():
        return set()
    ids = set()
    for pkg in q.rglob("*.json"):
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except Exception:
            continue
        exp = (data.get("metadata") or {}).get("experiment_id", "")
        if exp.startswith("cf_"):
            ids.add(exp[3:])
    return ids


def run(root: Path, limit: int = 3, platforms: tuple[str, ...] = ("xhs", "wechat"),
         use_llm: bool = False, viz: bool = False, distribute: bool = False,
         analytics: bool = False) -> list[str]:
    from .factory import ContentFactory
    from .schemas import InsufficientSourceError, find_summary_path

    summaries_dir = root / "data" / "summaries"
    parsed_dir = root / "data" / "parsed"
    platforms_yaml = Path(__file__).resolve().parent / "platforms.yaml"

    staged = _staged_ids(root)
    # 取最新 N 篇未暂存的摘要
    candidates = sorted(summaries_dir.glob("*_summary.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    done: list[str] = []
    factory = ContentFactory(
        root=root, summaries_dir=summaries_dir, parsed_dir=parsed_dir,
        platforms_yaml=platforms_yaml, use_llm=use_llm,
    )
    for cand in candidates:
        pid = cand.stem.split("_summary")[0].split("_")[0]
        if pid in staged:
            continue
        try:
            result = factory.run(
                pid, platforms, viz=viz, interaction=viz,
                distribute=distribute, analytics=analytics,
            )
            factory.stage(result)
            done.append(pid)
            extra = []
            if viz:
                extra.append(f"viz×{len(result.visuals)}/ix×{len(result.interactions)}")
            if distribute:
                extra.append(f"dist×{len(result.distribution)}")
            if analytics:
                extra.append("analytics✓")
            suffix = f"（{'，'.join(extra)}）" if extra else ""
            print(f"[auto_runner] 已生成并暂存 {pid}（标题：{result.chosen_title}）{suffix}")
        except InsufficientSourceError as exc:
            print(f"[auto_runner] 跳过 {pid}：{exc}")
        except Exception as exc:  # 单篇失败不阻断其他
            print(f"[auto_runner] {pid} 异常：{exc}")
        if len(done) >= limit:
            break
    if not done:
        print("[auto_runner] 没有需要新生成的内容工厂草稿（均已暂存或源缺失）。")
    return done


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--platforms", default="xhs,wechat")
    ap.add_argument("--llm", action="store_true")
    ap.add_argument("--viz", action="store_true")
    ap.add_argument("--distribute", action="store_true")
    ap.add_argument("--analytics", action="store_true")
    args = ap.parse_args()
    plats = tuple(p.strip() for p in args.platforms.split(",") if p.strip())
    run(Path(args.root), limit=args.limit, platforms=plats,
        use_llm=args.llm, viz=args.viz, distribute=args.distribute, analytics=args.analytics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
