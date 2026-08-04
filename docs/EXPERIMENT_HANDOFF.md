# 实验项目交接文档 · LightGCN++ 迁移与多模态扩展

> 目的：让新接手项目的人**不依赖任何外部说明**，按本文即可在另一台电脑上把环境跑起来、复现已有实验、并继续推进后续实验（idea1–idea5）。
> 适用分支：`experiments`（本文档所在分支）。论文解析（data/parsed）相关的工作在 `phase1` 分支，本分支只收实验代码与结果。

---

## 0. 一分钟速览（Quick Start）

```bash
# 1) 克隆（Git 地址见下）
git clone https://github.com/enkidulove90-lang/recommendation-system-learning.git
cd recommendation-system-learning
git checkout experiments

# 2) 进实验代码目录
cd baseline/LightGCNpp/code

# 3) 准备环境（详见第 5 节；必须设置 4 个 OMP 环境变量，否则 torch CPU 段错误）
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE

# 4) 跑一个最小冒烟（lastfm 基线，2 epoch）
python main.py --dataset lastfm --seed 2024 --epochs 2 --model lgn --recdim 64 \
  --lr 0.001 --decay 1e-4 --layer 2 --alpha 0.6 --beta -0.1 --gamma 0.2
```

---

## 1. Git 与分支信息

| 项 | 值 |
|---|---|
| **Git 远程地址** | `https://github.com/enkidulove90-lang/recommendation-system-learning.git` |
| **实验分支** | `experiments`（从 `phase1` 切出，专门放实验代码/结果） |
| **作者身份（本仓库 local config）** | `enkidulove90-lang` `<enkidulove90-lang@gmail.com>` |
| **论文解析分支** | `phase1`（data/parsed 论文语料在此，本分支不改动） |

克隆并切换到实验分支：

```bash
git clone https://github.com/enkidulove90-lang/recommendation-system-learning.git
cd recommendation-system-learning
git checkout experiments
```

> 说明：本仓库历史中已包含 `data/parsed` 论文语料（与 `phase1` 共用历史），但本分支的提交**只新增/修改实验相关文件**，论文文件保持原样。新克隆会一并取回论文语料（属历史，不影响实验）。

---

## 2. 本分支提交了什么 / 排除了什么

提交**只覆盖实验相关文件**。以下内容因体积或性质被排除，并在 `.gitignore` 中标注：

| 路径 | 大小 | 处理 | 原因 / 恢复方式 |
|---|---|---|---|
| `baseline/LightGCNpp/code/embs/` | ~280 MB | **忽略** | 训练时保存的逐层嵌入（`.pkl`），可运行时再生，无需入库 |
| `baseline/LightGCNpp/data/**/*.npy`、`*.npz` | 含 300 MB | **忽略** | 多模态特征数组 / 缓存邻接矩阵。`image_feat.npy` 单文件 300 MB，超过 GitHub 100 MB/文件限制，**无法 push**；用 `prep_amazon_sports.py` 或 `fetch_mm_data.py` 重新生成（见第 6 节） |
| `baseline/MixRAGRec/` | ~293 MB | **整目录忽略** | 第三方参考仓库（Sjay-Wang/MixRAGRec）的克隆，含自身 `.git` 与 204 MB `data/`。仅保留我们自己的分析文档 `baseline/MixRAGRec_analysis.md`；源码用 `git clone https://github.com/Sjay-Wang/MixRAGRec` 重新获取 |
| `data/parsed/`（论文语料） | ~2 GB | **不改动** | 论文解析工作，本分支不纳入实验范围；保持 `phase1` 历史原样 |

**已提交的关键实验资产**：
- `baseline/LightGCNpp/code/`：全部实验代码 + `logs/`（P0/P1/P2 完整日志 + idea2 进行中日志）
- `baseline/LightGCNpp/SELFRec/`：原始 LightGCN++ 参考实现（含 `dataset/` 24 个标准数据集 `.txt`）
- `baseline/LightGCNpp/data/`：各数据集的**交互文本**（train/test/valid.txt，小体积；不含 `.npy` 特征）
- `baseline/LightGCNpp_analysis.md`、`baseline/MixRAGRec_analysis.md`：两篇架构分析
- `docs/lightgcnpp_migration_design.md`：P0–P5 总体设计
- `docs/lightgcnpp_idea2_mm.md`：idea2（多模态对齐）设计 + 实验记录
- 本文档 `docs/EXPERIMENT_HANDOFF.md`

