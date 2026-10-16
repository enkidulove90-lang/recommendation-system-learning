#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""博客三维正交分类：领域大类 / 任务场景 / 技术方法。

设计（用户 2026-10-16 定）：
  维度1 领域大类（单选，必填）→ 决定 Hexo 一级 category 与顶部导航
  维度2 任务场景（多选）      → Hexo 二级 category + 进入 tags
  维度3 技术方法（多选）      → 进入 tags

Hexo 落地约定：
  categories: [<一级>, <二级>]     例 [推荐系统, 多模态推荐]
  tags: [<任务…>, <方法…>]         例 [多模态推荐, 对比学习, 图神经网络]

用法：
  python skills/blog_taxonomy.py --plan     # 输出 58 篇的归类表，人工复核
  python skills/blog_taxonomy.py --posts    # 重排已发布文章的 front matter
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = r"C:/Users/xu.yan1/enkidu-blog/repo/source/_posts"
TMP = os.environ.get("TEMP", "/tmp")

# —— 维度1：领域大类（一级分类）——
DOMAIN_RECSYS = "推荐系统"
DOMAIN_AI = "AI"
DOMAIN_GRAPH = "图学习"
DOMAIN_MISC = "跨学科与基础"

# —— 二级分类（任务/方向）——
SUB_MM = "多模态推荐"
SUB_KG = "知识图谱"
SUB_COLD = "冷启动"
SUB_SEQ = "序列推荐"
SUB_GEN = "生成式推荐"
SUB_GCL = "图对比学习"
SUB_LTR = "长尾推荐"
SUB_COMMON = "基础推荐算法"
SUB_AGENT = "大模型与智能体"
SUB_RAG = "检索增强生成"
SUB_SCHOLAR = "学术检索"

TASK_VOCAB = ["冷启动", "多模态推荐", "序列推荐", "生成式推荐", "长尾推荐",
              "图对比学习", "学术检索", "信息检索"]
METHOD_VOCAB = ["大模型微调", "强化学习", "图神经网络", "混合专家", "多智能体",
                "对比学习", "扩散模型"]

# 标题关键词 → (level1, level2)
RULES = [
    (["多模态", "模态", "视觉", "跨模态"], DOMAIN_RECSYS, SUB_MM),
    (["知识图谱", "图谱", "KG"], DOMAIN_RECSYS, SUB_KG),
    (["冷启动"], DOMAIN_RECSYS, SUB_COLD),
    (["序列推荐", "多行为", "序列建模"], DOMAIN_RECSYS, SUB_SEQ),
    (["生成式", "生成推荐", "检索增强生成推荐", "RAG 推荐"], DOMAIN_RECSYS, SUB_GEN),
    (["图对比", "邻层图"], DOMAIN_RECSYS, SUB_GCL),
    (["长尾"], DOMAIN_RECSYS, SUB_LTR),
    (["推荐", "协同过滤", "rec", "CTR"], DOMAIN_RECSYS, SUB_COMMON),
    # 非推荐系统
    (["学术检索", "论文搜索", "文献检索", "科研论文检索", "文献"], DOMAIN_AI, SUB_SCHOLAR),
    (["检索增强生成", "RAG", "检索增强"], DOMAIN_AI, SUB_RAG),
    (["智能体", "Agent", "大语言模型", "大模型", "语言模型", "注意力",
      "世界模型", "基准", "推理", "红队"], DOMAIN_AI, SUB_AGENT),
    (["图学习", "图神经", "图与"], DOMAIN_GRAPH, ""),
]

