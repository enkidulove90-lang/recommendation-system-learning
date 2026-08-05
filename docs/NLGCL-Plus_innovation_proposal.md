# 基于 NLGCL+ 的可落地创新提案：ASW-NLGCL（稀疏低秩·符号安全·置信度门控的自适应样本加权）

> **生成时间**：2026-08-05
> **上游依据**：
> - 论文全文：`data/parsed/3806231_NLGCL-Plus/3806231_NLGCL-Plus.md`（MinerU v4 解析，106,776 字符）
> - 论文摘要：`data/summaries/3806231_NLGCL-Plus_邻接层自然对比学习与自适应样本加权_summary.md`
> - 论文↔代码交叉分析：`docs/NLGCL-Plus_cross_analysis.md`（差异 D1–D11）
> - 落地载体：`baseline/LightGCNpp/`（本项目 P1 已接入 NLGCL-H）
> **本文档定位**：Step 5 交付物 —— 模块设计 / 算法伪代码 / 可行性说明

---

## 0. TL;DR

| 项 | 内容 |
| --- | --- |
| **模块名** | **ASW-NLGCL**（Adaptive Sample Weighting for Neighbour-Layer GCL），文件 `code/asw_module.py` |
| **一句话** | 把 NLGCL+ 论文标题里承诺、但官方开源代码**完全没有实现**的 ASW（差异 D1）真正做出来，并顺手修掉论文自身留下的 3 个硬伤：显存不可扩展、权重可为负、单正样本退化 |
| **增量点** | ① 低秩恒等式免物化 → 论文没算的 2.61 GB 权重矩阵开销可降到 55 MB；② 均值保持 + 符号安全归一化 → 消除「W 偷改有效温度」与「W<0 语义翻转」；③ **置信度门控 ASW（ASW-G）** → 复用本项目 idea2 的 `conf_vec`，噪声模态自动退化为标准 NLGCL，论文无此机制 |
| **改动量** | 新增 1 文件（~180 行）+ 修改 5 处已有文件（合计 ~60 行），**推理路径零改动** |
| **可退化性** | `--asw 0` 逐字节等价于当前 P1 NLGCL-H；`--asw_beta 0` 数学上等价于无加权。**任何时候都能安全回退** |
| **主战场** | `amazon-baby-mmssl`（实测为真实 MMSSL 特征）；`amazon-sports` 作**安慰剂对照**（实测其 `image_feat.npy` 是高斯合成噪声） |

---

## 1. 出发点：从 11 条差异中挑出 3 个真正可攻击的缺口

`docs/NLGCL-Plus_cross_analysis.md` 列出的 D1–D11 里，多数是工程口径差（如 D3 转置轴、D10 命名混淆），不值得投入。真正有研究价值、且**本项目具备落地条件**的是下面 3 条，且它们互相咬合：

| 缺口 | 论文说法 | 官方代码实况 | 本项目机会 |
| --- | --- | --- | --- |
| **G1 = D1** | 标题级卖点：用多模态原始特征算相似度矩阵 $\mathcal{W}$ 给每个对比样本加权（Eq.10–11） | 全仓库 grep 无任何 $\mathcal{W}$ 预计算；`*_plus.py` 一律标准无权 InfoNCE。`cohesion_plus.py::adaptive_optimization` 是 COHESION 自带的模态融合权重，**不是 ASW** | 本项目 `data/amazon-baby-mmssl/` 已有真实 `image_feat.npy`+`text_feat.npy`，具备实现 Eq.10–11 的全部输入 |
| **G2 = D2 + D6** | Eq.12 分子对 $\mathcal{N}_u$ 全体正邻居连乘，外层有 $\frac{1}{G\|\mathcal{U}\|}\cdot\frac{1}{\|\mathcal{N}_u\|}$ 归一化 | 单个 `pos_item`，`.sum()` 无归一化 → 这正是官方 `cl_reg∈{1e-4,1e-5,1e-6}` 与论文 $\lambda=10^{-2}$ 差 2–5 个数量级的原因（D5 与 D6 互相解释） | 补上归一化后 $\lambda$ 量纲与论文一致，超参可直接照搬论文 §5.7，省一轮搜参 |
| **G3（论文未提，本项目实测发现）** | Eq.11 直接把各模态余弦相似度**求和**当权重 | — | 实测（§2.2）：baby 图像模态离对角余弦均值 **0.206**、文本 **0.194**，故 $\mathcal{W}$ 均值 ≈ 0.40 且含负值。$\exp(\mathcal{W}\cdot s/\tau)$ 里 $\mathcal{W}$ 均值 ≠ 1 等价于**把有效温度从 $\tau$ 悄悄放大到 $\tau/0.4=2.5\tau$**；$\mathcal{W}<0$ 时正样本被推远，**语义翻转** |

> **额外发现（论文潜在陷阱，建议实现时规避）**：Eq.10 用「交互物品原始特征均值」构造用户特征，论文未声明使用 train-only 交互。若把 valid/test 交互也算进去，$\mathcal{W}$ 会**泄漏测试信息**。本提案强制使用 `dataset.UserItemNet`（该矩阵在 `dataloader.py:304` 构造时只用 `trainUser/trainItem`），从源头杜绝泄漏。

---

## 2. 落地环境实况（本次实测，非引用）

### 2.1 代码资产

