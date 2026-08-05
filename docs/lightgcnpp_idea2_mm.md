# idea2 知识对齐（align-then-fuse）多模态扩展 — 实验报告

> **状态**: 🔄 **实验进行中（2026-08-05 v3 重跑）** — 演进：① 融合层尺度失配（已修复，证伪非主因）；② 投影头梯度饥饿（**v2 修复不彻底**：`fuse()` 的 no_grad 缓存仍切断 BPR→proj 梯度，`conf_mean` 反跌至 0.026）；③ **v3 用 `fuse_subset()` 把 BPR 梯度经 γ 残差直通路接回投影头**（commit `12063f3`）。**v3 仅确认梯度通路通（单测 V3_GRAD_OK），但 epoch10 实测 `conf_mean` 仍塌缩（idea2 0.169→0.046、idea3 0.006→0.002）、seed2024 R@20 配对仍 −1.8%，尚未超越 baseline**（见 §10.1 校正）。idea2/idea3 各 3 种子 × 20 epoch 后台推进中；下一步以 **E1 强制融合消融**定路线（§10.2）。  
> **基座**: `baseline/LightGCNpp/`（RecSys 2024，α/β/γ 三参数改进）  
> **迁移源**: `baseline/MixRAGRec/`（KDD 2026，Knowledge Alignment Agent）  
> **设计依据**: `docs/lightgcnpp_migration_design.md` §2（路线 2：公开多模态基线数据）  
> **数据**: `data/amazon-baby-mmssl/` — **真实 MMSSL 特征**（image 18357×4096 float32 + text 18357×384 float32），非合成  
> **代码**: `baseline/LightGCNpp/code/{mm_align.py, model.py, dataloader.py, run_idea2.py, aggregate_idea2.py, prep_amazon_sports.py}`

---

> ## 🔍 关键负面发现 ①：融合层尺度失配（已修复，但**证伪为非主因**）
>
> 首轮（修复前）在 amazon-baby-mmssl 真实特征上，idea2 相对 baseline **同种子配对增益为负**（seed2024：R@20 −1.83%、N@20 −1.31%）。诊断过程与结论如下。
>
> **观测**：训练收敛后置信门控 `conf_mean = 0.088` —— 模型只放行 **8.8%** 的多模态知识；类型门控本身正常（image 0.288 / text 0.712）。初始化时 `conf_mlp` 为 xavier + zero-bias，即 `σ(0)=0.5`；训练后 σ 输入均值降到 **−2.34**，说明是 BPR 主动把 c 压下去的，不是初始化问题。
>
> **根因（实现缺陷，非语义问题）**：`fuse()` 中 `pooled` 经 `F.normalize` 后**模长恒为 1.000、18357 个物品完全相同**；而 `id_emb`（`normal(0, 0.1)`, dim=64）模长 ≈ **0.798 且随流行度分化**（std 0.069）。残差融合 `fused = id_emb + c·(pooled − id_emb)` 在 c→1 时会把物品表示的模长**强行拉成常数 1**，抹平全部流行度信号。数值验证 `corr(‖id_emb‖, ‖fused‖)`：
>
> | c    | 修复前              | 修复后             |
> | ---- | ---------------- | --------------- |
> | 0.25 | 0.860            | **0.919**       |
> | 0.50 | 0.497            | **0.814**       |
> | 1.00 | **−0.016**（信息全毁） | **1.000**（完整保留） |
>
> 又因 `computer()` 中 `embs_zero = embs[0]` **绕过逐层 L2 归一化**，以 `light_out = γ·embs_zero + (1−γ)·embs_prop`（γ=0.2）直通最终表示 —— 被污染的 layer-0 占最终表示 20% 权重。BPR 面对「引入语义方向 = 损失流行度排序能力」的取舍，把 c 压到 0.088 是**理性自保**，而非"图文语义确实不符"。
>
> **修复（范数对齐，`mm_align.py: fuse()`）**：让多模态只提供**方向**，模长沿用该物品自身的 ID 嵌入模长：
>
> ```python
> id_scale = id_emb.norm(dim=-1, keepdim=True).detach()   # [n,1]，detach 防模型缩小 id_emb 走捷径
> pooled_scaled = pooled * id_scale                        # 同模长，仅换方向
> fused = id_emb + c * (pooled_scaled - id_emb)
> ```
>
> 修复后 c=1 时融合模长分布与 ID 嵌入完全一致（0.798 ± 0.069），与 baseline 的 layer-0 尺度行为对齐，采纳多模态不再有"代价"。
>
> **结果：假设被证伪。** 修复后重跑到同一 epoch5，`conf_mean` 从 **0.093 → 0.091**，几乎无变化。尺度失配是真实缺陷（数值验证成立、值得保留修复），但**不是** idea2 零增益的主因。这促成了第二轮诊断。
>
> **方法论教训**：首轮聚合器曾用**非配对**均值比较（baseline 2 seed vs idea2 1 seed）得出 "+1.74%" 的假增益，而同种子配对实为 **−1.83%**，方向相反。`aggregate_idea2.py` 已加入 `paired_gain()`，所有结论**只用双方共同跑完的种子**计算。
>
> **修复前日志归档**：`baseline/LightGCNpp/code/logs/_archive_prefix_scalebug/`（避免与修复后结果混入同一 append 文件被聚合器取 max）。

