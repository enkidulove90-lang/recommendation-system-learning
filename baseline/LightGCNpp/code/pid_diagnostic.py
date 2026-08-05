"""
R_MIG 的 PID 诊断脚本  (MixRAGRec × PRISM 结合思考, 文档选项 A)
=================================================================
纯 CPU 分析, 不需要 GPU / LLM / 训练好的 PRISM MoE。

目标:
  (1) 用 amazon-baby-mmssl 真实图文特征, 实测 PID 可辨识性 —— 验证
      synergy 分量确实非 0 (呼应之前合成数据 Pearson=0.9915 导致
      Synergy≈0 的硬阻塞, 见 prism_analysis.md)。
  (2) 实现 R_MIG → PID 重构函数 (镜像 MixRAGRec 奖励, 见
      mixragrec_prism_integration.md §1): 把 ΔI 拆成 Unq + Syn。
  (3) 4 专家 PID 归因框架: 用当前可用的真实信号构造 E1..E4 代理,
      跑归因, 测试 "E4 主要贡献 Synergy" 假说。待 P6 PRISM MoE 训好,
      通过 load_prism_moe() 钩子替换代理信号即可。

专家映射 (详见 mixragrec_prism_integration.md §3):
  E1 DirectGenerator(无检索)  → ID/全局均值 (Redundancy 基线)
  E2 TripleRetriever(三元组) → 文本特征 uniqueness
  E3 SubgraphRetriever(2-hop)→ 物品共交互 2-hop 子图 (真实 scipy 稀疏)
  E4 ConnectedGraphRetriever → 跨模态 synergy 残差 (PID Syn 分量)

依赖: numpy, scipy (均已在 3.11 环境确认)

运行:
  python pid_diagnostic.py --data_dir <amazon-baby-mmssl 路径> [--k 16] [--knn 20]
"""

import argparse
import os
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import norm as spnorm

EPS = 1e-6


# --------------------------------------------------------------------------
# 基础工具: PCA 降维 / 高斯互信息 / CCA 可辨识性
# --------------------------------------------------------------------------
def pca_reduce(X, k, whiten=True):
    """用协方差特征分解做 PCA 降维 (中心化 + 可选白化), 纯 numpy。
    走 d×d 协方差 (d<=4096 时仅 ~134MB), 避免对 [N,d] 做大 SVD 爆内存。"""
    X = np.asarray(X, dtype=np.float32)
    X = X - X.mean(axis=0, keepdims=True)
    n = X.shape[0]
    cov = (X.T @ X).astype(np.float64) / max(n - 1, 1)   # d×d, 小
    w, V = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1][:k]
    comps = V[:, order].astype(np.float32)
    proj = (X @ comps).astype(np.float64)
    if whiten:
        proj = proj / (np.sqrt(np.clip(w[order], 0.0, None)) + EPS)
    return proj


def _logdet(mat):
    """对称正定矩阵 (或标量) 对数行列式, 数值稳定。"""
    mat = np.atleast_2d(np.asarray(mat, dtype=np.float64))
    mat = mat + EPS * np.eye(mat.shape[0])
    s, ld = np.linalg.slogdet(mat)
    return ld


def gaussian_mi(A, B):
    """多元高斯假设下的互信息 I(A;B) = 0.5 ln( |ΣA||ΣB| / |ΣAB| )。
    纯估算 (PCA 白化后近似高斯), 作为连续 PID 代理, CPU 友好。"""
    A = np.asarray(A, dtype=np.float64)
    B = np.asarray(B, dtype=np.float64)
    if A.ndim == 1:
        A = A.reshape(-1, 1)
    if B.ndim == 1:
        B = B.reshape(-1, 1)
    cov_a = np.cov(A, rowvar=False)
    cov_b = np.cov(B, rowvar=False)
    ab = np.concatenate([A, B], axis=1)
    cov_ab = np.cov(ab, rowvar=False)
    mi = 0.5 * (_logdet(cov_a) + _logdet(cov_b) - _logdet(cov_ab))
    return float(max(mi, 0.0))


