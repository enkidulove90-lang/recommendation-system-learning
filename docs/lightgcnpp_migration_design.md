# MixRAGRec → LightGCN++ 四模块迁移设计方案

> **生成时间**: 2026-08-04  
> **基座**: `baseline/LightGCNpp/`（RecSys 2024，$\alpha/\beta/\gamma$ 三参数改进）  
> **迁移源思想**: `baseline/MixRAGRec/`（KDD 2026，多粒度 KG 检索 + MMAPO）  
> **配套文档**: `baseline/LightGCNpp_analysis.md`（源码分析）、`baseline/MixRAGRec_analysis.md`

---

## 0. 总览与依赖关系

四个 idea 并非平行，存在明确的依赖与耦合：

```
        idea1 多粒度自适应传播 ──────┐
        (每节点用几阶/多大子图)      │  共享"逐层嵌入 [N,L+1,d]"
                  │                  │
                  │ 产生"深度选择"    ├──► idea4 NLGCL 层间对比
                  ▼                  │   (层 l 与 l+1 天然对比视图)
        idea3 成本感知约束 ◄─────────┘
        (给深度选择加价格标签)
                  ▲
                  │ 成本项同样可约束"要不要引入外部知识"
                  │
        idea2 知识对齐 ──────────────┘
        (外部知识/图像 → 先对齐再融合)
```

**落地优先级建议**：`idea4 → idea1 → idea3 → idea2`。

- idea4 是纯 loss 插件（约 30 行），可立即验证收益，且能作为后续所有实验的增强基线；
- idea1 是核心创新点，但**必须先做前提验证实验**（见 1.2），否则可能做无用功；
- idea3 依附于 idea1 的深度选择才有意义；
- idea2 受限于数据可得性（当前 `baseline/LightGCNpp/data/` 五个数据集**均无图像/属性特征**），需先解决数据源。

---

## 1. idea1：多粒度结构信息利用 —— 自适应传播阶数与子图范围

### 1.1 从 MixRAGRec 迁移的是什么

MixRAGRec 的 4 个检索专家构成粒度阶梯：无检索 → 三元组 → 2-hop 子图 → 连通子图，由 Expert Selector（PPO）按查询难度动态选择。

映射到 LightGCN++：

| MixRAGRec         | LightGCN++ 对应物           | 说明             |
| ----------------- | ------------------------ | -------------- |
| Expert 1 无检索      | $e^{(0)}$ ego embedding  | 不传播，纯 ID 嵌入    |
| Expert 2 三元组      | $e^{(1)}$ 一阶邻居           | 1-hop          |
| Expert 3 2-hop 子图 | $e^{(2)}$                | 2-hop          |
| Expert 4 连通子图     | $e^{(3)},e^{(4)}$ / 扩展邻域 | 高阶             |
| Expert Selector   | 逐节点层权重 $w_u^{(l)}$       | **本 idea 的核心** |

**关键观察**：LightGCN++ 的 $\gamma$ 本身就是一个"全局的、只有两档的粒度选择器"——  
$e^{final} = \underbrace{\gamma}_{\text{层0权重}} e^{(0)} + (1-\gamma)\cdot\overline{e^{(1..L)}}$  
本 idea 等价于把这个**全局标量 $\gamma$ 泛化为逐节点的层分布 $w_u^{(l)}$**：  
$e_u^{final} = \sum_{l=0}^{L} w_u^{(l)} e_u^{(l)},\qquad \sum_l w_u^{(l)}=1,\ w_u^{(l)}\ge 0$

这个表述的好处：**LightGCN++ 原模型是它的严格特例**（$w^{(0)}=\gamma$，其余均为 $(1-\gamma)/L$），消融对比天然公平。

### 1.2 ⚠️ 先做前提验证：Oracle 层选择实验（最重要的一步）

在写任何自适应模块之前，**必须先回答："不同节点是否真的需要不同阶数？上限有多高？"** 如果 oracle 上限只比固定 $L$ 高 1~2%，这条路就不值得走。

好消息：`baseline/LightGCNpp/` **已经有全部所需基础设施**，不用改模型就能做：

- `model.py::computer()` 第 4 个返回值 `_users/_items` 就是 `[N, L+1, d]` 逐层嵌入；
- `main.py --save_layer_emb 1` 会把它 pickle 到 `embs/*.pkl`；
- `Procedure.py::Test_Offline(dataset, all_users, all_items)` 接收**预计算嵌入**跑完整 Top-K 评估。

**⚠️ 拦路石**：`main.py` L43 有 `if world.args.layer == 4: exit(0)` 的硬编码短路（作者调参残留，静默退出不报错）。做 $L=4$ 实验前必须先删掉。同理 L40 的 `decay` 短路。

**实验步骤**：