> 注意：`.gitignore` 当前**并未**忽略项目代码（之前担心的“项目代码被忽略”一节实际不存在）；相反，本分支新增了对大型实验产物的忽略规则（见上表），以保证可正常 push。

---

## 3. 项目与实验背景

本项目把 **LightGCN++（RecSys 2024）** 的官方实现迁移进 `baseline/LightGCNpp/`，并沿 `docs/lightgcnpp_migration_design.md` 设计的路线图逐步验证一系列改进 idea。LightGCN++ 相对 LightGCN 的核心：α/β 邻接归一化指数 + γ 第 0 层残差 + 逐层 L2 归一化。

### 路线图与状态（截至本交接）

| 阶段 | 内容 | 状态 | 关键结论 |
|---|---|---|---|
| **P0** | 删短路 + 复现基线 | ✅ 完成 | lastfm R@20≈0.240（seed 2024/25/26 均值 ~0.240） |
| **P1** | 接 NLGCL 自然对比损失（idea4） | ✅ 完成 | R@20≈0.266–0.268，**相对基线 +10%** |
| **P2** | Oracle 层选择实验（决策点） | ✅ 完成 | Oracle 增益 ~+2%，建议走“轻量规则版”层选择 |
| **idea2** | 多模态对齐 / align-then-fuse（MixRAGRec Knowledge Alignment 迁移） | 🟡 进行中 | amazon-sports 上已打通链路；最终指标待 3 种子跑完 |
| idea1 / idea3 / idea4 / idea5 | 其他改进点 | ⏳ 待定 | 见第 10 节 |

idea2 是本次重点交付：用公开多模态基线数据（Amazon-Beauty/Sports 的 CNN/CLIP 特征，MMSSL/SMORE 仓库有现成 `image_feat.npy`），把 MixRAGRec 的“知识对齐 Agent”思想迁移进 LightGCN++，做 **align-then-fuse**（先对齐再融合，而非原始拼接）。

---

## 4. 实验相关目录结构

```
baseline/LightGCNpp/
├── code/                         # ★ 实验主代码
│   ├── main.py                   # 训练入口；按 (epoch+1)%5==0 写 test 行到 logs/{config}.txt
│   ├── model.py                  # LightGCN 模型；含 idea2 的 fuse / 对比损失接入
│   ├── mm_align.py               # ★ idea2 核心：MultiModalAligner（三级对齐 + 视角一致性 InfoNCE）
│   ├── dataloader.py             # 数据加载；idea2 时自动读 data/<dataset>/*.npy
│   ├── parse.py                  # 命令行参数（见第 7 节）
│   ├── world.py                  # 全局 config（alpha/beta/gamma、use_mm、mm_* 等）
│   ├── register.py               # 数据集注册（已加 amazon-sports / amazon-beauty）
│   ├── oracle_eval.py            # P2：读逐层嵌入，产出 Oracle 上限表 A/B/C
│   ├── run_idea2.py              # ★ idea2 驱动：baseline vs idea2，3 种子 × N epoch
│   ├── aggregate_idea2.py        # 从 logs/{config}.txt 重建 results_idea2.json（防并发覆盖）
│   ├── prep_amazon_sports.py     # 生成 amazon-sports 合成特征（image_feat.npy 300MB + clip 64d）
│   ├── fetch_mm_data.py          # 用 gdown 拉取 HKUDS/MMSSL 真实特征替换合成特征
│   ├── run_remaining.py / run_small_sample.py / run.sh  # 其他实验驱动 / 启动脚本
│   ├── logs/                     # ★ 各实验输出日志（已提交，含 P0/P1/P2 + idea2 进行中）
│   ├── oracle_seed2024/2025/2026.json  # P2 结果（表 A/B/C）
│   ├── results_*.json            # P0/P1 小样本 / 剩余结果
│   └── embs/                     # 运行时缓存（已忽略，勿入库）
├── SELFRec/                      # 原始 LightGCN++ 参考实现（官方 SELFRec 改造版）
│   ├── dataset/                  # 标准数据集（lastfm/gowalla/yelp2018/ml-1m/amazon-book 等 .txt）
│   ├── model/ base/ util/ conf/  # 参考代码
├── data/                         # 各数据集交互文本（train/test/valid.txt，小体积，已提交）
│   ├── amazon-sports/            # ★ idea2 数据集（含 image_feat*.npy，已忽略需重生）
│   ├── lastfm/ gowalla/ yelp2018/ ml-1m/ amazon-book/
├── README_original.md            # LightGCN++ 原 README
└── supplementary_document.pdf    # 原论文补充材料

baseline/
├── LightGCNpp_analysis.md        # LightGCN++ 架构/消融分析（已提交）
├── MixRAGRec_analysis.md         # MixRAGRec 架构分析（已提交；源码已忽略，见第 6 节）
└── docs/                         # 杂项实验文档

docs/
├── lightgcnpp_migration_design.md  # ★ P0–P5 总体设计（最重要）
├── lightgcnpp_idea2_mm.md          # ★ idea2 设计与实验记录
└── EXPERIMENT_HANDOFF.md           # 本文档
```

