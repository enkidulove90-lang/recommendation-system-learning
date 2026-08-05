# NLGCL+：邻接层自然对比学习 + 多模态自适应样本加权

> 本文档严格依据论文原文（MinerU 解析全文 `data/parsed/3806231_NLGCL-Plus/3806231_NLGCL-Plus.md`）撰写。
> 每条结论标注来源（§章节 / Eq.公式号 / Table 表号 / Fig.图号）。论文未提及处标注「论文未提及」，阅读者推断标注 `[阅读者判断]`。

---

## 维度 0：元信息

| 字段 | 内容 | 来源 |
|------|------|------|
| 论文标题 | NLGCL+: Naturally Existing Neighbour Layers Graph Contrastive Learning with Adaptive Sample Weighting for Multimodal Recommendation | 标题页 |
| 作者 / 机构 | Jinfeng Xu, Zheyu Chen, Shuo Yang, Jinze Li, Hewei Wang, Wei Wang, Xiping Hu, Edith Ngai\*（香港大学 EEE、北京理工大学、卡内基梅隆大学、澳门理工大学） | 标题页 |
| 发表 venue | ACM Transactions on Recommender Systems (TORS) | 页脚 "ACM Trans. Recomm. Syst." |
| 发表年份 | 2026（DOI 3806231） | 文件标识 |
| arXiv ID / DOI | ACM DL 3806231；无 arXiv ID | 标题页 |
| 论文类型 | 期刊长文（25 页）；期刊扩展版（会议版 NLGCL [43] 的 journal extension） | §1 "Our previous work, NLGCL [43]" |
| 阅读日期 | 2026-08-05 | — |
| 一句话概括 | 用 GNN 相邻层天然构成对比视图，并用多模态原始特征预计算权重加权正负样本 | 摘要 |
| 代码 | https://github.com/Jinfeng-Xu/NLGCL-Plus | 摘要末 |

---

## 维度 1：论文类型

- **按篇幅/venue**：TORS 期刊正式长文，25 页，含完整方法、理论证明（Theorem 1）、8 个 RQ 的实验。
- **按贡献类型**（多重）：
  | 类型 | 本文对应 |
  |------|----------|
  | 方法/模型创新 | ASW（Adaptive Sample Weighting）模块，Eq.10–15 |
  | 理论创新 | Theorem 1 + Lemma 1 + Corollary 1（低层对比视图互信息更高），§4.1 |
  | 训练策略创新 | 免增强（augmentation-free）的邻接层对比范式，§3.2 |
  | 数据集/评测创新 | 无（沿用 MMRec [53] 标准划分） |
  | 应用/系统创新 | 无 |
- **定位**：plug-and-play 即插即用模块，不是独立推荐模型（§1 contributions、§3.1）。

---

## 维度 2：研究背景与问题定义

### 背景与动机
- **要解决的问题**：多模态推荐中 GNN 受数据稀疏性制约；现有 GCL 依赖计算密集的数据增强策略，且可能引入语义无关噪声（摘要 + §1 第 2 段）。
- **为什么重要**：多模态场景下"构建、处理、存储多个增强图视图"带来显著时间与内存开销，严重限制 GCL 在真实多模态推荐中的可扩展性与部署（§1 第 3 段）。
- **现有方法不足**（论文明确列出，§1 第 3 段）：
  1. **有效性**：随机增强（节点/边 dropout、特征掩码、加噪）可能破坏关键结构与特征信息；多模态场景下任意扰动无法保持跨模态一致性。
  2. **效率**：多模态信息与模态专属复合图本身已增加复杂度，再构建多视图开销剧增。
  3. **负样本武断**：传统 GCL 把语义相似节点武断地当作负样本（§3.2 Analysis 段）。
  4. **样本等权**：多正样本情形下等权处理是次优的（§3.3，引用 [7]）。

