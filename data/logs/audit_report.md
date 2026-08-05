# 推荐系统论文解析链路 · 项目审计报告

> **生成时间**：2026-08-04 11:13  
> **审计范围**：`data/parsed/`（75 文件夹）、`data/summaries/`（110 文件）、`data/registry/`、`skills/`、`config/`、`pipeline/`  
> **审计目的**：对照优化提示词的 6 类问题，逐项诊断现状并输出可执行的整改清单

---

## 一、统计总览

| 指标 | 数值 |
|------|------|
| `data/parsed/` 文件夹总数 | 75 |
| 结构类型 A（MinerU 完整：.md + 4 JSON + .pdf + images/） | 40 |
| 结构类型 B（仅 .md + .pdf，无 JSON/images） | 5 |
| 结构类型 C（仅 images/ 目录） | 1 |
| 结构类型 D（含 images_hd/ 目录） | 5 |
| 结构类型 E（仅 .pdf，未解析） | 19 |
| 结构类型 F（不规则结构） | 5 |
| 命名模式：{arXiv ID}\_{中文标题} | 27 |
| 命名模式：{arXiv ID}\_{英文标题/缩写} | 29 |
| 命名模式：{arXiv ID} 仅 | 14 |
| 命名模式：非 arXiv 名称 | 5 |
| `data/summaries/` .md 文件数 | 69 |
| `data/summaries/` .json 文件数 | 41 |
| 同时有 .md + .json 的论文数 | 41 |
| 仅有 .md 的论文数 | 28 |
| 无任何摘要的 parsed 文件夹 | 6 |
| `papers.jsonl` 注册记录数 | 30 / 75 |
| `papers.jsonl` 中 research_directions 为空 | 8 / 30 |
| `_figures.json` 视觉描述文件数 | 0 |
| `data/logs/` 目录 | 不存在（本次创建） |
| `baseline/` 目录 | 不存在 |
| `.env` 文件 | 不存在 |
| `~/.workbuddy/skills/` 已有 Skill | 0 |

---

## 二、6 类问题诊断

### 问题 1：多任务交织无序

**诊断结论**：确认存在。当前管线将爬取、解析、摘要、整理、集成全部耦合在 `main.py` 的单一 CLI 流水线中，无阶段隔离。

**证据**：

| 检查项 | 现状 | 问题 |
|--------|------|------|
| `main.py` 流水线定义 | `爬取 → PDF下载 → MinerU解析 → DeepSeek摘要 → 文档合并` | 5 个步骤串行排列，无阶段边界、无质量门、无回退机制 |
| `pipeline/batch_pipeline.py` | 批量执行 parse → summarize → merge | 无阶段间校验，单篇失败直接跳过不记录 |
| `pipeline/merge_pipeline.py` | 文档合并器 | 合并时不检查摘要字段完整度 |
| Skill 封装 | `~/.workbuddy/skills/` 目录为空 | 11 维度摘要模板未封装为可复用 Skill |
| `.claude/skills/paper-summarize/SKILL.md` | 仅覆盖摘要生成的 8 字段 | 未涵盖解析、分类、整理、集成环节 |
| MixRAGRec 集成 | `baseline/` 目录不存在 | 源码未下载，集成设计未开始 |

**影响**：Agent 无法判断当前应执行哪个阶段，容易跳步（如未解析就生成摘要）或遗漏（如整理后未更新 papers.jsonl）。

---

### 问题 2：视觉模型未充分利用

**诊断结论**：确认存在。Qwen3.5-397B-A17B 视觉模型已在 `config/settings.py` 中配置环境变量，但项目中无任何代码实际调用它。

**证据**：