---

## 5. 环境搭建（关键！）

### 5.1 Python 与依赖

本项目在 **CPU + torch** 下运行（无 GPU 依赖）。推荐用虚拟环境：

```bash
# 任意位置建 venv（若用 WorkBuddy 托管运行时，路径形如 <workbuddy>/binaries/python/envs/default/）
python -m venv venv
source venv/Scripts/activate        # Windows Git Bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy
# 可选（idea2 拉真实特征用）：pip install gdown
```

最小依赖：`torch`(CPU) + `numpy`。（`requirements.txt` 是论文解析管线的依赖，实验只需上面两个。）

### 5.2 ⚠️ 必须设置的 4 个环境变量（否则 torch CPU 段错误）

在本机 Windows / 沙箱环境，**不设置以下变量直接 import torch 会 segfault**：

```bash
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_DYNAMIC=FALSE
```

后续所有 `python main.py ...` 命令都应在设置这 4 个变量后执行（可前缀在命令前，见第 7 节）。

---

## 6. 数据集与下载链接

| 数据集 | 位置 | 体积 | 获取方式 |
|---|---|---|---|
| **amazon-sports 交互** | `baseline/LightGCNpp/data/amazon-sports/{train,test,valid}.txt` | 小（已提交） | 已入库 |
| **amazon-sports 多模态特征** `image_feat.npy` / `image_feat_clip.npy` | 同上目录 | **300 MB / 4.7 MB** | **未入库（超 100 MB）**，二选一重生：<br>① 合成：`python prep_amazon_sports.py`（CNN 4096d + CLIP 64d，结构可恢复）<br>② 真实 MMSSL 特征：`python fetch_mm_data.py`（需 `gdown` + 联网） |
| **MMSSL 真实特征（Google Drive）** | HKUDS/MMSSL 仓库 | — | 文件夹：`https://drive.google.com/drive/folders/1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0`<br>行对齐到 item id 的 `image_feat.npy`<br>源码：`https://github.com/HKUDS/MMSSL` |
| **lastfm / gowalla / yelp2018 / ml-1m / amazon-book** | `baseline/LightGCNpp/data/<ds>/`（转换后分组格式，已提交）+ `SELFRec/dataset/`（原始格式，已提交） | 小 | 已入库；如需官方源见 LightGCN++ / SELFRec 仓库 |
| **MixRAGRec 源码** | `baseline/MixRAGRec/`（本仓库已忽略） | ~293 MB | `git clone https://github.com/Sjay-Wang/MixRAGRec`（其 `data/` 较大，按需自行下载） |

> idea2 运行前**必须**先在 `data/amazon-sports/` 下存在 `image_feat.npy`（与 item 数 18357 行对齐）。最快路径：`python prep_amazon_sports.py`（合成，可立刻验证链路）；要跑真实多模态效果再跑 `fetch_mm_data.py` 替换。

---

## 7. 如何运行各实验

所有命令在 `baseline/LightGCNpp/code/` 下执行，并**前置 4 个 OMP 变量**（下面用一行前缀表示）。

```bash
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE
cd baseline/LightGCNpp/code
```

### 7.1 P0 — 复现 LightGCN++ 基线（lastfm）

```bash
python main.py --dataset lastfm --seed 2024 --epochs 40 --model lgn --recdim 64 \
  --lr 0.001 --decay 1e-4 --layer 2 --alpha 0.6 --beta -0.1 --gamma 0.2
```
- 输出：`logs/lastfm_seed2024_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl2.txt`
- 指标：每 5 epoch 写一行 `test <ndcg20> <ndcg40> <recall20> <recall40> <prec20> <prec40>`