| 资产 | 位置 | 状态 |
| --- | --- | --- |
| NLGCL-H 损失（可复用纯函数） | `code/nlgcl_module.py`（96 行，`nlgcl_info_nce` / `nlgcl_neighbor_cl_loss` / `NLGCLHLoss`） | ✅ 已完成，工程质量优于官方（G 可调 + 越界钳位） |
| NLGCL-H 类内实现（实际训练走这条） | `code/model.py:232-252`（`InfoNCE` / `neighbor_cl_loss`） | ✅ 与 `nlgcl_module.py` 逻辑一致，**两处需同步改** |
| 逐层嵌入缓存（避免二次图传播） | `code/model.py:273-276`（`_cl_embs_list`） | ✅ 已有，ASW 直接复用，零额外传播 |
| 多模态特征加载 | `code/dataloader.py:321-340`（`_load_mm_feats`，读取目录下所有 `*.npy`） | ✅ 已有，仅需放宽触发条件 |
| 多模态置信度 $c_i$（ASW-G 依赖） | `code/mm_align.py::MultiModalAligner.fuse()` 返回 `info['conf_vec']`，`[n_items,1]` | ✅ 已有（idea2/idea3 资产） |
| 配置注入 | `code/parse.py:43-55`、`code/world.py:58-71` | ✅ 模板清晰，照抄即可 |
| 训练循环 / epoch 钩子 | `code/main.py:80-84`（`mm_new_epoch()` → `BPR_train_original`） | ✅ ASW-G 的 $c_i$ 刷新挂这里 |

### 2.2 数据集实况（关键：决定实验怎么设计）

规模（两数据集同为 35,598 用户 / 18,357 物品）：

| 数据集 | 训练交互 | 模态特征 | 离对角余弦相似度（前 200 物品） | 判定 |
| --- | --- | --- | --- | --- |
| `amazon-baby-mmssl` | 190,930 | `image_feat.npy` (18357, 4096)<br>`text_feat.npy` (18357, 384) | image: mean **0.2063**, std 0.1158<br>text: mean **0.1942**, std 0.1315<br>image 取值 min 0 / max 40.5（ReLU 长尾） | ✅ **真实 MMSSL 特征**，含语义结构 → **ASW 主战场** |
| `amazon-sports` | 211,807 | `image_feat.npy` (18357, 4096)<br>`image_feat_clip.npy` (18357, 64) | image: mean **−0.0001**, std 0.1377；特征本身 mean 0.0012 / std 1.0077 | ⚠️ **高斯合成噪声**（`prep_amazon_sports.py` 产物），无语义 → **天然安慰剂对照** |

> 这张表是本提案实验设计的地基：**同一套代码、同一套超参，在真实特征上应涨点、在合成噪声上应不掉点**（因为门控会把 $c_i$ 压向 0）。这构成一个内置的可证伪检验，比单纯刷点更有说服力。

### 2.3 现有基线数字（20 epoch，`results_*_aggregated.json`）

| 数据集 | 配置 | R@20 | N@20 |
| --- | --- | --- | --- |
| lastfm | baseline → NLGCL(idea4) | 0.2401 → **0.2680**（+11.6%） | 0.2354 → 0.2579 |
| amazon-baby-mmssl | baseline（n=2 seeds） | 0.0812 ± 0.0042 | 0.0414 ± 0.0021 |
| amazon-baby-mmssl | idea2 多模态对齐（n=1） | 0.0826 | 0.0423 |
| amazon-sports | baseline（n=2 seeds） | 0.0888 ± 0.0016 | 0.0438 ± 0.0011 |

> **重要空白**：NLGCL(+11.6%) 只在 **lastfm** 上验证过，而 lastfm **没有多模态特征**；而有多模态特征的两个 amazon 数据集**从未跑过 `use_cl=1`**。因此本提案的 **Phase A 第一件事不是做 ASW，而是先在 baby 上补齐 NLGCL-H 对照组**，否则 ASW 的增益无从归因。

---

## 3. 模块设计

### 3.1 模块概览

- **模块名称**：`ASW-NLGCL`
- **实现文件**：`baseline/LightGCNpp/code/asw_module.py`（新增）
- **两级形态**：
  - **ASW-S**（Static）：忠实复现论文 Eq.10–11 + 本提案的低秩/归一化修正。用于回答"论文的 ASW 到底值多少点"。
  - **ASW-G**（Gated）：在 ASW-S 上叠加本项目 idea2 的置信度门控 $c_i$。**论文没有，本项目独有**。用于回答"模态不可靠时能否自动免疫"。

### 3.2 输入 / 输出

**预计算阶段（`ASWWeights.build`，训练前一次性）**

| | 内容 | 形状 / 类型 | 来源 |
| --- | --- | --- | --- |
| 输入 1 | 多模态原始特征字典 $\{f^m_i\}$ | `{name: [n_items, d_m]}` float32 | `dataloader._load_mm_feats()` |
| 输入 2 | 训练交互二部图（**train-only**） | `csr_matrix [n_users, n_items]` | `dataset.UserItemNet`（`dataloader.py:304`） |
| 输入 3 | 后端与超参 | `backend / proj_dim / beta / clamp` | `parse.py` 新增参数 |
| 输出 1 | 权重查询器 | `ASWWeights` 对象，提供 `gather(users, items) -> [B, B]` | 内存驻留（或磁盘缓存） |
| 输出 2 | 全局统计量 | $\bar{\mathcal{W}}, \sigma_{\mathcal{W}}$（标量） | 分块累加，无需物化全矩阵 |

**训练阶段（`asw_weighted_info_nce`）**

| | 内容 | 形状 |
| --- | --- | --- |
| 输入 | anchor `v1`、正样本 `v2`、负样本视图 `view`、权重块 `W_blk`、温度 $\tau$ | `[B,d] / [B,d] / [M,d] / [B,M]` |
| 输出 | 加权 InfoNCE 标量损失（已按 $\frac{1}{G\|\mathcal{U}\|\|\mathcal{N}_u\|}$ 归一化） | `scalar` |

**推理阶段**：**无输入、无输出、无改动**。ASW 只塑形训练梯度，`getUsersRating()` 路径与骨干完全一致 → 推理零开销，这是该方案相对"改图/改传播"类方法的核心工程优势。

### 3.3 在整体流程中的位置

