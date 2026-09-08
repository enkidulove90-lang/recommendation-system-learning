# 统一实验设计路线图（LightGCN++ / MMGCF-P3 / MSCA 三模块）

> ⚠️ **2026-08-06 更新：本文档的 Phase 0 已被 `docs/experiment_roadmap_v2.md` 取代。**
> E1/E2/E6 跑完后发现，Phase 0 门禁盯的 `conf_mean` 是个**被测错的量**——
> 图传播读 epoch 级投影缓存（c≈0.055），而预算/训练路径每 batch 新鲜（c≈0.823），两者不是同一个 c。
> 新地基是 `--mm_proj_refresh`；`--mm_eval_fresh` 已证伪。
> **Phase 1（MSCA B/A/C）、Phase 2（P3）、Phase 3、Phase 4 的设计仍然有效**，继续以本文档为准。

> 整合来源：
> - `docs/MMGCF_innovation_proposal.md`（P3 `post_mm_fuse` 尾融合，提案）
> - `docs/MSCA_innovation_proposal.md`（B 共现图 / A 协同锚定对比 / C 旁路加性注入，提案）
> - 现有 baseline：`baseline/LightGCNpp/code/`（idea1 NLGCL-H ✅、idea2 mm_align ✅+v3、idea3 cost_reg ✅）
> - 对话审计结论：v2 梯度修复反而让 BPR→投影头梯度归零（conf_mean 0.091→0.026），v3 已落地待训练验证；PRISM/P6 被 sports Pearson 0.9915 阻塞。

---

## 0. 三条不可违反的约束（决定整个设计）

**约束 A — v3 是 MM 模块的命脉，必须先验证**
idea2/3 的 `mm_align` 是所有多模态模块（P3 post-fuse、MSCA A 模态视图、C 模态分支）的共同底座。v2 在训练中不崩溃却让 BPR→投影头梯度=0 步，证明**"能跑通 + 无报错" ≠ 有效**。任何 MM 模块上线前，必须先确认 v3 让 `conf_mean` 从 0.026 回升到 0.3~0.7。

**约束 B — 数据集按 MM 真实性分级，模块只能吃对的数据**

| 数据集 | MM 真实性 | 能跑的模块 |
|--------|----------|-----------|
| `amazon-baby-mmssl` | ✅ 真图文（image 4096 + text 384） | 全部 MM 模块（idea2 / P3 / A-modal / C-modal） |
| `amazon-sports` | ⚠️ 仅 CLIP 真（`image_feat.npy` 是合成高斯噪声） | 结构模块 + idea1；MM 模块只能用 CLIP，**不能信 `image_feat`** |
| `amazon-book / gowalla / lastfm / ml-1m / yelp2018` | ❌ 零 npy | 仅结构模块（B/A-no-modal/C-struct）；这是 B 共现图的**唯一价值点** |

**约束 C — 每个新模块必须附带"梯度健康探针"单测**
v2→v3 的教训：新增模块必须写一个最小单测，断言 **BPR 梯度能流到该模块的可学参数**（proj 头 / α / W_f / cooc 结构参数）。仅 `py_compile` + 不崩溃 **不够**。探针同 `baseline/LightGCNpp/code/_test_v3_grad.py` 范式。

---

## 1. 数据集 × 模块 分配矩阵

```
                  baby-mmssl   sports       5-no-npy(lastfm/gowalla/ml-1m/yelp/amazon-book)
idea1 NLGCL-H        ✅          ✅            ✅
idea2 pre-fuse(MM)   ✅真图文     ⚠️仅CLIP      ❌无MM
idea3 cost_reg       ✅          ✅(依赖idea2) ❌
P3 post-fuse(MM)     ✅真图文     ⚠️仅CLIP      ❌
B cooc_graph         ✅          ✅            ✅   ← B 独有价值
A cacl(no-modal)     ✅          ✅            ✅
A cacl(modal)        ✅          ❌噪声         ❌
C bypass(struct)     ✅          ✅            ✅
C bypass(struct+modal)✅         ❌            ❌
PRISM/P6             ⚠️待PID校验  ❌Pearson0.99 ❌
```

---

## 2. 分阶段路线图

### Phase 0 — 地基验证（阻塞所有 MM 实验，~0.5 天）
**目标**：确认 v3 修复在训练中真的生效。

1. 在你的终端停掉 v2 退化进程（我的沙箱跨进程隔离无法 kill）：
   ```bat
   taskkill /PID 10944 /F   :: v2 idea2
   taskkill /PID 22200 /F   :: v2 idea3
   :: baseline(14968) 保留 —— use_mm=0，不受影响
   ```
