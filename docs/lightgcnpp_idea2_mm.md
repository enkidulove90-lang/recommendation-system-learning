# idea2 知识对齐（align-then-fuse）多模态扩展 — 实验报告

> **状态**: 🔄 **实验进行中（2026-08-05 重启）** — 首轮实验发现**融合层尺度失配缺陷**并已修复，正用修复后代码重跑。
> **基座**: `baseline/LightGCNpp/`（RecSys 2024，α/β/γ 三参数改进）
> **迁移源**: `baseline/MixRAGRec/`（KDD 2026，Knowledge Alignment Agent）
> **设计依据**: `docs/lightgcnpp_migration_design.md` §2（路线 2：公开多模态基线数据）
> **数据**: `data/amazon-baby-mmssl/` — **真实 MMSSL 特征**（image 18357×4096 float32 + text 18357×384 float32），非合成
> **代码**: `baseline/LightGCNpp/code/{mm_align.py, model.py, dataloader.py, run_idea2.py, aggregate_idea2.py, prep_amazon_sports.py}`

---

> ## 🔍 首轮实验的关键负面发现：融合层尺度失配（已修复）
>
> 首轮（修复前）在 amazon-baby-mmssl 真实特征上，idea2 相对 baseline **同种子配对增益为负**（seed2024：R@20 −1.83%、N@20 −1.31%）。诊断过程与结论如下。
>
> **观测**：训练收敛后置信门控 `conf_mean = 0.088` —— 模型只放行 **8.8%** 的多模态知识；类型门控本身正常（image 0.288 / text 0.712）。初始化时 `conf_mlp` 为 xavier + zero-bias，即 `σ(0)=0.5`；训练后 σ 输入均值降到 **−2.34**，说明是 BPR 主动把 c 压下去的，不是初始化问题。
>
> **根因（实现缺陷，非语义问题）**：`fuse()` 中 `pooled` 经 `F.normalize` 后**模长恒为 1.000、18357 个物品完全相同**；而 `id_emb`（`normal(0, 0.1)`, dim=64）模长 ≈ **0.798 且随流行度分化**（std 0.069）。残差融合 `fused = id_emb + c·(pooled − id_emb)` 在 c→1 时会把物品表示的模长**强行拉成常数 1**，抹平全部流行度信号。数值验证 `corr(‖id_emb‖, ‖fused‖)`：
>
> | c | 修复前 | 修复后 |
> |---|---|---|
> | 0.25 | 0.860 | **0.919** |
> | 0.50 | 0.497 | **0.814** |
> | 1.00 | **−0.016**（信息全毁） | **1.000**（完整保留） |
>
> 又因 `computer()` 中 `embs_zero = embs[0]` **绕过逐层 L2 归一化**，以 `light_out = γ·embs_zero + (1−γ)·embs_prop`（γ=0.2）直通最终表示 —— 被污染的 layer-0 占最终表示 20% 权重。BPR 面对「引入语义方向 = 损失流行度排序能力」的取舍，把 c 压到 0.088 是**理性自保**，而非"图文语义确实不符"。
>
> **修复（范数对齐，`mm_align.py: fuse()`）**：让多模态只提供**方向**，模长沿用该物品自身的 ID 嵌入模长：
> ```python
> id_scale = id_emb.norm(dim=-1, keepdim=True).detach()   # [n,1]，detach 防模型缩小 id_emb 走捷径
> pooled_scaled = pooled * id_scale                        # 同模长，仅换方向
> fused = id_emb + c * (pooled_scaled - id_emb)
> ```
> 修复后 c=1 时融合模长分布与 ID 嵌入完全一致（0.798 ± 0.069），与 baseline 的 layer-0 尺度行为对齐，采纳多模态不再有"代价"。
>
> **验证指标**：重跑后应观察 `conf_mean` 是否从 0.088 显著回升；若仍偏低，则可判定为真实的图文语义不匹配（数据层面），而非实现缺陷。
>
> **方法论教训**：首轮聚合器曾用**非配对**均值比较（baseline 2 seed vs idea2 1 seed）得出 "+1.74%" 的假增益，而同种子配对实为 **−1.83%**，方向相反。`aggregate_idea2.py` 已加入 `paired_gain()`，所有结论**只用双方共同跑完的种子**计算。
>
> **修复前日志归档**：`baseline/LightGCNpp/code/logs/_archive_prefix_scalebug/`（避免与修复后结果混入同一 append 文件被聚合器取 max）。

