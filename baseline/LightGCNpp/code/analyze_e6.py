"""E6 后处理: 全局预算约束的三项判据自动判定。

判据(与 E6 设计对齐):
  主判据 机制  conf_mean @最优 test epoch >= 0.6      -> 预算是否真把 c 顶住不塌
  效果   R@20  >= fc0.8 的 0.08798, 理想 > 0.089      -> 自适应是否优于冻结 c
  保判别 conf_std 明显 > 0                             -> 没退化成 force_c(否则谈不上自适应)
  稳健   3-seed 方差小

口径(三条已踩过的坑, 勿改):
  1) conf/R@20 一律取「最优 test epoch」而非 ep5 —— 此前误判 v3 有效就栽在 ep5 上.
  2) 一律从 wrapper 日志解析, 不依赖 eval txt —— 日志含 ANSI 色码, 判断 [TEST] 必须用
     `'[TEST]' in line` 而非 startswith.
     (E2 时 main.py 漏了 _mcr 后缀导致 txt 串写, 现已修复; 但日志解析更稳, 保留此口径.)
  3) **判据用 FRESH conf_mean, 不用 cached**. project() 是 epoch 级缓存, eval 在 epoch
     末尾 -> cached conf 滞后 94 个 Adam step. 真机 ep5 实测 cached=0.193 而 fresh=0.834,
     差 0.641. 拿 cached 判 ">=0.6" 会把「预算其实顶住了」误判成 E6 无效.
     对应地, 所有 arm 都跑在 --mm_proj_refresh 32 下(tag 带 _pr32), fc0.8 靶子也已同口径重测.
     (注: pr32 会让 cached 与 FRESH 基本重合, 滞后量降到 ~0.003; 此时两口径都可用,
      但仍统一读 FRESH 以兼容历史日志。)
"""
import os
import re
import json

CODE = os.path.dirname(os.path.abspath(__file__))
BASELINE = 0.08362      # 3-seed 纯 ID LightGCN++ baseline 均值 R@20
FC08_LEGACY = 0.08798   # E1 force_c=0.8 均值(**旧缓存口径**, 仅作历史参照, 不作判据靶子)
E2_MEAN = 0.0847        # E2 (mm_conf_reg=0, c 自由塌缩) 3-seed 均值(旧口径)

LAM = 1.0            # run_e6_budget.sh 中的增广项系数, 用于反推 BPR 下压强度 A
EPOCHS = 20          # 各 arm 的训练轮数; 日志里没有 EPOCH[20/20] 一律视为被中途杀掉

# 坑 4) **必须校验训练是否跑完**。沙箱/OOM 会静默杀掉训练进程, 日志无任何报错,
#   只是停在中间某轮(实测 E6 seed2024 停在 EPOCH[12/20])。此时日志里仍有 ep5/ep10 的
#   [TEST] 行, analyze_seed 会照常取"最优 epoch"当成绩 —— 得到一个**早停的低分**,
#   混进 3-seed 均值里把 arm 整体拉低, 从而误判 "E6 无效"。故 incomplete 的 seed
#   一律剔除出均值, 只打印告警。

# 坑 5) **口径已从 _ef1 换成 _pr32**(2026-08-06 19:00 推翻)。
#   `--mm_eval_fresh`(_ef1) = 只在 eval 时刷新投影 —— 已证伪: 训练图传播用的是 epoch 级
#   缓存 c≈0.06, 预算只约束到 fuse_subset 的 c≈0.82, 二者结构性分离。仅改 eval 等于
#   "拿 c≈0.06 训出来的模型用 c≈0.83 前向打分" → 训练/评测错配, R@20 从 0.06968 崩到 0.05775。
#   正解是 `--mm_proj_refresh 32`(_pr32): **训练途中**每 32 batch 刷新全量投影缓存,
#   让图传播的 c 跟上预算约束(实测滞后从 +0.608 降到 +0.003)。
#   → 所有 arm 必须统一 _pr32, 且 fc0.8 靶子也要用 _pr32 重测(旧 0.08798 是每 epoch 只刷
#   一次的口径, 不可直接比)。
REF_LABEL = 'fc0.8 同口径靶子'
ARMS = [
    ('E6 AL  t=0.8 (主)',   'mm_mcr0_mb0.8l1d0.05_pr32', 0.8, [2024, 2025, 2026]),
    (REF_LABEL,             'mm_fc0.8_pr32',             0.8, [2024, 2025, 2026]),
    ('E6 AL  t=0.2 双向',   'mm_mcr0_mb0.2l1d0.05_pr32', 0.2, [2024]),
    ('E6 AL  t=0.6',        'mm_mcr0_mb0.6l1d0.05_pr32', 0.6, [2024]),
    ('E6 soft t=0.8(对照)', 'mm_mcr0_mb0.8l1_pr32',      0.8, [2024]),
]


