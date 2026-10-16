# -*- coding: utf-8 -*-
"""
build_xhs_draft_unipinrec.py
============================
UniPinRec（RecSys 2026 / Pinterest，arXiv 2606.00422）小红书草稿。

论文自带图较少（3 张矢量 PDF），但每张信息量都很大；再补 1 张从 PDF 裁出的 tikz 图
（fig_scaling_flops，用 crop_pdf_figure.py）+ 2 张自制数字卡，凑成 6 图。

重点（用户要求「突出重点」）：
  ① 全栈统一 = 输入格式 / 模型 / 训练 / 服务 四件事一起统一（不只统一架构）
  ② 线上真实涨点（两个场景 A/B）+  延迟 −11.1% / QPS +63.6%
  ③ 离线：排序 Hit@3 比线上排序模型高 14.7%，召回与生产模型持平
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2606.00422"
IMAGES = PARSED / "images"
PAPER_URL = "https://arxiv.org/abs/2606.00422"


def font(size: int, bold: bool = False):
    cands = ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"] if bold else ["C:/Windows/Fonts/msyh.ttc"]
    for c in cands:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def card_shell(title: str, subtitle: str, height: int):
    W = 1840
    img = Image.new("RGB", (W, height), (250, 251, 253))
    d = ImageDraw.Draw(img)
    BLUE = (36, 88, 168)
    d.rectangle([0, 0, W, 14], fill=BLUE)
    d.text((70, 60), title, font=font(58, True), fill=(30, 34, 42))
    d.text((70, 142), subtitle, font=font(29), fill=(120, 128, 140))
    return img, d, W


def draw_online_card(out: Path) -> Path:
    rows = [
        ("Board More Ideas", "场景内收藏", "+0.95%", True),
        ("Board More Ideas", "站内收藏", "+0.08%", False),
        ("通知", "推送打开", "+0.91%", False),
        ("通知", "推送打开（沉默用户）", "+1.72%", True),
        ("通知", "通知页收藏", "+3.84%", True),
        ("通知", "邮件点击", "+0.30%", False),
        ("通知", "周活跃用户", "+0.09%", False),
    ]
    rh, top = 118, 232
    img, d, W = card_shell("上线 A/B：两个真实场景都在涨", "对比基线 = Pinterest 原生产召回模型 PinRec（数据来源：论文 Table 5 / Table 6）",
                           top + rh * len(rows) + 150)
    x0, x1 = 70, W - 70
    DARK, GREY, ACCENT = (30, 34, 42), (120, 128, 140), (198, 78, 40)
    f_head, f_cell, f_val = font(30, True), font(33), font(44, True)

    d.rounded_rectangle([x0, top, x1, top + 72], radius=12, fill=(232, 238, 248))
    d.text((x0 + 28, top + 20), "场景", font=f_head, fill=(36, 88, 168))
    d.text((x0 + 560, top + 20), "指标", font=f_head, fill=(36, 88, 168))
    d.text((x0 + 1360, top + 20), "提升", font=f_head, fill=(36, 88, 168))
    y = top + 72
    for i, (scene, metric, val, hot) in enumerate(rows):
        d.rectangle([x0, y, x1, y + rh], fill=(255, 255, 255) if i % 2 == 0 else (245, 247, 250))
        d.line([x0, y, x1, y], fill=(226, 230, 238), width=2)
        d.text((x0 + 28, y + 40), scene, font=f_cell, fill=DARK)
        d.text((x0 + 560, y + 40), metric, font=f_cell, fill=DARK)
        d.text((x0 + 1360, y + 34), val, font=f_val, fill=ACCENT if hot else (60, 66, 76))
        y += rh
    d.line([x0, y, x1, y], fill=(200, 206, 216), width=3)
    d.text((70, y + 34), "两个场景日均服务数百万用户；站内收藏 +0.08% 是在全站量级上的净增益",
           font=font(30, True), fill=(36, 88, 168))
    img.save(out, optimize=True)
    return out


def draw_efficiency_card(out: Path) -> Path:
    rows = [
        ("端到端延迟（已上线 bf16 方案）", "-11.1%"),
        ("QPS（同方案）", "+63.6%"),
        ("单次排序前向 25.72ms → 6.56ms", "3.92×"),
        ("其中：KV 缓存复用（把排序的重算变成 decode）", "≈2.4×"),
        ("再加：fp8 + CUDA graph（相对 bf16+compile）", "≈1.25×"),
        ("再加：flex attention", "≈1.3×"),
    ]
    rh, top = 120, 236
    img, d, W = card_shell("一套模型，省在哪", "相对「召回/排序各部署一套」的基线（数据来源：论文 Table 2 / Table 3）",
                           top + rh * len(rows) + 168)
    x0, x1 = 70, W - 70
    DARK, ACCENT = (30, 34, 42), (198, 78, 40)
    f_cell, f_val = font(34), font(46, True)
    y = top
    for i, (label, val) in enumerate(rows):
        d.rectangle([x0, y, x1, y + rh], fill=(255, 255, 255) if i % 2 == 0 else (245, 247, 250))
        d.line([x0, y, x1, y], fill=(226, 230, 238), width=2)
        d.text((x0 + 30, y + 40), label, font=f_cell, fill=DARK)
        d.text((x1 - 300, y + 32), val, font=f_val, fill=ACCENT)
        y += rh
    d.line([x0, y, x1, y], fill=(200, 206, 216), width=3)
    d.text((70, y + 32), "三层优化基本正交，叠加才有 3.92×；线上为了不与下游排序器打架仍用 bf16 方案",
           font=font(29, True), fill=(36, 88, 168))
    d.text((70, y + 96), "fp8 方案 QPS 可到 +109.1%，但要等 batch 凑形状，延迟反而 +6.7%", font=font(27), fill=(120, 128, 140))
    img.save(out, optimize=True)
    return out


print("online card:", draw_online_card(IMAGES / "fig_card_online.png"))
print("efficiency card:", draw_efficiency_card(IMAGES / "fig_card_efficiency.png"))

FIG_ORDER = [
    "fig_unipinrec_flat.png",       # 封面：数据层 → 共享主干 → 双解码器
    "fig_comparison_table_slim.png",  # 统一到什么程度（HSTU / OneRec / Ours）
    "fig_serve_diagram.png",        # 线上服务拓扑：共享 KV 缓存
    "fig_card_online.png",          # 自制：上线 A/B 数字卡
    "fig_card_efficiency.png",      # 自制：效率数字卡
    "fig_scaling_flops.png",        # 容量扩展：Hit@3 vs FLOPs（从 PDF 裁出）
]

figure_meta = {
    "fig_unipinrec_flat.png": ("architecture",
        "论文主架构图（Figure 2）：Data Layer 把用户历史行为（Pin/Action/Search Query/Board）与未来曝光位（未来 feedview + 展示未点击的负样本）都编码进同一条序列，训练时对 20% 历史行为做随机掩码；Model Layer 用一条 GPT2 主干（自定义 mask 关闭未来位置之间的互相注意），分成 pin decoder（Sampled Softmax，负责召回）与 action decoder（BCE，负责排序）两个头；右上角是因果下三角注意力掩码的可视化。"),
    "fig_comparison_table_slim.png": ("framework",
        "论文对比图（Figure 1）：把「统一到哪一层」拆成输入格式 / 架构 / 训练 / 服务四个维度，对比 HSTU（只统一架构：2 种输入格式、共享主干但要两次前向、分开训练、两个独立服务）、OneRec（端到端生成式，但训练是多阶段流水线、且与既有服务栈不兼容）与 UniPinRec（1 种输入格式、1 次 prefill + 2 次 decode、单阶段联合损失、可直接替换原服务栈并复用计算）。"),
    "fig_serve_diagram.png": ("framework",
        "线上服务拓扑图（Figure 3）：召回与排序是两个独立 Triton 节点，中间是 CPU 上的 Faiss 索引。ANN 检索同时返回候选 Pin ID 和重建后的物品向量（省掉排序阶段单独取 embedding 的一次开销）；召回阶段算好的用户历史 KV 缓存在共享内存里直接给排序阶段复用（图左上 Shared KV Cache → Past Sequence KV → Ranking Inference）。"),
    "fig_card_online.png": ("custom_card",
        "自制数字卡（标注为自制）：把论文 Table 5（Board More Ideas）与 Table 6（通知）的线上 A/B 结果整理成手机可读版。"),
    "fig_card_efficiency.png": ("custom_card",
        "自制数字卡（标注为自制）：端到端延迟与 QPS 的线上收益，以及单次排序前向 3.92× 的三层来源（KV 缓存复用 / fp8+CUDA graph / flex attention），附 fp8 的延迟-QPS 权衡说明。"),
    "fig_scaling_flops.png": ("result",
        "容量扩展实验（Figure 4）：Hit@3 随相对 FLOPs 的变化，两条轴分别是加深层数（L=2→24，序列长固定 1024）与加长序列（S=256→2K，层数固定 12）。两条曲线都还在涨，说明模型未饱和；但深度随算力线性增长，序列长度是注意力的平方开销。"),
}
(PARSED / "unipinrec_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2606.00422 源包（submission/figures/*.pdf，矢量，3.6x 渲染）+ 从 PDF 按图注裁出的 Figure 4（crop_pdf_figure.py）+ 2 张自制数字卡。",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

summary = {
    "paper_id": "2606.00422",
    "title_zh": "召回+排序合成一个模型，延迟降11%",
    "title_en": "UniPinRec: Full-Stack Unification of Retrieval and Ranking at Pinterest",
    "venue": "RecSys 2026 (industrial track), Pinterest",
    "one_liner": "召回与排序虽都用大 Transformer 编码同一份用户行为，却长期分开训练与部署；UniPinRec 把输入格式/模型/训练/服务四层一起统一，线上互动约 +1%、端到端延迟 −11.1%、QPS +63.6%。",
    "problem_definition": {
        "task_type": "工业推荐系统的召回与排序统一（full-stack unification）",
        "challenges": [
            "两阶段各自训练大模型 → 参数/算力/服务成本重复付",
            "此前工作只统一架构：输入格式（交错 vs 非交错）、训练流程、服务栈仍割裂",
            "离线联合训练容易拖累召回质量，影响线上索引兼容性",
        ],
    },
    "main_contributions": [
        {"point": "全栈统一：一种输入格式、一个模型、一个训练阶段，可直接部署进既有服务栈。"},
        {"point": "Masked Action Modeling（MAM）：不交错拼接 Item/Action，避免上下文翻倍，使两任务共享权重成为可能。"},
        {"point": "Blended training examples：把行为序列与曝光位样本配对，联合满足召回与排序目标。"},
        {"point": "Cross-stage KV cache sharing：召回阶段的用户历史 KV 供排序复用，把排序从 prefill 变成 decode。"},
    ],
    "datasets": [{"name": "Pinterest Board More Ideas feed（离线训练与评估）"},
                 {"name": "线上 A/B：Board More Ideas 与 Notification 两个场景（日均数百万用户）"}],
    "baselines": ["TransAct V2 + DCNv2（线上排序模型）", "HSTU（统一检索排序 SOTA）", "PinRec（线上召回模型）",
                  "PinRec finetuned（先召回后微调排序）", "UniPinRec w/o item loss（只训排序）"],
    "metrics": ["Hit@3（排序）", "Recall@10（召回）", "线上场景收藏 / 推送打开 / 周活", "端到端延迟、QPS"],
    "main_results": {
        "offline_ranking": "Hit@3 = 0.10096（TransActV2+DCNv2 0.088008 → +14.7%；HSTU 0.097326；PinRec finetuned 0.095869）",
        "offline_retrieval": "Recall@10 = 0.77659（PinRec 0.77486 → +0.2%，持平不退化；HSTU 0.76161）",
        "online_bmi": "Board More Ideas：场景内收藏 +0.95%、站内收藏 +0.08%",
        "online_notification": "推送打开 +0.91%、沉默用户推送打开 +1.72%、通知页收藏 +3.84%、邮件点击 +0.30%、周活 +0.09%",
        "serving": "端到端延迟 −11.1%、QPS +63.6%（已上线 bf16 方案）；单次排序前向 25.72ms → 6.56ms（3.92×）；fp8 方案 QPS +109.1% 但延迟 +6.7%",
    },
    "ablation": {"conclusions": [
        "MAM 掩码率 p_mask：0.0 → Hit@3 0.09923；0.1 → 0.10078；0.2 → 0.10096（最优）；0.3 → 0.10075（收益递减）",
        "任何掩码都优于不掩码；掩码同时提供额外的行为预测信号与正则",
        "联合训练优于「先召回再微调排序」：后者因冻结 item embedder 无法为排序调整表示",
        "只训排序的变体（w/o item loss）不如联合训练 → 召回目标反过来提升了排序质量",
    ]},
    "limitations": ["线上收益叠加在已有下游排序器之上，被稀释",
                    "fp8 为满足 Transformer Engine 形状约束需攒 batch，QPS 高但延迟变差，线上仍用 bf16",
                    "仅在 Pinterest 两个流量场景验证"],
    "reproducibility": {"code_release": "论文未见公开代码（工业界工作，未给仓库地址）", "code_status": "not_released"},
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2606.00422_unipinrec_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary ok")

TITLE = "召回+排序合成一个模型，延迟降11%"
assert len(TITLE) <= 20, len(TITLE)

BODY = """🎓 一句话：召回要给上百万候选快速打分，排序只对几百个候选做更贵的交叉计算——算法形态不同，但两边编码的是同一份用户行为历史。Pinterest 把它们合进一个模型（输入、训练、服务一起统一，此前只统过主干）：线上互动 +1%，延迟 −11.1%，QPS +63.6%。

