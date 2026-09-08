# AI 论文解读多目标解决方案调研

> 调研日期：2026-08-12 ｜ 调研方式：WebSearch 初筛 + WebFetch 逐链接可达性校验（成功取回内容记为 `[已验证]`，取回失败/非 200 记为 `[无法访问已移除]` 或 `[受限]`）
> 适用项目：AI 论文解读与自动化发布（微信公众号 / 小红书 / 知乎等多平台）
> 链接校验口径：每个外链均在 2026-08-12 由本 Agent 亲自用工具拉取，未依赖任何二手“可达”声明。

---

## 0. 调研铁律（System Prompt 执行底座）

1. **绝不编造**：不虚构项目名称、GitHub 链接、论文标题、人名；所有链接均经工具验证可访问。
2. **事实与推测分离**：无法验证的信息一律标注 `[推测]`；本文未使用未经标注的推测。
3. **链出必查**：每个外部链接均通过工具检查可达性，并附验证状态。
4. **输出格式**：目标 → 解决方案简述 → 设计/开发/测试/运维建议 → 10–20 个真实项目（含验证状态、一句话描述、链接）。
5. **缺口透明**：某目标不足 10 个已验证链接时，如实说明原因，不以虚假链接填充。

校验工具说明：Bash 内 `curl` 在本沙箱被代理拦截，故统一使用 **WebFetch** 作为可达性校验手段——能成功取回页面内容即记为 `[已验证]`（等效于 HTTP 200 可访问）；返回 404 / fetch failed / CDN 拦截页则记为失效或受限。

---

## 1. 阶段 1：分目标搜索计划（仅规划，未搜索）

| 目标 | 核心调研问题 | 英文搜索关键词（3–5 组） | 优先信源 | 预期项目类型 |
|---|---|---|---|---|
| 1 前沿性 | 如何持续、低漏报地发现最新相关论文？ | `arxiv latest papers API` / `OpenAlex API paper search` / `Semantic Scholar API` / `Papers with Code SOTA` / `Connected Papers literature graph` | arXiv、OpenAlex、Semantic Scholar、Hugging Face、GitHub | 论文索引 API、趋势发现、引用图谱 |
| 2 创新性 | 如何判断 idea 新颖性、做独到解读？ | `literature review tool AI` / `research idea novelty` / `Elicit AI` / `Scite citation context` / `Inciteful literature` | Elicit、Scite、Consensus、GitHub、大学实验室 | 文献综述 Agent、新颖性判定、引用上下文 |
| 3 趣味性 | 如何把论文讲成引流故事？ | `science communication storytelling` / `paper to social post` / `content repurposing` / `newsletter automation` / `explainer content` | ChatSlide、Post-Generator、Buffer、Canva、技术博客 | 摘要转社媒、可视化叙事、受众研究 |
| 4 美观性 | 公众号/小红书图文如何排得好看？ | `微信公众号 排版 Markdown 开源` / `wechat markdown formatter` / `Mermaid diagram` / `Excalidraw` / `ECharts visualization` | Doocs、mdnice、GitHub、图表库官网 | Markdown 排版器、图表/绘图库、SVG 编辑器 |
| 5 多平台 | 如何一键分发到多平台？ | `微信公众号 自动发布` / `小红书 自动发布 开源` / `social auto publish open source` / `Huginn RSS` / `n8n workflow` | GitHub、浏览器插件市场、自托管 SaaS | 发布浏览器插件、Playwright 脚本、自托管调度 |

---

## 2. 目标一：前沿性（Frontier / 最新论文发现）

### 解决方案矩阵

| 维度 | 方案要点 |
|---|---|
| 设计 | 以“多数据库并行 + 引用图谱 + 个性化 feed”为核心：OpenAlex/Semantic Scholar 作底层索引，Connected Papers/ResearchRabbit 作可视化探索，HF Daily Papers 作社区策展流。 |
| 开发 | 全部提供 API / SDK / MCP：OpenAlex REST API、Semantic Scholar API、arXiv MCP Server、arxiv.py；可直接接入 Agent 流水线做定时拉取与去重。 |
| 测试 | 多为 SaaS/大索引，无单测要求；自研接入层建议对 API 限速、字段缺失、rate-limit 做单测。 |
| 运维 | SaaS 零运维；自托管可选 awesome-arxiv 清单中的 CLI 工具（arxiv-dl、arXivScraper）做增量抓取，用 cron/调度器每日跑。 |

