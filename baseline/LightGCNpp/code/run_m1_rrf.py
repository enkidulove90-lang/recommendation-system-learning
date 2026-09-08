# -*- coding: utf-8 -*-
"""
M1: RRF 双轨融合落地脚本
========================
CF 轨(LightGCN++ 已训练嵌入) ⊕ 内容轨(e_u 多模态画像余弦) → 倒数秩融合 → R@20/N@20 对比。

数据来源:
  - CF 轨: embs/<config>.pkl  = [all_users(35598,64), all_items(18357,64)]  (CPU torch.Tensor)
  - 内容轨: m3_eu_profiles.npz (M3 产物, eu_cat 画像 + train_items 排除清单)
  - 真值:   data/amazon-baby-mmssl/test.txt

输出:
  - m1_report.json: 单轨 vs RRF(k,w 网格) 的 R@20/N@20
  - 控制台表格 + 融合增益结论

用法(PowerShell, torch 脚本):
  & python run_m1_rrf.py [--emb amazon-baby-mmssl_seed2026_..._fc0.8_pr32.pkl]
"""
import os
import sys
import json
import argparse
import pickle

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data", "amazon-baby-mmssl")
EMB_DIR = os.path.join(BASE, "embs")
M3_NPZ = os.path.join(BASE, "m3_eu_profiles.npz")
TEST = os.path.join(DATA, "test.txt")
TOP_K = 20

DEFAULT_EMB = "amazon-baby-mmssl_seed2026_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl4_mm_mr0.001_mt0.1_fc0.8_pr32.pkl"


