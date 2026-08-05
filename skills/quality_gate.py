"""
skills/quality_gate.py — 管线阶段间质量门控

在解析 -> 摘要 -> 整理 各阶段之间执行质量校验，
确保每个阶段的输出满足最低质量标准后才进入下一阶段。

质量门类型：
  G1 — 解析质量门：检查 MinerU 解析结果是否完整
  G2 — 视觉增强质量门：检查 _figures.json 是否生成且非空
  G3 — 摘要质量门：检查 11 维度字段完整度
  G4 — 分类质量门：检查 taxonomies 标签是否合规
  G5 — 文件夹标准化质量门：检查文件夹结构和命名
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from config import settings

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# 11 维度字段定义（用于 G3 摘要质量门）
# ------------------------------------------------------------------

REQUIRED_DIMENSIONS = [
    "paper_id",
    "title_zh",
    "title_en",
    "paper_type",
    "venue",
    "year",
    "problem_definition",
    "innovations",
    "modules",
    "training",
    "datasets",
    "benchmark",
    "related_papers",
    "reproducibility",
    "limitations",
]

# 各维度的子字段（用于深度检查）
DIMENSION_SUBFIELDS = {
    "problem_definition": ["task_type", "input", "output"],
    "innovations": ["point", "category", "source"],
    "modules": ["name", "role", "input", "output", "source"],
    "training": ["loss", "negative_sampling", "optimizer", "pretrain"],
    "datasets": ["name", "users", "items", "interactions", "split"],
    "benchmark": ["metrics", "baselines", "main_results"],
    "related_papers": ["ref_id", "relation", "summary"],
    "reproducibility": ["code_open", "data_open", "hyperparams_complete"],
}

# 允许为"论文未提及"的字段（不计为缺失）
OPTIONAL_FIELDS = {"venue", "limitations"}


class QualityGate:
    """
    管线质量门控器。

    使用示例:
        gate = QualityGate()
        result = gate.check_parse(paper_dir="data/parsed/2505.19525_ConfSMoE")
        if not result["passed"]:
            print(result["issues"])
    """

    def __init__(self, logs_dir: str = "") -> None:
        self.logs_dir = Path(logs_dir) if logs_dir else settings.DATA_DIR / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # G1: 解析质量门
    # ------------------------------------------------------------------

    def check_parse(self, paper_dir: str, arxiv_id: str = "") -> dict[str, Any]:
        """
        检查 MinerU 解析结果是否完整。

        通过条件：
        - 存在 .md 文件且非空
        - 存在 images/ 目录（vlm 模式应提取图片）
        - .md 文件字符数 >= 500（排除空白解析）
        """
        paper_path = Path(paper_dir)
        issues: list[str] = []

        # 查找 .md 文件
        md_files = list(paper_path.glob("*.md"))
        if not md_files:
            issues.append("无 .md 文件——解析失败或未执行")
        else:
            # 取最大的 .md 文件作为全文
            md_file = max(md_files, key=lambda f: f.stat().st_size)
            try:
                text = md_file.read_text(encoding="utf-8")
                char_count = len(text.strip())
                if char_count < 500:
                    issues.append(f".md 文件内容过短（{char_count} 字符），可能解析不完整")
            except (UnicodeDecodeError, OSError) as e:
                issues.append(f"无法读取 .md 文件: {e}")

        # 检查 images/ 目录
        images_dir = paper_path / "images"
        if not images_dir.exists():
            issues.append("无 images/ 目录——可能未使用 vlm 模式")
        else:
            image_count = len([
                f for f in images_dir.iterdir()
                if f.suffix.lower() in (".jpg", ".png", ".jpeg", ".gif", ".webp")
            ])
            if image_count == 0:
                issues.append("images/ 目录为空")

        # 检查 _content.json（MinerU 结构化输出）
        content_json = list(paper_path.glob("*_content.json"))
        if not content_json:
            issues.append("无 _content.json——MinerU 结构化输出缺失")

        passed = len(issues) == 0
        return {
            "gate": "G1_parse",
            "passed": passed,
            "issues": issues,
            "paper_dir": str(paper_path),
            "arxiv_id": arxiv_id,
            "checked_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # G2: 视觉增强质量门
    # ------------------------------------------------------------------

    def check_vision(self, paper_dir: str, arxiv_id: str = "") -> dict[str, Any]:
        """
        检查 _figures.json 是否已生成且内容非空。
        """
        paper_path = Path(paper_dir)
        issues: list[str] = []

        figures_path = paper_path / f"{arxiv_id}_figures.json"
        if not figures_path.exists():
            issues.append(f"无 {arxiv_id}_figures.json——视觉增强未执行")
        else:
            try:
                data = json.loads(figures_path.read_text(encoding="utf-8"))
                figures = data.get("figures", [])
                if not figures:
                    issues.append("_figures.json 为空——视觉理解未产出任何描述")
                else:
                    # 检查是否有 architecture 类型的描述
                    arch_count = sum(1 for f in figures if f.get("figure_type") == "architecture")
                    table_count = sum(1 for f in figures if f.get("figure_type") == "result_table")
                    if arch_count == 0 and table_count == 0:
                        issues.append("未识别到架构图或结果表——可能图片分类有误")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                issues.append(f"_figures.json 解析失败: {e}")

        passed = len(issues) == 0
        return {
            "gate": "G2_vision",
            "passed": passed,
            "issues": issues,
            "paper_dir": str(paper_path),
            "arxiv_id": arxiv_id,
            "checked_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # G3: 摘要质量门
    # ------------------------------------------------------------------

    def check_summary(self, summary_json_path: str) -> dict[str, Any]:
        """
        检查摘要 JSON 的 11 维度字段完整度。

        通过条件：
        - 必需字段完整度 >= 80%
        - 每条结论有 source 标注（innovations/modules 至少有一项有 source）
        - 非"论文未提及"的字段有实际内容
        """
        issues: list[str] = []
        summary_path = Path(summary_json_path)

        if not summary_path.exists():
            return {
                "gate": "G3_summary",
                "passed": False,
                "issues": ["摘要 JSON 文件不存在"],
                "completeness": 0.0,
                "checked_at": datetime.now().isoformat(),
            }

        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return {
                "gate": "G3_summary",
                "passed": False,
                "issues": [f"JSON 解析失败: {e}"],
                "completeness": 0.0,
                "checked_at": datetime.now().isoformat(),
            }

        # 逐字段检查
        total_fields = len(REQUIRED_DIMENSIONS)
        present_fields = 0

        for field in REQUIRED_DIMENSIONS:
            value = data.get(field)
            if field in OPTIONAL_FIELDS:
                # 可选字段，有就算有，没有也不扣分
                if value is not None and str(value).strip():
                    present_fields += 1
                continue

            if value is None:
                issues.append(f"字段 '{field}' 缺失")
            elif isinstance(value, str) and not value.strip():
                issues.append(f"字段 '{field}' 为空字符串")
            elif isinstance(value, (list, dict)) and len(value) == 0:
                issues.append(f"字段 '{field}' 为空列表/字典")
            else:
                present_fields += 1

        completeness = present_fields / total_fields

        # 检查 source 标注
        innovations = data.get("innovations", [])
        if isinstance(innovations, list) and innovations:
            has_source = any(
                isinstance(inv, dict) and inv.get("source")
                for inv in innovations
            )
            if not has_source:
                issues.append("创新点列表缺少 source 标注（无原文定位）")

        modules = data.get("modules", [])
        if isinstance(modules, list) and modules:
            has_source = any(
                isinstance(mod, dict) and mod.get("source")
                for mod in modules
            )
            if not has_source:
                issues.append("模块列表缺少 source 标注（无原文定位）")

        # 完整度阈值
        threshold = 0.80
        if completeness < threshold:
            issues.append(f"字段完整度 {completeness:.0%} 低于阈值 {threshold:.0%}")

        passed = len(issues) == 0
        return {
            "gate": "G3_summary",
            "passed": passed,
            "issues": issues,
            "completeness": round(completeness, 4),
            "total_fields": total_fields,
            "present_fields": present_fields,
            "checked_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # G4: 分类质量门
    # ------------------------------------------------------------------

    def check_classification(self, paper_dir: str, arxiv_id: str = "") -> dict[str, Any]:
        """
        检查论文分类标签是否合规（使用 taxonomies.yaml 受控词表）。
        """
        paper_path = Path(paper_dir)
        issues: list[str] = []

        # 加载 taxonomies
        taxonomies_path = settings.DATA_DIR / "registry" / "taxonomies.yaml"
        if not taxonomies_path.exists():
            return {
                "gate": "G4_classification",
                "passed": False,
                "issues": ["taxonomies.yaml 不存在"],
                "checked_at": datetime.now().isoformat(),
            }

        try:
            import yaml
            taxonomies = yaml.safe_load(taxonomies_path.read_text(encoding="utf-8"))
        except Exception as e:
            return {
                "gate": "G4_classification",
                "passed": False,
                "issues": [f"taxonomies.yaml 解析失败: {e}"],
                "checked_at": datetime.now().isoformat(),
            }

        # 从 papers.jsonl 中查找该论文的分类
        papers_jsonl = settings.DATA_DIR / "registry" / "papers.jsonl"
        paper_record = None
        if papers_jsonl.exists():
            for line in papers_jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if record.get("arxiv_id") == arxiv_id:
                        paper_record = record
                        break
                except json.JSONDecodeError:
                    continue

        if not paper_record:
            issues.append(f"论文 {arxiv_id} 不在 papers.jsonl 中")
        else:
            classification = paper_record.get("classification", {})

            # 检查各标签是否使用受控词表
            valid_directions = set(taxonomies.get("research_directions", {}).keys())
            directions = classification.get("research_directions", [])
            if not directions:
                issues.append("research_directions 为空")
            else:
                for d in directions:
                    if d not in valid_directions:
                        issues.append(f"research_direction '{d}' 不在受控词表中")

            valid_paradigms = set(taxonomies.get("technical_paradigms", {}).keys())
            paradigms = classification.get("technical_paradigms", [])
            for p in paradigms:
                if p not in valid_paradigms:
                    issues.append(f"technical_paradigm '{p}' 不在受控词表中")

            valid_types = set(taxonomies.get("paper_type", {}).keys())
            ptype = classification.get("paper_type", "")
            if ptype and ptype not in valid_types:
                issues.append(f"paper_type '{ptype}' 不在受控词表中")

        passed = len(issues) == 0
        return {
            "gate": "G4_classification",
            "passed": passed,
            "issues": issues,
            "paper_dir": str(paper_path),
            "arxiv_id": arxiv_id,
            "checked_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # G5: 文件夹标准化质量门
    # ------------------------------------------------------------------

    def check_folder_standard(self, paper_dir: str, arxiv_id: str = "") -> dict[str, Any]:
        """
        检查文件夹是否已标准化（命名 + 内部结构）。
        """
        paper_path = Path(paper_dir)
        folder_name = paper_path.name
        issues: list[str] = []

        # 检查命名格式：{arXiv ID}_{标题}_[方向标签]
        # 方向标签可选
        pattern = r"^\d{4}\.\d{4,5}_.+"
        if not re.match(pattern, folder_name):
            issues.append(f"文件夹名 '{folder_name}' 不符合标准格式 {{arXiv ID}}_{{标题}}")

        # 检查是否有方向标签
        has_direction_tag = bool(re.search(r"\[.+_.+\]", folder_name))
        if not has_direction_tag:
            issues.append("文件夹名缺少方向标签 [方向A×方向B]")

        # 检查内部结构
        expected_files = {
            "md": list(paper_path.glob("*.md")),
            "content_json": list(paper_path.glob("*_content.json")),
            "figures_json": list(paper_path.glob("*_figures.json")),
            "origin_pdf": list(paper_path.glob("*_origin.pdf")),
            "images_dir": paper_path / "images",
        }

        if not expected_files["md"]:
            issues.append("缺少 .md 全文文件")
        if not expected_files["content_json"]:
            issues.append("缺少 _content.json")
        if not expected_files["figures_json"]:
            issues.append("缺少 _figures.json（视觉描述）")
        if not expected_files["origin_pdf"]:
            issues.append("缺少 _origin.pdf（原始 PDF）")
        if not expected_files["images_dir"].exists():
            issues.append("缺少 images/ 目录")

        # 检查是否有非标准文件/目录
        standard_names = {".md", "_content.json", "_content_full.json", "_layout.json",
                         "_model.json", "_figures.json", "_origin.pdf", "_result.zip"}
        standard_dirs = {"images", "images_hd", "arxiv_source"}

        for item in paper_path.iterdir():
            if item.is_file():
                # 检查文件名是否为标准格式
                is_standard = any(
                    item.name.endswith(suffix) or item.name == f"{arxiv_id}{suffix}"
                    for suffix in standard_names
                )
                if not is_standard and not item.name.startswith("."):
                    # 允许 .md 文件以 arxiv_id 命名
                    if item.suffix == ".md":
                        continue
                    issues.append(f"非标准文件: {item.name}")
            elif item.is_dir() and item.name not in standard_dirs:
                issues.append(f"非标准目录: {item.name}")

        passed = len(issues) == 0
        return {
            "gate": "G5_folder",
            "passed": passed,
            "issues": issues,
            "paper_dir": str(paper_path),
            "arxiv_id": arxiv_id,
            "checked_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # 批量检查 + 日志记录
    # ------------------------------------------------------------------

    def batch_check(
        self,
        papers: list[dict[str, str]],
        gate_type: str = "G1_parse",
    ) -> dict[str, Any]:
        """
        批量执行质量门检查。

        参数:
            papers    : [{"paper_dir": "...", "arxiv_id": "..."}]
            gate_type : "G1_parse" | "G2_vision" | "G3_summary" | "G4_classification" | "G5_folder"

        返回:
            {
                "gate": str,
                "total": int,
                "passed": int,
                "failed": int,
                "results": list[dict],
                "log_path": str,
            }
        """
        gate_map = {
            "G1_parse": self.check_parse,
            "G2_vision": self.check_vision,
            "G4_classification": self.check_classification,
            "G5_folder": self.check_folder_standard,
        }

        check_fn = gate_map.get(gate_type)
        if not check_fn:
            return {
                "gate": gate_type,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "results": [],
                "error": f"Unknown gate type: {gate_type}",
            }

        results = []
        passed_count = 0

        for paper in papers:
            paper_dir = paper.get("paper_dir", "")
            arxiv_id = paper.get("arxiv_id", "")

            if gate_type == "G3_summary":
                # G3 需要 summary json 路径
                summary_path = paper.get("summary_json_path", "")
                if not summary_path:
                    # 尝试自动推断
                    summary_dir = settings.DATA_DIR / "summaries"
                    summary_path = str(summary_dir / f"{arxiv_id}_summary.json")
                result = self.check_summary(summary_path)
            else:
                result = check_fn(paper_dir=paper_dir, arxiv_id=arxiv_id)

            results.append(result)
            if result["passed"]:
                passed_count += 1

        total = len(papers)
        failed = total - passed_count

        # 写入日志
        log_entry = {
            "gate": gate_type,
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "passed": passed_count,
            "failed": failed,
            "failed_items": [
                {"arxiv_id": r.get("arxiv_id", ""), "issues": r.get("issues", [])}
                for r in results if not r["passed"]
            ],
        }

        log_path = self.logs_dir / f"quality_gate_{gate_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.write_text(
            json.dumps(log_entry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("[QualityGate] %s: %d/%d passed, log -> %s", gate_type, passed_count, total, log_path.name)

        return {
            "gate": gate_type,
            "total": total,
            "passed": passed_count,
            "failed": failed,
            "results": results,
            "log_path": str(log_path),
        }
