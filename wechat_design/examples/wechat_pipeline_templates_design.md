# 微信公众号内容链路模板架构设计

> 目标：在重排 `loopsbench_v2_illustrated.html` 之前，先确定公众号"链路模板"的拆分方式、每条链路选用哪些组件、具体排版参数、以及内容生成质量的评估标准。
> 配套文件：`wechat_design/references/htmlanything_patterns.md`（html-anything 模板提取结果）

---

## 0. 当前项目问题复盘（为什么需要这套架构）

`loopsbench_v2_illustrated.html`（当前"成品"草稿）经读者视角审查，存在以下阻断性问题：

| 等级 | 问题 | 根因 |
|------|------|------|
| **P0** | 7 张图片全部本地绝对路径 `C:/Users/.../*.jpg` → 公众号里全裂图 | 未走图床上传（`multi-platform-publishing` 的 `WeChatDraftDelivery` 未用） |
| **P1** | KPI 卡用 `display:flex`；非封面图 `width:100%`；arxiv `<a href>` 外链被吞 | 违反公众号红线（flex 受限、外链被吃） |
| **P2** | 无章节编号/关键词下划线/金句/目录；6 张概念插图无真实论文图；13px `#999` 图注；KPI 蓝 `#3a5fcd` 在 `#f5f8ff` 上对比度低；ZWJ emoji `🧑‍🎓` | 缺乏移动端排版规范 + 主题变量未对齐 |
| **公式** | 本篇无公式；但后续 recsys 论文必有公式 → 当前技能栈无公式渲染方案 | gzh-design 组件库缺公式块 |

**结论**：必须先把"技能栈 → 链路模板 → 组件 → 排版参数 → 质量门"固化成文档，再按全链路重排，否则会重复踩坑。

---

## 1. 已就位的技能栈（5 层）

| 层 | 技能 | 层级 | 角色 | 关键能力 |
|----|------|------|------|----------|
| 引擎 | `gzh-design` | 项目级 | 排版引擎 | 7 主题（默认 `recsys-blue`）、自动章节编号 01/02/03、关键词下划线、12 个内联组件、`validate_gzh_html.py` 红线校验 |
| 移动增强 | `xiaowan-wechat-layout-lite` | 用户级 | 移动端审美 + 反馈学习 | 首屏=完整信息单元、层级代替线条、装饰预算≤5、为手机断行写句子（禁 2–3 字孤行）、7 状态工作流、发布清单 |
| 封面/社交卡 | `guizang-social-card-skill` | 用户级 | 封面与多平台卡片 | 微信 21:9 主图 + 1:1 方图、XHS 3:4、Editorial/Swiss 双体系、`validate-social-deck.mjs` 9 规则校验 |
| 分发 | `multi-platform-publishing` | 用户级 | 发布与图床 | `paper_to_wechat` + `WeChatDraftDelivery`（浏览器桥接，复用登录态上传素材库，把 `src` 改写为 `https://`） |
| 预览/导出 | `html-anything`（nexu-io） | 伴随工具（非 skill） | 模板参考 + 公式转图 | 85 个模板作布局参考；`juice` 内联 CSS + `data-eeimg` 公式→图片，填补公式 gap |

> **重要边界**：html-anything 是 Next.js 网页应用，其模板大量使用 `<div class>` / 外部字体 / `Chart.js` `<script>`，**不能直接 juice 后粘进公众号**（div/class/script 会被平台剥离）。它在本架构里只做两件事：① 提供"视觉结构参考"映射为 gzh-design 组件；② 提供 `juice`+`eeimg` 公式转图逻辑集成进导出链。

---

## 2. 公众号拆分为几条链路模板

按本项目的实际内容产出（推荐系统论文学习），公众号应拆分为 **4 条正文主链路 + 1 条封面/社交卡辅链路**：

```
A 论文精读长文   ── 完整解读单篇论文（最高频，对应 loopsbench 这类）
B 数据/实验复盘  ── benchmark / 消融 / 实验对比
C 方法论/观点短篇 ── 轻量避坑、趋势、观点
D 系列/合集导航   ── 论文关系、知识图谱、合集索引

E 封面 & 社交卡   ── (辅) guizang 生成 21:9+1:1+XHS，分发多平台
```

拆分依据：
- **A 是主营收**，必须最完整、最稳；当前 loopsbench 草稿即 A 类，重排首选它。
- **B 复用 A 的 KPI/表格/图表组件**，但结构更"数据导向"，单独成链路便于固化数据叙事模板。
- **C 是流量/互动型**，短、快、金句驱动，用 xiaowan 装饰预算≤5 约束，避免和 A 同质。
- **D 属于留存/SEO 型**，把碎片化论文串成体系，用卡片网格而非长文。
- **E 不属于正文**，是分发层，单独管理封面与小红书/知乎/Twitter 卡片。

---

## 3. 每条链路的组件选择

### 链路 A — 论文精读长文（Paper Deep-Dive）
**来源**：gzh-design `recsys-blue` 全组件 + xiaowan 移动层覆盖 + 封面用 guizang。

