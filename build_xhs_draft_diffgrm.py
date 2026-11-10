# -*- coding: utf-8 -*-
"""
build_xhs_draft_diffgrm.py
==========================
DiffGRM（arXiv 2510.21805，WWW 2026 / pp.5853-5864）小红书草稿。

图源：arXiv e-print 源包 Figures/*.pdf 共 6 张矢量图，3x 渲染（framework 2827px / sup 2654px）
+ 1 张自制数字卡（主结果 + 消融，论文表格在手机上不可读）。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2510.21805"
IMAGES = PARSED / "images"
PAPER_URL = "https://arxiv.org/abs/2510.21805"
CODE_URL = "https://github.com/liuzhao09/DiffGRM"


def font(size: int, bold: bool = False):
    cands = ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"] if bold else ["C:/Windows/Fonts/msyh.ttc"]
    for c in cands:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_numbers_card(out: Path) -> Path:
    W = 1840
    BLUE = (30, 78, 156)
    DARK, GREY, ACCENT = (28, 32, 40), (116, 124, 136), (188, 68, 34)
    img = Image.new("RGB", (W, 1310), (250, 251, 253))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=BLUE)
    d.text((70, 56), "换掉一行生成方式，代价与收益", font=font(56, True), fill=DARK)
    d.text((70, 142), "Amazon Reviews 三个类目 · 对比对象为各表最强基线 · 数据来源：论文 Table 2 / Table 3",
           font=font(26), fill=GREY)

    f_sec = font(31, True)
    f_name = font(33, True)
    f_val = font(44, True)
    f_pct = font(34, True)

    # ---- 区块 A：主结果 ----
    d.text((70, 216), "① NDCG@10（越大越好）", font=f_sec, fill=BLUE)
    blocks = [("Sports", "0.0305", "+15.5%"), ("Beauty", "0.0502", "+8.2%"), ("Toys", "0.0524", "+6.9%")]
    bw, gap = 520, 40
    top = 268
    for i, (name, val, pct) in enumerate(blocks):
        x = 70 + i * (bw + gap)
        d.rounded_rectangle([x, top, x + bw, top + 210], radius=18, fill=(255, 255, 255), outline=(224, 229, 238), width=3)
        d.text((x + 36, top + 26), name, font=font(30, True), fill=GREY)
        d.text((x + 36, top + 74), val, font=font(72, True), fill=DARK)
        d.text((x + 36, top + 158), pct, font=font(38, True), fill=ACCENT)

    # ---- 区块 B：消融 ----
    d.text((70, 522), "② 消融：换掉一个零件，Sports 上 NDCG@10 怎么变", font=f_sec, fill=BLUE)
    rows = [
        ("完整 DiffGRM", "0.0305", "", False),
        ("PSE → RQ-Kmeans（换回残差分词）", "0.0200", "−34.4%", True),
        ("PSE → 随机码字", "0.0138", "−54.8%", True),
        ("去掉 OCN（改回随机掩码）", "0.0250", "−18.0%", True),
        ("去掉 on-policy（保留相干加噪）", "0.0263", "−13.8%", True),
        ("去掉 CPD（改回固定顺序）", "0.0273", "−10.5%", True),
    ]
    rh, y = 92, 586
    x0, x1 = 70, W - 70
    for i, (name, val, pct, is_drop) in enumerate(rows):
        d.rectangle([x0, y, x1, y + rh], fill=(233, 240, 252) if not is_drop else ((255, 255, 255) if i % 2 == 0 else (245, 247, 250)))
        d.line([x0, y, x1, y], fill=(226, 230, 238), width=2)
        d.text((x0 + 28, y + 26), name, font=f_name, fill=DARK)
        d.text((x1 - 400, y + 22), val, font=f_val, fill=DARK)
        d.text((x1 - 235, y + 30), pct, font=f_pct, fill=ACCENT)
        y += rh
    d.line([x0, y, x1, y], fill=(198, 205, 215), width=3)

    d.text((70, y + 34), "12 个指标里 11 个第一；唯一输的是 Toys 的 Recall@10（0.0834 vs RPG 0.0869，−4.03%）",
           font=font(28, True), fill=BLUE)
    d.text((70, y + 86), "分词换错跌得最狠：说明并行生成的前提是「4 位解耦」，不是把解码器一换就完事",
           font=font(26), fill=GREY)
    img.save(out, optimize=True)
    return out


print("numbers card:", draw_numbers_card(IMAGES / "fig_card_numbers.png"))

FIG_ORDER = [
    "intro.png",            # 封面：ARM 错一位 → 全盘跑偏；Ours 先补高置信位再回改难位
    "framework.png",        # 总架构：编码器 + MD-Decoder；(a) OCN 训练 (b) CPD 推理
    "sup.png",              # ARM vs MDM 的注意力与监督信号对比
    "fig_card_numbers.png",  # 自制数字卡
    "exp.png",              # 样本效率：ESP vs NDCG/Recall
    "beam.png",             # CPD beam size
]

figure_meta = {
    "intro.png": ("motivation",
        "论文图 1（动机，封面）：(a) 一个物品由 n 位 SID 共同定义（Dior Rouge 999 Velvet 拆成品类/品牌/类型/尺码），四位之间是双向的组内一致性，而各位的语义粒度与可预测性不同（数字间异质性）。(b) 上排 ARM：Ball<233> 猜对后，难位品牌只依据前缀 <233> 被误判成 <131>（应为 <134>），因果约束不许回看后面的数字，错误继续传到 <55>、<88>，最终生成一个毫不相干的球。(b) 下排 Ours：先填置信度高的第三位 <56>，再带着 <233>+<56> 回改难位到 <134>，最后补完 <90>，得到正确的 Spalding 篮球。"),
    "framework.png": ("architecture",
        "论文图 2（总架构）：左侧编码器把用户历史的 SID 序列编码成 H_u；(a) 训练侧 MD-Decoder 用非因果自注意力 + 对 H_u 的 cross-attention，由 OCN 决定掩哪些位——先全掩码探测得到每位置信度/难度，按难度从高到低构造嵌套视图（掩 1→2→…→n 位），把加噪预算压在难位上；(b) 推理侧 CPD 从 t_R=1 全掩码起步逐级反解到 t_1=0，每一步在（位, 码字）联合空间里选置信度最高的填上，其余保持 MASK，可并行出多个 Top-K 候选。"),
    "sup.png": ("mechanism",
        "论文附录图（ARM 与 MDM 的对照）：左半是 ARM——因果自注意力，每个位置只在前缀下受监督，黄色格是被预测的目标、橙色格是它拿到的监督信号，能看到监督被压成一条从左到右的对角路径；右半是 MDM——非因果自注意力，配合不同的掩码视图，黄色目标可以拿到多组上下文的监督，监督信号在矩阵上铺开。这张图直观解释了「每样本 n 条 vs n·2^(n−1) 条」的差别。"),
    "fig_card_numbers.png": ("custom_card",
        "自制数字卡（标注为自制）：把论文 Table 2（主结果 NDCG@10 与相对最强基线提升）与 Table 3（消融，Sports）重排成手机可读版——完整模型 0.0305，换回 RQ-Kmeans 分词跌到 0.0200，随机码字 0.0138，去 OCN 0.0250，去 on-policy 0.0263，去 CPD 0.0273。"),
    "exp.png": ("result",
        "论文图 3（样本效率）：横轴是有效样本轮次 ESP = best_epoch × 每样本每 epoch 视图数（相干加噪 k 倍则视图为 n×k），纵轴为 NDCG@10（上排）与 Recall@10（下排）。星号是 DiffGRM，圆点是 k=1…10 倍相干加噪的基线，虚线是对这些点的对数拟合。三个数据集上星号都落在拟合曲线左上方——用更少的 ESP 拿到同等或更好的效果。"),
    "beam.png": ("result",
        "论文图 4（CPD 的 beam size）：beam 从 32 增到 256，三个数据集的 NDCG@10 都单调上升，Beauty/Toys 在 128→256 后趋于饱和，Sports 在 64 之后基本走平。说明并行去噪同样吃 beam 的收益，但边际递减。"),
}
(PARSED / "diffgrm_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2510.21805v2 e-print 源包 Figures/*.pdf（矢量，3x 渲染：framework 2827×1243、sup 2654×915、exp 2469×1112、dim 1735×628、beam 1622×525、intro 1275×784）+ 1 张自制数字卡。",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

summary = {
    "paper_id": "2510.21805",
    "title_zh": "把逐位生成换成并行补全",
    "title_en": "DiffGRM: Diffusion-based Generative Recommendation Model",
    "venue": "The ACM Web Conference 2026 (WWW '26), pp. 5853-5864, DOI 10.1145/3774904.3792156；arXiv v1 2025-10-21 / v2 2026-08-13 (camera-ready)",
    "one_liner": "生成式推荐把每个物品编成 n 位语义 ID 再逐位生成；DiffGRM 用掩码离散扩散（MDM）替掉自回归解码器，让 n 位数字在双向上下文下任意顺序并行生成，并配套 PSE（解耦分词）/ OCN（难度优先相干加噪）/ CPD（置信度引导并行去噪）三处改造，NDCG@10 相对最强基线提升 6.9%~15.5%。",
    "problem_definition": {
        "task_type": "语义 ID 生成式推荐（next-item，SID 为 4 位、每位码本 256）",
        "challenges": [
            "组内一致性：n 位数字共同定义同一物品，但因果注意力只允许前缀上下文，双向互证被阻断，监督塌缩为单条因果路径",
            "数字间异质性：各位语义粒度与可预测性不同（品类/品牌/类型/尺码），next-token 目标对各位置等权，简单位过训、困难位欠训",
            "掩码扩散的监督组合爆炸：n 层码本有 n·2^(n-1) 条目标-上下文信号，全覆盖至少需 2^n − 1 种掩码配置（n=4 时 32 条 / 15 种）",
        ],
    },
    "main_contributions": [
        {"point": "首个用掩码离散扩散替换自回归解码器的生成式推荐框架，去掉从左到右约束。"},
        {"point": "PSE 分词：OPQ 式正交旋转 + 均分 n 段 + 逐位码本最近质心，去除残差式顺序依赖，使并行预测成立。"},
        {"point": "OCN 训练：全掩码探测得每位难度 δ=1−p_max，按难度降序构造嵌套掩码视图，把加噪预算集中到难位。"},
        {"point": "CPD 推理：全局并行 beam search，在（位, 码字）联合空间按置信度逐步填充，产出多样 Top-K。"},
    ],
    "datasets": [{"name": "Amazon Reviews 2014：Sports（35,598 用户 / 18,357 物品）、Beauty（22,363 / 12,101）、Toys（19,412 / 11,924）"}],
    "baselines": ["GRU4Rec", "HGN", "SASRec", "BERT4Rec", "FDSA", "S3-Rec", "VQ-Rec", "RecJPQ", "TIGER", "HSTU", "ActionPiece", "RPG"],
    "metrics": ["Recall@5", "Recall@10", "NDCG@5", "NDCG@10", "ESP（有效样本轮次）"],
    "main_results": {
        "ndcg10": "Sports 0.0305（+15.53%）、Beauty 0.0502（+8.19%）、Toys 0.0524（+6.94%），相对各表最强基线",
        "recall10": "Sports 0.0550（+10.00%）、Beauty 0.0876（+8.28%）、Toys 0.0834（−4.03% vs RPG 0.0869）",
        "coverage": "12 个指标中 11 个第一",
        "efficiency": "同等或更低 ESP 下追平 k 倍相干路径加噪；训练复杂度与 ARM 同级（编码器主导），推理解码器多一个 n 倍因子",
        "encoder_ablation": "sentence-t5-base 0.0305/0.0502/0.0524；bge-large-en 0.0327/0.0564/0.0508；gte-large-en 0.0342/0.0549/0.0510",
    },
    "ablation": {"conclusions": [
        "PSE→RQ-Kmeans：0.0305→0.0200 / 0.0502→0.0343 / 0.0524→0.0305（残差层级与并行去噪冲突）",
        "PSE→随机码字：0.0305→0.0138 / 0.0502→0.0300 / 0.0524→0.0206",
        "w/o OCN（改回随机掩码）：0.0305→0.0250 / 0.0502→0.0368 / 0.0524→0.0385",
        "w/o on-policy（保留相干加噪）：0.0305→0.0263 / 0.0502→0.0455 / 0.0524→0.0430",
        "w/o CPD（固定随机顺序）：0.0305→0.0273 / 0.0502→0.0496 / 0.0524→0.0499",
        "OCN 变体：least+static 最优，most+refresh 最差（Beauty −19.11%、Toys −24.47%），说明按难度选位与静态顺序都重要",
    ]},
    "limitations": [
        "Toys 的 Recall@10 低于 RPG 4.03%（NDCG@5/@10 仍更高）",
        "d_m 需按数据集调（Sports/Beauty 256、Toys 1024，1024 在 Toys 上才不 OOM）",
        "换更强语义编码器在 Sports/Beauty 涨、Toys 反降 0.0508/0.0510 vs 0.0524",
        "只在三个 Amazon 类目验证，无工业级线上数据",
    ],
    "reproducibility": {"code_release": "https://github.com/liuzhao09/DiffGRM（官方 PyTorch 实现，含 AR_GRM/DIFF_GRM 两套配置与复现命令，CC BY-NC 4.0）", "code_status": "released"},
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2510.21805_diffgrm_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary ok")

TITLE = "DiffGRM：把逐位生成换成并行补全"
assert len(TITLE) <= 20, len(TITLE)

BODY = """🎓 一句话：生成式推荐把物品编成 4 位语义 ID 再逐位写；DiffGRM 改成"掩码扩散、任意顺序并行补全"，NDCG@10 比最强基线高 6.9%~15.5%（WWW 2026）。