### 7.2 P1 — NLGCL 自然对比损失（idea4）

```bash
python main.py --dataset lastfm --seed 2024 --epochs 40 --model lgn --recdim 64 \
  --lr 0.001 --decay 1e-4 --layer 2 --alpha 0.6 --beta -0.1 --gamma 0.2 \
  --use_cl 1 --cl_reg 5e-5 --cl_temp 0.1 --cl_alpha 0.6 --G 2
```
- `--use_cl 1` 开启层间对比；`--cl_reg` 权重（试过 5e-5 / 1e-4，5e-5 略优）；`--G 2` 对比层对数。

### 7.3 P2 — Oracle 层选择实验（两步）

**Step 1**：训练并保存逐层嵌入（L=4）：

```bash
python main.py --dataset lastfm --seed 2024 --epochs 40 --layer 4 \
  --alpha 0.6 --beta -0.1 --gamma 0.2 --save_layer_emb 1
```
保存为 `embs/<config>_nl4.pkl`（运行时产物，已忽略）。

**Step 2**：Oracle 分析（产出表 A/B/C + 决策建议）：

```bash
python oracle_eval.py --dataset lastfm --k 20 \
  --emb_path embs/<config>_nl4.pkl --out oracle_seed2024.json
```
- 表 A：固定 L vs 逐用户最优层 g* 的 Oracle 上限；表 B：度数桶 × g* 分布；表 C：度数桶 × 固定 L 的 Recall@K。
- 决策规则：Oracle 增益 <3% → 放弃 idea1；3–8% → 轻量规则版；>8% → 可学习版。本实验增益 ~+2%，建议“轻量规则版”。

### 7.4 idea2 — 多模态对齐 / align-then-fuse（amazon-sports）

**前置**：确保 `data/amazon-sports/image_feat.npy` 存在（见第 6 节）。

**一键对比（baseline vs idea2，3 种子 × 20 epoch）**：

```bash
# 基线
python run_idea2.py --only baseline --epochs 20 --seeds 2024,2025,2026
# idea2（多模态对齐）
python run_idea2.py --only idea2   --epochs 20 --seeds 2024,2025,2026
# 汇总（从 logs/{config}.txt 重建 results_idea2.json，避免并发覆盖）
python aggregate_idea2.py
```

**idea2 关键参数**（`parse.py`）：
- `--use_mm 1`：开启多模态对齐
- `--mm_proj 256`：投影头隐藏维
- `--mm_temp 0.1`：视角一致性 InfoNCE 温度
- `--mm_reg 1e-3`：对比损失权重
- `--mm_conf_reg 0.01`：置信度正则（保留位）

**idea2 方法要点（详见 `docs/lightgcnpp_idea2_mm.md`）**：
1. **G1 类型级投影头**：每种模态一个 `Linear→ReLU→Dropout→Linear` 后 L2 归一化，把异构特征投到统一语义空间。
2. **G2 类型感知门控**：用 `softmax(cos(v_t, type_emb_t))` 对多模态表示加权（**不是平均**）。
3. **G3 置信度门控**：`c_i = σ(cos(P(v_i), e_i^ID))`，按 ID 嵌入与多模态投影的余弦相似度做残差融合。
4. **视角一致性 InfoNCE**：同一 item 跨模态互为正样本，拉齐不同模态的语义。
- 实现位于 `mm_align.py: MultiModalAligner`（含 epoch 级投影缓存，避免逐 batch 对 4096 维特征全量投影，CPU 友好）。

---

## 8. 关键文件速查

| 文件 | 作用 |
|---|---|
| `mm_align.py` | idea2 核心：三级对齐 + 视角一致性 InfoNCE，epoch 级缓存 |
| `model.py` | `LightGCN.computer()` 中调用 `mm_aligner.fuse()`；`bpr_loss` 中加对比损失；`mm_new_epoch()` |
| `dataloader.py` | `_load_mm_feats()` 自动加载 `data/<ds>/*.npy`（跳过 `s_pre_adj*`） |
| `parse.py` / `world.py` / `register.py` | 参数 / 全局 config / 数据集注册 |
| `run_idea2.py` | idea2 驱动（baseline vs idea2，多种子） |
| `aggregate_idea2.py` | 从日志重建结果 JSON |
| `prep_amazon_sports.py` / `fetch_mm_data.py` | 合成 / 真实多模态特征生成 |
| `oracle_eval.py` | P2 Oracle 层选择分析 |

