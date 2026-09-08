"""
E-X1b — PID 目标敏感性探针（A 闸门的收口实验）
==============================================================================
背景（E-X1 结果，logs/ex1_pid_diagnostic.log）:
  - 冗余指数 = 0.0588（旧合成数据是 Pearson=0.9915）→ **数据轴可辨识性确已解除**
  - 阳性对照 T=synergy 特征 → Syn=4.5646 (71.3%) → **工具正确**
  - 但 PID{image,text}→**popularity** 的 Synergy = 0.0000 (0.0%)

即：§5 硬阻塞的「数据不可辨识」已解除，残余的 Synergy=0 是**目标(target)问题**，
不是数据问题。popularity 是 1 维弱标量，信息容量上限极低（全 PID 总量仅 0.0107 nats），
结构上承载不了跨模态协同。pid_diagnostic.py:372 自己也写明需「换用 synergy-敏感
目标 T（如训练好的 CF 嵌入 / 用户偏好预测）重测」。

本脚本即做这件事：把 target 从 popularity 换成**多维 CF 嵌入**，判 Synergy 是否 > 0。
CF 嵌入用 user-item 交互矩阵的截断 SVD（= 矩阵分解 CF，纯 scipy/CPU，无需训练权重；
E13 未存 checkpoint，故不用 LightGCN++ 权重，SVD 是同族的无训练替代）。

决策门（A 闸门的真正判据）:
  - 若 CF 目标下 Syn > 0 且占比可观 → 数据+目标双轴通过，**开 E14→E15**，
    且 E15 的 L_syn 有真实信号可学。
  - 若 CF 目标下 Syn 仍 ≈ 0 → 该数据集的跨模态协同对 CF 信号无贡献，
    PRISM 的 syn 专家在此数据集上先天无料 → 必须先跑 E14 合成探针（Idea-α）
    验证机制，且 E15 应下调 λ_syn 预期（或换数据集）。

运行:
  python ex1b_target_probe.py --data_dir baseline/LightGCNpp/data/amazon-baby-mmssl
"""
import argparse
import os
import sys

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import svds

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pid_diagnostic import (  # 复用真实已存在的签名，不重写
    pca_reduce, gaussian_mi, pid_2src, load_features,
    load_popularity_target, synergy_feature,
)


def load_ui_matrix(data_dir):
    """train.txt → 稀疏 user-item 二部图 csr。"""
    rows, cols = [], []
    n_items = 0
    with open(os.path.join(data_dir, "train.txt")) as f:
        for u, line in enumerate(f):
            parts = line.split()
            if len(parts) < 2:
                continue
            items = [int(x) for x in parts[1:]]
            n_items = max(n_items, max(items))
            rows.extend([u] * len(items))
            cols.extend(items)
    n_items += 1
    n_users = rows[-1] + 1 if rows else 0
    ui = sparse.csr_matrix(
        (np.ones(len(rows), dtype=np.float32), (rows, cols)),
        shape=(n_users, n_items),
    )
    return ui


def cf_item_embedding(ui, k=16, weighting="bm25"):
    """截断 SVD 取物品侧因子 = CF 嵌入 [n_items, k]。

    weighting: 'none' = 原始 0/1；'bm25' ≈ 隐式反馈常用的置信度加权
    （降低热门物品主导，让嵌入更多承载"口味"而非"流行度"——这正是
      我们要的 synergy-敏感目标，避免又退化成 popularity）。
    """
    X = ui.tocsc().astype(np.float64)
    if weighting == "bm25":
        # 列(物品)IDF + 行(用户)长度归一, 抑制流行度主导
        df = np.asarray((X > 0).sum(axis=0)).ravel()
        idf = np.log((X.shape[0] + 1) / (df + 1))
        X = X.multiply(sparse.csr_matrix(idf.reshape(1, -1)))
        row_len = np.asarray(X.sum(axis=1)).ravel()
        row_len[row_len == 0] = 1.0
        X = sparse.diags(1.0 / np.sqrt(row_len)) @ X
    X = X.tocsc()
    # svds 取 top-k 奇异三元组; 物品因子 = Vt.T * s
    u, s, vt = svds(X, k=k)
    order = np.argsort(s)[::-1]
    item_emb = (vt[order].T * s[order]).astype(np.float64)   # [n_items, k]
    return item_emb