```
┌─ 启动期（一次） ────────────────────────────────────────────┐
│ dataloader._load_mm_feats()   → {image_feat, text_feat}     │
│ dataset.UserItemNet (train)   → 稀疏交互                     │
│            ↓                                                 │
│  【新增】ASWWeights.build()                                  │
│   ① Eq.10 用户特征 f_u^m = mean_{i∈N_u^train} f_i^m          │
│   ② L2 归一化 → 低秩因子 (Û^m, Î^m)                          │
│   ③ 分块扫描求 W̄, σ_W（不物化全矩阵）                        │
│   ④ 按 backend 物化 / 保持因子形式 / 缓存到磁盘               │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌─ 每 epoch ──────────────────────────────────────────────────┐
│ main.py:82  Recmodel.mm_new_epoch()                          │
│   └─【新增】若 ASW-G：刷新 conf_vec 快照 c_i（no_grad）       │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌─ 每 batch（model.py::bpr_loss） ────────────────────────────┐
│ getEmbedding() → _cl_embs_list  ← 已有缓存，直接复用          │
│            ↓                                                 │
│ neighbor_cl_loss(embs_list, users, pos)                      │
│   for g in 0..G-1:                                           │
│     【新增】W_blk = asw.gather(users, pos)   # [B,B] 查表     │
│     【改造】InfoNCE(..., w=W_blk)            # 加权           │
│            ↓                                                 │
│ bpr_term += cl_reg * cl        ← 已有接入点（model.py:297）   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌─ 推理 ──────────────────────────────────────────────────────┐
│ getUsersRating() —— 完全不变，ASW 不参与                      │
└──────────────────────────────────────────────────────────────┘
```

### 3.4 数学形式（三处修正）

#### (a) 低秩恒等式：$\mathcal{W}$ 根本不需要物化

论文 Eq.11：$\mathcal{W}_{u,i}=\sum_{m\in\mathcal{M}}\cos(f^m_u, f^m_i)$。令 $\hat{f}$ 表示 L2 归一化后的特征，则

$$\mathcal{W} \;=\; \sum_{m\in\mathcal{M}} \hat{U}^{m}\,(\hat{I}^{m})^{\top},\qquad \hat{U}^m\in\mathbb{R}^{|\mathcal{U}|\times d_m},\ \hat{I}^m\in\mathbb{R}^{|\mathcal{I}|\times d_m}$$

即 $\mathcal{W}$ **天然是秩 $\le \sum_m d_m$ 的低秩矩阵**。这不是近似，是恒等式。于是任意子块可即时算出：

$$\mathcal{W}[\text{users},\text{items}] \;=\; \sum_m \hat{U}^m[\text{users}]\,\big(\hat{I}^m[\text{items}]\big)^{\top}$$

论文 Table 4 的内存分析漏掉了 $|\mathcal{U}|\times|\mathcal{I}|$ 这一项，在 Clothing（39,387×23,033）上是 3.6 GB，在本项目上是 **2.61 GB**（fp32）。用低秩因子后降到 **0.97 GB**；再叠加一次随机投影（JL 引理，$k=128$/模态）降到 **55 MB**。

#### (b) 符号安全 + 均值保持归一化（解决 G3）

$$z_{u,i}=\mathrm{clamp}\!\left(\frac{\mathcal{W}_{u,i}-\bar{\mathcal{W}}}{\sigma_{\mathcal{W}}},\,-3,\,3\right),\qquad
\tilde{\mathcal{W}}_{u,i}=\mathrm{clamp}\big(1+\beta\, g_i\, z_{u,i},\; w_{\min},\; w_{\max}\big)$$

其中 $g_i\in[0,1]$ 是门控（ASW-S 时 $g_i\equiv1$），默认 $\beta=0.5,\ w_{\min}=0.1,\ w_{\max}=3.0$。三个性质：

1. $\mathbb{E}[\tilde{\mathcal{W}}]\approx1$ → **有效温度不被偷改**，$\tau$ 保持论文语义（对照：原式均值 0.40 相当于把 $\tau=0.2$ 变成 $0.5$）。
2. $\tilde{\mathcal{W}}>0$ 恒成立 → **不会出现负权翻转正样本**。
3. $\beta=0 \Rightarrow \tilde{\mathcal{W}}\equiv1$ → **数学上严格退化为标准 NLGCL**，消融干净、回退安全。

#### (c) 置信度门控 ASW-G（论文无，本项目独有）

$$g_i = \begin{cases} c_i & \text{ASW-G，}c_i \text{ 取自 } \texttt{mm\_aligner.fuse().info['conf\_vec']}\\ 1 & \text{ASW-S}\end{cases}$$

动机：论文的 $\mathcal{W}$ 来自**与推荐任务无关的原始 CNN/BERT 特征**。当模态噪声大时（本项目 `amazon-sports` 就是极端案例：余弦均值 −0.0001），$\mathcal{W}$ 纯属噪声，加权只会**主动伤害**训练。门控让模型自己决定"这个物品的模态信号可不可信"，不可信就退回标准 NLGCL。

#### (d) 采样式多正样本 + 归一化（解决 G2）

$$\mathcal{L}_{nl_u}=-\frac{1}{G|\mathcal{U}_B|}\sum_{g}\sum_{u\in\mathcal{U}_B}\frac{1}{K}\sum_{k=1}^{K}\log\frac{\exp\big(\tilde{\mathcal{W}}_{u,i_k^+}\,(\mathbf{e}_u^{(g)\top}\mathbf{e}_{i_k^+}^{(g+1)})/\tau\big)}{\sum_{\hat{i}}\exp\big(\tilde{\mathcal{W}}_{u,\hat{i}}\,(\mathbf{e}_u^{(g)\top}\mathbf{e}_{\hat{i}}^{(g+1)})/\tau\big)}$$

$K=1$ 时等价于当前实现；$K\to|\mathcal{N}_u|$ 时逼近论文 Eq.12。加上 $\frac{1}{G|\mathcal{U}_B|}$ 后 $\lambda$ 与论文 $10^{-2}$ 同量纲（当前 `cl_reg=5e-5` ≈ $10^{-2}/(2048\cdot2)$，**数值上本就自洽**，只是量纲没对齐 → 归一化后可直接用论文超参）。

