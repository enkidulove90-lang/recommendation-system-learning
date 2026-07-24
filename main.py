#!/usr/bin/env python3
"""
main.py — arXiv 推荐系统论文爬取工具 CLI 入口

用法:
  # 1. 爬取所有预定义主题（2024年及以后）
  python main.py crawl-all

  # 2. 爬取单个主题
  python main.py crawl --topic agent-recommendation

  # 3. 自定义搜索
  python main.py search --query 'all:"graph neural network" AND all:"recommendation"' --max 30

  # 4. 解析单篇论文 PDF（需要 MinerU API Key）
  python main.py parse --arxiv-id 2503.21460

  # 5. 列出所有注册的技能和主题
  python main.py list

功能流水线:
  Search -> Metadata Extraction -> Storage -> (可选) PDF Parse
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from config import settings
from utils.helpers import setup_logging
from skills.base_module import get_skill, list_registered_skills
from crawler.arxiv_crawler import ArxivCrawler


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


def cmd_crawl_topic(topic: str, max_results: int, parse_pdf: bool) -> None:
    """爬取单个主题。"""
    crawler = ArxivCrawler()
    result = crawler.run_topic(
        topic_name=topic,
        max_results=max_results,
        parse_pdf=parse_pdf,
    )
    print(f"[{topic}] Crawled {result.get('total', 0)} papers.")


def cmd_search(query: str, max_results: int) -> None:
    """自定义搜索。"""
    searcher = get_skill("arxiv-search")
    extractor = get_skill("metadata-extract")

    print(f"Searching: {query}")
    result = searcher.execute(
        query=query,
        max_results=max_results,
        start_year=settings.START_YEAR,
    )
    papers = result.get("results", [])

    # 元数据清洗
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


def cmd_parse(arxiv_id: str) -> None:
    """解析单篇论文 PDF。"""
    parser = get_skill("pdf-parse")
    if not parser.is_ready:
        print("ERROR: MinerU API key not configured. Set MINERU_API_KEY in .env")
        sys.exit(1)

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    print(f"Parsing PDF: {pdf_url}")
    result = parser.execute(pdf_url=pdf_url, arxiv_id=arxiv_id)

    if result["error"]:
        print(f"ERROR: {result['error']}")
    elif result["content"]:
        content = result["content"]
        text = content.get("text", "")
        print(f"Parsed {len(text)} characters.")
        print(f"Sections: {len(content.get('sections', []))}")
        print(f"Tables:   {len(content.get('tables', []))}")
        print(f"Figures:  {len(content.get('figures', []))}")


def cmd_list() -> None:
    """列出所有已注册的技能和搜索主题。"""
    print("Registered Skills:")
    for name in list_registered_skills():
        print(f"  - {name}")

    print("\nSearch Topics:")
    for name, query in settings.SEARCH_TOPICS.items():
        print(f"  - {name}")
        print(f"    query: {query}")


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="arXiv Recommendation System Paper Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py crawl-all
  python main.py crawl --topic agent-recommendation --max 20 --pdf
  python main.py search --query 'all:"multimodal" AND all:"recommendation"' --max 10
  python main.py parse --arxiv-id 2503.21460
  python main.py list
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ---- crawl-all ----
    subparsers.add_parser("crawl-all", help="Crawl all predefined topics")

    # ---- crawl (single topic) ----
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a single topic")
    crawl_parser.add_argument("--topic", "-t", required=True, help="Topic name")
    crawl_parser.add_argument("--max", dest="max_results", type=int, default=50)
    crawl_parser.add_argument("--pdf", action="store_true", help="Also parse PDFs (needs MinerU)")

    # ---- search ----
    search_parser = subparsers.add_parser("search", help="Custom arXiv search")
    search_parser.add_argument("--query", "-q", required=True, help="arXiv query string")
    search_parser.add_argument("--max", dest="max_results", type=int, default=20)

    # ---- parse ----
    parse_parser = subparsers.add_parser("parse", help="Parse a single paper PDF")
    parse_parser.add_argument("--arxiv-id", required=True, help="arXiv ID (e.g. 2503.21460)")

    # ---- list ----
    subparsers.add_parser("list", help="List registered skills and topics")

    args = parser.parse_args()

    if args.command == "crawl-all":
        cmd_crawl_all()
    elif args.command == "crawl":
        cmd_crawl_topic(args.topic, args.max_results, args.pdf)
    elif args.command == "search":
        cmd_search(args.query, args.max_results)
    elif args.command == "parse":
        cmd_parse(args.arxiv_id)
    elif args.command == "list":
        cmd_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
