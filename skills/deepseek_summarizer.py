"""
skills/deepseek_summarizer.py — DeepSeek 论文摘要生成技能

使用 DeepSeek API (OpenAI 兼容格式) 对论文全文进行深度解读，
提取核心贡献、创新点、Benchmark/数据集、实验效果，
以及对该方向 Agent 开发的借鉴价值。

所有外部工具 / API 调用封装为 Skill，符合项目架构规范。
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

# DeepSeek API 端点（OpenAI 兼容）
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


@register_skill("deepseek-summarize")
class DeepSeekSummarizer(BaseSkill):
    """
    DeepSeek 论文深度解读技能。

    读取论文全文（Markdown），调用 DeepSeek 生成结构化解读，
    包括主要贡献、创新点、数据集、实验结果、Agent 可借鉴之处。

    使用示例:
        summarizer = DeepSeekSummarizer()
        result = summarizer.execute(
            arxiv_id="2602.21756",
            title="Persona4Rec: ...",
            full_text="...",          # Markdown 全文
            output_dir="data/summaries/",
        )
        summary = result["summary"]  # PaperSummary dict
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key: str = settings.DEEPSEEK_API_KEY or kwargs.get("api_key", "")
        self._model: str = kwargs.get("model", settings.DEEPSEEK_MODEL)
        self._client: OpenAI | None = None

        if self._api_key:
            self._client = OpenAI(
                api_key=self._api_key,
                base_url=DEEPSEEK_BASE_URL,
            )

    @property
    def is_ready(self) -> bool:
        """检查 DeepSeek API 是否已配置并可用。"""
        return bool(self._api_key) and self._client is not None

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        生成论文深度解读。

        参数:
            arxiv_id    (str): arXiv ID
            title       (str): 论文标题
            abstract    (str): 论文摘要
            full_text   (str): 论文全文（Markdown 格式）
            output_dir  (str): 输出目录，保存 {arxiv_id}_summary.md
            max_retries (int): 最大重试次数，默认 3

        返回:
            {
                "ready": bool,
                "arxiv_id": str,
                "summary": {  # PaperSummary 结构
                    "paper_id": str,
                    "title": str,
                    "main_contribution": str,
                    "innovation_points": [...],
                    "benchmark_datasets": [...],
                    "experimental_conditions": {
                        "task_and_data": str,
                        "baselines": str,
                        "metrics": str,
                        "implementation": str,
                    },
                    "experimental_results": str,
                    "agent_relevance": str,
                    "methodology": str,
                    "full_summary_text": str,
                    "generated_at": str,
                },
                "summary_path": str | None,
                "error": str | None,
            }
        """
        if not self.is_ready:
            logger.warning("DeepSeek API key not configured.")
            return {
                "ready": False,
                "arxiv_id": kwargs.get("arxiv_id", ""),
                "summary": None,
                "summary_path": None,
                "error": "DEEPSEEK_API_KEY not set in .env",
            }

        arxiv_id: str = kwargs.get("arxiv_id", "")
        title: str = kwargs.get("title", "")
        abstract: str = kwargs.get("abstract", "")
        full_text: str = kwargs.get("full_text", "")
        figure_descriptions: str = kwargs.get("figure_descriptions", "")
        output_dir: str = kwargs.get("output_dir", "")
        max_retries: int = kwargs.get("max_retries", 3)

        if not full_text and not abstract:
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "summary": None,
                "summary_path": None,
                "error": "Either full_text or abstract must be provided.",
            }

        # ---- 截断全文以避免超出 API Token 限制 ----
        # DeepSeek 支持 128K 上下文，但论文全文可能很长
        # 保留前 ~40000 字符 + 关键章节
        trimmed_text = self._trim_paper_text(full_text, max_chars=40000)

        # ---- 确定输出路径 ----
        if not output_dir:
            output_dir = str(settings.DATA_DIR / "summaries")
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        md_path = out_path / f"{arxiv_id}_summary.md"
        json_path = out_path / f"{arxiv_id}_summary.json"
        # ---- 构建 Prompt ----
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(title, abstract, trimmed_text, figure_descriptions)

        # ---- 调用 API（含重试） ----
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "[DeepSeek] Generating summary for %s (attempt %d/%d) ...",
                    arxiv_id, attempt, max_retries,
                )
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                )

                raw_output = response.choices[0].message.content
                logger.info("[DeepSeek] Response received | len=%d chars", len(raw_output))

                # 解析结构化输出
                summary_data = self._parse_response(raw_output, arxiv_id, title)
                summary_data["full_summary_text"] = raw_output
                summary_data["generated_at"] = datetime.now().isoformat()

                # 保存到文件（.md + .json 双格式）
                self._save_summary(summary_data, md_path, json_path)

                return {
                    "ready": True,
                    "arxiv_id": arxiv_id,
                    "summary": summary_data,
                    "summary_path": str(md_path),
                    "summary_json_path": str(json_path),
                    "error": None,
                }

            except Exception as exc:
                logger.error("[DeepSeek] Attempt %d error: %s", attempt, exc)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)

        return {
            "ready": True,
            "arxiv_id": arxiv_id,
            "summary": None,
            "summary_path": None,
            "error": f"Failed after {max_retries} retries.",
        }

    def extract_experimental_conditions(self, **kwargs: Any) -> dict[str, Any]:
        """Extract experiment setup fields without regenerating an existing summary."""
        if not self.is_ready:
            return {
                "ready": False,
                "experimental_conditions": None,
                "error": "DEEPSEEK_API_KEY not set in .env",
            }

        title = str(kwargs.get("title", ""))
        full_text = str(kwargs.get("full_text", ""))
        max_retries = int(kwargs.get("max_retries", 3))
        if not full_text:
            return {
                "ready": True,
                "experimental_conditions": None,
                "error": "full_text is required.",
            }

        experiment_context = self._trim_paper_text(full_text, max_chars=35000)
        system_prompt = """你是一位推荐系统实验复现审计专家。