### 3.5 与现有代码的接入点（精确清单）

| # | 文件 | 位置 | 改动类型 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `code/asw_module.py` | — | **新增 ~180 行** | `ASWWeights`（build/gather/stats/cache）+ `asw_weighted_info_nce` |
| 2 | `code/parse.py` | 第 48 行后（NLGCL 参数块尾） | 新增 7 行 | `--asw`（0=off,1=S,2=G）、`--asw_beta`、`--asw_backend`、`--asw_proj_dim`、`--asw_clamp`、`--asw_K`、`--asw_cache` |
| 3 | `code/world.py` | 第 62 行后 | 新增 7 行 | 仿 `config['cl_reg']=args.cl_reg` 逐条注入 |
| 4 | `code/dataloader.py` | 第 318 行 | 改 1 行 | `if config.get('use_mm',0) or config.get('asw',0):` → ASW 单独开启时也能拿到 `mm_feats` |
| 5 | `code/model.py` | 第 129 行后 | 新增 ~10 行 | 读 ASW 配置；`self.asw = ASWWeights.build(...)`（仅 `use_cl and asw` 时） |
| 6 | `code/model.py` | `InfoNCE` (232) / `neighbor_cl_loss` (242) | 改 ~15 行 | 增加可选形参 `w=None`；`pos`/`ttl` 两处乘权重；补 $\frac{1}{G\|U_B\|}$ 归一化（由 `--asw_norm` 控制，默认开） |
| 7 | `code/nlgcl_module.py` | `nlgcl_info_nce` (21) / `nlgcl_neighbor_cl_loss` (40) | 改 ~15 行 | **同步 #6**，保持"纯函数版"与"类内版"一致（否则未来迁移到 CCDRec 会失配） |
| 8 | `code/model.py` | `mm_new_epoch` (156) | 新增 ~5 行 | ASW-G：每 epoch `no_grad` 刷新 $c_i$ 快照 |
| 9 | `code/main.py` | 配置名拼接处 | 改 1 行 | 日志名追加 `_asw{mode}b{beta}`，与既有 idea2/idea3 日志隔离 |

**关键点：`main.py:82` 已经在调 `mm_new_epoch()`，训练循环本身一行都不用改。**

### 3.6 新增超参

| 参数 | 默认 | 取值 | 含义 |
| --- | --- | --- | --- |
| `--asw` | 0 | 0/1/2 | 0=关（等价现状）；1=ASW-S；2=ASW-G |
| `--asw_beta` | 0.5 | 0.0–1.5 | 加权强度；0 = 数学退化为无权 |
| `--asw_backend` | `dense_fp16` | `dense_fp16` / `lowrank` / `sparse_topk` | 见 §5 存储后端 |
| `--asw_proj_dim` | 0 | 0=不投影，或 128/256 | 随机投影维度（JL 加速） |
| `--asw_clamp` | `0.1,3.0` | — | $w_{\min},w_{\max}$ |
| `--asw_K` | 1 | 1/2/4 | 每 anchor 采样正邻居数 |
| `--asw_norm` | 1 | 0/1 | 是否启用 $\frac{1}{G\|U_B\|}$ 归一化（开启后 `cl_reg` 需按论文 $\lambda$ 量纲设为 ~1e-2） |
| `--asw_cache` | 1 | 0/1 | 是否落盘缓存 `data/<ds>/asw_W_*.npy` |

---

## 4. 算法伪代码

### 4.1 阶段一：权重预计算（训练前一次性）

```python
def ASWWeights.build(mm_feats, UserItemNet_train, cfg):
    """
    mm_feats:          {name: Tensor[n_items, d_m]}   # 原始模态特征
    UserItemNet_train: csr_matrix[n_users, n_items]   # 仅训练交互, 杜绝泄漏
    返回: 支持 gather(users, items) -> [B, B] 的权重查询器
    """
    # ---------- 0. 磁盘缓存命中直接返回 ----------
    key = hash(dataset_name, sorted(mm_feats.keys()), cfg.proj_dim, cfg.backend)
    if cfg.cache and exists(f"data/{ds}/asw_{key}.npz"):
        return ASWWeights.load(f"data/{ds}/asw_{key}.npz")

    U_factors, I_factors = [], []
    # ---------- 1. 逐模态构造低秩因子 ----------
    deg = UserItemNet_train.sum(axis=1).clip(min=1)          # [n_users,1] 训练度
    for m, F_i in mm_feats.items():                          # F_i: [n_items, d_m]

        # 1a. 可选随机投影 (JL 引理): 4096 维 -> proj_dim, 保余弦近似
        if cfg.proj_dim > 0 and F_i.shape[1] > cfg.proj_dim:
            R  = randn(F_i.shape[1], cfg.proj_dim) / sqrt(cfg.proj_dim)   # 固定 seed
            F_i = F_i @ R

        # 1b. Eq.10: 用户特征 = 其训练交互物品的原始特征均值
        F_u = (UserItemNet_train @ F_i) / deg                 # 稀疏 matmul, [n_users, d_m]

        # 1c. L2 归一化 -> 内积即余弦
        U_factors.append(l2_normalize(F_u, dim=1))
        I_factors.append(l2_normalize(F_i, dim=1))

    Uh = concat(U_factors, dim=1)     # [n_users, D],  D = Σ_m d_m'
    Ih = concat(I_factors, dim=1)     # [n_items, D]
    # 恒等式: W = Uh @ Ih.T  (秩 <= D), 无需近似

    # ---------- 2. 分块扫描统计 W 均值/方差 (不物化全矩阵) ----------
    s = ss = n = 0
    for blk in chunks(range(n_users), size=2048):
        Wb = Uh[blk] @ Ih.T                                   # [2048, n_items]
        s += Wb.sum();  ss += (Wb ** 2).sum();  n += Wb.numel()
    W_mean = s / n
    W_std  = sqrt(ss / n - W_mean ** 2) + 1e-8
    log(f"[ASW] W_mean={W_mean:.4f} W_std={W_std:.4f} neg_ratio={...}")
    #  ↑ 实测预期 baby: W_mean ≈ 0.40 -> 印证 §1 G3 的"有效温度被偷改"论断

    # ---------- 3. 按后端物化 ----------
    if cfg.backend == "dense_fp16":       # 本项目 CPU 训练首选: RAM 1.31 GB, 查表 O(1)
        W = empty([n_users, n_items], dtype=fp16)
        for blk in chunks(range(n_users), 2048):
            W[blk] = ((Uh[blk] @ Ih.T) - W_mean) / W_std      # 直接存标准化后的 z
            W[blk] = W[blk].clamp(-3, 3)
        store = DenseStore(W)
    elif cfg.backend == "lowrank":        # GPU 显存紧张时: 只存因子 (55 MB @ proj_dim=128)
        store = LowRankStore(Uh, Ih, W_mean, W_std)
    else:                                  # sparse_topk: 只保留训练边 + 每用户 top-k, 其余 z=0
        store = SparseStore(topk_rows(Uh, Ih, k=cfg.topk), UserItemNet_train, W_mean, W_std)

    if cfg.cache: store.save(f"data/{ds}/asw_{key}.npz")
    return ASWWeights(store, W_mean, W_std, cfg)


def ASWWeights.gather(self, users, items, conf=None):
    """返回 [B_u, B_i] 的最终权重 W~, 已完成门控/符号安全/均值保持。"""
    z = self.store.z_block(users, items)              # 标准化相似度, ∈[-3,3]
    g = 1.0 if conf is None else conf[items].view(1, -1)   # ASW-G: 置信度门控
    return (1.0 + self.beta * g * z).clamp(self.w_min, self.w_max)   # E[W~] ≈ 1
```

