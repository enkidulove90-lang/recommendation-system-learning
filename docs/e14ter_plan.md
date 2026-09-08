# E14-ter：L_syn 改造方案（让 syn 承载互补内容）

> 起草日期：2026-08-17 ｜ 关联：E14(FAIL) / E14-bis(FAIL) / E15c(FAIL, 机制定位 L_syn) / E15(真实数据复现)
> 目标：回应用户观点②——「syn 正交残差可作多样性/互补信号帮推荐」——把 L_syn 从「纯 decorrelation 正则器」升级为「互补内容承载器」，使其在保留正交性的同时承载与预测目标 y 相关的信息。

---

## 0. 背景与动机（为什么必须改 L_syn）

| 实验 | 结论 | 对 L_syn 的含义 |
|---|---|---|
| E14 解耦探针 | syn 专家线性探针 R²=0.147 恒平（corr=0.015） | L_syn 未锚定真值协同，专家学任意正交方向 |
| E14-bis 真值锚定 | 无 L_syn 时 syn·c_syn cos=0.43；加 L_syn=0.5 即锁死 0.27（锚定 λ 扫到 10 仍 0.27） | L_syn 几何 decorrelation 在参数空间**抵消**锚定梯度 |
| E15c 互补路由 | ②分支关 L_syn → R@20=0.281≈baseline（机制有效）；开 L_syn → R@20=0.181（被抽干 FAIL） | syn 被锁在正交子空间后残差不含预测 y 所需信息 |

**根因（统一）**：当前 `synergy_loss`（PRISM.py:83-91）=
```python
def synergy_loss(self, anchor, negatives):
    # negatives = 单模态残缺版 (uni_v, uni_t)
    anchor_n = F.normalize(anchor, p=2, dim=-1)
    for neg in negatives:
        cos = einsum('bd,bd->b', anchor_n, F.normalize(neg, p=2, dim=-1))
        loss += cos.mean()
    return loss / len(negatives)
```
它**只做几何 decorrelation**（把 syn 推离单模态子空间），不锚定任何与 y 相关的信息 → syn 收敛到单模态子空间的任意正交方向 = 纯噪声。这正是 E14/E14-bis 失败的同一根因的两个侧面。

**用户观点②的可行性条件**：②成立 ⇔ syn 承载「与 y 相关、但在 {uni_v, uni_t} 子空间正交补方向」的内容。当前 L_syn 只满足「正交」，缺「与 y 相关」。E14-ter 补上后者。

---

## 1. 改造目标

```
syn  ⟶  与 {uni_v, uni_t} 正交  ∩  与预测目标 y 相关  的残差
        （保留 decorrelation / 多样性）   （新增 informativeness / 互补信号）
```

- 不抛弃 L_syn 的 decorrelation（这是②的多样性价值所在）；
- 新增互补监督，使 syn 的「正交补」分量可预测 y。
- 因互补项只看 `syn_⊥`（已强制正交），它**无法靠复制 uni 来满足** → 与 L_syn 对齐而非冲突，**修复 E14-bis 的梯度抵消**。

---

## 2. 数学定义

设单模态子空间 `E = span{uni_v, uni_t}`，`P_E(·)` 为到 E 的 Gram-Schmidt 投影（E15c `syn_complement` 已实现，复用）：

```
syn_⊥ = syn − P_E(syn)                      # 单模态子空间的正交补 = 纯互补信号
```

**当前**
```
L_syn^old = ½·[ cos(syn, uni_v) + cos(syn, uni_t) ]      # 仅 decorrelation
```

**E14-ter 新损失**
```
L_syn^ter = λ_dec · L_syn^old  +  λ_comp · L_comp

L_comp = dist( y_proxy , comp_head(syn_⊥) )
  · 合成体制：y_proxy = c_syn（真值正交协同，天然 ⊥ uni）→ dist = MSE
  · 真实体制：y_proxy = 下一 item 推荐监督（next-item embedding 或 CE logit 残差）
```

`comp_head`：轻量 `nn.Linear(hidden, hidden)`（与 E15c 同思路，但吸收进**主损失**而非仅路由）。

**关键不变量**：`syn_⊥` 已强制 ∈ E^⊥，故 L_comp 只能从 E 之外学 y 信息 → 与 L_syn^old 几何一致，无梯度抵消。

---

## 3. 改动落点（PRISM.py 原码，已打 P1-P5 补丁）

### 3.1 Interaction_Expert_Layer 内新增
```python
# init 中
self.comp_head = nn.Linear(hidden_size, hidden_size)          # 互补投影
self.lambda_comp = getattr(args, 'lambda_comp', 0.1)           # P5 同款破硬编码

# 类内（无 state，复用 E15c）
def syn_complement(self, expert_embs):
    uv = _l2(expert_embs["uni_v"]); ut = _l2(expert_embs["uni_t"]); s = _l2(expert_embs["syn"])
    utp = _l2(ut - (ut*uv).sum(-1,keepdim=True)*uv)
    proj = (s*uv).sum(-1,keepdim=True)*uv + (s*utp).sum(-1,keepdim=True)*utp
    return _l2(s - proj)

# 互补损失（合成/真实统一接口）
def synergy_complementary_loss(self, syn_perp, y_proxy):
    pred = self.comp_head(syn_perp)
    return F.mse_loss(pred, y_proxy)        # 真实体制可换成对比/CE
```

