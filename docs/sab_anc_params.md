# SAB-ANC 参数决议与默认值 · Decision Record v1.0

> 配套文档：`docs/sab_anc_design.md`（设计基线 v1.0）
> 状态：**本文件为参数唯一权威来源**。设计与代码中出现的任何数值，若与本文件冲突，以本文件为准，并须在同一提交内改掉冲突处。
> 日期：2026-11-10 ｜ 分支：`experiments`

---

## 0. 三态约定

每个参数标注三种状态之一，避免"以为定了其实没定"：

| 标记 | 含义 | 改动权限 |
|---|---|---|
| **【锚】** | 论文锚定值，不可改（改了就不是复现） | 禁止改动，只允许在报告中记录偏差 |
| **【定】** | 已定，实现按此写死 | 需走变更记录（§9） |
| **【拍】** | 本次拍板，给出默认值 + 网格 + 推翻判据 | 有数据支撑即可在网格内调整 |

---

## 1. 参数总表

### 1.1 上游 DST（CGAd 参数模块）

| 参数 | 值 | 状态 | 说明 |
|---|---|---|---|
| `CGAd` | 256 | 【锚】 | 参数模块隐维 |
| 流形约束 | 单位超球面（L2 归一化） | 【锚】 | 所有参数/码字投影后 `x / ‖x‖₂`，ε=1e-8 |
| 体积目标 | Gram 体积 | 【锚】 | 见 §2.1 主/备选 |
| 体积损失形式 | **完整 L_D2A + L_A2D（Eq.1）** | 【定】 | 主方案；纯体积最小化作降级备选，仅在主方案数值不稳时启用 |
| `Φ_fuse` | **mean 为主**，attention 为消融 | 【拍】 | 见 §2.2 |
| 码本更新 | STE + commitment `sg[·]` | 【锚】 | 前向取最近码字，反向直通；commitment 只推 encoder |
| `β`（commitment） | **1.0**，网格 {0.1, 1, 10} | 【拍】 | 见 §2.4 |
| `λ`（体积损失权重） | **1.0**，网格 {0.1, 1, 10} | 【拍】 | 同上 |

### 1.2 RQN

| 参数 | 值 | 状态 |
|---|---|---|
| `RQN_sh`（共享层数） | 3 | 【锚】 |
| `K`（码本大小） | 512 | 【锚】 |
| 投影维度 | 512 × 256（输入 512 → 码字 256） | 【锚】 |

### 1.3 PSGR

| 参数 | 值 | 状态 | 说明 |
|---|---|---|---|
| `H`（头数） | **4 主 / 8 消融** | 【定】 | 8 只用于容量消融，不进主表 |
| `q_proj` 结构 | **2 层 MLP（256→256→256），GELU + LayerNorm** | 【拍】 | 见 §2.3 |
| `q_proj` 参数共享 | **全头共享一套** | 【拍】 | 见 §2.3 |
| 每头维度 | `d/H`：H=4 → 64，H=8 → 32 | 【定】 | 由 256 整除得出 |
| key/value 投影 | 按头独立 | 【定】 | 与 q_proj 共享形成对照，便于归因 |

### 1.4 vCLUB

| 参数 | 值 | 状态 | 说明 |
|---|---|---|---|
| `q_θ` 分布假设 | 高斯 `q(z_i｜z_j)=N(μ,σ²)` | 【锚】 | 用重参数化 |
| `q_θ` 结构 | **2 层 MLP，hidden 256，ELU**，输出 `2d`（μ, log σ²） | 【拍】 | 见 §2.5 |
| `log σ²` 裁剪 | [-6, 6] | 【拍】 | 防方差塌陷/爆炸 |
| MI 权重 `λ_vcl` | **0.05**，网格 {0.01, 0.05, 0.1} | 【拍】 | MI 上界量级大于 CE，需小权重 |
| 估计器 | vCLUB 上界，batch 内构造负对 | 【定】 | batch < 512 时对 MI 估计做 EMA(0.99) 平滑，仅用于日志 |
| 评估期采样 | 用 `μ`（不采样） | 【定】 | 降方差 |

