# PRISM → LightGCN++ 集成分析

> **生成时间**: 2026-08-05
> **论文**: PRISM: Personalized Recommendation via Information Synergy Module（arXiv 2601.10944）
> **论文解析**: `data/parsed/2601.10944_PRISM/2601.10944.md` ｜ **摘要**: `data/summaries/2601.10944_summary.md`
> **源码位置**: `baseline/PRISM/`（迁移自 `C:\Users\xu.yan1\workspace\lightgcn_learning\baselines\PRISM`，22 文件 / 5.5 MB，已剥离 git submodule 指针）
> **集成目标**: `baseline/LightGCNpp/`（RecSys 2024，α/β/γ 三参数改进）
> **现状依据**: `baseline/docs/lightgcnpp_p0p1p2_report.md`、`docs/lightgcnpp_idea2_mm.md`、`docs/lightgcnpp_roadmap_status.md`

---

## 0. 结论速览

| 结论 | 内容 |
| --- | --- |
| **可集成性** | 三个 idea **均可**落到 LightGCN++，但都不是"抄代码"，因为 PRISM 是**序列推荐（SR）**模块，LightGCN++ 是**图协同过滤（Graph CF）**，中间隔着"没有序列编码器"这道结构鸿沟 |
| **最优落点** | 现有 `mm_align.py` 的**三级对齐 G1→G2→G3** 正好是 PRISM 的天然宿主：**G1 保留**（当 modality encoder）、**G2 被 PRISM 的 MoE + AFL 替换**、**G3 保留**（本项目自有贡献，与 PRISM 正交） |
| **⛔ 硬阻塞** | 当前 `amazon-sports` 的两路特征是**同一 64 维 latent 派生的两个视图**（实测 item-item 相似度 Pearson **0.9915**）。PID 分解在此数据上**不可辨识**：Unq≈0、Syn≈0、Red≈全部。**synergy 专家必然学不到东西** |
| **优先动作** | 先解决数据（拿 MMSSL 真实 `image_feat.npy` + `text_feat.npy`），再谈模型。数据不换，做多少专家都是自欺 |
| **性价比排序** | idea3(MoE 解耦) > idea1(三损失) > idea2(兴趣感知 AFL)。前两者是一体的（无损失则专家不分化），idea2 在图 CF 里退化风险最大 |
| **成本** | 新增参数 ≈ 24 万（197,888 experts + 41,604 AFL），相对 ID 嵌入 3,453,120 增加 **6.9%**；CPU 单线程下每 epoch 额外 **5–30 s**（取决于是否只在 batch 物品上算损失） |

---

## 1. PRISM 三大 idea 的原文定位

PRISM 的三个 idea 不是并列的，而是**一条链**：

```
idea3 (MoE 架构) —— 提供 4 个结构相同、参数独立的专家
     ↓ 光有 4 个 MLP 不会自动分化
idea1 (三种交互损失) —— 用 mask 扰动 + anchor/pos/neg 逼每个专家专精一种交互
     ↓ 4 种交互对不同用户重要性不同
idea2 (兴趣感知 AFL) —— 按用户历史行为动态加权 4 个专家的输出
```

**读法提醒**：论文里 idea1 与 idea3 都写在 §2.3 Interaction Expert Layer 里；idea2 写在 §2.4 Adaptive Fusion Layer。摘要维度 3 把"Interaction Expert Layer"同时归给 idea2 和 idea3，是摘要的措辞含混——以论文小节为准：**Interaction Expert Layer = idea3 的架构 + idea1 的损失；Adaptive Fusion Layer = idea2 的兴趣感知**。

### 1.1 idea3 — MoE 显式解耦 U / R / S（§2.3.1，图 2c/2d）

四个专家，每个是独立 MLP，输入都是 `concat(e^img, e^txt)`：

$$\mathbf{e}^{j} = E_j(\mathbf{e}^{img}, \mathbf{e}^{txt}),\quad j \in \{\text{uni-i}, \text{uni-t}, \text{syn}, \text{rdn}\} \tag{1}$$

关键机制是 **随机掩码（random masking）**：把某一路模态换成随机向量 $\mathbf r$（每次迭代重采样），得到三种预测：

| 记号 | 输入 | 含义 |
| --- | --- | --- |
| $\mathbf y$ | $(\mathbf e^{img}, \mathbf e^{txt})$ | 完整多模态（anchor） |
| $\mathbf y^{img}$ | $(\mathbf e^{img}, \mathbf r)$ | 仅图像（文本被掩） |
| $\mathbf y^{txt}$ | $(\mathbf r, \mathbf e^{txt})$ | 仅文本（图像被掩） |

论文 Table 4 实测：Random 掩码 > Mean > Zero（Yelp 上 R@10 0.0422 / 0.0376 / 0.0361），理由是随机向量最彻底地切断残余信号泄漏。

### 1.2 idea1 — 三种交互特定损失（§2.3.2，公式 5–9）

这是论文自称的 **core innovation**。四个损失全部作用在 $(\mathbf y, \mathbf y^{img}, \mathbf y^{txt})$ 三元组上，只是 anchor/正/负的角色分配不同：

| 损失 | 公式 | 正例 | 负例 | 直觉 |
| --- | --- | --- | --- | --- |
| $\mathcal L_{\text{uni-i}}$ | $\text{Triplet}(\mathbf y, \mathbf y^{img}, \mathbf y^{txt})$ (5) | $\mathbf y^{img}$ | $\mathbf y^{txt}$ | 掩掉文本后预测应不变 → 该专家只吃图像独有信息 |
| $\mathcal L_{\text{uni-t}}$ | $\text{Triplet}(\mathbf y, \mathbf y^{txt}, \mathbf y^{img})$ (6) | $\mathbf y^{txt}$ | $\mathbf y^{img}$ | 对称 |
| $\mathcal L_{\text{syn}}$ | $\frac12[\cos(\mathbf y,\mathbf y^{img}) + \cos(\mathbf y,\mathbf y^{txt})]$ (7) | — | 两个都是负例 | 协同信息**只在双模态同时存在时涌现**，掩掉任一路就崩塌 → 逼 $\mathbf y$ 远离两个单模态预测 |
| $\mathcal L_{\text{rdn}}$ | $1 - \frac12[\cos(\mathbf y,\mathbf y^{img}) + \cos(\mathbf y,\mathbf y^{txt})]$ (8) | 两个都是正例 | — | 冗余信息两路都有，掩一路不该改变预测 |

