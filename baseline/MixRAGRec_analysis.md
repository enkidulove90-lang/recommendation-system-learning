# MixRAGRec 源码分析报告

> **生成时间**: 2026-08-04
> **源码位置**: `baseline/MixRAGRec/`
> **GitHub**: https://github.com/Sjay-Wang/MixRAGRec
> **论文**: "Mixture-of-Experts Knowledge Graph Retrieval-Augmented Generation for Multi-Agent LLM-based Recommendation" (KDD 2026, arXiv:2605.28175)

---

## 一、系统架构总览

MixRAGRec 是一个基于多 Agent 协作的知识图谱检索增强推荐系统，核心由 3 个 Agent + 4 个检索专家组成：

```
用户查询 → Expert Selector Agent → 选择检索专家 (1-4)
                                        ↓
                              KG Retriever (4 Experts)
                                        ↓
                           Knowledge Alignment Agent
                              (KG → 自然语言)
                                        ↓
                           Recommendation Agent
                              (生成推荐 + 解释)
                                        ↓
                                   推荐结果
```

**训练框架**: MMAPO (Mixture-of-Experts Multi-Agent Policy Optimization)
- Expert Selector & Knowledge Aligner: PPO 策略优化
- Recommender: 偏好优化 (DPO-like with hard negatives)

---

## 二、5A — 多粒度知识图谱分析

### 2.1 KG 粒度层级（4 级）

| Expert ID | 名称 | 粒度层级 | 检索方式 | 源码位置 |
|-----------|------|---------|---------|---------|
| 1 | DirectGenerator | 无检索 | 使用 LLM 内部知识，不做 KG 检索 | `kg/retrieval/expert_direct.py` (50行) |
| 2 | TripleRetriever | 实体级（三元组） | 向量相似度检索 (h, r, t) 三元组 | `kg/retrieval/expert_triple.py` (120行) |
| 3 | SubgraphRetriever | 路径级（2-hop 子图） | 从种子实体出发，BFS 提取 2-hop 子图 | `kg/retrieval/expert_subgraph.py` (180行) |
| 4 | ConnectedGraphRetriever | 子图级（连通子图） | PageRank + MST 构建连通子图 | `kg/retrieval/expert_connected.py` (340行) |

### 2.2 KG 构建方式

| 维度 | 详情 | 源码位置 |
|------|------|---------|
| 数据源 | DBpedia 实体和关系（通过 SPARQL 查询） | `kg/utils/dbpedia_downloader.py` (238行) |
| 存储 | SQLite 数据库（`data/parsed_kg_from_dump.db`） | `kg/database/kg_database.py` (259行) |
| 实体对齐 | 电影/艺术家名称 → DBpedia URI 映射（map.csv） | `kg/database/rdf_parser.py` (159行) |
| 索引构建 | sentence-transformers/all-MiniLM-L6-v2 向量索引 | `kg/indexing/indexer.py` (245行) |
| 文本生成 | 将三元组转为自然语言描述 | `kg/indexing/text_generator.py` (257行) |

### 2.3 KG 检索方式

| Expert | 检索方式 | 参数 | 配置项 |
|--------|---------|------|--------|
| Expert 2 (Triple) | 向量相似度 Top-K | top_m=3 | `knowledge_graph.retrieval_top_m` |
| Expert 3 (Subgraph) | BFS 2-hop + 向量过滤 | max_neighbors_per_hop=20, max_subgraph_radius=2 | `knowledge_graph.max_neighbors_per_hop`, `max_subgraph_radius` |
| Expert 4 (Connected) | PageRank (alpha=0.85) + MST 连通 | pagerank_alpha=0.85, pagerank_max_iter=100 | `knowledge_graph.pagerank_alpha`, `pagerank_max_iter` |

### 2.4 KG 与推荐模型融合方式

- **非端到端**: KG 检索结果不直接作为 embedding 输入推荐模型
- **知识对齐**: Knowledge Alignment Agent 将结构化 KG 转为自然语言描述
- **Prompt 融合**: 对齐后的知识文本作为 LLM 推荐器的上下文输入
- **LoRA 微调**: 推荐器通过 LoRA (r=8, alpha=16) 微调以适应知识增强输入

---

## 三、5B — 多 Agent 选择分析

### 3.1 Agent 角色划分

| Agent | 角色 | 实现方式 | 源码位置 |
|-------|------|---------|---------|
| Expert Selector | 检索策略选择 | RL (PPO, Policy+Value Network) | `agents/expert_selector.py` (407行) |
| Knowledge Alignment | 知识对齐 | LLM (LoRA fine-tuned, 8-bit quantization) | `agents/knowledge_aligner.py` (1217行) |
| Recommendation | 推荐生成 | LLM (LoRA fine-tuned, constrained decoding) | `agents/recommender.py` (1528行) |

### 3.2 Agent 间协作机制

**串行 pipeline**（`agents/agent_coordinator.py`, 441行）:

```
Expert Selector → KG Retriever → Knowledge Alignment → Recommendation
     (选 expert)    (检索 KG)      (KG → NL)           (生成推荐)
```

- Expert Selector 根据用户查询状态选择最优检索专家 (1-4)
- KG Retriever 使用选中的专家执行检索
- Knowledge Alignment Agent 将结构化 KG 知识转为自然语言描述
- Recommendation Agent 基于对齐后的知识生成推荐（支持 constrained decoding 和 explanation）