---

## 2. 待拍板项决议

### 2.1 体积损失：主方案与降级路径

**主【定】：完整 L_D2A + L_A2D（Eq.1）**——双向 Gram 体积对齐，两个方向的体积项都保留。

**降级备选：纯体积最小化**（只压 Gram 行列式，不做方向对齐）。触发条件（任一即降级，须在日志中记录 `cgal_mode: volume_only`）：

- 主方案 `L_cgal` 在 200 step 内不下降（相对初值降幅 < 5%）；
- Gram 矩阵出现秩塌陷（最小奇异值 / 最大奇异值 < 1e-4 连续 20 step）；
- 主方案下指标方差显著大于备选（3 seed std 之比 > 2）。

降级不是自由选择：必须在报告中写明"主方案失败 → 备选"的因果链与证据。

### 2.2 Φ_fuse：mean 为主，attention 为消融

**拍板：mean（等权均值，零参数）为主版本。**

理由：
1. **几何相容性**：CGAd 约束在单位超球面，等权均值天然落在球内且方向稳定；attention 加权会破坏模长一致性，必须额外加 re-norm，等于引入一个未在论文中定义的算子。
2. **可归因性**：主表数字若来自零参数融合，则性能提升只能归因于锚定结构本身，不会被"多了一组注意力参数"混淆。
3. **样本量**：5k 子集/21 万交互量级下，注意力融合的额外参数容易过拟合；其收益通常要百万级交互才显现。

**消融版本**：单头 scaled dot-product，`query` 为可学习向量 `d=256`，输出接 `LayerNorm` + L2 归一化（拉回球面），与 mean 版本**参数量差异单独报告**。

**推翻判据**（满足才允许把 attention 升级为主版本）：
- valid NDCG@10 提升 > 1 个 seed 标准差；
- **且** 3 个 seed 中至少 2 个方向一致；
- **且** 参数量增加不影响训练稳定性（无 NaN、无梯度爆炸）。

否则主表永远用 mean，attention 只出现在消融表。

### 2.3 PSGR `q_proj`：MLP + 全头共享

**拍板：`q_proj` = 2 层 MLP（`256→256→256`，GELU + LayerNorm），H 个查询头共享同一套权重。**

- 只有 `q` 共享；`k` / `v` 仍按头独立——这样"共享 vs 独立"的对照是干净的。
- 为什么不让 q 也按头独立：参数量从 `O(d²)` 变 `O(H·d²)`，H=8 消融时会与容量效应混淆，无法判断提升来自多头还是来自参数变多。
- 为什么不用单层线性：2 层给非线性，且 LayerNorm 保证输出尺度与 unit-sphere 约束一致；3 层以上在 256 维、H≤8 的规模下无收益先例。
- 输出分割：`q_proj(x)` 产出 256 维，按头切成 `H` 段（H=4 → 每段 64），不做额外投影。

### 2.4 β / λ：为什么主值取 1.0

用户建议网格 {0.1, 1, 10}，三点几何等距，主值取**几何中位 1.0**（不是算术拍脑袋）：

| 参数 | 主值 | 起点理由 | Guard 指标 | 调整规则 |
|---|---|---|---|---|
| `β`（commitment） | 1.0 | 太小 → 码本不收敛（码字漂移）；太大 → encoder 被 commitment 项拖死（重建先坏）。1.0 是唯一能同时观察到两侧失效模式的起点 | 码本 perplexity（`exp(entropy)`），目标区间 **K 的 10%–30%**（K=512 → 51–154） | 利用率 < 5% → β↑（1→10）；利用率 > 80% 且 L_rec 不降 → β↓（1→0.1） |
| `λ`（体积） | 1.0 | 体积项与重建项量级需在首 100 step 内可比；λ=1 时若体积项压过重建，说明归一化有问题而非 λ 太大 | `L_cgal` 与 `L_rec` 的比值，健康区间 **[0.1, 10]** | 比值 > 10 → λ↓；比值 < 0.1 且体积无下降 → λ↑ |