请仅根据论文原文提取实验条件，并严格返回合法 JSON：
{
  "task_and_data": "实验任务、数据规模、预处理、训练/验证/测试划分",
  "baselines": "主要对比方法、基线与消融设置",
  "metrics": "评价指标和计算口径",
  "implementation": "硬件、软件、模型版本、优化器、学习率、批大小、轮数及推理参数"
}
要求：
1. 使用中文，专业名称保留英文。
2. 只记录原文明确给出的事实，不得推测。
3. 某类信息未提供时写“原文未披露”。
4. 只输出 JSON，不要附加解释。"""
        user_prompt = f"## 论文标题\n{title}\n\n## 论文实验相关正文\n{experiment_context}"

        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=1600,
                )
                raw_output = response.choices[0].message.content or ""
                text = raw_output.strip()
                if "```json" in text:
                    start = text.index("```json") + 7
                    end = text.index("```", start)
                    text = text[start:end].strip()
                elif "```" in text:
                    start = text.index("```") + 3
                    end = text.index("```", start)
                    text = text[start:end].strip()
                conditions = self._normalize_experimental_conditions(json.loads(text))
                return {
                    "ready": True,
                    "experimental_conditions": conditions,
                    "error": None,
                }
            except Exception as exc:
                logger.error(
                    "[DeepSeek] Experiment conditions attempt %d error: %s",
                    attempt,
                    exc,
                )
                if attempt < max_retries:
                    time.sleep(2 ** attempt)

        return {
            "ready": True,
            "experimental_conditions": None,
            "error": f"Failed after {max_retries} retries.",
        }

    # ------------------------------------------------------------------
    # Prompt 构建
    # ------------------------------------------------------------------

    @staticmethod
    def _build_system_prompt() -> str:
        """构建系统提示词（11 维度模板）。"""
        return """你是一位顶级的推荐系统研究科学家。你的任务是对学术论文进行深度解读，按照 11 维度模板生成结构化总结。

## 防幻觉三条铁律
1. 每条结论须标注来源（章节号/图表号/公式号/页码）。
2. 论文未提及的字段填「论文未提及」，不得用通识补全。个人判断须标注 [阅读者判断]。
3. 数字一律抄录原文，不做推算合并。

请严格按照以下 JSON 格式输出（确保是合法 JSON）：

