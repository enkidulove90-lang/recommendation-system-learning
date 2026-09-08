"""
E-X1c — 探针盲区检定（判 E-X1/E-X1b 的 Synergy=0 是"数据事实"还是"工具盲区"）
==============================================================================
为什么必须做这一步:
  E-X1/E-X1b 在 popularity 与 CF-SVD(4/8/16) 全部目标上得到 Synergy=0，
  且 CI 一律为**正**(+0.0015 ~ +0.0173，即 Red > Syn)。但两处方法学隐患使该
  负结果**不能**直接外推成"数据无跨模态协同":

  隐患①（分辨率上限）: pid_diagnostic.pid_2src 用 interaction-information 分辨率,
      CI = Red - Syn 是**单个标量**, 故 Syn = max(0,-CI) 与 Red = max(0,CI)
      **互斥**——数学上永远不可能同时报出 Red>0 且 Syn>0。
      真实 PID（Williams-Beer / BROJA-2PID）允许两者并存。
      所以"Syn=0"严格含义只是「**净**协同未超过净冗余」, 而非"零协同"。

  隐患②（高斯假设盲区，更致命）: gaussian_mi 假设 PCA 白化后近似高斯, 只能捕捉
      **线性/二阶**相依。而 E-X1 的阳性对照 T=synergy_feature 是由
      `comb - proj_img - proj_txt`（**线性**最小二乘残差）构造的, 天生线性可检 →
      它通过, 只证明工具能检**线性**协同, **不**证明能检**非线性**协同。
      而 PRISM 的 syn 专家是 MLP, 针对的正是非线性协同（XOR/乘积型）。

本脚本用「已知真值」的非线性协同目标做阳性对照:
  P1 线性协同   : T = (comb - proj_img - proj_txt)[:,0]   → 已知可检（复现基线）
  P2 乘积型协同 : T = img_pc1 * txt_pc1                    → 需两路相乘
  P3 XOR 型协同 : T = sign(img_pc1) * sign(txt_pc1)        → 教科书纯协同
                  （单看任一路互信息≈0, 两路联合才完全确定 → 理论 Syn 应最大）

判定:
  - 若 P2/P3 也报 Syn>0 → 工具对非线性协同有效 ⇒ E-X1b 的 Syn=0 是**数据事实**,
    PRISM 的 syn 专家在本数据集先天无料（应下调 λ_syn 预期 / 换数据集）。
  - 若 P2/P3 报 Syn≈0（而 P1 正常）→ **工具盲区证实**: 高斯 MI 看不见非线性协同,
    ⇒ E-X1/E-X1b 的负结果**无权否定** PRISM, 必须靠 E14 合成探针（可学 MLP）
    来判机制, 且后续 PID 归因需换非线性 MI 估计器（KSG/kNN 或离散化 BROJA）。

运行:
  python ex1c_nonlinear_probe.py --data_dir baseline/LightGCNpp/data/amazon-baby-mmssl
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pid_diagnostic import pca_reduce, pid_2src, load_features, synergy_feature


def ksg_mi_1d(x, y, n_bins=24):
    """离散化（等频分箱）互信息, 作为**非线性**敏感的 MI 估计器对照。
    高斯 MI 只看二阶相依; 分箱 MI 能捕捉 XOR/乘积这类非线性依赖。
    x: [N, dx] (dx<=2 时逐维联合分箱), y: [N,1]。返回 nats。"""
    def _disc(a):
        out = np.zeros(a.shape[0], dtype=np.int64)
        mult = 1
        for j in range(a.shape[1]):
            q = np.quantile(a[:, j], np.linspace(0, 1, n_bins + 1)[1:-1])
            b = np.searchsorted(q, a[:, j])
            out += b * mult
            mult *= n_bins
        return out

    xs, ys = _disc(np.atleast_2d(x)), _disc(np.atleast_2d(y))
    # 联合直方图 → MI
    xu, xi = np.unique(xs, return_inverse=True)
    yu, yi = np.unique(ys, return_inverse=True)
    joint = np.zeros((len(xu), len(yu)), dtype=np.float64)
    np.add.at(joint, (xi, yi), 1.0)
    joint /= joint.sum()
    px = joint.sum(axis=1, keepdims=True)
    py = joint.sum(axis=0, keepdims=True)
    nz = joint > 0
    return float((joint[nz] * np.log(joint[nz] / (px @ py)[nz])).sum())


def pid_binned(x1, x2, t, n_bins=16):
    """分箱版 interaction-information PID（非线性敏感）。x1/x2/t 均取 1 维。"""
    i1 = ksg_mi_1d(x1, t, n_bins)
    i2 = ksg_mi_1d(x2, t, n_bins)
    i12 = ksg_mi_1d(np.concatenate([x1, x2], axis=1), t, n_bins)
    ci = i1 + i2 - i12
    return {"I_T_X": i1, "I_T_Y": i2, "I_T_XY": i12, "CI": ci,
            "Syn": max(0.0, -ci), "Red": max(0.0, ci),
            "Unq_X": max(0.0, i1 - max(0.0, ci)),
            "Unq_Y": max(0.0, i2 - max(0.0, ci))}


def show(tag, gauss, binned):
    def fmt(p):
        tot = p["Red"] + p["Unq_X"] + p["Unq_Y"] + p["Syn"]
        tot = tot if tot > 0 else 1e-12
        flag = "✅ Syn>0" if p["Syn"] > 1e-3 else "❌ Syn≈0"
        return (f"CI={p['CI']:+.4f}  Syn={p['Syn']:.4f} ({p['Syn']/tot*100:5.1f}%)  "
                f"Red={p['Red']:.4f}  {flag}")
    print(f"\n  ── {tag}")
    print(f"     [高斯 MI ]  {fmt(gauss)}")
    print(f"     [分箱 MI ]  {fmt(binned)}")
    return gauss["Syn"], binned["Syn"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir",
                    default="baseline/LightGCNpp/data/amazon-baby-mmssl")
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--bins", type=int, default=16)
    args = ap.parse_args()

    print("=" * 74)
    print("E-X1c  探针盲区检定 (线性 vs 非线性协同阳性对照)")
    print("=" * 74)

    img, txt = load_features(args.data_dir)
    img_p = pca_reduce(img, args.k)
    txt_p = pca_reduce(txt, args.k)
    N = img_p.shape[0]
    print(f"\n[源] N={N}, PCA k={args.k}")
    print("     注: 为让两种估计器同口径, 协同目标一律用 img_pc1 / txt_pc1 两个 1 维源")

    x1 = img_p[:, 0:1]
    x2 = txt_p[:, 0:1]

    # ---- P1 线性协同（复现 E-X1 阳性对照口径）----
    t_lin = synergy_feature(img_p, txt_p, args.k)[:, 0:1]
    s1g, s1b = show("P1 线性协同 T=(comb-proj_img-proj_txt)[:,0]  (16维源, 已知可检)",
                    pid_2src(img_p, txt_p, t_lin),
                    pid_binned(x1, x2, t_lin, args.bins))

    # ---- P2 乘积型协同 ----
    t_prod = (x1 * x2)
    t_prod = (t_prod - t_prod.mean()) / (t_prod.std() + 1e-9)
    s2g, s2b = show("P2 乘积型协同 T = img_pc1 × txt_pc1",
                    pid_2src(x1, x2, t_prod),
                    pid_binned(x1, x2, t_prod, args.bins))

    # ---- P3 XOR 型协同（教科书纯协同）----
    t_xor = (np.sign(x1) * np.sign(x2)).astype(np.float64)
    s3g, s3b = show("P3 XOR 型协同 T = sign(img_pc1) × sign(txt_pc1)  (理论纯 Syn)",
                    pid_2src(x1, x2, t_xor),
                    pid_binned(x1, x2, t_xor, args.bins))

    # ---------------- 判定 ----------------
    print("\n" + "=" * 74)
    print("盲区判定")
    print("=" * 74)
    gauss_blind = (s2g <= 1e-3) or (s3g <= 1e-3)
    binned_ok = (s2b > 1e-3) and (s3b > 1e-3)
    print(f"  高斯 MI :  P1={s1g:.4f}  P2={s2g:.4f}  P3={s3g:.4f}")
    print(f"  分箱 MI :  P1={s1b:.4f}  P2={s2b:.4f}  P3={s3b:.4f}")
    if gauss_blind and binned_ok:
        print("\n  ⚠️ **工具盲区证实**: 高斯 MI 检得线性协同(P1)却漏检非线性协同(P2/P3),")
        print("     而分箱 MI 两者皆检出。")
        print("  => E-X1/E-X1b 的 'Synergy=0' **无权否定** PRISM:")
        print("     PRISM 的 syn 专家(MLP)针对的正是高斯探针看不见的那类协同。")
        print("  => 结论: (1) 立刻做 E14 合成探针(可学 MLP)判机制, 这是唯一有效判据;")
        print("           (2) PID 归因改用分箱/KSG 估计器, 勿再用高斯 MI 下结论;")
        print("           (3) E15 不因本负结果降级, 但须以 E14 为前置。")
    elif gauss_blind and not binned_ok:
        print("\n  ⚠️ 两估计器均未稳定检出非线性协同 → 构造或分箱参数待查(勿据此下结论)。")
    else:
        print("\n  ✅ 高斯 MI 对非线性协同亦有效 ⇒ E-X1b 的 Syn=0 是**数据事实**:")
        print("     本数据集跨模态协同对 CF/popularity 信号无净贡献。")
        print("  => PRISM syn 专家先天无料: 下调 λ_syn 预期, 或换数据集, 或先跑 E14。")
    print("=" * 74)


if __name__ == "__main__":
    main()
