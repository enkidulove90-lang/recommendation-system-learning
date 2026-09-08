# PRISM × MixRAGRec 集成 — A 闸门诊断报告 & B 骨架交付

- **执行时间**：2026-08-17 10:06 – 10:19（沙箱 CPU）
- **依据文档**：`docs/prism_mixragrec_integration_plan.md`
- **执行路线**：用户选定的 **A+B 串行** —— A（E-X1 闸门）出结论，B（代码骨架）同期编写不训练
- **一句话结论**：**§5 硬阻塞的"数据轴"确认解除，但 A 闸门在真实数据上无法给出可信的 Synergy 阳性**——根因是诊断工具（高斯 MI 估计器）对 PRISM 所针对的非线性协同存在**盲区**（已实证）。故**不按文档原计划"Synergy>0 即开 E15"**，改为把 **E14 合成探针升级为必做前置且是主证**。

---

## 1. 执行了什么（A 闸门实际扩展为四步诊断链）

文档 §7 的 A 只有一步（跑 `pid_diagnostic.py`）。第一步返回的结果与文档预期相反（Synergy=0 而非 >0），我**没有直接接受这个负结果**，而是自建三步反证链去分辨"数据真的没协同"还是"工具测不出协同"。四步全部 EXIT=0。

| 步骤 | 脚本 | 状态 | 作用 |
|---|---|---|---|
| E-X1 | `pid_diagnostic.py`（已有） | ✅ | 文档指定的闸门本体 |
| E-X1b | `ex1b_target_probe.py`（新建） | ✅ | 换 target：popularity → CF-SVD 嵌入 |
| E-X1c | `ex1c_nonlinear_probe.py`（新建） | ✅ | **探针盲区检定**（关键） |
| E-X1d | `ex1d_nonlinear_real.py`（新建） | ✅ | 换非线性估计器 + 置换检验重测真实数据 |

---

## 2. 四步结果与逐步推理

### 2.1 E-X1：数据轴解锁 ✅，但目标轴 Synergy=0 ⚠️

真实数据 `amazon-baby-mmssl`：

```
典型相关 top-3 : [0.6817  0.5961  0.5143]
冗余指数(med r²) = 0.0588          ← 关键
PID{image,text} → popularity:
    Redundancy = 0.0015 (13.6%)
    Synergy    = 0.0000 ( 0.0%)
[阳性对照] T=人造 synergy 特征 → Syn=4.5646 (71.3%)
```

- **冗余指数 0.0588**（旧合成数据 Pearson=0.9915）→ 图文两路独立性强，**PID 在数据层面可辨识 = §5 的"数据轴"硬阻塞成立解除**。
- 但 `→popularity` 的 Synergy 精确为 0；同时阳性对照能检出 71.3%，所以**当时的初判是"工具没坏、是 target 太弱"**。
- 专家间归因同样为 0：`pid_2src(E1,E4,T)` → `Unq(E4)=0.0066, Syn=0.0000`，联合 MI=0.0355 ≤ 边缘和 0.0426（`Syn=max(0,-CI)` 在 CI>0 时必然被压成 0）。

### 2.2 E-X1b：换 CF 目标，Synergy 仍全 0

用 user–item 矩阵（BM25 加权）截断 SVD 造多维 CF 嵌入当 target，扫 `dim ∈ {4, 8, 16}`：**三档 Synergy 全为 0**，CI 全程为正（+0.0015 → +0.0173）。"弱 target"假说被推翻——换强 target 也测不出。

### 2.3 E-X1c：探针盲区证实（本次诊断最重要的发现）🔴

造三组**协同真值已知**的阳性对照，同一份数据分别用高斯 MI 与分箱 MI 估计：

| 对照组 | 构造 | 高斯 MI 测得 Syn | 分箱 MI 测得 Syn |
|---|---|---|---|
| P1 线性协同 | `(comb - proj_img - proj_txt)[:,0]` | **4.5646** ✅ | 0.0419 |
| P2 乘积型协同 | `img_pc1 × txt_pc1` | **0.0000** ❌ | **1.2712** ✅ |
| P3 XOR 型协同 | `sign(img_pc1) × sign(txt_pc1)` | **0.0001** ❌ | **0.5412** ✅ |