| 检查项 | 现状 | 问题 |
|--------|------|------|
| `config/settings.py` MODELSCOPE 配置 | `MODELSCOPE_API_KEY`、`MODELSCOPE_BASE_URL`、`MODELSCOPE_VISION_MODEL=Qwen/Qwen3.5-397B-A17B` 均已定义 | 配置存在但从未被使用 |
| `skills/` 目录 MODELSCOPE 引用 | `grep -r "MODELSCOPE\|modelscope\|Qwen3.5" skills/` → **0 匹配** | 无任何脚本调用视觉模型 API |
| `_figures.json` 文件数 | **0** | 75 个论文文件夹中无任何视觉图表描述文件 |
| 含 images/ 目录的文件夹 | 48 / 75 | 已提取图片但未做视觉理解 |
| 图片文件总数 | ~1488 个 .jpg + ~148 个 .png | 大量架构图/结果表未被结构化描述 |
| `skills/pdf_parser.py` vlm 模式 | 支持 `MINERU_MODEL_VERSION=vlm`，解析后保留 images/ 子目录 | L1 解析层正常工作，但 L2 增强层和 L3 校验层完全缺失 |
| 摘要中视觉信息 | 抽查 `2605.28175_summary.md`，无架构图描述、无结果表结构化提取 | 摘要完全基于文本，丢失图表关键信息 |

**影响**：架构图中的模块拓扑、结果表中的精确数值未进入摘要，摘要质量受限。

---

### 问题 3：质量门缺失

**诊断结论**：确认存在。解析→摘要→整理三个阶段之间无任何校验环节，仅有事后的论文质量评分（与管线无关）。

**证据**：

| 检查项 | 现状 | 问题 |
|--------|------|------|
| `skills/quality_scorer.py` | 评分维度：引用网络深度、引用数量、合作网络、主题新颖度、内容完整度 | 评估的是**论文本身的质量**，而非**解析/摘要的质量**；不作为管线门控 |
| `skills/profile_validator.py` | 校验 profile 与 evidence 的一致性、taxonomy 标签合规性 | 是事后校验，不在管线流程中；不检查解析→摘要的衔接 |
| `pipeline/batch_pipeline.py` 中的门控 | 无 | parse 失败后直接跳过，summarize 不检查 .md 是否完整 |
| 解析质量门（L3 校验层） | 不存在 | 无图片-文本交叉校验 |
| 摘要质量门 | `.claude/skills/paper-summarize/SKILL.md` 有 5 项 checklist | 仅在 Skill 文档中定义，未在代码中实现自动化检查 |
| `data/logs/` 目录 | **不存在** | 无 Phase 完成记录、无异常日志 |
| 摘要字段完整度自动检查 | 不存在 | 28 篇仅有 .md 的摘要未检查字段是否完整 |

**影响**：垃圾进垃圾出——19 个仅含 PDF 的文件夹无 .md 全文，但其中部分已有摘要（基于 PDF 直接生成），摘要质量不可控。

---

### 问题 4：摘要模板过时

**诊断结论**：确认存在。现有模板为 8 字段，新模板有 11 个维度，缺失 5 个关键维度。

**字段对照表**：

