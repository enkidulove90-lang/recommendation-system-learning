# idea 实现问题盘点与修复（2026-08-05）

> 范围：`baseline/LightGCNpp/code/` 中 idea2（多模态对齐）/ idea3（成本感知）/ idea4（NLGCL）的运行时代码。
> idea1 自适应传播已放弃（Oracle 增益 +1.96% < 3% 阈值），不在本次范围。
> P6（PRISM MoE）按用户指示暂缓，本文档不触及其训练。

## 0. 当前实验状态（事实依据）

来自 `results_idea2_aggregated.json`（权威源 `logs/*.txt`）：

| 变体 | seed | R@20 | N@20 | 状态 |
|------|------|------|------|------|
| baseline | 2024 | 0.08416 | 0.04287 | done |
| baseline | 2025 | 0.07825 | 0.03995 | partial(2/4) |
| idea2 | 2024 | 0.08262 | 0.04231 | done（配对 baseline **-1.83%** R@20） |
| idea3 | — | — | — | **全部 missing**（后台重跑未完成） |

对齐诊断：`idea2` 的 `conf_mean = 0.088`（gate: image 0.288 / text 0.712）。
即 G3 置信门控只放行 **8.8%** 的多模态知识 → 多模态信号基本被掐断，这是 idea2 近零增益的直接线索。

此前把根因归结为"G3 温度参数（mt=0.1）"，但本次代码审查发现**更底层、更致命的根因**（见 Bug ①），温度只是次要因素。

---

## 1. 问题清单（按严重度排序）

### 🔴 Bug ①【致命】对齐器梯度冻结 —— idea2 失效的真正根因
**位置**：`mm_align.py` 的 `project()` epoch 级 detach 缓存。

**原代码**：
```python
def project(self, feats, epoch=None):
    if epoch is None: epoch = self._epoch
    if self._proj_cache is None or self._proj_epoch != epoch:
        fresh = self._compute_proj(feats)          # 仅此一次带梯度
        self._proj_cache = {t: v.detach() for t, v in fresh.items()}
        self._proj_epoch = epoch
        return fresh
    return self._proj_cache                         # 其余 batch 全 detach
```

**问题**：`set_epoch()` 每 epoch 只调用一次（main.py:80），于是**每 epoch 仅第 1 个 batch 的投影带梯度**，其余 16/17 个 batch 的投影是 `detach` 副本。这导致：
- `proj` 投影头、`gate_weights` 的 `type_emb`、`conf_mlp` 在每 epoch **99% 的 batch 上收不到梯度 → 对齐器等效被冻结**；
- 20 epoch 下来，对齐器基本没被训练 → `conf_mean` 卡在 0.088、门控退化为接近均匀、idea2 无增益。

**这才是 idea2 失效的真正根因**，比之前推测的"温度参数"更根本——温度最多让 c 偏移，但梯度都没回传，调温度毫无意义。

**修复**：`project()` 改为**每 batch 全量投影带梯度**（CPU 实测单 batch ≈ 413ms；17 batch × 20 epoch × 3 变体 ≈ +7min 总开销，单 seed 仅 +2min ≈ 3%，可接受）。`contrastive_loss` 仍用 `fuse()` 缓存的 `_last_proj_feats`（带梯度），正例也带梯度，对比损失现在能正常训练对齐器。

**验证**：单元测试确认 proj 头 / gate 原型 / conf_mlp **每个 batch 都收到梯度**（修复前仅第 1 个 batch 有）。

---

### 🟠 Bug ②【功能缺失】置信度判别正则从未接入 loss（死代码）
**位置**：`model.py` 读 `mm_conf_reg_w = config['mm_conf_reg']`，但 `bpr_loss` 从未使用；`mm_align.py` 的 `conf_reg()` 方法定义却从未被调用。

**问题**：设计意图是"防止 c 全趋于极端（0 或 1）"，但该正则实际**完全没进训练**。同时，由于 conf 已偏低（0.088），缺少这个把 c 往 0.5 拉的判别项，多模态知识更难进入 `e^(0)_item`。

**修复**：删除死方法 `conf_reg()`，在 `bpr_loss` 内联接线：
```python
if self.mm_conf_reg_w > 0:
    loss = loss + self.mm_conf_reg_w * (1.0 - torch.abs(2.0 * c - 1.0)).mean()
```
直接复用 `fuse()` 已缓存的 `conf_vec`，零额外计算。

---

### 🟡 Bug ③【效率/隐性成本】`bpr_loss` 二次全量图传播
**位置**：`model.py` 的 `bpr_loss`，当 `use_cl` 开启时第 284-288 行**再次调用 `self.computer()`**，而 `getEmbedding`（line 272）已调用过一次。

**问题**：每个训练 step 跑**两次**完整图传播 + 两次对齐器融合（2× 算力）。当 `use_mm` 也开时，第二次还会再跑一遍对齐器。纯属浪费，且让"对齐器已冻结"雪上加霜。

