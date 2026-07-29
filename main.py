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

  # 围绕一篇种子论文推荐并下载相关论文
  python main.py recommend --seed 2606.26859 --top-k 8 --download-pdf

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

  # 发布到小红书（基础模式）
  python main.py publish --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --topic "推荐系统"

  # 发布到小红书（知识图谱增强）
  python main.py publish --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --topic "推荐系统" --kg
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
from redbook.scripts.publish import main as publish_main
from storage.asset_governance import AssetGovernance
from storage.paper_metadata import save_paper_metadata
from storage.paper_assets import find_parsed_markdown, paper_id_from_folder


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
        print(f"WARN: MinerU parse failed: {result['error']}")
        local_parser = get_skill("pdf-parse-local")
        local_pdf = Path(pdf_path) if pdf_path else settings.DATA_DIR / "papers" / f"{arxiv_id}.pdf"
        fallback = local_parser.execute(
            arxiv_id=arxiv_id,
            pdf_path=str(local_pdf),
        )
        if fallback["error"]:
            print(f"ERROR: Local fallback failed: {fallback['error']}")
            sys.exit(1)
        text = fallback.get("content", {}).get("text", "")
        print(f"Local fallback complete: {fallback['markdown_path']} ({len(text)} chars)")
    elif result["downloaded"]:
        print(f"Downloaded: {result['pdf_path']} ({result['file_size']} bytes)")
    else:
        print(f"Already exists: {result['pdf_path']} ({result['file_size']} bytes)")


def cmd_recommend(
    seed_arxiv_id: str,
    max_results_per_query: int,
    top_k: int,
    download_pdf: bool,
    parse_seed: bool,
    use_profiles: bool = False,
) -> None:
    """围绕一篇种子论文发现、排序并可选下载相关论文。"""
    if use_profiles:
        reranker = get_skill("research-profile-rerank")
        result = reranker.execute(seed_id=seed_arxiv_id, top_k=top_k)
        if result.get("error"):
            print(f"ERROR: {result['error']}")
            return
        print("=" * 60)
        print(f"  Profile-aware Recommendation: {seed_arxiv_id}")
        print("=" * 60)
        print(
            f"Candidates: {result['candidate_count']} | "
            f"Top-K: {len(result['results'])}"
        )
        for item in result["results"]:
            print(
                f"{item['rank']:2d}. {item['paper_id']} | "
                f"score={item['score']:.2f} | role={item['comparison_role']} | "
                f"{item['title']}"
            )
            print(f"    why: {'; '.join(item['why_this_paper'])}")
        print(f"\nReport JSON: {result['report_json_path']}")
        print(f"Report Markdown: {result['report_md_path']}")
        return

    recommender = get_skill("related-paper-recommend")

    print("=" * 60)
    print(f"  Related Paper Recommendation: {seed_arxiv_id}")
    print("=" * 60)
    result = recommender.execute(
        seed_arxiv_id=seed_arxiv_id,
        max_results_per_query=max_results_per_query,
        top_k=top_k,
        download_top_k=download_pdf,
        start_year=settings.START_YEAR,
    )

    if result.get("error"):
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    seed = result["seed"]
    print(f"\nSeed: {seed['title']}")
    print(f"arXiv: {seed['arxiv_url']}")
    print(f"Candidates: {result['total_candidates']} | Top-K: {len(result['results'])}")

    print("\nTop recommendations:")
    for i, paper in enumerate(result["results"], 1):
        print(
            f"  {i:2d}. {paper['arxiv_id']} | "
            f"score={paper['relevance_score']} | {paper['title']}"
        )
        print(f"      reason: {paper['recommendation_reason']}")
        if paper.get("local_pdf_path"):
            print(f"      pdf: {paper['local_pdf_path']}")

    print(f"\nReport JSON: {result['report_json_path']}")
    print(f"Report Markdown: {result['report_md_path']}")

    if parse_seed:
        parser = PDFParser()
        if not parser.is_ready:
            print("\nMinerU API key not configured; using local PDF text fallback.")
            local_parser = get_skill("pdf-parse-local")
            local_pdf = settings.DATA_DIR / "papers" / f"{seed_arxiv_id}.pdf"
            local_result = local_parser.execute(
                arxiv_id=seed_arxiv_id,
                pdf_path=str(local_pdf),
                title=seed.get("title", ""),
            )
            if local_result["error"]:
                print(f"Local parse ERROR: {local_result['error']}")
            else:
                text_len = len(local_result.get("content", {}).get("text", ""))
                print(f"Local parsed Markdown: {local_result['markdown_path']} ({text_len} chars)")
        else:
            print(f"\nParsing seed paper with MinerU: {seed_arxiv_id}")
            parse_result = parser.execute(
                pdf_url=seed.get("pdf_url", f"https://arxiv.org/pdf/{seed_arxiv_id}"),
                arxiv_id=seed_arxiv_id,
                title=seed.get("title", ""),
            )
            if parse_result["error"]:
                print(f"Parse ERROR: {parse_result['error']}")
            else:
                print(f"Parsed Markdown: {parse_result.get('markdown_path')}")


