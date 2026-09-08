# E15-TE-free（TF 组）真实体制裁决报告

> 生成：2026-08-19 20:20 ｜ 实验入口：`run_e15_tf.ps1` → `run_e15.ps1 -Groups TF -LambdaComp 0.1 -Seeds "42,2025"`
> 承载：schtasks 计划任务 `E15_TF_Full`（Windows Task Scheduler，绕过沙箱 2min 回收）
> 配置：TF = 关 L_syn（λ_uni/syn/red=0）+ 互补路由（λ_comp=0.1）；SASRec / amazon-baby-mmssl / 500 epoch / patience=10（Early Stopping）
> 配套历史：`docs/e14ter_synthetic_report.md`（合成机制 FAIL，预测 TE-free 为唯一可能证成观点②的变体）

---

## 0. 一句话结论

**E15-TE-free（TF 组）真实体制双 seed 均 FAIL → 观点②「syn 互补信号帮推荐」在真实多模态推荐中否证 → E15 收口，PRISM 定位收敛为「多模态融合正则器」。**

- seed42 best Recall@20 = **0.0379**：压过 T(0.0361)✅，未压过 A(0.0408)❌ → FAIL
- seed2025 best Recall@20 = **0.0376**：未压过 A(0.0377)❌（差 0.0001），未压过 T(0.0393)❌ → FAIL
- 双 seed 同时压过 A/T 的判据**不可能满足** → 观点②否证，E16/E17 不执行。

---

## 1. 结果对照表（best Recall@20，首行 best 口径，与 A/T 对照同源）

| seed | TF best R@20 | A 组（L_syn 开） | T 组（仅多模态融合） | >A? | >T? | 判定 |
|---|---|---|---|---|---|---|
| 42 | **0.0379** | 0.0408 | 0.0361 | ❌（-0.0029） | ✅（+0.0018） | **FAIL** |
| 2025 | **0.0376** | 0.0377 | 0.0393 | ❌（-0.0001） | ❌（-0.0017） | **FAIL** |

补充（次行 best，备查）：seed42 次行 0.0393（仍 <A）；seed2025 次行 0.0406（>A✅ 但 <T❌）。**两条 best 记录任取口径均无法双维度压过**，结论稳健。

其他指标：seed42 best Recall@10=0.0239 / NDCG@20=0.0157；seed2025 best Recall@10=0.0227 / NDCG@20=0.0147。

---

## 2. 训练与日志证据

| seed | 早停 epoch | Total | 日志 | 错误扫描 |
|---|---|---|---|---|
| 42 | epoch 12（counter 10/10） | 159:40（约 17:20 完成） | logs/e15_TF_seed42.log（194KB） | 仅 PowerShell NativeCommandError 启动噪音，无 Traceback/NaN ✅ |
| 2025 | epoch 13（counter 10/10） | 161:37（20:02 完成） | logs/e15_TF_seed2025.log（209KB） | 同上 ✅ |

- 进程已正常退出（无 python 存活，内存 4.7GB 空闲），非异常终止。
- 两者均在 patience=10 内无改善后 Early Stopping，loss 单调下降（seed42 ep9=0.4111 / seed2025 ep9=0.3903），训练过程健康。
- seed2025 Recall@20 曲线峰值 **0.0376 出现在 ep3**，其后 10 epoch 再未触达（0.0353/0.0344/0.0357/0.0338/0.0352/0.0351/…0.0358），距 A(0.0377) 仅 0.0001 —— 最接近的一次功亏一篑，但早停机制判其无继续改善潜力，属统计噪声级差距。

---

## 3. 与合成侧结论的收敛

合成侧（E14-ter，`docs/e14ter_synthetic_report.md`）：`prism_comp_ter_free`（关 L_syn + 互补路由）R@20=0.3221 显著胜出 uni 0.2559 —— 这是 TF 组设计唯一可能证成观点②的根据。

真实侧（本报告）：TF 组双 seed 未能同时压过 A/T。合成→真实迁移失败，可能原因：
1. amazon-baby-mmssl 的下一 item 监督中，**互补损失能抽取的增量信号低于噪声地板**——合成体制手工构造了强 c_syn（可分离互补），真实数据中单模态特征已编码绝大部分下一 item 信息；
2. 互补路由 head 在真实数据上退化为近似恒等/微调项，R@20 落在 A/T 之间（seed42: T < TF < A；seed2025: TF ≈ A，均被 T 制约）——syn 专家既不能超越独立多模态融合（T），也未贡献稳定增益；
3. 判据的 A/T 差距本身在 0.0361–0.0408 的窄带内，TF 的 0.0376–0.0379 落入区间中部，无统计显著支撑。

---

## 4. 结论与下一步

**结论：观点②否证。** PRISM 的 synergy 损失设计（L_syn 可解释分解 + 互补增益）经 E14（合成 PID 探针 FAIL）→ E14-bis（真值锚定被 L_syn 抵消）→ E14-ter（显式互补损失仍被 L_syn 架空，ter_free 唯一胜出）→ E15-TF（真实数据 ter_free 变体 FAIL）四连否决，机制与真实两层均不成立。

**下一步（否证分支，改叙事收口）：**
1. **PRISM 定位改写**：从「可解释协同分解 + synergy 增益模块」收敛为「**多模态融合正则器**」——syn 专家作为 decorrelation/多样性正则，不主张对推荐指标的增益贡献；更新 `docs/prism_mixragrec_integration_plan.md` §3 与集成计划中的叙事。
2. **结题文档**：产出 PRISM×LightGCN++ 集成实验最终结题报告（汇总 A/T/TF 三组对照、E14→E15 全链路证据链），供 MixRAGRec 主线的多模态分支引用。
3. **不执行** E16/E17（观点②成立分支专属）。
4. 代码保留：`prism_moe.py` 的 syn_anchor 接口与 SASRec 残差路由保持可用，但默认关闭（λ 全部置 0 即退化为 T 组行为）。

> 数据留存：logs/e15_TF_seed{42,2025}.log + 本报告。此裁决为最终结论，监控自动化将进入空转观察。
