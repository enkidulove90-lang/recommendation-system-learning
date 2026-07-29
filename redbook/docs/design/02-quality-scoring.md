# 第 2 章：质量评分实现

实现位于 `redbook/automation/scoring.py` 的 `QualityScorerV2`。它不在评分阶段联网：引用、机构、主题和可复现性证据由第 1 章的标准化记录或缓存增强结果提供。

| 维度 | 权重 | 输入字段 |
| --- | ---: | --- |
| 学术影响力 | 0.20 | `citing_q1_ratio`、`citation_count`、`age_months` |
| 颠覆性 | 0.15 | `citing_focal_only`、`citing_prior_only`、`citing_both` |
| 绝对新颖性 | 0.20 | `problem_method_frequency` |
| 知识演化 | 0.15 | 方法、应用、数据集改进分 |
| 合作网络 | 0.10 | 机构、地域、作者数量 |
| 内容完整度 | 0.10 | MinerU/摘要完整度 |
| 可复现性 | 0.10 | 官方代码或可复现工具 |

颠覆性原始量为 `(N_i - N_j)/(N_i + N_j + N_k)`，实现中映射到 0–1。总分至少 0.72 时进入 `full_analysis`；否则为 `basic_only`。评分函数纯函数化，既可替换旧 `skills/quality_scorer.py` 的调用，也可在离线测试中复现。
