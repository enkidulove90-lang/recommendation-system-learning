# E14-bis 机制诊断结论（PRISM × MixRAGRec 集成）

> 关联：`docs/prism_mixragrec_integration_plan.md` §3.1 E14；`docs/prism_gate_a_report.md` §6（E14 FAIL 根因）；`baseline/LightGCNpp/code/ex14bis_anchor_probe.py`；`baseline/LightGCNpp/code/logs/ex14bis_cos/report.md`

## 1. 实验演进

E14 FAIL 根因（gate_a_report §6）：PRISM 的 `L_syn` 仅约束「syn 专家远离单模态残缺版」= 几何 decorrelation，未锚定真值 → syn 专家学任意正交方向（线性探针 R²=0.147 平台）。

E14-bis 干预（用户拍板）：给 syn 专家加「真值 c_syn 重建」辅助损失做锚定，重测探针。

**第一轮（naive MSE 锚定）**：`syn_anchor_lambda=0.5`，`F.mse_loss(syn_emb, c_syn)`。
- 结果：syn-R²=0.147（与无锚定完全相同）→ **锚定完全没生效**。
- 诊断发现（npz 验证）：`final_anchor=0.031` 是 per-element MSE，对 64 维单位向量等价于 `cos≈0`（正交水平，因 `per-element MSE = 2(1−cos)/d`）。误判 MSE 小=对齐好，实为正交。

**量纲修正**：L_syn 是 `mean cos`（梯度 O(1)），naive MSE 是 `per-element 平均`（梯度 O(1/64)）。即便 λ 同为 0.5，L_syn 梯度量级压过锚定约 50 倍 → 淹没锚定。
→ 改锚定损失为 **cos 距离（1−cos）**，与 L_syn 同量纲（`prism_moe.PRISMExpertLayer.syn_anchor_mode="cos"`）。

**第二轮（cos 锚定）**：`syn_anchor_lambda=0.5`，`1−cos(syn_emb, c_syn)`。
- 结果：syn-R²=0.155（w_syn=0.9），仍远低于 0.5 门槛 → **仍 FAIL**。
- 但比 MSE 锚定（0.147）略升，证实量纲修正方向对，但 L_syn 压制仍在。

## 2. λ 扫描诊断（铁证）

固定 `L_syn=0.5`，cos 锚定，扫 `syn_anchor_lambda`：

| anchor λ | syn·c_syn cos |
|---|---|
| 1.0 | 0.258 |
| 2.0 | 0.271 |
| 5.0 | 0.283 |
| 10.0（L_syn 的 20 倍） | 0.273 |

**锚定强度增大完全无效**：λ 从 1 到 10，cos 卡死在 0.27。排除「λ 不够」假说。

## 3. 最小对照（隔离干扰）

| 配置 | syn·c_syn cos |
|---|---|
| 纯锚定（L_syn=0, AFL=off） | **0.43** |
| 纯锚定（L_syn=0, AFL=on） | 0.28 |
| 带 L_syn=0.5（任意 anchor λ） | **0.27** |

→ 只要加 `L_syn=0.5`，syn 专家对齐 c_syn 的能力从 0.43 跌到 0.27，且锚定推不动。**L_syn 是元凶**。

## 4. 机制结论（耐久）

**PRISM 的 syn 专家在 `L_syn`（几何 decorrelation 交互损失）+ AFL 训练下，本质上无法被真值锚定拉向真协同 c_syn。** 根因：L_syn 强制 syn 专家「远离单模态残缺版」（与 ablate 版负相关），该几何约束在优化中占主导，把 syn 专家锁死在与真值 c_syn 正交的子空间；锚定梯度在参数空间被 L_syn 结构抵消（非简单 λ 竞争，因 λ=10 仍无效）。

这与 E14（无锚定，syn 学任意正交方向 R²=0.147）方向一致，但 E14-bis 证明**即使给真值锚定也救不回** → 排除「缺锚定信号」假说，确诊为**机制缺陷**。

**已排除的实现/超参嫌疑**：
- 锚定梯度断（最小对照纯锚定 cos=0.43，梯度工作）❌
- 量纲错配（改 cos 锚定后仍 0.27）❌
- λ 不够（扫到 10 仍 0.27）❌
- syn 专家容量不足（纯锚定 0.43）❌

## 5. E15 裁定

**E14-bis = FAIL（机制缺陷，非超参/量纲/实现 bug）→ E15 严格不开。**

PRISM 的 syn 专家不是真值协同的可靠估计器：既不能被高斯 MI 验证（E-X1c 盲区：乘积型 MI=0/分箱=1.27），也不能被真值锚定（E14-bis 机制锁死 cos≈0.27）。「可解释协同分解」的集成核心卖点不成立。

## 6. 下一步选项（待用户拍板）

1. **改 L_syn 设计（E14-ter）**：把 syn 专家的「远离 ablate」约束改为「与残差/真值一致」的约束（或把锚定融入 L_syn 作为主损失）。真实场景用 proxy 替代真值 c_syn。但 proxy 弱时 L_syn 仍可能压制，需重新验证门控。
2. **改叙事（推荐）**：承认 PRISM 4 专家是**多样性正则器**而非真 PID 分解器；集成价值改为「多样性正则带来的推荐增益」，E15 直接看 R@20（+2% 门槛），放弃可解释协同主张。
3. **放弃 PRISM 集成**：若可解释协同是硬需求，PRISM 的交互损失设计不满足，考虑替代（显式 PID 估计器 + 残差监督）。

## 7. 产物

- `baseline/LightGCNpp/code/ex14bis_anchor_probe.py`（E14-bis 脚本，支持 --anchor_mode cos/mse）
- `baseline/LightGCNpp/code/logs/ex14bis/report.md`（naive MSE 锚定，FAIL）
- `baseline/LightGCNpp/code/logs/ex14bis_cos/report.md`（cos 锚定，FAIL）
- `prism_moe.PRISMExpertLayer`：`syn_anchor_lambda` + `syn_anchor_mode`（cos/mse）接口已落地，供 E14-ter 复用
