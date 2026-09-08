#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
peek_e6.py — E6 运行中速览（不等跑完，随时可看）

用途: analyze_e6.py 只在全部跑完后出终判; 跑的过程中想看"现在到哪了、
      和 fc0.8 同期比如何", 用这个。

它解决三件事:
  1. 从 wrapper 日志直接解析 test R@20 轨迹(不依赖 eval txt, 因为 txt 是 append 的会新旧混杂)
  2. conf 取 FRESH 值，缓存值只作滞后诊断 —— 详见 mm_align.refresh_proj
     (正式口径已从 _ef1 换成 _pr32: 训练途中每 32 batch 刷新投影, 而非只在 eval 前刷。
      _ef1 已证伪, 会造成训练/评测错配, 见 analyze_e6.py 坑 5)
  3. **同期对比**: E6 起步比 fc0.8 低是正常的(前几个 epoch 对偶乘子还在爬),
     所以不能只看绝对值, 要看同 epoch 对比 + 增长斜率

坑位备忘:
  - 日志含 ANSI 色码 -> 判 [TEST] 必须用 `in`, 不能 startswith
  - 每个 eval 点先打 [VALIDATION] 再打 [TEST], 各跟一行 dict; 只取 [TEST] 后那行
  - topks=[20,40] -> recall 数组第 0 个才是 R@20
