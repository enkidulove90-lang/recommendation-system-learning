# PRISM × MixRAGRec × LightGCN++ 集成后续实验设计方案

> **生成时间**: 2026-08-17
> **范围**: 把三篇文档（`prism_analysis.md` / `MixRAGRec_analysis.md` / `mixragrec_prism_integration.md`）设想的集成，落成**可执行的实验矩阵**。
> **基线状态**（来自集成审计 + E13 终报）:
> - 当前落地资产：`baseline/PRISM/`（上游源码未改）、`baseline/MixRAGRec/`（105 文件未接线）、`data/amazon-baby-mmssl/`（真实图文特征，已解除 §5 的 Pearson=0.9915 不可辨识硬阻塞）、`code/pid_diagnostic.py`（§11 选项 A）+ 其四步扩展 `ex1b_target_probe.py`/`ex1c_nonlinear_probe.py`/`ex1d_nonlinear_real.py` 与 B 骨架 `prism_moe.py`（~17.6KB，冒烟通过未训练）。
> - **A 闸门裁决（2026-08-17）**：E-X1 四步链证真实数据 Synergy **不可判**（高斯 MI 仅见线性协同，E-X1c 盲区），但数据轴阻塞确已解除；**E14 合成探针升级为必做主证闸门，E15 须待 E14 通过**；后续 PID 一律换分箱/KSG。详见 `docs/prism_gate_a_report.md`。
> - **E13 已结案**：idea2 深度轴 nl4@EP100 均值 = 0.090897，与 E11(nl2@EP100=0.09039) 无显著差异 → 深度不抬顶，算力转真实特征 / 模块集成。
> - 最深的桥 = `R_MIG`（MixRAGRec 奖励）⟷ `PID 分解`（PRISM 理论）；最实用的桥 = `Expert Selector(RL)` ⟷ `Interaction Expert Layer(idea2)`；最稳的第一步 = 在真实特征上跑通 PID 诊断。

---

## 0. 设计原则（铁律）

1. **数据先于模型**：PRISM 实验一律跑在 `amazon-baby-mmssl`（真实 CLIP+SBERT），**绝不**回 `amazon-sports` 合成视图（Pearson=0.9915，Synergy≈0，任何负结果都不可归因）。
2. **表征级损失方案 A**（`prism_analysis.md §4.2`）：专家在 64 维投影空间工作，损失算在专家输出嵌入上，每 batch **只实算一次**（不套 `project()` 的 epoch 缓存）。
3. **四组专家参数完全独立**：`L_syn + L_rdn ≡ 1`，共享骨干会梯度抵消（§1.2 警告）。
4. **最小的改动单变量推进**：A2-1（物品级融合）先验，确认正向再加 A2-2/3；绝不一口气上三层新模块。
5. **CPU 沙箱只做表征层 + 诊断 + 数据预备**；MixRAGRec 生成式接线（G 组）必须上 GPU 机器。
6. **判别指标先看"专家分化"再看推荐指标**：专家两两余弦 > 0.95 即四个一样的 MLP，无论 R@20 涨跌都不能声称解耦。

---

## 1. 模块划分（3 大模块）

| 模块 | 来自 | 性质 | 算力 | 当前就绪度 |
|---|---|---|---|---|
| **M1 PRISM MoE 表征层** | `prism_analysis.md §4` | 训练（4 专家 + 3 交互损失 + AFL） | CPU 可训（3–7 s/epoch，batch 子集损失） | ❌ greenfield：`prism_moe.py`/`use_prism` 分支/`run_prism.py` 全缺 |
| **M2 PID 诊断 & Synergy 量化** | `pid_diagnostic.py` + `mixragrec_prism_integration.md §1` | 分析（CCA/MI/PID 分解 + R_MIG→PID 重构） | CPU | ⚠️ 框架就绪（M1/M2/M3），真实归因待 P6 经 `load_prism_moe()` 钩子替换 |
| **M3 MixRAGRec 生成式接线** | `mixragrec_prism_integration.md §1–§8` | 训练/接线（RL 路由 + LLM 生成 + MMAPO） | **GPU** | ❌ 仅上游源码 + 1 个诊断钩子 |

