# SAB-ANC 参数决议与默认值 · Decision Record v1.2

> 配套：`docs/sab_anc_design.md`（设计基线）
> 状态：**本文件为参数唯一权威来源**。代码/设计中任何数值与本文件冲突，以本文件为准，并须在同一提交内改掉冲突处。
> v1.2（2026-11-10）：三项偏离裁决封闭 —— ①第三模态定为 **behavioral(SASRec)**（非类别品牌）；②动作头 **关闭**，rating/verified 不可得 → 改 4 维可计算行为辅助输入；③BLIP-2 → 预计算特征（路径 A）正式拍板，新增 **偏差登记册**（§2.6）与 **闸门-0 跨模态可对齐性预检**（§2.7）。
> v1.1（2026-11-10）：按论文原文定值 Eq.1、弃用 `CGAd`、修正 PSGR 输入、数据集基准切到 MMSSL Baby + 5k item 子集。
> v1.0（2026-11-10）：首版（基于 Amazon-2023 假设，部分内容已被 v1.1 取代）

---

## 0. 三态约定 + 基准变更

| 标记 | 含义 | 改动权限 |
|---|---|---|
| **【锚】** | 论文锚定值（已由论文原文确认） | 禁止改动，只允许在报告中记录偏差 |
| **【定】** | 已定，实现按此写死 | 需走变更记录（§9） |
| **【拍】** | 本次拍板，给默认值 + 网格 + 推翻判据 | 有数据支撑即可在网格内调整 |

**基准变更（v1.0 → v1.1）**：数据集从 "Amazon-2023 Movies&TV/Books + 全局时间切分" 改为 **MMSSL Amazon-Baby + 5k item 子集**（v3 裁决-3）。Amazon-2023 内容全部移到附录 A 作备选路径保留，不再是主线。

---

## 1. 参数总表

### 1.1 上游 DST / CGA（几何对齐）

> ⚠️ **`CGAd` 弃用**。论文中不存在该符号，CGA 章节只有 `d`（公共维度）、`z_{i,j}`（对齐特征）、`G_i`（Gram 矩阵）、`Vol_i`（体积）。本文件与代码统一用 **`d = 256`**。

| 参数 | 值 | 状态 | 说明 |
|---|---|---|---|
| `d`（CGA 公共维度） | 256 | 【锚】 | 原 `CGAd=256` 的所指 |
| 流形约束 | 单位超球面（L2 归一化） | 【锚】 | `x / ‖x‖₂`，ε=1e-8 |
| 体积定义 | `Vol_i = √det(G_i)`，`G_i[j,k] = z_{i,j}ᵀ z_{i,k}` | 【锚】 | §2.1 |
| 对齐损失 | **对称对比 `L_align = (L_D2A + L_A2D)/2`** | 【锚】 | §2.2，Eq.1 |
| `τ`（体积对比温度） | **0.07** 主，0.1 敏感性 | 【拍】 | §2.3 |
| `N_m`（模态数） | **3 = visual + textual + behavioral** | 【定】 | v1.2 裁决，见 §2.5；与论文结构一一对应 |
| 码本组数 | **6 组 = 3 共享（`RQN_sh`）+ 3 模态特定** | 【定】 | 由 `N_m=3` 推出，与论文一致 |
| anchor 轮换 | **3 模态逐一轮换，3 组 D2A/A2D 取平均** | 【拍】 | §2.4 |
| `Φ_fuse` | **mean 为主**，attention 为消融 | 【拍】 | §3.1 |
| 码本更新 | STE + commitment `sg[·]` | 【锚】 | 前向最近码字，反向直通 |
| `β`（commitment） | 1.0，网格 {0.1, 1, 10} | 【拍】 | §3.3 + guard |
| `λ`（对齐权重） | 1.0，网格 {0.1, 1, 10} | 【拍】 | §3.3 + guard |

### 1.2 RQN

| 参数 | 值 | 状态 |
|---|---|---|
| `RQN_sh`（共享量化层数） | 3 | 【锚】 |
| `K`（码本大小） | 512 | 【锚】 |
| 投影维度 | 512 × 256（输入 512 → 码字 256） | 【锚】 |

### 1.3 PSGR（**输入已按论文修正**）

| 参数 | 值 | 状态 | 说明 |
|---|---|---|---|
| 主输入 | **共享量化残差 `r_{N_sh}`**（`r = f − ẑ_sh` 一路下来的残差） | 【锚】 | 不是"用户表征/物品表征拼接" |
| query 来源 | **item 的第 j 模态对齐特征 `z_j` 作 semantic probe** | 【锚】 | `z_sp^(j) = Attn(z_j, K̃, Ṽ)` |
| `q_proj` 输入维度 | **`d = 256`**（z_j 已是 CGA 输出维度） | 【锚】 | 物品侧特征，与用户表征无关 |
| `H`（头数） | 4 主 / 8 消融 | 【定】 | |
| `q_proj` 结构 | 2 层 MLP（256→256→256，GELU + LayerNorm） | 【拍】 | §3.2 |
| `q_proj` 共享 | 全头共享一套；k/v 按头独立 | 【拍】 | §3.2 |
| 每头维度 | `d/H`：H=4 → 64，H=8 → 32 | 【定】 | |

> ⚠️ **归属澄清**：DST/PSGR 阶段处理的是 **item 的多模态特征**，输出 item 语义 token；**用户侧序列建模在 HMAT 阶段**。任何把 PSGR query 写成"用户表征"的描述都是偏离论文的，必须改。

### 1.4 vCLUB

| 参数 | 值 | 状态 |
|---|---|---|
| `q_θ` 分布 | 高斯 `N(μ,σ²)`，重参数化 | 【锚】 |
| `q_θ` 结构 | 2 层 MLP，hidden 256，ELU，输出 `2d` | 【拍】 |
| `log σ²` 裁剪 | [-6, 6] | 【拍】 |
| `λ_vcl` | 0.05，网格 {0.01, 0.05, 0.1} | 【拍】 |
| 评估期 | 用 `μ`，不采样 | 【定】 |

---

## 2. Eq.1 实现规格（论文原文定值）

### 2.1 体积

```
G_i ∈ R^{N_m × N_m},  (G_i)_{j,k} = z_{i,j}ᵀ z_{i,k}
Vol_i = sqrt(det(G_i))
```

`z_{i,j}` 是第 i 个样本第 j 模态的对齐特征，已 L2 归一化（单位超球面约束）→ `G_i` 对角为 1，`det ∈ [0,1]`。

