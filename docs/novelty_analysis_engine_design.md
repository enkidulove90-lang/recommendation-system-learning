# 论文创新性分析引擎 · 工程方案

> 设计目标：增强人工对论文的深度理解（提取贡献点、与文献图谱对比、生成差异分析），**非全自动评判**。所有技术决策引用《创新性调研报告》项目索引（见文末清单）。

## 1. 系统架构

数据流：**PDF → 解析模块 → 抽取模块 → 图谱查询模块 → 对比模块 → 报告生成模块 → 辅助分析报告**。

- **解析模块**：PDF 经 GROBID（报告项目12）或 MinerU（项目14）转为 TEI XML / Markdown 结构化文本。
- **抽取模块**：SciBERT（项目2）微调识别贡献句（contribution sentences）；SPECTER2（项目1）proximity adapter 生成论文级嵌入。
- **图谱查询模块**：以论文 ID 调 Semantic Scholar Graph API（项目4）与 OpenAlex（项目5）获取引用/被引邻域及作者/概念标签。
- **对比模块**：SPECTER2（项目1）+ SciNCL（项目3）近邻检索，复用 UKP Lab（项目17）三阶段证据对比。
- **报告生成**：借鉴 OpenNovelty（项目15）的 `can_refute / cannot_refute / unclear` 三态标签，输出"差异点"而非终审结论。

## 2. 技术选型与报告引用

| 模块 | 选型 | 报告索引 |
|---|---|---|
| 解析 | GROBID / MinerU | 12 / 14 |
| 贡献句抽取 | SciBERT 微调 | 2 |
| 论文嵌入 | SPECTER2（proximity adapter） | 1 |
| 近邻检索 | SciNCL | 3 |
| 图谱查询 | Semantic Scholar API + OpenAlex | 4 / 5 |
| 证据对比 | UKP Lab 三阶段管线 | 17 |
| 差异标签 | OpenNovelty 三态标注 | 15 |
| 设计轴定位 | FactReview 设计轴矩阵 | 18 |
| 可视化锚定 | Connected Papers / Inciteful | 6 / 8 |

## 3. 知识图谱集成方案

**本地快照**：以目标论文为 seed，用 Semantic Scholar Graph API（项目4）拉取引用/被引邻域（含 abstracts、paper IDs），OpenAlex（项目5）补全作者与概念标签；用 Connected Papers（项目6）共被引图、Inciteful（项目8）链接预测图作可视化锚定。嵌入经 SPECTER2（项目1）计算后存入本地 FAISS 索引（报告运维层面提及的通用技术）。

**增量更新**：OpenAlex 每日更新、S2 批量数据集夜间刷新（报告运维层面）。用定时任务（通用技术）拉取增量，重算受影响子图嵌入并重建 FAISS 索引；图谱按日期快照版本化，支持回滚。

## 4. 人机协同设计

系统**不输出"新颖/不新颖"终审**，只呈现"建议审视的差异点"。

- **差异矩阵**：复用 FactReview（项目18）"设计轴定位矩阵"——把目标论文与邻域工作放在同一组设计维度（如对齐方式、损失项、评估协议）上，标出各维度差异点。
- **三态标签**：每个差异点附 OpenNovelty（项目15）式 `can_refute / cannot_refute / unclear` 标签与证据片段（Scite（项目10）smart citations 或 S2 摘要）。
- **界面抽象（三栏）**：左栏=论文四维度剖面料（背景/方法/实验/声明）；中栏=差异矩阵（可点击，不显示"不新"判定）；右栏=邻域论文卡片 + Connected Papers 缩略图。点击差异点展开证据面板（参考 Elicit（项目20）句级引用溯源）。用户据证据自行判断。

## 5. 开发路线

- **阶段1 模型微调**：用领域论文（如推荐系统）微调 SciBERT（项目2）抽贡献句；部署 SPECTER2（项目1）嵌入服务。
- **阶段2 图谱构建**：封装 Semantic Scholar API（项目4）+ OpenAlex（项目5）拉取器，建本地图 + FAISS 索引；接入 Connected Papers（项目6）/Inciteful（项目8）可视化。
- **阶段3 API 封装**：复用 UKP Lab（项目17）三阶段管线（提取→检索 + SPECTER2 排序（RankGPT，报告开发层面提及）→对比），参考 GraphMind（项目16）REST API 模式暴露服务。
- **阶段4 前端原型**：差异矩阵 + 证据面板（参考 Elicit（项目20）），先出只读原型，再迭代标注闭环。

## 6. 测试与验证

- **贡献抽取基准**：人工标注 100 篇领域论文的贡献句集合，以 F1 评测 SciBERT（项目2）抽取；以 UKP Lab（项目17）在 182 篇 ICLR-2025 上 86.5% 推理对齐为参照验收线。
- **图谱查询相关性**：人工判定 top-K 邻域论文相关性，对比 SPECTER2（项目1）vs SciNCL（项目3）vs BM25 混合召回（通用技术）的 nDCG@10。
- **鲁棒性**：跨领域测试——SPECTER2 训练偏 CS/BioMed（MDCR 基准 BM25 反超），故采用"嵌入 + BM25 混合召回"以保覆盖。

## 7. 运维考虑

- **模型服务化**：SPECTER2（项目1）经 transformers+adapters 本地推理；GROBID（项目12）以 Docker 常驻（报告验证）；MinerU（项目14）已在现有管线。LLM 抽取后端用报告中 UKP Lab 管线所用的 OpenAI/GPT（报告运维层面提及）。
- **图谱同步**：OpenAlex（项目5）每日、S2 批量夜间刷新（报告运维层面）；定时增量同步 + 本地 FAISS 重建；快照版本化。
- **成本**：S2/OpenAlex 免费；OpenAI/GPT 与 Scite（项目10）/Elicit（项目20）为付费项，批处理优先、在线查询限流。

## 引用项目清单（接受校验）

- **直接调用**：1 SPECTER2 · 2 SciBERT · 3 SciNCL · 4 Semantic Scholar Graph API · 5 OpenAlex · 6 Connected Papers · 8 Inciteful · 10 Scite · 12 GROBID · 14 MinerU · 15 OpenNovelty · 16 GraphMind · 17 UKP Lab assessing-paper-novelty · 18 FactReview/Review-Assistant · 20 Elicit
- **报告中提及的通用/具体技术**：FAISS、RankGPT、Docker、OpenAI/GPT（均见报告正文）；BM25 混合召回、定时任务、Web 前端框架（通用技术）。
- **报告内但未直接调用（扩展预留）**：7 ResearchRabbit · 9 Litmaps · 11 Papers With Code · 13 PaperMage · 19 SEA
