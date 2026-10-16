# -*- coding: utf-8 -*-
"""
build_xhs_draft_2609_20804.py
==============================
arXiv 2609.20804 — An Empirical Study of Harness Design for Coding Agents (2026-09-17)

规格（用户要求 + skill 约束）：
- 图片：全部用论文原图（6 张，PyMuPDF 从源 PDF 渲染高清 PNG，无自制卡）
- 标题 ≤20 字；正文 ≤1000 字；风格 30% 人性化 + 70% 科学严谨
- 走规范 stage →（人工确认）→ publish CDP 全链路
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2609.20804"
IMAGES = PARSED / "images"

# ============================================================
# 1. 6 张论文原图（顺序 = 笔记图序，封面为手绘 graphical abstract）
# ============================================================
FIG_ORDER = [
    "fig_graphical_abstract.png",    # 封面：全篇手绘概览（4 模型/2 基准/4 窗口/176 设置）
    "fig_harness_overview_v2.png",   # harness 架构 + T4 上下文管理流程（M1/M2/M3）
    "fig_window_overflow.png",       # 结论1：窗口预算 vs 成功率与溢出率
    "fig_tier_cost.png",             # 结论2：T0-T4 各档成功率与成本
    "fig_planning_effect.png",       # 结论3：planning 开/关的成功率与成本
    "fig_tool_effect.png",           # 结论4：仅 bash vs 全工具集
]

figure_meta = {
    "fig_graphical_abstract.png": (
        "architecture",
        "Graphical abstract of the study: coding harness components (context management T0-T4, planning on/off, tool set vs bash-only), 4 models (Nemotron-3 30B/120B/550B, Mistral-3.5 128B), 2 benchmarks (SWE-Bench Verified, Terminal-Bench 2.1), 4 context windows (32k-128k), 176 settings.",
    ),
    "fig_harness_overview_v2.png": (
        "framework",
        "Overview of the coding harness: ReAct loop (input assembly -> coding model -> tool execution -> observation -> context history) and the T4 context-management strategy (M1 placeholder elision, M2 external store + recall_event, M3 mid-region summarization; soft/hard thresholds B1<B2).",
    ),
    "fig_window_overflow.png": (
        "result",
        "Success rate and window-overflow rate vs context-window budget across 4 models x 2 benchmarks. Managed tiers (blue) vs T0 no management (black); orange = T0 overflow rate. Managed-T0 gap shrinks from 35.7pp at 32k to 2.7pp at 128k on SWE-Bench; T0 overflow falls 78.7%->8.7%; managed tiers have zero overflow.",
    ),
    "fig_tier_cost.png": (
        "result",
        "Success rate (capsules, min-max over 4 window budgets) and mean cost per task (orange line) for context-management tiers T0-T4. T4 highlighted (green) as the default tier; elision-then-summarization gives the best efficiency.",
    ),
    "fig_planning_effect.png": (
        "result",
        "Absolute performance and cost with vs without planning (T4, 128k, full tool set). Planning raises success for the weaker 30B (+11.6pp SWE-Bench, +4.5pp Terminal-Bench) but mainly cuts cost for stronger models.",
    ),
    "fig_tool_effect.png": (
        "result",
        "Effect of the action space: bash-only vs full tool set (T4, 128k, planning on). Success rate, mean cost per task, and share of actions issued through bash when all tools are enabled.",
    ),
}

figures_payload = {
    "figures": [
        {
            "image_file": f"images/{name}",
            "figure_type": figure_meta[name][0],
            "description": figure_meta[name][1],
        }
        for name in FIG_ORDER
    ],
    "figures_count": len(FIG_ORDER),
    "source": "arXiv 2609.20804 (2026-09-17), original figure PDFs rendered at 2.6x via PyMuPDF",
    "note": "全部为论文原图，无自制插图。",
}
(PARSED / "2609.20804_figures.json").write_text(
    json.dumps(figures_payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"figures.json written: {len(FIG_ORDER)} figures")

# ============================================================
# 2. 摘要记录（11 维 schema 对齐）
# ============================================================
summary = {
    "paper_id": "2609.20804",
    "title_zh": "编码 Agent：脚手架该加还是该减？",
    "title_en": "An Empirical Study of Harness Design for Coding Agents",
    "one_liner": "固定执行循环、只动 planning / 工具集 / 上下文管理三件事，在 4 个模型 × 2 个编码基准 × 4 个上下文窗口共 176 组设置里量出每个部件的真实贡献。",
    "problem_definition": {
        "task_type": "Coding-agent harness 组件级消融（component-level ablation）",
        "challenges": [
            "harness 常被当作一个整体评估，各部件贡献不清",
            "上下文管理、规划、工具集的收益是否随模型变强而消失，缺乏系统测量",
            "工程界普遍照抄同一套 harness 配置",
        ],
    },
    "main_contributions": [
        {"point": "固定执行循环，单独消融 planning / action space / context management 三个部件，共 176 组匹配设置。"},
        {"point": "上下文管理收益主要来自「避免溢出」：窗口越紧越值钱，全档 managed 零溢出。"},
        {"point": "规则省略 + LLM 摘要的组合效率最优；把省略内容做成可召回反而无用（36/64 组从不调用）。"},
        {"point": "规划对弱模型提分、对强模型省钱；工具集对弱 bash 模型有用，强 bash 模型仅用 bash 更便宜。"},
    ],
    "datasets": [
        {"name": "SWE-Bench Verified"},
        {"name": "Terminal-Bench 2.1"},
    ],
    "baselines": {
        "context_management": ["T0 无管理", "T1 省略", "T2 省略+召回", "T3 摘要", "T4 省略+召回+摘要（默认）"],
        "planning": ["off", "on"],
        "action_space": ["bash-only", "full tool set"],
    },
    "metrics": ["success rate (%)", "context-overflow failure rate (%)", "mean cost per task ($)"],
    "training": {
        "env": "4 models: Nemotron-3 30B / 120B / 550B, Mistral-Medium-3.5-128B; Docker/E2B task container",
        "optimizer": "N/A (inference-time ablation study)",
        "valid_metric": "task success rate on SWE-Bench Verified / Terminal-Bench 2.1",
    },
    "main_results": {
        "context_management": {"managed_minus_T0_SWE_32k_to_128k_pp": [35.7, 15.9, 5.5, 2.7],
                               "managed_minus_T0_TB_32k_to_128k_pp": [9.5, 7.5, 4.8, 2.8],
                               "T0_overflow_rate_SWE": "78.7% -> 8.7%", "managed_overflow": "0/全档"},
        "recall_mechanism": {"T2_vs_T1_mean_pp": -0.36, "settings_never_calling_recall_event": "36/64",
                             "heaviest_config_vs_T1_pp": -3.37},
        "planning": {"30B_SWE_pp": 11.6, "30B_TB_pp": 4.5, "120B_SWE_pct": 1.6, "120B_TB_pct": 4.5},
        "action_space": {"550B_bash_only_SWE_pct": 3.6, "550B_bash_only_TB_pct": 5.6,
                         "550B_cost_change": "-53% SWE / -30% TB"},
    },
    "ablation": {
        "conclusions": [
            "上下文管理的价值几乎全部来自「不让任务因为窗口溢出而死」，而不是让模型更聪明。",
            "机制不是越多越好：可召回省略（M2）增加了机械复杂度却没有精度收益。",
        ],
    },
    "reproducibility": {
        "env": "176 matched settings; costs priced via OpenRouter (Aug 2026)",
        "code_release": "论文未声明公开代码",
    },
}
(ROOT / "data" / "summaries").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "summaries" / "2609.20804_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("summary written")

# ============================================================
# 3. 标题 + 正文（≤20 / ≤1000；30% human + 70% rigor）
# ============================================================
TITLE = "编码 Agent：脚手架该加还是该减？"
assert len(TITLE) <= 20, f"title too long: {len(TITLE)}"

BODY = (
    "🎓 一句话：模型之外的一切都算 harness——它到底给你提分，还是只让你烧钱？\n"
    "\n"
    "🧠 解决什么问题\n"
    "上下文管理、规划、工具集被当成一整套「最佳实践」到处抄，但几乎没人单独量过每个部件的贡献，也没人验证过：模型变强之后，这些收益还在吗？\n"
    "\n"
    "✨ 怎么做的\n"
    "固定执行循环不动，只变三个部件：planning、action space、context management。4 个模型（Nemotron-3 30B/120B/550B + Mistral-3.5 128B）× SWE-Bench Verified + Terminal-Bench 2.1 × 4 个上下文窗口（32k/64k/96k/128k），共 176 组匹配设置。\n"
    "\n"
    "📊 四个结论\n"
    "1. 上下文管理是「防猝死」：窗口越紧越值钱。managed 与无管理的差距从 32k 的 35.7 个百分点，缩到 128k 的 2.7；而 T0 因窗口溢出而失败的比例从 78.7% 掉到 8.7%，所有 managed 档位在四个窗口下溢出数都是 0。它买的是「别把任务撑死」，不是「模型更聪明」。\n"
    "2. 机制不是越多越好：先规则化省略、再 LLM 摘要最划算；而把省略内容做成可召回的 external store，64 组里 36 组从头到尾没调用过一次，用量最重的配置反而比 T1 低 3.37 个百分点。\n"
    "3. 规划看模型：对弱一点的 30B 是提分项（SWE-Bench +11.6pp、Terminal-Bench +4.5pp），到 120B 精度收益缩到 1.6%/4.5%，主要价值变成「更省」。\n"
    "4. 工具集是给弱 bash 模型的：550B 只给 bash，成功率反而 +3.6%/+5.6%，成本降 53%/30%。能写好命令行的模型，不需要预定义工具。\n"
    "\n"
    "💡 给做 Agent 的人\n"
    "别照抄别人的 harness 配置：它应该是模型能力的函数。先量你的模型弱在哪（窗口溢出 / 命令行不熟 / 擅长跑长），再决定加什么——加错机制不会掉太多精度，但会稳定地让你多花钱。\n"
    "\n"
    "⚠️ 局限：4 个模型、2 个基准，成本按 OpenRouter 价目估算；单次运行未报多次重复的方差。\n"
    "\n"
    "📄 论文：https://arxiv.org/abs/2609.20804\n"
    "✨ 关注我，持续拆解 Agent / 大模型最新论文 📚"
)
assert len(BODY) <= 1000, f"body too long: {len(BODY)}"
print(f"title ({len(TITLE)} chars): {TITLE}")
print(f"body  ({len(BODY)} chars)")

# ============================================================
# 4. stage
# ============================================================
from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2609.20804",
    platform="xhs",
    canonical_url="https://arxiv.org/abs/2609.20804",
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={
        "paper": "https://arxiv.org/abs/2609.20804",
        "pdf": "https://arxiv.org/pdf/2609.20804",
        "code": "",
    },
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "智能体", "AI编程"],
        "pdf_path": str(PARSED / "2609.20804_origin.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文，仅作学术解读。",
    },
    review_status="pending",
)
print(f"package: title={len(TITLE)}c body={len(BODY)}c images={len(package.image_paths)}")

publisher = XhsPublisher(root=ROOT)
staged = publisher.stage(package)
print("STAGED:", staged)
