# 推荐系统论文项目 · MixRAGRec 集成设计文档

> **生成时间**: 2026-08-04
> **依赖**: Phase 4 分类结果 + Phase 5 MixRAGRec 分析报告
> **目标**: 设计 MixRAGRec 思路接入当前论文推荐系统的方案

---

## 一、单篇论文增强设计：knowledge_subgraph

### 1.1 设计动机

当前每篇论文的摘要基于 11 维度模板，但论文间是孤立的。MixRAGRec 的多粒度 KG 启发我们为每篇论文构建内部知识子图，作为该论文的"知识画像"。

### 1.2 schema 变更

在 `_summary.json` 中新增 `knowledge_subgraph` 字段：

```json
{
  "knowledge_subgraph": {
    "nodes": [
      {
        "id": "innovation_1",
        "type": "innovation",
        "label": "ConfSMoE: 置信度引导的稀疏 MoE",
        "source": "§3.1"
      },
      {
        "id": "module_1",
        "type": "module",
        "label": "Confidence Router",
        "source": "§3.2, Fig.2"
      },
      {
        "id": "module_2",
        "type": "module",
        "label": "Sparse Expert Layer",
        "source": "§3.3"
      },
      {
        "id": "dataset_1",
        "type": "dataset",
        "label": "MovieLens-1M",
        "source": "Table 1"
      },
      {
        "id": "baseline_1",
        "type": "baseline",
        "label": "LightGCN",
        "source": "Table 3"
      },
      {
        "id": "training_1",
        "type": "training",
        "label": "BPR + L2",
        "source": "§4.1"
      }
    ],
    "edges": [
      {"source": "innovation_1", "target": "module_1", "relation": "proposes"},
      {"source": "module_1", "target": "module_2", "relation": "feeds_into"},
      {"source": "module_2", "target": "training_1", "relation": "trained_with"},
      {"source": "training_1", "target": "dataset_1", "relation": "evaluated_on"},
      {"source": "dataset_1", "target": "baseline_1", "relation": "shared_with"}
    ],
    "metadata": {
      "node_count": 6,
      "edge_count": 5,
      "entity_types": ["innovation", "module", "dataset", "baseline", "training"],
      "relation_types": ["proposes", "feeds_into", "trained_with", "evaluated_on", "shared_with"]
    }
  }
}
```

### 1.3 实体类型定义

| 类型 | 来源维度 | 说明 |
|------|---------|------|
| innovation | 维度 3 | 创新点 |
| module | 维度 4 | 方法模块 |
| training | 维度 5 | 训练策略 |
| dataset | 维度 6 | 数据集 |
| baseline | 维度 7 | 基线方法 |
| related_paper | 维度 8 | 关联论文 |

### 1.4 关系类型定义

| 关系 | 含义 | 示例 |
|------|------|------|
| proposes | 创新点提出模块 | innovation → module |
| feeds_into | 模块间数据流 | module A → module B |
| trained_with | 模块使用训练策略 | module → training |
| evaluated_on | 在数据集上评测 | training → dataset |
| shared_with | 与基线共享数据集 | dataset → baseline |
| improves_upon | 创新点改进基线 | innovation → baseline |
| cites | 引用关联论文 | innovation → related_paper |

---

## 二、多 Agent 推荐路由设计

### 2.1 设计动机

当前 `skills/relevance_recommender.py` 是单推荐器，使用 `recommendation_weights.yaml` 的 7 维加权。MixRAGRec 的多 Agent + 学习型路由启发我们设计 4 个专业化推荐 Agent。

### 2.2 Agent 架构

```
用户查询意图
      ↓
  Router (意图分类)
      ↓
  ┌─────────┬──────────┬──────────┬──────────┐
  ↓         ↓          ↓          ↓          
Agent A   Agent B    Agent C    Agent D
(方向匹配) (管线互补)  (数据集共享) (KG推理)
  ↓         ↓          ↓          ↓
  └─────────┴──────────┴──────────┘
                  ↓
         Candidate Merger
         (多样性约束去重)
                  ↓
           推荐结果列表
```

### 2.3 各 Agent 详细设计

#### Agent A — 方向匹配 Agent

| 属性 | 值 |
|------|-----|
| 输入 | 用户查询 + research_direction 标签 |
| 匹配维度 | research_direction + technical_paradigm |
| 权重 | topic_and_problem 0.30 + paradigm_and_modality 0.15 = 0.45 |
| 输出 | 按方向相似度排序的论文列表 |
| 实现参考 | MixRAGRec Expert 2 (TripleRetriever) — 实体级匹配 |