### 4.2 阶段二：训练（完整流程）

```python
# ============ 加权 InfoNCE（替换 model.py:232 / nlgcl_module.py:21）============
def asw_info_nce(v1, v2, view, tau, w_pos=None, w_ttl=None, norm=1.0):
    """
    v1  : [B, d]  anchor
    v2  : [B, d]  positive
    view: [M, d]  negatives (当前实现 M = B, batch 内负样本)
    w_pos: [B]    正样本对权重 W~_{u,i+}       (None -> 全 1, 退化为原实现)
    w_ttl: [B, M] anchor 对全体候选的权重 W~   (None -> 全 1)
    """
    v1, v2, view = l2norm(v1), l2norm(v2), l2norm(view)
    s_pos = (v1 * v2).sum(1)                     # [B]
    s_all = v1 @ view.t()                        # [B, M]
    if w_pos is not None: s_pos = w_pos * s_pos          # Eq.12 分子加权
    if w_ttl is not None: s_all = w_ttl * s_all          # Eq.12 分母加权(论文同步加权)
    # 数值稳定: 减去每行最大值再 exp
    m      = s_all.max(dim=1, keepdim=True).values.detach()
    logZ   = ((s_all - m) / tau).exp().sum(1).log() + m.squeeze(1) / tau
    loss   = -(s_pos / tau - logZ)               # [B]
    return loss.sum() * norm                     # norm = 1/(G*B) 时与论文 λ 同量纲


# ============ NLGCL-H 主损失（替换 model.py:242）============
def neighbor_cl_loss(self, embs_list, users, pos_list):
    """pos_list: [B, K] —— K 个采样正邻居 (K=1 时退化为当前实现)"""
    eu, ei = split(embs_list[0], [n_users, n_items])
    conf   = self._conf_snapshot if self.asw_mode == 2 else None   # ASW-G
    norm   = 1.0 / (self.G * len(users)) if self.asw_norm else 1.0
    cl_u = cl_i = 0.
    for g in range(self.G):
        cu, ci = split(embs_list[g + 1], [n_users, n_items])
        for k in range(K):                                # 多正样本采样
            pos = pos_list[:, k]
            if self.asw:
                W_blk = self.asw.gather(users, pos, conf)  # [B, B] 查表, 无梯度
                w_pos, w_ttl = W_blk.diagonal(), W_blk
            else:
                w_pos = w_ttl = None
            # 用户侧: anchor e_u^(g), 正样本 = 下一层邻居物品 e_{i+}^(g+1)
            cl_u += asw_info_nce(ci[pos], eu[users], eu[users], self.cl_temp,
                                 w_pos, w_ttl, norm) / K
            # 物品侧: anchor e_i^(g), 正样本 = 下一层邻居用户 e_{u+}^(g+1)
            cl_i += asw_info_nce(cu[users], ei[pos], ei[pos], self.cl_temp,
                                 w_pos, w_ttl.t(), norm) / K
        eu, ei = cu, ci
    return self.cl_alpha * cl_u + (1 - self.cl_alpha) * cl_i


# ============ 完整训练流程（main.py + Procedure.py，★ = 新增/改动）============
def train():
    dataset = Loader(path=f"data/{world.dataset}")
    #   └─ dataloader.py:318 ★ `use_mm or asw` 时加载 mm_feats
    model = LightGCN(config, dataset)
    if config.use_cl and config.asw:                               # ★
        model.asw = ASWWeights.build(dataset.mm_feats,             # ★ 一次性预计算
                                     dataset.UserItemNet, config)  # ★ train-only

    for epoch in range(TRAIN_epochs):
        model.mm_new_epoch()
        #   └─ ★ ASW-G: with no_grad: model._conf_snapshot = aligner.fuse(...)['conf_vec']

        S = UniformSample_original(dataset)                # (u, i+, i-)
        # ★ K>1 时: 额外从 dataset._allPos[u] 再采 K-1 个正邻居 -> pos_list [B,K]
        for (bu, bp, bn) in minibatch(shuffle(S), batch_size=2048):
            # ---- 前向 ----
            all_u, all_i, _u, _i = model.computer()        # 一次图传播
            model._cl_embs_list  = [cat(_u[:,l,:], _i[:,l,:]) for l in 0..L]  # 已有缓存

            # ---- BPR 主损失 ----
            loss = softplus(neg_score - pos_score).mean() + decay * reg

            # ---- NLGCL(+ASW) 对比损失 ----
            if model.use_cl:
                cl   = model.neighbor_cl_loss(model._cl_embs_list, bu, bp_list)  # ★
                loss = loss + model.cl_reg * cl
                #  ★ asw_norm=1 时 cl_reg 用论文量纲 λ≈1e-2; =0 时沿用 5e-5

            # ---- idea2/idea3 多模态对齐（已有，与 ASW 正交，可叠加）----
            if model.use_mm:
                loss = loss + mm_reg * L_align + cost_reg * cost_term

            loss.backward(); opt.step(); opt.zero_grad()

        if epoch % 10 == 0:
            Procedure.Test(dataset, model, epoch)          # 推理路径不变
```

