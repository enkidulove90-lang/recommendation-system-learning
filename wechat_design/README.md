# 公众号设计范式（wechat_design）

本目录是项目级微信公众号「排版 + 配图」双轨设计系统，由两份开源 skill 组合落地：

- **排版引擎**：`gzh-design`（`~/.workbuddy/skills/gzh-design` 或本项目 `.workbuddy/skills/gzh-design`）
  —— Markdown → 内联样式 HTML，主题组件库 + 双关卡校验脚本。
- **配图框架**：`baoyu-article-illustrator`（`.workbuddy/skills/baoyu-article-illustrator`）
  —— 文章结构分析 + `Type × Style × Palette` 三维配图。

两者结合 = 项目的公众号设计范式：**文字排版交给组件库 + 校验脚本兜底，配图交给 baoyu 框架决策**。

---

## 目录结构

```
wechat_design/
├── README.md              # 本文件：设计范式总纲
├── themes/
│   └── theme-recsys-blue.md   # 项目主主题：科技蓝（设计变量 + 骨架 + 配方 + 映射）
├── components/
│   └── components.md          # 组件库：每个组件一段合规 <section> HTML，可直接拷贝
├── illustration/
│   └── illustration.md        # baoyu 配图框架落地：本项目的 Type×Style×Palette 决策表
├── scripts/
│   ├── validate_gzh_html.py   # 产物合规校验（平台红线 + span leaf 包裹）
│   └── component_lint.py      # 组件库源头检查（反模式扫描）
└── examples/
    └── loopsbench_v2.html     # 用组件重排的 LOOPSBENCH 范例（纯 <section> 正文片段）
```

---

## 平台红线（粘贴进公众号后样式才不丢）

**禁止**：`<style>` / `<script>` / `<div>`、`class` / `id` 属性、`position:fixed|absolute|sticky`、
`float`、`@media` / `@keyframes` / `@import`、`display:grid`、CSS 变量 `var(--x)`、外部字体/CSS。

**必须**：样式全部内联 `style`；每个中文文字节点用 `<span leaf="">文字</span>` 包裹
（否则粘贴后样式整片丢失——这是最高频致命错）。

**可用**：`display:flex`（有限）、`linear-gradient`、`border-radius`、`box-shadow`、
`<section>/<p>/<span>/<strong>/<img>/<h1-3>/<table>/<a>`。

---

## 配色 / 字号铁律（recsys-blue 主题）

| 角色 | 取值 | 用法 |
|------|------|------|
| 主色 | `#3a5fcd` | 色条、标题强调、链接、下划线 |
| 浅底 | `#eef3ff` | 一句话高亮框底 |
| 卡片底 | `#f5f8ff` | KPI 卡片底 |
| 标题色 | `#1a1a1a` | 标题/小标题 |
| 正文色 | `#3f3f3f` | 正文（深灰优于纯黑，减疲劳） |
| 辅助灰 | `#8a94a6` | 副标、图注、注释 |
| 警示色 | `#f0a020` / 底 `#fff7ec` | 局限/诚实备注 |
| 成功色 | `#1a9e57` | 正向数据高亮 |

字号：正文 15px、小标题 17px、大标题 20px、图注 13px；行距 1.75–1.85；正文两端对齐；
全角标点（，。！？：；""''（）—— …），代码块/URL 内保持半角。

---

## 工作流

1. **写内容**：用 Markdown 写正文（标题 `##`、列表 `-`、表格 `|`、图片 `![说明](url)`）。
2. **选主题**：本项目默认 `recsys-blue`（见 `themes/theme-recsys-blue.md`）。
3. **装配**：按主题骨架，从 `components/components.md` 取对应组件的 HTML 粘到对应位置。
4. **校验（强制）**：
   ```bash
   python wechat_design/scripts/validate_gzh_html.py wechat_design/examples/loopsbench_v2.html
   ```
   ERROR 必须清零；半角标点 WARNING 也建议清零再交付。
5. **配图**：用 `illustration/illustration.md` 的决策表，为各节选 `Type×Style×Palette`，
   按 baoyu 流程生成配图（prompt 落 `prompts/NN-{type}-{slug}.md`）。
6. **预览**：用 gzh-design 的 `wrap_preview.py` 包成带「复制」按钮的预览页，浏览器打开 → 复制 → 公众号粘贴。

---

## 与已安装 skill 的关系

- `gzh-design` 是通用排版引擎（多主题）；本项目只用它的 `recsys-blue` 派生主题 + 校验脚本，
  组件库以本项目 `components/components.md` 为准（更贴合推荐系统/AI 论文解读场景）。
- `baoyu-article-illustrator` 只负责「配什么图、什么风格」，不参与排版；
  它的产物（配图）通过 `components.md` 的 `figure` 组件接入正文。
