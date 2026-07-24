#!/usr/bin/env python3
"""
main.py — arXiv 推荐系统论文爬取与解析工具 CLI 入口

功能流水线:
  爬取 → PDF下载 → MinerU解析 → DeepSeek摘要 → 文档合并

用法:
  # 列出技能和主题
  python main.py list

  # 爬取所有主题
  python main.py crawl-all

  # 爬取单个主题（含 PDF 下载）
  python main.py crawl --topic agent-recommendation --max 10 --download-pdf

  # 自定义搜索
  python main.py search --query 'all:"recommendation system" AND cat:cs.IR' --max 20

  # 下载单篇论文 PDF
  python main.py download --arxiv-id 2602.21756

  # 解析单篇论文 PDF（MinerU）
  python main.py parse --arxiv-id 2602.21756

  # 生成单篇论文摘要（DeepSeek）
  python main.py summarize --arxiv-id 2602.21756

  # 合并文档
  python main.py merge --target 200000

  # 端到端流水线（单个论文测试）
  python main.py pipeline --arxiv-id 2602.21756

  # 批量端到端流水线
  python main.py pipeline-all --topics all --max-per-topic 5
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from config import settings
from utils.helpers import setup_logging
from skills.base_module import get_skill, list_registered_skills
from skills.pdf_parser import PDFParser
from skills.pdf_downloader import PDFDownloader
from skills.deepseek_summarizer import DeepSeekSummarizer
from crawler.arxiv_crawler import ArxivCrawler
from pipeline.merge_pipeline import DocumentMerger


# ======================================================================
# 命令实现
# ======================================================================

def cmd_list() -> None:
    """列出所有已注册的技能和搜索主题。"""
    print("=" * 50)
    print("  Registered Skills")
    print("=" * 50)
    for name in list_registered_skills():
        print(f"  - {name}")

    print("\n" + "=" * 50)
    print("  Search Topics (6 directions)")
    print("=" * 50)
    for name, query in settings.SEARCH_TOPICS.items():
        print(f"\n  [{name}]")
        print(f"    query: {query}")

    print("\n" + "=" * 50)
    print("  Extra Search Queries")
    print("=" * 50)
    for item in settings.EXTRA_SEARCH_QUERIES:
        print(f"\n  [{item['name']}] {item['description']}")
        print(f"    query: {item['query']}")


def cmd_crawl_all() -> None:
    """爬取所有预定义主题。"""
    print("=" * 60)
    print("  arXiv Recommendation System Paper Crawler")
    print(f"  Start Year: {settings.START_YEAR}")
    print(f"  Output Dir: {settings.OUTPUT_DIR}")
    print("=" * 60)

    crawler = ArxivCrawler()
    results = crawler.run_all_topics()

    print("\nDone! Summary:")
    for topic, info in results.items():
        if "error" in info:
            print(f"  [{topic}] ERROR: {info['error']}")
        else:
            print(f"  [{topic}] {info.get('total', 0)} papers")


def cmd_crawl_topic(topic: str, max_results: int, download_pdf: bool, parse_pdf: bool) -> None:
    """爬取单个主题。"""
    crawler = ArxivCrawler()
    result = crawler.run_topic(
        topic_name=topic,
        max_results=max_results,
        parse_pdf=parse_pdf,
    )
    print(f"[{topic}] Crawled {result.get('total', 0)} papers.")

    if download_pdf:
        papers = result.get("results", [])
        print(f"\nDownloading PDFs for {len(papers)} papers...")
        downloader = PDFDownloader()
        for i, paper in enumerate(papers, 1):
            aid = paper.get("arxiv_id", "")
            dl_result = downloader.execute(arxiv_id=aid)
            if dl_result["error"]:
                print(f"  [{i}/{len(papers)}] {aid}: ERROR - {dl_result['error']}")
            elif dl_result["downloaded"]:
                print(f"  [{i}/{len(papers)}] {aid}: Downloaded ({dl_result['file_size']} bytes)")
            else:
                print(f"  [{i}/{len(papers)}] {aid}: Already exists")


def cmd_search(query: str, max_results: int) -> None:
    """自定义搜索。"""
    searcher = get_skill("arxiv-search")
    extractor = get_skill("metadata-extract")

    print(f"Searching: {query}")
    result = searcher.execute(query=query, max_results=max_results, start_year=settings.START_YEAR)
    papers = result.get("results", [])

    clean_result = extractor.execute(mode="refine", papers=papers)
    cleaned = clean_result.get("results", [])

    print(f"\nFound {len(cleaned)} papers (valid: {clean_result['valid']}):\n")
    for i, paper in enumerate(cleaned, 1):
        print(f"{i:3d}. {paper['title']}")
        print(f"      Authors: {', '.join(paper['authors'][:3])}"
              f"{'...' if len(paper['authors']) > 3 else ''}")
        print(f"      Published: {paper['published']}")
        print(f"      arXiv: {paper['arxiv_url']}")
        print()


def cmd_download(arxiv_id: str) -> None:
    """下载单篇论文 PDF。"""
    downloader = PDFDownloader()
    result = downloader.execute(arxiv_id=arxiv_id)
    if result["error"]:
        print(f"ERROR: {result['error']}")
    elif result["downloaded"]:
        print(f"Downloaded: {result['pdf_path']} ({result['file_size']} bytes)")
    else:
        print(f"Already exists: {result['pdf_path']} ({result['file_size']} bytes)")


def cmd_parse(arxiv_id: str, pdf_path: str = "") -> None:
    """解析单篇论文 PDF（MinerU v4）。"""
    parser = get_skill("pdf-parse")
    if not parser.is_ready:
        print("ERROR: MinerU API key not configured. Set MINERU_API_KEY in .env")
        sys.exit(1)

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    print(f"Parsing: {pdf_url}")
    print(f"Model: {settings.MINERU_MODEL_VERSION}")
    print("This may take 30-120 seconds (async submit + poll + download)...")

    kwargs = {"pdf_url": pdf_url, "arxiv_id": arxiv_id}
    if pdf_path:
        kwargs["pdf_path"] = pdf_path
        kwargs.pop("pdf_url")

    result = parser.execute(**kwargs)

    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        print(f"\nParse complete!")
        if result.get("markdown_path"):
            md_path = Path(result["markdown_path"])
            if md_path.exists():
                text = md_path.read_text(encoding="utf-8")
                print(f"  Markdown: {result['markdown_path']} ({len(text)} chars)")
        if result.get("json_path"):
            print(f"  JSON: {result['json_path']}")
        if result.get("content") and result["content"].get("text"):
            preview = result["content"]["text"][:200]
            # 安全打印，避免 Windows GBK 编码错误
            try:
                print(f"\nPreview:\n{preview}...")
            except UnicodeEncodeError:
                print(f"\nPreview:\n{preview.encode('ascii', errors='replace').decode('ascii')}...")


def cmd_summarize(arxiv_id: str, md_path: str = "", title: str = "", abstract: str = "") -> None:
    """生成单篇论文摘要（DeepSeek）。"""
    summarizer = DeepSeekSummarizer()
    if not summarizer.is_ready:
        print("ERROR: DeepSeek API key not configured. Set DEEPSEEK_API_KEY in .env")
        sys.exit(1)

    # 读取全文
    full_text = ""
    if md_path:
        full_text = Path(md_path).read_text(encoding="utf-8", errors="replace")
    else:
        # 自动查找解析结果
        auto_md = settings.DATA_DIR / "parsed" / arxiv_id / f"{arxiv_id}.md"
        if auto_md.exists():
            md_path = str(auto_md)
            full_text = auto_md.read_text(encoding="utf-8", errors="replace")
            print(f"Auto-loaded parsed text from: {auto_md}")

    if not full_text:
        print("ERROR: No full text available. Provide --md-path or parse the paper first.")
        sys.exit(1)

    print(f"Generating summary for {arxiv_id}...")
    print(f"  Model: {settings.DEEPSEEK_MODEL}")
    print(f"  Text length: {len(full_text)} chars")

    result = summarizer.execute(
        arxiv_id=arxiv_id,
        title=title,
        abstract=abstract,
        full_text=full_text,
    )

    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        summary = result["summary"]
        print(f"\nSummary generated!")
        print(f"  Saved to: {result['summary_path']}")
        print(f"\n{'='*50}")
        print(f"Title: {summary.get('title', arxiv_id)}")
        print(f"\nMain Contribution:\n{summary.get('main_contribution', 'N/A')[:300]}...")
        print(f"\nInnovation Points:")
        for i, p in enumerate(summary.get("innovation_points", []), 1):
            print(f"  {i}. {p[:100]}...")
        print(f"\nBenchmarks/Datasets: {', '.join(summary.get('benchmark_datasets', []))}")
        print(f"\nAgent Relevance:\n{summary.get('agent_relevance', 'N/A')[:300]}...")


def cmd_merge(
    target: int = 200_000,
    strategy: str = "all",
    paper_list_file: str = "",
) -> None:
    """合并论文文档。"""
    merger = DocumentMerger()

    paper_list = None
    if paper_list_file:
        with open(paper_list_file, encoding="utf-8") as f:
            paper_list = json.load(f)

    if strategy == "all":
        strategies = ["full", "key-sections", "summary-only"]
        target_sizes = [175_000, 200_000, 225_000]
    elif strategy == "sliding":
        result = merger.generate_sliding_windows(target_tokens=target, paper_list=paper_list)
        print(f"\nGenerated {len(result)} sliding windows:")
        for w in result:
            print(f"  Window {w['window_index']}: {w['path']} ({w['size_tokens']} tokens)")
        return
    elif strategy == "hierarchical":
        result = merger.generate_hierarchical(target_tokens=target, paper_list=paper_list)
        print(f"\nGenerated {len(result)} hierarchical levels:")
        for r in result:
            print(f"  Level {r['level']} ({r['level_name']}): {r['path']} ({r['size_tokens']} tokens)")
        return
    else:
        strategies = [strategy]
        target_sizes = [target]

    print(f"Merging papers | strategies={strategies} targets={target_sizes}")
    report = merger.merge_all(
        target_sizes=target_sizes,
        strategies=strategies,
        paper_list=paper_list,
    )

    print(f"\nMerge complete!")
    print(f"  Papers available: {report['paper_count']}")
    print(f"  Total tokens available: {report['total_tokens_available']}")
    print(f"\nGenerated files:")
    for f in report.get("generated_files", []):
        print(f"  - {f['path']}")
        print(f"    Strategy: {f['strategy']}, Target: {f['target']}, Actual: {f['size_tokens']} tokens")


def cmd_pipeline(arxiv_id: str) -> None:
    """端到端流水线：单篇论文 下载 → 解析 → 摘要。"""
    print("=" * 60)
    print(f"  Pipeline: {arxiv_id}")
    print("=" * 60)

    # Step 1: Download
    print("\n[1/3] Downloading PDF...")
    downloader = PDFDownloader()
    dl_result = downloader.execute(arxiv_id=arxiv_id)
    if dl_result["error"]:
        print(f"  Download ERROR: {dl_result['error']}")
    else:
        print(f"  PDF: {dl_result['pdf_path']} ({dl_result['file_size']} bytes)")

    # Step 2: Parse
    print("\n[2/3] Parsing PDF with MinerU...")
    parser = PDFParser()
    if not parser.is_ready:
        print("  SKIP: MinerU API key not configured.")
    else:
        parse_result = parser.execute(
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
            arxiv_id=arxiv_id,
        )
        if parse_result["error"]:
            print(f"  Parse ERROR: {parse_result['error']}")
        else:
            md_path = parse_result.get("markdown_path", "")
            text_len = len(parse_result.get("content", {}).get("text", ""))
            print(f"  Markdown: {md_path} ({text_len} chars)")

    # Step 3: Summarize
    print("\n[3/3] Generating summary with DeepSeek...")
    summarizer = DeepSeekSummarizer()
    if not summarizer.is_ready:
        print("  SKIP: DeepSeek API key not configured.")
    else:
        # Read parsed text
        md_file = settings.DATA_DIR / "parsed" / arxiv_id / f"{arxiv_id}.md"
        if md_file.exists():
            full_text = md_file.read_text(encoding="utf-8", errors="replace")
            summary_result = summarizer.execute(
                arxiv_id=arxiv_id,
                full_text=full_text,
            )
            if summary_result["error"]:
                print(f"  Summary ERROR: {summary_result['error']}")
            else:
                print(f"  Summary saved: {summary_result['summary_path']}")
                s = summary_result["summary"]
                print(f"  Main contribution: {s.get('main_contribution', '')[:150]}...")
        else:
            print("  SKIP: No parsed Markdown found. Run parse step first.")

    print("\nPipeline complete!")


def cmd_pipeline_all(
    topics: str = "all",
    max_per_topic: int = 5,
    skip_parse: bool = False,
    skip_summarize: bool = False,
) -> None:
    """批量端到端流水线。"""
    print("=" * 60)
    print("  Batch Pipeline: Crawl → Download → Parse → Summarize")
    print("=" * 60)

    # 选择主题
    if topics == "all":
        topic_list = list(settings.SEARCH_TOPICS.keys())
    else:
        topic_list = [t.strip() for t in topics.split(",")]

    all_papers: list[dict] = []

    # Step 1: Crawl + Download
    crawler = ArxivCrawler()
    searcher = get_skill("arxiv-search")
    extractor = get_skill("metadata-extract")
    downloader = PDFDownloader()
    parser = PDFParser()
    summarizer = DeepSeekSummarizer()

    for topic in topic_list:
        print(f"\n--- Topic: {topic} ---")
        query = settings.SEARCH_TOPICS.get(topic, "")
        if not query:
            print(f"  Unknown topic: {topic}")
            continue

        search_result = searcher.execute(query=query, max_results=max_per_topic, start_year=settings.START_YEAR)
        papers = search_result.get("results", [])
        extract_result = extractor.execute(mode="refine", papers=papers)
        cleaned = extract_result.get("results", [])
        print(f"  Found: {len(cleaned)} papers")

        for paper in cleaned:
            aid = paper.get("arxiv_id", "")
            title = paper.get("title", "")

            # 保存元数据
            paper["research_direction"] = topic
            all_papers.append(paper)

            # Download
            dl_result = downloader.execute(arxiv_id=aid)
            if dl_result["downloaded"]:
                print(f"    Downloaded: {aid}")
            paper["local_pdf_path"] = dl_result.get("pdf_path")
            all_papers.append(paper)

            if not skip_parse and parser.is_ready:
                parse_result = parser.execute(
                    pdf_url=paper.get("pdf_url", f"https://arxiv.org/pdf/{aid}"),
                    arxiv_id=aid,
                )
                if not parse_result["error"]:
                    paper["local_md_path"] = parse_result.get("markdown_path")
                    paper["local_json_path"] = parse_result.get("json_path")
                    print(f"    Parsed: {aid}")

            if not skip_summarize and summarizer.is_ready:
                md_file = settings.DATA_DIR / "parsed" / aid / f"{aid}.md"
                if md_file.exists():
                    full_text = md_file.read_text(encoding="utf-8", errors="replace")
                    summary_result = summarizer.execute(
                        arxiv_id=aid,
                        title=title,
                        abstract=paper.get("abstract", ""),
                        full_text=full_text,
                    )
                    if not summary_result["error"]:
                        paper["local_summary_path"] = summary_result.get("summary_path")
                        print(f"    Summarized: {aid}")

    # 保存元数据
    meta_path = settings.DATA_DIR / "papers_metadata.json"
    meta_path.write_text(
        json.dumps(all_papers, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nMetadata saved: {meta_path} ({len(all_papers)} papers)")

    # 合并文档
    print("\n--- Merging documents ---")
    merger = DocumentMerger()
    report = merger.merge_all(
        target_sizes=[175_000, 200_000, 225_000],
        strategies=["full", "key-sections", "summary-only"],
    )
    print(f"\nGenerated {len(report.get('generated_files', []))} merge files.")
    print("\nBatch pipeline complete!")


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="arXiv Recommendation System Paper Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py list
  python main.py crawl-all
  python main.py crawl --topic agent-recommendation --max 10 --download-pdf
  python main.py search --query 'all:"multimodal" AND all:"recommendation"' --max 20
  python main.py download --arxiv-id 2602.21756
  python main.py parse --arxiv-id 2602.21756
  python main.py summarize --arxiv-id 2602.21756
  python main.py merge --target 200000
  python main.py pipeline --arxiv-id 2602.21756
  python main.py pipeline-all --max-per-topic 5
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ---- list ----
    subparsers.add_parser("list", help="List registered skills and topics")

    # ---- crawl-all ----
    subparsers.add_parser("crawl-all", help="Crawl all predefined topics")

    # ---- crawl (single topic) ----
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a single topic")
    crawl_parser.add_argument("--topic", "-t", required=True, help="Topic name")
    crawl_parser.add_argument("--max", dest="max_results", type=int, default=50)
    crawl_parser.add_argument("--download-pdf", action="store_true", help="Download PDFs after crawl")
    crawl_parser.add_argument("--pdf", action="store_true", help="Also parse PDFs (needs MinerU)")

    # ---- search ----
    search_parser = subparsers.add_parser("search", help="Custom arXiv search")
    search_parser.add_argument("--query", "-q", required=True, help="arXiv query string")
    search_parser.add_argument("--max", dest="max_results", type=int, default=20)

    # ---- download ----
    dl_parser = subparsers.add_parser("download", help="Download a paper PDF")
    dl_parser.add_argument("--arxiv-id", required=True, help="arXiv ID (e.g. 2602.21756)")

    # ---- parse ----
    parse_parser = subparsers.add_parser("parse", help="Parse a paper PDF with MinerU v4")
    parse_parser.add_argument("--arxiv-id", required=True, help="arXiv ID")
    parse_parser.add_argument("--pdf-path", default="", help="Local PDF path (optional)")

    # ---- summarize ----
    sum_parser = subparsers.add_parser("summarize", help="Generate paper summary with DeepSeek")
    sum_parser.add_argument("--arxiv-id", required=True, help="arXiv ID")
    sum_parser.add_argument("--md-path", default="", help="Path to parsed Markdown file")
    sum_parser.add_argument("--title", default="", help="Paper title (optional)")
    sum_parser.add_argument("--abstract", default="", help="Paper abstract (optional)")

    # ---- merge ----
    merge_parser = subparsers.add_parser("merge", help="Merge papers into test documents")
    merge_parser.add_argument("--target", type=int, default=200_000, help="Target token size")
    merge_parser.add_argument(
        "--strategy", default="all",
        help="Merge strategy: full, key-sections, summary-only, hybrid, sliding, hierarchical, all"
    )
    merge_parser.add_argument("--paper-list", default="", help="Path to paper list JSON file")

    # ---- pipeline (single paper) ----
    pipe_parser = subparsers.add_parser("pipeline", help="Run full pipeline for a single paper")
    pipe_parser.add_argument("--arxiv-id", required=True, help="arXiv ID")

    # ---- pipeline-all (batch) ----
    pipe_all_parser = subparsers.add_parser("pipeline-all", help="Run batch pipeline")
    pipe_all_parser.add_argument("--topics", default="all", help="Comma-separated topic names, or 'all'")
    pipe_all_parser.add_argument("--max-per-topic", type=int, default=5, help="Max papers per topic")
    pipe_all_parser.add_argument("--skip-parse", action="store_true", help="Skip MinerU parsing")
    pipe_all_parser.add_argument("--skip-summarize", action="store_true", help="Skip DeepSeek summarization")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "crawl-all":
        cmd_crawl_all()
    elif args.command == "crawl":
        cmd_crawl_topic(args.topic, args.max_results, getattr(args, 'download_pdf', False), args.pdf)
    elif args.command == "search":
        cmd_search(args.query, args.max_results)
    elif args.command == "download":
        cmd_download(args.arxiv_id)
    elif args.command == "parse":
        cmd_parse(args.arxiv_id, args.pdf_path)
    elif args.command == "summarize":
        cmd_summarize(args.arxiv_id, args.md_path, args.title, args.abstract)
    elif args.command == "merge":
        cmd_merge(args.target, args.strategy, args.paper_list)
    elif args.command == "pipeline":
        cmd_pipeline(args.arxiv_id)
    elif args.command == "pipeline-all":
        cmd_pipeline_all(args.topics, args.max_per_topic, args.skip_parse, args.skip_summarize)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