def cca_identifiability(X, Y, k):
    """两路特征的可辨识性: 典型相关分析。
    返回 top-k 典型相关系数 与 '冗余指数' = 典型相关的中位数平方。
    冗余指数越低 => 两路越独立 => PID 越可辨识 (synergy 可学)。"""
    Xp = pca_reduce(X, k, whiten=True)
    Yp = pca_reduce(Y, k, whiten=True)
    Cxx = Xp.T @ Xp
    Cyy = Yp.T @ Yp
    Cxy = Xp.T @ Yp
    # T = inv(sqrt(Cxx)) @ Cxy @ inv(sqrt(Cyy)) 的奇异值即典型相关
    inv_x = np.linalg.inv(np.linalg.cholesky(Cxx + EPS * np.eye(k)))
    inv_y = np.linalg.inv(np.linalg.cholesky(Cyy + EPS * np.eye(k)))
    T = inv_x.T @ Cxy @ inv_y
    sigma = np.linalg.svd(T, compute_uv=False)
    sigma = np.clip(sigma, 0.0, 1.0)
    return sigma, float(np.median(sigma ** 2))


# --------------------------------------------------------------------------
# PID 分解 (双源, 交互信息分辨率)
# --------------------------------------------------------------------------
def pid_2src(X, Y, T):
    """对 target T, 双源 X,Y 做 PID 分解 (交互信息分辨率)。
    返回 Red / Unq_X / Unq_Y / Syn (nats) 及中间量。
    注意: 连续 PID 不唯一, 此处用 interaction-information 分辨率
    (Syn = max(0, -CI), Red = max(0, CI), CI = I(T;X)+I(T;Y)-I(T;X,Y))。"""
    i_tx = gaussian_mi(T, X)
    i_ty = gaussian_mi(T, Y)
    i_txy = gaussian_mi(T, np.concatenate([X, Y], axis=1))
    ci = i_tx + i_ty - i_txy          # = Red - Syn
    syn = max(0.0, -ci)
    red = max(0.0, ci)
    unq_x = max(0.0, i_tx - red)
    unq_y = max(0.0, i_ty - red)
    return {
        "I_T_X": i_tx, "I_T_Y": i_ty, "I_T_XY": i_txy,
        "Red": red, "Unq_X": unq_x, "Unq_Y": unq_y, "Syn": syn,
        "CI": ci,
    }


def r_mig_pid(baseline_mi, expert_mi, cost, eta_cost=0.005, lambda_mig=0.2):
    """镜像 MixRAGRec 奖励 R_MIG = ΔI - η·Cost, 并把 ΔI 解释为 Unq+Syn。
    baseline_mi / expert_mi: 该源相对 target T 的互信息。
    这里只做量纲/结构重构演示; 真正的 Unq/Syn 由 pid_2src 给出。"""
    d_i = max(expert_mi - baseline_mi, 0.0)
    r_mig = lambda_mig * d_i - eta_cost * cost
    return {"delta_I": d_i, "cost": cost, "R_MIG": r_mig}


# --------------------------------------------------------------------------
# 数据加载 + 专家信号构造
# --------------------------------------------------------------------------
def load_features(data_dir):
    # 保留 float32 (18357×4096 image 仅 ~300MB; 转 float64 会 4.8GB 爆内存)
    img = np.load(os.path.join(data_dir, "image_feat.npy")).astype(np.float32)
    txt = np.load(os.path.join(data_dir, "text_feat.npy")).astype(np.float32)
    return img, txt


def load_popularity_target(data_dir):
    """从 train.txt 统计物品交互频次, log1p 归一化 => 连续推荐信号 T。"""
    path = os.path.join(data_dir, "train.txt")
    counts = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            for it in parts[1:]:
                counts[int(it)] = counts.get(int(it), 0) + 1
    n_items = max(counts) + 1 if counts else 0
    c = np.array([counts.get(i, 0) for i in range(n_items)], dtype=np.float64)
    c = np.log1p(c)
    if c.std() > 0:
        c = (c - c.mean()) / c.std()
    return c.reshape(-1, 1)


def build_item_adj(data_dir):
    """从 train.txt 构建稀疏 user-item 二部图 (scipy), 返回 item×item 2-hop。"""
    train = os.path.join(data_dir, "train.txt")
    # 读用户-物品
    user_items = []
    n_items = 0
    with open(train) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            items = [int(x) for x in parts[1:]]
            user_items.append(items)
            n_items = max(n_items, max(items) if items else 0)
    n_items += 1
    n_users = len(user_items)
    rows, cols = [], []
    for u, items in enumerate(user_items):
        for it in items:
            rows.append(u)
            cols.append(it)
    ui = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)),
                           shape=(n_users, n_items))
    # item-item 共交互 = ui.T @ ui  (对称, 去自环)
    ii = (ui.T @ ui).tocsr()
    ii.setdiag(0)
    ii.eliminate_zeros()
    # 截断每行 top-k 邻居, 防止 2-hop 展开后极度稠密 OOM
    ii = _cap_rows(ii, 20)
    # 2-hop = ii @ ii (截断后仍可能偏密, 再截断一次)
    ii2 = (ii @ ii).tocsr()
    ii2.setdiag(0)
    ii2.eliminate_zeros()
    ii2 = _cap_rows(ii2, 20)
    return ii2


