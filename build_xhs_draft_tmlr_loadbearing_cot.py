# -*- coding: utf-8 -*-
"""
build_xhs_draft_tmlr_loadbearing_cot.py
=======================================
TMLR (accepted 2026-09-18) — "From Decorative to Load-Bearing: Task Difficulty Shapes the
Causal Role of Chain-of-Thought"（Renee Jia, DI MU）
OpenReview: https://openreview.net/forum?id=TiZQnKDIHq （PDF 有 JS 挑战，无法直连）
代码库（含论文源与全部原图）: https://github.com/r2m-ai/load-bearing-cot

规格：6 张论文原图（来自官方仓库 figures/）；标题 ≤20 字；正文 ≤1000 字；30% 人性化 + 70% 严谨。
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "openreview_TiZQnKDIHq"
IMAGES = PARSED / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

# 原图（官方仓库 figures/*.png，直接 copy）
FIG_ORDER = [
    "fig_method_flow.png",          # 封面：协议流程 + 三种行为模式及占比
    "fig_difficulty_gradient.png",  # 核心结果：难度-承重梯度
    "fig_judge_sensitivity.png",    # 判官提示敏感性（C 率不变）
    "fig_human_agreement.png",      # n=500 双人盲标一致性
    "fig_layer_sweep.png",          # 42 层探针（机制证据）
    "fig_steering.png",             # 激活引导的 null 结果
]
SRC_MAP = {
    "fig_method_flow.png": "method_flow.png",
    "fig_difficulty_gradient.png": "difficulty_gradient_unified.png",
    "fig_judge_sensitivity.png": "judge_sensitivity.png",
    "fig_human_agreement.png": "human_agreement.png",
    "fig_layer_sweep.png": "layer_sweep.png",
    "fig_steering.png": "steering.png",
}
for dst, src in SRC_MAP.items():
    s = PARSED / "source_figs" / src
    if s.exists():
        shutil.copy2(s, IMAGES / dst)
        print("img", dst, (IMAGES / dst).stat().st_size // 1024, "KB")

figure_meta = {
    "fig_method_flow.png": ("architecture",
        "Continuation-based causal testing pipeline: faithful baseline (correct answer + multi-step CoT) -> parse CoT into steps -> perturb one step (at 25/50/75% through the chain) -> truncate at the perturbed step -> continue generation from the corrupted prefix -> compare final answers. Three behavioural modes: silent bypass 38.7% / self-correction 18.3% / error propagation 43.0% (rule-based; judge-corrected 45.3% / 26.9% / 27.8%)."),
    "fig_difficulty_gradient.png": ("result",
        "The decorative-to-load-bearing transition at subject-level resolution. Blue circles = 29 MMLU subjects (Gemma-2-9B-IT); diamond/triangle/square = dataset averages for Gemma, Llama-3.1-8B-Instruct and DeepSeek-R1-Distill-Qwen-7B. Error-propagation rate rises continuously as base accuracy falls: Gemma spans 7.5% (HS psychology) to 53.7% (global facts); shaded bands mark the CoT-causal (pink) and CoT-decorative (purple) regimes."),
    "fig_judge_sensitivity.png": ("result",
        "Judge prompt sensitivity. Left: four prompt variants shift the A/B boundary by an order of magnitude but leave error propagation (red) unchanged. Right: dataset-level C rates are identical across variants."),
    "fig_human_agreement.png": ("result",
        "The n=500 two-annotator blind study: per-source agreement of the human consensus with the production label, three-way (A/B/C) and binary (C vs non-C), with 95% Wilson CIs and per-source inter-annotator kappa. Annotators agree on the C-vs-non-C split on every row (kappa = 1.00, versus 0.93 on the three-way label)."),
    "fig_layer_sweep.png": ("result",
        "Layer-wise probe accuracy across all 42 layers of Gemma-2-9B-IT (N = 2,000, grouped 5-fold CV, judge labels). 3-class probe: MLP 75.3% vs linear ~7pp lower (chance 33%); bypass probe ~80% (chance 50%); error-propagation probe also reported."),
    "fig_steering.png": ("result",
        "Single-direction activation steering at layer 21: per-type error rate under the error-propagation direction (coloured) and a random direction (grey dashed), alpha in [-10, +10], 95% Wilson CIs, n = 66 per type per alpha. The probe and random traces overlap, i.e. the null is not direction-specific."),
}

figures_payload = {
    "figures": [
        {"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]}
        for n in FIG_ORDER
    ],
    "figures_count": len(FIG_ORDER),
    "source": "Official code repo figures/ (github.com/r2m-ai/load-bearing-cot), 2026-09-20; all original paper figures",
    "note": "全部为论文原图。OpenReview PDF 直连被 JS 挑战拦截，改用官方仓库（含 paper/main.pdf 与 figures/*.png）。",
}
(PARSED / "loadbearing_cot_figures.json").write_text(json.dumps(figures_payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json written")

summary = {
    "paper_id": "TiZQnKDIHq",
    "title_zh": "CoT 从装饰到承重：越难越关键",
    "title_en": "From Decorative to Load-Bearing: Task Difficulty Shapes the Causal Role of Chain-of-Thought",
    "one_liner": "用「扰动一步→截断→续写」的因果测法量 CoT 对答案的约束力：任务越接近模型能力边界，CoT 越从装饰变成承重。",
    "problem_definition": {
        "task_type": "CoT 因果承重性测量（continuation-based causal testing）",
        "challenges": [
            "CoT 监控的前提是写出来的链因果约束答案，但该约束强度从未被量化",
            "机制可解释性（CoT 是否反映内部计算）与因果承重性是两回事，后者更容易被误用",
            "行为标签带主观性，需要判官与人工双重校验",
        ],
    },
    "main_contributions": [
        {"point": "提出 continuation-based causal testing：扰动单个推理步、截断、强制续写，量化 CoT→答案的因果承重性。"},
        {"point": "发现承重性随「模型相对难度」连续变化：CoT 从装饰过渡到承重，且是能力条件化的规律。"},
        {"point": "方差分解证明难度是主导轴（98.8% vs 扰动类型 0.8%），并用判官变体与 n=500 盲标界定主观残余。"},
    ],
    "datasets": [{"name": "GSM8K"}, {"name": "MMLU"}, {"name": "BIG-Bench Hard (BBH)"}],
    "baselines": {"models": ["Gemma-2-9B-IT", "Llama-3.1-8B-Instruct", "DeepSeek-R1-Distill-Qwen-7B"],
                  "comparisons": ["silent bypass", "self-correction", "error propagation"]},
    "metrics": ["error propagation rate (%)", "explained-deviance partition (%)", "probe accuracy (%)", "Cohen's kappa"],
    "training": {"env": "inference-time intervention study; 3 model families (8B class)",
                 "optimizer": "N/A", "valid_metric": "behavioural taxonomy over continuations"},
    "main_results": {
        "behaviour_rule_based": "silent bypass 38.7% / self-correction 18.3% / error propagation 43.0%",
        "behaviour_judge_corrected": "45.3% / 26.9% / 27.8%",
        "difficulty_gradient_Gemma": "7.5% (HS psychology) -> 53.7% (global facts) across 29 MMLU subjects",
        "propagation_MMLU_to_BBH": "22% -> 41% (+12-24pp per strategy)",
        "matched_2x2": "16x rise in error propagation within a single perturbation type as difficulty rises",
        "variance_partition": "n=28,584 continuations: 98.8% difficulty / 0.8% perturbation type / 0.4% interaction",
        "human_validation": "n=500 blind, 2 annotators, kappa=1.00 (C vs non-C) / 0.93 (three-way); judge-prompt invariant C rates",
        "steering_null": "single- and multi-direction activation steering at layer 21 does not move error rate",
    },
    "ablation": {"conclusions": [
        "难度轴远强于扰动类型与扰动强度（后者约 15-20x 弱）。",
        "推理 RL 训练（DeepSeek-R1-Distill）整体压低误差传播、压缩梯度，非传播侧转向自我纠正。",
    ]},
    "reproducibility": {"env": "scripts/prompts/analysis + camera-ready source + human-annotation materials released",
                        "code_release": "https://github.com/r2m-ai/load-bearing-cot"},
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "TiZQnKDIHq_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary written")

TITLE = "CoT 从装饰到承重：越难越关键"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 一句话：模型写出来的推理链，是「解释给人看」，还是真的在决定答案？这篇 TMLR 新论文给了因果测法——看难度。\n"
    "\n"
    "🧠 解决什么问题\n"
    "拿 CoT 做监控，前提是写出来的链因果上约束了答案，但这个约束有多强，一直没人量过。（它测的是 CoT→答案这一向，不涉及「CoT 是否反映内部计算」。）\n"
    "\n"
    "✨ 怎么测的\n"
    "取正确多步 CoT → 切成步 → 在链的 25%/50%/75% 处扰动一步 → 在该处截断 → 让模型续写 → 比最终答案。三种行为：silent bypass 38.7%、self-correction 18.3%、error propagation 43.0%（判官校正后 45.3%/26.9%/27.8%）。\n"
    "\n"
    "📊 四个关键数字\n"
    "1. 难度梯度：Gemma 在 29 个 MMLU 学科上，误差传播率从 7.5%（高中心理）连续升到 53.7%（全球事实）；同一套文本策略下 GSM8K→BBH 从 22% 升到 41%。\n"
    "2. 谁在主导：固定扰动类型（数值）后，难度上来误差传播涨 16 倍；n=28,584 条续写的方差分解把 98.8% 的解释偏差归给难度，扰动类型只占 0.8%。\n"
    "3. 推理 RL 的影响：DeepSeek-R1-Distill 把误差传播整体压低、梯度被压扁，非传播侧更多转向自我纠正。\n"
    "4. 验证强度：判官提示换 4 个变体，error propagation 不变、C 率完全一致；n=500 双人盲标在 C-vs-non-C 上每行都一致（κ=1.00）。\n"
    "\n"
    "💡 给用 CoT 的人\n"
    "推理链只在「承重区」才值得当监控信号，而且要按「模型相对难度」校准——同一个任务，对强模型是装饰，对弱模型可能承重。想直接改这条链（激活引导）在本文实验里改不动。\n"
    "\n"
    "⚠️ 局限：只测 CoT→答案方向；3 个 8B 级模型、3 个基准；行为标签仍有余留主观性。\n"
    "\n"
    "📄 论文（TMLR 2026-09-18）：https://openreview.net/forum?id=TiZQnKDIHq\n"
    "💻 代码：https://github.com/r2m-ai/load-bearing-cot\n"
    "✨ 关注我，持续拆解大模型 / Agent 最新论文 📚"
)
assert len(BODY) <= 1000, len(BODY)
print(f"title ({len(TITLE)}): {TITLE}")
print(f"body  ({len(BODY)})")

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="TiZQnKDIHq",
    platform="xhs",
    canonical_url="https://openreview.net/forum?id=TiZQnKDIHq",
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={
        "paper": "https://openreview.net/forum?id=TiZQnKDIHq",
        "pdf": "https://openreview.net/pdf?id=TiZQnKDIHq",
        "code": "https://github.com/r2m-ai/load-bearing-cot",
    },
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "深度学习", "AI"],
        "pdf_path": str(PARSED / "lb_cot_main.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文，仅作学术解读。",
    },
    review_status="pending",
)
print(f"package: title={len(TITLE)}c body={len(BODY)}c images={len(package.image_paths)}")
print("STAGED:", XhsPublisher(root=ROOT).stage(package))
