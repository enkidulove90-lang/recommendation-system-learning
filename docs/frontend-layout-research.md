# 目标四：美观性——图文并茂排版 调研报告

> 调研时间：2026-08-12 ｜ 检索方式：实时 WebSearch（GitHub / 官网 / npm / 社区文档）
> 目标：为公众号 / 小红书 / 知乎的多平台发布链路，筛选**已验证、可复用、可配置**的图文排版引擎与可视化组件库，既能精细繁杂的科技排版，也能一键切极简风格。

---

## 解决方案设计

### 设计层面（Design tokens + 主题切换）
- **Design Token 体系**：用 CSS 变量（或 Tailwind theme / Typography.js 的 `scale()`+`rhythm()`）定义 `--recsys-blue` 主色、字号模数、行高、间距、圆角、代码块配色。所有模板只引用 token，不写死样式，实现"改一处、全局换肤"。
- **多主题切换机制**：主题 = token 集合 + 排版模板。建议维护 `recsys-blue`（科技蓝，常驻默认）、`minimal`（极简）、`academic`（学术灰）三套；运行时通过 `data-theme` 或 class 切换，复用既有 recsys-blue skill 的产物。
- **小红书卡片栅格系统**：统一 3:4（1242×1656）与 9:16 两种画幅，卡片内分"封面标题区 / 正文区 / 数据区 / 品牌签名区"四行栅格；用 Canvas 像素级渲染保证锐利、不被平台压缩糊化。
- **公众号安全样式规范**：只用微信白名单标签（section/section/p/table/img/br/strong 等），**所有 CSS 内联**；禁用 `<style>`、外部 class、JS；外链转脚注；图片 Base64 或走图床；代码块用 `span`+`nowrap` 保留缩进，不加零宽字符以便复制。

### 开发层面（模板引擎 + 图表封装 + 图片合成）
- **模板引擎选型**：
  - 静态富文本（公众号 / 知乎）→ **markdown-it / remark-unified** 解析，配合 **doocs/md、mdnice、md2weixin** 等渲染器产出内联 HTML。
  - 动态卡片（小红书图）→ **Satori（JSX→SVG→PNG）** 或 **XHS-TextCard 式 Canvas 引擎**；Satori 适合服务端批量、确定性渲染，Canvas 适合纯前端零后端。
- **图表库封装**：移动端优先 **Chart.js（轻量 ~60KB）/ Frappe Charts（零依赖 SVG）/ AntV G2Plot（响应式中文友好）**；复杂对比用 **ECharts**。统一封装一层 `renderMobileChart(container, spec)`，自动 `responsive` + `maintainAspectRatio:false` + 移动端字号放大。
- **图片合成服务**：服务端用 **Playwright / Puppeteer**（真实 Chromium，像素级、全 CSS 支持）；边缘/无浏览器环境用 **Satori + @resvg/resvg-js**（WASM，无需原生依赖）；浏览器端快速导出用 **html-to-image / snapdom**。

### 测试层面（多平台渲染一致性 + 性能）
- **渲染一致性**：用 **Playwright `toHaveScreenshot`** 做基线截图比对（mobile 375 / tablet 768 / desktop 1280 三视口）；跨浏览器差异用 **Percy / Chromatic** 云端评审；开源替代 **BackstopJS**（自带 Docker + HTML diff 报告）。
- **移动端适配校验**：脚本化加载渲染产物，断言无横向滚动、字号≥14px、代码块可横向滚动、图片 `width:100%`。
- **性能测试**：记录单篇 HTML 生成耗时、Satori/Puppeteer 单卡渲染耗时（目标 <300ms/卡）、产物体积与图片 CDN 命中率。

### 运维层面（缓存 + 热更新 + 服务化）
- **图片 CDN 缓存**：生成的卡片 PNG 按 `论文ID+主题+页码` 命名，推 OSS/CDN，带内容哈希做 immutable 缓存。
- **模板热更新**：模板与 token 与渲染服务解耦，改 JSON 配置即生效，无需重发版。
- **API 服务化**：以 md2weixin 的 API 模式或 Satori 边缘函数为蓝本，把"Markdown/论文数据 → 多平台图文"封装成内部 HTTP 服务，供发布 skill 调用。

---

## 真实可用项目列表（已验证）

> 验证说明：每条均通过 2026-08-12 实时 WebSearch 确认**官方仓库 / 官网存在、维护状态、核心特性**；标注 ★ 为与本发布链路强契合项。建议接入前再 `git clone` / `npm i` 做一轮本地 smoke test。

