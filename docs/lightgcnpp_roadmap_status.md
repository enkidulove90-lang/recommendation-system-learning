# LightGCN++ 四模块迁移 — 路线图状态与下一步设计

> **生成时间**: 2026-08-05
> **依据**: `docs/lightgcnpp_migration_design.md`（MixRAGRec → LightGCN++ 迁移设计）
> **配套**: `docs/lightgcnpp_idea2_mm.md`（idea2 实验报告，结果待填）

---

## 1. 四大 idea 当前状态

| idea | 内容 | 状态 | 关键结果（lastfm, seed2024） |
| --- | --- | --- | --- |
| **idea4 NLGCL** | 层间对比损失（纯 loss 插件，~30 行） | ✅ 完成 | R@20 0.2401→**0.2680**（+11.6% 相对），N@20 0.2354→0.2579 |
| **idea1 自适应传播** | 逐节点层权重 $w_u^{(l)}$ | ⛔ **放弃**（见 §2） | Oracle 上限仅 +2.0%，低于 3% 阈值 |
| **idea2 知识对齐** | align-then-fuse 多模态 | 🔄 训练中（本次恢复） | 3 种子 × 20 epoch 后台运行，结果待出 |
| **idea3 成本感知** | 给"知识引入"加成本标签（idea2 的 G3 门控） | ✅ 已实现（待跑，见 §3） | 挂 idea2 的 G3 置信度门控；新增 `cost_reg` 损失项 |

---

## 2. idea1 放弃的决策依据（设计文档 §1.2 判定线）

- **P2 Oracle 实验**（L=4，逐用户选最优层 $g_u^*$）：R@20 = **0.2448** vs 固定层基线 0.2401 → **+1.96% 相对增益**。
- 设计文档硬性规则：*Oracle 增益 < 3% → 放弃自适应，转做 idea3/idea4*。
- **含义**：不同节点对传播阶数的需求差异很小，自适应传播的上限收益不足以支撑其复杂度（方案 A/B/C 都要改 `computer()` + 新增参数/注意力）。idea4(NLGCL) 已用极小代价拿到 +11.6%，性价比远超 idea1。
- **结论**：不再实现 idea1 的方案 A/B/C，把算力留给 idea2 / idea3。

> 注：Oracle 在 lastfm 上测得。若后续换数据集（如 gowalla）想复核，可重跑 `run_P2` 流程（`--save_layer_emb 1` → `oracle_eval.py`），但阈值规则不变。

---

## 3. idea3 重构设计（挂到 idea2 而非 idea1）

原 idea3 是"给 idea1 的深度选择加价格标签"。idea1 放弃后，按设计文档 §0 的提示——*"成本项同样可约束'要不要引入外部知识'"*——**idea3 应改挂到 idea2 的知识引入决策上**：

- 现有 idea2 已有 **G3 置信度门控** $c_i=\sigma(\cdots)$ 控制"图文相符才引入视觉"。
- idea3 的增量：加一个**显式成本项**，约束"引入外部知识的样本比例 / 被门控屏蔽的样本数"，防止对齐器在噪声特征上过度引入外部知识：
  - 损失新增 `cost_reg · (1 - c_i).mean()`（或 `cost_reg · nnz(被引入)`），与已有 `mm_reg·L_mm` 并列；
  - 超参 `cost_reg` 接入 `world.py` / `parse.py` / `register.py`（仿 `mm_reg`）。
- **判定**：对比 idea2 有无 `cost_reg`，画 R@20 vs "知识引入率" 的 Pareto 曲线（等算力下比较，呼应设计文档 §1.5 的 iso-cost 思想）。

### 3.1 实现状态（2026-08-05 已完成编码，待 idea2 跑完后启动）

- `parse.py` / `world.py`：新增 `--cost_reg`（默认 0.0，关闭）。
- `mm_align.py::fuse()`：`info` 增加 `conf_vec`（逐物品知识引入权重 $c_i$，`[n_items,1]`）。
- `model.py`：`__init_weight` 读 `self.mm_cost_w = config.get('cost_reg',0.0)`；`bpr_loss` 在 idea2 块内复用 `idx`，加
  `cost_loss = mm_cost_w * c_vec[idx].mean()`（对知识引入率征税，实现成本-效果权衡）。
- `main.py`：`use_mm` 且 `cost_reg>0` 时 config 名追加 `_cr{cost_reg}`（与 idea2 日志隔离）。
- `run_idea2.py`：支持 `--only idea3 --cost_reg 0.01`，并复用已有 `results_idea2.json` 的 baseline/idea2_mm 做对比。
- 全部 6 文件 `py_compile` 通过；idea2 后台训练不受影响（用启动时的内存旧码）。

---

## 4. 推荐后续节奏（idea2 训练完成后）

1. **回填 idea2 结果**：用 `aggregate_idea2.py` 聚合 3 种子，填 `lightgcnpp_idea2_mm.md` 第 6 节结果表；若 R@20 相对基线正向 → idea2 成立。
2. **二选一推进**：
   - **(A) 强化 idea2**：切真实 MMSSL `image_feat.npy`（`fetch_mm_data.py`）+ 增至 50–100 epoch，确认**效果**（而非仅机制正确性）。
   - **(B) 实现 idea3 重构版**：在 idea2 上加成本感知门控，验证"成本–效果"权衡。
3. 时间允许时，(A)(B) 可合并为"对齐 + 成本感知"的最终多模态增强版。

---

## 5. 环境 / 复现备忘

- venv：`C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe`
- CPU 必设 4 个 env 变量（否则 torch 段错误）：`KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE`
- 后台运行：`run_idea2.py --only baseline|idea2 --epochs 20 --seeds 2024,2025,2026`
- 当前后台任务：baseline=`GS09Ax`，idea2=`cGV1ae`（3 种子 × 20 epoch）
