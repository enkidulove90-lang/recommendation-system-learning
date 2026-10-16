#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成博客发文待办清单：把 data/summaries + data/parsed 与已发布文章做差集。

用法:
    python skills/blog_worklist.py

输出 docs/blog_publish_worklist.md：
  A. 有全文解析稿 + 有配图（可做深度重写，优先）
  B. 有全文但无配图
  C. 无像样解析稿（只能按摘要写）
同时打印统计，并把 A 组落到临时 json 供后续脚本消费。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = r"C:/Users/xu.yan1/enkidu-blog/repo/source/_posts"
MIN_FULL = 20000          # 「像样的解析稿」阈值

TOPIC_RULES = [
    ("多模态", "MM"), ("知识图谱", "KG"), ("生成式", "GEN"),
    ("大语言模型", "LLM"), ("LLM", "LLM"), ("智能体", "AGENT"), ("Agent", "AGENT"),
    ("冷启动", "COLD"), ("对比", "GCL"), ("推荐", "REC"),
]


def topic(title):
    for kw, tag in TOPIC_RULES:
        if kw in title:
            return tag
    return "OTHER"


def published_ids():
    ids = set()
    for f in glob.glob(os.path.join(POSTS, "*.md")):
        t = open(f, encoding="utf-8").read()
        ids |= set(re.findall(r"arxiv\.org/abs/([\w.\-]+)", t))
        ids |= set(re.findall(r"arXiv[:：]\s*([\w.\-]+)", t))
    return ids


def main():
    pub_ids = published_ids()
    rows = {}
    for f in sorted(os.listdir(os.path.join(ROOT, "data", "summaries"))):
        if not f.endswith(".md") or "papers_full" in f:
            continue
        t = open(os.path.join(ROOT, "data", "summaries", f), encoding="utf-8").read()
        m = re.search(r"^\*\*arXiv\s*ID\*\*[:：][ \t]*(\S*)", t, re.M)
        aid = m.group(1).strip() if m else ""
        h = re.search(r"^# (.+)$", t, re.M)
        title = h.group(1).strip() if h else ""
        pdirs = ([d for d in glob.glob(os.path.join(ROOT, "data", "parsed", "*" + aid + "*"))
                  if os.path.isdir(d)] if aid else [])
        full, nimg, name = 0, 0, ""
        for d in pdirs:
            for md in glob.glob(os.path.join(d, "*.md")):
                if os.path.getsize(md) > full:
                    full, name = os.path.getsize(md), os.path.basename(d)
            nimg = max(nimg, len(glob.glob(os.path.join(d, "images", "*"))))
        key = aid or f
        if key not in rows or full > rows[key]["full"]:
            rows[key] = dict(aid=aid, title=title, full=full, nimg=nimg, pdir=name)

    un = [v for k, v in rows.items() if k not in pub_ids]
    ready = sorted([v for v in un if v["full"] >= MIN_FULL and v["nimg"] > 0], key=lambda x: -x["full"])
    noimg = sorted([v for v in un if v["full"] >= MIN_FULL and v["nimg"] == 0], key=lambda x: -x["full"])
    notfull = sorted([v for v in un if v["full"] < MIN_FULL], key=lambda x: -x["full"])

    L = ["# 博客发文待办清单（论文 → 深度重写文章）", "",
         f"- 摘要库去重后条目：**{len(rows)}**",
         f"- 已发布（按 arXiv 编号匹配）：**{len(pub_ids & set(rows))}**",
         f"- 待发布：**{len(un)}** —— 有全文可深度重写 {len(ready) + len(noimg)}"
         f"（有配图 {len(ready)} / 无配图 {len(noimg)}），无像样解析稿 {len(notfull)}", "",
         "## A. 优先：有全文解析稿 + 有配图", "",
         "| # | 主题 | 编号 | 标题 | 全文KB | 图 | 解析目录 |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ready, 1):
        L.append(f"| {i} | {topic(r['title'])} | {r['aid']} | {r['title'][:44]} | "
                 f"{r['full']//1024} | {r['nimg']} | `{r['pdir'][:40]}` |")
    L += ["", "## B. 有全文但无配图", ""]
    for i, r in enumerate(noimg, 1):
        L.append(f"{i}. `{r['aid']}` {r['title']} （{r['full']//1024}KB）")
    L += ["", "## C. 无像样解析稿（只能按摘要写）", ""]
    for i, r in enumerate(notfull, 1):
        L.append(f"{i}. `{r['aid'] or '-'}` {r['title']}")

    out = os.path.join(ROOT, "docs", "blog_publish_worklist.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    json.dump(ready, open(os.path.join(os.environ.get("TEMP", "/tmp"), "blog_ready.json"),
                          "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"待发布 {len(un)} | 有图 {len(ready)} | 无图 {len(noimg)} | 无全文 {len(notfull)}")
    print("written", out)


if __name__ == "__main__":
    main()