```bash
# Step 0: 先删除 main.py L40-44 的两处 exit(0) 短路
# Step 1: 训一个 L=4 的模型并保存逐层嵌入
cd baseline/LightGCNpp/code
python main.py --dataset=gowalla --alpha 0.6 --beta -0.1 --gamma 0.2 \
               --layer 4 --save_layer_emb 1
```

**P0 删短路+复现基线 → P1 接 NLGCL → P2 Oracle 实验（决策点）**

> 实现提示：`Test_Offline` 目前把逐 batch 结果直接累加求均值（L300-307）。做一个 `Test_PerUser` 变体，保留 `utils.RecallPrecision_ATk` 的逐用户中间值即可，改动很小。

**三张必须产出的结果表**：

**表 A — Oracle 上限（决定这条路走不走）**

| 方案                   | Recall@20 | NDCG@20 | 相对最优固定 $L$ |
| -------------------- | --------- | ------- | ---------- |
| 固定 $L$=1 / 2 / 3 / 4 | ...       | ...     | —          |
| **Oracle 逐用户选 $g$**  | ...       | ...     | **+X%**    |

判定标准（经验值）：**Oracle 增益 < 3% → 放弃自适应，转做 idea3/idea4；3%~8% → 值得做轻量规则版；> 8% → 值得做可学习版。**

**表 B — 最优粒度 $g^*_u$ 与用户度数的关系（决定"难度"怎么定义）**

按度数分桶（建议 5 桶：`[1,5] [6,10] [11,20] [21,50] >50`，用 `dataset.users_D` 直接取），统计每桶内 $g^*_u$ 的分布：

| 度数桶      | 用户占比 | $g^*$=0 | $g^*$=1 | $g^*$=2 | $g^*$=3 | $g^*$=4 | 众数        |
| -------- | ---- | ------- | ------- | ------- | ------- | ------- | --------- |
| [1,5] 冷启 |      |         |         |         |         |         | 预期偏**高**阶 |
| [6,10]   |      |         |         |         |         |         |           |
| ...      |      |         |         |         |         |         |           |
| >50 活跃   |      |         |         |         |         |         | 预期偏**低**阶 |

**这张表是整个 idea 的成败关键**：若各桶众数一致，说明度数不是好的难度信号，需换指标；若单调变化，则规则版就能吃掉大部分收益。

**表 C — 固定 $L$ 的分桶性能矩阵（交叉验证表 B）**

行为度数桶、列为 $L\in\{1,2,3,4\}$ 的 Recall@20 热力图。若每行的 argmax 列不同 → 前提成立。

### 1.3 "难度"信号的候选与选择

不要一开始就上复杂特征，按这个顺序试：

| 层级 | 信号                                      | 计算方式                                | 成本         |
| -- | --------------------------------------- | ----------------------------------- | ---------- |
| L0 | **度数** $d_u$                            | `dataset.users_D`，现成                | 0          |
| L1 | 二阶邻域膨胀率 $\|N^2(u)\|/\|N^1(u)\|$         | `UserItemNet @ UserItemNet.T` 行 nnz | 低（预计算一次）   |
| L2 | 邻居度数熵 $H(\{d_i\}_{i\in N_u})$           | 反映邻居是否都是热门物品                        | 低          |
| L3 | **层间嵌入变化量** $\|e_u^{(l+1)}-e_u^{(l)}\|$ | 训练中在线可得，是过平滑的直接度量                   | 中（但已有逐层嵌入） |

L3 尤其值得试：它直接刻画"再传播一层还有没有新信息"，**与 idea3 的边际增益是同一个量**，两个 idea 在此汇合。

### 1.4 三档实现方案（按代价递增）

**方案 A（推荐起步）— 规则式分桶 $\gamma$**，新增 2 个参数：

```python
# model.py __init_weight() 中预计算，无训练开销
deg = torch.tensor(self.dataset.users_D)                      # [n_users]
gamma_u = torch.sigmoid(self.a * torch.log(deg + 1) + self.b) # a,b 为可学习标量
# computer() 中：
light_out = gamma_node[:,None] * embs_zero + (1 - gamma_node[:,None]) * embs_prop
```

其中 `gamma_node` 是 user/item 拼接后的 `[N,1]`。**这一步几乎零额外算力，是性价比最高的验证。**

**方案 B — 可学习逐节点层注意力**，新增 $O(d\cdot L)$ 参数：

```python
# 输入：ego embedding + 度数特征
feat = torch.cat([embs[0], torch.log(deg_all + 1).unsqueeze(1)], dim=1)  # [N, d+1]
w = torch.softmax(self.layer_attn(feat), dim=-1)          # [N, L+1]
light_out = (torch.stack(embs, 1) * w.unsqueeze(-1)).sum(1)
```

`self.layer_attn = nn.Linear(d+1, L+1)`。注意 **`embs[0]` 是未归一化的 ego embedding**（见源码分析 §1 注），做注意力输入前建议先 L2 归一化，否则范数尺度会主导 attention。

