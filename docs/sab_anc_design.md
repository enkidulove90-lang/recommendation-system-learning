# SAB-ANC 设计文档 · 三模态（visual/textual/behavioral）几何对齐 + 量化 + 锚定下游模型

> 项目代号：**SAB-ANC**（**SASRec-Anchored Behavior/Content downstream**，命名可改，全局替换即可）
> 状态：设计基线 v1.2（2026-11-10）｜分支：`experiments`
> **参数数值以 `docs/sab_anc_params.md`（Decision Record v1.2）为唯一权威来源**，本文与之处突时以参数决议文件为准。
> v1.2 变更：第三模态定为 **behavioral(SASRec, d=512)** → `N_m=3`、6 组码本；**动作头关闭**（Baby 无 rating/verified）改 4 维辅助特征；BLIP-2 → 预计算特征**正式拍板为路径 A**，新增**偏差登记册**与**闸门-0 可对齐性预检**。项目名中的 "B(BLIP-2)" 已不成立，命名待改。
> v1.1 变更：数据集切到 **MMSSL Amazon-Baby + 5k item 子集**（v3 裁决）；切分改为 **per-user chronological holdout**（数据无时间戳）；`CGAd` 弃用改 `d=256`；PSGR 输入按论文修正为残差 + `z_j` probe。
> 前置阅读：`docs/EXPERIMENT_HANDOFF.md`（环境与 4 个 OMP 变量）、`docs/e14bis_mechanism_diagnosis.md`（锚定机制教训来源）、`docs/e15_tf_report.md`（SASRec 训练成本实测）

---

## 0. 一句话定位

用**冻结的 SASRec** 同时产出两样东西 —— 用户序列表征（行为上下文）与 item 行为嵌入（第三模态）；把 visual / textual / behavioral 三路 item 特征经 **CGA 几何对齐（Eq.1）→ RQN 量化 → PSGR 语义聚合**，再通过结构性锚点 token **[ANC]** 与用户行为段汇聚，训练一个轻量**单头召回**打分模型。

三条设计铁律（均有前车之鉴）：

| 铁律 | 来源教训 |
|---|---|
| SASRec 只许看 `train.txt`，valid/test 对其完全不可见 | 特征提取器泄漏 = 下游指标虚高 |
| 切分用**官方 per-user 前缀/后段 holdout**，不用随机切（Baby 无时间戳，全局时间切分不可用） | 随机切 = 用户后段项混进训练 = 真实泄漏 |
| 锚定靠**结构**（[ANC] 插在行为段与内容段之间），不靠辅助损失 | E14-bis：cos 锚定 λ 扫到 10 仍被 L_syn 压制（cos 卡死 0.27） |

> ⚠️ 第四条铁律（v1.2 新增）：**任何跨编码器/跨数据集的偏离都必须进登记册（params §2.6），不许沉默处理**。本方案的高级别偏离有 2 个（D1 非同源编码器、D5 无动作信号），都会直接削弱结论强度。

---

## 1. 现状核查（2026-11-09，本地实测）

| 项 | 结论 |
|---|---|
| SASRec checkpoint | **全分支无任何 `.ckpt/.pth`**（E15-TF 训练完权重即弃，只留 logs）→ 必须重训 |
| 数据基准 | **MMSSL Amazon-Baby**（v3 裁决）：35,598 u / 18,357 i / train 190,930 项（avg 5.4）/ valid 37,899 / test 67,508。**无时间戳**，为 per-user 序列三件套 |
| 时间戳 | **无** → 全局时间切分不可用，改 per-user chronological holdout（§2.2 修正） |
| 多模态特征 | MMSSL 预计算 `image_feat`(**CNN** 4096) + `text_feat`(1024)；**无原始封面图、无 image_url 映射** → BLIP-2 无法自产；已拍板走路径 A（params §4.4） |
| 第三模态 | ✅ **behavioral 可得**：由本地重训 SASRec 的 item embedding 表提供（`d=512`），与 visual/textual 构成论文同构的 `N_m=3`（params §2.5） |
| 动作信号 | ❌ **不可得**：Baby 无 `rating` / `verified_purchase` / timestamp → 动作头关闭，动作词表整节删除（params §4.5） |
| [ANC] | 仓库无既有定义，本文首次明确化（§5.2） |
| 本机硬件 | RTX 5060 Ti ×1 / 16GB / driver 610.88；CPU 28 线程；RAM 32GB；D 盘 1.6TB 可用 |
| SASRec 重训成本 | Baby 19 万交互、单卡 16GB 约 20–40 min/100 epoch 量级 |
| BLIP-2 推理 | opt-2.7b（~8GB）16GB 可跑——**但前提是有原始图片，当前不满足** |