**修复**：`getEmbedding` 内置缓存逐层嵌入 `self._cl_embs_list`；`bpr_loss` 的 NLGCL 分支直接复用，不再二次 `computer()`。

---

### 🟡 Bug ④【设计缺陷】门控原型零初始化 → 门控退化为均匀平均
**位置**：`mm_align.py` `type_emb` 初始化 `nn.Parameter(torch.zeros(id_dim))`。

**问题**：`gate_weights` 里 `proto = F.normalize(type_emb)`，而 `normalize(0)=0` → 所有类型的门控打分 `sim` 恒为 0 → `softmax` 退化为**均匀平均**，"类型感知门控"名存实亡（图片与文本等权，无法突出信息密度高的类型）。

**修复**：`type_emb` 改为小幅随机初始化 `torch.randn(id_dim) * 0.1`，让各类型起步即有区分度，门控打分非退化。

---

### 🟡 Bug ⑤【自相矛盾】idea3 纯征税在 conf 已偏低时退化
**位置**：`model.py` idea3 原 `cost_loss = cost_reg * c.mean()`。

**问题**：idea3 的设计是"引入知识有成本，模型仅在收益足以抵消时才引入"。但实测 conf 已经只有 0.088（门控几乎不放行），再对 `c.mean()` 征税会把 conf 进一步压到 ≈0 → **idea3 退化为纯 baseline**，机制完全失去意义。

**修复**：重构为**预算式**成本（opt-in，向后兼容）：
```python
if self.cost_target > 0:
    cost_loss = self.mm_cost_w * (c - self.cost_target).pow(2).mean()   # 鼓励 c 稳定在目标值
else:
    cost_loss = self.mm_cost_w * c.mean()                               # 原纯征税语义
```
新增 `--cost_target`（默认 0 = 原语义）。设 `--cost_target 0.2` 即鼓励平均引入率稳定在 20%，既不过压也不过度放开。

---

### ⚪ Bug ⑥【遗留日志】`mm_new_epoch` 误打印
**位置**：`model.py` `mm_new_epoch` 末尾 `print("lgn is already to go(dropout:...)")`。

**问题**：原 LightGCN 遗留的 misplaced 日志，每次 epoch 打印一句与对齐器无关的废话，污染日志、干扰诊断。

**修复**：删除该行。

---

### ⚠️ 非 bug 但需知晓：NLGCL 的 `InfoNCE` 用 `.sum()` 而非 `.mean()`
**位置**：`model.py` `InfoNCE` line 236 `pos = torch.exp((v1*v2).sum(1)/tau)` → 返回 `-log(pos/ttl).sum()`。

**说明**：这是 NLGCL 论文约定（paper convention），已在注释中标注。但副作用是**对比损失量纲随 batch size 缩放**——`cl_reg` 实际效果依赖于 batch size。当前 `cl_reg=5e-5` 是按某 batch size 调好的；若改 batch size 需同步重调 `cl_reg`。**本次不变更**（改动会动到已验证的 +11.6% 结果），仅作提醒。

---

## 2. 修复验证

| 检查 | 结果 |
|------|------|
| `py_compile` model/mm_align/parse/world/main/run_idea2 | ✅ 全部通过 |
| 单元测试：对齐器 proj/gate/conf 每 batch 梯度 | ✅ 修复前仅 batch0 有梯度，修复后每 batch 都有 |
| 端到端冒烟：`amazon-baby-mmssl` 1 epoch `--use_mm 1 --cost_target 0.2` | ✅ `EPOCH[1/1] loss0.329`，EXIT=0，无报错 |

## 3. 修复后预期

1. 对齐器现在每 batch 都被训练 → `conf_mean` 应显著上升（判别正则把它往 0.5 拉），多模态知识真正进入 `e^(0)_item`。
2. idea2 的 R@20 有望从配对 -1.83% 转为正增益（需重跑 3 seed × 20 epoch 验证）。
3. idea3 用 `--cost_target 0.2` 预算式，应能看到"受控的知识引入率"，而非退化为 baseline。
4. 计算开销可控（+~3%/seed）。

## 4. 下一步建议（待用户定）

- **重跑 idea2 + idea3（用新代码）**：`python run_idea2.py --dataset amazon-baby-mmssl --only idea2` 与 `--only idea3 --cost_target 0.2`（3 seed × 20 epoch，后台并行）。
- 关键观察量：`conf_mean` 是否从 0.088 上升、idea2/idea3 配对增益是否转正。
- 若 conf 仍偏低，再回头调 G3 的 `conf_mlp` 偏置或门控温度（此时梯度已通，调参才有意义）。

> 注：之前后台启动的"正式重跑"实际未完整落盘（idea3 全空、seed2026 全空），应丢弃旧 `results_idea2_aggregated.json`，用新代码重跑后以 `logs/*.txt` 为准重新聚合。

---

## 5. ⚠️ 重要更正：v2 的"梯度修复"实际使问题恶化（已用 v3 替代）