### 问题形式化
- **任务类型**：多模态推荐 Top-K 排序（隐式反馈）。
- **输入**：用户-物品交互二部图 $\mathcal{G}$；物品多模态原始特征 $\mathbf{x}_i^m$（$m \in \mathcal{M}=\{t,v,a\}$ 文本/视觉/音频）+ 行为模态 $id$。
- **输出**：融合后的用户/物品表征 $\bar{E}_u, \bar{E}_i$，用于打分排序。
- **核心符号**（Table 1）：

  | 符号 | 含义 |
  |------|------|
  | $\mathcal{M}=\{t,v,a\}$, $id$ | 显式模态（文/视/音）与行为模态 |
  | $\mathbf{x}_i^m,\mathbf{x}_u^m$ | 物品 i / 用户 u 在模态 m 的**原始特征** |
  | $\mathbf{e}_u^{m/id}(l)$ | 第 l 层用户表征 |
  | $\mathcal{W}$ | **相似度矩阵**（ASW 权重） |
  | $\mathcal{L}_{nl_u},\mathcal{L}_{nl_i},\mathcal{L}_{nl}$ | 用户侧 / 物品侧 / 总邻接层 GCL 损失 |
  | $\mathcal{L}_{ori}$ | 骨干模型原始推荐损失 |
  | $G$ | 对比视图组数，$G \le L$ |

---

## 维度 3：主要创新点

- **创新点 1（主）**：*"leverages the naturally existing contrastive views within GNNs"* —— 指出 GNN 消息传递机制下，**相邻层的异构节点天然构成正样本对**，无需任何外部数据增强（§3.2，由 Eq.8 与 Eq.9 联立推导）。
  - 分类：方法 + 训练策略。
- **创新点 2（主）**：*"fully harnesses multimodal information to perform adaptive sample weighting"* —— **ASW**：用多模态**原始特征**（而非训练中动态学习的表征）在训练前预计算相似度矩阵 $\mathcal{W}$，对正/负样本分别加权（§3.3，Eq.10–15）。
  - 分类：方法。
  - 关键论证：动态学习的多模态表征会引入噪声与偏置、易陷入局部最优（引用 [32,54,35]）；原始特征"质量稳定、训练中不变、处于同一特征空间"（引用 [40]）。
- **创新点 3（理论）**：Theorem 1 —— 相邻层 $(l, l+1)$ 构成的对比视图在 $l$ 越小时越有效；因此选**前 G 组**最优（§3.3 陈述，§4.1 证明）。
- **创新点 4（范围划分）**：提出 Heterogeneous（H）与 Entire（E）两种负样本 scope，并实证 H 优于 E（Table 2 定义，Table 6 实证）。

**与最接近工作（自家会议版 NLGCL [43]）的区别**（论文自述，§5.2 Observation4）：
> "compared to NLGCL, it performs adaptive sample weighting guided by modality information, enabling more fine-grained representation learning."

即：NLGCL → NLGCL+ 的**唯一增量就是 ASW**（外加多模态场景适配与理论补强）。

**自我评估** `[阅读者判断]`：属于**期刊扩展的增量式创新**。邻接层对比视图是会议版已有的核心洞见；本文的实质新增是 ASW（一个训练前预计算的余弦相似度加权项）。理论部分（Theorem 1）严谨性有限——Lemma 1 假设高斯嵌入分布、Eq.20 中 $\Sigma^{(l)}=\tilde{\mathcal{A}}^2\Sigma^{(l-1)}$ 的推导略去了 $\tilde{\mathcal{A}}$ 与 $\Sigma$ 不可交换的问题。

---

## 维度 4：方法与模块

### 整体架构
- 架构图：Fig. 1（(a) 传统 GCL 增强视图 vs (b) 本文自然邻接层视图）。
- Pipeline（训练阶段）：

