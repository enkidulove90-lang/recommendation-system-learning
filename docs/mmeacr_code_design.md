# MMEACR 代码落地阅读 + 后续实验设计

> **生成时间**: 2026-08-20
> **仓库**: https://github.com/JordanSancholhz/MMEACR → 已克隆至 `baseline/MMEACR/`（2026-08-20，depth=1）
> **论文**: Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation（arXiv:2607.07108）
> **前置文档**: `docs/mmeacr_migration_analysis.md`（论文级迁移评估，2026-08-19，当时结论"无代码"——**现已推翻，本档为代码级补充与实验设计**）
> **关联结论**: `docs/e15_tf_report.md`（PRISM 观点②否证，PRISM 收口为"多模态融合正则器"，E16/E17 未执行）

---

## 0. 结论速览（代码级）

| 维度 | 结论 |
| --- | --- |
| **仓库性质** | 论文官方代码（内部名 **Multi-modal AgentCF**），但**不等于论文全文**——只实现了论文叙事的一部分（属性引导 + 记忆门控 + RRF 评估；**MEM/GME 嵌入轨是评估期离线方案，无训练回路**） |
| **可运行性** | ⚠️ **不可直接运行**：数据集/embeddings/initial 记忆未提交（`dataset/` 仅 `dataset.md`）；路径硬编码 `/root/cds_images_*`；`negative_sampler.py`、`AgentCF_long_memory_eval.py` 缺失 |
| **代码里最有价值的 3 个机制** | ① **属性引导的强化-反思记忆更新**（创新点1，训练回路真实存在）② **UAMG 三段式记忆门控**（创新点2：置信度 + 非对称 + 软融合）③ **RRF 双轨融合评估**（`rrf_k=60` 等权倒数秩） |
| **与项目的关系** | 不是"拿来跑"，是"拆机制移植"：RRF 融合层（G 组接线）+ 属性引导记忆（PRISM 叙事转型的新锚）+ e_u 多模态画像（零外网，立即算） |
| **关键差距（必须诚实）** | 代码的"正确性信号"= `fuzz.ratio` 字符串匹配（**模拟环境合成标签**），非真实反馈 → 移植时需换成项目真实 next-item 标签 |

---

## 1. 代码结构地图（落地后）

```
baseline/MMEACR/
├── AgentCF_train_check.py   (46KB) 训练主循环：双 agent 对练 → 属性提取 → 门控 → 记忆更新
├── AgentCF_Test_log-.py     (24KB) 评估：LLM 排序 / Embedding 排序 / RRF 融合，输出 NDCG@1/5/10, MRR
├── memory_manager.py        (35KB) 记忆门控核心：STM/LTM 分数、非对称门控、软融合、门控回溯
├── prompt.py                (85KB) 全部 prompt 模板（属性提取/记忆更新/评估/置信度）
├── config.py                (12KB) 统一配置：数据集×训练模式×评估模式矩阵 + 创新点开关
├── dataPrepare.py           (7.8KB) 数据读取（.item/.train.inter/.test.inter/.random）
├── request.py / request1.py (4/5KB) GPT-4o 系 / GLM 系 API 异步封装（Semaphore+重试退避）
├── run_train_and_test.sh / run_train_test_for_reflection.sh
├── dataset/  memory/  log/         （空壳：无真实数据，只有占位文件）
└── README.md                        （训练/测试/代理配置说明）
```

### 执行流（训练 → 评估）

```
训练（AgentCF_train_check.py，5 轮/用户，round 0-4）
  per interaction:
    ① 读 user/item 记忆(纯文本) → LLM 从 pos/neg 二选一
    ② is_choice_right = fuzz.ratio(选中标题,pos) > fuzz.ratio(选中标题,neg)   ← 合成标签
    ③ [创新点1] 属性提取 prompt → LLM 输出 "attribute: item | polarity | score" → parse_attribute_rationale
    ④ create_prompts（round<2 基础 / 2-3 带 STM / >=4 带 STM+LTM）→ LLM 更新 self-introduction
    ⑤ [创新点2] parse_confidence(1-5→[0,1]) → evaluate_asymmetric_gate → soft_fusion_memory
       DIRECT(≥0.5) / FUSION(0.3~0.5 追加新句) / REJECT(<0.3)
    ⑥ update_user_memory（纯文本覆盖/融合）/ update_item_memory（不受门控）
  断点续训：checkpoint.json + gate_history 同轮覆盖去重

评估（AgentCF_Test_log-.py，4 模式）
  basic/description = 纯 LLM 排序；embedding = 纯 GME 余弦；rrf = LLM⊕embedding 倒数秩融合
  指标：NDCG@1/5/10 + MRR（不是项目 R@20 口径）
```