**两个结构性问题被同时暴露：**

1. **高斯 MI 只看得见线性协同。** P2/P3 是理论上的纯协同，高斯估计器读数≈0，分箱估计器全部检出。
2. **E-X1 的阳性对照是自证循环。** 它用的 T 恰好是线性最小二乘残差（P1 同型），天然可被高斯 MI 检出——所以"工具可正确检出 synergy"这句话只在线性范围内成立。

**推论：E-X1 / E-X1b 的负结果无权否定 PRISM。** PRISM 的交互专家是 MLP，本就是为非线性协同设计的，而验证它的探针恰好对非线性协同失明。

> 附带的方法论问题：`pid_2src` 用 interaction-information 分辨率（单标量 CI），`Syn=max(0,-CI)` 与 `Red=max(0,CI)` **数学上互斥**——不可能同时报出正 Synergy 和正 Redundancy。这不是 bug，但意味着它无法刻画"部分冗余+部分协同"的真实混合态。

### 2.4 E-X1d：换非线性估计器重测真实数据 → 不可判（贴地板）

换分箱 MI + 置换零假设（16 组 PC 对 × {popularity, CF-SVD pc1}，n_perm=20）：

```
target=popularity : 显著 1/16   最强 img_pc4×txt_pc3  Syn=0.0333 (null_P95=0.0320)
target=CF-SVD pc1 : 显著 8/16   最强 img_pc1×txt_pc2  Syn=0.0463 (null_P95=0.0385)
[效应量] 最大 Syn/null_P95 = 1.20   (阈值 ≥1.3)
[多重比较] 每 target 16 组合, α=0.05 期望假阳 ≈ 0.8 组
```

表面看 CF 目标 8/16 显著很像阳性，但我加了效应量守门后**主动推翻了它**：

- **效应量贴地板**：最大比值 1.20 < 1.3 阈值，观测值几乎骑在分箱估计器的正偏地板上。
- **置换零假设依赖不匹配（更致命）**：置换 T 会摧毁全部真实依赖，而观测态下 `I(T; txt)` 较强会抬高分箱偏差 → 零分布**系统性低估**偏差 → 显著性被高估。

**最终判定：⚠️ 不可判**，不是阴性也不是阳性。A 闸门在真实数据上无法给出可信结论。

---

## 3. 拍板结论

| 文档原计划 | 本次实测后的裁决 |
|---|---|
| A 跑通 → "Synergy 非 0" → 关 §5 硬阻塞 | **部分成立**：数据轴（冗余指数 0.0588）确认解除；Synergy 非 0 **未能证实** |
| Synergy>0 → 立刻开 E14 → E15 | **改**：E14 从"可选前置"升级为**必做前置且是主证**；E15 必须待 E14 通过再开 |
| 用 `pid_diagnostic.py` 做 PID 归因 | **改**：后续所有 PID 归因换分箱/KSG 估计器，高斯版仅留作线性基线 |

**为什么 E14 是唯一有效判据**：E14 是合成探针，协同真值由构造给定（不依赖 MI 估计）、判据是"可学 MLP 能否把协同分量学出来"（不依赖估计器偏差）。它同时绕开了 2.3 的盲区和 2.4 的偏差地板。若 E14 上 PRISM 能显著超过无交互专家的基线，才有理由把它接到真实数据上（E15+）。

**明确不建议做的事**：不要因为 2.4 出现"8/16 显著"就直接开 E15——那是偏差地板伪影，会把整条 λ 网格建在假阳性上。

---

## 4. B 骨架交付状态（已写，未训练执行）

按用户"现在就写不执行"的要求，`baseline/LightGCNpp/code/prism_moe.py`（~330 行）已完成，**文档 §4 的 8 个工程坑全部预修**：

