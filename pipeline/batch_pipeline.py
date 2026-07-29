#!/usr/bin/env python3
"""
pipeline/batch_pipeline.py — 批量论文处理脚本

端到端流程:
  1. 从 papers_metadata.json 读取论文列表
  2. 下载 PDF -> data/papers/
  3. MinerU 解析 -> data/parsed/
  4. DeepSeek 摘要 -> data/summaries/
  5. 文档合并 -> data/merged/

特性:
  - 支持断点续传（已处理的论文自动跳过）
  - 错误隔离（单篇失败不影响其他论文）
  - 实时进度保存
  - 最终生成三份目标 token 数的测试文档

用法:
  python pipeline/batch_pipeline.py [--skip-download] [--skip-parse] [--skip-summarize] [--skip-merge]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from config import settings
from utils.helpers import setup_logging
from skills.pdf_downloader import PDFDownloader
from skills.pdf_parser import PDFParser
from skills.deepseek_summarizer import DeepSeekSummarizer
from pipeline.merge_pipeline import DocumentMerger
from storage.paper_assets import find_parsed_markdown

logger = logging.getLogger(__name__)


class BatchPipeline:
    """批量论文处理流水线。"""

    def __init__(self) -> None:
        self._metadata_path = settings.DATA_DIR / "papers_metadata.json"
        self._state_path = settings.DATA_DIR / "pipeline_state.json"
        self._downloader = PDFDownloader()
        self._parser = PDFParser()
        self._summarizer = DeepSeekSummarizer()
        self._merger = DocumentMerger()

        # 加载论文列表和状态
        self._papers: list[dict[str, Any]] = []
        self._state: dict[str, Any] = {}
        self._load_metadata()
        self._load_state()

    # ==================================================================
    # 公共入口
    # ==================================================================

    def run(
        self,
        skip_download: bool = False,
        skip_parse: bool = False,
        skip_summarize: bool = False,
        skip_merge: bool = False,
    ) -> None:
        """执行完整的批量流水线。"""
        print("=" * 60)
        print("  Batch Paper Processing Pipeline")
        print(f"  Papers: {len(self._papers)}")
        print(f"  MinerU: {'ready' if self._parser.is_ready else 'NOT CONFIGURED'}")
        print(f"  DeepSeek: {'ready' if self._summarizer.is_ready else 'NOT CONFIGURED'}")
        print("=" * 60)

        if not self._papers:
            print("ERROR: No papers found in metadata. Run crawl first.")
            return

        # Step 1: Download PDFs
        if not skip_download:
            self._step_download()
        else:
            print("\n[SKIP] PDF download")

        # Step 2: Parse PDFs
        if not skip_parse:
            self._step_parse()
        else:
            print("\n[SKIP] PDF parsing")

        # Step 3: Generate summaries
        if not skip_summarize:
            self._step_summarize()
        else:
            print("\n[SKIP] Summarization")

        # Step 4: Merge documents
        if not skip_merge:
            self._step_merge()
        else:
            print("\n[SKIP] Document merge")

        print("\n" + "=" * 60)
        print("  Pipeline Complete!")
        self._print_stats()
        print("=" * 60)

    # ==================================================================
    # Step 实现
    # ==================================================================

    def _step_download(self) -> None:
        """Step 1: Download all PDFs. Skip if already downloaded."""
        print(f"\n{'='*40}")
        print("  [1/4] Downloading PDFs")
        print(f"{'='*40}")

        for i, paper in enumerate(self._papers, 1):
            aid = paper.get("arxiv_id", "")
            if not aid:
                continue

            # 检查是否已下载
            if paper.get("local_pdf_path") and Path(paper["local_pdf_path"]).exists():
                print(f"  [{i}/{len(self._papers)}] {aid}: Already downloaded")
                self._mark_step_done(aid, "download")
                continue

            print(f"  [{i}/{len(self._papers)}] {aid}: Downloading...")
            result = self._downloader.execute(arxiv_id=aid)

            if result["error"]:
                print(f"    ERROR: {result['error']}")
                self._mark_step_error(aid, "download", result["error"])
            else:
                paper["local_pdf_path"] = result["pdf_path"]
                paper["file_size"] = result["file_size"]
                print(f"    OK ({result['file_size']} bytes)")
                self._mark_step_done(aid, "download")

            self._save_metadata()
            time.sleep(1.0)  # Rate limiting

    def _step_parse(self) -> None:
        """Step 2: Parse PDFs with MinerU. Skip if already parsed."""
        if not self._parser.is_ready:
            print("\n[SKIP] MinerU not configured, skipping parse step.")
            return

        print(f"\n{'='*40}")
        print("  [2/4] Parsing PDFs with MinerU")
        print(f"{'='*40}")

        for i, paper in enumerate(self._papers, 1):
            aid = paper.get("arxiv_id", "")
            if not aid:
                continue

            # 检查是否已解析
            md_path = find_parsed_markdown(aid)
            if md_path is not None:
                paper["local_md_path"] = str(md_path)
                print(f"  [{i}/{len(self._papers)}] {aid}: Already parsed")
                self._mark_step_done(aid, "parse")
                self._save_metadata()
                continue

            # 检查是否有 PDF
            pdf_path = paper.get("local_pdf_path", "")
            if not pdf_path or not Path(pdf_path).exists():
                print(f"  [{i}/{len(self._papers)}] {aid}: PDF not found, skipping")
                continue

            print(f"  [{i}/{len(self._papers)}] {aid}: Parsing...")
            result = self._parser.execute(
                pdf_url=paper.get("pdf_url", f"https://arxiv.org/pdf/{aid}"),
                arxiv_id=aid,
                title=paper.get("chinese_title") or paper.get("title", ""),
            )

            if result["error"]:
                print(f"    ERROR: {result['error']}")
                self._mark_step_error(aid, "parse", result["error"])
            else:
                paper["local_md_path"] = result.get("markdown_path")
                paper["local_json_path"] = result.get("json_path")
                text_len = len(result.get("content", {}).get("text", ""))
                print(f"    OK ({text_len} chars)")
                self._mark_step_done(aid, "parse")

            self._save_metadata()
            time.sleep(1.0)  # Rate limiting

    def _step_summarize(self) -> None:
        """Step 3: Generate summaries with DeepSeek. Skip if already done."""
        if not self._summarizer.is_ready:
            print("\n[SKIP] DeepSeek not configured, skipping summarize step.")
            return

        print(f"\n{'='*40}")
        print("  [3/4] Generating Summaries with DeepSeek")
        print(f"{'='*40}")

        for i, paper in enumerate(self._papers, 1):
            aid = paper.get("arxiv_id", "")
            if not aid:
                continue

            # 检查是否已生成
            summary_path = settings.DATA_DIR / "summaries" / f"{aid}_summary.md"
            if summary_path.exists():
                paper["local_summary_path"] = str(summary_path)
                print(f"  [{i}/{len(self._papers)}] {aid}: Already summarized")
                self._mark_step_done(aid, "summarize")
                self._save_metadata()
                continue

            # 读取全文
            md_path = paper.get("local_md_path", "")
            if not md_path:
                resolved_md = find_parsed_markdown(aid)
                md_path = str(resolved_md) if resolved_md is not None else ""

            full_text = ""
            if md_path and Path(md_path).exists():
                full_text = Path(md_path).read_text(encoding="utf-8", errors="replace")

            if not full_text:
                # 只有摘要时，仍然可以生成
                full_text = paper.get("abstract", "")

            print(f"  [{i}/{len(self._papers)}] {aid}: Summarizing... ({len(full_text)} chars)")

            result = self._summarizer.execute(
                arxiv_id=aid,
                title=paper.get("title", ""),
                abstract=paper.get("abstract", ""),
                full_text=full_text,
            )

            if result["error"]:
                print(f"    ERROR: {result['error']}")
                self._mark_step_error(aid, "summarize", result["error"])
            else:
                paper["local_summary_path"] = result.get("summary_path")
                summary = result.get("summary", {})
                main_contrib = summary.get("main_contribution", "")[:80]
                print(f"    OK — {main_contrib}...")
                self._mark_step_done(aid, "summarize")

            self._save_metadata()
            time.sleep(1.0)  # Rate limiting

    def _step_merge(self) -> None:
        """Step 4: Merge all parsed papers into target-sized documents."""
        print(f"\n{'='*40}")
        print("  [4/4] Merging Documents")
        print(f"{'='*40}")

        # 构建 paper list for merger
        paper_list = []
        for paper in self._papers:
            aid = paper.get("arxiv_id", "")
            resolved_md = find_parsed_markdown(aid)
            md_path = paper.get("local_md_path") or (str(resolved_md) if resolved_md else "")
            summary_path = paper.get("local_summary_path") or str(settings.DATA_DIR / "summaries" / f"{aid}_summary.md")

            paper_list.append({
                "arxiv_id": aid,
                "md_path": md_path,
                "summary_path": summary_path,
            })

        # 生成标准三份文档
        report = self._merger.merge_all(
            target_sizes=[175_000, 200_000, 225_000],
            strategies=["full", "key-sections", "summary-only"],
            paper_list=paper_list,
        )

        print(f"\n  Generated {len(report.get('generated_files', []))} merged documents:")
        for f in report.get("generated_files", []):
            print(f"    {Path(f['path']).name}: {f['size_tokens']} tokens [{f['strategy']}]")

        # 额外生成层次版和滑动窗口版
        print("\n  Generating hierarchical versions...")
        self._merger.generate_hierarchical(target_tokens=200_000, paper_list=paper_list)

        print("  Generating sliding window versions...")
        self._merger.generate_sliding_windows(target_tokens=200_000, paper_list=paper_list)

    # ==================================================================
    # 状态管理
    # ==================================================================

    def _load_metadata(self) -> None:
        """加载论文元数据。"""
        if self._metadata_path.exists():
            self._papers = json.loads(self._metadata_path.read_text(encoding="utf-8"))
            logger.info("Loaded %d papers from metadata.", len(self._papers))
        else:
            logger.warning("No papers_metadata.json found at %s", self._metadata_path)

    def _save_metadata(self) -> None:
        """保存更新后的元数据。"""
        self._metadata_path.write_text(
            json.dumps(self._papers, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_state(self) -> None:
        """加载流水线状态。"""
        if self._state_path.exists():
            self._state = json.loads(self._state_path.read_text(encoding="utf-8"))
        else:
            self._state = {
                "started_at": datetime.now().isoformat(),
                "completed_steps": {},
                "errors": {},
            }

    def _save_state(self) -> None:
        """保存流水线状态。"""
        self._state["updated_at"] = datetime.now().isoformat()
        self._state_path.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _mark_step_done(self, arxiv_id: str, step: str) -> None:
        """标记某步骤已完成。"""
        self._state.setdefault("completed_steps", {}).setdefault(arxiv_id, {})[step] = {
            "status": "done",
            "timestamp": datetime.now().isoformat(),
        }
        self._save_state()

    def _mark_step_error(self, arxiv_id: str, step: str, error: str) -> None:
        """记录步骤错误。"""
        self._state.setdefault("errors", {}).setdefault(arxiv_id, {})[step] = {
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_state()

    def _print_stats(self) -> None:
        """打印流水线统计。"""
        downloads = sum(
            1 for p in self._papers
            if p.get("local_pdf_path") and Path(p["local_pdf_path"]).exists()
        )
        parsed = sum(
            1 for p in self._papers
            if p.get("local_md_path") and Path(p["local_md_path"]).exists()
        )
        summarized = sum(
            1 for p in self._papers
            if p.get("local_summary_path") and Path(p["local_summary_path"]).exists()
        )
        print(f"\n  Papers total: {len(self._papers)}")
        print(f"  Downloaded:   {downloads}")
        print(f"  Parsed:       {parsed}")
        print(f"  Summarized:   {summarized}")
        print(f"  Output dir:   {settings.OUTPUT_DIR}")
        print(f"  Data dir:     {settings.DATA_DIR}")


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="Batch Paper Processing Pipeline")
    parser.add_argument("--skip-download", action="store_true", help="Skip PDF download step")
    parser.add_argument("--skip-parse", action="store_true", help="Skip MinerU parsing step")
    parser.add_argument("--skip-summarize", action="store_true", help="Skip DeepSeek summarization step")
    parser.add_argument("--skip-merge", action="store_true", help="Skip document merging step")
    args = parser.parse_args()

    pipeline = BatchPipeline()
    pipeline.run(
        skip_download=args.skip_download,
        skip_parse=args.skip_parse,
        skip_summarize=args.skip_summarize,
        skip_merge=args.skip_merge,
    )


if __name__ == "__main__":
    main()