```
[多模态原始特征 x_i^m] ──(Eq.10 均值池化)──> [用户原始特征 x_u^m]
          │                                          │
          └──────────(Eq.11 余弦相似度)──────────────┘
                            ↓
                 [相似度矩阵 W]  ← 训练前一次性预计算（仅用训练集）
                            ↓
[骨干多模态模型] ─逐层融合表征─> [E(0), E(1), ..., E(L)]
                            ↓
        取前 G 组相邻层 (g, g+1) 构成对比视图
                            ↓
        [ASW 加权 InfoNCE] Eq.12/13 (H) 或 Eq.14/15 (E)
                            ↓
        L = L_ori + λ · L_nl     (Eq.16)
```

- **推理阶段**：ASW 与 CL 损失完全不参与，结构与骨干模型一致（§3.4，`[阅读者判断]` 由 Eq.16 只作用于训练损失推得）。

### 模块清单

#### 模块 A：自然邻接层对比视图构造（Naturally Existing Contrastive Views）

| 字段 | 内容 |
|------|------|
| 模块名称 | Naturally Existing Contrastive Views within GNNs（§3.2） |
| 作用 | 不做任何数据增强，直接把 GNN 相邻两层的异构节点表征当作对比视图 |
| 输入 | 骨干模型逐层融合表征 $\{\bar{E}(0),\dots,\bar{E}(L)\}$ |
| 输出 | $G$ 组对比视图对 $(\bar{E}(g), \bar{E}(g+1))$，$g=0..G-1$ |
| 实现细节 | Eq.8（消息传递）+ Eq.9（改写）联立推导；正样本定义 §3.2.1，负样本定义 §3.2.2，汇总于 Table 2 |
| 关键设计选择 | 对**融合后的最终表征**做对比而非各模态单独对比 —— 理由：提升跨模型泛化性、消除不同模态聚合策略的影响、降低复杂度且效果更好（§3.1 末段 + §5.1.4 末段） |
| 消融证据 | 无独立消融（该部分是会议版 NLGCL 的贡献）；但 Table 6 中 NLGCL 一行即为"仅此模块"的效果 |

**正/负样本定义（Table 2）**：

| 锚点 | Scope | 正样本 | 负样本 |
|------|-------|--------|--------|
| $\mathbf{e}_u^{m/id}(l-1)$ | Heterogeneous | $\mathbf{e}_{\tilde i}^{m/id}(l),\ \tilde i \in \mathcal{N}_u$ | $\mathbf{e}_{\hat i}^{m/id}(l),\ \hat i \notin \mathcal{N}_u$ |
| $\mathbf{e}_u^{m/id}(l-1)$ | Entire | 同上 | $\mathbf{e}_{\hat i}^{m/id}(l) \cup \mathbf{e}_u^{m/id}(l)$ |
| $\mathbf{e}_i^{m/id}(l-1)$ | Heterogeneous | $\mathbf{e}_{\tilde u}^{m/id}(l),\ \tilde u \in \mathcal{N}_i$ | $\mathbf{e}_{\hat u}^{m/id}(l),\ \hat u \notin \mathcal{N}_i$ |
| $\mathbf{e}_i^{m/id}(l-1)$ | Entire | 同上 | $\mathbf{e}_{\hat u}^{m/id}(l) \cup \mathbf{e}_i^{m/id}(l)$ |

> **关键特性**：每个锚点有**多个正样本**（其全部一阶邻居），这与传统 GCL 的单正样本范式根本不同（§3.2 Analysis）。

#### 模块 B：ASW 自适应样本加权（Adaptive Sample Weighting）