$$\mathcal L_{\exp} = \lambda_{\text{uni-i}}\mathcal L_{\text{uni-i}} + \lambda_{\text{uni-t}}\mathcal L_{\text{uni-t}} + \lambda_{\text{syn}}\mathcal L_{\text{syn}} + \lambda_{\text{rdn}}\mathcal L_{\text{rdn}} \tag{9}$$

$$\mathcal L = \mathcal L_{\text{rec}} + \mathcal L_{\exp} \tag{12}$$

> ⚠️ **必须注意**：$\mathcal L_{\text{syn}} + \mathcal L_{\text{rdn}} \equiv 1$。这两个损失在数学上完全对立。之所以不冲突，**唯一原因是它们作用在两组独立参数的专家上**（$E_{\text{syn}}$ 与 $E_{\text{rdn}}$）。任何"共享专家骨干、只换 head"的省参数改造，都会让这两项梯度直接抵消（当 $\lambda_{\text{syn}}=\lambda_{\text{rdn}}$ 时精确为零）。移植时**四组参数必须完全独立**。

**PID 理论对应（附录 A.3，公式 13–20）**：

$$I(T; X^{img}, X^{txt}) = \text{Red} + \text{Syn} + \text{Unq}(T; X^{img}\setminus X^{txt}) + \text{Unq}(T; X^{txt}\setminus X^{img})$$

四个损失分别近似四项。**这也是第 5 节数据阻塞的理论依据**：如果两路特征互为确定性变换，则 $\text{Unq}=\text{Syn}=0$，四个专家退化成同一个。

### 1.3 idea2 — 兴趣感知的 Adaptive Fusion Layer（§2.4，公式 10–11）

$$w^{j} = \mathrm W\big(\mathbf e^{\text{uni-i}}, \mathbf e^{\text{uni-t}}, \mathbf e^{\text{syn}}, \mathbf e^{\text{rdn}}, \mathbf e^{id}\big),\quad \mathbf e^{m} = \sum_j w^j \mathbf e^{j} \tag{10,11}$$

$\mathrm W$ 是一个两层 MLP + temperature softmax。**"兴趣感知"体现在 $\mathbf e^{id}$ 这一项**——源码 `PRISM.py:246` 里是 `id_emb = item_embeddings.mean(dim=1)`，即**对序列维求均值**，等于"用户历史行为的平均画像"。这是整个 idea2 的技术核心，也是迁移到图 CF 时最需要重新设计的地方（§4.3）。

论文 §3.5 案例：无用户偏好引导时四类权重近乎均分；有引导时 synergy 权重升到 **40.27%**。

### 1.4 与 DGMRec / REARM 的差异

论文 §3.1 把基线分三组，第三组"Focused on Uniqueness and Redundancy"专门列 PAMD / DGMRec / REARM：**它们通过对比学习、正交约束或图建模解耦"模态独有 / 模态共享"，但不建模 synergy**。PRISM 的定位就是补上第三块。

**但消融表（Table 3, Yelp）给出的排序值得警惕**：

| 变体 | R@10 | 相对完整模型 |
| --- | --- | --- |
| PRISM 完整 | 0.0422 | — |
| w/o $E_{\text{uni-t}}$ | 0.0361 | **−14.5%** |
| w/o $E_{\text{uni-i}}$ | 0.0376 | −10.9% |
| w/o $E_{\text{syn}}$ | 0.0381 | **−9.7%** |
| w/o AFL | 0.0386 | −8.5% |
| w/o $E_{\text{rdn}}$ | 0.0391 | −7.3% |

**synergy 只排第三**，贡献低于两个 uniqueness 专家。论文的 headline claim（"我们显式建模 synergy"）与消融证据（"文本 uniqueness 才是最大贡献者"）之间存在张力。移植时应把这个当作**先验预期**：syn 专家能带来约 10% 量级的相对增益，但不是主力；如果我们的实现里 syn 消融后掉得比 uni 还多，反而要怀疑是实现串味了。

---

## 2. 源码校对：论文 vs `baseline/PRISM/PRISM.py` 的 5 处出入

移植前必读。逐条核对过 `PRISM.py` 全文（267 行）：

| # | 位置 | 论文写法 | 代码实际 | 移植处置 |
| --- | --- | --- | --- | --- |
| 1 | `PRISM.py:79` | $d(a,b) = 1-\cos(a,b)$（§2.3.2 明文） | `nn.TripletMarginLoss(margin=1.0, p=2)` → **欧氏距离** | 尺度敏感。LightGCN++ 有逐层 L2 归一化，**必须改成余弦版**，否则 margin=1.0 的量纲毫无意义 |
| 2 | `PRISM.py:18-24` `Expert.forward` | 标准 MLP + Dropout | `x = self.drop(x)` 作用在**输入** `x` 上且结果被丢弃，`out` 从未过 dropout → **dropout 是死代码** | 移植时修好（真加 dropout），或明确记录"按原样复现=无 dropout" |
| 3 | `PRISM.py:63` | 4 个专家 | `num_branches = num_modalities * num_experts_per_type + 2` = 4（当 `num_experts_per_type=1`） | 参数 `num_experts_per_type>1` 时分支数变多但 `forward()` 里 `expert_outputs[i]`/`[-2]`/`[-1]` 的索引假设会**错位**。保持 =1 |
| 4 | `PRISM.py:72-75` | λ 网格搜索 {0.01,…,1.0}，最优值在 §3.4 | 四个 λ **硬编码 = 0.1** | 需外提到 `world.py`/`parse.py` |
| 5 | `PRISM.py:243-266` `Adaptive_Fusion_Layer` | 输入含 $\mathbf e^{id}$ | `id_emb = item_embeddings.mean(dim=1)`（序列维均值） | **图 CF 无序列维**，这是迁移的核心改造点，见 §4.3 |