---

## 2. 数据与切分（v1.1 基准：MMSSL Baby）

### 2.1 数据源（实测）

```
数据源: MMSSL Amazon-Baby  →  baseline/LightGCNpp/data/amazon-baby-mmssl/
  train.txt   35,598 行 / 190,930 项   (每行: user_id item_id1 ... item_idn，按时间序)
  valid.txt   35,598 行 /  37,899 项   (34,190 用户 1 项)
  test.txt    35,598 行 /  67,508 项   (18,301 用户 1 项，10,958 用户 2 项)
  物品数 18,357 (max_item_id=18356)；物品交互频次 train: median 6 / p90 21 / max 686
  时间戳: 无
多模态: MMSSL 预计算 image_feat.npy (4096, CNN) + text_feat.npy (1024, SBERT)
  ⚠️ 原始封面图/image_url 本地均无 → BLIP-2 自产受阻（params §4.4，三条路径待拍板）
```

### 2.2 切分（per-user chronological holdout）

```
每个用户的交互序列按时间先后排列：
|<———— train.txt（前缀）————>|<— valid.txt —>|<— test.txt —>|
   SASRec 与下游共享此段         早停 + 超参      只跑一次
```

- **直接用 MMSSL 三件套**：`train/valid/test` 已是 per-user 前缀/后段划分，不自造切分。
- **SASRec 预训练**：只用 `train.txt` 序列，next-item 目标；内部再切 train 尾部 10% 做早停；**禁止**触碰 valid/test 项。
- **下游**：train 同 `train.txt`（SASRec 冻结出特征），valid/test 用对应文件。
- **冷启动分桶**：test 段首次出现的 user/item 单独报告，不计入主均值。
- **子集**：在 `train.txt` 上抽 5,000 个 item（分层，见 params §4.3），三份文件同步裁剪，落盘 `data/splits/baby_5k_item.json` 并以其 sha256 作 `split_hash`。

### 2.3 全局时间 vs per-user（**裁定修正**）

| 方案 | 适用性 | 裁定 |
|---|---|---|
| 全局交互时间 80/10/10 | **不可用**：Baby 无绝对时间戳，无法定边界日期 | ❌ 仅 Amazon-2023 路径（附录 A）可用 |
| per-user 随机切分 | 用户后段项可能混进训练 → 真实泄漏 | ❌ 禁用 |
| **per-user 时间后段切分（前缀训练/后段测试）** | SASRec 只见前缀 → **无泄漏**；且是序列推荐标准协议 | ✅ **主方案** |

v1.0 曾把"per-user"一律判为泄漏，这是过强论断：**泄漏来自随机切，而非来自 per-user 本身**。此处用的是官方前缀/后段划分，铁律 1（SASRec 只许见 train）仍严格成立。

副作用（有利）：MMSSL / MSCA / MMRec 等已发表结果同用此划分 → **数字可同表对标**，化解跨切分不可比的风险。

---

## 3. SASRec 重训约定

| 项 | 约定 |
|---|---|
| 入口 | 复用 `baseline/PRISM/SASRec.py` 骨干（去掉 PRISM 头），或独立脚本 `code/train_sasrec.py` |
| 目标 | next-item 交叉熵（负采样 1:1），**hidden=512**（对齐论文 behavioral `d=512`），2 层 Transformer，max_len=50 |
| Early stop | 内部 holdout（train 尾部 10%），patience=20，**best-by-internal-valid** |
| 产物 | `ckpt/sasrec_best.pt`（权重 + config + `split_hash` 一并存） |
| 使用（两个出口） | **(a) 用户侧**：末层隐状态近 K=5 步 mean-pool → `h_beh`（进 [BEH] 区段）；**(b) item 侧**：`item_embedding` 矩阵（18357×512）L2 归一化 → **behavioral 模态**，与 image/text 并列进 CGA |
| Git | `.ckpt` 一律 gitignore，只入库 config + 日志 + 指标 |

> ⚠️ **(b) 是 v1.2 新增且关键**：同一份 SASRec 同时供"行为上下文"与"第三模态"。这让 `behavior-only` 消融几乎等价于 SASRec 本身（params §2.5 风险 2），但也保证了与论文 `N_m=3` 的结构一致——这是本轮权衡后选择的"结构优先"。若后续审稿质疑"behavioral 与标签同源"，退路是把 (b) 换成**item 共现图上的 LightGCN 嵌入**（同为行为侧但不含序列目标），作为 D8 的备选，成本约半天。

