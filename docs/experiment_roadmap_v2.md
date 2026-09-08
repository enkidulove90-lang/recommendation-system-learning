# 实验路线图 v2（2026-08-06 修订）

> 取代 `docs/experiment_design.md`（v1）的 Phase 0 部分，其余 Phase 保留但重新排序。
> v1 写于 idea2 的 v3 梯度修复"待验证"时期；E1/E2/E6 跑完后，**v1 的 Phase 0 门禁定义已经失效**——
> 它把 `conf_mean` 回升当作目标，而实测证明 `conf_mean` 本身是个**被测错的量**。

---

## 0. 现状快照（全部为实测，非估计）

### 0.1 已完成实验（amazon-baby-mmssl，20 epoch，3 seed，R@20）

| 实验 | 机制 | R@20 均值 | vs 纯 ID | conf_mean | 结论 |
|------|------|----------|---------|-----------|------|
| baseline | 纯 ID LightGCN++ | 0.08362 | — | — | 对照 |
| **E1 fc0.8** | `force_c=0.8` 冻结融合权重 | **0.08798** | **+5.2%** | 0.8（常数） | **多模态特征确实有用** |
| E1 fc1.0 | 全用多模态 | 0.08719 | +4.3% | 1.0 | 略逊于 0.8 |
| E1 fc0.3 | 少量多模态 | 0.08507 | +1.7% | 0.3 | 单调性成立 |
| E2 | `mm_conf_reg=0`，c 自由学 | 0.08471 | +1.3% | **0.0057** | c 塌缩，软正则**不是**元凶 |

E2 的 conf 轨迹（三 seed 逐点重合）：`0.385 → 0.161 → 0.042 → 0.006`，
而 R@20 反而同步上升 `0.0757 → 0.0808 → 0.0833 → 0.0847`。
**即：BPR 的局部梯度主动丢弃多模态，且丢弃过程中指标还在涨。**
这是本课题的核心矛盾——全局最优（c=0.8 → 0.088）与局部梯度方向（c→0 → 0.085）不一致。

### 0.2 阻断级发现：被约束的 c 和被使用的 c 不是同一个（2026-08-06 18:40 定位）

E6 用增广拉格朗日把 `mean(c)` 顶到 0.8，日志显示 `batch_c=0.823`，看似成功。但：

```
训练/预算路径：  fuse_subset() → project_subset()   每 batch 新鲜   → c ≈ 0.82   ← 预算约束的是这个
图传播路径：     fuse()        → project()          epoch 级缓存    → c ≈ 0.055  ← 模型真正用的是这个
```

`project()` 的投影缓存**每个 epoch 只刷新一次**，而预算每个 batch 都在推投影头。
两条路径永远追不上（实测 graph c≈0.055 vs budget batch_c≈0.823）。
**结论：E6 约束的是一个图传播根本没用到的影子变量。**

### 0.3 `--mm_eval_fresh` 已被证伪（不要再用）

第一版补丁想在 eval 前刷新缓存来"对齐口径"，实测**加重了问题**：
模型在 c≈0.06 的传播下训练，却在 c≈0.83 下被打分 → 训练/评测失配，
R@20 从 0.06968 掉到 0.05775（valid 同步掉、loss 同步升）。
`parse.py` 已把该开关标记为 `[DISPROVEN - keep 0]`，仅保留作 A/B 证据。

**真正的修复是 `--mm_proj_refresh K`**：训练途中每 K 个 batch 同步一次全量投影缓存，
让两条路径始终一致，eval 无需任何事后补丁。建议 K=32（94 batch/epoch，约 +7.5s/epoch）。

### 0.4 ⚠️ 当前正在跑的 E6 队列是无效的

`run_e6_budget.sh`（17:50 定稿，17:57 启动）在 `run()` 里**对所有 9 个 run 硬编码了 `--mm_eval_fresh 1`**，
而证伪结论是 18:40 才得出的。因此：

- 队列里 9 个 run × 20 epoch（ETA 次日 01:00）全部建立在已证伪的开关上；
- 已产出的 seed2024 正是教科书式的失配曲线：ep5 R@20=0.06968 → ep10 **0.05775**（越训越差）；
- 更糟的是 **代码版本在实验中途被改**：seed2024/2025 跑的是 18:41 之前的 `model.py`，
  seed2026 会跑之后的版本 → 同一 arm 内混了两个代码版本，3-seed 均值不可用。

> **建议：中止当前队列，等 `seed9997` 的 `--mm_proj_refresh 32` 冒烟出结果后按 §2 重启。**

### 0.5 代码资产盘点