---

> ## 🔍 关键负面发现 ②：投影头梯度饥饿（**真实根因**，已修复）
>
> 尺度修复无效后，改从「谁在训练、谁没在训练」的角度复核，定位到 `mm_align.py: project()` 的缓存实现缺陷。
>
> **缺陷**：原实现为省算力做 epoch 级缓存，仅在**每 epoch 第 1 个 batch** 返回带梯度的新鲜投影，其余 93 个 batch 返回 `detach()` 缓存。后果是各模块的 Adam 更新步数严重失衡（20 epoch × 94 batch）：
>
> | 模块                                     | 梯度步数     | 说明                 |
> | -------------------------------------- | -------- | ------------------ |
> | `proj[image/text]`（G1 投影头，4096→256→64） | **20**   | 每 epoch 仅 1 步，等效冻结 |
> | `conf_mlp`（G3 置信度头）                    | **1880** | 每 batch 更新         |
> | `type_emb`（G2 门控原型）                    | **1880** | 每 batch 更新         |
> | `embedding_item`（ID 嵌入）                | **1880** | 每 batch 更新         |
>
> 相差 **94 倍**。更糟的是 `contrastive_loss()` 读的是 `fuse()` 缓存的 `_last_proj_feats`——94 个 batch 里有 93 个是 detach 缓存，**本该独立训练投影头的 InfoNCE 完全没有梯度回传**。
>
> **因果链**：投影头近似随机 → `pooled` 是随机方向的噪声 → BPR 的最快降损路径就是**关掉门控**（c 从 0.5 掉到 0.09 只用了 5 个 epoch）→ `conf_mean≈0.09`。也就是说，门控关掉的确实是噪声，它做得没错；错的是"投影头从未被训练"。这同时解释了为什么修尺度没用——尺度对齐让"采纳多模态"不再有代价，但被采纳的东西本身仍是噪声。
>
> **附带缺陷**：`type_emb` 初始化为 `zeros` → `F.normalize(0)=0` → 门控打分恒为 0 → softmax 退化为均匀平均，G2 类型感知门控实际失效。已改为 `randn(id_dim)*0.1`。
>
> **修复（混合梯度路径）**：不能简单改成"每 batch 全量带梯度投影"——实测全量投影 fwd+bwd 单次 **2502 ms**，94 batch 即 **+235 s/epoch（单轮 132→367 s，+178%）**，不可接受。采用的方案是把「图传播需要的全量投影」与「投影头需要的梯度」拆开：
>
> ```python
> # ① 全量投影: no_grad + epoch 缓存, 只供 fuse() 生成全部 n_items 的 e^(0) 给图传播
> def project(self, feats, epoch=None):
>     if self._proj_cache is None or self._proj_epoch != epoch:
>         with torch.no_grad():
>             self._proj_cache = self._compute_proj(feats)
>         self._proj_epoch = epoch
>     return self._proj_cache
>
> # ② batch 子集重投影: 带梯度, proj 头唯一的梯度来源
> def project_subset(self, feats, idx):          # idx = 本 batch pos+neg 去重, 约 2048
>     return {t: self._l2(self.proj[t](feats[t][idx].float())) for t in self.types}
> ```
>
> `bpr_loss` 侧把原始特征一并传入，让对比损失走带梯度路径：
>
> ```python
> idx = torch.cat([pos.long(), neg.long()]).unique()
> cl_mm = self.mm_aligner.contrastive_loss(idx, feats=self.mm_feats)
> ```
>
> **开销与收益**（`_bench_proj.py` / `_smoke_gradfix.py` 实测）：
>
> | 方案                                  | proj 梯度步数 | 每 epoch 额外耗时          |
> | ----------------------------------- | --------- | --------------------- |
> | 修复前（epoch 缓存 + 刷新 batch）            | 20        | 0                     |
> | 每 batch 全量带梯度                       | 1880      | +235 s（**+178%**，不可行） |
> | **本方案（no_grad 全量缓存 + batch 子集带梯度）** | **1880**  | **+33.5 s（+25%）**     |
>
> 冒烟测试 5 项全部通过：缓存确为 `no_grad` 且跨 batch 复用、`contrastive_loss(feats=)` 给出 `|g_image|=1211.6 / |g_text|=160.3` 的投影头梯度、旧调用路径确认无梯度（证明梯度确实来自新路径）、`fuse()` 仍正常训练 `type_emb`/`conf_mlp`/`id_emb`、初始 `conf_mean=0.489`（≈σ(0)，符合预期）。
>
> **待验证**：重跑后 `conf_mean` 若从 ~0.09 显著回升，则确认根因判断正确；若仍被压到 0.1 以下，才可归因为真实的图文语义不匹配（数据层面）。
>
> **修复前日志归档**：`logs/_archive_gradstarve/`（尺度已修但投影头仍饥饿的那一版）。