---

## 4. 目录规划（新增到 experiments 分支）

```
baseline/sab_anc/
├── code/
│   ├── fetch_mm_feats.py          # MMSSL 预计算特征拉取（复用 LightGCNpp/code/fetch_mm_data.py）
│   ├── build_item_subset.py       # 5k item 分层抽样 → data/splits/baby_5k_item.json + sha256
│   ├── audit_split.py             # 切分审计（无泄漏/子集覆盖/hash 一致），P0 必交付
│   ├── gate0_alignability.py      # ★ 闸门-0：跨模态可对齐性预检（params §2.7），不过禁启 P2
│   ├── train_sasrec.py            # SASRec 重训（§3 约定，hidden=512）
│   ├── extract_sasrec_feat.py     # 两个出口：beh_feat.npy（用户侧）+ sasrec_item_emb.npy（behavioral 模态）
│   ├── cga_align.py               # CGA 投影 + Eq.1 对称对比（Vol=√det(G)，τ=0.07，3 组轮换，N_m=3）
│   ├── rqn_psgr.py                # RQN 共享量化(N_sh=3,K=512) + PSGR(残差 ← z_j probe)，码本 6 组
│   ├── extract_blip2_feat.py      # 路径B/C 专用（当前 blocked，见 params §4.4）
│   ├── run_baseline_lightgcnpp.sh # 同切分重跑 baseline（params §7 强制）
│   ├── main_downstream.py         # 下游单头召回训练/评估入口
│   ├── model_downstream.py        # token 组织 + [ANC] + 召回头 + 4 维辅助特征
│   └── analyze_anc.py             # [ANC] 探针（对齐余弦/检索命中率，防 E14 复刻）
├── data/
│   ├── splits/baby_5k_item.json   # ★ 入库（小文件），sha256 作 split_hash
│   └── ...                        # gitignore: 交互 txt / *.npy 特征
├── ckpt/                          # gitignore
├── logs/                          # 入库
├── metrics/                       # 入库（schema 见 params §8.1）
├── figures/                       # 入库
├── configs/
│   └── sab_anc_baby.yaml          # ★ config 模板见 §7
├── .gitignore
└── README.md

docs/
├── sab_anc_design.md              # 本文档
├── sab_anc_params.md              # 参数决议（数值唯一权威）
└── sab_anc_p0_report.md ...       # 阶段报告
```

依赖增量：`transformers>=4.40`、`torch`(CUDA)、`datasets`(HF)、`sentence-transformers`、`Pillow`。其余沿用 `EXPERIMENT_HANDOFF.md`。

---

## 5. 下游模型定义

### 5.0 前置：item 侧特征链（CGA → RQN → PSGR，均已按论文定值）

```
三路 item 模态特征（visual 4096 CNN / textual 1024 / behavioral 512 SASRec item emb）
   └─L2 归一化 → 各过 W_j 投影→ z_j ∈ R^d (d=256, 单位超球面)
        └─Eq.1 对称对比对齐：L_align = (L_D2A + L_A2D)/2，Vol=√det(G)，Vol 入 e^{-Vol/τ} softmax，τ=0.07
          （N_m=3 → anchor 逐一轮换 3 组，data = 其余两模态均值）
             └─RQN 共享量化 N_sh=3, K=512, 512→256   ── 码本 6 组 = 3 共享 + 3 模态特定
                  ├→ 残差 r_{N_sh} = f − ẑ_sh        ← PSGR 主输入
                  └→ z_j (原始对齐特征)               ← PSGR 的 semantic probe（query 来源）
                       └─PSGR: z_sp^(j) = Attn(z_j, K̃, Ṽ)，聚合残差 → item 语义 token
                            └→ HMAT 阶段做用户序列建模（不在本文档范围）
```

**三条必须守住的归属**（v1.0 曾混）：

| 项 | 正确表述 | 错误表述 |
|---|---|---|
| PSGR 主输入 | 共享量化残差 `r_{N_sh}` | "用户表征"或"用户/物品拼接" |
| PSGR query | **item 的第 j 模态对齐特征 `z_j`** | 用户表征 |
| 处理对象 | DST/PSGR 全在 **item 多模态特征**上；用户序列在 HMAT | "PSGR 处理用户序列" |

