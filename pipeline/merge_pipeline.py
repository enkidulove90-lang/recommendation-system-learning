"""
pipeline/merge_pipeline.py — 文档合并与 Token 控制

收集所有论文的解析全文和摘要，合并为目标 token 大小的测试文档。
支持三种策略:
  1. Full — 保留全文，按论文顺序累积到目标 token 数
  2. Key-Sections — 仅提取关键章节（Introduction, Method, Experiments）
  3. Summary-Only — 仅使用摘要代替全文（最大压缩比）

同时提供超长上下文压缩思路的实现:
  - 层级摘要法: 摘要合集 → 关键论文全文 → 全部全文
  - 滑动窗口切块: 多片段连续输出
  - 重要性加权: 按论文引用/新颖度分配篇幅
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import settings
from utils.token_counter import count_tokens, count_tokens_file, token_size_friendly

logger = logging.getLogger(__name__)


class DocumentMerger:
    """
    论文文档合并器。

    将多篇论文的全文和摘要合并为指定 token 大小的测试文档，
    用于 Coding Agent 上下文窗口压力测试。

    使用示例:
        merger = DocumentMerger()
        merger.merge_all(
            paper_metadata="data/papers_metadata.json",
            target_sizes=[175000, 200000, 225000],
            strategies=["full", "key-sections", "summary-only"],
        )
    """

    def __init__(self, output_dir: str | Path | None = None):
        self._output_dir = Path(output_dir) if output_dir else settings.DATA_DIR / "merged"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def merge_all(
        self,
        target_sizes: list[int] | None = None,
        strategies: list[str] | None = None,
        paper_list: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        主入口：生成所有目标大小 × 所有策略的合并文档。

        参数:
            target_sizes: 目标 token 大小列表，默认 [175000, 200000, 225000]
            strategies:   策略列表，默认 ["full", "key-sections", "summary-only"]
            paper_list:   论文信息列表 [{"arxiv_id": ..., "title": ..., "md_path": ..., "summary_path": ...}]

        返回:
            {
                "generated_files": [{"path": str, "size_tokens": int, "strategy": str, "target": int}, ...],
                "total_tokens_available": int,  # 所有论文总 token 数
                "paper_count": int,
            }
        """
        if target_sizes is None:
            target_sizes = [175_000, 200_000, 225_000]
        if strategies is None:
            strategies = ["full", "key-sections", "summary-only"]

        # 收集论文内容
        if paper_list is None:
            paper_list = self._scan_data_directories()

        if not paper_list:
            logger.error("No papers found for merging.")
            return {"generated_files": [], "total_tokens_available": 0, "paper_count": 0}

        # 加载每篇论文的全文内容和 token 统计
        papers = []
        for p in paper_list:
            paper_info = self._load_paper_content(p)
            if paper_info:
                papers.append(paper_info)

        if not papers:
            logger.error("Failed to load any paper content.")
            return {"generated_files": [], "total_tokens_available": 0, "paper_count": 0}

        total_tokens = sum(p["full_tokens"] for p in papers)
        logger.info(
            "Loaded %d papers | total tokens: %s | avg: %s/paper",
            len(papers),
            token_size_friendly(total_tokens),
            token_size_friendly(total_tokens // len(papers)),
        )

        generated = []
        for strategy in strategies:
            for target in target_sizes:
                result = self._generate_document(papers, target, strategy)
                if result:
                    generated.append(result)

        # 保存报告
        report_path = self._output_dir / f"merge_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_tokens_available": total_tokens,
            "paper_count": len(papers),
            "generated_files": generated,
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Merge report saved -> %s", report_path)

        return report

    def generate_single(
        self,
        target_tokens: int,
        strategy: str = "full",
        paper_list: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """
        生成单个目标大小的合并文档。

        参数:
            target_tokens: 目标 token 数
            strategy:      合并策略
            paper_list:    论文列表

        返回:
            {"path": str, "size_tokens": int, "strategy": str, "target": int} 或 None
        """
        if paper_list is None:
            paper_list = self._scan_data_directories()

        papers = []
        for p in paper_list:
            info = self._load_paper_content(p)
            if info:
                papers.append(info)

        if not papers:
            return None

        return self._generate_document(papers, target_tokens, strategy)

    # ------------------------------------------------------------------
    # 内部: 内容收集
    # ------------------------------------------------------------------

    @staticmethod
    def _scan_data_directories() -> list[dict[str, Any]]:
        """扫描 data/parsed 和 data/summaries 目录，构建论文列表。"""
        parsed_dir = settings.DATA_DIR / "parsed"
        summaries_dir = settings.DATA_DIR / "summaries"
        paper_list: list[dict[str, Any]] = []

        if parsed_dir.exists():
            for item in sorted(parsed_dir.iterdir()):
                if item.is_dir():
                    md_file = item / f"{item.name}.md"
                    json_file = item / f"{item.name}.json"
                    paper_list.append({
                        "arxiv_id": item.name,
                        "md_path": str(md_file) if md_file.exists() else None,
                        "json_path": str(json_file) if json_file.exists() else None,
                        "summary_path": str(summaries_dir / f"{item.name}_summary.md"),
                    })

        return paper_list

    @staticmethod
    def _load_paper_content(paper: dict[str, Any]) -> dict[str, Any] | None:
        """加载单篇论文的全文和摘要。"""
        arxiv_id = paper.get("arxiv_id", "unknown")
        full_text = ""
        summary_text = ""
        title = arxiv_id

        # 读取全文
        md_path = paper.get("md_path")
        if md_path and Path(md_path).exists():
            full_text = Path(md_path).read_text(encoding="utf-8", errors="replace")
            # 尝试提取标题（第一行 # heading）
            for line in full_text.split("\n"):
                stripped = line.strip()
                if stripped.startswith("# ") and len(stripped) > 3:
                    title = stripped[2:].strip()
                    break

        # 读取摘要
        summary_path = paper.get("summary_path")
        if summary_path and Path(summary_path).exists():
            summary_text = Path(summary_path).read_text(encoding="utf-8", errors="replace")

        if not full_text and not summary_text:
            return None

        full_tokens = count_tokens(full_text)
        summary_tokens = count_tokens(summary_text)
        key_sections_text = DocumentMerger._extract_key_sections(full_text)
        key_sections_tokens = count_tokens(key_sections_text)

        return {
            "arxiv_id": arxiv_id,
            "title": title,
            "full_text": full_text,
            "full_tokens": full_tokens,
            "summary_text": summary_text,
            "summary_tokens": summary_tokens,
            "key_sections_text": key_sections_text,
            "key_sections_tokens": key_sections_tokens,
        }

    @staticmethod
    def _extract_key_sections(full_text: str) -> str:
        """
        从论文全文中提取关键章节。

        保留: Introduction, Method/Approach/Framework, Experiments/Results, Conclusion
        去除: Related Work, Background, Appendix, References, Acknowledgements
        """
        if not full_text:
            return ""

        # 用 Markdown 标题分割章节
        sections = re.split(r"\n(?=#{1,3}\s)", full_text)

        keep_keywords = [
            "introduction", "intro",
            "method", "approach", "proposed", "framework", "architecture", "model",
            "experiment", "result", "evaluation", "performance", "analysis",
            "conclusion", "discussion", "summary",
        ]
        drop_keywords = [
            "related work", "background", "preliminar",
            "acknowledgment", "acknowledgement",
            "appendix", "supplement", "reference", "bibliography",
        ]

        kept: list[str] = []
        for sec in sections:
            # 获取章节标题 (第一行)
            first_line = sec.strip().split("\n")[0].lower()
            # 清理 Markdown 标记
            heading = re.sub(r"^#+\s*", "", first_line).strip()

            should_keep = any(kw in heading for kw in keep_keywords)
            should_drop = any(kw in heading for kw in drop_keywords)

            if should_keep and not should_drop:
                kept.append(sec.strip())
            elif not should_drop and not heading:
                # 无标题内容（可能在 document preamble）
                pass
            elif should_drop:
                # 对丢弃的章节添加占位，保持上下文意识
                if len(kept) > 0 and not kept[-1].startswith("[已省略"):
                    kept.append(f"[已省略: {heading}]")

        result = "\n\n".join(kept)
        if not result:
            # 如果什么都没保留，返回原文前 1/3
            result = full_text[:len(full_text) // 3]

        return result

    # ------------------------------------------------------------------
    # 内部: 文档生成
    # ------------------------------------------------------------------

    def _generate_document(
        self,
        papers: list[dict[str, Any]],
        target_tokens: int,
        strategy: str,
    ) -> dict[str, Any] | None:
        """
        生成单个合并文档。

        策略:
          - "full":          使用每篇论文的全文
          - "key-sections":  使用每篇论文的关键章节提取
          - "summary-only":  仅使用 DeepSeek 生成的摘要
          - "hybrid":        混合策略 — 核心论文全文 + 其余论文摘要
        """
        logger.info(
            "Generating document | target=%s strategy=%s papers=%d",
            token_size_friendly(target_tokens), strategy, len(papers),
        )

        # 按 token 消耗排序（从小到大），确保先填小论文
        if strategy == "full":
            sorted_papers = sorted(papers, key=lambda p: p["full_tokens"])
        elif strategy == "key-sections":
            sorted_papers = sorted(papers, key=lambda p: p["key_sections_tokens"])
        elif strategy == "summary-only":
            sorted_papers = sorted(papers, key=lambda p: p["summary_tokens"])
        elif strategy == "hybrid":
            sorted_papers = sorted(
                papers,
                key=lambda p: (p["full_tokens"] if p["full_tokens"] < 15000 else p["summary_tokens"]),
            )
        else:
            logger.error("Unknown strategy: %s", strategy)
            return None

        # 构建文档内容
        doc_sections: list[str] = []
        total = 0
        paper_count = 0
        truncated_count = 0

        header = self._build_header(strategy, target_tokens, len(papers))
        header_tokens = count_tokens(header)
        total += header_tokens
        doc_sections.append(header)

        toc_lines: list[str] = []

        for paper in sorted_papers:
            if total >= target_tokens:
                break

            aid = paper["arxiv_id"]
            title = paper.get("title", aid)

            if strategy == "full":
                text = paper["full_text"]
            elif strategy == "key-sections":
                text = paper["key_sections_text"]
            elif strategy == "summary-only":
                text = paper["summary_text"] or paper["key_sections_text"]
            elif strategy == "hybrid":
                # 混合: 全文 < 15k token 的保留全文，否则用摘要
                if paper["full_tokens"] < 15000:
                    text = paper["full_text"]
                else:
                    text = paper["summary_text"] or paper["key_sections_text"]
            else:
                text = ""

            text_tokens = count_tokens(text)
            remaining = target_tokens - total

            if text_tokens <= 0:
                continue

            if text_tokens <= remaining:
                # 完整放入
                section = self._wrap_paper_section(aid, title, text, strategy)
                section_tokens = count_tokens(section)
            else:
                # 需要截断
                truncated_count += 1
                trunc_ratio = max(0.5, remaining / text_tokens)
                trunc_chars = int(len(text) * trunc_ratio)
                truncated_text = text[:trunc_chars] + "\n\n[... 内容因 Token 限制已截断 ...]"
                section = self._wrap_paper_section(aid, title, truncated_text, strategy)
                section_tokens = count_tokens(section)

            if total + section_tokens > target_tokens and paper_count > 0:
                # 放不下，跳过此论文
                continue

            doc_sections.append(section)
            total += section_tokens
            paper_count += 1

            toc_lines.append(
                f"{paper_count}. **{title}** ({aid}) — "
                f"{token_size_friendly(count_tokens(text))} tokens [{strategy}]"
            )

        # 更新目录
        toc_text = "\n".join(toc_lines) if toc_lines else "(无论文)"
        doc_sections[0] = header.replace("<!--TOC_PLACEHOLDER-->", toc_text)

        # 添加 footer 和统计信息
        footer = self._build_footer(paper_count, truncated_count, total, target_tokens, strategy)
        doc_sections.append(footer)
        total = count_tokens("\n\n".join(doc_sections))

        # 写入文件
        filename = f"papers_{strategy}_{token_size_friendly(target_tokens)}.md"
        filepath = self._output_dir / filename
        full_content = "\n\n---\n\n".join(doc_sections)
        filepath.write_text(full_content, encoding="utf-8")

        logger.info(
            "Generated: %s | papers=%d truncated=%d tokens=%s/%s (%.1f%%)",
            filename, paper_count, truncated_count,
            token_size_friendly(total), token_size_friendly(target_tokens),
            100 * total / max(1, target_tokens),
        )

        return {
            "path": str(filepath),
            "size_tokens": total,
            "size_chars": len(full_content),
            "strategy": strategy,
            "target": target_tokens,
            "paper_count": paper_count,
            "truncated_count": truncated_count,
            "generated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def _wrap_paper_section(arxiv_id: str, title: str, text: str, strategy: str) -> str:
        """将单篇论文的内容包装为一个 Markdown 章节。"""
        strategy_labels = {
            "full": "📄 全文",
            "key-sections": "📑 关键章节",
            "summary-only": "📝 摘要",
            "hybrid": "📋 混合",
        }
        label = strategy_labels.get(strategy, "📄")

        return f"""## {label} | {title}

**arXiv ID**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})

{text}
"""

    @staticmethod
    def _build_header(strategy: str, target_tokens: int, total_papers: int) -> str:
        """构建文档头部。"""
        strategy_desc = {
            "full": "全文模式 — 保留每篇论文的完整解析内容",
            "key-sections": "关键章节模式 — 仅保留 Introduction, Method, Experiments, Conclusion",
            "summary-only": "摘要模式 — 仅包含 DeepSeek 生成的论文深度解读",
            "hybrid": "混合模式 — 短论文保留全文，长论文使用摘要",
        }

        return f"""# 推荐系统前沿论文集 — 合并文档

> **生成策略**: {strategy_desc.get(strategy, strategy)}
> **目标大小**: {token_size_friendly(target_tokens)} tokens
> **论文总数**: {total_papers} 篇
> **生成时间**: {datetime.now().isoformat()}

---

## 目录

<!--TOC_PLACEHOLDER-->

---

"""

    @staticmethod
    def _build_footer(
        paper_count: int,
        truncated_count: int,
        actual_tokens: int,
        target_tokens: int,
        strategy: str,
    ) -> str:
        """构建文档尾部统计。"""
        return f"""---

## 📊 文档统计

| 指标 | 值 |
|------|-----|
| 收录论文数 | {paper_count} |
| 截断论文数 | {truncated_count} |
| 实际 Token 数 | {token_size_friendly(actual_tokens)} |
| 目标 Token 数 | {token_size_friendly(target_tokens)} |
| 达成率 | {100 * actual_tokens / max(1, target_tokens):.1f}% |
| 合并策略 | {strategy} |
| 生成时间 | {datetime.now().isoformat()} |

---

> 本文档由 `DocumentMerger` 自动生成，用于 Coding Agent 上下文窗口压力测试。
"""

    # ------------------------------------------------------------------
    # 超长上下文压缩思路实现
    # ------------------------------------------------------------------

    def generate_sliding_windows(
        self,
        target_tokens: int = 200_000,
        overlap_tokens: int = 20_000,
        paper_list: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        滑动窗口法: 将论文集按固定窗口切分为多个重叠片段。

        适用于: 模拟 Agent 处理长上下文时的分块策略测试。

        参数:
            target_tokens:  每个窗口的 token 数
            overlap_tokens: 窗口间重叠的 token 数
            paper_list:     论文列表

        返回:
            [{path, size_tokens, window_index}, ...]
        """
        if paper_list is None:
            paper_list = self._scan_data_directories()

        papers = []
        for p in paper_list:
            info = self._load_paper_content(p)
            if info:
                papers.append(info)

        if not papers:
            return []

        # 构建统一的全文流
        all_text = ""
        for paper in papers:
            all_text += f"\n\n## {paper['title']}\n\n{paper['full_text']}"

        total_tokens = count_tokens(all_text)
        step = target_tokens - overlap_tokens
        windows: list[dict[str, Any]] = []

        for i, start in enumerate(range(0, total_tokens, step)):
            # 计算窗口范围
            window_start = max(0, start)
            window_end = min(total_tokens, start + target_tokens)

            # 估算字符范围
            char_ratio = len(all_text) / max(1, total_tokens)
            char_start = int(window_start * char_ratio)
            char_end = int(window_end * char_ratio)

            window_text = all_text[char_start:char_end]
            window_tokens = count_tokens(window_text)

            filename = f"sliding_window_{i+1:03d}_{token_size_friendly(window_tokens)}.md"
            filepath = self._output_dir / filename
            filepath.write_text(window_text, encoding="utf-8")

            windows.append({
                "path": str(filepath),
                "size_tokens": window_tokens,
                "window_index": i + 1,
                "token_range": f"{window_start}-{window_end}",
            })

            logger.info("Sliding window %d: %s tokens", i + 1, token_size_friendly(window_tokens))

        return windows

    def generate_hierarchical(
        self,
        target_tokens: int = 200_000,
        paper_list: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        层级摘要法: 生成三层文档结构。

        Level 1 — 摘要合集（全摘要，最小体积）
        Level 2 — 混合版（核心论文全文 + 其余摘要）
        Level 3 — 全文版（尽可能多论文的全文）

        适用于: 测试 Agent 在不同信息密度下的表现。
        """
        if paper_list is None:
            paper_list = self._scan_data_directories()

        papers = []
        for p in paper_list:
            info = self._load_paper_content(p)
            if info:
                papers.append(info)

        if not papers:
            return []

        results = []

        # Level 1: 全摘要版
        result = self._generate_document(papers, target_tokens, "summary-only")
        if result:
            result["level"] = 1
            result["level_name"] = "摘要合集"
            results.append(result)

        # Level 2: 混合版
        result = self._generate_document(papers, target_tokens, "hybrid")
        if result:
            result["level"] = 2
            result["level_name"] = "混合版"
            results.append(result)

        # Level 3: 全文版
        result = self._generate_document(papers, target_tokens, "full")
        if result:
            result["level"] = 3
            result["level_name"] = "全文版"
            results.append(result)

        return results