| # | 新 11 维度模板 | 旧 8 字段模板 | deepseek_summarizer.py JSON | 差异 |
|---|---------------|-------------|---------------------------|------|
| 0 | 元信息（标题/作者/venue/年份/arXiv ID/论文类型/一句话概括） | 头部元信息（标题/英文标题/arXiv ID/会议/作者/GitHub/创新评级） | paper_id, title, chinese_title | 旧模板缺 venue 年份；新模板增"论文类型"和"一句话概括" |
| 1 | **论文类型**（长文/短文/工业界/综述/复现 + 贡献类型分类） | ❌ 缺失 | ❌ 缺失 | **完全缺失** |
| 2 | 研究背景与问题定义（动机/任务类型/输入/输出/数学符号） | 部分含在"主要贡献"中 | main_contribution | 旧模板无问题形式化定义 |
| 3 | 主要创新点（主次分类/与最接近工作区别/自我评估） | 创新点（≥3条编号） | innovation_points | 旧模板无创新点分类和自我评估 |
| 4 | **方法与模块**（整体架构 + 模块清单表 + RecSys 常见模块速查） | 方法论（≥2句简述） | methodology | **模块拆解完全缺失**：旧模板仅一段话，新模板要求逐模块记录输入/输出/公式号/消融证据 |
| 5 | **训练策略**（损失函数/正负样本构造/优化流程/嵌入初始化） | ❌ 缺失 | ❌ 缺失 | **完全缺失** |
| 6 | 数据集选择（清单表 + 预处理切分 + 私有数据） | Benchmark 与数据集（表格） | benchmark_datasets | 旧模板无预处理/切分方式 |
| 7 | 实验与 Benchmark（指标/基线/结果表/在线实验） | 基线方法 + 实验效果（两个独立区块） | experimental_results | 旧模板拆分为两个区块，新模板统一；新模板增在线 A/B 实验维度 |
| 8 | **关联论文**（对标工作/方法论依据/同期后续） | ❌ 缺失 | ❌ 缺失 | **完全缺失** |
| 9 | **总结标准**（准确性/完整性/可复现导向/批判性/结构化） | ❌ 缺失 | ❌ 缺失 | **完全缺失**（质量自检标准） |
| 10 | **复现性自检清单**（代码/数据/超参/种子/硬件/公式/切分/负采样） | ❌ 缺失 | ❌ 缺失 | **完全缺失** |

**5 个缺失维度汇总**：

| 缺失维度 | 影响 |
|----------|------|
| 论文类型 | 无法区分综述/实验/系统/基准论文，分类策略无法差异化 |
| 模块拆解 | 无法支持 MixRAGRec 集成设计中的 knowledge_subgraph 构建 |
| 训练策略 | 无法评估可复现性，无法做训练策略层面的论文对比 |
| 关联论文 | 论文间关系网络断裂，推荐系统缺少关联依据 |
| 复现性检查 | 无法判断哪些论文值得投入复现 effort |

**摘要格式覆盖**：

| 格式 | 论文数 | 占比 |
|------|--------|------|
| .md + .json 双格式 | 41 | 59% |
| 仅 .md | 28 | 41% |
| 无摘要 | 6 | — |

---

### 问题 5：已有资产未复用

**诊断结论**：确认存在。`taxonomies.yaml` 受控词表已定义但项目中零代码引用。

**证据**：

| 资产 | 路径 | 状态 | 引用情况 |
|------|------|------|---------|
| 受控词表 | `data/registry/taxonomies.yaml` | ✅ 存在，4477 字节 | `grep -r "taxonomies" skills/ config/ pipeline/ models/ --include="*.py"` → **0 匹配** |
| 论文注册表 | `data/registry/papers.jsonl` | ✅ 存在，30 条记录 | 75 个文件夹中仅 30 个有注册记录（覆盖率 40%）；8 条记录的 research_directions 为空 |
| 推荐权重 | `config/recommendation_weights.yaml` | ✅ 存在，7 维加权 + 多样性约束 | `skills/relevance_recommender.py` 可能引用（需确认），但摘要生成时不使用 |
| 数据集注册表 | `data/registry/datasets.yaml` | ✅ 存在，1547 字节 | `deepseek_summarizer.py` 不引用，数据集名称为自由文本 |
| 研究画像 schema | `data/registry/research_profile_v2.schema.json` | ✅ 存在，16034 字节 | `profile_builder.py` 引用，但与摘要模板不对齐 |
| MinerU 解析器 | `skills/pdf_parser.py` | ✅ 存在，支持 vlm | 正常使用 |
| DeepSeek 摘要器 | `skills/deepseek_summarizer.py` | ✅ 存在 | 使用 8 字段模板，不引用 taxonomies |
| Profile 构建器 | `skills/profile_builder.py` | ✅ 存在 | 使用 research_profile_v2 schema，不引用新 11 维度模板 |
| 关系推荐器 | `skills/relevance_recommender.py` | ✅ 存在 | 单推荐器，未拆分为多 Agent |
| MixRAGRec 论文 | `data/parsed/2605.28175/` | ✅ 已解析（结构类型 A） | 源码未下载，分析未进行 |