---

> ## 🔍 关键负面发现 ③：v2 修复不彻底 —— `fuse()` 的 no_grad 缓存仍切断 BPR→投影头梯度
>
> v2（commit `aebf34c`）把投影头梯度来源从「epoch 缓存」改为「`project_subset` 每 batch 带梯度 + InfoNCE（权重 1e-3）」，proj 头梯度步数表面恢复到 1880。但重跑后 `conf_mean` **不升反降（0.093 → 0.026 / 0.002）**，门控退化成 0.50/0.50 —— 比 v0/v1 更差。说明根因判断有偏差，v2 只是把问题换了个位置。
>
> **真实缺陷（结构性的）**：`bpr_loss` 里 BPR 用的 $e^{(0)}_{\text{item}}$ 来自 `computer()` → `fuse()`，而 `fuse()` 内部走的是 `project()` 的 `with torch.no_grad()` 缓存（v2 为省算力引入）。于是：
>
> - **BPR → proj 步数 = 0**（v0/v1 是 20 步）；
> - 带梯度的 `project_subset` 只接进了 `contrastive_loss`（InfoNCE，权重仅 1e-3，与推荐目标近似正交）。
>
> 后果：投影头 100% 被图文一致性目标驱动，BPR 面对「引入的图文方向 = 噪声」只能**把门控彻底关死**——`conf_mean` 从 0.5 一路压到 0.026。尺度已对齐（①）、投影头也在更新（②），但更新方向由与推荐无关的 InfoNCE 决定，BPR 完全够不到投影头。
>
> **三版梯度步数对照**（核心诊断）：
>
> | 版本          | BPR→proj 步数 | InfoNCE→proj 步数 | epoch5 conf_mean  |
> | ----------- | ----------- | --------------- | ----------------- |
> | v0 原始（尺度失配） | 20          | 20              | 0.093             |
> | v1 尺度修复     | 20          | 20              | 0.091             |
> | v2 投影头「修复」  | **0**       | **1880**        | **0.026 / 0.002** |
>
> **修复（v3，`fuse_subset`）**：不让 BPR 用 `fuse()` 的 no_grad 缓存，而是对 batch 内 pos+neg 去重子集用**已算好的带梯度 `project_subset`** 重算 $e^{(0)}$（`fuse_subset`），拼回 `light_out` 的 `γ·embs_zero` 项：
>
> ```python
> cat_pn = torch.cat([pos.long(), neg.long()])
> idx, inverse = cat_pn.unique(return_inverse=True)
> fused_idx, c_idx = self.mm_aligner.fuse_subset(self.mm_feats, self.embedding_item.weight, idx)
> pos_emb2 = self.gamma * fused_idx[pos_map] + (1 - self.gamma) * ep_pos   # ep = computer() 无梯度传播项
> neg_emb2 = self.gamma * fused_idx[neg_map] + (1 - self.gamma) * ep_neg
> bpr_term = mean(softplus(neg_scores2 - pos_scores2))   # BPR 梯度沿此直通路回 proj/type_emb/conf_mlp
> ```
>
> 复用同一次子集投影（`contrastive_loss(idx)` 读 `_subset_proj_feats` 缓存），**零额外开销**；开销与 v2 相同（+25%/epoch）。
>
> **验证**（`_test_v3_grad.py`，`V3_GRAD_OK`）：BPR 风格损失经 `fuse_subset` 反传，`proj[img]=23.6 / proj[txt]=17.8 / type_emb=0.93 / conf_mlp=3.14` 梯度**全部非零** —— 确认 BPR→投影头梯度通路已恢复。
>
> **当前状态**：commit `12063f3` 已落地 v3；v2 的 idea2/idea3 进程已 kill，用 v3 代码重启 `run_idea2.py --only idea2/idea3`（各 3 种子 × 20 epoch，amazon-baby-mmssl）。
>
> **关键观测（epoch5, seed2024）**：
>
> - **idea2**：`conf_mean=0.169`（v2 的 0.026 → **6.5× 回升**），gate=`{image 0.417 / text 0.583}`（G2 类型门控不再退化 0.50/0.50，已生效）。**梯度修复确认有效** —— BPR→proj 通路恢复，门控不再被掐死。但 0.169 低于原预期的 0.3–0.7 区间：模型在「多模态信号有用但含噪」下理性地只放行 ~17% 知识，属合理行为；是否还需调 G3 `conf_mlp` 偏置/温度，待看最终 R@20/N@20 配对增益再定。
> - **idea3**（`cost_reg=0.01, cost_target=0.2`）：`conf_mean=0.006`，gate=`{image 0.447 / text 0.553}`。该值**反常地低于 idea2 的 0.169、甚至低于 v2 的 0.026** —— 与「预算式把 c 拉到 ~0.2」的预期相反。两种可能：(a) epoch5 仍早，成本正则（权重仅 0.01）尚未把 c 拉离 BPR 偏好的低位，后续 epoch 会回升；(b) 成本正则量级过小（0.01）相对 BPR 可忽略，idea3≈idea2 时本不应出现 0.006，暗示存在 bug 或盆地翻转。需看 epoch10/15/20 的 conf_mean 是否回升；若稳定在低位，则 idea3 成本机制需排查（`mm_cost_w` 量级 / 与 BPR+conf_reg 的竞争关系）。
>
> **日志说明**：v2 那版（no_grad 缓存、conf_mean 0.026）保留在 `logs/run_idea2_mm_seed2024.log` 第 63 行附近，v3 结果 append 在同文件后续 epoch5 行。

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
- `image_feat.npy` (18357×4096)：`latent @ W + 噪声`，其中热门物品共享更强的 latent 分量 → **「热门物品视觉更相似」**&#x8FD9;一可恢复结构。
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

