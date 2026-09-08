# -*- coding: utf-8 -*-
"""
M3: e_u 多模态用户画像落地脚本
===============================
e_u = mean(CLIP⊕SBERT of user's interacted items)  —— 零 LLM、纯 numpy、CPU 立即可跑。

产物:
  1. e_u 画像落盘: baseline/LightGCNpp/code/m3_eu_profiles.npz
     - uid2idx: 测试用户 id 数组 (N_test,)
     - eu_img : (N_test, 4096)  图像特征均值 (L2 归一化)
     - eu_txt : (N_test, 384)   文本特征均值 (L2 归一化)
     - eu_cat : (N_test, 4480)  图像⊕文本 concat 均值 (L2 归一化) ← M1 内容轨主用
     - train_neg_mask: (N_test, n_items) 该用户 train 交互过的物品 mask(排除用)
  2. 一致性验证指标:
     - hit@20: e_u 与 held-out 交互物品的余弦 top-20 命中率(画像有效性的直接证据)
     - mean_cos_pos / mean_cos_rand: 画像与正例/随机物品的平均余弦差
  3. 纯内容轨 R@20 基线(不融合, 仅画像排序) —— M1 的"轨2单独"对照

用法(PowerShell, 纯 numpy 无 torch):
  & python run_m3_eu.py
"""
import os
import sys
import json
import numpy as np

# stdout 重配置 utf-8，防 Windows GBK 崩溃
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------- 路径 ----------------
BASE = os.path.dirname(os.path.abspath(__file__))          # .../LightGCNpp/code
DATA = os.path.join(BASE, "..", "data", "amazon-baby-mmssl")
IMG_FEAT = os.path.join(DATA, "image_feat.npy")   # (n_items, 4096)
TXT_FEAT = os.path.join(DATA, "text_feat.npy")    # (n_items, 384)
TRAIN = os.path.join(DATA, "train.txt")
TEST = os.path.join(DATA, "test.txt")
OUT_NPZ = os.path.join(BASE, "m3_eu_profiles.npz")
OUT_JSON = os.path.join(BASE, "m3_report.json")

TOP_K = 20
NEG_SAMPLE = 1000  # 随机物品采样数(一致性验证用)


def load_interactions(path):
    """每行: uid item1 item2 ... → {uid: [items]}"""
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            uid = int(parts[0])
            items = [int(x) for x in parts[1:]]
            data[uid] = items
    return data


def l2norm(x):
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