🧠 自回归的两个毛病
组内一致性：4 位共同指向一个物品（品类/品牌/类型/尺码），但因果注意力只看得见前缀。图 1 里品牌位该是 <134>，模型只凭 <233> 猜成 <131>，后两位顺着错下去，生成一个毫不相干的球。
数字间异质性：品牌位远比尺码位难，损失却给每位同样权重——简单的过训、难的欠训。

✨ 三处改造
🔤 PSE 分词：先学一个正交旋转矩阵把物品向量转一下（降量化失真），再均分成 4 段，各段在 256 码本里找最近质心。关键是没残差依赖——RQ 后一位依赖前一位，4 位解耦才能并行。
🎯 OCN 训练：先做一次全掩码探测，用 1−最大概率给每位打难度分，再按难度从高到低做一组嵌套掩码，把加噪预算压在难位上。这步必需：4 位码本下自回归只有 4 条监督信号、一条样本够用，掩码扩散有 4×2³=32 条，全覆盖要 15 种配置，硬枚举不现实。
⚡ CPD 推理：从全掩码起步，每步在（位置, 码字）里挑置信度最高的一对填上，其余继续掩着；beam 32~256 就能产出多样 Top-K。

📊 数字（Amazon 三件套，vs 最强基线）
NDCG@10：0.0305（+15.5%）、0.0502（+8.2%）、0.0524（+6.9%），12 个指标 11 个第一；同等 ESP 追平 k 倍相干加噪。
消融最狠的是分词：PSE 换回 RQ-Kmeans，Sports 从 0.0305 掉到 0.0200；换随机码字只剩 0.0138；去 OCN 0.0250，去 CPD 0.0273。跌得最狠说明前提是"4 位解耦"，不是换解码器就行。

