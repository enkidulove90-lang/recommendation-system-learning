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
import time

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
# 必须带 4 个 OMP 环境变量, 否则 venv torch 偶发段错误
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OMP_DYNAMIC', 'FALSE')
PY = os.environ.get('VENV_PY', 'C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe')
# 单个 seed 训练被静默杀掉时的最大尝试次数(含首次)。设 1 即关闭自动重跑。
MAX_RUN_ATTEMPTS = int(os.environ.get('MAX_RUN_ATTEMPTS', '2'))

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


def _g(s):
    """把数值串归一化成 main.py 用的 :.6g 形式('1.0'->'1', '0.80'->'0.8').

    否则 '--mm_budget 1.0' 在这里拼出 _mb1.0 而 main.py 拼出 _mb1, 两侧对不上,
    parse_best_test 就会找不到 txt 并静默返回 -1(E2 已经踩过一次同类坑)."""
    return f"{float(s):.6g}"


def _arg_val(tokens, flag, default):
    """在 token 列表里取 flag 后的取值, 找不到返回 default."""
    try:
        return tokens[tokens.index(flag) + 1]
    except (ValueError, IndexError):
        return default


def config_name(extra):
    """复刻 main.py 的 config 命名(用于定位 logs/<config>.txt)."""
    # layer: extra 优先, 否则 COMMON(默认 2); 与 main.py 的 _nl{layer} 对齐.
    layer = int(_arg_val(extra, '--layer', _arg_val(COMMON, '--layer', '2')))
    cfg = f'{DATASET}_seed{{seed}}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl{layer}'
    if '--use_mm' in extra:
        # mm_reg / mm_temp: 与 main.py 的 _mm_mr{mm_reg}_mt{mm_temp} 对齐
        # (main.py 用 float 默认 str, 故这里 float():g 还原成同一串).
        mm_reg = float(_arg_val(extra, '--mm_reg', '1e-3'))
        mm_temp = float(_arg_val(extra, '--mm_temp', '0.1'))
        cfg += f"_mm_mr{mm_reg:g}_mt{mm_temp:g}"
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
                cfg += f"_fc{_g(fc)}"
        if '--mm_conf_reg' in extra:
            i = extra.index('--mm_conf_reg')
            mcr = extra[i + 1]
            if float(mcr) != 0.01:
                cfg += f"_mcr{_g(mcr)}"
        # E6: 与 main.py 的 _mb{t}l{lam}[d{eta}] 严格对齐(顺序也必须一致: cr -> fc -> mcr -> mb)
        if '--mm_budget' in extra:
            mb = extra[extra.index('--mm_budget') + 1]
            mbl = extra[extra.index('--mm_budget_lambda') + 1] \
                if '--mm_budget_lambda' in extra else '0'
            mbd = extra[extra.index('--mm_budget_dual') + 1] \
                if '--mm_budget_dual' in extra else '0'
            if float(mb) > 0 and (float(mbl) > 0 or float(mbd) > 0):
                cfg += f"_mb{_g(mb)}l{_g(mbl)}"
                if float(mbd) > 0:
                    cfg += f"d{_g(mbd)}"
        # eval 前刷新投影缓存(另一评测口径), 与 main.py 的 '_ef1' 对齐, 且必须排在最后
        if '--mm_eval_fresh' in extra and int(extra[extra.index('--mm_eval_fresh') + 1]):
            cfg += "_ef1"
        # 训练途中周期性刷新投影缓存(E6 真修复), 排在 _ef1 之后, 与 main.py 一致
        if '--mm_proj_refresh' in extra:
            _prv = int(extra[extra.index('--mm_proj_refresh') + 1])
            if _prv:
                cfg += f"_pr{_prv}"
    return cfg


def archive_eval_txt(seed, extra):
    """(重)跑之前把旧的 eval .txt 挪走。

    main.py 用 'a' 追加模式写 logs/<cfg>.txt。若上一次运行被沙箱/OOM 中途杀掉,
    残留的 eval 行会和本次新跑的行混在同一个文件里, parse_best_test 取全局最好,
    于是**上一轮截断 run 的高点会冒充本轮结果**(E6 seed2024 已真实踩到)。
    所以每次 run_one 之前先归档, 保证 .txt 只含当前这一次训练的评测点。"""
    txt = os.path.join(CODE_DIR, 'logs', config_name(extra).format(seed=seed) + '.txt')
    if not os.path.exists(txt):
        return
    import datetime as _dt
    try:
        os.rename(txt, txt + f'.prev{_dt.datetime.now():%m%d%H%M%S}')
    except OSError:
        pass    # 被占用就算了, 下面的完整性校验仍会兜底