**注意**：VQ-VAE 原论文 commitment 用 0.25，但那是 β 单独作用、无体积竞争项的场景。这里有 CGAL 体积损失同时拉扯 encoder，所以不照搬 0.25，改用建议网格的中位 1.0 起步，由 guard 指标决定落点。三档全跑（9 组）在 5k 子集上约 9×40 epoch，单卡可承受。

### 2.5 vCLUB：完整默认值

```yaml
vclub:
  q_hidden: 256
  q_layers: 2
  q_act: elu
  out_dim: 2 * d          # μ 与 log σ²，d=256
  logvar_clip: [-6, 6]
  reparam: true           # 训练期采样，评估期用 μ
  mi_weight: 0.05         # λ_vcl，网格 {0.01, 0.05, 0.1}
  ema_decay: 0.99         # 仅平滑日志中的 MI 估计，不参与反传
  batch_min: 512          # batch < 512 时 MI 估计方差大，只记录不用于早停
```

- 估计式（vCLUB 上界）：`Î = E_p[log q(z_i|z_j)] − E_{p(z_i)p(z_j)}[log q(z_i|z_j)]`，负对来自同 batch 打乱。
- 反传只走 `q_θ` 的参数更新方向（最小化上界），**不**对主表征做梯度阻断以外的干预；主表征侧若需阻断，用 `detach()`，且必须在 config 里显式 `vclub.detach_main: true`。
- 数值保护：`log q` 计算前把 `logvar` clamp 到 [-6, 6]，避免 exp 溢出导致 NaN（本仓库历史上有过 NaN 事故，见 instability 日志惯例）。

---

## 3. 负采样完整规格

### 3.1 候选池范围

| 阶段 | 池 | 理由 |
|---|---|---|
| 训练（召回） | **train 段出现过的 item** | 排除只在 valid/test 出现的 item，否则等于把未来物品信息泄进训练 |
| 训练（对齐 L_align） | batch 内其他样本的正例 | 零额外开销，天然随 batch 增大而变难 |
| valid | **full catalog**（主）+ 100-neg sampled（辅） | 主指标用全库排序（无采样偏差）；辅指标便于与文献表格对齐 |
| test | **full catalog**，只跑一次 | 同 valid，禁止调参 |

### 3.2 比例

| 场景 | 比例 | 有效负例数 |
|---|---|---|
| 召回训练 | in-batch（`B−1`）+ 每正例采样 `n_neg=4` | `B=1024` 时 ≈ 1027 |
| 召回训练（Books，item 9 万） | 采样 `n_neg=4096` 固定池（复用 design R2） | 4096 |
| 动作头 | 无需负采样（多分类 CE） | — |
| L_align | batch 内，温度 `τ=0.07` | `B−1` |

下限约束：**任何 batch 的有效负例数不得少于 256**，否则 softmax 方差过大、梯度噪声盖过信号（batch 小就退化为固定池采样，不允许"负例不够也照跑"）。

### 3.3 是否按流行度

**主实验：均匀采样（uniform，无偏）。**

理由：全库排序评估下，均匀负例会系统性高估热门物品——这是**已知且可报告的偏差**，比"按流行度采样再偷偷加权校正"更诚实、更容易被审稿人接受。

**鲁棒性消融（单独一行进附表，不进主表）**：`p(item) ∝ freq^0.75`（word2vec 式）。若两者 test 指标差异 > 2 个点，说明模型对负例分布敏感，须在局限性一节写明。

禁止做法：训练用流行度采样、评估报全库数字、却不声明——这是隐性指标美化。

### 3.4 随机种子

