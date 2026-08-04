"""
aggregate_idea2.py — 从 logs/{config}.txt 稳健重建 idea2 结果(不依赖可能被并发覆盖的 json)
匹配: amazon-sports_seed{seed}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl2[.txt]
       idea2 版多 _mm_mr0.001_mt0.1 后缀
取每个 seed 的最佳 N@20 / R@20(测试期), 计算均值与相对增益, 并收集 idea2 置信度日志。
"""
import os
import re
import json
import glob

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET = 'amazon-sports'


def best_of(txt_path):
    best_r = best_n = -1
    try:
        with open(txt_path) as f:
            for line in f:
                if line.strip().startswith('test '):
                    nums = re.findall(r'[-+]?\d*\.?\d+', line.strip()[5:])
                    if len(nums) >= 6:
                        ndcg20, ndcg40, recall20, recall40, prec20, prec40 = map(float, nums[:6])
                        if ndcg20 > best_n:
                            best_n, best_r = ndcg20, recall20
    except FileNotFoundError:
        return None, None
    return (best_r, best_n) if best_r > 0 else (None, None)


def conf_of(log_path):
    """从 run_idea2 子日志提取 idea2 置信度均值(取最后一次出现的 [idea2] conf_mean)。"""
    try:
        with open(log_path) as f:
            last = None
            for line in f:
                if '[idea2] conf_mean' in line:
                    m = re.search(r'conf_mean=([\d.]+)', line)
                    if m:
                        last = float(m.group(1))
            return last
    except FileNotFoundError:
        return None


def main():
    files = glob.glob(os.path.join(CODE_DIR, 'logs', f'{DATASET}_seed*_lgn_dim64_*.txt'))
    base, mm = {}, {}
    seeds = set()
    for fp in files:
        base_name = os.path.basename(fp)
        m = re.search(r'seed(\d+)_', base_name)
        if not m:
            continue
        seed = int(m.group(1))
        seeds.add(seed)
        is_mm = '_mm_' in base_name
        r, n = best_of(fp)
        if is_mm:
            mm[seed] = {'R@20': r, 'N@20': n}
        else:
            base[seed] = {'R@20': r, 'N@20': n}

    seeds = sorted(seeds)

    def avg(d):
        rs = [d[s]['R@20'] for s in seeds if d.get(s, {}).get('R@20')]
        ns = [d[s]['N@20'] for s in seeds if d.get(s, {}).get('N@20')]
        return (sum(rs) / len(rs), sum(ns) / len(ns)) if rs else (0, 0)

    br, bn = avg(base)
    mr, mn = avg(mm)
    summary = {
        'dataset': DATASET,
        'seeds': seeds,
        'baseline': base,
        'idea2_mm': mm,
        'base_R@20': round(br, 4), 'base_N@20': round(bn, 4),
        'idea2_R@20': round(mr, 4), 'idea2_N@20': round(mn, 4),
        'delta_R@20': round(mr - br, 4),
        'rel_R@20': round((mr - br) / br * 100, 2) if br else 0,
        'delta_N@20': round(mn - bn, 4),
        'rel_N@20': round((mn - bn) / bn * 100, 2) if bn else 0,
    }
    out = os.path.join(CODE_DIR, 'results_idea2.json')
    with open(out, 'w') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"saved -> {out}")


if __name__ == '__main__':
    main()