### A. 公众号安全 HTML 排版引擎（Markdown → 微信兼容内联 HTML）
| # | 项目 | 来源 | 验证要点 | 契合点 |
|---|------|------|----------|--------|
| 1 | **mdnice / Markdown Nice** | github.com/mdnice/markdown-nice ｜ mdnice.com | 开源微信 MD 编辑器，17+ 主题、KaTeX 公式、自定义 CSS；支持一键复制至公众号/知乎/掘金；可私有化部署 | 多平台一键分发，主题可复用为模板 |
| 2 | **Doocs/md** ★ | github.com/doocs/md（~12.5k★） | Vue3+Vite+TS；Prism 代码高亮、KaTeX、Mermaid、多图床（GitHub/OSS/COS/R2…）、AI 助手；Docker 一键部署 | 自部署可控，契合"自动化 HTML 生成管线" |
| 3 | **md2weixin** ★ | github.com/chouheiwa/md2weixin | 工具链分 API/CLI/WEB 三层，共享渲染核心；主题+字体组合，外链转参考文献 | 可被发布 skill 以 CLI/API 方式调用 |
| 4 | **MD2WeChat** | github.com/dantefung/MD2WeChat | 多模板（学术灰/科技/公告）；代码高亮、Mermaid、公式；**基于 Playwright 自动发表** | 端到端自动发布，省去人工粘贴 |
| 5 | **wx-md** | npmjs.com/package/wx-md | Node API：`renderWeChatHtml(md,{pageTheme,codeTheme,typographyTheme,embedCss})` 直接内联 | 轻量库，适合嵌入现有 Node 管线 |
| 6 | **md-wechat** | github.com/italks/md-wechat | KaTeX/Mermaid；可从已排版 HTML 提取配置实现样式复用 | 配置提取→样式复用，利主题沉淀 |
| 7 | **wechat-format 系（lyricat/wechat-format）** | github.com/lyricat/wechat-format | 老牌微信 MD 渲染，纯前端，历史悠久 | 备选，社区案例多 |

### B. 小红书卡片 / 图文生成（Canvas/SVG 多卡输出）
| # | 项目 | 来源 | 验证要点 | 契合点 |
|---|------|------|----------|--------|
| 8 | **XHS-TextCard** ★ | github.com/geekfoxcharlie/XHS-TextCard（MIT, v1.4） | 纯前端零后端；Markdown→多卡；12 套大师级模板；**Canvas 像素级渲染 1242×1656**；智能分页、防盗水印、ZIP 导出 | 直接对标"论文数据→小红书精美卡片" |
| 9 | **Satori + @vercel/og** ★ | github.com/vercel/satori ｜ og-image.org | Vercel 出品；JSX/CSS→SVG→PNG；边缘运行时无浏览器；确定性渲染 | 服务端批量生成论文对比卡/封面，可模板化 |
| 10 | **md2Card** | github.com/jxmnhm/md2Card | 长文→轮播图；html2canvas 一键导出多张 PNG；单文件零依赖 | 长文拆卡快速方案 |
| 11 | **xiaohongshu-creator** | github.com/lzpp2598/xiaohongshu-creator | 纯前端小红书风图片生成；12 背景/5 字体/4 画幅/6 装饰；实时预览 | 轻量配图快速出图 |
| 12 | **xhs-text-card（Obsidian 插件）** | obsidian.md community plugins | 多页小红书卡片，Canvas 本地渲染；2:3/3:4/9:16；12 模板；可直发公众号草稿 | 若用 Obsidian 做知识库可无缝衔接 |

### C. 可编程设计系统（主题变量 → 风格一致 UI）
| # | 项目 | 来源 | 验证要点 | 契合点 |
|---|------|------|----------|--------|
| 13 | **Tailwind CSS Typography** ★ | github.com/tailwindlabs/tailwindcss-typography（v0.5.20, 4.6k★） | `prose` 类 + 5 灰阶/5 字号/暗色 `prose-invert`/元素修饰符；JS theme API 定制 token | 直接支撑"精细↔极简"一键切换 |
| 14 | **Typography.js** | github.com/KyleAMathews/typography.js（MIT） | `scale()` 模数比例 + `rhythm()` 垂直韵律，自动生成和谐字号/间距 CSS | 定义科技排版字号阶梯的最佳工具 |