```yaml
seed:
  global: [42, 2025, 2026]      # 与 design §6 一致
  split: 42                     # 切分永远用 42，保证所有 seed 面对同一份数据
  neg_stream: independent       # 负采样独立 RNG，不与 init/data order 共享
  neg_seed_rule: "base * 100003 + epoch * 1009 + batch_idx"
```

- **必须独立 stream**：否则换 batch 顺序会改变负例序列，"只改了一个超参"的实验其实同时改了负例，归因失效。
- **按 `batch_idx` 派生而非顺序消耗**：`num_workers>0` 时 DataLoader 顺序不确定，顺序消耗的 RNG 不可复现；派生式 seed 与 worker 数无关。
- 复现审计：每个 epoch 落盘 `neg_hash`（采样索引数组的 `xxhash` 前 8 位），写入 `logs/neg_audit.jsonl`。两次同 seed 运行 `neg_hash` 序列必须逐 epoch 相同，否则判定复现失败。

---

## 4. 训练轮数 / 早停 / Checkpoint

### 4.1 分模块约定

| 阶段 | max epoch | 早停指标 | patience | 评估频率 | 保留 ckpt |
|---|---|---|---|---|---|
| SASRec 预训练 | 500 | 内部 valid **R@20**（副 NDCG@20 做 guard） | 20 | 每 epoch | best + last |
| 码本/CGAd 预热 | 20 | 重建 MSE 相对降幅 < 1% | 5 | 每 epoch | best |
| 主训练（DST + RQN + PSGR + vCLUB + 双头） | 100 | 下游 valid **NDCG@10** | 10 | 每 epoch | best + last |
| β/λ/λ_vcl 网格单格 | 40 | 同上 | 8 | 每 epoch | 仅 best（其余删） |
| 5k 子集快速筛 | 30 | 同上 | 6 | 每 epoch | 仅 best |

补充规则：
- **早停指标唯一**：主指标 NDCG@10 决定停机，R@20 只做 guard（若 NDCG 升而 R@20 跌 > 2 点，判为不稳定，回退一档 lr）。
- SASRec 的早停**只许**看内部 valid（train 尾部 10%），与下游 valid 物理隔离（design §2.2 铁律）。
- 梯度裁剪 `max_norm=1.0`，全阶段统一。
- 优化器：AdamW；下游 `lr=1e-3`、SASRec `lr=1e-3`、码本 `lr=1e-4`（码字走 EMA 更新时此项不适用）；warmup = 5% total steps；cosine decay 到 `lr×0.01`。

### 4.2 Checkpoint 保存规则

命名：`ckpt/{stage}_{seed}_{tag}.pt`，例 `ckpt/downstream_s42_mean_b1.0.pth`

必存字段：

```python
{
  "model": state_dict,
  "optimizer": opt.state_dict(),
  "scheduler": sch.state_dict(),
  "epoch": int, "best_metric": float,
  "config_hash": str,        # resolved config 的 sha256
  "git_commit": str,
  "seed": int,
  "split_hash": str,         # splits/*.json 的 sha256，防止换切分后误用旧 ckpt
}
```

- 只留 **best + last**，中间 epoch 不落盘（Amazon 规模下 100 epoch × 每个 30MB 会吃掉数十 GB，D 盘虽大但没必要）。
- 网格搜索的每个格子只保留 best，跑完即删其余，避免 9 组 × 3 seed 堆积。
- `ckpt/` 一律 gitignore；`config_hash` + `split_hash` 使任何 ckpt 都能反查出生配置。
- **加载保护**：加载 ckpt 时校验 `split_hash` 与当前 splits 一致，不一致直接报错退出（防止最隐蔽的一类错误：换了切分却复用旧权重）。

### 4.3 不稳定处理

- 连续 3 个 step 非有限 loss → 回滚到上一个 ckpt，`lr *= 0.5`，写 `logs/instability.jsonl`。
- 同一 run 回滚 3 次 → 终止该 run，标记 `status: unstable`，不进指标汇总。
- 静默跳过 NaN batch 是禁止行为（会让指标虚高且不可复现）。

