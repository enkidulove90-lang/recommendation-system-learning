"""
aggregate_idea2.py — 从 logs/*.txt 权威重建 idea2/idea3 实验指标
================================================================
为什么需要独立聚合器:
  run_idea2.py 的 results_idea2.json 是每个 runner 进程各自 load 快照 +
  写回, 多 runner 并行时存在覆盖风险。而 main.py 写的
  logs/<config>.txt 是 append 的、每个 (config, seed) 一个文件, 永不互相
  覆盖 —— 因此它才是唯一可信的原始记录。本脚本只读这些 txt。

txt 每轮评测两行 (列序已用 results_idea2.json 反查验证):
  valid  NDCG@20  NDCG@40  Recall@20  Recall@40  Prec@20  Prec@40
  test   NDCG@20  NDCG@40  Recall@20  Recall@40  Prec@20  Prec@40
取 best = test 行中 NDCG@20 最大者 (与 run_idea2.parse_best_test 一致)。

用法:
  python aggregate_idea2.py --dataset amazon-baby-mmssl --seeds 2024,2025,2026
  python aggregate_idea2.py --dataset amazon-baby-mmssl --cost_reg 0.01 --md report.md
"""
import os
import re
import json
import argparse
import statistics

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(CODE_DIR, 'logs')

BASE_SUFFIX = 'lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl2'


def cfg_filename(dataset, seed, variant, cost_reg=0.01):
    name = f'{dataset}_seed{seed}_{BASE_SUFFIX}'
    if variant in ('idea2', 'idea3'):
        name += '_mm_mr0.001_mt0.1'
    if variant == 'idea3':
        name += f'_cr{cost_reg:.6g}'
    return os.path.join(LOG_DIR, name + '.txt')


def parse_txt(path):
    """返回 (best_dict | None, n_eval_rounds, n_distinct_rounds)."""
    if not os.path.exists(path):
        return None, 0, 0
    rows = []
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if not s.startswith('test '):
                continue
            nums = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', s[5:])
            if len(nums) >= 6:
                rows.append(tuple(float(x) for x in nums[:6]))
    if not rows:
        return None, 0, 0
    distinct = sorted(set(rows))
    best = max(rows, key=lambda r: r[0])  # 按 NDCG@20
    return ({
        'N@20': best[0], 'N@40': best[1],
        'R@20': best[2], 'R@40': best[3],
        'P@20': best[4], 'P@40': best[5],
    }, len(rows), len(distinct))


# run_idea2.py 里 run_one(label,...) 用 label 命名子日志
RUN_LABEL = {'baseline': 'base', 'idea2': 'mm', 'idea3': 'cost'}


def parse_align_diag(dataset, seed, variant):
    """从 run_idea2_{label}_seed{seed}.log 提取 G3 置信度与 G2 门控均值。

    main.py:87 在每次评测后打印:
      [idea2] conf_mean=0.088 gate={'image_feat': 0.288, 'text_feat': 0.712}
    取最后一次(训练末期)的值。对 idea3 尤为关键 —— cost_reg 正是压制
    conf, 若 idea3 的 conf_mean 显著低于 idea2, 即成本项真实生效的证据。
    """
    label = RUN_LABEL.get(variant)
    if not label:
        return None
    path = os.path.join(LOG_DIR, f'run_idea2_{label}_seed{seed}.log')
    if not os.path.exists(path):
        return None
    conf, gate = None, None
    # 关键: 子日志文件名不含 dataset (run_idea2_mm_seed2025.log 会被
    # amazon-sports 和 amazon-baby-mmssl 两次运行复用/覆盖)。必须校验日志
    # 内容确实属于本 dataset, 否则会把旧数据集的 conf_mean 张冠李戴。
    # main.py 会打印 checkpoints\lgn-<dataset>-... 与 mm_feats 路径, 均含 dataset 名。
    belongs = False
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not belongs and dataset in line:
                belongs = True
            if 'conf_mean' not in line:
                continue
            m = re.search(r'conf_mean=([\d.]+)', line)
            if m:
                conf = float(m.group(1))
            g = re.search(r'gate=\{(.*?)\}', line)
            if g:
                gate = {k: round(float(v), 4) for k, v in
                        re.findall(r"'([^']+)':\s*([\d.eE+-]+)", g.group(1))}
    if not belongs:
        return None  # 该日志属于其它数据集的旧运行, 丢弃
    if conf is None and gate is None:
        return None
    return {'conf_mean': conf, 'gate_mean': gate}