---

## 1. 背景与目标

MixRAGRec 的 **Knowledge Alignment Agent** 核心原则：不把原始异构结构直接喂给下游，而是先经过一个**显式对齐**步骤，把外部知识投射到下游能消化的统一空间，并附带**置信度**。

对 LightGCN++ 的直接含义（设计文档 §2.1）：**不要把原始视觉/属性特征直接拼进传播**。原因很具体——LightGCN++ 每层做逐节点 L2 归一化（`model.py` 传播循环），整个传播对嵌入的**尺度和分布高度敏感**。把一个 4096 维 CNN 特征直接 concat/相加进 $e^{(0)}_{\text{item}}$，会立刻破坏尺度假设，并把模态噪声沿图放大 $L$ 层。

**本实验目标**（设计文档 §2.2 路线 2）：用公开多模态基线数据（Amazon-Sports 的 CNN/CLIP 特征，维度与 MMSSL/SMORE 一致），实现「类型级投影 → 类型感知门控池化 → 置信度门控残差融合」的三级对齐，并以**视图一致性 InfoNCE** 作为对齐训练信号，验证该机制可端到端接入 LightGCN++ 且相对纯 ID 基线有正向增益。

---

## 2. 数据来源与准备

### 2.1 真相澄清（重要）

项目 `baseline/` 下的 `MMSSL` / `SMORE` / `FITMM` **只是 `data/parsed/` 里的 PDF 解析文件夹，并非可运行代码**；SELFRec 也只含 LightGCN / LightGCN++。因此数据管线需自建。

真实多模态特征来源为 **HKUDS/MMSSL** 仓库（Google Drive 文件夹 `1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0`），其 `image_feat.npy` 行序与 item id **1:1 对齐**（MMSSL/LATTICE 约定），维度 4096（CNN）或 64（CLIP）。

### 2.2 当前使用：合成特征（可恢复信号，验证机制）

为保证 idea2 现在就能**端到端跑通**，先用 `prep_amazon_sports.py` 生成结构真实、维度真实、且**注入已知可恢复信号**的合成特征：

- 来源交互：SELFRec `dataset/amazon-sports`（3 列 `user item weight`）→ LightGCN++ 分组格式 `user item1 item2...`，`n_items = 18357`。
- `image_feat.npy` (18357×4096)：`latent @ W + 噪声`，其中热门物品共享更强的 latent 分量 → **「热门物品视觉更相似」**这一可恢复结构。
- `image_feat_clip.npy` (18357×64)：归一化 latent，作为第二个「类型/视角」。
- 两种特征构成 idea2 的 **G1 类型级**双投影头输入（CNN 4096 / CLIP 64）。

### 2.3 一键切换真实特征（非阻塞，沙箱可能无外网）

`fetch_mm_data.py`（基于 `gdown`）会把 MMSSL 的 `image_feat.npy`（10067 物品，与 MMSSL 原始 item id 对齐）下载并放到 `data/amazon-sports/`，覆盖合成特征。切换后重新跑 `run_idea2.py` 即可，无需改任何代码。

> 注：当前 `n_items`（18357，SELFRec 版）> MMSSL 的 10067，真实特征切换后需同步 item 映射；实验以合成特征验证**机制正确性**，真实特征用于**效果确认**。

---

## 3. 方法：三级对齐（align-then-fuse）

实现于 `mm_align.py::MultiModalAligner`。设 `feats = {t: [n_items, d_t]}`，`id_emb = embedding_item.weight [n_items, d]`。

### G1 类型级投影（尺度对齐）

