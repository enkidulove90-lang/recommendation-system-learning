# SAB-ANC 设计文档 · SASRec 行为特征 × BLIP-2 内容特征的锚定下游模型

> 项目代号：**SAB-ANC**（**SASRec-Anchored Behavior/Content downstream**，命名可改，全局替换即可）
> 状态：设计基线 v1.1（2026-11-10）｜分支：`experiments`
> **参数数值以 `docs/sab_anc_params.md`（Decision Record v1.1）为唯一权威来源**，本文与之处突时以参数决议文件为准。
> v1.1 变更：数据集切到 **MMSSL Amazon-Baby + 5k item 子集**（v3 裁决）；切分改为 **per-user chronological holdout**（数据无时间戳）；`CGAd` 弃用改 `d=256`；PSGR 输入按论文修正为残差 + `z_j` probe；BLIP-2 特征存在数据阻塞（见 params §4.4）。
> 前置阅读：`docs/EXPERIMENT_HANDOFF.md`（环境与 4 个 OMP 变量）、`docs/e14bis_mechanism_diagnosis.md`（锚定机制教训来源）、`docs/e15_tf_report.md`（SASRec 训练成本实测）

---

## 0. 一句话定位

用**冻结的 SASRec** 从行为序列提取用户表征，用 **BLIP-2** 从封面图提取内容表征，通过结构性锚点 token **[ANC]** 把两侧信息汇聚，双头（召回头 + 动作头）联合训练一个轻量下游打分模型。

三条设计铁律（均有前车之鉴）：

| 铁律 | 来源教训 |
|---|---|
| SASRec 只许看 train 时间段，valid/test 对其完全不可见 | 特征提取器泄漏 = 下游指标虚高 |
| 时间切分用**全局交互时间**，不用 per-user leave-last-N | per-user 切分会让 SASRec 见过测试期行为模式 |
| 锚定靠**结构**（[ANC] 插在行为段与内容段之间），不靠辅助损失 | E14-bis：cos 锚定 λ 扫到 10 仍被 L_syn 压制（cos 卡死 0.27） |

---

## 1. 现状核查（2026-11-09，本地实测）

| 项 | 结论 |
|---|---|
| SASRec checkpoint | **全分支无任何 `.ckpt/.pth`**（E15-TF 训练完权重即弃，只留 logs）→ 必须重训 |
| 数据基准 | **MMSSL Amazon-Baby**（v3 裁决）：35,598 u / 18,357 i / train 190,930 项（avg 5.4）/ valid 37,899 / test 67,508。**无时间戳**，为 per-user 序列三件套 |
| 时间戳 | **无** → 全局时间切分不可用，改 per-user chronological holdout（§2.2 修正） |
| 多模态特征 | 仅 MMSSL 预计算 `image_feat`(**CNN** 4096) + `text_feat`(SBERT 1024)；**无原始封面图、无 image_url 映射** → BLIP-2 无法自产（params §4.4） |
| [ANC] / 动作词表 | 仓库无既有定义，本文首次明确化（§5、§6） |
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
| 目标 | next-item 交叉熵（负采样 1:1），hidden=64-128，2 层 Transformer，max_len=50 |
| Early stop | 内部 holdout（train 尾部 10%），patience=10，**best-by-internal-valid** |
| 产物 | `ckpt/sasrec_best.pt`（权重 + config + `split_hash` 一并存） |
| 使用 | 冻结前向，输出 (a) 用户末层隐状态近 K=5 步 mean-pool → `h_beh`；(b) item embedding 矩阵（供召回头初始化/融合） |
| Git | `.ckpt` 一律 gitignore，只入库 config + 日志 + 指标 |

---

## 4. 目录规划（新增到 experiments 分支）

