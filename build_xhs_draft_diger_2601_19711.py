# -*- coding: utf-8 -*-
"""
build_xhs_draft_diger_2601_19711.py
===================================
换稿：DIGER（Differentiable Semantic ID for Generative Recommendation）—— 满足用户三条要求：
  ① 有**真正的算法架构图**（论文自带 STE vs DIGER 对比架构图，矢量 PDF → 3x 渲染 4107×1859 高清）
  ② **图片质量高**（6 张全部 ≥2300px 宽或 >300KB；无 600px 小图）
  ③ 文本写清楚（输入/中间加了一步什么/输出给谁/不改什么 + 显式引用图号）

候选对比依据（上一轮已实测图库与渲染质量）：
  DIGER 2601.19711（8 图：2 张 framework + 2 motivation + 3 张大图）> GenCDSR 2607.28659（4 图）
  > UniPinRec 2606.00422（3 图）> GraphLoRA 2606.07526（6 图）> ACE 2605.29322（无架构图，已弃）
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2601.19711"
IMAGES = PARSED / "images"

FIG_ORDER = [
    "fig_arch_compare.png",       # 封面：传统 STE（硬更新） vs DIGER（可微软更新）架构对比
    "fig_motivation_old.png",     # 问题：两阶段冻结 SID → 梯度被阻断 + 目标错配
    "fig_diger_vs_ste.png",       # 关键证据：DIGER vs STE 的 NDCG@10 曲线 + 码本平衡度
    "fig_codebook_heatmap.png",   # 码本使用热力图（4 方法 × 3 层 × 256 码）
    "fig_sid_drift.png",          # 四种 SID 分配方法随训练的漂移对比
    "fig_uncertainty_decay.png",  # 两种不确定性衰减策略（SDUD / FrqUD）
]

figure_meta = {
    "fig_arch_compare.png": ("architecture",
        "论文核心架构对比图（Figure：Comparison of conventional two-stage generative recommendation and training with differentiable semantic IDs）。上排 STE：商品内容 → Encoder → Codebook → **硬更新（红色虚线）** → 生成式推荐器；下排 DIGER：商品内容 → Encoder → **DRIL Codebook（加入 Gumbel 噪声 + 不确定性衰减）** → **软更新（可微，红色虚线）** → 生成式推荐器。"),
    "fig_motivation_old.png": ("framework",
        "动机图：传统两阶段流水线把 RQ-VAE 语义 ID 冻结（预训练后不再更新），推荐器的梯度传不回 tokenizer，造成 gradient blocking 与 objective mismatch。"),
    "fig_diger_vs_ste.png": ("result",
        "关键对比（B-Shop 数据集）：上图为 DIGER 与朴素 STE 的验证集 NDCG@10 随 epoch 的变化曲线；下图用三层码本覆盖率的均值（含标准差）刻画码本平衡度。STE 出现明显塌缩，DIGER 保持较高码本利用率。"),
    "fig_codebook_heatmap.png": ("result",
        "最好 checkpoint 下四种方法的码本使用分布：每个 16×16 网格对应 256 个码字，颜色深浅代表使用概率，三列对应三层量化——直观展示哪些方法只用了少数码（塌缩）而 DIGER 用得更均匀。"),
    "fig_sid_drift.png": ("result",
        "四种语义 ID 分配方法随训练轮次的演化对比（含 Incremental SID Drift 等），说明静态/增量式分配与可微分配的差异。"),
    "fig_uncertainty_decay.png": ("framework",
        "两种不确定性衰减策略：基于标准差的 SDUD 与基于使用频率的 FrqUD，用于把早期探索逐步退火为对已学语义 ID 的利用。"),
}
(PARSED / "diger_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2601.19711 源包（figs/），全部为论文原图；矢量 PDF 以 3.0–3.2x 渲染成高清 PNG",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

summary = {
    "paper_id": "2601.19711",
    "title_zh": "让推荐损失回头去调语义 ID",
    "title_en": "DIGER: Differentiable Semantic ID for Generative Recommendation",
    "one_liner": "生成式推荐的语义 ID 只按「能还原内容」学、与推荐目标脱节；DIGER 让推荐梯度直接更新 SID，并用 Gumbel 探索 + 不确定性衰减避免码本塌缩。",
    "problem_definition": {
        "task_type": "生成式推荐（离散语义 ID / RQ-VAE 索引 + 推荐器）",
        "challenges": ["SID 由 tokenizer 独立训练，推荐损失无法回传（目标错配）",
                       "直接把索引做成可微会引起码本塌缩（只用少数码）",
                       "早期确定性分配限制了码本探索，优化不稳定"],
    },
    "main_contributions": [
        {"point": "指出并形式化生成式推荐中的 objective mismatch：索引损失与推荐损失各自优化、tokenizer 与推荐器解耦。"},
        {"point": "提出 DIGER：用 Gumbel 噪声显式鼓励早期码本探索，缓解塌缩、提升码字利用率。"},
        {"point": "提出两种不确定性衰减（SDUD/FrqUD），实现从探索到利用的平滑过渡。"},
    ],
    "datasets": [{"name": "B-Shop (Beauty)"}, {"name": "I-Shop (Instruments)"}, {"name": "Yelp"}],
    "baselines": {"tokenizers": ["RQ-VAE", "LETTER"], "recommenders": ["TIGER", "ETEGRec", "SASRec"], "variant": ["naive STE (直接可微)"]},
    "metrics": ["Recall@10", "NDCG@10", "codebook utilization / balance"],
    "training": {"env": "three public datasets; two-stage (tokenizer + recommender) 基线 vs 联合可微训练",
                 "optimizer": "N/A（训练策略/索引层方法）", "valid_metric": "Recall@10 / NDCG@10"},
    "main_results": {
        "B-Shop": "R@10 0.0610(两阶段) → 0.0657–0.0696；N@10 0.0331 → 0.0361–0.0376（相对最高 +14.1%）",
        "I-Shop": "R@10 0.1058 → 0.1124–0.1138；N@10 0.0797 → 0.0823–0.0844",
        "Yelp": "R@10 0.0407 → 0.0432–0.0439；N@10 0.0213 → 0.0227",
        "naive_STE_collapse": "朴素 STE 在 B-Shop 上 R@10 掉到 0.0134（相比两阶段 0.0610），即码本塌缩",
    },
    "ablation": {"conclusions": ["Gumbel 噪声与两种不确定性衰减各自有贡献，组合后既缓解塌缩又保证收敛。",
                                 "码本容量 K 与 SID 长度 m 影响效果（论文有专门分析）。"]},
    "reproducibility": {"env": "公开数据集 + 公开代码", "code_release": "https://github.com/junchen-fu/DIGER"},
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2601.19711_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary ok")

TITLE = "让推荐损失回头去调语义 ID"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 一句话：生成式推荐把商品压成一串离散的「语义 ID」，但它只按「能不能还原内容」来学，跟「推荐准不准」是两套目标；DIGER 让推荐损失能反过来更新它，B-Shop 上 Recall@10 最高涨 14%。\n"
    "\n"
    "🧠 问题：两套目标，各学各的\n"
    "生成式推荐通常分两步：先用 tokenizer（如 RQ-VAE）把商品内容压成语义 ID，再交给推荐器预测下一次交互。麻烦是 tokenizer 训完就冻住了——推荐损失传不回去，索引只管「还原得像不像」，推荐只管「排得准不准」（看图 2）。\n"
    "\n"
    "✨ 直接做成可微？会崩\n"
    "论文试了：让推荐梯度直接穿过量化步骤（STE），结果码本塌缩——只用到少数几个码，优化极不稳定。B-Shop 上 Recall@10 从两阶段的 0.0610 掉到 0.0134。\n"
    "\n"
    "🔧 DIGER 的两步改法（看图 1 的上下对比）\n"
    "① 量化选择里加 Gumbel 噪声：早期强制它去试不同的码，避免一开始就锁死（对应图 4 的码本使用热力图，DIGER 用得更均匀）。\n"
    "② 两种不确定性衰减（SDUD 按标准差 / FrqUD 按使用频率，图 6）：随训练把噪声降下来，从「探索」过渡到「利用」。\n"
    "这样量化这一步仍然可微（软更新），但不会因为早期乱选而塌缩。\n"
    "\n"
    "📊 效果（Recall@10 / NDCG@10）\n"
    "• B-Shop：R@10 0.0610 → 0.0657–0.0696，N@10 0.0331 → 0.0361–0.0376。\n"
    "• I-Shop：R@10 0.1058 → 0.1124–0.1138。\n"
    "• Yelp：R@10 0.0407 → 0.0432–0.0439。\n"
    "• 在 B-Shop 与 I-Shop 上超过所有列出的基线（TIGER / ETEGRec / LETTER 等）。\n"
    "\n"
    "💡 对我们的意义\n"
    "只要系统里有「独立训练 + 离散化」的环节，梯度就会断。修法不一定要硬拆成两段，而是让梯度能过去，同时给早期探索留点噪声，再逐步退火。\n"
    "\n"
    "⚠️ 局限：三个公开数据集、离散语义 ID 场景；噪声强度与衰减超参（r、λ）需要调。\n"
    "\n"
    "📄 论文：https://arxiv.org/abs/2601.19711\n"
    "💻 代码：https://github.com/junchen-fu/DIGER\n"
    "✨ 关注我，持续拆解推荐系统 / 大模型最新论文 📚"
)
print(f"title ({len(TITLE)}): {TITLE}")
print(f"body  ({len(BODY)})")
assert len(BODY) <= 1000, f"body too long: {len(BODY)}"

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2601.19711",
    platform="xhs",
    canonical_url="https://arxiv.org/abs/2601.19711",
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": "https://arxiv.org/abs/2601.19711", "pdf": "https://arxiv.org/pdf/2601.19711",
           "code": "https://github.com/junchen-fu/DIGER"},
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "推荐系统", "深度学习"],
        "pdf_path": str(PARSED / "2601.19711_origin.pdf"),
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