| 字段 | 内容 |
|------|------|
| 模块名称 | Adaptive Sample Weighting via Multimodal Information（§3.3） |
| 作用 | 用多模态原始特征的跨模态语义一致性，区分难负样本与无关负样本，给每个正/负样本对赋权 |
| 输入 | 物品原始多模态特征 $\mathbf{x}_i^m$（视觉 4096-d / 文本 384-d 等） |
| 输出 | 相似度矩阵 $\mathcal{W} \in \mathbb{R}^{(\vert\mathcal{U}\vert+\vert\mathcal{I}\vert)\times(\vert\mathcal{U}\vert+\vert\mathcal{I}\vert)}$（E scope）或 $\mathbb{R}^{\vert\mathcal{U}\vert\times\vert\mathcal{I}\vert}$（H scope） |
| 实现细节 | Eq.10（用户原始特征 = 其交互物品原始特征均值）；Eq.11（各模态余弦相似度**求和**） |
| 关键设计选择 | ① 用**原始特征**而非训练中的表征 —— 稳定、无噪声/偏置、可训练前预计算；② 严格只用训练集构建，避免信息泄漏（§3.3 明确声明） |
| 复杂度 | 一次性预计算：E scope $O(\vert\mathcal{M}\vert\vert\mathcal{V}\vert^2 d_m)$，H scope $O(\vert\mathcal{M}\vert\vert\mathcal{U}\vert\vert\mathcal{I}\vert d_m)$；训练期零额外开销（§3.3 Efficiency） |
| 消融证据 | **有**：§5.3 w/o-ASW 变体（Fig. 2）。Observation1 —— 带 ASW 显著优于 w/o-ASW，验证 ASW 必要性 |

**已知局限（论文自承，§3.3）**：Eq.10 的均值池化对交互极少的用户会产生噪声表征；论文以 5-core 过滤作为部分缓解。

#### 模块 C：损失函数

**Heterogeneous scope（Eq.12/13）**：

$$\mathcal{L}_{nl_u} = -\frac{1}{G|\mathcal{U}|}\sum_{g=0}^{G-1}\sum_{u\in\mathcal{U}}\frac{1}{|\mathcal{N}_u|}\log\frac{\prod_{i^+\in\mathcal{N}_u}\exp(\mathcal{W}_{u,i^+}(\mathbf{e}_u^{(g)\top}\mathbf{e}_{i^+}^{(g+1)})/\tau)}{\sum_{\hat i\in\mathcal{I}}\exp(\mathcal{W}_{u,\hat i}(\mathbf{e}_u^{(g)\top}\mathbf{e}_{\hat i}^{(g+1)})/\tau)}$$

$$\mathcal{L}_{nl_i} = -\frac{1}{G|\mathcal{I}|}\sum_{g=0}^{G-1}\sum_{i\in\mathcal{I}}\frac{1}{|\mathcal{N}_i|}\log\frac{\prod_{u^+\in\mathcal{N}_i}\exp(\mathcal{W}_{i,u^+}(\mathbf{e}_i^{(g)\top}\mathbf{e}_{u^+}^{(g+1)})/\tau)}{\sum_{\hat u\in\mathcal{U}}\exp(\mathcal{W}_{i,\hat u}(\mathbf{e}_i^{(g)\top}\mathbf{e}_{\hat u}^{(g+1)})/\tau)}$$

**Entire scope（Eq.14/15）**：分母改为在 $\mathcal{V}=\mathcal{I}\cup\mathcal{U}$ 上求和。

**合并**：$\mathcal{L}_{nl} = \mathcal{L}_{nl_u} + \mathcal{L}_{nl_i}$（§3.3.2 末，**等权相加，无平衡系数**）。

**最终损失（Eq.16）**：$\mathcal{L} = \mathcal{L}_{ori} + \lambda\,\mathcal{L}_{nl}$

> ⚠️ 三个易被忽略的细节：① 分子是**连乘** $\prod_{i^+\in\mathcal{N}_u}$（多正样本）；② 权重 $\mathcal{W}$ **同时**作用于分子与分母（正负样本都加权）；③ 归一化含 $\frac{1}{G|\mathcal{U}|}\cdot\frac{1}{|\mathcal{N}_u|}$。

---

## 维度 5：训练策略

