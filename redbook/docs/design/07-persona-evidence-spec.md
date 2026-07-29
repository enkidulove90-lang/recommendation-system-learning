# Persona 证据化内容设计规范

更新：2026-07-29。本文定义 `redbook/personas/*.yaml` 的结构化策略层，并说明它如何把科学传播研究转为当前论文图文链路中的可审核约束。

## 设计目标

Persona 不是“更活泼的语气包”，而是一次明确的内容决策：读者要完成什么任务、什么事实可说、先看什么图、如何发起可回答的讨论、用什么指标评估。这避免了把“高互动”误当作唯一内容质量。

## 配置模型

```yaml
strategy:
  version: 2
  reader_job: "读者需要完成的具体动作"
  research_basis:
    - evidence_id: scicomm_证据包中的论文 ID
      use: "允许迁移的设计结论"
  content_contract:
    opening: "首屏规则"
    sequence: [正文段落顺序]
    evidence_rule: "事实和不确定性的表达规则"
    link_rule: "论文、PDF、代码的独立链接规则"
  interaction_design:
    question_type: "可回答的问题"
    follow_up: "评论回复规则"
  visual_plan:
    order: [图片页顺序]
    accessibility: "图注和可读性要求"
  success_signal:
    primary: "主要指标"
    secondary: "辅助指标"
    do_not_optimize_for: "禁止的虚荣指标"
  experiment:
    variable: "账号内 A/B 变量"
    guardrail: "保证可比较的边界"
```

## 研究到设计规则的映射

| 研究 | 经验证据 | 在本项目中的可迁移设计 | 不可宣称 |
| --- | --- | --- | --- |
| Wang et al., 2018 | 社交注意力与文章访问相关，效果集中在发布早期。 | 首屏与链接清晰指向论文对象；记录链接点击。 | 发帖必然提高引用、任意平台必然爆发。 |
| Habibi & Salim, 2021 | 在其 Instagram/TikTok 场景，动态实验内容参与更高。 | 将首图或动态图作为小红书账号内可测试变量。 | 小红书论文图文必须视频化。 |
| Martin & MacDonald, 2020 | 人际化表达、具体问题与回复和科学对话相关。 | Persona 使用可回答的问题，并定义运营跟进。 | 具体提问必然提高小红书评论量。 |
| Cinelli et al., 2022 | 清晰度、叙事、行动号召、受众匹配可与透明度并存。 | 用 `reader_job`、清晰图注、结构化行动指引与平台内实验。 | 任一文案结构可复制出固定互动率。 |

上述结论均为转述；原始论文、解析 Markdown 路径和适用范围记录在 [`scicomm_2026.yaml`](../../config/evidence_packs/scicomm_2026.yaml) 与 [`content_evidence_policy.yaml`](../../config/content_evidence_policy.yaml)。

## 当前角色的任务分工

| Persona | 首要读者任务 | 主要成功信号 | 关键防错点 |
| --- | --- | --- | --- |
| `research_translator` | 判断是否需要继续读 | 收藏后打开原文 | 不用名人或爆点替代论文本身。 |
| `implementation_reviewer` | 判断是否值得复现 | 复现实验清单请求 | 不补造参数、代码或结果。 |
| `industry_analyst` | 判断技术路线影响 | 含场景和约束的评论 | 推断与论文事实分开。 |
| `study_coach` | 带着问题回看原图 | 含图号/术语的提问 | 类比不替代原文定义。 |
| `evidence_auditor` | 核验证据与适用范围 | 可检验的证据讨论 | 相关性不写成因果。 |
| `weekly_curator` | 多篇中筛出精读对象 | 打开论文详情页 | 不用热点词伪造时效或影响力。 |

## 运行时约束

`PersonaPostComposer.build_generation_prompt()` 在生成任何草稿时同时注入 persona 的 `strategy` 与全局证据策略。这样，即使采用 Qwen/DeepSeek 等模型，模型也必须按内容顺序、事实边界、互动问题和链接规则生成。

所有 A/B 测试仅在同一账号内做，并固定论文、事实、链接、主题和可比发布时间；先积累可比样本，再调整 persona。草稿生成和测试均不等于自动公开发布。