✅ 校对通过的部分：`forward_multiple` 的索引映射正确（`outputs[1]`=图像被替换=**文本单模态**，`outputs[2]`=文本被替换=**图像单模态**），与 §1.1 的表一致；`synergy_loss` 返回 $\overline{\cos}$（待最小化）、`redundancy_loss` 返回 $\overline{1-\cos}$，与公式 (7)(8) 严格一致。

---

## 3. 结构性鸿沟：SR → 图 CF 的四个不可直接迁移点

| # | PRISM 依赖 | LightGCN++ 现状 | 影响 |
| --- | --- | --- | --- |
| **G1** | 序列编码器 $S_j(\cdot)$ + 预测层 $P_j(\cdot)$，损失作用在**预测分数** $\mathbf y$ 上（公式 2–4） | 无序列编码器；"预测"= $\langle \mathbf e_u, \mathbf e_i\rangle$，且 $\mathbf e_i$ 要先过 $L$ 层图传播 | 若严格按论文在**分数级**算损失，每个专家每种掩码都要跑一次完整图传播 → **4 专家 × 3 条件 = 12 次稀疏矩阵乘 / batch**，CPU 上不可行 |
| **G2** | $\mathbf e^{id}$ = 用户序列的物品嵌入均值 → 天然是"用户兴趣" | 物品嵌入是全局的，没有 per-user 的物品集合视图（除非显式取邻居） | idea2 的"兴趣感知"必须重新定义 |
| **G3** | 融合结果直接喂序列编码器，**不经过图传播** | 融合结果注入 $\mathbf e^{(0)}_{\text{item}}$ 后要过 $L$ 层**逐节点 L2 归一化**传播 | 尺度敏感（`docs/lightgcnpp_idea2_mm.md` §1 已踩过这个坑）。专家输出**必须 L2 归一化后再融合** |
| **G4** | 图像 + 文本两个**异质**模态，来自预训练 CLIP 双塔 | 当前只有 CNN 4096 + CLIP 64 两个**同源合成视图** | 见 §5，这是硬阻塞 |

---

## 4. 集成方案

### 4.0 总体架构：PRISM 插进现有三级对齐

现有 `mm_align.py::MultiModalAligner` 的结构与 PRISM 的关系是**互补而非冲突**：

| 现有模块 | 职责 | PRISM 对应 | 处置 |
| --- | --- | --- | --- |
| **G1** 类型级投影 $v_t = \text{L2}(\text{MLP}_t(x_t))$，4096/64 → 64 | 尺度对齐 | 论文的 imgEmb/textEmb（预训练 CLIP 编码器） | ✅ **保留**，正好充当 modality encoder，让专家在 64 维空间工作（成本极低） |
| **G2** 类型感知门控 softmax(cos(v_t, 原型)) | 多视图聚合 | — | ❌ **被替换**：PRISM 的 MoE + AFL 是它的严格超集（G2 只有"哪个模态更重要"，PRISM 有"哪种**交互类型**更重要"） |
| **G3** 置信度门控 $c_i=\sigma(\cdot)$ + 残差融合 | 图文不符时退化为纯 ID | — | ✅ **保留**。这是本项目自有贡献（源自 MixRAGRec Knowledge Alignment），与 PRISM **正交**：PRISM 决定"注入**什么**"，G3 决定"**要不要**注入"。也是 idea3 成本感知的挂载点（见 `docs/lightgcnpp_roadmap_status.md` §3） |

改造后的数据流：

```
image_feat(4096) ──G1投影──┐
                            ├─→ [e^img; e^txt] (128) ─→ ┌─ E_uni-i ─┐
text_feat(1024) ───G1投影──┘        ↑ 随机掩码 r        ├─ E_uni-t ─┤ 4×64
                                                        ├─ E_syn   ─┤     ↓
                                                        └─ E_rdn   ─┘  AFL 加权
                                                                          ↓ e^m (64)
                                              G3 置信度门控 ─→ e^(0)_item = e^ID + c·(e^m − e^ID)
                                                                          ↓
                                              LightGCN++ α/β/γ 传播（不动）
```

### 4.1 idea3 落地 — Interaction Expert Layer

**新建 `baseline/LightGCNpp/code/prism_moe.py`**，从 `baseline/PRISM/PRISM.py` 移植，按 §2 修掉 5 处出入。

关键设计决定：**专家在 64 维投影空间工作，不在 4096 维原始空间**。
- 论文里专家输入 = `hidden_size × num_modalities` = 128（PRISM 的 CLIP 编码器已经降过维）
- 我们让 G1 承担降维职责，专家输入同样是 128 → 成本与论文一致
- 若跳过 G1 直接喂 4096+1024，专家第一层就是 5120×256，参数量暴涨 20 倍且尺度失控

**成本核算**（`n_items=18357`，专家 128→256→64）：

| 项 | 数值 |
| --- | --- |
| 单专家单条件全量前向 | 18357 × (128×256 + 256×64) ≈ 0.90 GMAC |
| 4 专家 × 3 条件 | ≈ 10.8 GMAC ≈ 21.7 GFLOP |
| 反向 ≈ 2× 前向 | 总 ≈ 65 GFLOP / 次全量刷新 |
| CPU 单线程（`OMP_NUM_THREADS=1` 强制，见环境备忘）约 2–5 GFLOPS | **13–30 s / 次** |

