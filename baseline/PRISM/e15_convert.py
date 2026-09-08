# -*- coding: utf-8 -*-
"""
E15 数据转换：把 baseline/LightGCNpp/data/amazon-baby-mmssl 转成 PRISM 原码契约。

输入（我方 LightGCN++ mmssl 格式）：
  - train.txt / valid.txt / test.txt ：每行 `user_id 物品...`，物品 0-based，0 是真实物品。
  - image_feat.npy (N,4096) / text_feat.npy (N,384) ：特征行 i 对应物品 i（0-based）。

输出（PRISM 契约）：
  - data/amazon-baby-mmssl/reviews_amazon-baby-mmssl.txt ：单文件，物品整体 +1（0=pad）。
      每行 = `user_id 物品...`，full_seq = train + valid + test[0]（让 PRISM 内部 LOO 复现 valid/test）。
  - data/amazon-baby-mmssl/image_features_amazon-baby-mmssl.pt / text_features_*.pt ：
      torch.Tensor(N,dim)，行 i 对应 PRISM 物品 i+1（原样拷贝，无需重映射）。

运行：PowerShell（torch 在 Git Bash 下 segfault）
  & "C:\Program Files\Python311\python.exe" e15_convert.py
"""
import os
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_BIN = os.path.dirname(HERE)  # .../baseline
SRC = os.path.join(REPO_BIN, "LightGCNpp", "data", "amazon-baby-mmssl")
NAME = "amazon-baby-mmssl"
OUT_DIR = os.path.join(HERE, "data", NAME)
OUT_REVIEWS = os.path.join(OUT_DIR, f"reviews_{NAME}.txt")
OUT_IMG = os.path.join(OUT_DIR, f"image_features_{NAME}.pt")
OUT_TXT = os.path.join(OUT_DIR, f"text_features_{NAME}.pt")


def read_split(path):
    """返回 {user_id: [items]}（0-based，原值）。"""
    d = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            u = int(parts[0])
            items = [int(x) for x in parts[1:]]
            d[u] = items
    return d


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    train = read_split(os.path.join(SRC, "train.txt"))
    valid = read_split(os.path.join(SRC, "valid.txt"))
    test = read_split(os.path.join(SRC, "test.txt"))

    users = set(train) | set(valid) | set(test)
    kept = 0
    dropped = 0
    max_raw_item = 0
    with open(OUT_REVIEWS, "w", encoding="utf-8") as f:
        for u in sorted(users):
            full = (train.get(u, []) + valid.get(u, []) + test.get(u, [])[:1])
            full = [x for x in full if x >= 0]  # 保险：过滤异常负值
            if len(full) < 3:
                dropped += 1
                continue
            max_raw_item = max(max_raw_item, max(full))
            # 整体 +1 偏移（0=padding，物品从 1 起）
            new_items = [x + 1 for x in full]
            f.write(str(u) + " " + " ".join(str(x) for x in new_items) + "\n")
            kept += 1

    print(f"[txt] users={len(users)} kept={kept} dropped(<3)={dropped} max_raw_item={max_raw_item}")

    # 特征：原样拷贝为 torch .pt
    for npy, pt in [(os.path.join(SRC, "image_feat.npy"), OUT_IMG),
                    (os.path.join(SRC, "text_feat.npy"), OUT_TXT)]:
        arr = np.load(npy)
        t = torch.from_numpy(arr.astype(np.float32))
        torch.save(t, pt)
        print(f"[feat] {os.path.basename(npy)} shape={tuple(t.shape)} -> {os.path.basename(pt)}")

    print(f"[done] reviews -> {OUT_REVIEWS}")


if __name__ == "__main__":
    main()
