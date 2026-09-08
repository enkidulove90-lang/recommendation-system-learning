# E14-ter 合成体制机制判定报告

> 生成：2026-08-17 14:08 ｜ 实验脚本：`baseline/LightGCNpp/code/ex15c_complementarity.py`（新增 `prism_comp_ter` / `prism_comp_ter_free` 两组）
> 配套方案：`docs/e14ter_plan.md` ｜ 落地代码：`prism_moe.py::PRISMComplementarityNet.synergy_complementary_loss`
> 数据：合成 PID（N=1500, d=64, 乘积型协同 c_syn），3 seed × 3 w_syn 网格，CPU 分钟级

---

## 0. 一句话结论

**E14-ter 本体（保留 L_syn + 加显式互补损失 L_comp）在合成体制 FAIL**；但**关掉 L_syn 的 `prism_comp_ter_free` 显著胜出**（R@20=0.322 > uni 0.256 / baseline 0.284）。
根因：乘积型真值协同 `c_syn` 与单模态相关，**强制 syn⊥uni 后 syn_⊥ 根本承载不了 c_syn**。这推翻了方案 §2「c_syn 天然 ⊥ uni」的隐含假设。

---

## 1. 关键结果（高 w_syn=0.9，synergy 主导，3 seed 均值）

| 模型 | λ_syn | λ_comp | R@20 | pred_R2 | syn_probe_R2 | syn·c_syn cos | AFL_w[syn] |
|---|---|---|---|---|---|---|---|
| uni（仅双模态均值池） | — | — | **0.2559** | 0.9859 | — | — | — |
| baseline_mlp（等参） | — | — | 0.2837 | 0.9867 | — | — | — |
| prism_decorr（现骨架 4 专家+L_syn+AFL） | 0.5 | 0 | 0.1466 | 0.9845 | 0.1480 | -0.0041 | 0.1841 |
| prism_comp（② 互补路由，L_syn 开） | 0.5 | 0 | 0.1807 | 0.9845 | 0.1472 | 0.0019 | 0.2553 |
| **prism_comp_ter（E14-ter 本体）** | 0.5 | 0.5 | **0.1817** | 0.9845 | 0.1474 | 0.0017 | 0.2563 |
| **prism_comp_ter_free（E14-ter 关 L_syn）** | 0 | 0.5 | **0.3221** | 0.9879 | **0.2148** | 0.0007 | 0.2722 |

E14-ter 判据（方案 §4）：
- c1 syn_probe_R2(ter) > 0.147 → **PASS**（0.1474，刚过阈值）
- c2 syn·c_syn cos(ter) > 0.27 → **FAIL**（0.0017，与锁死值同量级）
- c3 R@20(ter) ≥ R@20(uni) → **FAIL**（0.1817 < 0.2559）
- **E14ter = ❌ FAIL**

对照 `prism_comp_ter_free`：R@20=0.3221（全场最佳）、syn_probe_R2=0.2148（显著高于 0.147）→ **显式互补损失本身有效，且仅在关 L_syn 时生效**。

---

## 2. 根因（机制层，决定性）

E14-ter 的设计前提是「syn_⊥ = syn − P_E(syn) 强制 ⊥ {uni_v, uni_t}，且 c_syn 也 ⊥ uni → L_comp 可在 E^⊥ 上学到 c_syn，与 L_syn 几何一致、无梯度抵消」。

**该前提对乘积型协同不成立**：
`c_syn = _unit(z_img@W_i * z_txt@W_t)`，而 `uni_v = _unit(z_img@W_i)`、`uni_t = _unit(z_txt@W_t)`。
标量层面 `a*b` 与 `a` 不正交（`Σ aᵢ²bᵢ ≠ 0`）；向量层面 `c_syn·uni_v = Σᵢ (z_img@W_i)ᵢ² (z_txt@W_t)ᵢ ≠ 0`。
→ **c_syn 与单模态子空间 E 显著相关**，其信息正落在 E 里。

因此：
1. L_syn 把 syn 锁在 E^⊥（远离 uni）→ 同时把 syn 推离「c_syn 所在的 E 方向」；
2. syn_⊥（= E^⊥ 里的 syn）天然**无法承载 c_syn 中位于 E 的那部分** → L_comp 的 MSE 地板高、学不动；
3. 加性残差路由 `pred = uni_head(uni_base) + comp_head(syn_⊥)` 的互补项被抽成噪声 → R@20 反低于 uni。

关 L_syn 后，syn 自由，可部分对齐 E 方向以编码 c_syn，syn_⊥ 仍能保留 c_syn 的正交残差 → `prism_comp_ter_free` 成功。

