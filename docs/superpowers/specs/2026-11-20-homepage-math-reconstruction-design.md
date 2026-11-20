# P0-A：个人主页公式统一渲染与证据驱动重建设计

日期：2026-11-20
状态：已确认，待实施
范围：`D:/enkidulove90-lang.github.io` 的 Hexo 个人主页；主仓仅保留本设计与后续跨仓审计证据。
不在范围：部署、公开发布、小红书或微信公众号投递、全文重写、无证据内容补写。

## 1. 目标与已核验基线

P0-A 统一个人主页论文文章的数学内容渲染，并恢复早期文章中已经丢失的公式或表格。恢复必须保持来源可追溯、重复执行幂等，且不覆盖已存在的中文解读、图片、链接或人工编辑内容。

已核验的基线如下：

- Hexo 7.3.0 与 Butterfly 5.2.2 已使用；Butterfly 原生支持 MathJax。
- 站点有 101 篇文章，50 篇命名为 `paper-<arxiv_id>.md`，其中 6 篇仍有 LaTeX 数学定界符。
- `paper-2607.16633.md`（BONSAI）和 `paper-2610.05432.md`（OpticalRec）已由用户目检确认公式渲染正确，是本次回归基准。
- 当前仅 OpticalRec 通过 `paper-2610.05432.js` 与 `scripts/opticalrec-math.js` 加载/保护数学内容；主题配置没有统一数学运行时，导致文章间行为不一致。
- 旧论文文章通常没有 `arxiv_id` front matter，但文件名中的 `<arxiv_id>` 是稳定、可审计的来源键。

## 2. 公式与表格规范

所有新生成、重建或规范化的论文文章采用以下格式；BONSAI 和 OpticalRec 作为可视回归样本。

1. 行内公式使用 `$...$`，仅用于短变量、指标和短表达式。
2. 独立公式使用单独的 `$$` 开闭行，公式前后各留一个空行；公式块中不插入 Markdown 列表或 HTML。
3. 统一用 LaTeX 表示数学符号和排版：集合/空间用 `\\mathcal{}`，向量/矩阵用 `\\mathbf{}`，直立文本或缩写用 `\\mathrm{}`，命名算子用 `\\operatorname{}`。希腊字母、乘号、正负号和关系符使用 LaTeX 命令而非 Unicode 数学字符。
4. 多行公式使用 `\\begin{aligned}...\\end{aligned}`；不把公式渲染为图片。
5. 表格使用 GFM 管道表。表格前必须给出来源表号或简短说明；表格后的解释不得新增原文不存在的数值结论。
6. 任何恢复块均放在成对锚点之间，锚点含 `block_id`、`arxiv_id`、来源类型与页码/解析定位。锚点不在网页正文呈现。

示例：

```markdown
<!-- paper-recovery:start id=method-objective arxiv=2607.16633 source=pdf page=5 -->

$$
\\mathcal{L}_{\\mathrm{SFT}} = -\\sum_{k=1}^{m} \\log P_{\\theta}(y_k \\mid x, y_{<k})
$$

<!-- paper-recovery:end id=method-objective -->
```

## 3. 架构与职责边界

### 3.1 主题级数学运行时

主题统一声明 `math.use: mathjax`。数学脚本只由一个共享运行时加载，不能同时保留 Butterfly 的 MathJax 和页面专属 MathJax 加载器。

为限制非论文页开销，采用 `math.per_page: false`，并只向审计确认含数学内容的文章写入 `mathjax: true` front matter。运行时资产须固定为一个已验收版本；实施阶段将在站点本地 `source/js/vendor/mathjax/` 资产与 Butterfly 配置的资源映射之间选择唯一实现，并通过离线构建及页面加载测试确认，不允许依赖两个版本或重复 typeset。

`paper-2610.05432.js` 不再负责 MathJax 初始化、加载或 typeset；其只可保留与该文章样式相关的代码。`scripts/opticalrec-math.js` 演进为通用的公式保护 filter，输入只限被标记为 `mathjax: true` 的文章。

### 3.2 审计清单

新增机器可读的审计清单（YAML），一篇论文一条记录，键为 `arxiv_id`。每条记录至少包含：

- 文章路径与来源 PDF/解析 Markdown 路径；
- `renderable`、`repairable`、`blocked` 或 `verified` 状态；
- 缺失块列表、块锚点、来源页码或 MinerU 段落定位；
- 原因、最后审计时间、恢复后内容摘要和验证证据路径。

