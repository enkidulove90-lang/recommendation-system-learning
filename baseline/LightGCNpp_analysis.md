# LightGCN++ 源码分析报告

> **生成时间**: 2026-08-04
> **源码位置**: `baseline/LightGCNpp/`
> **迁移来源**: `C:\Users\xu.yan1\workspace\lightgcn_learning\baselines\LightGCNpp`
> **论文**: "Revisiting LightGCN: Unexpected Inflexibility, Inconsistency, and A Remedy Towards Improved Recommendation" (RecSys 2024 Short Paper)
> **DOI**: 10.1145/3640457.3688176 ｜ 期刊扩展版 TORS: 10.1145/3760763
> **上游实现**: 基于 gusye1234/LightGCN-PyTorch

---

## 一、核心思想：三处"不灵活/不一致"及其修补

LightGCN 的传播公式为固定形式：

$$\hat{A} = D^{-1/2} A D^{-1/2},\quad e^{(l+1)} = \hat{A}e^{(l)},\quad e^{final} = \frac{1}{L+1}\sum_{l=0}^{L} e^{(l)}$$

论文指出其中三个被"写死"的设计，并分别引入一个标量超参数放开：

| # | LightGCN 的固化设计 | 问题 | LightGCN++ 的修补 | 参数 |
|---|---------------------|------|-------------------|------|
| 1 | 对称归一化 $D^{-1/2}AD^{-1/2}$ | 左右两侧强制同指数，无法调节度数惩罚强度 | 解耦为 $D^{-\alpha}AD^{-\beta}$ | $\alpha,\beta$ |
| 2 | 各层等权平均（含第 0 层） | 层 0（ego embedding）与传播层被同等对待 | 层 0 单独加权：$\gamma e^{(0)} + (1-\gamma)\overline{e^{(1..L)}}$ | $\gamma$ |
| 3 | 各层嵌入范数量级不一致 | 深层范数漂移，导致层间聚合被某一层主导 | 每层传播前做逐节点 L2 归一化 | 无（结构性修改） |

最终传播式：

$$\tilde{A} = D^{-\alpha} A D^{-\beta},\quad
e^{(l+1)} = \tilde{A}\cdot \frac{e^{(l)}}{\|e^{(l)}\|_2},\quad
e^{final} = \gamma\, e^{(0)} + (1-\gamma)\cdot\frac{1}{L}\sum_{l=1}^{L} e^{(l)}$$

> 注意第 3 点：L2 归一化作用在**传播前**，且第 0 层也会被归一化后参与传播，但 $e^{final}$ 中的 $e^{(0)}$ 用的是**未归一化的原始 ego embedding**（`embs[0]` 在归一化之前就已入列）。这个细节在改造时极易踩坑。

---

## 二、代码落点（精确行号）

### 2.1 $\alpha,\beta$ —— 在数据层，不在模型层

`code/dataloader.py` `getSparseGraph()`：

```python
# L377-390
rowsum_left  = np.array(adj_mat.sum(axis=1)) ** -self.alpha   # D^{-alpha}
rowsum_right = np.array(adj_mat.sum(axis=1)) ** -self.beta    # D^{-beta}
d_mat_left, d_mat_right = sp.diags(d_inv_left), sp.diags(d_inv_right)
norm_adj = d_mat_left.dot(adj_mat).dot(d_mat_right)
```

**关键工程细节**：归一化后的邻接矩阵按 `s_pre_adj_mat_{alpha}_{beta}.npz` 缓存到数据目录（L364/L394）。
- 好处：换 $\gamma$ 不必重算图。
- 陷阱：若改造图结构（idea1 的子图传播范围）却沿用同一文件名，会**静默加载旧图**。改造时必须把新的结构标识写进缓存文件名。

### 2.2 $\gamma$ 与逐层 L2 归一化 —— 在模型层

`code/model.py` `LightGCN.computer()` L143-184：

```python
embs = [all_emb]                      # embs[0] = 未归一化的 ego embedding
for layer in range(self.n_layers):
    norm = torch.norm(all_emb, dim=1) + 1e-12
    all_emb = all_emb / norm[:, None]          # ← 修补 #3：传播前 L2 归一化
    all_emb = torch.sparse.mm(g_droped, all_emb)
    embs.append(all_emb)

embs_zero = embs[0]
embs_prop = torch.mean(torch.stack(embs[1:], dim=1), dim=1)
light_out = (self.gamma * embs_zero) + ((1 - self.gamma) * embs_prop)   # ← 修补 #2

_users, _items = torch.split(torch.stack(embs, dim=1), [n_users, m_items])
users,  items  = torch.split(light_out, [n_users, m_items])
return users, items, _users, _items
```

