# 双轨排版引擎（DTLE）系统设计

> 基于 `docs/frontend-layout-research.md`《美观性：可繁杂可简洁的图文并茂排版》调研报告（2026-08-12）设计的升级版排版引擎。
> 目标：一套配置，双轨输出 —— **A 轨 微信安全富文本 HTML** + **B 轨 小红书长图卡片**，支持 recsys-blue / minimal / academic 等主题一键切换。
> 防幻觉约束：本文所有工具均来自上述报告，文末附引用清单（报告条目编号）。

---

## 1. 总体架构（分层）

```
┌──────────────────────────────────────────────────────────────┐
│  L0  设计 Token 层 (Design Token Layer)                       │
│      themes/{recsys-blue,minimal,academic}.yaml  → tokens.css │
│      + tokens.json  (Typography.js #14 生成 scale/rhythm)     │
├──────────────────────────────────────────────────────────────┤
│  L1  组件层 (Platform-Agnostic Component Layer)               │
│      ComponentSpec(11 个 recsys-blue 组件抽象)                │
│        ├─ toHTML(props, theme)   → 微信内联片段               │
│        └─ toCard(props, theme)   → SVG/卡片块                │
├──────────────────────────────────────────────────────────────┤
│  L2  渲染层 (Render Layer)                                    │
│   ┌─ A 轨 RichTextRenderer ──► doocs/md(#2)/md2weixin(#3) 内核 │
│   │       + markdown-it/remark 解析                           │
│   └─ B 轨 CardRenderer ──────► Satori(#9)+resvg / XHS(#8) 参考 │
│         + Puppeteer(#23)+Sharp 兜底（复杂 CSS）               │
│   共享 ChartRenderer ────────► ECharts(#17) 移动封装 / Chart.js(#15)│
├──────────────────────────────────────────────────────────────┤
│  L3  校验层 (Validation Layer)                                │
│      WeChatHTMLGate(白名单+内联校验) + Playwright(#24) 三视口 │
│      截图比对 / BackstopJS(#26) / Percy+Chromatic(#25)        │
├──────────────────────────────────────────────────────────────┤
│  L4  服务运维层 (Service/Ops Layer)                           │
│      CDN 缓存 + 模板热更新 + HTTP API 服务化                  │
└──────────────────────────────────────────────────────────────┘
```

**分层职责**
- **L0 Token 层**：唯一事实源。所有颜色/字号阶梯/间距/圆角/代码配色/品牌签名均定义为 token，不写死在模板里。
- **L1 组件层**：组件与平台解耦。同一份 `ComponentSpec` 经两个 adapter 映射到不同目标输出，保证"一处改、双轨一致"。
- **L2 渲染层**：A 轨产内联 HTML（微信可粘贴），B 轨产 PNG 长图（小红书可上传）；图表轨道共享。
- **L3 校验层**：发布前必过两道门 —— 结构安全门（微信白名单/内联）+ 视觉一致性门（截图比对）。
- **L4 运维层**：图片服务化、缓存、热更新。

---

## 2. 技术选型（全部引用调研报告）

### 2.1 设计 Token 管理
- **Typography.js（报告 #14）**：用 `scale(baseFontSize, scaleRatio)` + `rhythm()` 自动生成和谐的字号阶梯与垂直韵律 CSS，杜绝手调字号导致的比例失调。这是 token 体系里"字体比例"的算法来源。
- **Tailwind CSS Typography（报告 #13）**：用 `prose` 类 + 灰阶/字号/暗色 `prose-invert` / 元素修饰符（`prose-headings:`、`prose-a:` 等）把 token 应用到 A 轨富文本；其 JS theme API 可把 recsys-blue 主色注入 `--tw-prose-*` 变量，实现"精细↔极简"切换。
- **单一来源**：`tokens.yaml` 同时驱动两套产物 —— `build-tokens` 脚本产出 `tokens.css`（供 HTML 轨）与 `tokens.json`（供 Satori 卡片轨）。

### 2.2 公众号渲染（A 轨）
- **模板引擎**：`markdown-it` / `remark-unified` 链路解析 Markdown（报告"开发层面"已论证），渲染内核复用 **doocs/md（#2）** 或 **md2weixin（#3）** —— 二者均产出微信兼容内联 HTML、支持主题/代码高亮/公式/Mermaid。优先 `md2weixin`（#3）的 API/CLI 内核做嵌入，doocs/md（#2）做自部署可视化兜底。
- **微信安全校验**：复用项目既有 `validate_gzh_html` 白名单门禁（任务 #61），并接 **Playwright Visual Comparison（#24）** 做自动化安全/一致性校验（断言无 `<style>`、无外部 class、无横向滚动、字号≥14px）。开源替代 **BackstopJS（#26）**，云端评审用 **Percy/Chromatic（#25）**。

