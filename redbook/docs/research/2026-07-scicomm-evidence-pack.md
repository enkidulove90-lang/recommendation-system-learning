# 科技论文分享与科学传播：证据包

更新：2026-07-29。证据包清单见 `redbook/config/evidence_packs/scicomm_2026.yaml`；PDF、MinerU Markdown、布局 JSON 与图片资产保存在 `data/evidence/scicomm-2026/`。本包用于约束内容创作，不用于宣称小红书算法规律。

## 已下载并解析的开放论文

| 论文 | 可用结论 | 明确边界 | 项目约束 |
| --- | --- | --- | --- |
| Wang et al., 2018, *Social Media Attention Increases Article Visits* | 论文发布后的社交注意力会带来访问，且效应集中在早期并迅速衰减。 | 研究观察的是文章级 referral/attention；不能推出“发帖会提高引用”或任一平台必然爆发。 | 用论文、PDF、代码的清晰链接服务点击；不用“必涨引用”等承诺。 |
| Habibi & Salim, 2021, *Static vs. Dynamic Methods of Delivery for Science Communication* | 在其 Instagram/TikTok 实验场景中，动态实验性内容获得更高参与。 | 结果不等于小红书论文图文必须改视频，且内容、账号与算法均不同。 | 图文保持“原始架构图→结果图→案例/知识图谱”的可读结构；将动态形式列为后续平台内实验变量。 |
| Martin & MacDonald, 2020, *Using Interpersonal Communication Strategies to Encourage Science Conversations* | 人际化表达、具体可回答的问题和对回复的跟进与科学对话相关。 | 基于 Twitter/Instagram，不能量化预测小红书评论。 | 每个 persona 留一个具体评论问题；运营端应回复评论，而不是只在文案末尾索取互动。 |
| Cinelli et al., 2022, *Promoting Engagement with Quality Communication in Social Media* | 清晰标题、叙事、行动号召和受众匹配可与质量、透明度并存；应用真实数据做迭代。 | 研究对象是 Facebook/Twitter 的机构账号，不是推荐流平台的算法说明。 | 以收藏、评论、链接点击等任务指标分开评估，并在账号内做 A/B 测试。 |

## 对当前 Redbook 流程的监督方式

1. `content_evidence_policy.yaml` 将四篇论文的适用范围、不可外推项和落地规则写成机器可加载的策略。
2. `PersonaPostComposer.build_generation_prompt()` 每次构建 LLM 文案提示词时都会注入策略：事实必须来自论文解析或官方链接；“论文证明”“合理推断”“原文未披露”分开写；没有官方代码必须明示。
3. 固定图文模板不以“爆款”作为事实判断：封面和标题服务点击，正文的原图、结果和案例服务理解与收藏，评论问题服务对话；指标分别记录。
4. 任何“动态内容更好”“某时段必爆”“互动提高引用”的说法均被标为不可外推。要验证，只能在本账号、同一主题和相近内容质量下做 A/B 测试。

## 推荐的后续实验

在不公开自动发布的前提下，先保存草稿并人工审核。以同一篇论文的两个标题或两种首图进行平台内对照；每个版本记录展示、点击、完读/停留、收藏、评论和链接点击。连续积累至少 10 个可比样本后，再调整 persona 的标题、首图或评论问题规则。

## 可追溯入口

- [Wang et al. 2018](https://arxiv.org/abs/1801.02383)
- [Habibi & Salim 2021](https://doi.org/10.1371/journal.pone.0248507)
- [Martin & MacDonald 2020](https://doi.org/10.1371/journal.pone.0241972)
- [Cinelli et al. 2022](https://doi.org/10.1371/journal.pone.0275534)