---

## 2. 优先级模块的**具体实现形式**（代码级，可移植）

### P0 ⭐ RRF 融合 —— `AgentCF_Test_log-.py:294` `rrf_fusion(embedding_ranking, llm_ranking, candidate_list, rrf_k=60)`

```python
emb_rank_dict = {item_id: rank+1 for rank, (item_id,_) in enumerate(embedding_ranking)}
llm_rank_dict = {item_id: rank+1 for rank, item_id in enumerate(llm_ranking)} if llm_ranking else {}
for item_id in candidate_list:
    r = 1.0/(rrf_k + emb_rank_dict.get(item_id, len(candidate_list)+1)) \
      + 1.0/(rrf_k + llm_rank_dict.get(item_id, len(candidate_list)+1))
```

**实现要点**：`rrf_k=60`（config `EVAL_CONFIGS["rrf"]`）；未出现项取 `len(candidates)+1` 倒数秩；**两轨等权 w=1**（无权重学习）；embedding 轨用 `dataset/embeddings/{D}/user_embeddings_gme.pkl` + `item_embeddings_gme.pkl`（`{'embedding': ...}` 字典），评分 = 归一化点积（余弦）。
**结论**：纯排序操作、零训练零 LLM，约 15 行 → **整个仓库里落地成本最低、收益最确定的模块**。

### P1 ⭐ 属性引导的强化-反思记忆更新 —— 创新点1（训练回路真实实现）

- **属性提取器**（`prompt.py:159/211` `attribute_analysis_prompt_correct/incorrect`）：9 维属性空间 `ATTRIBUTE_DIMENSIONS`（Functionality/Protection/Aesthetics/Compatibility/Durability/Portability/Innovation/Premium Quality/Security），要求 LLM 输出 `- Attribute: item_name | positive|negative | score(1-5)`，无属性输出 `NONE`；`temperature=0.1` 保证可解析性。
- **解析器**（`memory_manager.py:13` `parse_attribute_rationale`）：正则 `- \[?attr\]?: item | positive|negative | \d+` → `{dim: {item_name, polarity, score}}`，维度名 `lower().replace(' ','_')`。
- **强化/反思信号**：`is_choice_right=True` 用 correct prompt（强化：记忆里固化该属性）；`False` 用 incorrect prompt（反思：LLM 重写 self-introduction 纠正）——**prompt 分叉即"强化-反思"的实现形式**。
- **记忆载体**：纯文本 `user/user.{id}`（最新 self-introduction）+ `user-long/user.{id}`（每轮快照 `\n=====\n` 分隔，供 long-memory 评估）+ `stm_history/user_{id}.json`（结构化属性历史 `{round, gate_score, extracted_attrs}`）。

**移植价值**：这是 E14/E15 否证（L_syn 机制性阻断协同学习）之后，PRISM 叙事转型的最优承接——"从**协同学**（Unq/Syn/Red 信息论分解，失败）到**属性学**（显式属性轴偏好记忆，MMEACR 式强化-反思）"。

### P2 ⭐ e_u 多模态用户画像 —— `AgentCF_Test_log-.py:105` `compute_embedding_ranking`

- 用户嵌入 = `user_embeddings_gme.pkl` 预计算（GME: `Alibaba-NLP/gme-Qwen2-VL-7B-Instruct`，多模态编码标题+图像）；item 同理；排序 = 余弦相似度。
- 论文公式 e_u = mean(MEM(H_u, v̄_i)) 对应代码里"离线预计算 pkl"，**无在线训练回路**——即"嵌入轨是评估时离线方案"。
- **项目映射**：amazon-baby-mmssl 已有 CLIP 4096 + SBERT 384 真实特征 → `e_u = mean(CLIP⊕SBERT of interacted items)` 零外网直接可算，是 `prism_analysis.md §4.3` A2-2 用户级门控输入的升级版。