`q_proj` 输入维度 = `d = 256`，故 §7 config 的 `psgr.q_proj` 输入固定 256，不随下游 `d_model=128` 变化（两者是不同空间，中间靠投影桥接）。

### 5.1 输入 token 组织（每候选物品一条样本）

```
[BEH_1..BEH_5] ⊕ aux(4d)   [ANC]   [VIS_i] [TXT_i] [BHV_i]   → 召回打分
└── 用户行为上下文（冻结）──┘  └锚点┘  └──── 候选物品三模态（CGA 输出）────┘
```

| token | 定义 | 维度/来源 | 可学? |
|---|---|---|---|
| `[BEH_1..5]` | SASRec 末层隐状态近 K=5 步，各经共享线性投影（非 mean-pool——保留步序信息） | `beh_feat.npy` | 仅投影层 |
| `aux` | 4 维辅助特征（流行度/重复/位置/序列长）经 MLP(4→16)，**加到 `[BEH_1]` 上** | params §4.5 | MLP |
| `[ANC]` | **可学习锚点 token（1 个）**，物理插在行为段与内容段之间 | `d_model` | ✅ |
| `[VIS_i]` | visual 模态 CGA 输出 `z_vis`（4096→256） | `image_feat.npy` | CGA 的 `W_vis` |
| `[TXT_i]` | textual 模态 CGA 输出 `z_txt`（1024→256） | `text_feat.npy` | CGA 的 `W_txt` |
| `[BHV_i]` | behavioral 模态 CGA 输出 `z_beh`（512→256） | `sasrec_item_emb.npy` | CGA 的 `W_beh` |

三个模态 token 均取 **CGA 之后的 `z_j`（256 维）**，再各过一层线性投到 `d_model=128`；候选融合表征 `v_i = MLP([z_vis; z_txt; z_beh])`。

> ⚠️ **`[CAT_i]/[BRD_i]` 已删除**（v1.2）：Baby **无 meta 文件**，类别/品牌字段不存在，token 无法构造。这是第 10 项偏离（params §2.6 D10）。若将来补到 meta，再以 flag 开关恢复。

### 5.2 [ANC] 的双重作用

1. **信息汇聚**：`h_anc` = [ANC] 位置的输出隐状态，是两个预测头的唯一源泉。
2. **对齐锚点**：`L_align` 把 `h_anc` 拉向正样本内容表征、推远 batch 内负样本（InfoNCE）。与 E14-bis 的区别：不与任何几何 decorrelation 损失共存，锚定即结构。

### 5.3 动作头：**关闭**（v1.2 裁决，原词表整节删除）

**数据事实**（实测，不可绕过）：

```
data/amazon-baby-mmssl/ 仅 train.txt / valid.txt / test.txt，无 meta 文件
每行 = user_id + item 序列，无第三列 rating、无 verified_purchase、无 timestamp
```

| 项 | 结论 |
|---|---|
| 原 8 个 `[ACT_*]` token（R1–R5 / NOVER / VERIFY / UNVERIFIED） | ❌ **全部无法构造** → 词表从设计中删除，不得出现在方案/论文 |
| 双头 | ❌ 退化为**单头召回** |
| `rating`/`verified` 作辅助输入 | ❌ 字段不存在，**不做** |
| 替代信号 | ✅ **4 维可计算辅助特征**（下表），只作输入、不设预测头 |

| # | 特征 | 来源 | 归一化 |
|---|---|---|---|
| A1 | `log1p(item_train_freq)` | **train.txt 频次表（冻结）** | / `log1p(max_freq)` |
| A2 | `repeat_flag` | item 是否已在用户 **train 前缀**出现 | 0/1 |
| A3 | `pos_ratio` | 目标相对 **train 前缀内**的位置 | /(prefix_len−1)，clamp |
| A4 | `log1p(seq_len)` | 用户 **train 段**序列长 | / `log1p(max_len)` |

**统计范围铁律（params §4.5 v1.3）**：频次表只从 `train.txt` 计数并冻结（valid/test 查表，冷 item 记 0）；A3 分母用 train 前缀长（**不用全序列长**）；A4 只算 train 段（valid/test 新增交互不计）；`max_freq`/`max_len` 等**归一化常数只在 train 上算一次**，冻结进 `configs/aux_norm.json` 并随 ckpt 校验。`audit_split.py` 加负向审计：用全量重算的表必须与冻结表**不一致**（证明没有偷用全量统计）。