2. 用 v3 重启 idea2 + idea3（重点盯 `conf_mean`）：
   ```bat
   python run_idea2.py --dataset amazon-baby-mmssl --only idea2 --epochs 20 --seeds 2024,2025,2026
   python run_idea2.py --dataset amazon-baby-mmssl --only idea3 --cost_reg 0.01 --cost_target 0.2 --epochs 20 --seeds 2024,2025,2026
   ```
**门禁（Definition of Done）**：
- `conf_mean` 从 0.026 **回升到 0.3~0.7**；
- 配对 R@20 增益从 -1.83% 转正或显著收窄；
- 若仍偏低 → 回 model.py 调 G3 `conf_mlp` 偏置 / 门控温度（此时梯度已通，调参才有意义）。
**未过门禁则 Phase 1/2 全部停摆**——因为 P3 与 MSCA 模态分支都复用 `mm_align`。

---

### Phase 1 — MSCA 结构模块（B + A + C）【最高性价比、最低风险，~3 天】
**为什么先做这个**：B/A/C 不依赖 MM 路径（约束 A 的 v3 尚未稳），且能在 5 个零-npy 数据集上产生**独有价值**（MM 模块做不到）。是论文最稳的增量。

**实现顺序（PR 拆分）**：
- PR1：`cooc_graph.py`（B）—— 全程 `scipy.sparse` 逐行 top-k，**严禁 `.toarray()`**（规避 D4 爆内存）。
- PR2：`cacl.py`（A）—— 协同锚定对比，复用现有 `InfoNCE`；`@grad探针` 断言 BPR 梯度到结构参数。
- PR3：`bypass_fuse.py`（C）—— `E* = Ē_collab + α·Ê_view`，α 可学。

**每个 PR 落地前必跑梯度探针单测**（约束 C）。

**实验矩阵（Tier-1 声明级 / Tier-2 论文级）**：

| 实验 | 内容 | 数据集 | seeds | Tier |
|------|------|--------|-------|------|
| 1.1 | 基线 E0（LightGCN++) + idea1 | sports/baby/gowalla/yelp | 3 | T1 |
| 1.2 | +B（共现图） | 同上 4 个 | 3 | T1 |
| 1.3 | +B+A（无模态） | 同上 4 个 | 3 | T1 |
| 1.4 | +B+A+modal（A 开模态） | baby 仅 | 3 | T1（验 A 模态分支） |
| 1.5 | +B+A on 5-no-npy 全量 | lastfm/ml-1m/amazon-book + 1.2 的 2 个 | 3 | T2 |
| 1.6 | +B+A+C（struct） | sports/baby | 3 | T2（第三种注入位置） |

> 命令范式（sports，纯结构）：
> ```bat
> python main.py --dataset amazon-sports --model lgn --use_cl 1 --use_cacl 1 --use_cooc 1 \
>   --cooc_k 10 --cooc_min_count 1 --cooc_mode binary --cacl_temp 0.2 --cacl_reg 0.005 --cacl_use_modal 0 \
>   --layer 3 --lr 1e-3 --epochs 1000 --seed 2020
> ```
> 变量 `mode`：sports/baby 用 `--cacl_use_modal 0`（sports 噪声、baby 已另有 idea2 承载模态）；5-no-npy 只能 0。

**门禁**：
- H1：sports 上 +B+A 的 R@20 > E0（≥0.111，逼近 MSCA 0.1210）；
- H2：5-no-npy 上 +B 给出正增益（证明纯交互结构图有效性）；
- H3：+C 的 α 收敛到 (0.2~0.4) 区间、不淹没协同（监控 `E_final` 与 `embs_prop` 余弦）。

---

### Phase 2 — MMGCF P3 尾融合【受 Phase 0 门禁约束，~2 天】
**目标**：验证"先传播后融合"优于"先融合后传播"（idea2）。

**实现**：`post_mm_fuse.py`（~150 行）+ `model.py` 接线（约束 C：BPR→α/W_f 梯度探针必过）。

**实验矩阵（只在 baby-mmssl 真图文上跑，绝不用 sports 的 `image_feat`）**：

| 实验 | 内容 | seeds | 目的 |
|------|------|-------|------|
| 2.1 | P3 单独（use_mm=0, post_mm_fuse=1, α+mean） | 3 | P0 可运行性 |
| 2.2 | 2×2：{use_idea2}×{post_mm_fuse} | 3×4=12 | **证 H1（post vs pre）** |
| 2.3 | weighting×fusion 网格（alpha/equal/normalized × mean/sum/concat）固定 use_idea2=1 | 3×9=27→压缩到 best-first 9 | 证 H2/H3 |
| 2.4 | +distill（post→pre KL） | 1~3 | 证 H3 平滑性 |

