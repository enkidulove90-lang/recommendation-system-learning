# SAB-ANC 设计文档 · SASRec 行为特征 × BLIP-2 内容特征的锚定下游模型

> 项目代号：**SAB-ANC**（**SASRec-Anchored Behavior/Content downstream**，命名可改，全局替换即可）
> 状态：设计基线 v1.0（2026-11-09）｜分支：`experiments`
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
| 现有数据时间戳 | **无**（`user item 1` 三元组，SELFRec 2014 版）→ 时间切分必须用 Amazon 2023 raw（含 `unixReviewTime`） |
| [ANC] / 动作词表 | 仓库无既有定义，本文首次明确化（§5、§6） |
| 本机硬件 | RTX 5060 Ti ×1 / 16GB / driver 610.88；CPU 28 线程；RAM 32GB；D 盘 1.6TB 可用 |
| SASRec 重训成本 | amazon-baby-mmssl（35598u/18357i/21.2 万交互）约 1-2h/500 epoch（E15-TF 实测早停 ep12-13） |
| BLIP-2 推理 | opt-2.7b（~8GB）16GB 显存可跑；flan-t5-xl 需 int8 |

---

## 2. 数据与三层时间切分

### 2.1 数据源

```
数据源: McAuley-Lab/Amazon-Reviews-2023 (HuggingFace)
  - raw_review_Movies_and_TV / raw_review_Books   (含 user_id, parent_asin, rating, timestamp, verified_purchase)
  - raw_meta_Movies_and_TV / raw_meta_Books       (含 title, images, categories, brand/store)
时间窗: 只取近 5 年 (2018-01-01 ~ 数据末日)，避免远古分布主导
```

### 2.2 三层切分（全局交互时间）

```
|<———————— SASRec 与下游共享的 train ————————>|<— valid —>|<— test —>|
t0 ────────────────────────── T1 ─────────────── T2 ──────── T_end
        80% 交互                       10%         10%
```

- **切分规则**：全部交互按 `unixReviewTime` 排序，按**交互条数累计分位数**切 80/10/10。边界日期 = 分位数落点日期，写死进 config（可复现），不用手拍日历日期。
- **SASRec 预训练**：只用 `[t0, T1)`，next-item 目标。其 early stopping 在 `[t0, T1)` 内部再切尾部 10% 作内部 valid；**禁止**触碰 `[T1, T_end)`。
- **下游**：train=`[t0, T1)`（与 SASRec 同段，SASRec 冻结出特征），valid=`[T1, T2)`（早停 + λ 网格），test=`[T2, T_end)`（只跑一次）。
- **冷启动分桶**：test 段首次出现的 user / item 单独报告，不计入主均值。

### 2.3 全局时间 vs 每用户时间（裁定记录）

| 方案 | 泄漏风险 | 裁定 |
|---|---|---|
| 全局时间切分 | SASRec 训练期不知道任何未来交互 → 无泄漏 | ✅ **主方案** |
| per-user leave-last-N | 用户 A 测试项可能晚于用户 B 训练项 → SASRec 已吸收测试期模式 → 特征污染 | ❌ 仅作文献可比的参考列 |

---

## 3. SASRec 重训约定

| 项 | 约定 |
|---|---|
| 入口 | 复用 `baseline/PRISM/SASRec.py` 骨干（去掉 PRISM 头），或独立脚本 `code/train_sasrec.py` |
| 目标 | next-item 交叉熵（负采样 1:1），hidden=64-128，2 层 Transformer，max_len=50 |
| Early stop | 内部 valid（train 尾部 10%），patience=10，**best-by-internal-valid** |
| 产物 | `ckpt/sasrec_best.pt`（权重+config+分位边界日期一并存） |
| 使用 | 冻结前向，输出 (a) 用户末层隐状态近 K=5 步 mean-pool → `h_beh`；(b) item embedding 矩阵（供召回头初始化/融合） |
| Git | `.ckpt` 一律 gitignore，只入库 config + 日志 + 指标 |

---

## 4. 目录规划（新增到 experiments 分支）

```
baseline/sab_anc/
├── code/
│   ├── download_amazon2023.py     # HF 数据下载（走代理/hf-mirror）
│   ├── build_time_split.py        # 分位数切分 → 边界日期写 config + splits/*.json
│   ├── train_sasrec.py            # SASRec 重训（§3 约定）
│   ├── extract_sasrec_feat.py     # 冻结前向 → beh_feat.npy / sasrec_item_emb.npy
│   ├── extract_blip2_feat.py      # 封面图 → Q-Former 32×256 → pooled 256d → blip2_feat.npy
│   ├── build_meta_tokens.py       # title/categories/brand → txt_feat.npy + 离散词表
│   ├── main_downstream.py         # 下游双头模型训练/评估入口
│   ├── model_downstream.py        # token 组织 + [ANC] + 双头
│   └── analyze_anc.py             # [ANC] 探针（对齐余弦/检索命中率，防 E14 复刻）
├── data/                          # gitignore: 交互 txt / *.npy 特征 / splits json 体积小可入库
├── ckpt/                          # gitignore
├── logs/                          # 入库（与 LightGCNpp/code/logs 惯例一致）
├── configs/
│   ├── sab_anc_movies.yaml        # ★ config 模板见 §7
│   └── sab_anc_books.yaml
├── .gitignore
└── README.md

docs/
├── sab_anc_design.md              # 本文档
└── sab_anc_phase1_report.md       # （未来）SASRec 重训 + 特征抽取报告
```

