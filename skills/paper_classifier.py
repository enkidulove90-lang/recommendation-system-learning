"""
skills/paper_classifier.py — 论文分类技能

使用 data/registry/taxonomies.yaml 受控词表对论文进行分类，
将分类结果回写到 data/registry/papers.jsonl。

分类维度：
  - research_direction (8 选 1-2)
  - pipeline_stage (8 选 1-3)
  - technical_paradigm (9 选 1-3)
  - modality (7 选 1-3)
  - paper_type (6 选 1)
  - maturity (3 选 1)
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill("paper-classify")
class PaperClassifier(BaseSkill):
    """
    论文分类技能，使用 taxonomies.yaml 受控词表。

    使用示例:
        classifier = PaperClassifier()
        result = classifier.execute(
            arxiv_id="2505.19525",
            summary_json_path="data/summaries/2505.19525_summary.json",
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._taxonomies: dict[str, dict] = {}
        self._load_taxonomies()

    def _load_taxonomies(self) -> None:
        """加载 taxonomies.yaml 受控词表。"""
        tax_path = settings.DATA_DIR / "registry" / "taxonomies.yaml"
        if tax_path.exists():
            try:
                self._taxonomies = yaml.safe_load(tax_path.read_text(encoding="utf-8"))
                logger.info("[Classifier] Loaded taxonomies: %d categories", len(self._taxonomies))
            except Exception as e:
                logger.error("[Classifier] Failed to load taxonomies: %s", e)

    @property
    def is_ready(self) -> bool:
        return bool(self._taxonomies)

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        对论文进行分类。

        参数:
            arxiv_id           (str): arXiv ID
            summary_json_path  (str): 摘要 JSON 路径（11 维度模板输出）
            update_papers_jsonl (bool): 是否回写到 papers.jsonl，默认 True

        返回:
            {
                "arxiv_id": str,
                "classification": dict,
                "updated": bool,
                "error": str | None,
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        summary_path: str = kwargs.get("summary_json_path", "")
        update_jsonl: bool = kwargs.get("update_papers_jsonl", True)

        if not summary_path:
            return {
                "arxiv_id": arxiv_id,
                "classification": {},
                "updated": False,
                "error": "summary_json_path is required.",
            }

        # 读取摘要 JSON
        try:
            summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            return {
                "arxiv_id": arxiv_id,
                "classification": {},
                "updated": False,
                "error": f"Cannot read summary JSON: {e}",
            }

        # 执行分类
        classification = self._classify_paper(summary)

        # 回写 papers.jsonl
        updated = False
        if update_jsonl:
            updated = self._update_papers_jsonl(arxiv_id, classification)

        return {
            "arxiv_id": arxiv_id,
            "classification": classification,
            "updated": updated,
            "error": None,
        }

    # ------------------------------------------------------------------
    # 分类逻辑
    # ------------------------------------------------------------------

    def _classify_paper(self, summary: dict) -> dict[str, Any]:
        """
        基于摘要内容执行分类。

        策略：从摘要中提取关键词，与 taxonomies.yaml 的 aliases 进行匹配。
        """
        # 收集摘要中的所有文本用于匹配
        text_parts: list[str] = []
        text_parts.append(str(summary.get("title_zh", "")))
        text_parts.append(str(summary.get("title_en", "")))
        text_parts.append(str(summary.get("one_line_summary", "")))
        text_parts.append(str(summary.get("paper_type", "")))

        prob_def = summary.get("problem_definition", {})
        if isinstance(prob_def, dict):
            text_parts.append(str(prob_def.get("task_type", "")))
            text_parts.append(str(prob_def.get("input", "")))

        # 创新点文本
        innovations = summary.get("innovations", [])
        if isinstance(innovations, list):
            for inv in innovations:
                if isinstance(inv, dict):
                    text_parts.append(str(inv.get("point", "")))
                else:
                    text_parts.append(str(inv))

        # 模块文本
        modules = summary.get("modules", [])
        if isinstance(modules, list):
            for mod in modules:
                if isinstance(mod, dict):
                    text_parts.append(str(mod.get("name", "")))
                    text_parts.append(str(mod.get("role", "")))

        # 训练策略文本
        training = summary.get("training", {})
        if isinstance(training, dict):
            text_parts.append(str(training.get("loss", "")))
            text_parts.append(str(training.get("negative_sampling", "")))

        # 数据集文本
        datasets = summary.get("datasets", [])
        if isinstance(datasets, list):
            for ds in datasets:
                if isinstance(ds, dict):
                    text_parts.append(str(ds.get("name", "")))

        # Benchmark 基线
        benchmark = summary.get("benchmark", {})
        if isinstance(benchmark, dict):
            baselines = benchmark.get("baselines", [])
            if isinstance(baselines, list):
                text_parts.extend(str(b) for b in baselines)

        full_text = " ".join(text_parts).lower()

        # 执行各维度分类
        classification = {
            "research_directions": self._match_taxonomy(
                full_text, "research_directions", max_select=2
            ),
            "pipeline_stages": self._match_taxonomy(
                full_text, "pipeline_stages", max_select=3
            ),
            "technical_paradigms": self._match_taxonomy(
                full_text, "technical_paradigms", max_select=3
            ),
            "modalities": self._match_taxonomy(
                full_text, "modalities", max_select=3
            ),
            "paper_type": self._match_taxonomy(
                full_text, "paper_type", max_select=1
            ),
            "maturity": self._match_taxonomy(
                full_text, "maturity", max_select=1
            ),
        }

        # 从 paper_type 字段直接提取（如果摘要已包含）
        pt = str(summary.get("paper_type", "")).lower()
        if "综述" in pt or "survey" in pt:
            classification["paper_type"] = ["survey"]
        elif "工业" in pt or "industrial" in pt or "system" in pt:
            classification["paper_type"] = ["system"]
        elif "理论" in pt or "theory" in pt:
            classification["paper_type"] = ["theory"]

        return classification

    def _match_taxonomy(
        self, text: str, category: str, max_select: int = 2
    ) -> list[str]:
        """
        将文本与 taxonomies.yaml 中的 aliases 进行匹配。

        返回匹配到的受控词表 key 列表（最多 max_select 个）。
        """
        entries = self._taxonomies.get(category, {})
        if not entries:
            return []

        scores: dict[str, int] = {}
        for key, spec in entries.items():
            if not isinstance(spec, dict):
                continue
            aliases = spec.get("aliases", [])
            score = 0
            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower in text:
                    score += len(alias_lower)  # 越长的匹配越可信
            if score > 0:
                scores[key] = score

        # 按分数排序，取 top-N
        sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
        return sorted_keys[:max_select]

    # ------------------------------------------------------------------
    # 回写 papers.jsonl
    # ------------------------------------------------------------------

    def _update_papers_jsonl(
        self, arxiv_id: str, classification: dict
    ) -> bool:
        """更新 papers.jsonl 中对应论文的分类标签。"""
        jsonl_path = settings.DATA_DIR / "registry" / "papers.jsonl"
        if not jsonl_path.exists():
            # 创建新文件
            jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "arxiv_id": arxiv_id,
                "classification": classification,
                "updated_at": datetime.now().isoformat(),
            }
            jsonl_path.write_text(
                json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            return True

        # 读取所有记录
        lines = jsonl_path.read_text(encoding="utf-8").splitlines()
        records: list[dict] = []
        found = False

        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if record.get("arxiv_id") == arxiv_id:
                    record["classification"] = classification
                    record["updated_at"] = datetime.now().isoformat()
                    found = True
                records.append(record)
            except json.JSONDecodeError:
                continue

        if not found:
            records.append({
                "arxiv_id": arxiv_id,
                "classification": classification,
                "updated_at": datetime.now().isoformat(),
            })

        # 写回
        jsonl_path.write_text(
            "\n".join(
                json.dumps(r, ensure_ascii=False) for r in records
            ) + "\n",
            encoding="utf-8",
        )
        logger.info("[Classifier] Updated papers.jsonl for %s", arxiv_id)
        return True

    # ------------------------------------------------------------------
    # 生成方向标签（用于文件夹命名）
    # ------------------------------------------------------------------

    @staticmethod
    def generate_direction_tag(classification: dict) -> str:
        """
        根据分类结果生成文件夹命名用的方向标签。

        示例：
          - 1 个方向: llm_ranking
          - 2 个方向: [llm_ranking×efficient_retrieval]
        """
        directions = classification.get("research_directions", [])
        if not directions:
            return ""
        if len(directions) == 1:
            return directions[0]
        return f"[{chr(215).join(directions)}]"  # × = U+00D7
