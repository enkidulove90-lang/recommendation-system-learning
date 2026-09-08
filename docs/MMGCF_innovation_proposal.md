# MMGCF-Inspired 端融合 (Post-Propagation Fusion) 模块

> 来源：MMGCF (UMAP '26) + 本项目 `baseline/LightGCNpp/` (idea2 mm_align + idea1 NLGCL-H 已完成)
> 目标：把 MMGCF 的"尾融合"哲学落到 LightGCN++ 上, 与现有 idea1/idea2 协同而非替代
> 模块代号：**`post_mm_fuse`** (P3 = Post-propagation Multimodal Fusion)

---

## 0. 立项动机 (Why)

**MMGCF 论文主张**（§1）:
> "existing multimodal RSs often rely on highly sophisticated architectures ... the resulting performance gains are often marginalized by a substantial increase in computational overhead"
> "MMGCF augments LightGCN's item ID embeddings with multimodal signals using lightweight weighting and fusion mechanisms"

**本项目现状**:
- idea2 (`mm_align.py`) **先融合再传播**：物品 ID 嵌入先被 `MultiModalAligner` 改造, 再送入 LightGCN 图传播。
- idea1 (`nlgcl_module.py`) 已经在 ego 层做层间对比, 与图传播紧耦合。
- **从未测试过"先传播再融合"** —— 即 MMGCF 的 late-fusion 路线。
- 有多模态特征可用：`amazon-baby-mmssl/(image,text).npy`, `amazon-sports/(image,image_clip).npy`。
- LightGCN++ 在 `amazon-sports` 的 R@20 约 0.111（idea1 E0 起点）, 距离 MMGCF 报告的 0.1169 还有空间。

**核心假设 (可证伪)**:
> H1: 在稀疏数据集 (Sports 99.95%) 上, **post-propagation fusion 优于 pre-propagation fusion**, 因为 MM 特征不会在浅层图传播中被高频 ID 邻居淹没.
> H2: learnable α (MMGCF Eq.3) 优于固定权重, 但只在 post-fuse 设置下增益显著.
> H3: post-fuse 与 pre-fuse 的预测应当**近似**（若两者都学会"如何用 MM"）, 可用 KL 蒸馏做正则——论文没提, 是本提案的增量创新点.

---

## 1. 模块设计

### 1.1 模块名

**`post_mm_fuse`** —— 后置多模态融合 (Post-Propagation Multimodal Fusion)

### 1.2 作用

在 LightGCN++ 完成 K 层图传播之后, 把 K 层的 `items_emb` (经过聚合) 与多模态特征投影做**加权融合**, 输出最终的 `items_emb_final` 供 BPR loss 使用.

**与 idea2 (pre-fuse) 的对比**:

| 阶段 | idea2 (pre-fuse) | post_mm_fuse (本提案) |
|------|-----------------|----------------------|
| 1. 多模态投影 | ID 嵌入 + α·MM_proj | 先传播, 再投影加权 |
| 2. 送入 GCN | fused_emb 进入传播 | ID 嵌入独立传播 |
| 3. 输出 | K 层聚合结果 | K 层聚合 ⊕ MM_proj 加权 |
| 4. 训练目标 | BPR + contrastive(MM-views) | BPR + 可选 distillation |

### 1.3 输入/输出

| 接口 | 张量 | 含义 |
|------|------|------|
| 输入 (训练 & 推理) | `ego_items: Tensor[n_items, d]` | GCN 传播后物品 ID 嵌入 |
| 输入 (训练 & 推理) | `mm_proj_items: Tensor[n_items, d]` | 多模态特征投影（独立 LazyLinear 头, **不**与 GCN 共享梯度） |
| 输入 (推理 only) | `conf: Tensor[n_items]` (可选) | 来自 idea2 mm_aligner 的置信度 |
| 输出 | `items_final: Tensor[n_items, d]` | 加权融合后的物品嵌入, 用于 BPR 评分 |

### 1.4 流程位置

```
训练/推理主循环 (main.py):
  ↓
[已有] getEmbedding(users, items)
  ├─ 传播 K 层 LightGCN
  └─ 产出 ego_users, ego_items
  ↓
[本提案] post_mm_fuse.fuse(ego_items, mm_proj_items, mode)  ← 插入此处
  └─ 产出 items_final
  ↓
[已有] bpr_loss(ego_users, items_final[batch]) + 蒸馏项 (可选)
```

**与现有代码的接入点**:

| 文件 | 位置 | 改动类型 |
|------|------|----------|
| `code/model.py` `Model.forward` (L191-205) | `getEmbedding` 返回后 | **插入** `items_final = self.post_mm_fuse(ego_items, mm_proj_items)` |
| `code/model.py` `Model.__init__` (L120-145) | 紧跟 `mm_aligner` 实例化后 | **新增** `self.post_mm_fuse = PostMMFuse(...)` |
| `code/model.py` `Model.bpr_loss` (L302-330) | `items_emb = self.embedding_item.weight` 替换 | **改写** 为用 `items_final[batch_idx]` |
| `code/parse.py` | 新增 5 个 CLI 参数 | **新增** `--post_mm_fuse --post_mm_alpha_init --post_mm_temp --post_mm_distill --post_mm_distill_w` |
| `code/world.py` (config 注入) | 同 use_mm 模式 | **新增** 同名 config key |
| `code/dataloader.py` | 无需改 | 复用 idea2 已有的 `_load_mm_feats` |
| `code/post_mm_fuse.py` (新文件) | 新建 | **新增** 模块实现 (~150 行) |

### 1.5 与其他 idea 的关系

- **idea1 (NLGCL-H)**: 在 ego 层做, 与 post-fuse **正交**。本提案不动 `nlgcl_module.py`。
- **idea2 (mm_align)**: 仍在传播**前**给 ID 嵌入加 MM 增益。本提案在传播**后**再加一次融合。两者**并存**时是"双重注入", 可通过 `--post_mm_fuse 0` 关掉, `--use_mm 0` 关掉 idea2, 形成 2×2 设计矩阵.
- **idea3 (cost_reg)**: 借用同一套 conf_vec, 不重复实现.

---

## 2. 算法伪代码

### 2.1 PostMMFuse 模块 (前向)

```text
class PostMMFuse(nn.Module):
    init(latent_dim, n_modalities, weighting='alpha', fusion='mean', alpha_init=0.5):
        # weighting 模式
        if weighting == 'equal':
            self.alpha = None                     # 标量, 不学习
        elif weighting == 'alpha':
            self.alpha = nn.Parameter(torch.tensor(alpha_init))  # sigmoid 后∈[0,1]
        elif weighting == 'normalized':
            self.alpha = None                     # 用 1/M 缩放

        # fusion 模式
        if fusion == 'mean':
            self.fuse = lambda x: x.mean(0)      # 沿 modality 轴
        elif fusion == 'sum':
            self.fuse = lambda x: x.sum(0)
        elif fusion == 'concat':
            self.W_f = nn.Linear(M*d, d)         # 投影回 d
            self.fuse = lambda x: self.W_f(torch.cat(x, -1))

    forward(ego_items, mm_proj_list, conf=None):
        # mm_proj_list: List[Tensor[n_items, d]] 各模态独立投影
        # conf: Optional[Tensor[n_items]] idea2 置信度, ∈[0,1]
        if self.weighting == 'equal':
            ids = ego_items
            mms = self.fuse(mm_proj_list)
            ids_w = ids
            mms_w = mms
        elif self.weighting == 'alpha':
            a = torch.sigmoid(self.alpha)
            ids_w = a * ego_items
            mms_w = (1 - a) * self.fuse(mm_proj_list)
        elif self.weighting == 'normalized':
            ids_w = len(mm_proj_list) * F.normalize(ego_items, dim=-1)
            mms_w = F.normalize(self.fuse(mm_proj_list), dim=-1)

        # 可选置信度门控 (idea2 conf)
        if conf is not None:
            # 让 conf 低的物品回退到纯 ID
            mms_w = conf.unsqueeze(-1) * mms_w

        # 融合: 默认 mean, 论文 mean > concat/sum
        items_final = 0.5 * (ids_w + mms_w)
        return items_final
```

**关键设计**:
- `mm_proj_list` 是**预计算缓存**（与 idea2 的 `mm_aligner.set_epoch` 一致）, 不在 GCN backward 中重新投影, 避免显存爆炸.
- `alpha` 标量参数在 `[0,1]` 由 sigmoid 保证, 与 MMGCF Eq.3 完全一致.
- 推理时 `model.eval()` 锁定 `alpha` 与 `mm_proj`, 无额外开销.

### 2.2 训练流程伪代码

```text
输入: train_edges, MM_feats {m1..MK}, hyperparams
初始化: ego_items = item_id_embedding  (n_items, d)
       mm_proj_cache = LazyLinear(m1) | LazyLinear(m2) | ...   # K 头, 共享 d
       post_mm_fuse = PostMMFuse(weighting, fusion, alpha_init)
       mm_aligner = MultiModalAligner(...)   # idea2, 可关
       alpha_distill = 0 或 1               # 是否开蒸馏

每个 epoch:
    mm_new_epoch()                          # idea2 刷新缓存
    mm_aligner.set_epoch(e)                 # 同步 idea2 缓存

    每个 batch (u, pos, neg):
        # ---- 1. GCN 传播 (保持不变) ----
        embs_list = getEmbedding()         # K+1 个 (n, d) 嵌入
        ego_users, ego_items = embs_list[0][users], embs_list[0][all_items]

        # ---- 2. 准备多模态投影 (本提案新增) ----
        mm_proj_list = [proj(feats[k]) for k in 1..K]  # 复用 mm_aligner proj 头 or 新增
        # 注: idea2 已用 LazyLinear, 可直接复用 (detached) 或新增

        # ---- 3. 后置融合 (本提案新增) ----
        items_post = post_mm_fuse(ego_items, mm_proj_list)  # (n_items, d)

        # ---- 4. 蒸馏项 (可选, 本提案新增) ----
        if alpha_distill:
            # 用 pre-fuse (idea2) 的预测做教师, post-fuse 做学生
            with torch.no_grad():
                items_pre = idea2_fused_teacher(ego_items)  # idea2 当前输出
            # KL: 让 post-fuse 趋近 pre-fuse, 防 drift
            distill_loss = F.kl_div(
                F.log_softmax(items_post @ ego_users.T, dim=-1),
                F.softmax(items_pre @ ego_users.T, dim=-1),
                reduction='batchmean'
            )
        else:
            distill_loss = 0

        # ---- 5. BPR (改写) ----
        bpr = -log σ(items_post[pos] @ ego_users - items_post[neg] @ ego_users)

        # ---- 6. idea1 NLGCL (不变) ----
        if use_cl:
            cl = nlgcl_neighbor_cl_loss(embs_list, ...)

        # ---- 7. 总损失 ----
        L = bpr + cl_reg * cl + post_mm_distill_w * distill_loss

        L.backward()
        optimizer.step()
```

**关键设计选择**:
- **不**用 `mm_aligner.contrastive_loss` 重新算视图对比 —— idea2 已经在自己的 epoch 级循环里算了。本提案**只**算蒸馏, 不重复对比损失.
- `mm_proj_list` 用 `with torch.no_grad()` 包装可节省显存（idea2 proj 头只通过它自己的 cl_loss 学习）, 但**会牺牲 post-fuse 对 MM 特征的自适应能力**。所以默认**有梯度**, 通过 `freeze_mm_proj` 开关控制.
- `distill_loss` 在 R1~R8 阶段不开启, 等 P0 baseline 跑稳再加.

### 2.3 推理流程

```text
输入: ego_items, mm_proj_cache (freeze)
输出: items_post

1. mm_proj_list = cache（已无梯度）
2. items_post = post_mm_fuse(ego_items, mm_proj_list)
3. score[u, i] = ego_users[u] @ items_post[i]
4. topK 排序
```

**推理时**:
- `alpha` 已经是常数（sigmoid 后）, 不需要重新计算.
- 关闭 distill, 关闭 NLGCL, 关闭 mm_aligner.contrastive_loss.
- 总额外耗时 ≈ 1 个 `items_post = 0.5 * (a*ego + (1-a)*mm_proj)` —— 几乎免费.

---

## 3. 接入点代码 (示意, 不含完整实现)

### 3.1 `code/post_mm_fuse.py` (新文件, ~150 行)

```python
"""post_mm_fuse.py — P3: Post-Propagation Multimodal Fusion

设计来源: MMGCF (UMAP '26) §2 weighting+fusion + 本项目 docs/lightgcnpp_roadmap_status.md
核心原则: 在 LightGCN++ 传播完成后, 复用 MMGCF Eq.3-7 的 3×3=9 种组合,
          让 idea2 (pre-fuse) 与 post-fuse 并存, 形成 2×2 设计矩阵.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class PostMMFuse(nn.Module):
    def __init__(self, latent_dim, n_modalities,
                 weighting='alpha', fusion='mean', alpha_init=0.5,
                 use_conf=False):
        super().__init__()
        self.weighting = weighting
        self.fusion = fusion
        self.use_conf = use_conf

        if weighting == 'alpha':
            self.alpha = nn.Parameter(torch.tensor(alpha_init))
        if fusion == 'concat':
            self.W_f = nn.Linear(n_modalities * latent_dim, latent_dim)

    def forward(self, ego_items, mm_proj_list, conf=None):
        # 1. 模态融合
        if self.fusion == 'mean':
            mm = torch.stack(mm_proj_list, dim=0).mean(0)
        elif self.fusion == 'sum':
            mm = torch.stack(mm_proj_list, dim=0).sum(0)
        elif self.fusion == 'concat':
            mm = self.W_f(torch.cat(mm_proj_list, dim=-1))
        else:
            raise ValueError(self.fusion)

        # 2. 加权
        if self.weighting == 'equal':
            ids_w, mm_w = ego_items, mm
        elif self.weighting == 'alpha':
            a = torch.sigmoid(self.alpha)
            ids_w, mm_w = a * ego_items, (1 - a) * mm
        elif self.weighting == 'normalized':
            ids_w = len(mm_proj_list) * F.normalize(ego_items, dim=-1)
            mm_w = F.normalize(mm, dim=-1)
        else:
            raise ValueError(self.weighting)

        # 3. 可选置信度门控
        if self.use_conf and conf is not None:
            mm_w = conf.unsqueeze(-1) * mm_w

        return 0.5 * (ids_w + mm_w)
```

### 3.2 `code/model.py` 改动 (伪 diff)

```python
# __init__ (L120-145 后追加)
+ from post_mm_fuse import PostMMFuse
  if self.use_mm:
      # ... 已有 idea2 初始化 ...
+     self.post_mm_fuse = PostMMFuse(
+         latent_dim=self.latent_dim,
+         n_modalities=len(self.dataset.mm_feats),
+         weighting=self.config.get('post_mm_weighting', 'alpha'),
+         fusion=self.config.get('post_mm_fusion', 'mean'),
+         alpha_init=self.config.get('post_mm_alpha_init', 0.5),
+         use_conf=self.config.get('post_mm_use_conf', 0),
+     ).to(world.device)
+     self.post_mm_distill_w = self.config.get('post_mm_distill_w', 0.0)
+ else:
+     self.post_mm_fuse = None

# forward (L191-205) 改写
  def getEmbedding(self):
      # ... 已有 GCN 传播 ...
+     if self.use_mm and self.post_mm_fuse is not None:
+         mm_proj_list = [self.mm_aligner.project(feats[k], ids)
+                         for k, feats in self.dataset.mm_feats.items()]
+         items_post = self.post_mm_fuse(ego_items, mm_proj_list,
+                                        conf=getattr(self, '_last_conf', None))
+         ego_items = items_post
      return ego_users, ego_items

# bpr_loss (L302-330) 把 self.embedding_item.weight 替换为 ego_items[batch_idx]
```

### 3.3 `code/parse.py` 新增 5 参数

```python
parser.add_argument('--post_mm_fuse', type=int, default=0,
    help='P3: enable post-propagation multimodal fusion (0=off, 1=on)')
parser.add_argument('--post_mm_weighting', type=str, default='alpha',
    choices=['equal','alpha','normalized'])
parser.add_argument('--post_mm_fusion', type=str, default='mean',
    choices=['mean','sum','concat'])
parser.add_argument('--post_mm_alpha_init', type=float, default=0.5)
parser.add_argument('--post_mm_distill_w', type=float, default=0.0,
    help='distillation loss weight from pre-fuse teacher (0=off)')
```

---

## 4. 可行性说明

### 4.1 改动范围 (LOC 估算)

| 文件 | 新增行 | 改写行 | 风险 |
|------|-------|-------|------|
| `code/post_mm_fuse.py` | 150 | 0 | 低 (新文件) |
| `code/model.py` | 30 | 15 | 中 (forward 是热点) |
| `code/parse.py` | 15 | 0 | 低 (CLI) |
| `code/world.py` | 5 | 0 | 低 (config) |
| `code/dataloader.py` | 0 | 0 | 无 |
| `code/main.py` | 5 | 0 | 低 (config tag) |
| **合计** | **~205** | **~15** | — |

**编码时间预估**: 0.5~1 人天（含单元测试）.

### 4.2 实验设计 (2×2×3×3 网格)

| 维度 | 取值 |
|------|------|
| use_idea2 (pre-fuse) | {0, 1} |
| post_mm_fuse (本提案) | {0, 1} |
| weighting | {equal, alpha, normalized} |
| fusion | {mean, sum, concat} |
| 数据集 | {amazon-sports, amazon-baby-mmssl} (有 MM 特征) |
| seed | {19, 42, 2024} (3 seeds) |

**总实验数**: 2 × 2 × 3 × 3 × 2 × 3 = **216** —— 不现实。压缩为：

- **Phase A (P0)**: 验证 post-fuse 可运行, 在 amazon-sports 上与 E0 (idea1+idea2) baseline 对照, 只跑 `alpha+mean` 一种组合 ×3 seeds = 3 runs.
- **Phase B (P1)**: 在 P0 之上扫 weighting × fusion, 固定 `use_idea2=1`（保持协同）, 3×3=9 runs × 2 数据集 = 18 runs.
- **Phase C (P2)**: 关掉 idea2, 单独跑 post-fuse, 9 runs × 2 数据集 = 18 runs, **证 H1**.
- **Phase D (P3)**: 加入 distill, 验证 idea2 蒸馏是否帮助 post-fuse 收敛, 1 run.
- **总计**: 40 runs ≈ 2~3 天（每 run 假设 1 小时, amazon-sports 实际每 epoch 几秒）.

**预期收益**:
- **若 H1 成立**: 在 Sports 上 R@20 应能逼近 0.115-0.120 区间, 与 MMGCF 报告 0.1169 同量级.
- **若 H2 成立**: `alpha` 的最优值应大于 0.5 (ID 主导, MM 辅助), 与 MMGCF "alpha > equal" 结论一致.
- **若 H3 成立**: 蒸馏开启后, post-fuse 的训练曲线更平滑, 最终指标提升 1-2%.

### 4.3 风险与缓解

| 风险 | 描述 | 缓解 |
|------|------|------|
| R1: OOM | `mm_proj_list` 在 full-batch 投影时占用显存 | 复用 idea2 的 `mm_aligner.set_epoch` 缓存模式, 一次性算完 detach; 提供 `--freeze_mm_proj` 开关 |
| R2: 数值不稳定 | alpha 收敛到 0 或 1, 退化为纯 ID / 纯 MM | 加 `--post_mm_alpha_clip` (默认 [0.1, 0.9]) 显式约束 |
| R3: idea1 退化 | post-fuse 改 ego_items, 可能让 NLGCL-H 拿不到 ego 嵌入 | 在 `forward` 末尾用 `ego_items_post = self.post_mm_fuse(ego_items_pre, ...)`, NLGCL 仍用 `ego_items_pre`（detached 缓存） |
| R4: 与 idea2 双注入冗余 | 两次融合可能让 MM 信号过强 | 2×2 设计矩阵显式对比, 选最优组合; 不在产品代码中默认开启两者 |
| R5: Sports 已有"伪特征"问题 | `image_feat.npy` 余弦均值 0.0001 (高斯合成), text 真实 | 与 idea2 共用 `mm_feats`, 实验结果会反映这个事实; 若有真实 MMSSL features 替换可一并收益 |
| R6: 训练时间翻倍 | 后置融合 + idea2 前置融合 = 两次 LazyLinear 投影 | 用 `--post_mm_share_proj 1` 开关, 让 post-fuse 复用 idea2 的 proj 头 (weight-tying) |
| R7: 推理延迟 | alpha 标量 + 一次 add, 几乎免费 | 实测增加 <1ms (per-user) |
| R8: 论文-代码数据不一致 (继承自 MMGCF 仓库) | amazon-sports 是真实特征, 但 baby-mmssl 才是 MMSSL 真实特征 | 严格用 amazon-baby-mmssl 做主实验, sports 做辅助验证 |

---

## 5. 与 MMGCF 论文的边界声明

**本提案借鉴**:
- MMGCF Eq.3 (sigmoid α 加权) — `alpha` 参数化.
- MMGCF Eq.4 (L2 normalize + 1/M 缩放) — `normalized` 加权.
- MMGCF Eq.5/6/7 (mean/sum/concat fusion) — `fusion` 参数.
- MMGCF Table 3 消融模式 — 实验设计.

**本提案不复制**:
- 不复制 MMGCF 的 `train_full.txt` 切分（沿用 LightGCN++ 现有 train/val/test）.
- 不复制 MMGCF 的 `lambda_reg=1e-4` 硬编码（沿用 `config['reg_weight']`）.
- 不复制 MMGCF 的 `torch.compile`（沿用 LightGCN++ 现有 `world.args.compile`）.
- 不复制 MMGCF 的 `L2 normalize 在投影前` (idea2 已有自己的 normalize, 沿用).
- 不复制 MMGCF 的 `1:1 随机负采样` (沿用 LightGCN++ `dataloader.sample_negs`).

**本提案的增量**:
- **post-fuse + pre-fuse 双注入的 2×2 矩阵** (MMGCF 论文没有 pre-fuse 路径, 本项目有).
- **置信度门控** (idea2 conf 复用, MMGCF 没有).
- **蒸馏正则** (post→pre, 论文没提).
- **与 NLGCL-H 协同** (paper 没有对比学习基线).

---

## 6. 评估指标

| 指标 | 目标 | 报告 |
|------|------|------|
| Recall@20 (Sports) | ≥ 0.115 (≥MMGCF) | `results/post_mm_*_sports.json` |
| Recall@20 (Baby) | ≥ 0.140 (idea2 baseline) | `results/post_mm_*_baby.json` |
| NDCG@20 (Sports) | ≥ 0.054 | 同上 |
| 训练时间/epoch | ≤ LightGCN++ × 1.2 | `results/time_per_epoch.json` |
| 参数量 | ≤ +1.5K (alpha 1 + W_f 768×64 ≈ 49K 取决于 d) | 脚本自动打印 |
| 推理延迟 (top-20, 6K users) | ≤ +5ms | torch.profiler 测 |

---

## 7. 验收清单 (Definition of Done)

- [ ] P0 (P3 单独开启, alpha+mean, Sports) Recall@20 ≥ 0.105 (idea1 起点)
- [ ] P0 alpha 在训练后处于 [0.3, 0.7] 区间 (不退化)
- [ ] P1 9 组合中 best ≥ P0 (验证 weighting×fusion 网格有效)
- [ ] P2 关闭 idea2 后 post-fuse 仍 ≥ 0.105 (证 H1)
- [ ] P3 distill 开启后曲线更平滑 (方差 < baseline)
- [ ] 训练时间 ≤ idea1+idea2 × 1.2
- [ ] 推理延迟 ≤ idea1+idea2 × 1.05
- [ ] 文档同步: `docs/lightgcnpp_roadmap_status.md` 追加 P3 章节
- [ ] memory log: `.workbuddy/memory/2026-08-06.md` 追加 P3 进展

---

## 8. 一句话总结

> **post_mm_fuse 是 MMGCF "尾融合"哲学的 LightGCN++ 实现, 关键创新在于与现有 idea2 (pre-fuse) 形成 2×2 设计矩阵, 给出"双注入 vs 单注入" 的可证伪对比. 改动 ~220 行, 40 实验 ~ 3 天, 预期在 Sports 上 R@20 追平 MMGCF 0.1169.**