→ **必须沿用 `mm_align.py` 已有的 epoch 级投影缓存模式**（`project()` / `set_epoch()`），每 epoch 只刷新一次。
→ **更省的做法（推荐）**：损失只在**本 batch 涉及的物品**上算（`idx = cat(pos, neg).unique()`，约 4096 个 ≈ 22%）→ **3–7 s/epoch**。融合前向仍用全量缓存。这与现有 `bpr_loss` 里 `mm_aligner.contrastive_loss(idx)` 的写法完全一致，零心智负担。

### 4.2 idea1 落地 — 三种交互损失：表征级 vs 打分级

这是**整个集成里最关键的技术选择**（对应鸿沟 G1）。

| 方案 | $\mathbf y$ 的定义 | 每 batch 图传播次数 | 忠实度 | 判断 |
| --- | --- | --- | --- | --- |
| **A. 表征级**（推荐） | $\mathbf y_j = \mathbf e^j_i = E_j(\mathbf e^{img},\mathbf e^{txt})$，损失直接算在**专家输出嵌入**上 | **1**（不变） | 中：PID 近似退化为"表征空间的 PID"而非"预测空间的 PID" | ✅ **首选**。CPU 可行，改动局限在 `prism_moe.py` 内部 |
| **B. 打分级**（论文原味） | $\mathbf y_j = \langle \mathbf e_u^{(L)}, \mathbf e_{i,j}^{(L)}\rangle$，需对每个专家每种掩码单独传播 | **12** | 高 | ❌ 否决。稀疏矩阵乘 ×12，CPU 上每 epoch 从分钟级涨到小时级 |
| **C. 折中：伪打分级** | $\mathbf y_j = \langle \mathbf e_u^{(0)}, \mathbf e^j_i\rangle$，用**未传播**的用户 ego 嵌入打分 | **1** | 中高：保留了"损失作用在分数上"的语义 | 🔶 备选。若 A 的专家分化不明显（见 §6 诊断指标），换 C |

**选 A 的额外理由**：LightGCN++ 的传播含逐节点 L2 归一化，把余弦损失放在传播**之后**会与归一化操作纠缠，梯度路径变得难以分析；放在传播**之前**（表征级）则专家层是一个干净的、与图无关的模块，可独立调试。

**方案 A 的具体形式**（把公式 5–8 里的 $\mathbf y$ 换成 $\mathbf e$）：

$$\mathcal L_{\text{uni-i}} = \max\big(0,\ m + d_{\cos}(\mathbf e^{\text{uni-i}}, \mathbf e^{\text{uni-i}}_{img}) - d_{\cos}(\mathbf e^{\text{uni-i}}, \mathbf e^{\text{uni-i}}_{txt})\big),\quad d_{\cos}=1-\cos$$

$$\mathcal L_{\text{syn}} = \tfrac12\big[\cos(\mathbf e^{\text{syn}}, \mathbf e^{\text{syn}}_{img}) + \cos(\mathbf e^{\text{syn}}, \mathbf e^{\text{syn}}_{txt})\big],\qquad \mathcal L_{\text{rdn}} = 1 - \tfrac12[\cdots]$$

其中 $\mathbf e^j_{img} = E_j(\mathbf e^{img}, \mathbf r)$，$\mathbf e^j_{txt} = E_j(\mathbf r, \mathbf e^{txt})$，$\mathbf r \sim \mathcal N(0,I)$ **每 epoch 重采样**（论文是每 iteration，但我们用 epoch 缓存，只能降到 epoch 粒度——这是缓存换算力的必然代价，需在报告中声明）。

> **与 idea4 NLGCL 的关系**：NLGCL 作用在「层轴」（跨层对比），$\mathcal L_{\exp}$ 作用在「交互类型轴」，现有 idea2 InfoNCE 作用在「模态轴」。三者数学上不冲突，但**同时开三个对比项，`cl_reg`/`mm_reg`/`λ_*` 的相对量纲需要重新校准**——注意 `InfoNCE()` 用的是 `.sum()` 而非 `.mean()`（`model.py:236` 有注释），量纲比 λ 系列大 ~batch_size 倍。别直接把论文的 λ=0.1 抄进来就开跑。

### 4.3 idea2 落地 — 兴趣感知在图 CF 里怎么定义（对应鸿沟 G2）

PRISM 的 $\mathbf e^{id}$ = 序列物品嵌入均值。图 CF 里的**直接对应物**是：**用户在二部图上的一阶邻居均值**

$$\mathbf p_u = \text{L2}\Big(\frac{1}{|\mathcal N(u)|}\sum_{i\in\mathcal N(u)} \mathbf e_i^{ID}\Big)$$

这在语义上就是"用户历史行为的平均画像"，且 `dataset.UserItemNet` / `users_D` 已现成，一次预计算即可（稀疏矩阵乘一次，$\mathcal O(|E|d)$）。

但随之而来一个 SR 里不存在的问题：**权重的粒度**。

| 实例化 | 权重形状 | 融合发生在 | 优点 | 缺点 |
| --- | --- | --- | --- | --- |
| **A2-1 物品级** | $w^j_i$，$[n_i, 4]$ | 传播**前**，注入 $\mathbf e^{(0)}_{\text{item}}$ | 改动最小，完全复用现有 `fuse()` | **丢掉"兴趣感知"**——退化成 G2 的加强版，idea2 名存实亡 |
| **A2-2 用户级** | $w^j_u$，$[n_u, 4]$ | 传播**后**，作为打分残差项 | 真正 per-user 个性化，$\mathcal O(B\times4)$ | 融合信息**进不了图传播**，多模态信号无法沿边扩散 |
| **A2-3 双阶段（推荐）** | 两者都要 | 前 + 后 | 兼得：物品级融合喂图传播，用户级重加权做个性化打分 | 参数与调参量翻倍 |

