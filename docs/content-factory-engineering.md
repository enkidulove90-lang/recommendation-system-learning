# 科研故事化内容工厂 — 系统工程方案

> 输入：调研报告 `docs/content-strategy-research.md`（27 个已验证项目，A–E 五类）
> 设计目标：把「论文 → 故事化草稿 → 标题变体 → 可视化叙事 → 交互嵌入 → 多平台发布 → A/B 优化」做成端到端可工程化流水线
> 防幻觉规则：每个选型标注「报告第 X 项」，无对应工具者标【通用设计】

---

## 1. 内容生产线架构（端到端流水线）

```
[Stage 0] 输入
   论文 PDF / arXiv ID / 11维摘要(paper-summary-log skill 产出)
        │
        ▼
[Stage 1] 叙事引擎 ──── 四段式(问题/方法/实验/结论) → 故事模板
   规则骨架(ABT+Freytag+Six Steps, 报告 1/2/3) + LLM 润色【通用设计】
        │
        ▼
[Stage 2] 草稿生成
   长文模板(公众号) / 卡片模板(小红书) 两套
        │
        ▼
[Stage 3] 标题工厂
   生成 3–5 变体【通用设计】→ 评分门禁(Sharethrough 14 + CoSchedule 13 + 免费评分器 17) → <70 触发重写
        │
        ▼
[Stage 4] 可视化叙事
   交互图(Idyll 6 / Observable 10 / Vizzu 7) + 自动信息图(AntV 9 / 纳图 8) + 滚动叙事(NarroViz 12 / litvis 11)
        │
        ▼
[Stage 5] 交互组件注入
   代码 playground(Replit/Trinket/CodePen 18) + 测验/投票(Apester 19 / CoRise 20) + 参数滑块(Idyll 6 / Observable 10)
        │
        ▼
[Stage 6] 多平台适配
   标题/导语按平台规则 YAML 改写【通用设计】+ 平台剧本(25)；canonical 同步(Dev.to/Hashnode 24)
        │
        ▼
[Stage 7] 发布 + 线上 A/B
   Buffer/CoSchedule/Later API 定时(23) + Headline Goat(15)/Bandito(16)/@appnest-ab-test(27) 分流
        │
        ▼
[Stage 8] 数据回收 → 看板【通用设计: GA4 + Metabase】
   点击/停留/完读/转发/测验作答 → 回流 Stage 1 调参(叙事模板效果回归)
```

---

## 2. 模块设计与选型（逐项匹配报告）

| # | 功能模块 | 选型 | 报告项 | 类型 |
|---|---------|------|-------|------|
| M1 | 叙事结构骨架 | ABT + Freytag×IMRAD + Six Steps | 1 / 2 / 3 | 方法论 |
| M2 | 故事语言润色 | LLM 提示链（基于 11 维摘要） | — | 【通用设计】 |
| M3 | 交互可视化图 | Idyll / Observable / Vizzu(ipyvizzu) | 6 / 10 / 7 | 代码/API |
| M4 | 自动信息图 | AntV Infographic / Narrative Chart(纳图) | 9 / 8 | 代码/API |
| M5 | 滚动叙事线 | NarroViz / litvis | 12 / 11 | 代码/API |
| M6 | 标题变体生成 | LLM 多候选（配方：数字+power word+缺口+<60字符） | — | 【通用设计】 |
| M7 | 标题评分门禁 | Sharethrough(6维免费) + CoSchedule(0–100) + 免费评分器 | 14 / 13 / 17 | 代码/API |
| M8 | 标题线上 A/B | Headline Goat(Wilson+z-test) / Bandito(多臂) | 15 / 16 | 代码/API |
| M9 | 代码 Playground | Replit / Trinket / CodePen iframe（h=600） | 18 | 代码/API |
| M10 | 测验 / 投票 | Apester(quiz/poll/story) / CoRise MCQ block | 19 / 20 | 代码/API |
| M11 | 参数滑块探索 | Idyll / Observable Inputs | 6 / 10 | 代码/API |
| M12 | 多平台文案改写 | LLM + 平台规则 YAML | — + 25 | 【通用设计】+方法论 |
| M13 | 定时发布 | Buffer / CoSchedule / Later / Hootsuite API | 23 | 代码/API |
| M14 | canonical 同步 | Dev.to / Hashnode API（先源站 2–10 天再跨发） | 24 | 代码/API |
| M15 | 私域沉淀 | Beehiiv / Substack Newsletter | 26 | 代码/API |
| M16 | 组件级 A/B | @appnest/ab-test（接 GA4） | 27 | 代码/API |
| M17 | 数据看板 | GA4 事件 + Metabase 看板 | — | 【通用设计】 |
| M18 | 事件埋点 Schema | 曝光/滚动深度/quiz 作答/play 运行/CTA | — | 【通用设计】 |
| M19 | 内容日历调度 | CoSchedule 营销日历(23) + GitHub Action 监测 data/parsed/ | 23 + — | 代码/API + 【通用设计】 |

---

## 3. 叙事引擎设计

### 3.1 四段式 → 故事模板映射
| 论文四段式 | 故事角色 | 映射方法（报告项） | 输出节 |
|-----------|---------|------------------|-------|
| 问题 | 钩子/反派 | ABT 的「AND…BUT」(1) + Freytag 冲突(2) + Six Steps「问题=反派」(3) | 「为什么现在重要」 |
| 方法 | 主角入场 | Freytag 上升动作(2) + Six Steps「方法=主角」(3) | 「我们怎么打」 |
| 实验 | 高潮 | Freytag 高潮(2) + 反直觉发现节 | 「最反直觉的 1 个数」 |
| 结论 | 结局+开放问题 | Six Steps 终幕(3) + Distill 可探索性(4) | 「它在哪会失效？」 |