**损失函数**
- 主损失：$\mathcal{L}_{ori}$，即各骨干模型自身的损失（FREEDOM/LGMRec/COHESION 等通常为 BPR + 正则）。
- 辅助自监督损失：ASW 加权 InfoNCE，权重 $\lambda$，温度 $\tau$。
- 正则项：论文未在 Eq.16 中显式列出 L2，由骨干模型自带（§5.1.4 提到对各基线做超参搜索）。

**正负样本构造**
- 正样本：锚点节点的**全部一阶邻居**在下一层的表征（多正样本，非单正样本）。
- 负样本：H scope = 全部异构节点（非邻居）；E scope = 全部节点（异构 + 同构）。
- 负样本数量：论文未给出显式采样比例；§4.2 说明"in-batch negative sampling is a widely used trick in GCL [4]"，复杂度分析以 batch 内节点数 $M$ 计。
- 数据增强：**无**（这是本文核心卖点）。

**优化与训练流程**
- 优化器：Adam [15]；初始化：Xavier [9]，均用默认参数（§5.1.4）。
- Batch size = 2048；Embedding size = 64（§5.1.4）。
- 早停：20 epoch，指标 NDCG@20（§5.1.4）。
- 两阶段：**否**（端到端多任务联合优化，§3.4）。但 $\mathcal{W}$ 需训练前离线预计算一次。
- 训练效率（Table 7，Baby 数据集）：
  | 骨干 | T/E | #E | Total | N@10 |
  |------|-----|----|----|------|
  | COHESION | 4.47s | 62 | 4m37s | 0.0354 |
  | COHESION-NLGCL | 7.07s | 51 | 6m1s | 0.0368 |
  | COHESION-NLGCL+ | 7.31s | **43** | 5m14s | **0.0379** |
  | COHESION-SimGCL | 8.36s | 76 | 10m35s | 0.0364 |
  - 结论：NLGCL+ 单 epoch 略慢于纯骨干，但**收敛 epoch 数最少**，总时长在所有 GCL 方法中最优。
- $\mathcal{W}$ 预计算开销：Fig. 3 显示各数据集上均可忽略，且每数据集只需构建一次、可被任意骨干复用。

**超参搜索空间**（§5.1.4）
| 超参 | 范围 | 论文推荐 |
|------|------|----------|
| $\lambda$ | $\{10^{-3},10^{-2},10^{-1}\}$ | **$10^{-2}$**（全模型全数据集一致，Fig.5a） |
| $\tau$ | $\{0.1,0.2,0.3,0.4\}$ | **0.2**（全模型全数据集一致，Fig.5b） |
| $L$ | $\{1,2,3,4\}$ | MMGCN/DualGNN → 3；FREEDOM/LGMRec/COHESION → 2（§5.7.2） |
| $G$ | $\{1,\dots,L\}$ | **2**（全数据集一致，Fig.6） |

---

## 维度 6：数据集选择

**数据集清单（Table 5）**

| 数据集 | 领域 | 模态 (维度) | 用户 | 物品 | 交互 | 稀疏度 |
|--------|------|-------------|------|------|------|--------|
| Baby | 电商 (Amazon) | V(4096), T(384) | 19,445 | 7,050 | 160,792 | 99.88% |
| Sports | 电商 (Amazon) | V(4096), T(384) | 35,598 | 18,357 | 296,337 | 99.95% |
| Clothing | 电商 (Amazon) | V(4096), T(384) | 39,387 | 23,033 | 278,677 | 99.97% |
| Pet | 电商 (Amazon) | V(4096), T(384) | 19,856 | 8,510 | 157,836 | 99.91% |
| TikTok | 短视频 | V(128), T(768), A(128) | 9,319 | 6,710 | 59,541 | 99.90% |