def load_interactions(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            data[int(parts[0])] = [int(x) for x in parts[1:]]
    return data


def rrf_fusion(rank1, rank2, k):
    """rank: list of item ids (desired order). 返回 {item: rrf_score}"""
    scores = {}
    for item in rank1:
        scores[item] = 1.0 / (k + 1)          # rank=1 → 1/(k+1)
    for item in rank2:
        if item in scores:
            scores[item] += 1.0 / (k + 1)     # 两轨都出现
        else:
            scores[item] = 1.0 / (k + len(rank2) + 1)  # 未出现在 rank1 → 给 rank2 位置
    return scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emb", default=DEFAULT_EMB)
    ap.add_argument("--ks", default="40,60,100")
    ap.add_argument("--ws", default="1.0,2.0,4.0,8.0")  # w_cf: 内容轨权重固定 1.0, 扫 CF 相对权重
    ap.add_argument("--limit", type=int, default=0)  # 冒烟: 仅前 N 个测试用户
    args = ap.parse_args()

    ks = [int(x) for x in args.ks.split(",")]
    ws = [float(x) for x in args.ws.split(",")]

    # ---------------- CF 轨: 加载嵌入 ----------------
    print("[M1] loading CF embeddings ...")
    emb_path = os.path.join(EMB_DIR, args.emb)
    with open(emb_path, "rb") as f:
        obj = pickle.load(f)
    all_users, all_items = obj[0], obj[1]
    all_users = all_users.numpy() if hasattr(all_users, "numpy") else np.asarray(all_users)
    all_items = all_items.numpy() if hasattr(all_items, "numpy") else np.asarray(all_items)
    print(f"      users={all_users.shape} items={all_items.shape}")

    # ---------------- 内容轨: e_u 画像 ----------------
    print("[M1] loading M3 e_u profiles ...")
    m3 = np.load(M3_NPZ, allow_pickle=True)
    uid2idx = m3["uid2idx"].tolist()
    eu_cat = m3["eu_cat"]
    train_items = m3["train_items"].tolist()
    uid_pos = {u: i for i, u in enumerate(uid2idx)}
    print(f"      profiles={eu_cat.shape} users={len(uid2idx)}")

    # ---------------- 内容特征 (余弦排序用) ----------------
    img_feat = np.load(os.path.join(DATA, "image_feat.npy")).astype(np.float32)
    txt_feat = np.load(os.path.join(DATA, "text_feat.npy")).astype(np.float32)
    cat_n = np.hstack([img_feat, txt_feat])
    cat_n = cat_n / (np.linalg.norm(cat_n, axis=1, keepdims=True) + 1e-8)

    # ---------------- 真值 ----------------
    test_inter = load_interactions(TEST)
    test_uids = [u for u in uid2idx if u in test_inter]
    if args.limit > 0:
        test_uids = test_uids[:args.limit]
    print(f"[M1] eval users: {len(test_uids)}")

    # ---------------- CF 轨排序 ----------------
    print("[M1] computing CF ranking (sigmoid(U@I^T)) ...")
    # 分块: 每块 1000 用户, 排序取 top200 (够了, RRF 只需前若干)
    CF_CAND = 200
    cf_topk = {}      # uid -> list of item ids
    B = 1000
    all_users_n = all_users / (np.linalg.norm(all_users, axis=1, keepdims=True) + 1e-8)
    for start in range(0, len(test_uids), B):
        batch = test_uids[start:start + B]
        idx = [uid_pos[u] for u in batch]
        U = all_users_n[idx]
        rating = U @ all_items.T          # (B, n_items)
        for j, u in enumerate(batch):
            exclude = set(train_items[uid_pos[u]])
            rating[j, list(exclude)] = -1e9
            top = np.argsort(-rating[j])[:CF_CAND]
            cf_topk[u] = top.tolist()
    print(f"      CF topk done for {len(cf_topk)} users")

    # ---------------- 内容轨排序 ----------------
    print("[M1] computing content ranking (e_u cos) ...")
    emb_topk = {}
    for start in range(0, len(test_uids), B):
        batch = test_uids[start:start + B]
        idx = [uid_pos[u] for u in batch]
        Eu = eu_cat[idx]
        rating = Eu @ cat_n.T
        for j, u in enumerate(batch):
            exclude = set(train_items[uid_pos[u]])
            rating[j, list(exclude)] = -1e9
            top = np.argsort(-rating[j])[:CF_CAND]
            emb_topk[u] = top.tolist()
    print(f"      content topk done for {len(emb_topk)} users")

    # ---------------- 评估 ----------------
    def recall_ndcg(rank_items, gt, k=TOP_K):
        """rank_items: list of item ids; gt: set"""
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

    # 单轨
    print("[M1] evaluating single tracks ...")
    cf_r, cf_n = [], []
    emb_r, emb_n = [], []
    for u in test_uids:
        gt = set(x for x in test_inter[u] if x < all_items.shape[0])
        r, n = recall_ndcg(cf_topk[u], gt)
        cf_r.append(r); cf_n.append(n)
        r, n = recall_ndcg(emb_topk[u], gt)
        emb_r.append(r); emb_n.append(n)
    cf_r20 = np.mean(cf_r); cf_n20 = np.mean(cf_n)
    emb_r20 = np.mean(emb_r); emb_n20 = np.mean(emb_n)

    # RRF 网格 (向量化: 预建 cf/emb 分数矩阵)
    print("[M1] RRF grid ...")
    # 统一候选集: 每用户 cf_topk ∪ emb_topk (<=400)
    cand_list = []
    cf_pos = np.zeros((len(test_uids), 400), dtype=np.int64)   # item -> position in cand_list
    emb_pos = np.zeros((len(test_uids), 400), dtype=np.int64)
    cand_arr = np.zeros((len(test_uids), 400), dtype=np.int64)
    for i, u in enumerate(test_uids):
        cf = cf_topk[u]
        emb = emb_topk[u]
        union = list(dict.fromkeys(cf + emb))   # 去重保序
        cand_arr[i, :len(union)] = np.array(union)
        pos_cf = {it: idx + 1 for idx, it in enumerate(cf)}
        pos_emb = {it: idx + 1 for idx, it in enumerate(emb)}
        for c_idx, it in enumerate(union):
            cf_pos[i, c_idx] = pos_cf.get(it, 0)
            emb_pos[i, c_idx] = pos_emb.get(it, 0)

    # ground truth 稀疏索引
    gt_sets = [set(x for x in test_inter[u] if x < all_items.shape[0]) for u in test_uids]

    results = {"cf_only": {"R@20": float(cf_r20), "N@20": float(cf_n20)},
               "content_only": {"R@20": float(emb_r20), "N@20": float(emb_n20)}}
    best = None
    for k in ks:
        for w in ws:
            # score = w*1/(k+cf_pos) + 1/(k+emb_pos); pos=0 → 该轨未出现
            cf_term = np.where(cf_pos > 0, w / (k + cf_pos), 0.0)
            emb_term = np.where(emb_pos > 0, 1.0 / (k + emb_pos), 0.0)
            fused_scores = cf_term + emb_term          # (N, 400)
            order = np.argsort(-fused_scores, axis=1)[:, :TOP_K]   # (N, 20) 索引到 cand_arr
            rrs, nns = [], []
            for i in range(len(test_uids)):
                fused = cand_arr[i, order[i]]
                r, n = recall_ndcg(fused.tolist(), gt_sets[i])
                rrs.append(r); nns.append(n)
            r20 = float(np.mean(rrs)); n20 = float(np.mean(nns))
            tag = f"RRF_k{k}_w{w}"
            results[tag] = {"R@20": r20, "N@20": n20}
            print(f"      {tag}: R@20={r20:.4f} N@20={n20:.4f}")
            if best is None or r20 > best[1]:
                best = (tag, r20)

    # 汇总
    print("\n[M1] ================ 结果汇总 ================")
    print(f"  CF only      : R@20={cf_r20:.4f} N@20={cf_n20:.4f}")
    print(f"  Content only : R@20={emb_r20:.4f} N@20={emb_n20:.4f}")
    for tag, v in results.items():
        print(f"  {tag:<18}: R@20={v['R@20']:.4f} N@20={v['N@20']:.4f}")
    if best:
        gain = (best[1] - cf_r20) / cf_r20 * 100
        print(f"\n  BEST: {best[0]} R@20={best[1]:.4f} (vs CF only {cf_r20:.4f}, {gain:+.2f}%)")

    results["best"] = best
    results["emb_file"] = args.emb
    with open(os.path.join(BASE, "m1_report.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[M1] saved -> m1_report.json")


if __name__ == "__main__":
    main()