---

## 2. 跨模块可复用 Idea（即"可用的实验 idea"）

这些是文档里点到但未展开、或我额外提炼的高杠杆点子，**每条都能单独成实验**：

- **Idea-α 合成 PID 正确性探针（机制验证）**：照 `prism_analysis.md §5.4 P1` 造"真值已知"的图文（Unq/Red/Syn 用 XOR/乘积编码），训 PRISM MoE 后验证 4 专家是否还原真值。这是审稿人最买账的 *synthetic sanity check*，且**零外网依赖、CPU 可跑**，是给整条 PRISM 集成降风险的必做第一步。
- **Idea-β 数据质量门控（可复用工具）**：把 `pid_diagnostic.py` 的 CCA 冗余指数封装成 `paper_monitor` 的一个 checker——任何新数据集只要图文 Pearson/典型相关 > 0.99 就自动标红，永不再为不可辨识数据浪费算力。跨项目通用。
- **Idea-γ 专家分化度作训练信号**：用 4 专家输出两两余弦均值 `div` 构造 early-stop / 退火——`div` 不降则提前停（省算力），或把 `(1-div)` 当正则项逼专家分化。把"分化"从**看**的图变成**训**的信号。
- **Idea-δ 冷启动零样本迁移**：冻结训好的 PRISM MoE，取 4 路 PID 嵌入当物品**内容特征**，直接喂没见过的域 / 长尾冷物品做 LightGCN++ 冷启动 R@20。检验"解耦表征是否真有域外泛化力"（文档未提，纯新 idea）。
- **Idea-ε Synergy-aware 融合温度（双向耦合）**：`mixragrec_prism_integration.md §2` 只说了路由熵→AFL 温度，反向也可做——PRISM 算出的用户级 synergy 偏好标量直接调制 AFL 的 `τ`，synergy-seeking 用户用更尖锐的模态加权。
- **Idea-ζ Cost-aware MMAPO 零成本红利**：`idea3` 成本感知已落地（挂在 G3），`R_MIG` 的 `η·Cost` 项系数与 `eta_cost` 完全同构 → **不用写新代码**，只把已实现的成本模块暴露给 `RewardCalculator`（config `reward.eta_cost`）。最稳的胜利。

---

## 3. 实验矩阵（P 组=表征层 CPU / X 组=诊断&数据预备 CPU / G 组=生成式 GPU）

> **⚠️ A 闸门裁决更新（2026-08-17，覆盖本节及 §5/§7/§8 旧口径）** —— 详见 `docs/prism_gate_a_report.md`。
> 原"E-X1 确认真实特征 Synergy>0 → 开 E15"已被推翻。E-X1 扩展为四步反证链（E-X1→E-X1b→E-X1c→E-X1d），核心结论：
> 1. **数据轴阻塞确已解除**（冗余指数 0.0588，旧合成数据 0.991 → §5 硬阻塞的"数据轴"成立解除；
> 2. **真实数据 Synergy 不可判**：高斯 MI 仅见线性协同（E-X1c 证盲区：乘积型 MI=0.0000 / 分箱=1.2712，XOR 型 0.0001 / 0.5412），且 E-X1 阳性对照是自证循环（T=线性残差）→ 负结果**无权否定 PRISM**；
> 3. **E14 升级为必做主证闸门**：合成 PID 探针协同真值由构造给定、判据为"可学 MLP 能否学出协同"，绕开盲区与偏差地板；**E15 必须待 E14 通过才开**；
> 4. **后续 PID 归因一律换分箱/KSG 估计器**，高斯版仅留作线性基线。
> **严禁**因 E-X1d 出现"8/16 显著"（效应量 Syn/null_P95=1.20<1.3，偏差地板伪影）就直接开 E15。