"""
import re
import os
import glob

LOGDIR = "logs"
EVAL_EVERY = 5

# (标签, 日志文件名 glob, 说明)
CURVES = [
    ("E1 fc0.8",   "run_idea2_mm_fc0.8_seed{s}.log",                    "强制融合 靶子(旧缓存口径)"),
    ("E1 fc1.0",   "run_idea2_mm_fc1_seed{s}.log",                      "强制全融合"),
    ("E2 mcr0",    "run_idea2_mm_mcr0_seed{s}.log",                     "关 conf_reg, c 塌缩"),
    ("A0 fc0.8pr", "run_idea2_mm_fc0.8_pr32_seed{s}.log",                "fc0.8 同口径重测 = 真靶子"),
    ("A  E6 t0.8", "run_idea2_mm_mcr0_mb0.8l1d0.05_pr32_seed{s}.log",    "主实验 增广拉格朗日"),
    ("B  E6 t0.2", "run_idea2_mm_mcr0_mb0.2l1d0.05_pr32_seed{s}.log",    "低档 双向控制验证"),
    ("B  E6 t0.6", "run_idea2_mm_mcr0_mb0.6l1d0.05_pr32_seed{s}.log",    "中档"),
    ("C  soft0.8", "run_idea2_mm_mcr0_mb0.8l1_pr32_seed{s}.log",         "无对偶 软惩罚对照"),
]

REC_RE = re.compile(r"recall.{0,4}:\s*array\(\[\s*([0-9.eE+-]+)")
FRESH_RE = re.compile(r"FRESH conf_mean=([0-9.]+)\s+conf_std=([0-9.]+)")
CACHED_RE = re.compile(r"\[idea2\] conf_mean=([0-9.]+)\s+conf_std=([0-9.]+)")
BATCH_RE = re.compile(r"batch_c=([0-9.]+)\s+budget_loss=([-0-9.eE]+)")
EPOCH_RE = re.compile(r"EPOCH\[(\d+)/(\d+)\]")


def parse_log(path):
    """返回 dict: recalls[], fresh[], cached[], batch_c[], last_epoch, total_epoch"""
    if not os.path.exists(path):
        return None
    out = {"recalls": [], "fresh": [], "cached": [], "batch": [],
           "last_ep": 0, "total_ep": 0}
    want_test = False
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = EPOCH_RE.search(line)
            if m:
                out["last_ep"] = int(m.group(1))
                out["total_ep"] = int(m.group(2))
            if "[TEST]" in line:          # ANSI 色码 -> 必须用 in
                want_test = True
                continue
            if want_test:
                mm = REC_RE.search(line)
                if mm:
                    out["recalls"].append(float(mm.group(1)))
                    want_test = False
                continue
            mf = FRESH_RE.search(line)
            if mf:
                out["fresh"].append((float(mf.group(1)), float(mf.group(2))))
                continue
            mc = CACHED_RE.search(line)
            if mc:
                out["cached"].append((float(mc.group(1)), float(mc.group(2))))
            mb = BATCH_RE.search(line)
            if mb:
                out["batch"].append((float(mb.group(1)), float(mb.group(2))))
    return out


def fmt_traj(vals, width=8):
    return " ".join(f"{v:.5f}".rjust(width) for v in vals) if vals else "  (无)"


def main():
    seeds = ["2024", "2025", "2026"]
    print("=" * 78)
    print("E6 运行中速览   (R@20 轨迹, 每 %d epoch 一个点)" % EVAL_EVERY)
    print("=" * 78)

    found_any = False
    ref_curve = None   # 同口径靶子, 用于同期对比

    for label, pat, note in CURVES:
        for s in seeds:
            path = os.path.join(LOGDIR, pat.format(s=s))
            d = parse_log(path)
            if not d or (not d["recalls"] and d["last_ep"] == 0):
                continue
            found_any = True
            prog = f"ep{d['last_ep']}/{d['total_ep']}" if d["total_ep"] else "?"
            head = f"{label} s{s}"
            print(f"\n[{head:<18}] {prog:<9} {note}")
            print(f"   R@20 : {fmt_traj(d['recalls'])}")

            if d["fresh"]:
                fm, fs = d["fresh"][-1]
                cm, cs = d["cached"][-1] if d["cached"] else (float('nan'), float('nan'))
                flag = "OK" if fm >= 0.6 else "!! <0.6"
                disc = "OK" if fs > 0.02 else "!! std过小,退化成force_c"
                print(f"   conf : FRESH={fm:.3f}(std {fs:.3f}) {flag} {disc}"
                      f"   | 缓存={cm:.3f} 滞后 {fm - cm:+.3f}")
            elif d["cached"]:
                cm, cs = d["cached"][-1]
                print(f"   conf : 缓存={cm:.3f}(std {cs:.3f})  [该跑未开 --mm_proj_refresh, 值滞后不可信]")

            if d["batch"]:
                bc, bl = d["batch"][-1]
                print(f"   预算 : batch_c={bc:.3f} budget_loss={bl:+.4f}")

            # 记录靶子(优先同口径 A0, 退而求其次旧 fc0.8)
            if label.startswith("A0") and s == "2024":
                ref_curve = ("A0 fc0.8pr32", d["recalls"])
            elif ref_curve is None and label.startswith("E1 fc0.8") and s == "2024":
                ref_curve = ("E1 fc0.8(旧口径)", d["recalls"])

    if not found_any:
        print("\n  还没有任何日志产出。")
        return

    # ---- 同期对比: E6 起步慢是预期的, 关键看斜率 ----
    e6 = parse_log(os.path.join(LOGDIR,
                   "run_idea2_mm_mcr0_mb0.8l1d0.05_pr32_seed2024.log"))
    if ref_curve and e6 and e6["recalls"]:
        rname, rvals = ref_curve
        print("\n" + "-" * 78)
        print(f"同期对比  E6 t0.8 s2024  vs  {rname}")
        print("-" * 78)
        n = min(len(rvals), len(e6["recalls"]))
        for i in range(n):
            ep = (i + 1) * EVAL_EVERY
            a, b = e6["recalls"][i], rvals[i]
            print(f"  ep{ep:<3} E6={a:.5f}  ref={b:.5f}  差 {(a/b-1)*100:+6.2f}%")
        if n >= 2:
            sa = (e6["recalls"][n-1] / e6["recalls"][0] - 1) * 100
            sb = (rvals[n-1] / rvals[0] - 1) * 100
            print(f"\n  ep{EVAL_EVERY}->ep{n*EVAL_EVERY} 增幅:  E6 {sa:+.2f}%   ref {sb:+.2f}%")
            print("  " + ("E6 爬升更快, 起步低不代表终点低, 继续观察"
                          if sa > sb else
                          "E6 爬升不占优, 若 ep15 仍落后需考虑 dual_eta/预热调整"))
        if len(rvals) > n:
            print(f"\n  (ref 已跑完 {len(rvals)*EVAL_EVERY} ep, 终值 {rvals[-1]:.5f}; "
                  f"E6 还在 ep{e6['last_ep']})")

    print("\n提示: 终判以 analyze_e6.py 为准(全部跑完后自动执行)。")


if __name__ == "__main__":
    main()