**这是 E14-bis（syn→c_syn 直接锚定被 L_syn 抵消）的同一根因的更深层表述**：L_syn 的「强制 syn⊥uni」与「让 syn 承载与 y 相关的互补内容」根本冲突——因为真实互补信息（c_syn / 下一 item）与单模态相关，不在 E^⊥ 里。

---

## 3. 对观点②与 PRISM 集成的判定

- **观点②「syn 正交残差可作互补信号帮推荐」**：机制层**部分成立**——
  - 互补路由本身（comp_head + 残差加法）**有效**（ter_free R@20=0.322 > uni 0.256，syn_probe_R2=0.215）；
  - 但**必须在 syn 不被 L_syn 锁死的前提下**才成立。PRISM 当前 L_syn 设计恰是这个锁死机制。
- **PRISM 集成核心卖点（可解释协同分解 + synergy 增益模块）不成立**：
  - E14：syn 专家线性探针 R²≈0.15，不能解码 PID 真值协同；
  - E14-bis：加真值锚定被 L_syn 梯度抵消；
  - E14-ter：加互补损失仍被 L_syn 架空（c_syn 与 uni 相关）；
  - 三连 FAIL 收敛到同一结论——**L_syn 下的 syn 专家只能当 decorrelation 正则 / 多样性噪声，既不能真值解码、也不能承载互补内容**。

---

## 4. 真实体制（E15-TE）预测与建议

基于合成机制，真实 amazon-baby-mmssl 的下一 item 预测同样**与单模态特征相关**（下一 item 的语义本就含图像/文本信息），故：

- **E15-TE（保留 L_syn + λ_comp，方案 §5 原设计）预计 FAIL**——同因：syn_⊥（⊥uni）承载不了与 uni 相关的下一 item 监督。
- **真正有信息量的真实实验是 E15-TE-free（互补路由 + 关 L_syn）**：它对应合成侧 `prism_comp_ter_free`，是唯一可能让 syn 互补信号在真实数据生效的变体；但它等于**放弃 PRISM 的 synergy 损失设计**（把 syn 专家退化成自由专家）。
- **收敛叙事**：若真实 E15-TE-free 也胜 T/A，则结论为「syn 互补增益可行，但需脱离 L_syn 架构」；若仍不赢，则「syn 互补信号在真实多模态推荐无稳定增益，PRISM 仅作多模态融合正则器」。

> 沙箱限制：本环境后台训练进程在 ~1 epoch 后被回收（见自动化 memory），500-epoch 真实 E15 无法在此跑完。真实体制裁决须在持久机执行；代码已就绪（PRISM.py + SASRec.py + run_e15.ps1 的 TE / TE-free 组），短 smoke 已验证可运行（见后续回合）。

---

## 5. 与 E14 / E14-bis / E15c 的序列关系

| 实验 | 问的问题 | 结论 |
|---|---|---|
| E14 | syn 专家能否线性解码真值 c_syn？ | ❌ R²≈0.15（高斯 MI 盲区绕开） |
| E14-bis | 加真值锚定能否修？ | ❌ 被 L_syn 梯度抵消（cos 锁 0.27） |
| E15c | syn 正交残差能否当互补信号帮推荐？ | ❌ 带 L_syn 时 R@20 反降；关 L_syn 的 free 胜 |
| **E14-ter（本）** | 加显式互补损失 L_comp 能否让 syn 承载互补内容？ | ❌ 带 L_syn 仍 FAIL；**关 L_syn 的 ter_free 成功（R@20=0.322）** |

四实验指向同一收敛：**L_syn（强制 syn⊥uni）是 PRISM synergy 模块在「可解释分解」与「互补增益」两条路上的共同阻断点**，根因是真实协同与单模态相关、不在 E^⊥。

---

## 6. 下一步选项（待拍板）

- **(A) 真实给裁决（按本结论修正）**：跑 E15-TE-free（互补路由 + 关 L_syn）而非原 E15-TE，作为唯一可能证成观点②的真实实验；原 E15-TE 预计 FAIL 可省算力。
- **(B) 改 L_syn 设计**：把 L_syn 从「强制 syn⊥uni」改为「鼓励 syn 与 uni 互补但不正交」（如 cos 下限而非惩罚），使 syn 可同时含 uni 相关信息与互补信息——需重新设计几何约束，工程量较大。
- **(C) 叙事收敛**：接受 PRISM 为「多模态多样性正则器 / 融合器」，放弃「可解释协同分解」卖点，论文据此改写；syn 互补增益路线仅作未来工作（脱离 L_syn 架构验证）。