### 4.3 阶段三：推理

```python
def inference(model, users, topk=20):
    """★ 与骨干完全一致 —— ASW 不参与推理，零额外开销。"""
    all_users, all_items, _, _ = model.computer()   # 与 use_cl / asw 无关
    scores = sigmoid(all_users[users] @ all_items.t())
    scores[train_mask] = -inf
    return scores.topk(topk)
```

> 这一点值得单独强调：**ASW 是纯训练期的梯度整形器**。相比"改图结构 / 改传播 / 加融合分支"的方案，它不引入任何在线延迟、不增加模型参数、不影响已部署的推理服务 —— 这是它在工程上最容易被接受的理由。

---

## 5. 复杂度与显存实测测算（|U|=35,598, |I|=18,357, B=2048）

### 5.1 存储

| 方案 | 公式 | 本项目数值 | 评价 |
| --- | --- | --- | --- |
| 论文隐含的稠密 $\mathcal{W}$ (fp32) | $\|U\|\|I\|\cdot4$ | **2.61 GB** | 论文 Table 4 未计入；Clothing 上是 3.6 GB |
| `dense_fp16`（本提案默认） | $\|U\|\|I\|\cdot2$ | **1.31 GB** | CPU 训练场景 RAM 完全放得下，gather 为 O(1) 查表 |
| `lowrank`（不投影） | $(\|U\|+\|I\|)\cdot\sum d_m\cdot4$ | 0.97 GB | 精确无损 |
| `lowrank` + `proj_dim=128`/模态 | $(\|U\|+\|I\|)\cdot256\cdot4$ | **55 MB** | JL 近似，显存降 47× |
| `sparse_topk`（仅训练边） | $\|E\|\cdot4$ | **0.76 MB** | 极致省内存，但分母权重需退化为 1 |
| 每 batch 权重块 | $B^2\cdot4$ | 16.8 MB | 因当前实现负样本取自 batch 内（`view=eu[users]`），**不是全 $\|I\|$** |

> **一个容易踩的坑**：如果照论文字面把分母取全物品集，batch 权重块会变成 $B\times|I|$ = 150 MB/batch，CPU 上不可行。当前 LightGCN++ 实现用 batch 内负样本，恰好让 ASW 的 batch 开销降到 16.8 MB —— 这是本方案在本项目能跑通的前提，也应在报告中如实声明（属于 D3 口径差的下游影响）。

### 5.2 计算

| 环节 | FLOPs | 预估耗时 |
| --- | --- | --- |
| Eq.10 用户特征（稀疏 matmul） | $\|E\|\cdot\sum d_m$ ≈ 0.86 GFLOP | < 1 s |
| 预计算全 $\mathcal{W}$（精确，4096+384 维） | $2\|U\|\|I\|\sum d_m$ ≈ **5.85 TFLOP** | 多线程 BLAS ~50 GFLOPS → **约 2 分钟**（一次性，可缓存） |
| 预计算（`proj_dim=128`×2 模态） | ≈ 0.33 TFLOP | **< 10 s** |
| 每 batch gather（`dense_fp16`） | 0（纯索引） | 可忽略 |
| 每 batch gather（`lowrank`） | $2B^2\cdot D$ ≈ 2.1 GFLOP（D=256） | CPU 单线程约 0.3–1 s/batch → **CPU 下不推荐** |

**结论**：本项目当前是 **CPU 训练**（`OMP_NUM_THREADS=1`，见 `docs/lightgcnpp_roadmap_status.md` §5），因此默认 `--asw_backend dense_fp16`：用 1.31 GB RAM 换取**训练期零额外计算**。预计算阶段可临时放开 BLAS 线程数。

---

## 6. 实验设计

### 6.1 必须先补的对照组

`use_cl=1` 从未在 amazon 两个数据集上跑过。**Phase A 的第一组实验是 NLGCL-H 本身**，否则 ASW 的增益无法归因。

### 6.2 消融矩阵（每格 3 seeds ∈ {2024,2025,2026}）

| # | 配置 | `use_cl` | `asw` | `beta` | 目的 |
| --- | --- | --- | --- | --- | --- |
| E0 | LightGCN++ baseline | 0 | 0 | — | 已有（baby 0.0812±0.0042） |
| E1 | + NLGCL-H | 1 | 0 | — | **缺失的对照组**，先补 |
| E2 | + ASW-S | 1 | 1 | 0.5 | 论文 ASW 值多少点（论文 Fig.2 只有定性柱状图，无数值） |
| E3 | + ASW-S, β=0 | 1 | 1 | 0.0 | **健全性检查**：必须与 E1 数值一致，否则实现有 bug |
| E4 | + ASW-G | 1 | 2 | 0.5 | 门控增量（需 `use_mm=1` 提供 $c_i$） |
| E5 | + ASW-S, K=4 | 1 | 1 | 0.5 | 多正样本（G2）的贡献 |
| E6 | + ASW-S, 归一化关 | 1 | 1 | 0.5 | 验证 D5/D6 的量纲自洽性论断 |
| **P1** | **sports 上跑 E2**（合成噪声特征） | 1 | 1 | 0.5 | **安慰剂对照**：预期不涨或略掉 |
| **P2** | **sports 上跑 E4** | 1 | 2 | 0.5 | **门控免疫检验**：预期回到 E1 水平 |

