# -*- coding: utf-8 -*-
"""
build_xhs_draft_2609_22086.py
==============================
arXiv 2609.22086 — Designer-RSI: Evolving Procedural Memory from User Traffic for Agentic
Graphic Design (2026-09-18)

规格：全论文原图 6 张；标题 ≤20 字；正文 ≤1000 字；30% 人性化 + 70% 科学严谨。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2609.22086"
IMAGES = PARSED / "images"

FIG_ORDER = [
    "fig_teaser.png",              # 封面：系统总览（Phase1 创作评估 / Phase2 反思演化）
    "fig_snow_before.png",         # 无技能：雪渲染为稀疏圆点
    "fig_snow_after.png",          # 有技能：按用户偏好渲染成密集风雪
    "fig_skill_bank_growth.png",   # 技能库 5 轮演化（76 冷启动 + 63 新铸 = 139）
    "fig_widening_pipeline.png",   # 拓宽：聚类未覆盖子任务 → 蒸馏新技能 → 回放门控
    "fig_deepening_pipeline.png",  # 深化：对比失败/成功历史重写技能 → 门控
]

figure_meta = {
    "fig_teaser.png": ("architecture",
        "System overview. Phase 1 Creation & Evaluation: brief from user prompt enters the graphic-design agent; the Skill Bank retrieves matching skills and filters the tool list; the agent executes >230 design tools through intermediate document states. Phase 2 Reflection & Evolution: skill deepening (contrastive reflection over success vs failure, load-balance selection, rewrite, pairwise verification gate), skill widening (cluster unmatched-request gaps, distill new skills, replay gate), and personalization (multi-turn distillation)."),
    "fig_snow_before.png": ("result",
        "Personalization, Base arm (no personalized skill): the default renders snow as a sparse particle / bokeh field on the frozen backbone."),
    "fig_snow_after.png": ("result",
        "Personalization, Ours arm (with the user-flagged skill): the same frozen backbone now renders snow as a dense, realistic streak field, matching the user's stated method preference."),
    "fig_skill_bank_growth.png": ("result",
        "Skill-bank evolution over five rounds (BGE-small-en-v1.5 embeddings, UMAP, cosine). Hollow markers = 76 cold-start skills distilled from internal documentation; filled = 63 skills minted from user data; colours mark the target application (Photoshop 55 / Illustrator 47 / InDesign 37). Bank grows 76 -> 139 with no weight updates."),
    "fig_widening_pipeline.png": ("framework",
        "Widening pipeline: histories with no skill retrieved are clustered into recurring coverage gaps, distilled into candidate skills, and admitted to the bank only through the replay performance gate (pass -> Skill Bank, fail -> discarded)."),
    "fig_deepening_pipeline.png": ("framework",
        "Deepening pipeline: failure-prone skills are revised by contrasting failed and successful histories; a candidate enters the bank only if it wins at the replay gate on the skill's worst failing prompts."),
}

figures_payload = {
    "figures": [
        {"image_file": f"images/{n}", "figure_type": figure_meta[n][0], "description": figure_meta[n][1]}
        for n in FIG_ORDER
    ],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2609.22086 (2026-09-18); original figures (teaser/personalization/UMAP copied, pipeline PDFs rendered at 3x via PyMuPDF)",
    "note": "全部为论文原图，无自制插图。",
}
(PARSED / "2609.22086_figures.json").write_text(json.dumps(figures_payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("figures.json:", len(FIG_ORDER))

summary = {
    "paper_id": "2609.22086",
    "title_zh": "不重训模型，给设计 Agent 加技能库",
    "title_en": "Designer-RSI: Evolving Procedural Memory from User Traffic for Agentic Graphic Design",
    "one_liner": "冻结前沿模型不改一个权重，靠外部自然语言「技能库」的拓宽与深化，五轮把专业设计执行成功率从 72.7% 抬到 99.3%。",
    "problem_definition": {
        "task_type": "Agentic graphic design（长程、结构化可编辑产物、无可靠程序化 oracle）",
        "challenges": [
            "专业设计是长程任务，结果缺乏可靠的程序化对错信号",
            "冻结模型无法通过权重更新持续适应",
            "新增经验容易修好失败却回退既有成功",
        ],
    },
    "main_contributions": [
        {"point": "外部程序化记忆（自然语言技能库）替代权重更新：拓宽补齐未覆盖子任务、深化重写易失败技能。"},
        {"point": "匹配回放门控：只接受「修好失败且不回退成功」的技能改动。"},
        {"point": "5 轮 1406 briefs / 1869 条自动评分轨迹，零权重更新、零人工标注，技能库 76→139。"},
    ],
    "datasets": [
        {"name": "GenEval2"},
        {"name": "user-traffic benchmark (200 held-out briefs)"},
        {"name": "four specialized graphic-design benchmarks"},
    ],
    "baselines": {
        "backbones": ["Claude-Sonnet-4", "Claude-Opus-4.6", "Qwen3.6-27B"],
        "arms": ["Base (no skill bank)", "Evolve (widening + deepening)"],
    },
    "metrics": ["execution success rate (%)", "generation quality (point gain)", "pairwise win rate vs no-skill agent (%)"],
    "training": {
        "env": "Frozen frontier models operating Photoshop / Illustrator / InDesign through >230 tools",
        "optimizer": "N/A（无权重更新；记忆层演化）",
        "valid_metric": "GenEval2 execution success + GPT-5.4 judged pairwise win rate",
    },
    "main_results": {
        "skill_bank": "76 -> 139 skills (63 minted from user data)",
        "GenEval2_success_ClaudeSonnet4": "72.7% -> 99.3%",
        "generation_quality_gain": "+11.99 points",
        "win_rate_vs_noskill": {"Claude-Sonnet-4": "61.8%", "Claude-Opus-4.6": "67.6%"},
        "ablation_200_briefs": {"widening_only": "49.4%", "deepening_only": "48.6%", "combined": "58.5% (p=0.025)"},
        "scale": "5 rounds / 1406 briefs / 1869 auto-graded trajectories; no weight updates, no human labels",
    },
    "ablation": {
        "conclusions": [
            "单独拓宽或深化都无显著优势，两者组合出现超加性交互（+3.85 completeness）。",
            "记忆层的价值来自「可编辑的自然语言流程」，而不是模型能力提升。",
        ],
    },
    "reproducibility": {
        "env": "Graphic-Eval 自动评分器 + 用户流量 brief；Qwen3.6-27B 本地部署受稳定性限制",
        "code_release": "论文未声明公开代码",
    },
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2609.22086_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("summary written")

TITLE = "不重训模型，给设计 Agent 加技能库"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 一句话：不改一个权重，让设计 Agent 五轮把执行成功率从 72.7% 抬到 99.3%。\n"
    "\n"
    "🧠 解决什么问题\n"
    "专业设计是长程任务——要产出可编辑的工程文件（PS/AI/ID），几十步互相依赖，而且还说不出什么叫「做对了」。没有可靠的程序化对错信号，模型怎么持续变强？微调贵、还会遗忘。\n"
    "\n"
    "✨ 怎么做的\n"
    "冻结前沿模型，让它操作 Photoshop / Illustrator / InDesign 的 230+ 工具；在模型外面挂一个「自然语言技能库」，用两种机制自我演化：\n"
    "1. 拓宽：把没检索到技能的失败历史聚类成重复覆盖缺口，蒸馏出新技能。\n"
    "2. 深化：拿失败与成功的历史做对比反思，重写容易翻车的旧技能。\n"
    "3. 回放门控：任何改动都要在「原本会失败的 prompt」上通过验证，且不能回退已成功的案例。\n"
    "\n"
    "📊 关键数字\n"
    "• 5 轮 / 1406 条 brief / 1869 条自动评分轨迹，零权重更新、零人工标注。\n"
    "• 技能库从 76 条（内部文档冷启动）长到 139 条（其中 63 条从用户数据新铸）。\n"
    "• GenEval2 执行成功率：Claude-Sonnet-4 上 72.7% → 99.3%，生成质量 +11.99 分。\n"
    "• 对「无技能」Agent 的两两胜率：Sonnet-4 61.8%、Opus-4.6 67.6%。\n"
    "• 消融（200 条留出 brief）：只拓宽 49.4%、只深化 48.6%，两者组合 58.5%（p=0.025）——单独做都没优势，合起来才有超加性。\n"
    "\n"
    "💡 最直观的证据是「个性化」那张对比：同一句 prompt、同一个冻结模型，没技能时雪是稀疏圆点，加上用户标注的技能后就变成密集风雪——技能是可以用自然语言写、能改、能回滚的。\n"
    "\n"
    "⚠️ 局限：依赖 Graphic-Eval 自动评分器与用户流量 brief，设计域特化；本地小模型（Qwen3.6-27B）受部署稳定性限制。\n"
    "\n"
    "📄 论文：https://arxiv.org/abs/2609.22086\n"
    "✨ 关注我，持续拆解 Agent / 大模型最新论文 📚"
)
assert len(BODY) <= 1000, len(BODY)
print(f"title ({len(TITLE)}): {TITLE}")
print(f"body  ({len(BODY)})")

from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2609.22086",
    platform="xhs",
    canonical_url="https://arxiv.org/abs/2609.22086",
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={"paper": "https://arxiv.org/abs/2609.22086", "pdf": "https://arxiv.org/pdf/2609.22086", "code": ""},
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "智能体", "AI绘画"],
        "pdf_path": str(PARSED / "2609.22086_origin.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文，仅作学术解读。",
    },
    review_status="pending",
)
print(f"package: title={len(TITLE)}c body={len(BODY)}c images={len(package.image_paths)}")
print("STAGED:", XhsPublisher(root=ROOT).stage(package))