def main():
    print("[M3] loading features ...")
    img_feat = np.load(IMG_FEAT).astype(np.float32)   # (n_items, 4096)
    txt_feat = np.load(TXT_FEAT).astype(np.float32)   # (n_items, 384)
    n_items = img_feat.shape[0]
    print(f"      img={img_feat.shape} txt={txt_feat.shape}")

    print("[M3] loading interactions ...")
    train_inter = load_interactions(TRAIN)   # {uid: [items]}
    test_inter = load_interactions(TEST)

    # 归一化特征(余弦用)
    img_n = l2norm(img_feat)
    txt_n = l2norm(txt_feat)
    cat_n = l2norm(np.hstack([img_feat, txt_feat]))  # (n_items, 4480)

    # 测试用户(在 test 中出现且 train 中有交互的)
    test_uids = sorted([u for u in test_inter if u in train_inter and len(train_inter[u]) > 0])
    N_test = len(test_uids)
    print(f"[M3] test users: {N_test} / n_items: {n_items}")

    eu_img = np.zeros((N_test, img_feat.shape[1]), dtype=np.float32)
    eu_txt = np.zeros((N_test, txt_feat.shape[1]), dtype=np.float32)
    eu_cat = np.zeros((N_test, img_feat.shape[1] + txt_feat.shape[1]), dtype=np.float32)
    train_items_list = []   # 每用户 train 交互列表(供 M1 排除, 避免 2.6GB 稠密矩阵)

    rng = np.random.default_rng(42)
    pos_cos = np.zeros(N_test)
    rand_cos = np.zeros(N_test)

    for i, uid in enumerate(test_uids):
        items = train_inter[uid]
        items_arr = np.array(items, dtype=np.int64)
        items_arr = items_arr[items_arr < n_items]
        if len(items_arr) == 0:
            train_items_list.append([])
            continue
        eu_img[i] = img_n[items_arr].mean(axis=0)
        eu_txt[i] = txt_n[items_arr].mean(axis=0)
        eu_cat[i] = cat_n[items_arr].mean(axis=0)
        train_items_list.append(items_arr.tolist())

        # 一致性: 画像 vs test 正例 / 随机物品
        pos_items = [x for x in test_inter[uid] if x < n_items]
        if pos_items:
            pos_cos[i] = eu_cat[i] @ cat_n[pos_items].mean(axis=0)
            rand_items = rng.choice(n_items, size=min(NEG_SAMPLE, n_items), replace=False)
            rand_cos[i] = eu_cat[i] @ cat_n[rand_items].mean(axis=0)

    # L2 归一化画像
    eu_img = l2norm(eu_img)
    eu_txt = l2norm(eu_txt)
    eu_cat = l2norm(eu_cat)

    # ============ 纯内容轨 R@20 基线(画像排序, 分块避免 2.6GB 稠密矩阵) ============
    print("[M3] content-only R@20 baseline (e_u 画像排序) ...")
    BATCH = 2000
    hit_all = 0
    total = 0
    with open(os.path.join(BASE, "m3_content_top20.json"), "w", encoding="utf-8") as f:
        f.write("{\n")
        for start in range(0, N_test, BATCH):
            end = min(start + BATCH, N_test)
            rating = eu_cat[start:end] @ cat_n.T        # (B, n_items)
            # 排除 train 交互
            for j in range(start, end):
                for it in train_items_list[j]:
                    rating[j - start, it] = -1e9
            topk_idx = np.argsort(-rating, axis=1)[:, :TOP_K]
            for j in range(start, end):
                uid = test_uids[j]
                gt = set(x for x in test_inter[uid] if x < n_items)
                if gt:
                    hit_all += len(gt & set(topk_idx[j - start].tolist()))
                    total += 1
                    f.write(f'  "{uid}": {json.dumps(topk_idx[j - start].tolist())},\n')
        f.write('  "_total_users": %d\n}' % total)
    recall_content = hit_all / max(total, 1) / TOP_K

    # 汇总一致性
    mean_pos = float(pos_cos[pos_cos != 0].mean()) if (pos_cos != 0).any() else 0.0
    mean_rand = float(rand_cos[rand_cos != 0].mean()) if (rand_cos != 0).any() else 0.0
    margin = mean_pos - mean_rand

    print(f"[M3] === 一致性验证 ===")
    print(f"      mean_cos(画像 vs 正例)  = {mean_pos:.4f}")
    print(f"      mean_cos(画像 vs 随机)  = {mean_rand:.4f}")
    print(f"      画像-正例边际            = {margin:+.4f}")
    print(f"[M3] === 内容轨基线 ===")
    print(f"      content-only R@{TOP_K} = {recall_content:.4f}")

    # 落盘
    np.savez_compressed(
        OUT_NPZ,
        uid2idx=np.array(test_uids, dtype=np.int64),
        eu_img=eu_img,
        eu_txt=eu_txt,
        eu_cat=eu_cat,
        train_items=np.array(train_items_list, dtype=object),
    )
    report = {
        "test_users": N_test,
        "n_items": n_items,
        "mean_cos_pos": mean_pos,
        "mean_cos_rand": mean_rand,
        "margin": margin,
        "content_only_R@20": recall_content,
        "top_k": TOP_K,
        "note": "e_u = L2(mean(L2(features of train items)))",
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[M3] saved -> {OUT_NPZ}")
    print(f"[M3] saved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