---

## 5. 5k 子集抽取协议

用途：P3 之前的快速迭代与超参筛选；**最终数字必须回到全集**。

### 5.1 抽取标准：分层（按用户交互量），不是随机也不是 Top

```
Step 1 过滤：train 段交互数 ≥ 5（序列模型最小可学长度）
            且 valid 段 ≥ 1 且 test 段 ≥ 1（否则该用户无法评估）
Step 2 分桶：按 train 交互数分五层（长尾到头部）
            [5,6] / [7,10] / [11,20] / [21,50] / [51,+inf)
Step 3 层内抽样：按 sha1(user_id) 排序后等距取 1000（确定性，不依赖 RNG 调用顺序）
Step 4 补足：某层不足 1000 时全取，缺口由下一层补；最终用户数记实际值（可能 ≠ 5000，允许 4800–5200）
Step 5 覆盖 guard：统计 item 覆盖率；若 < 60%，对未覆盖 item 按其交互用户追加抽样 200 用户，
            记为 extra_pool，最终用户数上限 5200
```

**为什么不分纯随机**：纯随机会按交互量比例自然偏向头部用户（Amazon 头部用户交互可达数百条），子集与全集分布一致但**序列长度分布被压缩**，长序列相关结论在子集上不成立。分层可保证五档用户量都有样本，子集上的结论能外推。

**为什么不用 Top 交互量**：Top 用户是最"好学"的一批，任何模型在其上都好看，会系统性高估方案效果——这是最危险的一种子集偏差。

### 5.2 交互量下限

- 用户侧：**train ≥ 5**（低于 5 无法构造有意义的 next-item 上下文）。
- 物品侧：不过滤，但要求子集 item 覆盖率 ≥ 60%（Step 5 guard），否则补样。
- 序列截断：`max_len=50`，超出保留**最近 50 条**（不是最早 50 条）。

### 5.3 分布一致性验收

子集 vs 全集必须报下表，任一不达标则重新抽（换 `sub_seed`，最多 3 次）：

| 指标 | 容差 |
|---|---|
| 用户交互量均值 / 中位 / P90 | 相对偏差 < 10% |
| item 覆盖率 | ≥ 60% |
| 冷启动用户比例（test 段首现） | 绝对差 < 3 个百分点 |
| KS 检验（交互量分布） | p > 0.05 |

验收结果写入 `metrics/subset_audit.json`，随报告一并交付。

---

## 6. CLIP 4096 / SBERT 1024 来源核实（**含纠错**）

### 6.1 实测结论

本地核查 `baseline/LightGCNpp/code/prep_amazon_sports.py` 头部注释（git 可查）：

```
image_feat.npy      : [n_items, 4096]  CNN 特征(MMSSL 维度)
image_feat_clip.npy : [n_items, 64]    CLIP 特征
```

**因此："CLIP 4096" 是错误表述。** 真实情况：

| 说法 | 实际 | 证据 |
|---|---|---|
| "CLIP 4096" | ❌ 4096 = **CNN 特征**（MMSSL 官方发布维度），与 CLIP 无关 | `prep_amazon_sports.py` L9 |
| CLIP 维度 | 64（本仓库合成版）或 512（`PRISM/data/process_clip.py` 用 `ViT-B/32`） | 两处代码 |
| SBERT 1024 | MMSSL 官方 `text_feat.npy` 是 1024，但**具体模型名本仓库无留档** | `prism_analysis.md` L353 仅写 "Sentence-BERT (1024)" |
| 另有一处 384 | `mixragrec_prism_integration.md` 与 design §7 写 `all-MiniLM-L6-v2`，该模型输出 **384**，与 1024 冲突 | 两处文档互斥 |

### 6.2 对本项目的处置

SAB-ANC 走 Amazon 2023 + BLIP-2 自产特征，**不复用 MMSSL 遗留特征**，从根上绕开这个含混：

