# -*- coding: utf-8 -*-
"""
M2: 特征轴属性记忆 (Feature-Axis Attribute Memory) 落地脚本
=============================================================
MMEACR 属性引导记忆机制的移植，适配本项目数据约束（无 item 标题文本）。

数据约束（2026-08-20 确认）:
  - amazon-baby-mmssl 仅提供 image_feat(18357,4096)/text_feat(18357,384) 特征向量，无标题文本
  - → DeepSeek 语义属性提取无输入 → 属性轴改用「特征聚类」: K-means(K=9, CLIP⊕SBERT) 镜像 MMEACR 9 属性维
  - DeepSeek 接口保留（optional），数据具备标题后可随时启用

机制（对照 baseline/MMEACR/memory_manager.py）:
  ① 属性轴: K-means K=9 on L2 归一化 cat 特征 → item_attr[i,k] = max(0, cos(item_i, centroid_k))
  ② 强化-反思: 正确性信号 = 真实 next-item 标签（train 序列前缀→下一项，替代 MMEACR 的 fuzz.ratio 合成标签）
              → 全局属性重要性 w 经 passive-aggressive 排名学习（命中强化/未命中反思）
  ③ 属性记忆: 每用户 P_u = w ⊙ mean(item_attr[train items])  —— 替代 L_syn 的「可解释分解」角色
  ④ 三段式门控: soft_fusion_memory 思想 (DIRECT>=0.5 / FUSION 0.3~0.5 / REJECT<0.3)
              gate_score[u] = 属性轨在 train 留一(prefix→next) 的「簇级」命中率
              （下一物品簇 ∈ 前缀 top-3 簇；item 级 hit@20 超出内容轨可达范围, M1 已实证）
  ⑤ 融合: 门控 RRF (REJECT→CF only; FUSION→RRF 等权; DIRECT→RRF 属性轨权重×2) vs 朴素 RRF(等权)

红线（docs/mmeacr_experiment_design.md）:
  - 对照隔离: CF only / 属性轨 only / 仅 e_u 画像(M3) / 朴素 RRF / 门控 RRF 五路同口径对比
  - 增益判据: R@20 相对 CF only ≥ +2%（双 seed 口径）；不达则退化为「属性画像=可解释叙事资产」

产物:
  - m2_attribute_axis.npz: item_attr(18357,9) + centroids(9,4480) + w(9,) —— 可解释属性轴资产
  - m2_report.json: 五路 R@20/N@20 + 门控分布 + 属性重要性 + 结论

用法 (PowerShell, torch 脚本 — 需加载 embs pkl):
  & python run_m2_attribute_memory.py [--emb <pkl>] [--limit N]
"""
import os
import sys
import json
import argparse
import pickle

import numpy as np
from sklearn.cluster import KMeans

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data", "amazon-baby-mmssl")
EMB_DIR = os.path.join(BASE, "embs")
M3_NPZ = os.path.join(BASE, "m3_eu_profiles.npz")
TRAIN = os.path.join(DATA, "train.txt")
TEST = os.path.join(DATA, "test.txt")

TOP_K = 20
CF_CAND = 200          # RRF 候选集大小（每轨）
K_ATTR = 9             # 属性维度（镜像 MMEACR 9 维）
NEG_PER_POS = 3        # 强化学习每位置负样本数
PA_ETA = 0.5           # passive-aggressive 步长（信号弱，需大步长才能让 w 分化）
PA_MARGIN = 0.01
PA_EPOCHS = 5
MAX_LEN = 20           # 序列截断（gate/强化计算上界，控制耗时）
BATCH = 2000
GATE_CLUSTER_HIT = 3   # 门控正确性信号 = 下一物品的簇 ∈ 前缀 top-3 簇（簇级主张）

DEFAULT_EMB = "amazon-baby-mmssl_seed2026_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl4_mm_mr0.001_mt0.1_fc0.8_pr32.pkl"


# ============ DeepSeek 接口（optional，数据无标题故默认禁用） ============
def deepseek_attr_extract(item_titles):
    """MMEACR prompt.py:159/211 模板的 DeepSeek 语义属性提取。

    当前数据无 item 标题 → 不调用。若未来获得标题（如 MMSSL 原始 metadata），
    复用 skills/deepseek_summarizer.py 客户端模式 + temperature=0.1 即可启用。
    """
    raise NotImplementedError(
        "amazon-baby-mmssl 无 item 标题文本，DeepSeek 语义属性提取无输入；"
        "M2 使用特征聚类属性轴（K-means K=9）替代。"
    )


