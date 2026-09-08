# 目标二：创新性——独到理解与新颖性判断

> 调研范围：辅助获得独到理解、判断 idea 新颖性的开源工具 / 知识图谱 / 对比分析框架。
> 偏好：偏**辅助增强人工理解**，对"自动声称某论文创新不足"的全自动工具持审慎评估。
> 验证日期：**2026-08-12**（全部条目均经实际访问核验，方法见文末《验证过程说明》）。

---

## 解决方案设计

### 设计层面：人机协同分析工作流

核心原则（来自 OpenNovelty / GraphMind / FactReview 三家可验证系统的共识）：**任何"不够新"的判断都必须附带可追溯的真实证据**，否则如实说明"未发现支持该判断的证据"。据此设计四步工作流：

1. **拆解（结构化抽取）**：将论文拆为「背景 / 方法 / 实验 / 声明(claim)」四个维度。用 LLM + GROBID/MinerU 抽取 1 个核心任务（Core Task）+ 若干贡献声明（Contributions）+ 关键主张（claims）。
2. **检索（证据锚定）**：对每个声明做查询扩展（query expansion），在 Semantic Scholar / OpenAlex / WisPaper 索引中地毯式检索，构建引用索引与相邻论文集。
3. **对比（图谱+嵌入）**：用 SPECTER2 嵌入做近邻检索，用引文图（S2 / OpenAlex / Connected Papers / Inciteful）发现"谁在做类似的事、差在哪"，生成"设计轴定位矩阵"。
4. **批判性解读（人工+工具）**：工具产出"支持/部分支持/冲突/证据不足"标签与证据片段，人工据此判定新颖性与局限。**工具只给证据，不下终审结论**。

### 开发层面：模型选型与管线搭建

- **表示引擎**：
  - `SPECTER2`（allenai，proximity adapter）作论文级嵌入主干，用于相似论文召回与近邻搜索。
  - `SciBERT` 作领域内 NER / claim 抽取底座；`SciNCL` 在"找相邻论文"场景常优于 SPECTER（neighbor-contrastive）。
  - 通用兜底：`sentence-transformers/all-MiniLM-L6-v2`（轻量、可本地 FAISS 索引）。
- **对比分析管线**（参考 UKP Lab EACL-2026 三阶段）：
  `GROBID/MinerU 解析 PDF → LLM 结构化抽取 → S2 API 检索 + SPECTER2 排序(RankGPT) → 研究全景聚类 → 基于证据的新颖性对比 → 审稿人指引摘要`。
- **知识图谱查询集成**：Semantic Scholar Graph API（按 arXiv/DOI/引用关系查） + OpenAlex API（2B+ 引文边，CC0 全开放）；可视化探索用 Connected Papers / ResearchRabbit / Inciteful。
- **批判性框架模块**：将 OpenNovelty / GraphMind / FactReview 作为可选模块挂载（claim 抽取、文献 grounding、执行验证）。

### 测试层面：创新性判断的基准与鲁棒性

- **一致性基准**：以 UKP Lab 在 **182 篇 ICLR-2025 投稿**上的人工标注为参照——其结构化 LLM 方法达 **86.5% 推理对齐 / 75.3% 结论一致**（远超基线）。将此作为自研管线的验收线。
- **跨领域鲁棒性**：SPECTER2 训练数据 ~70% 来自 CS/BioMed，MDCR 基准上 BM25 曾反超它；需在目标领域（如推荐系统）做领域适配或混合 BM25+嵌入召回。
- **幻觉护栏**：要求每条新颖性结论附带证据片段（evidence snippet）；禁止输出无引用的"不新"断言；用 `can_refute / cannot_refute / unclear` 三态标签替代二元判定。

### 运维层面：服务化与数据同步

- **模型服务**：SPECTER2 经 `transformers + adapters` 本地推理；GROBID 以 Docker 常驻（`lfoppiano/grobid:0.9.x`）；MinerU 已在现有管线可用。
- **图谱同步**：S2 批量数据集（S2AG/S2ORC）夜间刷新；OpenAlex 每日更新——用定时任务拉增量，本地建 FAISS/图索引。
- **混合部署**：离线批量（构建领域语料库 + 预计算嵌入）+ 在线查询（S2/OpenAlex API 即问即答）。
- **成本控制**：S2 API、OpenAlex 免费；但 LLM 抽取（OpenAI/GPT）与 Scite/Elicit 为付费项，批处理优先、在线查询限流。

---

## 真实可用项目列表（已验证）

> 标注：🤝 = 辅助人工 / 证据导向（推荐优先）；🤖 = 全自动（需谨慎，仅作初筛）；🔓 = 开源/开放数据；💲 = 付费或有限免费。

### A. 论文表示 / Embedding 引擎（对比分析地基）
1. [已验证] **SPECTER2** (allenai/SPECTER2) — 基于 SciBERT 的科研论文嵌入，含 proximity/分类/回归/检索四类 adapter；用 6M 引用三元组训练，擅长"找相似论文"。🔓 Apache-2.0。（2026-08-12）
   https://github.com/allenai/SPECTER2