```json
{
  "title_zh": "论文中文标题翻译（简洁准确，15字以内）",
  "title_en": "论文英文原标题",
  "paper_type": "长文/短文/工业界/综述/复现 + 贡献类型(方法创新/理论创新/训练策略创新/数据集评测创新/应用系统创新)",
  "venue": "发表会议/期刊名+届次（论文未提及则填'论文未提及'）",
  "year": "发表年份",
  "one_line_summary": "用<=30字概括这篇论文做了什么",
  "problem_definition": {
    "task_type": "评分预测/Top-K排序/序列推荐/CTR预估/召回/重排/冷启动/多模态等",
    "input": "用户特征/物品特征/交互历史/上下文/辅助信息",
    "output": "预测分数/排序列表/概率/嵌入",
    "source": "来源章节号"
  },
  "innovations": [
    {"point": "创新点描述", "category": "方法/理论/训练/数据/评测/系统", "source": "来源章节号"},
    {"point": "与最接近工作的区别", "category": "方法", "source": "来源章节号"}
  ],
  "modules": [
    {"name": "模块名称", "role": "作用", "input": "输入张量/特征", "output": "产出", "source": "公式号/图号"}
  ],
  "training": {
    "loss": "主损失类型(BPR/CE/Hinge/InfoNCE等)+多任务loss+辅助loss+正则项",
    "negative_sampling": "正样本定义+负样本策略+比例+mask策略",
    "optimizer": "优化器/学习率/warmup/衰减/batch_size/epochs/早停",
    "pretrain": "是否两阶段(预训练->微调)+预训练数据来源（论文未提及则填'论文未提及'）",
    "source": "来源章节号/超参表号"
  },
  "datasets": [
    {"name": "数据集名称", "users": "用户数", "items": "物品数", "interactions": "交互数", "split": "切分方式", "source": "表格号"}
  ],
  "benchmark": {
    "metrics": ["Recall@K", "NDCG@K", "AUC等"],
    "baselines": ["基线方法1", "基线方法2"],
    "main_results": "主结果表关键列：数据集×指标×方法×提升幅度",
    "significance": "统计显著性检验结果（论文未提及则填'论文未提及'）",
    "online_ab": "在线A/B实验设置与结论（论文未提及则填'论文未提及'）",
    "source": "表格号/章节号"
  },
  "related_papers": [
    {"ref_id": "引文编号[12]", "relation": "对标/改进/理论依据/同期", "summary": "一句话概括"}
  ],
  "reproducibility": {
    "code_open": false,
    "data_open": false,
    "hyperparams_complete": false,
    "seed": "随机种子（论文未提及则填'论文未提及'）"
  },
  "limitations": "论文自承局限+[阅读者判断]风险（须标注个人判断）",
  "summary_criteria_check": {
    "accuracy": true,
    "completeness": true,
    "reproducibility_oriented": true,
    "critical": true
  }
}
```

