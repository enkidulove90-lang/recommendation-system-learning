#!/usr/bin/env python3
"""
run_batch_pipeline.py — 批量执行 7 Phase 操作层面工作

用法:
  python run_batch_pipeline.py --step 1    # MinerU vlm 解析
  python run_batch_pipeline.py --step 2    # 视觉模型 _figures.json
  python run_batch_pipeline.py --step 3    # 11 维度摘要重写
  python run_batch_pipeline.py --step 4    # 分类回写 papers.jsonl
  python run_batch_pipeline.py --step 5    # 文件夹标准化
  python run_batch_pipeline.py --step all  # 顺序执行 1-5
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from config import settings
from utils.helpers import setup_logging
from skills.pdf_parser import PDFParser
from skills.vision_enhancer import VisionEnhancer
from skills.deepseek_summarizer import DeepSeekSummarizer
from skills.paper_classifier import PaperClassifier
from skills.folder_standardizer import FolderStandardizer
from storage.paper_assets import find_parsed_markdown, paper_id_from_folder

logger = logging.getLogger(__name__)

PARSED_DIR = settings.DATA_DIR / "parsed"
SUMMARIES_DIR = settings.DATA_DIR / "summaries"
LOG_DIR = settings.DATA_DIR / "logs"


# ======================================================================
# 工具函数
# ======================================================================

def get_all_paper_folders() -> list[Path]:
    """获取 data/parsed/ 下所有论文文件夹（排除备份和特殊目录）。"""
    skip_prefixes = ("_", "mineru_july_2026")
    folders = []
    for d in sorted(PARSED_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith(skip_prefixes):
            folders.append(d)
    return folders


def get_arxiv_id(folder: Path) -> str:
    """从文件夹名提取 arXiv ID。"""
    return paper_id_from_folder(folder.name) or folder.name.split("_")[0]


def load_figure_descriptions(arxiv_id: str, paper_dir: Path) -> str:
    """加载 _figures.json 中的图表描述，作为摘要生成的上下文。"""
    figures_path = paper_dir / f"{arxiv_id}_figures.json"
    if not figures_path.exists():
        # 尝试旧命名
        figures_path = paper_dir / "_figures.json"
    if not figures_path.exists():
        return ""

    try:
        data = json.loads(figures_path.read_text(encoding="utf-8"))
        figures = data.get("figures", [])
        if not figures:
            return ""

        parts = []
        for fig in figures:
            fig_type = fig.get("figure_type", "other")
            desc = fig.get("description", "")
            img_file = fig.get("image_file", "")
            parts.append(f"[{fig_type}] {img_file}:\n{desc}")

        return "\n\n".join(parts)
    except (json.JSONDecodeError, OSError):
        return ""


def save_step_log(step: int, results: list[dict]) -> Path:
    """保存步骤执行日志。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"batch_step{step}_{timestamp}.json"
    log_data = {
        "step": step,
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "succeeded": sum(1 for r in results if not r.get("error")),
        "failed": sum(1 for r in results if r.get("error")),
        "results": results,
    }
    log_path.write_text(
        json.dumps(log_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("[Step %d] Log saved -> %s", step, log_path)
    return log_path


# ======================================================================
# Step 1: MinerU vlm 解析
# ======================================================================

def step1_mineru_parse() -> list[dict]:
    """对有 PDF 但无 .md 的文件夹执行 MinerU vlm 解析。"""
    logger.info("=" * 60)
    logger.info("  Step 1: MinerU vlm Parsing")
    logger.info("=" * 60)

    parser = PDFParser()
    if not parser.is_ready:
        logger.error("MinerU API key not configured. Skipping Step 1.")
        return [{"error": "MINERU_API_KEY not set"}]

    results = []
    folders = get_all_paper_folders()
    processed_aids: set[str] = set()

    for folder in folders:
        arxiv_id = get_arxiv_id(folder)

        # 跳过已处理的 arxiv_id（避免重复文件夹）
        if arxiv_id in processed_aids:
            continue

        md_files = list(folder.glob("*.md"))

        # 跳过已有 .md 的文件夹
        if md_files:
            processed_aids.add(arxiv_id)
            logger.info("[Step1] SKIP %s (already has .md)", arxiv_id)
            continue

        processed_aids.add(arxiv_id)

        # 查找 PDF 文件
        pdf_files = list(folder.glob("*.pdf"))
        paper_pdf = settings.DATA_DIR / "papers" / f"{arxiv_id}.pdf"
        arxiv_source_pdf = folder / "arxiv_source"
        source_pdfs = list(arxiv_source_pdf.glob("*.pdf")) if arxiv_source_pdf.exists() else []

        pdf_path = None
        if pdf_files:
            pdf_path = pdf_files[0]
        elif paper_pdf.exists():
            pdf_path = paper_pdf
        elif source_pdfs:
            pdf_path = source_pdfs[0]

        if not pdf_path:
            logger.warning("[Step1] SKIP %s (no PDF found)", arxiv_id)
            results.append({"arxiv_id": arxiv_id, "error": "No PDF found"})
            continue

        # 确定解析方式
        # arXiv ID 格式: YYMM.NNNNN 或 YYMM.NNNNNvN
        is_arxiv = bool(re.match(r"\d{4}\.\d{4,5}", arxiv_id))

        logger.info("[Step1] Parsing %s (PDF: %s)", arxiv_id, pdf_path.name)

        try:
            if is_arxiv:
                # 使用 arXiv URL
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
                result = parser.execute(
                    pdf_url=pdf_url,
                    arxiv_id=arxiv_id,
                    title="",
                )
            else:
                # 非 arXiv 论文，尝试使用 URL 模式
                # MinerU v4 API 可能不支持本地文件，但我们尝试
                logger.info("[Step1] Non-arXiv paper %s, trying URL upload...", arxiv_id)
                # 先尝试将 PDF 作为本地文件解析
                result = parser.execute(
                    pdf_path=str(pdf_path),
                    arxiv_id=arxiv_id,
                    title="",
                )

            if result.get("error"):
                logger.error("[Step1] FAILED %s: %s", arxiv_id, result["error"])
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": result["error"],
                    "markdown_path": None,
                })
            else:
                md_path = result.get("markdown_path", "")
                text_len = len(result.get("content", {}).get("text", ""))
                logger.info("[Step1] OK %s: %s (%d chars)", arxiv_id, md_path, text_len)
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": None,
                    "markdown_path": md_path,
                    "text_length": text_len,
                })

        except Exception as e:
            logger.error("[Step1] EXCEPTION %s: %s", arxiv_id, e)
            results.append({"arxiv_id": arxiv_id, "error": str(e)})

        # API 速率控制
        time.sleep(2)

    return results