> **🔴 E15-TF 最终裁决（2026-08-19，否证·收口，覆盖本节 P 组/G 组全部依赖 E15 的行）** —— 详见 `docs/e15_tf_report.md` + `docs/prism_conclusion_report.md`。
> 1. **E14 系列（合成 PID 探针）三连 FAIL**：E14（syn 线性探针 R² 恒平 0.147，L_syn 未锚真值）→ E14-bis（加真值锚定被 L_syn 结构抵消，λ 扫到 10 仍卡 cos≈0.27；纯锚定对照 0.43）→ E14-ter（显式互补损失仍被 L_syn 架空：带 L_syn R@20=0.1817<uni；**关 L_syn 的 ter_free 合成胜出 0.3221>uni 0.2559**）。
> 2. **E15-TE-free（TF 组，真实体制，用户拍板变体）双 seed FAIL**：seed42 best R@20=0.0379（>T 0.0361✅ <A 0.0408❌）、seed2025=0.0376（<A 0.0377❌ 差 0.0001 <T 0.0393❌）。首行口径双 seed 均不压；max 口径下 seed2025（0.0406）可压过 A/T，但 seed42（max 0.0393）仍 <A → **"双 seed 同时压过"判据任何口径均不成立 → 观点②真实体制否证**。
> 3. **根因收敛（机制层 + 数据层双重）**：L_syn 的"强制 syn⊥uni"与"承载与 y 相关互补内容"根本冲突（互补信息与单模态相关，不在 E^⊥ 里）；且真实下一 item 监督中互补信号低于噪声地板——合成可分离 c_syn ≠ 真实。
> 4. **PRISM 叙事正式收敛为「多模态融合正则器」**：syn 专家仅作 decorrelation/多样性正则，不主张对推荐指标的增益贡献。E16/E17/E18 取消；G1/G5 下架；G2 的 PID 归因改由 E-X2 独立承担。

### 3.1 P 组 — PRISM MoE 训练主线（M1 + M2，CPU）

> **状态（2026-08-19 后）：P 组主线已全部裁定/收口，不再新开训练。** 下表保留历史设计供追溯，执行状态以最后一列为准。

