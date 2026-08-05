"""
run_idea2.py — idea2 / idea3 小样本测试驱动器
对比: baseline (纯 ID LightGCN++)  vs  idea2 (use_mm 对齐融合)  vs  idea3 (idea2 + 成本感知门控)
数据集: amazon-sports  (合成多模态特征, 维度/结构真实, 见 prep_amazon_sports.py)
种子: 2024/2025/2026 ; epoch: 由 --epochs 控制
结果: results_idea2.json  (R@20/N@20 best per seed, + 增益)

用法:
  python run_idea2.py --only baseline --epochs 20 --seeds 2024,2025,2026
  python run_idea2.py --only idea2    --epochs 20 --seeds 2024,2025,2026
  python run_idea2.py --only idea3 --cost_reg 0.01 --epochs 20 --seeds 2024,2025,2026
"""
import os
import sys
import re
import json
import subprocess
import argparse
import atexit

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


LOCK_DIR = os.path.join(CODE_DIR, 'logs')


def acquire_lock(key):
    """单实例去重改由外部(host 侧 PowerShell)在启动后按 key 杀掉重复 runner 实现。

    原因: 后台框架为同一命令起 2 份副本, 且副本处于相互不可见的隔离环境
    (独立 FS overlay + 可能独立的 PID 命名空间), 进程内基于 wmic/O_EXCL 的锁
    无法稳定协调(实测: 2x 副本均存活 / 或两副本均退出)。两份副本执行完全相同的
    工作, 因此外部在启动后 ~10s 杀掉每 key 的多余 runner(保留最早启动者)即可
    保证恰好一份存活, 且不损失进度(幸存者从头跑完整训练)。
    """
    return None


def config_name(extra):
    """复刻 main.py 的 config 命名(用于定位 logs/<config>.txt)."""
    cfg = f'{DATASET}_seed{{seed}}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl2'
    if '--use_mm' in extra:
        cfg += "_mm_mr0.001_mt0.1"
        # idea3: cost-aware weight (与 main.py 的 _cr{world.args.cost_reg} 对齐)
        if '--cost_reg' in extra:
            i = extra.index('--cost_reg')
            cr = extra[i + 1]
            if float(cr) > 0:
                cfg += f"_cr{cr}"
        if '--force_c' in extra:
            i = extra.index('--force_c')
            fc = extra[i + 1]
            if float(fc) > 0:
                cfg += f"_fc{fc}"
    return cfg


def run_one(label, extra, seed):
    cmd = [PY, '-u', 'main.py'] + COMMON + ['--seed', str(seed)] + extra
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
    """并发安全的增量落盘: 读-改-写合并 + 原子替换。

    多个 runner (baseline / idea2 / idea3) 可能同时运行, 各自在启动时
    load 了一份 prior 快照。若直接全量覆盖写, 最后落盘者会抹掉其他
    runner 期间新增的 config/seed。这里改为每次写盘前重读磁盘最新内容,
    按 configs[config][seed] 粒度合并后再写, 保证互不覆盖。
    """
    out = os.path.join(CODE_DIR, 'results_idea2.json')
    try:
        with open(out) as f:
            disk = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        disk = {}

    merged = {
        'dataset': results.get('dataset', disk.get('dataset')),
        'epochs': results.get('epochs', disk.get('epochs')),
        'seeds': results.get('seeds', disk.get('seeds')),
        'configs': {},
    }
    # 磁盘在前、本进程在后 —— 本进程的新结果优先
    for src in (disk, results):
        for cfg_k, seed_map in (src.get('configs') or {}).items():
            merged['configs'].setdefault(cfg_k, {})
            for seed_k, metrics in (seed_map or {}).items():
                merged['configs'][cfg_k][str(seed_k)] = metrics
    # summary_* 字段同理合并
    for src in (disk, results):
        for k, v in src.items():
            if k.startswith('summary'):
                merged[k] = v

    tmp = out + f'.tmp{os.getpid()}'
    with open(tmp, 'w') as f:
        json.dump(merged, f, indent=2)
    os.replace(tmp, out)  # Windows 上亦为原子替换
    return out