### 2.2 对称对比损失（Eq.1 原式）

```
L_D2A = −(1/B) Σ_i log [ exp(−Vol(a_i, r_i)/τ) / Σ_k exp(−Vol(a_k, r_i)/τ) ]
L_A2D = −(1/B) Σ_i log [ exp(−Vol(a_i, r_i)/τ) / Σ_k exp(−Vol(a_i, r_k)/τ) ]
L_align = (L_D2A + L_A2D) / 2
```

- **不是 det 的对数，也不是归一化体积比**：`Vol` 直接作为指数里的距离，外面套 softmax。
- 负号含义：匹配对体积小 → `e^{−Vol/τ}` 大 → 分母占比高 → loss 低。等价于"最小化匹配对体积、最大化不匹配对体积"。
- 两方向差异：`L_D2A` 固定 data 遍历 anchor（分母 k 遍历 `a_k`）；`L_A2D` 固定 anchor 遍历 data（分母 k 遍历 `r_k`）。
- 与 CGA 章节的"体积最小化"是**同一个 Vol**，不矛盾：CGA 描述几何目标，Eq.1 是它的对比式训练实现。

### 2.3 τ 的定值【拍】

| 项 | 值 | 理由 |
|---|---|---|
| 主值 | **τ = 0.07** | 与业界 InfoNCE 默认一致（SimCLR/CLIP 0.07），且 `Vol ∈ [0,1]` 量级与余弦距离相近，不需要重标度 |
| 敏感性 | τ ∈ {0.05, 0.07, 0.1, 0.2}，5k 子集上跑 1 seed | τ太小 → 只学最难的负例、梯度噪声大；太大 → 对比失效（等价均匀 softmax） |
| 判据 | 主值取 valid NDCG@10 最优且 3 seed 稳定者 | 若 τ=0.07 与最优差 > 1 个 seed std，改用最优值并更新本表 |

**数值实现要点**（必须按此写，否则 det 会爆/塌）：

```python
# 稳定版：logdet 代替 det
def volume(z):                      # z: [B, N_m, d]
    G = z @ z.transpose(1, 2)       # [B,N_m,N_m]
    G = G + 1e-6 * torch.eye(N_m, device=z.device)   # jitter 防奇异
    _, logdet = torch.linalg.slogdet(G)
    return torch.exp(0.5 * logdet)  # = sqrt(det)
```

- `Vol` 上界为 1（对角全 1 时取等），下界 0；`det < 0` 因数值误差出现时由 jitter 兜住，若仍出现则判实现错误而非调参。
- B×B 的 `Vol` 矩阵一次算完（`[B,B]`），两个方向只是 softmax 的 dim 不同（dim=0 / dim=1），**不要写两个循环**。

### 2.4 N_m=3 的 anchor 轮换【拍】

论文只写"指定一个模态为 anchor、其余为 data"，未说明 3 模态是否轮换。

**拍板：一次前向内轮换 3 次，3 组 (L_D2A + L_A2D)/2 取算术平均。**

```
for j in range(3):
    anchor = z[:, j]                  # 第 j 模态
    data   = z[:, other_two].mean(1)  # 其余两模态的融合（Φ_fuse=mean 时天然可用）
    L += (L_D2A(anchor, data) + L_A2D(anchor, data)) / 2
L_align = L / 3
```

理由：不轮换等于随机指定 anchor，结果依赖模态顺序（不可复现的隐性变量）；轮换后损失对模态排列对称，与"几何对齐"语义一致，且代价只有 3 倍（B×B 矩阵，B=1024 时每步多 ~2ms）。

**v1.2 更新**：第三模态已定为 **behavioral(SASRec)**（§2.5），`N_m=3` 成立，本节 3 组轮换可完整执行，**不再有 2 模态降级路径**。

### 2.5 第三模态 = behavioral(SASRec)【v1.2 裁决】

论文的 `N_m=3` 是 **visual / textual / behavioral**，不是三类内容特征。因此第三模态必须用行为侧表征，类别/品牌不能顶替。

| 模态 | 本地实现 | 输入维 | 状态 |
|---|---|---|---|
| visual | MMSSL `image_feat.npy` | **4096（CNN）** | 【定】⚠️ 非 BLIP-2、非 CLIP，见 §2.6 D2 |
| textual | MMSSL `text_feat.npy` | **1024**（sentence-transformers 系，型号未留档；以实际 `load` 打印 shape 为准） | 【定】⚠️ 见 §2.6 D3 |
| behavioral | **冻结 SASRec 的 item embedding 表**（`train.txt` 序列训练，L2 归一化后进 CGA） | **512**（对齐论文 `d=512`） | 【定】 |

**结构后果（全部自动成立，无需额外决策）**：
- Eq.1 → 3 组 anchor 轮换（§2.4）；
- 码本 → `RQN_sh=3` 共享 + 3 组模态特定 = **6 组**，与论文一致；
- 5k 子集不改变 `N_m`，码本组数仍 6。

**边界（防混淆）**：`[CAT_i]/[BRD_i]` 是**下游内容输入**，属 SAB-ANC 自有设计，**不是模态**。若用它们顶替 behavioral，则名义 `N_m=3` 但结构与论文不对应 → **禁止**，且 `CAT/BRD` 本地同样无 meta 文件（Baby 无 meta），实际也造不出来。

#### ⚠️ behavioral 模态的两个固有风险（必须写进报告）

**风险 1：同源捷径（与标签同源）**。SASRec item embedding 与下游标签都来自 `train.txt` 的 next-item 目标 → behavioral 是最强捷径，`behavior-only` 可能已接近全模型。这不是 bug，**论文自己的消融就是这个结论**（behavior-only 是强基线，甚至超过 Text+Image）。

因此：
- **禁止**把"三模态 > 全模态对比"当作主结论的唯一形式（会被质疑提升来自行为侧）；
- **主结论必须落在 cold-start 子集**（行为不可靠处），与论文 "Image+Behavior 的 Cold AUC +3.50%" 叙事对齐；
- 强制报告 **7 行消融矩阵**：`V / T / B / V+T / V+B / T+B / V+T+B`，且 **warm 与 cold 分开列**。

**cold / warm 定义（可复现，写死）**：