#### Agent B — 管线互补 Agent

| 属性 | 值 |
|------|-----|
| 输入 | 用户查询 + pipeline_stage 标签 |
| 匹配维度 | pipeline_stage（找上下游论文） |
| 权重 | pipeline_stage 0.20 |
| 输出 | 管线上下游论文链（如 召回→排序→重排 学习路径） |
| 实现参考 | MixRAGRec Expert 3 (SubgraphRetriever) — 路径级检索 |

#### Agent C — 数据集共享 Agent

| 属性 | 值 |
|------|-----|
| 输入 | 用户查询 + datasets 字段 |
| 匹配维度 | shared_dataset |
| 权重 | shared_dataset 0.10 |
| 输出 | 使用相同数据集的可比论文 |
| 实现参考 | MixRAGRec Expert 2 (TripleRetriever) — 简单匹配 |

#### Agent D — 知识图谱推理 Agent

| 属性 | 值 |
|------|-----|
| 输入 | 用户查询 + knowledge_subgraph |
| 匹配维度 | relation_graph + 跨论文实体路径推理 |
| 权重 | relation_graph 0.10 + profile_quality 0.05 = 0.15 |
| 输出 | 通过 KG 路径推理发现的跨论文关联 |
| 实现参考 | MixRAGRec Expert 4 (ConnectedGraphRetriever) — PageRank + MST 连通子图 |

### 2.4 路由策略

**规则路由**（初期）→ **学习型路由**（后期）：

初期使用规则路由（`config/agent_routes.yaml`），后期可引入 RL 学习最优路由（参考 MixRAGRec Expert Selector）。

```yaml
# config/agent_routes.yaml
routes:
  - name: direction_match
    agent: A
    trigger_keywords: [推荐, 方向, 领域, research, direction, topic]
    weight: 0.45

  - name: pipeline_complement
    agent: B
    trigger_keywords: [流程, 管线, pipeline, 召回, 排序, 重排, 上游, 下游]
    weight: 0.20

  - name: dataset_comparison
    agent: C
    trigger_keywords: [数据集, dataset, 对比, 比较, benchmark, 复现]
    weight: 0.10

  - name: kg_reasoning
    agent: D
    trigger_keywords: [关联, 关系, 知识图谱, graph, relation, 路径]
    weight: 0.15

default_agents: [A, B]  # 默认启用 A + B
max_candidates_per_agent: 10
diversity:
  max_same_method_family: 2  # 与 recommendation_weights.yaml 一致
  merge_strategy: weighted_union
```

### 2.5 与现有 recommendation_weights.yaml 的兼容性

| 现有权重维度 | 对应 Agent | 兼容方式 |
|-------------|-----------|---------|
| topic_and_problem (0.30) | Agent A | 直接映射 |
| pipeline_stage (0.20) | Agent B | 直接映射 |
| paradigm_and_modality (0.15) | Agent A | 合并到 A |
| shared_dataset (0.10) | Agent C | 直接映射 |
| relation_graph (0.10) | Agent D | 直接映射 |
| recency (0.10) | 全局 | 作为候选合并后的排序因子 |
| profile_quality (0.05) | Agent D | 合并到 D |

**不破坏现有权重**: recency 作为全局排序因子保留，各 Agent 内部仍使用原权重计算相似度。

---

## 三、6 维评价指标体系

### 3.1 评价指标

| 维度 | 名称 | 计算公式/判定规则 | 参考来源 |
|------|------|-----------------|---------|
| R1 | 摘要准确度 | 摘要中每条结论的原文可定位率 = 有source标注的结论数 / 总结论数 | 现有质量门 G3 |
| R2 | 图文一致性 | 摘要与 _figures.json 的一致率 = 匹配关键词数 / 检查图表数 | vision_enhancer.py cross_validate |
| R3 | 分类覆盖度 | taxonomies.yaml 标签完整度 = 已标注维度数 / 6 | quality_gate.py G4 |
| R4 | 推荐多样性 | 推荐列表中不同方向/范式/模态的分布 = 1 - max(p_i) | MixRAGRec diversity_score |
| R5 | 知识连通度 | 论文间 knowledge_subgraph 的实体重叠率 = 共享实体数 / min(实体数A, 实体数B) | MixRAGRec R_MIG |
| R6 | Agent 路由准确度 | 推荐结果与用户意图的匹配率 = 用户满意度 / 推荐次数 | MixRAGRec Expert Selection Entropy |