| 模块 | 状态 | 备注 |
|------|------|------|
| `mm_align.py`（idea2 pre-fuse） | ✅ | 含 `refresh_proj()` / `diag_fresh_conf()` |
| `force_c` / `mm_conf_reg` / `cost_reg` | ✅ | E1 / E2 / idea3 |
| `mm_budget` + 对偶上升（E6） | ✅ | 双侧 clip，可双向控 c |
| `mm_proj_refresh`（真修复） | ✅ 冒烟中 | seed9997，5 epoch |
| `mm_eval_fresh` | ⛔ 证伪 | 保留作 A/B 证据 |
| `cooc_graph.py`（MSCA-B） | ❌ 未实现 | v1 Phase 1 |
| `cacl.py`（MSCA-A） | ❌ 未实现 | v1 Phase 1 |
| `bypass_fuse.py`（MSCA-C） | ❌ 未实现 | v1 Phase 1 |
| `post_mm_fuse.py`（MMGCF-P3） | ❌ 未实现 | v1 Phase 2 |

CLI 里**没有** `--use_cacl / --use_cooc / --post_mm_fuse`——v1 文档 §Phase1 的命令范式目前跑不通，属提案而非现状。

### 0.6 数据集（与 v1 一致，已复核）

| 数据集 | npy | 可跑模块 |
|--------|-----|---------|
| `amazon-baby-mmssl` | image 4096 + text 384（真） | 全部 MM 模块 |
| `amazon-sports` | 2 个，但 `image_feat.npy` 是合成高斯噪声 | 结构模块；**MM 禁用 image_feat** |
| `amazon-book / gowalla / lastfm / ml-1m / yelp2018` | 0 | 仅结构模块 ← B 的独有价值 |

---

## 1. 三条结论驱动的路线调整

**结论 1｜"c 塌缩"不是 bug，是 BPR 的理性选择。**
E2 证明去掉正则 c 照样塌，且塌的过程中指标在涨。所以不该继续"想办法让 c 别塌"（v1 Phase 0 思路），
而应该问：**为什么全局 c=0.8 更好，但局部梯度却指向 c=0**。这是个优化路径问题，不是正则强度问题。

**结论 2｜在 §0.2 修复前，任何 MM 实验结果都不可信。**
包括 E6 全部、以及所有依赖 `mm_align` 的下游模块（P3 尾融合、MSCA-A 模态分支、MSCA-C 模态分支）。
**这是新的 Phase 0 门禁。**

**结论 3｜靶子是 0.08798（E1 fc0.8），不是 baseline。**
自适应门控要有意义，必须打赢"把 c 冻死在 0.8"这个极其简单的对照。目前没有任何一档做到。

---

## 2. Phase 0'（新地基）— 投影同步 + E6 重测

**阻塞级，先于一切。**

### Step 0.1 冒烟确认（进行中，seed9997）
判据：`graph c` 与 `batch_c` 差距 < 0.05（此前 0.055 vs 0.823）。

### Step 0.2 E0-refresh 回归重测（**必做，容易被跳过**）
`mm_proj_refresh` 改变了 idea2 的训练动力学，所以 **E1/E2 的旧结论也必须在新口径下复测**，
否则新旧数字不可比：

| run | 命令要点 | 目的 |
|-----|---------|------|
| R1 | `--force_c 0.8 --mm_proj_refresh 32` | 新口径靶子（取代 0.08798） |
| R2 | `--mm_conf_reg 0 --mm_proj_refresh 32` | 新口径下 c 还塌不塌 |

3 seed × 20 epoch。**R2 是关键**：如果投影同步后 c 不再塌到 0.006，
那么"c 塌缩"从头到尾只是缓存伪影，E2 的结论要整个改写。

### Step 0.3 E6' 正式重跑
沿用 `run_e6_budget.sh` 的阶段结构，但：
- 删除所有 `--mm_eval_fresh 1`；
- 全部加 `--mm_proj_refresh 32`；
- Stage A0 的靶子换成 Step 0.2 的 R1。

**门禁**：
- G1 机制：`conf_mean@best ≥ 0.6`（现在 cached 与 fresh 已一致，两个口径都得满足）
- G2 保判别：`conf_std > 0.02`（否则退化成 force_c，谈不上自适应）
- G3 效果：`R@20 ≥ R1`；`≥ R1 × 1.012` 才算 **PASS+（自适应优于冻结）**

**若 G1/G2 过而 G3 不过** → 说明门控把预算分给了错的物品，
问题在**逐物品分配**而非引入率 → 进 Phase 0.4。

### Step 0.4（条件触发）E7 逐物品预算分配
当前门控只受全局均值约束，物品间怎么分完全由 BPR 决定。备选：
- E7a：按物品热度分层，冷门物品给高 c（多模态本就该救冷启动）；
- E7b：按模态特征质量（image/text 一致性）分配；
- E7c：Top-k 稀疏预算——只让 k% 的物品拿高 c，其余压 0，避免均摊稀释。

**这才是本课题真正的创新点候选**：从"全局引入多少多模态"升级到"给谁引入"。

---

## 3. Phase 1 — MSCA 结构模块（B + A + C）