| ID | 内容 | 假设 | 关键配置 | 决策门 | 依赖 | 算力 | 实际状态 |
|---|---|---|---|---|---|---|---|
| **E14-0** | idea2 基线迁 `amazon-baby-mmssl` | 真实特征上 idea2 仍可跑通，建立 PRISM 对照靶 | `run_idea2.py --dataset amazon-baby-mmssl --only idea2 --seeds 2024,25,26` | R@20 > 0 且无 NaN；记下靶值 | — | CPU | ✅ 完成（E12/E13 深度轴 0.0909 结案，见 lightgcnpp_idea2_mm.md） |
| **E14** ⭐主证闸门 | 合成可辨识数据 + 专家分化诊断（Idea-α / §5.4 P1 / P6-a） | 4 专家能还原已知 Unq/Red/Syn 真值（协同真值由构造给定，不依赖 MI 估计） | 造数据脚本 + `prism_moe.py` 仅跑损失，20 ep | `L_syn<0.5`、专家两两余弦 < 0.8、4 损失曲线分离；PRISM 在 syn 主导配置显著超无交互基线 | 新造数据 | CPU | ❌ **FAIL**（syn 探针 R² 恒平 0.147，L_syn 仅几何 decorrelation 未锚真值） |
| **E14-bis** | syn 专家真值锚定干预（用户拍板） | 加 c_syn 重建辅助损失可把 syn 拉向真值 | `prism_moe.py` syn_anchor_lambda/syn_anchor_mode；MSE→cos 量纲修正 + λ 扫描 1→10 | syn·c_syn cos > 0.5 | E14 | CPU | ❌ **FAIL·机制缺陷**（纯锚定 0.43 → 带 L_syn 即 0.27，λ=10 仍无效） |
| **E14-ter** | 显式互补损失 L_comp（E14-bis 后选项①） | comp_head(syn_⊥) 可学剩余互补 | `synergy_complementary_loss` + 关 L_syn 变体 | R@20 ≥ uni | E14-bis | CPU | ❌ 本体 FAIL（0.1817<uni）；⚠️ **ter_free 合成胜出**（0.3221）→ 成 E15-TF 依据 |
| **E15** | PRISM MoE 真实特征 P6-b（A2-1 物品级） | MoE+损失 > idea2 基线 > +2% | `prism_moe.py` + `mm_align.use_prism` + `run_prism.py`；λ 9 组网格（§6）选优→3 seed | **⛔ 必须 E14 通过才开**；通过后 R@20 mean > E14-0 +2%，否则不继续 | E14-0, E14（E14 须 PASS） | CPU | ⛔ 原设计未开（E14 FAIL）；改以 **E15-TF（TE-free 变体）真实裁决**执行 → ❌ **否证**（见上） |
| **E16** | 消融 **w/o L_exp**（容量 vs 损失，审稿人第一问） | 增益来自"损失驱动分化"非"多了 4 个 MLP" | 保留 4 专家但不加 `prism_loss` | w/o L_exp 应显著低于 Full（否则 PRISM 故事不成立） | E15 | CPU | 🚫 **取消**（E15 否证，前提不存在） |
| **E17** | AFL 升级 P7（A2-2 用户级 → A2-3 双阶段） | 真实兴趣感知再 +1% | `afl_mode=user`/`dual`；`eta` warmup | 相对 E15 +>1% 且 4 类权重熵 < 1.3 nats（非均分） | E15 | CPU | 🚫 **取消**（同上） |
| **E18** | NLGCL × L_exp 联合（§4.2 风险 / P8） | 三对比损失不打架 | 开 `nlgcl_module` + `prism_loss`；重校 λ 量纲（注意 InfoNCE 用 `.sum()`） | 联合 ≥ 单开；若联合更差则逐个开定位冲突 | E15, E17 | CPU | 🚫 **取消**（同上）；NLGCL 单独已 PASS（lastfm R@20 0.2401→0.2680，见 §9 结题） |

> ~~**E15 超参预算**（沿用 §6，CPU 可行）：固定 `λ_rdn=0.1`，`λ_uni_i=λ_uni_t=λ_uni`，二维网格 `λ_uni × λ_syn ∈ {0.05,0.1,0.5}²` = 9 组单 seed 20 ep 选优 → +3 seed 出终数，共 12 次训练，与 `run_idea2.py` 同量级。~~ 已随 E15 否证作废。

### 3.2 X 组 — PID 诊断 & 数据预备（M2，CPU，**立刻可做**）

| ID | 内容 | 假设 | 关键动作 | 决策门 | 依赖 | 算力 |
|---|---|---|---|---|---|---|
| **E-X1** | 真实特征 PID 可辨识性四步诊断链（E-X1→E-X1b→E-X1c→E-X1d；挂 `pid_diagnostic.py` 及其扩展） | 数据轴阻塞确已解除（冗余指数 0.0588）；真实数据 Synergy 经四步链证为**不可判**（高斯 MI 盲区，非真无协同）→ 无权否定 PRISM | `pid_diagnostic.py`（E-X1）+ `ex1b_target_probe.py`（E-X1b）+ `ex1c_nonlinear_probe.py`（E-X1c 盲区检定）+ `ex1d_nonlinear_real.py`（E-X1d 分箱MI+置换+效应量守门） | 冗余指数 < 0.1（已 0.0588→数据轴解除）；四步全 EXIT=0；结论=不可判；**后续 PID 归因一律换分箱/KSG** | — | CPU |
| **E-X2** | R_MIG→PID 重构落到 `reward_functions.py`（§1，Idea 承接） | `compute_R_MIG`/`compute_delta_I` 能拆出每专家 PID 直方图 | 在 `RewardCalculator` 加 `pid_decompose(delta_I, cost)` → 输出 Unq/Syn/Red 贡献；改 `compute_total_reward` 返回 `pid_hist` | 单测 `test_reward_calculator` 仍过 + PID 字段非空 | — | CPU |
| **E-X3** | E1–E4 知识文件预备（§3 选项 B / §7 域统一） | `amazon-baby-mmssl` 可包装成 MixRAGRec 的 KG 替代品 | 扩 `pid_diagnostic.build_expert_signals` 落盘 `kg_e1_id.npy`/`e2_triple.npy`/`e3_2hop.npy`/`e4_syn.npy` | 4 文件行数 = N 物品，可被 MixRAGRec loader 读 | E-X1 | CPU |