### P3 UAMG 记忆门控 —— 创新点2（`memory_manager.py`）

- **置信度门控 P0**（`parse_confidence`:115）：LLM 输出 `[Confidence Assessment] ... (1-5): <n> Justification:` → `n/5` 归一化 [0,1]，解析失败回退 0.5。
- **非对称门控 P1**（`evaluate_asymmetric_gate`:807）：两阶段——新属性准入低门槛（选对 0.9 / 选错 0.5）、已有属性极性翻转高门槛（有证据 0.5 / 无证据 0.0 硬拒绝）；探索权重 `0.5·exp(-0.3·(round-2))` 随轮次衰减；综合 `gate = 0.4·attr + 0.3·conf + 0.3·(1|0.5)`；无证据翻转封顶 0.35；阈值 0.30→0.35→0.40 随轮收紧。
- **软融合 P3**（`soft_fusion_memory`:955）：`≥0.5 → DIRECT`（整段替换）/ `0.3~0.5 → FUSION`（按句切分，与旧记忆词重叠<60% 视为新信息，追加 `" Additionally, ..."`）/ `<0.3 → REJECT`（保留旧记忆）。
- **门控失败回溯**（`find_best_attributes_from_history`:699 + `build_user_anchor`/`check_anchor_violation`）：门控不过时从 gate_history 找历史最高分轮次（Phase A: round≥2 最高分；Phase B: round 0 兜底），回滚其 user_response 与属性。

**移植价值**：门控机制与"5 轮 LLM 模拟"强耦合，**不建议整套移植**；但其中"三段式软融合 + 极性翻转硬保护"的思想可简化为轻量规则层，用于 PRISM 属性记忆的更新决策（见 §4 实验 M2）。

### 附带：数据与 API 封装（供移植参考）

- 数据：`.item`（id\t title）、`.train/.test.inter`（`user_id:token`/`item_id:token`）、`.random`（user\t candidates）；固定负样本 `train_negatives_seed42.json`（`total_pairs`+`negatives`）+ 评估候选 `eval_candidates_seed42.json`（`candidates[uid]={'candidates':[10],'target':id}`，即 **9 负 + 1 目标，candidate_num=10**）。
- API：`request.py`（OpenAI AsyncOpenAI，Semaphore=20，timeout=120s，重试 3 次退避 `2^n+U(0,0.5)`s，temp=0.6/max_tokens=2000，代理 127.0.0.1:7897）；`request1.py`（GLM httpx 直连 bigmodel.cn，默认 glm-4-flash）。→ 项目可复用此异步封装模式接 Zhipu GLM-4V-Flash 免费通道。

---

## 3. 与项目资产的接线点（更新自迁移分析 §2）

| 项目资产 | 接线点 | MMEACR 对应实现 | 依赖 |
| --- | --- | --- | --- |
| **MixRAGRec G 组**（LLM 生成 + Expert Selector RL） | RRF 融合层：LLM 生成排 ⊕ LightGCN++ 打分排 | `rrf_fusion`（P0） | 无（CPU，纯排序） |
| **PRISM**（E15 否证后=多模态融合正则器） | 属性引导记忆替代 L_syn：属性轴偏好记忆 + 强化-反思更新 | `attribute_analysis_prompt` + `parse_attribute_rationale` + 门控（P1/P3） | 需真实标签（替代 fuzz） |
| **LightGCN++ mm_align A2-2**（用户级门控，E17 未执行） | e_u 多模态用户画像输入 | GME 离线 pkl → 项目 CLIP/SBERT 均值（P2） | 无（零外网） |
| **评估口径** | 双轨 RRF 评估通道（新增 eval mode） | `EVAL_CONFIGS["rrf"]` + `rrf_fusion` | 无 |

---

## 4. 后续实验设计（怎么用）

### 总原则

> **移植机制，不移植代码**。仓库不可直接运行 + 正确性信号是合成 fuzz 标签 + 5 轮 LLM 模拟与项目图 CF 范式不同 → 按 §2 优先级抽取 P0/P1/P2 三个机制，分别落到项目现有资产上，全部用项目真实数据/标签重做口径。

### 实验矩阵（按优先级，均可 CPU 先行）