def mean_std(vals):
    if not vals:
        return None, None
    m = statistics.fmean(vals)
    s = statistics.stdev(vals) if len(vals) > 1 else 0.0
    return m, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default='amazon-baby-mmssl')
    ap.add_argument('--seeds', default='2024,2025,2026')
    ap.add_argument('--cost_reg', type=float, default=0.01)
    ap.add_argument('--expected_rounds', type=int, default=4,
                    help='20 epoch / eval每5轮 = 4 次评测, 用于判定 run 是否跑完')
    ap.add_argument('--out', default='results_idea2_aggregated.json')
    ap.add_argument('--md', default='', help='额外输出 markdown 表格到该文件')
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(',')]
    variants = [('baseline', 'baseline (纯 ID LightGCN++)'),
                ('idea2', 'idea2 (三级多模态对齐)'),
                ('idea3', f'idea3 (对齐 + 成本感知 cost_reg={args.cost_reg:g})')]

    per = {}   # variant -> seed -> metrics
    status = {}  # variant -> seed -> 'done'/'partial'/'missing'
    diag = {}   # variant -> seed -> {conf_mean, gate_mean}
    for v, _ in variants:
        per[v], status[v], diag[v] = {}, {}, {}
        for sd in seeds:
            path = cfg_filename(args.dataset, sd, v, args.cost_reg)
            best, n_rows, n_dist = parse_txt(path)
            d = parse_align_diag(args.dataset, sd, v)
            if d:
                diag[v][sd] = d
            if best is None:
                status[v][sd] = 'missing'
                continue
            per[v][sd] = best
            status[v][sd] = ('done' if n_dist >= args.expected_rounds
                             else f'partial({n_dist}/{args.expected_rounds})')

    # 聚合
    agg = {}
    for v, _ in variants:
        entry = {}
        for k in ('R@20', 'N@20', 'R@40', 'N@40'):
            vals = [per[v][sd][k] for sd in seeds if sd in per[v]]
            m, s = mean_std(vals)
            entry[k] = {'mean': m, 'std': s, 'n': len(vals)}
        agg[v] = entry

    def gain(a, b, k):
        """(a 相对 b 的相对增益 %) —— 非配对, 仅供参考"""
        ma, mb = agg[a][k]['mean'], agg[b][k]['mean']
        if not ma or not mb:
            return None
        return (ma - mb) / mb * 100.0

    def paired_gain(a, b):
        """配对对比: 只用 a、b 都跑完的公共 seed。这才是可信的增益。

        非配对均值会把"不同 seed 集合"的方差当成方法增益, 极易得出
        与事实相反的结论 (例如 baseline 有 2024+2025、idea2 只有 2024 时,
        非配对显示 idea2 +1.7%, 但同 seed 2024 上 idea2 其实是 -1.9%)。
        """
        common = [sd for sd in seeds if sd in per[a] and sd in per[b]]
        if not common:
            return {'n': 0, 'seeds': [], 'R@20': None, 'N@20': None, 'wins': None}
        res = {'n': len(common), 'seeds': common}
        for k in ('R@20', 'N@20'):
            va = statistics.fmean(per[a][sd][k] for sd in common)
            vb = statistics.fmean(per[b][sd][k] for sd in common)
            res[k] = (va - vb) / vb * 100.0 if vb else None
        res['wins'] = sum(1 for sd in common if per[a][sd]['N@20'] > per[b][sd]['N@20'])
        return res

    pairs = [('idea2', 'baseline'), ('idea3', 'baseline'), ('idea3', 'idea2')]
    gains = {f'{a}_vs_{b}': {k: gain(a, b, k) for k in ('R@20', 'N@20')} for a, b in pairs}
    paired = {f'{a}_vs_{b}': paired_gain(a, b) for a, b in pairs}

    out = {
        'dataset': args.dataset, 'seeds': seeds, 'cost_reg': args.cost_reg,
        'source': 'logs/*.txt (权威原始记录)',
        'per_seed': {v: {str(s): m for s, m in per[v].items()} for v, _ in variants},
        'status': {v: {str(s): st for s, st in status[v].items()} for v, _ in variants},
        'aggregate': agg,
        'gains_pct_unpaired': gains,
        'gains_pct_paired': paired,
        'align_diagnostics': {v: {str(s): d for s, d in diag[v].items()} for v, _ in variants},
    }
    out_path = os.path.join(CODE_DIR, args.out)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # 控制台 / markdown
    lines = []
    lines.append(f'## 实验结果聚合 — {args.dataset} ({len(seeds)} seeds x 20 epoch)\n')
    lines.append('### 各 seed 完成状态\n')
    lines.append('| 变体 | ' + ' | '.join(str(s) for s in seeds) + ' |')
    lines.append('|---|' + '---|' * len(seeds))
    for v, label in variants:
        lines.append(f'| {label} | ' + ' | '.join(status[v].get(s, 'missing') for s in seeds) + ' |')
    lines.append('\n### 逐 seed test 指标 (best by NDCG@20)\n')
    lines.append('| 变体 | seed | R@20 | N@20 | R@40 | N@40 |')
    lines.append('|---|---|---|---|---|---|')
    for v, label in variants:
        for sd in seeds:
            if sd in per[v]:
                m = per[v][sd]
                lines.append(f'| {v} | {sd} | {m["R@20"]:.4f} | {m["N@20"]:.4f} | '
                             f'{m["R@40"]:.4f} | {m["N@40"]:.4f} |')
    lines.append('\n### 均值 ± 标准差\n')
    lines.append('| 变体 | n | R@20 | N@20 |')
    lines.append('|---|---|---|---|')
    for v, label in variants:
        e = agg[v]
        if e['R@20']['n'] == 0:
            lines.append(f'| {label} | 0 | — | — |')
            continue
        lines.append(f'| {label} | {e["R@20"]["n"]} | '
                     f'{e["R@20"]["mean"]:.4f} ± {e["R@20"]["std"]:.4f} | '
                     f'{e["N@20"]["mean"]:.4f} ± {e["N@20"]["std"]:.4f} |')
    lines.append('\n### 配对相对增益 (只用双方共同完成的 seed —— 以此为准)\n')
    lines.append('| 对比 | 公共 seed | ΔR@20 | ΔN@20 | 胜出 seed 数 |')
    lines.append('|---|---|---|---|---|')
    for k, g in paired.items():
        if g['n'] == 0:
            lines.append(f'| {k} | 0 | — | — | — |')
            continue
        r, n = g['R@20'], g['N@20']
        lines.append(f'| {k} | {g["n"]} ({",".join(str(s) for s in g["seeds"])}) | ' +
                     (f'{r:+.2f}%' if r is not None else '—') + ' | ' +
                     (f'{n:+.2f}%' if n is not None else '—') +
                     f' | {g["wins"]}/{g["n"]} |')
    lines.append('\n### 非配对相对增益 (seed 集合不同时不可信, 仅存档)\n')
    lines.append('| 对比 | ΔR@20 | ΔN@20 |')
    lines.append('|---|---|---|')
    for k, g in gains.items():
        r, n = g['R@20'], g['N@20']
        lines.append(f'| {k} | ' +
                     (f'{r:+.2f}%' if r is not None else '—') + ' | ' +
                     (f'{n:+.2f}%' if n is not None else '—') + ' |')
    has_diag = any(diag[v] for v, _ in variants)
    if has_diag:
        lines.append('\n### 对齐诊断 (G3 置信度 / G2 门控, 训练末期)\n')
        lines.append('| 变体 | seed | conf_mean | gate_mean |')
        lines.append('|---|---|---|---|')
        for v, _ in variants:
            for sd in seeds:
                d = diag[v].get(sd)
                if not d:
                    continue
                cm = f'{d["conf_mean"]:.4f}' if d.get('conf_mean') is not None else '—'
                gm = (', '.join(f'{k}={val:.3f}' for k, val in d['gate_mean'].items())
                      if d.get('gate_mean') else '—')
                lines.append(f'| {v} | {sd} | {cm} | {gm} |')
        # idea3 成本项是否真实压低了知识引入率
        c2 = [diag['idea2'][s]['conf_mean'] for s in seeds
              if diag['idea2'].get(s, {}).get('conf_mean') is not None]
        c3 = [diag['idea3'][s]['conf_mean'] for s in seeds
              if diag['idea3'].get(s, {}).get('conf_mean') is not None]
        if c2 and c3:
            m2, m3 = statistics.fmean(c2), statistics.fmean(c3)
            delta = (m3 - m2) / m2 * 100 if m2 else float('nan')
            lines.append(f'\n> **成本项有效性**: idea2 conf_mean={m2:.4f} → '
                         f'idea3 conf_mean={m3:.4f} ({delta:+.1f}%)。'
                         + ('成本项确实压低了知识引入率。' if m3 < m2
                            else '成本项未压低知识引入率, 需检查 cost_reg 量级。'))

    text = '\n'.join(lines)
    print(text)
    print(f'\n[saved] {out_path}')
    if args.md:
        md_path = os.path.join(CODE_DIR, args.md)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
        print(f'[saved] {md_path}')


if __name__ == '__main__':
    main()