def report(name, pid, extra=""):
    tot = pid["Red"] + pid["Unq_X"] + pid["Unq_Y"] + pid["Syn"]
    tot = tot if tot > 0 else 1e-12
    print(f"\n  ── target = {name} {extra}")
    print(f"     I(T;img)={pid['I_T_X']:.4f}  I(T;txt)={pid['I_T_Y']:.4f}  "
          f"I(T;img,txt)={pid['I_T_XY']:.4f}   CI={pid['CI']:+.4f}")
    print(f"     Redundancy = {pid['Red']:.4f} ({pid['Red']/tot*100:5.1f}%)")
    print(f"     Unq(image) = {pid['Unq_X']:.4f} ({pid['Unq_X']/tot*100:5.1f}%)")
    print(f"     Unq(text)  = {pid['Unq_Y']:.4f} ({pid['Unq_Y']/tot*100:5.1f}%)")
    print(f"     Synergy    = {pid['Syn']:.4f} ({pid['Syn']/tot*100:5.1f}%)"
          f"   {'✅ Syn>0' if pid['Syn'] > 1e-4 else '❌ Syn≈0'}")
    return pid["Syn"], tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir",
                    default="baseline/LightGCNpp/data/amazon-baby-mmssl")
    ap.add_argument("--k", type=int, default=16, help="图文 PCA 维度")
    ap.add_argument("--cf_dims", default="4,8,16",
                    help="CF 目标维度扫描（逗号分隔）")
    args = ap.parse_args()

    print("=" * 74)
    print("E-X1b  PID 目标敏感性探针 | 数据:", args.data_dir)
    print("=" * 74)

    img, txt = load_features(args.data_dir)
    img_p = pca_reduce(img, args.k)
    txt_p = pca_reduce(txt, args.k)
    print(f"\n[源] image/text PCA→{args.k} 维, N={img.shape[0]}")

    print("\n[T1] 对照复现: target = popularity (1 维弱标量)")
    t_pop = load_popularity_target(args.data_dir)
    report("popularity", pid_2src(img_p, txt_p, t_pop), "(1-dim)")

    print("\n[T2] 主实验: target = CF 嵌入 (user-item 截断 SVD, BM25 加权)")
    ui = load_ui_matrix(args.data_dir)
    print(f"     user-item: {ui.shape}, nnz={ui.nnz}")
    results = {}
    for d in [int(x) for x in args.cf_dims.split(",")]:
        cf = cf_item_embedding(ui, k=d, weighting="bm25")
        # 白化到同维, 使 MI 估计数值稳定 (与源同口径)
        cf_w = pca_reduce(cf, min(d, cf.shape[1]), whiten=True)
        syn, tot = report(f"CF-SVD", pid_2src(img_p, txt_p, cf_w), f"(dim={d}, BM25)")
        results[d] = (syn, tot)

    print("\n[T3] 阳性对照: target = 真实 synergy 特征 (工具有效性)")
    t_syn = synergy_feature(img_p, txt_p, args.k)[:, 0:1]
    report("synergy-feature", pid_2src(img_p, txt_p, t_syn), "(positive control)")

    # ---------------- 闸门判定 ----------------
    print("\n" + "=" * 74)
    print("A 闸门判定")
    print("=" * 74)
    best_d = max(results, key=lambda d: results[d][0])
    best_syn, best_tot = results[best_d]
    share = best_syn / best_tot * 100 if best_tot > 0 else 0.0
    print(f"  CF 目标最佳: dim={best_d}, Synergy={best_syn:.4f} ({share:.1f}% of PID)")
    if best_syn > 1e-3 and share > 5.0:
        print("  ✅ 通过: 数据轴(冗余指数 0.0588) + 目标轴(CF 下 Syn>0) 双轴均通过")
        print("     => 立刻开 E14(合成探针) → E15(真实特征 A2-1); L_syn 有真实信号可学")
    elif best_syn > 1e-4:
        print("  ⚠️ 弱通过: CF 目标下 Syn 为正但占比小")
        print("     => 仍开 E14→E15, 但 λ_syn 取网格低端(0.05), 且以 E14 合成探针为主证")
    else:
        print("  ❌ 未通过: 换 CF 目标后 Synergy 仍≈0")
        print("     => 该数据集跨模态协同对 CF 信号无贡献; PRISM syn 专家先天无料")
        print("        必须先跑 E14 合成探针验证机制, 勿直接上 E15 真实特征")
    print("=" * 74)


if __name__ == "__main__":
    main()