$v_t = \text{L2}\big(\text{MLP}_t(x_t)\big),\qquad \text{MLP}_t: d_t \to d_{\text{hidden}} \to d$

投影把异构尺度特征映射到 ID 嵌入空间（维度 $d=64$），L2 归一化消除尺度差异。**这是直接 concat 与本方案的根本区别。**

### G2 类型感知门控（不简单平均）

每种类型按「投影与对应类型原型的余弦相似度」做 softmax，信息密度高的类型获得更高权重：

$w_t^{(i)} = \text{softmax}_t\big(\cos(v_t^{(i)}, \mathbf{t}_t)\big),\qquad \bar v^{(i)} = \sum_t w_t^{(i)} v_t^{(i)}$

### G3 跨模态置信度门控（图文不符自动退化）

$c_i = \sigma\big(\text{MLP}_{\text{conf}}([\bar v^{(i)}; e_i^{\text{ID}}]) + 2\cdot\cos(\bar v^{(i)}, e_i^{\text{ID}})\big)\in(0,1)$

残差融合：图文相符（$c_i\to1$）引入视觉；不符（$c_i\to0$）退化为纯 ID：

$e_{\text{item}}^{(0,i)} = e_i^{\text{ID}} + c_i\big(\bar v^{(i)} - e_i^{\text{ID}}\big)$