def cmd_parse(arxiv_id: str, pdf_path: str = "") -> None:
    """解析单篇论文 PDF（MinerU v4）。"""
    parser = get_skill("pdf-parse")
    if not parser.is_ready:
        print("WARN: MinerU API key not configured. Using local PDF text fallback.")
        local_parser = get_skill("pdf-parse-local")
        local_pdf = Path(pdf_path) if pdf_path else settings.DATA_DIR / "papers" / f"{arxiv_id}.pdf"
        result = local_parser.execute(
            arxiv_id=arxiv_id,
            pdf_path=str(local_pdf),
        )
        if result["error"]:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

        text = result.get("content", {}).get("text", "")
        print(f"\nLocal parse complete!")
        print(f"  Markdown: {result['markdown_path']} ({len(text)} chars)")
        preview = text[:200]
        try:
            print(f"\nPreview:\n{preview}...")
        except UnicodeEncodeError:
            print(f"\nPreview:\n{preview.encode('ascii', errors='replace').decode('ascii')}...")
        return

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
        auto_md = find_parsed_markdown(arxiv_id)
        if auto_md is not None:
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


def _available_profile_ids() -> list[str]:
    parsed_root = settings.DATA_DIR / "parsed"
    if not parsed_root.exists():
        return []
    paper_ids = sorted({
        paper_id_from_folder(path.name)
        for path in parsed_root.iterdir()
        if path.is_dir()
    })
    return AssetGovernance().filter_active(paper_ids)


def cmd_profile(arxiv_id: str = "", all_profiles: bool = False, force: bool = False) -> None:
    """Build Summary 2.0 research profiles from local paper assets."""
    builder = get_skill("research-profile-build")
    paper_ids = _available_profile_ids() if all_profiles else [arxiv_id]
    success = skipped = failed = 0
    for index, paper_id in enumerate(paper_ids, 1):
        result = builder.execute(arxiv_id=paper_id, force=force)
        if result.get("error"):
            failed += 1
            print(f"[{index}/{len(paper_ids)}] {paper_id}: ERROR {result['error']}")
        elif result.get("skipped"):
            skipped += 1
            print(f"[{index}/{len(paper_ids)}] {paper_id}: up to date")
        else:
            success += 1
            print(f"[{index}/{len(paper_ids)}] {paper_id}: {result['profile_path']}")
    print(f"Profile build complete: generated={success}, skipped={skipped}, failed={failed}")


