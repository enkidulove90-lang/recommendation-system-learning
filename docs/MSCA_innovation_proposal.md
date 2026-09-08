# MSCA-Inspired 三视图协同锚定多模态增强 模块设计

> 来源：MSCA (WWW '26, DOI 10.1145/3774904.3792192) + 本项目 `baseline/LightGCNpp/`
> 衔接现状：idea1 NLGCL-H（层间对比，已完成）、idea2 `mm_align`（先融合再传播，已完成）、idea3 `cost_reg`（已完成）、P3 `post_mm_fuse`（传播后融合，提案）
> 模块代号：**`cooc_graph`（B 纯交互共现图）+ `cacl`（A 协同锚定对比）+ `bypass_fuse`（C 旁路加性注入）**
> 三模块构成设计空间：pre-fuse（idea2，传播前改 e⁽⁰⁾）｜ post-fuse（P3，传播后改 light_out）｜ **bypass-additive（C，E\* = Ē_collab + α·Ê_view，第三种位置）**

---

## 0. 立项动机 (Why)

**MSCA 论文真正独立的贡献**（见 `docs/MSCA_cross_analysis.md` §3 与 D1–D10）只有两条：

1. **共现结构图**（item-item co-occurrence, `RᵀR` → top-k kNN）→ 1 层 GCN 得到结构视图 `Eⁱˢ`。
2. **协同锚定对比**（SCA）：以**协同表征**（图传播后 `E_bar`，**排除第 0 层**）为锚点，各增强视图（结构/模态）为正样本做 InfoNCE——**不是跨模态对比**，而是"协同锚定 + 视图增强"。

其余组件（MAF 注意力减冗余）经交叉分析确认是 MGCN Behavior-Aware Fuser 的逐字移植；公式 Eq.12–14 在数学上退化（见 D1），**真实可用逻辑只在代码里**。因此本提案**只迁移上述两条独立贡献**，并规避 D4（`.toarray()` 31.7 GB 爆炸）。

**本项目现状与缺口**：

| 能力 | idea1/2/3/P3 | MSCA 三模块补位 |
|------|-------------|----------------|
| 跨层对比 | ✅ NLGCL-H | — |
| 传播前 MM 注入 | ✅ idea2 (`mm_align.fuse`) | — |
| 传播后 MM 注入 | ✅ P3 `post_mm_fuse` | — |
| **item-item 纯交互结构图**（不依赖模态） | ❌ 缺失 | ✅ **B `cooc_graph`** |
| **协同锚定对比**（锚=协同，正=增强视图） | ❌ 缺失（现有对比均为层间/跨视图） | ✅ **A `cacl`** |
| **旁路加性注入** `E* = Ē + α·Ê` | ❌ 缺失（第三种位置） | ✅ **C `bypass_fuse`** |

**关键数据集事实**（来自 prior context 核对）：
- 真实可用 MM 特征：`amazon-baby-mmssl/(image,text).npy`、`amazon-sports/(image,image_clip).npy`（但 sports 的 `image_feat.npy` 是合成高斯噪声，不可用）。
- **5 个数据集无 npy**：`lastfm / gowalla / ml-1m / yelp2018 / amazon-book` → 只能靠 **B 的纯交互共现图**（不依赖模态）获得结构视图。
- LightGCNpp 在 `amazon-sports` 的 R@20 ≈ 0.111（idea1 起点），距离 MSCA 报的 0.1210 有空间。

**核心假设 (可证伪)**：
> H1: 在稀疏数据集上，**协同锚定对比（A）比跨模态对比更稳**，因为它不依赖有噪声的模态特征，锚点始终是协同信号。
> H2: **纯交互共现图（B）能在 5 个无 npy 数据集上提供有效结构正则**，且不引入模态噪声。
> H3: **旁路加性注入（C）与 pre/post-fuse 正交**，三者 2×2×2 = 8 组合构成完整注入设计空间；C 的 α 可学优于固定。

---

## 1. 模块设计（三个模块）

### 1.1 模块 B — `CooccurrenceGraphBuilder`（纯交互共现图）

**模块名称**：`CooccurrenceGraphBuilder`（代号 `cooc_graph`）

**作用**：从用户-物品二部交互矩阵 `R` 构造 item-item 共现图 `Ā_s = kNN(RᵀR, k=10, count>1)`，再用 1 层 GCN 得到**结构视图** `Eⁱˢ`（不依赖任何模态特征）。**关键：全程 sparse，绝不 `.toarray()`（规避 D4）**。

**输入/输出**：

| 接口 | 张量 | 含义 |
|------|------|------|
| 输入 | `R`: `scipy.sparse` 用户-物品 (n_users×n_items) | 二部交互（0/1 或计数） |
| 输入 | `i_bar`: `Tensor[n_items, d]` | 协同物品表征（= `embs_prop`，见 §2.2） |
| 输出 | `A_s_coo`: `scipy.sparse` (n_items×n_items) | top-k 共现邻接（二值或余弦归一） |
| 输出 | `E_struct`: `Tensor[n_items, d]` | 1 层 GCN 结构视图：`Ã_s · i_bar` |
| 输出 | `E_struct_u`: `Tensor[n_users, d]` | 用户结构视图：`normalize(R · E_struct)`（反投影，对应 MSCA `semantic_encode`） |

**流程位置**：
```
dataset.getSparseGraph() → R
  ↓
[本提案 B] cooc_graph.build(R, k=10, min_count=1)  → Ā_s (sparse)
[本提案 B] cooc_graph.encode(Ā_s, i_bar)           → E_struct, E_struct_u
  ↓
[本提案 A] cacl.align(i_bar, u_bar, E_struct, E_struct_u)
[本提案 C] bypass_fuse.fuse(i_bar, E_struct[, modal_emb])
```

**与现有代码接入点**：

| 文件 | 位置 | 改动 |
|------|------|------|
| `code/model.py` `__init_weight` (L131-150) | 紧跟 `use_mm` 块后 | **新增** `self.use_cooc`、`self.cooc_k`、`self.cooc_min_count`、`self.cooc_mode` 与 `self.cooc_graph = CooccurrenceGraphBuilder(...)` |
| `code/model.py` `computer()` (L228-229) | `users, items = split(light_out)` 后 | **新增** `if self.use_cooc: self._struct = self.cooc_graph.encode(A_s, items_prop)` 缓存 `E_struct`/`E_struct_u`（复用 `embs_prop` 作 `i_bar`） |
| `code/cooc_graph.py`（新文件） | — | **新增** 模块实现（~120 行） |
| `code/parse.py` (L63 之后) | — | **新增** `--use_cooc --cooc_k --cooc_min_count --cooc_mode` |
| `code/world.py` | 同 `use_mm` 注入模式 | **新增** 同名 config key |

**B 的实现要点（避开 D4）**：
```python
# R_tR = R.T @ R  → scipy sparse (item-item), 不 densify
R_tR = (R.T @ R).tocsr()
# 逐行: 过滤 count<=min_count, 取 top-k（用 scipy 或 torch sparse topk）
for i in range(n_items):
    row = R_tR.getrow(i)
    mask = row.data > min_count
    idx, val = row.indices[mask], row.data[mask]
    if cooc_mode == 'binary':
        val = np.ones_like(val)
    # top-k by val
    if len(val) > k:
        thr = np.sort(val)[-k]
        keep = val >= thr
        idx, val = idx[keep], val[keep]
    # 写入稀疏 Ā_s[i, idx] = val
# E_struct = sparse_mm(Ã_s_norm, i_bar)   # 1 层 GCN, 对称归一
```

---

### 1.2 模块 A — `CollaborationAnchoredCL`（协同锚定对比）

**模块名称**：`CollaborationAnchoredCL`（代号 `cacl`）

**作用**：把对比学习的**锚点固定为协同表征**（图传播后、排除第 0 层的 `Ē_collab`），正样本为 B 产出的结构视图（及可选模态视图），负样本为全图节点。即 MSCA Eq.15–16 的 SCA，但**锚点非模态**。

**与现有 NLGCL / mm_align 对比**：

| 对比损失 | 锚点 | 正样本 | 位置 |
|---------|------|--------|------|
| idea1 `neighbor_cl_loss` | 同层 ego | 跨层 + 跨节点邻居 | ego 层 |
| idea2 `mm_aligner.contrastive_loss` | fused ID | 模态投影 | 传播前 |
| **A `cacl`** | **协同传播表征 Ē_collab** | **结构/模态视图** | 传播后 |

**输入/输出**：

| 接口 | 张量 | 含义 |
|------|------|------|
| 输入 | `u_bar`, `i_bar`: `Tensor[n_users,n_items, d]` | 协同表征（= `embs_prop` 拆分） |
| 输入 | `E_struct_u`, `E_struct`: `Tensor` | 来自 B 的结构视图 |
| 输入（可选） | `E_modal_u`, `E_modal`: `Tensor` | 来自 `mm_aligner` 模态投影（仅 baby/sports） |
| 输出 | `L_cacl`: `scalar` | 4 项 InfoNCE 之和（用户/物品 × 结构/模态） |

**流程位置**：接入 `bpr_loss`（与 idea1/idea2 并列，L291-330 同区段），复用已缓存的 `embs_prop` 与 B 的 `self._struct`。

**与现有代码接入点**：

| 文件 | 位置 | 改动 |
|------|------|------|
| `code/model.py` `bpr_loss` (L291-299 区段) | `if self.use_cl:` 块**旁** | **新增** `if self.use_cacl:` 调用 `self.cacl.align(...)` 并加到 `bpr_term` |
| `code/model.py` `__init_weight` | `use_cl` 块后 | **新增** `self.use_cacl`、`self.cacl_temp`、`self.cacl_reg`、`self.cacl_use_modal` |
| `code/model.py` `InfoNCE` (L234-242) | 直接复用 | **不改**，A 调用 `self.InfoNCE(i_bar[batch], E_struct[batch], all_items, tau)` |
| `code/cacl.py`（新文件） | — | **新增** 模块（~60 行，4 项 InfoNCE 封装） |
| `code/parse.py` | — | **新增** `--use_cacl --cacl_temp --cacl_reg --cacl_use_modal` |

**A 的 4 项损失（沿用现有 InfoNCE 语义）**：
```
L_cacl = L^C_u + L^C_i + (L^M_u + L^M_i if modal else 0)
L^C_i = InfoNCE(i_bar[batch], E_struct[batch], all_items, τ)      # 物品: 锚=协同, 正=结构
L^C_u = InfoNCE(u_bar[batch], E_struct_u[batch], all_users, τ)    # 用户: 锚=协同, 正=结构(反投影)
# 模态视图(可选, baby/sports): 用 mm_aligner 投影作为 E_modal / E_modal_u
```

---

### 1.3 模块 C — `BypassAdditiveFusion`（旁路加性注入）

**模块名称**：`BypassAdditiveFusion`（代号 `bypass_fuse`）

**作用**：补全三种注入位置的最后一格。最终表征 `E* = Ē_collab + α · Ê_view`，其中 `Ē_collab = embs_prop`（排除第 0 层，对应 MSCA `E_bar`），`Ê_view = MAF(E_struct, [E_modal])`（注意力加权视图和，对应 MSCA Eq.12 真实代码逻辑）。

**三种注入位置设计空间**：

| 位置 | 模块 | 公式 | 现有状态 |
|------|------|------|---------|
| 传播前改 e⁽⁰⁾ | idea2 `mm_align` | `e⁽⁰⁾_item ← fuse` | ✅ |
| 传播后改 light_out | P3 `post_mm_fuse` | `light_out ⊕ MM_proj` | 提案 |
| **旁路加性（第三种）** | **C `bypass_fuse`** | **`E* = Ē_collab + α·Ê_view`** | ✅ 本提案 |

**输入/输出**：

| 接口 | 张量 | 含义 |
|------|------|------|
| 输入 | `E_collab`: `Tensor[n, d]` | `embs_prop`（用户+物品拼接） |
| 输入 | `E_struct`: `Tensor[n_items, d]` | 来自 B |
| 输入（可选） | `E_modal`: `Tensor[n_items, d]` | 来自 `mm_aligner`（baby/sports） |
| 输出 | `E_final`: `Tensor[n, d]` | `E_collab + α · MAF(E_struct, [E_modal])` |
| 状态 | `α`: `nn.Parameter` (scalar) | 可学融合系数（MSCA `fusion_coeff`） |

**流程位置**：
```
computer() → (users, items, _users, _items)
  ↓ embs_prop = mean(layers 1..L)  ← Ē_collab (排除第 0 层, 对齐 MSCA Eq.1-3)
[本提案 C] E_final = bypass_fuse.fuse(embs_prop, E_struct[, E_modal])
  ↓
getUsersRating / bpr_loss 使用 E_final 替代 light_out
```

**与现有代码接入点**：

| 文件 | 位置 | 改动 |
|------|------|------|
| `code/model.py` `computer()` (L223-229) | `embs_prop` 计算后 | **新增** `if self.use_bypass: return self.bypass_fuse.fuse(embs_prop, self._struct, modal)`（注意：返回 `E_final` 而非 `light_out`，但 `_users/_items` 仍返回供 idea1 用） |
| `code/model.py` `__init_weight` | `use_mm` 块后 | **新增** `self.use_bypass`、`self.bypass_alpha_init`、`self.bypass_mode`（`'struct'`/`'struct+modal'`）、`self.bypass_fuse = BypassAdditiveFusion(...)` |
| `code/model.py` `getUsersRating` (L256-262) | `all_users, all_items = computer()` | **不改**（C 已在 computer 内返回 E_final） |
| `code/bypass_fuse.py`（新文件） | — | **新增** 模块（~90 行，含 MAF 注意力减冗余） |
| `code/parse.py` | — | **新增** `--use_bypass --bypass_alpha_init --bypass_mode` |

---

## 2. 算法伪代码

### 2.1 模块 B — `CooccurrenceGraphBuilder`

```
# ---- 离线, __init__ 时构造一次 ----
function BUILD_COOC(R, k, min_count, mode):
    R_tR = (R.T @ R).tocsr()                 # sparse item-item, 不 densify (避 D4)
    rows, cols, vals = [], [], []
    for i in 0..n_items-1:
        r = R_tR.getrow(i)
        m = r.data > min_count               # 共同用户数 > 1
        idx, v = r.indices[m], r.data[m]
        if mode == 'binary': v = ones_like(v)
        if len(v) > k:
            thr = sort(v)[-k];               # 逐行 top-k
            keep = v >= thr; idx, v = idx[keep], v[keep]
        rows.extend([i]*len(idx)); cols.extend(idx); vals.extend(v)
    A_s = sparse(rows, cols, vals, (n_items, n_items))
    D_inv = diag(1/sqrt(A_s.sum(1)+eps))
    A_s_norm = D_inv @ A_s @ D_inv           # 对称归一 (MSCA Eq.4-6)
    return A_s_norm

# ---- 训练/推理, 每次 computer() 调用 ----
function ENCODE(A_s_norm, i_bar):
    E_struct     = A_s_norm @ i_bar                       # 1 层 GCN 结构视图 (Eq.5)
    E_struct_u   = normalize(R @ E_struct)                # 反投影: item→user (semantic_encode)
    return E_struct, E_struct_u
```

### 2.2 训练流程（A + B + C 协同，挂载到 `bpr_loss`）

```
# ===== LightGCNpp 训练步 =====
function TRAIN_STEP(users, pos, neg):
    # --- 1. 协同传播 (现有 computer) ---
    all_u, all_i, _u, _i = computer()          # _u/_i: 逐层 [n, L+1, d]
    embs_prop = mean(_i[:, 1:, :], dim=1)       # Ē_collab, 排除第 0 层 (对齐 MSCA Eq.1-3)
    u_bar, i_bar = split(embs_prop)             # 协同锚点

    # --- 2. 模块 B: 结构视图 (computer 内已缓存 self._struct) ---
    E_struct, E_struct_u = self._struct         # 来自 cooc_graph.encode

    # --- 3. 模块 C: 旁路加性注入 (E* = Ē_collab + α·Ê_view) ---
    if use_bypass:
        E_final = bypass_fuse.fuse(embs_prop, E_struct, modal_emb?)   # 覆盖 computer 返回
        all_u, all_i = split(E_final)            # 供评分使用

    # --- 4. BPR 主损失 (现有) ---
    bpr = mean(softplus(neg_score - pos_score))  # 用 all_u/all_i

    # --- 5. 模块 A: 协同锚定对比 (复用现有 InfoNCE L234-242) ---
    if use_cacl:
        L_c = InfoNCE(i_bar[batch], E_struct[batch], all_i, τ_c) \
            + InfoNCE(u_bar[batch], E_struct_u[batch], all_u, τ_c)
        if cacl_use_modal and has_mm:            # baby/sports 才走
            L_c += InfoNCE(i_bar[batch], E_modal[batch], all_i, τ_c) \
                 + InfoNCE(u_bar[batch], E_modal_u[batch], all_u, τ_c)
        bpr = bpr + cacl_reg * L_c

    # --- 6. 既有 idea1/idea2/idea3 损失 (不变) ---
    if use_cl:    bpr += cl_reg * neighbor_cl_loss(...)
    if use_mm:    bpr += mm_reg * mm_aligner.contrastive_loss(...) + cost_reg

    return bpr, reg_loss
```

### 2.3 推理流程

```
function INFER(users):
    all_u, all_i, _, _ = computer()            # 若 use_bypass, 内部已返回 E_final
    scores = sigmoid(all_u[users] @ all_i.T)   # 与现有 getUsersRating 完全一致
    return scores

# 注: 推理时模块 A(对比) 不激活; 模块 B/C 的视图与融合参数已固定, 零额外推理开销(除 1 层稀疏 GCN)。
```

---

## 3. 可行性说明

### 3.1 改动范围

| 模块 | 新增文件 | 改动文件 | 改动行数(估) | 依赖 |
|------|---------|---------|------------|------|
| B `cooc_graph` | `code/cooc_graph.py` (~120 行) | `model.py`(+15)、`parse.py`(+4)、`world.py`(+4) | ~145 | 无 |
| A `cacl` | `code/cacl.py` (~60 行) | `model.py`(+18)、`parse.py`(+4)、`world.py`(+4) | ~90 | 依赖 B 的 `E_struct` |
| C `bypass_fuse` | `code/bypass_fuse.py` (~90 行) | `model.py`(+20)、`parse.py`(+3)、`world.py`(+3) | ~120 | 依赖 B（及可选 idea2 模态） |

**总改动**：3 个新文件（~270 行）+ `model.py`/`parse.py`/`world.py` 增量约 60 行。与现有 idea1/2/3/P3 **完全正交**，均可通过 CLI flag 独立开关，形成 2⁴（含 P3）设计矩阵。

### 3.2 预期收益

| 模块 | 预期收益 | 证据支撑 |
|------|---------|---------|
| B | 为 5 个无 npy 数据集（lastfm/gowalla/ml-1m/yelp2018/amazon-book）提供**免费结构正则**，无需任何外部特征 | MSCA 在 Baby/Sports/Electronics R@20 0.1049/0.1210/0.0734 均超越最强基线，结构视图是核心贡献之一 |
| A | 对比学习更稳：锚点恒为协同信号，不随模态噪声抖动；在 sports 合成噪声特征上尤其安全 | 现有 idea2 跨模态对比在 sports 可能因噪声退化；A 不依赖模态 |
| C | 第三种注入位置，α 可学；与 pre/post-fuse 组合可系统搜索最优注入策略 | MSCA 报告 `E* = Ē + α·Ê` 形式在 3 数据集均最优；α 由 YAML 调（Baby 0.4/Sports 0.3/Electronics 0.2） |

**最稳首验组合**：`--use_cooc 1 --use_cacl 1 --use_bypass 0`（即 B+A，纯结构，不碰模态），在 sports 上验证结构视图增益，再叠加 C。

### 3.3 潜在风险与规避

| 风险 | 等级 | 规避 |
|------|------|------|
| **D4 复现**：共现矩阵 densify 爆内存（Electronics Q=63001 → 31.7 GB） | 🔴 高 | B 全程 `scipy.sparse` 逐行 top-k，**严禁 `.toarray()`**；已写入伪代码强制约束 |
| **C 与 idea2 双重注入冲突**：pre-fuse 已改 e⁽⁰⁾，C 又加 α·Ê_view 可能过强 | 🟡 中 | 默认 `--use_bypass 0`；开 C 时建议关 idea2（`--use_mm 0`）做 2×2 隔离实验 |
| **α 过大淹没协同信号** | 🟡 中 | α 初始化 0.3（取 MSCA Sports 值），配 `cacl_reg` 同量级；监控 `E_final` 与 `embs_prop` 余弦相似度 |
| **`E_struct_u` 反投影引入噪声**（用户侧共现稀疏） | 🟡 中 | 用户侧对比损失权重可用 `cacl_alpha`（复用 idea1 的 user/item 权重参数）下调 |
| **D1 公式退化**：若照抄 Eq.12–14 会得 `Ê=0` | 🔴 高(若照搬) | **不抄公式**，直接移植 MSCA 真实代码逻辑（跨视图 `(N,3)` Softmax 注意力），已在本提案 §1.3 与伪代码中明确 |
| **单种子无显著性（D9）** | 🟡 中 | 复验时用多 seed（如 [2020,999,42]）报告均值±std，不沿用 MSCA `seed:[999]` |
| **Sports `image_feat.npy` 为合成噪声** | 🟡 中 | A 的模态视图仅对 `amazon-baby-mmssl` 开启（`cacl_use_modal` 默认 0） |

---

## 4. 与现有 idea 的整合矩阵（落地路线）

```
                 use_mm(idea2)  post_mm_fuse(P3)  use_bypass(C)   use_cacl(A)   use_cooc(B)
Sports(无真模态)     0               0/1            0/1            1             1   ← 首验
Baby(真模态)         1               0/1            0/1            1(if modal)   1
lastfm/gowalla/      0               0             0/1            1             1   ← B 唯一价值点
 ml-1m/yelp/amazon-book
```

**建议提交顺序**：
1. **PR1**：`cooc_graph`（B）单独上线 → 在 5 无 npy 数据集验证结构图本身增益。
2. **PR2**：`cacl`（A）挂载 B → 验证协同锚定对比。
3. **PR3**：`bypass_fuse`（C）作为第三种注入位置 → 与 idea2/P3 做 2×2×2 消融。

---

## 5. 一键复验命令（示例）

```bash
cd baseline/LightGCNpp/code
# 首验: 纯结构 (B+A), sports 无模态噪声
python main.py --dataset amazon-sports --model lgn \
  --use_cl 1 --use_cacl 1 --use_cooc 1 --cooc_k 10 --cooc_min_count 1 --cooc_mode binary \
  --cacl_temp 0.2 --cacl_reg 0.005 --cacl_use_modal 0 \
  --layer 3 --lr 1e-3 --epochs 1000 --seed 2020

# baby 带模态 (A 开模态视图)
python main.py --dataset amazon-baby-mmssl --model lgn \
  --use_cl 1 --use_cacl 1 --use_cooc 1 --cacl_use_modal 1 \
  --use_mm 1 --use_bypass 0 \
  --layer 2 --cacl_reg 0.005 --cacl_temp 0.2 --seed 2020
```

> 注：超参参考 MSCA YAML 最优值（`tau=0.2, k=10, dim=64, batch=2048, lr=1e-3`），但**改多 seed 复验**以规避 D9；`cacl_reg` 默认对齐 MSCA `lambda1=0.005`。