**申报口径（写进报告）**：这 4 维是"可得的行为语义代理"，**不是论文的动作模态**，命名不得用 `[ACT_*]`。代码里保留 `act_head.enabled` 开关（默认 false），换 Amazon-2023 时可开启，主路径不编译该分支。

### 5.4 预测头（单头召回）

| 头 | 输入 | 结构 | 指标 |
|---|---|---|---|
| 召回头 | `h_anc` ⊕ 候选融合表征 `v_i = MLP([z_vis; z_txt; z_beh])` | 双线性 `h_ancᵀW v_i` + **全 18,357 item 全量 softmax**（Baby 规模无需采样） | R@10/20、NDCG@10/20（warm / cold 分开） |
| ~~动作头~~ | — | **关闭**（§5.3） | — |

### 5.5 监督损失（v1.2：去掉动作项）

```
L = L_rec        # 召回头 CE / InfoNCE（1 正 + in-batch 负 + 每正 4 负）
  + λ₂·L_align   # [ANC]-内容 InfoNCE（batch 内负采样），λ₂ ∈ {0.0, 0.1, 0.5}
```

- `L_act` 项随动作头一并删除（D5）。
- SASRec 冻结 → 无需对其正则；下游模型小（~10–15M 参数），单卡 epoch 分钟级。
- 消融开关全部做成 config 布尔：`use_visual` / `use_txt` / `use_beh_modality` / `use_anc`（`use_anc=false` 时 [ANC] 退化为普通拼接池化，核心消融）。
- **强制 7 行消融矩阵**：`V / T / B / V+T / V+B / T+B / V+T+B`，warm 与 cold-item 并排列（params §2.5 风险 1）。

---

## 6. 评估协议

| 段 | 指标 | 规则 |
|---|---|---|
| valid | R@20 / NDCG@20（下游早停 + τ/β/λ 网格） | 多 seed {42, 2025, 2026}，报均值±方差（沿用 E15 惯例） |
| test | R@10/20, NDCG@10/20 **分三桶**：`warm-item` / `cold-item`（freq≤5）/ `cold-user`（len≤3） | 只跑一次最终 config；禁止在 test 上调参 |
| **主结论** | **cold-item 上的提升**（对应论文 Cold AUC 叙事） | 总体均值只作附表；warm 单独一列 |
| 消融 | 7 行模态矩阵 + `use_anc` + Φ_fuse(mean/attn) + H(4/8) | 每行 3 seed，误差棒报 std |
| 探针 | `analyze_anc.py`：h_anc↔内容余弦、检索 R@K | 防重演 E14（探针 R²=0.147 平台）——探针不过线则先修锚定再谈指标 |
| 闸门-0 | 跨模态检索 R@10（V–T/V–B/T–B）+ 打乱对照 | `gate0_alignability.json` 缺失 → P2 禁启 |

---

## 7. Config 模板（`configs/sab_anc_movies.yaml`）

