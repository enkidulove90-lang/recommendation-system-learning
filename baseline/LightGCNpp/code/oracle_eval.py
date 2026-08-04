"""
P2 — Oracle 层选择实验 (idea1 §1.2 决策点)

读取 main.py --save_layer_emb 1 保存的 [N, L+1, d] 逐层嵌入，
产出：
  表A  Oracle 上限 (固定 L=0..L  vs  逐用户选最优层 g*)
  表B  最优层 g*_u 在用户度数桶中的分布
  表C  各度数桶 × 固定 L 的 Recall@K 矩阵

用法:
  cd baseline/LightGCNpp/code
  python oracle_eval.py --dataset lastfm --k 20 \
      --emb_path embs/<config_seedXXX_..._nl4>.pkl
"""
import argparse
import os
import sys
import json
import pickle as pkl
import numpy as np
import torch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

DEVICE = torch.device('cpu')


def ndcg_at_k(ranked_items, gt_set, k):
    """ranked_items: list of item ids (top-k order); gt_set: set of ground-truth items."""
    dcg = 0.0
    for i, it in enumerate(ranked_items[:k]):
        if it in gt_set:
            dcg += 1.0 / np.log2(i + 2)
    # ideal: min(|gt|, k) relevant items at top
    ideal = min(len(gt_set), k)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal))
    return dcg / idcg if idcg > 0 else 0.0


def recall_at_k(ranked_items, gt_set, k):
    if len(gt_set) == 0:
        return 0.0
    hits = len(gt_set.intersection(set(ranked_items[:k])))
    return hits / len(gt_set)