# 手工钉死（关键词判错/需要更准的）
OVERRIDE = {
    "2303.05979": (DOMAIN_MISC, "", ["理论推导"], []),          # 拉普拉斯稳定性反例
    "2503.00987": (DOMAIN_MISC, "", ["流体力学"], []),          # 管道流湍流
    "2508.00543": (DOMAIN_MISC, "", ["海事认证"], []),          # 海事远程操作认证
    "2505.00556": (DOMAIN_MISC, "", ["理论推导"], []),          # A+xA=R（数学）
    "2504.00678": (DOMAIN_MISC, "", ["无线感知"], []),          # Wi-Fi 人宠检测
    "2505.19525": (DOMAIN_RECSYS, SUB_MM, ["多模态推荐"], ["混合专家"]),  # ConfSMoE
    "2601.13969": (DOMAIN_RECSYS, SUB_KG, ["知识图谱"], ["强化学习"]),     # ARK
    "2605.28175": (DOMAIN_RECSYS, SUB_KG, ["知识图谱"], ["混合专家", "多智能体"]),
    "2505.20773": (DOMAIN_RECSYS, SUB_KG, ["冷启动"], ["检索增强生成"]),
    "2510.21652": (DOMAIN_AI, SUB_AGENT, ["学术检索"], ["多智能体"]),      # AstaBench
    "2501.10120": (DOMAIN_AI, SUB_SCHOLAR, ["学术检索"], ["多智能体"]),    # PaSa
    "2507.15245": (DOMAIN_AI, SUB_SCHOLAR, ["学术检索"], ["多智能体"]),    # SPAR
    "2407.18940": (DOMAIN_AI, SUB_SCHOLAR, ["学术检索"], []),              # LitSearch
    "2605.25007": (DOMAIN_AI, SUB_AGENT, [], ["多智能体"]),                # Meta-Modal Agent
    "2606.22151": (DOMAIN_AI, SUB_SCHOLAR, ["学术检索"], ["多智能体"]),
    "2605.14306": (DOMAIN_AI, SUB_SCHOLAR, ["学术检索"], []),
    "2508.05666": (DOMAIN_AI, SUB_RAG, ["信息检索"], ["检索增强生成"]),    # HySemRAG
    "2510.27566": (DOMAIN_AI, SUB_RAG, ["信息检索"], ["检索增强生成"]),    # Interact-RAG
    "2507.21892": (DOMAIN_AI, SUB_RAG, [], ["强化学习", "检索增强生成"]),  # Graph-R1
    "2506.18019": (DOMAIN_GRAPH, "", [], ["多智能体"]),                    # Graphs Meet AI Agents
    "gpt-red": (DOMAIN_AI, SUB_AGENT, [], ["多智能体", "强化学习"]),
    "ra-rft": (DOMAIN_AI, SUB_AGENT, [], ["大模型微调", "强化学习"]),
    "2510.22049": (DOMAIN_MISC, "", ["序列建模"], []),                     # VISTA
    "2605.10730": (DOMAIN_AI, SUB_AGENT, [], []),                          # Qwen-Image-2.0（多模态大模型技术报告）
    "2302.08191": (DOMAIN_RECSYS, SUB_GCL, ["图对比学习"], ["图神经网络", "对比学习"]),
    "2507.07522": (DOMAIN_RECSYS, SUB_GCL, ["图对比学习"], ["图神经网络", "对比学习"]),
}

TASK_KEYS = {
    "冷启动": ["冷启动", "cold-start", "cold start"],
    "多模态推荐": ["多模态", "模态"],
    "序列推荐": ["序列", "sequential", "多行为"],
    "生成式推荐": ["生成式", "generative"],
    "长尾推荐": ["长尾", "long-tail"],
    "图对比学习": ["图对比", "对比学习", "contrastive"],
    "学术检索": ["学术", "论文检索", "论文搜索", "文献"],
    "信息检索": ["检索", "retrieval"],
}
METHOD_KEYS = {
    "大模型微调": ["微调", "fine-tun", "指令调优", "instruction tuning", "rft"],
    "强化学习": ["强化学习", "reinforcement", "ppo", "dpo", "rl "],
    "图神经网络": ["图卷", "GNN", "GCN", "图神经", "graph"],
    "混合专家": ["混合专家", "MoE", "expert"],
    "多智能体": ["多智能体", "智能体", "agent", "多代理"],
    "对比学习": ["对比学习", "contrastive", "自监督"],
    "扩散模型": ["扩散", "diffusion"],
}


