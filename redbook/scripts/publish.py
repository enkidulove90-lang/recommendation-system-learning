"""
redbook/scripts/publish.py — 统一论文发布入口

整合直接 API 发布（上传 PDF + 图片 + 话题全自动）与可选的知识图谱分析增强。

用法:
  # 基础发布（不加 --kg，直接 API 发布含 PDF）
  python publish.py --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --topic "推荐系统" --topic "LLM"

  # 带知识图谱的增强发布
  python publish.py --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --topic "推荐系统" --kg

  # 干跑预览
  python publish.py --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --kg --dry-run

设计原则:
  - 不加 --kg: 主链路完全保持现有行为，直接把 Paper 发布到 xhs
  - 加 --kg: 主链路 + 分析增强层（A1→A2→A3→A4→A5），任何步骤失败自动降级
  - 分析层完全解耦，通过文件 I/O 通信，不修改现有代码
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from config import settings
from utils.helpers import setup_logging

logger = logging.getLogger(__name__)

# ======================================================================
# 路径常量
# ======================================================================

PROJECT_ROOT = _PROJECT_ROOT
SUMMARIES_DIR = PROJECT_ROOT / "data" / "summaries"
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"


# ======================================================================
# 论文数据查找
# ======================================================================

def find_summary(arxiv_id: str) -> str | None:
    """查找论文摘要 Markdown 文件。"""
    for f in SUMMARIES_DIR.iterdir():
        if f.name.startswith(arxiv_id) and f.name.endswith("_summary.md"):
            return str(f)
    return None


def find_summary_json(arxiv_id: str) -> str | None:
    """查找论文摘要 JSON 文件。"""
    for f in SUMMARIES_DIR.iterdir():
        if f.name.startswith(arxiv_id) and f.name.endswith("_summary.json"):
            return str(f)
    return None


def find_parsed_dir(arxiv_id: str) -> str | None:
    """查找论文解析目录。"""
    for d in PARSED_DIR.iterdir():
        if d.is_dir() and d.name.startswith(arxiv_id):
            return str(d)
    return None


def find_images(arxiv_id: str, count: int = 5) -> list[str]:
    """查找论文架构图片（优先 Figure 1-3）。"""
    parsed = find_parsed_dir(arxiv_id)
    if not parsed:
        return []

    # 优先 test_images/ 或 images_hd/
    for sub in ["test_images", "images_hd", "images"]:
        img_dir = Path(parsed) / sub
        if img_dir.is_dir():
            images = sorted(
                [str(img_dir / f) for f in os.listdir(img_dir)
                 if f.lower().endswith((".png", ".jpg", ".jpeg"))],
                # 优先架构图
                key=lambda x: (0 if any(kw in os.path.basename(x).lower()
                    for kw in ["framework", "model", "illustration", "overview", "arch"])
                    else 1, x),
            )
            return images[:count]

    return []


def find_pdf(arxiv_id: str) -> str | None:
    """查找论文 PDF 文件。"""
    parsed = find_parsed_dir(arxiv_id)
    if not parsed:
        return None
    for f in Path(parsed).iterdir():
        if f.suffix.lower() == ".pdf":
            return str(f)
    return None


def load_paper_metadata(arxiv_id: str) -> dict:
    """从 papers_metadata.json 加载论文元数据。"""
    meta_path = settings.DATA_DIR / "papers_metadata.json"
    if not meta_path.exists():
        return {}

    try:
        all_papers = json.loads(meta_path.read_text(encoding="utf-8"))
        for paper in all_papers:
            if paper.get("arxiv_id", "").startswith(arxiv_id):
                return paper
    except (json.JSONDecodeError, KeyError):
        pass
    return {}


# ======================================================================
# 正文格式化
# ======================================================================

def format_body_from_summary(summary_text: str, arxiv_id: str, github_url: str = "") -> str:
    """
    从基础摘要格式化小红书面板正文（不加 --kg 时使用）。
    与现有 publish_paper.py 的 format_body() 行为一致。
    """
    text = re.sub(r'^# .*?\n\n', '', summary_text)
    text = re.sub(r'\*\*英文标题\*\*: .*?\n', '', text)
    text = re.sub(r'\*\*arXiv ID\*\*: .*?\n', '', text)
    text = re.sub(r'\*\*生成时间\*\*: .*?\n', '', text)
    text = re.sub(r'\n---\n.*$', '', text.strip(), flags=re.DOTALL) + '\n'

    section_map = [
        ('主要贡献', '🌟  核心贡献', 500),
        ('创新点', '🔍 关键创新', 500),
        ('方法论', '🧠 核心设计', 600),
        ('Benchmark', '📊 实验设置', 300),
        ('实验效果', '📊 实验效果', 400),
        ('对推荐系统', '💡 借鉴价值', 400),
    ]

    parts = re.split(r'\n## ', text)
    body_sections = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        for keyword, emoji, limit in section_map:
            if part.startswith(keyword):
                content_lines = part.split('\n', 1)
                content = content_lines[1] if len(content_lines) > 1 else ''
                content = re.sub(r'^\d+\.\s*创新点\d+[：:]', '• ', content, flags=re.MULTILINE)
                content = re.sub(r'^\d+\)\s*', '• ', content, flags=re.MULTILINE)
                content = re.sub(r'^- ', '• ', content, flags=re.MULTILINE)
                content = re.sub(r'\*\*', '', content)
                content = re.sub(r'\n{2,}', '\n', content).strip()
                content = content[:limit]
                if content:
                    body_sections.append(f'{emoji}\n{content}')
                break

    body = '\n\n'.join(body_sections)
    body += f'\n\narxiv 🔗：https://arxiv.org/abs/{arxiv_id}'
    if github_url:
        body += f'\ngithub 🔗：{github_url}'
    body += f'\n📎 原文 PDF：https://arxiv.org/pdf/{arxiv_id}'

    return body


# ======================================================================
# 分析增强层 (--kg 时触发)
# ======================================================================

def run_kg_analysis(arxiv_id: str, parsed_dir: str, metadata: dict) -> dict:
    """
    运行完整的分析增强流水线（A1→A2→A3→A4→A5）。

    返回:
        {
            "enriched_narrative_path": str | None,
            "enriched_images": [str, ...],
            "quality_score": float,
            "quality_decision": "full_analysis" | "basic_only",
            "errors": [str, ...],   # 每步的错误（不阻塞）
            "steps_completed": [str, ...],
        }
    """
    from skills.citation_collector import CitationCollector
    from skills.graph_builder import GraphBuilder
    from skills.quality_scorer import QualityScorer
    from skills.narrative_generator import NarrativeGenerator
    from skills.graph_visualizer import GraphVisualizer

    result = {
        "enriched_narrative_path": None,
        "enriched_images": [],
        "quality_score": 0.0,
        "quality_decision": "basic_only",
        "errors": [],
        "steps_completed": [],
    }

    # ---- A1: 引用采集 ----
    print("\n[A1] 引用数据采集...")
    try:
        collector = CitationCollector()
        a1_result = collector.execute(
            arxiv_id=arxiv_id,
            parsed_dir=parsed_dir,
            metadata=metadata,
            sources=["pdf_refs", "semantic_scholar"],
        )
        if a1_result.get("error"):
            logger.warning("A1 partial error: %s", a1_result["error"])
            result["errors"].append(f"A1: {a1_result['error']}")
        result["steps_completed"].append("A1_citation_collect")
        print(f"  [OK] 参考文献: {len(a1_result.get('references', []))} 篇")
        print(f"  [OK] 被引: {len(a1_result.get('citations', []))} 次")
        print(f"  [OK] 数据源: {', '.join(a1_result.get('sources_used', []))}")
    except Exception as exc:
        logger.warning("A1 failed: %s", exc)
        result["errors"].append(f"A1: {exc}")
        a1_result = {"references": [], "citations": [], "related": []}
        print(f"  [WARN] 失败: {exc}")

    # ---- A2: 图谱构建 ----
    print("\n[A2] 图谱构建...")
    academic_graph = None
    try:
        builder = GraphBuilder()
        if not builder.is_ready:
            logger.warning("A2: DeepSeek API not configured, using metadata only")
        a2_result = builder.execute(
            arxiv_id=arxiv_id,
            references=a1_result.get("references", []),
            citations=a1_result.get("citations", []),
            related=a1_result.get("related", []),
            metadata=metadata,
        )
        if a2_result.get("error"):
            logger.warning("A2 failed: %s", a2_result["error"])
            result["errors"].append(f"A2: {a2_result['error']}")
        else:
            academic_graph = a2_result.get("academic_graph")
            result["steps_completed"].append("A2_graph_build")
            stats = academic_graph.get("statistics", {}) if academic_graph else {}
            print(f"  [OK] 图谱节点: {len(academic_graph.get('citation_graph', {}).get('nodes', [])) if academic_graph else 0}")
            print(f"  [OK] 总引用: {stats.get('total_references', 0)} 篇")
    except Exception as exc:
        logger.warning("A2 failed: %s", exc)
        result["errors"].append(f"A2: {exc}")
        print(f"  [WARN] 失败: {exc}")

    if not academic_graph:
        return result  # 无法继续后续步骤

    # ---- A3: 质量评分 ----
    print("\n[A3] 质量评分...")
    try:
        # 加载基础摘要
        summary = {}
        summary_json = find_summary_json(arxiv_id)
        if summary_json:
            summary = json.loads(Path(summary_json).read_text(encoding="utf-8"))

        scorer = QualityScorer()
        a3_result = scorer.execute(
            arxiv_id=arxiv_id,
            academic_graph=academic_graph,
            summary=summary,
        )
        result["quality_score"] = a3_result.get("score", 0.0)
        result["quality_decision"] = a3_result.get("decision", "basic_only")
        result["steps_completed"].append("A3_quality_score")
        print(f"  [OK] 综合评分: {result['quality_score']:.2f}")
        print(f"  [OK] 决策: {result['quality_decision']}")
        print(f"  [OK] 各维度: {json.dumps(a3_result.get('dimensions', {}), ensure_ascii=False)}")
    except Exception as exc:
        logger.warning("A3 failed: %s", exc)
        result["errors"].append(f"A3: {exc}")
        result["quality_decision"] = "basic_only"  # 安全降级
        print(f"  [WARN] 失败: {exc}, 降级为基础发布")

    # 低分 → 跳过 A4/A5
    threshold = settings.QUALITY_THRESHOLD
    if result["quality_score"] < threshold:
        logger.info(
            "Score %.2f < threshold %.2f, skipping A4/A5", result["quality_score"], threshold
        )
        print(f"\n  [SKIP] 评分 ({result['quality_score']:.2f}) < 阈值 ({threshold}), 跳过 A4/A5")
        return result

    # ---- A4: 叙事生成 ----
    print("\n[A4] 增强叙事生成...")
    try:
        summary = {}
        summary_json = find_summary_json(arxiv_id)
        if summary_json:
            summary = json.loads(Path(summary_json).read_text(encoding="utf-8"))

        gen = NarrativeGenerator()
        a4_result = gen.execute(
            arxiv_id=arxiv_id,
            academic_graph=academic_graph,
            summary=summary,
            timeline={},
            template="auto",
        )
        if a4_result.get("error"):
            logger.warning("A4 failed: %s", a4_result["error"])
            result["errors"].append(f"A4: {a4_result['error']}")
        else:
            result["enriched_narrative_path"] = a4_result.get("narrative_path")
            result["steps_completed"].append("A4_narrative_generate")
            print(f"  [OK] 叙事文案: {a4_result.get('narrative_path', '')}")
            sections = a4_result.get("sections", {})
            for key in ["core_contribution", "lineage", "citation_network"]:
                if sections.get(key):
                    print(f"    - {key}: {len(sections[key])} chars")
    except Exception as exc:
        logger.warning("A4 failed: %s", exc)
        result["errors"].append(f"A4: {exc}")
        print(f"  [WARN] 失败: {exc}")

    # ---- A5: 图谱可视化 ----
    print("\n[A5] 图谱可视化...")
    try:
        viz = GraphVisualizer()
        if not viz.is_ready:
            logger.warning("A5: matplotlib/networkx not available, skipping")
            result["errors"].append("A5: matplotlib/networkx not installed")
            print("  [WARN] matplotlib/networkx 不可用, 跳过")
        else:
            a5_result = viz.execute(
                arxiv_id=arxiv_id,
                academic_graph=academic_graph,
                output_types=["citation_graph", "timeline"],
            )
            if a5_result.get("error"):
                logger.warning("A5 partial: %s", a5_result["error"])
                result["errors"].append(f"A5: {a5_result['error']}")
            for img in a5_result.get("images", []):
                result["enriched_images"].append(img["path"])
            result["steps_completed"].append("A5_graph_visualize")
            print(f"  [OK] 生成图片: {len(a5_result.get('images', []))} 张")
            for img in a5_result.get("images", []):
                print(f"    - {os.path.basename(img['path'])}")
    except Exception as exc:
        logger.warning("A5 failed: %s", exc)
        result["errors"].append(f"A5: {exc}")
        print(f"  [WARN] 失败: {exc}")

    return result


# ======================================================================
# 发布（xhs_cli API）
# ======================================================================

def publish_to_xhs(
    title: str,
    body: str,
    images: list[str],
    topics: list[str],
    pdf_path: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    发布到小红书（直接 API 模式，含 PDF 附件）。

    复用 publish_ssr_final.py 和 publish_with_pdf.py 的已验证代码路径。
    """
    if dry_run:
        print("\n" + "=" * 60)
        print("  DRY RUN — 不实际发布")
        print("=" * 60)
        print(f"  Title: {title} ({len(title)} chars)")
        print(f"  Body: {len(body)} chars")
        print(f"  Images: {len(images)}")
        for img in images:
            print(f"    - {os.path.basename(img)}")
        print(f"  Topics: {topics}")
        if pdf_path:
            print(f"  PDF: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path):,} bytes)")
        print(f"\nBody preview (first 500 chars):")
        try:
            print(body[:500])
        except UnicodeEncodeError:
            print(body[:500].encode("ascii", errors="replace").decode("ascii"))
        return {"ok": True, "dry_run": True}

    # ---- 真实发布 ----
    try:
        import mimetypes
        from xhs_cli.commands._common import get_cookies
        from xhs_cli.client import XhsClient
        from xhs_cli.constants import CREATOR_HOST, UPLOAD_HOST

        print("\n[发布] 连接小红书 API...")

        # 认证
        browser_name, cookies = get_cookies("auto")
        client = XhsClient(cookies)

        with client:
            # Step 1: 上传 PDF（如果有）
            pdf_file_id = None
            pdf_doc_id = None
            if pdf_path and os.path.exists(pdf_path):
                print(f"  [1/4] 上传 PDF: {os.path.basename(pdf_path)}...")

                # 获取 doc_id
                doc = client._creator_post("/api/galaxy/v2/creator/doc/gen_id", {})
                pdf_doc_id = str(doc["id"])

                # 获取上传许可
                pdf_permit = client._creator_get(
                    "/api/media/v1/upload/creator/permit",
                    {
                        "biz_name": "sns", "scene": "web_doc",
                        "file_count": 1, "version": 1, "source": "web",
                    },
                )
                pp = pdf_permit["uploadTempPermits"][0]
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()
                pdf_url = f"https://{pp['uploadAddr']}/{pp['fileIds'][0]}"
                r = client._request_with_retry(
                    "PUT", pdf_url,
                    headers={"X-Cos-Security-Token": pp["token"], "Content-Type": "application/pdf"},
                    content=pdf_data,
                )
                pdf_file_id = pp["fileIds"][0]
                pdf_size = len(pdf_data)
                print(f"    [OK] PDF 上传完成 ({pdf_size:,} bytes)")

            # Step 2: 上传图片
            print(f"  [2/4] 上传图片 ({len(images)} 张)...")
            image_fids = []
            for img_path in images:
                img_name = os.path.basename(img_path)
                ip = client._creator_get(
                    "/api/media/v1/upload/creator/permit",
                    {
                        "biz_name": "spectrum", "scene": "image",
                        "file_count": 1, "version": 1, "source": "web",
                    },
                )
                ipp = ip["uploadTempPermits"][0]
                with open(img_path, "rb") as f:
                    img_data = f.read()
                img_url = f"https://{ipp['uploadAddr']}/{ipp['fileIds'][0]}"
                content_type = mimetypes.guess_type(img_path)[0] or "image/jpeg"
                client._request_with_retry(
                    "PUT", img_url,
                    headers={"X-Cos-Security-Token": ipp["token"], "Content-Type": content_type},
                    content=img_data,
                )
                image_fids.append(ipp["fileIds"][0])
                print(f"    [OK] {img_name} ({len(img_data):,} bytes)")
                time.sleep(0.5)

            # Step 3: 搜索话题 ID
            print(f"  [3/4] 搜索话题 ({len(topics)} 个)...")
            topic_payloads = []
            for t in topics:
                try:
                    data = client.search_topics(t)
                    items = data.get("topic_info_dtos", [])
                    if items:
                        best = items[0]
                        topic_payloads.append({
                            "id": best.get("id", ""),
                            "name": best.get("name", t),
                            "type": "topic",
                        })
                        print(f"    [OK] {t}: id={best.get('id', '?')}")
                    else:
                        topic_payloads.append({"id": "", "name": t, "type": "topic"})
                        print(f"    [WARN] {t}: 未找到，使用 fallback")
                except Exception:
                    topic_payloads.append({"id": "", "name": t, "type": "topic"})
                time.sleep(0.3)

            # Step 4: 创建笔记
            print("  [4/4] 创建笔记...")
            images_payload = [
                {"file_id": fid, "metadata": {"source": -1}} for fid in image_fids
            ]

            business_binds = json.dumps({
                "version": 1, "noteId": 0,
                "noteOrderBind": {},
                "notePostTiming": {"postTime": None},
                "noteCollectionBind": {"id": ""},
            })

            payload = {
                "common": {
                    "type": "normal", "title": title, "note_id": "",
                    "desc": body,
                    "source": '{"type":"web","ids":"","extraInfo":"{\\"subType\\":\\"official\\"}"}',
                    "business_binds": business_binds,
                    "ats": [], "hash_tag": topic_payloads, "post_loc": {},
                    "privacy_info": {"op_type": 1, "type": 0},
                },
                "image_info": {"images": images_payload},
                "video_info": None,
            }

            # 附加 PDF
            if pdf_file_id and pdf_doc_id:
                payload["related_file"] = {
                    "file_id": pdf_file_id,
                    "name": os.path.basename(pdf_path) if pdf_path else "paper.pdf",
                    "size": pdf_size if pdf_size else 0,
                    "type": "pdf",
                }

            result = client._main_api_post(
                "/web_api/sns/v2/note", payload,
                {"origin": CREATOR_HOST, "referer": f"{CREATOR_HOST}/"},
            )

            note_id = result.get("data", {}).get("id", result.get("id", ""))
            if note_id:
                print(f"\n  [OK] Published!")
                print(f"  Note ID: {note_id}")
                print(f"  URL: https://www.xiaohongshu.com/explore/{note_id}")
                print(f"  Images: {len(image_fids)}")
                print(f"  Topics: {len(topic_payloads)}")
                if pdf_file_id:
                    print(f"  PDF: [OK]")
                return {"ok": True, "note_id": note_id, "url": f"https://www.xiaohongshu.com/explore/{note_id}"}
            else:
                print(f"\n  [ERROR] 发布失败: {json.dumps(result, ensure_ascii=False)[:500]}")
                return {"ok": False, "error": str(result)[:500]}

    except ImportError as exc:
        print(f"\n  [ERROR] 缺少依赖: {exc}")
        print("  请安装: pip install xiaohongshu-cli")
        return {"ok": False, "error": f"Missing dependency: {exc}"}
    except Exception as exc:
        logger.error("Publish failed: %s", exc)
        print(f"\n  [ERROR] 发布异常: {exc}")
        return {"ok": False, "error": str(exc)}