```
baseline/sab_anc/
├── code/
│   ├── fetch_mm_feats.py          # MMSSL 预计算特征拉取（复用 LightGCNpp/code/fetch_mm_data.py）
│   ├── build_item_subset.py       # 5k item 分层抽样 → data/splits/baby_5k_item.json + sha256
│   ├── audit_split.py             # 切分审计（无泄漏/子集覆盖/hash 一致），P0 必交付
│   ├── train_sasrec.py            # SASRec 重训（§3 约定）
│   ├── extract_sasrec_feat.py     # 冻结前向 → beh_feat.npy / sasrec_item_emb.npy
│   ├── cga_align.py               # CGA 投影 + Eq.1 对称对比（Vol=√det(G)，τ=0.07，3 组轮换）
│   ├── rqn_psgr.py                # RQN 共享量化(N_sh=3,K=512) + PSGR(残差 ← z_j probe)
│   ├── extract_blip2_feat.py      # 路径B/C 专用（当前 blocked，见 params §4.4）
│   ├── run_baseline_lightgcnpp.sh # 同切分重跑 baseline（params §7 强制）
│   ├── main_downstream.py         # 下游双头训练/评估入口
│   ├── model_downstream.py        # token 组织 + [ANC] + 双头
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
多模态原始特征 (image 4096 / text 1024)
   └─CGA 投影→ z_j ∈ R^d (d=256, 单位超球面)
        └─Eq.1 对称对比对齐：L_align = (L_D2A + L_A2D)/2，Vol=√det(G)，Vol 入 e^{-Vol/τ} softmax，τ=0.07
             └─RQN 共享量化 N_sh=3, K=512, 512→256
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
[BEH]→(h_beh_1..h_beh_k, k=5, SASRec 近5步 mean-pool 投影) [ANC] [VIS_i] [TXT_i] [CAT_i] [BRD_i] → 预测 [ACT_*]
```

| token | 定义 | 维度/来源 |
|---|---|---|
| `[BEH]` 区段 | SASRec 末层隐状态近 K=5 步 mean-pool，经 1 层线性投影 | 冻结，仅投影层可学 |
| `[ANC]` | **可学习锚点 token（1 个）**，物理插在行为段与内容段之间 | 两侧信息必须经过它 → 结构性锚定 |
| `[VIS_i]` | BLIP-2 Q-Former 32×256 → MLP 压成 **1 个** token（省显存；book 规模下 32 token 会拖垮 batch） | blip2_feat.npy `[n_items,256]` |
| `[TXT_i]` | 标题 SBERT（`all-MiniLM-L6-v2`，**384 维**） | txt_feat.npy `[n_items,384]` |
| `[CAT_i]` | 类别离散 token（Top-N 频次 + `[UNK]`），可学习 embedding | 词表随 config |
| `[BRD_i]` | 品牌/store 离散 token，同上 | 词表随 config |

### 5.2 [ANC] 的双重作用

1. **信息汇聚**：`h_anc` = [ANC] 位置的输出隐状态，是两个预测头的唯一源泉。
2. **对齐锚点**：`L_align` 把 `h_anc` 拉向正样本内容表征、推远 batch 内负样本（InfoNCE）。与 E14-bis 的区别：不与任何几何 decorrelation 损失共存，锚定即结构。

### 5.3 动作词表（按 Amazon 2023 实际字段收敛，~12 个）

```
[ACT_R1] ~ [ACT_R5]     # rating 1..5 星桶
[ACT_NOVER]             # 无文字评分（评分缺失但有交互）
[ACT_VERIFY] / [ACT_UNVERIFIED]  # verified_purchase 真伪
```

⚠️ 数据里没有点击/加购/收藏——动作词表**只允许**由 rating + verified_purchase 构成，方案书/论文不得写全行为词表（审稿人一查数据即穿）。

### 5.4 预测头（双头）

| 头 | 输入 | 结构 | 用途 |
|---|---|---|---|
| 召回头 | `h_anc` ⊕ 候选融合表征 `v_i`（VIS+TXT+CAT+BRD 拼接过 MLP，可初始化自 SASRec item emb） | 双线性 `h_ancᵀW v_i` + 全 item softmax（Baby 18,357 item 直接全量，无需采样） | Recall@10/20、NDCG@10/20 |
| 动作头 | `[h_anc; v_i]` | 2 层 MLP → 动作词表 softmax | 动作分类 Acc/Macro-F1 |

### 5.5 监督损失

```
L = L_rec        # 召回头 CE/InfoNCE（1 正 + 全量或采样负例）
  + λ₁·L_act     # 动作头 CE，λ₁≈0.3（valid 网格 0.1/0.3/1.0）
  + λ₂·L_align   # [ANC]-内容 InfoNCE（batch 内负采样），λ₂≈0.1（0/0.1/0.5）
```

- SASRec 冻结 → 无需对其正则；下游模型小（~10M 参数），单卡 epoch 分钟级。
- 消融开关全部做成 config 布尔：`use_beh` / `use_visual` / `use_txt` / `use_anc`（`use_anc=false` 时 [ANC] 退化为普通拼接池化，作为核心消融）。

---

## 6. 评估协议

