"""
E-X1d — 用非线性敏感估计器重测真实数据（A 闸门的最终判据）
==============================================================================
前情:
  E-X1  高斯 MI: popularity 目标 Synergy=0
  E-X1b 高斯 MI: CF-SVD(4/8/16) 目标 Synergy 全为 0
  E-X1c **证实高斯 MI 存在盲区**: 线性协同 P1=4.5646 可检, 但
        乘积型 P2=0.0000 / XOR 型 P3=0.0001 漏检（分箱 MI 分别为 1.2712 / 0.5412）
        ⇒ E-X1/E-X1b 的负结果**无效**, 必须用非线性估计器重测真实数据。

本脚本 = 重测。要点:
  1. 估计器换成分箱 MI（非线性敏感, 见 ex1c.ksg_mi_1d）。
  2. **置换零假设校正**: 分箱 MI 有正偏（有限样本下即使独立也 >0）。
     对每个组合做 n_perm 次 target 置换, 得到 CI 的零分布,
     报「观测 Syn」与「零分布 95 分位」比较, 只有显著超出才算真协同。
  3. 多 PC 对扫描: (img_pc_i, txt_pc_j), i,j ∈ [0,4) 共 16 组,
     因协同可能只存在于特定方向对, 单看 pc1 会漏。

判定（A 闸门最终）:
  - 若存在显著 Syn（观测 > 零分布 P95）→ 真实数据确有非线性跨模态协同,
    PRISM syn 专家**有真实信号可学** ⇒ 开 E14 → E15, λ_syn 可取网格中高端。
  - 若全部不显著 → 真实数据在 CF/popularity 目标下无可检协同（此时结论才可信,
    因为已排除工具盲区）⇒ E14 合成探针仍必做（验证机制正确性）, 但 E15 的
    L_syn 预期应下调, 并考虑换更依赖协同的数据集/目标。

运行:
  python ex1d_nonlinear_real.py --data_dir baseline/LightGCNpp/data/amazon-baby-mmssl
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pid_diagnostic import pca_reduce, load_features, load_popularity_target
from ex1b_target_probe import load_ui_matrix, cf_item_embedding
from ex1c_nonlinear_probe import ksg_mi_1d


def binned_ci(x1, x2, t, bins):
    """CI = I(T;X1) + I(T;X2) - I(T;X1,X2)；CI<0 ⇒ 净协同。"""
    i1 = ksg_mi_1d(x1, t, bins)
    i2 = ksg_mi_1d(x2, t, bins)
    i12 = ksg_mi_1d(np.concatenate([x1, x2], axis=1), t, bins)
    return i1 + i2 - i12, i1, i2, i12


def probe_pair(x1, x2, t, bins, n_perm, rng):
    """返回 (观测 Syn, 零分布 P95 Syn, 观测 CI, 是否显著)。"""
    ci, i1, i2, i12 = binned_ci(x1, x2, t, bins)
    syn_obs = max(0.0, -ci)
    null = []
    for _ in range(n_perm):
        tp = t[rng.permutation(t.shape[0])]
        ci_p, *_ = binned_ci(x1, x2, tp, bins)
        null.append(max(0.0, -ci_p))
    p95 = float(np.quantile(null, 0.95)) if null else 0.0
    return syn_obs, p95, ci, (syn_obs > p95 and syn_obs > 1e-3), (i1, i2, i12)


def scan(name, img_p, txt_p, t, bins, n_pc, n_perm, seed=0):
    rng = np.random.default_rng(seed)
    print(f"\n{'='*74}\n[target = {name}]  分箱 MI + 置换零假设 (bins={bins}, "
          f"n_perm={n_perm})\n{'='*74}")
    print(f"  {'PC 对':<14}{'I(T;img)':>10}{'I(T;txt)':>10}{'I(T;both)':>11}"
          f"{'CI':>10}{'Syn':>9}{'null_P95':>10}  判定")
    hits = []
    for i in range(n_pc):
        for j in range(n_pc):
            x1 = img_p[:, i:i + 1]
            x2 = txt_p[:, j:j + 1]
            syn, p95, ci, sig, (i1, i2, i12) = probe_pair(x1, x2, t, bins, n_perm, rng)
            mark = "✅ 显著" if sig else "—"
            if sig:
                hits.append((f"img_pc{i+1}×txt_pc{j+1}", syn, p95))
            print(f"  img{i+1}×txt{j+1}{'':<7}{i1:>10.4f}{i2:>10.4f}{i12:>11.4f}"
                  f"{ci:>+10.4f}{syn:>9.4f}{p95:>10.4f}  {mark}")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir",
                    default="baseline/LightGCNpp/data/amazon-baby-mmssl")
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--bins", type=int, default=12)
    ap.add_argument("--n_pc", type=int, default=4, help="每模态取前 n_pc 个 PC 做扫描")
    ap.add_argument("--n_perm", type=int, default=20)
    args = ap.parse_args()

    print("=" * 74)
    print("E-X1d  非线性估计器重测真实数据 (A 闸门最终判据)")
    print("=" * 74)

    img, txt = load_features(args.data_dir)
    img_p = pca_reduce(img, args.k)
    txt_p = pca_reduce(txt, args.k)
    print(f"\n[源] N={img_p.shape[0]}, PCA k={args.k}, 扫描前 {args.n_pc} 个 PC "
          f"({args.n_pc**2} 组合)")

    all_hits = {}

    # ---- 目标 1: popularity ----
    t_pop = load_popularity_target(args.data_dir)
    all_hits["popularity"] = scan("popularity (1-dim)", img_p, txt_p, t_pop,
                                  args.bins, args.n_pc, args.n_perm)

    # ---- 目标 2: CF-SVD 主因子 ----
    ui = load_ui_matrix(args.data_dir)
    cf = cf_item_embedding(ui, k=8, weighting="bm25")
    cf1 = cf[:, 0:1]
    cf1 = (cf1 - cf1.mean()) / (cf1.std() + 1e-9)
    all_hits["CF-SVD pc1"] = scan("CF-SVD 主因子 (dim=8, BM25, 取 f1)",
                                  img_p, txt_p, cf1, args.bins, args.n_pc, args.n_perm)

    # ---------------- 闸门判定 ----------------
    print("\n" + "=" * 74)
    print("A 闸门最终判定")
    print("=" * 74)
    total = 0
    for name, hits in all_hits.items():
        print(f"\n  target={name}: 显著协同组合 {len(hits)} / {args.n_pc**2}")
        for h, syn, p95 in sorted(hits, key=lambda z: -z[1])[:5]:
            print(f"     {h}: Syn={syn:.4f} (null_P95={p95:.4f})")
        total += len(hits)

    # ---- 效应量守门（防止把"分箱正偏噪声"当协同信号）----
    # 观测 Syn 与零分布 P95 的比值; <1.3 视为"贴着偏差地板", 不足以下阳性结论。
    ratios = [syn / p95 for hits in all_hits.values() for _, syn, p95 in hits if p95 > 0]
    max_ratio = max(ratios) if ratios else 0.0
    n_comp = args.n_pc ** 2
    exp_fp = 0.05 * n_comp          # α=0.05 下每个 target 的期望假阳数
    print()
    print(f"  [效应量] 最大 Syn/null_P95 = {max_ratio:.2f}"
          f"   (>1.3 才算脱离偏差地板)")
    print(f"  [多重比较] 每 target {n_comp} 组合, α=0.05 期望假阳 ≈ {exp_fp:.1f} 组")

    strong = max_ratio >= 1.3
    beats_chance = any(len(h) > 2 * exp_fp for h in all_hits.values())

    if strong and beats_chance:
        print("\n  ✅ **通过**: 真实数据检出脱离偏差地板的显著非线性协同")
        print("  => PRISM syn 专家有真实信号可学。开 E14 → E15, λ_syn 取中高端。")
    elif beats_chance:
        print("\n  ⚠️ **不可判（贴地板）**: 显著组合数超随机期望, 但效应量贴着分箱正偏地板")
        print(f"     (最大 Syn/null_P95={max_ratio:.2f} < 1.3), 且置换零假设**依赖不匹配**——")
        print("     置换 T 会摧毁全部真实依赖, 而观测态下 I(T;txt) 较强会抬高分箱偏差,")
        print("     故零分布系统性**低估**偏差 ⇒ 显著性被高估, 不能据此宣称阳性。")
        print("  => 结论: A 闸门在真实数据上**无法给出可信阳性**。唯一有效判据是")
        print("     **E14 合成探针**（真值已知 + 可学 MLP，不受估计器盲区/偏差影响）。")
        print("     行动: E14 升级为**必做前置且是主证**; E15 待 E14 通过再开。")
    else:
        print("\n  ❌ 未通过: 已排除工具盲区后仍未检出脱离地板的协同")
        print("  => 行动: E14 合成探针必做(验机制); E15 下调 λ_syn 预期。")
    print("=" * 74)


if __name__ == "__main__":
    main()