def main():
    global COMMON
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=20)
    ap.add_argument('--seeds', type=str, default='2024,2025,2026')
    ap.add_argument('--only', type=str, default='', help='baseline|idea2|idea3 (run subset)')
    ap.add_argument('--dataset', type=str, default='amazon-sports',
                    help='dataset dir under ../data/ (e.g. amazon-sports | amazon-baby-mmssl)')
    ap.add_argument('--cost_reg', type=float, default=0.01,
                    help='idea3 cost weight on knowledge-introduction rate; ignored unless --only idea3')
    ap.add_argument('--cost_target', type=float, default=0.0,
                    help='idea3 budget target rate for c_i.mean(); 0=pure tax, >0=budget mode')
    ap.add_argument('--force_c', type=float, default=0.0,
                    help='E1 forced-fusion: freeze c=force_c; 0=learned (default)')
    args = ap.parse_args()
    global DATASET
    DATASET = args.dataset
    COMMON[COMMON.index('--dataset') + 1] = DATASET
    seeds = [int(s) for s in args.seeds.split(',')]
    cr_str = f"{args.cost_reg:.6g}"
    ct_str = f"{args.cost_target:.6g}"
    fc_str = f"{args.force_c:.6g}"
    # 单实例锁: 防止框架重复启动多份 runner 竞争写同一日志
    # force_c 感知: 不同 force_c 视为不同实验, 互不锁定(否则 E1 并行会被串行化)
    lock_key = f"{DATASET}__{args.only or 'all'}" + (f"_fc{fc_str}" if args.force_c > 0 else "")
    acquire_lock(lock_key)
    if '--epochs' in COMMON:
        COMMON[COMMON.index('--epochs') + 1] = str(args.epochs)
    else:
        COMMON.extend(['--epochs', str(args.epochs)])

    results = {'dataset': DATASET, 'epochs': args.epochs, 'seeds': seeds, 'configs': {}}

    # 载入已有结果, 使 idea3 能直接对比 baseline / idea2_mm
    try:
        with open(os.path.join(CODE_DIR, 'results_idea2.json')) as f:
            prior = json.load(f)
            for k, v in prior.get('configs', {}).items():
                results['configs'].setdefault(k, v)
    except (FileNotFoundError, json.JSONDecodeError):
        prior = {'configs': {}}

    def avg(d):
        rs = [d[s]['R@20'] for s in seeds if d.get(s, {}).get('R@20', 0) > 0]
        ns = [d[s]['N@20'] for s in seeds if d.get(s, {}).get('N@20', 0) > 0]
        return (sum(rs) / len(rs), sum(ns) / len(ns)) if rs else (0, 0)

    def run_block(key, label, extra):
        d = {}
        for s in seeds:
            run_one(label, extra, s)
            r, n = parse_best_test(s, extra)
            d[s] = {'R@20': r, 'N@20': n}
            print(f"[{label}] seed {s}: R@20={r:.4f} N@20={n:.4f}")
            results['configs'][key] = d
            save(results)   # 增量保存, 防沙箱杀进程丢结果
        return d

    if args.only in ('', 'baseline'):
        run_block('baseline', 'base', [])
    if args.only in ('', 'idea2'):
        extra = ['--use_mm', '1', '--mm_reg', '1e-3']
        if args.force_c > 0:
            extra += ['--force_c', fc_str]
            # force_c 感知 label/key, 避免与 v3 learned-c idea2 的子日志(run_idea2_mm_*)互相覆盖
            lbl = f'mm_fc{fc_str}'
            key = f'idea2_mm_fc{fc_str}'
        else:
            lbl = 'mm'
            key = 'idea2_mm'
        run_block(key, lbl, extra)
    if args.only == 'idea3':
        if args.cost_reg <= 0:
            print("ERROR: --only idea3 requires --cost_reg > 0"); sys.exit(1)
        extra = ['--use_mm', '1', '--mm_reg', '1e-3', '--cost_reg', cr_str]
        if args.cost_target > 0:
            extra += ['--cost_target', ct_str]
        if args.force_c > 0:
            extra += ['--force_c', fc_str]
        run_block('idea3_cost', 'cost', extra)

    # ---- 汇总 ----
    cfgs = results['configs']
    if 'baseline' in cfgs and 'idea2_mm' in cfgs:
        br, bn = avg(cfgs['baseline'])
        mr, mn = avg(cfgs['idea2_mm'])
        results['summary_baseline_vs_idea2'] = {
            'base_R@20': round(br, 4), 'base_N@20': round(bn, 4),
            'idea2_R@20': round(mr, 4), 'idea2_N@20': round(mn, 4),
            'delta_R@20': round(mr - br, 4),
            'rel_R@20(%)': round((mr - br) / br * 100, 2) if br else 0,
            'delta_N@20': round(mn - bn, 4),
            'rel_N@20(%)': round((mn - bn) / bn * 100, 2) if bn else 0,
        }
        save(results)
        print("\n=== SUMMARY baseline vs idea2 ===")
        print(json.dumps(results['summary_baseline_vs_idea2'], indent=2))

    if 'idea3_cost' in cfgs:
        idea2 = cfgs.get('idea2_mm') or prior.get('configs', {}).get('idea2_mm')
        base = cfgs.get('baseline') or prior.get('configs', {}).get('baseline')
        if idea2:
            br2, bn2 = avg(idea2)
            cr_, cn_ = avg(cfgs['idea3_cost'])
            results['summary_idea2_vs_idea3'] = {
                'idea2_R@20': round(br2, 4), 'idea2_N@20': round(bn2, 4),
                'idea3_R@20': round(cr_, 4), 'idea3_N@20': round(cn_, 4),
                'delta_R@20': round(cr_ - br2, 4),
                'rel_R@20(%)': round((cr_ - br2) / br2 * 100, 2) if br2 else 0,
                'delta_N@20': round(cn_ - bn2, 4),
                'rel_N@20(%)': round((cn_ - bn2) / bn2 * 100, 2) if bn2 else 0,
            }
            save(results)
            print("\n=== SUMMARY idea2 vs idea3 (cost-aware) ===")
            print(json.dumps(results['summary_idea2_vs_idea3'], indent=2))
        if base:
            br, bn = avg(base)
            cr_, cn_ = avg(cfgs['idea3_cost'])
            results['summary_baseline_vs_idea3'] = {
                'base_R@20': round(br, 4), 'base_N@20': round(bn, 4),
                'idea3_R@20': round(cr_, 4), 'idea3_N@20': round(cn_, 4),
                'delta_R@20': round(cr_ - br, 4),
                'rel_R@20(%)': round((cr_ - br) / br * 100, 2) if br else 0,
            }
            save(results)


if __name__ == '__main__':
    main()