### 2.3 小红书卡片生成（B 轨）
- **主方案 Satori（报告 #9）+ @resvg/resvg-js**：JSX/CSS → SVG → PNG，边缘运行时无浏览器、确定性渲染，最适合"论文数据 → 多张对比卡/封面"的服务端批量生成；模板即 JSX 组件，主题切换只是换 props。
- **参考 XHS-TextCard（报告 #8）**：其 Canvas 像素级渲染（1242×1656 / 3:4）、智能分页、12 套模板、防盗水印，作为卡片栅格与模板设计的参考实现（纯前端零后端场景可直接用它）。
- **兜底合成服务 Puppeteer + Sharp（报告 #23）**：当卡片用到 Satori 不支持的 CSS（Grid/伪元素/动画）时，用 Puppeteer 真实 Chromium 截图，Sharp 做 PNG 压缩优化。
- **浏览器端快速出图 html-to-image / snapdom（报告 #21）**：用于编辑器内实时预览与一键导出，零服务端。

### 2.4 图表组件（共享轨道）
- **ECharts（报告 #17）移动优化封装**为主：统一封装 `renderMobileChart(container, spec)`，强制 `responsive:true` + `maintainAspectRatio:false` + 移动端字号放大 + `myChart.resize()` 监听视口；复杂多模型对比/力导向图用 ECharts。
- **轻量替代 Chart.js（#15）/ AntV G2Plot（#16）**：简单柱状/折线/饼图用 Chart.js（~60KB）或 G2Plot（中文视觉规范好）；极简风格下可用 **Frappe Charts（#18）** 零依赖 SVG。
- 图表在 A 轨输出为内联 SVG（微信不支持 JS 图表，须预渲染成图后嵌入）；在 B 轨直接合成进卡片 PNG。

---

## 3. 主题切换机制

**定义**：主题 = `tokens.yaml` 中一组 token + 组件模板绑定。预设三套：
- `recsys-blue`（默认，科技蓝 `#3a5fcd`，精细繁杂）
- `minimal`（极简，大留白、弱装饰）
- `academic`（学术灰，衬线、克制）

**加载与热切换**：
```yaml
# themes/recsys-blue.yaml
name: recsys-blue
colors:
  primary: "#3a5fcd"
  text: "#1f2329"
  bg: "#ffffff"
  code-bg: "#f6f8fa"
type:
  baseFontSize: 16px
  scaleRatio: 1.25      # 由 Typography.js(#14) 生成阶梯
spacing: { base: 8, rhythmUnit: 24 }
radius: 8
brand: { signature: "@RecSysLab", watermark: true }
```

```ts
// theme-loader.ts
export async function loadTheme(name: ThemeName) {
  const t = await yaml.load(`themes/${name}.yaml`);
  // 1) 生成 CSS 变量(A轨)
  const css = typography(t).toString();           // #14 生成 scale/rhythm
  // 2) 生成 JSON(B轨 Satori)
  const json = toSatoriTokens(t);
  return { css, json, meta: t };
}
// 热切换：HTML 轨换 <body data-theme> 或重内联；卡片轨用新 json 重渲，无代码改动
```

**热更新策略**：主题/组件 spec 与代码解耦，改 YAML 即生效（L4 配置驱动 reload），无需重发版。

---

## 4. 组件库设计（平台无关抽象）

将现有 recsys-blue 的 11 个组件抽象为 `ComponentSpec`，每个组件提供 `toHTML` 与 `toCard` 两个 adapter：

```ts
// components/types.ts
interface ComponentSpec {
  name: "section_header" | "one_liner" | "body_para" | "body_li"
      | "body_bul" | "kpi_cards" | "limitation" | "cta"
      | "references" | "cover" | "figure" | "hook_title";
  props: Record<string, any>;
  toHTML(props: any, theme: ThemeTokens): string;   // A轨：内联微信 HTML
  toCard(props: any, theme: CardTokens): SatoriNode;// B轨：SVG/卡片块
}
```

**示例：kpi_cards（论文指标卡）**
```ts
kpi_cards.toHTML = (p, t) => `
  <section style="display:flex;gap:${t.spacing.base}px">
    ${p.items.map(i => `
      <div style="flex:1;background:${t.colors.codeBg};
                  border-radius:${t.radius}px;padding:${t.spacing.base}px">
        <p style="color:${t.colors.primary};font-size:20px;font-weight:700">${i.value}</p>
        <p style="color:${t.colors.text}">${i.label}</p>
      </div>`).join("")}
  </section>`;

kpi_cards.toCard = (p, t) => ({
  type:"div", props:{ style:{ display:"flex", gap:16 },
    children: p.items.map(i => ({
      type:"div", props:{ style:{
        flex:1, background:t.colors.codeBg, borderRadius:t.radius,
        padding:16, alignItems:"center" },
      children:[
        { type:"p", props:{ style:{ fontSize:28, color:t.colors.primary, fontWeight:700 }, children:i.value }},
        { type:"p", props:{ style:{ fontSize:16, color:t.colors.text }, children:i.label }},
      ]})})}});
```
> 两个 adapter 共享同一份 `theme` 与 `props`，保证双轨视觉一致。新增平台（知乎/微博）只需加一个 adapter，不改组件定义。