**taxonomies.yaml 词表统计**：

| 词表类别 | 条目数 | 示例 |
|---------|--------|------|
| research_directions | 8 | agent_recommendation, multimodal_recommendation, llm_retrieval, llm_ranking, generative_recommendation, rag_recommendation, cold_start, efficient_retrieval |
| pipeline_stages | 8 | candidate_generation, pre_ranking, ranking, reranking, retrieval_index, user_modeling, online_learning, evaluation |
| problems | 9 | cold_start, long_tail, sparsity, debiasing, fairness, efficiency, robustness, missing_modality, explainability |
| technical_paradigms | 9 | collaborative_filtering, gnn, transformer, llm, rag, reinforcement_learning, causal_inference, contrastive_learning, diffusion |
| modalities | 7 | id, text, image, video, audio, knowledge_graph, behavior_sequence |
| paper_type | 6 | survey, experiment, system, benchmark, dataset, theory |
| maturity | 3 | research_prototype, industrial_validation, conceptual |

**影响**：分类口径不一致——papers.jsonl 中的标签可能使用自由文本而非受控词表；新论文分类时无标准可循。

---

### 问题 6：文件夹不一致

**诊断结论**：确认存在。75 个文件夹有 6 种内部结构、4 种命名模式。

#### 6.1 内部结构类型分布

| 类型 | 描述 | 数量 | 占比 | 代表文件夹 |
|------|------|------|------|-----------|
| A_complete | .md + 4 JSON (\_content/\_content_full/\_layout/\_model) + .pdf + images/ | 40 | 53% | `2605.28175`, `2501.01945_大模型冷启动推荐综述` |
| B_md_pdf_only | 仅 .md + .pdf，无 JSON 或 images/ | 5 | 7% | `2403.06447`, `2404.16924`, `2504.16420`, `2505.09777`, `2606.26859` |
| C_images_only | 仅 images/ 目录，无 .md/.pdf/.json | 1 | 1% | `2507.02626` |
| D_with_hd | 含 images_hd/ 目录（部分含完整结构，部分仅 hd） | 5 | 7% | `2412.19302`, `2507.21892`, `2604.08011`, `2606.24597_qwen_agentworld`, `2607.04433_agentic_recs` |
| E_pdf_only | 仅一个 .pdf 文件，完全未解析 | 19 | 25% | `2505.19525_ConfSMoE`, `2508.05352_M3BSR`, `2002.02126_LightGCN` 等 |
| F_special | 不规则结构（有 md+img 但无 JSON / 容器文件夹） | 5 | 7% | `2606.12373_races`, `2607.02980`, `gpt-red`, `mineru_july_2026`, `ra-rft` |

**关键发现**：
- 19 个文件夹（25%）仅有 PDF，从未被 MinerU 解析——包括两篇目标论文 `2505.19525` (ConfSMoE) 和 `2508.05352` (M3BSR)
- `2507.02626` 存在两个文件夹：`2507.02626`（仅 images/）和 `2507.02626_VRAgent-R1：强化学习增强视频推荐`（完整结构），属于重复/分裂
- `mineru_july_2026` 是容器文件夹，内含 `meta-ra-rft`、`mmeacr`、`tencent-hils` 三个子文件夹
- 5 个 D 类文件夹的 images_hd/ 应合并到 images/

#### 6.2 命名模式分布

| 模式 | 示例 | 数量 | 占比 |
|------|------|------|------|
| {arXiv ID}\_{中文标题} | `2501.01945_大模型冷启动推荐综述` | 27 | 36% |
| {arXiv ID}\_{英文标题/缩写} | `2505.19525_ConfSMoE` | 29 | 39% |
| {arXiv ID} 仅 | `2403.06447`, `2605.28175` | 14 | 19% |
| 非 arXiv 名称 | `AMMRM`, `gpt-red`, `LightGCN++`, `mineru_july_2026`, `ra-rft` | 5 | 7% |