| 段落 | 选用组件（gzh-design） | xiaowan 覆盖规则 |
|------|------------------------|------------------|
| 封面 | guizang 21:9 主图（主题蓝派生成） | 首屏=完整信息单元（标题+一句话结论+封面同框） |
| 一句话高亮 | `one-liner` | 重点覆盖完整语义，不截断 |
| 背景/动机 | `section-header` + `body-para`（关键词下划线 1–3 处） | 层级留白代替线条 |
| 方法/框架 | `figure`（用论文真实架构图，非概念插图）+ `body-para` | 图片必须证明观点；多图预拼拼图 |
| 实验 | `rr-table` + `kpi-cards` + `figure` | KPI 卡对比度按 xiaowan 提亮 |
| 局限/取舍 | `limitation` | 诚实备注块 |
| 实践启发 | `body-para` + 金句（引用块） | 金句独立成行、字号放大 |
| 读者分层/结语 | `cta` + `references` | 互动钩子（提问/投票） |

**公式**：若论文含公式，走 `htmlanything_patterns.md` 的 eeimg 方案（公式→SVG/PNG 内联）。

### 链路 B — 数据/实验复盘（Data & Experiment Readout）
**来源**：html-anything `data-report` / `experiment-readout` 结构 → 映射为 gzh-design 静态组件。

| 段落 | 组件 | 说明 |
|------|------|------|
| 头部 | `section-header`（报告标题+区间+数据源） | data-report 头部规范 |
| KPI 网格 | `kpi-cards`（3–5 个，数值+同比+迷你趋势线**用静态 SVG 替代 Chart.js**） | 公众号禁 script，图表须预渲染为图 |
| 主图区 | `figure`（柱状/折线图先本地渲染成 PNG 再上传） | 不内联 Chart.js |
| 数据表 | `rr-table`（zebra + sticky header） | 原样保留 |
| 洞察块 | `body-para` + emoji 开头列表 | data-report 的"洞察块"模式 |
| 方法论 | 折叠区 → 用 `references` 块代替（公众号无 `<details>`） | 降级处理 |

### 链路 C — 方法论/观点短篇（Methodology & Opinion）
**来源**：article-magazine 简化版 + xiaowan 装饰预算≤5。

| 段落 | 组件 | 约束 |
|------|------|------|
| 封面 | guizang 1:1 方图（轻量） | 装饰锚点≤5 |
| 金句开场 | 引用块（大字号 serif） | 首屏即观点 |
| 论点 | `body-para` + 自定义 bullet（小方块） | 禁 2–3 字孤行 |
| 收尾 | `cta` | 一句话行动 |

### 链路 D — 系列/合集导航（Series Hub）
**来源**：deck 导航风格 → 卡片网格（公众号无 grid，用纵向卡片列表模拟）。

| 段落 | 组件 | 说明 |
|------|------|------|
| 目录 | `section-header` + 编号列表 | 自动 01/02/03 |
| 论文卡 | `figure`（封面缩略）+ `body-para`（一句话定位）纵排 | 每篇一张卡，点击跳转用"阅读原文"或菜单 |
| 关系图 | `figure`（知识图谱 PNG） | 跨论文关系可视化 |

### 辅链路 E — 封面 & 社交卡（Cover & Social Card）
**来源**：guizang 全能力。

- 微信 21:9 主封面 + 1:1 方图（朋友圈/视频号）
- XHS 3:4 卡片（分发小红书）
- 知乎/Twitter 用 html-anything `card-xhs-post` / `social-x-post-card` 思路生成
- 校验：`validate-social-deck.mjs`（9 规则）

---

## 4. 具体排版参数（统一规范）

> 以下参数同时覆盖 gzh-design `recsys-blue` 主题变量 + xiaowan 移动层。所有样式必须内联，`<span leaf="">` 包裹每个中文文本节点。

### 4.1 字体（禁用外部字体，用系统栈）
```
正文/标题： -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif
金句/引用： "Songti SC", "SimSun", serif   （衬线制造对比）
代码：      "SF Mono", "JetBrains Mono", Menlo, monospace
```
> 不引入 Google Fonts / 外部 woff（被剥离且拖慢）。

### 4.2 字号 / 行高 / 字距
| 元素 | 字号 | 行高 | 字距 | 备注 |
|------|------|------|------|------|
| 封面大标题 | 22px | 1.4 | 0 | 不超过 18 字/行 |
| 章节小标题 | 18px | 1.5 | 0.5px | 左色条 `border-left:4px solid #3a5fcd` + 左缩进 12px |
| 正文 | 16px | 1.8 | 0 | 行宽≤手机屏，不强制 max-width |
| 金句/引用 | 18px | 1.7 | 0 | serif + 左粗 accent 边线 |
| 图注 | 13px | 1.6 | 0 | 颜色 `#666`（非 `#999`，提升对比） |
| 表格内容 | 14px | 1.6 | 0 | zebra 行 `#f5f8ff` |