# ======================================================================
# Step 2: 视觉模型 _figures.json
# ======================================================================

def step2_vision_enhance() -> list[dict]:
    """对有 images/ 但无 _figures.json 的文件夹执行视觉模型理解。"""
    logger.info("=" * 60)
    logger.info("  Step 2: Vision Enhancement (Qwen3.5)")
    logger.info("=" * 60)

    enhancer = VisionEnhancer()
    if not enhancer.is_ready:
        logger.error("ModelScope API key not configured. Skipping Step 2.")
        return [{"error": "MODELSCOPE_API_KEY not set"}]

    results = []
    folders = get_all_paper_folders()
    processed_aids: set[str] = set()

    for folder in folders:
        arxiv_id = get_arxiv_id(folder)

        # 跳过已处理的 arxiv_id
        if arxiv_id in processed_aids:
            continue
        processed_aids.add(arxiv_id)

        images_dir = folder / "images"
        figures_path = folder / f"{arxiv_id}_figures.json"

        # 检查是否有 images 目录
        if not images_dir.exists():
            logger.info("[Step2] SKIP %s (no images/ dir)", arxiv_id)
            continue

        # 检查图片数量
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in image_exts and f.is_file()]
        if not image_files:
            logger.info("[Step2] SKIP %s (no images in images/)", arxiv_id)
            continue

        # 跳过已存在 _figures.json（但检查是否有实际内容）
        if figures_path.exists():
            try:
                existing = json.loads(figures_path.read_text(encoding="utf-8"))
                if existing.get("figures_count", 0) > 0:
                    logger.info("[Step2] SKIP %s (already has _figures.json with %d figures)", arxiv_id, existing["figures_count"])
                    continue
                else:
                    logger.info("[Step2] REPROCESS %s (empty _figures.json, will retry)", arxiv_id)
            except (json.JSONDecodeError, OSError):
                logger.info("[Step2] REPROCESS %s (corrupt _figures.json, will retry)", arxiv_id)

        logger.info("[Step2] Processing %s (%d images)", arxiv_id, len(image_files))

        try:
            result = enhancer.execute(
                paper_dir=str(folder),
                arxiv_id=arxiv_id,
                max_figures=3,
                skip_existing=True,
            )

            if result.get("error"):
                logger.warning("[Step2] WARN %s: %s", arxiv_id, result["error"])
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": result["error"],
                    "figures_count": 0,
                })
            else:
                count = result.get("figures_count", 0)
                logger.info("[Step2] OK %s: %d figures described", arxiv_id, count)
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": None,
                    "figures_count": count,
                    "figures_path": result.get("figures_path"),
                })

        except Exception as e:
            logger.error("[Step2] EXCEPTION %s: %s", arxiv_id, e)
            results.append({"arxiv_id": arxiv_id, "error": str(e)})

        # API 速率控制
        time.sleep(1)

    return results