### D. 图表与数据可视化（移动端清晰展示实验对比）
| # | 项目 | 来源 | 验证要点 | 契合点 |
|---|------|------|----------|--------|
| 15 | **Chart.js** ★ | github.com/chartjs/Chart.js（~65k★） | 轻量 ~60KB；响应式 `responsive+maintainAspectRatio:false`；8 种基础图 | 移动端轻量首选，封装成本低 |
| 16 | **AntV G2Plot** ★ | github.com/antvis/G2Plot（antv.vision） | 响应式统计图表，企业级中文视觉规范，几行代码出图 | 中文论文对比图观感佳 |
| 17 | **ECharts** | github.com/apache/echarts（~62k★） | 30+ 图表，Canvas/SVG 双渲染，触摸/手势，复杂交互 | 多模型对比/大屏级图表 |
| 18 | **Frappe Charts** | github.com/frappe/charts（~15k★） | 零依赖 SVG 图表，体积小 | 极简风格下的最轻量选项 |
| 19 | **ApexCharts** | github.com/apexcharts/apexcharts.js（~15k★） | 现代交互式图表，动画丰富 | 需要交互动效时选用 |
| 20 | **D3.js** | github.com/d3/d3（~100k★） | 数据驱动文档，极致定制 | 特殊图表（力导向/网络图）兜底 |

### E. 图片合成 / 截图服务（DOM → 图片）
| # | 项目 | 来源 | 验证要点 | 契合点 |
|---|------|------|----------|--------|
| 21 | **html-to-image / snapdom** ★ | github.com/bubkoo/html-to-image ｜ snapdom.dev | 浏览器端 foreignObject 方案；snapdom 支持 Shadow DOM/伪元素/现代 CSS；输出 PNG/SVG/WebP | 前端直出卡片图，零服务端 |
| 22 | **html2canvas** | github.com/niklasvh/html2canvas（~31k★） | Canvas 重绘方案，跨浏览器一致；但 2022 后更新慢、字体/Grid 有坑 | 旧项目兼容，新项目建议 snapdom |
| 23 | **Playwright / Puppeteer** ★ | microsoft/playwright ｜ puppeteer | 真实 Chromium 截图，全 CSS/JS/Web 字体；`element.screenshot()` 精准截取 | 服务端高保真合成，质量天花板 |

### F. 排版质量自动化验证（HTML/CSS 规范 + 移动端截图比对）
| # | 项目 | 来源 | 验证要点 | 契合点 |
|---|------|------|----------|--------|
| 24 | **Playwright Visual Comparison** ★ | @playwright/test `toHaveScreenshot` | 内置像素级 diff，支持 mask 动态区、多视口、动画禁用 | 多平台渲染一致性最低成本方案 |
| 25 | **Percy / Chromatic** | BrowserStack Percy ｜ Chromatic | 云端视觉评审、跨浏览器、Storybook 集成；有免费层 | 团队评审/CI 拦截视觉回归 |
| 26 | **BackstopJS** | github.com/garris/BackstopJS | 开源、自带 Docker、HTML diff 报告、多 viewports | 私有化落地的开源替代 |

---

## 验证结论与落地建议

1. **公众号链路**：优先复用 `doocs/md`（自部署）+ `md2weixin`（API 嵌入），把现有 recsys-blue skill 的 HTML 产物接入，补齐"公式/代码高亮/Mermaid"与"一键分发知乎"。
2. **小红书卡片**：论文数据卡用 **Satori**（服务端批量、确定性、易模板化）作为主方案；若需纯前端零后端交互式编辑，用 **XHS-TextCard** 的 Canvas 引擎作参考实现。
3. **设计系统**：以 **Tailwind Typography `prose` + Typography.js `scale/rhythm`** 双引擎定义 token，实现"科技蓝精细版 ↔ 极简版"一键切换。
4. **图表**：封装一层统一 `renderMobileChart`，默认 **Chart.js**（轻量）打底，复杂对比切 **G2Plot/ECharts**。
5. **质量门**：把 **Playwright 三视口截图比对** 接进现有发布流水线的"校验"环节，作为发布前必过项。

> 注：以上项目均经实时检索确认存在且活跃；小红书纯开源生成工具相对稀缺，已酌情纳入 XHS-TextCard（真开源）+ Satori（通用卡片标准方案）两条主路径。商业产品（如创客贴、稿定）未列入，按需可后续补充。