- 来源：Amazon 数据集 [17]；TikTok [14]。反馈类型：隐式。
- **特征提取**：视觉 4096-d 由预训练 CNN [11] 提取；文本 384-d 由 sentence-transformers [21] 提取；TikTok 文本 768-d 同法，其余模态直接采用已发布特征集（§5.1.1）。
- **预处理与切分**：完全遵循 MMRec [53] 的方法学；具体的过滤阈值 / 切分比例 —— **论文未提及**（仅间接提到 5-core 是推荐系统常见做法，§3.3）。
- 时间跨度：论文未提及。
- 冷启动划分：遵循 [40, 50] 的通用设定（§5.6），具体细节论文未展开。

---

## 维度 7：实验与 Benchmark

### 评测指标
- Recall@10、NDCG@10（主结果 Table 6、冷启动 Table 8）；早停用 NDCG@20。
- 效率指标：T/E（每 epoch 时间）、#E（收敛 epoch 数）、TT（总训练时长）（Table 7）。
- 复杂度/内存：Table 3（时间复杂度）、Table 4（内存占用）。

### 骨干模型（5 个，被增强的对象）
MMGCN [29]、DualGNN [26]、FREEDOM [54]、LGMRec [10]、COHESION [37]。

### 基线（7 个 GCL 方法，被对比的对象）
SGL [30]、NCL [16]、SimGCL [46]、LightGCL [2]、DCCF [22]、BIGCF [51]、NLGCL [43]（自家会议版）。

- 复现方式：全部基于 MMRec [53] 统一框架实现；已有实现的模型直接复用 [16,44] 的报告数值；其余按各自论文做网格搜索（§5.1.4）。
- 硬件：Intel i9-13900K + 64GB DDR5 + RTX 4090 (24GB)，Ubuntu 22.04 / CUDA 12.1 / PyTorch 2.1（§5.1.4）。

### 主结果（Table 6 摘录，Recall@10 / NDCG@10）

| 骨干 | 变体 | Baby | Sports | Clothing | Pet | TikTok |
|------|------|------|--------|----------|-----|--------|
| FREEDOM | 原始 | .0627/.0330 | .0717/.0385 | .0629/.0341 | .1086/.0595 | .0589/.0295 |
| FREEDOM | -NLGCL | .0653/.0343 | .0743/.0399 | .0651/.0355 | .1127/.0617 | .0633/.0315 |
| FREEDOM | **-NLGCL+(H)** | **.0665/.0352** | **.0757/.0408** | **.0664/.0366** | **.1138/.0625** | **.0658/.0320** |
| FREEDOM | -NLGCL+(E) | .0660/.0348 | .0753/.0405 | .0658/.0362 | .1129/.0619 | .0652/.0324 |
| FREEDOM | Improv. | 6.06%/6.67% | 5.58%/5.97% | 5.56%/7.33% | 4.79%/5.04% | 11.71%/8.47% |
| COHESION | 原始 | .0680/.0354 | .0752/.0409 | .0665/.0358 | .1132/.0619 | .0680/.0341 |
| COHESION | -NLGCL | .0704/.0368 | .0776/.0425 | .0690/.0372 | .1172/.0641 | .0710/.0359 |
| COHESION | **-NLGCL+(H)** | **.0722/.0379** | **.0799/.0438** | **.0713/.0384** | **.1199/.0656** | **.0740/.0376** |
| MMGCN | Improv. | 9.79%/8.50% | 13.24%/12.44% | 9.17%/10.91% | 15.02%/14.59% | **22.25%/19.48%** |

**五条核心观察（§5.2）**：
1. **Obs1**：H 与 E 两种 scope 在 5 骨干 × 5 数据集上均显著提升（p < 0.01）。
2. **Obs2**：TikTok 上提升最大（MMGCN 达 +22.25% R@10）—— 归因于 TikTok 有 3 个模态，模态权重分配更细粒度。
3. **Obs3**：**NLGCL+(H) 在所有模型与数据集上一致优于 NLGCL+(E)** —— 归因于用户与物品之间存在不可避免的语义鸿沟，H 的负采样范围更精确。
4. **Obs4**：NLGCL+ 优于全部 GCL 基线；相比自家 NLGCL 的增益来自 ASW。
5. **Obs5**：**LightGCL 在所有骨干上都掉点**（唯一一致负向的基线）—— 因其依赖近似 SVD 构造视图，在多模态融合表征上引入大量任务无关噪声。此外 MMGCN 上多数 GCL 方法退化，因其表征能力弱、自监督信号质量差。

