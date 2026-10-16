# -*- coding: utf-8 -*-
"""
build_xhs_draft_tmlr_cot_v2.py
==============================
TMLR《From Decorative to Load-Bearing》小红书草稿 v2 —— 重写文案（去学术行话，改平实叙述）。

v1 问题（用户反馈）："写法太生硬了不知道在写什么" —— 翻译腔 + 术语堆砌
（承重区 / 方差分解 / 解释偏差 / silent bypass 等直接搬英文）。
v2 原则：说人话——术语一律给中文解释、句子短、先讲"怎么测的"再给数字；
精确数字一个不少（严谨度不变），但不再用学术腔包装。

流程：stage → 删除草稿箱旧稿(s:3abfa504-…) → publish 新稿 → 待核验
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "openreview_TiZQnKDIHq"
IMAGES = PARSED / "images"
OLD_DRAFT_ID = "s:3abfa504-2171-4e25-a141-a330704d42a9"   # v1 草稿（生硬版），发布成功后删除

FIG_ORDER = [
    "fig_method_flow.png",
    "fig_difficulty_gradient.png",
    "fig_judge_sensitivity.png",
    "fig_human_agreement.png",
    "fig_layer_sweep.png",
    "fig_steering.png",
]

TITLE = "题目越难，CoT 越决定答案"
assert len(TITLE) <= 20, len(TITLE)

BODY = (
    "🎓 模型写的推理过程（CoT），到底是给它自己看的草稿，还是真的决定了答案？TMLR 这篇新论文给了一个测因果的办法，结论是：看题目难不难。\n"
    "\n"
    "🧠 它想解决什么\n"
    "现在很多产品拿 CoT 当监控，看模型怎么一步步推。前提是：写出来的链得真的在影响答案；否则你监控的只是一段「事后编的解释」。而这个前提，以前没人量过。\n"
    "\n"
    "✨ 怎么测的\n"
    "思路很朴素，像做对照实验：\n"
    "1. 找一道模型本来能答对、且会写多步推理的题；\n"
    "2. 把中间某一步（推理链的 25%、50%、75% 处）故意改错；\n"
    "3. 从错的地方把链截断，让它接着写；\n"
    "4. 看最后的答案：是被带跑偏了，还是自己纠回来了。\n"
    "结果分三种：43.0% 被带跑偏（跟着错的算下去）、18.3% 自己纠回来、38.7% 干脆无视那处改动。\n"
    "\n"
    "📊 四个关键数字\n"
    "1. 题目越难，CoT 越「算数」。Gemma 在 29 个 MMLU 学科上，被带跑偏的比例从 7.5%（心理学）升到 53.7%（全球常识）；换成 GSM8K→BBH 这组题、同一套改法，则从 22% 升到 41%。\n"
    "2. 起作用的是「难度」，不是「怎么改」。只改数字类错误时，题目变难会让带跑偏率涨 16 倍；对 28,584 条数据做归因，难度能解释 98.8% 的差异，改动方式只占 0.8%。\n"
    "3. 用推理 RL 训过的模型（DeepSeek-R1-Distill）更不容易被带跑偏，难度造成的差距也被压平，更多是自己纠回来。\n"
    "4. 结论经得起查。换 4 种判官提示结果不变；两位标注者盲标 500 条，在「是否被带跑偏」上每条都一致。\n"
    "\n"
    "💡 对我们的意义\n"
    "CoT 监控只在「这题对模型够难」时才有效，简单题上它可能只是装饰；同一套规则，对不同水平的模型要重新校准。另外想用激活引导直接改这条链，这篇实验里没改成。\n"
    "\n"
    "⚠️ 局限：只做了 3 个 8B 级模型、3 个基准；也只测了「推理链→答案」这个方向，不代表这条链能反映模型内部真实的计算。\n"
    "\n"
    "📄 论文（TMLR 2026-09-18）：https://openreview.net/forum?id=TiZQnKDIHq\n"
    "💻 代码：https://github.com/r2m-ai/load-bearing-cot\n"
    "✨ 关注我，持续拆解大模型 / Agent 最新论文 📚"
)
print(f"title ({len(TITLE)}): {TITLE}")
print(f"body  ({len(BODY)})")
assert len(BODY) <= 1000, f"body too long: {len(BODY)}"

# ---------- stage ----------
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
staged = XhsPublisher(root=ROOT).stage(package)
staged_id = staged["staged_id"]
print("STAGED:", staged)

# ---------- 先发新稿；成功后再删旧稿（避免新稿失败导致草稿箱两头空） ----------
from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery

result = XhsPublisher(root=ROOT).publish(staged_id)
print("PUBLISH RESULT:", result)

if isinstance(result, dict) and result.get("ok"):
    try:
        delivery = OpenCliXiaohongshuDelivery()
        delivery._delete(OLD_DRAFT_ID)
        print("DELETE OLD OK:", OLD_DRAFT_ID)
    except Exception as e:
        print("DELETE OLD FAILED（新稿已成功，旧稿需手动删）:", type(e).__name__, str(e)[:200])
else:
    print("新稿发布失败 → 保留旧稿，不删除")