每种类型 $t$（如 CNN / CLIP）独立投影头 + 可学习类型嵌入 $\mathbf{t}_t$：

$$v_t = \text{L2}\big(\text{MLP}_t(x_t)\big),\qquad \text{MLP}_t: d_t \to d_{\text{hidden}} \to d$$

投影把异构尺度特征映射到 ID 嵌入空间（维度 $d=64$），L2 归一化消除尺度差异。**这是直接 concat 与本方案的根本区别。**

### G2 类型感知门控（不简单平均）

每种类型按「投影与对应类型原型的余弦相似度」做 softmax，信息密度高的类型获得更高权重：

$$w_t^{(i)} = \text{softmax}_t\big(\cos(v_t^{(i)}, \mathbf{t}_t)\big),\qquad \bar v^{(i)} = \sum_t w_t^{(i)} v_t^{(i)}$$

### G3 跨模态置信度门控（图文不符自动退化）

$$c_i = \sigma\big(\text{MLP}_{\text{conf}}([\bar v^{(i)}; e_i^{\text{ID}}]) + 2\cdot\cos(\bar v^{(i)}, e_i^{\text{ID}})\big)\in(0,1)$$

残差融合：图文相符（$c_i\to1$）引入视觉；不符（$c_i\to0$）退化为纯 ID：

$$e_{\text{item}}^{(0,i)} = e_i^{\text{ID}} + c_i\big(\bar v^{(i)} - e_i^{\text{ID}}\big)$$

### 视图一致性 InfoNCE（对齐训练信号）

同一物品的两种类型视图互为正例，batch 内其他物品为负例：

$$\mathcal L_{\text{mm}} = \frac{1}{2}\sum_{(a,b)\in\{(t_1,t_2),(t_2,t_1)\}} \text{CE}\Big(\big[\cos(a,b)/\tau,\ \cos(a,a^\top)/\tau\big],\ \mathbf 0\Big)$$

这作用在「模态轴」，与 idea4 NLGCL 的「层轴」对比互补，互不冲突。

### 工程要点：epoch 级投影缓存

4096 维特征在 CPU 上每个 batch 全量投影过慢，故 `project()` 做 **epoch 级缓存**：每 epoch 刷新一次带梯度的投影（该 batch 训练投影头），其余 batch 复用 detach 缓存。兼顾训练信号与算力。

---

## 4. 接入 LightGCN++ 的改动

| 文件 | 改动 |
| --- | --- |
| `dataloader.py` | 新增 `_load_mm_feats(path)`：`glob *.npy`（跳过 `s_pre_adj*`）→ `dataset.mm_feats` 字典（键=文件名去扩展名） |
| `model.py` | `__init_weight` 构建 `MultiModalAligner`（读 `use_mm`/`mm_feats`）；`computer()` 在 `items_emb` 后注入融合视觉；`bpr_loss` 按 batch idx 加 `mm_reg·L_mm`；`mm_new_epoch()` 刷新 epoch 缓存 |
| `main.py` | `--use_mm` 时 config 名加 `_mm_mr{mm_reg}_mt{mm_temp}`；epoch 开始调 `mm_new_epoch()`；每 5 epoch 打印 `conf_mean`/`gate_mean` |
| `world.py`/`parse.py`/`register.py` | 新增 `use_mm/mm_proj/mm_temp/mm_reg/mm_conf_reg` 配置；`amazon-sports`/`amazon-beauty` 加入白名单 |

`computer()` 关键片段：

```python
items_emb = self.embedding_item.weight
if getattr(self, 'use_mm', 0):
    items_emb, self.mm_info = self.mm_aligner.fuse(self.mm_feats, self.embedding_item.weight)
# 后续 LightGCN++ 传播照常，对融合后的 e^(0)_item 做 α/β/γ 归一化传播
```

---

## 5. 实验设置