**`computer()` 返回 4 个值，这是本仓库区别于原版 LightGCN 的重要接口**：
- `users, items`：$\gamma$ 加权后的最终嵌入，`[N, d]`
- `_users, _items`：**逐层嵌入堆叠**，`[N, L+1, d]`

`_users/_items` 是后续所有改造的抓手 —— 逐层嵌入已经现成暴露出来，idea1（逐层加权）和 idea4（NLGCL 层间对比）都不需要额外前向。

### 2.3 训练与评估

| 文件 | 职责 | 备注 |
|------|------|------|
| `code/main.py` | 训练主循环，每 5 epoch 验证 | 早停 patience=10 |
| `code/Procedure.py` | `BPR_train_original` / `Valid` / `Test` / `Test_Offline` | 见下 |
| `code/utils.py` | `BPRLoss`、`UniformSample_original`、Recall/NDCG 计算 | |
| `code/world.py` | 全局 config 字典 | 新增超参数在此注册 |
| `code/parse.py` | argparse | `--alpha/--beta/--gamma/--save_layer_emb` |

**`Procedure.Test_Offline(dataset, all_users, all_items)`（L243-312）值得单独点名**：它接收**预计算好的嵌入**而非模型对象来跑完整 Top-K 评估。配合 `--save_layer_emb` 保存的 `[N, L+1, d]`，可以在不重新训练的前提下，任意组合各层嵌入并评估 —— 这正是 idea1 "oracle 层选择"实验所需的全部基础设施。

---

## 三、⚠️ 迁移后必须知道的三个"地雷"

`code/main.py` L36-44 有三段作者调参时留下的硬编码短路，**会静默 `exit(0)` 且不报错**：

```python
if os.path.exists(emb_path):                              # L36  已跑过则直接退出
    print('Exists.'); exit(0)
if world.args.decay == 1e-6 or world.args.decay == 1e-8:  # L40  这两个 decay 直接退出
    exit(0)
if world.args.layer == 4:                                 # L43  L=4 直接退出！
    exit(0)
```

| 地雷 | 影响 | 处置建议 |
|------|------|----------|
| `layer == 4` 短路 | **直接阻断 idea1 的 oracle 实验**（需要 L=4 逐层嵌入） | 改造时删除或改为可控开关 |
| `decay` 短路 | 网格搜索时这两个取值会静默跳过 | 同上 |
| `emb_path` 存在即退出 | 换随机种子重跑会被跳过（种子已在文件名中，影响有限）；但改造后若沿用同名会误判 | 加 `--force` 参数 |

另有一处小瑕疵：`main.py` 的早停判断 `if patience == 10` 位于 epoch 循环内、但 `patience` 仅在每 5 epoch 的验证分支里自增，逻辑可用但不够严谨。

---

## 四、超参数与最优配置

### 4.1 命令行

```bash
cd baseline/LightGCNpp/code
python main.py --dataset="yelp2018" --alpha 0.6 --beta -0.1 --gamma 0.1
```

默认推荐：$\alpha=0.6,\ \beta=-0.1,\ \gamma=0.2$；`--layer 2`、`--recdim 64`、`--lr 0.001`、`--decay 1e-4`、`--bpr_batch 2048`。

### 4.2 各数据集最优三元组（论文 Table）

| Dataset | LastFM | CiteULike | ML-1M | Gowalla | Yelp | Amz-Sports | Amz-Beauty | Amz-Book | ML-10M | Alibaba |
|---------|--------|-----------|-------|---------|------|------------|------------|----------|--------|---------|
| **α** | 0.6 | 0.5 | 0.4 | 0.6 | 0.6 | 0.6 | 0.5 | 0.6 | 0.6 | 0.6 |
| **β** | -0.1 | -0.1 | 0.1 | -0.1 | -0.1 | -0.1 | 0.0 | -0.1 | -0.1 | 0.0 |
| **γ** | 0.0 | 0.4 | 0.0 | 0.2 | 0.0 | 0.0 | 0.2 | 0.2 | 0.0 | 0.1 |