```yaml
# ============ SAB-ANC 实验配置 ============
project: sab_anc
dataset: mmssl_amazon_baby             # v3 裁决：仅 Baby，不跑 Amazon-2023
data:
  root: baseline/LightGCNpp/data/amazon-baby-mmssl
  train: train.txt                     # 35,598 行 / 190,930 项
  valid: valid.txt                     # 37,899 项
  test:  test.txt                      # 67,508 项
  n_users: 35598
  n_items: 18357
  feat:                                # MMSSL 预计算（路径 A，params §4.4）
    image: image_feat.npy              # [18357, 4096] CNN —— 非 CLIP、非 BLIP-2（D2）
    text:  text_feat.npy               # [18357, 1024] sentence-transformers（型号未留档，D3）
    # ⚠️ P0 第 2 步：load 打印 shape，若 text=384 则改 d_txt=384 并更新 params §1.1
  net: {proxy: "http://127.0.0.1:7897", gdrive_via: fetch_mm_data.py}

split:                                 # ★ per-user chronological holdout（唯一权威切分）
  mode: per_user_prefix_holdout         # 官方三件套，不自造
  split_file: data/splits/baby_5k_item.json
  split_hash: null                      # 由抽子集脚本写入 sha256，加载 ckpt 时校验
  cold_start_bucket: true
  sasrec_internal_holdout: 0.10         # train 尾部 10%，SASRec 早停专用

sasrec:
  hidden: 512                          # ★ 对齐论文 behavioral d=512（params §6 v1.3 重估）
  layers: 2
  max_len: 50
  epochs: 300                          # Baby 规模下调（params §6）
  patience: 20                         # 按"评估次数"计（见 eval_interval）
  eval_interval: 2                     # ★ 每 2 epoch 评估一次（512 维下评估占比高）
  amp: fp16                            # ★ 强制缓解：hidden=512 每 seed 7–20h → 4–10h
  batch_size: 256                      # 显存峰值估 4–6GB，16GB 充裕
  timing_gate: true                    # ★ P1 第一步：1 epoch 计时外推，>24h/seed → 触发 L3 降 hidden=256（D11）
  seeds: [42, 2025, 2026]
  ckpt: baseline/sab_anc/ckpt/sasrec_best.pt
  freeze: true                         # ★ 下游阶段强制冻结
  outputs: [user_beh, item_emb]        # item_emb = behavioral 模态来源

feat:
  beh_k: 5                             # 近 K 步隐状态各一个 token（保留步序）
  source: mmssl_precomputed            # 【路径A 已拍板】mmssl_precomputed | blip2_selfbuilt
  # ---- 路径 A：三模态输入维（CGA 的 W_j 按此自适应）----
  image_dim: 4096                      # CNN（非 CLIP！D2）
  text_dim: 1024                       # 待 P0 实测确认（D3/D4）
  beh_dim: 512                         # SASRec item embedding（D8）
  # ---- 路径 B/C（另立里程碑，不混跑）----
  blip2:
    enabled: false
    model: "Salesforce/blip2-opt-2.7b"
    qformer_tokens: 32
    pooled_dim: 256
    blocker: "本地无原始封面图、无 image_url 映射（params §4.4）"

gate0:                                 # ★ 跨模态可对齐性预检（params §2.7），不过禁启 P2
  enabled: true
  probe: ridge_linear
  folds: 5
  recall_k: 10
  pass_ratio: 10.0                     # R@10 ≥ 10× 随机基线
  warn_ratio: 3.0
  shuffle_control_reps: 10
  pairs: [[visual, textual], [visual, behavioral], [textual, behavioral]]
  out: metrics/gate0_alignability.json

# ---- 上游 DST / CGA 参数模块（数值唯一权威见 sab_anc_params.md §1.1；CGAd 已弃用）----
dst:
  n_m: 3                               # 【定】visual + textual + behavioral（§2.5）
  codebook_groups: 6                   # 【定】3 共享 + 3 模态特定
  d: 256                               # 【锚】CGA 公共维度（原 CGAd，论文无此符号）
  manifold: unit_sphere                # 【锚】L2 归一化，eps 1e-8
  cgal_mode: full_eq1                  # 【定】full_eq1（主）/ volume_only（降级备选）
  anchor_rotation: 3                   # 【拍】3 组 D2A/A2D 轮换取平均
  tau_cgal: 0.07                       # 【拍】§2.3
  phi_fuse: mean                       # 【拍】mean 主；attention 仅消融
  phi_fuse_attn_renorm: true           # attention 版本输出 LayerNorm + L2
  rqn_shared_layers: 3                 # 【锚】
  codebook_size: 512                   # 【锚】
  proj_dim: [512, 256]                 # 【锚】
  ste: true                            # 【锚】直通估计
  commitment_sg: true                  # 【锚】sg[·] 只推 encoder
  beta: 1.0                            # 【拍】两端优先 {0.1, 10}（params §3.3）
  lambda_cgal: 1.0                     # 【拍】两端优先 {0.1, 10}

psgr:
  heads: 4                             # 【定】主；8 为容量消融
  head_dim: 64                         # 256 / heads
  q_proj: mlp2                         # 【拍】256→256→256, GELU + LayerNorm
  q_proj_shared: true                  # 【拍】全头共享；k/v 按头独立

vclub:
  q_hidden: 256
  q_layers: 2
  q_act: elu
  gaussian: true                       # 【锚】μ / log σ²
  logvar_clip: [-6, 6]
  mi_weight: 0.05                      # 【拍】网格 {0.01, 0.05, 0.1}
  ema_decay: 0.99
  detach_main: true

sampling:                              # 负采样全规格见 sab_anc_params.md §3
  pool_train: train_items_only
  pool_eval: full_catalog
  n_neg_train: 4                       # in-batch 之外另采
  n_neg_books: 4096
  min_neg_per_batch: 256
  popularity_alpha: 0.0                # 0 = uniform（主）；0.75 仅鲁棒性消融
  neg_seed_rule: "base*100003 + epoch*1009 + batch_idx"
  tau_align: 0.07

subset:                                # 5k **item** 子集协议见 sab_anc_params.md §4.3
  enabled: true
  unit: item                           # ★ v1.2 修正：按 item 抽，非按用户
  n_items: 5000
  strata_item_freq: [[1,3],[4,6],[7,11],[12,21],[22,null]]   # 实测四分位
  per_stratum: proportional            # 等比分配，每层 ≥200
  min_user_train_inter: 3              # 子集内重算（Baby 原始 min=3）
  min_user_keep: 20000
  min_inter_keep: 0.55
  ks_p_min: 0.05
  max_retries: 3
  out: data/splits/baby_5k_item.json   # sha256 → split_hash

policy:                                # 失败升级策略见 sab_anc_params.md §8
  forbid_test_tuning: true
  forbid_skip_nan_batch: true
  report_all_seeds: true
  escalation: [L1_impl, L2_tune, L3_scale, L4_stop]

downstream:
  d_model: 128
  tokens: {vis: 1, txt: 1, beh: 1, behavior_steps: 5}       # [VIS][TXT][BHV] + [BEH_1..5]
  aux_feat: [item_freq, repeat_flag, pos_ratio, seq_len]     # 4 维（params §4.5 v1.3）
  aux_stats:
    freq_table: train_only             # ★ 频次表只从 train.txt 计数，冻结 + sha256
    norm_consts: train_only            # max_freq/max_len 只在 train 算一次 → configs/aux_norm.json
    cold_item_value: 0.0               # 查表无此 item → log1p(0)=0（冷编码）
    audit_negative_check: true         # 全量重算必须与冻结表不一致，否则判泄漏
  heads: {rec: bilinear_softmax}                             # 单头（v1.2）
  act_head: {enabled: false, vocab: null}                    # D5；换 Amazon-2023 才可开
  negatives: all                                             # 18,357 全量 softmax，无需采样
  lambdas: {rec: 1.0, align: 0.1}                            # L_act 已删除
  lambda_grid: {align: [0.0, 0.1, 0.5]}
  ablations: [use_visual, use_txt, use_beh_modality, use_anc]
  ablation_matrix: [[V],[T],[B],[V,T],[V,B],[T,B],[V,T,B]]    # 7 行强制
  report_buckets: [warm_item, cold_item, cold_user]          # 三分开，主结论在 cold_item
  epochs: 100
  patience: 10

env:                                   # ★ 4 个变量必设（torch 段错误）
  KMP_DUPLICATE_LIB_OK: TRUE
  OMP_NUM_THREADS: "1"
  MKL_NUM_THREADS: "1"
  OMP_DYNAMIC: FALSE
```