| 模态 | 采用模型 | 维度 | 状态 |
|---|---|---|---|
| 视觉 | `Salesforce/blip2-opt-2.7b` Q-Former | 32×256 → pool 到 **256** | 【定】 |
| 文本 | `sentence-transformers/all-MiniLM-L6-v2` | **384** | 【定】 |
| 文本（备选，若 384 表达力不足） | `BAAI/bge-large-zh-v1.5` 或 `bge-large-en-v1.5` | 1024 | 【拍】仅在文本消融显著弱时启用 |

**必须同步修正 design 文档两处**：§5.1 `[TXT_i]` 写"SBERT / BLIP-2 文本特征"未给维度 → 补 384；§7 config `txt_model` 保留 `all-MiniLM-L6-v2` 但显式标注 `txt_dim: 384`。

若后续要引用 MMSSL 特征做对照实验，必须先在报告中写一句"MMSSL 官方 1024 维文本特征的具体编码器模型未在源仓库留档"，不得直接称其为 CLIP 特征。

---

## 7. 交付产物规范

### 7.1 目录与入库策略

```
baseline/sab_anc/
├── configs/          # 入库：模板 + 每次 run 的 resolved config（yaml，含 config_hash）
├── logs/             # 入库：train_*.log（文本）、metrics_*.jsonl（逐 epoch）、instability.jsonl、neg_audit.jsonl
├── metrics/          # 入库：*.json 结构化指标（见 7.2 schema）、subset_audit.json
├── figures/          # 入库：png（300dpi）+ pdf（矢量），命名见 7.3
├── ckpt/             # gitignore（体积）
├── data/             # gitignore（交互 txt / npy 特征）
└── reports/          # 入库：阶段性 md（或放 docs/）
```

### 7.2 指标 JSON schema（强制字段）

```json
{
  "run_id": "sab_anc_movies_s42_mean_b1.0_20261110T1300",
  "stage": "downstream",
  "seed": 42,
  "config_hash": "sha256:...",
  "git_commit": "...",
  "split_hash": "...",
  "valid": { "ndcg@10": 0.0, "ndcg@20": 0.0, "recall@10": 0.0, "recall@20": 0.0 },
  "test":  { "ndcg@10": 0.0, "ndcg@20": 0.0, "recall@10": 0.0, "recall@20": 0.0,
             "cold_start": { "ndcg@10": 0.0, "user_ratio": 0.0 } },
  "act_head": { "acc": 0.0, "macro_f1": 0.0 },
  "diagnostics": {
    "codebook_perplexity": 0.0, "codebook_usage_ratio": 0.0,
    "gram_volume": 0.0, "gram_min_sv_ratio": 0.0,
    "vclub_mi": 0.0, "anc_content_cos": 0.0,
    "cgal_mode": "full_eq1"
  },
  "ablation": { "phi_fuse": "mean", "use_anc": true, "heads": 4 },
  "runtime": { "gpu_hours": 0.0, "wall_sec": 0, "peak_vram_mb": 0 },
  "status": "ok"
}
```

`status` 取值：`ok` / `unstable` / `aborted` / `degraded`（走了降级路径必须标 `degraded` 并在 `notes` 写原因）。

### 7.3 图表清单（每份报告必须齐）

| 图 | 内容 | 判读要点 |
|---|---|---|
| `fig_loss_curve` | L_rec / L_cgal / L_act / L_align / L_vcl 分线 | 五项是否同量级、有无互相压制（E14 教训） |
| `fig_valid_curve` | valid NDCG@10 / R@20 vs epoch | 早停点是否合理，是否过拟合 |
| `fig_gram_volume` | Gram 体积 vs step | 单调压降为健康；抖动或反弹 = 归一化问题 |
| `fig_codebook_usage` | 码字使用直方图 | 目标 perplexity 51–154（K 的 10%–30%） |
| `fig_vclub_mi` | MI 上界 vs step | 应缓慢下降；持续上升 = 负对构造有误 |
| `fig_anc_cos` | h_anc 与正/负样本内容余弦分布 | 两分布应有可见分离，重叠则锚定未起效 |
| `fig_ablation_bar` | mean vs attention、H=4 vs 8、use_anc 开关 | 误差棒为 3 seed std |