### 消融实验（§5.3, Fig. 2）
- 唯一变体：**w/o-ASW**。
- Obs1：H 与 E 均显著优于各自的 w/o-ASW 版本 → ASW 必要。
- Obs2：在都去掉 ASW 后，H w/o-ASW 仍优于 E w/o-ASW → H scope 的优势独立于 ASW。
- **缺失的消融** `[阅读者判断]`：未拆解 ASW 内部（例如"仅正样本加权 vs 仅负样本加权"、"原始特征 vs 训练中表征"、"各模态相似度求和 vs 加权和"），也未做 $\mathcal{W}$ 稀疏化/截断的鲁棒性分析。

### 稀疏性与冷启动
- **稀疏性（§5.5, Fig.4）**：Baby 按交互数分组，NLGCL+ 在所有稀疏档位均提升，在 1–5 交互组最明显。
- **冷启动（§5.6, Table 8）**：全部 5 骨干 × 4 数据集上 H > E > 骨干。例：COHESION Baby R@10 从 0.0399 → 0.0433（+8.5%）；FREEDOM Sports R@10 从 0.0389 → 0.0430（+10.5%）。

### 在线实验
无（论文未提及 A/B 测试）。

---

## 维度 8：关联论文

**直接对标 / 改进对象**
- **[43] NLGCL**（自家会议版）—— 本文的直接前身，NLGCL+ = NLGCL + ASW + 多模态适配 + 理论证明。
- **[7] Chen et al., SIGIR 2025, "Squeeze and Excitation: A Weighted Graph Contrastive Learning for CF"** —— 提供"负样本不应等权"的论据（§3.3 引用）。

**骨干模型（被增强对象）**
[29] MMGCN、[26] DualGNN、[54] FREEDOM、[10] LGMRec、[37] COHESION。

**GCL 基线**
[30] SGL（边 dropout 增强）、[16] NCL（EM 聚类找语义邻居）、[46] SimGCL（加噪扰动）、[2] LightGCL（SVD 轻量视图）、[22] DCCF（解耦表征）、[51] BIGCF（意图个体性/集体性）。

**方法论依据**
- [19] InfoNCE —— 对比损失基础形式（Eq.7）。
- [4] SimCLR —— in-batch 负采样 trick（§4.2）。
- [8] Cover, Elements of Information Theory —— entropy-power inequality，用于 Lemma 1 证明。
- [53] MMRec —— 统一多模态推荐框架，全部实验实现基础。
- [40] —— 支撑"原始特征稳定、同一特征空间"的论据，以及用户特征均值池化做法。

**同期工作**
[5] ICASSP 2025（减小节点-邻居差异）、[6] CIKM 2025 HPMRec（超复数）、[14] DiffMM、[18] SMORE、[42] MENTOR —— 均为同期多模态推荐工作，作为 Related Work 提及。

---

## 维度 9：质量准则自检

**准确性**：本文档所有数字均抄录自 Table 1–8 与 §5.1.4 / §5.7；无推算合并。
**完整性**：维度 0–8 全覆盖；论文未提供的数据切分比例、随机种子已标注「论文未提及」。
**可复现导向**：
- 关键公式可定位：Eq.8/9（消息传递）、Eq.10（用户原始特征）、Eq.11（相似度矩阵）、Eq.12–15（ASW-InfoNCE）、Eq.16（总损失）。
- 超参表完整（$\lambda,\tau,L,G$，batch=2048，dim=64，Adam+Xavier）。
- **复现障碍**：① 数据集切分比例未给出（需回溯 MMRec 默认）；② 随机种子未给出；③ 冷启动划分细节需回溯 [40,50]；④ **开源代码未实现 ASW**（见交叉分析报告，这是最严重的复现障碍）。