| 桶 | 定义 | 依据 |
|---|---|---|
| cold-item | `train.txt` 中该 item 交互频次 **≤ 5** | 实测频次分布 p25=4 / median=6，`≤5` 约占 30–40%，规模够 |
| warm-item | 频次 **> 5** | 同上 |
| cold-user | 该用户 `train.txt` 序列长 **≤ 3** | 实测 min=3 |
| 主指标 | **cold-item 上的 AUC / NDCG@10** | 与论文 Cold 口径对应 |
| 辅指标 | warm-item 同指标；cold-user 单列 | |

**风险 2：behavior-only 消融 ≈ SASRec 本身**。这是好事——可当 sanity check：若 `B` 行显著低于已知 SASRec 水平，说明特征抽取链路有 bug，先查实现不查方法。

### 2.6 偏差登记册（Deviation Register）【v1.2 新增】

论文设定 vs 本地实况的逐项偏离登记。**报告/论文中每一行都必须对应一句显式声明**，不得沉默处理。

| ID | 论文设定 | 本地实况 | 级别 | 处理 | 报告必须写 |
|---|---|---|---|---|---|
| **D1** | 视觉与文本**同出一个 BLIP-2**（visual 2560 / textual 1408） | 视觉 CNN 4096 + 文本 SBERT 1024，**两个异质模型** | **高** | 闸门-0 预检（§2.7）；结论不得声称"复现论文编码器条件" | "视觉/文本**非同源**编码器，跨模态可对齐性前提弱于论文" |
| **D2** | BLIP-2 (2.7B) 视觉编码 | MMSSL 预计算 **CNN**（多篇论文口径一致：4096-d CNN） | 中 | 路径 A（§4.4） | "视觉特征为 CNN，非 BLIP-2" |
| **D3** | BLIP-2 文本编码 | sentence-transformers 系，**编码器型号未留档** | 中 | 同上 | "文本编码器型号未随数据发布，无法追溯" |
| **D4** | 维 2560 / 1408 | 4096 / 1024 | 低 | CGA 的 `W_j` 按输入维自适应 | 附表列维度即可 |
| **D5** | 动作模态 `a_t` 入 token 流 + 动作 NLL（SFT） | **无 rating、无 verified、无 timestamp、无评论文本** | **高（结构）** | 动作头关闭（§4.5），改 4 维行为辅助输入 | "数据集无动作监督信号，动作预测分支未实现" |
| **D6** | 多数据集（Baby/Sports/Clothing 等） | **仅 Baby，且 5k item 子集** | 中 | 原型定位，最终数字回全集 | "单数据集原型验证；子集 sha256 见附表" |
| **D7** | 全局时间切分 | per-user 前缀/后段 holdout | 低-中 | §4.2 | "per-user chronological holdout，**非**全局时间切分" |
| **D8** | behavioral 由论文 SASRec 出 | 本地重训 SASRec（同架构、权重不同） | 低 | §3 约定 | "behavioral 特征来自本地重训 SASRec" |
| **D9** | baseline = WuKong/HSTU/MTGR/QARM/PSRQ+MCCA/DLRM | 本地 LightGCN++ 同切分重跑 | 中 | §7 | "表中本地复现行为 LightGCN++；其余为原文引用" |
| **D10** | 内容侧含类别/品牌等语义先验 | Baby **无 meta 文件**，类别/品牌字段不存在 | 中 | `[CAT]/[BRD]` token 删除（design §5.1） | "内容侧仅 image+text 两路，无类别/品牌先验" |
| **D11**（条件项，未触发不生效） | behavioral `d=512` | 仅当 P1 计时外推 >24h/seed 时触发：`hidden=256` + 进 CGA 前线性升维 256→512 | 低 | L3 降级路径（§6），触发才登记 | "behavioral 编码器容量减半，接口维经投影补偿" |

**级别判据**：高 = 可能改变洞见有效性（必须在正文声明，不能只放附录）；中 = 影响数字可比性（表注声明）；低 = 仅实现差异（附表）。

**合计 10 项偏离（D11 为条件项），其中高级 2 项（D1 非同源编码器、D5 无动作信号）**。D1 由闸门-0（§2.7）兜底，D5 由"动作头关闭 + 4 维辅助特征"兜底且在正文声明。这两项决定了本方案的性质：**是"结构复现 + 条件偏离下的原型验证"，不是论文方法的严格复刻**。任何对外表述都必须守住这条边界。

### 2.7 闸门-0：跨模态可对齐性预检【v1.2 新增，P2 前强制】

**为什么必须做**：D1 的实质含义是——论文的"可对齐性"由 BLIP-2 单模型保证，本地换成两个异质编码器后，这个前提**退化为待验证假设**。若 `image_feat` 与 `text_feat` 之间本就没有可学的对应关系，Eq.1 的 `Vol` 无法有意义地下降，CGA 整个环节的结论都不可信。

**做法**（`code/gate0_alignability.py`，5k 子集、冻结特征、5-fold）：

| 指标 | 计算 |
|---|---|
| M1 跨模态检索 | 在 train-item 上 5-fold 学线性映射 `W: R^{d1}→R^{d2}`（岭回归，`α` 由内层 valid 选），held-out 上算 `image→text` **R@10** |
| M2 随机基线 | `R@10_random = 10 / N_item_subset`（5k → 0.2%） |
| M3 打乱对照 | 打乱配对标签重跑 M1（10 次），应 ≈ M2 ± 2σ（不≈则说明有标签泄漏或数据重复） |

**三对全测**：`V–T`、`V–B`、`T–B`（B = behavioral item embedding）。

| 对 | 通过 | 告警 | 失败 |
|---|---|---|---|
| **V–T** | R@10 ≥ **10× M2** | 3–10× → 可跑但结论须弱化为"弱可对齐条件下" | < 3× |
| **V–B / T–B** | ≥ 10× | 其余一律 **仅告警**（SASRec embedding 是 ID 空间，与内容空间本不同构，不可对齐是预期） | — |

**判定规则**：
- `V–T` **通过或告警** → 开训；
- `V–T` **失败** → CGA 无可对齐信号 → 判 D1 致命，**停**，写失败报告，改走附录 A（Amazon-2023 + BLIP-2）或另换特征源；
- `V–B / T–B` 接近随机 → **不算失败**，反而是 CGA 的价值所在（把不可对齐的拉到一起），但必须在报告中说明"几何对齐主要发生在 V–T 对，行为侧对齐信号弱"。

输出 `metrics/gate0_alignability.json`（含三对 R@10、随机基线、打乱对照均值与 σ、`verdict`）。**该文件缺失 → P2 禁止启动。**

---

## 3. 待拍板四项的决议

