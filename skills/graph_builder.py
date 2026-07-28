"""
skills/graph_builder.py — A2 图谱构建技能

将多源引用数据融合为统一的 AcademicGraph 结构：
  - 构建引用关系 DAG（目标论文 → 引用/被引论文）
  - 构建合作网络（作者 ↔ 机构）
  - 构建时间线（按年份排序的里程碑）
  - 调用 DeepSeek 进行主题标签分类

去重键: (title_normalized, first_author_surname, year)
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

from config import settings
from skills.base_module import BaseSkill, register_skill
from models.academic_graph import (
    AcademicGraph,
    SourcePaper,
    Author,
    GraphNode,
    GraphEdge,
    CitationGraph,
    CollaborationNetwork,
    Timeline,
    TimelineMilestone,
    TopicAnnotation,
    GraphStatistics,
)

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


@register_skill("graph-build")
class GraphBuilder(BaseSkill):
    """
    图谱构建器。

    将 CitationCollector 的输出（references.json + citations.json + related_works.json）
    融合为统一的 AcademicGraph 格式，供下游消费者（叙事生成、可视化、配图）使用。

    使用示例:
        builder = GraphBuilder()
        result = builder.execute(
            arxiv_id="2605.28175",
            references=[...],
            citations=[...],
            related=[...],
            metadata={"title": "...", "authors": [...], "year": 2026},
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
        构建 AcademicGraph。

        参数:
            arxiv_id    (str): arXiv ID
            references  (list): 参考文献列表
            citations   (list): 被引列表
            related     (list): 相关论文推荐
            metadata    (dict): 论文元数据
            output_dir  (str): 输出目录

        返回:
            {
                "academic_graph": AcademicGraph dict,
                "graph_path": "data/graphs/{id}/academic_graph.json",
                "timeline": Timeline dict,
                "error": None,
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        references: list[dict] = kwargs.get("references", [])
        citations: list[dict] = kwargs.get("citations", [])
        related: list[dict] = kwargs.get("related", [])
        metadata: dict = kwargs.get("metadata", {})
        output_dir: str = kwargs.get("output_dir", "")

        if not arxiv_id:
            return {"academic_graph": None, "error": "arxiv_id is required"}

        if not output_dir:
            output_dir = str(settings.DATA_DIR / "graphs" / arxiv_id)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        try:
            # 1. 构建源论文信息
            source_paper = self._build_source_paper(arxiv_id, metadata)

            # 2. 构建引用关系图
            citation_graph = self._build_citation_graph(
                arxiv_id, source_paper, references, citations, related
            )

            # 3. 构建合作网络
            collab_network = self._build_collaboration_network(
                source_paper, references, citations
            )

            # 4. 构建时间线
            timeline = self._build_timeline(
                arxiv_id, source_paper, references, citations
            )

            # 5. 主题标注 (DeepSeek)
            topic_annotations = self._annotate_topics(arxiv_id, source_paper)

            # 6. 统计摘要
            statistics = self._compute_statistics(
                references, citations, related, citation_graph
            )

            # 7. 组装 AcademicGraph
            graph = AcademicGraph(
                schema_version="1.0",
                generated_at=datetime.now().isoformat(),
                source_paper=source_paper,
                citation_graph=citation_graph,
                collaboration_network=collab_network,
                timeline=timeline,
                topic_annotations=topic_annotations,
                statistics=statistics,
            )

            # 8. 保存
            graph_path = out_path / "academic_graph.json"
            graph_path.write_text(
                json.dumps(graph.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            timeline_path = out_path / "timeline.json"
            timeline_path.write_text(
                json.dumps(timeline.model_dump(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            logger.info("[GraphBuilder] AcademicGraph saved to %s", graph_path)

            return {
                "academic_graph": graph.to_dict(),
                "graph_path": str(graph_path),
                "timeline": timeline.model_dump(),
                "error": None,
            }

        except Exception as exc:
            logger.error("[GraphBuilder] Failed: %s", exc)
            return {"academic_graph": None, "error": str(exc)}

    # ------------------------------------------------------------------
    # 子步骤实现
    # ------------------------------------------------------------------

    @staticmethod
    def _build_source_paper(arxiv_id: str, metadata: dict) -> SourcePaper:
        """从 metadata 构建 SourcePaper。"""
        authors = []
        for author_data in metadata.get("authors", []):
            if isinstance(author_data, str):
                authors.append(Author(name=author_data))
            elif isinstance(author_data, dict):
                authors.append(Author(
                    name=author_data.get("name", ""),
                    institution=author_data.get("institution", ""),
                    is_corresponding=author_data.get("is_corresponding", False),
                ))

        return SourcePaper(
            arxiv_id=arxiv_id,
            title=metadata.get("title", ""),
            year=metadata.get("year"),
            venue=metadata.get("venue", ""),
            authors=authors,
            keywords=metadata.get("keywords", []),
            research_area=metadata.get("research_direction", ""),
        )

    def _build_citation_graph(
        self,
        arxiv_id: str,
        source: SourcePaper,
        references: list[dict],
        citations: list[dict],
        related: list[dict],
    ) -> CitationGraph:
        """构建引用关系 DAG。"""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        # 目标论文节点
        target_id = f"paper_{arxiv_id}"
        nodes.append(GraphNode(
            id=target_id,
            label=source.title[:80] or arxiv_id,
            type="target",
            year=source.year,
            authors=[a.name for a in source.authors],
            institution=source.authors[0].institution if source.authors else "",
            importance=1.0,
        ))

        seen_ids: set[str] = {target_id}

        # 参考文献节点
        for ref in references:
            ref_id = GraphBuilder._make_node_id(ref)
            if ref_id in seen_ids:
                continue
            seen_ids.add(ref_id)

            nodes.append(GraphNode(
                id=ref_id,
                label=ref.get("title", "")[:80],
                type="reference",
                year=ref.get("year"),
                authors=ref.get("authors", []),
                importance=GraphBuilder._estimate_importance(ref),
            ))
            edges.append(GraphEdge(
                source=target_id,
                target=ref_id,
                relation="cites",
                weight=0.5,
                description=ref.get("relation_description", ""),
            ))

        # 被引节点
        for cit in citations:
            cit_id = GraphBuilder._make_node_id(cit)
            if cit_id in seen_ids:
                continue
            seen_ids.add(cit_id)

            nodes.append(GraphNode(
                id=cit_id,
                label=cit.get("title", "")[:80],
                type="citation",
                year=cit.get("year"),
                authors=cit.get("authors", []),
                importance=min(cit.get("citation_count", 0) / 100.0, 1.0),
            ))
            edges.append(GraphEdge(
                source=cit_id,
                target=target_id,
                relation="cited_by",
                weight=0.5,
            ))

        # 相关论文节点
        for rel in related:
            rel_id = GraphBuilder._make_node_id(rel)
            if rel_id in seen_ids:
                continue
            seen_ids.add(rel_id)

            nodes.append(GraphNode(
                id=rel_id,
                label=rel.get("title", "")[:80],
                type="related",
                year=rel.get("year"),
                authors=rel.get("authors", []),
                importance=0.3,
            ))
            edges.append(GraphEdge(
                source=target_id,
                target=rel_id,
                relation="extends",
                weight=0.3,
            ))

        return CitationGraph(nodes=nodes, edges=edges)

    @staticmethod
    def _build_collaboration_network(
        source: SourcePaper,
        references: list[dict],
        citations: list[dict],
    ) -> CollaborationNetwork:
        """构建合作网络（作者 ↔ 机构）。"""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        seen_inst: set[str] = set()
        seen_auth: set[str] = set()

        # 源论文的作者和机构
        for author in source.authors:
            auth_id = f"author_{author.name.lower().replace(' ', '_')}"
            if auth_id not in seen_auth:
                seen_auth.add(auth_id)
                nodes.append(GraphNode(
                    id=auth_id, label=author.name,
                    type="author", institution=author.institution,
                    paper_count=1,
                ))

            if author.institution:
                inst_id = f"inst_{author.institution.lower().replace(' ', '_')[:50]}"
                if inst_id not in seen_inst:
                    seen_inst.add(inst_id)
                    nodes.append(GraphNode(
                        id=inst_id, label=author.institution,
                        type="institution", paper_count=1,
                    ))
                edges.append(GraphEdge(
                    source=auth_id, target=inst_id,
                    relation="affiliated_with", weight=0.8,
                ))

        return CollaborationNetwork(nodes=nodes, edges=edges)

    def _build_timeline(
        self,
        arxiv_id: str,
        source: SourcePaper,
        references: list[dict],
        citations: list[dict],
    ) -> Timeline:
        """按年份构建时间线。"""
        milestones: list[TimelineMilestone] = []
        all_papers = references + citations

        # 按年份分组
        year_groups: dict[int, list[dict]] = {}
        for paper in all_papers:
            year = paper.get("year")
            if year:
                year_groups.setdefault(year, []).append(paper)

        for year in sorted(year_groups.keys()):
            papers = year_groups[year]
            # 选取最高引用的论文作为代表
            papers_sorted = sorted(papers, key=lambda p: p.get("citation_count", 0), reverse=True)
            top_paper = papers_sorted[0]

            # 判断里程碑类型
            if year <= (source.year or 2025) - 3:
                mtype = "foundation"
            elif len(papers_sorted) >= 3:
                mtype = "breakthrough"
            else:
                mtype = "incremental"

            milestones.append(TimelineMilestone(
                year=year,
                event=top_paper.get("title", f"{len(papers)} papers published")[:120],
                paper_ids=[GraphBuilder._make_node_id(p) for p in papers_sorted[:3]],
                type=mtype,
                impact_description=f"{len(papers)} related works",
            ))

        # 添加目标论文
        if source.year:
            milestones.append(TimelineMilestone(
                year=source.year,
                event=source.title[:120],
                paper_ids=[f"paper_{arxiv_id}"],
                type="breakthrough",
                impact_description="Target paper",
            ))

        # 重新排序
        milestones.sort(key=lambda m: m.year)

        years = [m.year for m in milestones]
        span = (min(years) if years else 2020, max(years) if years else 2026)

        return Timeline(
            target_paper_id=arxiv_id,
            milestones=milestones,
            span_years=span,
            narrative=self._build_timeline_narrative(milestones),
        )

    @staticmethod
    def _build_timeline_narrative(milestones: list[TimelineMilestone]) -> str:
        """生成时间线叙述文本。"""
        if not milestones:
            return ""
        parts = []
        for m in milestones:
            type_emoji = {
                "foundation": "🏛️",
                "breakthrough": "🚀",
                "incremental": "📌",
                "application": "🔧",
            }.get(m.type, "📄")
            parts.append(f"{type_emoji} {m.year}: {m.event[:100]}")
        return " → ".join(parts)

    def _annotate_topics(
        self, arxiv_id: str, source: SourcePaper
    ) -> list[TopicAnnotation]:
        """使用 DeepSeek 对论文进行主题标签分类。"""
        if not self.is_ready:
            # 从标题和关键词中提取简单标签
            return [TopicAnnotation(
                paper_id=f"paper_{arxiv_id}",
                topics=[{"label": kw, "confidence": 0.8} for kw in source.keywords[:5]],
            )]

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Classify this paper into 3-5 research topics. "
                        f"Return JSON array of {{label, confidence}}:\n\n"
                        f"Title: {source.title}\n"
                        f"Keywords: {', '.join(source.keywords)}\n"
                    ),
                }],
                temperature=0.2,
                max_tokens=300,
            )
            raw = response.choices[0].message.content
            topics = self._parse_topic_json(raw)
            return [TopicAnnotation(paper_id=f"paper_{arxiv_id}", topics=topics)]
        except Exception as exc:
            logger.warning("[GraphBuilder] Topic annotation failed: %s", exc)
            return [TopicAnnotation(
                paper_id=f"paper_{arxiv_id}",
                topics=[{"label": kw, "confidence": 0.5} for kw in source.keywords[:5]],
            )]

    @staticmethod
    def _compute_statistics(
        references: list[dict],
        citations: list[dict],
        related: list[dict],
        citation_graph: CitationGraph,
    ) -> GraphStatistics:
        """计算图谱统计摘要。"""
        all_refs = references + citations
        years = [r.get("year") for r in all_refs if r.get("year")]
        institutions: dict[str, int] = {}
        for node in citation_graph.nodes:
            if node.institution:
                institutions[node.institution] = institutions.get(node.institution, 0) + 1

        top_insts = sorted(institutions, key=institutions.get, reverse=True)[:5]

        return GraphStatistics(
            total_references=len(references),
            total_citations=len(citations),
            total_related=len(related),
            reference_year_span=(
                (min(years) if years else 2020),
                (max(years) if years else 2026),
            ),
            top_institutions=top_insts,
            avg_citation_year=sum(years) / len(years) if years else 2024.0,
        )

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _make_node_id(paper: dict) -> str:
        """生成节点唯一 ID。"""
        arxiv = paper.get("arxiv_id", "")
        if arxiv:
            return f"paper_{arxiv}"
        title = re.sub(r'[^a-z0-9]', '', paper.get("title", "").lower())[:20]
        author = paper.get("first_author_surname", "").lower()
        year = paper.get("year", "")
        return f"paper_{author}_{year}_{title}"

    @staticmethod
    def _estimate_importance(paper: dict) -> float:
        """估算论文重要度。"""
        score = 0.3
        cc = paper.get("citation_count", 0)
        if cc > 100:
            score = 0.95
        elif cc > 50:
            score = 0.8
        elif cc > 10:
            score = 0.6
        elif cc > 0:
            score = 0.4
        return score

    @staticmethod
    def _parse_topic_json(raw: str) -> list[dict]:
        """解析 DeepSeek 返回的主题 JSON。"""
        try:
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            data = json.loads(raw.strip())
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [data]
        except (json.JSONDecodeError, ValueError, IndexError):
            pass
        # 回退：从文本中提取
        return [{"label": t.strip(), "confidence": 0.5} for t in raw.split(",")[:5]]