### 6.3 判定线（沿用项目既有决策规则风格）

- **E3 ≠ E1**（相对差 > 0.5%）→ 实现有 bug，停止，先修。
- **E2 相对 E1 提升 < 2%**（3 seeds 均值，且 ±1 std 区间重叠）→ 判定"论文的 ASW 在本项目数据上无效"，**如实记录并停止**，不做超参轰炸。这本身就是有价值的负面结论（因为官方代码没实现它，社区无人验证过）。
- **E2 ≥ +2% 且 E4 相对 E2 再 ≥ +1%，同时 P1/P2 在 sports 上不掉点** → ASW-G 成立，进入 Phase C（与 idea2/idea3 联合调参）。
- **P1 在 sports 上显著涨点** → **警报**：说明增益不来自模态语义（sports 特征是纯噪声），需回查是否只是"随机权重扰动等价于正则化"。这个对照能挡掉一类典型的自欺欺人结论。

### 6.4 复现命令

```bash
# 环境（见 docs/lightgcnpp_roadmap_status.md §5）
PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE

cd baseline/LightGCNpp/code

# E1: NLGCL-H 对照组（先跑这个）
$PY main.py --dataset amazon-baby-mmssl --layer 3 --epochs 20 --seed 2024 \
            --use_cl 1 --cl_temp 0.2 --cl_reg 5e-5 --cl_alpha 0.6 --G 2

# E2: ASW-S
$PY main.py --dataset amazon-baby-mmssl --layer 3 --epochs 20 --seed 2024 \
            --use_cl 1 --cl_temp 0.2 --cl_reg 5e-5 --cl_alpha 0.6 --G 2 \
            --asw 1 --asw_beta 0.5 --asw_backend dense_fp16

# E4: ASW-G（需 idea2 的置信度）
$PY main.py --dataset amazon-baby-mmssl --layer 3 --epochs 20 --seed 2024 \
            --use_cl 1 --cl_temp 0.2 --cl_reg 5e-5 --G 2 \
            --asw 2 --asw_beta 0.5 --use_mm 1 --mm_reg 1e-3

# P1: 安慰剂对照（sports 的 image_feat.npy 是高斯合成噪声）
$PY main.py --dataset amazon-sports --layer 3 --epochs 20 --seed 2024 \
            --use_cl 1 --G 2 --asw 1 --asw_beta 0.5
```

> 超参取值依据论文 §5.7：$\tau=0.2$、$G=2$、$L$（弱骨干）=3。`cl_reg` 先沿用项目已验证的 `5e-5`（`--asw_norm 0` 语义）；若开启 `--asw_norm 1`，改用论文量纲 $\lambda=10^{-2}$。

---

## 7. 可行性说明

### 7.1 改动范围

| 维度 | 评估 |
| --- | --- |
| 新增文件 | 1 个（`code/asw_module.py`，~180 行） |
| 修改文件 | 5 个（`parse.py` +7 / `world.py` +7 / `dataloader.py` 改 1 行 / `model.py` +25 / `nlgcl_module.py` +15 / `main.py` 改 1 行），合计 **≈ 60 行** |
| 训练循环 | **零改动**（`main.py:82` 的 `mm_new_epoch()` 钩子已存在） |
| 推理路径 | **零改动**（§4.3） |
| 与 idea2/idea3 关系 | **正交可叠加**。ASW 改的是对比损失的样本权重，idea2 改的是 $e^{(0)}_{item}$ 的融合，两者作用在不同环节；ASW-G 只是**只读消费** idea2 的 `conf_vec`，不改其梯度通路 |
| 回退成本 | `--asw 0` 即恢复现状；所有改动都是可选形参 `w=None` 走原分支 |
| 预计工作量 | 编码 + 自测 0.5–1 天；E0–E6 + P1/P2 共 9 组 × 3 seeds × 20 epoch，CPU 上按现有速度约 2–3 天挂后台 |

### 7.2 预期收益

| 层面 | 收益 |
| --- | --- |
| **学术** | 论文 §5.4 Fig.2 只给了 w/o-ASW 的**定性柱状图，正文无任何数值**，而官方代码根本没实现 ASW（D1）→ 目前**社区没有任何人定量验证过 ASW 的真实贡献**。本实验产出的数字（哪怕是负面结论）具有独立价值 |
| **方法** | 三项修正都是可写进论文的技术点：低秩恒等式（免 2.61 GB 物化）、均值保持归一化（消除隐式温度漂移）、置信度门控（噪声模态自免疫）。其中门控 ASW **论文完全没有** |
| **性能（保守估计）** | NLGCL-H 在 lastfm 已验证 +11.6%；ASW 作为其精细化加权，参考同类"相似度加权对比学习"工作的一般幅度，预期在 baby 上带来 **+1%~3%** 的额外相对增益。**注意：这是估计不是承诺**，论文没给数值，判定线（§6.3）已设为 2% |
| **工程** | 训练期开销近零（dense_fp16 查表）、推理期严格零开销；`asw_module.py` 与 `nlgcl_module.py` 一样是纯函数式，未来可整体迁到 CCDRec 的 CF 分支 |
| **副产物** | 一张"模态特征质量 → ASW 有效性"的对照表（真实 MMSSL vs 高斯合成），可直接支撑"多模态推荐里特征质量比模型结构更重要"的论点 |

### 7.3 潜在风险与缓解