状态只允许按如下方向迁移：

```text
discovered -> renderable | repairable | blocked
renderable -> verified
repairable -> verified | blocked
blocked -> repairable
```

`verified` 只能在构建、来源校验与目检均通过后写入。`blocked` 是正常安全结果，不能由生成器自动绕过。

### 3.3 证据驱动回填器

回填器以文章文件名 `paper-<arxiv_id>.md` 定位来源；优先使用已有 MinerU Markdown，缺失时才使用原始 PDF。它只恢复可明确定位的公式或表格块：

1. 解析已有文章，找出显式的缺失锚点或审计清单声明的插入位置。
2. 从 MinerU 段落或 PDF 指定页提取候选块；公式保留 LaTeX，表格保留结构化 Markdown。
3. 对候选块执行符号、数值、表号和页码核对；任一项无法确认则标为 `blocked`。
4. 仅替换同一 `block_id` 的受控锚点内容，或在清单指定的稳定标题锚点后插入一次。
5. 写回后更新审计清单与证据路径；再次执行不得产生第二个同名锚点或重复块。

回填器绝不重写整篇文章、绝不改写普通解释段、绝不从模型臆造数学式或实验数值。

## 4. 数据流

```text
paper-<arxiv_id>.md
  -> 数学内容审计
  -> 审计 YAML（renderable / repairable / blocked）
  -> MinerU Markdown 或原始 PDF 的页码证据
  -> 定点回填器（受控锚点）
  -> 主题级公式保护与单一 MathJax 运行时
  -> hexo generate + 页面目检
  -> verified 审计记录
```

个人主页是本阶段唯一消费者。小红书和微信公众号不读取、不写入该审计清单；三平台的投递状态继续由各自 registry 管理，避免 P0-A 引入跨平台耦合。

## 5. 错误处理与安全规则

- 来源 PDF 不存在、解析 Markdown 不存在或文件名无法解析 arXiv ID：写 `blocked` 和明确原因，不改文章。
- 公式/表格与来源的数值、符号、表号或页码不一致：拒绝写入。
- 一个文章已有同 `block_id` 但内容哈希不匹配：停止并要求人工复核，避免覆盖人工修订。
- MathJax 加载失败、重复加载或 typeset 失败：构建/页面测试失败，不能进入 `verified`。
- 所有文件写入前先生成审计 diff；不执行 Hexo deploy，也不触发 GitHub Actions 发布。

## 6. 测试与验收

### 自动测试

1. 公式规范化测试：BONSAI、OpticalRec 和代表性输入覆盖行内、独立、多行、希腊字母及 Markdown 表格格式。
2. 公式保护 filter 测试：被标记文章的 `$$`、`\\[...\\]` 和 `$...$` 在 Markdown 渲染前后保持等价；未标记文章不被改写。
3. 审计器测试：由文件名得到 arXiv ID；正确分类 `renderable`、`repairable`、`blocked`。
4. 回填器测试：仅插入/替换指定锚点、证据不全拒绝、同输入运行两次结果不变。
5. 来源测试：每个写入块都能回溯到 PDF 页码或 MinerU 段落，数值和表号一致。
6. 站点测试：`npm test`、`npm run test:python` 与 `npm run build` 全部通过；构建产物没有重复 MathJax loader。

### 视觉验收

- BONSAI 和 OpticalRec 页面必须继续正确显示其已验证的公式。
- 每类恢复块至少抽样一页，在浏览器中确认独立公式、行内公式和表格无原始定界符泄漏、无重叠、无横向不可读溢出。
- 每个 `verified` 记录需链接对应构建日志和截图/页面检查证据。

## 7. 实施顺序

1. 建立审计模型、规范化规则和 fixture 测试；不修改公开文章。
2. 接入单一主题级 MathJax 运行时，将 BONSAI 与 OpticalRec 作为回归基线。
3. 实现审计器，生成初始 YAML 清单并只报告候选，不回填。
4. 实现受控锚点回填器，以少量 `repairable` 文章做离线验证。
5. 按清单逐批恢复、构建和目检；`blocked` 条目保留人工复核。
6. 全量构建与证据归档通过后，单独评估部署；部署不属于本设计的自动动作。