### 3.1 Φ_fuse：mean 为主，attention 为消融

**拍板：mean（等权均值，零参数）。**

1. **几何相容**：单位超球面下均值方向稳定；attention 加权破坏模长一致性，必须额外 re-norm（论文未定义的算子）。
2. **可归因**：零参数融合使提升只能归因于锚定结构。
3. **样本量**：5k item 子集（约 5–8 万交互）下注意力融合的额外参数易过拟合。

消融版：单头 scaled dot-product，可学习 query（d=256），输出 `LayerNorm + L2` 拉回球面，参数量差异单独报告。

**升级判据**：valid NDCG@10 提升 > 1 个 seed std，且 ≥2/3 seed 同向，且无 NaN/梯度爆炸。否则主表永远 mean。

### 3.2 PSGR `q_proj`：MLP + 全头共享

**拍板：2 层 MLP（256→256→256，GELU + LayerNorm），H 头共享；k/v 按头独立。**

- 只共享 q、不共享 k/v，形成干净对照。
- 若 q 也按头独立，参数量 `O(d²)→O(H·d²)`，H=8 消融时与"参数变多"混淆，无法归因。
- 不用单层线性：LayerNorm 保证输出尺度与 unit-sphere 一致；≥3 层在 256 维、H≤8 下无收益先例。
- 输入已按论文修正为 `z_j`（d=256 item 特征），**不是用户表征拼接维**。

### 3.3 β / λ：主值 1.0 的依据

用户给网格 {0.1, 1, 10}，三点几何等距，主值取几何中位 1.0：

| 参数 | 主值 | 起点理由 | Guard | 调整规则 |
|---|---|---|---|---|
| `β`（commitment） | 1.0 | 太小码本不收敛；太大 encoder 被拖死。1.0 能同时观察到两侧失效模式 | 码本 perplexity `exp(H)`，目标 **51–154**（K 的 10–30%） | 利用率<5% → β↑；>80% 且 L_rec 不降 → β↓ |
| `λ`（L_align 权重） | 1.0 | 对齐项与重建项需在首 100 step 内量级可比 | `L_align / L_rec` 健康区间 **[0.1, 10]** | >10 → λ↓；<0.1 且 Vol 不降 → λ↑ |

注：VQ-VAE 原论文 commitment 用 0.25，但那是无体积竞争项的场景；此处 CGAL 同时拉扯 encoder，不照搬，由 guard 决定落点。

**搜索顺序【v1.2 定】**（不做 3×3 全交叉，省预算且先看失效模式）：

```
Step 1  固定 β=λ=1，扫 τ ∈ {0.05, 0.07, 0.1, 0.2}       → 定 τ
Step 2  固定 λ=1、τ=τ*，扫 β ∈ {0.1, 10}（两端）          → 看两侧失效模式
        两端都健康 → 补 β=1.0 三选一；某端明显崩 → 直接排除该侧区间
Step 3  固定 β=β*、τ=τ*，扫 λ ∈ {0.1, 10} → 同上
```
每格 40 epoch、单 seed；只有进入最终候选的组合才补 3 seed。

### 3.4 vCLUB 完整默认值

```yaml
vclub:
  q_hidden: 256
  q_layers: 2
  q_act: elu
  out_dim: 2 * d          # μ 与 log σ²
  logvar_clip: [-6, 6]
  reparam: true           # 训练采样，评估用 μ
  mi_weight: 0.05         # 网格 {0.01, 0.05, 0.1}
  ema_decay: 0.99         # 仅平滑日志 MI，不参与反传
  batch_min: 512          # batch<512 时 MI 只记录不进早停
  detach_main: true
```

---

## 4. 数据基准：MMSSL Amazon-Baby（v3 裁决）

### 4.1 实测事实（2026-11-10，`data/amazon-baby-mmssl/`）

| 项 | 值 |
|---|---|
| 用户数 | 35,598 |
| 物品数 | 18,357（`max_item_id=18356`） |
| train / valid / test 行数 | 35,598 / 35,598 / 35,598（每行一个用户） |
| train 交互项数 | 190,930（avg 5.4，min 3，max 207） |
| valid 项数 | 37,899（34,190 用户仅 1 项） |
| test 项数 | 67,508（18,301 用户 1 项，10,958 用户 2 项） |
| 时间戳 | **无**（纯 id 序列，无绝对时间） |
| item 交互频次（train） | min 1 / p25 4 / median 6 / p75 11 / p90 21 / max 686 |

### 4.2 切分协议（**铁律修正**）

v1.0 写的"SASRec 必须用全局时间切分、per-user 必泄漏"在新基准下**不成立**，必须修正：

| 旧表述（v1.0） | 修正后（v1.1） |
|---|---|
| 全局交互时间 80/10/10 | **不可用**：数据无绝对时间戳 |
| per-user leave-last-N 一律判为泄漏 | **过于笼统**：per-user 随机切才泄漏；**per-user 时间后段切分**（序列前缀训练 / 后段验证测试）是合法且是序列推荐标准协议 |

**执行口径**：
- 直接用 MMSSL 提供的 `train/valid/test` 三份文件（已是 per-user 时间后段划分）。
- SASRec 只用 `train.txt` 的序列训练；`valid/test` 项对其**完全不可见** → 铁律 1（无泄漏）仍严格成立。
- 论文/报告中必须写 **"per-user chronological holdout（前缀/后段），非全局时间切分"**，不得声称全局时间切分。
- 冷启动仍单独分桶：test 段首次出现的 user/item 不计入主均值。

**副作用（有利）**：MMSSL / MSCA / MMRec 等已发表结果均在同一 Baby 划分上 → **数字可直接同表对标**，这比 Amazon-2023 自切分强得多，也化解了"跨切分不可比"的主要风险。

### 4.3 5k item 子集（v3 口径：按 item 抽，不是按用户）

目的：P3 前快速迭代。**最终数字回到全集。**

```
Step 1 统计每个 item 在 train.txt 中的交互频次 c_i
Step 2 按 c_i 分五层（长尾→头部）：
       L1 c∈[1,3] / L2 [4,6] / L3 [7,11] / L4 [12,21] / L5 [22,∞]
       （边界取实测四分位，脚本内自动重算并落盘）
Step 3 层内按 sha1(item_id) 排序等距抽样，配额按各层 item 数等比分配，
       总目标 5000（每层至少保 200，不足则全取并在下层补）
Step 4 保留与选中 item 有交互的用户；用户 train 交互数（子集内重算）≥ 3 才保留
       （Baby 原始 min=3，用 5 会砍掉大量用户，故降为 3 并报告影响）
Step 5 验收（任一不过则换 sub_seed 重抽，最多 3 次）
```