**A2-2 / A2-3 的打分形式**：

$$\hat y_{ui} = \underbrace{\langle \mathbf e_u^{(L)}, \mathbf e_i^{(L)}\rangle}_{\text{LightGCN++ 原打分}} + \eta \cdot \big\langle \mathbf e_u^{(L)},\ \textstyle\sum_j w^j_u\, \mathbf e^j_i \big\rangle,\qquad w^j_u = \text{softmax}_\tau\big(\mathrm W([\mathbf p_u; \bar{\mathbf e}^{\text{uni-i}}; \bar{\mathbf e}^{\text{uni-t}}; \bar{\mathbf e}^{\text{syn}}; \bar{\mathbf e}^{\text{rdn}}])\big)$$

$\bar{\mathbf e}^{j}$ 是该专家在全体物品上的均值（作为"该交互类型的全局画像"，对应论文把四个专家嵌入喂进门控）。$\eta$ 是新超参，建议初始 0.1 并配 warmup。

**落地节奏建议**：先做 **A2-1**（一天内可跑通，验证 MoE+损失是否有效），确认 idea3+idea1 有正向增益后再加 **A2-2** 升级到 A2-3。**不要一次性上 A2-3**——三个新模块同时引入，出了问题无法归因。

### 4.4 代码改动清单

| 文件 | 改动 | 规模 |
| --- | --- | --- |
| `code/prism_moe.py` | **新建**。`InteractionExpertLayer`（4 专家 + 掩码 + 4 损失，余弦版 Triplet）、`AdaptiveFusionLayer`（A2-1 物品级 / A2-2 用户级双模式）。移植自 `baseline/PRISM/PRISM.py`，修 §2 的 5 处 | ~220 行 |
| `code/mm_align.py` | `MultiModalAligner.__init__` 增 `use_prism` 分支：为真时用 `InteractionExpertLayer + AdaptiveFusionLayer` 替代 `gate_weights()`；`fuse()` 里 pooled 的来源改为 AFL 输出；新增 `prism_loss(idx)` 返回 $\mathcal L_{\exp}$；`info` 里补 4 类权重均值 | ~60 行改动 |
| `code/model.py` | `bpr_loss` 在 `mm_reg*cl_mm` 后追加 `loss += self.mm_aligner.prism_loss(idx)`（λ 已在模块内加权）；A2-3 时 `getEmbedding`/`forward` 加残差打分项；`__init_weight` 预计算 $\mathbf p_u$ | ~30 行 |
| `code/parse.py` / `world.py` / `register.py` | 新增 `--use_prism --lam_uni_i --lam_uni_t --lam_syn --lam_rdn --prism_temp --prism_eta --afl_mode`，仿 `mm_reg` 的注册方式 | ~25 行 |
| `code/dataloader.py` | `_load_mm_feats` 已 `glob *.npy`，**放上 `text_feat.npy` 即自动加载，零改动** ✅ | 0 |
| `code/main.py` | config 名加 `_prism_s{λ_syn}u{λ_uni}`；每 5 epoch 打印四类权重分布（可解释性诊断，对应论文 §3.5） | ~15 行 |
| `code/run_prism.py` | **新建**，仿 `run_idea2.py` 的多种子驱动 | ~80 行 |

**⚠️ 缓存陷阱**（`LightGCNpp_analysis.md` §2.1 已警告过）：归一化邻接矩阵缓存为 `s_pre_adj_mat_{alpha}_{beta}.npz`。PRISM **不改图结构**，所以可以安全复用现有缓存——但如果后续做"多模态 item-item 图"扩展，**必须把结构标识写进文件名**，否则静默加载旧图。

### 4.5 关键代码骨架

```python
# code/prism_moe.py（要点节选）
class InteractionExpertLayer(nn.Module):
    """4 个参数完全独立的专家。切勿共享骨干——L_syn 与 L_rdn 会梯度抵消。"""
    def __init__(self, d=64, n_mod=2, hidden=256, lams=(0.1, 0.1, 0.1, 0.1)):
        super().__init__()
        self.names = ['uni_i', 'uni_t', 'syn', 'rdn']
        self.experts = nn.ModuleDict({
            n: nn.Sequential(nn.Linear(d * n_mod, hidden), nn.GELU(),
                             nn.Dropout(0.1),                 # 修出入#2：真的加 dropout
                             nn.Linear(hidden, d))
            for n in self.names})
        self.lam = dict(zip(self.names, lams))
        self.margin = 0.3

    @staticmethod
    def _cos(a, b):
        return F.cosine_similarity(a, b, dim=-1)

    def _triplet_cos(self, a, p, n):                          # 修出入#1：余弦距离版
        return F.relu(self.margin + (1 - self._cos(a, p)) - (1 - self._cos(a, n))).mean()

    def forward(self, e_img, e_txt, idx=None):
        r_i, r_t = torch.randn_like(e_img), torch.randn_like(e_txt)   # epoch 级重采样
        outs = {}
        for n, E in self.experts.items():
            full = F.normalize(E(torch.cat([e_img, e_txt], -1)), dim=-1)   # y
            only_i = F.normalize(E(torch.cat([e_img, r_t], -1)), dim=-1)   # y^img
            only_t = F.normalize(E(torch.cat([r_i, e_txt], -1)), dim=-1)   # y^txt
            outs[n] = (full, only_i, only_t)

        s = (slice(None) if idx is None else idx)             # 损失只在 batch 物品上算
        y, yi, yt = outs['uni_i']; L_ui = self._triplet_cos(y[s], yi[s], yt[s])
        y, yi, yt = outs['uni_t']; L_ut = self._triplet_cos(y[s], yt[s], yi[s])
        y, yi, yt = outs['syn'];   L_sy = 0.5 * (self._cos(y[s], yi[s]) + self._cos(y[s], yt[s])).mean()
        y, yi, yt = outs['rdn'];   L_rd = 1 - 0.5 * (self._cos(y[s], yi[s]) + self._cos(y[s], yt[s])).mean()

        L_exp = (self.lam['uni_i'] * L_ui + self.lam['uni_t'] * L_ut
                 + self.lam['syn'] * L_sy + self.lam['rdn'] * L_rd)
        embs = {n: outs[n][0] for n in self.names}            # 只有完整多模态输出参与融合
        return embs, L_exp, {'L_uni_i': L_ui.item(), 'L_uni_t': L_ut.item(),
                             'L_syn': L_sy.item(), 'L_rdn': L_rd.item()}
```

