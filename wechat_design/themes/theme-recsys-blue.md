---
name: recsys-blue
description: 项目主主题——科技蓝，面向推荐系统 / AI 论文解读、技术科普、数据复盘类公众号文章。
主色: "#3a5fcd"
适用: 论文解读 / 技术科普 / 数据复盘 / 方法论拆解
组件库: ../components/components.md
下划线 CSS: 'border-bottom:1px solid #3a5fcd;color:#3a5fcd;font-weight:700;'
---

# 主题：recsys-blue（科技蓝）

本项目公众号文章的统一视觉基调。设计变量、骨架、配方、映射规则如下。
具体组件 HTML 一律从 `../components/components.md` 取，不要凭记忆手写。

## 设计变量速查

| 角色 | 值 |
|------|-----|
| 主色 ACCENT | `#3a5fcd` |
| 浅底 BG | `#eef3ff` |
| 卡片底 CARD | `#f5f8ff` |
| 标题色 TITLE | `#1a1a1a` |
| 正文色 BODY | `#3f3f3f` |
| 辅助灰 MUTE | `#8a94a6` |
| 警示色 WARN / 底 | `#f0a020` / `#fff7ec` |
| 成功色 OK | `#1a9e57` |

## 完整文章模板骨架

```
封面图 → 一句话高亮框 → 背景段 →
[色条小标题 + 正文/图] × N →
关键结果（数据表格 + KPI 卡片 + 诚实备注）→
局限 → 取舍 → 实践建议 → 读者分层 → 结语 →
互动引导 → 参考文献
```

## 文章类型 → 组件组合配方

| 主导类型 | 核心组件 | 点缀组件 |
|----------|----------|----------|
| 论文解读 / 数据复盘 | hook-title · one-liner · section-header · rr-table · kpi-cards · figure · limitation · cta · references | limitation（诚实备注） |
| 技术科普 / 方法论 | hook-title · section-header · body-para（关键词下划线）· figure · cta | kpi-cards |
| 工具盘点 / 清单 | hook-title · section-header · body-para（列表式）· cta | figure |

> 一篇文章只用本主题这一套组件，不跨主题混用。

## Markdown → 组件映射规则

| Markdown | 组件 |
|----------|------|
| `# 标题` | hook-title（大标题） |
| `## 标题` | section-header |
| `> 引用开头金句` | one-liner |
| `**短语**` / `==短语==` | body-para 内关键词下划线 |
| `\| 表格 \|` | rr-table |
| `![说明](url)` | figure（有说明才加图注） |
| 数字对比段 | kpi-cards |
| 局限 / 诚实说明 | limitation |
| 结尾互动句 | cta |
| 参考链接 | references |

## 平台红线（生成时必须遵守）

- 禁止：`<style>` / `<script>` / `<div>`、`class` / `id`、`position:fixed|absolute|sticky`、
  `float`、`@media` / `@keyframes` / `@import`、`display:grid`、`var(--x)`、外部字体/CSS。
- 必须：样式全内联；每个中文文字节点 `<span leaf="">文字</span>` 包裹。
- 图片：`max-width:100%;height:auto;display:block;margin:0 auto`（本主题封面/图用 `width:100%` 居中铺满，小图保持原尺寸）。
- 强调用「小标签 / 左竖条」，不用四周虚线框；半角标点改全角（代码/URL 内除外）。
