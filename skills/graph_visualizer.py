"""
skills/graph_visualizer.py — A5 图谱可视化技能

将 AcademicGraph 中的图数据渲染为适合小红书展示的 PNG 图片：
  - citation_graph.png — 引用关系 DAG
  - timeline.png — 时间线演化图

技术方案: matplotlib + networkx 本地渲染（零外部服务依赖）
图片规格: 1200×800px, DPI 150, 白色背景, 小红书适配配色
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

# 延迟导入，避免 matplotlib 在无图形环境崩溃
_HAS_MATPLOTLIB = False
_HAS_NETWORKX = False

try:
    import matplotlib
    matplotlib.use("Agg")  # 非交互后端
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    _HAS_MATPLOTLIB = True
except ImportError:
    pass

try:
    import networkx as nx
    _HAS_NETWORKX = True
except ImportError:
    pass


@register_skill("graph-visualize")
class GraphVisualizer(BaseSkill):
    """
    图谱可视化器。

    将 AcademicGraph 渲染为适合社交平台展示的 PNG 图片。

    使用示例:
        viz = GraphVisualizer()
        result = viz.execute(
            arxiv_id="2605.28175",
            academic_graph={...},
            output_types=["citation_graph", "timeline"],
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._dpi: int = kwargs.get("dpi", settings.GRAPH_VIZ_DPI)
        self._size: tuple[int, int] = kwargs.get("size", settings.GRAPH_VIZ_SIZE)
        self._font_family: str = kwargs.get("font_family", self._detect_chinese_font())

    @property
    def is_ready(self) -> bool:
        return _HAS_MATPLOTLIB and _HAS_NETWORKX

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        渲染图谱为 PNG。

        参数:
            arxiv_id       (str): arXiv ID
            academic_graph (dict): AcademicGraph 数据
            output_types   (list): 图片类型，默认 ["citation_graph", "timeline"]
            output_dir     (str): 输出目录

        返回:
            {
                "images": [
                    {"type": "citation_graph", "path": "..."},
                    {"type": "timeline", "path": "..."},
                ],
                "error": None,
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        academic_graph: dict = kwargs.get("academic_graph", {})
        output_types: list[str] = kwargs.get(
            "output_types", ["citation_graph", "timeline"]
        )
        output_dir: str = kwargs.get("output_dir", "")

        if not arxiv_id or not academic_graph:
            return {"images": [], "error": "arxiv_id and academic_graph are required"}

        if not self.is_ready:
            return {
                "images": [],
                "error": "matplotlib or networkx not installed. Run: pip install matplotlib networkx",
            }

        if not output_dir:
            output_dir = str(settings.DATA_DIR / "enriched" / arxiv_id)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        images: list[dict] = []
        errors: list[str] = []

        for output_type in output_types:
            try:
                if output_type == "citation_graph":
                    img_path = self._render_citation_graph(
                        academic_graph, out_path, arxiv_id
                    )
                elif output_type == "timeline":
                    img_path = self._render_timeline(
                        academic_graph, out_path, arxiv_id
                    )
                else:
                    continue

                if img_path:
                    images.append({"type": output_type, "path": img_path})
                    logger.info("[GraphVisualizer] Generated %s → %s", output_type, img_path)

            except Exception as exc:
                logger.error("[GraphVisualizer] %s failed: %s", output_type, exc)
                errors.append(f"{output_type}: {exc}")

        return {
            "images": images,
            "error": "; ".join(errors) if errors else None,
        }

    # ------------------------------------------------------------------
    # 引用关系图渲染
    # ------------------------------------------------------------------

    def _render_citation_graph(
        self, graph: dict, output_dir: Path, arxiv_id: str
    ) -> str | None:
        """渲染引用关系 DAG。"""
        cg = graph.get("citation_graph", {})
        nodes = cg.get("nodes", [])
        edges = cg.get("edges", [])

        if not nodes:
            logger.warning("Citation graph has no nodes, skipping")
            return None

        # 构建 networkx 图
        G = nx.DiGraph()

        # 节点颜色映射
        color_map = {
            "target": "#FF6B6B",     # 红 — 目标论文
            "reference": "#4ECDC4",  # 青 — 参考文献
            "citation": "#45B7D1",   # 蓝 — 被引论文
            "related": "#96CEB4",    # 绿 — 相关论文
        }

        node_colors = []
        node_sizes = []
        labels = {}

        for node in nodes:
            nid = node.get("id", "")
            G.add_node(nid)
            node_colors.append(color_map.get(node.get("type", ""), "#CCCCCC"))
            node_sizes.append(300 + node.get("importance", 0.5) * 1500)
            # 标签：截断标题
            label = node.get("label", nid)[:30]
            if node.get("year"):
                label += f"\n({node['year']})"
            labels[nid] = label

        for edge in edges:
            G.add_edge(edge.get("source", ""), edge.get("target", ""))

        if len(G.nodes) == 0:
            return None

        # 渲染
        fig, ax = plt.subplots(figsize=(self._size[0] / self._dpi, self._size[1] / self._dpi))

        # 布局：分层布局（目标论文在中心）
        try:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        except Exception:
            pos = nx.circular_layout(G)

        # 绘制边
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edge_color="#CCCCCC",
            arrows=True,
            arrowsize=12,
            width=1.0,
            alpha=0.6,
            connectionstyle="arc3,rad=0.1",
        )

        # 绘制节点
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            edgecolors="white",
            linewidths=1.5,
        )

        # 绘制标签
        nx.draw_networkx_labels(
            G, pos, labels, ax=ax,
            font_size=6,
            font_family=self._font_family,
            font_color="#333333",
        )

        # 图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=10, label=t)
            for t, c in [("目标论文", "#FF6B6B"), ("参考文献", "#4ECDC4"),
                         ("被引论文", "#45B7D1"), ("相关论文", "#96CEB4")]
        ]
        ax.legend(handles=legend_elements, loc="upper right", fontsize=8)

        ax.set_title(
            f"Citation Graph — {arxiv_id}",
            fontsize=14, fontweight="bold", fontfamily=self._font_family,
        )
        ax.axis("off")

        # 保存
        img_path = output_dir / "citation_graph.png"
        fig.savefig(
            str(img_path), dpi=self._dpi, bbox_inches="tight",
            facecolor="white", edgecolor="none",
        )
        plt.close(fig)

        return str(img_path)

    # ------------------------------------------------------------------
    # 时间线图渲染
    # ------------------------------------------------------------------

    def _render_timeline(
        self, graph: dict, output_dir: Path, arxiv_id: str
    ) -> str | None:
        """渲染时间线演化图。"""
        timeline = graph.get("timeline", {})
        milestones = timeline.get("milestones", [])

        if not milestones:
            # 尝试从 citation_graph 节点构建简易时间线
            milestones = self._build_milestones_from_nodes(graph)

        if not milestones:
            logger.warning("No timeline milestones, skipping")
            return None

        # 按年份排序
        milestones = sorted(milestones, key=lambda m: m.get("year", 0))

        years = [m.get("year", 0) for m in milestones]
        events = [m.get("event", "")[:60] for m in milestones]
        types = [m.get("type", "incremental") for m in milestones]

        # 颜色映射
        color_map = {
            "foundation": "#4ECDC4",
            "breakthrough": "#FF6B6B",
            "incremental": "#45B7D1",
            "application": "#96CEB4",
        }
        colors = [color_map.get(t, "#CCCCCC") for t in types]

        fig, ax = plt.subplots(figsize=(self._size[0] / self._dpi, self._size[1] / self._dpi))

        # 水平时间线
        y_positions = list(range(len(milestones)))

        # 连线
        for i in range(len(milestones) - 1):
            ax.plot(
                [years[i], years[i + 1]],
                [y_positions[i], y_positions[i + 1]],
                color="#CCCCCC", linewidth=1.5, alpha=0.6, zorder=1,
            )

        # 节点
        ax.scatter(years, y_positions, c=colors, s=200, zorder=2, edgecolors="white", linewidths=1.5)

        # 标签
        for i, (year, event, color) in enumerate(zip(years, events, colors)):
            ax.annotate(
                f"{year}: {event}",
                xy=(year, y_positions[i]),
                xytext=(15, 0),
                textcoords="offset points",
                fontsize=8,
                fontfamily=self._font_family,
                color="#333333",
                va="center",
            )

        # 图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=10, label=t)
            for t, c in [("奠基工作", "#4ECDC4"), ("突破", "#FF6B6B"),
                         ("增量", "#45B7D1"), ("应用", "#96CEB4")]
        ]
        ax.legend(handles=legend_elements, loc="upper left", fontsize=8)

        ax.set_title(
            f"Research Timeline — {arxiv_id}",
            fontsize=14, fontweight="bold", fontfamily=self._font_family,
        )
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylim(-1, len(milestones))
        ax.set_yticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # 保存
        img_path = output_dir / "timeline.png"
        fig.savefig(
            str(img_path), dpi=self._dpi, bbox_inches="tight",
            facecolor="white", edgecolor="none",
        )
        plt.close(fig)

        return str(img_path)

    @staticmethod
    def _build_milestones_from_nodes(graph: dict) -> list[dict]:
        """从 citation_graph 节点构建简易时间线。"""
        cg = graph.get("citation_graph", {})
        nodes = cg.get("nodes", [])

        milestones = []
        for node in nodes:
            year = node.get("year")
            if not year:
                continue
            mtype = "foundation" if year <= 2020 else "incremental"
            if node.get("type") == "target":
                mtype = "breakthrough"
            milestones.append({
                "year": year,
                "event": node.get("label", "")[:60],
                "type": mtype,
            })

        return milestones

    # ------------------------------------------------------------------
    # 字体检测
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_chinese_font() -> str:
        """检测系统中可用的中文字体。"""
        if not _HAS_MATPLOTLIB:
            return "sans-serif"

        # 常见中文字体
        candidates = [
            "SimHei", "Microsoft YaHei", "Noto Sans SC",
            "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",
            "STHeiti", "PingFang SC", "Heiti SC",
            "AR PL UMing CN", "AR PL UKai CN",
            "sans-serif",
        ]

        available = {f.name for f in fm.fontManager.ttflist}
        for font in candidates:
            if font in available:
                return font

        return "sans-serif"
