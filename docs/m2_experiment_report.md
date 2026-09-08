# M2 特征轴属性记忆（Feature-Axis Attribute Memory）实验报告

> **生成时间**: 2026-08-20
> **实验依据**: `docs/mmeacr_experiment_design.md`（M2 属性引导记忆，P1 核心）+ `docs/m1m3_experiment_report.md`（红线对照）
> **数据**: amazon-baby-mmssl（35598 用户 / 18357 物品，真实 CLIP 4096 + SBERT 384）
> **CF 轨**: `embs/amazon-baby-mmssl_seed2026_..._nl4_mm_mr0.001_mt0.1_fc0.8_pr32.pkl`（CF only R@20=0.0902）
> **脚本**: `baseline/LightGCNpp/code/run_m2_attribute_memory.py`（产物 `m2_attribute_axis.npz` + `m2_report.json`）

---

## 0. 结论速览

| 维度 | 结果 | 判定 |
|---|---|---|
| **机制① 属性轴构造** | K-means(K=9) on CLIP⊕SBERT + softmax(T=0.1) 锐化，簇规模 704~2852 无退化 | ✅ PASS |
| **机制② 强化-反思** | PA 真实 next-item 标签学习：violation 0.9095→0.9093，mean(sp−sn)=+0.0015（弱正信号），w 轻微分化 | ✅ 机制可运行（信号弱） |
| **机制③ 簇级信号** | 簇级 next-item hit@3 = **0.3829**（随机 0.3333，**+4.96pp**）→ 属性轴捕获真实品类偏好 | ✅ 可解释资产 |
| **机制④ 三段式门控** | DIRECT=12421 / FUSION=9209 / REJECT=13968（mean gate 0.318）→ 分布有意义 | ✅ 门控可运行 |
| **推荐增益（红线）** | 属性轨 R@20=0.0032；等权 RRF −32.2%；门控 RRF **−43.9%** | ❌ **FAIL**（不达 +2%） |

**一句话**：属性记忆机制完整落地且机制可归因（簇级信号真实存在），但**簇级偏好信号（hit@3=38%）无法转化为 item 级排名增益**——属性轨在 item 级仍是噪声，门控在簇级"信任"它反而放大稀释（门控 RRF 0.0506 < 等权 0.0611）。与 M1/E15 同构：CF 主导数据上内容/属性互补信号低于噪声地板。**M2 按设计红线退化为「可解释画像资产」**（供 MixRAGRec G4 verbalize），不主张推荐增益。

---

## 1. 设置（适配数据约束的机制移植）

### 数据约束 → 方案
- 数据**无 item 标题** → DeepSeek 语义属性提取无输入 → 属性轴改用 **K-means(K=9) 特征聚类**（镜像 MMEACR 9 属性维），DeepSeek 接口保留但未启用
- 冒烟实证：**行归一化会抹平判别力**（violation=1.0、w 不收敛）→ 改用 **softmax(T=0.1) 锐化亲和度**（保留区分度且天然归一）

### 机制管线
```
① 属性轴:   item_attr[i,k] = softmax_T(cos(item_i, centroid_k)),  K=9, T=0.1
② 强化-反思: 正确性信号 = 真实 next-item 标签（train 留一, 替代 MMEACR fuzz.ratio 合成标签）
            PA 排名学习全局属性重要性 w（命中强化/未命中反思）
③ 属性记忆:  P_u = w ⊙ mean(item_attr[train items of u])
④ 三段式门控: gate_score[u] = 簇级留一命中率（下一物品簇 ∈ 前缀 top-3 簇）
            DIRECT≥0.5 → w_attr=2.0 / FUSION 0.3~0.5 → w_attr=1.0 / REJECT<0.3 → w_attr=0
⑤ 融合:     门控 RRF vs 朴素等权 RRF vs 三单轨（attr/cf/eu）五路同口径 R@20/N@20
```

**门控粒度选择理由**：item 级 hit@20 对内容轨不可能达到（M1 实证 content-only R@20≈0.008），门控测属性轨**实际可达的簇级主张**（"用户下一品类选择是否正确"），与 MMEACR gate 语义对齐。

---

## 2. 机制验证（✅ 可归因）