| # | 风险 | 概率 | 影响 | 缓解措施 |
| --- | --- | --- | --- | --- |
| R1 | **内存**：`dense_fp16` 占 1.31 GB RAM | 中 | 中 | 已提供三档后端；机器紧张时切 `lowrank --asw_proj_dim 128`（55 MB）或 `sparse_topk`（0.76 MB）。启动时打印实际占用并在超阈值时自动降级 |
| R2 | **权重为负 / 温度漂移**（论文原式的真实缺陷，实测 $\bar{\mathcal{W}}$≈0.40） | **高**（必然发生） | 高 | §3.4(b) 的均值保持 + clamp 已从形式上根除；预计算阶段打印 `W_mean/W_std/neg_ratio` 供核对 |
| R3 | **ASW 无效甚至掉点**（模态语义与协同信号不相关） | 中 | 中 | ① ASW-G 门控让 $c_i\to0$ 时自动退回标准 NLGCL；② $\beta$ 可调至 0；③ §6.3 判定线明确写了"无效就如实记录并停止"，避免陷入超参轰炸 |
| R4 | **测试集泄漏**（Eq.10 若用了全量交互） | 中（论文未声明，易踩） | **高**（结论作废） | 强制使用 `dataset.UserItemNet`（`dataloader.py:304` 只用 `trainUser/trainItem`）；在 `build()` 里 assert 输入矩阵的 nnz == `trainDataSize` |
| R5 | **sports 上的"假涨点"**（随机权重当正则化用） | 中 | 高 | §6.2 的 P1/P2 安慰剂对照专门用来抓这个；若 P1 显著涨点则判定增益与模态语义无关 |
| R6 | **两处 NLGCL 实现不同步**（`model.py` 类内版 vs `nlgcl_module.py` 纯函数版） | **高**（已存在的技术债） | 中 | 接入点 #6/#7 强制同步修改；补一个 `_smoke_asw.py`，随机张量下断言两条路径输出差 < 1e-6（仿已有 `_smoke_gradfix.py` 风格） |
| R7 | **预计算耗时**（精确模式 4096 维约 2 分钟，若单线程则 ~1.5 小时） | 中 | 低 | 预计算阶段临时放开 `OMP_NUM_THREADS`；结果落盘缓存（`--asw_cache 1`），同数据集只算一次 |
| R8 | **多正样本 K>1 的采样成本** | 低 | 低 | 复用 `dataset._allPos`（`dataloader.py:311` 已预计算），采样为纯索引操作；默认 K=1 不启用 |

### 7.4 分阶段落地计划

| 阶段 | 内容 | 产出 | 判定 |
| --- | --- | --- | --- |
| **Phase A**（半天） | 补 E1（NLGCL-H on baby/sports，3 seeds） | 缺失的对照数字 | NLGCL-H 在 amazon 上是否也有效？若无效，先查 amazon 场景的 NLGCL 适配性，暂缓 ASW |
| **Phase B**（1 天） | 实现 `asw_module.py` + 5 处接入 + `_smoke_asw.py`；跑 E3 健全性检查 | 可运行的 ASW-S | E3 必须 ≡ E1 |
| **Phase C**（2 天） | E2/E5/E6 + 安慰剂 P1 | ASW-S 的定量贡献 + 论文修正项的验证 | 见 §6.3 判定线 |
| **Phase D**（1 天） | E4 + P2（依赖 idea2 训练完成产出稳定的 `conf_vec`） | ASW-G 的门控增量 | 门控在噪声数据上是否真能免疫 |
| **Phase E** | 汇总为 `docs/asw_nlgcl_report.md`，回填 `results_*_aggregated.json` | 实验报告 | — |

> **依赖提醒**：Phase D 需要 idea2（`use_mm=1`）先跑出稳定的置信度分布。按 `docs/lightgcnpp_roadmap_status.md` §4，idea2 结果尚在回填中，因此 **Phase A→C 可立刻开始，Phase D 排在 idea2 收尾之后**。

---

## 8. 本提案对 11 条差异的覆盖情况

| 差异 | 严重度 | 本提案是否处理 | 方式 |
| --- | --- | --- | --- |
| D1 ASW 完全缺失 | 致命 | ✅ **核心目标** | §3.4 完整实现 Eq.10–11 |
| D2 单正样本 | 严重 | ✅ | `--asw_K` 采样式多正样本 |
| D3 转置 softmax 轴 | 中 | ⚪ 保持现状 | 不改口径以保证与已有 lastfm 结果可比；影响已在 §5.1 说明 |
| D4 论文无 alpha | 中 | ⚪ 保持现状 | `cl_alpha=0.6` 已在 lastfm 调优，不动 |
| D5 `cl_reg` 差 2–5 数量级 | 中 | ✅ | `--asw_norm` 对齐量纲，E6 专门验证 |
| D6 缺 $1/(G\|U\|)$ 归一化 | 中 | ✅ | 同上 |
| D7 G 硬编码 = L | 中 | ✅ 已解决 | 本项目 `nlgcl_module.py` 早已支持 `--G` 可调 |
| D8 FREEDOM+/LGMRec+ 的 CL 只在纯 ID 嵌入上 | 严重 | ⚪ 不适用 | 本项目骨干是 LightGCN++，无该问题 |
| D9 无 Entire scope | 中 | ⚪ 不做 | 论文 Table 6 已证 H 全面优于 E，无复现价值 |
| D10 命名混淆 | 低 | ✅ | 新模块显式命名 `asw_module.py`，与 COHESION 的 `adaptive_optimization` 区分 |
| D11 代码微瑕 | 低 | ✅ | `_smoke_asw.py` 双路径一致性断言 |

---

## 9. 一句话总结

> NLGCL+ 把 ASW 写进了标题、写进了公式、写进了消融图，**却没写进代码**。本提案在本项目已跑通的 NLGCL-H 之上，用约 240 行改动把它真正实现出来，并在实现过程中修掉论文自身的三个硬伤（2.61 GB 不可扩展的权重矩阵、会翻转语义的负权重、被悄悄放大 2.5 倍的有效温度），再叠加一个论文没有的置信度门控，让它在噪声模态上能够自动免疫。整套方案训练期近零开销、推理期严格零开销、任何时刻都能一键回退。