**关键问题**：
- 中文标题与英文标题混用，无法统一排序/检索
- 14 个文件夹仅有 arXiv ID，无法直观识别论文内容
- 5 个非 arXiv 名称文件夹无法通过 ID 关联到 papers.jsonl
- 无方向标签（如 `_[llm_ranking×efficient_retrieval]`），无法按分类浏览

---

## 三、整改清单

### 需重新解析列表（结构类型 C/E 或 .md 缺失）

共 **20** 个文件夹需重新解析（19 个 E 类 + 1 个 C 类）：

| # | 文件夹 | 当前状态 | 优先级 |
|---|--------|---------|--------|
| 1 | `2505.19525_ConfSMoE` | 仅 ConfSMoE.pdf | **P0（目标论文）** |
| 2 | `2508.05352_M3BSR` | 仅 paper.pdf | **P0（目标论文）** |
| 3 | `2002.02126_LightGCN` | 仅 LightGCN.pdf | P1 |
| 4 | `2302.10632_MMSSL` | 仅 .pdf | P1 |
| 5 | `2303.05979_SingleBranch` | 仅 .pdf | P1 |
| 6 | `2308.15980_AMF多模态自适应融合` | 仅 .pdf | P1 |
| 7 | `2412.14978_SMORE` | 仅 .pdf | P1 |
| 8 | `2504.16524_MARGO` | 仅 .pdf | P1 |
| 9 | `2506.00107_门控多模态图学习推荐` | 仅 .pdf | P1 |
| 10 | `2508.04247_I3-MRec` | 仅 .pdf | P1 |
| 11 | `2508.08042_MAMEX` | 仅 .pdf | P1 |
| 12 | `2601.10944_PRISM` | 仅 .pdf | P1 |
| 13 | `2601.22498_FITMM` | 仅 .pdf | P1 |
| 14 | `2602.00682_RecGOAT` | 仅 .pdf | P1 |
| 15 | `2602.20723_MAGNET` | 仅 .pdf | P1 |
| 16 | `2603.04320_CAMMSR` | 仅 .pdf | P1 |
| 17 | `2607.26720_CaIRec` | 仅 .pdf | P1 |
| 18 | `AMMRM` | 仅 .pdf，非 arXiv 名称 | P2 |
| 19 | `LightGCN++` | 仅 .pdf，非 arXiv 名称 | P2 |
| 20 | `2507.02626` | 仅 images/（C 类），与 `2507.02626_VRAgent-R1` 重复 | P2 |

### 需补充摘要列表（无摘要或字段完整度 < 60%）

| 类别 | 数量 | 论文 |
|------|------|------|
| 无任何摘要 | 6 | `2506.00107`, `2508.04247`, `2508.08042`, `2601.10944`, `2601.22498`, `2602.00682`, `2602.20723`, `2603.04320`, `2607.26720` 等未解析论文 |
| 仅有 .md 无 .json | 28 | 需补生成 .json 格式 |
| 已有摘要但字段不完整（缺 5 个新维度） | 全部 69 篇 | 需用 11 维度模板重写 |

### 需重命名列表（命名不符合 `{arXiv ID}_{中文标题}` 规范）

| 类别 | 数量 | 处理方式 |
|------|------|---------|
| {arXiv ID} 仅（14 个） | 14 | 补充中文标题 |
| {arXiv ID}\_{英文标题}（29 个） | 29 | 英文标题→中文标题 |
| 非 arXiv 名称（5 个） | 5 | 识别 arXiv ID 后重命名 |
| 全部 75 个 | 75 | Phase 4 分类后追加方向标签 `_[方向A×方向B]` |

### 需分类列表（在 papers.jsonl 中无 research_direction 或无注册记录）

| 类别 | 数量 |
|------|------|
| 无 papers.jsonl 注册记录 | 45 / 75 |
| 有记录但 research_directions 为空 | 8 / 30 |
| 合计需分类 | 53 / 75 |