def classify(title, aid, text=""):
    if aid in OVERRIDE:
        d, sub, tasks, methods = OVERRIDE[aid]
        return dict(domain=d, sub=sub, tasks=list(tasks), methods=list(methods))
    low = title.lower()
    dom, sub = DOMAIN_MISC, ""
    for kws, d, s in RULES:
        if any(k.lower() in low for k in kws):
            dom, sub = d, s
            break
    hay = title.lower()
    tasks = [t for t, kws in TASK_KEYS.items() if any(k.lower() in hay for k in kws)]
    methods = [m for m, kws in METHOD_KEYS.items() if any(k.lower() in hay for k in kws)]
    if dom == DOMAIN_RECSYS and sub and sub not in tasks:
        tasks.insert(0, sub)
    if sub in (SUB_MM, SUB_KG, SUB_AGENT, SUB_RAG, SUB_SCHOLAR) and sub not in tasks:
        tasks.insert(0, sub)
    return dict(domain=dom, sub=sub, tasks=tasks[:3], methods=methods[:3])


def plan():
    ready = json.load(open(os.path.join(TMP, "blog_ready.json"), encoding="utf-8"))
    rows = []
    for r in ready:
        c = classify(r["title"], r["aid"])
        rows.append((r, c))
    order = [DOMAIN_RECSYS, DOMAIN_AI, DOMAIN_GRAPH, DOMAIN_MISC]
    L = ["# A 组 58 篇：三维分类映射（复核用）", ""]
    for d in order:
        rs = [x for x in rows if x[1]["domain"] == d]
        if not rs:
            continue
        L.append(f"## {d}（{len(rs)} 篇）")
        L.append("")
        L.append("| 编号 | 二级 | 任务 | 方法 | 标题 |")
        L.append("|---|---|---|---|---|")
        for r, c in sorted(rs, key=lambda x: (x[1]["sub"], -x[0]["full"])):
            L.append(f"| {r['aid']} | {c['sub'] or '-'} | {'、'.join(c['tasks']) or '-'} | "
                     f"{'、'.join(c['methods']) or '-'} | {r['title'][:38]} |")
        L.append("")
    open(os.path.join(ROOT, "docs", "blog_taxonomy_map.md"), "w", encoding="utf-8",
         newline="\n").write("\n".join(L) + "\n")
    for d in order:
        print(f"  {d}: {len([x for x in rows if x[1]['domain'] == d])}")
    print("-> docs/blog_taxonomy_map.md")


def restamp_posts():
    """按新分类重写已发布文章的 categories / tags（保留其它 front matter 与正文）。"""
    n = 0
    for f in sorted(glob.glob(os.path.join(POSTS, "*.md"))):
        txt = open(f, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        t = re.search(r'^title:\s*"?(.*?)"?\s*$', fm, re.M)
        title = t.group(1) if t else ""
        arx = re.search(r"arxiv\.org/abs/([\w.\-]+)", body) or re.search(r"arXiv[:：]\s*([\w.\-]+)", body)
        aid = arx.group(1) if arx else ""
        c = classify(title, aid, body)
        cats = [c["domain"]] + ([c["sub"]] if c["sub"] else [])
        tags = list(dict.fromkeys(["论文速读"] + c["tasks"] + c["methods"]))
        fm = re.sub(r"^categories:.*$", "categories: [" + ", ".join(cats) + "]", fm, flags=re.M)
        if re.search(r"^tags:.*$", fm, re.M):
            fm = re.sub(r"^tags:.*$", "tags: [" + ", ".join(tags) + "]", fm, flags=re.M)
        else:
            fm += "\ntags: [" + ", ".join(tags) + "]"
        open(f, "w", encoding="utf-8", newline="\n").write("---\n" + fm + "\n---\n" + body)
        n += 1
        print(f"  {os.path.basename(f)[:-3]:44s} -> {' / '.join(cats)}  #{', '.join(tags)}")
    print(f"restamped {n} posts")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--posts", action="store_true")
    a = ap.parse_args()
    if a.plan:
        plan()
    elif a.posts:
        restamp_posts()
    else:
        ap.print_help()