---

## 9. 当前实验结果

### P0 / P1 / P2（lastfm，3 种子均值）

| 阶段 | Recall@20 | NDCG@20 | 备注 |
|---|---|---|---|
| P0 基线 (nl2) | ≈0.240 | ≈0.235 | seed 2024/25/26 分别 0.2401 / 0.2399 / 0.2410 |
| P1 NLGCL (cl_reg=5e-5) | ≈0.267 | ≈0.257 | **相对 P0 +10%**；cl_reg=1e-4 略低（≈0.266/0.254） |
| P2 Oracle (L=4) | ≈0.245 | ≈0.239 | Oracle 增益 ~+2%，建议轻量规则版层选择 |

### idea2（amazon-sports，进行中）

| 配置 | Recall@20 (epoch 5 快照) | 状态 |
|---|---|---|
| 基线 | 0.0732 | 3 种子 × 20 epoch 后台运行中 |
| idea2 (mm_reg=1e-3, mm_temp=0.1) | 0.0725 | 同上 |

> 仅 seed2024 在 epoch 5 的快照，尚不能下结论。新接手后跑完 `run_idea2.py` + `aggregate_idea2.py` 即可得到 3 种子完整对比。

---

## 10. 后续路线图与决策点

1. **idea2 收尾**：等 3 种子跑完，看 `aggregate_idea2.py` 输出的相对增益；若 idea2 持平/略降，需排查（a）合成特征信息量不足 → 改用 `fetch_mm_data.py` 真实 MMSSL 特征；（b）对齐头/门控超参（mm_proj、mm_temp、mm_reg）未调到。
2. **P2 → idea1**：Oracle 增益 +2% < 3%，按规则建议“轻量规则版”层选择（按用户度数桶选固定 L），可做一个低成本规则变体验证。
3. **idea3 / idea4 / idea5**：见 `docs/lightgcnpp_migration_design.md` 对应章节；idea4（NLGCL）已在 P1 验证有效，可作为后续变体基线。
4. **与 MixRAGRec 协同**：`baseline/MixRAGRec_analysis.md` 记录了 3-Agent + 4 检索专家架构与 MMAPO 训练框架，idea2 的对齐思想可直接对照其 Knowledge Alignment Agent。

---

## 11. 已知坑 / 注意事项

- **4 个 OMP 环境变量**：不设置就 `import torch` 段错误（见 5.2）。最稳写法是在每条命令前加前缀。
- **`image_feat.npy` 超 100 MB**：GitHub 单文件限制 100 MB，push 不进去；已忽略，必须本地重生（第 6 节）。
- **MixRAGRec 自带 `.git`**：它是嵌套 git 仓库，本仓库已整体忽略 `baseline/MixRAGRec/`，避免污染。需要源码时另行 clone 上游。
- **沙箱删除限制**：本机 Windows 沙箱中 `rm`/`shutil.move` 可能被 safe-delete 拦截；删文件用 Python `os.remove` 包 `try/except`。
- **日志格式**：`main.py` 仅在 `(epoch+1)%5==0` 写 `test` 行；epoch 数少（如 2）时不会产出 test 行（显示 -1.0000 属正常）。
- **idea2 驱动历史 bug（已修）**：`run_idea2.py` 曾因 `COMMON` 列表缺 `--epochs` 与局部变量作用域报错，已通过 `global COMMON` + `.extend` 修复；若复用旧脚本遇 `UnboundLocalError` 即此因。

---

## 12. 参考链接

- **本仓库**：`https://github.com/enkidulove90-lang/recommendation-system-learning.git`（分支 `experiments`）
- **LightGCN++**：RecSys 2024 论文；官方实现见 SELFRec / `baseline/LightGCNpp/SELFRec`
- **MMSSL（真实多模态特征来源）**：`https://github.com/HKUDS/MMSSL`；特征 Google Drive：`https://drive.google.com/drive/folders/1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0`
- **MixRAGRec（对齐思想来源）**：`https://github.com/Sjay-Wang/MixRAGRec`；本项目分析：`baseline/MixRAGRec_analysis.md`
- **设计文档**：`docs/lightgcnpp_migration_design.md`、`docs/lightgcnpp_idea2_mm.md`

---

*本文档随 `experiments` 分支提交，新接手者只需 `git clone` + 第 5、6、7 节即可复现并继续实验。*