| 段 | 指标 | 规则 |
|---|---|---|
| valid | R@20 / NDCG@20（下游早停+λ 网格） | 多 seed {42, 2025, 2026}，报均值±方差（沿用 E15 惯例） |
| test | R@10/20, NDCG@10/20 + 动作 Acc/Macro-F1 + 冷启动分桶 | 只跑一次最终 config；禁止在 test 上调参 |
| 探针 | `analyze_anc.py`：h_anc↔内容余弦、检索 R@K | 防止重演 E14（探针 R²=0.147 平台）——探针不过线则先修锚定再谈指标 |

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
  feat:                                # MMSSL 预计算（BLIP-2 阻塞见 params §4.4）
    image: image_feat.npy              # [18357, 4096] CNN
    text:  text_feat.npy               # [18357, 1024] SBERT
  net: {proxy: "http://127.0.0.1:7897", gdrive_via: fetch_mm_data.py}

split:                                 # ★ per-user chronological holdout（唯一权威切分）
  mode: per_user_prefix_holdout         # 官方三件套，不自造
  split_file: data/splits/baby_5k_item.json
  split_hash: null                      # 由抽子集脚本写入 sha256，加载 ckpt 时校验
  cold_start_bucket: true
  sasrec_internal_holdout: 0.10         # train 尾部 10%，SASRec 早停专用

sasrec:
  hidden: 128
  layers: 2
  max_len: 50
  epochs: 300                          # Baby 规模下调（params §6）
  patience: 10
  seeds: [42, 2025, 2026]
  ckpt: baseline/sab_anc/ckpt/sasrec_best.pt
  freeze: true                         # ★ 下游阶段强制冻结

feat:
  beh_k: 5                             # 近 K 步 mean-pool
  source: mmssl_precomputed            # 【默认路径A】mmssl_precomputed | blip2_selfbuilt
  # ---- 路径 A（默认）：直接用 MMSSL 预计算，零成本，先跑通链路 ----
  image_dim: 4096                      # CNN（非 CLIP！见 params §6/§1）
  text_dim: 1024                       # SBERT（模型名未留档）
  # ---- 路径 B/C（另立里程碑，不与主实验混跑）----
  blip2:
    enabled: false
    model: "Salesforce/blip2-opt-2.7b"
    qformer_tokens: 32
    pooled_dim: 256
    blocker: "本地无原始封面图、无 image_url 映射（params §4.4）"
  txt_model: "sentence-transformers/all-MiniLM-L6-v2"
  txt_dim: 384                         # ★ 已核实：all-MiniLM-L6-v2 = 384 维（非 1024）
                                        #   4096 维是 MMSSL 的 CNN 特征，与 CLIP 无关，见 sab_anc_params.md §6

# ---- 上游 DST / CGA 参数模块（数值唯一权威见 sab_anc_params.md §1.1；CGAd 已弃用）----
dst:
  d: 256                               # 【锚】CGA 公共维度（原 CGAd，论文无此符号）
  manifold: unit_sphere                # 【锚】L2 归一化，eps 1e-8
  cgal_mode: full_eq1                  # 【定】full_eq1（主）/ volume_only（降级备选）
  phi_fuse: mean                       # 【拍】mean 主；attention 仅消融
  phi_fuse_attn_renorm: true           # attention 版本输出 LayerNorm + L2
  rqn_shared_layers: 3                 # 【锚】
  codebook_size: 512                   # 【锚】
  proj_dim: [512, 256]                 # 【锚】
  ste: true                            # 【锚】直通估计
  commitment_sg: true                  # 【锚】sg[·] 只推 encoder
  beta: 1.0                            # 【拍】网格 {0.1, 1, 10}
  lambda_cgal: 1.0                     # 【拍】网格 {0.1, 1, 10}

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

subset:                                # 5k 子集协议见 sab_anc_params.md §5
  enabled: true
  n_users: 5000
  min_train_inter: 5
  strata: [[5,6],[7,10],[11,20],[21,50],[51,null]]
  per_stratum: 1000
  min_item_coverage: 0.60

policy:                                # 失败升级策略见 sab_anc_params.md §8
  forbid_test_tuning: true
  forbid_skip_nan_batch: true
  report_all_seeds: true
  escalation: [L1_impl, L2_tune, L3_scale, L4_stop]

downstream:
  d_model: 128
  vis_tokens: 1                        # 32→1 压缩
  cat_topn: 200                        # 类别词表 Top-N + [UNK]
  brand_topn: 500
  action_vocab: [ACT_R1, ACT_R2, ACT_R3, ACT_R4, ACT_R5, ACT_NOVER, ACT_VERIFY, ACT_UNVERIFIED]
  heads: {rec: bilinear_softmax, act: mlp2}
  negatives: all                       # 全量 softmax；books 数据改 sampled_4096
  lambdas: {rec: 1.0, act: 0.3, align: 0.1}
  lambda_grid: {act: [0.1, 0.3, 1.0], align: [0.0, 0.1, 0.5]}
  ablations: [use_beh, use_visual, use_txt, use_anc]   # 全布尔开关
  epochs: 100
  patience: 10