| 坑 | 内容 | 骨架中的处置 |
|---|---|---|
| #1 | epoch 缓存陷阱 | 不提供任何 epoch 级缓存接口，专家层每 batch 实算 |
| #2 | L_syn·L_rdn 数学对立 | 4 组**完全独立** `nn.ModuleDict` 专家（冒烟实测共享 0 参数） |
| #3 | 欧氏 Triplet 与余弦空间不符 | `_cos_triplet`：`d = 1 - cos`，`margin=0.2` |
| #4 | 融合前未归一化 | `AdaptiveFusionLayer._l2` 兜底（冒烟实测 fused L2 = 1.0） |
| #5 | 三对比损失量纲打架 | `loss_dict` 回传**裸值**（未乘 λ），InfoNCE 用 `.sum()` |
| #6 | Dropout 死代码 | `Expert` 修正作用位置，默认 `dropout=0.0` 保可复现 |
| #7 | `num_experts_per_type` 须为 1 | 固定为 1，与 #2 的独立专家一致 |
| #8 | 图结构缓存命名 | 命名含 PRISM 配置签名，避免跨配置串缓存 |

**冒烟自检（形状/梯度，非训练）已通过**：

```
loss = 0.147787
loss_dict = {'uniqueness_v': 0.2183, 'uniqueness_t': 0.2439, 'synergy': 0.5313, 'redundancy': 0.4844}
fused (37, 64) | afl_w (37, 4) | afl_w rowsum = 1.0
div = -0.0091 | afl_entropy = 1.3801 | fused L2 norm = 1.0
param independence (kengt2): OK, 4 experts share 0 params
grad reaches img/txt: True True
SMOKE TEST PASS
```

尚未写（待 E14 放行后再动）：`mm_align.use_prism` 分支、`run_prism.py`（镜像 `run_idea2.py` 的 seed/retry/lock）。

---

## 5. 环境坑记录（重要，影响后续所有 torch 实验）

**`torch 2.13.0+cpu` 在 Git Bash（MSYS）壳层下必然 Segmentation fault（EXIT=139），在 PowerShell 下完全正常。**

```
# bash：仅 import torch 即 segfault
$ python.exe -c "import torch"        → EXIT=139  Segmentation fault

# PowerShell：正常
> & python.exe -c "import torch; print(torch.__version__)"
torch 2.13.0+cpu
```

- 与代码无关（纯 `import torch` 即崩），与 torch 安装无关（PowerShell 可用），是壳层 DLL 加载路径问题。
- **后续所有涉及 torch 的脚本（E14 及之后的全部训练/探针）必须走 PowerShell 启动**，不要用 bash。
- 纯 numpy/scipy 脚本（E-X1 ~ E-X1d）在 bash 下正常。

---

## 6. 产出文件清单

| 文件 | 类型 | 说明 |
|---|---|---|
| `baseline/LightGCNpp/code/prism_moe.py` | 新建 | B 骨架，预修 8 坑，冒烟通过未训练 |
| `baseline/LightGCNpp/code/ex1b_target_probe.py` | 新建 | CF-SVD 目标探针 |
| `baseline/LightGCNpp/code/ex1c_nonlinear_probe.py` | 新建 | 探针盲区检定（含分箱 MI / PID） |
| `baseline/LightGCNpp/code/ex1d_nonlinear_real.py` | 新建 | 非线性估计器 + 置换检验 + 效应量守门 |
| `baseline/LightGCNpp/code/_smoke_prism.py` | 新建 | 骨架形状/梯度自检 |
| `baseline/LightGCNpp/code/logs/ex1*.log`、`smoke_prism.log` | 新建 | 全部原始日志 |
| `docs/prism_gate_a_report.md` | 新建 | 本报告 |

---

## 7. 待用户确认

E14 合成 PID 探针（Idea-α）已具备全部前置条件（骨架就绪 + 判据明确 + 启动方式已知），**尚未动手**。请确认是否立即开工。建议的 E14 最小设计：

1. 构造已知真值的合成图文对：`uni_v` / `uni_t` / `syn`（乘积或 XOR 型）/ `rdn` 四分量按已知权重合成 target；
2. 对照组：`PRISMExpertLayer(use_afl=True)` vs 无交互专家的普通 MLP 基线（等参数量）；
3. 判据：PRISM 在协同主导配置（syn 权重高）上显著超基线，且 `export_pid_components` 落盘的 syn 分量与真值权重正相关；
4. 全程 PowerShell 启动，CPU 可跑，3 seed。