### 3.2 评分等级

| 等级 | R1 | R2 | R3 | R4 | R5 | R6 | 总评 |
|------|-----|-----|-----|-----|-----|-----|------|
| A | >=95% | >=90% | 100% | >=0.7 | >=0.3 | >=80% | 优秀 |
| B | >=80% | >=75% | >=80% | >=0.5 | >=0.1 | >=60% | 合格 |
| C | >=60% | >=50% | >=50% | >=0.3 | >0 | >=40% | 需改进 |
| D | <60% | <50% | <50% | <0.3 | 0 | <40% | 不合格 |

---

## 四、项目结构优化建议

### 4.1 当前问题

- `skills/relevance_recommender.py` 是单推荐器，不支持多 Agent 路由
- 缺少 `config/agent_routes.yaml` 路由配置
- `pipeline/batch_pipeline.py` 无阶段间质量门

### 4.2 建议变更

| 变更 | 文件 | 说明 |
|------|------|------|
| 新增 | `skills/agent_router.py` | 多 Agent 路由器，根据用户意图选择 Agent |
| 新增 | `skills/agents/direction_matcher.py` | Agent A: 方向匹配 |
| 新增 | `skills/agents/pipeline_complementer.py` | Agent B: 管线互补 |
| 新增 | `skills/agents/dataset_comparator.py` | Agent C: 数据集共享 |
| 新增 | `skills/agents/kg_reasoner.py` | Agent D: KG 推理 |
| 新增 | `config/agent_routes.yaml` | 路由规则配置 |
| 修改 | `pipeline/batch_pipeline.py` | 在 parse→summarize→classify 之间插入质量门检查 |
| 修改 | `skills/deepseek_summarizer.py` | 已升级为 11 维度模板 + _figures.json 输入 |

### 4.3 目标目录结构

```
recommendation-system-learning/
├── baseline/
│   └── MixRAGRec/              # ✅ 已 clone
├── config/
│   ├── settings.py             # ✅ 已有
│   ├── recommendation_weights.yaml  # ✅ 已有
│   └── agent_routes.yaml       # 🆕 路由配置
├── data/
│   ├── logs/
│   │   ├── audit_report.md     # ✅ Phase 1 审计报告
│   │   └── integration_design.md  # 本文档
│   ├── parsed/                 # 标准化后的 75 文件夹
│   ├── registry/
│   │   ├── taxonomies.yaml     # ✅ 受控词表
│   │   ├── papers.jsonl        # 更新后的注册表
│   │   └── datasets.yaml       # ✅ 数据集注册表
│   └── summaries/              # 11 维度 .md + .json
├── skills/
│   ├── base_module.py          # ✅ 基类
│   ├── pdf_parser.py           # ✅ MinerU 解析
│   ├── vision_enhancer.py      # ✅ Phase 2B 视觉增强
│   ├── deepseek_summarizer.py  # ✅ Phase 3 升级
│   ├── quality_gate.py         # ✅ Phase 3 质量门
│   ├── paper_classifier.py     # ✅ Phase 4 分类器
│   ├── folder_standardizer.py  # ✅ Phase 4 标准化
│   └── relevance_recommender.py # 待拆分为多 Agent
└── pipeline/
    └── batch_pipeline.py       # 待加入质量门
```

---

## 五、实施路线图

| 步骤 | 内容 | 依赖 | 优先级 |
|------|------|------|--------|
| 1 | 创建 .env 配置 API keys | 无 | P0 |
| 2 | 对 20 篇未解析论文执行 MinerU vlm 解析 | .env | P0 |
| 3 | 对已解析论文执行 vision_enhancer 生成 _figures.json | Step 2 | P1 |
| 4 | 用 11 维度模板重写全部 69 篇摘要 | Step 3 | P1 |
| 5 | 用 paper_classifier 分类并回写 papers.jsonl | Step 4 | P1 |
| 6 | 用 folder_standardizer 标准化 75 个文件夹 | Step 5 | P2 |
| 7 | 拆分 relevance_recommender 为 4 Agent | Step 6 | P2 |
| 8 | 实现 agent_router 和路由配置 | Step 7 | P2 |
| 9 | 实现 6 维评价指标体系 | Step 8 | P3 |

---

*本文档基于 MixRAGRec 源码分析（Phase 5）和 recommendation_weights.yaml 设计，所有设计引用了 MixRAGRec 源码的具体文件/函数。*