---

## 8. 风险表（R0…R13）

| # | 风险 | 缓解 |
|---|---|---|
| R0 | SASRec 特征泄漏（切分不严） | 只用官方 train/valid/test 三件套，不自造切分；SASRec 内部 holdout 与下游 valid 物理分离；`audit_split.py` 核验"train 项未出现在 valid/test"；`split_hash` 随 ckpt 存并校验 |
| R1 | [ANC] 锚定失效重演（E14-bis） | 探针前置（analyze_anc 不过线不进指标阶段）；锚定只靠结构不与 decorrelation 损失共存 |
| R2 | Eq.1 体积数值不稳（det 爆/塌/负） | `slogdet` + jitter 1e-6；`Vol∈[0,1]` 断言；`gram_min_sv_ratio < 1e-4` 连续 20 step → 触发降级到 volume_only |
| R3 | **BLIP-2 无图可用** | 已拍板路径 A（预计算 CNN 4096）；登记 D1–D4；报告中不得声称"自产 BLIP-2 特征" |
| R4 | ~~N_m=3 但只有 2 路模态~~ **已解决** | 第三模态 = behavioral(SASRec item emb, d=512)。残余风险：SASRec 未收敛导致 behavioral 无信息 → 此时回退 `N_m=2` 并声明偏离，**不得**用 CAT/BRD 顶替 |
| R5 | ~~动作词表数据不支持~~ **已关闭** | 动作头关闭、词表删除（D5）；4 维辅助特征只作输入；`act_head.enabled=false` 必须落进 metrics JSON |
| R6 | C 盘剩 30GB | 数据/ckpt 一律放 D 盘 baseline/sab_anc 下 |
| R7 | 跨切分搬 baseline 数字 | 同切分重跑 LightGCN++；旧 P0-P2 数字标"协议不一致"不进同表（params §7） |
| R8 | MMSSL 特征需 GDrive（gdown），网络受限 | `fetch_mm_data.py` 已实现；失败则用 `prep_amazon_sports.py` 的合成特征仅做链路自测，不得用于结论 |
| R9 | 子集抽取偏离全集分布 | params §4.3 验收表（KS p>0.05、交互保留率≥55%）；不过则换 sub_seed 重抽，最多 3 次 |
| R10 | τ / β / λ 网格叠加导致组合爆炸 | 分级搜索：先固定 β=λ=1 扫 τ，再两端扫 β，最后两端扫 λ；不做全交叉 |
| **R11** | **behavioral 与标签同源 → 提升可能是捷径**（D8） | 7 行模态消融矩阵 + **主结论只落 cold-item**；`B` 行须 ≈ 已知 SASRec 水平（偏离则该行判实现 bug）；报告中显式承认 behavioral 是 ID 空间特征、非内容特征 |
| **R12** | **视觉/文本非同源 → 跨模态可对齐性弱于论文**（D1，最实质的偏离） | **闸门-0**（params §2.7）前置于 P2；`V–T` 失败即停并改附录 A；`V–B/T–B` 接近随机属预期，须在报告中说明"几何对齐主要发生在 V–T 对" |
| **R13** | **无 meta → 类别/品牌先验缺失**（D10） | `[CAT]/[BRD]` token 已删除；不得用 item id / 频次等伪造"内容特征"；内容侧只有 image+text 两路，须声明 |
| **R14** | **patience × eval_interval 语义错配**（params §6 v1.4） | patience 一律按**评估次数**计（等效 = patience × eval_interval = 40 epoch）；代码只维护 `eval_counter`，禁出现 epoch 版 patience 变量；误按 epoch 用 → 等效容忍减半、早停偏早 |
| **R15** | **辅助特征负向审计断言放宽后的防泄漏强度下降**（params §4.5 v1.4） | 两表一致 → `warn_review_required`（不静默放行）：`review_note` 人工签字后才进 P1；一致的高危成因是重算脚本读错文件，复核必须核对脚本实际读取的文件路径 |

