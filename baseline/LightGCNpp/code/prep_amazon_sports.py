"""
prep_amazon_sports.py — 为 idea2 准备 Amazon-Sports 多模态数据(本地合成特征版)

作用:
  1. 把 SELFRec/dataset/amazon-sports 的 3 列 (user item weight) 交互数据
     转换成 LightGCN++ dataloader 要求的 "user item1 item2..." 分组格式,
     写入 code/data/amazon-sports/{train,valid,test}.txt
  2. 生成维度/结构真实的合成视觉特征(无需 Google Drive 即可端到端验证 idea2):
       image_feat.npy     : [n_items, 4096]  CNN 特征(MMSSL 维度)
       image_feat_clip.npy: [n_items, 64]    CLIP 特征
     特征结构: 所有物品共享一个 64 维隐因子; 热门物品(度数高)的隐因子被拉向
     "热门质心", 模拟真实 Amazon 中同类目热门商品视觉更相似的现象.
     这样 aligner 能学到"对热门物品用视觉、对冷启物品退化为 ID"(置信度门控自然生效),
     且 CNN/CLIP 同源 → 视图一致性 InfoNCE 有真实正例信号.

真实数据替换: 拿到 MMSSL 的 image_feat.npy(行序=item id)后, 直接覆盖
  code/data/amazon-sports/image_feat.npy 即可, 其余代码零改动.
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'SELFRec', 'dataset', 'amazon-sports')
DST = os.path.join(HERE, '..', 'data', 'amazon-sports')

RNG = np.random.default_rng(2026)


def convert_split(path, fname):
    """3 列 (user item weight) → dict[user] = [items]"""
    d = {}
    with open(os.path.join(path, fname)) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            u, i = int(parts[0]), int(parts[1])
            d.setdefault(u, []).append(i)
    return d


def write_grouped(path, fname, d):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, fname), 'w') as f:
        for u in sorted(d.keys()):
            items = d[u]
            f.write(f"{u} " + " ".join(str(x) for x in items) + "\n")


def main():
    os.makedirs(DST, exist_ok=True)
    # 1) 转换交互数据
    for split in ['train', 'valid', 'test']:
        d = convert_split(SRC, f'{split}.txt')
        write_grouped(DST, f'{split}.txt', d)
    # 统计 item 数
    all_items = set()
    for split in ['train', 'valid', 'test']:
        d = convert_split(SRC, f'{split}.txt')
        for u, items in d.items():
            all_items.update(items)
    n_items = max(all_items) + 1
    print(f"[prep] amazon-sports: n_items={n_items}, n_users~={len(convert_split(SRC,'train.txt'))}")

    # 2) 计算物品度数(用于注入热门视觉结构)
    train_d = convert_split(SRC, 'train.txt')
    deg = np.zeros(n_items, dtype=np.float64)
    for u, items in train_d.items():
        for i in items:
            deg[i] += 1
    deg_max = deg.max() + 1e-8
    strength = np.clip(deg / deg_max, 0, 1) * 0.6   # 热门物品强度更高

    # 3) 生成 64 维隐因子(所有物品共享), 热门拉向质心
    latent = RNG.normal(0, 1, size=(n_items, 64)).astype(np.float32)
    popular_centroid = latent[deg > deg_max * 0.5].mean(axis=0, keepdims=True) \
        if (deg > deg_max * 0.5).any() else latent.mean(axis=0, keepdims=True)
    for i in range(n_items):
        latent[i] = latent[i] + strength[i] * (popular_centroid[0] - latent[i])

    # CLIP = 64 维隐因子本身(已 L2 归一化模拟)
    clip = latent / (np.linalg.norm(latent, axis=1, keepdims=True) + 1e-8)
    # CNN = 随机投影到 4096 维 + 噪声(与 CLIP 同源 → 视角一致性有信号)
    W = RNG.normal(0, 1 / np.sqrt(64), size=(64, 4096)).astype(np.float32)
    cnn = latent @ W
    cnn = cnn + 0.25 * RNG.normal(0, 1, size=cnn.shape).astype(np.float32)
    cnn = cnn.astype(np.float32)

    np.save(os.path.join(DST, 'image_feat.npy'), cnn)
    np.save(os.path.join(DST, 'image_feat_clip.npy'), clip)
    print(f"[prep] saved image_feat.npy {cnn.shape}, image_feat_clip.npy {clip.shape}")
    print(f"[prep] done -> {DST}")


if __name__ == '__main__':
    main()