def run_complete(log, epochs):
    """判定一次训练是否真的跑完。返回 (ok, reason)。

    判据: 日志里必须出现最后一轮 'EPOCH[N/N]', 且没有 Traceback。
    沙箱杀进程时 **不会** 留下任何报错(E6 seed2024 停在 EPOCH[12/20] 且日志干净),
    所以只靠 grep Traceback 检不出来, 必须核对轮次。"""
    try:
        with open(log, errors='ignore') as f:
            body = f.read()
    except OSError as e:
        return False, f'日志不可读: {e}'
    if 'Traceback' in body:
        tail = [l for l in body.strip().splitlines() if l.strip()]
        return False, f'训练抛异常 ({tail[-1][:120] if tail else "?"})'
    if f'EPOCH[{epochs}/{epochs}]' not in body:
        done = re.findall(r'EPOCH\[(\d+)/\d+\]', body)
        got = done[-1] if done else '0'
        return False, f'训练被中断: 只到 EPOCH[{got}/{epochs}](无报错, 疑沙箱/OOM 杀进程)'
    return True, 'ok'


def run_one(label, extra, seed, epochs):
    """跑一次训练。返回 (log_path, ok, reason)。"""
    archive_eval_txt(seed, extra)
    cmd = [PY, '-u', 'main.py'] + COMMON + ['--seed', str(seed)] + extra
    log = os.path.join(CODE_DIR, 'logs', f'run_idea2_{label}_seed{seed}.log')
    # 偶发 PermissionError: 沙箱文件监视器 / 残留句柄可能短暂占用日志文件。重试 + 退路。
    for attempt in range(3):
        try:
            with open(log, 'w') as f:
                subprocess.run(cmd, cwd=CODE_DIR, stdout=f, stderr=subprocess.STDOUT, text=True)
            return (log,) + run_complete(log, epochs)
        except PermissionError:
            try:
                os.remove(log)
            except OSError:
                pass
            time.sleep(2)
    # 最终退路: 带时间戳的备用日志名 (parse_best_test 读的是 eval .txt, 不依赖此文件名)
    import datetime as _dt
    alt = log + f'.{_dt.datetime.now():%H%M%S}'
    with open(alt, 'w') as f:
        subprocess.run(cmd, cwd=CODE_DIR, stdout=f, stderr=subprocess.STDOUT, text=True)
    return (alt,) + run_complete(alt, epochs)


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
    # 沙箱文件监视器 / 残留句柄可能短暂占用目标文件, 导致 os.replace 偶发 PermissionError。
    # 重试若干次, 仍失败则退化为直接覆盖写 (放弃原子性, 但保证落盘)。
    for attempt in range(5):
        try:
            os.replace(tmp, out)
            return out
        except OSError:
            if attempt < 4:
                time.sleep(1.0)
                continue
            try:
                with open(out, 'w') as f:
                    json.dump(merged, f, indent=2)
                try:
                    os.remove(tmp)
                except OSError:
                    pass
                return out
            except OSError as e2:
                print(f"[save] WARN: 落盘失败 {e2}")
                return None
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
    ap.add_argument('--mm_conf_reg', type=float, default=0.01,
                    help='idea2 confidence-discrimination reg weight (0 disables the (1-|2c-1|) push-to-0 term); forwarded to main.py')
    # ---- E6: global budget hard constraint ----
    ap.add_argument('--mm_budget', type=float, default=0.0,
                    help='E6 c_target for the batch-mean budget penalty; 0 disables. '
                         'Use 0.8 (E1 optimum), NOT the legacy idea3 value 0.2.')
    ap.add_argument('--mm_budget_lambda', type=float, default=0.0,
                    help='E6 lambda_b weight in lambda_b*(c_target-mean(c))^2; 0 disables. '
                         'Fixed lambda alone undershoots by A/(2*lambda_b) -- see --mm_budget_dual.')
    ap.add_argument('--mm_budget_dual', type=float, default=0.0,
                    help='E6 dual-ascent step eta (augmented Lagrangian). >0 => mean(c) hits '
                         'c_target exactly regardless of BPR pressure. 0 = soft quadratic only.')
    ap.add_argument('--mm_eval_fresh', type=int, default=0,
                    help='Refresh the projection cache before eval. The cache is rebuilt only '
                         'at epoch START while eval runs at epoch END, so the scored model '
                         'lags 94 Adam steps (conf_mean 0.193 cached vs 0.834 fresh at ep5). '
                         'Off by default to keep legacy numbers comparable; enable it for '
                         'BOTH arms when comparing.')
    ap.add_argument('--mm_proj_refresh', type=int, default=0,
                    help='每 K 个训练 batch 刷新一次全量投影缓存(0=关). '
                         'E6 真修复: 让图传播的 c 跟上预算约束的 c, 建议 32。')
    ap.add_argument('--mm_reg', type=str, default='1e-3',
                    help='idea2 MM 对齐正则权重(forwarded to main.py). E3 扫描 {1e-2,1e-1}.')
    ap.add_argument('--layer', type=int, default=2,
                    help='LightGCN 层数(forwarded to main.py via COMMON). E12 扫描 {2,3}.')
    args = ap.parse_args()
    global DATASET
    DATASET = args.dataset
    COMMON[COMMON.index('--dataset') + 1] = DATASET
    COMMON[COMMON.index('--layer') + 1] = str(args.layer)
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
            # 完整性校验 + 自动重跑: 沙箱/OOM 会静默杀掉训练进程(日志无任何报错),
            # 旧版直接 parse_best_test 会把"截断到一半的最好点"当成最终成绩写库,
            # 均值被污染且看不出来。现在跑不完就重跑, 重跑仍失败则记 -1 并跳过均值。
            # 注意: 只对**静默中断**(沙箱/OOM)重试。Traceback 是确定性的代码 bug,
            # 重跑必然再挂, 白烧 ~46min; 直接放弃并把原因打出来更划算。
            ok = False
            for attempt in range(1, MAX_RUN_ATTEMPTS + 1):
                _log, ok, why = run_one(label, extra, s, args.epochs)
                if ok:
                    break
                print(f"[{label}] seed {s}: !! 第 {attempt}/{MAX_RUN_ATTEMPTS} 次失败 -> {why}",
                      flush=True)
                if why.startswith('训练抛异常'):
                    print(f"[{label}] seed {s}: 代码异常不重试, 请修好再跑", flush=True)
                    break
            if not ok:
                d[s] = {'R@20': -1, 'N@20': -1, 'status': 'INCOMPLETE'}
                print(f"[{label}] seed {s}: FAILED 放弃, 该 seed 不计入均值", flush=True)
            else:
                r, n = parse_best_test(s, extra)
                d[s] = {'R@20': r, 'N@20': n}
                print(f"[{label}] seed {s}: R@20={r:.4f} N@20={n:.4f}")
            results['configs'][key] = d
            save(results)   # 增量保存, 防沙箱杀进程丢结果
        bad = [s for s in seeds if d.get(s, {}).get('R@20', 0) <= 0]
        if bad:
            print(f"[{label}] WARN: {len(bad)}/{len(seeds)} 个 seed 未完成 {bad}, "
                  f"均值仅由剩余 seed 得出, 不可直接用于结论", flush=True)
        return d

    if args.only in ('', 'baseline'):
        run_block('baseline', 'base', [])
    if args.only in ('', 'idea2'):
        mcr_str = f"{args.mm_conf_reg:.6g}"
        mb_str = f"{args.mm_budget:.6g}"
        mbl_str = f"{args.mm_budget_lambda:.6g}"
        extra = ['--use_mm', '1', '--mm_reg', args.mm_reg, '--mm_conf_reg', mcr_str]
        # 后缀按 main.py 的拼接顺序累积(fc -> mcr -> mb), 保证 label/key/txt 三者一致.
        # 每个消融都拿到独立 key + 独立 txt, 不覆盖 v3 默认 idea2_mm.
        sfx = ''
        if args.force_c > 0:
            extra += ['--force_c', fc_str]
            sfx += f'_fc{fc_str}'
        if args.layer != 2:
            sfx += f'_nl{args.layer}'
        if args.mm_reg != '1e-3':
            sfx += f'_mr{args.mm_reg}'
        if args.mm_conf_reg != 0.01:
            sfx += f'_mcr{mcr_str}'
        if args.mm_budget > 0 and (args.mm_budget_lambda > 0 or args.mm_budget_dual > 0):
            mbd_str = f"{args.mm_budget_dual:.6g}"
            extra += ['--mm_budget', mb_str, '--mm_budget_lambda', mbl_str]
            sfx += f'_mb{mb_str}l{mbl_str}'
            if args.mm_budget_dual > 0:
                extra += ['--mm_budget_dual', mbd_str]
                sfx += f'd{mbd_str}'
        if args.mm_eval_fresh:
            extra += ['--mm_eval_fresh', '1']
            sfx += '_ef1'          # 与 main.py 顺序一致
        if args.mm_proj_refresh:
            extra += ['--mm_proj_refresh', str(args.mm_proj_refresh)]
            sfx += f'_pr{args.mm_proj_refresh}'   # 必须排最后, 与 main.py 一致
        lbl = 'mm' + sfx
        key = 'idea2_mm' + sfx
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