要求:
1. innovations 至少列出 3 个创新点，每个必须有 source 标注
2. modules 逐模块记录，论文未显式拆分则记录为"未显式拆分"并尽量从架构图还原
3. training 必须覆盖 loss/负采样/优化器/预训练，原文未披露的字段填"论文未提及"
4. datasets 数字必须抄录论文表格原文，不做心算合并
5. benchmark.baselines 列出全部基线，标注是否重跑
6. related_papers 至少列出 3 篇核心关联论文
7. reproducibility 各布尔字段根据论文是否披露判断
8. 所有中文回答，专业术语可保留英文
9. 只输出 JSON，不要有其他内容"""

    @staticmethod
    def _build_user_prompt(
        title: str,
        abstract: str,
        full_text: str,
        figure_descriptions: str = "",
    ) -> str:
        """构建用户提示词（包含论文内容 + 图表视觉描述）。"""
        prompt_parts = ["请分析以下论文:\n"]

        if title:
            prompt_parts.append(f"## 标题\n{title}\n")

        if abstract:
            prompt_parts.append(f"## 摘要\n{abstract}\n")

        if full_text:
            prompt_parts.append(f"## 全文（可能已截断关键部分）\n{full_text}\n")

        if figure_descriptions:
            prompt_parts.append(
                f"## 图表视觉理解结果（由 Qwen3.5 视觉模型生成）\n{figure_descriptions}\n"
            )

        prompt_parts.append("请按照 11 维度模板输出上述 JSON 格式的分析结果。每条结论标注来源。")
        return "\n".join(prompt_parts)

    # ------------------------------------------------------------------
    # 文本截断策略
    # ------------------------------------------------------------------

    @staticmethod
    def _trim_paper_text(full_text: str, max_chars: int = 40000) -> str:
        """
        智能截断论文全文，保留关键章节。

        优先级: Introduction > Methodology/Approach > Experiments > Results > Conclusion
        去除: Related Work, Acknowledgements, Appendix, References
        """
        if len(full_text) <= max_chars:
            return full_text

        # 章节关键词优先级
        high_priority = [
            "introduction", "method", "approach", "proposed",
            "methodology", "framework", "architecture", "model",
            "experiment", "result", "evaluation", "performance",
            "experimental setup", "implementation", "dataset", "baseline", "metric",
            "conclusion", "discussion",
        ]
        low_priority = [
            "related work", "background", "acknowledgment",
            "appendix", "reference", "bibliography",
        ]

        lines = full_text.split("\n")
        sections: list[tuple[str, list[str]]] = []
        current_heading = "_preamble"
        current_lines: list[str] = []

        for line in lines:
            # 检测 Markdown 标题
            stripped = line.strip()
            if stripped.startswith("#"):
                if current_lines:
                    sections.append((current_heading, current_lines))
                current_heading = stripped.lstrip("#").strip().lower()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_heading, current_lines))

        # 排序：高优先级在前
        def section_rank(heading: str) -> int:
            heading_lower = heading.lower()
            for i, kw in enumerate(high_priority):
                if kw in heading_lower:
                    return i
            for kw in low_priority:
                if kw in heading_lower:
                    return 100
            return 50  # 中等优先级

        ranked = sorted(sections, key=lambda s: section_rank(s[0]))

        # 按优先级拼接直到达到 max_chars
        result_lines: list[str] = []
        total = 0
        for _heading, sec_lines in ranked:
            sec_text = "\n".join(sec_lines)
            if total + len(sec_text) > max_chars:
                # 部分截断
                remaining = max_chars - total
                result_lines.append(sec_text[:remaining])
                result_lines.append("\n\n[... 全文因长度限制已截断 ...]")
                break
            result_lines.append(sec_text)
            total += len(sec_text)

        return "\n".join(result_lines)

    # ------------------------------------------------------------------
    # 响应解析与保存
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_experimental_conditions() -> dict[str, str]:
        return {
            "task_and_data": "原文未披露",
            "baselines": "原文未披露",
            "metrics": "原文未披露",
            "implementation": "原文未披露",
        }

    @staticmethod
    def _normalize_experimental_conditions(value: Any) -> dict[str, str]:
        conditions = DeepSeekSummarizer._empty_experimental_conditions()
        if isinstance(value, dict):
            for key in conditions:
                text = str(value.get(key, "")).strip()
                if text:
                    conditions[key] = text
        elif value:
            conditions["task_and_data"] = str(value).strip()
        return conditions

    @staticmethod
    def _parse_response(raw: str, arxiv_id: str, title: str) -> dict[str, Any]:
        """解析 DeepSeek 返回的 11 维度 JSON 响应。"""
        default = {
            "paper_id": arxiv_id,
            "title": title,
            "title_zh": "",
            "title_en": title,
            "paper_type": "",
            "venue": "",
            "year": "",
            "one_line_summary": "",
            "problem_definition": {},
            "innovations": [],
            "modules": [],
            "training": {},
            "datasets": [],
            "benchmark": {},
            "related_papers": [],
            "reproducibility": {},
            "limitations": "",
            "summary_criteria_check": {},
        }

        try:
            # 尝试提取 JSON 块
            text = raw.strip()
            if "```json" in text:
                start = text.index("```json") + 7
                end = text.index("```", start)
                text = text[start:end].strip()
            elif "```" in text:
                start = text.index("```") + 3
                end = text.index("```", start)
                text = text[start:end].strip()

            data = json.loads(text)

            return {
                "paper_id": arxiv_id,
                "title": title,
                "title_zh": str(data.get("title_zh", data.get("chinese_title", ""))),
                "title_en": str(data.get("title_en", title)),
                "paper_type": str(data.get("paper_type", "")),
                "venue": str(data.get("venue", "")),
                "year": str(data.get("year", "")),
                "one_line_summary": str(data.get("one_line_summary", "")),
                "problem_definition": data.get("problem_definition", {}),
                "innovations": data.get("innovations", []),
                "modules": data.get("modules", []),
                "training": data.get("training", {}),
                "datasets": data.get("datasets", []),
                "benchmark": data.get("benchmark", {}),
                "related_papers": data.get("related_papers", []),
                "reproducibility": data.get("reproducibility", {}),
                "limitations": str(data.get("limitations", "")),
                "summary_criteria_check": data.get("summary_criteria_check", {}),
            }
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning("[DeepSeek] JSON parse failed: %s. Using raw text.", exc)
            return {
                **default,
                "one_line_summary": raw[:500] if raw else "",
                "limitations": "JSON parsing failed; raw text preserved.",
            }

    @staticmethod
    def _save_summary(summary_data: dict, md_path: Path, json_path: Path | None = None) -> None:
        """Save summary as Markdown (.md) + JSON (.json) dual format."""
        # ---- JSON 格式（机器可读）----
        if json_path is None:
            json_path = md_path.with_suffix(".json")
        json_path.write_text(
            json.dumps(summary_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("[DeepSeek] Summary JSON saved -> %s", json_path.name)

        # ---- Markdown 格式（人类可读，按 11 维度排版）----
        title_zh = summary_data.get("title_zh", "") or summary_data.get("title", "Unknown Title")
        title_en = summary_data.get("title_en", summary_data.get("title", ""))
        paper_id = summary_data.get("paper_id", "")
        paper_type = summary_data.get("paper_type", "")
        venue = summary_data.get("venue", "")
        year = summary_data.get("year", "")
        one_line = summary_data.get("one_line_summary", "")

        md_content = f"""# {title_zh}