```python
# code/mm_align.py::MultiModalAligner.fuse （改造后）
def fuse(self, feats, id_emb, p_u=None):
    proj = self.project(feats)                                # G1 保留（epoch 缓存）
    self._last_proj_feats = proj
    if not proj:
        return id_emb, {'conf_mean': 0.0, 'n_types': 0}

    if self.use_prism:
        e_img, e_txt = proj[self.types[0]], proj[self.types[1]]
        expert_embs, self._prism_loss_cache, diag = self.prism(e_img, e_txt, self._batch_idx)
        pooled = self.afl(expert_embs, id_emb, p_u)           # 替代 G2 gate_weights
    else:
        gates = self.gate_weights(proj)                       # 旧 G2 路径（消融用）
        pooled = sum(gates[t] * proj[t] for t in proj)
    pooled = self._l2(pooled)                                 # 鸿沟 G3：喂图传播前必须归一化

    # ---- G3 置信度门控：原样保留 ----
    id_det = self._l2(id_emb.detach())
    c = torch.sigmoid(self.conf_mlp(torch.cat([pooled, id_det], -1))
                      + 2.0 * (pooled * id_det).sum(-1, keepdim=True))
    return id_emb + c * (pooled - id_emb), {...}
```

---

## 5. ⛔ 阻塞项：当前数据不满足 PID 可辨识条件

**这是本次分析最重要的发现，优先级高于所有模型设计。**

### 5.1 事实

`baseline/LightGCNpp/data/amazon-sports/` 只有两个特征文件，且都由 `prep_amazon_sports.py` 从**同一个 64 维 latent** 合成（源码 L76–86）：

```python
latent = RNG.normal(0, 1, size=(n_items, 64))          # 唯一信息源
clip   = latent / ||latent||                            # → image_feat_clip.npy (18357, 64)
W      = RNG.normal(0, 1/sqrt(64), size=(64, 4096))
cnn    = latent @ W                                     # → image_feat.npy      (18357, 4096)
```

即 `cnn` 是 `clip` 的一个**近似等距随机线性映射**。两者不是"图像和文本"，是**同一路信息的两套坐标**。

### 5.2 实测量化（1500 物品随机采样，112 万物品对）

| 指标 | 数值 | 含义 |
| --- | --- | --- |
| item-item 相似度 Pearson | **0.9915** | 两个视图给出的物品邻域几乎完全一致 |
| item-item 相似度 Spearman | **0.9907** | 排序层面同样一致 |
| 跨视图典型相关（64 维平均） | **0.994** | 全部 64 个方向都近乎完全相关，**没有任何一个方向是某一视图独有的** |

### 5.3 后果（直接映射到公式 13）

$$I(T; X^1, X^2) = \underbrace{\text{Red}}_{\approx\ \text{全部}} + \underbrace{\text{Syn}}_{\approx\ 0} + \underbrace{\text{Unq}_1}_{\approx\ 0} + \underbrace{\text{Unq}_2}_{\approx\ 0}$$

预期实验现象（可作为**验证本判断的预注册预测**）：
1. $\mathcal L_{\text{rdn}}$ 迅速降到 ≈ 0（冗余专家轻松达成目标）；
2. $\mathcal L_{\text{syn}}$ **卡在 ≈ 1 不降**（要 $\cos(\mathbf y,\mathbf y^{img})\to -1$，但信息全冗余，做不到）；
3. 两个 $\mathcal L_{\text{uni}}$ 停在 margin 附近（正负例本质无区分）；
4. AFL 权重四类近似均分（0.25 各），退化为简单平均；
5. **整体指标相对现有 idea2 基线无显著变化，甚至因多余参数轻微下降。**

**结论：在换数据之前，任何 PRISM 实验的"负结果"都不能归因于方法失效，只能归因于数据不可辨识。** 这类实验做了也不能写进论文。

### 5.4 解决路径

| 优先级 | 方案 | 说明 |
| --- | --- | --- |
| **P0（必做）** | 拉取 MMSSL 真实特征 | `fetch_mm_data.py` 的复制清单（L100）**已包含 `text_feat.npy`**，说明设计时就预留了。HKUDS/MMSSL 的 amazon-sports 提供 `image_feat.npy`(4096, CNN) + `text_feat.npy`(1024, Sentence-BERT)——**这才是真正的图像 + 文本双模态**。`dataloader._load_mm_feats` 用 `glob *.npy`，放进去即自动加载，**代码零改动** |
| **P0 配套** | item 映射对齐 | 已知问题（`docs/lightgcnpp_idea2_mm.md` §8.3）：MMSSL 版 10067 物品 vs 当前 SELFRec 版 18357 物品。**建议直接换用 MMSSL 的交互文件**，保证 item id 与特征行序 1:1，而不是做映射（映射会引入缺失特征的物品，又要额外处理） |
| **P1（兜底）** | 改造 `prep_amazon_sports.py`，合成**真正有 PID 结构**的特征 | 三段式：$x^{img} = [\,\mathbf u_{img};\ \mathbf s;\ f(\mathbf z)\,]$、$x^{txt} = [\,\mathbf u_{txt};\ \mathbf s;\ g(\mathbf z)\,]$，其中 $\mathbf u_*$ 各自独有、$\mathbf s$ 共享冗余、$\mathbf z$ 只能通过**双路联合**恢复（如 $\mathbf z$ 的 XOR/乘积编码）。这样 Unq/Red/Syn 三项的**真值已知**，可以直接验证四个专家是否学对了——比真实数据更适合做**机制正确性验证**，可作为论文的 synthetic sanity check 一节 |
| **P2** | 无外网时的替代 | 用 `redbook/` 的真实图文数据（项目内有 7737 张 jpg + 文本），自建小规模图文双模态数据集 |

