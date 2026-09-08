# 配图框架（baoyu-article-illustrator 落地）

排版由 `gzh-design` 组件库负责；**配图**由 baoyu 的 `Type × Style × Palette` 三维框架决策。
本文件把它落到本项目（recsys-blue 主题）的具体用法。

## ⚠️ 图片来源优先级（2026-08-11 起生效，覆盖原 AI 生图默认）

技术类论文推文**严禁用 AI 生图表达技术内容**——语义不可控、易与正文细节错位，且削弱专业可信度。配图来源按以下优先级取：

1. **论文原图提取（首选）**：优先复用论文自带图（架构/流程/实验/表格截图），经 `vision_enhancer` 提取并人工挑「美观且相关」的图（见 `data/parsed/<id>/<id>_figures.json`）。最贴合文本、零版权风险、可署名「图表摘自论文」。
2. **检索图（次选）**：仅当某节论文无对应图、且确需场景/氛围图时使用（如「背景痛点」配开发者实拍）。须确认可商用/署名授权，规避公众号发布版权风险；不确定时宁可不放图。
3. **AI 生图（最后手段）**：仅用于纯装饰性封面/分隔，绝不用于方法、结果、实验等技术内容；且须人工核验与文本一致。

> 默认关闭 AI 生图；新文章配图先走「提取论文图 → 缺则检索」两路，AI 生图需显式确认才启用。

## 三维定义

- **Type（信息结构）**：`infographic`(数据/指标) · `scene`(叙事/氛围) · `flowchart`(流程/步骤)
  · `comparison`(对比/取舍) · `framework`(架构/模型) · `timeline`(演进/历史)
- **Style（渲染风格）**：`notion`(知识分享) · `blueprint`(架构/系统性) · `minimal`(核心概念)
  · `warm`(亲和/反思) · `elegant`(观点/深度) · `watercolor`(生活/创意)
- **Palette（配色，可选，覆盖 Style 默认色）**：本项目统一用 **tech-blue**（主色 `#3a5fcd` 衍生，
  浅蓝 `#eef3ff` / 深蓝 `#1f3a8a` / 中性灰 `#8a94a6`），保证配图与正文主题色一致。

> 组合示例：`--type framework --style blueprint --palette tech-blue`

## 本项目文章各节配图决策表（以 LOOPSBENCH 为例）

| 文章节 | 目的 | Type | Style | Palette | 来源优先级 |
|--------|------|------|-------|---------|-----------|
| 钩子 / 背景 | 制造痛点氛围 | scene | warm | tech-blue | 论文图（无则检索） |
| 方法框架（DAG / 双容器） | 讲清架构 | framework | blueprint | tech-blue | **论文图** |
| 关键结果 | 数据可视化 | infographic | blueprint | tech-blue | **论文图** |
| 局限 / 诚实备注 | 对比反思 | comparison | warm | tech-blue | 论文图 |
| 实践建议（5 步） | 流程步骤 | flowchart | notion | tech-blue | 论文图（无则省略/检索） |
| 写在最后 | 观点升华 | timeline | elegant | tech-blue | 论文图（无则省略） |

## 工作流（遵循 baoyu skill）

1. **分析结构**：识别哪些节需要配图（隐喻→可视化底层概念，不画字面图）。
2. **确认设置**（AskUserQuestion，可跳过若用户说「直接生成」）：Type / Density / Style / Palette / 语言。
3. **提取论文图**：先查 `data/parsed/<id>/<id>_figures.json` 的已筛选图；没有则跑 `vision_enhancer` 提取并由人工挑图。论文图直接进正文，图注标「论文图 N」。
4. **缺图再检索 / 最后才 AI 生图**：论文无对应图的节，优先检索可授权图；仍缺且为纯装饰时才写 prompt 用 `ImageGen` 生成，并人工核验语义一致。
5. **接入正文**：图通过 `components.md` 的 `figure` 组件插入对应节，配图注（论文图注明来源与图号）。

## prompt 文件模板

```markdown
# NN-framework-method-arch
Type: framework
Style: blueprint
Palette: tech-blue
Purpose: 用依赖 DAG 表达「循环改代码」的任务结构，节点=可独立测试单元，边=前置关系
Visual: 浅蓝背景，节点为圆角方块连成有向无环图，顶部标注「编辑执行 / 测试裁决」双容器
Language: zh
Negative: 不要出现真实代码、不要堆文字、保持留白
```

## 与排版系统的衔接

- 配图产物只走 `figure` 组件进正文，不自带样式/脚本。
- 配图风格（tech-blue）必须与 `themes/theme-recsys-blue.md` 主色一致，避免图文掉色。
- 没有真实图 URL 时，用 `figure` 的占位说明（如「图 N｜待补：方法架构示意图」），不要留空 `<img>`。
