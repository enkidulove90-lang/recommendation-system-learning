"""
skills/narrative_generator.py — A4 增强叙事生成技能

基于 AcademicGraph 和现有论文摘要，调用 DeepSeek 生成包含
"发展脉络"和"引用网络解读"段落的增强版小红书文案。

复用现有的双模板系统：
  - Template A: 单篇深度解读（增加"📖 发展脉络"段落）
  - Template B: 综述摘要（增加"🔗 关键引用网络"段落）

降级策略: DeepSeek 不可用时 → 使用规则模板从 AcademicGraph 直接拼装
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

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


@register_skill("narrative-generate")
class NarrativeGenerator(BaseSkill):
    """
    增强叙事生成器。

    在现有 DeepSeekSummarizer 生成的基础摘要之上，
    融入 AcademicGraph 中的引用脉络、时间线、合作网络信息，
    生成更丰富的小红书发布文案。

    使用示例:
        gen = NarrativeGenerator()
        result = gen.execute(
            arxiv_id="2605.28175",
            academic_graph={...},
            summary={...},
            timeline={...},
            template="auto",
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key: str = settings.DEEPSEEK_API_KEY or kwargs.get("api_key", "")
        self._model: str = kwargs.get("model", settings.DEEPSEEK_MODEL)
        self._client: OpenAI | None = None
        if self._api_key:
            self._client = OpenAI(api_key=self._api_key, base_url=DEEPSEEK_BASE_URL)

    @property
    def is_ready(self) -> bool:
        return bool(self._api_key) and self._client is not None

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        生成增强版叙事文案。

        参数:
            arxiv_id       (str): arXiv ID
            academic_graph (dict): AcademicGraph 数据
            summary        (dict): 基础摘要
            timeline       (dict): 时间线数据
            template       (str): "auto" | "template_a" | "template_b"
            output_dir     (str): 输出目录

        返回:
            {
                "narrative_md": "完整 Markdown 文案",
                "narrative_path": "enriched/{id}/narrative.md",
                "sections": {
                    "core_contribution": "...",
                    "innovation": "...",
                    "lineage": "...",          ★ 发展脉络
                    "citation_network": "...", ★ 引用网络解读
                    "experiments": "...",
                    "takeaways": "...",
                },
                "error": None,
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        academic_graph: dict = kwargs.get("academic_graph", {})
        summary: dict = kwargs.get("summary", {})
        timeline: dict = kwargs.get("timeline", {})
        template: str = kwargs.get("template", "auto")
        output_dir: str = kwargs.get("output_dir", "")

        if not arxiv_id:
            return {"narrative_md": "", "narrative_path": "", "error": "arxiv_id is required"}

        if not output_dir:
            output_dir = str(settings.DATA_DIR / "enriched" / arxiv_id)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        try:
            if self.is_ready:
                narrative_md, sections = self._generate_with_deepseek(
                    arxiv_id, academic_graph, summary, timeline
                )
            else:
                logger.warning(
                    "[NarrativeGenerator] DeepSeek not available, using rule-based fallback"
                )
                narrative_md, sections = self._generate_rule_based(
                    arxiv_id, academic_graph, summary, timeline
                )
        except Exception as exc:
            logger.error("[NarrativeGenerator] DeepSeek failed: %s, falling back to rules", exc)
            narrative_md, sections = self._generate_rule_based(
                arxiv_id, academic_graph, summary, timeline
            )

        # 保存
        narrative_path = out_path / "narrative.md"
        narrative_path.write_text(narrative_md, encoding="utf-8")

        # 同时保存结构化 JSON
        enriched_path = out_path / "enriched_summary.json"
        enriched_path.write_text(
            json.dumps(sections, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info("[NarrativeGenerator] Saved to %s", narrative_path)

        return {
            "narrative_md": narrative_md,
            "narrative_path": str(narrative_path),
            "sections": sections,
            "error": None,
        }

    # ------------------------------------------------------------------
    # DeepSeek 生成
    # ------------------------------------------------------------------

    def _generate_with_deepseek(
        self,
        arxiv_id: str,
        graph: dict,
        summary: dict,
        timeline: dict,
    ) -> tuple[str, dict]:
        """使用 DeepSeek 生成增强版文案。"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(arxiv_id, graph, summary, timeline)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=4096,
        )

        raw = response.choices[0].message.content
        sections = self._parse_sections(raw, arxiv_id)

        narrative_md = self._format_narrative_md(sections, arxiv_id)
        return narrative_md, sections

    @staticmethod
    def _build_system_prompt() -> str:
        return """你是一位推荐系统领域的研究科学家，擅长撰写小红书风格的技术论文解读。

基于输入的基础摘要、引用图谱和时间线数据，撰写一篇增强版解读文案。
请严格按以下 sections 输出 JSON：

```json
{
  "core_contribution": "论文核心贡献（150-250字中文，含数字冲击力）",
  "innovation": "关键创新点（3-5个bullet，每个1-2句话）",
  "methodology": "核心方法论简述（100-200字）",
  "lineage": "📖 发展脉络段落（150-250字）：从奠基性工作到本论文的演进路径，突出继承了哪些思想、突破了哪些瓶颈。引用图谱中的关键节点。口语化表达。",
  "citation_network": "🔗 引用网络解读（100-200字）：关键的被引和引用关系，哪些经典工作被引用，这篇论文的学术位置。避免堆砌论文标题，用故事化表达。",
  "experiments": "实验效果（100-200字，含具体数值）",
  "takeaways": "对推荐系统Agent开发的3个可探索方向（每个1-2句话）"
}
```

要求:
1. lineage 和 citation_network 是新增板块，要写得有故事感、口语化
2. 所有中文输出，专业术语保留英文
3. 数字用 ↑/↓/× 制造冲击力
4. 只输出 JSON，不要其他内容
5. 总长度控制在 1500字以内"""

    @staticmethod
    def _build_user_prompt(
        arxiv_id: str, graph: dict, summary: dict, timeline: dict
    ) -> str:
        """构建包含图谱数据的用户提示。"""
        parts = [f"生成论文 {arxiv_id} 的增强版解读:\n"]

        # 基础摘要
        if summary:
            parts.append("## 基础摘要")
            parts.append(f"主要贡献: {summary.get('main_contribution', 'N/A')}")
            points = summary.get("innovation_points", [])
            if points:
                parts.append(f"创新点: {'; '.join(points[:5])}")
            parts.append(f"实验效果: {summary.get('experimental_results', 'N/A')}")
            parts.append(f"方法论: {summary.get('methodology', 'N/A')}")
            parts.append("")

        # 图谱统计
        stats = graph.get("statistics", {})
        if stats:
            parts.append("## 引用统计")
            parts.append(f"参考文献: {stats.get('total_references', 0)} 篇")
            parts.append(f"被引: {stats.get('total_citations', 0)} 次")
            parts.append(f"年份跨度: {stats.get('reference_year_span', (2020, 2026))}")
            parts.append(f"Top 机构: {', '.join(stats.get('top_institutions', []))}")
            parts.append("")

        # 关键引用节点
        cg = graph.get("citation_graph", {})
        important_nodes = [
            n for n in cg.get("nodes", [])
            if n.get("importance", 0) >= 0.6
        ][:10]
        if important_nodes:
            parts.append("## 关键引用关系")
            for node in important_nodes:
                parts.append(
                    f"- {node.get('label', '')} ({node.get('year', '')}) "
                    f"[{node.get('type', '')}] importance={node.get('importance', 0):.2f}"
                )
            parts.append("")

        # 时间线
        milestones = timeline.get("milestones", [])
        if milestones:
            parts.append("## 时间线")
            for m in milestones:
                parts.append(f"- {m.get('year', '')}: {m.get('event', '')[:100]}")
            parts.append("")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # 规则降级生成
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_rule_based(
        arxiv_id: str, graph: dict, summary: dict, timeline: dict
    ) -> tuple[str, dict]:
        """不使用 DeepSeek，从 AcademicGraph 直接拼装文案。"""
        sections = {
            "core_contribution": summary.get("main_contribution", "论文深入研究了推荐系统的关键技术问题。"),
            "innovation": "\n".join(
                f"• {p}" for p in summary.get("innovation_points", [])[:5]
            ) or "• 提出了创新的解决方案",
            "methodology": summary.get("methodology", "采用先进的深度学习技术。"),
            "lineage": NarrativeGenerator._build_lineage_from_graph(graph, timeline),
            "citation_network": NarrativeGenerator._build_citation_network_text(graph),
            "experiments": summary.get("experimental_results", "实验验证了方法的有效性。"),
            "takeaways": NarrativeGenerator._build_takeaways_text(summary),
        }

        narrative_md = NarrativeGenerator._format_narrative_md(sections, arxiv_id)
        return narrative_md, sections

    @staticmethod
    def _build_lineage_from_graph(graph: dict, timeline: dict) -> str:
        """从图谱和时间线构建发展脉络段落（规则版）。"""
        milestones = timeline.get("milestones", [])
        if not milestones:
            return "本文的研究建立在推荐系统领域的长期积累之上。"

        # 取 foundation 和 breakthrough 类型的里程碑
        key_events = [
            m for m in milestones
            if m.get("type") in ("foundation", "breakthrough")
        ][:5]

        if not key_events:
            key_events = milestones[:3]

        parts = ["这项研究的学术脉络可以追溯到："]
        for m in key_events:
            year = m.get("year", "")
            event = m.get("event", "")[:100]
            parts.append(f"• {year}年 — {event}")

        parts.append("本文在这些工作的基础上，进一步突破了关键瓶颈。")
        return "\n".join(parts)

    @staticmethod
    def _build_citation_network_text(graph: dict) -> str:
        """构建引用网络解读文本（规则版）。"""
        stats = graph.get("statistics", {})
        cg = graph.get("citation_graph", {})

        total_refs = stats.get("total_references", 0)
        total_cits = stats.get("total_citations", 0)
        top_insts = stats.get("top_institutions", [])

        parts = [
            f"这篇论文引用了 {total_refs} 篇相关工作，",
            f"已被 {total_cits} 篇后续工作引用。" if total_cits > 0 else "",
        ]

        if top_insts:
            parts.append(f"引用网络中涉及 {', '.join(top_insts[:3])} 等顶尖机构的研究。")

        # 高重要性节点
        important = [
            n for n in cg.get("nodes", [])
            if n.get("importance", 0) >= 0.7 and n.get("type") == "reference"
        ][:3]
        if important:
            parts.append("其中几篇奠基性工作包括：")
            for n in important:
                parts.append(f"• {n.get('label', '')[:80]} ({n.get('year', '')})")

        return "\n".join(p for p in parts if p)

    @staticmethod
    def _build_takeaways_text(summary: dict) -> str:
        """从摘要中构建可探索方向文本（规则版）。"""
        relevance = summary.get("agent_relevance", "")
        if relevance:
            lines = relevance.split("。")
            takeaways = [l.strip() + "。" for l in lines if len(l.strip()) > 10][:3]
            if takeaways:
                return "\n".join(f"方向{i+1}：{t}" for i, t in enumerate(takeaways))

        return (
            "方向一：将本文方法迁移到 Agent 推荐场景，探索 LLM Agent 与推荐系统的深度融合。\n"
            "方向二：在更广泛的推荐领域验证方法的泛化性，如电商、音乐、视频推荐。\n"
            "方向三：优化推理效率，降低计算开销以适应实时推荐场景。"
        )

    # ------------------------------------------------------------------
    # 格式化输出
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_sections(raw: str, arxiv_id: str) -> dict:
        """解析 DeepSeek 返回的 JSON sections。"""
        default = {
            "core_contribution": "",
            "innovation": "",
            "methodology": "",
            "lineage": "",
            "citation_network": "",
            "experiments": "",
            "takeaways": "",
        }
        try:
            text = raw.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text)
            return {**default, **{k: str(v) for k, v in data.items()}}
        except (json.JSONDecodeError, ValueError, IndexError):
            # 回退：全部放入 core_contribution
            default["core_contribution"] = raw[:1000] if raw else ""
            return default

    @staticmethod
    def _format_narrative_md(sections: dict, arxiv_id: str) -> str:
        """将 sections 格式化为小红书面板 Markdown。"""
        parts = []

        if sections.get("core_contribution"):
            parts.append(f"🎓 {sections['core_contribution']}")

        if sections.get("innovation"):
            parts.append(f"✨ 关键创新\n{sections['innovation']}")

        if sections.get("methodology"):
            parts.append(f"🧠 核心设计\n{sections['methodology']}")

        if sections.get("lineage"):
            parts.append(f"📖 发展脉络\n{sections['lineage']}")

        if sections.get("citation_network"):
            parts.append(f"🔗 引用网络\n{sections['citation_network']}")

        if sections.get("experiments"):
            parts.append(f"📊 实验效果\n{sections['experiments']}")

        if sections.get("takeaways"):
            parts.append(f"💡 可探索方向\n{sections['takeaways']}")

        parts.append(f"\n📄 arXiv：https://arxiv.org/abs/{arxiv_id}")
        parts.append(f"📎 PDF：https://arxiv.org/pdf/{arxiv_id}")

        return "\n\n".join(parts)
