# -*- coding: utf-8 -*-
"""
build_xhs_draft_sage.py
=======================
SAGE（arXiv 2601.21452，RecSys 2026 / 小红书）小红书草稿。

图源：arXiv e-print 源包内 5 张 PNG 原图（PDF 内嵌的就是这几张，1024px 是分辨率天花板）
+ 1 张自制数字卡（论文三张表都在正文里，手机上不可读，重排成大字号）。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2601.21452"
IMAGES = PARSED / "images"
PAPER_URL = "https://arxiv.org/abs/2601.21452"


def font(size: int, bold: bool = False):
    cands = ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"] if bold else ["C:/Windows/Fonts/msyh.ttc"]
    for c in cands:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def upscale(src: Path, dst: Path, factor: float = 1.8) -> Path:
    """1024px 的原图放大一档 + 轻锐化，手机全宽显示时文字边缘更顺。"""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im = im.resize((int(w * factor), int(h * factor)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=3))
    im.save(dst, optimize=True)
    return dst


def draw_numbers_card(out: Path) -> Path:
    W = 1840
    BLUE = (36, 88, 168)
    DARK, GREY, ACCENT = (30, 34, 42), (118, 126, 138), (196, 74, 36)
    rows = [
        ("冷启动召回@10", [("0.326 → 0.619", "+89.9%"), ("0.282 → 0.567", "+101%"), ("0.365 → 0.705", "+93.2%")]),
        ("多样性 Entropy@10", [("2.285 → 2.551", "+11.6%"), ("2.274 → 2.528", "+11.2%"), ("2.315 → 2.574", "+11.2%")]),
        ("精度 NDCG@10", [("0.0550 → 0.0557", "+1.3%"), ("0.0317 → 0.0320", "+1.0%"), ("0.0581 → 0.0585", "+0.7%")]),
    ]
    top = 236
    rh = 168
    H = top + 76 + rh * len(rows) + 250
    img = Image.new("RGB", (W, H), (250, 251, 253))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=BLUE)
    d.text((70, 58), "同一个骨架，只换优化器：三组数字", font=font(56, True), fill=DARK)
    d.text((70, 144), "Amazon 三个类目 · 对比基线 OneRec-GBPO · 数据来源：论文 Table 1 / Table 2",
           font=font(27), fill=GREY)

    x_lab = 70
    col_x = [560, 990, 1420]
    x1 = W - 70
    f_head = font(29, True)
    f_lab = font(33, True)
    f_val = font(32)
    f_pct = font(40, True)

    d.rounded_rectangle([x_lab, top, x1, top + 76], radius=12, fill=(232, 238, 248))
    d.text((x_lab + 26, top + 23), "指标（GBPO → SAGE）", font=f_head, fill=BLUE)
    for cx, name in zip(col_x, ["Beauty", "Sports", "Toys"]):
        d.text((cx, top + 23), name, font=f_head, fill=BLUE)

    y = top + 76
    for i, (label, cells) in enumerate(rows):
        d.rectangle([x_lab, y, x1, y + rh], fill=(255, 255, 255) if i % 2 == 0 else (245, 247, 250))
        d.line([x_lab, y, x1, y], fill=(226, 230, 238), width=2)
        d.text((x_lab + 26, y + 36), label, font=f_lab, fill=DARK)
        d.text((x_lab + 26, y + 88), "越高越好" if i < 2 else "持平微升", font=font(24), fill=GREY)
        for cx, (v, pct) in zip(col_x, cells):
            d.text((cx, y + 28), v, font=f_val, fill=(64, 70, 80))
            d.text((cx, y + 80), pct, font=f_pct, fill=ACCENT)
        y += rh
    d.line([x_lab, y, x1, y], fill=(200, 206, 216), width=3)

    d.text((70, y + 40), "换成原生文本动作空间（TextRec）后精度再上一层：NDCG@10 比 GBPO 高 6.3%~7.8%",
           font=font(29, True), fill=BLUE)
    d.text((70, y + 96), "消融最能说明分工：去掉 Boost → 冷启动召回剩 0.50；去掉熵惩罚 → 多样性剩 0.78；",
           font=font(27), fill=GREY)
    d.text((70, y + 146), "去掉解耦 → NDCG 剩 0.90（Amazon-Beauty，数值已归一化到完整 SAGE）",
           font=font(27), fill=GREY)
    img.save(out, optimize=True)
    return out


for src, dst in [("gradient1.png", "fig_gradient_1p8x.png"), ("Evolution2.png", "fig_evolution_1p8x.png")]:
    print("upscale:", upscale(IMAGES / src, IMAGES / dst))
print("numbers card:", draw_numbers_card(IMAGES / "fig_card_numbers.png"))

FIG_ORDER = [
    "paper-all-pic.png",       # 封面：用户画像 → 行为 → prompt → 生成列表（论文原图）
    "paper-sft-sage.png",      # 架构：特征工程 → SFT → RLHF(SAGE) → 列表
    "fig_gradient_1p8x.png",   # 机制核心：GBPO 平线 vs SAGE 非对称边界
    "fig_evolution_1p8x.png",  # 训练动态：冷启概率 / 列表熵 双面板
    "fig_card_numbers.png",    # 自制数字卡
    "ablationstudy4.png",      # 消融：三个零件各管一件事
]

figure_meta = {
    "paper-all-pic.png": ("motivation",
        "论文图 1（动机示意）：一条 prompt 的构成。上半部分把用户画像（骑行/旅行/健身/时尚等兴趣簇）与近期行为（近 7 天与近 1 年的品类次数）拼成自然语言描述；中间是最终拼出的 prompt 段落；下半部分是模型按这条 prompt 生成的 10 个真实笔记缩略图，呈现明显的主题一致性与多样性。"),
    "paper-sft-sage.png": ("architecture",
        "论文图 2（建模总览，两阶段）：Input → Feature Engineering（用户画像与历史行为构造 / prompt 构造 / 物品侧描述特征构造）→ Stage 1 Supervised Fine-tuning（LLM，Qwen3-8B 做 SFT 热启动）→ Stage 2 RLHF（SAGE 替换掉原有的 GBPO 优化器）→ 输出长度为 L=10 的推荐列表。全图的关键在于 Stage 2 只换优化器，模型与 SFT→RLHF 的接口都不动。"),
    "fig_gradient_1p8x.png": ("mechanism",
        "论文图 3（梯度边界对比，SAGE 的核心机制）：横轴是 slate 级重要性比率 r，纵轴是有效梯度系数 r/Φ。红色虚线 GBPO 在 r>1 处被硬截到 1.0（对称保守）；深蓝实线 SAGE 在 r>1 处继续上抬到 1+ε_boost——这是 Case A，正样本可以超线性更新（冷启动 Boost）；在 r<1 一侧，SAGE 给低多样性负样本（浅蓝）比高多样性负样本（深蓝）更低的系数——这是 Case B，熵越低惩罚越重。"),
    "fig_evolution_1p8x.png": ("result",
        "论文图 4（训练动态演化）：(a) 冷启动物品的平均生成概率——GBPO 一万步后仍停在 0.05 附近，SAGE 升到约 0.18；(b) 平均列表熵——GBPO 从 3.8 一路掉到 2.5（多样性塌缩），SAGE 稳定在 3.7 附近。两个面板分别对应 Positive Boost 与 Entropy-Aware Penalty 的作用。"),
    "fig_card_numbers.png": ("custom_card",
        "自制数字卡（标注为自制）：把论文 Table 1 / Table 2 里「同骨架只换优化器（OneRec-GBPO → OneRec-SAGE）」的三组指标重排成手机可读版——冷启动召回@10、多样性 Entropy@10、NDCG@10 在 Beauty/Sports/Toys 上的变化，并附 TextRec（原生文本空间）的精度增益与消融结论。"),
    "ablationstudy4.png": ("result",
        "论文图 5（Amazon-Beauty 消融，数值归一化到完整 SAGE）：去掉 Positive Boost 后冷启动召回掉到 0.50（近腰斩）而多样性与精度基本不变；去掉 Entropy Penalty 后多样性掉到 0.78；去掉 Signal Decoupling 后 NDCG 掉到 0.90。三个组件各自只负责一个目标，互不替代。"),
}
(PARSED / "sage_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2601.21452v3 e-print 源包内 5 张 PNG（PDF 内嵌为同一批文件，1024px 为源分辨率）；fig_gradient_1p8x / fig_evolution_1p8x 为 1.8x LANCZOS 放大 + 轻锐化；fig_card_numbers 为自制。",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

summary = {
    "paper_id": "2601.21452",
    "title_zh": "只换优化器，冷启动召回翻倍",
    "title_en": "SAGE: Sequence-level Adaptive Gradient Evolution for Generative Recommendation",
    "venue": "arXiv 2601.21452v3（2026-01-29 首版）；作者来自小红书",
    "one_liner": "生成式推荐在 SFT 之后的 RLHF 阶段，GBPO 的截断是逐样本、对称、与推荐信号无关的；SAGE 保留模型结构与 SFT→RLHF 接口，只替换优化器——slate 级几何平均比率、按优势符号与列表熵条件化的非对称边界、先解耦再聚合的多目标优势——冷启动召回 +89.9%~+101%，多样性 +11%，精度不降。",
    "problem_definition": {
        "task_type": "生成式推荐的 RLHF 偏好对齐（list-wise slate 生成，L=10）",
        "challenges": [
            "Symmetric Conservatism：GBPO 对称保守的上界压制稀有正样本（冷启动）的学习信号，线上冷启动曝光 -44.7%",
            "静态负向约束无法阻止拒识主导反馈下的多样性塌缩，簇密度 +11.7%",
            "group 归一化的多目标奖励被压成同一优势值，训练信号分辨率低（reward collapse）",
        ],
    },
    "main_contributions": [
        {"point": "Sequence-level 重要性比率：token 级比率改为整条 slate 的几何平均（L=10），降低 token 级方差。"},
        {"point": "非对称自适应边界：A≥0 时上界抬到 1+ε_boost（ε=0.3）做 Positive Boost；A<0 时用 λ=1+β·tanh(max(0,H̄−H)) 按列表熵加重惩罚（β=0.5）。"},
        {"point": "先解耦再聚合的优势估计：每个目标在采样组内独立 z-score 后加权求和，再整批 z-score，保留多目标分辨率。"},
    ],
    "datasets": [{"name": "Amazon Product Reviews（Beauty / Sports / Toys）"},
                 {"name": "RecIF-Bench（约 120M 交互、200K 用户，短视频/广告/商品/交互/标签条件/标签预测六个任务）"}],
    "baselines": ["SASRec", "ReaRec", "TIGER", "LC-Rec", "OneRec-GRPO", "OneRec-GBPO", "Only SFT (TextRec)"],
    "metrics": ["R@5/R@10", "N@5/N@10", "Entropy@10（二级类目）", "Cold-Recall@10（训练集频次最低 5%）",
                "RecIF-Bench：Pass@1/Pass@32/Recall@32/AUC"],
    "main_results": {
        "cold_start": "Beauty 0.326→0.619 (+89.9%)、Sports 0.282→0.567 (+101%)、Toys 0.365→0.705 (+93.2%)（vs OneRec-GBPO）",
        "diversity": "Entropy@10 Beauty 2.285→2.551 (+11.64%)、Sports 2.274→2.528 (+11.17%)、Toys 2.315→2.574 (+11.19%)",
        "accuracy_semantic_id": "OneRec-SAGE 相对 OneRec-GBPO 微弱上升（N@10 +0.69%~+1.27%），论文自述为 competitive but mixed",
        "accuracy_native_text": "TextRec（原生文本 + SAGE）NDCG 比 OneRec-GBPO 高 6.27%~7.8%，R@10 +4.35%~+6.26%",
        "recif_bench": "TextRec 在六个任务上普遍优于 OneRec-GBPO（如 Interactive Rec Pass@1 0.1310 vs 0.1256）；OneRec-SAGE 在 Entropy@10/Cold-Recall@10 上绝对值最高（4.455 / 0.637）",
    },
    "ablation": {"conclusions": [
        "去掉 Positive Boost：Cold-Recall@10 归一化 0.50（近腰斩），Entropy 1.01、NDCG 0.97 基本不变",
        "去掉 Entropy Penalty：Entropy@10 降到 0.78，Cold 0.92、NDCG 1.01",
        "去掉 Signal Decoupling（改回加权求和）：NDCG@10 降到 0.90，Entropy 0.94、Cold 0.93",
        "三个组件各自负责一个目标，缺一不可，但作用面互不重叠",
    ]},
    "limitations": [
        "冷启动口径为训练集交互频次最低 5%，多样性用二级类目熵，换数据集需重调口径",
        "语义 ID 动作空间下强探索会过激，精度只持平；原生文本空间才拿到最好精度，说明结论依赖动作空间",
        "原生文本方案需先把商品渲染成语言，对延迟敏感系统不友好（作者列为主要限制）",
        "arXiv 备注存在与 2506.19235 的文本重叠提示；无公开代码",
    ],
    "reproducibility": {"code_release": "论文全文未见 GitHub 链接或开源声明", "code_status": "not_released"},
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2601.21452_sage_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary ok")

TITLE = "SAGE：只换优化器，冷启动召回翻倍"
assert len(TITLE) <= 20, len(TITLE)

BODY = """🎓 模型和 SFT→RLHF 流程都不动，只把 RLHF 里那个"截断式更新"的优化器换掉，冷启动召回 0.326→0.619。

