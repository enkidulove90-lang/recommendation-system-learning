# E15 · 用 PRISM 原码在 `amazon-baby-mmssl` 复现论文增益

> 目的：在 E14-bis 判决「PRISM syn 专家机制缺陷（真值不可锚定、MI 不可验证）」之后，按用户拍板，
> **先用 `baseline/PRISM/` 原码（不是我们自己的 `prism_moe.py` 骨架）在 `amazon-baby-mmssl` 上跑一遍**，
> 确认论文声称的「plug-and-play 增益」在我们数据上可复现，避免 `prism_moe.py` 的重建偏差混进来。
>
> 关联：`docs/e14bis_mechanism_diagnosis.md`（FAIL，机制缺陷）、`docs/prism_gate_a_report.md`（A 闸门：真实数据 Synergy 不可判）。

---

## 0. 一句话结论（设计阶段）

本实验**不验证「可解释协同分解」**（E14-bis 已判死），只验证论文更弱的、也是论文唯一实证的主张：
**「把 PRISM 模块（4 专家 + 3 交互损失 + AFL）叠到多模态序列推荐骨架上，下游 R@20/NDCG@20 会涨」**。
处理组 = PRISM 全损失（λ=0.1），对照组 = 同架构但 λ=0（多模态基线，无交互正则），可选第三组 = 纯 id SASRec（vanilla）。
若 `PRISM(full) − PRISM(λ=0)` 在 baby 上为正且达阈值 → 论文增益在我方数据上复现，E15 通过，可进入集成落地；
若为 0 或负 → 在我方特征上 PRISM 的 synergy 模块也没带来增益（与 E14-bis 指向一致），需重新评估集成价值。

---

## 1. 数据契约差距（已核实，决定为何不能直接 `python main.py`）

### 1.1 PRISM 原码期望的输入
- `data/{name}/reviews_{name}.txt`：**单文件**，每行 `user_id 物品...`，物品 **1-based**（0=padding，max_item+1=mask）。
  `get_user_seqs` 内部做 leave-one-out 切分（train=[:-3], valid=[-2], test=[-1]）。
- `data/{name}/image_features_{name}.pt` / `text_features_{name}.pt`：`torch.Tensor`，shape `[max_item, feat_dim]`，
  按 `weight.data[1:-1] = features` 填进 embedding 表 → **特征行 i 对应物品 i+1**。
- `pretrain_emb_dim`（默认 512）：图像与文本特征**必须同维**（CLIP 512）。原码 `fc_mean_image`/`fc_mean_text` 共用一个 `pretrain_emb_dim`。

### 1.2 我方 `amazon-baby-mmssl` 实际格式
| 项 | 我方 | PRISM 期望 | 差距 |
|---|---|---|---|
| 序列文件 | `train.txt`/`valid.txt`/`test.txt` 三文件 | 单 `reviews_*.txt` | 需合并 |
| 物品索引 | **0-based**，0 是真实物品（序列中出现 5 次），范围 0..18356 | 1-based，0=pad | 全体 +1 偏移 |
| 物品数 | 18357（`max_item`） | — | — |
| 用户数 | 106794（三文件合计行数） | — | — |
| 图像特征 | `image_feat.npy` **(18357, 4096)** | `.pt` [18357, 512] | **维度 4096≠512，且类型 .npy** |
| 文本特征 | `text_feat.npy` **(18357, 384)** | `.pt` [18357, 512] | **维度 384≠512，异构于图像，且类型 .npy** |

### 1.3 关键错配
1. **特征维度**：图像 4096、文本 384 —— 既不是论文的 CLIP 512，也**彼此不等维**。PRISM 原码假设同维，无法直接吃。
2. **特征类型**：`.npy`（numpy）vs `.pt`（torch）。
3. **序列索引**：0-based（0 当真实物品）vs 1-based（0 当 pad）。
4. **序列拆分**：三文件 vs 单文件内部切分。

**索引对齐已验证**：`image_feat.npy` 行 `i` 对应物品 `i`（0-based），物品 0 也有特征行 0。
→ 转换只需 **txt 全体物品 +1 偏移**，特征 `.pt` **原样拷贝**（行 i → PRISM 物品 i+1），无需重映射特征。

---

## 2. 原码本身的可跑性问题（已核实，必须补丁）

| # | 位置 | 问题 | 补丁（最小、机械） |
|---|---|---|---|
| P1 | `SASRec.py` `__init__` | `image_mean_embeddings`/`image_cov_embeddings`/`text_mean_embeddings`/`text_cov_embeddings` 四个 Embedding 表**根本没定义**（原 clone 缺片段），`replace_embedding` 必 `AttributeError` | 补 4 个 `nn.Embedding(item_size, per_modality_dim, padding_idx=0)` |
| P2 | `SASRec.py` `fc_mean_image`/`fc_mean_text` | 共用 `pretrain_emb_dim=512`，与 4096/384 不符 | 拆成 `image_emb_dim`/`text_emb_dim`，各自 Linear |
| P3 | `PRISM.py` `Interaction_Expert_Layer.__init__` | `lambda_uni_v/lambda_uni_t/lambda_syn/lambda_red` **硬编码 0.1**，`main.py` 的 `--lambda_*` 参数无效 | 改读 `args`（破除硬编码，使 ablation 可做） |
| P4 | `main.py:232` `test_real_memory_usage` | 调 `torch.cuda.*`，CPU 环境崩溃 | 用 `if torch.cuda.is_available():` 守卫 |
| P5 | `trainers.py:118` `load()` | `torch.load(..., map_location='cuda:0')` 硬编码 | 改 `map_location='cpu'` when no cuda |

