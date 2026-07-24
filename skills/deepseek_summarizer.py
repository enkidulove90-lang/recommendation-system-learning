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
            output_dir  (str): 输出目录，保存 {arxiv_id}_summary.md 和 .json
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
        user_prompt = self._build_user_prompt(title, abstract, trimmed_text)

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

                # 保存到文件
                self._save_summary(summary_data, md_path, json_path)

                return {
                    "ready": True,
                    "arxiv_id": arxiv_id,
                    "summary": summary_data,
                    "summary_path": str(md_path),
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

    # ------------------------------------------------------------------
    # Prompt 构建
    # ------------------------------------------------------------------

    @staticmethod
    def _build_system_prompt() -> str:
        """构建系统提示词。"""
        return """你是一位顶级的推荐系统研究科学家。你的任务是对学术论文进行深度解读。

请严格按照以下 JSON 格式输出（确保是合法 JSON）：

```json
{
  "chinese_title": "论文的中文标题翻译（简洁准确，15字以内）",
  "main_contribution": "论文的主要贡献（100-200字中文概括）",
  "innovation_points": [
    "创新点1：具体描述",
    "创新点2：具体描述",
    "创新点3：具体描述"
  ],
  "methodology": "论文采用的方法论简述（50-150字）",
  "benchmark_datasets": [
    "数据集/基准名称1",
    "数据集/基准名称2"
  ],
  "experimental_results": "关键实验效果总结，包含主要指标数值对比（100-200字）",
  "agent_relevance": "对推荐系统Agent开发的借鉴价值：算法设计思路、评估方法、系统架构、数据处理等方面（100-200字）"
}
```

要求:
1. innovation_points 至少列出 3 个创新点，每个用 1-2 句话描述
2. benchmark_datasets 列出论文使用的所有数据集和评估基准
3. experimental_results 要包含具体的性能提升百分比或数值
4. agent_relevance 要具体说明可借鉴的算法设计、评估方法、系统架构等
5. 所有中文回答，专业术语可保留英文
6. 只输出 JSON，不要有其他内容"""
        return system_prompt

    @staticmethod
    def _build_user_prompt(title: str, abstract: str, full_text: str) -> str:
        """构建用户提示词（包含论文内容）。"""
        prompt_parts = ["请分析以下论文:\n"]

        if title:
            prompt_parts.append(f"## 标题\n{title}\n")

        if abstract:
            prompt_parts.append(f"## 摘要\n{abstract}\n")

        if full_text:
            # 如果全文很短，直接全部传入
            prompt_parts.append(f"## 全文（可能已截断关键部分）\n{full_text}\n")

        prompt_parts.append("请输出上述 JSON 格式的分析结果。")
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
    def _parse_response(raw: str, arxiv_id: str, title: str) -> dict[str, Any]:
        """解析 DeepSeek 返回的 JSON 响应。"""
        default = {
            "paper_id": arxiv_id,
            "title": title,
            "chinese_title": "",
            "main_contribution": "",
            "innovation_points": [],
            "benchmark_datasets": [],
            "experimental_results": "",
            "agent_relevance": "",
            "methodology": "",
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
                "chinese_title": str(data.get("chinese_title", "")),
                "main_contribution": str(data.get("main_contribution", "")),
                "innovation_points": [str(p) for p in data.get("innovation_points", [])],
                "benchmark_datasets": [str(d) for d in data.get("benchmark_datasets", [])],
                "experimental_results": str(data.get("experimental_results", "")),
                "agent_relevance": str(data.get("agent_relevance", "")),
                "methodology": str(data.get("methodology", "")),
            }
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning("[DeepSeek] JSON parse failed: %s. Using raw text.", exc)
            return {
                **default,
                "main_contribution": raw[:500] if raw else "",
                "innovation_points": [],
                "agent_relevance": "",
            }

    @staticmethod
    def _save_summary(summary_data: dict, md_path: Path, json_path: Path) -> None:
        """保存摘要为 Markdown 和 JSON 文件。"""
        # Markdown 格式
        md_content = f"""# {summary_data.get('chinese_title', '') or summary_data.get('title', 'Unknown Title')}

**英文标题**: {summary_data.get('title', 'Unknown Title')}
**arXiv ID**: {summary_data.get('paper_id', '')}
**生成时间**: {summary_data.get('generated_at', '')}

---

## 主要贡献

{summary_data.get('main_contribution', 'N/A')}

## 创新点

"""
        for i, point in enumerate(summary_data.get("innovation_points", []), 1):
            md_content += f"{i}. {point}\n"

        md_content += f"""
## 方法论

{summary_data.get('methodology', 'N/A')}

## Benchmark 与数据集

"""
        for ds in summary_data.get("benchmark_datasets", []):
            md_content += f"- {ds}\n"

        md_content += f"""
## 实验效果

{summary_data.get('experimental_results', 'N/A')}

## 对推荐系统 Agent 开发的借鉴

{summary_data.get('agent_relevance', 'N/A')}

---

*由 DeepSeek ({settings.DEEPSEEK_MODEL}) 自动生成*
"""

        md_path.write_text(md_content, encoding="utf-8")

        # JSON 格式
        json_path.write_text(
            json.dumps(summary_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info("[DeepSeek] Summary saved -> %s, %s", md_path.name, json_path.name)
