# -*- coding: utf-8 -*-
"""
build_xhs_draft_2609_05339.py
==============================
为 arXiv 2609.05339（Does Your Agent's Memory Survive a Model Upgrade?，2026-09-04）
手工构造小红书草稿，跳过 paper_to_xhs 自动渲染（其强 RecSys 调性 + 硬编码 MSCA/RecSys 脚注不适合本篇）。

资产：
- 3 张 arXiv 源 PNG（study_design / memory_formats / key_results），高质
- 2 张 PIL 自制中文要点卡（takeaways / 实践清单）
- 手工标题/正文/话题，全部走规范 stage 校验 + CDP 发布链路
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
PARSED = ROOT / "data" / "parsed" / "2609.05339"
IMAGES = PARSED / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. 5 张高质量配图：3 原生 + 2 自制卡
# ============================================================
FIG_ORDER = [
    "study_design.png",        # 封面：研究设计总览
    "memory_formats.png",      # 4 种记忆格式对比
    "key_results.png",         # 关键数字 4 联图
    "card_takeaways.png",      # 自制：3 条结论速览
    "card_builder_checklist.png",  # 自制：给做 Agent 的人实践清单
]

CJK_FONT = Path(r"C:/Windows/Fonts/msyh.ttc")  # 微软雅黑，Windows 自带
TITLE_FONT_CANDIDATES = [
    r"C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑 Bold
    CJK_FONT,
]
BODY_FONT_CANDIDATES = [
    CJK_FONT,
]


def load_font(candidates, size):
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_card(out_name: str, bg_rgb, title: str, blocks: list[tuple[str, str]],
              accent_rgb=(255, 87, 87)):
    """PIL 自制竖版要点卡 (1080x1440)。blocks: [(headline, body), ...]"""
    W, H = 1080, 1440
    img = Image.new("RGB", (W, H), bg_rgb)
    d = ImageDraw.Draw(img)

    title_font = load_font(TITLE_FONT_CANDIDATES, 64)
    head_font = load_font(BODY_FONT_CANDIDATES, 52)
    body_font = load_font(BODY_FONT_CANDIDATES, 36)

    # 顶部装饰条
    d.rectangle([0, 0, W, 18], fill=accent_rgb)

    # 标题
    d.text((60, 70), title, font=title_font, fill=(28, 28, 28))
    d.line([(60, 180), (220, 180)], fill=accent_rgb, width=8)

    y = 240
    for headline, body in blocks:
        d.text((60, y), headline, font=head_font, fill=accent_rgb)
        y += 72
        # 自动换行
        for line in wrap_text(d, body, body_font, W - 130):
            d.text((70, y), line, font=body_font, fill=(60, 60, 60))
            y += 52
        y += 30

    # 底部
    d.text((60, H - 80), "arXiv 2609.05339  ·  2026-09-04",
           font=load_font(BODY_FONT_CANDIDATES, 28), fill=(140, 140, 140))
    img.save(IMAGES / out_name, optimize=True)
    return out_name


def wrap_text(d, text, font, max_width):
    """按 max_width 像素切分 text 为多行。"""
    lines = []
    cur = ""
    for ch in text:
        nxt = cur + ch
        bbox = d.textbbox((0, 0), nxt, font=font)
        if bbox[2] - bbox[0] > max_width:
            lines.append(cur)
            cur = ch
        else:
            cur = nxt
    if cur:
        lines.append(cur)
    return lines


# Card A：3 条结论速览
draw_card(
    "card_takeaways.png",
    bg_rgb=(250, 250, 250),
    title="三条结论速览",
    blocks=[
        ("① KG-fixed 最稳",
         "换作者后，固定模式知识图谱的准确率仅漂移 +0.0004 ± 0.0020；构造时是什么模型，读时换什么模型几乎不影响。"),
        ("② NOTES 看方向",
         "自然语言压缩笔记迁移呈强烈不对称：Llama→Qwen 掉 13.3 个百分点，Qwen→Llama 反而涨 9.9 个百分点。同一份记忆，换谁读谁决定一切。"),
        ("③ RAG 不要混索引",
         "嵌入升级 bge-large-en v1.0→v1.5：旧索引 43%，新索引 54%；把新旧向量混在同一个索引里只到 48%，7 个点本来能拿的丢了。"),
    ],
    accent_rgb=(54, 84, 158),
)

# Card B：给做 Agent 的人实践清单
draw_card(
    "card_builder_checklist.png",
    bg_rgb=(252, 248, 240),
    title="给做 Agent 的人",
    blocks=[
        ("✅ 跨模型前：方向性测试",
         "不要假设「A 写的记忆 B 能读」或反过来，先用 5-10 条样本做双向迁移测试，看到方向差再决定是否要重写。"),
        ("✅ 别把新旧嵌入混一锅",
         "升级 retriever 就要全量重嵌。半新半旧是最差的中间态——你花钱买了延迟，但没买到性能。"),
        ("✅ 压缩笔记要存原文",
         "只存模型压缩后的 notes，等换模型时基本救不回来（48 条历史全失败）。原文留底，笔记只是索引。"),
        ("✅ 想稳：用结构化记忆",
         "固定 schema 知识图谱是这份研究里唯一「换模型不变形」的格式，代价是 schema 设计的人工成本。"),
    ],
    accent_rgb=(178, 70, 30),
)

# ============================================================
# 2. 手工 5 图精选（figure_type 排序：architecture/result 优先）
# ============================================================
figures_payload = {
    "figures": [
        {
            "image_file": "images/study_design.png",
            "figure_type": "architecture",
            "description": "Figure: Study design and migration setup. 48 synthetic histories, 160 questions, two open-weight <10B models, 4 memory formats, controlled migration directions.",
        },
        {
            "image_file": "images/memory_formats.png",
            "figure_type": "framework",
            "description": "Figure: Comparison of the four memory formats (LC-RAW / RAG / NOTES / KG-fixed) on stored content, inference use, portability risk, repair path. Most portable = KG-fixed; most writer-dependent = NOTES; most retrieval-dependent = RAG.",
        },
        {
            "image_file": "images/key_results.png",
            "figure_type": "result",
            "description": "Figure: Key empirical results. NOTES asymmetric transfer (-13.3 / +9.9), KG-fixed +0.0004, RAG mixed index loses 7 pts, store-only NOTES repair 0/48 vs raw-retained 34/48, loss decomposition NOTES 80% at construction / RAG 81% at retrieval.",
        },
        {
            "image_file": "images/card_takeaways.png",
            "figure_type": "other",
            "description": "Custom card: 3 takeaways (KG-fixed stability, NOTES directionality, RAG mixed-index loss).",
        },
        {
            "image_file": "images/card_builder_checklist.png",
            "figure_type": "other",
            "description": "Custom card: practitioner checklist for Agent builders (directional test, no mixed embeddings, keep raw source, prefer structured memory).",
        },
    ],
    "figures_count": 5,
    "source": "arXiv 2609.05339 (2026-09-04) + custom take-aways (PIL)",
    "note": "3 native figures from arXiv source tar + 2 custom Chinese summary cards (PIL/msyh.ttc).",
}
figures_path = PARSED / "2609.05339_figures.json"
figures_path.write_text(json.dumps(figures_payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"figures.json: {figures_path}  ({len(figures_payload['figures'])} figures)")

# ============================================================
# 3. 11 维摘要（asset 记录用，render_note 跳过所以可极简）
# ============================================================
summary = {
    "paper_id": "2609.05339",
    "title_zh": "换模型后，Agent会失忆？记忆移植实测",
    "title_en": "Does Your Agent's Memory Survive a Model Upgrade? A Controlled Study of Memory Portability",
    "one_liner": "把同一份对话历史存成 4 种格式（LC-RAW/RAG/NOTES/KG-fixed），跨两个 10B 级模型交换读，覆盖率从 0 到 -13 个百分点。",
    "problem_definition": {
        "task_type": "LLM Agent memory portability (controlled cross-model evaluation)",
        "challenges": [
            "换模型后，记忆存储可能「水土不服」",
            "压缩后的自然语言笔记高度依赖写笔记的模型",
            "RAG 嵌入版本混用会偷走一大半迁移收益",
        ],
    },
    "main_contributions": [
        {"point": "首次给出 Agent 记忆四类格式的迁移效应定量对比，覆盖 48 段合成历史 × 2 个开源 10B 模型。"},
        {"point": "指出 KG-fixed 几乎不漂移、NOTES 强烈不对称、RAG 嵌入升级需全量重嵌三条实践准则。"},
        {"point": "把端到端损失分解到「构造 vs 检索」，给出可定位的修复起点。"},
    ],
    "datasets": [
        {"name": "48 段合成多轮对话历史（每段 160 道精确匹配题 + 随机化答案码）"},
    ],
    "baselines": {
        "memory_formats": ["LC-RAW", "RAG", "NOTES", "KG-fixed"],
    },
    "metrics": ["exact-match accuracy", "swap Δ percentage points", "loss decomposition (construction vs retrieval)"],
    "training": {
        "env": "2 open-weight models, 7-8B parameters",
        "optimizer": "N/A (inference-time controlled study)",
        "valid_metric": "exact-match vs ground-truth answer codes",
    },
    "main_results": {
        "KG-fixed": {"writer_swap_pp": 0.0004, "sem": 0.0020},
        "NOTES": {"llama_to_qwen_pp": -13.28, "qwen_to_llama_pp": 9.91},
        "RAG": {"old_index_acc": 43, "mixed_index_acc": 48, "full_reembed_acc": 54},
        "repair": {"notes_raw_retained_90pct_target": "34/48", "notes_store_only": "0/48"},
        "loss_decomp": {"NOTES_construction_share": 0.80, "RAG_retrieval_share": 0.81},
    },
    "ablation": {
        "conclusions": [
            "方向性测试比大小更重要；同一份 NOTES 换边读差异可超过 20 个百分点。",
            "检索失败的 81% 集中在「用了旧索引」，修了就能拿回；构造损失的 80% 已被「压缩时丢掉」，存原文才能救。",
        ],
    },
    "reproducibility": {
        "env": "2 open-weight 7-8B models, exact scoring against randomized codes",
        "code_release": "未公开（论文处于审稿中）",
    },
}
summary_path = ROOT / "data" / "summaries" / "2609.05339_summary.json"
summary_path.parent.mkdir(parents=True, exist_ok=True)
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"summary: {summary_path}")

# ============================================================
# 4. 标题 + 正文（≤20字 / ≤1000字 / 30% human + 70% rigor）
# ============================================================
TITLE = "换模型后，Agent会失忆？记忆移植实测"
assert len(TITLE) <= 20, f"title too long: {len(TITLE)}"

BODY = (
    "🎓 一句话：换一个大模型，Agent 记的事可能就变味。\n"
    "\n"
    "🧠 解决什么问题\n"
    "升级模型是工程日常，迁移记忆不是。同一个 memory store，换个 reader 就能「记错」：压缩笔记被新模型读偏、混合嵌入索引让检索半失灵、原文不存就修不回来。\n"
    "\n"
    "✨ 关键设计\n"
    "1. 同一份 48 段合成多轮历史，存成 4 种记忆格式（LC-RAW / RAG / NOTES / KG-fixed）。\n"
    "2. 两个开源 7-8B 模型互换读 + 三种 RAG 嵌入版本（bge-large-en v1.0/混合/v1.5）。\n"
    "3. 端到端准确率精确匹配 + 损失拆到「构造 vs 检索」两个阶段。\n"
    "\n"
    "📊 三个最关键数字\n"
    "• KG-fixed 换作者后仅漂移 +0.0004 ± 0.0020 个百分点；结构化记忆真的能跨模型。\n"
    "• NOTES 跨模型迁移呈强烈方向性：Llama→Qwen 掉 13.3，Qwen→Llama 反涨 9.9；同一份笔记谁写谁读决定一切。\n"
    "• RAG 嵌入升级 bge-large-en v1.0→v1.5：全量重嵌 +12 个百分点；只把新旧向量混在同一个索引里只 +5，丢了一半的潜在收益。\n"
    "\n"
    "💡 给做 Agent 的人\n"
    "• 跨模型前先做 5-10 条样本的双向迁移测试，不要拍脑袋。\n"
    "• 升级 retriever 就全量重嵌，半新半旧是最差的中间态。\n"
    "• 模型压缩的笔记一定要存原文——只存 notes，48 条历史换模型后修复 0 条能达标。\n"
    "\n"
    "⚠️ 局限：合成历史 + 2 个 10B 级开源模型；真实多模态/长程/工具调用场景待补。\n"
    "\n"
    "📄 论文：https://arxiv.org/abs/2609.05339\n"
    "✨ 关注我，下一篇继续拆最新 LLM/Agent 论文"
)

assert len(BODY) <= 1000, f"body too long: {len(BODY)}"
print(f"title ({len(TITLE)} chars): {TITLE}")
print(f"body  ({len(BODY)} chars)")
print(f"ratio human/rigor: 开头 hook + 实践段 = human; 中段精确数字 = rigor")

# ============================================================
# 5. stage 草稿（人工审核后 --publish 推草稿箱）
# ============================================================
from redbook.automation.publishing import PublicationPackage, XhsPublisher

package = PublicationPackage(
    paper_id="2609.05339",
    platform="xhs",
    canonical_url="https://arxiv.org/abs/2609.05339",
    title=TITLE,
    body_markdown=BODY,
    image_paths=[str(IMAGES / p) for p in FIG_ORDER],
    links={
        "paper": "https://arxiv.org/abs/2609.05339",
        "pdf": "https://arxiv.org/pdf/2609.05339",
        "code": "",
    },
    metadata={
        "topics": ["论文分享", "人工智能", "大模型", "智能体", "知识图谱"],
        "pdf_path": str(PARSED / "2609.05339_origin.pdf"),
        "author": "",
        "source_attribution": "图表摘自论文，仅作学术解读。",
    },
    review_status="pending",
)
print(f"package ready: title={len(TITLE)}c body={len(BODY)}c images={len(package.image_paths)} pdf={package.metadata['pdf_path']}")

publisher = XhsPublisher(root=ROOT)
staged_path = publisher.stage(package)
print(f"STAGED: {staged_path}")
print(f"review_status=pending — 待人工核对后执行 --publish")