---

## 9. 里程碑

| 阶段 | 内容 | 判据 |
|---|---|---|
| P0 | 特征拉取 + shape 回填 + 5k item 子集 + 切分审计 + **闸门-0** + baseline 同切分重跑 | `split_audit.json` 通过 + `gate0_alignability.json`（`V–T` 不 fail）+ LightGCN++ 子集基线（warm/cold 分开） |
| P1 | SASRec 重训 ×3 seed（hidden=512） | 内部 holdout R@20 达 E15-TF 量级（~0.038）；3 seed 方差可报 |
| P2 | CGA/RQN/PSGR item 特征链 + Eq.1 对齐（N_m=3，6 组码本） | `L_align` 下降、Gram 体积单调压降、码本 perplexity 落入 51–154、6 组均被使用 |
| P3 | 下游单头召回训练 + τ/β/λ 分级网格 | valid 曲线健康、探针过线、warm/cold 均无塌陷 |
| P4 | test 一次裁决 + 7 行模态消融 + `use_anc` + Φ_fuse + H=4/8 | ≥2 seed 可复现；**cold-item 提升可报** |

> ⚠️ P0 有三条硬门禁：①`split_audit.json` 不过 → 不进 P1；②`gate0_alignability.json` 缺失或 `V–T` fail → 不进 P2；③baseline 必须与 SAB-ANC 同 `split_hash`，否则不得同表。
> 闸门-0 刻意排在 P1 之前——它只依赖已有特征、几分钟可跑，若 `V–T` 失败则数据源要换，此时烧 3 seed SASRec 是纯浪费。

---

## 附录 A：Amazon-2023 路径（备选，非主线）

若后续决定恢复 BLIP-2 自产特征，走此路径：HF `McAuley-Lab/Amazon-Reviews-2023` 的 `raw_review/raw_meta_Movies_and_TV`（含 `unixReviewTime`、`images` URL）→ 可用**全局时间切分**（80/10/10 分位数）→ BLIP-2 Q-Former 抽 256 维 → 但**失去与 MMSSL 同协议可比性**，baseline 须全部重跑。此路径下 `docs/sab_anc_params.md` §6 的 BLIP-2 参数才生效。

> 环境提醒：跑任何脚本前 `export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE`（EXPERIMENT_HANDOFF §5.2）。