### 4.3 颜色（`recsys-blue` 变量对齐）
```
主色    #3a5fcd  （科技蓝，标题/色条/链接）
背景    #eef3ff  （页面）
卡片底  #f5f8ff  （卡片/表格 zebra）
强调文字 #1a2b6b （深蓝，用于 KPI 数值，解决低对比）
正文    #333333
次要    #666666
分割线  #d9e2f3  （浅蓝灰，替代 xiaowan 的"留白代替线条"时备用）
```
> KPI 数值必须用 `#1a2b6b`（深蓝）而非 `#3a5fcd`，避免在浅底上对比度不足（修复 loopsbench 的 P2）。

### 4.4 间距 / 断行（xiaowan 移动层硬规则）
- 段间距：`margin: 1.2em 0`
- 章节间隔：`padding: 14px 0 0; margin-top: 28px; border-top: 1px solid #d9e2f3`（或纯留白 28px）
- **禁 2–3 字孤行**：写句子时保证换行处不剩 2–3 个汉字；长数字/英文词用 `word-break: keep-all`
- 装饰锚点预算 ≤ 5（色条、分隔 ornament、引用边线、KPI 卡、封面图 = 刚好 5，不超）
- emoji 只用基础单码（禁 ZWJ 组合如 `🧑‍🎓`，用 `👤` 替代）

### 4.5 图片规则
- 所有图先经 `WeChatDraftDelivery` 上传素材库 → `src` 改写为 `https://mmbiz.qpic.cn/...`
- 非封面图宽度：`width: 100%` 仅限全宽封面；正文图用 `width: 92%; margin: 0 auto`（留边）
- 论文真实图优先；概念插图仅在无真实图时补 1 张点睛
- 多图预拼成一张拼图，减少滑动疲劳

---

## 5. 内容生成质量评估标准

分三层门禁，全部通过才允许进入发布流程。

### L0 — 机器红线校验（自动，必须 0 错）
| 工具 | 规则 | 阈值 |
|------|------|------|
| `gzh-design/validate_gzh_html.py` | ERROR + 半角 WARNING | 必须 = 0 |
| `gzh-design/component_lint.py` | 组件命名/span-leaf 包裹 | 必须通过 |
| `guizang/validate-social-deck.mjs` | 封面 9 规则（尺寸/对比/留白） | 必须通过 |
| 外链检查 | `<a href>` 外链 | 必须改写为"阅读原文"或删除（公众号吞外链） |
| 图片检查 | `src` 含 `file://` / `C:/` / 相对路径 | 必须 0 |

### L1 — 内容质量（半自动 / 清单）
- [ ] 基于 11 维摘要，无幻觉、论点有论文依据
- [ ] 以"读者视角"组织（背景→方法→实验→局限→实践启发→参考）
- [ ] 至少 1 句金句、1 个互动钩子
- [ ] 图片均"证明观点"而非装饰（xiaowan 规则）
- [ ] 公式已转图（如适用）
- [ ] 章节编号连续、关键词下划线 1–3 处/段

### L2 — 读者反馈闭环（xiaowan 反馈路由）
收集发布后反馈，按路由表回流：

| 反馈类型 | 示例 | 触发更新 |
|----------|------|----------|
| 排版断裂 | "手机上图裂了/字重叠" | 重跑 L0 + 检查图床 |
| 可读性差 | "太长/看不懂" | 收紧 C 链路或拆 A 为上下篇 |
| 审美投诉 | "太花/太素" | 调整装饰预算或主题变量 |
| 内容错误 | "数据错了" | 回 11 维摘要复核 |

> 每次反馈沉淀为 gzh-design / xiaowan 的规则补丁，进入 `wechat_design/examples/` 迭代记录。

---

## 6. html-anything 模板提取方案

详见 `wechat_design/references/htmlanything_patterns.md`。要点：

1. **提取为布局参考库**（不直接当发布器）：
   - `article-magazine` → A 链路 hero + 引用 + 行动卡结构
   - `data-report` / `experiment-readout` → B 链路 KPI/表格/洞察块
   - `magazine-poster` → 封面 headline + 编号 section 设计语言
   - `deck-guizang-editorial` → 与已装 guizang 对齐验证
2. **提取技术桥**：
   - `juice` 内联 CSS 逻辑 → 集成进 gzh-design 导出（可选增强）
   - `data-eeimg` 公式→图片 → 解决 recsys 论文公式显示 gap（**本架构最高优先级补洞**）
3. **不提取**：Chart.js / 外部字体 / `<div class>` 富交互模板（违反公众号红线）。

---

## 7. 下一步

1. 先按本架构 + `htmlanything_patterns.md` 重排 `loopsbench_v2_illustrated.html`（链路 A）。
2. 重排后跑 L0 门禁，确认 0 错再走 `multi-platform-publishing` 图床上传。
3. 沉淀首版为 A 链路"标准样例"，后续论文直接套用。

---
*文档生成：基于 gzh-design / xiaowan-wechat-layout-lite / guizang-social-card-skill / multi-platform-publishing / html-anything 五层技能栈审计结果。*