def cmd_validate_profile(arxiv_id: str = "", all_profiles: bool = False) -> None:
    """Validate profiles against schema, evidence, hashes, and taxonomies."""
    validator = get_skill("research-profile-validate")
    paper_ids = _available_profile_ids() if all_profiles else [arxiv_id]
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    failed = 0
    report_rows = []
    for index, paper_id in enumerate(paper_ids, 1):
        result = validator.execute(arxiv_id=paper_id)
        if result.get("error"):
            failed += 1
            print(f"[{index}/{len(paper_ids)}] {paper_id}: ERROR {result['error']}")
            continue
        grade = result["grade"]
        counts[grade] += 1
        report_rows.append(result)
        print(
            f"[{index}/{len(paper_ids)}] {paper_id}: "
            f"grade={grade} status={result['status']} issues={len(result['issues'])}"
        )
    print(
        "Validation complete: "
        + ", ".join(f"{grade}={count}" for grade, count in counts.items())
        + f", failed={failed}"
    )
    if all_profiles:
        report_path = settings.DATA_DIR / "reviews" / "quality_report.md"
        report_lines = [
            "# Research Profile Quality Report",
            "",
            f"Generated at: {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            "| Grade | Count |",
            "|---|---:|",
            *[f"| {grade} | {counts[grade]} |" for grade in ("A", "B", "C", "D")],
            "",
            "## Papers",
            "",
            "| Paper | Grade | Status | Evidence coverage | Issues |",
            "|---|---|---|---:|---:|",
        ]
        report_lines.extend(
            f"| {row['paper_id']} | {row['grade']} | {row['status']} | "
            f"{row['evidence_coverage']:.3f} | {len(row['issues'])} |"
            for row in report_rows
        )
        report_lines.extend(["", "## Blocked Papers", ""])
        blocked = [row for row in report_rows if row["grade"] == "D"]
        if not blocked:
            report_lines.append("None.")
        for row in blocked:
            report_lines.append(f"### {row['paper_id']}")
            report_lines.append("")
            for issue in row["issues"]:
                report_lines.append(
                    f"- `{issue['code']}`: {issue['message']}"
                )
            report_lines.append("")
        governance = AssetGovernance()
        report_lines.extend(["## Asset Repairs", ""])
        report_lines.extend(
            [
                "| Original | Resolution | Active replacement |",
                "|---|---|---|",
            ]
        )
        for repair in governance.repairs:
            report_lines.append(
                f"| {repair.get('original_id', '')} | "
                f"{repair.get('resolution', '')} | "
                f"{repair.get('replacement_id', '')} |"
            )
        report_lines.append("")
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        print(f"Quality report: {report_path}")


def cmd_search_profile(
    *,
    stage: str = "",
    problem: str = "",
    paradigm: str = "",
    modality: str = "",
    quality: str = "",
    query: str = "",
    limit: int = 20,
) -> None:
    """Search local machine-readable profiles."""
    searcher = get_skill("research-profile-search")
    result = searcher.execute(
        stage=stage,
        problem=problem,
        paradigm=paradigm,
        modality=modality,
        quality=quality,
        query=query,
        limit=limit,
    )
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return
    print(f"Matched profiles: {result['total']}")
    for index, item in enumerate(result["results"], 1):
        title = item["chinese_title"] or item["title"] or item["paper_id"]
        print(
            f"{index:2d}. {item['paper_id']} | grade={item['quality']['grade']} | {title}"
        )
        print(
            "    "
            f"stages={','.join(item['pipeline_stages']) or '-'} "
            f"problems={','.join(item['problems']) or '-'} "
            f"paradigms={','.join(item['technical_paradigms']) or '-'}"
        )


def cmd_build_relations(arxiv_id: str = "", max_semantic_edges: int = 6) -> None:
    """Build citation and semantic relation edges for active profiles."""
    builder = get_skill("research-relations-build")
    result = builder.execute(
        arxiv_id=arxiv_id,
        max_semantic_edges=max_semantic_edges,
    )
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return
    print(
        f"Relation graph: profiles={result['profile_count']} "
        f"edges={result['edge_count']}"
    )
    if arxiv_id:
        print(f"Edges touching {arxiv_id}: {result['selected_edge_count']}")
    print(f"Graph JSON: {result['graph_path']}")
    print(f"Relations JSONL: {result['jsonl_path']}")


def cmd_learning_path(
    topic: str = "",
    level: str = "intermediate",
    all_paths: bool = False,
    max_papers: int = 0,
) -> None:
    """Generate one or the five default explainable learning paths."""
    builder = get_skill("research-learning-path")
    if all_paths:
        from skills.learning_path_builder import DEFAULT_PATHS

        requests = list(DEFAULT_PATHS)
    else:
        requests = [(topic, level)]
    failed = 0
    for path_topic, path_level in requests:
        result = builder.execute(
            topic=path_topic,
            level=path_level,
            max_papers=max_papers,
        )
        if result.get("error"):
            failed += 1
            print(f"{path_topic}/{path_level}: ERROR {result['error']}")
            continue
        print(
            f"{result['path_id']}: steps={len(result['steps'])} "
            f"markdown={result['markdown_path']}"
        )
    print(f"Learning paths complete: generated={len(requests) - failed}, failed={failed}")


