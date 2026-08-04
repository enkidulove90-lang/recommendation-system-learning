"""
fetch_mm_data.py — 拉取真实 Amazon 多模态数据(MMSSL / LATTICE 约定)

数据来源: HKUDS/MMSSL 处理后数据(Google Drive)
  https://drive.google.com/drive/folders/1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0
  该数据 "compatible with MMSSL/LATTICE/MICRO, requires no additional preprocessing",
  包含 (1) 交互 train/test/valid.txt  (2) 多模态特征 image_feat.npy(行序 = item id)

本脚本做的事:
  1. 用 gdown 下载 Google Drive 文件夹(HKUDS/MMSSL 的 all-datasets 文件夹)
  2. 取出 Amazon-Sports(或 Amazon-Baby)子目录
  3. 把交互数据从 MMSSL 格式转换为 LightGCN++ dataloader 要求的
     "user item1 item2 ..." 分组格式, 写入 code/data/amazon-sports/
  4. 复制 image_feat.npy(及 image_feat_clip.npy 若存在)到同目录
     —— 行序与 item id 1:1 对齐, 覆盖合成特征即可用真实特征跑 idea2

注意:
  - Google Drive 在受限沙箱里可能下载失败; 失败不影响 idea2 管线(合成特征已可用).
    在能访问 Drive 的机器上直接 `python fetch_mm_data.py` 即可换入真实特征.
  - MMSSL 提供的是 Amazon-Baby / Amazon-Sports (非 Beauty). Beauty 可用 SMORE
    仓库的同结构数据(kennethorq/SMORE)替换, 流程一致.
"""
import os
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
DST = os.path.join(ROOT, 'data', 'amazon-sports')

MMSSL_DRIVE_FOLDER = '1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0'   # HKUDS/MMSSL all datasets
DATASET_NAME = 'Amazon-Sports'   # MMSSL 子目录名(注意是 Sports 非 Beauty)


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
    # gdown 文件夹下载(可能较大; 超时由调用方控制)
    gdown.download_folder(folder_id, output=out_dir, quiet=False, use_cookies=False)


def to_grouped(src_file, dst_file):
    """MMSSL 格式(user item 每行一条) → LightGCN++ 分组(user item1 item2...)."""
    d = {}
    with open(src_file) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            u, i = int(parts[0]), int(parts[1])
            d.setdefault(u, []).append(i)
    with open(dst_file, 'w') as f:
        for u in sorted(d.keys()):
            f.write(f"{u} " + " ".join(str(x) for x in d[u]) + "\n")


def main():
    import tempfile
    tmp = tempfile.mkdtemp(prefix='mmssl_')
    ensure_gdown()
    download(MMSSL_DRIVE_FOLDER, tmp)

    # 找 Amazon-Sports 子目录
    src = None
    for root, dirs, _ in os.walk(tmp):
        for d in dirs:
            if d.lower() == DATASET_NAME.lower():
                src = os.path.join(root, d)
                break
        if src:
            break
    if not src:
        # 退而求其次: 直接找含 image_feat.npy 的目录
        for root, _, files in os.walk(tmp):
            if 'image_feat.npy' in files:
                src = root
                break
    if not src:
        print(f"[fetch] ERROR: 在下载内容中未找到 {DATASET_NAME} 或 image_feat.npy")
        return 1

    print(f"[fetch] found source: {src}")
    os.makedirs(DST, exist_ok=True)
    for split in ['train', 'valid', 'test']:
        s = os.path.join(src, f'{split}.txt')
        if os.path.exists(s):
            to_grouped(s, os.path.join(DST, f'{split}.txt'))
            print(f"[fetch] converted {split}.txt")
    # 复制特征(行序 = item id)
    for feat in ['image_feat.npy', 'image_feat_clip.npy', 'text_feat.npy']:
        s = os.path.join(src, feat)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(DST, feat))
            print(f"[fetch] copied {feat} -> {DST}")
    print(f"[fetch] DONE. Real features ready at {DST}")
    print(f"[fetch] 现在可直接跑: python run_idea2.py  (无需 --use_mm 之外改动)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