> **PRISM 机制（Interaction Expert Layer、uniqueness/synergy/redundancy 三损失、Adaptive Fusion Layer）保持字节级原样。**
> 我们自己的 `prism_moe.py` 骨架**完全不使用**，重建偏差被排除。

### 补丁为何不算「改论文方法」
- P1/P2 是让原码能加载**我方既有特征**的管道（维度对齐），不改任何前向/损失逻辑。
- P3 只是把已被硬编码的 0.1 变成可由命令行控制（默认值仍是 0.1，处理组数值与论文一致）。
- P4/P5 是 CPU 环境兼容（论文在 GPU 跑，原码无 cpu 守卫）。

---

## 3. 实验协议

### 3.1 模型
- 骨架：**SASRec**（论文三骨架中最轻、最快，论文报告其增益；STOSA/InDiRec 留作后续）。
- 原码路径：`baseline/PRISM/main.py` + `SASRec.py` + `PRISM.py`（仅上述 P1–P5 补丁）。

### 3.2 三组（同一数据、同一特征）
| 组 | 命令差异 | 含义 |
|---|---|---|
| **T（treatment）** | `--lambda_uni 0.1 --lambda_syn 0.1 --lambda_red 0.1` | PRISM 全损失（=论文默认） |
| **A（ablation）** | `--lambda_uni 0 --lambda_syn 0 --lambda_red 0` | 同架构多模态，无交互正则（PRISM 机制贡献的净对照） |
| **V（vanilla，可选）** | `--disable_mm`（跳过多模态+交互注入） | 纯 id SASRec，测多模态整体增益 |

### 3.3 超参（沿用论文 main.py 默认，仅关 GPU）
`--model_name SASRec --hidden_size 256 --max_seq_length 100 --num_hidden_layers 1 --num_attention_heads 4`
`--batch_size 256 --lr 0.001 --epochs 500 --patience 10 --no_cuda --seed {S}`
`--image_emb_dim 4096 --text_emb_dim 384 --pretrain_emb_dim 4096`
`--ckp 10`（如需预训练阶段，本实验不预训练，直接端到端）

### 3.4 指标
`SASRecTrainer` 的 `get_full_sort_score` 输出 **Recall@10/20, NDCG@10/20**（full ranking over all items）。
主判据：**R@20、NDCG@20**（3 seed 均值 ± std）。

### 3.5 决策阈值
- **增益复现（E15 PASS）**：`R@20(T) − R@20(A) ≥ +1.0% 相对提升`（且与论文方向一致为正），
  或 `NDCG@20(T) > NDCG@20(A)`。若同时 `R@20(T) > R@20(V)` 更佳（证明多模态+PRISM 双增益）。
- **增益未复现（E15 存疑）**：`R@20(T) ≤ R@20(A)`（在误差内）→ PRISM synergy 模块在我方特征上无正向贡献，
  与 E14-bis「syn 专家无用」一致，集成价值需重议。
- 注意：我方特征是异构非 CLIP、Baby 不在论文 4 数据集（Home/Beauty/Sports/Yelp）内，
  **不与论文绝对数值直接比较**，只比较「相对增益方向/量级」。

---

## 4. 运行环境铁律（沿用 E14-bis）
- **torch 在 Git Bash 下 segfault（EXIT=139）** → 所有 torch 脚本（转换 + 训练）走 **PowerShell**。
- 本机 `C:\Program Files\Python311\python.exe` 装有 numpy/scipy/torch(cpu)，用于本次实验。
- CPU 训练时长预估：baby 106k 用户 × 18357 物品，hidden 256，~30–90s/epoch，early-stop(patience10) 通常 30–80 epoch → 单组 ~30–90 min；T+A 两组 + 可选 V，合计 1–3 h。后台运行。

---

## 5. 产物
- `baseline/PRISM/e15_convert.py` — 数据转换（txt→单文件 + npy→pt）。
- `baseline/PRISM/data/amazon-baby-mmssl/reviews_amazon-baby-mmssl.txt` + `image_features_*.pt` + `text_features_*.pt` — 转换后数据。
- `baseline/PRISM/run_e15.ps1` — 多组多 seed 训练启动器（PowerShell）。
- `baseline/PRISM/outputs/amazon-baby-mmssl/*` — 每组日志（含 R@20/NDCG@20）。
- `baseline/PRISM/logs/e15_report.md` — 增益判定报告。

---

## 6. 风险与对策
1. **特征维度≠CLIP**：已用 P2 拆维解决；但异构编码器（图像 ViT-类 4096 / 文本 384）可能影响 PRISM 专家对齐质量——
   若 T 与 A 几乎无差，属「特征异构导致交互信号弱」，仍是有价值的负结果，不掩盖。
2. **原码缺失 embedding（P1）**：非我们引入，是论文 clone 缺口；补的是机械定义，不改变机制。
3. **CPU 慢**：后台跑，early-stop 控时长；必要时降 `max_seq_length` 或 `batch_size` 加速预验。
4. **Baby 不在论文数据集**：结论限定为「我方数据上的相对增益」，不主张对标论文绝对指标。