### 3.3 G 组 — MixRAGRec 生成式接线（M3，GPU 机器）

> **状态（2026-08-19 后）：G1/G5 因依赖 E15 下架；G2 的 PID 归因改由 E-X2 独立承担；G3/G4/G6 保留但 G4 不再依赖 G1。**

| ID | 内容 | 假设 | 关键改动点（真实锚） | 决策门 | 依赖 | 算力 |
|---|---|---|---|---|---|---|
| ~~**G1**~~ | ~~Expert Selector 注入 PRISM synergy 偏好~~ | — | — | — | ~~E15, E-X3~~（E15 否证） | ~~GPU~~ 🚫 下架 |
| **G2** | R_MIG→PID 作 MMAPO 奖励（§1，P0） | 可诊断路由归因替代黑盒 KL | `reward_functions.compute_R_MIG` 调 E-X2 的 `pid_decompose`；`config.reward.lambda_mig/eta_cost` 已存在 | 训练后每专家 PID 直方图可解释 + 推荐指标不降 | **E-X2**（独立承担，不再依赖 E15） | GPU |
| **G3** | LightGCN++ ID 嵌入注入 LLM 重排（§4，P2） | CF 信号补 MixRAGRec 冷启动短板 | `RecommendationAgent` 后接 LightGCN++ 打分重排（最近邻映射选项→物品 ID） | 冷启动 / 长尾 R@20 提升 | E14-0（已完成） | GPU |
| **G4** | Knowledge Alignment LoRA ⟷ G2/G3 verbalize（§5，P2） | PID 三组件决定 prompt 写哪路知识 | `KnowledgeAlignment` 接 G3 门控输出 → NL | 生成解释与用户模态偏好一致 | E-X3, G3 | GPU |
| ~~**G5**~~ | ~~PRISM L_exp → DPO 偏好信号~~ | — | — | — | ~~E15~~（E15 否证） | ~~GPU~~ 🚫 下架 |
| **G6** | SynRAGRec 最小原型端到端（§8，选项 C） | 表征层喂生成层闭环成立 | `LightGCN++ → 多模态融合正则器 → MixRAGRec pipeline`（E2/E3/E4 知识文件驱动） | Top-K 指标 ≥ 各单模块；可解释输出可用 | G2, G3 | GPU |

---

## 4. 关键工程坑（移植必读，来自 §7 + 真实代码核对）

