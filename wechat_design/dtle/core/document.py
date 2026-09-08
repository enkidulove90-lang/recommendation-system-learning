"""Markdown → Document 轻量解析（实现 recsys-blue 主题的 Markdown→组件映射规则）。

映射（来自 wechat_design/themes/theme-recsys-blue.md）：
  # 标题        → hook_title
  ## 标题       → section_header
  > 引用金句     → one_liner
  **短语**/==短语== → body_para 内关键词下划线
  | 表格 |      → rr_table
  ![说明](url)  → figure
  数字对比段     → kpi_cards（解析 "值 标签" 对）
  结尾互动句     → cta
  参考链接       → references
"""
from __future__ import annotations

import re
from typing import List

from .types import Block, Document

_BOLD = re.compile(r"\*\*(.+?)\*\*|==(.+?)==")
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
_IMG = re.compile(r"!\[([^\]]*)\]\((https?://[^)]+)\)")
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_KPI_PAIR = re.compile(r"([+\-]?\d+(?:\.\d+)?%?)\s*[—\-:：]?\s*(.+)")


def _extract_keywords(text: str) -> List[str]:
    return [_m.group(1) or _m.group(2) for _m in _BOLD.finditer(text)]


def _strip_bold(text: str) -> str:
    return _BOLD.sub(lambda m: m.group(1) or m.group(2), text)


def parse_markdown(md: str, title: str = "", theme: str = "recsys-blue") -> Document:
    lines = md.splitlines()
    doc = Document(title=title, theme=theme)
    i, n = 0, len(lines)
    pending_para: List[str] = []

    def flush_para():
        if pending_para:
            text = " ".join(pending_para).strip()
            if text:
                doc.add("body_para", text=_strip_bold(text),
                        keywords=_extract_keywords(text))
            pending_para.clear()

    while i < n:
        line = lines[i]
        raw = line.strip()

        # 标题
        if raw.startswith("# ") and not raw.startswith("##"):
            flush_para()
            doc.add("hook_title", title=raw[2:].strip())
            i += 1
            continue
        if raw.startswith("## "):
            flush_para()
            doc.add("section_header", text=raw[3:].strip())
            i += 1
            continue

        # 引用 → one_liner
        if raw.startswith("> "):
            flush_para()
            doc.add("one_liner", text=raw[2:].strip())
            i += 1
            continue

        # 图片 → figure
        m = _IMG.match(raw)
        if m:
            flush_para()
            doc.add("figure", src=m.group(2), caption=m.group(1))
            i += 1
            continue

        # 表格
        if _TABLE_ROW.match(raw) and i + 1 < n and _TABLE_ROW.match(lines[i + 1]) \
                and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            flush_para()
            headers = [c.strip() for c in raw.strip().strip("|").split("|")]
            rows = []
            i += 2  # 跳过分隔行
            while i < n and _TABLE_ROW.match(lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            doc.add("rr_table", headers=headers, rows=rows)
            continue

        # 列表 → 尝试 KPI，否则普通段
        if re.match(r"^[-*]\s+", raw):
            flush_para()
            item = re.sub(r"^[-*]\s+", "", raw)
            km = _KPI_PAIR.match(item)
            if km and re.search(r"\d", item):
                # 简单启发：出现数字则视为 KPI 候选，累积后续列表项
                kpis = [km]
                j = i + 1
                while j < n and re.match(r"^[-*]\s+", lines[j].strip()):
                    ni = re.sub(r"^[-*]\s+", "", lines[j].strip())
                    nm = _KPI_PAIR.match(ni)
                    if nm:
                        kpis.append(nm)
                    j += 1
                doc.add("kpi_cards", items=[{"value": k.group(1), "label": k.group(2).strip()}
                                            for k in kpis])
                i = j
                continue
            else:
                doc.add("body_para", text=_strip_bold(item),
                        keywords=_extract_keywords(item))
                i += 1
                continue

        # 空行
        if not raw:
            flush_para()
            i += 1
            continue

        # 普通段累积
        pending_para.append(raw)
        i += 1

    flush_para()
    return doc


def parse_markdown_file(path: str, theme: str = "recsys-blue") -> Document:
    with open(path, encoding="utf-8") as f:
        return parse_markdown(f.read(), theme=theme)