env:                                   # ★ 4 个变量必设（torch 段错误）
  KMP_DUPLICATE_LIB_OK: TRUE
  OMP_NUM_THREADS: "1"
  MKL_NUM_THREADS: "1"
  OMP_DYNAMIC: FALSE
```

---

## 8. 风险表（R0…R10）

| # | 风险 | 缓解 |
|---|---|---|
| R0 | SASRec 特征泄漏（切分不严） | 只用官方 train/valid/test 三件套，不自造切分；SASRec 内部 holdout 与下游 valid 物理分离；`audit_split.py` 核验"train 项未出现在 valid/test"；`split_hash` 随 ckpt 存并校验 |
| R1 | [ANC] 锚定失效重演（E14-bis） | 探针前置（analyze_anc 不过线不进指标阶段）；锚定只靠结构不与 decorrelation 损失共存 |
| R2 | Eq.1 体积数值不稳（det 爆/塌/负） | `slogdet` + jitter 1e-6；`Vol∈[0,1]` 断言；`gram_min_sv_ratio < 1e-4` 连续 20 step → 触发降级到 volume_only |
| R3 | **BLIP-2 无图可用**（本地无封面图/无 image_url） | 默认路径 A（用 MMSSL 预计算 CNN 4096）；B/C 另立里程碑；报告中不得声称"自产 BLIP-2 特征" |
| R4 | **N_m=3 但本地只有 2 路模态** | 优先补第三模态（类别/品牌编码）；补不上则 N_m=2 并在报告显式声明偏离论文 |
| R5 | 动作词表被质疑数据不支持 | Baby **无 rating / verified 字段** → 动作头无法按 Amazon-2023 口径构造；须改为可得的隐式信号或砍掉动作头（§5.3 待复核） |
| R6 | C 盘剩 30GB | 数据/ckpt 一律放 D 盘 baseline/sab_anc 下 |
| R7 | 跨切分搬 baseline 数字 | 同切分重跑 LightGCN++；旧 P0-P2 数字标"协议不一致"不进同表（params §7） |
| R8 | MMSSL 特征需 GDrive（gdown），网络受限 | `fetch_mm_data.py` 已实现；失败则用 `prep_amazon_sports.py` 的合成特征仅做链路自测，不得用于结论 |
| R9 | 子集抽取偏离全集分布 | params §4.3 验收表（KS p>0.05、交互保留率≥55%）；不过则换 sub_seed 重抽，最多 3 次 |
| R10 | τ / β / λ 三组网格叠加导致组合爆炸 | 分级搜索：先固定 β=λ=1 扫 τ，再扫 β，最后扫 λ；不做全交叉 |

---

## 9. 里程碑

| 阶段 | 内容 | 判据 |
|---|---|---|
| P0 | 特征拉取 + 5k item 子集 + 切分审计 + baseline 同切分重跑 | `baby_5k_item.json` + `split_audit.json` 通过 + LightGCN++ 子集基线数字 |
| P1 | SASRec 重训 ×3 seed | 内部 holdout R@20 达到 E15-TF 量级（~0.038 起）；3 seed 方差可报 |
| P2 | CGA/RQN/PSGR item 特征链 + Eq.1 对齐 | `L_align` 下降、Gram 体积单调压降、码本 perplexity 落入 51–154 |
| P3 | 下游双头训练 + τ/β/λ 分级网格 | valid 曲线健康、探针过线 |
| P4 | test 一次裁决 + 消融（use_anc 核心、Φ_fuse mean/attn、H=4/8） | ≥2 seed 可复现 |

> ⚠️ P0 有两条硬门禁：①`split_audit.json` 不过 → 不进 P1；②BLIP-2 路径未拍板 → 只跑路径 A，P2 的视觉特征标注"MMSSL CNN 4096（非 BLIP-2）"。

---

## 附录 A：Amazon-2023 路径（备选，非主线）

若后续决定恢复 BLIP-2 自产特征，走此路径：HF `McAuley-Lab/Amazon-Reviews-2023` 的 `raw_review/raw_meta_Movies_and_TV`（含 `unixReviewTime`、`images` URL）→ 可用**全局时间切分**（80/10/10 分位数）→ BLIP-2 Q-Former 抽 256 维 → 但**失去与 MMSSL 同协议可比性**，baseline 须全部重跑。此路径下 `docs/sab_anc_params.md` §6 的 BLIP-2 参数才生效。

> 环境提醒：跑任何脚本前 `export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE`（EXPERIMENT_HANDOFF §5.2）。