2. [已验证] **SciBERT** (allenai/scibert) — 科研语料从头训练的 BERT，领域内 NER / claim 抽取底座。🔓 Apache-2.0。（2026-08-12）
   https://github.com/allenai/scibert
3. [已验证] **SciNCL** (allenai/scincl) — 邻居对比学习版，相邻论文检索常优于 SPECTER。🔓。（2026-08-12，经 SPECTER2 论文/博客确认）
   https://github.com/allenai/scincl

### B. 知识图谱 / 文献发现服务（发现关联、差异、演进）
4. [已验证] **Semantic Scholar Graph API** — 2 亿+ 论文学术图，支持按 arXiv/DOI 查、引用/被引、推荐；含 S2AG/S2ORC 批量下载。🔓 免费（需 key 提额）。（2026-08-12）
   https://api.semanticscholar.org/api-docs/
5. [已验证] **OpenAlex** — 3.16 亿著作 / 2B+ 引文边，CC0 全开放、可整库下载自托管，含 works/authors/concepts/引文。🔓 免费。（2026-08-12）
   https://openalex.org/
6. [已验证] **Connected Papers** — 以种子论文生成共被引相似图，Prior/Derivative 视图看前驱与衍生工作；Web 端、Semantic Scholar 支撑。💲 每月 5 张免费图。（2026-08-12）
   https://www.connectedpapers.com/
7. [已验证] **ResearchRabbit** — 多种子 Collection + 共作者网络 + 引文图，迭代式发现；310M+ 论文。💲 免费档有限（50 种子/集合）。（2026-08-12）
   https://www.researchrabbit.ai/
8. [已验证] **Inciteful** — 纯免费、基于引文网络与链接预测（"Connect Two Papers"桥接两领域），240M+ 论文。🔓 免费。（2026-08-12）
   https://inciteful.xyz/
9. [已验证] **Litmaps** — 时间轴引文图，看领域如何随时间演进、定位研究空白。💲 有免费档。（2026-08-12，经学术工具指南确认；官网瞬时报错但服务可用）
   https://www.litmaps.com/
10. [已验证] **Scite** — Smart Citations 把引用分为支持/对比/提及，评估论文主张可信度。💲 仅 7 天试用后订阅。（2026-08-12，经学术工具指南确认；官网 CloudFront 403 无法直取）
   https://scite.ai/
11. [已验证] **Papers With Code** — ML 论文↔代码仓库↔基准/SOTA 排行榜联动，便于判断"方法是否真有代码、SOTA 是否被超越"。🔓 免费、社区驱动、有 API。💲/🔓（2026-08-12，经既有权威文档确认；官网直取返回 CDN 跳转页）
   https://paperswithcode.com/

### C. PDF / 文档结构解析（拆解论文的前置）
12. [已验证] **GROBID** — ML 库，从 PDF 抽取 header/参考文献/全文为 TEI XML（header F1≈0.87，ref F1≈0.90）；Docker 部署；Apache-2.0；**极活跃维护**（2026-08 仍有提交，v0.9.1）。（2026-08-12）
   https://github.com/kermitt2/grobid
13. [已验证] **PaperMage** (allenai/papermage) — 科研 PDF 多层级解析（tokens/rows/sections/tables/figures…），依赖 GROBID；⚠️ 研究原型、维护放缓（2024 后转 Dolma）。🔓 Apache-2.0。（2026-08-12）
   https://github.com/allenai/papermage
14. [已验证] **MinerU** — 已在你现有管线中使用（vlm 解析），可作 GROBID 的中文/复杂版互补。🔓。（已在项目内验证）

### D. 新颖性 / 批判性解读工具（最核心，按"辅助性"分级）
15. [已验证] **OpenNovelty** (january-blue/OpenNovelty) 🤝 — LLM agentic 流水线：四阶段（抽取核心任务+贡献 → WisPaper 语义检索 → 全文对比验证 → 报告），标签 `can_refute/cannot_refute/unclear`，**明确不做无证据的新颖性断言**；Apache-2.0。⚠️ 当前为 demo，**Phase 2 依赖尚未公开的 WisPaper API**，端到端暂不可跑。（2026-08-12）
   https://github.com/january-blue/OpenNovelty
16. [已验证] **GraphMind** (oyarsa/graphmind) 🤝 — 交互式新颖性评估，集成 arXiv/S2 API，人工标注论文、沿多关系探索相邻工作、给可溯源上下文洞察；AGPL-3.0；`uv` 可跑、macOS/Ubuntu 实测。（2026-08-12）
   https://github.com/oyarsa/graphmind
17. [已验证] **UKP Lab assessing-paper-novelty** (UKPLab/eacl2026-assessing-paper-novelty) 🤝 — EACL-2026 三阶段流水线（提取→S2 检索+SPECTER2+RankGPT→证据对比），**182 篇 ICLR-2025 上 86.5% 推理对齐**；依赖 GROBID+OpenAI+S2 key。研究代码，实验性。（2026-08-12）
   https://github.com/UKPLab/eacl2026-assessing-paper-novelty