# ======================================================================
# Step 3: 11 维度摘要重写
# ======================================================================

def step3_summarize() -> list[dict]:
    """对所有有 .md 的论文执行 11 维度摘要重写。"""
    logger.info("=" * 60)
    logger.info("  Step 3: 11-Dimension Summary Rewrite")
    logger.info("=" * 60)

    summarizer = DeepSeekSummarizer()
    if not summarizer.is_ready:
        logger.error("DeepSeek API key not configured. Skipping Step 3.")
        return [{"error": "DEEPSEEK_API_KEY not set"}]

    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    folders = get_all_paper_folders()
    processed_aids: set[str] = set()

    for folder in folders:
        arxiv_id = get_arxiv_id(folder)

        # 跳过已处理的 arxiv_id
        if arxiv_id in processed_aids:
            continue
        processed_aids.add(arxiv_id)

        # 查找 .md 文件
        md_file = find_parsed_markdown(arxiv_id)
        if md_file is None:
            # 尝试文件夹内查找
            md_files = list(folder.glob("*.md"))
            if not md_files:
                logger.info("[Step3] SKIP %s (no .md)", arxiv_id)
                continue
            md_file = md_files[0]

        # 读取全文
        try:
            full_text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.error("[Step3] READ ERROR %s: %s", arxiv_id, e)
            results.append({"arxiv_id": arxiv_id, "error": f"Read error: {e}"})
            continue

        if not full_text.strip():
            logger.warning("[Step3] SKIP %s (empty .md)", arxiv_id)
            results.append({"arxiv_id": arxiv_id, "error": "Empty markdown"})
            continue

        # 加载图表描述
        figure_desc = load_figure_descriptions(arxiv_id, folder)
        if figure_desc:
            logger.info("[Step3] %s: loaded %d chars figure descriptions", arxiv_id, len(figure_desc))

        # 检查是否已有新的 11 维度摘要（含 title_zh 字段）
        existing_json = SUMMARIES_DIR / f"{arxiv_id}_summary.json"
        if existing_json.exists():
            try:
                existing = json.loads(existing_json.read_text(encoding="utf-8"))
                if existing.get("title_zh") and existing.get("problem_definition"):
                    logger.info("[Step3] SKIP %s (already has 11-dim summary)", arxiv_id)
                    results.append({
                        "arxiv_id": arxiv_id,
                        "error": None,
                        "skipped": True,
                        "summary_path": str(existing_json),
                    })
                    continue
            except (json.JSONDecodeError, OSError):
                pass  # 文件损坏，重新生成

        logger.info("[Step3] Summarizing %s (%d chars text)", arxiv_id, len(full_text))

        try:
            result = summarizer.execute(
                arxiv_id=arxiv_id,
                title="",
                abstract="",
                full_text=full_text,
                figure_descriptions=figure_desc,
                output_dir=str(SUMMARIES_DIR),
            )

            if result.get("error"):
                logger.error("[Step3] FAILED %s: %s", arxiv_id, result["error"])
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": result["error"],
                    "summary_path": None,
                })
            else:
                md_path = result.get("summary_path", "")
                json_path = result.get("summary_json_path", "")
                summary = result.get("summary", {})
                title_zh = summary.get("title_zh", "") if summary else ""
                logger.info("[Step3] OK %s: %s | %s", arxiv_id, title_zh, md_path)
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": None,
                    "summary_path": md_path,
                    "summary_json_path": json_path,
                    "title_zh": title_zh,
                })

        except Exception as e:
            logger.error("[Step3] EXCEPTION %s: %s", arxiv_id, e)
            results.append({"arxiv_id": arxiv_id, "error": str(e)})

        # API 速率控制
        time.sleep(2)

    return results