### 3.2 模板引擎实现思路（混合式：规则 + LLM）
- **规则层（保结构 / 防幻觉）**：用 Jinja2/JSON 模板强制四节骨架，每节绑定「必须引用 11 维摘要的字段」（如实验节必须出现 `key_result` 数值，方法节必须出现 `method_name`），缺失即阻断生成。此层确保不漏段、不编造。
- **LLM 层（润色 / 类比）**：在规则层填好事实后，用提示词做语言改写、通俗类比生成（如「相当于 100 人里精准召回 87 个」）。LLM 仅做表达，不引入原文外的数字。
- **双模板**：`long` 模板（公众号，含滚动叙事占位）+ `card` 模板（小红书，结论前置 + 封面文案）。模板 selection 由 frontmatter `platform` 决定。
- **反直觉发现节**为强制节（来自报告设计层结论），是转发率最高段落，引擎在实验节后自动插入。

---

## 4. 读者互动与数据收集

### 4.1 组件技术嵌入方案
- **测验**：Apester(19) 单元以 `<iframe>` 注入 CMS；技术栈自托管场景用 CoRise MCQ block(20)（Markdown+MCQ JSON），自带点击/时长统计。
- **投票**：Apester poll unit(19) 嵌文末，采集读者立场。
- **代码 Playground**：Replit/Trinket/CodePen(18) iframe（h=600），跑论文伪代码；加「打不开看原链接」fallback（报告 18 指南）。
- **参数滑块**：Idyll(6) / Observable Inputs(10) 注入，让读者拖参看结果变化（如调 c_target 看 R@20 曲线）。
- **组件级 A/B**：@appnest/ab-test(27) 包裹标题/CTA 变体，选择事件写入 GA4。

### 4.2 数据采集（事件 Schema，【通用设计】）
```
impression   : 文章/组件曝光
scroll_depth : 25/50/75/100% 完成
quiz_answer  : {block_id, correct: bool}
play_run     : {editor, ran: bool}
cta_click    : {platform, variant}
ab_assign    : {experiment, variant}
```
回收到 GA4 → Metabase(17【通用设计】) 看板，按「ABT 钩子 vs 无」「有交互 vs 无」打标做回归（对应报告测试层）。

---

## 5. 开发与测试

### 5.1 前端交互组件测试策略
- **单元**：playground iframe 沙箱隔离、quiz 状态机、滑块联动——Vitest + Testing Library。
- **可视化回归**：各图在桌面/移动断点截图比对（工具【通用设计】：Playwright screenshot diff / Chromatic）。
- **E2E**：Playwright 跑通「读 → 答 quiz → 提交 → 看正确率反馈」主路径。
- **埋点校验**：单元测试断言每个交互触发对应事件（防漏采）。

### 5.2 A/B 测试框架集成
- 站点端标题 A/B：Headline Goat(15)（Wilson 区间 + z-test，95% 置信才宣布胜者）。
- 多标题实时择优：Bandito(16)（多臂，单文至多 8 标题）。
- 组件/CTA 变体：@appnest/ab-test(27) 接 GA4。
- 统计纪律：未达 95% 不切换胜者，防假阳性（继承报告 C 类验证结论）。

### 5.3 内容版本管理
- Git 管理 Markdown 源，每篇论文一个 folder；frontmatter 记录 `title_variants / experiment_id / platforms / status`。
- 状态机：`draft → title_ab → scheduled → published → archived`。
- Conventional commits（`feat(wechat): ...` / `test(title): ...`）；标题变体独立 commit 便于回滚与 A/B 归因。

---

## 6. 运维

### 6.1 内容日历自动化
- CoSchedule 营销日历(23) / Buffer 队列(23) 编排状态机：论文入库 → 摘要 → 配图 → 标题 A/B → 多平台发布。
- GitHub Action（【通用设计】）监测 `data/parsed/` 新论文自动建卡并触发 Stage 1–6。
- 发布节奏：1 篇深读 → 5–7 资产（X 线程 / 小红书 / 公众号 / Newsletter / HN / playground demo），约「写 4h : 复用 2h」。

### 6.2 多平台标题适配配置管理
- `platforms.yaml` 定义每平台规则：长度上限、语气、emoji 策略、话题标签、是否陈述句。
- LLM(6【通用设计】) 按 YAML 改写；绑定平台剧本(25)：HN 用陈述句、美东 9–11 点提交、首评答疑；Reddit 投细分 sub 先贡献再链接；Dev.to/Hashnode 设 canonical(24)；小红书/公众号错峰（早 8 / 晚 9）。
- 配置即代码，纳入 Git，改平台策略不碰生成逻辑。

---

## 7. 防幻觉合规声明

- 全部【代码/API】与【方法论】选型均能在报告 A–E 类（第 1–27 项）找到对应，链接见原报告。
- 标【通用设计】的仅有：M2 LLM 润色层、M6 标题变体生成、M12 改写规则执行器、M17 数据看板(GA4+Metabase)、M18 事件 Schema、M19 调度 Action、5.1 可视化回归测试工具。这些为工程实现基底，报告中无一一对应开源项目，已显式标注，未冒用任何报告项目。
- 叙事引擎的「四段式映射」「反直觉发现节」均源自报告设计层结论（ABT/Freytag/Six Steps/Distill），非新造概念。
- 所有数值/结论引用仅来自报告与项目既有 `paper-summary-log` 11 维摘要，LLM 层不引入外部数字。