| 验收指标 | 容差 |
|---|---|
| 交互保留率 | ≥ 55%（5k/18357=27% 的 item 通常覆盖 60–75% 交互） |
| item 覆盖率 | 100%（构造保证） |
| 用户保留数 | ≥ 20,000 |
| 序列长分布 KS（子集 vs 全集） | p > 0.05 |
| 冷启动 item 比例 | 与全集差 < 3 个百分点 |

抽完落盘 `data/splits/baby_5k_item.json`（item id 列表 + sha256），**后续所有实验以该文件的 sha256 为 `split_hash`**。

### 4.4 特征可得性（**BLIP-2 阻塞项**）

| 事实 | 证据 |
|---|---|
| 本地无 Baby 原始封面图 | `docs/MMGCF_cross_analysis.md` L148：`data/sports/images/` 只有 `download_data.md` |
| 本地无 image_url → item 映射 | 全分支检索无 `image_url` 文件 |
| 只有预计算特征 | MMSSL 发布 `image_feat.npy`(4096, **CNN**) + `text_feat.npy`(1024, SBERT)，需 `fetch_mm_data.py` 从 Google Drive 拉 |
| `Image_download.py` 在 PRISM 下**内容为空** | `git show` 无输出（README 提到但脚本缺失） |

**结论：BLIP-2 特征在当前基准下无法自产。** 这是项目名里的 "B"，必须显式决策：

| 路径 | 做法 | 代价 | 后果 |
|---|---|---|---|
| **A（默认）** | 退回 MMSSL 预计算 **CNN 4096 + SBERT 1024**，项目定位改为"预计算多模态特征 + 几何对齐" | 零 | 放弃 BLIP-2 视觉编码，需改项目叙述 |
| B | 下载 Amazon-2014 Baby 元数据（含 `imUrl`）→ 抓图 → BLIP-2 自产 | 1.8 万图，Amazon 老图失效率高（经验 30–40%） | 保住 BLIP-2，但数据缩水、耗时 1–2 天 |
| C | 改回 Amazon-2023 Movies&TV（HF meta 自带 images URL，失效少） | 推翻 v3 裁决-3 | 保住 BLIP-2 + 全局时间切分，但丢掉与 MMSSL 同协议可比性 |

### 4.4 特征来源：路径 A 已拍板【v1.2 封闭】

**裁决：走路径 A —— 用 MMSSL 预计算特征，BLIP-2 不在本轮实现。** 登记为偏离 D1–D4（§2.6），不是"等价替换"。

**先说清一个仓库内部的错误记载（必须纠正，否则整篇方案的特征描述都是错的）**：

| 出处 | 说法 | 判定 |
|---|---|---|
| `code/prep_amazon_sports.py:9` | `image_feat.npy: [n_items,4096] CNN 特征(MMSSL 维度)` | ✅ **正确** |
| `baseline/prism_analysis.md:353` | MMSSL 提供 `image_feat`(4096, **CNN**) + `text_feat`(1024, Sentence-BERT) | ✅ 正确 |
| **`code/fetch_mm_data.py:12`** | "其 `image_feat.npy`(**CLIP-ViT** 4096)" | ❌ **错误**，需修正注释 |
| 外部独立证据 | 仓库内 MARGO 论文（`data/parsed/2504.16524_MARGO`）："the image feature is a **4096-dimensional vector extracted by a CNN model**, and the text feature is a **384-dimensional vector** extracted by a pretrained sentence-transformers" | ✅ 4096 = CNN 得到第三方确认 |

**结论：`4096` 维是 CNN 特征，不是 CLIP，也不是 BLIP-2。** 全仓库唯一真实的 CLIP 是 PRISM `process_clip.py` 的 `ViT-B/32`（512 维）与合成的 64 维版本。**任何文档/报告不得把 4096 称作 CLIP**。

**文本维度存疑（P0 必须实测确认）**：MMSSL 发布档按仓库记载为 1024，但 MARGO 对同源处理的 Baby 写的是 384。两者可能来自不同预处理版本。**P0 第一步动作**：

```bash
python -c "import numpy as np; \
  print(np.load('data/amazon-baby-mmssl/image_feat.npy').shape); \
  print(np.load('data/amazon-baby-mmssl/text_feat.npy').shape)"
```

以实测 shape 为准回填 §1.1 与 config；若 `text=384`，则 `d_txt=384`，与 `D4` 一并更新。

**路径 B/C 处置**：保留为"BLIP-2 复现"独立里程碑，不与主实验混跑；C（改回 Amazon-2023）与本轮 v3 预算前提冲突，除非闸门-0 判定 `V–T` 失败（§2.7）才会被动启用。

### 4.5 动作头：关闭，改 4 维行为辅助输入【v1.2 裁决】

**先纠正一个前提**：上一轮建议"砍掉动作头但把 `rating`/`verified_purchase` 保留为辅助输入"——**这条在 Baby 上无法执行**，因为两个字段都不存在。

实测证据（2026-11-10）：

```
data/amazon-baby-mmssl/  只有 train.txt / valid.txt / test.txt，无任何 meta 文件
train.txt 前两行： "0 3369 13372 5458 11981 17787"
                   "1 8802 5044 6554 7215 3087 11502 15278 4281 2322 2374 6677 9198 15249"
→ 每行只有 user_id + item 序列，无第三列 rating、无 verified、无 timestamp
```

| 项 | 裁决 |
|---|---|
| 动作头 | ❌ **关闭**（`act_head.enabled: false`），代码路径保留以便将来换 Amazon-2023 时开启 |
| 动作词表（8 个 `[ACT_*]`） | ❌ **删除**，不再出现在设计/论文中（D5） |
| `rating` / `verified` 作辅助输入 | ❌ **不可执行**（字段不存在），不做 |
| 替代方案 | ✅ **4 维可计算行为辅助特征**（见下），只作输入、不设预测头 |

**4 维辅助特征**（每条 `(u, i)` 样本，全部从 `train.txt` 计算，无标签泄漏）：