**批判性**
- 论文自承局限：Eq.10 均值池化对低交互用户噪声大（§3.3）。
- `[阅读者判断]` 额外风险：
  1. **$\mathcal{W}$ 的显存问题**：H scope 下 $|\mathcal{U}|\times|\mathcal{I}|$，Clothing 上是 39,387 × 23,033 ≈ 9.07 亿个 float32 ≈ 3.6 GB。论文只讨论了预计算的**时间**开销（Fig.3），完全回避了**存储/显存**开销，而 Table 4 的内存分析里也没有 $\mathcal{W}$ 这一项。这是分析上的明显缺口。
  2. **Eq.11 的量纲问题**：多模态余弦相似度直接求和，取值范围 $[-|\mathcal{M}|, |\mathcal{M}|]$，可能为**负数**。$\exp(\mathcal{W}\cdot s/\tau)$ 在 $\mathcal{W}<0$ 时会把相似度符号翻转，语义上等价于"把这个正样本推远"。论文未讨论是否做了裁剪/归一化到 $[0,1]$。
  3. **Eq.12 分子连乘 + 分母单项**：分子是 $|\mathcal{N}_u|$ 项连乘、分母只有一项求和，二者不同量纲，$\log$ 后并非标准 InfoNCE 下界。虽有 $1/|\mathcal{N}_u|$ 归一化，但仍是一个"多正样本 InfoNCE"的非标准变体，论文未给出理论辩护。
  4. **基线充分性**：对比的 GCL 基线较充分（7 个），但缺少同为"免增强"路线的方法（如 SimGCL 之外的 XSimGCL、LightGCN-based 的 NCL 变体），也未与"负样本加权"专线方法（如 [7] 自家 SIGIR'25 工作）直接对比。

---

## 维度 10：复现性自检清单

- [x] 代码是否开源 —— https://github.com/Jinfeng-Xu/NLGCL-Plus（**但缺 ASW 实现**）
- [x] 数据是否公开 —— Amazon [17] / TikTok [14]，MMRec [53] 标准处理
- [x] 超参表是否完整 —— $\lambda,\tau,L,G$、lr、batch、dim 均给出（§5.1.4）
- [ ] 随机种子是否给出 —— **论文未提及**
- [x] 硬件环境是否说明 —— i9-13900K / RTX 4090 24GB / CUDA 12.1 / PyTorch 2.1
- [x] 关键模块公式是否可定位 —— Eq.8–16
- [ ] 切分方式是否可复现 —— 仅说"follows MMRec [53]"，比例未给
- [ ] 负采样细节是否充分 —— 只说 in-batch，未给采样数与实现细节

---

## 附：可复用结论速查

| 结论 | 数值/设置 | 出处 |
|------|-----------|------|
| 最优 $\lambda$ | $10^{-2}$（跨全部模型与数据集） | Fig.5a |
| 最优 $\tau$ | 0.2 | Fig.5b |
| 最优 $G$ | 2 | Fig.6 |
| 最优 $L$ | 强骨干 2，弱骨干 3 | §5.7.2 |
| H vs E | **H 永远更好**（效果 + 效率双赢） | Table 6, Table 3 |
| 提升幅度区间 | 弱骨干 (MMGCN) 9–22%；强骨干 (COHESION/FREEDOM) 5–12% | Table 6 |
| 模态数效应 | 模态越多提升越大（TikTok 3 模态最高） | §5.2 Obs2 |
| 收敛加速 | 收敛 epoch 数比纯骨干少 20–30% | Table 7 |
| ASW 贡献 | 消融显示为正贡献（w/o-ASW 全面下降） | Fig.2 |