# ======================================================================
# 主入口
# ======================================================================

def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="统一论文发布入口 — 直接 API 发布 + 可选知识图谱增强",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础发布（不加 --kg）
  python publish.py --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --topic "推荐系统" --topic "LLM"

  # 带知识图谱增强
  python publish.py --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --kg

  # 干跑预览
  python publish.py --arxiv-id 2605.28175 --title "KDD26｜MixRAGRec" --kg --dry-run
        """,
    )
    parser.add_argument("--arxiv-id", required=True, help="arXiv ID (e.g. 2605.28175)")
    parser.add_argument("--title", required=True, help="帖子标题 (≤20 chars)")
    parser.add_argument("--topic", action="append", default=[], help="话题标签 (可多次指定)")
    parser.add_argument("--github", default="", help="GitHub URL (可选)")
    parser.add_argument("--kg", action="store_true", help="启用知识图谱分析增强")
    parser.add_argument("--dry-run", action="store_true", help="仅打印预览，不发布")
    parser.add_argument("--image-count", type=int, default=5, help="论文图片数量 (默认5)")
    args = parser.parse_args()

    arxiv_id = args.arxiv_id

    # ================================================================
    # 基础数据查找（无论加不加 --kg 都需要）
    # ================================================================

    print("=" * 60)
    print(f"  Paper Publisher — {arxiv_id}")
    print(f"  Mode: {'KG-enhanced' if args.kg else 'Basic'}")
    print("=" * 60)

    # 查找摘要
    summary_path = find_summary(arxiv_id)
    if not summary_path:
        print(f"[ERROR] 未找到摘要: data/summaries/{arxiv_id}_*_summary.md")
        sys.exit(1)
    print(f"[OK] 摘要: {os.path.basename(summary_path)}")

    summary_text = Path(summary_path).read_text(encoding="utf-8")

    # 查找图片
    images = find_images(arxiv_id, args.image_count)
    print(f"[OK] 论文图片: {len(images)} 张")

    # 查找 PDF
    pdf_path = find_pdf(arxiv_id)
    if pdf_path:
        print(f"[OK] PDF: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path):,} bytes)")
    else:
        print("[WARN] 未找到 PDF 文件，将不带附件发布")

    # 加载元数据
    metadata = load_paper_metadata(arxiv_id)
    if metadata:
        print(f"[OK] 元数据: {metadata.get('title', '')[:60]}...")

    # ================================================================
    # 分析增强层（仅 --kg 时）
    # ================================================================

    body = ""
    enriched_images: list[str] = []
    analysis_result = None

    if args.kg:
        print("\n" + "-" * 40)
        print("  知识图谱分析增强")
        print("-" * 40)

        parsed_dir = find_parsed_dir(arxiv_id) or str(PARSED_DIR / arxiv_id)

        analysis_result = run_kg_analysis(arxiv_id, parsed_dir, metadata)

        # 使用 enhanced narrative（如果生成成功）
        if analysis_result.get("enriched_narrative_path"):
            enriched_path = Path(analysis_result["enriched_narrative_path"])
            if enriched_path.exists():
                body = enriched_path.read_text(encoding="utf-8")
                # 追加链接
                body += f"\n\n📄 arXiv：https://arxiv.org/abs/{arxiv_id}"
                body += f"\n📎 PDF：https://arxiv.org/pdf/{arxiv_id}"
                if args.github:
                    body += f"\n💻 GitHub：{args.github}"

        # 图谱图片
        enriched_images = analysis_result.get("enriched_images", [])

        # 降级检查：如果 enhanced narrative 为空，使用基础摘要
        if not body:
            print("\n  [WARN] 增强叙事不可用，降级为基础摘要")
            body = format_body_from_summary(summary_text, arxiv_id, args.github)

        # 报告分析结果
        print(f"\n{'='*40}")
        print(f"  分析层结果:")
        print(f"    质量评分: {analysis_result.get('quality_score', 0):.2f}")
        print(f"    决策: {analysis_result.get('quality_decision', 'basic_only')}")
        print(f"    完成步骤: {', '.join(analysis_result.get('steps_completed', []))}")
        if analysis_result.get("errors"):
            print(f"    降级/警告: {len(analysis_result['errors'])} 项")
            for e in analysis_result["errors"]:
                print(f"      - {e}")
    else:
        # 不加 --kg: 使用基础摘要格式化
        body = format_body_from_summary(summary_text, arxiv_id, args.github)

    # ================================================================
    # 组装最终图片列表
    # ================================================================

    final_images = []
    # 优先图谱图片（至多 2 张）
    for img in enriched_images[:2]:
        if os.path.exists(img):
            final_images.append(img)
    # 补充论文图片（至多 5 张总数）
    remaining = args.image_count - len(final_images)
    for img in images[:remaining]:
        if os.path.exists(img):
            final_images.append(img)

    # ================================================================
    # 话题默认值
    # ================================================================

    topics = args.topic or ["推荐系统", "LLM", "论文分享", "AI"]

    # ================================================================
    # 发布
    # ================================================================

    result = publish_to_xhs(
        title=args.title,
        body=body,
        images=final_images,
        topics=topics,
        pdf_path=pdf_path,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print(f"\n[OK] DRY RUN 完成")

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
