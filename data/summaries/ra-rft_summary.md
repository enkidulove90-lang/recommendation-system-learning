# 类比推理的检索增强强化微调

**英文标题**: Learning to Reason by Analogy via Retrieval-Augmented Reinforcement Fine-Tuning
**arXiv ID**: ra-rft
**论文类型**: 长文 + 方法创新（训练策略创新）
**venue**: 论文未提及
**年份**: 2026
**一句话概括**: 提出RA-RFT框架，用推理效用检索增强RLVR训练，提升数学推理能力。
**生成时间**: 2026-08-04T14:16:38.800739

---

## 维度 0: 元信息

| 字段 | 内容 |
|------|------|
| 论文标题 | 类比推理的检索增强强化微调 |
| 英文标题 | Learning to Reason by Analogy via Retrieval-Augmented Reinforcement Fine-Tuning |
| arXiv ID | ra-rft |
| 论文类型 | 长文 + 方法创新（训练策略创新） |
| venue | 论文未提及 |
| 年份 | 2026 |

## 维度 1: 论文类型

长文 + 方法创新（训练策略创新）

## 维度 2: 研究背景与问题定义

- **任务类型**: 数学推理（竞赛级）
- **输入**: 数学问题文本（q），可选检索到的推理轨迹（c）
- **输出**: 答案（a）及推理过程
- **来源**: Section 3.1

## 维度 3: 主要创新点

1. **提出gold-relevance distillation，用judge模型（GPT-4o）直接评估候选推理轨迹与目标问题的推理相关性，构建基于推理效用的检索监督信号。**
   - 分类: 方法
   - 来源: Section 3.2, Algorithm 1 (lines 3-7)
2. **训练reasoning-aware retriever，使用对比学习（InfoNCE）优化密集检索器，使其能检索到结构相似但表面不相似的推理轨迹。**
   - 分类: 方法
   - 来源: Section 3.3, Equation (2)
3. **将检索到的推理轨迹作为演示注入RLVR训练，通过GRPO等策略优化算法，使模型学会利用外部类比推理轨迹，提高奖励信号密度。**
   - 分类: 训练策略
   - 来源: Section 3.4, Equation (3)
4. **与最接近工作QuestA（课程学习）和OPSD（自蒸馏）的区别：RA-RFT不依赖逐步提示或特权轨迹，而是通过检索外部类比轨迹来增强推理，且与具体策略优化算法无关。**
   - 分类: 方法
   - 来源: Section 3.1, Section 4.2, Table 1

## 维度 4: 方法与模块

| 模块名称 | 作用 | 输入 | 输出 | 来源 |
|----------|------|------|------|------|
| Gold-Relevance Distillation | 构建检索监督信号，评估推理轨迹与查询的推理相关性 | 训练问题(q_i)、候选轨迹(c)、judge模型(M_judge) | 二元相关性标签(y_{i,c}) | Section 3.2, Algorithm 1 (lines 3-7) |
| Reasoning-Aware Retriever | 根据推理相关性检索top-k个类比推理轨迹 | 查询(q)、检索语料库(C)、查询嵌入(e_q)、轨迹嵌入(e_c) | top-k推理轨迹({c_1, ..., c_k}) | Section 3.3, Equation (2), Algorithm 1 (line 15) |
| Reinforcement Fine-Tuning with Retrieved Demonstrations | 利用检索到的推理轨迹作为上下文，通过RLVR优化目标模型 | 问题(q)、检索到的轨迹({c_j})、目标模型(M_phi)、奖励函数(r) | 更新后的模型参数(phi) | Section 3.4, Equation (3), Algorithm 1 (lines 16-19) |

## 维度 5: 训练策略

