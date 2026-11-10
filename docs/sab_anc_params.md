# SAB-ANC 参数决议与默认值 · Decision Record v1.1

> 配套：`docs/sab_anc_design.md`（设计基线）
> 状态：**本文件为参数唯一权威来源**。代码/设计中任何数值与本文件冲突，以本文件为准，并须在同一提交内改掉冲突处。
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
| `N_m`（模态数） | 3（论文）→ **本地只有 2 路，见 §2.4** | ⚠️冲突 | 需补第三模态或改 2 组轮换 |
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

**⚠️ 本地数据只有 2 路模态**（`image_feat` + `text_feat`），见 §2.5——`N_m=2` 时改为 2 组轮换，`data` 即另一路单模态，不做平均。

### 2.5 第三模态缺口（阻塞项）

| 事实 | 证据 |
|---|---|
| 本地 Baby 只有 2 路特征：`image_feat`(4096) + `text_feat`(1024) | MMSSL 官方发布，`prism_analysis.md` L353 |
| 论文 `N_m=3` | 用户提供的论文原文 |

三条补法（P0 必须选一条，否则 `N_m` 只能取 2，Eq.1 的 3 组轮换退化为 2 组）：

| 方案 | 做法 | 成本 | 风险 |
|---|---|---|---|
| **A（推荐）** | 第 3 模态 = **类别/品牌元数据编码**（`categories` 多热 或 `brand` embedding），与 image/text 一并进 CGA | 低（Baby meta 可得） | 需先有 meta 文件，本地同样缺 |
| B | 第 3 模态 = **文本再编码的第二视角**（标题 SBERT 384 + 描述 TF-IDF） | 低 | 与 text 同源，几何多样性弱，审稿人会质疑"第三个模态"名不副实 |
| C | 直接 `N_m=2`，论文口径改为"双模态"，Eq.1 只跑 2 组轮换 | 零 | 与论文 `N_m=3` 不一致，必须在报告中声明偏差 |

**默认执行 A**，若 meta 不可得则退 C 并在报告写明"仅 2 模态，已偏离论文 N_m=3"。

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

**默认执行 A**（先让模型链路跑通），B/C 作为"BLIP-2 复现"独立里程碑，不与主实验混跑。此决策需你确认（见 §10-1）。

### 4.5 动作头存废（新基准下的第二个硬冲突）

design §5.3 的动作词表 `[ACT_R1..R5] + [ACT_NOVER] + [ACT_VERIFY]/[ACT_UNVERIFIED]` **完全建立在 Amazon-2023 的 `rating` 与 `verified_purchase` 字段上**。

MMSSL Baby 的实测字段：只有 `user_id` + `item_id` 序列，**无 rating、无 verified、无 timestamp、无 review 文本**。

| 项 | 结论 |
|---|---|
| 动作词表可行性 | ❌ 8 个 token 全部无法构造（无评分桶、无验证购买标记） |
| 动作头可行性 | ❌ 监督信号不存在 → 双头退化为**单头（只有召回头）** |
| 方案表述影响 | 论文中若保留"双头/动作词表"章节即数据不支持，审稿人一查即穿（与 design R5 同类风险，但这次是致命级） |

三条出路：

| 方案 | 做法 | 代价 |
|---|---|---|
| **A（推荐）** | **砍掉动作头**，方案改为单任务召回；[ANC] + Eq.1 + 量化链路全部保留 | 论文少一个创新点，但方案自洽 |
| B | 用可得信号造伪动作词表：如"该物品是否出现在用户序列的前半/后半""序列内位置桶" | 语义勉强，审稿人可能质疑"这不是动作" |
| C | 换回 Amazon-2023（有 rating + verified） | 与 v3 裁决冲突，且 BLIP-2 问题仍在 |

**默认 A**，并在设计文档删除 §5.3 词表与 §5.4 动作头。需你确认（§10-2）。

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
| 动作头 | 无需负采样 |
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
| Hi-SAM 的 baseline | WuKong / HSTU / MTGR / QARM / PSRQ+MCCA / DLRM 是**论文 baseline，不是本地模型**；引用时必须标注"原文结果"，不得让读者误以为本地复现 |
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

指标 JSON 必含：`run_id / stage / seed / config_hash / split_hash / git_commit / valid{...} / test{...} / act_head{...} / diagnostics{cgal_mode, gram_volume, gram_min_sv_ratio, codebook_perplexity, vclub_mi, phi_fuse} / runtime{wall_sec, peak_vram_mb} / status(ok|unstable|aborted|degraded)`。

7 张必备图：五项 loss 分线、valid NDCG 曲线、Gram 体积 vs step、码本使用直方图、vCLUB MI 曲线、模态对齐余弦分布、消融柱状（误差棒=3 seed std）。

### 8.2 四级升级

| 级 | 动作 | 时限 | 触发 |
|---|---|---|---|
| L1 实现 | 单 batch overfit、逐层梯度范数、shape/归一化断言、`det(G)` 检查、最小复现 | ≤2h | loss 不降 / NaN / 指标≈随机 / 码本全塌 |
| L2 调参 | lr 网格、β/λ/λ_vcl 网格、τ 网格、warmup | ≤1d | 能训但不过 baseline |
| L3 缩规模 | 5k→2k item；d 256→128；K 512→256；H 4→2；RQN_sh 3→2 | ≤1d | OOM / epoch>30min / 显存>14GB |
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

---

## 10. 仍需你拍板（5 项）

1. **BLIP-2 怎么办（§4.4）**：A 退预计算 CNN 4096（零成本、改叙述）／ B 抓 Amazon-2014 Baby 图自产（1–2 天、失效率 30–40%）／ C 改回 Amazon-2023（推翻 v3，但保住 BLIP-2 + 全局时间切分）。**建议 A 先跑通链路，B/C 另开里程碑。**
2. **动作头存废（§4.5）**：A 砍掉动作头改单任务（方案自洽）／ B 造伪动作词表（语义勉强）／ C 换数据。**建议 A。**
3. **第三模态（§2.5）**：A 类别/品牌编码（需 meta 文件，本地同样缺）／ B 文本第二视角／ C 只做 2 模态并声明偏离论文 `N_m=3`。
4. **`β` 与 `λ` 的网格优先级**：9 格全跑（5k 子集约 9×40 epoch）还是先粗扫 {0.1, 10} 两端再定中间？**建议后者**（先看两端失效模式，再定落点）。
5. **Hi-SAM 的 6 个 baseline**（WuKong/HSTU/MTGR/QARM/PSRQ+MCCA/DLRM）是否也要本地复现（成本高），还是仅作外部引用？**建议仅引用**，本地只复现 LightGCN++。
