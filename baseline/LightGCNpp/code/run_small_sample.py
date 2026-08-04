"""
Small-sample test harness for the P0->P1->P2 plan.

Runs LightGCN++ baseline (P0), NLGCL variants (P1), and an L=4 oracle model (P2)
across 3 seeds (2024/2025/2026) on lastfm, with a small epoch budget.
Collects Recall@20 / NDCG@20 into results_small_sample.json and prints a summary.

Usage:
  python run_small_sample.py
(assumes it is run from the code/ directory, or set CODE_DIR below)
"""
import os
import re
import json
import subprocess
import glob
import sys

# --- Windows OpenMP / MKL conflict fix (avoid flaky segfault on torch import) ---
for _k, _v in [('KMP_DUPLICATE_LIB_OK', 'TRUE'), ('OMP_NUM_THREADS', '1'),
               ('MKL_NUM_THREADS', '1'), ('OMP_DYNAMIC', 'FALSE')]:
    os.environ[_k] = _v

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
PY = os.environ.get('VENV_PY')  # set by caller
assert PY, "set env VENV_PY to the python executable"

DATASET = 'lastfm'
SEEDS = [2024, 2025, 2026]
EPOCHS = 40
COMMON = [
    '--dataset', DATASET, '--alpha', '0.6', '--beta', '-0.1', '--gamma', '0.2',
    '--topks', '[20,40]', '--epochs', str(EPOCHS), '--force',
]

# configs: (label, extra_args)
CONFIGS = [
    ('P0_baseline', ['--model', 'lgn', '--layer', '2']),
    ('P1_nlgcl_5e-5', ['--model', 'lgn', '--layer', '2', '--use_cl', '1', '--G', '2',
                        '--cl_temp', '0.1', '--cl_alpha', '0.6', '--cl_reg', '5e-5']),
    ('P1_nlgcl_1e-4', ['--model', 'lgn', '--layer', '2', '--use_cl', '1', '--G', '2',
                        '--cl_temp', '0.1', '--cl_alpha', '0.6', '--cl_reg', '1e-4']),
    ('P2_oracle_L4', ['--model', 'lgn', '--layer', '4', '--save_layer_emb', '1']),
]


def run_one(label, extra, seed):
    cmd = [PY, 'main.py'] + COMMON + ['--seed', str(seed)] + extra
    log = os.path.join(CODE_DIR, 'logs', f'run_{label}_seed{seed}.log')
    with open(log, 'w') as f:
        proc = subprocess.run(cmd, cwd=CODE_DIR, stdout=f, stderr=subprocess.STDOUT,
                              text=True)
    return log, proc.returncode


def config_name(label, seed):
    """Replicate main.py's config-string construction so we can read its log file."""
    base = f'lastfm_seed{seed}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2'
    if label == 'P2_oracle_L4':
        return base + '_nl4'
    if label == 'P1_nlgcl_5e-5':
        return base + '_nl2_cl5e-05_G2_ct0.1_ca0.6'
    if label == 'P1_nlgcl_1e-4':
        return base + '_nl2_cl0.0001_G2_ct0.1_ca0.6'
    return base + '_nl2'  # P0_baseline


def parse_best_test(label, seed):
    """Parse logs/<config>.txt written by main.py; return (recall20, ndcg20)."""
    cfg = config_name(label, seed)
    # CL suffix may render slightly differently; glob to be safe
    candidates = glob.glob(os.path.join(CODE_DIR, 'logs', f'*seed{seed}*.txt'))
    target = None
    for c in candidates:
        bn = os.path.basename(c)
        if bn == cfg + '.txt':
            target = c
            break
    if target is None:
        # fallback: match nl level
        nl = 'nl4' if label == 'P2_oracle_L4' else 'nl2'
        for c in candidates:
            bn = os.path.basename(c)
            if f'seed{seed}' in bn and nl in bn and bn.endswith('.txt'):
                target = c
                break
    if target is None:
        return -1, -1
    best_r, best_n = -1, -1
    with open(target) as f:
        for line in f:
            if line.strip().startswith('test '):
                nums = re.findall(r'[-+]?\d*\.?\d+', line.strip()[5:])
                if len(nums) >= 4:
                    ndcg20, _n40, recall20, _r40 = map(float, nums[:4])
                    if ndcg20 > best_n:
                        best_n, best_r = ndcg20, recall20
    return best_r, best_n


def main():
    results = {}
    for label, extra in CONFIGS:
        per_seed = []
        for seed in SEEDS:
            log, rc = run_one(label, extra, seed)
            r, n = parse_best_test(label, seed)
            per_seed.append({'seed': seed, 'recall20': r, 'ndcg20': n, 'rc': rc, 'log': os.path.basename(log)})
            print(f'[{label} seed={seed}] rc={rc} R@20={r:.4f} N@20={n:.4f}')
        results[label] = per_seed

    # aggregate
    summary = {}
    for label, recs in results.items():
        rs = [x['recall20'] for x in recs if x['recall20'] >= 0]
        ns = [x['ndcg20'] for x in recs if x['ndcg20'] >= 0]
        if rs:
            summary[label] = {'recall20_mean': sum(rs)/len(rs), 'recall20_std': (sum((x-sum(rs)/len(rs))**2 for x in rs)/len(rs))**0.5,
                              'ndcg20_mean': sum(ns)/len(ns), 'ndcg20_std': (sum((x-sum(ns)/len(ns))**2 for x in ns)/len(ns))**0.5,
                              'n': len(rs)}
    out = os.path.join(CODE_DIR, 'results_small_sample.json')
    with open(out, 'w') as f:
        json.dump({'results': results, 'summary': summary}, f, indent=2)
    print('\n========== SUMMARY (mean over', len(SEEDS), 'seeds) ==========')
    for label, s in summary.items():
        print(f'{label:18s} R@20={s["recall20_mean"]:.4f}±{s["recall20_std"]:.4f}  N@20={s["ndcg20_mean"]:.4f}±{s["ndcg20_std"]:.4f}')
    print(f'\n[done] -> {out}')


if __name__ == '__main__':
    main()