- **损失函数**: 主损失：GRPO（组相对策略优化），基于二元结果奖励；辅助损失：检索器训练使用InfoNCE对比损失；无额外正则项（KL惩罚被禁用）。
- **正负样本构造**: 正样本：judge模型判定为推理相关的轨迹；负样本：批次内其他轨迹（in-batch negatives）；比例：未明确提及；mask策略：未提及。
- **优化与训练流程**: 策略模型：AdamW，学习率1e-6；检索器：学习率3e-5，线性warmup（10%步数），权重衰减0.01，批次大小128，训练3个epoch；策略模型训练使用64块H100 GPU。
- **预训练**: 两阶段：先训练检索器（基于Reason-ModernColBERT），再冻结检索器训练策略模型；检索器预训练数据为推理密集型语料（Reason-ModernColBERT），策略模型从Qwen3-1.7B/4B Instruct初始化。
- **来源**: Section 4.1, Section A

## 维度 6: 数据集选择

| 名称 | 用户数 | 物品数 | 交互数 | 切分方式 | 来源 |
|------|--------|--------|--------|---------|------|
| QuestA训练集 | 论文未提及 | 论文未提及 | 12.5k问题 | 训练查询 | Section 4.1 |
| OpenR1-Math-220K | 论文未提及 | 论文未提及 | 220K问题（作为检索语料库） | 排除与训练集重叠的问题 | Section 4.1 |
| AIME 2024 | 论文未提及 | 论文未提及 | 论文未提及 | 测试集 | Section 4.1 |
| AIME 2025 | 论文未提及 | 论文未提及 | 论文未提及 | 测试集 | Section 4.1 |
| HMMT February 2025 | 论文未提及 | 论文未提及 | 论文未提及 | 测试集 | Section 4.1 |
| BrUMO 2025 | 论文未提及 | 论文未提及 | 论文未提及 | 测试集 | Section 4.1 |

## 维度 7: 实验与 Benchmark

- **评测指标**: average@32 accuracy
- **基线方法**: Base (Instruct), GRPO, OPSD (结果来自原论文，average@16), QuestA (仅Qwen3-1.7B)
- **主结果**: Qwen3-1.7B: RA-RFT在AIME24上55.1 vs GRPO 50.4 (+4.7), AIME25上48.7 vs 41.6 (+7.1), HMMT25上28.2 vs 26.3 (+1.9), BrUMO25上57.4 vs 54.8 (+2.6), Avg 47.4 vs 43.3 (+4.1)。Qwen3-4B: RA-RFT在AIME24上75.8 vs GRPO 74.8 (+1.0), AIME25上69.2 vs 66.4 (+2.8), HMMT25上47.3 vs 46.4 (+0.9), BrUMO25上75.7 vs 69.8 (+5.9), Avg 67.0 vs 64.4 (+2.6)。
- **显著性**: 论文未提及
- **在线实验**: 论文未提及
- **来源**: Table 1, Section 4.2

## 维度 8: 关联论文

- [[Shao et al., 2024]] 对标/改进: GRPO，标准RLVR方法，RA-RFT以其为基础并改进。
- [[Li et al., 2026]] 对标: QuestA，通过课程学习注入部分解决方案，RA-RFT与其对比。
- [[Zhao et al., 2026]] 对标: OPSD，自蒸馏方法，RA-RFT与其对比。
- [[Chafin, 2025]] 理论依据/基础: Reason-ModernColBERT，多向量检索模型，RA-RFT的检索器初始化于此。
- [[Su et al., 2025]] 理论依据: BRIGHT基准，论证了推理效用与语义相似性的弱相关性。

## 维度 9: 复现性

- 代码开源: 否/论文未提及
- 数据公开: 否/论文未提及
- 超参完整: 是
- 随机种子: 论文未提及

## 维度 10: 局限性

论文自承局限：未显式提及。 [阅读者判断]：1) 依赖GPT-4o作为judge模型，成本高且可能引入偏差；2) 检索语料库和训练集均来自NuminaMath-1.5，可能限制了泛化性；3) 仅评估了数学推理领域，未验证在其他推理任务上的有效性；4) 训练计算资源需求高（64块H100），可能限制可复现性。

---

*由 DeepSeek (deepseek-chat) 自动生成 | 11 维度模板*