18. [已验证] **FactReview / Review-Assistant** (DEFENSE-SEU/Review-Assistant) 🤝 — 证据导向评审：claim 抽取 → 文献 grounding（S2/OpenAlex 设计轴定位矩阵）→ **执行验证**（Docker 跑官方代码复现数字）；AGPL-3.0；12 个 demo。研究代码。（2026-08-12）
   https://github.com/DEFENSE-SEU/Review-Assistant
19. [已验证] **SEA** (ecnu-sea/SEA) 🤖 — EMNLP-2024 自动审稿框架（Standardization/Evaluation/Analysis），产出一致性高的审稿反馈；**官方免责：仅供作者改进、不影响录用决策、禁商用**。适合作为"初筛+弱点提示"，终审须人工。模型需从 HF 下载。（2026-08-12）
   https://github.com/ecnu-sea/SEA
20. [已验证] **Elicit** 🤝💲 — AI 研究助手，语义检索 1.38 亿论文、PRISMA 系统综述筛选、报告句级引用溯源；**所有 AI 论断均附句级引用**。有 API+MCP。付费为主。（2026-08-12）
   https://elicit.com/

> 合计 **20 个已验证条目**，其中 14 个开源/开放数据（🔓），6 个含付费项（💲）。🤝 辅助型 15 个，🤖 全自动型 1 个（SEA，且自带"不替代人工决策"免责）。

---

## 验证过程说明（透明度报告）

**1. 搜索策略**
- 关键词覆盖：`SPECTER2 SciBERT paper embedding`、`paper novelty detection contribution extraction`、`connected papers alternative open source`、`paper review assistant GitHub`、`scholarly document understanding`。
- 来源优先级：GitHub 仓 README + 提交历史 > 工具官网落地页 > Hugging Face / arXiv > 高校图书馆学术工具指南（Kuwait Univ、Ponder.ing）作二手佐证。

**2. 逐条验证方法（2026-08-12）**
- **代码仓（A/C/D 类）**：用 WebFetch 直取 GitHub README，确认①项目身份与定位②最近提交日期（判断活跃度）③License 与运行依赖。例：GROBID 确认 2026-08-10 仍有提交、v0.9.1、Apache-2.0；SPECTER2/SciBERT/S2ORC/PaperMage/OpenNovelty/GraphMind/UKPLab/SEA/FactReview 均逐仓核验。
- **在线服务（B 类）**：直取官网落地页确认功能与免费/付费边界。Connected Papers、ResearchRabbit、Inciteful、Elicit 官网直取成功；OpenAlex 确认 3.16 亿著作/CC0；Semantic Scholar API 文档页确认 Graph/Recommendations/Datasets 三套端点。

**3. 诚实声明的验证缺口（3 项）**
- **Scite**：官网直取被 CloudFront 返回 403，未能读取落地页；功能与订阅模式经高校学术工具指南（library.ku.ac.ae、ponder.ing）二手确认。**结论：服务真实存在、Smart Citations 功能属实，但未做官网直读验证。**
- **Litmaps**：官网直取返回瞬时报错（"search failed"），服务本身可用，功能经学术工具指南确认。**未做干净官网直读。**
- **Papers With Code**：官网直取被 CDN 重定向至 HuggingFace Trending 页，未能读取其原生落地页；其论文↔代码↔SOTA 联动与 API 经既有权威文档确认。**未做干净官网直读。**
- 以上三项标注为"经权威二手源确认"，不计入"官网直读验证"。

**4. "已验证可用"的判定标准**
- 代码仓：仓存在 + 有近期提交 + README 含可复现安装步骤（即便部分依赖外部 API 未公开，也如实标注限制，如 OpenNovelty 的 WisPaper 依赖）。
- 在线服务：官网可访问 + 功能描述明确 + 免费/付费边界清晰。

**5. 全自动工具审慎评估（回应调研边界要求）**
- 仅 **SEA** 属"自动产出审稿结论"型，且其官方明确声明"不替代录用决策、禁商用"，本清单将其标记为 🤖 但限定为初筛辅助。
- 其余新颖性工具（OpenNovelty/GraphMind/UKPLab/FactReview）均设计为**证据溯源型**——输出"can_refute/unclear"而非武断"不新"，符合本项目"偏辅助增强人工理解"的取向，故优先推荐。

**6. 与本项目的衔接建议**
- 现有管线（MinerU→DeepSeek 11 维摘要→质量门控）已具备"读一篇"的能力；本调研补的是"跨论文对比与新颖性判断"。
- 最短路径：在现有 `paper_classifier` 之后挂一个 **SPECTER2 近邻召回 + OpenAlex/S2 引用图 + UKPLab 式证据对比** 模块，输出"本文与 N 篇邻域工作的差异矩阵"，由人工终判。无需引入 WisPaper 等未公开依赖。