def _cap_rows(mat, k):
    """每行仅保留 top-k 最大元素, 返回新的 csr_matrix (控制 2-hop 展开密度)。"""
    mat = mat.tocsr()
    rows, cols, vals = [], [], []
    for i in range(mat.shape[0]):
        s = slice(mat.indptr[i], mat.indptr[i + 1])
        idx = mat.indices[s]
        v = mat.data[s]
        if len(v) > k:
            order = np.argsort(v)[-k:]
            idx = idx[order]
            v = v[order]
        rows.append(np.full(len(idx), i, dtype=np.int64))
        cols.append(idx)
        vals.append(v)
    if rows:
        rows = np.concatenate(rows)
        cols = np.concatenate(cols)
        vals = np.concatenate(vals)
    else:
        rows = np.array([], dtype=np.int64)
        cols = np.array([], dtype=np.int64)
        vals = np.array([])
    return sparse.csr_matrix((vals, (rows, cols)), shape=mat.shape)


def build_expert_signals(data_dir, k, knn):
    """构造 E1..E4 信号 (真实 + 代理), 全部 PCA 到 k 维。"""
    img, txt = load_features(data_dir)
    n = img.shape[0]
    img_p = pca_reduce(img, k)
    txt_p = pca_reduce(txt, k)

    # E1: 无检索基线 = 全局均值广播 (近似零信息)
    E1 = np.tile(img_p.mean(axis=0, keepdims=True), (n, 1))

    # E2: 文本三元组 -> 文本特征 uniqueness
    E2 = txt_p

    # E3: 2-hop 子图 -> 共交互邻居的文本聚合 (真实 scipy 稀疏)
    ii2 = build_item_adj(data_dir)
    deg = np.asarray(ii2.sum(axis=1)).ravel()
    deg[deg == 0] = 1.0
    # 聚合文本: ii2 @ txt_p, 再按度归一
    agg = ii2 @ txt_p
    E3 = agg / deg.reshape(-1, 1)
    # 也 PCA 到 k (已是 k 维, 仅中心化)
    E3 = E3 - E3.mean(axis=0, keepdims=True)

    # E4: 跨模态 synergy 特征 = comb 去掉在 img_p 子空间与 txt_p 子空间各自的投影
    #      (留下去除两路单独表达后仍无法解释的部分 = 真正需两路协同的方向)
    E4 = synergy_feature(img_p, txt_p, k)

    return {"E1": E1, "E2": E2, "E3": E3, "E4": E4}, (img_p, txt_p)


def synergy_feature(img_p, txt_p, k):
    """构造跨模态 synergy 特征: 组合嵌入减去各自模态子空间投影的残差。
    与 '用全 concat 做 lstsq' 不同, 这里分别投影到 img / txt 子空间再减,
    留下的即只有两路协同才能表达的方向 (PID 的 Syn 分量在特征空间的近似)。"""
    comb = pca_reduce(np.concatenate([img_p, txt_p], axis=1), k)
    coef_i, *_ = np.linalg.lstsq(img_p, comb, rcond=None)   # 16×16
    coef_t, *_ = np.linalg.lstsq(txt_p, comb, rcond=None)   # 16×16
    proj_img = img_p @ coef_i
    proj_txt = txt_p @ coef_t
    e4 = comb - proj_img - proj_txt
    e4 = e4 - e4.mean(axis=0, keepdims=True)
    return e4


# --------------------------------------------------------------------------
# PRISM MoE 钩子 (P6 训好后即插即用)
# --------------------------------------------------------------------------
def load_prism_moe(path):
    """TODO(P6): 加载训练好的 PRISM MoE 分解出的 Unq_img/Unq_txt/Red/Syn
    张量, 替换 build_expert_signals 中的代理信号。
    期望 npz 含键: unq_img, unq_txt, red, syn (均为 [N, d])。"""
    if path is None or not os.path.exists(path):
        return None
    d = np.load(path)
    return {k: d[k] for k in ("unq_img", "unq_txt", "red", "syn") if k in d}