def topk_per_layer(layer_users, layer_items, test_users, exclude_pos, test_gt, k, batch=256):
    """返回 rec_l: {u: [topk item ids]}"""
    rec = {}
    n_items = layer_items.shape[0]
    with torch.no_grad():
        for st in range(0, len(test_users), batch):
            bu = test_users[st:st + batch]
            bu_t = torch.tensor(bu, dtype=torch.long, device=DEVICE)
            ue = layer_users[bu_t]                       # [b, d]
            rating = torch.sigmoid(ue @ layer_items.t())  # [b, n_items]
            # exclude train/valid positives
            for j, u in enumerate(bu):
                ex = exclude_pos[u]
                if ex:
                    rating[j, torch.tensor(list(ex), dtype=torch.long, device=DEVICE)] = -(1 << 10)
            _, idx = torch.topk(rating, k=k)
            for j, u in enumerate(bu):
                rec[u] = idx[j].cpu().tolist()
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=str, default='lastfm')
    ap.add_argument('--emb_path', type=str, required=True, help='pkl saved by --save_layer_emb 1 (L=4)')
    ap.add_argument('--k', type=int, default=20)
    ap.add_argument('--out', type=str, default=None, help='json path to save results')
    args = ap.parse_args()

    # 关键：必须先解析自己的参数，再把 sys.argv 换成 register/world 认识的
    # 干净版本，否则 register 在 import 期调用 world.world()->parse_args()
    # 会因 --emb_path/--out 报 "unrecognized arguments"。
    sys.argv = ['oracle_eval', '--dataset', args.dataset]
    import world
    import dataloader
    import register
    from register import dataset
    global DEVICE
    DEVICE = world.device

    k = args.k
    with open(args.emb_path, 'rb') as f:
        blob = pkl.load(f)  # main.py 用 pickle.dump 保存，必须用 pickle.load
    # blob = [all_users, all_items, _all_users, _all_items]
    if len(blob) == 4:
        all_users, all_items, _all_users, _all_items = blob
    else:
        all_users, all_items = blob
        raise SystemExit('emb_path was saved WITHOUT per-layer emb (need --save_layer_emb 1)')

    L = _all_users.shape[1] - 1          # num propagation layers
    n_users = _all_users.shape[0]
    print(f'[oracle] L={L}, n_users={n_users}, n_items={all_items.shape[0]}, k={k}')

    test_users = [int(u) for u in dataset.testDict.keys()]
    # getUserPosItems expects an iterable of users and returns a list of per-user pos arrays
    _pos_list = dataset.getUserPosItems(test_users)
    exclude_pos = {int(u): set(int(x) for x in p) for u, p in zip(test_users, _pos_list)}   # train+valid pos
    test_gt = {u: set(dataset.testDict[u]) for u in test_users}

    # degree per user
    deg = {u: int(dataset.users_D[u]) for u in test_users}

    # ---- per-layer top-k ----
    rec_by_layer = {}
    for l in range(L + 1):
        lu = _all_users[:, l, :].to(DEVICE)
        li = _all_items[:, l, :].to(DEVICE)
        rec_by_layer[l] = topk_per_layer(lu, li, test_users, exclude_pos, test_gt, k)

    # ---- per-user recall/ndcg per layer ----
    recall = {u: np.zeros(L + 1) for u in test_users}
    ndcg = {u: np.zeros(L + 1) for u in test_users}
    for u in test_users:
        gt = test_gt[u]
        for l in range(L + 1):
            rk = rec_by_layer[l][u]
            recall[u][l] = recall_at_k(rk, gt, k)
            ndcg[u][l] = ndcg_at_k(rk, gt, k)

    # ===== 表A: fixed L vs oracle =====
    mean_recall = [float(np.mean([recall[u][l] for u in test_users])) for l in range(L + 1)]
    mean_ndcg = [float(np.mean([ndcg[u][l] for u in test_users])) for l in range(L + 1)]
    oracle_recall = float(np.mean([recall[u].max() for u in test_users]))
    oracle_ndcg = float(np.mean([ndcg[u].max() for u in test_users]))
    best_fixed_l = int(np.argmax(mean_recall))
    best_fixed_recall = mean_recall[best_fixed_l]
    gain_over_best_fixed = oracle_recall - best_fixed_recall

    tableA = {
        'fixed_L_recall@%d' % k: {f'L={l}': mean_recall[l] for l in range(L + 1)},
        'fixed_L_ndcg@%d' % k: {f'L={l}': mean_ndcg[l] for l in range(L + 1)},
        'best_fixed_L': best_fixed_l,
        'best_fixed_recall@%d' % k: best_fixed_recall,
        'oracle_recall@%d' % k: oracle_recall,
        'oracle_ndcg@%d' % k: oracle_ndcg,
        'oracle_gain_over_best_fixed(%)': gain_over_best_fixed * 100,
    }

    # ===== 表B: degree bucket x g* =====
    buckets = [(1, 5), (6, 10), (11, 20), (21, 50), (51, 10**9)]
    bucket_label = {b: (f'{b[0]}-{b[1]}' if b[1] < 10**9 else f'>{b[0]}') for b in buckets}
    gstar = {u: int(recall[u].argmax()) for u in test_users}   # ties -> lowest layer
    tableB = {}
    for b in buckets:
        members = [u for u in test_users if b[0] <= deg[u] <= b[1]]
        if not members:
            continue
        dist = {f'g*={l}': 0 for l in range(L + 1)}
        for u in members:
            dist[f'g*={gstar[u]}'] += 1
        n = len(members)
        tableB[bucket_label[b]] = {
            'n_users': n,
            'share(%)': round(100 * n / len(test_users), 2),
            'dist': {kk: round(100 * vv / n, 1) for kk, vv in dist.items()},
            'mode_g*': int(max(dist, key=dist.get).split('=')[1]),
        }

    # ===== 表C: bucket x fixed-L recall =====
    tableC = {}
    for b in buckets:
        members = [u for u in test_users if b[0] <= deg[u] <= b[1]]
        if not members:
            continue
        row = {}
        for l in range(L + 1):
            row[f'L={l}'] = round(float(np.mean([recall[u][l] for u in members])), 4)
        tableC[bucket_label[b]] = row

    result = {
        'dataset': args.dataset, 'L': L, 'k': k,
        'tableA': tableA, 'tableB': tableB, 'tableC': tableC,
    }
    print('\n========== 表A: Oracle 上限 ==========')
    print(json.dumps(tableA, indent=2, ensure_ascii=False))
    print('\n========== 表B: 度数桶 × 最优层 g* ==========')
    print(json.dumps(tableB, indent=2, ensure_ascii=False))
    print('\n========== 表C: 度数桶 × 固定L Recall@%d ==========' % k)
    print(json.dumps(tableC, indent=2, ensure_ascii=False))

    decision = 'ABANDON idea1' if gain_over_best_fixed * 100 < 3 else (
        '轻量规则版' if gain_over_best_fixed * 100 < 8 else '可学习版')
    print(f'\n>>> Oracle 增益 = {gain_over_best_fixed*100:.2f}%  →  建议: {decision}')

    out = args.out or (args.emb_path.rsplit('.', 1)[0] + '_oracle.json')
    with open(out, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'[oracle] saved -> {out}')


if __name__ == '__main__':
    main()