依赖增量：`transformers>=4.40`、`torch`(CUDA)、`datasets`(HF)、`sentence-transformers`、`Pillow`。其余沿用 `EXPERIMENT_HANDOFF.md`。

---

## 5. 下游模型定义

### 5.1 输入 token 组织（每候选物品一条样本）

```
[BEH]→(h_beh_1..h_beh_k, k=5, SASRec 近5步 mean-pool 投影) [ANC] [VIS_i] [TXT_i] [CAT_i] [BRD_i] → 预测 [ACT_*]
```

| token | 定义 | 维度/来源 |
|---|---|---|
| `[BEH]` 区段 | SASRec 末层隐状态近 K=5 步 mean-pool，经 1 层线性投影 | 冻结，仅投影层可学 |
| `[ANC]` | **可学习锚点 token（1 个）**，物理插在行为段与内容段之间 | 两侧信息必须经过它 → 结构性锚定 |
| `[VIS_i]` | BLIP-2 Q-Former 32×256 → MLP 压成 **1 个** token（省显存；book 规模下 32 token 会拖垮 batch） | blip2_feat.npy `[n_items,256]` |
| `[TXT_i]` | 标题 SBERT / BLIP-2 文本特征 | txt_feat.npy |
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
| 召回头 | `h_anc` ⊕ 候选融合表征 `v_i`（VIS+TXT+CAT+BRD 拼接过 MLP，可初始化自 SASRec item emb） | 双线性 `h_ancᵀW v_i` + 全 item softmax（Movies&TV 万级 item 直接全量；Books 9 万级采样 4096 负例） | Recall@10/20、NDCG@10/20 |
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
dataset: amazon2023_movies_tv          # amazon2023_books 另一份
data:
  hf_dataset: McAuley-Lab/Amazon-Reviews-2023
  review_split: raw_review_Movies_and_TV
  meta_split: raw_meta_Movies_and_TV
  time_window: {start: "2018-01-01", end: null}   # null=数据末日
  net: {proxy: "http://127.0.0.1:7897", hf_mirror: "https://hf-mirror.com", use_mirror_on_fail: true}

split:                                 # ★ 全局交互时间切分（唯一权威切分）
  mode: global_quantile                # global_quantile | (禁用: per_user_loo)
  quantiles: [0.80, 0.90, 1.00]        # train/valid/test
  boundary_dates:                      # 由 build_time_split.py 首跑后回填并冻结
    t1: null                           # 例 "2022-06-14"
    t2: null
  sasrec_internal_valid: 0.10         # train 尾部 10%，SASRec 早停专用

sasrec:
  hidden: 128
  layers: 2
  max_len: 50
  epochs: 200
  patience: 10
  seeds: [42, 2025, 2026]
  ckpt: baseline/sab_anc/ckpt/sasrec_best.pt
  freeze: true                         # ★ 下游阶段强制冻结

feat:
  beh_k: 5                             # 近 K 步 mean-pool
  blip2:
    model: "Salesforce/blip2-opt-2.7b" # 16GB 显存可跑；xl 需 int8
    qformer_tokens: 32
    pooled_dim: 256                    # 压缩后维度
  txt_model: "sentence-transformers/all-MiniLM-L6-v2"

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

## 8. 风险表（R0…）

| # | 风险 | 缓解 |
|---|---|---|
| R0 | SASRec 特征泄漏（切分不严） | 单一权威切分文件；SASRec 内部 valid 与下游 valid 物理分离；审计脚本核验边界日期 |
| R1 | [ANC] 锚定失效重演（E14-bis） | 探针前置（analyze_anc 不过线不进指标阶段）；锚定只靠结构不与 decorrelation 损失共存 |
| R2 | Books 数据全量 softmax OOM | `negatives: sampled_4096` |
| R3 | BLIP-2 显存吃紧 | opt-2.7b + fp16；不行退 blip2-opt-6.2b 的 Q-Former 单独跑或 int8 |
| R4 | HF 下载被墙 | proxy + hf-mirror 双通道（config 已内置） |
| R5 | 动作词表被质疑数据不支持 | 词表只由 rating+verified 构成（§5.3 已锁死） |
| R6 | C 盘剩 30GB | 数据/ckpt 一律放 D 盘 baseline/sab_anc 下 |
| R7 | raw_meta 字段缺失率（brand/store 常缺） | 缺失 → [UNK]；统计缺失率写入报告 |

---

## 9. 里程碑

| 阶段 | 内容 | 判据 |
|---|---|---|
| P0 | 数据下载 + 时间切分 + 规模统计（复用问卷口径） | splits json + 边界日期冻结 |
| P1 | SASRec 重训 ×3 seed | 内部 valid R@20 达到 E15-TF 水平（~0.038）量级 |
| P2 | 特征抽取（SASRec + BLIP-2 + 文本） | 特征文件齐全 + 抽查余弦合理性 |
| P3 | 下游双头训练 + λ 网格 | valid 曲线健康、探针过线 |
| P4 | test 一次裁决 + 消融（use_anc 为主消融） | 双 seed 以上可复现 |

> 环境提醒：跑任何脚本前 `export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE`（EXPERIMENT_HANDOFF §5.2）。