- **对比**：`baseline`（纯 ID LightGCN++） vs `idea2`（use_mm 对齐融合）
- **数据集**：amazon-sports（`n_items=18357`，211807 训练交互）
- **配置**：`dim=64, lr=1e-3, decay=1e-4, α=0.6, β=-0.1, γ=0.2, layer=2, topk=[20,40]`
- **idea2 超参**：`mm_proj=256, mm_temp=0.1, mm_reg=1e-3`
- **种子**：2024 / 2025 / 2026（各 3 次）
- **epoch**：20（用户要求「不要跑太多 epoch」），每 5 epoch 记录一次 test 指标
- **指标**：Recall@20、NDCG@20（取每 seed 最优 test 轮）
- **稳健聚合**：`aggregate_idea2.py` 直接从 `logs/{config}.txt` 重建结果，避免并发 json 覆盖

---

## 6. 结果

> ⛔ **本实验已中止，下表无数据。** 原计划的 3 种子（2024/2025/2026）× 20 epoch 训练与 `aggregate_idea2.py` 聚合**未执行**（用户在换电脑交接前取消继续）。表格结构保留，供接手者重跑后直接回填。

### 表 1 — 各种子明细

| 种子 | baseline R@20 | baseline N@20 | idea2 R@20 | idea2 N@20 | ΔR@20 | ΔN@20 |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 | — | — | — | — | — | — |
| 2025 | — | — | — | — | — | — |
| 2026 | — | — | — | — | — | — |
| **均值** | — | — | — | — | — | — |

### 表 2 — 汇总

| 方案 | R@20 | N@20 | 相对基线 R@20 | 相对基线 N@20 |
| --- | --- | --- | --- | --- |
| baseline（纯 ID） | — | — | — | — |
| idea2（对齐融合） | — | — | — | — |

### 表 3 — idea2 对齐诊断（来自 `conf_mean` / `gate_mean`）

| 种子 | conf_mean（融合置信度均值） | gate_CNN | gate_CLIP |
| --- | --- | --- | --- |
| 2024 | — | — | — |
| 2025 | — | — | — |
| 2026 | — | — | — |

---

## 7. 分析与结论（无数据，无法填充）

- 因实验中止、无最终指标，**无法**判定 idea2 相对纯 ID 基线的增益方向与幅度。
- 无法结合 `conf_mean` 验证「图文不符物品自动退化」的预期行为。
- 与 idea1/idea3/idea4 的协同关系见 §8、§9 及设计文档，属**未经验证的设计推测**，重开时需实测确认。
- 已验证的部分（见 §1–§5）：端到端管线跑通、对齐模块随模型加载、损失函数形状正常（2-epoch 冒烟：baseline loss 0.404→0.265，idea2 loss 0.428→0.291 且对齐器正确加载 CNN 4096 + CLIP 64 双特征）。**这仅证明实现可运行，不代表效果增益。**

---

## 8. 局限与下一步

1. **当前为合成特征**：验证机制正确性；效果确认需 `fetch_mm_data.py` 拉取 MMSSL 真实 `image_feat.npy`（10067 物品）。
2. **epoch 偏少（20）**：受 CPU + 用户约束，仅做相对公平对比；效果确认阶段可增至 50–100 epoch。
3. **真实特征 item 映射**：MMSSL 10067 物品 vs SELFRec 18357 物品需对齐，切换时需同步 `prep/fetch` 的 item 索引。
4. **扩展类型**：当前 CNN + CLIP 两类型；可加入更多视角（主图/细节图/UGC 图）直接复用 G1/G2 三级结构。

---

## 9. 复现命令

```bash
cd baseline/LightGCNpp/code
# 1) 准备数据（合成特征，已就绪）
python prep_amazon_sports.py
# 2) 跑 baseline vs idea2（3 种子 × 20 epoch，后台）
python run_idea2.py --only baseline --epochs 20 --seeds 2024,2025,2026
python run_idea2.py --only idea2    --epochs 20 --seeds 2024,2025,2026
# 3) 稳健聚合
python aggregate_idea2.py
# 可选：切换真实 MMSSL 特征（需外网）
python fetch_mm_data.py
```