### 3.2 calculate_total_interaction_loss 增加一项
```python
comp = interaction_losses_dict.get("synergy_comp")
if comp is not None:
    total_loss += self.lambda_comp * comp
```

### 3.3 SASRec.finetune 接入（真实体制 y_proxy）
```python
embs = fusion_results["expert_embs"]
syn_perp = interaction_layer.syn_complement(embs)
comp_logit = torch.matmul(comp_head(syn_perp), item_emb.t())   # [B, n_item]
score = base_score + comp_logit                                   # 加性残差路由
# 复用现有 BPR/CE 推荐损失 → syn 拿到直接 y 梯度
```
合成体制则把 `y_proxy=c_syn` 传进 `synergy_complementary_loss`（ex15c 框架改造）。

---

## 4. 合成体制快速验证（复用 ex15c 框架 + TE 组）

- 在 `ex15c_complementarity.py` 的 5 对照基础上新增：
  - `prism_comp_ter`：λ_syn=0.5, λ_comp=0.5（开 decorrelation + 互补）
  - `prism_comp_ter_free`：λ_syn=0, λ_comp=0.5（对照 E15c 的 free，确认互补头本身）
- 指标：R@20 / `syn_probe_R2`(c_syn) / `pred_R2`。
- **判据 E14-ter PASS** ⟺
  1. `syn_probe_R2(ter)` > `syn_probe_R2(decorr 现骨架 0.147)`（修复 E14-bis 锚定）；
  2. syn·c_syn cos(ter) 显著高于 0.27；
  3. `R@20(ter)` ≥ `R@20(uni=0.256)`。
- 预期：ter 在保留 decorrelation 下恢复 c_syn 锚定 → 机制层证明②可在「syn 承载互补内容」前提下成立。

---

## 5. 真实体制测试（E15 变体，最终裁决场）

- 改 PRISM.py + SASRec.py 后，复用已转换 `data/amazon-baby-mmssl/`（异构 4096/384 特征，1-epoch smoke 已跑通 Recall@20=0.0265）。
- 新增 E15 变体组（run_e15.ps1 扩展）：
  - **E15-T**（原 λ=0.1，treatment）
  - **E15-TE**（T + E14-ter：λ_syn=0.1, λ_comp=0.1，让 syn 承载互补内容）
  - **E15-A**（λ 全=0，ablation / id-only）
  - （可选）**E15-V**（`--disable_mm`，纯 id-only 基线）
- **判据**：若 `Recall@20(E15-TE) > E15-T` 且 `> E15-A` → 观点②在真实数据成立（syn 互补信号确实帮推荐）；否则②仅在「多样性正则器」意义成立。

---

## 6. 能否在真实数据体制上测试 —— 结论

**可以，且是观点②的最终裁决场。**

- ✅ 数据已就绪：`data/amazon-baby-mmssl/`（image 4096d / text 384d / item 18359 / user 35598），1-epoch smoke 完成无报错。
- ✅ 零新增数据成本：真实体制无合成 c_syn 真值，y_proxy 直接复用 PRISM 既有的下一 item 推荐监督（BPR/CE），comp_head 残差路由进 item score。
- ⚠️ 注意点：
  1. `λ_comp` 与 `λ_syn` 需小网格扫（0.05 / 0.1 / 0.3）防 syn 坍缩到只追 y 而丢正交性；
  2. 真实体制 L_syn 本就有微弱增益（论文 claimed），E14-ter 须与 E15 T/A 同口径对照；
  3. 真实体制 syn 互补增益可能较小，需多 seed（42/2025）确认。
- 🔁 与 E15 并行策略：E15 后台跑真实复现（T+A）；E14-ter 先在合成体制（ex15c+TE，CPU 分钟级）快速验证机制，通过后再上真实数据，避免真实数据长跑白烧。

---

## 7. 风险与收敛叙事

- 若真实体制 E15-TE 无增益 → 证实 syn 在真实数据也未承载互补内容，观点②仅在「多样性正则器」意义成立；叙事收敛为：**「PRISM 是多模态多样性正则器，非可解释协同分解」**（与 E14/E14-bis 结论一致）。
- 与 E14-bis 关系：E14-ter **不推翻** E14-bis（syn ≠ PID 真值），而是提供「让 syn 承载互补内容」的改造路径，使②复用路线成立。

---

## 8. 待拍板（下一步）

- (a) 先落 **ex15c + TE** 合成验证（快，CPU 分钟级，先证机制）？
- (b) 直接改 **PRISM.py + SASRec.py** 上真实数据（E15-TE 组）？
- (c) 两者并行（推荐：合成证机制 + 真实给裁决）？

> 注：E15 当前真实训练（T+A）已于 2026-08-17 13:08 因后台进程被回收而停在 epoch1 batch23/140，本回合已重新以 detached 进程拉起（详见自动化 memory）。