# ======================================================================
# Step 4: 分类回写 papers.jsonl
# ======================================================================

def step4_classify() -> list[dict]:
    """使用 taxonomies.yaml 对论文进行分类，回写 papers.jsonl。"""
    logger.info("=" * 60)
    logger.info("  Step 4: Classification & papers.jsonl Update")
    logger.info("=" * 60)

    classifier = PaperClassifier()
    if not classifier.is_ready:
        logger.error("Taxonomies not loaded. Skipping Step 4.")
        return [{"error": "taxonomies.yaml not loaded"}]

    results = []
    folders = get_all_paper_folders()
    processed_aids: set[str] = set()

    for folder in folders:
        arxiv_id = get_arxiv_id(folder)

        # 跳过已处理的 arxiv_id
        if arxiv_id in processed_aids:
            continue
        processed_aids.add(arxiv_id)

        summary_json = SUMMARIES_DIR / f"{arxiv_id}_summary.json"

        if not summary_json.exists():
            logger.info("[Step4] SKIP %s (no summary JSON)", arxiv_id)
            results.append({"arxiv_id": arxiv_id, "error": "No summary JSON"})
            continue

        logger.info("[Step4] Classifying %s", arxiv_id)

        try:
            result = classifier.execute(
                arxiv_id=arxiv_id,
                summary_json_path=str(summary_json),
                update_papers_jsonl=True,
            )

            if result.get("error"):
                logger.error("[Step4] FAILED %s: %s", arxiv_id, result["error"])
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": result["error"],
                })
            else:
                classification = result.get("classification", {})
                directions = classification.get("research_directions", [])
                logger.info("[Step4] OK %s: directions=%s", arxiv_id, directions)
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": None,
                    "classification": classification,
                    "updated": result.get("updated", False),
                })

        except Exception as e:
            logger.error("[Step4] EXCEPTION %s: %s", arxiv_id, e)
            results.append({"arxiv_id": arxiv_id, "error": str(e)})

    return results


# ======================================================================
# Step 5: 文件夹标准化
# ======================================================================