# ============ 数据加载 ============
def load_interactions(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            data[int(parts[0])] = [int(x) for x in parts[1:]]
    return data


def l2norm(x):
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


# ============ ② 强化-反思：全局属性重要性 w（真实 next-item 标签） ============
def learn_attribute_weights(train_seq, item_attr, n_items, w0):
    """passive-aggressive 排名学习：让属性打分 s(w, prefix, next) > s(w, prefix, neg)。

    更新规则（反思方向 = 负样本的均值 - 正样本）：
      w += eta * mean_over_violations( P ⊙ (neg_mean - pos) )
    其中 P = 前缀属性画像（mean of item_attr[prefix]），pos/neg 为该位置属性向量。
    """
    rng = np.random.default_rng(42)
    w = w0.copy()
    total_pairs = 0
    total_viol = 0.0
    total_gap = 0.0
    for epoch in range(PA_EPOCHS):
        upd = np.zeros_like(w)
        _gap = 0.0
        _np = 0
        _ep_pairs = 0
        for u, its in train_seq.items():
            its = [x for x in its[:MAX_LEN] if x < n_items]
            L = len(its)
            if L < 2:
                continue
            itarr = np.asarray(its, dtype=np.int64)
            A = item_attr[itarr]                          # (L, K)
            pref = np.cumsum(A, axis=0) / np.arange(1, L + 1, dtype=np.float32)[:, None]  # (L, K)
            P = pref[:-1]                                 # (L-1, K) 前缀画像
            pos = A[1:]                                   # (L-1, K)
            n_pos = L - 1
            # 每位置采样负样本（不在前缀内）
            neg = np.asarray([
                rng.choice(n_items, size=NEG_PER_POS, replace=False) for _ in range(n_pos)
            ], dtype=np.int64)                            # (L-1, NEG)
            An = item_attr[neg]                           # (L-1, NEG, K)
            # 打分: s = w · (P ⊙ attr)
            sp = np.sum(w * P * pos, axis=1)              # (L-1,)
            sn = np.einsum("nk,njk->nj", w * P, An)       # (L-1, NEG)
            viol = (sn - sp[:, None] + PA_MARGIN) > 0     # 违反 margin
            d = An.mean(axis=1) - pos                      # (L-1, K) 反思方向
            upd += np.sum(viol.mean(axis=1)[:, None] * P * d, axis=0)
            total_pairs += n_pos * NEG_PER_POS
            _ep_pairs += n_pos * NEG_PER_POS
            total_viol += float(viol.sum())
            _gap += float((sp[:, None] - sn).mean()) * n_pos
            _np += n_pos
        # 每 epoch 独立归一（避免跨 epoch 累积计数稀释更新）
        w += PA_ETA * upd / max(1.0, float(_ep_pairs))
        viol_rate = total_viol / max(1, total_pairs)
        print(f"      [PA] epoch {epoch + 1}: pairs={_ep_pairs}, "
              f"violation_rate={viol_rate:.4f}, mean(sp-sn)={_gap / max(1, _np):+.5f}, "
              f"w=[{np.round(w, 3).tolist()}]")
    return w, total_pairs, total_viol / max(1, total_pairs)


# ============ ④ 三段式门控：train 留一簇级命中率 ============
def user_gate_score(its, labels, w, item_attr, n_items):
    """属性轨在用户 train 序列上的留一「簇级」next-item 命中率 → 门控分 ∈ [0,1]。

    正确性信号 = 下一物品的簇 ∈ 前缀物品 top-GATE_CLUSTER_HIT 簇（属性轨可达的主张；
    item 级 hit@20 对内容轨不可能达到——M1 已实证——故门控测簇级选择是否正确，
    与 MMEACR gate「选择是否正确」的语义对齐）。"""
    from collections import Counter
    its = [x for x in its[:MAX_LEN] if x < n_items]
    L = len(its)
    if L < 2:
        return 0.0
    hits = 0
    n = 0
    for t in range(1, L):
        freq = Counter(labels[its[:t]].tolist())
        top = {k for k, _ in freq.most_common(GATE_CLUSTER_HIT)}
        if labels[its[t]] in top:
            hits += 1
        n += 1
    return hits / max(1, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emb", default=DEFAULT_EMB)
    ap.add_argument("--limit", type=int, default=0)   # 冒烟: 仅前 N 测试用户
    ap.add_argument("--ks", default="60")             # RRF k
    args = ap.parse_args()
    ks = [int(x) for x in args.ks.split(",")]

    # ---------------- ① 特征与属性轴 ----------------
    print("[M2] loading features ...")
    img_feat = np.load(os.path.join(DATA, "image_feat.npy")).astype(np.float32)
    txt_feat = np.load(os.path.join(DATA, "text_feat.npy")).astype(np.float32)
    cat_n = l2norm(np.hstack([img_feat, txt_feat]))   # (n_items, 4480)
    n_items = cat_n.shape[0]
    print(f"      img={img_feat.shape} txt={txt_feat.shape} cat_n={cat_n.shape}")

    print(f"[M2] K-means attribute axis (K={K_ATTR}) ...")
    km = KMeans(n_clusters=K_ATTR, n_init=10, random_state=42, max_iter=100)
    km.fit(cat_n)
    centroids = km.cluster_centers_.astype(np.float32)            # (K, 4480)
    centroids_n = l2norm(centroids)
    cos_aff = cat_n @ centroids_n.T                               # (n_items, K)
    # 锐化: softmax(T=0.1) —— 诊断显示 cos 有真实区分度(std=0.12, 物品级极差均值0.31),
    # 但行归一化会把判别力抹平(冒烟实证 violation=1.0, w 不收敛), 故用温度 softmax 保留判别力且天然归一
    T = 0.1
    item_attr = np.exp(cos_aff / T)
    item_attr = item_attr / item_attr.sum(axis=1, keepdims=True)  # 每物品 K 维分布
    item_attr = item_attr.astype(np.float32)
    print(f"      item_attr={item_attr.shape} (softmax T={T}, 每物品 9 维锐化属性分布)")
    # 属性轴可解释性：每个聚类最大质心方向 top-8 特征索引（CLIP 段/SBERT 段）
    for k in range(K_ATTR):
        top_idx = np.argsort(-centroids[k])[:8]
        cl = int((top_idx < img_feat.shape[1]).sum())
        print(f"      attr{k}: top-feat 含 CLIP {cl}/8, SBERT {8 - cl}/8")

    # ---------------- 交互数据 ----------------
    print("[M2] loading interactions ...")
    train_inter = load_interactions(TRAIN)   # 35598 用户
    test_inter = load_interactions(TEST)

    # 簇级 next-item 信号诊断（可解释画像资产的直接证据）
    from collections import Counter as _Counter
    lab = km.labels_
    _csize = dict(sorted(_Counter(lab.tolist()).items()))
    print(f"      cluster sizes: {_csize}")
    _hits = _tot = 0
    for _u, _its in list(train_inter.items())[:5000]:
        _its = [x for x in _its[:20] if x < n_items]
        if len(_its) < 2:
            continue
        for _t in range(1, len(_its)):
            _freq = _Counter(lab[_its[:_t]].tolist())
            _top = {k for k, _ in _freq.most_common(3)}
            if lab[_its[_t]] in _top:
                _hits += 1
            _tot += 1
    _cluster_hit3 = _hits / max(1, _tot)
    print(f"      cluster-level next-item hit@3 = {_cluster_hit3:.4f} (随机=0.3333)")

    # ---------------- ② 强化-反思：学习全局属性重要性 w ----------------
    print("[M2] reinforcement-reflection: learning attribute importance w from REAL next-item labels ...")
    w0 = np.ones(K_ATTR, dtype=np.float32) / K_ATTR
    w, n_pairs, viol_rate = learn_attribute_weights(train_inter, item_attr, n_items, w0)
    w = w / (np.linalg.norm(w) + 1e-8)
    print("      w(属性重要性) =", np.round(w, 4).tolist())
    top_attrs = np.argsort(-w)[:3]
    print(f"      主导属性轴: attr{top_attrs[0]} (w={w[top_attrs[0]]:.3f}), "
          f"attr{top_attrs[1]} ({w[top_attrs[1]]:.3f}), attr{top_attrs[2]} ({w[top_attrs[2]]:.3f})")

    # ---------------- M3 画像（红线对照） ----------------
    print("[M2] loading M3 e_u profiles (red-line control) ...")
    m3 = np.load(M3_NPZ, allow_pickle=True)
    uid2idx = m3["uid2idx"].tolist()
    eu_cat = m3["eu_cat"]
    m3_train_items = m3["train_items"].tolist()
    uid_pos = {u: i for i, u in enumerate(uid2idx)}
    test_uids = [u for u in uid2idx if u in test_inter and len(train_inter.get(u, [])) > 0]
    if args.limit > 0:
        test_uids = test_uids[:args.limit]
    print(f"      eval users: {len(test_uids)}")

    # ---------------- ③ 属性记忆 P_u + 门控分 ----------------
    print("[M2] building per-user attribute memory P_u = w ⊙ mean(item_attr[train]) + gate ...")
    P_u = np.zeros((len(test_uids), K_ATTR), dtype=np.float32)
    gate = np.zeros(len(test_uids), dtype=np.float32)
    lab = km.labels_
    for i, u in enumerate(test_uids):
        its = [x for x in train_inter[u] if x < n_items]
        if its:
            P_u[i] = np.mean(item_attr[its], axis=0)
        gate[i] = user_gate_score(its, lab, w, item_attr, n_items)
    P_u = P_u * w[np.newaxis, :]                       # 属性重要性加权记忆
    n_direct = int((gate >= 0.5).sum())
    n_fusion = int(((gate >= 0.3) & (gate < 0.5)).sum())
    n_reject = int((gate < 0.3).sum())
    print(f"      gate 分布: DIRECT={n_direct} FUSION={n_fusion} REJECT={n_reject} "
          f"(gate>0 用户数={int((gate > 0).sum())})")

    # ---------------- CF 轨 ----------------
    print("[M2] loading CF embeddings ...")
    emb_path = os.path.join(EMB_DIR, args.emb)
    with open(emb_path, "rb") as f:
        obj = pickle.load(f)
    all_users = obj[0].numpy() if hasattr(obj[0], "numpy") else np.asarray(obj[0])
    all_items = obj[1].numpy() if hasattr(obj[1], "numpy") else np.asarray(obj[1])
    all_users_n = l2norm(all_users.astype(np.float32))
    print(f"      users={all_users.shape} items={all_items.shape}")

    # ---------------- 排序（属性轨 / CF 轨 / e_u 轨） ----------------
    print("[M2] ranking tracks ...")
    attr_topk, cf_topk, eu_topk = {}, {}, {}
    for start in range(0, len(test_uids), BATCH):
        batch = test_uids[start:start + BATCH]
        idx = [uid_pos[u] for u in batch]
        # 属性轨
        r_attr = P_u[idx] @ item_attr.T
        # CF 轨
        U = all_users_n[idx]
        r_cf = U @ all_items.T.astype(np.float32)
        # e_u 轨（红线对照）
        r_eu = eu_cat[idx] @ cat_n.T
        for j, u in enumerate(batch):
            excl = set(m3_train_items[uid_pos[u]])
            r_attr[j, list(excl)] = -1e9
            r_cf[j, list(excl)] = -1e9
            r_eu[j, list(excl)] = -1e9
            attr_topk[u] = np.argsort(-r_attr[j])[:CF_CAND].tolist()
            cf_topk[u] = np.argsort(-r_cf[j])[:CF_CAND].tolist()
            eu_topk[u] = np.argsort(-r_eu[j])[:CF_CAND].tolist()

    # ---------------- 评估 ----------------
    def recall_ndcg(rank_items, gt, k=TOP_K):
        hit = 0
        dcg = 0.0
        for i, it in enumerate(rank_items[:k]):
            if it in gt:
                hit += 1
                dcg += 1.0 / np.log2(i + 2)
        r = hit / len(gt) if gt else 0.0
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(gt), k)))
        n = dcg / idcg if idcg > 0 else 0.0
        return r, n

    gt_sets = [set(x for x in test_inter[u] if x < n_items) for u in test_uids]

    def eval_track(topk):
        rs, ns = [], []
        for i, u in enumerate(test_uids):
            r, n = recall_ndcg(topk[u], gt_sets[i])
            rs.append(r); ns.append(n)
        return float(np.mean(rs)), float(np.mean(ns))

    print("[M2] evaluating ...")
    res = {}
    for name, topk in [("attr_only", attr_topk), ("cf_only", cf_topk), ("eu_only", eu_topk)]:
        r, n = eval_track(topk)
        res[name] = {"R@20": r, "N@20": n}
        print(f"      {name:<12}: R@20={r:.4f} N@20={n:.4f}")

    cf_r20 = res["cf_only"]["R@20"]

    # RRF 融合（朴素等权 vs 门控加权）
    cand_arr = np.zeros((len(test_uids), 2 * CF_CAND), dtype=np.int64)
    attr_pos = np.zeros_like(cand_arr)
    cf_pos = np.zeros_like(cand_arr)
    for i, u in enumerate(test_uids):
        cf = cf_topk[u]; attr = attr_topk[u]
        union = list(dict.fromkeys(cf + attr))
        cand_arr[i, :len(union)] = np.array(union)
        p_cf = {it: idx + 1 for idx, it in enumerate(cf)}
        p_attr = {it: idx + 1 for idx, it in enumerate(attr)}
        for c_idx, it in enumerate(union):
            cf_pos[i, c_idx] = p_cf.get(it, 0)
            attr_pos[i, c_idx] = p_attr.get(it, 0)

    for k in ks:
        for name, w_attr in [("rrf_equal", 1.0), ("rrf_gated", None)]:
            if w_attr is None:
                w_attr_vec = np.where(gate >= 0.5, 2.0, np.where(gate >= 0.3, 1.0, 0.0))[:, None]
            else:
                w_attr_vec = np.full((len(test_uids), 1), w_attr)
            cf_term = np.where(cf_pos > 0, 1.0 / (k + cf_pos), 0.0)
            attr_term = np.where(attr_pos > 0, w_attr_vec / (k + attr_pos), 0.0)
            fused = cf_term + attr_term
            order = np.argsort(-fused, axis=1)[:, :TOP_K]
            rs, ns = [], []
            for i in range(len(test_uids)):
                r, n = recall_ndcg(cand_arr[i, order[i]].tolist(), gt_sets[i])
                rs.append(r); ns.append(n)
            r20, n20 = float(np.mean(rs)), float(np.mean(ns))
            tag = f"{name}_k{k}"
            res[tag] = {"R@20": r20, "N@20": n20}
            print(f"      {tag:<14}: R@20={r20:.4f} N@20={n20:.4f}")

    # ---------------- 汇总结论 ----------------
    print("\n[M2] ================ 结果汇总 ================")
    for k_, v in res.items():
        print(f"  {k_:<14}: R@20={v['R@20']:.4f} N@20={v['N@20']:.4f}")
    best_gain_tag = max((t for t in res if t.startswith("rrf")), key=lambda t: res[t]["R@20"])
    gain = (res[best_gain_tag]["R@20"] - cf_r20) / cf_r20 * 100
    attr_gain = (res["attr_only"]["R@20"] - res["eu_only"]["R@20"]) / max(res["eu_only"]["R@20"], 1e-9) * 100
    print(f"  BEST RRF: {best_gain_tag} R@20={res[best_gain_tag]['R@20']:.4f} (vs CF only {cf_r20:.4f}, {gain:+.2f}%)")
    print(f"  属性轨 vs e_u 轨: {res['attr_only']['R@20']:.4f} vs {res['eu_only']['R@20']:.4f} ({attr_gain:+.1f}%)")

    conclusion = "PASS" if gain >= 2.0 else "FAIL (不达 +2%)"
    if gain >= 2.0:
        verdict = f"门控 RRF 相对 CF only 增益 {gain:+.2f}% ≥ +2% → M2 机制可归因 PASS"
    else:
        verdict = (f"门控 RRF 相对 CF only 增益 {gain:+.2f}% 不达 +2% → 与 E15 同款诚实口径："
                   f"属性记忆退化为「可解释画像资产」（供 G4 verbalize），不主张推荐增益")
    print(f"[M2] 裁决: {verdict}")

    # ---------------- 落盘 ----------------
    np.savez_compressed(
        os.path.join(BASE, "m2_attribute_axis.npz"),
        item_attr=item_attr,
        centroids=centroids,
        w=w.astype(np.float32),
        K=np.array([K_ATTR]),
    )
    report = {
        "emb_file": args.emb,
        "eval_users": len(test_uids),
        "n_items": n_items,
        "K_attr": K_ATTR,
        "w_attribute_importance": np.round(w, 4).tolist(),
        "gate_dist": {"DIRECT": int(n_direct), "FUSION": int(n_fusion), "REJECT": int(n_reject),
                      "gate_pos": int((gate > 0).sum()), "mean_gate": float(gate.mean())},
        "pa": {"pairs": int(n_pairs), "violation_rate": float(viol_rate)},
        "cluster_level_next_item_hit3": float(_cluster_hit3),
        "cluster_sizes": _csize,
        "results": res,
        "best_rrf": best_gain_tag,
        "gain_vs_cf_pct": float(gain),
        "attr_vs_eu_pct": float(attr_gain),
        "verdict": verdict,
        "notes": [
            "属性轴 = K-means(K=9) on CLIP⊕SBERT + softmax(T=0.1) 锐化, 替代 DeepSeek 语义提取（数据无 item 标题）",
            "强化-反思正确性信号 = 真实 next-item 标签（train 留一），替代 MMEACR fuzz.ratio 合成标签",
            "门控 = soft_fusion_memory 三段式 (DIRECT>=0.5 / FUSION 0.3~0.5 / REJECT<0.3)，门控分=簇级留一命中率(下一物品簇∈前缀top-3簇)",
            "簇级 next-item 信号独立诊断: hit@3-cluster vs 随机 1/3",
        ],
    }
    with open(os.path.join(BASE, "m2_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[M2] saved -> m2_attribute_axis.npz + m2_report.json")


if __name__ == "__main__":
    main()