def cmd_pipeline(arxiv_id: str) -> None:
    """端到端流水线：单篇论文 下载 → 解析 → 摘要。"""
    print("=" * 60)
    print(f"  Pipeline: {arxiv_id}")
    print("=" * 60)

    paper_metadata = {}
    try:
        metadata_fetcher = get_skill("related-paper-recommend")
        paper_metadata = metadata_fetcher._fetch_by_id(arxiv_id) or {}
        if paper_metadata:
            save_paper_metadata(paper_metadata)
            print(f"  Metadata: {paper_metadata.get('title', arxiv_id)}")
    except Exception as exc:
        print(f"  Metadata WARN: {exc}")
    paper_title = str(paper_metadata.get("title", ""))
    paper_abstract = str(paper_metadata.get("abstract", ""))

    # Step 1: Download
    print("\n[1/6] Downloading PDF...")
    downloader = PDFDownloader()
    dl_result = downloader.execute(arxiv_id=arxiv_id)
    if dl_result["error"]:
        print(f"  Download ERROR: {dl_result['error']}")
    else:
        print(f"  PDF: {dl_result['pdf_path']} ({dl_result['file_size']} bytes)")

    # Step 2: Parse
    print("\n[2/6] Parsing PDF with MinerU...")
    parser = PDFParser()
    if not parser.is_ready:
        print("  MinerU API key not configured; using local PDF text fallback.")
        local_parser = get_skill("pdf-parse-local")
        local_pdf = Path(dl_result.get("pdf_path") or settings.DATA_DIR / "papers" / f"{arxiv_id}.pdf")
        local_result = local_parser.execute(
            arxiv_id=arxiv_id,
            pdf_path=str(local_pdf),
            title=paper_title,
        )
        if local_result["error"]:
            print(f"  Local parse ERROR: {local_result['error']}")
        else:
            text_len = len(local_result.get("content", {}).get("text", ""))
            print(f"  Local Markdown: {local_result['markdown_path']} ({text_len} chars)")
    else:
        parse_result = parser.execute(
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
            arxiv_id=arxiv_id,
            title=paper_title,
        )
        if parse_result["error"]:
            print(f"  MinerU parse WARN: {parse_result['error']}")
            local_parser = get_skill("pdf-parse-local")
            local_pdf = Path(
                dl_result.get("pdf_path")
                or settings.DATA_DIR / "papers" / f"{arxiv_id}.pdf"
            )
            local_result = local_parser.execute(
                arxiv_id=arxiv_id,
                pdf_path=str(local_pdf),
                title=paper_title,
            )
            if local_result["error"]:
                print(f"  Local fallback ERROR: {local_result['error']}")
            else:
                text_len = len(local_result.get("content", {}).get("text", ""))
                print(
                    f"  Local fallback Markdown: "
                    f"{local_result['markdown_path']} ({text_len} chars)"
                )
        else:
            md_path = parse_result.get("markdown_path", "")
            text_len = len(parse_result.get("content", {}).get("text", ""))
            print(f"  Markdown: {md_path} ({text_len} chars)")

    # Step 3: Summarize
    print("\n[3/6] Generating summary with DeepSeek...")
    summarizer = DeepSeekSummarizer()
    if not summarizer.is_ready:
        print("  SKIP: DeepSeek API key not configured.")
    else:
        # Read parsed text
        md_file = find_parsed_markdown(arxiv_id)
        if md_file is not None:
            full_text = md_file.read_text(encoding="utf-8", errors="replace")
            summary_result = summarizer.execute(
                arxiv_id=arxiv_id,
                title=paper_title,
                abstract=paper_abstract,
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

    print("\n[4/6] Building Summary 2.0 profile...")
    profile_builder = get_skill("research-profile-build")
    profile_result = profile_builder.execute(arxiv_id=arxiv_id)
    if profile_result.get("error"):
        print(f"  Profile ERROR: {profile_result['error']}")
    else:
        state = "up to date" if profile_result.get("skipped") else "generated"
        print(f"  Profile {state}: {profile_result['profile_path']}")

    print("\n[5/6] Validating profile...")
    validator = get_skill("research-profile-validate")
    validation_result = validator.execute(arxiv_id=arxiv_id)
    if validation_result.get("error"):
        print(f"  Validation ERROR: {validation_result['error']}")
    else:
        print(
            f"  Quality: grade={validation_result['grade']} "
            f"status={validation_result['status']} "
            f"issues={len(validation_result['issues'])}"
        )

    print("\n[6/6] Updating relation graph...")
    relation_builder = get_skill("research-relations-build")
    relation_result = relation_builder.execute(arxiv_id=arxiv_id)
    if relation_result.get("error"):
        print(f"  Relations ERROR: {relation_result['error']}")
    else:
        print(
            f"  Relation graph: edges={relation_result['edge_count']} "
            f"touching_paper={relation_result['selected_edge_count']}"
        )

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
                    title=title,
                )
                if not parse_result["error"]:
                    paper["local_md_path"] = parse_result.get("markdown_path")
                    paper["local_json_path"] = parse_result.get("json_path")
                    print(f"    Parsed: {aid}")

            if not skip_summarize and summarizer.is_ready:
                md_file = find_parsed_markdown(aid)
                if md_file is not None:
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
  python main.py recommend --seed 2606.26859 --top-k 8 --download-pdf
  python main.py parse --arxiv-id 2602.21756
  python main.py summarize --arxiv-id 2602.21756
  python main.py profile --arxiv-id 2602.21756
  python main.py validate-profile --arxiv-id 2602.21756
  python main.py search-profile --problem cold_start --quality B,C
  python main.py merge --target 200000
  python main.py pipeline --arxiv-id 2602.21756
  python main.py pipeline-all --max-per-topic 5
  python main.py publish --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --topic "推荐系统"
  python main.py publish --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --kg --dry-run
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

    # ---- recommend ----
    rec_parser = subparsers.add_parser(
        "recommend",
        help="Find related papers from a seed arXiv paper",
    )
    rec_parser.add_argument("--seed", required=True, help="Seed arXiv ID (e.g. 2606.26859)")
    rec_parser.add_argument(
        "--max-per-query",
        type=int,
        default=10,
        help="Max arXiv results fetched for each expanded query",
    )
    rec_parser.add_argument("--top-k", type=int, default=8, help="Recommended papers to keep")
    rec_parser.add_argument("--download-pdf", action="store_true", help="Download Top-K PDFs")
    rec_parser.add_argument(
        "--parse-seed",
        action="store_true",
        help="Parse the seed paper with MinerU after recommendation",
    )
    rec_parser.add_argument(
        "--use-profiles",
        action="store_true",
        help="Use validated local profiles and relation graph for reranking",
    )

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

    # ---- profile ----
    profile_parser = subparsers.add_parser(
        "profile",
        help="Build a Summary 2.0 machine-readable research profile",
    )
    profile_target = profile_parser.add_mutually_exclusive_group(required=True)
    profile_target.add_argument("--arxiv-id", help="arXiv ID")
    profile_target.add_argument("--all", action="store_true", help="Build all local parsed papers")
    profile_parser.add_argument("--force", action="store_true", help="Rebuild even if source hashes match")

    # ---- validate-profile ----
    validate_parser = subparsers.add_parser(
        "validate-profile",
        help="Validate profiles and generate quality review records",
    )
    validate_target = validate_parser.add_mutually_exclusive_group(required=True)
    validate_target.add_argument("--arxiv-id", help="arXiv ID")
    validate_target.add_argument("--all", action="store_true", help="Validate all local profiles")

    # ---- search-profile ----
    profile_search_parser = subparsers.add_parser(
        "search-profile",
        help="Search local structured research profiles",
    )
    profile_search_parser.add_argument("--stage", default="", help="Controlled pipeline stage")
    profile_search_parser.add_argument("--problem", default="", help="Controlled research problem")
    profile_search_parser.add_argument("--paradigm", default="", help="Controlled technical paradigm")
    profile_search_parser.add_argument("--modality", default="", help="Controlled input modality")
    profile_search_parser.add_argument("--quality", default="", help="Comma-separated grades, e.g. A,B")
    profile_search_parser.add_argument("--query", default="", help="Free-text substring query")
    profile_search_parser.add_argument("--limit", type=int, default=20)

    # ---- build-relations ----
    relation_parser = subparsers.add_parser(
        "build-relations",
        help="Build citation and semantic relations between active profiles",
    )
    relation_parser.add_argument("--arxiv-id", default="", help="Show edges touching one paper")
    relation_parser.add_argument(
        "--max-semantic-edges",
        type=int,
        default=6,
        help="Maximum semantic neighbours retained per profile",
    )

    # ---- learning-path ----
    learning_parser = subparsers.add_parser(
        "learning-path",
        help="Generate explainable reading paths from profiles and relations",
    )
    learning_target = learning_parser.add_mutually_exclusive_group(required=True)
    learning_target.add_argument("--topic", default="", help="Topic or controlled tag")
    learning_target.add_argument("--all", action="store_true", help="Generate five default paths")
    learning_parser.add_argument(
        "--level",
        choices=("beginner", "intermediate", "advanced"),
        default="intermediate",
    )
    learning_parser.add_argument("--max-papers", type=int, default=0)

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

    # ---- publish (统一发布入口) ----
    pub_parser = subparsers.add_parser(
        "publish",
        help="Publish paper to Xiaohongshu (direct API + optional KG analysis)",
    )
    pub_parser.add_argument("--arxiv-id", required=True, help="arXiv ID (e.g. 2605.28175)")
    pub_parser.add_argument("--title", required=True, help="Post title (max 20 chars)")
    pub_parser.add_argument("--topic", action="append", default=[], help="Topic tags (repeatable)")
    pub_parser.add_argument("--github", default="", help="GitHub URL (optional)")
    pub_parser.add_argument("--kg", action="store_true", help="Enable knowledge graph analysis enhancement")
    pub_parser.add_argument("--dry-run", action="store_true", help="Preview only, do not publish")

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
    elif args.command == "recommend":
        cmd_recommend(
            args.seed,
            args.max_per_query,
            args.top_k,
            args.download_pdf,
            args.parse_seed,
            args.use_profiles,
        )
    elif args.command == "parse":
        cmd_parse(args.arxiv_id, args.pdf_path)
    elif args.command == "summarize":
        cmd_summarize(args.arxiv_id, args.md_path, args.title, args.abstract)
    elif args.command == "profile":
        cmd_profile(args.arxiv_id or "", args.all, args.force)
    elif args.command == "validate-profile":
        cmd_validate_profile(args.arxiv_id or "", args.all)
    elif args.command == "search-profile":
        cmd_search_profile(
            stage=args.stage,
            problem=args.problem,
            paradigm=args.paradigm,
            modality=args.modality,
            quality=args.quality,
            query=args.query,
            limit=args.limit,
        )
    elif args.command == "build-relations":
        cmd_build_relations(args.arxiv_id, args.max_semantic_edges)
    elif args.command == "learning-path":
        cmd_learning_path(args.topic, args.level, args.all, args.max_papers)
    elif args.command == "merge":
        cmd_merge(args.target, args.strategy, args.paper_list)
    elif args.command == "pipeline":
        cmd_pipeline(args.arxiv_id)
    elif args.command == "pipeline-all":
        cmd_pipeline_all(args.topics, args.max_per_topic, args.skip_parse, args.skip_summarize)
    elif args.command == "publish":
        # 将 argparse namespace 转为 publish.py 需要的参数
        sys.argv = [
            "publish.py",
            "--arxiv-id", args.arxiv_id,
            "--title", args.title,
        ]
        if args.kg:
            sys.argv.append("--kg")
        if args.dry_run:
            sys.argv.append("--dry-run")
        if args.github:
            sys.argv.extend(["--github", args.github])
        for t in args.topic:
            sys.argv.extend(["--topic", t])
        publish_main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