🧠 原来的优化器哪里"瞎"
生成式推荐先给视频编语义 ID，再让模型自回归吐 10 个候选，SFT 后过一遍 RLHF。OneRec-V2 的 GBPO 用梯度边界稳住了训练，但它的截断逐样本、对称、跟推荐信号无关：
· 新视频的稀有正样本也被压在 r≤1 里，线上冷启动曝光 -44.7%。
· 拒识占多数，静态负向边界拦不住多样性塌缩，簇密度 +11.7%。
· 多目标奖励各自归一化再加和，点击和评论压成同一个优势值。

✨ 只改三处（图 2 链路，图 3 核心）
① 比率：逐 token 换成整条列表的几何平均（L=10），一个列表一个更新幅度。
② 边界不对称：优势 ≥0 上界抬到 1+ε（ε=0.3）可超线性涨；优势 <0 按列表熵压边界，熵比历史均值越低惩罚越重（β=0.5）。
③ 优势先解耦再聚合：每个目标组内归一化、加权求和，再整批 z-score。

📊 数字（Amazon 三件套，vs GBPO）
· 冷启动召回@10：0.326→0.619、0.282→0.567、0.365→0.705（+89.9%/+101%/+93.2%）
· 多样性 Entropy@10：+11.2%~+11.6%
· 精度没掉：NDCG@10 +0.7%~+1.3%
原生文本空间（TextRec）更进一步：NDCG 比 GBPO 高 6.3%~7.8%。
消融最直白：去掉 Boost 冷启动召回剩 0.50、去掉熵惩罚多样性剩 0.78、去掉解耦 NDCG 剩 0.90——各管一件事。

