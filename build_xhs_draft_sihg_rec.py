# -*- coding: utf-8 -*-
"""
build_xhs_draft_sihg_rec.py
===========================
SIHG-Rec（ACM TORS, DOI 10.1145/3847662）小红书草稿。

论文没有 arXiv 版、ACM 直连 403 → 用 OpenCLI 真实 Chrome 会话 fetch 拿到 CC-BY 官方 PDF
（fetch_acm_pdf.py），再用 PyMuPDF 按图注定位裁剪矢量图、4x 渲染成高清 PNG
（extract_sihg_assets.py）。

配图策略（用户要求：高质量图 + 有架构图、好看优先）：
  1. Fig.1 总览架构图（封面，1852×1259）
  2. 自制「冷启动数字卡」（论文 Table 6 的数字，手机上比原表更可读）
  3. Fig.2 消融（分组柱状图，配色好）
  4. Fig.3 稀疏度分析（三数据集折线，冷/稀疏用户）
  5. Fig.11 自适应权重动态（机制故事：行为模态权重从 0.7 升到 1.0）
  6. Fig.5 超参热力图（学习率 × 正则权重，体现严谨性）
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "sihg_rec"
IMAGES = PARSED / "images"

PAPER_URL = "https://doi.org/10.1145/3847662"
PDF_PATH = PARSED / "10.1145_3847662.pdf"


def font(size: int, bold: bool = False):
    cands = ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"] if bold else ["C:/Windows/Fonts/msyh.ttc"]
    for c in cands:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------- 自制：冷启动数字卡
# 数据来源：论文 Table 6（每个冷用户只保留 3 条交互），COHESION = 最强基线
COLD = [
    ("Baby",     "0.0145", "0.0286", "+97.2%", "0.0231", "0.0451", "+95.2%", "0.0078", "0.0154", "+97.4%", "0.0104", "0.0203", "+95.2%"),
    ("Sports",   "0.0155", "0.0295", "+90.3%", "0.0246", "0.0472", "+91.9%", "0.0087", "0.0163", "+87.4%", "0.0111", "0.0209", "+88.3%"),
    ("Clothing", "0.0118", "0.0228", "+93.2%", "0.0190", "0.0364", "+91.6%", "0.0063", "0.0118", "+87.3%", "0.0084", "0.0158", "+88.1%"),
]
METRICS = ["Recall@10", "Recall@20", "NDCG@10", "NDCG@20"]


def draw_cold_start_card(out: Path) -> Path:
    W, H = 1840, 1080
    img = Image.new("RGB", (W, H), (250, 251, 253))
    d = ImageDraw.Draw(img)

    BLUE, ACCENT, GREY, DARK = (36, 88, 168), (198, 78, 40), (120, 128, 140), (30, 34, 42)
    d.rectangle([0, 0, W, 14], fill=BLUE)

    f_t1, f_t2 = font(60, True), font(30)
    f_head, f_ds, f_val, f_pct = font(32, True), font(40, True), font(34), font(40, True)

    d.text((70, 62), "冷启动：每个冷用户只留 3 条交互", font=f_t1, fill=DARK)
    d.text((70, 146), "随机抽走 20% 用户，每人只保留 3 条交互训练；SIHG-Rec vs 最强基线 COHESION",
           font=f_t2, fill=GREY)

    x0, x1 = 70, W - 70
    y = 224
    col_ds = 250
    col_w = (x1 - x0 - col_ds) / 4

    # 表头
    d.rounded_rectangle([x0, y, x1, y + 74], radius=12, fill=(232, 238, 248))
    d.text((x0 + 28, y + 20), "数据集", font=f_head, fill=BLUE)
    for i, m in enumerate(METRICS):
        cx = x0 + col_ds + i * col_w
        d.text((cx + 40, y + 20), m, font=f_head, fill=BLUE)
    y += 74

    # 数据行
    for r, row in enumerate(COLD):
        rh = 176
        bg = (255, 255, 255) if r % 2 == 0 else (245, 247, 250)
        d.rectangle([x0, y, x1, y + rh], fill=bg)
        d.line([x0, y, x1, y], fill=(226, 230, 238), width=2)
        d.text((x0 + 28, y + 66), row[0], font=f_ds, fill=DARK)
        for i in range(4):
            cx = x0 + col_ds + i * col_w
            before, after, pct = row[1 + i * 3], row[2 + i * 3], row[3 + i * 3]
            d.text((cx + 40, y + 30), before + "  →  " + after, font=f_val, fill=DARK)
            d.text((cx + 40, y + 100), pct, font=f_pct, fill=ACCENT)
        y += rh

    d.line([x0, y, x1, y], fill=(200, 206, 216), width=3)
    d.text((70, y + 40), "四项指标 × 三个数据集：提升 87.3% ~ 97.4%（全部 p < 0.01）",
           font=font(38, True), fill=BLUE)
    d.text((70, y + 100), "数据来源：论文 Table 6（User cold-start analysis）",
           font=font(26), fill=GREY)

    img.save(out, optimize=True)
    return out


card = draw_cold_start_card(IMAGES / "fig0_coldstart_card.png")
print("card:", card, Image.open(card).size)

FIG_ORDER = [
    "fig1_overview.png",          # 封面：总览架构图
    "fig0_coldstart_card.png",    # 自制：冷启动数字卡（Table 6）
    "fig2_ablation.png",          # 消融
    "fig3_sparsity.png",          # 稀疏度分析
    "fig11_adaptive.png",         # 自适应权重动态
    "fig5_hyper_lr.png",          # 超参热力图
]

figure_meta = {
    "fig1_overview.png": ("architecture",
        "论文总览架构图（Fig. 1. The overview structure of SIHG-Rec）。左上：语义与交互同构图构建（训练前，用户/物品各有语义图与交互图，物品图用文本/图像特征求相似度后 Top-k 建边，交互图按共现关系建边）；右上：双阶段融合的早期阶段（文本/ID/图像编码后用行为引导校准）；中下：同构图增强（训练中）四条边分别对应 semantic-item / interactive-item / semantic-user / interactive-user；右下：后期融合；左下：自适应优化损失（L_Adaptive + L_Standard BPR + λ||Θ||）。"),
    "fig0_coldstart_card.png": ("custom_card",
        "自制数字卡（标注为自制）：把论文 Table 6 的冷启动结果整理成手机可读版——三个数据集 × 四个指标，COHESION → SIHG-Rec 的绝对值和相对提升。"),
    "fig2_ablation.png": ("result",
        "消融实验（Fig. 2）：8 个变体在 Baby/Sports/Clothing 上的 Recall@20 与 NDCG@20。变体含 w/o Semantic（去语义图）、w/o Interactive（去交互图）、w/o Adaptive（去自适应损失）、w/o Behavior（不校准行为模态）、r MeanPool、w Early（换早融合）、w Late（换晚融合）与完整 SIHG-Rec。"),
    "fig3_sparsity.png": ("result",
        "稀疏度分析（Fig. 3）：按训练交互数把用户分桶后各方法的 Recall@20。越稀疏的一段差距越明显，说明增益主要来自交互证据极少的用户。"),
    "fig11_adaptive.png": ("mechanism",
        "自适应权重动态（Fig. 11）：训练过程中文本/视觉/行为三个模态的权重变化。此外附了 Fig. 10（clothing 数据集交互图统计）以说明图构建前的邻居数分布。"),
    "fig5_hyper_lr.png": ("hyperparameter",
        "超参分析（Fig. 5）：学习率 × 正则化权重的 Recall@20 热力图（三个数据集各一张）。"),
}
(PARSED / "sihg_rec_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "ACM TORS 官方 PDF（DOI 10.1145/3847662, CC-BY）。所有图来自论文原文，矢量内容按图注定位后以 4x 渲染（≈288 DPI）；其中 fig0_coldstart_card.png 为依据 Table 6 自制的数字卡。",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

summary = {
    "paper_id": "10.1145/3847662",
    "arxiv_id": None,
    "title_zh": "两张图 + 双阶段融合，冷启动涨 97%",
    "title_en": "SIHG-Rec: Unleashing the Power of Semantic and Interactive Homogeneous Graphs via Dual-Stage Fusion for Multimodal Recommendation",
    "venue": "ACM Transactions on Recommender Systems (TORS), accepted 2026-09-03, online 2026-09-14",
    "doi": "10.1145/3847662",
    "license": "CC-BY 4.0（开放获取）",
    "authors": ["Jinfeng Xu (HKU)", "Zheyu Chen (BIT)", "Wei Wang (MPU)", "Xiping Hu (BIT)", "Sang-Wook Kim (Hanyang)", "Edith Ngai (HKU)"],
    "one_liner": "多模态推荐里图文特征只长在物品侧，用户侧没有；SIHG-Rec 同时建语义同构图与交互同构图、并把早/晚融合串成两阶段，每个冷用户只留 3 条交互时四项指标相对最强基线提升 87.3%~97.4%。",
    "problem_definition": {
        "task_type": "多模态推荐（用户冷启动）",
        "challenges": [
            "同构图基本只用语义（图文相似）建边，交互（协同）信号被浪费",
            "多模态融合多为单阶段：早融合抹掉模态特性，晚融合抓不住跨模态关系",
            "用户侧没有天然图文特征，交互极少的冷用户几乎无信息可用",
        ],
    },
    "main_contributions": [
        {"point": "同时构建语义同构图与交互同构图（用户侧 + 物品侧），用户多模态表示由交互过的物品特征均值聚合得到。"},
        {"point": "两张图训练前预算并冻结，不增加训练开销，且与模型解耦。"},
        {"point": "双阶段融合：早期用行为引导校准降噪并保留模态特性，后期再融合表示。"},
        {"point": "自适应优化：动态给表现较差的模态更高权重，保证模态间均衡学习。"},
    ],
    "datasets": [{"name": "Baby"}, {"name": "Sports"}, {"name": "Clothing"}, {"name": "TikTok (短剧/短视频场景)"}],
    "baselines": ["MF-BPR", "LightGCN", "DualGNN", "LATTICE", "FREEDOM", "MENTOR", "SMORE", "HPMRec", "COHESION", "LGMRec"],
    "metrics": ["Recall@10", "Recall@20", "NDCG@10", "NDCG@20"],
    "training": {"env": "3 个公开数据集（5-core），视觉 4096 维 / 文本 384 维；5 个随机种子取均值",
                 "baseline_for_gain": "COHESION（SIGIR'25）"},
    "main_results": {
        "cold_start": "每冷用户仅留 3 条交互：Baby R@10 0.0145→0.0286 (+97.2%)、N@10 +97.4%；Sports R@10 +90.3%、R@20 +91.9%；Clothing R@10 +93.2%、N@10 +87.3%；四项指标提升区间 87.3%~97.4%，全部 p<0.01",
        "overall": "常规设置全面最优但幅度小：Baby R@20 0.1052→0.1055、Sports 0.1137→0.1150、Clothing 0.0983→0.1005（对 COHESION）",
        "efficiency": "Baby 每 epoch 3.66s（COHESION 4.47s、HPMRec 21.03s），显存 2.80GB",
    },
    "ablation": {"conclusions": [
        "去掉语义同构图或交互同构图都会掉 → 两类图都必要",
        "去掉自适应损失会掉 → 模态均衡学习有效",
        "不校准行为模态会掉；换早融合/晚融合都不如双阶段",
    ]},
    "reproducibility": {"code_release": "论文正文明示开源地址：https://github.com/Jinfeng-Xu/Multimodal-Recommendation-Library（MIT，作者持续维护的多模态推荐模型库，318 stars，最近推送 2026-10-12）；但截至 2026-10-13 该库 src/models（27 个模型）与 src/configs/model（26 个配置）尚未包含 SIHG-Rec 实现，两份 README 也无 SIHG 条目 → 属“论文声明开源、实现待补”状态。作者另有 NLGCL / NLGCL-Plus / COHESION / IIMRec 等独立仓库。", "code_url": "https://github.com/Jinfeng-Xu/Multimodal-Recommendation-Library", "code_status": "declared_but_not_yet_released (as of 2026-10-13)"},
    "artifacts": {
        "pdf": "data/parsed/sihg_rec/10.1145_3847662.pdf",
        "figures": "data/parsed/sihg_rec/images/",
        "fetch_script": "fetch_acm_pdf.py（OpenCLI 真实浏览器 fetch 官方 CC-BY PDF）",
        "extract_script": "extract_sihg_assets.py（按图注定位裁剪矢量图 + 4x 渲染）",
    },
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "10.1145_3847662_sihg_rec_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary ok")

TITLE = "两张图+双阶段融合，冷启动涨97%"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 一句话：多模态推荐里图文特征都长在物品上、用户身上没有，所以冷用户最难。这篇 ACM TORS 论文给用户也建了图：每个冷用户只留 3 条交互时，四项指标比最强基线高 87%~97%。\n"
    "\n"
    "🧠 问题：用户侧没有「内容」可用\n"
    "以前做法缺两块：① 同构图基本只按「图文像不像」建边，「行为像不像」被丢了；② 融合多为单阶段——早融合抹掉各模态特点，晚融合又抓不住模态间关系。\n"
    "\n"
    "✨ 怎么做的（看图 1）\n"
    "两张同构图一起建，用户侧物品侧各一张：语义图按图文相似度连边，交互图按历史共现连边。用户没有自己的图文特征，就用「他交互过的物品特征取平均」当他的多模态表示。两张图都在训练前算好并冻结，不增加训练开销。\n"
    "融合分两步：早期先用行为信号校准（压掉与推荐无关的噪声、保住各模态特性），后期再融合各模态表示。最后加自适应优化——哪个模态学得差就给它更高权重（图 5：行为模态从 0.7 提到 1.0）。\n"
    "\n"
    "📊 数字\n"
    "1. 冷启动（抽走 20% 用户、每人只留 3 条交互）：Baby 的 R@10 从 0.0145 升到 0.0286（+97.2%）、N@10 +97.4%；Sports R@10 +90.3%；Clothing N@10 +87.3%。四项指标三个数据集，涨幅 87.3%~97.4%，全部 p<0.01。\n"
    "2. 常规设置也全面最优，但幅度很小：Baby R@20 0.1052→0.1055、Sports 0.1137→0.1150（对 COHESION）。\n"
    "3. 消融（图 2）：去掉语义图 / 交互图 / 自适应，不校准行为模态，或换成早融合、晚融合，都会掉——四个部件都必要。\n"
    "4. 效率：Baby 上 3.66 秒/epoch（COHESION 4.47、HPMRec 21.03）。\n"
    "\n"
    "💡 对我们的意义\n"
    "用户侧没内容，可以用「他碰过的东西」补上；图分开建（语义+交互）比揉在一起更可控。也别只看总体指标——卖点几乎全在冷启动那一档。\n"
    "\n"
    "⚠️ 局限：只在 Baby/Sports/Clothing（+TikTok）验证；冷启动涨幅大但绝对值仍低（R@10 0.0286≈2.9%）；图预计算冻结，依赖上游图文特征质量。\n"
    "\n"
    "📄 论文（ACM TORS 2026-09）：https://doi.org/10.1145/3847662\n"
    "✨ 关注我，持续拆解推荐系统最新论文 📚"
)
print("title (%d): %s" % (len(TITLE), TITLE))
print("body (%d)" % len(BODY))
assert len(BODY) <= 1000, "body too long: %d" % len(BODY)

missing = [p for p in FIG_ORDER if not (IMAGES / p).exists()]
assert not missing, "缺图: %s" % missing
for p in FIG_ORDER:
    im = Image.open(IMAGES / p)
    print("   %-34s %sx%s  %dKB" % (p, im.size[0], im.size[1], (IMAGES / p).stat().st_size // 1024))

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="10.1145/3847662",
    platform="xhs",
    canonical_url=PAPER_URL,
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": PAPER_URL, "pdf": "https://dl.acm.org/doi/pdf/10.1145/3847662", "code": ""},
    metadata={
        "topics": ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"],
        "pdf_path": str(PDF_PATH),
        "author": "",
        "source_attribution": "图表摘自论文（CC-BY），仅作学术解读。",
    },
    review_status="pending",
)
staged = XhsPublisher(root=ROOT).stage(package)
print("STAGED:", staged)

if os.environ.get("DRY_RUN"):
    print("DRY_RUN: 不发布")
    raise SystemExit(0)

result = XhsPublisher(root=ROOT).publish(staged["staged_id"])
print("PUBLISH RESULT:", result)
print("STAGED_ID:", staged["staged_id"])