### 视图一致性 InfoNCE（对齐训练信号）

同一物品的两种类型视图互为正例，batch 内其他物品为负例：

$\mathcal L_{\text{mm}} = \frac{1}{2}\sum_{(a,b)\in\{(t_1,t_2),(t_2,t_1)\}} \text{CE}\Big(\big[\cos(a,b)/\tau,\ \cos(a,a^\top)/\tau\big],\ \mathbf 0\Big)$

这作用在「模态轴」，与 idea4 NLGCL 的「层轴」对比互补，互不冲突。

### 工程要点：双路径投影（全量 no_grad 缓存 + batch 子集带梯度）

4096 维特征在 CPU 上全量投影一次 fwd+bwd 约 2.5 s，每 batch 全量带梯度会让单轮从 132 s 涨到 367 s（+178%）。但**图传播需要全部 n_items 的投影，而梯度只需要本 batch 参与 loss 的物品**——两者可以拆开：

- `project(feats)`：全量投影，`torch.no_grad()` + **epoch 级缓存**，只供 `fuse()` 生成所有物品的 $e^{(0)}$ 喂给图传播。每 epoch 算 1 次。
- `project_subset(feats, idx)`：只对本 batch 的 pos+neg 物品（约 2048 个）**重新做带梯度投影**，接进视图一致性 InfoNCE——这是投影头唯一的梯度来源。约 280 ms/batch。

结果：投影头梯度步数 20 → 1880（每 batch 1 步），额外开销仅 +25%。

> ⚠️ 早期实现只在「每 epoch 第 1 个 batch」返回带梯度投影，导致投影头 20 个 epoch 只走 20 步而门控走 1880 步，是 idea2 首轮零增益的根因，详见文首「关键负面发现 ②」。`project_subset` 必须**重新前向**，不能从 `_proj_cache` 切片（那是 no_grad 结果）。

---

## 4. 接入 LightGCN++ 的改动

| 文件                                  | 改动                                                                                                                                                                                                                                     |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dataloader.py`                     | 新增 `_load_mm_feats(path)`：`glob *.npy`（跳过 `s_pre_adj*`）→ `dataset.mm_feats` 字典（键=文件名去扩展名）                                                                                                                                              |
| `model.py`                          | `__init_weight` 构建 `MultiModalAligner`（读 `use_mm`/`mm_feats`）；`computer()` 在 `items_emb` 后注入融合视觉；`bpr_loss` 传 `feats=self.mm_feats` 让对比损失走 `project_subset`（投影头每 batch 拿梯度）并加 `mm_reg·L_mm` + 置信度判别正则；`mm_new_epoch()` 刷新全量 no_grad 缓存 |
| `main.py`                           | `--use_mm` 时 config 名加 `_mm_mr{mm_reg}_mt{mm_temp}`；epoch 开始调 `mm_new_epoch()`；每 5 epoch 打印 `conf_mean`/`gate_mean`                                                                                                                    |
| `world.py`/`parse.py`/`register.py` | 新增 `use_mm/mm_proj/mm_temp/mm_reg/mm_conf_reg` 配置；`amazon-sports`/`amazon-beauty` 加入白名单                                                                                                                                                |

`computer()` 关键片段：

```python
items_emb = self.embedding_item.weight
if getattr(self, 'use_mm', 0):
    items_emb, self.mm_info = self.mm_aligner.fuse(self.mm_feats, self.embedding_item.weight)