1. **`mm_align.project()` epoch 缓存陷阱（`mm_align.py:108–138`）**：G1 投影（4096→64，贵）继续 epoch 缓存；**PRISM 专家层（128→64，便宜）必须每 batch 实算**，只在 `idx = cat(pos,neg).unique()` 子集上算（~22% 物品）。否则 4 专家每 epoch 只更新 1 次 → 20 epoch 仅 20 步梯度，专家训不动。**这是从 idea2 迁 PRISM 最易照抄出错处。**
2. **`L_syn`/`L_rdn` 数学对立（§1.2）**：四组专家参数**完全独立**（`nn.ModuleDict` 各自 Sequential），任何共享 head 都会让两项梯度抵消。
3. **余弦版 Triplet（§2 出入#1）**：源码 `nn.TripletMarginLoss(p=2)` 是欧氏距离，LightGCN++ 有逐层 L2 归一化 → 必须改 `1-cos` 版本，否则 margin=1.0 量纲无意义。
4. **融合前 L2 归一化（§3 G3）**：专家输出必须 `F.normalize` 再喂 AFL、再喂 `e^(0)_item`，否则尺度爆炸破坏图传播（`conf_mean→1.0` 即门控失效）。
5. **三个对比损失量纲打架**：`InfoNCE()`（`model.py:236`）用 `.sum()` 非 `.mean()`，量纲比 λ 系列大约 `batch_size` 倍；开 NLGCL + mm InfoNCE + `L_exp` 时逐个开、重校（E18）。
6. **Dropout 死代码（§2 出入#2）**：移植时真加 `nn.Dropout`，或显式记录"按原样=无 dropout"。
7. **`num_experts_per_type` 必须 =1（§2 出入#3）**：否则 `forward` 索引错位。
8. **图结构缓存命名**：PRISM 不改图结构可复用 `s_pre_adj_mat_{alpha}_{beta}.npz`；若做"多模态 item-item 图"扩展，必须写进文件名防静默加载旧图。

---

## 5. 优先级路线图（now vs later）

```
🔴 2026-08-19 更新：E15-TF 否证收口后，原"E14 通过→E15→E16/17/18"链条已全部关闭。
✅ 已完成：E-X1 四步链（数据轴解除+盲区结论）、E14/E14-bis/E14-ter（合成三连 FAIL）、E15-TF（真实否证）、E14-0/idea2（真实特征，E12/E13 深度轴结案）
👇 现役路线：

立即（CPU）
  ├─ P0   PRISM 结题报告（docs/prism_conclusion_report.md）✅ 2026-08-20
  ├─ P1   MMEACR 属性引导记忆（新锚：e_u 画像升级 A2-2，强化-反思更新替代 L_syn）
  ├─ P2   RRF 融合（G 组前置，纯排序，零训练）
  └─ E-X2 R_MIG→PID 重构落到 reward_functions.py（G2 前置，独立于 E15）

近期（CPU）
  ├─ E-X3 E1–E4 知识文件落盘（G4 前置）
  └─ Idea-β 数据质量门控接入 paper_monitor

中期（CPU）
  └─ Idea-γ/δ 分化度信号 / 冷启动（复用 PRISM 正则器表征，不主张增益）

远期（GPU 机器）
  ├─ G2    R_MIG→PID 作 MMAPO 奖励（依赖 E-X2）
  ├─ G3    ID 嵌入注入 LLM 重排
  ├─ G4    Knowledge Alignment verbalize（依赖 E-X3, G3）
  └─ G6    SynRAGRec 端到端原型

🚫 已关闭：E15（原设计）/E16/E17/E18、G1/G5（依赖 E15 或 syn 偏好信号）
```

**算力分配建议**：深度轴已结案，idea2 系列剩余预算全转 **M1/M2（CPU 表征层 + 诊断）**；M3（G 组）等 GPU 机器到位再集中冲，中间用 E-X2/E-X3 把分析地基打好，避免 GPU 上"边训边补数据"。

---

## 6. 复用资产清单（不要重建）

