# 发布 persona

每个 YAML 是一个**发帖人角色**，不是受众标签。角色决定标题钩子、正文顺序、证据阈值、链接位置、话题与评论引导；同一篇论文可用不同 persona 产出不同稿件，再由反馈模块比较收藏率与讨论率。

除原有的 `id`、`name`、`audience`、`title_patterns`、`sections`、`topics`、`comment_prompt` 与 `prompt` 外，每个角色均包含可执行的 `strategy`：

| 字段 | 作用 |
| --- | --- |
| `reader_job` | 定义读者阅读后要完成的任务。 |
| `research_basis` | 连接本地证据包中的论文与允许采用的设计结论。 |
| `content_contract` | 规定开场、内容顺序、事实阈值与链接规则。 |
| `interaction_design` | 规定可回答的评论问题和运营回复方式。 |
| `visual_plan` | 规定原始图、结果图、知识图谱与论文详情页的次序。 |
| `success_signal` | 分开定义主要指标、次要指标和禁止优化的虚荣指标。 |
| `experiment` | 定义一个可在本账号内验证的变量及公平比较边界。 |

`PersonaPostComposer` 会把 `strategy` 和全局 `content_evidence_policy.yaml` 同时写入生成提示词。全局规则优先：只使用论文解析或官方来源事实；没有数字、代码或实验条件时明确写“原文未披露”；不使用夸大、恐吓或虚构的第一人称实验经历。

`redbook.cli compose-post --persona <id>` 会读取这里的配置并生成草稿 JSON，不会调用发布接口。`list-personas` 会输出完整的结构化策略，方便前端或人工审核读取。
