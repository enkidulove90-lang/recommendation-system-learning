# 主页论文文章写作规范（v1.0，2026-11-28）

适用于个人主页 `/article/<slug>/` 下的所有论文文章。渲染器：`paper_intake/notion_compiler.py::_review_markdown`。
本文件是唯一口径，改动需同步 `tests/test_notion_compiler.py` 与博客仓 `tools/paper_article.py::REQUIRED_SECTIONS`。

## 1. 结构

```
（导语：一段，不超过 3 句，说明这篇论文做了什么）
> 论文：<链接>　代码：<链接>

## 1 研究背景与问题
## 2 方法：{≤20 字的方法总结}
### 2.1 {≤20 字，含关键词}
### 2.2 {≤20 字}
### 2.3 {≤20 字}
## 3 实验：{≤20 字，点出实验最大特点}
### 3.1 数据集与 Benchmark
### 3.2 实验方法
### 3.3 实验指标与参数设置
### 3.4 实验结果与分析
## 4 论文总结：{≤15 字的核心创新与阅读价值}
## 5 References
```

硬性约束：

- **正文不出现标题**。标题只存在于 front matter，正文不得有 `# 一级标题`。
- 二级标题必须带阿拉伯数字编号（`1` / `2` / `3` / `4` / `5`）。编号只写一次：**不要**出现 `1. 一、` 这种双编号。
- 三级标题写成 `2.1` / `3.4`，不要 `（一）`。
- **没有内容的节整节不渲染**（连标题一起删）。禁止输出「原文或 FactPack 未提供，待核验」「待补充」这类占位文本。

## 2. 每节写什么

| 节 | 必写内容 | 字数下限 |
|---|---|---|
| 1 研究背景与问题 | 领域现状 → 具体痛点 → 为什么现在值得做 | 正文 ≥300 字 |
| 2 方法 | 先用一节总述输入、输出、整体流程；再按贡献拆 2–4 个点 | 总结 ≤20 字；总述 ≥150 字；每点 ≥120 字 |
| 3 实验 | 3.1 数据集与 benchmark；3.2 主实验/消融/提示词怎么跑；3.3 指标与超参；3.4 主结果 + 相对最强基线提升 + 原因 | 3.2 ≥200 字；3.4 ≥250 字 |
| 4 论文总结 | 核心创新 + 为什么值得读 | ≥120 字；标题 ≤15 字 |
| 5 References | 论文原始参考文献，完整书目 | — |

## 3. 图

- 方法与实验两节都要有图。**目标 4 张**（`FIGURE_TARGET=4`），是目标不是断言：论文只有两张合规图就放两张，不补假图、不把不相关的图表凑数。
- 图源优先级：arXiv LaTeX 源图 → PDF 288 dpi 重渲染（含 `table` 块）→ MinerU 抽图。同一张图跨来源时按 `figure_id` 去重。
- 图片位置：架构/框架类放第 2 节；结果/对比/案例类放 3.4 之后。
- **图注**：图后面必须紧跟 2–3 句可读描述，说明这张图在讲什么、对比了什么、读者该看哪里。禁止 `图示解释：<caption>` 这种前缀，也禁止只把英文 caption 原样贴过来。

## 4. 公式

- 用 `$...$`（行内）与 `$$...$$`（独立）。渲染前由 `locate_formula` 在原文中唯一定位，定位不到的不进正文、只记 `unplaced`。
- 不在公式上方加「原文公式（来源章节…）」这类说明行。

## 5. References 格式

一条一行，作者 → 年份 → **标题（加粗，带论文链接）** → 出处 → 可选代码链接：

```
Yueqi Wang, Zitian Guo, Yupeng Hou, Yifei Wang, Kibum Kim, Zhenrui Yue, Shuo Xing, Haodong Li, Heming Xia, Renrui Zhang, Zhengzhong Tu, and Julian McAuley. 2026. OpticalRec: Unified Optical Vision-Language Representation for Multimodal Recommendation. arXiv preprint arXiv:2610.05432.
Kibum Kim, Jiwan Kim, Kyle Min, Yueqi Wang, Jinyoung Moon, Julian McAuley, and Chanyoung Park. 2026. Sink-token-aware pruning for fine-grained video understanding in efficient video llms. arXiv preprint arXiv:2604.20937. （代码：https://github.com/rlqja1107/SToP）
OpenAI. 2026. OpenAI gpt-5 system card. Preprint, arXiv:2601.03267.
```

规则：

- 作者用 `A, B, and C` 连接；单个作者不加 `and`。
- 条目取自论文 PDF 自带的 References 段（`extract_references`），不靠模型编造；能定出 arXiv 号的给链接，定不出就只保留书目文本。
- 代码链接以 `（代码：<url>）` 形式接在条目末尾。
- **不写本地 PDF 链接**（`/papers/xxx.pdf` 一律不出现）。站点没有文件库，只保留 http(s) 网页链接。

## 6. 验收

编译产物（`article_input.markdown`）必须同时满足：

1. 不以 `# ` 开头；
2. 含 `## 1 研究背景与问题`、`## 2 方法`、`## 3 实验`、`## 4 论文总结`、`## 5 References`；
3. 不含 `待核验`、`图示解释`、`/papers/`；
4. 每张图后面都有 ≥20 字的说明段；
5. `tests/test_notion_compiler.py::test_manuscript_follows_the_five_section_site_spec` 通过。