✨ 三个改动（看图 1）
① 动作编成 multi-hot 拼到特征维、不插 token（长度与召回一致）；历史动作 20% 随机 mask、候选恒 mask，用每类动作一个 MLP 头做 BCE。
② 每条样本 = 过去行为序列 + 未来一次请求的完整曝光 slate（未交互曝光保 10%）：召回的正样本、排序的负样本一次都有了。
③ 历史的 O(n²) 自注意力只在召回侧 prefill 一次，KV 经 CUDA IPC 给排序复用（只做 O(n·k) decode）；Faiss 一次调用同时返回候选 ID 与 item 嵌入。

📊 结果
• 离线：排序 Hit@3 0.10096，比生产排序模型 TransActV2+DCNv2（0.08801）高 14.7%，也高于等长 HSTU（0.09733）；召回 Recall@10 0.7766 与 PinRec 持平。
• 消融：只训排序 0.09735 已超 HSTU 与生产排序模型，加回召回目标到 0.10096；先训召回再微调仅 0.09587（embedder 须冻结）。
• 效率：KV 复用让排序从 prefill 变 decode，单次前向 ≈2.4×，叠 flex attention+fp8 最高 3.92×（线上实际用 bf16）。

⚠️ 局限
① 线上只替换召回 + 粗排，下游原精排未动，离线 14.7% 的优势落到线上只剩约 1% 互动提升；
② fp8 把 QPS 推到 +109.1%，但量化使离线指标掉 0.5%、延迟反而 +6.7%，线上仍用 bf16；
③ 只在 Pinterest 两个场景验证，未开源。

📄 论文：https://arxiv.org/abs/2606.00422
💻 相关开源：github.com/pinterest/transformer_user_action、github.com/meta-recsys/generative-recommenders
✨ 关注我，持续拆解推荐系统论文 📚"""
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
    paper_id="2606.00422",
    platform="xhs",
    canonical_url=PAPER_URL,
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": PAPER_URL, "pdf": "https://arxiv.org/pdf/2606.00422", "code": ""},
    metadata={
        "topics": ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"],
        "pdf_path": str(PARSED / "2606.00422_origin.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文，仅作学术解读。",
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