⚠️ 局限
Toys 的 Recall@10 比 RPG 低 4.03%（NDCG 仍更高）；隐藏维按数据集调（Sports/Beauty 256、Toys 1024）；换更强编码器，Sports/Beauty 涨、Toys 反降。

📄 https://arxiv.org/abs/2510.21805
💻 https://github.com/liuzhao09/DiffGRM
✨ 关注我，持续拆解推荐系统论文 📚"""
print("title (%d): %s" % (len(TITLE), TITLE))
print("body (%d)" % len(BODY))
assert len(BODY) <= 1000, "body too long: %d" % len(BODY)

missing = [p for p in FIG_ORDER if not (IMAGES / p).exists()]
assert not missing, "缺图: %s" % missing
for p in FIG_ORDER:
    im = Image.open(IMAGES / p)
    print("   %-26s %sx%s  %dKB" % (p, im.size[0], im.size[1], (IMAGES / p).stat().st_size // 1024))

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2510.21805",
    platform="xhs",
    canonical_url=PAPER_URL,
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": PAPER_URL, "pdf": "https://arxiv.org/pdf/2510.21805", "code": CODE_URL},
    metadata={
        "topics": ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"],
        "visual_review": "ViewImage 逐张目检 6 张（含自制数字卡溢出复核）",
        "pdf_path": str(PARSED / "2510.21805_origin.pdf"),
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