> `code/run.sh` 与 README 表格在 LastFM/ML-1M/Yelp 的 $\gamma$ 上不一致（run.sh 用 0.2/0.0/0.1，README 表用 0.0/0.0/0.0）。**以 README 表格为准**，run.sh 疑似旧版残留。

规律：$\alpha \approx 0.6 > 0.5$ 说明**加大对源节点度数的惩罚**有益；$\beta \approx -0.1 < 0$ 意味着目标节点度数被**正向放大**（热门物品不再被过度抑制），这与 LightGCN 对称归一化的直觉相反，是本文最反直觉的发现。

---

## 五、迁移内容与验证

### 5.1 目录结构

```
baseline/LightGCNpp/
├── code/                      # 主实现（原生 PyTorch，改造主战场）
│   ├── model.py               # LightGCN / LightGCNGaudi
│   ├── dataloader.py          # alpha/beta 图归一化
│   ├── Procedure.py           # 训练/验证/测试/Test_Offline
│   ├── main.py  parse.py  world.py  utils.py  register.py
│   ├── *_gaudi.py             # Intel Gaudi 版本（dense mm 替代 sparse）
│   └── run.sh
├── data/                      # 5 个数据集，LightGCN 格式（train/valid/test.txt）
│   └── lastfm | ml-1m | gowalla | yelp2018 | amazon-book
├── SELFRec/                   # SELFRec 框架版本
│   ├── model/graph/LightGCNpp.py
│   ├── dataset/               # 8 个数据集
│   └── conf/  base/  util/
├── README_original.md
└── supplementary_document.pdf
```

**迁移取舍**：跳过了 SELFRec 的 `ml-10m`(103MB) 与 `alibaba`(23MB) 两个超大数据集（均非 LightGCN++ 主实验集），并清理了 `__pycache__`、`.ipynb_checkpoints`、`code/embs`（9.4MB 运行产物）。最终 105 文件 / 132MB。

### 5.2 运行验证 ✅

环境：`C:\Program Files\Python311\python.exe`（torch 2.13.0+cpu, numpy 2.4.6, scipy 1.17.1, sklearn 1.9.0, tqdm, tensorboardX 均已就绪）。

```
$ python main.py --dataset="lastfm" --alpha 0.6 --beta -0.1 --gamma 0.2 --epochs 2
64315 interactions for training / 9143 valid / 18321 test
lastfm Sparsity : 0.0028
generating adjacency matrix ... costing 2.63s, saved norm_mat
EPOCH[1/2] loss0.245
EPOCH[2/2] loss0.143
```

训练正常收敛。唯一告警是 `torch.sparse.FloatTensor` 的弃用提示（新版 torch 建议改用 `torch.sparse_coo_tensor`），不影响运行。

> 冒烟测试在 `data/lastfm/` 下生成了缓存 `s_pre_adj_mat_0.6_-0.1.npz`，可保留复用。

---

## 六、对四个改造方向的接口评估

| 改造方向 | 现成抓手 | 需改动 | 难度 |
|----------|----------|--------|------|
| **idea1** 多粒度自适应传播 | `computer()` 已返回 `[N,L+1,d]` 逐层嵌入；`Test_Offline` 支持离线嵌入评估；`dataset.users_D/items_D` 已有度数 | 把标量 $\gamma$ 换成逐节点层权重 $w_u^{(l)}$；**先删 `layer==4` 短路** | 低-中 |
| **idea2** 知识/视觉对齐 | 无现成多模态接口；`data/` 五个数据集均无图像特征 | 需新增特征加载 + 投影对齐模块；须先落实数据源 | 高（受数据制约） |
| **idea3** 成本感知权衡 | `nnz(Graph)` 可直接算 FLOPs；`utils.timer` 已有计时 | 新增成本正则项与 Pareto 评估脚本 | 中 |
| **idea4** NLGCL 对比约束 | 逐层嵌入现成，**无需二次前向**；`utils.BPRLoss.stageOne` 是唯一注入点 | 约 30 行：加 InfoNCE + 4 个配置项 | 低 |

四者中 **idea4 最易落地、idea1 次之且与 idea3 天然耦合、idea2 受限于数据可得性**。详细方案见 `docs/lightgcnpp_migration_design.md`。