**方案 C — RL 选择器（对标 MixRAGRec Expert Selector）**：  
只有当 (i) 表 A oracle 增益 > 8%，且 (ii) 方案 B 与 oracle 差距仍 > 4% 时才考虑。GCN 场景下节点数达百万级，PPO 的采样效率会成为瓶颈，且离散选择不可微、需 Gumbel-Softmax 松弛，**投入产出比通常不如方案 B**。

### 1.5 子图传播范围（阶数之外的第二个粒度轴）

阶数控制"传播多深"，子图范围控制"每层传播多宽"：

- **高度数节点做邻居剪枝**：保留 top-$k$ 重要邻居（重要性可用 $\tilde{A}$ 的边权，即 $d_u^{-\alpha}d_i^{-\beta}$），$k = \min(d_u, k_{max})$。既降成本又抑制热门物品的噪声聚合。
- **低度数节点做邻域扩展**：对 $d_u \le 5$ 的冷启用户，引入 2-hop 用户-用户共现边（$RR^T$ 的 top-$k$），缓解信息不足。

**⚠️ 工程陷阱**：`dataloader.py` L364/L394 按 `s_pre_adj_mat_{alpha}_{beta}.npz` 缓存归一化邻接矩阵。改造图结构后**必须把新结构标识写进文件名**（如 `s_pre_adj_mat_{alpha}_{beta}_prune{k}_exp{m}.npz`），否则会静默加载旧图，实验结果全错且极难排查。

**评估方式**：子图改造的收益必须放在 **iso-cost（等算力）** 下比较——用 idea3 的 $\text{nnz}(\tilde{A})\cdot d\cdot L$ 作为横轴，画 Recall-成本 Pareto 曲线，而不是只报绝对指标。

---

## 2. idea2：知识对齐（结构化 → 统一表示）的中间步骤

### 2.1 迁移的核心原则

MixRAGRec 的 Knowledge Alignment Agent 做的事本质是：**不把原始异构结构直接喂给下游，而是先经过一个显式的对齐步骤投射到下游能消化的空间，并附带置信度**。

对 LightGCN++ 的直接含义：**不要把原始视觉/属性特征直接拼进传播**。原因很具体——LightGCN++ 每层做逐节点 L2 归一化（源码 `model.py` L162-163），整个传播过程对嵌入的**尺度和分布高度敏感**。把一个 512 维 CLIP 特征直接 concat 或相加进 $e^{(0)}$，会立刻破坏这个尺度假设，且把模态噪声沿图放大 $L$ 层。

### 2.2 ⚠️ 先解决数据前提

**当前 `baseline/LightGCNpp/data/` 的 5 个数据集（lastfm / ml-1m / gowalla / yelp2018 / amazon-book）都只有交互三元组，没有任何图像或属性特征。** 这个 idea 无法在现有数据上直接开工，必须先二选一：

- **路线 1（推荐）**：换用项目里已有的多模态数据 —— `redbook/`（含 64 张 jpg + 结构化字段）或 `data/` 下的 2540 张 jpg。优点是贴合"不同类型不同视角图片"的真实场景；缺点是需要自建 train/valid/test 划分并对齐成 LightGCN 格式。
- **路线 2**：用公开多模态基线数据（Amazon-Beauty/Sports 的 CNN/CLIP 特征，MMSSL、SMORE 等仓库有现成 `image_feat.npy`），项目 `baseline/` 里已有 MMSSL、SMORE、FITMM 等多模态模型可复用其数据管线。

### 2.3 针对"不同类型 / 不同视角图片"的三级对齐

这是用户特别关注的点。MixRAGRec 的 4 级检索粒度可以直接映射成 **4 级视觉对齐粒度**：

| 粒度      | MixRAGRec 对应 | 视觉侧含义                 | 处理算法                     |
| ------- | ------------ | --------------------- | ------------------------ |
| G1 视角级  | 三元组          | 单张图（主图/细节图/场景图/UGC 图） | 视角编码器 $f_v$ + **视角类型嵌入** |
| G2 图像集级 | 2-hop 子图     | 同一物品的多张图              | **视角内一致性对比 + 注意力池化**     |
| G3 物品级  | 连通子图         | 物品的统一视觉表示             | 与 ID 嵌入做**跨模态对齐**        |
| G4 类目级  | —            | 同类目物品的视觉先验            | 类目原型，供冷启物品回退             |

**(a) 不同"类型"图片 —— 类型感知门控，不要简单平均**

不同类型图片的信息密度差异极大（主图 > 细节图 > UGC 图）。给每种类型 $t$ 一个可学习类型嵌入 $\mathbf{t}_t$，池化时做类型感知注意力：

lightgcnpp_migration_design.md思路