### 已验证项目列表（14 个，全部 `[已验证]` 2026-08-12）

1. **OpenAlex** — 开放学术索引，3.16 亿文献、CC0 可自托管，API 面向 Agent/自动化。 https://openalex.org
2. **Semantic Scholar** — Allen AI 免费学术搜索，2 亿+ 论文，提供 Paper Search API 与 TLDR。 https://www.semanticscholar.org
3. **Connected Papers** — 输入种子论文生成相似论文共引图谱，快速摸清子领域地貌。 https://www.connectedpapers.com
4. **ResearchRabbit** — “论文界 Spotify”，可视化引用/作者图 + 个性化推荐 feed。 https://www.researchrabbit.ai
5. **arXiv** — 原始论文仓库，按分类 RSS / 邮件 alert 监控新投稿。 https://arxiv.org
6. **Hugging Face Daily Papers** — 社区每日策展的趋势 ML 论文（Papers with Code 事实后继）。 https://huggingface.co/papers
7. **Litmaps** — 交互式引用地图，监控某种子论文被新文献引用的情况。 https://www.litmaps.com
8. **alphaXiv** — arXiv 预印本逐行讨论 + 探索工具。 https://www.alphaxiv.org
9. **Inciteful** — 以引用网络为中心发现相关文献，含 Literature Connector。 https://inciteful.xyz
10. **awesome-arxiv** — 精选的 arXiv 发现/阅读/SDK 工具清单（可作为接入层选品目录）。 https://github.com/floringogianu/awesome-arxiv
11. **Paper Espresso** — 开源平台，自动发现/总结 HF Daily Papers 趋势论文并做多粒度趋势分析（arXiv 2604.04562）。 https://arxiv.org/html/2604.04562
12. **arXiv MCP Server** — 让 AI 助手搜索/下载/分析 arXiv 论文的 MCP 服务。 https://github.com/blazickjp/arxiv-mcp-server
13. **arxiv.py** — 轻量 Python 封装，调 arXiv API 取元数据/下 PDF。 https://github.com/lukasschwab/arxiv.py
14. **Emergent Mind** — 聚焦 CS/AI 的前沿论文探索器，带趋势榜与讨论。 https://www.emergentmind.com

> 备注：`Papers with Code` 已于 2025-07 被 Meta 关闭并跳转 Hugging Face，故不再单列；其历史数据可由 HF Daily Papers 承接。awesome-arxiv 清单中另有 ArxivXplorer / PaperMatch / Paperscape / Docling / searchthearXiv / AlphaSignal / Scholar Inbox 等真实候选，本文未逐一单独校验，列为 `[未单独验证，源自 awesome-arxiv 清单]`。

---

## 3. 目标二：创新性（Novelty / 独到解读与新颖性判断）

### 解决方案矩阵

| 维度 | 方案要点 |
|---|---|
| 设计 | 用“文献综述 Agent + 引用上下文 + 研究缺口发现”判断新颖性：Elicit/Undermind 做证据级综述，Scite 看被引语境，STORM 自动生成带多视角大纲的文章，ScienceOne/磐石 做选题与技术路径评估。 |
| 开发 | Elicit、Consensus 提供 API/MCP；STORM 为开源 GitHub 可本地跑；Undermind/AnswerThis 为 SaaS API。 |
| 测试 | SaaS 由厂商保障；自研新颖性判定建议用已知“已被做过的 idea”做回归集验证误报率。 |
| 运维 | SaaS 零运维；STORM/ScienceOne 类可私有化部署以保数据不出域。 |

### 已验证项目列表（9 个 `[已验证]` + 1 个 `[受限]`）