# 后续 LightGCN++ 传播照常，对融合后的 e^(0)_item 做 α/β/γ 归一化传播
```

---

## 5. 实验设置

- **对比**：`baseline`（纯 ID LightGCN++） vs `idea2`（use_mm 对齐融合） vs `idea3`（idea2 + 成本感知门控：`--cost_reg 0.01 --cost_target 0.2`）
- **数据集**：amazon-baby-mmssl（**真实 MMSSL 特征**：image 18357×4096 + text 18357×384；211807 训练交互，`n_items=18357`）
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

| 种子     | baseline R@20 | baseline N@20 | idea2 R@20 | idea2 N@20 | ΔR@20 | ΔN@20 |
| ------ | ------------- | ------------- | ---------- | ---------- | ----- | ----- |
| 2024   | —             | —             | —          | —          | —     | —     |
| 2025   | —             | —             | —          | —          | —     | —     |
| 2026   | —             | —             | —          | —          | —     | —     |
| **均值** | —             | —             | —          | —          | —     | —     |

### 表 2 — 汇总

| 方案             | R@20 | N@20 | 相对基线 R@20 | 相对基线 N@20 |
| -------------- | ---- | ---- | --------- | --------- |
| baseline（纯 ID） | —    | —    | —         | —         |
| idea2（对齐融合）    | —    | —    | —         | —         |

### 表 3 — idea2 对齐诊断（来自 `conf_mean` / `gate_mean`）

| 种子   | conf_mean（融合置信度均值） | gate_CNN | gate_CLIP |
| ---- | ------------------ | -------- | --------- |
| 2024 | —                  | —        | —         |
| 2025 | —                  | —        | —         |
| 2026 | —                  | —        | —         |

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

---

## 10. 后续实验设计（2026-08-05 复盘后）

> 本节为 v3 跑出 epoch5 后、结合 epoch10 实测日志的**修正版**实验路线。v3 的核心修复（梯度通路）已验证，但实验结论需重判（见 §10.1）。

### 10.1 当前判断的校正（重要）

v3 提交 `12063f3` 后，仅凭 **epoch5 瞬时 `conf_mean`** 判定"修复有效"是误判。结合 `logs/run_idea2_*.log` 的 epoch10 实测：

| 变体 (seed2024) | conf_mean ep5 | conf_mean ep10 | gate ep10 | R@20 (best) | vs baseline |
| --------------- | ------------- | -------------- | --------- | ----------- | ----------- |
| idea2 (v3)      | 0.169         | **0.046**      | img0.462/txt0.538 | 0.0826 | **−1.8%** |
| idea3 (v3, cost_target=0.2) | 0.006 | **0.002** | img0.487/txt0.513 | — | 塌缩 |

**三处校正**：
1. **`conf_mean` 是瞬时值，会塌缩**：idea2 `0.169→0.046`、idea3 `0.006→0.002`，训练后期 c 仍被压到 ~0。epoch5 的高值只是早期 transient。
2. **真实指标仍负**：idea2 seed2024 R@20 = 0.0826 < baseline 0.0842（配对 **−1.8%**）。`results_idea2.json` 的 `summary` 段写 `idea2_R@20=0, rel -100%` 是聚合脚本 bug（仅 baseline 在场时计算），**一切结论以 `aggregate_idea2.py` 的配对值为准**。
3. **v3 修通的是"梯度通路"（单测 V3_GRAD_OK 证实 proj/type_emb/conf_mlp 梯度全非零），但训练出的模型仍学会关掉多模态**——问题已从"投影头饿死"转为"模型有梯度却选择忽略多模态"。

**idea3 反常根因（确定性，非 bug/盆地）**：`conf_reg` 项 `(1-|2c-1|)` 对 c<0.5 的梯度恒为 **+0.02（往 0 推）**；`cost_reg` 预算项 `(c-0.2)²` 在 c<0.2 时最大上推梯度仅 `0.02×0.2=0.004`。**`conf_reg` 恒强 5×，`conf_mean` 必塌到 0，预算 0.2 拉不起来**。两变体皆受其害——这直接指向 §10.3 的 E2/E5。

### 10.2 决策分流：E1 强制融合消融（最高优先，定路线）

**E1 是区分"机制问题 vs 数据问题"的唯一判别实验，必须最先做。**

- **做法**：冻结 `c = const ∈ {0.3, 0.5, 0.8, 1.0}`（`conf_mlp` 不更新），跑完整 20 epoch。
- **判定**：
  - 若某档 c 的 R@20 **高于 baseline** → 特征有用，是被门控/正则压死的**机制问题** → 走 §10.3 Phase A。
  - 若所有档 c 的 R@20 **仍低于 baseline** → 特征本身无效 → 走 §10.4 Phase B。
- **最小实现**（`mm_align.fuse_subset` 加开关）：
  ```python
  # mm_align.py: fuse_subset() 顶部
  if getattr(self, 'force_c', 0) > 0:
      c = torch.full_like(c_idx, self.force_c).detach()   # 冻结置信度，仅验证特征本身
  ```
  并在 `model.py/parse.py` 加 `--force_c`（默认 0 = 原行为），`run_idea2.py` 转发该参数。

```bash
# E1：强制融合扫描（在 run_idea2.py 转发 --force_c 后）
for C in 0.3 0.5 0.8 1.0; do
  python run_idea2.py --only idea2 --epochs 20 --seeds 2024,2025,2026 --force_c $C