**英文标题**: {title_en}
**arXiv ID**: {paper_id}
**论文类型**: {paper_type or '论文未提及'}
**venue**: {venue or '论文未提及'}
**年份**: {year or '论文未提及'}
**一句话概括**: {one_line or 'N/A'}
**生成时间**: {summary_data.get('generated_at', '')}

---

## 维度 0: 元信息

| 字段 | 内容 |
|------|------|
| 论文标题 | {title_zh} |
| 英文标题 | {title_en} |
| arXiv ID | {paper_id} |
| 论文类型 | {paper_type or '论文未提及'} |
| venue | {venue or '论文未提及'} |
| 年份 | {year or '论文未提及'} |

## 维度 1: 论文类型

{paper_type or '论文未提及'}

## 维度 2: 研究背景与问题定义

"""

        # 问题定义
        prob_def = summary_data.get("problem_definition", {})
        if isinstance(prob_def, dict):
            md_content += f"- **任务类型**: {prob_def.get('task_type', '论文未提及')}\n"
            md_content += f"- **输入**: {prob_def.get('input', '论文未提及')}\n"
            md_content += f"- **输出**: {prob_def.get('output', '论文未提及')}\n"
            md_content += f"- **来源**: {prob_def.get('source', '')}\n"
        else:
            md_content += f"{prob_def}\n"

        # 创新点
        md_content += "\n## 维度 3: 主要创新点\n\n"
        innovations = summary_data.get("innovations", [])
        if isinstance(innovations, list):
            for i, inv in enumerate(innovations, 1):
                if isinstance(inv, dict):
                    md_content += f"{i}. **{inv.get('point', '')}**\n"
                    md_content += f"   - 分类: {inv.get('category', '')}\n"
                    md_content += f"   - 来源: {inv.get('source', '')}\n"
                else:
                    md_content += f"{i}. {inv}\n"
        else:
            md_content += f"{innovations}\n"

        # 模块
        md_content += "\n## 维度 4: 方法与模块\n\n"
        modules = summary_data.get("modules", [])
        if isinstance(modules, list) and modules:
            md_content += "| 模块名称 | 作用 | 输入 | 输出 | 来源 |\n"
            md_content += "|----------|------|------|------|------|\n"
            for mod in modules:
                if isinstance(mod, dict):
                    md_content += f"| {mod.get('name', '')} | {mod.get('role', '')} | {mod.get('input', '')} | {mod.get('output', '')} | {mod.get('source', '')} |\n"
                else:
                    md_content += f"| {mod} | | | | |\n"
        else:
            md_content += "论文未提及或未显式拆分\n"

        # 训练策略
        md_content += "\n## 维度 5: 训练策略\n\n"
        training = summary_data.get("training", {})
        if isinstance(training, dict):
            md_content += f"- **损失函数**: {training.get('loss', '论文未提及')}\n"
            md_content += f"- **正负样本构造**: {training.get('negative_sampling', '论文未提及')}\n"
            md_content += f"- **优化与训练流程**: {training.get('optimizer', '论文未提及')}\n"
            md_content += f"- **预训练**: {training.get('pretrain', '论文未提及')}\n"
            md_content += f"- **来源**: {training.get('source', '')}\n"
        else:
            md_content += f"{training}\n"

        # 数据集
        md_content += "\n## 维度 6: 数据集选择\n\n"
        datasets = summary_data.get("datasets", [])
        if isinstance(datasets, list) and datasets:
            md_content += "| 名称 | 用户数 | 物品数 | 交互数 | 切分方式 | 来源 |\n"
            md_content += "|------|--------|--------|--------|---------|------|\n"
            for ds in datasets:
                if isinstance(ds, dict):
                    md_content += f"| {ds.get('name', '')} | {ds.get('users', '')} | {ds.get('items', '')} | {ds.get('interactions', '')} | {ds.get('split', '')} | {ds.get('source', '')} |\n"
                else:
                    md_content += f"| {ds} | | | | | |\n"
        else:
            md_content += "论文未提及\n"

        # 实验与 Benchmark
        md_content += "\n## 维度 7: 实验与 Benchmark\n\n"
        benchmark = summary_data.get("benchmark", {})
        if isinstance(benchmark, dict):
            metrics = benchmark.get("metrics", [])
            md_content += f"- **评测指标**: {', '.join(metrics) if isinstance(metrics, list) else metrics}\n"
            baselines = benchmark.get("baselines", [])
            md_content += f"- **基线方法**: {', '.join(baselines) if isinstance(baselines, list) else baselines}\n"
            md_content += f"- **主结果**: {benchmark.get('main_results', '论文未提及')}\n"
            md_content += f"- **显著性**: {benchmark.get('significance', '论文未提及')}\n"
            md_content += f"- **在线实验**: {benchmark.get('online_ab', '论文未提及')}\n"
            md_content += f"- **来源**: {benchmark.get('source', '')}\n"
        else:
            md_content += f"{benchmark}\n"

        # 关联论文
        md_content += "\n## 维度 8: 关联论文\n\n"
        related = summary_data.get("related_papers", [])
        if isinstance(related, list) and related:
            for rp in related:
                if isinstance(rp, dict):
                    md_content += f"- [{rp.get('ref_id', '')}] {rp.get('relation', '')}: {rp.get('summary', '')}\n"
                else:
                    md_content += f"- {rp}\n"
        else:
            md_content += "论文未提及\n"

        # 复现性
        md_content += "\n## 维度 9: 复现性\n\n"
        repro = summary_data.get("reproducibility", {})
        if isinstance(repro, dict):
            md_content += f"- 代码开源: {'是' if repro.get('code_open') else '否/论文未提及'}\n"
            md_content += f"- 数据公开: {'是' if repro.get('data_open') else '否/论文未提及'}\n"
            md_content += f"- 超参完整: {'是' if repro.get('hyperparams_complete') else '否/论文未提及'}\n"
            md_content += f"- 随机种子: {repro.get('seed', '论文未提及')}\n"
        else:
            md_content += f"{repro}\n"

        # 局限性
        md_content += f"\n## 维度 10: 局限性\n\n{summary_data.get('limitations', '论文未提及')}\n"

        md_content += f"\n---\n\n*由 DeepSeek ({settings.DEEPSEEK_MODEL}) 自动生成 | 11 维度模板*\n"

        md_path.write_text(md_content, encoding="utf-8")
        logger.info("[DeepSeek] Summary MD saved -> %s", md_path.name)