| # | 特征 | 含义 | 归一化 |
|---|---|---|---|
| A1 | `log1p(item_train_freq)` | 物品流行度 | 除以 `log1p(max_freq)` |
| A2 | `repeat_flag` | 该 item 是否已出现在该用户历史 | 0/1 |
| A3 | `pos_ratio` | 目标相对 **history（train 前缀）内**的位置 | /(prefix_len−1)，clamp [0,1] |
| A4 | `log1p(seq_len)` | 用户 **train 段**序列长（活跃度） | 除以 `log1p(max_len)` |

**统计范围铁律（v1.3 锁死，防跨时段泄漏）**——4 维里 A1/A4 依赖全局统计、A3 依赖序列定义，全部**只允许以 train 段为源**：

| # | train-only 规则 | 违反即泄漏的形态 |
|---|---|---|
| A1 | 频次表**只从 `train.txt` 计数**，冻结成 `aux_freq_table`（+sha256）；valid/test **查同一张表**，表中没有的 item 记 0（`log1p(0)=0`，即冷物品编码） | 用全量（train+valid+test）计数 → test 冷门物品的 A1 变相暴露了"它将来会出现" |
| A2 | 构造上因果：只查目标位置**之前**的 history prefix；评估时 history 与 SASRec 输入同源（train 前缀），天然不含 valid/test 项 | 把 valid/test 段的 item 也算进"已出现" |
| A3 | 分母用 **train 前缀长度**（prefix_len），**不用全序列长**——valid/test 样本的目标不参与定义自身位置 | 分母含 valid/test 段 → 目标前的"还剩多少"间接暴露未来长度 |
| A4 | `seq_len` = **train 段前缀长**，与 SASRec 输入前缀严格一致；valid/test 期间新增交互**不计入** | 用全历史长度 → 活跃度特征吸收了测试期行为量 |
| 归一化常数 | `max_freq` / `max_len` 等**只在 train 上算一次**，冻结进 `configs/aux_norm.json`（含 hash），落进 ckpt 随 `split_hash` 一起校验 | 每个 split 各算各的 → 同一物品在不同 split 语义漂移，且间接泄分布 |

**审计（并入 `audit_split.py`）**：①正向——断言 `aux_freq_table` 的 hash == config 记录值；②负向——用 train+valid+test 重算一份频次表，**必须与冻结表不一致**（证明代码确实没用全量）；③评估脚本加载 ckpt 时校验 `aux_stats_hash`，与 `split_hash` 任一不符直接报错拒绝运行。

接入方式：4 维 → 1 层 MLP（4→16）→ 与 `h_beh` 逐元素相加（或 concat 后线性降维回 `d_model`），**不做独立预测头**。

**为什么值得做**：这 4 维是 Baby 里唯一可得的"行为语义"，成本近乎零，且能让方案在"纯序列 + 内容特征"之外多一层可解释性。但**必须在报告中声明它们不是论文的动作模态**（D5），不得用 `[ACT_*]` 命名。

**将来若要恢复动作头**（换 Amazon-2023）：`act_head.enabled: true` + 词表 `[ACT_R1..R5] + [ACT_NOVER] + [ACT_VERIFY]/[ACT_UNVERIFIED]`，代码里按 flag 分支，不在主路径上编译。

---

## 5. 负采样规格

| 阶段 | 池 | 说明 |
|---|---|---|
| 训练（召回） | **train 段出现过的 item**（子集内） | 排除只在 valid/test 出现的 item，防泄未来 |
| 训练（L_align） | batch 内其他样本 | 零开销，随 batch 变难 |
| valid/test | **full catalog**（主）+ 100-neg sampled（辅） | 主指标无采样偏差；辅指标对齐文献表格 |

| 场景 | 比例 |
|---|---|
| 召回训练 | in-batch（B−1）+ 每正例采 4 个 → B=1024 时 ≈1027 |
| 动作头 | **已关闭**（§4.5，Baby 无监督信号）；开启时也无需负采样 |
| L_align | batch 内，τ_align=0.07 |

- **下限**：任何 batch 有效负例 ≥ 256，否则退固定池，不允许"负例不够照跑"。
- **流行度**：主用 uniform（无偏）；`freq^0.75` 仅作鲁棒性消融进附表。禁"训练按流行度采、评估报全库、却不声明"。
- **种子**：`base*100003 + epoch*1009 + batch_idx` 派生式（`num_workers>0` 下顺序消耗不可复现）；负采样独立 RNG stream；每 epoch 落 `neg_hash` 做审计。

```yaml
sampling:
  pool_train: train_items_only
  pool_eval: full_catalog
  n_neg_train: 4
  min_neg_per_batch: 256
  popularity_alpha: 0.0
  neg_seed_rule: "base*100003 + epoch*1009 + batch_idx"
  tau_align: 0.07
  seed_global: [42, 2025, 2026]
  seed_split: 42
```

---

## 6. 训练轮数 / 早停 / Checkpoint

| 阶段 | max epoch | 早停指标 | patience | ckpt |
|---|---|---|---|---|
| SASRec 预训练 | 300 | train 内部 holdout **R@20** | 20 | best+last |
| 码本/CGA 预热 | 20 | 重建 MSE 降幅 <1% | 5 | best |
| 主训练（DST+RQN+PSGR+vCLUB） | 100 | valid **NDCG@10** | 10 | best+last |
| 网格单格 | 40 | 同上 | 8 | 仅 best |

- **SASRec `hidden=512`**【定，成本 v1.3 重估】：对齐论文 behavioral `d=512`（D8 只偏离"权重来源"，不偏离"维度"）。**v1.2 写的"2–3 倍（估 1–2h/300ep）"按 128 维口径作废**，重估如下：

| 项 | `hidden=128`（旧口径） | `hidden=512`（重估） | 依据 |
|---|---|---|---|
| 参数量 | ~5M（emb 2.35M×2 + 0.4M） | **~16–25M**（emb 9.4M×2 视 tying + attn/FFN 6.3M） | 参数量主要被 item emb 主导，×4–5 |
| 计算量 | — | attn/FFN 项 O(d²) 理论 ×16，**实测经验 ×4–6**（emb lookup 与 softmax 项不随 d² 缩放，IO 占比上升） | (512/128)² = 16 为上界 |
| 每 epoch（fp32, batch128, 含全量评估） | 实测 ~10–12 min（E15-TF：500ep 预算、早停 ep12–13、总 2.7h） | **40–70 min** | 按经验放大系数 ×4–6 |
| 每 seed 实际耗时 | — | 早停典型 ep10–20 → **7–20h**；patience=20 下 300ep 预算不会跑满 | 早停节律与 hidden 无强相关 |
| 3 seed 串行 | — | **1–2.5 天**（缓解后见下） | — |
| 峰值显存 | <1GB | **2–4GB**（batch128 fp32）/ **4–6GB**（batch256+AMP）；主导项是 `B×L×N` logits ≈ 117M fp32 ≈ 0.5GB | 16GB **充裕，瓶颈是墙钟时间而非显存** |