💡 两点
"让 RLHF 稳定"和"让 RLHF 适合推荐"是两件事：GBPO 解决前者，SAGE 说病根在截断本身——逐样本、对称、看不见推荐特有的信号。
同一个优化器放进语义 ID 空间，探索过激、精度只持平；放进原生文本空间才最好——动作空间是隐藏变量。

⚠️ 局限
冷启动取训练集频次最低 5%、熵按二级类目算，换数据集要重调口径；原生文本要先渲染商品，对延迟敏感的系统不友好。

📄 https://arxiv.org/abs/2601.21452
✨ 做生成式推荐后训练的话，成本最低的一次实验：只把逐样本截断换成按优势符号分区截断，其他都不动。"""
print("title (%d): %s" % (len(TITLE), TITLE))
print("body (%d)" % len(BODY))
assert len(BODY) <= 1000, "body too long: %d" % len(BODY)

missing = [p for p in FIG_ORDER if not (IMAGES / p).exists()]
assert not missing, "缺图: %s" % missing
for p in FIG_ORDER:
    im = Image.open(IMAGES / p)
    print("   %-30s %sx%s  %dKB" % (p, im.size[0], im.size[1], (IMAGES / p).stat().st_size // 1024))

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2601.21452",
    platform="xhs",
    canonical_url=PAPER_URL,
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": PAPER_URL, "pdf": "https://arxiv.org/pdf/2601.21452", "code": ""},
    metadata={
        "topics": ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"],
        "pdf_path": str(PARSED / "2601.21452_origin.pdf"),
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
