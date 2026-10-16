# -*- coding: utf-8 -*-
"""独立复核 E15 的 A / T / TF 三组 best R@20（用于 PRISM 结题报告数字审计）。

日志为 UTF-16LE（含 NUL），先按字节剥掉 \\x00 再解码。
输出写到 e15_numbers_audit.txt（UTF-8），避免控制台编码问题。

用法：python verify_e15_numbers.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "baseline" / "PRISM" / "logs"
OUT = ROOT / "e15_numbers_audit.txt"

# 结题报告（docs/prism_conclusion_report.md §4）声称的值，用于对比
CLAIM = {
    ("A", "42"): {"first": 0.0408, "max": 0.0408},
    ("A", "2025"): {"first": 0.0377, "max": 0.0377},
    ("T", "42"): {"first": 0.0361, "max": 0.0361},
    ("T", "2025"): {"first": 0.0393, "max": 0.0393},
    ("TF", "42"): {"first": 0.0379, "max": 0.0393},
    ("TF", "2025"): {"first": 0.0376, "max": 0.0406},
}

EVAL_ROW = re.compile(r"\{[^{}]*'Epoch'[^{}]*\}")
RECALL20 = re.compile(r"'Recall@20':\s*'([0-9.]+)'")
NDCG20 = re.compile(r"'NDCG@20':\s*'([0-9.]+)'")


def load(p: Path) -> str:
    return p.read_bytes().replace(b"\x00", b"").decode("utf-8", "ignore")


def main() -> int:
    lines: list[str] = []

    def say(s: str = "") -> None:
        lines.append(s)

    say("E15 三组数字独立复核（源：baseline/PRISM/logs/e15_*.log）")
    say("=" * 72)
    buckets: dict[tuple[str, str], dict] = {}

    for group in ("A", "T", "TF"):
        for seed in ("42", "2025"):
            p = LOGS / f"e15_{group}_seed{seed}.log"
            if not p.exists():
                say(f"!! 缺失 {p}")
                continue
            raw = load(p)
            rows = EVAL_ROW.findall(raw)
            best = [r for r in rows if "'best'" in r]
            all_r = [float(m.group(1)) for r in rows if (m := RECALL20.search(r))]
            best_r = [float(m.group(1)) for r in best if (m := RECALL20.search(r))]
            best_n = [float(m.group(1)) for r in best if (m := NDCG20.search(r))]
            first = best_r[0] if best_r else None
            mx = max(all_r) if all_r else None
            buckets[(group, seed)] = {"first": first, "max_best": max(best_r) if best_r else None, "max_all": mx}
            claim = CLAIM.get((group, seed), {})
            say(f"\n[{group}] seed{seed}  rows={len(rows)}  best_rows={len(best_r)}")
            say(f"   best 行 R@20 依次 = {best_r}")
            say(f"   best 行 N@20 依次 = {best_n}")
            say(f"   全量最大 R@20（含非 best 行） = {mx}")
            say(f"   报告声称 first={claim.get('first')} / max={claim.get('max')}")
            ok_first = first is not None and abs(first - claim.get("first", -1)) < 5e-5
            ok_max = mx is not None and abs(mx - claim.get("max", -1)) < 5e-5
            say(f"   -> first 一致: {'OK' if ok_first else 'MISMATCH'}"
                f" | 全量最大一致: {'OK' if ok_max else 'MISMATCH'}")

    say("\n" + "=" * 72)
    say("判据复核（TF 须同 seed 同时 > A 且 > T）")
    for seed in ("42", "2025"):
        a = buckets.get(("A", seed), {}).get("first")
        t = buckets.get(("T", seed), {}).get("first")
        tf = buckets.get(("TF", seed), {}).get("first")
        if None in (a, t, tf):
            say(f"  seed{seed}: 数据不全，跳过")
            continue
        say(f"  seed{seed}: TF={tf} vs A={a} ({'>' if tf > a else '<'}) vs T={t} ({'>' if tf > t else '<'})"
            f" -> {'PASS' if (tf > a and tf > t) else 'FAIL'}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("written ->", OUT.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