| # | 实验 | 内容 | 复用代码 | 前置 | 判定标准 |
| --- | --- | --- | --- | --- | --- |
| **M1** | **RRF 双轨融合层**（P0，最优先） | 在现有 LightGCN++ 打分基础上，叠加第二轨（如 SBERT 相似度排 / 后续 G 组 LLM 排），RRF 融合出最终排；对比单轨 R@20 | `rrf_fusion` 原样移植（~15 行），k∈{40,60,100} 扫描 + 权重 w∈{0.5,1.0} 扫描 | 无 | R@20 超过单轨最优（+0 即止，防过度工程） |
| **M2** | **属性引导记忆（PRISM 叙事转型落点）**（P1） | 属性轴 = 多模态特征轴（CLIP/SBERT 降维 K 维或文本关键词轴）；f_attr = item 特征与用户画像相似度 z∈R^K；**正确性信号用真实 next-item 命中**（替代 fuzz）；更新决策用三段式软融合（DIRECT/FUSION/REJECT） | `parse_attribute_rationale` 的结构化思路、`soft_fusion_memory` 三段式、极性保护 | M1 的评估通道；PRISM 结题叙事定稿 | 与"无属性记忆"基线比 R@20；并做门控开/关消融 |
| **M3** | **e_u 多模态用户画像**（P0/P1，零外网立即做） | `e_u = mean(CLIP⊕SBERT of interacted items)`，供 A2-2 用户级门控 / PRISM 用户锚；与纯 ID 均值消融 | GME 离线编码思想（换成本地特征） | 无 | 画像一致性指标 + 下游 R@20 |
| **M4** | **LLM 推理轨双轨评估通道**（G 组预备） | 建立 LLM 排 ⊕ CF 排的 RRF 评估框架，待 G 组 GPU 到位即插即用 | `EVAL_CONFIGS` 多模式 + `rrf_fusion` | M1；G 组 GPU | 评估通道可用性（冒烟） |

### 决策树（与 E15-TF 否证结论衔接）

```
E15-TF 否证（已定）：PRISM = 多模态融合正则器，不再主张推荐增益
        │
        ├─ M3（e_u 画像）→ 若提升 → 支持"正则器+画像"叙事，补 PRISM 结题报告
        │
        ├─ M1（RRF）→ 若提升 → 双轨融合成为后续架构标配（G 组直接继承）
        │
        └─ M2（属性引导）→ 若提升 → PRISM 叙事完成转型：
            从「协同分解（L_syn，否证）」→「属性轴记忆（强化-反思，M2）」
            这正是 MMEACR 迁移分析 §5 预言的"叙事新锚"路径，现在有代码背书
```

### 风险清单（代码级，新增）

| 风险 | 说明 | 缓解 |
| --- | --- | --- |
| R1 仓库≠论文 | 论文的"Memory Agent 双轨记忆"叙事在代码里被简化成 AgentCF 对练 + 评估期 RRF；MEM 训练回路缺失 | 移植对象以**代码实现为准**（§2），论文仅作叙事参考 |
| R2 合成标签 | `fuzz.ratio` 判对错 → 记忆更新信号是模拟的，无真实反馈 | M2 强制换成真实 next-item 标签，这是与项目的本质区别 |
| R3 规模差异 | 代码 100 用户级 Amazon 子集，项目 35k 级 → LLM 逐交互训练成本爆炸 | 只移植机制，不在全量数据上跑 LLM 回路；属性提取规则化/特征化 |
| R4 不可直接运行 | 缺数据、缺文件、路径硬编码 | 不尝试原样运行；按 §2 抽函数移植 |

---

## 5. 一句话总结

> **代码落地后确认：MMEACR 仓库是"AgentCF 对练 + 属性引导记忆 + 三段式门控 + RRF 评估"的实现集合，不是论文全文的直译**。对项目而言，真正值得移植的是三个机制——**RRF 融合（P0，15 行，G 组双轨融合层）、属性引导强化-反思记忆（P1，E15 否证后 PRISM 叙事转型的新锚，正确性信号须换真实标签）、e_u 多模态画像（P2，零外网立即算）**；门控（P3）只取"三段式软融合+极性保护"思想。实验按 M1→M3→M2 次序推进，全部 CPU 可跑，判定标准统一用项目 R@20 口径。