def step5_standardize() -> list[dict]:
    """标准化所有论文文件夹的结构和命名。"""
    logger.info("=" * 60)
    logger.info("  Step 5: Folder Standardization")
    logger.info("=" * 60)

    standardizer = FolderStandardizer()

    # 先从 papers.jsonl 加载分类结果
    jsonl_path = settings.DATA_DIR / "registry" / "papers.jsonl"
    classifications: dict[str, dict] = {}
    if jsonl_path.exists():
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                aid = record.get("arxiv_id", "")
                if aid:
                    classifications[aid] = record.get("classification", {})
            except json.JSONDecodeError:
                continue

    # 从摘要 JSON 加载中文标题
    titles: dict[str, str] = {}
    for json_file in SUMMARIES_DIR.glob("*_summary.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            aid = data.get("paper_id", json_file.stem.replace("_summary", ""))
            title_zh = data.get("title_zh", "") or data.get("title", "")
            if aid and title_zh:
                titles[aid] = title_zh
        except (json.JSONDecodeError, OSError):
            continue

    # 获取所有文件夹并按 arxiv_id 分组
    all_folders = get_all_paper_folders()
    existing_names = {f.name for f in all_folders}

    # 按 arxiv_id 分组，每个 arxiv_id 只处理一次
    processed_aids: set[str] = set()
    results = []

    for folder in all_folders:
        arxiv_id = get_arxiv_id(folder)

        # 跳过已处理的 arxiv_id（避免处理原始 + 标准化后的重复文件夹）
        if arxiv_id in processed_aids:
            continue
        processed_aids.add(arxiv_id)

        # 获取中文标题
        chinese_title = titles.get(arxiv_id, "")
        if not chinese_title:
            # 从文件夹名提取
            parts = folder.name.split("_", 1)
            if len(parts) > 1:
                chinese_title = parts[1]
            else:
                chinese_title = arxiv_id

        # 获取方向标签
        classification = classifications.get(arxiv_id, {})
        direction_tag = PaperClassifier.generate_direction_tag(classification) if classification else ""

        # 构建目标文件夹名（与 standardizer 逻辑一致）
        safe_title = FolderStandardizer._sanitize_title(chinese_title or arxiv_id)
        safe_tag = FolderStandardizer._sanitize_tag(direction_tag) if direction_tag else ""
        desired_name = f"{arxiv_id}_{safe_title}"
        if safe_tag:
            desired_name = f"{desired_name}_{safe_tag}"

        # 检查目标文件夹是否已存在（前次运行已标准化）
        if desired_name in existing_names and folder.name != desired_name:
            logger.info("[Step5] SKIP %s (target already exists: %s)", arxiv_id, desired_name)
            results.append({
                "arxiv_id": arxiv_id,
                "error": None,
                "new_dir": str(PARSED_DIR / desired_name),
                "renamed_files": [],
                "moved_dirs": [],
                "skipped": True,
            })
            continue

        # 找到最佳源文件夹（当前文件夹就是最佳选择，因为它可能是唯一的或第一个）
        logger.info("[Step5] Standardizing %s -> title=%s, tag=%s", arxiv_id, chinese_title[:30], direction_tag)

        try:
            result = standardizer.execute(
                paper_dir=str(folder),
                arxiv_id=arxiv_id,
                chinese_title=chinese_title,
                direction_tag=direction_tag,
                backup=False,
            )

            if result.get("error"):
                logger.error("[Step5] FAILED %s: %s", arxiv_id, result["error"])
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": result["error"],
                })
            else:
                renamed = result.get("renamed_files", [])
                moved = result.get("moved_dirs", [])
                new_dir = result.get("new_dir", "")
                logger.info("[Step5] OK %s: %d renamed, %d moved -> %s",
                           arxiv_id, len(renamed), len(moved), Path(new_dir).name if new_dir else "N/A")
                results.append({
                    "arxiv_id": arxiv_id,
                    "error": None,
                    "new_dir": new_dir,
                    "renamed_files": renamed,
                    "moved_dirs": moved,
                })

        except Exception as e:
            logger.error("[Step5] EXCEPTION %s: %s", arxiv_id, e)
            results.append({"arxiv_id": arxiv_id, "error": str(e)})

    return results


# ======================================================================
# 主入口
# ======================================================================

def main():
    import argparse

    setup_logging()

    parser = argparse.ArgumentParser(description="Batch Pipeline Runner")
    parser.add_argument("--step", required=True, help="Step number (1-5) or 'all'")
    args = parser.parse_args()

    if args.step == "all":
        steps = [
            ("1", step1_mineru_parse),
            ("2", step2_vision_enhance),
            ("3", step3_summarize),
            ("4", step4_classify),
            ("5", step5_standardize),
        ]
    else:
        step_map = {
            "1": step1_mineru_parse,
            "2": step2_vision_enhance,
            "3": step3_summarize,
            "4": step4_classify,
            "5": step5_standardize,
        }
        if args.step not in step_map:
            print(f"Unknown step: {args.step}. Available: {list(step_map.keys())} or 'all'")
            sys.exit(1)
        steps = [(args.step, step_map[args.step])]

    all_logs = []
    for step_num, step_func in steps:
        logger.info("\n" + "#" * 60)
        logger.info("# Starting Step %s", step_num)
        logger.info("#" * 60)

        start_time = time.time()
        results = step_func()
        elapsed = time.time() - start_time

        log_path = save_step_log(int(step_num), results)
        all_logs.append({"step": step_num, "log": str(log_path), "elapsed_sec": elapsed})

        succeeded = sum(1 for r in results if not r.get("error"))
        failed = sum(1 for r in results if r.get("error"))
        logger.info("[Step %s] Done in %.1fs: %d succeeded, %d failed",
                    step_num, elapsed, succeeded, failed)

    # 打印总结
    logger.info("\n" + "=" * 60)
    logger.info("  Batch Pipeline Summary")
    logger.info("=" * 60)
    for entry in all_logs:
        logger.info("  Step %s: %.1fs -> %s", entry["step"], entry["elapsed_sec"], entry["log"])


if __name__ == "__main__":
    main()