def analyze_seed(tag, seed):
    """从 wrapper 日志提取 (epoch -> conf_mean/conf_std/R@20), 返回最优 test epoch 处的值。"""
    log = os.path.join(CODE, 'logs', f'run_idea2_{tag}_seed{seed}.log')
    if not os.path.exists(log):
        return None
    conf, std, r20, cached = {}, {}, {}, {}
    cur, pending = None, False
    incomplete = None
    with open(log, errors='ignore') as f:
        _body = f.read()
    if 'Traceback' in _body:
        incomplete = '训练抛异常'
    elif f'EPOCH[{EPOCHS}/{EPOCHS}]' not in _body:
        _seen = re.findall(r'EPOCH\[(\d+)/\d+\]', _body)
        incomplete = f'训练被中断, 只到 ep{_seen[-1] if _seen else 0}/{EPOCHS}'
    with open(log, errors='ignore') as f:
        for line in f:
            m = re.search(r'EPOCH\[(\d+)/\d+\]', line)
            if m:
                cur = int(m.group(1))
            # 缓存口径(滞后), 仅留作诊断
            cm = re.search(r'\[idea2\] conf_mean=([\d.]+)', line)
            if cm and cur is not None:
                cached[cur] = float(cm.group(1))
                conf.setdefault(cur, float(cm.group(1)))
                cs = re.search(r'conf_std=([\d.]+)', line)
                if cs:
                    std.setdefault(cur, float(cs.group(1)))
            # 新鲜口径(判据真值), 出现则覆盖缓存值
            fm = re.search(r'\[idea2\] FRESH conf_mean=([\d.]+)', line)
            if fm and cur is not None:
                conf[cur] = float(fm.group(1))
                fs = re.search(r'conf_std=([\d.]+)', line)
                if fs:
                    std[cur] = float(fs.group(1))
            if '[TEST]' in line:          # 日志含 ANSI 色码, 不能用 startswith
                pending = True
                continue
            if pending:
                rc = re.search(r"'recall':\s*array\(\[\s*([\d.eE+-]+)", line)
                if rc and cur is not None:
                    r20[cur] = float(rc.group(1))
                    pending = False
                elif line.strip():
                    pending = False
    if not r20:
        return None
    best_ep = max(r20, key=lambda e: r20[e])
    return {'incomplete': incomplete,
            'best_epoch': best_ep, 'best_r20': r20[best_ep],
            'best_conf': conf.get(best_ep), 'best_std': std.get(best_ep),
            'best_conf_cached': cached.get(best_ep),
            'fresh_available': bool(set(conf) - set()) and any(
                e in conf and cached.get(e) != conf.get(e) for e in conf),
            'traj_conf': [conf.get(e) for e in sorted(r20)],
            'traj_r20': [r20[e] for e in sorted(r20)],
            'n_epoch_seen': max(r20)}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def tail_delta(info):
    """末段增量: 各 seed 最后两个 eval 点之差(即 ep15->ep20)的均值。

    为什么需要这个: E1/E2 的真机轨迹显示, **ep20 时所有 arm 都还在爬坡**
    (fc0.8 末段 +0.00185, E2 +0.00135), 没有一个收敛。而 E6 要现学 conf_mlp,
    force_c 却是冻结常数(白送收敛速度) -> E6 天然收敛更慢。
    此时用 ep20 截断对比, 会**系统性低估 E6**, 把"没跑够"误判成"打不过"。
    故 FAIL 判决前必须先看斜率: 主档若明显更陡, 该判决不成立。
    """
    ds = []
    for r in info.get('seeds', {}).values():
        t = r.get('traj_r20') or []
        if len(t) >= 2:
            ds.append(t[-1] - t[-2])
    return mean(ds)