---

## 5. 开发与测试

**组件开发流程**
1. 在 `components/` 下新增/修改 `ComponentSpec`，同时实现 `toHTML` + `toCard`。
2. 本地预览：`npm run dev` 启动预览页，左编辑 props、右实时渲染 A 轨 HTML 与 B 轨卡片。
3. 提交前跑单元：`render()` 输出必须命中白名单标签（A 轨）与合法 Satori 节点（B 轨）。

**可视化回归测试（截图比对）**
- **A 轨**：用 **Playwright `toHaveScreenshot`（#24）** 在 375/768/1280 三视口截图，与基线 diff；动态区（时间戳/头像）用 `mask` 屏蔽；动画 `disabled`。
- **B 轨**：渲染卡片 PNG 后同样用 Playwright 截图比对；或用 **BackstopJS（#26）** 自带 Docker + HTML diff 报告做开源落地。
- **云端评审**：**Percy / Chromatic（#25）** 做团队 PR 级视觉评审与跨浏览器拦截。
- 断言脚本（示例）：
```ts
test("wechat safety + mobile layout", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/preview?theme=recsys-blue&track=wechat");
  await expect(page).toHaveScreenshot("wechat-recsys-blue-mobile.png", {
    maxDiffPixelRatio: 0.01,
    mask: [page.locator(".timestamp")],
  });
  // 安全断言：无 <style>、无横向滚动
  expect(await page.evaluate(() => document.querySelectorAll("style").length)).toBe(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth))
    .toBeLessThanOrEqual(375);
});
```

---

## 6. 部署运维

**图片生成服务（B 轨）**
- 架构：Node 服务，主用 **Satori(#9)+resvg**（WASM，无原生依赖，边缘可跑）；复杂卡片用 **Puppeteer(#23)+Sharp** 池兜底。
- 性能优化：
  - resvg WASM 模块级只 `initWasm` 一次（单例）。
  - 字体 ArrayBuffer 启动时预载，避免每次渲染 fetch。
  - `Sharp` 做 PNG 压缩（quality 90 / webp 可选），控制单图 <300KB。
  - 批量渲染：同一论文的多页卡片并发生成，限制并发数避免 OOM。
- 缓存：渲染产物按 `hash(paperId+theme+page)` 命名，推 OSS/CDN，immutable 缓存；命中则直接返回，不重复渲染。

**模板更新策略**
- `themes/*.yaml` 与 `components/*.ts` 经配置中心/版本库管理；改 YAML 触发 L0 重建 `tokens.css/json`，服务热加载，**不重启进程**。
- 模板变更走 PR + 视觉回归（§5），合入即生效，历史基线自动更新。

**API 服务化**
- 以 `md2weixin(#3)` API 模式为蓝本，暴露 `POST /render`：`{ source, track, theme } → { html | imageUrls }`，供现有 multi-platform-publishing skill 直接调用。

---

## 7. 防幻觉声明与引用清单

> 本节所列每一项工具均来自 `docs/frontend-layout-research.md`（2026-08-12 实时检索验证）。编号对应报告中的项目序号。

| 本报告用途 | 工具 | 报告条目 |
|-----------|------|----------|
| 字体比例/韵律 token 生成 | Typography.js | #14 |
| 富文本 token 应用 / prose 主题 | Tailwind CSS Typography | #13 |
| 公众号渲染内核（自部署） | Doocs/md | #2 |
| 公众号渲染内核（API/CLI 嵌入） | md2weixin | #3 |
| 微信安全/一致性自动化校验 | Playwright Visual Comparison | #24 |
| 开源视觉回归替代 | BackstopJS | #26 |
| 云端视觉评审 | Percy / Chromatic | #25 |
| 小红书卡片主引擎（JSX→PNG） | Satori + @vercel/og | #9 |
| 小红书卡片参考实现（Canvas） | XHS-TextCard | #8 |
| 服务端截图兜底合成 | Puppeteer / Playwright | #23 |
| 浏览器端快速出图 | html-to-image / snapdom | #21 |
| 图表主封装（移动优化） | ECharts | #17 |
| 图表轻量替代 | Chart.js | #15 |
| 图表中文视觉替代 | AntV G2Plot | #16 |
| 图表极简零依赖替代 | Frappe Charts | #18 |
| 图表动效/特殊替代 | ApexCharts / D3.js | #19 / #20 |

**未被本文采用的报告条目（留作扩展）**：#1 mdnice、#4 MD2WeChat（自动发表）、#5 wx-md、#6 md-wechat、#7 wechat-format、#10 md2Card、#11 xiaohongshu-creator、#12 xhs-text-card(Obsidian)、#22 html2canvas。

---
*设计约束：所有工具引用均可追溯至调研报告，无外部未经验证引入。*
