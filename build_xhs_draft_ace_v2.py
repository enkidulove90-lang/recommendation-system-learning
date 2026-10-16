# -*- coding: utf-8 -*-
"""
build_xhs_draft_ace_v2.py
=========================
ACE 草稿 v2 —— 修复用户反馈的三个问题：
  1) 「没有算法架构图」→ 论文/官方仓库都没有架构图，按 §3 方法**自绘高清架构图**（含 SVD 谱收缩机制）；
  2) 「图片质量不高」→ 自绘图为 1800×1000 高清；原论文 620px 小图改为**合成对比大图**并适度重采样；
  3) 「文本看不出在干什么」→ 正文重写：把 pipeline 逐步讲清（并配图 1 引用）；同时修正 v1 的事实错误
     （代码是公开的：github.com/DCheol/ACE）。

方法细节（据 sec-model.tex，确保画得准）：
  B̂ = (E Eᵀ + λI)⁻¹ E Eᵀ                                # LAE 闭式解，重建 + L2 正则
  E = U S Vᵀ ;  E_ACE = U · g_λ(S),  g_λ(σ)=√(σ²/(σ²+λ))  # 幅度相关的谱收缩，压掉主导奇异方向
  之后 γ 缩放标准差，再作为 SASRec/BERT4Rec 的物品初始 embedding 正常训练。

流程：stage → publish → 成功后删除 v1 旧稿
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2605.29322"
SRC = PARSED / "source" / "Figures"
IMAGES = PARSED / "images"
IMAGES.mkdir(parents=True, exist_ok=True)
OLD_DRAFT_ID = "s:30bada62-b887-46ee-abff-4fa8cce2d817"   # v1（缺架构图/图质低），新稿成功后删

FONT = r"C:/Windows/Fonts/msyh.ttc"
FONT_B = r"C:/Windows/Fonts/msyhbd.ttc"


def font(size, bold=False):
    for p in ((FONT_B, FONT) if bold else (FONT,)):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for ch in text:
        if d.textbbox((0, 0), cur + ch, font=f)[2] > maxw:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


# ============================================================
# 图 1：自绘架构图（1800×1000）
# ============================================================
def draw_architecture(out: Path):
    W, H = 2000, 1180
    img = Image.new("RGB", (W, H), (250, 251, 253))
    d = ImageDraw.Draw(img)

    BLUE, ORANGE, GREEN, GREY = (36, 88, 168), (214, 108, 32), (28, 130, 96), (110, 116, 126)
    d.rectangle([0, 0, W, 14], fill=BLUE)

    f_title, f_box, f_body, f_note = font(50, True), font(30, True), font(22), font(22)

    d.text((60, 46), "ACE：先把 LLM 给的物品向量「掰开」，再喂给推荐模型", font=f_title, fill=(28, 32, 40))
    d.text((60, 118), "LLM-as-Extractor 范式：物品文本 → LLM 编码 → 物品向量 → 序列推荐模型（ACE 只改中间那一步）",
           font=f_note, fill=(96, 104, 116))

    # 5 个模块（手工控制每行文字，避免自动换行溢出）
    boxes = [
        (60, "① 物品文本", ["标题 / 类目 / 品牌", "（Amazon 等数据集）"], GREY),
        (440, "② LLM 编码器", ["text-embedding-3-large", "另测 F2LLM-4B /", "Qwen3-8B /", "KaLM-12B"], GREY),
        (820, "③ 原始向量 E", ["强各向异性：向量", "几乎都指向同一个", "方向，谱严重不均"], ORANGE),
        (1200, "④ ACE：线性自编码器", ["重建损失保住语义 +", "L2 正则控制分散度", "（λ 是「掰多开」旋钮）", "SVD 后谱收缩：", "gλ(σ)=√(σ²/(σ²+λ))"], BLUE),
        (1580, "⑤ 调整后的向量 E_ACE", ["主导方向被压平，", "类目结构仍在；", "再按 γ 缩放标准差"], GREEN),
    ]
    BW, BY0, BY1 = 360, 230, 500
    for x0, title, lines, color in boxes:
        x1 = x0 + BW
        d.rounded_rectangle([x0, BY0, x1, BY1], radius=18, fill=(255, 255, 255), outline=color, width=4)
        d.rectangle([x0, BY0, x1, BY0 + 9], fill=color)
        d.text((x0 + 22, BY0 + 26), title, font=f_box, fill=color)
        for i, ln in enumerate(lines):
            d.text((x0 + 22, BY0 + 82 + i * 34), ln, font=f_body, fill=(72, 78, 88))

    for x in (420, 800, 1180, 1560):
        d.rectangle([x + 4, 356, x + 32, 366], fill=(150, 156, 166))
        d.polygon([(x + 18, 336), (x + 48, 361), (x + 18, 386)], fill=(150, 156, 166))

    # 下排：推荐骨干
    d.rounded_rectangle([60, 560, 1940, 740], radius=18, fill=(255, 255, 255), outline=(120, 128, 140), width=4)
    d.rectangle([60, 560, 1940, 569], fill=(120, 128, 140))
    d.text((88, 590), "⑥ 序列推荐骨干（SASRec / BERT4Rec）", font=f_box, fill=(56, 62, 72))
    d.text((88, 648), "把 E_ACE 当作物品的初始 embedding，其余照常训练：用户历史序列 → 预测下一次交互；",
           font=f_body, fill=(72, 78, 88))
    d.text((88, 686), "不改模型结构、不改损失函数 —— 所以它是一个「即插即用」的预处理步骤。",
           font=f_body, fill=(72, 78, 88))
    d.rectangle([986, 500, 1014, 545], fill=(120, 128, 140))
    d.polygon([(1000, 528), (972, 556), (1028, 556)], fill=(120, 128, 140))

    # 谱收缩示意（条形图，标签在条形上方，避免重叠）
    ix0, iy0, ix1, iy1 = 60, 790, 1940, 1100
    d.rounded_rectangle([ix0, iy0, ix1, iy1], radius=16, fill=(255, 255, 255), outline=(196, 202, 212), width=3)
    d.text((ix0 + 28, iy0 + 20), "为什么叫「掰开」：把奇异值谱压平", font=font(30, True), fill=(56, 62, 72))
    f_lbl = font(24, True)
    rows = [
        (iy0 + 100, "原始 E（各向异性）", ORANGE, [70, 15, 10, 7, 5, 4],
         "主方向特别长，其余接近 0 → 向量全挤在一起"),
        (iy0 + 232, "ACE 之后（λ=50）", GREEN, [70, 54, 46, 38, 32, 28],
         "长条压短、短条抬起 → 方向散开，大小的相对关系还在"),
    ]
    for y, label, color, vals, note in rows:
        d.text((ix0 + 28, y - 42), label, font=f_lbl, fill=color)
        d.text((ix0 + 320, y - 42), note, font=f_note, fill=(120, 126, 136))
        for i, v in enumerate(vals):
            x = ix0 + 320 + i * 74
            d.rectangle([x, y + 70 - v, x + 40, y + 70], fill=color)

    d.text((60, 1130), "示意图 · 依据 ACE 论文 §3（arXiv 2605.29322）方法绘制；论文正文与官方仓库均未提供架构图",
           font=font(22), fill=(150, 156, 166))
    img.save(out, optimize=True)
    return out


# ============================================================
# 图 2：三态嵌入对比合成图（论文原图 ×3 纵向堆叠 + 中文标注，1080 宽）
# ============================================================
def make_embedding_comparison(out: Path):
    panels = [
        ("emb_vis_PCA2.png", "① 不处理（原始 LLM 向量）", "向量挤成一条「雪茄」：香护品在一端、护肤品在另一端，方向几乎一致", (214, 108, 32)),
        ("emb_vis_LAE_02.png", "② 只做白化（λ=0，矫枉过正）", "散是散开了，但类目层级被破坏（标注处出现「语义失真」）", (150, 60, 160)),
        ("emb_vis_LAE_502.png", "③ ACE（λ=50，平衡点）", "方向散开、类目结构还在：红圈=洗护、蓝圈=护肤，仍是两组但不再是一条线", (28, 130, 96)),
    ]
    W = 1080
    pad, header = 40, 96
    scaled = []
    for name, title, desc, color in panels:
        im = Image.open(SRC / name).convert("RGB")
        w = W - pad * 2
        h = int(im.height * w / im.width)
        scaled.append((im.resize((w, h), Image.LANCZOS), title, desc, color, h))
    H = pad + sum(header + h + 34 for _, _, _, _, h in scaled) + 60
    img = Image.new("RGB", (W, H), (250, 251, 253))
    d = ImageDraw.Draw(img)
    f_t, f_d = font(34, True), font(24)
    y = pad
    for im, title, desc, color, h in scaled:
        d.rounded_rectangle([pad - 14, y - 10, W - pad + 14, y + header + h + 16], radius=14,
                            fill=(255, 255, 255), outline=color, width=3)
        d.text((pad, y + 6), title, font=f_t, fill=color)
        for i, ln in enumerate(wrap(d, desc, f_d, W - pad * 2)):
            d.text((pad, y + 46 + i * 30), ln, font=f_d, fill=(86, 92, 102))
        img.paste(im, (pad, y + header))
        y += header + h + 34
    d.text((pad, H - 44), "图来自 ACE 论文 Figure 1（Amazon Beauty 数据集的三维嵌入可视化）", font=font(20), fill=(150, 156, 166))
    img.save(out, optimize=True)
    return out


# ============================================================
# 图 3：关键数字卡（1080×1440，自绘）
# ============================================================
def make_numbers_card(out: Path):
    W, H = 1080, 1440
    img = Image.new("RGB", (W, H), (252, 250, 247))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 16], fill=(214, 108, 32))
    d.text((56, 60), "ACE 的成绩单", font=font(60, True), fill=(30, 34, 40))
    d.line([(56, 152), (216, 152)], fill=(214, 108, 32), width=8)
    rows = [
        ("+12.4%", "Recall@20 相对提升", "相对最强的 LLM 特征基线（4 个数据集里最高的一档）"),
        ("+11.8%", "NDCG@20 相对提升", "排序质量同样最高 +11.8%"),
        ("+4.9 / +5.9", "Recall@10 / NDCG@10", "这是绝对提升（百分点），不是相对数"),
        ("3 / 3", "换 LLM 编码器都最强", "F2LLM-4B、Qwen3-8B、KaLM-12B 三个来源下都排第一"),
    ]
    y = 210
    for big, mid, small in rows:
        d.rounded_rectangle([56, y, W - 56, y + 250], radius=16, fill=(255, 255, 255), outline=(228, 224, 216), width=3)
        d.text((86, y + 40), big, font=font(66, True), fill=(214, 108, 32))
        d.text((86, y + 126), mid, font=font(32, True), fill=(44, 50, 60))
        for i, ln in enumerate(wrap(d, small, font(24), W - 200)):
            d.text((86, y + 172 + i * 32), ln, font=font(24), fill=(104, 110, 120))
        y += 276
    d.text((56, H - 70), "数据：ACE 论文（arXiv 2605.29322）· 4 数据集 / SASRec+BERT4Rec", font=font(22), fill=(150, 156, 166))
    img.save(out, optimize=True)
    return out


print("draw arch  ->", draw_architecture(IMAGES / "fig_arch_ace.png").name)
print("draw embed ->", make_embedding_comparison(IMAGES / "fig_embedding_story.png").name)
print("draw card  ->", make_numbers_card(IMAGES / "fig_numbers.png").name)

# 原图（适度放大以适配手机显示；600-1280 → ~1500 宽）
for src, dst in [("hyperparam_beauty.png", "fig_lambda_beauty.png"),
                 ("emb_eigenvalue_dist.png", "fig_eigenvalue.png"),
                 ("fig_ACE_llmsource3.png", "fig_llm_sources.png")]:
    im = Image.open(SRC / src).convert("RGB")
    if im.width < 1500:
        im = im.resize((1500, int(im.height * 1500 / im.width)), Image.LANCZOS)
    im.save(IMAGES / dst, optimize=True)
    print("img", dst, im.size)

FIG_ORDER = [
    "fig_arch_ace.png",           # 封面：架构图（自绘）
    "fig_embedding_story.png",    # 三态嵌入对比（论文原图合成）
    "fig_numbers.png",            # 成绩单（自绘）
    "fig_lambda_beauty.png",      # λ 超参扫描
    "fig_llm_sources.png",        # 换编码器柱状图
    "fig_eigenvalue.png",         # 特征值谱
]

figure_meta = {
    "fig_arch_ace.png": ("architecture",
        "【自绘架构图】ACE 全流程：物品文本(标题/类目/品牌) → LLM 编码器 → 原始向量 E（强各向异性）→ ACE 线性自编码器（重建损失保语义 + L2 正则控分散，λ 控制幅度；SVD 后做谱收缩 gλ(σ)=√(σ²/(σ²+λ))）→ E_ACE → γ 缩放 → 作为 SASRec/BERT4Rec 的物品初始 embedding 正常训练。右下角 inset 用条形示意奇异值谱被压平。注：论文与官方仓库均未提供架构图，此图据论文 §3 自绘。"),
    "fig_embedding_story.png": ("result",
        "三态嵌入对比（论文 Figure 1 三块面板合成 + 中文标注，Amazon Beauty 三维可视化）：① 原始 LLM 向量挤成雪茄形；② 只白化（λ=0）散开但语义失真；③ ACE（λ=50）方向散开且类目结构保留（红圈洗护 / 蓝圈护肤）。"),
    "fig_numbers.png": ("result",
        "【自绘成绩单】+12.4% Recall@20、+11.8% NDCG@20（相对最强基线）；+4.9 Recall@10 / +5.9 NDCG@10（绝对）；三个 LLM 编码器下均最优。"),
    "fig_lambda_beauty.png": ("result",
        "λ 敏感性（Amazon Beauty）：在「不处理」与「过度白化」之间选平衡点，ACE 取 λ=50。"),
    "fig_llm_sources.png": ("result",
        "换 LLM 编码器（F2LLM-4B / Qwen3-8B / KaLM-12B）后的 Recall@20 对比，ACE 为每组最优。"),
    "fig_eigenvalue.png": ("result",
        "嵌入协方差的特征值分布：L2 项相当于谱收缩，把造成各向异性的主导方向压平。"),
}
(PARSED / "ace_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "论文原图 + 自绘（架构图/成绩单）；论文 Figure 1 三面板合成为一张对比图",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

TITLE = "LLM 给的向量挤成一团，怎么掰开"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 一句话：拿大模型给商品编码，向量几乎都指向同一个方向；SIGIR 2026 这篇 ACE 用一个很轻的线性自编码器把向量「掰开」，推荐效果最高涨 12.4%。\n"
    "\n"
    "🧠 现在流行的做法 & 卡在哪\n"
    "「LLM 当特征提取器」：把商品标题、类目、品牌喂给大模型，拿到一串向量，当作推荐模型里物品的初始表示，再照常训练。麻烦在于这些向量「各向异性」——都挤在一个方向（看图 2 第一张：香护和护肤品各占一端，整体细长一条）。几何上挤成这样，微调时很难学进用户行为里的协同信号。\n"
    "\n"
    "✨ ACE 怎么做的（看图 1 的流程图）\n"
    "做法只有一步：把向量矩阵送进一个线性自编码器，算出调整后的版本，再交给推荐模型。它的目标函数就两项：\n"
    "• 重建项：调整完之后，物品之间的语义关系还得保住；\n"
    "• L2 正则项：控制向量散开的力度，系数 λ 就是「掰多开」的旋钮。\n"
    "等价的几何解释更好懂：对向量矩阵做 SVD，然后按奇异值大小做收缩——原来的主方向特别长，就把它压短，短的方向稍微抬起来（右下角小图）。这样谱变平、方向散开，但谁大谁小的相对关系没变。最后再按 γ 统一缩放一下标准差，就可以喂给 SASRec/BERT4Rec 正常训练了——不改模型结构、不改损失函数。\n"
    "注意别掰过头：图 2 第二张是「只白化」（λ=0）——散开了但类目层级被打乱；第三张才是 ACE 的平衡点。\n"
    "\n"
    "📊 成绩（4 个数据集：Beauty/Toys/Yelp/ML-20M）\n"
    "• 相对最强的 LLM 特征基线：Recall@20 最高 +12.4%，NDCG@20 最高 +11.8%。\n"
    "• 绝对提升：Recall@10 +4.9、NDCG@10 +5.9。\n"
    "• 换编码器同样成立：F2LLM-4B、Qwen3-8B、KaLM-12B 三个来源下都排第一。\n"
    "\n"
    "💡 对我们的意义\n"
    "拿到 LLM 的向量别直接用，先看一眼它的几何形状；这类「预处理一步」的改动成本很低，但 λ 要按数据集调（Beauty 和 Yelp 的最优点不一样）。\n"
    "\n"
    "⚠️ 局限：只在序列推荐骨干（SASRec/BERT4Rec）上验证；λ 需逐数据集调参。\n"
    "\n"
    "📄 论文：https://arxiv.org/abs/2605.29322\n"
    "💻 代码：https://github.com/DCheol/ACE\n"
    "✨ 关注我，持续拆解推荐系统 / 大模型最新论文 📚"
)
print(f"title ({len(TITLE)}): {TITLE}")
print(f"body  ({len(BODY)})")
assert len(BODY) <= 1000, f"body too long: {len(BODY)}"

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2605.29322",
    platform="xhs",
    canonical_url="https://arxiv.org/abs/2605.29322",
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": "https://arxiv.org/abs/2605.29322", "pdf": "https://arxiv.org/pdf/2605.29322",
           "code": "https://github.com/DCheol/ACE"},
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "推荐系统", "深度学习"],
        "pdf_path": str(PARSED / "2605.29322_origin.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文（另含据论文方法自绘的示意图），仅作学术解读。",
    },
    review_status="pending",
)
staged = XhsPublisher(root=ROOT).stage(package)
print("STAGED:", staged)

import os
if os.environ.get("DRY_RUN"):
    print("DRY_RUN: 仅出图与 stage，不发布")
    raise SystemExit(0)

result = XhsPublisher(root=ROOT).publish(staged["staged_id"])
print("PUBLISH RESULT:", result)

if isinstance(result, dict) and result.get("ok"):
    try:
        from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery
        OpenCliXiaohongshuDelivery()._delete(OLD_DRAFT_ID)
        print("DELETE OLD OK:", OLD_DRAFT_ID)
    except Exception as e:
        print("DELETE OLD FAILED（新稿已成功）:", type(e).__name__, str(e)[:160])
else:
    print("新稿发布失败 → 保留旧稿")
