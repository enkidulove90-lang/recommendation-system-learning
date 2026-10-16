#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""摘要库编号体检：核对每篇摘要记录的 arXiv 编号与真实论文标题是否一致。

背景：曾发现两条摘要是凭空生成的（编号指向数学论文 / Wi-Fi 检测论文，
而记录的标题根本查不到对应论文）。这个脚本用 arXiv API 批量比对
「记录标题 ↔ 编号的真实标题」，把挂错的揪出来。

用法:
    python skills/audit_summary_ids.py [摘要目录] [报告输出路径]

判定分级：
    ✅ 一致        相似度 >= 0.75
    ⚠️ 略有差异    0.45 ~ 0.75（可能是副标题/版本差异，建议人工看一眼）
    ❌ 严重不符    < 0.45（基本可以确定编号挂错）
    ❓ 查无此文    编号在 arXiv 上不存在
    ⏭ 非 arXiv     编号是 DOI / ACM DL / 期刊号，需另行人工核
    🔍 需人工核对   记录里没有英文标题，无法自动比对（附 arXiv 真实标题供判断）
"""
import argparse
import difflib
import glob
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "recsys-summary-audit/1.0"}
NS = {"a": "http://www.w3.org/2005/Atom"}
ARXIV_NEW = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
ARXIV_OLD = re.compile(r"^[a-z\-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$")


def norm(s):
    """标题归一化：小写、去标点、压空白。"""
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", " ", s.lower())
    return " ".join(s.split())


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def scan(sumdir):
    """扫摘要目录，按 arXiv 编号聚合成一条记录（重复文件取信息最全的）。"""
    recs = {}
    for f in sorted(glob.glob(os.path.join(sumdir, "*.md"))):
        name = os.path.basename(f)
        if "papers_full" in name:
            continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        head = t[:1500]
        m = re.search(r"\*\*(?:arXiv\s*ID|arXiv)\*\*[:：][ \t]*(\S*)", head)
        aid = (m.group(1).strip() if m else "")
        # 注意：[:：] 后面只能用 [ \t]*，不能用 \s*——否则整行为空时 \s* 会吃掉换行、
        # 把下一行的内容当成“英文标题”（踩过，会造出假阳性）
        m2 = re.search(r"\*\*英文标题\*\*[:：][ \t]*(.+)", head)
        en = (m2.group(1).strip() if m2 else "")
        m3 = re.search(r"^#\s+(.+)$", t, re.M)
        zh = (m3.group(1).strip() if m3 else "")
        key = aid or ("__noid__" + zh)
        cur = recs.get(key)
        if cur is None or (not cur["en"] and en):
            recs[key] = {"id": aid, "en": en, "zh": zh, "file": name}
    return recs


def fetch_arxiv(ids, _unused=None):
    """取 arXiv 真实标题；返回 {id(base): title}。

    arXiv API 限流很严（连发几次就 429）：按 URL 长度切块、块间 sleep，
    并对 429 做指数退避重试。
    """
    got = {}
    # 按 URL 长度分块（id_list 太长会被拒）
    chunks, cur = [], []
    for i in ids:
        if len(",".join(cur + [i])) > 1200 and cur:
            chunks.append(cur)
            cur = []
        cur.append(i)
    if cur:
        chunks.append(cur)

    for ci, chunk in enumerate(chunks):
        url = ("https://export.arxiv.org/api/query?id_list=" + ",".join(chunk)
               + f"&max_results={len(chunk) * 2}")
        for attempt in range(4):
            try:
                root = ET.fromstring(urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=60).read())
                n = 0
                for e in root.findall("a:entry", NS):
                    rid = e.find("a:id", NS).text.rsplit("/", 1)[-1]
                    got[re.sub(r"v\d+$", "", rid)] = " ".join(e.find("a:title", NS).text.split())
                    n += 1
                print(f"  批次 {ci + 1}/{len(chunks)}：{len(chunk)} 个编号 → 命中 {n}")
                break
            except Exception as e:
                wait = 8 * (attempt + 1)
                print(f"  ! 批次 {ci + 1} 第 {attempt + 1} 次失败（{e}），{wait}s 后重试",
                      file=sys.stderr)
                time.sleep(wait)
        time.sleep(4)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sumdir", nargs="?", default="data/summaries")
    ap.add_argument("--out", default="docs/summary_library_id_audit.md")
    args = ap.parse_args()

    recs = scan(args.sumdir)
    arxiv_ids = sorted({r["id"] for r in recs.values() if ARXIV_NEW.match(r["id"] or "")
                        or ARXIV_OLD.match(r["id"] or "")})
    print(f"摘要条目 {len(recs)} 条，其中 arXiv 编号 {len(arxiv_ids)} 个，开始核对…")
    real = fetch_arxiv(arxiv_ids)

    buckets = {"ok": [], "near": [], "bad": [], "missing": [], "other": [], "manual": []}
    for r in recs.values():
        aid = r["id"] or ""
        if not aid:
            buckets["other"].append((r, "未填写编号", ""))
        elif not (ARXIV_NEW.match(aid) or ARXIV_OLD.match(aid)):
            buckets["other"].append((r, "编号非 arXiv 格式", ""))
        else:
            base = re.sub(r"v\d+$", "", aid)
            title = real.get(base)
            if not title:
                buckets["missing"].append((r, "编号在 arXiv 查无此文", ""))
            elif not r["en"]:
                buckets["manual"].append((r, f"arXiv 实际标题: {title}", ""))
            else:
                s = sim(r["en"], title)
                if s >= 0.75:
                    buckets["ok"].append((r, title, s))
                elif s >= 0.45:
                    buckets["near"].append((r, title, s))
                else:
                    buckets["bad"].append((r, title, s))

    lines = ["# 摘要库编号体检报告", "",
             f"- 扫描目录：`{args.sumdir}`",
             f"- 摘要条目：{len(recs)} 条（按编号去重后），其中 arXiv 编号 {len(arxiv_ids)} 个",
             f"- 结论：✅一致 {len(buckets['ok'])} / ⚠️略有差异 {len(buckets['near'])} / "
             f"❌严重不符 {len(buckets['bad'])} / ❓查无此文 {len(buckets['missing'])} / "
             f"⏭非 arXiv {len(buckets['other'])} / 🔍需人工核对 {len(buckets['manual'])}",
             ""]
    order = [("bad", "❌ 严重不符（基本可判定编号挂错，优先处理）"),
             ("missing", "❓ 编号在 arXiv 查无此文"),
             ("near", "⚠️ 标题略有差异（看是否是副标题/版本差异）"),
             ("manual", "🔍 缺英文标题，需人工核对（附 arXiv 实际标题）"),
             ("other", "⏭ 非 arXiv 编号（DOI / 期刊 / 会议，需另行核对）"),
             ("ok", "✅ 一致")]
    for key, head in order:
        rows = buckets[key]
        if not rows:
            continue
        lines += [f"## {head}（{len(rows)}）", ""]
        if key in ("bad", "near"):
            lines += ["| 摘要文件 | 记录标题 | arXiv 真实标题 | 相似度 |", "|---|---|---|---|"]
            for r, t, s in rows:
                lines.append(f"| `{r['file']}` | {r['en'][:70]} | {t[:70]} | {s:.2f} |")
        else:
            lines += ["| 摘要文件 | 编号 | 说明 |", "|---|---|---|"]
            for r, why, _ in rows:
                lines.append(f"| `{r['file']}` | `{r['id'] or '-'}` | {why[:100]} |")
        lines.append("")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n报告已写出: {args.out}")
    for key, head in order:
        print(f"  {head.split('（')[0]}: {len(buckets[key])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