> **建议顺序**：P1（合成可辨识数据，验证四个专家确实分化）→ P0（真实数据，验证效果增益）。P1 先做的理由：不依赖外网、可控、能直接产出"专家分化度"的定量证据，是 P0 的调试前置。

---

## 6. 实验设计

沿用项目既有的 P 编号（P0–P5 见 `baseline/docs/lightgcnpp_p0p1p2_report.md` 与 roadmap）：

| 阶段 | 内容 | 前置 | 判定标准 |
| --- | --- | --- | --- |
| **P6-a** | 合成可辨识 PID 数据（§5.4 P1）+ 专家分化诊断 | — | 四个损失曲线**分离**；$\mathcal L_{\text{syn}}$ 能降到 < 0.5；专家两两输出余弦 < 0.8 |
| **P6-b** | idea3 + idea1（MoE + 4 损失），AFL 用 A2-1 物品级 | P6-a 通过 | R@20 相对 idea2 基线 **> +2%**，否则不继续 |
| **P7** | idea2 升级：A2-2 用户级兴趣门控 → A2-3 双阶段 | P6-b 通过 | 相对 P6-b 再 **> +1%**；且四类权重分布**非均匀**（熵 < 1.3 nats，均分是 1.386） |
| **P8** | 换真实 MMSSL 图文特征重跑 P6-b / P7 | P0 数据到位 | 效果确认；同时对比合成 vs 真实的专家权重分布 |

**消融矩阵**（对齐论文 Table 3，全部在最优配置上跑 3 种子）：

| 变体 | 关闭内容 | 检验的问题 |
| --- | --- | --- |
| Full | — | — |
| w/o $E_{\text{syn}}$ | 去掉协同专家 + $\lambda_{\text{syn}}$ | **本文核心卖点**：显式建模 synergy 是否真有用 |
| w/o $E_{\text{rdn}}$ | 去掉冗余专家 | 论文里贡献最小（−7.3%），我们这边应类似 |
| w/o $E_{\text{uni-i}}$ / w/o $E_{\text{uni-t}}$ | 去掉单模态独有专家 | 论文里贡献最大，注意验证是否复现该排序 |
| w/o AFL | 四专家等权平均 | idea2 的价值 |
| w/o $\mathcal L_{\exp}$ | **保留 4 个专家但不加损失** | ⭐ **最关键的对照**——证明增益来自"损失驱动的分化"而非"多了 4 个 MLP 的容量" |
| w/o G3 | 去掉置信度门控 | 检验 PRISM 与本项目自有模块是否互补 |
| PRISM + NLGCL | idea4 同时开 | 三个对比损失是否打架 |

> `w/o L_exp` 这一栏论文**没有做**，但它是审稿人第一个会问的问题。必须补上。

**超参搜索预算**（论文网格 $\{0.01,0.05,0.1,0.2,0.5,1.0\}^4$ = 1296 组，CPU 上绝无可能）：

1. 固定 $\lambda_{\text{rdn}}=0.1$（论文 §3.4 明确说冗余系数**对变化容忍度大**）；
2. 令 $\lambda_{\text{uni-i}}=\lambda_{\text{uni-t}}=\lambda_{\text{uni}}$（对称设计，论文数值也接近）；
3. 二维网格 $\lambda_{\text{uni}} \times \lambda_{\text{syn}} \in \{0.05, 0.1, 0.5\}^2$ = **9 组**，单种子 20 epoch 选优；
4. 最优组 + 3 种子（2024/2025/2026）出最终数字。
   总计 **9 + 3 = 12 次训练**，与现有 `run_idea2.py` 的规模同量级。

**必须记录的诊断量**（每 5 epoch，写进日志，对应论文 §3.5 可解释性）：
`L_uni_i / L_uni_t / L_syn / L_rdn` 四条曲线、四类 AFL 权重均值与熵、专家输出两两余弦相似度矩阵、`conf_mean`（G3）。**专家间余弦相似度是判断"MoE 是否真的分化"的第一指标**——如果四个专家输出余弦都 > 0.95，那就是四个一样的 MLP，无论指标涨跌都不能声称做到了解耦。

---

## 7. 风险与失败模式

| 风险 | 概率 | 表现 | 缓解 |
| --- | --- | --- | --- |
| **数据不可辨识**（§5） | **已确认** | syn 损失不降、权重均分、指标持平 | 换数据，见 §5.4。**不解决就不要开跑** |
| 专家坍缩（四个 MLP 学成一样） | 中 | 专家两两余弦 > 0.95 | 加大 $\lambda$；检查是否误共享参数；margin 调大 |
| $\mathcal L_{\text{syn}}$ / $\mathcal L_{\text{rdn}}$ 梯度抵消 | 低但致命 | 两条曲线镜像、和恒为 1 且都不动 | **确认四组专家参数完全独立**（§1.2 的警告） |
| 尺度爆炸破坏图传播 | 中 | loss NaN，或 R@20 骤降到 ~0.00x | 融合前 L2 归一化（骨架已含）；`conf_mean` 若 → 1.0 说明门控失效 |
| 三个对比损失量纲打架 | 中高 | 开 NLGCL + mm InfoNCE + $\mathcal L_{\exp}$ 后反而变差 | 逐个开；注意 `InfoNCE` 用 `.sum()`（`model.py:236`），量纲差 batch_size 倍 |
| 表征级损失（方案 A）过弱 | 中 | 专家分化了但指标不涨 | 切方案 C（伪打分级，用 $\mathbf e_u^{(0)}$ 打分），改动约 20 行 |
| epoch 级掩码重采样导致方差大 | 低 | 种子间波动 > 2% | 降到"每 N 个 batch 刷新一次"，或固定多组 $\mathbf r$ 轮换 |
| CPU 算力不够 | 中 | 单 epoch > 5 min | 损失只在 batch 物品上算（§4.1）；专家 hidden 256 → 128 |