---

## 四、视觉模型三层介入现状评估

| 层 | 设计目标 | 当前状态 | 差距 |
|----|---------|---------|------|
| L1 解析层 | MinerU vlm 提取全文 + 图片 | ✅ 已实现（`pdf_parser.py` 支持 vlm，48 个文件夹有 images/） | 19 个文件夹未解析（仅 PDF） |
| L2 增强层 | Qwen3.5 视觉模型对架构图/结果表做结构化描述 | ❌ 完全未实现 | 配置已就绪但零代码调用，零 `_figures.json` 输出 |
| L3 校验层 | 摘要与图表描述交叉校验 | ❌ 完全未实现 | 无校验逻辑，无异常记录机制 |

---

## 五、可复用已有资产盘点

| 资产 | 路径 | 可复用性 | 当前引用 |
|------|------|---------|---------|
| 受控词表 | `data/registry/taxonomies.yaml` | ⭐⭐⭐ 核心 | **零引用** |
| 推荐权重 | `config/recommendation_weights.yaml` | ⭐⭐⭐ 核心 | relevance_recommender.py 可能引用 |
| 论文注册表 | `data/registry/papers.jsonl` | ⭐⭐⭐ 核心 | 覆盖率 40%，标签不完整 |
| 数据集注册表 | `data/registry/datasets.yaml` | ⭐⭐ 重要 | **零引用** |
| 研究画像 schema | `data/registry/research_profile_v2.schema.json` | ⭐⭐ 重要 | profile_builder.py 引用 |
| MinerU 解析器 | `skills/pdf_parser.py` | ⭐⭐⭐ 核心 | 正常使用 |
| DeepSeek 摘要器 | `skills/deepseek_summarizer.py` | ⭐⭐ 重要 | 使用旧 8 字段模板 |
| Profile 构建器 | `skills/profile_builder.py` | ⭐⭐ 重要 | 使用 v2 schema |
| 关系推荐器 | `skills/relevance_recommender.py` | ⭐⭐ 重要 | 单推荐器，未拆分多 Agent |
| MixRAGRec 论文 | `data/parsed/2605.28175/` | ⭐⭐ 重要 | 已解析，源码未下载 |
| 质量评分器 | `skills/quality_scorer.py` | ⭐ 可选 | 评估论文质量，非管线门控 |
| Profile 校验器 | `skills/profile_validator.py` | ⭐ 可选 | 事后校验，非管线门控 |

---

## 六、审计结论

### 6 类问题确认状态

| # | 问题 | 确认状态 | 严重度 | 影响范围 |
|---|------|---------|--------|---------|
| 1 | 多任务交织无序 | ✅ 确认 | 🔴 高 | 全管线 |
| 2 | 视觉模型未充分利用 | ✅ 确认 | 🔴 高 | 48 个有图片的文件夹 + 全部摘要 |
| 3 | 质量门缺失 | ✅ 确认 | 🔴 高 | 全管线 |
| 4 | 摘要模板过时 | ✅ 确认 | 🟡 中 | 全部 69 篇摘要 |
| 5 | 已有资产未复用 | ✅ 确认 | 🟡 中 | 分类/注册/推荐全链路 |
| 6 | 文件夹不一致 | ✅ 确认 | 🟡 中 | 75 个文件夹 |

### 优先执行建议

1. **P0 — 立即执行**：Phase 0 Skill 封装 + Phase 1 审计（本报告）+ Phase 2A 解析两篇目标论文
2. **P1 — 紧随执行**：Phase 2B 视觉模型 L2 增强 + Phase 3 摘要重写（11 维度模板）
3. **P2 — 批量处理**：Phase 4 分类整理 + Phase 5 MixRAGRec 源码
4. **P3 — 最后执行**：Phase 6 集成设计

---

*本报告由 WorkBuddy 自动生成，基于 2026-08-04 项目实际文件状态盘点。*
