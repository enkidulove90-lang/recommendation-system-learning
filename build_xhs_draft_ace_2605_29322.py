# -*- coding: utf-8 -*-
"""
build_xhs_draft_ace_2605_29322.py
=================================
从用户给的 7 篇候选里挑「配图观赏性最高」的一篇做小红书草稿。

候选（arXiv 可查到的 5 篇，均已核对图库存）：
  GenCDSR 2607.28659（4 图）/ UniPinRec 2606.00422（3 图）/ DIGER 2601.19711（8 图，折线+热力图）
  GraphLoRA 2606.07526（6 图）/ **ACE 2605.29322（8 图，含 3 张 3D 嵌入可视化）**
  M2R / SIHG-Rec：arXiv 检索无结果，跳过。
→ 视觉胜出：ACE（3 张彩色 3D 嵌入散点图，直接讲"各向异性/语义失真/平衡"的故事；DIGER 为常规折线图）。

ACE = Anisotropy-Controllable Embedding（SIGIR 2026；arXiv 2605.29322）
规格：6 张论文原图；标题 ≤20 字；正文 ≤1000 字；30% 人性化 + 70% 严谨；文风按 skill §3.1（说人话）。
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2605.29322"
IMAGES = PARSED / "images"
IMAGES.mkdir(parents=True, exist_ok=True)
SRC = PARSED / "source" / "Figures"

FIG_ORDER = [
    "fig_pca_anisotropy.png",     # 封面：PCA 视角下向量挤成"雪茄"（问题）
    "fig_whitened.png",           # 白化（λ=0）：散开了但语义层级被破坏
    "fig_ace_ours.png",           # ACE（λ=50）：既不过挤也不失真
    "fig_llm_sources.png",        # 换 3 个 LLM 编码器，ACE 都是最优
    "fig_eigenvalue.png",         # 特征值分布（几何侧证据）
    "fig_hyperparam_beauty.png",  # λ 超参扫描（Beauty）
]
SRC_MAP = {
    "fig_pca_anisotropy.png": "emb_vis_PCA2.png",
    "fig_whitened.png": "emb_vis_LAE_02.png",
    "fig_ace_ours.png": "emb_vis_LAE_502.png",
    "fig_llm_sources.png": "fig_ACE_llmsource3.png",
    "fig_eigenvalue.png": "emb_eigenvalue_dist.png",
    "fig_hyperparam_beauty.png": "hyperparam_beauty.png",
}
for dst, src in SRC_MAP.items():
    s = SRC / src
    if s.exists():
        shutil.copy2(s, IMAGES / dst)
        print("img", dst, (IMAGES / dst).stat().st_size // 1024, "KB")
    else:
        print("MISSING", src)

figure_meta = {
    "fig_pca_anisotropy.png": ("architecture",
        "Figure (motivation, PCA panel): 3D SVD view of LLM-generated item embeddings on Amazon Beauty. The point cloud collapses into a narrow cigar shape (strong anisotropy) - hair-care items at one end, skin-care items at the other - so most vectors point in similar directions and the geometry fights collaborative fine-tuning."),
    "fig_whitened.png": ("framework",
        "Figure (motivation, whitened-PCA panel = perfect isotropy, lambda=0): the cloud spreads out, but the semantic hierarchy is distorted - the skin-care cluster collapses inward (labelled 'Semantic distortion'), i.e. over-correcting anisotropy destroys item relationships."),
    "fig_ace_ours.png": ("result",
        "Figure (motivation, ACE panel, lambda=50): the balanced embedding space produced by the linear autoencoder - clusters stay separated (red dashed = hair care, blue dashed = skin care) while the distribution is no longer a degenerate cigar."),
    "fig_llm_sources.png": ("result",
        "Recall@20 grouped by LLM encoder (F2LLM-4B, Qwen3-8B, KaLM-12B) - ACE (dark blue) is the best bar in all three settings, i.e. the fix is not tied to one embedding source."),
    "fig_eigenvalue.png": ("result",
        "Eigenvalue distribution of the embedding covariance: the L2 term acts as spectral shrinkage, flattening the dominant directions that cause anisotropy."),
    "fig_hyperparam_beauty.png": ("result",
        "Sensitivity to the anisotropy-controlling weight lambda on Amazon Beauty; ACE (lambda=50) sits at the balance point between the anisotropic baseline and over-whitening."),
}
(PARSED / "ace_figures.json").write_text(json.dumps({
    "figures": [{"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]} for n in FIG_ORDER],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2605.29322 source tarball (figures/), all original paper figures",
    "selection_note": "从用户给的 7 篇候选中选图：ACE 有 3 张 3D 嵌入可视化，观赏性最高（DIGER/GraphLoRA/GenCDSR/UniPinRec 以折线图与框图为主）。",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json ok")

summary = {
    "paper_id": "2605.29322",
    "title_zh": "把挤成一团的向量掰开，涨了 12%",
    "title_en": "ACE: Anisotropy-Controllable Embedding for LLM-enhanced Sequential Recommendation",
    "one_liner": "LLM 给的物品向量都挤在一个方向（各向异性），用一个线性自编码器把它「掰开」，Recall@20 相对最强基线最高 +12.4%。",
    "problem_definition": {
        "task_type": "LLM-as-Extractor 范式的序列推荐（LLM 生成物品嵌入 + 微调）",
        "challenges": ["LLM 生成的物品嵌入各向异性强，向量集中在相似方向", "几何失衡导致微调时难以适配协同信号", "过度白化又会破坏语义层级"],
    },
    "main_contributions": [
        {"point": "指出并量化 LLM 物品嵌入的各向异性几何失衡问题，用 3D 可视化展示（PCA/白化/ACE 三态）。"},
        {"point": "提出 ACE：线性自编码器（LAE）重塑分布，L2 正则控制方向分散度、重建损失保语义。"},
        {"point": "四个基准数据集、两种骨干、多种 LLM 编码器下一致最优，即插即用不改结构。"},
    ],
    "datasets": [{"name": "Amazon Beauty"}, {"name": "Amazon Toys"}, {"name": "Yelp 2018"}, {"name": "ML-20M"}],
    "baselines": {"llm_as_extractor": ["LLM2X", "LLMEmb", "AlphaFuse（最强基线）"], "backbones": ["SASRec", "BERT4Rec"]},
    "metrics": ["Recall@10/20", "NDCG@10/20"],
    "training": {"env": "SASRec / BERT4Rec 骨干；物品文本用 text-embedding-3-large、F2LLM-4B、Qwen3-Embedding-8B、KaLM-12B 编码",
                 "optimizer": "N/A（初始化层方法）", "valid_metric": "Recall@20 / NDCG@20"},
    "main_results": {
        "relative_gain": "Recall@20 最高 +12.4%、NDCG@20 最高 +11.8%（相对最强 LLM-as-Extractor 基线）",
        "absolute_gain": "Recall@10 +4.9、NDCG@10 +5.9（相对最强竞争基线）",
        "encoder_robust": "在 F2LLM-4B / Qwen3-8B / KaLM-12B 三个编码器下均为最优；比 AlphaFuse 最高 +2.94%",
        "lambda_balance": "λ=∞（不处理）强各向异性、λ=0（完全白化）语义层级被破坏、λ=50 平衡",
    },
    "ablation": {"conclusions": ["L2 正则相当于对协方差做谱收缩，压掉造成各向异性的主导方向。",
                                 "λ 需按数据集调（Beauty 与 Yelp 曲线不同）。"]},
    "reproducibility": {"env": "四个基准数据集，过滤交互 <5 的用户/物品", "code_release": "论文未声明公开代码"},
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2605.29322_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary ok")

TITLE = "把挤成一团的向量掰开，涨了 12%"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 一句话：大模型很会「描述」物品，但它给的向量有个毛病——全都挤在一个方向上。这篇 SIGIR 2026 的论文用一个很小的自编码器把向量「掰开」，Recall@20 最高涨了 12.4%。\n"
    "\n"
    "🧠 问题出在哪\n"
    "现在做推荐常用「LLM 当特征提取器」：把商品标题、类目、品牌喂给大模型，拿到一串向量当作物品的初始表示，再拿去微调。麻烦是这些向量很「各向异性」——几乎所有向量都指向差不多的方向，挤成一条细细的雪茄（看图 1）。几何上失衡之后，微调时它很难学进去用户的协同信号。\n"
    "\n"
    "✨ 他们怎么修的\n"
    "方法叫 ACE，核心就是一个线性自编码器，两项损失各管一件事：\n"
    "• 重建损失：保证掰开之后，物品之间的语义关系还在；\n"
    "• L2 正则：控制向量散开的程度，这就是那个「掰多开」的旋钮（参数 λ）。\n"
    "所以它不是简单白化：图 2 是完全白化（λ=0）的结果——向量是散开了，但类目之间的层级被打乱（标注为「语义失真」）；图 3 才是 ACE（λ=50），既不过挤、也不失真。\n"
    "\n"
    "📊 几个关键数字\n"
    "• 4 个数据集：Amazon Beauty / Toys、Yelp、ML-20M；骨干用 SASRec 和 BERT4Rec。\n"
    "• 相对最强的 LLM 特征基线：Recall@20 最高 +12.4%，NDCG@20 最高 +11.8%。\n"
    "• 绝对提升：Recall@10 +4.9、NDCG@10 +5.9。\n"
    "• 换编码器也成立：F2LLM-4B、Qwen3-8B、KaLM-12B 三个来源下都最好，比最强基线最高再 +2.94%。\n"
    "\n"
    "💡 对我们做推荐的意义\n"
    "这是「即插即用」的初始化技巧，不用改模型结构；但它提醒一件事：拿到 LLM 向量别直接用，先看看它的几何形状。λ 也不是越大越好，要按数据集调（Beauty 和 Yelp 的最优点就不一样）。\n"
    "\n"
    "⚠️ 局限：只在序列推荐骨干（SASRec/BERT4Rec）上验证；没有公开代码；λ 需要逐数据集调。\n"
    "\n"
    "📄 论文（arXiv 2605.29322）：https://arxiv.org/abs/2605.29322\n"
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
    links={"paper": "https://arxiv.org/abs/2605.29322", "pdf": "https://arxiv.org/pdf/2605.29322", "code": ""},
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "推荐系统", "深度学习"],
        "pdf_path": str(PARSED / "2605.29322_origin.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文，仅作学术解读。",
    },
    review_status="pending",
)
staged = XhsPublisher(root=ROOT).stage(package)
print("STAGED:", staged)
print("STAGED_ID:", staged["staged_id"])