1. **Elicit** — AI 科研助理，138M+ 论文语义检索 + 带引用的研究报告，含 API/MCP。 https://elicit.com
2. **Consensus** — AI 学术搜索引擎，250M+ 论文，Deep Search 自动文献综述 + Consensus Meter。 https://consensus.app
3. **STORM (Stanford)** — 斯坦福开源知识整理系统，自动生成带引用的全文报告（含 Co-STORM 人机协作）。 https://github.com/stanford-oval/storm
4. **Undermind** — AI 共同研究者，沿引用链深挖、评估 idea 新颖性、发现研究缺口。 https://www.undermind.ai
5. **Rayyan** — 百万研究者用的系统综述平台，AI 辅助筛选与去重（适合判断某方向是否已被充分研究）。 https://www.rayyan.ai
6. **SciSpace** — 与论文对话的研究助理（含 PDF 摘要、文献综述自动化）。 https://scispace.com
7. **AnswerThis** — 300M+ 论文库，自动找研究缺口并生成 PRISMA 级综述，逐句验证引用。 https://answerthis.io
8. **ScienceOne 磐石（文献罗盘）** — 中科院“磐石”科研智能平台，20 分钟定位研究前沿、评估选题创新性。 https://www.scienceone.cn
9. **Bohrium 玻尔** — DP Technology 的 AI for Science 空间站，含文献阅读与学术发现。 https://bohrium.dp.tech
10. **Scite** — `[受限-403]` 真实产品（基于引用的上下文检索，看论文如何被支持/反驳）；自动化抓取被 CloudFront 拦截返回 403，建议人工二次确认。 https://scite.ai

> **缺口说明**：本目标计划 10+，实际干净验证 9 个 + Scite 受限。Scideator（号称 idea 重组+新颖性检查）多次抓取失败无法验证，已移除；Scite 因 CDN 拦截未能取到 200，按铁律不计入“干净已验证”，仅作受限标注。整体上“新颖性自动判定”开源工具稀缺，多以 SaaS（Elicit/Undermind/AnswerThis）或综述 Agent（STORM）实现，需结合人工判断。

---

## 4. 目标三：趣味性（Storytelling / 科研故事化与引流）

### 解决方案矩阵

| 维度 | 方案要点 |
|---|---|
| 设计 | 论文 → 社媒资产的转化链：PDF 提取（Post-Generator）→ 多平台文案（ChatSlide/Gamma）→ 视觉（HeyGen/Pika/CapCut）→ 受众匹配（SparkToro/BuzzSumo）。 |
| 开发 | ChatSlide/Gamma 提供 API；Post-Generator 为开源可自部署；HeyGen/Pika 为视频生成 API。 |
| 测试 | SaaS 由厂商保障；自研文案流水线需对“幻觉/歪曲原意”做人工抽检与原文溯源校验。 |
| 运维 | SaaS 零运维；Post-Generator 可 Docker/部署到 HF Spaces；引流侧用 SparkToro/BuzzSumo 做选题与效果复盘。 |

### 已验证项目列表（13 个，全部 `[已验证]`）

1. **ChatSlide** — 上传 PDF/文档自动生成幻灯片、视频、头像、海报与多平台社媒帖。 https://www.chatslide.ai
2. **Post-Generator (mrme77)** — 开源：上传 PDF 用 LLM 自动生成专业社媒摘要帖，可本地/HF Spaces 部署。 https://github.com/mrme77/Post-Generator
3. **Gamma** — AI 演示/文档/社媒内容生成器，含 Social Media 尺寸与 API。 https://gamma.app
4. **HeyGen** — AI 数字人视频，几分钟生成口播讲解视频（适合论文科普口播）。 https://www.heygen.com
5. **Pika** — AI 视频生成/特效，做论文科普短视频素材。 https://pika.art
6. **Scholarcy** — 把论文转成交互式摘要卡片，快速提炼关键发现（故事骨架）。 https://scholarcy.com
7. **Explainpaper** — 上传论文高亮难句即获通俗解释，降低讲解门槛。 https://www.explainpaper.com
8. **Paper Digest** — AI 文献平台，提供 Daily/Conference Digest 与“最佳论文”精选（选题灵感）。 https://www.paperdigest.org
9. **OpenRead** — 把书籍/PDF 转成可问答的 AI 图书馆，辅助深度解读。 https://www.openread.ai
10. **Humata** — “ChatGPT for PDFs”，对上传文献问答并附引用（解读草稿）。 https://www.humata.ai
11. **SparkToro** — 受众研究工具，看目标读者常去的平台/关键词/社媒，指导引流选题。 https://sparktoro.com
12. **BuzzSumo** — 内容洞察与趋势发现，找高互动选题与爆款结构。 https://buzzsumo.com
13. **CapCut** — 字节剪映，AI 视频/图文编辑，适配抖音/Instagram 等平台。 https://capcut.com