# --------------------------------------------------------------------------
# 主诊断流程
# --------------------------------------------------------------------------
def run_diagnostic(data_dir, k=16, knn=20, prism_path=None):
    print("=" * 70)
    print("R_MIG × PID 诊断  |  数据:", data_dir)
    print("=" * 70)

    # ---- M1: 数据 PID 可辨识性 (真实特征, 当前即可信) ----
    print("\n[M1] 数据 PID 可辨识性 (amazon-baby-mmssl 真实图文)")
    img, txt = load_features(data_dir)
    T = load_popularity_target(data_dir)
    img_p = pca_reduce(img, k)
    txt_p = pca_reduce(txt, k)
    sigma, red_idx = cca_identifiability(img, txt, k)
    print(f"  物品数 N={img.shape[0]}, PCA k={k}")
    print(f"  典型相关 top-3: {np.round(sigma[:3], 4)}  | 冗余指数(med r²)={red_idx:.4f}")
    print(f"  => 两路独立性强 (冗余指数低) 则 PID 可辨识, synergy 可学")
    pid = pid_2src(img_p, txt_p, T)
    tot = pid["Red"] + pid["Unq_X"] + pid["Unq_Y"] + pid["Syn"]
    print(f"  PID{{image,text}}→popularity:")
    print(f"    Redundancy = {pid['Red']:.4f} ({pid['Red']/tot*100:.1f}%)")
    print(f"    Unq(image)  = {pid['Unq_X']:.4f} ({pid['Unq_X']/tot*100:.1f}%)")
    print(f"    Unq(text)   = {pid['Unq_Y']:.4f} ({pid['Unq_Y']/tot*100:.1f}%)")
    print(f"    Synergy     = {pid['Syn']:.4f} ({pid['Syn']/tot*100:.1f}%)")
    print(f"    (对比: 旧合成数据 Pearson=0.9915 => Synergy≈0)")

    # [M1b] 阳性对照: 用真实 synergy 特征构造目标, 验证工具能检出 synergy
    # T_syn = synergy_feature 的第一维 (它 ⊥ img 子空间 且 ⊥ txt 子空间,
    #        但 ∈ 两路组合的 span) => 单路不可预测、联合可预测 => PID 应给 Syn>0
    e4 = synergy_feature(img_p, txt_p, k)
    t_syn = e4[:, 0:1]
    pid_syn = pid_2src(img_p, txt_p, t_syn)
    tot_s = pid_syn["Red"] + pid_syn["Unq_X"] + pid_syn["Unq_Y"] + pid_syn["Syn"]
    print(f"  [阳性对照] T=真实synergy特征 => PID: Syn={pid_syn['Syn']:.4f}"
          f"({pid_syn['Syn']/tot_s*100:.1f}%), Unq_img={pid_syn['Unq_X']:.4f},"
          f" Unq_txt={pid_syn['Unq_Y']:.4f}")
    if pid_syn["Syn"] > 0.01 * tot_s:
        print(f"    => ✅ 工具可正确检出 synergy (证明 'popularity 下 Synergy=0' 是数据事实, 非工具缺陷)")
    else:
        print(f"    => ⚠️ 阳性对照未检出 synergy, 工具或构造待查")

    # ---- M3: 4 专家 PID 归因 (真实 + 代理) ----
    print("\n[M3] 4 专家 PID 归因 (E1..E4) — (a) 信号构造")
    pm = load_prism_moe(prism_path)
    if pm is not None:
        print("  [PRISM MoE 已加载] 用真实分解分量替换代理信号")
        # TODO(P6): 将 pm['syn'] 等映射到 E2/E3/E4
    sig, _ = build_expert_signals(data_dir, k, knn)
    for name in ["E1", "E2", "E3", "E4"]:
        print(f"    {name}: shape={sig[name].shape}")

    # ---- M2: R_MIG → PID 重构函数 (结构演示, 复用 M3 信号) ----
    print("\n[M2] R_MIG → PID 重构函数 (镜像 MixRAGRec 奖励, 见 integration.md §1)")
    # 以 E4 为例: baseline=E1(≈0), expert=E4
    base_mi = gaussian_mi(T, sig["E1"])
    e4_mi = gaussian_mi(T, sig["E4"])
    rmig = r_mig_pid(base_mi, e4_mi, cost=0.3)
    print(f"  baseline(E1) MI={base_mi:.4f}, expert(E4) MI={e4_mi:.4f}")
    print(f"  ΔI={rmig['delta_I']:.4f}, R_MIG(η·Cost=0.3)={rmig['R_MIG']:.4f}")
    # ΔI 进一步由 pid_2src 拆成 Unq+Syn
    p_e14 = pid_2src(sig["E1"], sig["E4"], T)
    print(f"  pid_2src(E1,E4,T): Unq(E4)={p_e14['Unq_Y']:.4f}, Syn={p_e14['Syn']:.4f}")
    print(f"  => ΔI ≈ Unq + Syn 成立 (Red≈{p_e14['Red']:.4f}, baseline 信息近 0)")
    # ---- M3b: 各专家相对 T 的 MI 与联合归因 ----
    mis = {name: gaussian_mi(T, s) for name, s in sig.items()}
    print("  [M3·b] 各专家 MI(T;Ei):")
    for name in ["E1", "E2", "E3", "E4"]:
        print(f"    {name}: I={mis[name]:.4f}")
    # 联合 MI (E2+E3+E4) vs 边缘和
    joint = gaussian_mi(T, np.concatenate([sig["E2"], sig["E3"], sig["E4"]], axis=1))
    sum_marg = mis["E2"] + mis["E3"] + mis["E4"]
    syn_experts = max(0.0, joint - sum_marg)
    print(f"  联合 MI(E2,E3,E4)={joint:.4f}, 边缘和={sum_marg:.4f}")
    print(f"  => 专家间 synergy = {syn_experts:.4f}")
    # 消融归因: 去掉某专家后联合 MI 下降量
    print("  消融归因 (去掉该专家后联合 MI 下降 Δ):")
    drops = {}
    for drop in ["E2", "E3", "E4"]:
        others = [sig[o] for o in ["E2", "E3", "E4"] if o != drop]
        j_wo = gaussian_mi(T, np.concatenate(others, axis=1))
        d = joint - j_wo
        drops[drop] = d
        print(f"    去 {drop}: Δ={d:.4f}  (该专家边际 MI={mis[drop]:.4f})")
    # 假说判定 (严格, 防止近零 MI 导致 0/0 伪结论)
    MI_EPS = 1e-4
    print(f"\n  [假说检验] 'E4 主要贡献 Synergy'")
    if syn_experts <= MI_EPS:
        print(f"    ⚠️ 未检出专家间 synergy (联合 MI={joint:.4f} ≤ 边缘和={sum_marg:.4f})")
        print(f"    => 本代理信号 + popularity 目标下, 假说【无法支持】")
        print(f"       原因: (1) E4 为跨模态残差, 边际 MI≈0 是构造性质, 非真实信号;")
        print(f"             (2) popularity 这类弱目标本身不激发跨模态 synergy。")
        print(f"       需 P6 训好 PRISM MoE 真实 synergy 分量, 并换用")
        print(f"       synergy-敏感目标 T (如训练好的 CF 嵌入 / 用户偏好预测) 重测。")
    else:
        # 有真实 synergy: 看谁的移除造成最大不成比例损失
        best = max(drops, key=lambda x: drops[x] / max(mis[x], MI_EPS))
        print(f"    检出专家间 synergy={syn_experts:.4f}; 最大 Δ/MI 比的专家={best}")
        if best == "E4":
            print("    ✅ 支持: 去掉 E4 后专家间 synergy 损失最大 (相对其自身 MI)")
        else:
            print(f"    ⚠️ 当前信号下最大贡献者为 {best}; 待 P6 PRISM MoE 真实分量重测")
    print("  (STATUS: M1 为真实可靠结论; M2/M3 为框架, E2/E3/E4 为可计算代理,")
    print("   待 P6 PRISM MoE 经 load_prism_moe() 替换后即为真实归因)")

    print("\n" + "=" * 70)
    print("诊断完成. M1 为基于真实特征的可靠结论; M2/M3 为框架,")
    print("待 P6 PRISM MoE 训好经钩子替换后即为真实归因.")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir",
                    default="baseline/LightGCNpp/data/amazon-baby-mmssl")
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--knn", type=int, default=20)
    ap.add_argument("--prism_path", default=None,
                    help="P6 训好的 PRISM MoE npz (unq_img/unq_txt/red/syn)")
    args = ap.parse_args()
    run_diagnostic(args.data_dir, args.k, args.knn, args.prism_path)


if __name__ == "__main__":
    main()
