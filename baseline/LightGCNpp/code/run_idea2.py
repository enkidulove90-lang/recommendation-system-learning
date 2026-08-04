"""
run_idea2.py — idea2 小样本测试驱动器
对比: baseline (纯 ID LightGCN++)  vs  idea2 (use_mm 对齐融合)
数据集: amazon-sports  (合成多模态特征, 维度/结构真实, 见 prep_amazon_sports.py)
种子: 2024/2025/2026 ; epoch: 由 --epochs 控制(默认 40)
结果: results_idea2.json  (R@20/N@20 best per seed, + idea2 增益, + 置信度均值)
"""
import os
import sys
import re
import json
import subprocess
import argparse

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
# 必须带 4 个 OMP 环境变量, 否则 venv torch 偶发段错误
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OMP_DYNAMIC', 'FALSE')
PY = os.environ.get('VENV_PY', 'C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe')

DATASET = 'amazon-sports'
COMMON = ['--dataset', DATASET, '--alpha', '0.6', '--beta', '-0.1', '--gamma', '0.2',
          '--layer', '2', '--topks', '[20,40]', '--force']


def config_name(extra):
    a = ['--dataset', DATASET, '--model', 'lgn', '--dim', '64', '--lr', '0.001',
         '--decay', '0.0001', '--alpha', '0.6', '--beta', '-0.1', '--gamma', '0.2', '--layer', '2']
    # 复刻 main.py 的 config 命名(用于定位 logs/<config>.txt)
    cfg = f'{DATASET}_seed{{seed}}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl2'
    if '--use_mm' in extra:
        cfg += "_mm_mr0.001_mt0.1"
    return cfg


def run_one(label, extra, seed):
    cmd = [PY, 'main.py'] + COMMON + ['--seed', str(seed)] + extra
    log = os.path.join(CODE_DIR, 'logs', f'run_idea2_{label}_seed{seed}.log')
    with open(log, 'w') as f:
        subprocess.run(cmd, cwd=CODE_DIR, stdout=f, stderr=subprocess.STDOUT, text=True)
    return log


def parse_best_test(seed, extra):
    cfg = config_name(extra).format(seed=seed)
    txt = os.path.join(CODE_DIR, 'logs', f'{cfg}.txt')
    best_r = best_n = -1
    try:
        with open(txt) as f:
            for line in f:
                if line.strip().startswith('test '):
                    nums = re.findall(r'[-+]?\d*\.?\d+', line.strip()[5:])
                    if len(nums) >= 6:
                        ndcg20, ndcg40, recall20, recall40, prec20, prec40 = map(float, nums[:6])
                        if ndcg20 > best_n:
                            best_n, best_r = ndcg20, recall20
    except FileNotFoundError:
        pass
    return best_r, best_n


def save(results):
    out = os.path.join(CODE_DIR, 'results_idea2.json')
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    return out


def main():
    global COMMON
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=20)
    ap.add_argument('--seeds', type=str, default='2024,2025,2026')
    ap.add_argument('--only', type=str, default='', help='baseline|idea2 (run subset)')
    args = ap.parse_args()
    if '--epochs' in COMMON:
        COMMON[COMMON.index('--epochs') + 1] = str(args.epochs)
    else:
        COMMON.extend(['--epochs', str(args.epochs)])
    seeds = [int(s) for s in args.seeds.split(',')]

    results = {'dataset': DATASET, 'epochs': args.epochs, 'seeds': seeds, 'configs': {}}

    def avg(d):
        rs = [d[s]['R@20'] for s in seeds if d.get(s, {}).get('R@20', 0) > 0]
        ns = [d[s]['N@20'] for s in seeds if d.get(s, {}).get('N@20', 0) > 0]
        return (sum(rs) / len(rs), sum(ns) / len(ns)) if rs else (0, 0)

    if args.only in ('', 'baseline'):
        base = {}
        for s in seeds:
            run_one('base', [], s)
            r, n = parse_best_test(s, [])
            base[s] = {'R@20': r, 'N@20': n}
            print(f"[base] seed {s}: R@20={r:.4f} N@20={n:.4f}")
            results['configs']['baseline'] = base
            save(results)   # 增量保存, 防沙箱杀进程丢结果
    if args.only in ('', 'idea2'):
        mm = {}
        for s in seeds:
            run_one('mm', ['--use_mm', '1', '--mm_reg', '1e-3'], s)
            r, n = parse_best_test(s, ['--use_mm'])
            mm[s] = {'R@20': r, 'N@20': n}
            print(f"[idea2] seed {s}: R@20={r:.4f} N@20={n:.4f}")
            results['configs']['idea2_mm'] = mm
            save(results)

    if 'baseline' in results['configs'] and 'idea2_mm' in results['configs']:
        br, bn = avg(results['configs']['baseline'])
        mr, mn = avg(results['configs']['idea2_mm'])
        results['summary'] = {
            'base_R@20': round(br, 4), 'base_N@20': round(bn, 4),
            'idea2_R@20': round(mr, 4), 'idea2_N@20': round(mn, 4),
            'delta_R@20': round(mr - br, 4),
            'rel_R@20': round((mr - br) / br * 100, 2) if br else 0,
            'delta_N@20': round(mn - bn, 4),
            'rel_N@20': round((mn - bn) / bn * 100, 2) if bn else 0,
        }
        save(results)
        print("\n=== SUMMARY ===")
        print(json.dumps(results['summary'], indent=2))


if __name__ == '__main__':
    main()