**门禁**：
- H1：`post_mm_fuse=1` 的 R@20 > `use_idea2=1` 单独，且在 baby 上 ≥0.140；
- H2：`alpha` > 0.5（ID 主导、MM 辅助），与 MMGCF 结论一致；
- α 训练后落在 [0.3,0.7]，不退化到 0/1（约束 R2，可加 `--post_mm_alpha_clip`）。

---

### Phase 3 — 集成消融（注入位置完整设计空间，~3 天）
把四个注入位置做成可独立开关的 CLI 维度，做阶乘消融：

```
注入位置设计空间（每个可 0/1）：
  pre-fuse   = idea2 (e⁽⁰⁾ 改造)
  post-fuse  = P3  (light_out ⊕ MM)
  bypass     = C   (Ē_collab + α·Ê_view)
  structural = B+A (共现图 + 协同锚定)
```
- baby（真 MM）：2×2×2 = 8 组合 × 3 seeds，找最优注入策略；
- sports（结构为主）：{structural}×{bypass}×{idea1}，MM 仅 CLIP 谨慎启用；
- 每个组合报告 R@20 / NDCG@20 + 训练时间倍率（门禁：≤ baseline ×1.2）。

**量纲纪律**：idea1 InfoNCE（`.sum()`）+ idea2 InfoNCE（`.sum()`）+ A 的 InfoNCE 同时开时，`.sum()` 让损失比 λ 大 ~batch_size 倍。**联合实验必须逐个开、逐一重校准 λ**（约束：先单开验证，再叠加）。

---

### Phase 4 — PRISM / P6【当前阻塞，不排期】
**阻塞条件**：sports 双特征 Pearson=0.9915 → PID 不可辨识（Unq=Syn=0），任何 PRISM 负结果都不能归因于方法。
**解锁步骤**：
1. 对 `amazon-baby-mmssl` 跑 `pid_diagnostic.py`（image 4096 vs text 384），确认 PID 可分离（Unq/Syn 非零）再碰 P6；
2. 若 baby 仍不可分 → 合成有 PID 结构的数据，或换 MMSSL 真实图文；
3. P6 专家层（128→64）必须每 batch 实算（套用 `mm_align.project()` 会回到 epoch 缓存→4 专家每 epoch 只更 1 步，训不动——与 v2 同坑）。

---

## 3. 统一实验纪律（每条都来自踩坑教训）

1. **梯度探针 mandatory**：每个新模块（P3 / B / A / C）必须附 `_test_*_grad.py`，断言 BPR 梯度到其可学参数；单测不过不允许启动训练。
2. **多 seed 防 D9**：所有汇报用 3 seeds [19, 42, 2024]，报 mean±std；不沿用 MSCA 单 seed [999]。
3. **监控健康探针而非只看 loss**：
   - idea2/3 → 盯 `conf_mean`（梯度健康度）；
   - P3 → 盯 `alpha` 是否偏离 init、是否落 [0.3,0.7]；
   - B/A → 盯结构对比 loss 是否下降、α 是否收敛。
4. **数据集分级严格执行**：MM 模块只在 baby；sports 的 `image_feat` 视为噪声，禁用；5-no-npy 只用 B/A/C-struct。
5. **组合爆炸压缩**：先 Tier-1（4 数据集声明级）跑通假设，再 Tier-2（全 7 数据集）补论文级；网格用 best-first 而非全扫。
6. **v3 优先于一切新模块**：Phase 0 门禁未过，不启动 Phase 1/2 的 MM 子实验。

---

## 4. 风险登记

| 风险 | 来源 | 缓解 |
|------|------|------|
| v3 训练仍无效（conf_mean 不回升） | idea2 底座 | Phase 0 门禁卡死；回 model.py 调 G3 偏置 |
| D4 共现矩阵爆内存 | MSCA B | 全程 sparse 逐行 top-k，禁 `.toarray()` |
| α 退化到 0/1 | P3 | `--post_mm_alpha_clip [0.1,0.9]` |
| 多 InfoNCE `.sum()` 量纲战争 | idea1/2/A 叠加 | 逐个开、逐一校准 λ |
| sports 噪声污染 MM 模块 | 数据 | 约束 B：sports 禁 `image_feat` |
| PRISM 被 Pearson 0.99 阻塞 | 数据 | Phase 4 先跑 pid_diagnostic |
| 双注入过强（idea2 + P3 + C） | 设计 | 2×2×2 隔离实验选最优，不默认全开 |

---

## 5. 一句话总览

> **先锁 v3（Phase 0）→ 再做不依赖 MM 的结构模块 B+A+C（Phase 1，5 个零-npy 数据集独有价值）→ 再上 MMGCF 尾融合 P3（Phase 2，只在 baby 真图文）→ 阶乘集成消融（Phase 3）→ PRISM 先解数据阻塞（Phase 4）。每条新模块附梯度探针单测，数据集严格按 MM 真实性分级。**
