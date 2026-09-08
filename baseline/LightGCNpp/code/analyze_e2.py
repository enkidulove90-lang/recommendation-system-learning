"""E2 后处理: 提取 conf_mean@最优 test epoch 与 R@20, 对比 baseline / fc0.8。

依赖:
  - 训练 wrapper 日志: logs/run_idea2_mm_mcr0_seed{S}.log  (含 [idea2] conf_mean= 与 EPOCH[N/20])
  - 评估 txt:          logs/amazon-baby-mmssl_seed{S}_*_mcr0.txt (含 test N@20 N@40 R@20 ...)

关键口径修正: conf_mean 取「最优 test epoch」处的值(而非 ep5), 否则会被瞬时值误导
(此前误判 v3 有效就栽在 ep5 的 0.169 上, 实际 ep10 已塌到 0.046)。
"""
import os
import re
import json
import glob

CODE = os.path.dirname(os.path.abspath(__file__))
SEEDS = [2024, 2025, 2026]
BASELINE = 0.08362   # 3-seed 纯 ID LightGCN++ baseline 均值 R@20
FC08 = 0.08800       # E1 最优档 fc0.8 均值 R@20


def analyze_seed(seed):
    """conf_mean 与 test R@20 均直接从 wrapper 日志解析。

    注意: run_idea2.py 实际未给 eval txt 加 `_mcr0` 后缀, E2 的 test 行被 append 进了
    v3 的同名 txt (amazon-baby-mmssl_seed{S}_..._mt0.1.txt), 与旧记录混杂。
    因此不能依赖 txt, 必须以 wrapper 日志中的 [TEST] recall 数组为准。
    """
    log = os.path.join(CODE, 'logs', f'run_idea2_mm_mcr0_seed{seed}.log')
    conf_by_epoch = {}
    r20_by_epoch = {}
    cur = None
    pending_test = False
    if os.path.exists(log):
        with open(log) as f:
            for line in f:
                m = re.search(r'EPOCH\[(\d+)/20\]', line)
                if m:
                    cur = int(m.group(1))
                cm = re.search(r'\[idea2\] conf_mean=([\d.]+)', line)
                if cm and cur is not None:
                    conf_by_epoch[cur] = float(cm.group(1))
                if '[TEST]' in line:  # 日志含 ANSI 色码, 不能用 startswith
                    pending_test = True
                    continue
                if pending_test:
                    rc = re.search(r"'recall':\s*array\(\[\s*([\d.eE+-]+)", line)
                    if rc and cur is not None:
                        r20_by_epoch[cur] = float(rc.group(1))
                        pending_test = False
                    elif line.strip():
                        pending_test = False
    pairs = [(ep, conf_by_epoch.get(ep), r20) for ep, r20 in sorted(r20_by_epoch.items())]
    if not pairs:
        return None
    bi = max(range(len(pairs)), key=lambda j: pairs[j][2])
    ep, conf, r20 = pairs[bi]
    return {'best_epoch': ep, 'best_r20': r20, 'best_conf': conf, 'pairs': pairs}


def main():
    rows = []
    for s in SEEDS:
        r = analyze_seed(s)
        if r:
            rows.append((s, r))
    if not rows:
        print("E2: 未找到任何 seed 日志, 可能 E2 尚未开始或路径错误")
        return
    print("\n===== E2 (idea2 + mm_conf_reg=0) 结果 =====")
    print(f"{'seed':>6} | {'best_ep':>7} | {'R@20@best':>10} | {'conf@best':>10} | vs_base | vs_fc0.8")
    r20s, confs = [], []
    for s, r in rows:
        r20s.append(r['best_r20'])
        confs.append(r['best_conf'] if r['best_conf'] is not None else float('nan'))
        db = (r['best_r20'] - BASELINE) / BASELINE * 100
        df = (r['best_r20'] - FC08) / FC08 * 100
        cf = f"{r['best_conf']:.4f}" if r['best_conf'] is not None else "  n/a"
        print(f"{s:>6} | {r['best_epoch']:>7} | {r['best_r20']:>10.4f} | {cf:>10} | {db:+6.1f}% | {df:+6.1f}%")
    mr = sum(r20s) / len(r20s)
    mc = sum(c for c in confs if c == c) / max(1, sum(1 for c in confs if c == c))
    print(f"{'MEAN':>6} | {'-':>7} | {mr:>10.4f} | {mc:>10.4f} | {(mr-BASELINE)/BASELINE*100:+6.1f}% | {(mr-FC08)/FC08*100:+6.1f}%")
    print(f"\nbaseline(3-seed)={BASELINE:.4f}   fc0.8(E1最优)={FC08:.4f}")

    print("\n----- 判定 -----")
    if mc >= 0.3:
        print(f"[OK] conf_mean 在最优 test epoch 抬升到 {mc:.3f} (>=0.3): conf_reg 确为压制 c 的主因 -> 机制修复方向正确")
    else:
        print(f"[WARN] conf_mean 仍仅 {mc:.3f} (<0.3): c 依旧塌缩, 嫌疑转向 BPR/成本税 -> 上 E6 全局预算")
    if mr >= FC08 * 0.99:
        print(f"[OK] R@20={mr:.4f} 逼近 fc0.8({FC08:.4f}): 机制修复闭环, 走 Phase A 深化")
    else:
        print(f"[WARN] R@20={mr:.4f} 未逼近 fc0.8: 即便去掉 conf_reg 仍无增益, 需重新审视对齐信号(E3)")

    out = {'mean_r20': mr, 'mean_conf': mc, 'baseline': BASELINE, 'fc08': FC08,
           'seeds': {str(s): r for s, r in rows}}
    with open(os.path.join(CODE, 'logs', 'e2_analysis.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print("\n已写入 logs/e2_analysis.json")


if __name__ == '__main__':
    main()