**一个不容易注意到的坑**：现有 `mm_align.project()` 的 epoch 缓存里，**只有刷新那一个 batch 带梯度**，其余 batch 用 detach 缓存。PRISM 的专家层如果也套这个缓存，意味着**四个专家每 epoch 只被更新一次**——20 epoch = 20 次梯度步，专家根本训不动。

→ **必须区别对待**：G1 投影（4096 维，贵）继续 epoch 缓存；**PRISM 专家层（128→64，便宜）每 batch 都要实算**，只在 batch 物品子集上算即可（4096 物品 × 12 次前向 ≈ 2.4 GMAC/batch，可接受）。这是从 idea2 迁移到 PRISM 时**最容易照抄出错**的地方。

---

## 8. 建议优先级

```
①  换数据（§5.4 P1 合成可辨识 → P0 真实 MMSSL 图文）   ← 唯一的真阻塞
②  P6-a 专家分化诊断（不看推荐指标，只看四条损失曲线和专家余弦）
③  P6-b idea3+idea1，AFL 用最简的 A2-1 物品级
④  消融，重点是 w/o L_exp 和 w/o E_syn
⑤  P7 idea2 真正的兴趣感知（A2-2 → A2-3）
⑥  P8 真实特征复跑 + 与 NLGCL 联合
```

**为什么把 idea2 排在最后**：它在图 CF 里的语义损失最大（鸿沟 G2），而论文消融里它的贡献（−8.5%）低于两个 uniqueness 专家，属于"最难迁移、收益中等"的组合。而 idea3+idea1 是一个不可分割的整体（没有损失，MoE 就只是四个随机 MLP），且在图 CF 里语义几乎无损——**先拿最确定的分**。

**与现有路线图的衔接**：`docs/lightgcnpp_roadmap_status.md` 里 idea1（自适应传播）已因 Oracle 增益仅 +1.96% 被放弃，idea2（知识对齐）实验中止无结果，idea3（成本感知）待设计。PRISM 恰好可以**接管 idea2 的位置并大幅升级它**——从"对齐后融合"升级为"解耦后个性化融合"，同时 G3 置信度门控原封不动保留，成本感知（原 idea3）仍可挂在 G3 上。也就是说，**PRISM 不是另起炉灶，而是把已中止的 idea2 从"能跑"推进到"有故事"**。

---

## 附录 A：PRISM 源码清单（`baseline/PRISM/`）

| 文件 | 说明 | 移植相关性 |
| --- | --- | --- |
| `PRISM.py` | **核心模块**：Expert / InteractionExpertWrapper / Interaction_Expert_Layer / MLPReWeighting / Adaptive_Fusion_Layer | ⭐⭐⭐ 全部 |
| `main.py` | 训练入口、参数解析 | ⭐ 参考 λ 参数注册 |
| `trainers.py` | 训练循环，`L_rec + L_exp` 的组装位置 | ⭐⭐ 参考损失拼装 |
| `SASRec.py` / `STOSA.py` / `InDiRec.py` | 三个 SR 骨干（PRISM 的宿主） | — 我们的宿主是 LightGCN++ |
| `modules.py` / `utils.py` / `datasets.py` | SR 通用组件（注意力、序列采样） | — 图 CF 用不上 |
| `data/DataProcessing.py` / `Image_download.py` / `process_clip.py` | **数据管线：图片下载 + CLIP 特征抽取** | ⭐⭐⭐ 直接可用于 §5.4 的真实图文特征制备（尤其 `process_clip.py`） |
| `InDiRec/` | InDiRec 独立实现 | — |
| `images/Model.png` | 架构图（图 2） | ⭐ 对照理解 |

> `data/process_clip.py` 值得单独点名：如果 MMSSL 下载不通（沙箱无外网），它提供了**从原始图文直接产出 CLIP 双塔特征**的完整脚本，配合 `redbook/` 的 7737 张真实图片，可以自建图文双模态数据集，绕开外网依赖。

## 附录 B：论文关键数字速查

- **数据集**：Home(66519/28238/551682)、Beauty(22363/12102/198502)、Sports(35598/18358/296337)、Yelp(287116/148523/4392169)，5-core，leave-one-out
- **指标**：R@10/20, N@10/20；5 次运行取平均；配对 t 检验 p<0.05
- **最佳结果**：PRISM+InDiRec，Home R@10=0.0364 / N@10=0.0235（HM4SR 0.0333 / 0.0191）；Yelp N@10 相对 REARM +10.91%
- **λ 网格**：{0.01, 0.05, 0.1, 0.2, 0.5, 1.0}，源码默认全 0.1；uniqueness 与 synergy 系数敏感，redundancy 容忍度大
- **掩码策略**：Random > Mean > Zero（Yelp R@10: 0.0422 / 0.0376 / 0.0361）
- **开销**：SASRec+PRISM 在 Sports 上 7.19 → 20.81 s/epoch（**+189%**）；Yelp 显存 1.45 → 4.61 GB（+218%）。**骨干越轻，PRISM 相对开销越大**——LightGCN++ 是极轻骨干，这个警告对我们尤其适用
