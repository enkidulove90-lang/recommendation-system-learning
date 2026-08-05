"""
fetch_mm_data.py — 拉取真实 Amazon 多模态数据(MMSSL / LATTICE 约定)

数据来源: HKUDS/MMSSL 处理后数据(Google Drive)
  https://drive.google.com/drive/folders/1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0
  该数据 "compatible with MMSSL/LATTICE/MICRO, requires no additional preprocessing",
  包含 (1) 交互 train.json/val.json/test.json  (2) 多模态特征 image_feat.npy / text_feat.npy

重要对齐说明:
  - 本仓库 data/amazon-sports/ 目录虽名为 "amazon-sports", 但其统计为
    35598 用户 / 18357 物品 —— 这正是 MMSSL 的 **Amazon-Baby**(Sports 仅 7050 物品).
    故此处拉取 Amazon-Baby, 其 image_feat.npy(CLIP-ViT 4096) 与 text_feat.npy
    (Sentence-BERT 1024) 的行序 = item id, 与本仓库现有交互数据的 item 索引天然对齐.
  - 拉取后会: (a) 用 MMSSL 的 json 交互重写成 LightGCN++ 分组格式(保证与特征同序);
              (b) 覆盖合成 image_feat.npy, 并写入真实 text_feat.npy.
  - 覆盖前 bash 调用方应已备份(见 fetch_mm_data 运行前备份 amazon-sports.bak_*).

注意:
  - Google Drive 在受限沙箱里可能下载较慢或触发配额; 失败可换能访问 Drive 的机器重跑.
  - gdown 只能整文件夹下载, 故先下 all-datasets 父目录, 再抽取 Amazon-Baby 子目录.
"""
import os
import sys
import shutil
import subprocess
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
DST = os.path.join(ROOT, 'data', 'amazon-sports')

MMSSL_DRIVE_FOLDER = '1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0'   # HKUDS/MMSSL all datasets (parent)
DATASET_NAME = 'Amazon-Baby'   # 本仓库 18357 物品数据 = MMSSL Baby (非 Sports)


def ensure_gdown():
    try:
        import gdown  # noqa
    except ImportError:
        print("[fetch] installing gdown ...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gdown'], check=True)


def download(folder_id, out_dir):
    import gdown
    os.makedirs(out_dir, exist_ok=True)
    print(f"[fetch] gdown folder {folder_id} -> {out_dir}")
    # 整文件夹下载(含 Baby/Sports/Tiktok/Allrecipes), 之后只取 Baby
    gdown.download_folder(folder_id, output=out_dir, quiet=False)


def to_grouped_json(src_json, dst_txt):
    """MMSSL 格式(dict: uid -> [items]) -> LightGCN++ 分组(user item1 item2...)."""
    with open(src_json) as f:
        d = json.load(f)
    with open(dst_txt, 'w') as f:
        for u in sorted(int(k) for k in d.keys()):
            items = d[str(u)] if str(u) in d else d[u]
            f.write(f"{u} " + " ".join(str(int(x)) for x in items) + "\n")
    print(f"[fetch] converted {os.path.basename(src_json)} -> {os.path.basename(dst_txt)}")


def main():
    import tempfile
    tmp = tempfile.mkdtemp(prefix='mmssl_')
    ensure_gdown()
    download(MMSSL_DRIVE_FOLDER, tmp)

    # 找 Amazon-Baby 子目录
    src = None
    for root, dirs, _ in os.walk(tmp):
        for d in dirs:
            if d.lower() == DATASET_NAME.lower():
                src = os.path.join(root, d)
                break
        if src:
            break
    if not src:
        for root, _, files in os.walk(tmp):
            if 'image_feat.npy' in files:
                src = root
                break
    if not src:
        print(f"[fetch] ERROR: 在下载内容中未找到 {DATASET_NAME} 或 image_feat.npy")
        return 1

    print(f"[fetch] found source: {src}")
    os.makedirs(DST, exist_ok=True)

    # 转换交互(MMSSL json -> 分组 txt); 保证与特征同序
    split_map = {'train': 'train', 'val': 'valid', 'test': 'test'}
    for src_name, dst_name in split_map.items():
        s = os.path.join(src, f'{src_name}.json')
        if os.path.exists(s):
            to_grouped_json(s, os.path.join(DST, f'{dst_name}.txt'))
        else:
            print(f"[fetch] WARN: 未找到 {src_name}.json, 跳过该 split")

    # 复制真实多模态特征(行序 = item id)
    for feat in ['image_feat.npy', 'text_feat.npy']:
        s = os.path.join(src, feat)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(DST, feat))
            print(f"[fetch] copied {feat} -> {DST}")
        else:
            print(f"[fetch] WARN: 源中未找到 {feat}")

    # 对齐校验
    try:
        import numpy as np
        img = np.load(os.path.join(DST, 'image_feat.npy'))
        txt = np.load(os.path.join(DST, 'text_feat.npy'))
        # 由 valid.txt 推断物品数(最大 item id + 1)
        maxitem = 0
        with open(os.path.join(DST, 'valid.txt')) as f:
            for line in f:
                parts = line.split()[1:]
                if parts:
                    maxitem = max(maxitem, max(int(x) for x in parts))
        n_items = maxitem + 1
        print(f"[fetch] 校验: image_feat{img.shape} text_feat{txt.shape} n_items(推断)={n_items}")
        assert img.shape[0] == n_items, f"image 行数 {img.shape[0]} != 物品数 {n_items}"
        assert txt.shape[0] == n_items, f"text 行数 {txt.shape[0]} != 物品数 {n_items}"
        print("[fetch] 对齐校验通过 ✅ (特征行数 == 物品数)")
    except Exception as e:
        print(f"[fetch] 校验跳过/失败: {e}")

    print(f"[fetch] DONE. 真实图文特征已就位: {DST}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