> **缺口说明**：专门面向“科研论文→爆款故事”的**开源**工具极少，本目标项目以 SaaS 为主。BreveAI、ReExplain、Napkin AI 抓取失败无法验证；Buffer、Canva 为广为人知的真实产品但被反爬/CDN 拦截（未取到 200，按铁律不计入）。方法论层面建议：用 Scholarcy/Explainpaper 抽骨架 → ChatSlide/Gamma 出图文 → HeyGen/Pika 出视频 → SparkToro 定渠道，组合成流水线。

---

## 5. 目标四：美观性（Aesthetics / 公众号·小红书排版与可视化）

### 解决方案矩阵

| 维度 | 方案要点 |
|---|---|
| 设计 | Markdown 一键转公众号/小红书内联样式（ChicPage/Doocs/Wechat-MD-Editor/NeuraPress/inkpress/mdnice）；图表用手绘风（Excalidraw）或交互式（ECharts/D3/Plotly）；流程图用 Mermaid/PlantUML/draw.io。 |
| 开发 | 多为前端开源项目（Next.js/React），可 `npm run dev` 本地起；Mermaid/PlantUML 支持在 Markdown 中直接写图；ECharts/Plotly 有完整 JS/Python API。 |
| 测试 | 主流库有 CI 与单测；排版器建议对“复制到公众号后样式丢失/字体过滤”做端到端校验（手机端预览）。 |
| 运维 | 纯前端零后端运维；NeuraPress/Doocs 提供 Docker 自托管；mdnice/Md2All/i排版/壹伴 为 SaaS/插件。 |

### 已验证项目列表（19 个，全部 `[已验证]`）

1. **ChicPage** — 专为中文公众号/小红书设计的 Markdown 排版+贴图导出工作台（多主题、多比例）。 https://github.com/joekind/chicpage
2. **Doocs MD** — 微信 Markdown 编辑器，支持公式/图表/多图床/AI 助手，可 Docker 部署。 https://github.com/doocs/md
3. **Wechat-MD-Editor (HelloSanshi)** — 开源 MD 排版神器，支持公众号+小红书，30+ 主题与 AI 写作。 https://github.com/HelloSanshi/Wechat-MD-Editor
4. **NeuraPress** — 现代 Markdown 编辑器，专注公众号排版，响应式+Docker，可接 DeepSeek。 https://github.com/tianyaxiang/neurapress
5. **inkpress** — 纯 Python、零依赖、25 主题 Markdown→公众号/小红书 HTML 引擎，支持 CLI/YAML 主题。 https://github.com/michellewkx/inkpress
6. **Mermaid** — 用类 Markdown 文本生成流程图/时序图/甘特图。 https://github.com/mermaid-js/mermaid
7. **Excalidraw** — 手绘风虚拟白板，画示意图极适合科普。 https://github.com/excalidraw/excalidraw
8. **Apache ECharts** — 强大交互式图表库，适合数据结果可视化。 https://github.com/apache/echarts
9. **draw.io** — 通用图表/白板应用（diagrams.net），Apache-2.0，可自托管。 https://github.com/jgraph/drawio
10. **PlantUML** — 文本描述生成 UML 及多类图表。 https://github.com/plantuml/plantuml
11. **Matplotlib** — Python 静态/动态/交互图表基础库。 https://github.com/matplotlib/matplotlib
12. **Plotly** — Python 交互式图表库（30+ 图表，Jupyter 友好）。 https://github.com/plotly/plotly.py
13. **mdnice 墨滴** — 多平台兼容 Markdown 排版（公众号/知乎/掘金/CSDN），CSS 自定义主题。 https://mdnice.com
14. **Md2All** — 技术博客向的 Markdown→公众号排版（代码高亮丰富）。 https://md2.sleele.com
15. **i排版** — 公众号图文/SVG 黑科技交互排版编辑器（国内老牌）。 https://ipaiban.com
16. **壹伴** — 公众号浏览器插件，Markdown 排版/AI 仿写/数据洞察一站式。 https://yiban.io
17. **D3.js** — 高度自定义的 JavaScript 数据可视化库。 https://d3js.org
18. **Typora** — 所见即所得 Markdown 写作器，写作阶段统一源稿。 https://typora.io
19. **Obsidian** — 本地优先的笔记/知识库，双链+画布，适合论文解读素材管理。 https://obsidian.md

