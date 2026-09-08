# html-anything 模板提取结果（供本项目自用）

> 配套 `wechat_pipeline_templates_design.md` 第 6 节。
> 源仓库：`nexu-io/html-anything`（Apache-2.0，安全 P2）。
> 位置：`项目/.audit_htmlanything/`（Next.js 应用，非 skill，仅作参考源）。
> 共 85 个模板目录，本文件只提取对公众号链路有用的部分。

---

## 1. 提取原则

html-anything 的模板是**完整网页**（`<div class>` + 外部字体 + `Chart.js` `<script>`），**不能直接发布到公众号**（平台剥离 div/class/script）。因此只做两类提取：

1. **视觉结构参考** → 映射为 gzh-design 内联组件（见主文档第 3 节）。
2. **技术桥** → `juice` 内联 CSS + `data-eeimg` 公式转图，集成进导出链（填补公式 gap）。

---

## 2. 提取的布局参考（4 个模板）

### 2.1 `article-magazine` → 链路 A 结构
来源：`templates/skills/article-magazine/SKILL.md`
- hero：大标题 + 副标题 + 作者/阅读时间/日期元数据
- 正文单栏（参考宽度 ~700px，公众号用满屏即可）
- H2/H3 用 **serif 字体**与正文制造对比
- 引用块：**左侧粗 accent 色边线 + 斜体**
- 代码块：圆角 + 深色底 + 语言标签
- 列表：自定义 bullet（小方块 / accent 圆点）
- 章节分隔：`<hr>` 做成**中央居中小 ornament**
- 文末：**"如果觉得有用，欢迎转发"行动卡片**

→ 直接对应 gzh-design 的 `section-header` / `body-para` / `figure` / `cta` + xiaowan 引用块规范。

### 2.2 `data-report` → 链路 B 结构
来源：`templates/skills/data-report/SKILL.md`
- 头部：报告标题 + 时间区间 + 数据来源说明
- **KPI 卡片网格**：3–5 个，数值 + 同比变化 + 微型趋势线
- 主图表区：≥2 图（柱状/折线/饼/散点），用 Chart.js/ECharts（**公众号禁 script → 须预渲染为 PNG**）
- 数据表：`<table>` + zebra + hover + sticky header
- **洞察块**：3–5 条，emoji 开头，产品周报风格
- 底部方法论折叠区（公众号无 `<details>` → 降级为 `references` 块）

→ KPI 网格 + 表格 + 洞察块直接映射为 gzh-design `kpi-cards` / `rr-table` / `body-para`(emoji 列表)。

### 2.3 `experiment-readout` → 链路 B 的"决策型"变体
来源：`templates/skills/experiment-readout/SKILL.md`
- 9 段强制结构：Header → Hypothesis → Setup → Result snapshot → Metric table → Interpretation → Decision → Follow-up → Instrumentation
- **首屏必须有大号 decision badge + primary metric delta**
- 3 种风格：`product-readout`（默认）/ `lab-notebook`（研究探索）/ `growth-console`（增长实时）
- 真实性：只用用户数据，无显著性用 "directional/inconclusive/needs more data"

→ 适合把论文消融实验写成"上线/停止/继续"决策叙事，比纯数据报告更有观点。

### 2.4 `magazine-poster` → 封面设计语言
来源：`templates/skills/magazine-poster/SKILL.md`
- Dateline 顶栏（publication / date / issue）
- **Oversized serif headline**（含 strike-through + 斜体 accent）
- 双栏 body（公众号用单栏，但可借"编号 section"结构）
- 6 个编号 sections，每节小标题 + 1–2 段 + pull-quote
- 署名 + 小 ornament

→ 借给 guizang 封面"报纸全版"视觉语言（大衬线标题 + 编号 section）。

---

## 3. 技术桥（最高优先级补洞：公式显示）

### 3.1 `juice` 内联 CSS（可选增强，非必须）
来源：`next/src/lib/export/wechat.ts`
```ts
import juice from "juice";
// 收集 <style> → 用 juice.inlineContent(bodyHtml, css, {inlinePseudoElements, preserveImportant})
// 顶层子元素打 data-tool="html-anything" 标记
// 包成 <section data-tool="html-anything">...</section>
```
> 公众号编辑器对带 `data-tool` 标记的内容信任度更高。可作为 gzh-design 导出工具的增强选项（当前 gzh-design 已要求内联 + span-leaf，juice 是另一条可行路径）。

### 3.2 `data-eeimg` 公式 → 图片（**必做**，解决 recsys 论文公式 gap）
来源：`next/src/lib/export/zhihu.ts`
```ts
// 把 <mjx-container> 换成知乎识别的公式图标记：
html.replace(/<mjx-container[^>]*?>([\s\S]*?)<\/mjx-container>/g,
  (_full, inner) => {
    const tex = aria-label 或 <math> 内容;
    const safe = tex.replace(/"/g, "&quot;");
    return `<img class="Formula-image" data-eeimg="true" src="" alt="${safe}">`;
  });
```
> **本项目用法**：论文公式先用 KaTeX/MathJax 渲染出 SVG/PNG，再作为 `<img>` 内联（经图床上传为 `https://`）。gzh-design 当前组件库无公式块，此方案直接补洞。重排 loopsbench 后若遇到含公式的 recsys 论文，启用此路径。

---

## 4. 不提取的内容（违反公众号红线）

- `Chart.js` / `ECharts` 运行时 `<script>` → 公众号剥离，图表须预渲染 PNG
- 外部字体（Google Fonts / woff） → 剥离且拖慢，改用系统字体栈
- `<div class="...">` 富交互 / grid / `@media` → 剥离或失效
- `position:fixed|absolute|sticky` / `float` / CSS 变量 → 红线禁用

---

## 5. 集成建议

| 提取项 | 落在哪层 | 动作 |
|--------|----------|------|
| article-magazine 结构 | gzh-design 组件语义 | 已对齐，无需改 |
| data-report / experiment-readout 结构 | 链路 B/C 模板 | 写成 `wechat_design/examples/` 标准样例 |
| magazine-poster 视觉语言 | guizang 封面 | 提示 guizang 生成时采用报纸全版 |
| juice 内联 | gzh-design 导出工具 | 可选增强 |
| eeimg 公式转图 | gzh-design 公式块 | **新增**，补公式 gap |

---
*生成：审计 `nexu-io/html-anything` 85 模板后提取。*