**强制缓解（P1 执行）**：AMP fp16 + batch 256 + 评估间隔放宽为每 2 epoch（patience 按评估次数计，等效 40 epoch）→ 每 seed 压到 **4–10h**。**P1 第一步必须先跑 1 epoch 计时并外推**；外推 >24h/seed → 触发 L3 降级 `hidden=256` 并登记新偏差 **D11**（行为维度 256，进 CGA 前加线性升维 256→512 补偿，保住"第三模态接口维=512"）。
- Baby 规模（19 万交互）比 Amazon-2023 小两个量级，SASRec max epoch 从 500 降到 300。
- 早停指标唯一（NDCG@10）；R@20 只做 guard（NDCG 升而 R@20 跌 >2 点 → 判不稳定，lr 回退一档）。
- 梯度裁剪 1.0；AdamW：下游/SASRec `lr=1e-3`，码本 `1e-4`；warmup 5% steps；cosine → `lr×0.01`。
- ckpt 命名 `ckpt/{stage}_{seed}_{tag}.pt`，必存 `config_hash` / `split_hash` / `git_commit` / `best_metric`；加载时校验 `split_hash`，不一致直接报错。
- 只留 best+last；网格格只留 best。连续 3 step 非有限 loss → 回滚 + lr×0.5，写 `logs/instability.jsonl`；同 run 回滚 3 次终止并标 `unstable`。

---

## 7. Baseline 协议（同切分重跑，禁跨切分搬数）

| 项 | 决定 |
|---|---|
| 对照模型 | **LightGCN++ 在本地重跑**（够轻，单卡可跑） |
| 切分 | 必须用 §4.3 的同一份 `baby_5k_item.json` + 同一份 train/valid/test |
| 旧数字 | LightGCN++ P0-P2 的现成结果只能标"协议不一致（旧切分/全量）"，**不得进同一张表** |
| 同协议可直接对标 | MMSSL / MSCA / MMRec 等已发表 Baby 结果（同一官方划分），可作为外部参照并在表注写明"引用自原论文" |
| Hi-SAM 的 baseline | WuKong / HSTU / MTGR / QARM / PSRQ+MCCA / DLRM 是**论文 baseline，不是本地模型**；**v1.2 定：一律不复现**，只作原文引用，表注标"原文结果" |
| 报告必须写 | 切分方式（per-user chronological holdout）、边界定义（无绝对日期）、冷启动定义、子集抽取 sha256 |

审计脚本 `code/audit_split.py`（P0 交付）：核验①train/valid/test 用户集合一致 ②无 train 项泄漏进 valid/test ③子集 item 全覆盖 ④sha256 与 config 记录一致。

---

## 8. 交付产物 / 失败策略

### 8.1 产物

```
baseline/sab_anc/
├── configs/     # 入库：模板 + resolved config（含 config_hash）
├── logs/        # 入库：train_*.log、metrics_*.jsonl、instability.jsonl、neg_audit.jsonl
├── metrics/     # 入库：*.json（schema 见下）、subset_audit.json、split_audit.json
├── figures/     # 入库：png 300dpi + pdf
├── ckpt/        # gitignore
├── data/        # gitignore（txt / npy / 图）
└── reports/     # 入库
```

指标 JSON 必含：`run_id / stage / seed / config_hash / split_hash / git_commit / n_m / feature_source / valid{...} / test{warm{...}, cold_item{...}, cold_user{...}} / aux_feat{enabled:true} / act_head{enabled:false} / diagnostics{cgal_mode, gram_volume, gram_min_sv_ratio, codebook_perplexity, codebook_groups:6, vclub_mi, phi_fuse} / runtime{wall_sec, peak_vram_mb} / status(ok|unstable|aborted|degraded)`。

- `n_m=3` 与 `feature_source=mmssl_precomputed` 必须落进 JSON（对应 D1/D6，事后可审计）。
- **warm / cold 分开成三个键**，禁止只报总体均值——主结论在 `cold_item`（§2.5 风险 1）。
- `act_head.enabled=false` 显式写出，避免读者误以为双头模型。

9 张必备图：五项 loss 分线、valid NDCG 曲线、Gram 体积 vs step、码本使用直方图（6 组分开）、vCLUB MI 曲线、模态对齐余弦分布（3 对分开）、**7 行消融矩阵柱状（warm/cold 并排，误差棒=3 seed std）**、闸门-0 检索 R@10 对比、codebook 组间使用熵。

### 8.2 四级升级

| 级 | 动作 | 时限 | 触发 |
|---|---|---|---|
| L1 实现 | 单 batch overfit、逐层梯度范数、shape/归一化断言、`det(G)` 检查、最小复现 | ≤2h | loss 不降 / NaN / 指标≈随机 / 码本全塌 |
| L2 调参 | lr 网格、β/λ/λ_vcl 网格、τ 网格、warmup | ≤1d | 能训但不过 baseline |
| L3 缩规模 | 5k→2k item；d 256→128；K 512→256；H 4→2；RQN_sh 3→2；SASRec hidden 512→256（+D11） | ≤1d | OOM / **SASRec 1ep 计时外推 >24h/seed**（40–70min/epoch 是 512 维的正常水平，不触发）/ 显存>14GB |
| L4 停止 | 写失败报告（已排除项、日志、最小复现、假设）提交决策 | — | L1–L3 全过仍不过线；同失败重演 2 次 |

硬禁：test 调参 / 静默改切分 / 跳过 NaN batch / 降级不留痕 / 同 bug 修两次仍复现还继续。

---

## 9. 变更记录