- `baseline/PRISM/PRISM.py` — `InteractionExpertWrapper` / `Interaction_Expert_Layer` / `Adaptive_Fusion_Layer` 直接移植（修 §2 五处出入）。
- `baseline/LightGCNpp/code/run_idea2.py` — `run_prism.py` 镜像其 `--seeds/--force_c/--epochs` + 自动重跑 `MAX_RUN_ATTEMPTS` + `lock_key` 去重；复用 E13 的 `launch_safe.sh` 单实例 guard。
- `baseline/LightGCNpp/code/mm_align.py` — `project_subset()`(L140, 带梯度) 正是 PRISM 专家层要用的入口；`contrastive_loss(idx)`(L315) 写法可照搬。
- `baseline/LightGCNpp/code/pid_diagnostic.py` — `build_expert_signals` / `load_prism_moe` 钩子直接扩。
- `baseline/MixRAGRec/mixragrec/marl/reward_functions.py` — `RewardCalculator.compute_R_MIG` / `compute_delta_I` / `config['reward']['lambda_mig','eta_cost']` 现成。
- `baseline/MixRAGRec/mixragrec/agents/expert_selector.py` — `PolicyNetwork(state_dim=64)` / `_encode_state` 现成，注入点明确。
- `baseline/LightGCNpp/code/fetch_mm_data.py` — 已含 `text_feat.npy` 复制清单，数据拉取零改。

---

## 7. 立即动作选项（等你定夺）

> 🔴 **2026-08-19 更新**：本节的 A/B/C 已全部执行完毕并收口（E-X1 四步链 ✅ → E14/E14-bis/E14-ter 合成三连 FAIL → E15-TF 真实否证）。不再有"待跑"的 PRISM 训练动作。
> 现役立即动作转向：
> - **P1（推荐）**：MMEACR 属性引导记忆立项——用 e_u 用户画像升级 PRISM idea2 的 A2-2 输入，以强化-反思更新框架承接"原 L_syn 的角色"（详见 `docs/mmeacr_migration_analysis.md` §3.2/§3.3）。CPU 可跑、零 LLM 依赖。
> - **P2**：RRF 融合落地（G 组前置，纯排序，5 行代码量级），offline 验证双轨融合。
> - **E-X2**：R_MIG→PID 重构落到 `reward_functions.py`，为 G2 打地基。
> - **P0 收尾**：若本计划 §3 叙事仍被引用为"PRISM 增益"依据，一律以 `docs/prism_conclusion_report.md` 为准。

---

## 8. 风险登记

> 🔴 **2026-08-19 更新**：原"E15 通过后集成增益"相关风险项已随否证关闭；下表保留历史，标注现役状态。

| 风险 | 概率 | 触发表现 | 缓解（已在设计中） | 状态 |
|---|---|---|---|---|
| 真实数据 Synergy 不可判（高斯 MI 盲区） | 已转化为方法论结论（非阻塞） | E-X1c 证盲区、E-X1d 贴偏差地板 | 后续 PID 换分箱/KSG；主证闸门改 E14 合成探针（真值给定、MLP 可学性判据） | ✅ 已闭环 |
| 专家坍缩（4 个一样） | 中 | 专家两两余弦 > 0.95 | Idea-γ 分化度早停；加大 λ；查共享参数 | ⚠️ 不再追（PRISM 收口为正则器） |
| L_syn/L_rdn 抵消 | 低但致命 | 两曲线镜像、和恒 1 | 四专家参数完全独立（§1.2） | ✅ 已证 L_syn 本身即阻断点（E14-bis） |
| epoch 缓存套到专家层 | 中（最易踩） | 专家 20 ep 不分化 | §4 坑#1：专家层每 batch 实算 | ✅ 已在 E15 接线中解决（smoke PASS） |
| 三对比损失量纲打架 | 中高 | 联合反而更差 | E18 逐个开 + 重校 λ | 🚫 E18 取消（E15 否证） |
| G 组 GPU 算力未到位 | 高 | 无法训 MixRAGRec | X 组先把分析/数据地基打完，GPU 到位集中冲 | ⚠️ 仍现役（G2/G3/G4/G6 保留） |
| **PRISM 增益叙事被误用**（新增） | 中 | 文章/评审引用"PRISM 提升推荐" | 结题报告固化结论 + 本计划 §3 更新 + 文档互链 | 🔴 现役关注 |