done
python aggregate_idea2.py --dataset amazon-baby-mmssl
```

### 10.3 Phase A — 修机制（若 E1 显示特征有用）

- **E2 `mm_conf_reg=0` 消融**（首要嫌疑）：idea2 关掉"推向极端"正则，预期 `conf_mean` 不再被压向 0。
  ```bash
  python run_idea2.py --only idea2 --epochs 20 --seeds 2024,2025,2026 --mm_conf_reg 0
  ```
- **E5 idea3 清预算**：同时关 `conf_reg` + 扫 `cost_reg` 量级，验证 c 能否被拉到 ~0.2。
  ```bash
  for CR in 0.05 0.1 0.3 1.0; do
    python run_idea2.py --only idea3 --cost_reg $CR --cost_target 0.2 \
                        --epochs 20 --seeds 2024,2025,2026 --mm_conf_reg 0
  done
  ```
- **E6 全局预算**：把 `(c_i-0.2)².mean()` 换成 `(c.mean()-0.2)²`（语义更贴合"平均引入率≈预算"，不被逐物品 BPR 偏好抵消）。改 `model.py` cost_loss 一行即可。
- **E3 对齐信号扫描**：`mm_reg ∈ {1e-2, 1e-1}`，看更强 InfoNCE 是否改善 proj 头质量（当前 1e-3 过弱）。

### 10.4 Phase B — 换特征/数据（若 E1 显示特征无效）

- **E8 单模态拆解**：只喂 `image_feat`(4096) 或只喂 `text_feat`(384)，定位哪种模态在拖后腿（gate 已显示 text 权重偏高，但权重高≠贡献高）。
  - 实现：在 `dataloader._load_mm_feats` 用白名单只保留一个键，或 `mm_align` 接受 `--mm_types` 过滤。
- **E9 对齐质量探针（预训练，无梯度）**：训练前测"相似 image 的物品是否共现交互 / image-text 余弦是否正相关"，判断特征本身与推荐信号的对齐度。可复用 `baseline/LightGCNpp/code/pid_diagnostic.py` 的 CCA/互信息模块。
- **E10 amazon-sports 真实 MMSSL**：当前 baby 的 `text_feat`(384) 质量存疑，切到 10067 物品的真实 MMSSL 特征（需先解决 item 映射，见 §8.3）。
- **E12 层数消融**：`lightGCN_n_layers ∈ {2,3}`，看多模态 e⁽⁰⁾ 在更深传播下贡献变化。

### 10.5 通用对照（任何分支都要做）

- **E11 长训练**：c 在 ep10 仍在塌，需 50–100 ep 看是否收敛到稳定值、R@20 差距扩大还是收窄。
- **E13 随机投影对照**：冻结 proj 头为随机（无梯度）→ 应复现 v0/v1 的 c 低位、gate 退化，反证"梯度修复"是此前 0 增益的元凶。
- **E14 conf 初始化扫描**：`conf_mlp` bias 初始化使 c_init ∈ {0.3, 0.5, 0.7}，检验收敛是否 basin 依赖（初始化高是否锁在高位）。

### 10.6 立即行动项（当前 v3 跑完后）

1. **等 3 种子跑完**，用配对聚合（**不要**信 `results_idea2.json` 的 summary bug）：
   ```bash
   python aggregate_idea2.py --dataset amazon-baby-mmssl --cost_reg 0.01 --md report.md
   ```
2. **conf_mean 跟踪口径修正**：当前只在 `(epoch+1)%5==0` 打印（main.py:87），且只记 ep5 易被瞬时值误导。**改为在最优 test epoch 处记录 `conf_mean`**，否则会重复本轮"误判 v3 有效"的错误。建议直接在 `main.py` 评测块里，于 best-N@20 那一轮额外打印一次 `conf_mean`/`gate_mean`。
3. **先跑 E1**（§10.2）定路线，再决定 Phase A 或 B 的投入。