| 日期 | 项 | 原值 | 新值 | 依据 |
|---|---|---|---|---|
| 2026-11-10 | Eq.1 形式 | "双向 Gram 体积对齐"（描述性） | 对称对比 `(L_D2A+L_A2D)/2`，`Vol` 入 softmax 指数 | 论文原文 |
| 2026-11-10 | `CGAd` | 作为参数名使用 | **弃用**，改为 `d=256`（CGA 公共维度） | 论文无此符号 |
| 2026-11-10 | PSGR 输入 | 待定（曾考虑用户/物品表征拼接） | 残差 `r_{N_sh}` + `z_j` semantic probe，q 输入 `d=256` 的 item 特征 | 论文原文 |
| 2026-11-10 | `τ` | 未定 | 0.07 主，{0.05,0.07,0.1,0.2} 敏感性 | 本文件 §2.3 |
| 2026-11-10 | N_m=3 anchor | 未定 | 3 组轮换取平均（2 模态时 2 组） | 本文件 §2.4 |
| 2026-11-10 | 数据集 | Amazon-2023 Movies&TV/Books | **MMSSL Baby + 5k item 子集** | v3 裁决-3 |
| 2026-11-10 | 切分铁律 | "全局时间切分，per-user 必泄漏" | per-user chronological holdout（前缀/后段），SASRec 只见 train | 数据无时间戳（实测） |
| 2026-11-10 | 子集口径 | 5k 用户分层 | **5k item 分层** | v3 口径 |
| 2026-11-10 | baseline | 复用 P0-P2 数字 | 同切分重跑，旧数字标"协议不一致" | 跨切分不可比 |
| 2026-11-10 | 动作头 | 双头（召回+动作分类） | **默认砍掉动作头**（Baby 无 rating/verified，词表不可构造） | 实测字段缺失（§4.5） |
| 2026-11-10 | **第三模态** | 类别/品牌编码（默认 A） | **behavioral(SASRec item embedding, d=512)** | 论文 `N_m=3` = visual/textual/behavioral；CAT/BRD 属下下游输入（§2.5） |
| 2026-11-10 | `N_m` / 码本组数 | 2 路 / 降级待定 | **3 / 6 组（3 共享 + 3 特定）** | 同上 |
| 2026-11-10 | BLIP-2 | 待拍板（§4.4 A/B/C） | **路径 A 正式拍板**，登记偏差 D1–D4 | 成本/收益（§4.4） |
| 2026-11-10 | 特征命名 | `4096` 被称 "CLIP-ViT"（`fetch_mm_data.py:12`） | **`4096` = CNN 特征**，禁止称 CLIP | MARGO 2504.16524 原文 + `prep_amazon_sports.py:9` |
| 2026-11-10 | rating/verified 辅助输入 | 拟保留为辅助特征 | **不可执行**（字段不存在）→ 改 4 维可计算辅助特征 | 实测目录无 meta、序列无第三列（§4.5） |
| 2026-11-10 | 评估口径 | 总体均值 | **warm / cold-item / cold-user 三分开**，主结论在 cold-item | 论文 Cold AUC 叙事（§2.5） |
| 2026-11-10 | 新增门禁 | 无 | **闸门-0 跨模态可对齐性预检**，`gate0_alignability.json` 缺失禁启 P2 | D1 偏离的必然配套（§2.7） |
| 2026-11-10 | SASRec hidden | 64–128 | **512**（对齐论文 `d=512`） | 第三模态维度一致（§6） |
| 2026-11-10 | `β`/`λ` 网格 | 9 格全跑 | **先扫两端 {0.1, 10}**，健康再补 1.0 | 省预算、先看失效模式（§3.3） |
| 2026-11-10 | Hi-SAM 6 baseline | 待定是否复现 | **不复现**，仅原文引用 | 复现成本远超预算（§7） |
| 2026-11-10 | **SASRec hidden=512 成本** | "2–3 倍，估 1–2h/300ep"（128 维口径误用） | **每 seed 7–20h（缓解后 4–10h），显存 2–6GB**；P1 先 1 epoch 计时外推，>24h/seed 触发 L3 降 256 + D11 | 重估：参数 ×4–5、attn/FFN O(d²)（§6） |
| 2026-11-10 | **4 维辅助特征统计范围** | "全部从 train.txt 计算"（一句带过） | **逐维锁死 train-only 规则 + 冻结归一化常数 + 负向审计**（§4.5 表） | 防跨时段泄漏（A1 频次表/A3 位置分母/A4 长度） |

---

## 10. 拍板状态：全部封闭（0 项待定）+ P0 执行清单

v1.0/v1.1 遗留 5 项，v1.2 全部封闭：

| # | 事项 | 裁决 | 依据 |
|---|---|---|---|
| 1 | BLIP-2 路径 | **A**（预计算特征），登记 D1–D4 | 成本/收益 + v3 预算前提 |
| 2 | 动作头 | **关闭**，改 4 维可计算辅助特征 | Baby 无 rating/verified（实测） |
| 3 | 第三模态 | **behavioral(SASRec d=512)**，`N_m=3`、6 组码本 | 论文模态定义 |
| 4 | `β`/`λ` 网格 | **两端优先**：{0.1, 10} → 健康再补 1.0 | 省预算、先看失效模式 |
| 5 | Hi-SAM 6 baseline | **不复现**，仅原文引用 | 成本远超原型预算 |

**P0 执行清单（按序，前项不过不进下一项）**：

| # | 动作 | 产物 | 门禁 |
|---|---|---|---|
| 1 | `fetch_mm_data.py` 拉特征（走代理/GDrive） | `image_feat.npy` / `text_feat.npy` | 缺失则停（R8） |
| 2 | **打印特征 shape 回填 config** | 更新 §1.1 `d_txt`（1024 还是 384） | 维度不符 §2.5 表 → 先改表再改码 |
| 3 | `build_item_subset.py` 抽 5k item | `data/splits/baby_5k_item.json` + sha256 | 验收表 §4.3 |
| 4 | `audit_split.py` | `metrics/split_audit.json` | 无 train 项泄漏进 valid/test |
| 5 | **`gate0_alignability.py`（闸门-0）** | `metrics/gate0_alignability.json` | `V–T` 不得 fail（§2.7） |
| 6 | `train_sasrec.py`（hidden=512，3 seed） | `ckpt/sasrec_best.pt` ×3 | 内部 holdout R@20 达 E15-TF 量级 |
| 7 | `extract_sasrec_feat.py` | `beh_feat.npy`（用户侧）/ `sasrec_item_emb.npy`（behavioral 模态） | 后者 L2 范数≈1 |
| 8 | `run_baseline_lightgcnpp.sh` 同切分重跑 | baseline 数字（warm/cold 分开） | 必须与 SAB-ANC 用同一 `split_hash` |

> 顺序说明：把闸门-0 放在 SASRec 重训**之前**，是因为它只依赖已有特征、几分钟可跑完；若 `V–T` 失败，整个方案的视觉/文本对齐环节要重做数据源，此时烧 3 seed SASRec 是纯浪费。