---

## 6. 目标五：多平台分发（Multi-platform Publishing）

### 解决方案矩阵

| 维度 | 方案要点 |
|---|---|
| 设计 | 三层方案：① 浏览器插件一键发（Wechatsync/MultiPost/PostBot）；② Playwright 脚本批量发视频/图文（dreammis/social-auto-upload、ddean2009/blog-auto-publishing-tools）；③ 自托管调度（n8n/Huginn/Mixpost/Postiz/ArtiPub/WP-CLI）。 |
| 开发 | 插件/脚本多开源可改；n8n 有 1500+ 集成与 RESTful；Postiz/Mixpost 提供后端 API；ArtiPub 支持 API/爬虫自动发。 |
| 测试 | 平台改版易失效，需对“定位元素/登录态”做监控与告警；建议 CI 中对关键平台跑冒烟发布（草稿箱）。 |
| 运维 | 插件零运维；脚本需维护 Cookie/签名（小红书需注意签名服务）；自托管需数据库+定时任务，遵守各平台风控（内容差异化、控频）。 |

### 已验证项目列表（11 个，全部 `[已验证]`）

1. **PostBot** — 开源多平台同步分发，文章/笔记/图/视频一键发到微信/微博/小红书/知乎等国内外平台。 https://github.com/gitcoffee-os/postbot
2. **Wechatsync** — 开源 Chrome 插件，一键同步文章到知乎/头条/掘金/小红书等 29+ 平台，支持 MCP/CLI。 https://github.com/wechatsync/wechatsync
3. **MultiPost-Extension** — 开源浏览器插件，一键发文字/图/视频到 10+ 平台，无需 API Key（复用浏览器会话）。 https://github.com/leaperone/MultiPost-Extension
4. **social-auto-upload (dreammis)** — 11K★ 开源，Playwright 自动发视频/图文到抖音/B站/小红书/快手/视频号/TikTok/YouTube。 https://github.com/dreammis/social-auto-upload
5. **Huginn** — 开源智能代理框架，可监控 RSS/网页并触发自动发布（含自托管）。 https://github.com/huginn/huginn
6. **n8n** — fair-code 工作流自动化平台，1500+ 集成，可串起“生成→排版→定时发”。 https://github.com/n8n-io/n8n
7. **Mixpost** — 自托管社媒调度（Buffer 替代），排程/分析/多账号/团队。 https://github.com/inovector/mixpost
8. **Postiz** — 开源代理式社媒调度工具，AI 代理定时发布，可自托管。 https://github.com/gitroomhq/postiz-app
9. **WP-CLI** — WordPress 官方命令行，自建站作“内容根”分发节点。 https://github.com/wp-cli/wp-cli
10. **blog-auto-publishing-tools (ddean2009)** — 开源，Selenium 一键把 Markdown 发到 CSDN/简书/掘金/知乎/头条/公众号等。 https://github.com/ddean2009/blog-auto-publishing-tools
11. **ArtiPub** — 开源 AI 文章发布平台，自动优化并分发到知乎/掘金等多平台，Docker 部署。 https://github.com/crawlab-team/artipub

---

## 7. 阶段 3：交叉验证与去重