**不依赖 `mm_align`，可与 Phase 0' 并行开发（但训练要排队，见 §5 资源纪律）。**
v1 的判断依然成立：这是**最低风险、最高性价比**的增量，且在 5 个零-npy 数据集上有 MM 模块给不出的独有价值。

实现顺序与 v1 一致（PR1 `cooc_graph.py` → PR2 `cacl.py` → PR3 `bypass_fuse.py`），
每个 PR **必须先过梯度探针单测**（`_test_*_grad.py`，范式见 `_test_v3_grad.py`）。

`cooc_graph.py` 硬约束：全程 `scipy.sparse` 逐行 top-k，**严禁 `.toarray()`**（D4 爆内存）。

实验矩阵沿用 v1 §Phase1 的 1.1–1.6，门禁 H1/H2/H3 不变。

---

## 4. Phase 2 / 3 / 4

- **Phase 2（MMGCF-P3 尾融合）**：受 Phase 0' 门禁约束。
  额外要求：P3 复用 `mm_align.project()` 时**必须继承 `mm_proj_refresh` 语义**，否则会原样复现 §0.2 的缓存坑。
- **Phase 3（集成消融）**：`pre-fuse × post-fuse × bypass × structural` 阶乘。
  量纲纪律不变：多个 InfoNCE 的 `.sum()` 会让损失比 λ 大 ~batch_size 倍，**必须逐个开、逐一重校准 λ**。
- **Phase 4（PRISM/P6）**：仍被 sports Pearson=0.9915 阻塞。
  解锁前置：对 baby 跑 `pid_diagnostic.py` 确认 Unq/Syn 非零。
  P6 专家层若套用 `project()` 会**精确复现 §0.2 的坑**（每 epoch 只更 1 步）——必须每 batch 实算。

---

## 5. 工程优化清单（本轮已做 / 待做）

### 已修复（2026-08-06 18:47）
1. **截断 run 静默入库** — `run_idea2.py` 原先 `subprocess.run` 不查返回码，
   `parse_best_test` 又取"已有评测里最好的一个"。沙箱/OOM 杀掉训练时日志**不留任何报错**，
   于是早停的高点被当成最终成绩写库（E6 seed2024 把 ep12 截断跑的 ep5 值 0.06968 记成了结果）。
   → 新增 `run_complete()`（核对 `EPOCH[N/N]` + Traceback）、失败自动重跑（`MAX_RUN_ATTEMPTS=2`）、
   仍失败记 `-1 / INCOMPLETE` 且不进均值。
2. **eval txt 追加串数据** — `main.py` 以 `'a'` 写 `logs/<cfg>.txt`，重跑会把上一次的评测行混进来。
   → 新增 `archive_eval_txt()`，每次 run 前把旧 txt 改名 `.prevMMDDHHMMSS`。
3. **分析端兜底** — `analyze_e6.py` 原样信任日志里的评测点。
   → 新增完整性校验，未跑完的 seed 打印 `[剔除]` 并排除出均值（已验证能抓出 seed2024）。

### 待做（按优先级）
4. **结果单一真源** — 现在 `results_idea2.json` 里 `idea2_mm_mcr0` 三个 seed 全是 `-1`（配置名后缀对不上导致找不到 txt），
   真值只存在于 `logs/e2_analysis.json`。两套真源迟早出事。
   → 统一走"日志解析"，`results_idea2.json` 降级为缓存。
5. **实验期代码冻结** — 本轮出现 seed2024/2025 与 seed2026 跑不同 `model.py` 版本。
   → 队列启动时把 `git rev-parse HEAD`（或关键文件 md5）写进日志头，分析端校验一致性；改代码前先停队列。
6. **并发度控制** — 18:43 的冒烟与 E6 主队列并发，两个进程各占约 1.2GB，空闲内存一度降到 2.1GB/16.4GB，
   这很可能就是 seed2024 被杀的原因。→ 加一个全局训练信号量，同时最多 1 个训练进程。
7. **环境坑固化到脚本注释**：
   - 本机 bash 无 `nohup`、无 `sleep`，后台任务必须用工具的 background 机制；
   - Git Bash(MSYS) 会把 `tasklist /FI` 的 `/FI` 转成 `F:\I` 导致过滤器静默失效，
     改用 `tasklist | awk -v p=$PID '$2==p{f=1} END{exit !f}'`。

---

## 6. 一句话总览

> **先修投影同步（`--mm_proj_refresh`），在新口径下重测 E1/E2 拿到可比靶子，再重跑 E6'；
> 若 c 顶住但打不赢冻结档，就把课题推进到"逐物品预算分配"（E7）——这是真正的创新点。
> 结构模块 B+A+C 不依赖 MM，可并行开发，是最稳的论文增量。
> 当前正在跑的 E6 队列基于已证伪的 `--mm_eval_fresh`，建议中止。**