### 7.4 报告

`docs/sab_anc_p0_report.md` ~ `p4_report.md`，每份必须含：配置摘要（config_hash）、对照 baseline（LightGCN++ P0-P2 数字）、本阶段结论、失败与降级记录、下一步。

---

## 8. 失败默认策略（四级 escalation）

| 级别 | 动作 | 时限 | 触发条件 |
|---|---|---|---|
| **L1 实现排查** | 单 batch overfit（10 个 batch 能否把 loss 压到 ~0）；梯度范数逐层打印；shape/归一化/单位球断言；最小可复现用例 | ≤ 2 小时 | loss 不降 / NaN / 指标≈随机（NDCG@10 < 0.01）/ 码本全塌到一个码字 |
| **L2 调参** | lr 网格 {1e-4,3e-4,1e-3,3e-3}；β/λ 网格；warmup 比例；梯度裁剪 | ≤ 1 天 | 能训但不过 baseline（LightGCN++ P0-P2） |
| **L3 缩规模** | 全集 → 5k 子集 → 2k；`d_model` 256→128；`K` 512→256；`H` 4→2；`RQN_sh` 3→2 | ≤ 1 天 | OOM / 单 epoch > 30 min / 显存峰值 > 14 GB |
| **L4 停止并决策** | 写失败报告（已排除项清单、日志路径、曲线、最小复现命令、当前假设），提交拍板 | — | L1–L3 全走过仍不过线；或同一失败在两次独立 run 中重演 |

硬性规则（违反任何一条，该 run 数据作废）：

1. **禁止在 test 上调参**。test 只跑一次，跑完即锁定。
2. **禁止静默改切分**。任何切分变更须更新 `split_hash` 并重跑全部下游实验。
3. **禁止静默跳过 NaN batch** 或"过滤掉不收敛的 seed"。3 seed 必须全报，含方差。
4. **任何降级（cgal_mode / φ_fuse / 负采样策略）必须写进 logs 与 metrics 的 `notes`**，并在本文件 §9 变更记录中留痕。
5. 同一个 bug 修两次仍复现 → 直接 L4，不再尝试第三次（防止在错误前提上耗尽算力）。

---

## 9. 变更记录

| 日期 | 项 | 原值 | 新值 | 依据 |
|---|---|---|---|---|
| 2026-11-10 | 全表首版 | — | — | 本文件 v1.0 |
| 2026-11-10 | 文本特征维度 | design §7 未标（隐含 384） | 显式 `txt_dim: 384` | §6.1 核实 |
| 2026-11-10 | 视觉特征表述 | "CLIP 4096" | "CNN 4096（MMSSL）/ BLIP-2 256（本项目）" | §6.1 核实 |

---

## 10. 仍需你拍板的残余项

以下 5 项本文件无法定值，需要论文原文或你的判断：

1. **Eq.1 的具体形式**：L_D2A / L_A2D 各是什么？（我按"双向 Gram 体积对齐"理解：D2A = 数据侧 Gram 体积对锚定侧，A2D = 反向。若公式是 det 的对数、或归一化后的体积比，实现差异很大。）
2. **CGAd 的全称与语义**：是 Codebook-Gram Anchor dimension 一类？名字影响论文写作，不影响实现。
3. **PSGR 的输入是什么**：用户表征 / 物品表征 / 两者拼接？决定 `q_proj` 的输入维度。
4. **两个数据集先跑哪个**：建议先 Movies & TV（item 数少、全量 softmax 可跑），Books 作为规模泛化验证。
5. **baseline 对照用哪份数字**：直接用 LightGCN++ P0-P2 现有结果，还是需要在同一时间切分上重跑？（跨切分的数字不可直接比，这是最容易被审稿人抓的点。）
