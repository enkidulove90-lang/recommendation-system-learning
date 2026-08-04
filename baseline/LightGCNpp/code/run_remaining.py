"""
续跑脚本：后台网格 (C3cuNW) 被杀后，补跑剩余 run 并直接做 P2 Oracle 分析。
- 补 P1_nlgcl_1e-4 seed2026（之前被中断）
- 跑 P2_oracle_L4 seeds 2024/2025/2026（L=4 + save_layer_emb 1）
- 每个 P2 种子训练完后立即跑 oracle_eval.py 产出表A/B/C
结果汇总到 results_remaining.json
"""
import os
import re
import sys
import json
import subprocess

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
PY = os.environ.get('VENV_PY')
assert PY, "set env VENV_PY"
DATASET = 'lastfm'
EPOCHS = 40
COMMON = ['--dataset', DATASET, '--alpha', '0.6', '--beta', '-0.1', '--gamma', '0.2',
          '--topks', '[20,40]', '--epochs', str(EPOCHS), '--force']

ENV = {**os.environ,
       'KMP_DUPLICATE_LIB_OK': 'TRUE',
       'OMP_NUM_THREADS': '1',
       'MKL_NUM_THREADS': '1',
       'OMP_DYNAMIC': 'FALSE'}


def config_name(label, seed, extra):
    nl = 'nl4' if label == 'P2_oracle_L4' else 'nl2'
    base = f'{DATASET}_seed{seed}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_{nl}'
    if '--use_cl' in extra:
        cl_reg = extra[extra.index('--cl_reg') + 1]
        G = extra[extra.index('--G') + 1]
        cl_temp = extra[extra.index('--cl_temp') + 1]
        cl_alpha = extra[extra.index('--cl_alpha') + 1]
        base += f'_cl{cl_reg}_G{G}_ct{cl_temp}_ca{cl_alpha}'
    return base


def run_one(label, extra, seed):
    cmd = [PY, 'main.py'] + COMMON + ['--seed', str(seed)] + extra
    proc = subprocess.run(cmd, cwd=CODE_DIR, stdout=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT, env=ENV)
    cfg = config_name(label, seed, extra)
    logf = os.path.join(CODE_DIR, 'logs', f'{cfg}.txt')
    return logf, proc.returncode


def parse(logf):
    best_r, best_n = -1, -1
    try:
        with open(logf) as f:
            for line in f:
                if line.strip().startswith('test '):
                    nums = re.findall(r'[-+]?\d*\.?\d+', line.strip()[5:])
                    if len(nums) >= 6:
                        ndcg20, recall20 = float(nums[0]), float(nums[2])
                        if ndcg20 > best_n:
                            best_n, best_r = ndcg20, recall20
    except FileNotFoundError:
        pass
    return best_r, best_n


def run_oracle(seed):
    cfg = config_name('P2_oracle_L4', seed, ['--model', 'lgn', '--layer', '4', '--save_layer_emb', '1'])
    emb = os.path.join(CODE_DIR, 'embs', f'{cfg}.pkl')
    out = os.path.join(CODE_DIR, f'oracle_seed{seed}.json')
    if not os.path.exists(emb):
        print(f'[oracle] MISSING emb for seed {seed}: {emb}', flush=True)
        return None
    proc = subprocess.run([PY, 'oracle_eval.py', '--dataset', DATASET,
                           '--emb_path', emb, '--out', out],
                          cwd=CODE_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, env=ENV)
    print(f'--- oracle seed {seed} rc={proc.returncode} ---', flush=True)
    for ln in proc.stdout.splitlines():
        if ln.startswith('>>>') or 'oracle_gain' in ln or '建议' in ln:
            print(ln, flush=True)
    try:
        with open(out) as f:
            return json.load(f)
    except Exception:
        return None


def main():
    remaining = [
        ('P1_nlgcl_1e-4', ['--model', 'lgn', '--layer', '2', '--use_cl', '1', '--G', '2',
                           '--cl_temp', '0.1', '--cl_reg', '1e-4', '--cl_alpha', '0.6']),
        ('P2_oracle_L4', ['--model', 'lgn', '--layer', '4', '--save_layer_emb', '1']),
    ]
    seeds = [2024, 2025, 2026]
    results = {}
    # 1) 补 P1_1e-4 seed2026
    label, extra = remaining[0]
    for seed in seeds:
        if label == 'P1_nlgcl_1e-4' and seed in (2024, 2025):
            continue  # 已完成
        logf, rc = run_one(label, extra, seed)
        r, n = parse(logf)
        results[f'{label}_seed{seed}'] = {'rc': rc, 'R@20': r, 'N@20': n}
        print(f'[{label} seed={seed}] rc={rc} R@20={r:.4f} N@20={n:.4f}', flush=True)
    # 2) P2 L=4 ×3
    label, extra = remaining[1]
    oracle_results = {}
    for seed in seeds:
        logf, rc = run_one(label, extra, seed)
        r, n = parse(logf)
        results[f'{label}_seed{seed}'] = {'rc': rc, 'R@20': r, 'N@20': n}
        print(f'[{label} seed={seed}] rc={rc} R@20={r:.4f} N@20={n:.4f}', flush=True)
        # 3) Oracle 分析（仅 L=4 嵌入有效）
        oracle_results[seed] = run_oracle(seed)
    # 汇总
    summary = {'p1_1e4_seed2026': results.get('P1_nlgcl_1e-4_seed2026'),
               'p2': {f'seed{s}': results.get(f'P2_oracle_L4_seed{s}') for s in seeds},
               'oracle': oracle_results}
    with open(os.path.join(CODE_DIR, 'results_remaining.json'), 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print('ALL DONE -> results_remaining.json', flush=True)


if __name__ == '__main__':
    main()
