# idea2 知识对齐（align-then-fuse）多模态扩展 — 实验报告

> **状态**: ⛔ **实验已中止（2026-08-05，用户取消继续）** — 代码与方法完整保留，**无最终指标**，结果表留空。
> **基座**: `baseline/LightGCNpp/`（RecSys 2024，α/β/γ 三参数改进）
> **迁移源**: `baseline/MixRAGRec/`（KDD 2026，Knowledge Alignment Agent）
> **设计依据**: `docs/lightgcnpp_migration_design.md` §2（路线 2：公开多模态基线数据）
> **代码**: `baseline/LightGCNpp/code/{mm_align.py, model.py, dataloader.py, run_idea2.py, aggregate_idea2.py, prep_amazon_sports.py}`
> **接手者注意**: 本报告仅记录**方法设计与实现**；第 6 节结果表为空是因为实验在跑出指标前被取消，并非数据丢失。如需结论，按第 9 节命令重跑即可（约 3 种子 × 20 epoch，CPU 数小时）。

---

> ## ⛔ 实验中止说明
>
> - **中止时间**: 2026-08-05。用户在换电脑交接前决定**不再继续** idea2 多模态实验。
> - **已完成**: 全部 idea2 代码（`mm_align.py` 三级对齐 + `model.py`/`dataloader.py`/`parse.py`/`world.py`/`register.py`/`main.py` 接入 + `prep_amazon_sports.py`/`fetch_mm_data.py`/`run_idea2.py`/`aggregate_idea2.py` 驱动）、数据管线（合成特征已生成）、以及本方法文档。
> - **未执行**: 3 种子 × 20 epoch 的完整训练与指标聚合。仅留下 seed2024 的早期片段日志（无 test 指标），**不可作为结论**。
> - **代码去向**: 全部已提交并推送到 `experiments` 分支（`origin`, commit `7a6f7bf`），接手者在任意机器 `git clone` 后即可复现。
> - **为何保留本报告**: 方法章节（§1–§5、§8–§9）是完整的设计/实现记录，对后续若重开该方向有价值的参考；仅结果章节（§6–§7）因无数据而留空。

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
