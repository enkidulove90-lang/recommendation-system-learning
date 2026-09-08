"""Generate 4 polished XHS-style images for 2608.14429 (PriCoRec)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "sans-serif"]
rcParams["axes.unicode_minus"] = False

OUT_DIR = Path(r"C:/Users/xu.yan1/papers/recommendation-system-learning/data/parsed/2608.14429_隐私感知云-端协同广告推荐框架/images")
OUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1080, 1440
DPI = 120


def new_fig():
    plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)


def save(name: str):
    plt.tight_layout(pad=0.5)
    path = OUT_DIR / name
    plt.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.15)
    plt.close()
    return path


def img_features_split():
    new_fig()
    ax = plt.gca()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    ax.text(5, 9.4, "云-端特征隔离设计", fontsize=34, ha="center", va="top", weight="bold", color="#1a1a1a")
    ax.text(5, 8.8, "敏感特征留在设备端，云端只访问非敏感信号", fontsize=18, ha="center", va="top", color="#666666")

    cloud = mpatches.FancyBboxPatch((0.5, 5.0), 4.0, 3.2, boxstyle="round,pad=0.05,rounding_size=0.3",
                                    facecolor="#e8f4fd", edgecolor="#2196F3", linewidth=3)
    ax.add_patch(cloud)
    ax.text(2.5, 7.75, "☁️ 云端可访问特征", fontsize=22, ha="center", va="top", weight="bold", color="#1565C0")
    for i, it in enumerate(["物品特征", "上下文信号", "广告组 ID", "店铺 ID", "候选 1000→100"]):
        ax.text(2.5, 7.2 - i * 0.45, f"• {it}", fontsize=17, ha="center", va="top", color="#333333")

    device = mpatches.FancyBboxPatch((5.5, 5.0), 4.0, 3.2, boxstyle="round,pad=0.05,rounding_size=0.3",
                                     facecolor="#fff3e0", edgecolor="#FF9800", linewidth=3)
    ax.add_patch(device)
    ax.text(7.5, 7.75, "📱 设备端私有特征", fontsize=22, ha="center", va="top", weight="bold", color="#E65100")
    for i, it in enumerate(["性别", "职业", "年龄", "细粒度行为", "时间信号"]):
        ax.text(7.5, 7.2 - i * 0.45, f"• {it}", fontsize=17, ha="center", va="top", color="#333333")

    center = mpatches.FancyBboxPatch((3.5, 3.0), 3.0, 1.4, boxstyle="round,pad=0.05,rounding_size=0.3",
                                     facecolor="#e8f5e9", edgecolor="#4CAF50", linewidth=3)
    ax.add_patch(center)
    ax.text(5, 3.85, "🔒 隐私保护", fontsize=20, ha="center", va="top", weight="bold", color="#2E7D32")
    ax.text(5, 3.35, "敏感特征不上云，云端只传 logit", fontsize=15, ha="center", va="top", color="#555555")

    ax.annotate("", xy=(4.4, 3.85), xytext=(2.5, 5.0), arrowprops=dict(arrowstyle="->", color="#2196F3", lw=2))
    ax.annotate("", xy=(5.6, 3.85), xytext=(7.5, 5.0), arrowprops=dict(arrowstyle="->", color="#FF9800", lw=2))
    save("xhs_features_split.png")


def img_cloud_pre_ranking():
    new_fig()
    datasets = ["OpenMCC", "TaobaoAd", "Ali-CCP"]
    prico_gauc = [80.29, 89.36, 73.69]
    base_gauc = [80.06, 89.25, 72.93]
    prico_r100 = [50.41, 68.29, 47.72]
    base_r100 = [49.82, 67.85, 46.92]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    x = range(len(datasets))
    width = 0.35

    bars1 = ax1.bar([i - width / 2 for i in x], base_gauc, width, label="DP-SGD（最强基线）", color="#90A4AE")
    bars2 = ax1.bar([i + width / 2 for i in x], prico_gauc, width, label="PriCoRec", color="#42A5F5")
    ax1.set_ylabel("gAUC", fontsize=16)
    ax1.set_title("云端预排序：gAUC 对比", fontsize=24, weight="bold", pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets, fontsize=16)
    ax1.legend(fontsize=13)
    ax1.set_ylim(70, 92)
    for bar in bars2:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.3, f"{h:.2f}", ha="center", va="bottom", fontsize=13, weight="bold")

    bars3 = ax2.bar([i - width / 2 for i in x], base_r100, width, label="DP-SGD（最强基线）", color="#90A4AE")
    bars4 = ax2.bar([i + width / 2 for i in x], prico_r100, width, label="PriCoRec", color="#66BB6A")
    ax2.set_ylabel("R@100", fontsize=16)
    ax2.set_title("云端预排序：R@100 对比", fontsize=24, weight="bold", pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(datasets, fontsize=16)
    ax2.legend(fontsize=13)
    ax2.set_ylim(44, 72)
    for bar in bars4:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 0.4, f"{h:.2f}", ha="center", va="bottom", fontsize=13, weight="bold")

    plt.suptitle("云端预排序性能：PriCoRec vs 最强基线", fontsize=28, weight="bold", y=0.98)
    save("xhs_cloud_pre_ranking.png")


def img_on_device_ranking():
    new_fig()
    datasets = ["OpenMCC", "TaobaoAd", "Ali-CCP"]
    prico_r10 = [13.87, 21.74, 24.10]
    base_r10 = [11.37, 17.38, 20.97]
    gains = [p - b for p, b in zip(prico_r10, base_r10)]

    fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    x = range(len(datasets))
    width = 0.35

    bars1 = ax.bar([i - width / 2 for i in x], base_r10, width, label="DP-SGD", color="#90A4AE")
    bars2 = ax.bar([i + width / 2 for i in x], prico_r10, width, label="PriCoRec", color="#FFA726")

    ax.set_ylabel("R@10", fontsize=18)
    ax.set_title("端上排序 R@10 提升", fontsize=30, weight="bold", pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, fontsize=18)
    ax.legend(fontsize=15)
    ax.set_ylim(8, 26)

    for bar, gain in zip(bars2, gains):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.35, f"{h:.2f}\n(+{gain:.2f})",
                ha="center", va="bottom", fontsize=15, weight="bold", color="#E65100")
    save("xhs_on_device_ranking.png")


def img_key_numbers():
    new_fig()
    ax = plt.gca()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    ax.text(5, 9.4, "PriCoRec 关键数字", fontsize=36, ha="center", va="top", weight="bold", color="#1a1a1a")
    ax.text(5, 8.8, "RecSys'26 隐私感知云-端协同广告推荐", fontsize=18, ha="center", va="top", color="#666666")

    cards = [
        ("3", "个公开数据集", "OpenMCC / TaobaoAd / Ali-CCP", "#e3f2fd", "#2196F3"),
        ("+4.36", "R@10 最大提升", "TaobaoAd 端上排序", "#fff3e0", "#FF9800"),
        ("+0.76", "gAUC 最大提升", "Ali-CCP 云端预排序", "#e8f5e9", "#4CAF50"),
        ("1000→100", "级联漏斗", "云端预排压缩候选集", "#f3e5f5", "#9C27B0"),
    ]
    positions = [(1.2, 6.0), (5.5, 6.0), (1.2, 2.6), (5.5, 2.6)]
    for (x, y), (num, label, desc, bg, fg) in zip(positions, cards):
        box = mpatches.FancyBboxPatch((x, y), 3.3, 2.7, boxstyle="round,pad=0.05,rounding_size=0.3",
                                      facecolor=bg, edgecolor=fg, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + 1.65, y + 2.15, num, fontsize=36, ha="center", va="top", weight="bold", color=fg)
        ax.text(x + 1.65, y + 1.45, label, fontsize=20, ha="center", va="top", weight="bold", color="#333333")
        ax.text(x + 1.65, y + 0.85, desc, fontsize=14, ha="center", va="top", color="#555555")
    save("xhs_key_numbers.png")


if __name__ == "__main__":
    img_features_split()
    img_cloud_pre_ranking()
    img_on_device_ranking()
    img_key_numbers()
    manifest = {"generated": [str(OUT_DIR / n) for n in [
        "xhs_features_split.png",
        "xhs_cloud_pre_ranking.png",
        "xhs_on_device_ranking.png",
        "xhs_key_numbers.png",
    ]]}
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
