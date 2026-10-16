#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 A 组（有全文+有配图）的待发论文按博客分类归档，并排出写作顺序。

用法:
    python skills/blog_classify.py

输出:
    docs/blog_publish_plan.md  —— 分类分组 + 顺序
    %TEMP%/blog_plan.json      —— 机读版，供写作时消费
分类优先级（按用户 2026-10-16 指定）：多模态推荐 → 知识图谱推荐 → LLM 与生成式推荐
                                     → 大语言模型与Agent → 其他领域
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("TEMP", "/tmp")

# 手工override：标题关键词规则判错的，按 arXiv 编号钉死
OVERRIDE = {
    "2303.05979": "其他领域",        # 拉普拉斯-拉格朗日稳定性反例（数学）
    "2503.00987": "其他领域",        # 管道流湍流转变概率（流体力学）
    "2508.00543": "其他领域",        # 海事远程操作中心认证
    "2505.19525": "多模态推荐",      # ConfSMoE：任意模态输入的置信门控 MoE（推荐）
}

# 非推荐系统的选题（标题里没有"推荐"却属于 LLM/Agent 主题）
AGENTISH = ["智能体科学基准", "智能体基准", "编码", "软件工程", "红队", "世界模型",
            "稀疏注意力", "上下文建模", "可验证环境", "推理泛化", "智能体", "agent",
            "harness", "loop engineering", "文献", "检索增强生成框架", "知识增强检索生成"]
OTHER = ["湍流", "管道流", "拉普拉斯", "海事", "认证", "Wi-Fi", "宠物", "存在检测"]


def classify(title, aid):
    if aid in OVERRIDE:
        return OVERRIDE[aid]
    t = title.lower()
    is_rec = ("推荐" in title) or ("recommend" in t) or ("rec" in t)
    if not is_rec:
        for k in OTHER:
            if k.lower() in t:
                return "其他领域"
        for k in AGENTISH:
            if k.lower() in t:
                return "大语言模型与Agent"
        return "其他领域"
    if "知识图谱" in title or "图谱" in title:
        return "知识图谱推荐"
    if "多模态" in title or "模态" in title or "跨模态" in title:
        return "多模态推荐"
    if any(k in title for k in ["大语言模型", "LLM", "生成式", "大模型", "语义标识", "对话"]):
        return "LLM 与生成式推荐"
    return "LLM 与生成式推荐"


def main():
    p = os.path.join(TMP, "blog_ready.json")
    if not os.path.exists(p):
        sys.exit("先跑 skills/blog_worklist.py 生成 blog_ready.json")
    ready = json.load(open(p, encoding="utf-8"))
    groups = {}
    for r in ready:
        r["cat"] = classify(r["title"], r["aid"])
        groups.setdefault(r["cat"], []).append(r)
    order = ["多模态推荐", "知识图谱推荐", "LLM 与生成式推荐", "大语言模型与Agent", "其他领域"]
    L = ["# 待发论文分组与写作顺序", ""]
    total = 0
    for c in order:
        rs = sorted(groups.get(c, []), key=lambda x: -x["full"])
        total += len(rs)
        L.append(f"## {c}（{len(rs)} 篇）")
        L.append("")
        if not rs:
            L.append("（无）")
            L.append("")
            continue
        L.append("| # | 编号 | 标题 | 全文KB | 图 |")
        L.append("|---|---|---|---|---|")
        for i, r in enumerate(rs, 1):
            L.append(f"| {i} | {r['aid']} | {r['title'][:46]} | {r['full']//1024} | {r['nimg']} |")
        L.append("")
    L.append(f"合计 {total} 篇")
    open(os.path.join(ROOT, "docs", "blog_publish_plan.md"), "w", encoding="utf-8",
         newline="\n").write("\n".join(L) + "\n")
    json.dump(groups, open(os.path.join(TMP, "blog_plan.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for c in order:
        print(f"  {c}: {len(groups.get(c, []))}")
    print("total", total, "-> docs/blog_publish_plan.md")


if __name__ == "__main__":
    main()
