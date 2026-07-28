# 引用关系与发展脉络分析层 — 系统设计文档

> **版本**: 1.0  
> **最后更新**: 2026-07-28  
> **状态**: 设计阶段  
> **依赖**: 现有 6 阶段论文发布流水线 (phase1)

---

## 目录

1. [设计目标与原则](#1-设计目标与原则)
2. [整体数据流设计](#2-整体数据流设计)
3. [新增模块划分](#3-新增模块划分)
4. [数据模型定义](#4-数据模型定义)
5. [文件与目录结构](#5-文件与目录结构)
6. [工作流编排](#6-工作流编排)
7. [异常处理与容错](#7-异常处理与容错)
8. [扩展方向预留](#8-扩展方向预留)
9. [与现有系统的集成点](#9-与现有系统的集成点)

---

## 1. 设计目标与原则

### 1.1 核心目标

在现有 6 阶段流水线（爬取→下载→解析→摘要→配图→发布）基础上，插入一个**可选的分析增强层**，为每篇待发布论文自动生成：

- **引用关系图谱**：目标论文与引用/被引论文之间的继承演进关系
- **机构/作者合作网络**：核心实验室与作者之间的合作关系可视化
- **时间线演化**：从奠基性工作到近期突破的发展路径
- **领域热词/主题变迁**：研究焦点随时间迁移的趋势

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **可插拔（Pluggable）** | 新增模块完全独立于现有模块，通过文件 I/O 和 CLI 交互，不修改现有代码 |
| **可配置（Configurable）** | 分析工具（PaperGraph / Citracer / Semantic Scholar API）可灵活替换，通过 Skill 注册表切换 |
| **数据继承（Data Inheritance）** | 分析结果（`AcademicGraph`）以标准化 JSON 格式输出，下游文案/配图模块直接消费 |
| **质量筛选（Quality Gating）** | 仅对评分高的论文触发完整分析，低分论文降级为简单摘要发布 |
| **优雅降级（Graceful Degradation）** | 任何分析工具失败或超时，系统自动跳过该维度，不阻塞主流程 |
| **扩展优先（Extension-First）** | 每个分析维度设计为独立 Skill，新增数据源只需注册新 Skill |

### 1.3 约束条件

- 总耗时不超过现有链路的 1.5 倍（约 45 分钟）；超时需缓存或增量更新
- 不得依赖需要登录/付费的第三方服务（除已使用的 MinerU 和 DeepSeek API）
- 所有分析工具可本地运行或通过公开 API 调用

---

## 2. 整体数据流设计

### 2.1 增强后的完整流水线

```
现有链路（不修改）                         新增分析增强层
═══════════════                         ═══════════════

[① 论文检索] crawler/arxiv_crawler
      │
      ▼ papers_metadata.json
[② PDF下载] skills/pdf_downloader
      │
      ▼ data/parsed/{arxiv_id}/*.pdf
[③ 内容解析] skills/pdf_parser (MinerU)
      │
      ▼ data/parsed/{arxiv_id}/*.md + _content.json
      │
      ├──────────────────────────────────────────────┐
      │                                              │
      ▼                                              ▼
[④ 论文摘要]                          [A1 引用数据采集]
DeepSeekSummarizer                    CitationCollector
      │                                      │
      ▼ data/summaries/                      ▼ data/citations/{arxiv_id}/
      │                                      │  ├── references.json     ← 引用列表
      │                                      │  ├── citations.json      ← 被引列表
      │                                      │  └── related_works.json  ← 相关论文
      │                                      │
      │                                      ▼
      │                              [A2 图谱构建]
      │                              GraphBuilder
      │                                      │
      │                                      ▼ data/graphs/{arxiv_id}/
      │                                      │  ├── academic_graph.json  ← 统一图谱
      │                                      │  └── timeline.json        ← 时间线
      │                                      │
      │                                      ▼
      │                              [A3 质量评分与筛选]
      │                              QualityScorer
      │                                      │
      │                          ┌───────────┴───────────┐
      │                          │                       │
      │                     高分 (≥0.7)              低分 (<0.7)
      │                          │                       │
      │                          ▼                       ▼
      │              [A4 完整叙事生成]         [A4' 简单摘要]
      │              NarrativeGenerator       跳过图谱分析
      │                          │                       │
      │                          ▼                       │
      │              [A5 图谱可视化]                     │
      │              GraphVisualizer                     │
      │                          │                       │
      │                          └───────────┬───────────┘
      │                                      │
      ▼                                      ▼
[⑤ 配图准备]  ◄────────────  data/enriched/{arxiv_id}/
generators/images              │  ├── narrative.md        ← 增强版文案
                               │  ├── citation_graph.png   ← 引用关系图
                               │  ├── timeline.png         ← 时间线图
                               │  ├── topic_trend.png      ← 主题变迁图
                               │  └── enriched_summary.json← 增强版摘要
      │
      ▼
[⑥ 发布] publishers/xhs_cli
```

### 2.2 各环节输入/输出格式

| 环节 | 输入 | 输出 | 格式 |
|------|------|------|------|
| **A1 引用数据采集** | `parsed/{id}/_content.json` (参考文献段落) + arXiv ID | `citations/{id}/references.json` | JSON 数组，每项含 title/authors/year/arxiv_id/relation_type |
| **A2 图谱构建** | `citations/{id}/` + Semantic Scholar API 响应 | `graphs/{id}/academic_graph.json` | 统一 `AcademicGraph` 格式（见第4章） |
| **A3 质量评分** | `academic_graph.json` + `summaries/{id}_summary.md` | `graphs/{id}/quality_score.json` | `{score: float, dimensions: {...}, threshold_pass: bool}` |
| **A4 叙事生成** | `academic_graph.json` + `{id}_summary.md` + DeepSeek Prompt | `enriched/{id}/narrative.md` | Markdown，含引用脉络段落 |
| **A5 图谱可视化** | `academic_graph.json` | `enriched/{id}/citation_graph.png` 等 | PNG 图片，1200×800px，适配小红书 |
| **⑤ 配图准备（修改）** | 原有图片 + `enriched/{id}/*.png` | 最终配图列表 | 文件路径列表，最多 5 张 |
| **⑥ 发布（修改）** | `enriched/{id}/narrative.md` (替代原 summary) | 小红书笔记 | 通过 `xhs post` CLI |

### 2.3 标注：新增 vs 修改

**纯新增模块（不修改现有代码）：**
- A1 CitationCollector → `skills/citation_collector.py`
- A2 GraphBuilder → `skills/graph_builder.py`
- A3 QualityScorer → `skills/quality_scorer.py`
- A4 NarrativeGenerator → `skills/narrative_generator.py`
- A5 GraphVisualizer → `skills/graph_visualizer.py`
- 调度脚本 → `workflows/daily_publish_with_analysis.py`

**最小化修改（仅扩展输入源）：**
- `publish_paper.py` 的 `format_body()`: 增加一个可选分支，当 `enriched/{id}/narrative.md` 存在时优先使用
- `publish_paper.py` 的 `find_images()`: 增加对 `enriched/{id}/*.png` 的扫描
- `config/settings.py`: 新增 5-8 个分析层配置属性

---

## 3. 新增模块划分

### 3.1 模块总览

```
skills/
├── citation_collector.py    # A1 — 引用数据采集
├── graph_builder.py         # A2 — 图谱构建与融合
├── quality_scorer.py        # A3 — 论文质量评分
├── narrative_generator.py   # A4 — 增强叙事生成
└── graph_visualizer.py      # A5 — 图谱可视化

workflows/
└── daily_publish_with_analysis.py  # 调度编排脚本

models/
└── academic_graph.py        # AcademicGraph / Citation / Author / Institution 数据模型
```

### 3.2 A1 — CitationCollector（引用数据采集器）

| 属性 | 说明 |
|------|------|
| **注册名** | `citation-collect` |
| **职责** | 从多个数据源采集目标论文的引用关系、相关论文、作者/机构信息 |
| **输入** | `arxiv_id` (str), `parsed_content_path` (Path), 论文元数据 |
| **输出** | `citations/{arxiv_id}/references.json` — 参考文献列表（解析自 PDF）<br>`citations/{arxiv_id}/citations.json` — 被引列表（Semantic Scholar API）<br>`citations/{arxiv_id}/related_works.json` — 相关论文推荐 |
| **数据源** | ① 解析 `_content.json` 中的 References 段落 → 提取被引论文元数据<br>② Semantic Scholar API（免费，无需 API Key）→ 获取引用网络<br>③ arXiv API → 补充元数据 |
| **超时** | 单篇论文 180 秒 |
| **降级策略** | 若 Semantic Scholar 不可用 → 仅使用 PDF 内解析的参考文献 |

**接口定义（伪代码）：**

```
class CitationCollector(BaseSkill):
    skill_type = "citation-collect"
    
    execute(arxiv_id, parsed_dir, metadata, sources=["semantic_scholar", "arxiv", "pdf_refs"])
        → {
            "references": [{title, authors[], year, arxiv_id?, venue, relation_type}],
            "citations":  [{title, authors[], year, arxiv_id?, venue, citation_count}],
            "related":    [{title, authors[], year, arxiv_id?, similarity_score}],
            "collected_at": "ISO timestamp",
            "sources_used": ["pdf_refs", "semantic_scholar"],
            "error": None | "error message"
          }
```

### 3.3 A2 — GraphBuilder（图谱构建器）

| 属性 | 说明 |
|------|------|
| **注册名** | `graph-build` |
| **职责** | 将多源引用数据融合为统一的 `AcademicGraph` 结构；构建引用网络、合作网络、时间线 |
| **输入** | CitationCollector 的输出（三个 JSON 文件） |
| **输出** | `graphs/{arxiv_id}/academic_graph.json`<br>`graphs/{arxiv_id}/timeline.json` |
| **核心逻辑** | ① 以目标论文为中心节点，构建引用 DAG<br>② 提取所有作者→机构映射，构建合作网络<br>③ 按年份排序构建时间线<br>④ 通过 DeepSeek 对论文进行主题标签分类 |
| **去重** | 以 `(title_normalized, first_author_surname, year)` 为联合键去重 |
| **超时** | 单篇论文 120 秒 |

**接口定义（伪代码）：**

```
class GraphBuilder(BaseSkill):
    skill_type = "graph-build"
    
    execute(arxiv_id, references, citations, related, metadata)
        → {
            "academic_graph": AcademicGraph,  # 见第4章数据模型
            "timeline": Timeline,             # 时间线结构
            "graph_path": "data/graphs/{id}/academic_graph.json",
            "timeline_path": "data/graphs/{id}/timeline.json",
            "error": None
          }
```

### 3.4 A3 — QualityScorer（质量评分器）

| 属性 | 说明 |
|------|------|
| **注册名** | `quality-score` |
| **职责** | 基于多维度指标对论文进行质量评分，决定是否触发完整分析 |
| **输入** | `AcademicGraph` + `PaperSummary` |
| **输出** | `graphs/{arxiv_id}/quality_score.json` |
| **评分维度** | ① **引用网络深度**（0-1）：是否有清晰的奠基性工作 → 近期突破路径<br>② **引用数量**（0-1）：被引次数归一化得分<br>③ **合作网络广度**（0-1）：是否涉及多个知名机构/作者<br>④ **主题新颖度**（0-1）：与已发布论文的主题重叠度（越低越新颖）<br>⑤ **内容完整度**（0-1）：PDF 解析是否完整，摘要质量 |
| **阈值** | ≥0.7 → 触发完整分析 + 图谱可视化<br><0.7 → 仅发布基础摘要 |
| **超时** | 单篇 30 秒 |

**接口定义（伪代码）：**

```
class QualityScorer(BaseSkill):
    skill_type = "quality-score"
    
    execute(arxiv_id, academic_graph, summary)
        → {
            "score": 0.0-1.0,
            "dimensions": {
                "citation_depth": 0.8,
                "citation_count": 0.6,
                "collaboration_breadth": 0.7,
                "topic_novelty": 0.9,
                "content_completeness": 0.85
            },
            "threshold_pass": True | False,
            "decision": "full_analysis" | "basic_only",
            "reason": "High citation depth and topic novelty"
          }
```

### 3.5 A4 — NarrativeGenerator（叙事生成器）

| 属性 | 说明 |
|------|------|
| **注册名** | `narrative-generate` |
| **职责** | 基于 `AcademicGraph` 和现有摘要，调用 DeepSeek 生成包含"发展脉络"段落的增强版文案 |
| **输入** | `AcademicGraph` + `PaperSummary` + `Timeline` + 模板选择 |
| **输出** | `enriched/{arxiv_id}/narrative.md` — 含发展脉络的完整 Markdown 文案 |
| **模板** | 复用现有双模板系统：<br>① Template A — 单篇深度解读（增加"📖 发展脉络"段落）<br>② Template B — 综述摘要（增加"🔗 关键引用网络"段落） |
| **超时** | 单篇 60 秒（DeepSeek API 调用） |
| **降级** | 若 DeepSeek 不可用 → 使用规则模板从 AcademicGraph 直接拼装 |

**接口定义（伪代码）：**

```
class NarrativeGenerator(BaseSkill):
    skill_type = "narrative-generate"
    
    execute(arxiv_id, academic_graph, summary, timeline, template="auto")
        → {
            "narrative_md": "完整的Markdown文案...",
            "narrative_path": "enriched/{id}/narrative.md",
            "sections": {
                "core_contribution": "...",
                "innovation": "...",
                "lineage": "...",          # ★ 新增：发展脉络段落
                "citation_network": "...", # ★ 新增：引用网络解读
                "experiments": "...",
                "takeaways": "..."
            },
            "error": None
          }
```

### 3.6 A5 — GraphVisualizer（图谱可视化器）

| 属性 | 说明 |
|------|------|
| **注册名** | `graph-visualize` |
| **职责** | 将 `AcademicGraph` 中的图数据渲染为适合小红书展示的 PNG 图片 |
| **输入** | `AcademicGraph` |
| **输出** | `enriched/{arxiv_id}/citation_graph.png` — 引用关系图<br>`enriched/{arxiv_id}/timeline.png` — 时间线演化图<br>`enriched/{arxiv_id}/topic_trend.png` — 主题变迁图（可选） |
| **技术方案** | ① matplotlib/networkx 本地渲染（零外部依赖）<br>② 可选 Graphviz 布局引擎（需本地安装）<br>③ 中文字体：使用项目内置字体或系统 SimHei |
| **图片规格** | 1200×800px, DPI 150, 白色背景, 小红书适配配色 |
| **超时** | 单篇 60 秒 |

**接口定义（伪代码）：**

```
class GraphVisualizer(BaseSkill):
    skill_type = "graph-visualize"
    
    execute(arxiv_id, academic_graph, output_types=["citation_graph", "timeline"])
        → {
            "images": [
                {"type": "citation_graph", "path": "enriched/{id}/citation_graph.png"},
                {"type": "timeline", "path": "enriched/{id}/timeline.png"},
            ],
            "error": None
          }
```

### 3.7 模块依赖关系

```
CitationCollector (A1)
       │
       ▼
GraphBuilder (A2)
       │
       ├──────────────────────┐
       ▼                      ▼
QualityScorer (A3)    GraphVisualizer (A5)
       │                      │
       ▼                      │
NarrativeGenerator (A4)       │
       │                      │
       └──────────┬───────────┘
                  ▼
         现有 ⑤ 配图准备 + ⑥ 发布
```

依赖全部通过文件 I/O 解耦：A1 写 JSON → A2 读 JSON 写 JSON → A3/A4/A5 各读所需的 JSON，互不直接调用。

---

## 4. 数据模型定义

### 4.1 AcademicGraph — 统一中间数据格式

这是分析增强层的核心数据结构。所有分析工具的输出都转换为此格式，所有下游消费者（叙事生成、可视化、配图）都从此格式读取。

```
AcademicGraph {
  # ── 元信息 ──
  "schema_version": "1.0",
  "generated_at": "2026-07-28T10:30:00Z",
  "source_paper": {
    "arxiv_id": "2605.28175",
    "title": "MixRAGRec: ...",
    "year": 2026,
    "venue": "KDD 2026",
    "authors": [
      {"name": "Author Name", "institution": "PolyU", "is_corresponding": true}
    ],
    "keywords": ["recommendation", "knowledge graph", "mixture of experts"],
    "research_area": "agent-recommendation"
  },

  # ── 引用关系图 ──
  "citation_graph": {
    "nodes": [
      {
        "id": "paper_2605.28175",
        "label": "MixRAGRec",
        "type": "target",           # target | reference | citation | related
        "year": 2026,
        "authors": ["Author Name"],
        "institution": "PolyU",
        "importance": 1.0            # 0-1, 目标论文=1.0
      },
      {
        "id": "paper_2203.02155",
        "label": "Training language models to follow instructions",
        "type": "reference",
        "year": 2022,
        "authors": ["Ouyang L", "..."],
        "institution": "OpenAI",
        "importance": 0.95
      }
    ],
    "edges": [
      {
        "source": "paper_2605.28175",
        "target": "paper_2203.02155",
        "relation": "cites",         # cites | cited_by | extends | contrasts | uses_dataset
        "weight": 0.8,
        "description": "基座模型训练方法"  # DeepSeek 生成的简短说明
      }
    ]
  },

  # ── 合作网络 ──
  "collaboration_network": {
    "nodes": [
      {
        "id": "inst_polyu",
        "label": "Hong Kong Polytechnic University",
        "type": "institution",
        "paper_count": 15,
        "research_focus": ["recommendation", "knowledge graph"]
      },
      {
        "id": "author_xxx",
        "label": "Author Name",
        "type": "author",
        "institution": "PolyU",
        "paper_count": 8,
        "h_index_estimate": 12
      }
    ],
    "edges": [
      {
        "source": "author_xxx",
        "target": "inst_polyu",
        "relation": "affiliated_with"
      },
      {
        "source": "author_xxx",
        "target": "author_yyy",
        "relation": "co_author",
        "co_paper_count": 5
      }
    ]
  },

  # ── 时间线 ──
  "timeline": {
    "milestones": [
      {
        "year": 2022,
        "event": "InstructGPT 发布，RLHF 范式确立",
        "paper_ids": ["2203.02155"],
        "type": "foundation"         # foundation | breakthrough | incremental | application
      },
      {
        "year": 2026,
        "event": "MixRAGRec：MoE 驱动的自适应知识图谱检索推荐",
        "paper_ids": ["2605.28175"],
        "type": "breakthrough"
      }
    ]
  },

  # ── 主题标签 ──
  "topic_annotations": [
    {
      "paper_id": "paper_2605.28175",
      "topics": [
        {"label": "Mixture of Experts", "confidence": 0.9},
        {"label": "Knowledge Graph Reasoning", "confidence": 0.85},
        {"label": "Agent-based Recommendation", "confidence": 0.8}
      ]
    }
  ],

  # ── 统计摘要 ──
  "statistics": {
    "total_references": 42,
    "total_citations": 18,
    "total_related": 12,
    "reference_year_span": [2015, 2026],
    "top_institutions": ["PolyU", "NUS", "Tsinghua"],
    "avg_citation_year": 2023.5
  }
}
```

### 4.2 各外部数据源 → AcademicGraph 映射关系

| 数据源 | 提取字段 | 映射到 AcademicGraph |
|--------|---------|---------------------|
| **MinerU `_content.json`** 参考文献段落 | title, authors, year, venue | `citation_graph.nodes[type=reference]`<br>`citation_graph.edges[relation=cites]` |
| **Semantic Scholar `/paper/{id}/references`** | title, authors, year, venue, citationCount | `citation_graph.nodes[type=reference]` |
| **Semantic Scholar `/paper/{id}/citations`** | title, authors, year, venue, citationCount | `citation_graph.nodes[type=citation]`<br>`citation_graph.edges[relation=cited_by]` |
| **Semantic Scholar `/paper/{id}/recommendations`** | title, authors, year | `citation_graph.nodes[type=related]`<br>`citation_graph.edges[relation=extends]` |
| **arXiv API 作者信息** | author names, affiliations (from comment) | `collaboration_network` |
| **DeepSeek 主题标注** | 论文的主题标签 + 置信度 | `topic_annotations` |
| **DeepSeek 边描述** | 引用关系的简短说明 | `citation_graph.edges[description]` |

### 4.3 辅助数据模型

```
# ── 引用条目 ──
Citation {
  "title": "Paper Title",
  "title_normalized": "paper title",     # 小写 + 去标点，用于去重
  "authors": ["Author 1", "Author 2"],
  "first_author_surname": "Author",
  "year": 2025,
  "arxiv_id": "2503.xxxxx",             # 可选
  "doi": "10.xxxx/xxxxx",               # 可选
  "venue": "KDD 2025",                  # 可选
  "citation_count": 42,                 # 可选，来自 Semantic Scholar
  "relation_type": "cites|cited_by|extends|uses_dataset",
  "relation_description": "提供了 MoE 路由的基础框架"
}

# ── 时间线 ──
Timeline {
  "target_paper_id": "2605.28175",
  "milestones": TimelineMilestone[],
  "span_years": [2015, 2026],
  "narrative": "从 2015 年的基础 KG 嵌入方法...到 2026 年 MoE 驱动的自适应检索..."
}

TimelineMilestone {
  "year": 2024,
  "event": "首个 LLM Agent 推荐框架发布",
  "paper_ids": ["arxiv_id_1", ...],
  "type": "foundation|breakthrough|incremental|application",
  "impact_description": "为后续多 Agent 协作推荐奠定基础"
}

# ── 质量评分 ──
QualityScore {
  "arxiv_id": "2605.28175",
  "overall_score": 0.82,
  "dimensions": {
    "citation_depth": 0.8,
    "citation_count": 0.6,
    "collaboration_breadth": 0.7,
    "topic_novelty": 0.9,
    "content_completeness": 0.85
  },
  "threshold_pass": true,
  "decision": "full_analysis",
  "scored_at": "ISO timestamp"
}
```

---

## 5. 文件与目录结构

### 5.1 新增目录

```
recommendation-system-learning/
│
├── data/
│   ├── citations/                    # ★ 新增 — 引用数据（临时，可重建）
│   │   └── {arxiv_id}/
│   │       ├── references.json       # 参考文献列表
│   │       ├── citations.json        # 被引列表
│   │       └── related_works.json    # 相关论文推荐
│   │
│   ├── graphs/                       # ★ 新增 — 图谱数据（可重建但有成本）
│   │   └── {arxiv_id}/
│   │       ├── academic_graph.json   # 统一 AcademicGraph 格式
│   │       ├── timeline.json         # 时间线数据
│   │       └── quality_score.json    # 质量评分结果
│   │
│   ├── enriched/                     # ★ 新增 — 增强版发布素材（永久保留）
│   │   └── {arxiv_id}/
│   │       ├── narrative.md          # 增强版文案（可直接发布）
│   │       ├── enriched_summary.json # 结构化增强版摘要
│   │       ├── citation_graph.png    # 引用关系图
│   │       ├── timeline.png          # 时间线演化图
│   │       └── topic_trend.png       # 主题变迁图（可选）
│   │
│   ├── parsed/                       # [现有] 不修改
│   ├── summaries/                    # [现有] 不修改
│   ├── merged/                       # [现有] 不修改
│   └── papers_metadata.json          # [现有] 扩展字段
│
├── skills/                           # ★ 新增 5 个 Skill 文件
│   ├── citation_collector.py         # A1
│   ├── graph_builder.py              # A2
│   ├── quality_scorer.py             # A3
│   ├── narrative_generator.py        # A4
│   └── graph_visualizer.py           # A5
│
├── models/                           # ★ 新增 1 个 Model 文件
│   └── academic_graph.py             # AcademicGraph + 辅助模型
│
├── workflows/                        # ★ 新增目录
│   └── daily_publish_with_analysis.py # 调度编排脚本
│
├── config/
│   └── settings.py                   # [修改] 新增配置项
│
└── redbook/scripts/
    └── publish_paper.py              # [最小修改] 扩展输入源
```

### 5.2 各目录生命期与缓存策略

| 目录 | 生命期 | 缓存策略 | 说明 |
|------|--------|---------|------|
| `data/citations/` | **临时** | 可随时删除重建 | 仅用于构建 AcademicGraph，建完后可清理。若 Semantic Scholar API 限流则保留 7 天作为缓存 |
| `data/graphs/` | **半持久** | 保留至论文发布后 30 天 | 重建成本较高（需 API 调用 + DeepSeek 推理），建议缓存。发布后 30 天自动清理 |
| `data/enriched/` | **永久** | 不自动删除 | 最终发布素材，与 `summaries/` 同级保留 |
| `papers_metadata.json` | **永久** | 增量更新 | 扩展 `analysis_status` 和 `quality_score` 字段 |

### 5.3 papers_metadata.json 扩展字段

现有每篇论文条目新增以下可选字段：

```
{
  "arxiv_id": "2605.28175",
  ...现有字段...

  // ★ 新增
  "analysis_status": "pending|collecting|building_graph|scoring|generating|visualizing|complete|failed",
  "quality_score": 0.82,                           // 来自 QualityScorer
  "quality_decision": "full_analysis|basic_only",
  "citation_graph_path": "data/graphs/2605.28175/academic_graph.json",
  "enriched_narrative_path": "data/enriched/2605.28175/narrative.md",
  "enriched_images": [
    "data/enriched/2605.28175/citation_graph.png",
    "data/enriched/2605.28175/timeline.png"
  ],
  "analysis_error": null                           // 若某步骤失败，记录原因
}
```

---

## 6. 工作流编排

### 6.1 调度脚本 workflows/daily_publish_with_analysis.py

这是整个增强流水线的"指挥中心"，负责串联现有链路与新增分析层。

#### 伪代码执行流程

```
#!/ 伪代码 —— 描述执行步骤

WORKFLOW: daily_publish_with_analysis

INPUT:
    --topics: 要处理的论文主题列表，默认 all
    --max-per-topic: 每主题最大论文数，默认 3
    --force-full-analysis: 强制所有论文触发完整分析，默认 False
    --skip-analysis: 跳过分析增强层，退化为原有流程，默认 False
    --time-budget: 总时间预算（分钟），默认 45

OUTPUT:
    发布报告：每篇论文的发布状态、分析深度、使用的图片

STEPS:

# ============================================================
# PHASE 0: 准备
# ============================================================
1. 初始化日志与配置
2. 检查各 Skill 的 is_ready 状态：
   - CitationCollector: Semantic Scholar API 可访问性
   - GraphBuilder: 依赖检查
   - DeepSeekSummarizer / NarrativeGenerator: API Key 配置
   - GraphVisualizer: matplotlib + 中文字体
3. 记录每个 Skill 的可用性 → 决定降级策略

# ============================================================
# PHASE 1: 现有链路 — 爬取 → 下载 → 解析 → 摘要（不修改）
# ============================================================
4. 调用现有的 BatchPipeline.run() 或逐个执行：
   FOR each topic IN topics:
       4a. ArxivSearcher → 获取论文列表
       4b. MetadataExtractor → 清洗元数据
       4c. PDFDownloader → 下载 PDF
       4d. PDFParser (MinerU) → 解析全文
       4e. DeepSeekSummarizer → 生成基础摘要
   → 产出: data/summaries/{id}_summary.md + papers_metadata.json

# ============================================================
# PHASE 2: 分析增强层（新增）
# ============================================================
5. FOR each paper IN selected_papers:
       5a. 检查是否已有分析结果（enriched/{id}/narrative.md 存在）
           → 若存在且非 --force：跳过
       5b. 若 --skip-analysis：跳过全部，标记为 basic_only

6. FOR each paper（可并行，但需控制 API 限流）:
       # --- A1: 引用采集 ---
       6a. CitationCollector.execute(arxiv_id, parsed_dir, metadata)
           → data/citations/{id}/*.json
           
           ON FAILURE: 记录 warning，若 references.json 为空
           → 后续步骤自动降级，quality_score 中 citation_count=0

       # --- A2: 图谱构建 ---
       6b. GraphBuilder.execute(arxiv_id, references, citations, related, metadata)
           → data/graphs/{id}/academic_graph.json + timeline.json
           
           ON FAILURE: 重试 1 次，若仍失败 → 标记 analysis_status=failed
           → 跳过该论文的后续分析步骤

       # --- A3: 质量评分 ---
       6c. QualityScorer.execute(arxiv_id, academic_graph, summary)
           → data/graphs/{id}/quality_score.json
           
           若 score < 0.7 且非 --force-full-analysis:
               → 标记 quality_decision=basic_only
               → 跳过 A4/A5，直接使用基础摘要发布

       # --- A4: 叙事生成（仅高分论文）---
       6d. IF quality_decision == "full_analysis":
               NarrativeGenerator.execute(arxiv_id, academic_graph, summary, timeline)
               → data/enriched/{id}/narrative.md
               
               ON FAILURE: 若 DeepSeek 不可用
               → 使用规则模板从 AcademicGraph 拼装

       # --- A5: 图谱可视化（仅高分论文）---
       6e. IF quality_decision == "full_analysis":
               GraphVisualizer.execute(arxiv_id, academic_graph)
               → data/enriched/{id}/*.png
               
               ON FAILURE: 跳过，发布时仅使用解析出的论文图片

7. 更新 papers_metadata.json 中每篇论文的 analysis_status

# ============================================================
# PHASE 3: 发布（修改输入源）
# ============================================================
8. FOR each paper:
       8a. 确定使用的文案:
           IF enriched/{id}/narrative.md 存在:
               使用增强版文案
           ELSE:
               使用 data/summaries/{id}_summary.md（基础摘要）

       8b. 确定使用的配图（最多 5 张）:
           IF enriched/{id}/*.png 存在:
               优先选取：citation_graph.png (1张) + timeline.png (1张)
               + 原有论文图片 (3张) = 共 5 张
           ELSE:
               仅使用原有论文图片 (5张)

       8c. 调用 publish_paper.py（或直接调用 xhs CLI）:
           xhs post --title "..." --body "..." --images ... --topic ...

9. 生成发布报告：
   {
     "published_at": "ISO timestamp",
     "papers_processed": 15,
     "full_analysis": 5,
     "basic_only": 10,
     "failed": 0,
     "total_time_minutes": 38,
     "details": [
       {"arxiv_id": "...", "status": "published", "analysis_depth": "full", "images": 5},
       ...
     ]
   }

# ============================================================
# PHASE 4: 清理
# ============================================================
10. 清理超过 30 天的 graphs/ 目录
11. 清理超过 7 天的 citations/ 目录（若 API 未限流）
12. 归档发布报告到 data/reports/
```

### 6.2 与现有模块的集成方式

**不修改现有代码，通过以下方式集成：**

1. **CLI 编排**：`workflows/daily_publish_with_analysis.py` 调用现有 `main.py` 的子命令或直接 import `BatchPipeline`
2. **文件间通信**：分析层只读写 `data/citations/`、`data/graphs/`、`data/enriched/` 目录
3. **publish_paper.py 最小扩展**：`format_body()` 增加一个文件存在性检查（若 enriched 存在则优先读取），不影响现有逻辑
4. **配置扩展**：在 `settings.py` 新增分析层配置项，带默认值，现有代码完全不受影响

---

## 7. 异常处理与容错

### 7.1 降级策略矩阵

| 故障场景 | 影响范围 | 降级行为 | 发布结果 |
|---------|---------|---------|---------|
| **Semantic Scholar API 不可用** | A1 引用采集 | 仅使用 PDF 内解析的参考文献；citations/related 字段为空 | 引用信息不完整但仍然可用 |
| **PDF 参考文献解析失败** | A1 引用采集 | references.json 为空列表 | AcademicGraph 中无引用节点 |
| **GraphBuilder 超时** | A2 图谱构建 | 重试 1 次 → 仍失败则跳过整篇论文的分析 | 该论文降级为基础摘要发布 |
| **QualityScorer 异常** | A3 评分 | 默认 score=0.5, decision=basic_only | 安全降级，不触发完整分析 |
| **DeepSeek API 限流/不可用** | A4 叙事生成 | 使用规则模板从 AcademicGraph 拼装文案 | 文案质量下降但结构完整 |
| **GraphVisualizer 字体缺失** | A5 可视化 | 回退到英文标签 + ASCII 字符 | 图片可正常生成 |
| **GraphVisualizer 超时** | A5 可视化 | 跳过图片生成，仅使用论文内图片 | 配图数量减少 |
| **总耗时超过 45 分钟** | 全局 | 中断分析队列，剩余论文全部 basic_only | 保证每日发布不中断 |
| **某篇论文所有分析步骤失败** | 单篇 | 标记 analysis_status=failed，发布基础摘要 | 不影响其他论文 |

### 7.2 超时控制

```
全局超时:        45 分钟（settings.ANALYSIS_TIME_BUDGET_MINUTES）
单篇论文总超时:   8 分钟
  ├── A1 CitationCollector:  180 秒
  ├── A2 GraphBuilder:       120 秒
  ├── A3 QualityScorer:       30 秒
  ├── A4 NarrativeGenerator:  60 秒
  └── A5 GraphVisualizer:     60 秒
```

超时控制由调度脚本在进程级实现（`subprocess.run(timeout=N)` 或 `concurrent.futures` 的 `result(timeout=N)`）。

### 7.3 日志与监控

| 日志级别 | 内容 |
|---------|------|
| **INFO** | 每篇论文进入/完成各步骤；评分结果与决策；总耗时 |
| **WARNING** | 某数据源不可用但已降级；评分阈值附近（0.65-0.75）；接近超时 |
| **ERROR** | 步骤失败且无法降级；DeepSeek API 连续 3 次失败；文件写入异常 |

**建议监控指标：**
- 每日 `full_analysis` vs `basic_only` 论文比例
- 各步骤平均耗时（识别性能瓶颈）
- Semantic Scholar API 可用率
- 图谱可视化失败率（中文字体问题）

---

## 8. 扩展方向预留

### 8.1 新增数据源

当前设计预留了 `CitationCollector` 的 `sources` 参数。未来接入新数据源时：

| 数据源 | 接入方式 | 提供的数据 |
|--------|---------|-----------|
| **OpenAlex** | REST API, 免费无需 Key | 引用网络、作者/机构、研究领域标签 |
| **DBLP** | REST API | 计算机科学领域论文元数据 |
| **Connected Papers** | Web 抓取 | 可视化引用图谱（参考） |
| **Papers With Code** | REST API | 论文 → 代码仓库映射、Benchmark 结果 |
| **本地引用数据库** | SQLite/CSV 文件 | 离线批量引用数据 |

接入新数据源只需：
1. 在 `CitationCollector` 中新增一个 `_collect_from_xxx()` 私有方法
2. 在 `sources` 列表中添加新源名称
3. 在 `settings.py` 添加对应的 API Key/URL 配置
4. 合并结果时使用现有的去重逻辑（`title_normalized + first_author_surname + year`）

### 8.2 新增可视化类型

`GraphVisualizer` 的 `output_types` 参数支持扩展：

| 可视化类型 | 说明 | 适用场景 |
|-----------|------|---------|
| `citation_graph` | 引用关系 DAG | 所有论文 |
| `timeline` | 时间线演化 | 综述论文（效果更佳） |
| `topic_trend` | 主题变迁桑基图 | 综述/多篇论文系列 |
| `author_network` | 作者合作网络 | 知名团队论文 |
| `institution_map` | 机构地理分布 | 跨国合作论文 |
| `keyword_cloud` | 关键词词云 | 快速概览 |

新增类型只需实现 `_render_{type}()` 方法，接收 `AcademicGraph`，输出 PNG。

### 8.3 多账号/多平台发布

`AcademicGraph` 和 `narrative.md` 是平台无关的中间格式：

- **小红书**（当前）：`publish_paper.py` 消费 `narrative.md` + PNG 图片
- **微信公众号**：消费 `narrative.md` + 不同的排版模板
- **知乎**：消费 `narrative.md` + 引用列表
- **Twitter/Thread**：消费 `narrative.md` 的 TL;DR 摘要

新增平台只需新增对应的发布脚本，消费相同的 `data/enriched/{id}/` 素材。

### 8.4 增量更新与缓存

当前设计已预留缓存点：

- `data/citations/` — 可缓存 7 天（引用关系短期内不变）
- `data/graphs/` — 可缓存 30 天（重建成本高）
- `papers_metadata.json` 中 `analysis_status` 字段 — 断点续传

后续可增加：
- 基于 arXiv ID 的缓存键 → 同一篇论文只分析一次
- 基于 Semantic Scholar Corpus ID 的引用缓存 → 多篇论文共享引用数据

### 8.5 批量分析与领域综述

当积累足够多论文（>20 篇）后，可增加：

- **跨论文主题聚类**：对所有已分析论文的 `topic_annotations` 做聚类
- **领域引用网络**：合并多篇论文的 `citation_graph` 为全局引用网络
- **研究热点报告**：基于 `timeline` 合并生成"推荐系统领域半年进展"

这些功能的数据基础已在 `AcademicGraph` 中预留。

---

## 9. 与现有系统的集成点

### 9.1 配置扩展（config/settings.py 新增属性）

```
class Settings:
    ...现有属性...

    # ── 分析增强层 ──
    @property
    def ENABLE_ANALYSIS_LAYER(self) -> bool:
        """是否启用分析增强层。默认启用，可关闭回退到原始流程。"""
    
    @property
    def ANALYSIS_TIME_BUDGET_MINUTES(self) -> int:
        """分析层总时间预算，超时则剩余论文降级处理。默认 45"""
    
    @property
    def QUALITY_THRESHOLD(self) -> float:
        """质量评分阈值。>= 此值触发完整分析。默认 0.7"""
    
    @property
    def SEMANTIC_SCHOLAR_API_BASE(self) -> str:
        """Semantic Scholar API 端点。免费无需 Key。"""
    
    @property
    def CITATION_CACHE_DAYS(self) -> int:
        """引用数据缓存天数。默认 7"""
    
    @property
    def GRAPH_CACHE_DAYS(self) -> int:
        """图谱数据缓存天数。默认 30"""
    
    @property
    def MAX_ANALYSIS_PAPERS_PER_RUN(self) -> int:
        """每次运行最多触发完整分析的论文数。默认 5"""
    
    @property
    def GRAPH_VIZ_DPI(self) -> int:
        """图谱可视化 DPI。默认 150"""
    
    @property
    def GRAPH_VIZ_SIZE(self) -> tuple:
        """图谱可视化尺寸 (width, height)。默认 (1200, 800)"""
```

### 9.2 publish_paper.py 的最小修改点

仅修改两个函数，不改变现有接口：

```
# 修改点 1：format_body() — 当 enriched narrative 存在时优先使用
def format_body(summary_text, arxiv_id, github_url="", enriched_narrative_path=None):
    IF enriched_narrative_path AND file_exists(enriched_narrative_path):
        text = read(enriched_narrative_path)
        # enriched narrative 已经是格式化好的 Markdown
        # 仅追加链接
        RETURN text + f'\n\narxiv 🔗：https://arxiv.org/abs/{arxiv_id}'
    ELSE:
        # 现有逻辑完全不变
        ...

# 修改点 2：find_images() — 扫描 enriched 图片目录
def find_images(arxiv_id, count=5):
    images = []
    # 优先选取 enriched 图谱图片
    enriched_dir = f"data/enriched/{arxiv_id}/"
    IF dir_exists(enriched_dir):
        images += [enriched_dir + "citation_graph.png", enriched_dir + "timeline.png"]
        remaining = count - len(images)
        images += [原有逻辑选取 remaining 张论文图片]
        RETURN images[:count]
    ELSE:
        # 现有逻辑完全不变
        ...
```

### 9.3 main.py 新增 CLI 命令（可选）

```
# 触发分析增强
python main.py analyze --arxiv-id 2605.28175

# 仅构建引用图谱
python main.py build-graph --arxiv-id 2605.28175

# 查看论文质量评分
python main.py score --arxiv-id 2605.28175

# 批量分析
python main.py analyze-all --topics agent-recommendation --max 5
```

### 9.4 Skill 注册（skills/__init__.py 新增导入）

遵循项目现有模式，新增的 5 个 Skill 通过 import 触发装饰器注册：

```
# skills/__init__.py
from skills.citation_collector import CitationCollector    # noqa: F401
from skills.graph_builder import GraphBuilder              # noqa: F401
from skills.quality_scorer import QualityScorer           # noqa: F401
from skills.narrative_generator import NarrativeGenerator  # noqa: F401
from skills.graph_visualizer import GraphVisualizer        # noqa: F401
```

---

## 附录 A: 技术选型建议

| 组件 | 推荐方案 | 备选方案 | 理由 |
|------|---------|---------|------|
| **引用数据采集** | Semantic Scholar API + PDF 参考文献解析 | OpenAlex API, Crossref API | 免费无需 Key，覆盖 CS 领域充分 |
| **图谱构建** | 自建 GraphBuilder (Python dict → JSON) | NetworkX, Neo4j (太重) | 图谱规模小（每篇 <200 节点），无需图数据库 |
| **图谱可视化** | matplotlib + networkx 布局 | Graphviz (pygraphviz), Plotly | 零外部服务依赖，本地渲染可控 |
| **中文字体** | 项目内置 Noto Sans SC 或系统 SimHei | — | 避免依赖系统字体 |
| **叙事生成** | DeepSeek API（已使用） | 本地 Ollama + Qwen | 复用现有 API，质量有保障 |
| **主题标注** | DeepSeek 零样本分类 | 本地 sentence-transformers | 复用现有 API |

## 附录 B: 时间预算分析

以单次运行处理 15 篇论文（6 大主题 × 2-3 篇）为例：

| 阶段 | 单篇耗时 | ×15 篇 | 备注 |
|------|---------|--------|------|
| 现有链路（①-④） | ~120s | ~30 min | 爬取+下载+解析+摘要，部分可并行 |
| A1 引用采集 | ~45s | ~11 min | Semantic Scholar API，可并行 |
| A2 图谱构建 | ~30s | ~8 min | 纯计算，无 API 调用 |
| A3 质量评分 | ~10s | ~3 min | 纯计算 |
| A4 叙事生成 | ~30s | ~8 min | DeepSeek API（仅高分论文 ~5 篇） |
| A5 图谱可视化 | ~20s | ~2 min | 本地渲染（仅高分论文 ~5 篇） |
| **合计** | — | **~40 min** | 在 45 分钟预算内 |

实际耗时可通过对 A1 做并发请求（Semantic Scholar 无严格限流）进一步压缩到 ~35 分钟。