| 机制 | 关键证据 |
|---|---|
| 属性轴构造 | 簇规模 {0:2447, 1:2852, 2:2279, 3:785, 4:1982, 5:2530, 6:2547, 7:2231, 8:704}，无空簇/退化簇 |
| 簇级信号 | **cluster-level next-item hit@3 = 0.3829**（随机 0.3333，+4.96pp；全库 35598 用户） |
| 强化-反思 | PA 5 epoch：violation 0.9095→0.9093，mean(sp−sn)=**+0.0015**（正，说明打分对正例有微弱偏好），w 范围 0.331~0.335（9 轴近乎等权 → 簇间无强判别性重要性） |
| 三段式门控 | DIRECT=12421(34.9%) / FUSION=9209(25.9%) / REJECT=13968(39.2%)，mean gate=0.318 |

**解读**：属性轴确实捕获了用户品类偏好的真实结构（+4.96pp 簇级命中），w 学习也确实从真实标签中提取了（微弱的）属性重要性信号。**机制本身可运行、可归因**。

---

## 3. 推荐增益（❌ FAIL，红线口径）

### 五路对比（35598 测试用户全量）

| 配置 | R@20 | N@20 | vs CF only |
|---|---|---|---|
| **CF only** | **0.0902** | 0.0457 | — |
| e_u only（M3 画像，红线对照） | 0.0081 | 0.0045 | -91% |
| **属性轨 only（M2）** | **0.0032** | 0.0013 | **-96%**（比 e_u 还差 60.8%） |
| RRF 等权 k60（MMEACR 默认） | 0.0611 | 0.0269 | **-32.2%** ❌ |
| **RRF 门控 k60（M2）** | **0.0506** | 0.0242 | **-43.9%** ❌ |

### 为什么否证（三点可归因分析）
1. **簇级信号 ≠ item 级排名**：属性轴在簇级有真实信号（hit@3=38%），但 18357 物品的全库 item 级 top-20 排名中，簇频率画像无法区分簇内物品 → 属性轨 R@20=0.0032，比连续余弦的 e_u 轨（0.0081）还差（聚类丢掉了簇内判别信息）。
2. **等权 RRF 稀释**（同 M1）：属性轨 top-20 几乎全是噪声，等权融合把噪声抬进 top-20 → −32.2%。
3. **门控粒度错配放大伤害（M2 独有发现）**：门控在簇级给出 DIRECT（35% 用户 w_attr=2.0），但轨在 item 级是噪声 → 门控 RRF（0.0506）**比等权 RRF（0.0611）更差**。"簇级正确、item 级噪声"的轨被门控信任后，稀释反而加剧。**门控测的主张粒度（簇）必须与融合决策的粒度（item）一致，否则门控会放大错误信任**——这是可复用的机制设计教训。

### 判定
按 `docs/mmeacr_experiment_design.md` M2 判据（双 seed R@20 ≥ +2%）：**−32%~−44% 远不达 → M2 FAIL（推荐增益）**。按设计红线：**退化为「可解释画像资产」**，不重蹈 E15 叙事膨胀。

---

## 4. 对后续实验的影响（更新路线）

| 项 | 结论 / 调整 |
|---|---|
| M2 属性记忆（推荐增益） | ❌ 关闭——簇级信号真实但 item 级无增益，与 M1/E15 三连互证 |
| **属性轴资产** | ✅ **保留为可解释资产**：`m2_attribute_axis.npz`（item_attr + centroids + w）供 MixRAGRec G4 verbalize（"用户 9 维属性画像"）+ E-X2 PID 归因对照 |
| 门控粒度教训 | 写入红线：**门控的主张粒度必须与融合决策粒度一致**（簇级门控 + item 级融合 = 放大错误信任） |
| M4 LLM 推理轨评估 | 保留待 GPU/成本：DeepSeek 排序轨是唯一可能有 item 级信号的第二轨（语义≠余弦相似度） |

---

## 5. 产物

- `baseline/LightGCNpp/code/run_m2_attribute_memory.py` — M2 脚本（属性轴 + PA 强化-反思 + 簇级门控 + 五路 RRF 对比）
- `baseline/LightGCNpp/code/m2_attribute_axis.npz` — 可解释属性轴资产（item_attr(18357,9) + centroids(9,4480) + w(9,)）
- `baseline/LightGCNpp/code/m2_report.json` — 全量结果
- 日志：`baseline/LightGCNpp/code/logs/m2_full.txt`（全量）/ `m2_smoke.txt`（冒烟）