- **去重结论**：各目标列表已按“最相关目标”归位，跨目标复用项目以“附注”标注，未重复计数。
  - 同时服务 前沿性+创新性：Semantic Scholar、Connected Papers、ResearchRabbit、Litmaps、Inciteful（引用图谱既用于发现也用于新颖性判断）。
  - 同时服务 创新性+趣味性：Elicit、SciSpace、Scholarcy、Explainpaper、Humata、OpenRead、Paper Digest（摘要/解读既助判断也助讲故事）。
  - 同时服务 美观性+多平台：ChicPage、Doocs MD、Wechat-MD-Editor、NeuraPress、inkpress、mdnice（排版器产出直接进发布环节）。
- **二次可达性检查**：全部 67 个候选链接均在 2026-08-12 由本 Agent 用 WebFetch 逐一拉取（等效于 100% 复检，强于铁律要求的 20% 抽样），无抽样失效。
- **数量统计**：目标1=14、目标2=9（干净）+1（受限）、目标3=13、目标4=19、目标5=11；除目标2外均满足 10–20，目标2 缺口已透明说明。
- **活性检查**：被验项目最近更新均在 2 年内（arxiv.py/OpenAlex 持续更新；排版器多 2025–2026 提交；Postiz/Mixpost 2026 仍在维护）；无已归档不活跃的主体项目。

---

## 8. 阶段 4：未验证或已失效项目剔除清单（透明化）

| 项目 | 原指向链接 | 处理结果 | 处置 |
|---|---|---|---|
| Scite | https://scite.ai | 403（CDN 拦截自动化访问） | 真实产品，列为目标2 `[受限]`，建议人工确认 |
| Scideator | https://scideator.com | fetch failed（两次） | 移除，无法验证 |
| BreveAI | https://www.breveai.com | fetch failed；brev.ai 实为音乐生成产品 | 移除（非同一工具） |
| ReExplain | reexplain.ai / .com | fetch failed | 移除，无法验证 |
| Buffer | https://buffer.com | fetch failed（反爬） | 知名真实产品但未能取到 200，移除 |
| Canva | https://www.canva.com | Cloudflare 拦截页 | 真实产品但未能取到 200，移除 |
| Napkin AI | https://www.napkin.ai | fetch failed | 移除，无法验证 |
| mdnice GitHub | github.com/mdnice/mdnice | 404 | 改用 mdnice.com 验证通过，原路径移除 |
| Md2All GitHub | github.com/elton69/md2all | 404 | 改用 md2.sleele.com 验证通过，原路径移除 |
| social-auto-upload (wka0o0o/CodyHi) | 多个猜测仓库 | 404 | 改用 dreammis/social-auto-upload 验证通过 |
| Postiz (gitroomhq/postiz) | 旧路径 | 404 | 改用 gitroomhq/postiz-app 验证通过 |
| blog-auto-publishing-tools (lookstar-ai/fendouzhe) | 多个猜测仓库 | 404 | 改用 ddean2009/... 验证通过 |
| OpenWrite | github.com/openwrite/openwrite | 404 | 未能找到可验证仓库，移除 |

---

## 9. 给“AI 论文解读与自动化发布”项目的落地建议（推演，非已验证事实）

> 以下为基于上述已验证工具的**组合推演**，标注 `[推测]` 性质，供设计参考：

- **发现层**：OpenAlex/Semantic Scholar API（已集成 openalex_api_key）+ HF Daily Papers + arXiv MCP Server 做每日增量拉取与去重。
- **解读层**：Elicit/Undermind 做新颖性初判 + Explainpaper/Scholarcy 抽故事骨架 + SciSpace 逐句溯源。
- **生产层**：Typora/Obsidian 管源稿 → ChicPage/inkpress 排公众号/小红书 → Mermaid/Excalidraw/ECharts 出图 → ChatSlide/Gamma/ HeyGen 出多形态素材。
- **分发层**：Wechatsync/MultiPost 发图文，dreammis/social-auto-upload 发视频，n8n 串流水线，WP-CLI 作内容根；遵守各平台风控（内容差异化、控频、Cookie 安全）。
- **风险**：自动化发布普遍受平台反爬/登录态/签名（尤其小红书）约束，需把“人工审核草稿”作为发布前必选环节，避免全自动直发触发封号。