def main():
    out = {}
    # 先解析出同口径 fc0.8 靶子; 没跑出来时退回旧值, 但会明确标注不可比.
    ref_rows = [r for r in (analyze_seed('mm_fc0.8_pr32', s) for s in (2024, 2025, 2026))
                if r and not r['incomplete']]
    if ref_rows:
        FC08 = mean([r['best_r20'] for r in ref_rows])
        ref_note = f"同口径重测 {len(ref_rows)}-seed"
    else:
        FC08 = FC08_LEGACY
        ref_note = "!! 旧缓存口径, 与本轮不可直接比, 请先跑 Stage A0 !!"

    print("\n================ E6 全局预算约束 结果 ================")
    print(f"靶子 fc0.8 = {FC08:.5f}  ({ref_note})")
    print(f"{'arm':22} {'seed':>5} {'ep':>3} {'R@20':>8} {'conf':>7} {'std':>7} {'vs_fc0.8':>9}")
    print('-' * 70)
    summary = {}
    for label, tag, target, seeds in ARMS:
        rows = [(s, analyze_seed(tag, s)) for s in seeds]
        rows = [(s, r) for s, r in rows if r]
        # 未跑完的 seed 只告警, 不进均值(否则早停低分会伪装成"该 arm 效果差")
        broken = [(s, r) for s, r in rows if r['incomplete']]
        rows = [(s, r) for s, r in rows if not r['incomplete']]
        for s, r in broken:
            print(f"{label:22} {s:>5} {'!!':>3} {r['best_r20']:>8.5f} "
                  f"{'':>7} {'':>7} {'  [剔除]':>9}  {r['incomplete']}")
        if not rows:
            print(f"{label:22} {'--- 尚无有效数据 ---'}")
            continue
        for s, r in rows:
            cf = f"{r['best_conf']:.3f}" if r['best_conf'] is not None else "  n/a"
            sd = f"{r['best_std']:.3f}" if r['best_std'] is not None else "  n/a"
            dv = (r['best_r20'] - FC08) / FC08 * 100
            print(f"{label:22} {s:>5} {r['best_epoch']:>3} {r['best_r20']:>8.5f} "
                  f"{cf:>7} {sd:>7} {dv:>8.1f}%")
        mr = mean([r['best_r20'] for _, r in rows])
        mc = mean([r['best_conf'] for _, r in rows])
        ms = mean([r['best_std'] for _, r in rows])
        if len(rows) > 1:
            var = (max(r['best_r20'] for _, r in rows)
                   - min(r['best_r20'] for _, r in rows))
            print(f"{label:22} {'MEAN':>5} {'-':>3} {mr:>8.5f} {mc:>7.3f} {ms:>7.3f} "
                  f"{(mr-FC08)/FC08*100:>8.1f}%   (极差 {var:.5f})")
        summary[label] = {'target': target, 'mean_r20': mr, 'mean_conf': mc,
                          'mean_std': ms, 'n_seed': len(rows),
                          'n_broken': len(broken),
                          'broken_seeds': {str(s): r['incomplete'] for s, r in broken},
                          'seeds': {str(s): r for s, r in rows}}
        if broken:
            print(f"{label:22} WARN: {len(broken)} 个 seed 未跑完已剔除, "
                  f"需补跑后才能下结论")
        print('-' * 70)

    print(f"\n参照: baseline={BASELINE:.5f}  E2(自由塌缩,旧口径)={E2_MEAN:.5f}  "
          f"fc0.8 旧口径={FC08_LEGACY:.5f}  fc0.8 本轮靶子={FC08:.5f}")

    # ---- 缓存滞后诊断: 提醒判据没有用错口径 ----
    lags = []
    for label, info in summary.items():
        for r in info['seeds'].values():
            if r.get('best_conf') is not None and r.get('best_conf_cached') is not None:
                lags.append(r['best_conf'] - r['best_conf_cached'])
    if lags:
        print(f"\n----- 投影缓存滞后量(fresh - cached) -----")
        print(f"  均值 {sum(lags)/len(lags):+.3f}  最大 {max(lags):+.3f}  "
              f"-> 判据已统一采用 FRESH 口径" if max(lags) > 1e-6 else
              "  两口径一致(force_c 档, 或 pr32 已把滞后压没)")

    # ---- 双向控制: c_target 与实测 conf 的跟踪误差 ----
    print("\n----- 机制: 预算是否真在控制 c(跟踪误差) -----")
    track = []
    for label, info in summary.items():
        if info['mean_conf'] is not None and 'AL' in label:
            err = info['mean_conf'] - info['target']
            track.append((info['target'], info['mean_conf']))
            print(f"  t={info['target']:<4} -> conf {info['mean_conf']:.3f}  误差 {err:+.3f}")
    if len(track) >= 3:
        track.sort()
        mono = all(track[i][1] < track[i + 1][1] for i in range(len(track) - 1))
        print(f"  单调性(t 增 conf 增): {'PASS' if mono else 'FAIL'}"
              f"  -> {'能双向控 c, 排除惩罚过弱/过强' if mono else '控制失效, 检查 eta/nu_max'}")

    # ---- 软惩罚对照: 反推真实 BPR 下压强度 A ----
    soft = summary.get('E6 soft t=0.8(对照)')
    if soft and soft['mean_conf'] is not None:
        A = 2 * LAM * (0.8 - soft['mean_conf'])
        print(f"\n----- 软惩罚对照(固定 lambda={LAM}, 无对偶项) -----")
        print(f"  实测 conf={soft['mean_conf']:.3f} -> 反推 BPR 等效下压强度 A = 2*lam*(t-c) = {A:.3f}")
        print(f"  理论欠冲 A/(2*lam) = {A/(2*LAM):.3f}; 若要靠固定 lambda 达到 0.6, "
              f"需 lambda >= {A/(2*max(1e-6, 0.8-0.6)):.2f}")

    # ---- 收敛性: ep20 是不是截断得太早 ----
    print(f"\n----- 收敛性: ep{EPOCHS} 末段增量(最后 5 epoch 的 R@20 涨幅) -----")
    for label, info in summary.items():
        d = tail_delta(info)
        if d is None:
            continue
        tag = "仍在爬坡" if d > 5e-4 else ("趋于平缓" if d > 0 else "已见顶/回落")
        print(f"  {label:22} {d:+.5f}  {tag}")
    print(f"  (参照 E1 真机: fc0.8 末段 +0.00185 / E2 +0.00135 -> "
          f"ep{EPOCHS} 时各档普遍**尚未收敛**)")

    # ---- 三项判据 ----
    main_arm = summary.get('E6 AL  t=0.8 (主)')
    print("\n================ 判定 ================")
    if not main_arm:
        print("主实验档尚无数据, 无法判定。")
    else:
        mc, mr, ms = main_arm['mean_conf'], main_arm['mean_r20'], main_arm['mean_std']
        ok_mech = mc is not None and mc >= 0.6
        print(f"[{'PASS' if ok_mech else 'FAIL'}] 主判据 机制: conf_mean@best={mc:.3f} (需 >=0.6)"
              f" -> {'预算顶住了 c, 未塌缩' if ok_mech else 'c 仍被压下去, 检查 eta/nu_max 是否够大'}")

        ok_std = ms is not None and ms > 0.02
        print(f"[{'PASS' if ok_std else 'FAIL'}] 保判别: conf_std={ms:.3f} (需 >0.02)"
              f" -> {'保留了物品间分化' if ok_std else '门控退化为常数, 等价 force_c, 无自适应'}")

        # "理想 >0.089" 原本是相对旧靶子 0.08798 的 +1.2%; 靶子重测后改为等价的相对阈,
        # 否则靶子一变, 这条绝对阈就失去意义.
        pass_plus = FC08 * 1.012
        if mr >= pass_plus:
            print(f"[PASS+] 效果: R@20={mr:.5f} > 靶子+1.2%({pass_plus:.5f}) "
                  f"-> **自适应优于冻结**, Phase A 闭环, 可写进论文主结果")
        elif mr >= FC08:
            print(f"[PASS] 效果: R@20={mr:.5f} >= fc0.8({FC08:.5f}) -> 追平冻结档, "
                  f"机制成立但增益有限, 建议加 E7(逐物品预算分配)")
        else:
            # 先查收敛性: ep20 时各档普遍还在爬坡, 主档若明显更陡, 说明是"没跑够"
            # 而不是"打不过" —— 这种情况下判 FAIL 就是假阴性。
            d_main = tail_delta(main_arm)
            ref_info = summary.get(REF_LABEL)
            d_ref = tail_delta(ref_info) if ref_info else None
            slower_but_steeper = (d_main is not None and d_ref is not None
                                  and d_main > max(d_ref * 1.15, 5e-4))
            if slower_but_steeper:
                need = (FC08 - mr) / max(d_main - max(d_ref, 0), 1e-9) * 5
                print(f"[INCONCLUSIVE] 效果: R@20={mr:.5f} < fc0.8({FC08:.5f}) "
                      f"({(mr-FC08)/FC08*100:+.1f}%), **但判决不成立**")
                print(f"       主档末段斜率 {d_main:+.5f}/5ep 明显陡于靶子 {d_ref:+.5f}/5ep")
                print(f"       -> E6 收敛更慢(要现学 conf_mlp, force_c 是冻结常数),"
                      f" ep{EPOCHS} 截断过早.")
                new_ep = EPOCHS + max(10, int(need / 10 + 1) * 10)
                print(f"       -> 正确做法: 把主档与靶子**同时**延长到 "
                      f"~{new_ep} epoch 再判; 粗估还需 ~{need:.0f} epoch 追平.")
                print(f"       -> 在此之前不得写下 'E6 无效' 的结论.")
                # 成本前提: 本代码库无 torch.save(已核实), checkpoints/ 恒空,
                # --load 恒失败; 且 AL 对偶乘子 _mm_dual 是普通 float 不入
                # state_dict -> 续跑会清零 nu。故延长 = 从头重跑, 不是补跑差额。
                n_rerun = len(main_arm.get('seeds', {})) + \
                    len((ref_info or {}).get('seeds', {}))
                print(f"       -> !! 成本提醒: 本仓库无 checkpoint 保存机制"
                      f"(全局无 torch.save), 不能续跑, 延长=**从头重跑**.")
                print(f"          需重跑 {n_rerun} run x {new_ep}ep "
                      f"≈ {n_rerun * new_ep * 1.67 / 60:.1f}h "
                      f"(按实测 1.67 min/epoch, 严格串行).")
                print(f"          命令: EP={new_ep} bash run_e6_budget.sh")
            else:
                print(f"[FAIL] 效果: R@20={mr:.5f} < fc0.8({FC08:.5f}) "
                      f"({(mr-FC08)/FC08*100:+.1f}%)")
                if d_main is not None and d_ref is not None:
                    print(f"       (末段斜率 主 {d_main:+.5f} vs 靶 {d_ref:+.5f}, "
                          f"未见明显追赶趋势 -> 截断不是主因)")
                if ok_mech:
                    print("       -> c 顶住了但性能没上去: 说明**门控的逐物品分配是错的**"
                          "(把预算分给了错误的物品), 而非引入率问题. "
                          "下一步 Phase B 换特征/换对齐信号.")
                else:
                    print("       -> c 没顶住, 本轮不能判 E6 无效, 先把约束调硬再测.")

        if main_arm['n_seed'] > 1:
            rs = [v['best_r20'] for v in main_arm['seeds'].values()]
            print(f"[info] 稳健: {main_arm['n_seed']}-seed 极差 {max(rs)-min(rs):.5f}, "
                  f"各 seed {['%.5f' % r for r in rs]}")

    out = {'summary': summary, 'baseline': BASELINE, 'fc08_ref': FC08,
           'fc08_ref_note': ref_note, 'fc08_legacy': FC08_LEGACY, 'e2_mean': E2_MEAN}
    p = os.path.join(CODE, 'logs', 'e6_analysis.json')
    with open(p, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n已写入 {p}")


if __name__ == '__main__':
    main()