### 5.1 v2 修复后的实测（2026-08-05 重跑）
按 v2（每 batch 全量带梯度投影）重跑 idea2/idea3（seed2024），关键信号反而更差：

| 版本 | BPR→proj 梯度步数 | InfoNCE→proj 梯度步数 | epoch5 conf_mean |
|------|------------------|----------------------|------------------|
| v0 原始（尺度失配） | 20 | 20 | 0.093 |
| v1 尺度修复 | 20 | 20 | 0.091 |
| **v2 本次（梯度修复）** | **0** | **1880** | **0.026 / 0.014** |

门控退化成 0.50/0.50（type_emb 失去区分度）。

### 5.2 根因（比"梯度冻结"更深一层）
v2 把 `project()` 改成每 batch 全量带梯度，但 `project()` 的结果**只喂给 `fuse()` 的图传播**，而 `fuse()` 内部走的是 `no_grad` 缓存（`mm_align.py` `project()` 的 `with torch.no_grad()`）——所以 **BPR 用的 `e^(0)_item` 对投影头零梯度**。
带梯度的 `project_subset()` 只接进了 `contrastive_loss`（InfoNCE，权重 `mm_reg=1e-3`）。于是：
- 投影头 100% 由权重仅 1e-3 的"图文一致性"目标驱动，与推荐目标正交；
- BPR 只能把门控 c 关得更死 → conf_mean 从 0.091 跌到 0.026。

即 v2 修掉了"20 epoch 只 20 步"的表层问题，却让 BPR→proj 从 20 步变成 **0 步**——比 v0/v1 更糟。

### 5.3 v3 修复（当前生效）
**核心思路**：复用已经算好的带梯度 `project_subset`（batch 子集），重算这批物品的 `e^(0)_item`，**拼回 `light_out` 的 `γ·embs_zero` 项**。这样 BPR 梯度沿直通路回到投影头，且复用同一次投影、零额外开销。

新增 `mm_align.py: fuse_subset(feats, id_emb, idx)`：
- 用 `project_subset`（带梯度）算 batch 子集投影 → G2 门控 + G3 置信融合；
- 返回带梯度的 `fused` 与逐物品 `c`；
- 把子集投影缓存，`contrastive_loss(idx)` 直接复用（不再二次 project_subset）。

`model.py: bpr_loss` 接线：
```
pos_emb = γ·fused_subset[pos] + (1-γ)·embs_prop[pos]   # embs_prop 取 computer() 无梯度传播项
neg_emb = γ·fused_subset[neg] + (1-γ)·embs_prop[neg]
# 用拼接后的 pos/neg 重算 BPR 项；NLGCL/InfoNCE/idea2-3 正则照常累加
```
`embs_prop[pos] = self._items[pos, 1:, :].mean(dim=1)`（`getEmbedding` 已缓存逐层 item 嵌入 `self._items`）。
(1-γ) 项无需投影头梯度（本来就是 no_grad 传播），(γ) 项承载 BPR→proj 梯度。

### 5.4 v3 验证（2026-08-05）
| 检查 | 结果 |
|------|------|
| `py_compile` model/mm_align/… | ✅ 全部通过 |
| 单元测试：BPR 路径下 proj(img/txt)/type_emb/conf_mlp 梯度 | ✅ 全部非零（proj:img=23.6, txt=17.8, type_emb=0.93, conf_mlp=3.14） |
| 索引形状 `self._items[pos,1:,:].mean(1)` | ✅ `[len(pos), d]`，`unique+inverse` 映射正确 |

> v2 的"每 batch 全量投影"实测在 `amazon-baby-mmssl` 上 +178%/epoch 不可接受；v3 改回"全量 no_grad 缓存 + batch 子集带梯度"（方案 D），开销回到 ~+20%/epoch，且 BPR 梯度通。

### 5.5 当前运行处置（2026-08-05）
- 正在跑的 v2 idea2/idea3（PID 10944 / 22200）**应停掉**——它们产退化结果，再跑 3.5h 也是废数据。
- **baseline（PID 14968）保留**——它 `use_mm=0`，不受对齐器 bug 影响，留作对照。
- 用 v3 代码重启（**在你自己的终端执行**，沙箱跨进程隔离，无法代 kill / 代启动）：
  ```bat
  :: 1) 停掉 v2 idea2 / idea3（保留 baseline 14968）
  taskkill /PID 10944 /F
  taskkill /PID 22200 /F
  :: 2) v3 重启
  python run_idea2.py --dataset amazon-baby-mmssl --only idea2 --epochs 20 --seeds 2024,2025,2026
  python run_idea2.py --dataset amazon-baby-mmssl --only idea3 --cost_reg 0.01 --cost_target 0.2 --epochs 20 --seeds 2024,2025,2026
  ```
- 关键观察：`conf_mean` 应从 0.026 **回升**（预期 0.3~0.7 区间），idea2/3 配对增益是否转正。若 conf 仍偏低，再回头调 G3 `conf_mlp` 偏置或门控温度（此时梯度已通，调参才有意义）。