### 3.3 每个 Agent 的输入输出

| Agent | 输入 | 输出 | 决策依据 |
|-------|------|------|---------|
| Expert Selector | 用户查询 embedding (state_dim=64) | Expert ID (1-4) + action probability | Policy Network (256→128→4) + ε-greedy 探索 |
| Knowledge Alignment | 检索到的 KG 三元组/子图 | 自然语言知识描述 (max 256 tokens) | LLM 生成 + confidence score |
| Recommendation | 对齐后知识 + 用户历史 + 选项 | 推荐选项 (A-T) + 解释 + option distribution | LLM constrained decoding + LoRA |

### 3.4 Agent 选择策略

**学习型路由** (RL-based):
- Policy Network: `nn.Linear(64, 256) → ReLU → Dropout → nn.Linear(256, 128) → ReLU → Dropout → nn.Linear(128, 4) → Softmax`
- Value Network: `nn.Linear(64, 256) → ReLU → nn.Linear(256, 128) → ReLU → nn.Linear(128, 1)`
- 探索策略: ε-greedy, ε_start=1.0, ε_end=0.05, ε_decay=0.995
- 训练: PPO, clip_epsilon=0.2, gamma=0.99, gae_lambda=0.95

---

## 四、5C — 评价指标分析

### 4.1 标准评价指标

| 指标 | 说明 | 配置位置 |
|------|------|---------|
| Accuracy (Top-1) | 推荐选项是否正确 | `evaluation.metrics` |
| Recall@3 | 正确答案在 Top-3 中 | `evaluation.metrics` |
| Recall@5 | 正确答案在 Top-5 中 | `evaluation.metrics` |
| MRR | 平均倒数排名 | `evaluation.metrics` |

### 4.2 超越标准的创新指标

| 指标 | 公式/定义 | 源码位置 | 意义 |
|------|----------|---------|------|
| **R_MIG (Marginal Information Gain)** | R_MIG = ΔI - η·Cost | `marl/reward_functions.py` L1-483 | 衡量检索专家相比基线 (Expert 1) 的信息增益减去检索成本 |
| **Expert Selection Entropy** | H = -Σ p_i·log2(p_i) | `src/test.py` L347-359 | 衡量专家选择的多样性（0=单一选择, 1=均匀分布） |
| **Cost Penalty** | η · Cost(expert_id) | `marl/reward_functions.py` L24-29 | 惩罚高成本检索（Expert 1:0.0, 2:0.1, 3:0.2, 4:0.3） |
| **Diversity Score** | 推荐结果的多样性 | `core/evaluator.py` | 推荐列表中不同类型物品的分布 |
| **Quality Score** | 推荐质量 | `core/evaluator.py` | 基于推荐理由的质量评估 |
| **Confidence Score** | 生成置信度 | `agents/recommender.py` | LLM 生成的 option distribution 的最大值 |

### 4.3 奖励函数

```
R_total = R_rec + λ · R_MIG

其中:
  R_rec = 1.0 * confidence  (正确) 或 -0.1  (错误)
  R_MIG = ΔI - η · Cost(expert)
    ΔI = KL(P_expert || P_baseline)  (信息增益，用输出分布的 KL 散度)
    Cost = {1: 0.0, 2: 0.1, 3: 0.2, 4: 0.3}
    λ = 0.2 (lambda_mig), η = 0.005 (eta_cost)
```

### 4.4 评价流程

1. 对每个测试样本执行完整 pipeline（Selector → Retriever → Aligner → Recommender）
2. 使用 constrained decoding 提取预测选项 (A-T)
3. 计算 Top-1/3/5 accuracy
4. 统计 Expert 使用分布和选择熵
5. 保存详细结果到 `results/test_results_*.txt`

---

## 五、配置参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| LLM backbone | Llama-3.1-8B-Instruct / Mistral-7B / Qwen2.5-7B | 可选 LLM |
| LoRA rank | 8 | 知识对齐 + 推荐器 |
| LoRA alpha | 16 | 缩放系数 |
| state_dim | 64 | Expert Selector 状态维度 |
| num_experts | 4 | 检索专家数量 |
| retrieval_top_m | 3 | Top-M 检索结果 |
| max_subgraph_radius | 2 | 子图最大跳数 |
| max_neighbors_per_hop | 20 | 每跳最大邻居数 |
| pagerank_alpha | 0.85 | PageRank 阻尼系数 |
| PPO clip_epsilon | 0.2 | PPO 裁剪参数 |
| PPO gamma | 0.99 | 折扣因子 |
| preference_beta | 0.1-0.2 | 偏好优化温度 |
| lambda_mig | 0.2 | R_MIG 权重 |
| eta_cost | 0.005 | 成本惩罚系数 |
| seed | 42 | 随机种子 |

---

## 六、对当前项目的启示

1. **多粒度 KG 检索可迁移到论文间推荐**: MixRAGRec 的 4 级检索粒度（无检索→三元组→子图→连通图）可映射到论文知识图谱（论文→创新点→模块→数据集→基线）
2. **学习型路由优于固定路由**: Expert Selector 用 RL 学习最优路由策略，比固定规则更灵活
3. **知识对齐是关键中间步骤**: 结构化知识 → 自然语言的转换使 LLM 能有效利用 KG
4. **成本感知奖励函数**: R_MIG 兼顾信息增益和检索成本，适合论文推荐中"简单匹配 vs 深度推理"的权衡
