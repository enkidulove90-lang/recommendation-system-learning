# Agent 行为六类问题整改方案与失败测试修复计划（2026-11-22）

> 全部结论基于当日真实运行证据，非描述推断。失败分类已逐组复跑核实。

> 核实戳：2026-11-22。最初的失败归因是待验证假设；下表以当前 checkout 的命令输出为准。完整基线与回归日志保存在 Codex evidence `m0-baseline-20261122`、`m1-evidence-20261122`、`m2-regression-20261122` 中。

## 0. 当前提交树失败实况与旧结论对账

核验对象：`codex/main-worktree-recovery`，HEAD `273bf56cb9650700ac776ce7b763442129947e90`（父提交 `0d8dd49`）。核验方法：`git status --short`、`git ls-files`、`git check-ignore -v`、按模块 pytest 复跑、显式 Git 跟踪测试文件回归。以下结论仅适用于该提交树与当前 Windows/Python 3.13.11 环境。

| 组 | 当前代码事实 / 根因 | 修复与验证 |
|---|---|---|
| content_factory | 两个 JSON fixture 已由 Git 跟踪，且未被忽略；旧失败用例把 LightGCL 样本误当成门控融合论文，期待 `0.088`/“稀疏”。样本与来源 summary 实际为 SVD、Yelp R@20=`0.0793`，局限谈因果分析与可扩展性。 | 更新三个陈旧断言；模块 **57 passed**。在基于暂存树的 clean archive 中再次运行，**57 passed**。 |
| content_events | 测试辅助函数指向仓库根下不存在的生成目录 `publish_queue/`；Git 跟踪 fixture 在 `content_events/tests/fixtures/publish_queue/`，服务逻辑本身能处理 fixture。 | 辅助函数固定复制已跟踪 fixture；模块 **46 passed**。 |
| DTLE | `wechat_design/dtle/tests/test_dtle.py` 指向不存在的生成文件 `examples/loopsbench_dtle.json`；渲染器按公开契约把不存在路径当 Markdown 内容。 | 用受支持的 inline Markdown 输入测试同一渲染契约；模块 **13 passed**。 |
| sentinel | 当前 HEAD 没有 Sentinel runner/CLI 测试及其配置 fixture；不能用旧 worktree 路径宣称已复现或修复。 | 未修改；需将目标实现/测试纳入当前分支后再验证。 |
| ADA | 当前 HEAD 没有 ADA backend 并发测试或实现；“已知竞态”仅来自旧文档，不能当作当前结论。 | 未修改；需明确并合入目标分支后复现。 |
| pytest 环境与范围 | M0 默认收集在宽泛根目录遍历 archive/data 等路径时得到 **34 collection errors、0 tests**；原因包含路径冲突、缺依赖与平台专属导入，不能概括成单一 Temp 权限问题。 | 根级 `pytest.ini` 固定测试根和 `test_*.py` 模式；默认回归 **260 passed、11 subtests passed**。 |
| M1 后新增的全树失败 | 初次 36 模块确定性回归为 **13 failed、245 passed、11 subtests passed**：缺少且被 `*.json` 吞掉的 venue alias 配置 10 项；用户本地新增 note 使固定数量断言失败 2 项；Python 3.13 logging filter 返回 truthy `LogRecord` 而测试误用 `is True` 1 项。 | 增加明确、可跟踪的 `config/venue_alias.json` 和精确 ignore 例外；按确切迁移清单检查 note，允许 `data/parsed`/`data/evidence` 两类已观察根；按 filter truthiness 断言。最终默认回归 **260 passed、11 subtests passed**。 |

旧日志中的“27 failed、488 passed、1 skipped、11 subtests passed”来自另一工作树/较早状态，不是本 checkout 基线。M0 当前 checkout 初次根级测试为 34 collection errors；M2 后根级默认测试为 260 passed、11 subtests passed。不得继续互换这些数字或以一者覆盖另一者。

## 0.1 M2 与真实链路验证边界

- `AGENTS.md` 写入 `paper_intake` 不依赖 `redbook.*`；现有 `tests/test_paper_catalog.py` 增加 AST 方向检查与 Git 跟踪资产检查。
- 根 pytest 默认仅搜索已声明的项目测试根，`python -m pytest -q` 为可重放入口；现有内容日历 workflow 新增 PR-only 确定性测试 job。PR 不启动会写 `publish_queue` 的内容生产 job。
- 必需 fixture/config 的 SHA-256、workflow YAML 解析结果、clean archive 测试结果保存在上述 evidence 目录。pytest 的历史本地临时目录规则保留，并将 `.redbook_tmp/` 加入 ignore。
- 本次没有修改外部 API/平台投递逻辑；没有执行 arXiv、Notion、XHS 等 live 请求。`redbook/tests/smoke_test.py` 是会登录/请求真实小红书的交互脚本，不在确定性回归中运行。live 结果为“未运行”，不可表述成 live 通过。
- 初始方案中关于 Sentinel run_once 接入、WorktreeManager 审计、ADA 并发恢复等状态没有在当前 HEAD 验证，仍待目标代码进入当前分支。

## 1. 六类问题的根因与约束机制

> 本节列出的是待执行的风险控制方案，不代表代码已实现。实现状态以第 0 节的当前分支证据为准；来自其他工作树或会话的案例不作本分支验收证据。

### 1.1 擅自假设、默认决策不告知
**根因**：决策发生在"我替你选好了"的盲区里，且没有持久化载体，用户只有在后果显现时才能追溯。
**约束机制**：
1. **三态标注制度**（沿用 SAB-ANC 参数决议已验证的做法）：任何设计/配置落盘时，每个决策点标注【锚】(论文/用户指令锁定)【定】(已确认)【拍】(本次代拍，必须附网格与推翻判据)。
2. **代拍申报线**：凡涉及①删除/归档数据、②改配置默认值、③状态语义、④跨会话归属判断——必须显式提问，禁止代拍。
3. **假设登记表**：方案文档头部固定一节"本方案的代拍项与推翻条件"，交付时置顶展示，不出现在文末。

### 1.2 简单任务复杂化、产出难维护代码
**根因**：把"做出来"当目标，跳过"现状是否已有此能力"的检查。
**约束机制**：
1. **改动前合理性论证（≤5 行）**：现状 → 最小改动 → 被否备选方案。写不出这三行就不许动手。
2. **先复用后新建**：新文件前必须 grep 全仓同名/同职责实现。当前 HEAD 存在 `paper_intake/catalog.py`，未发现 `catalog_governance.py`；此前“70% 已落地”的说法不属于当前分支的已验证事实。
3. **diff 预算**：修复类任务新增文件数 >2 或新增行 >修改行 3 倍时，必须先说明为什么不是修改既有代码。

### 1.3 代码与文件层次混乱
**根因**：没有先回答"这个文件属于哪一层、谁能依赖谁"。
**约束机制**：
1. **层级判据**（已成文）：回答"论文是谁/在哪/何时/DOI"→ 全局层（paper_intake/、仓库根）；回答"某平台对它做了什么"→ 管线层（redbook/）。
2. **依赖方向红线**：`paper_intake` 永不 import `redbook.*`；写入 AGENTS.md 并在 CI 检查（import-linter 或简单 grep 门禁）。
3. **路由登记**：新模块进入仓库现有路由表；当前 HEAD 未发现 `config/skill_registry.yaml`，不得把它描述为现有机制。

### 1.4 临时产物臃肿
**根因**：`.gitignore` 的 `*.json` 这类宽泛规则**静默吞掉应入库资产**（fixtures 直接丢失=测试在他机必挂），以及快照目录无生命周期管理（486MB 孤儿）。
**约束机制**：
1. **gitignore 白名单注释制**：每条忽略规则必须带行尾注释说明意图；新增"应入库但被忽略"的资产必须显式加 `!` 例外（本批修复第一项）。
2. **测试资产入库门槛**：`tests/fixtures/`、`tests/conftest.py` 引用的文件必须可 `git archive` 后独立运行——加一条 CI 守卫测试。
3. **归档而非删除**：当前 HEAD 未发现 WorktreeManager 实现；本方案只要求未来清理经受控归档，不代表当前分支已有归档能力。
4. **哨兵周期审计**：当前 HEAD 未发现 Sentinel `run_once`/runner 实现；该项尚未在本分支落地或验证。

### 1.5 不关注真实数据、自测通过即交付
**根因**：把"测试绿"当终点；mock 闭环掩盖真实环境差异。
**约束机制**：
1. **DoD 真实冒烟**：涉及外部系统/API/文件的改动，必须有一次对真实数据的冒烟并留痕（本会话两次实证：urllib HTTPError 吞状态码、OpenReview 403/429 语义，全部是 mock 测试发现不了的）。
2. **交付声明**：最终回复必须含"已验证范围 / 未验证范围"两栏，禁止把单测通过表述为全链路完成。
3. **计数对账**：涉及统计（如"27 failed"）必须复跑对账，禁止转述未核实的数字。

### 1.6 被旧文档/旧实现带偏、防御性表达侵蚀整改
**根因**：文档与代码不同步且无"已验证日期"；整改时用"稳妥起见"话术偷换为保守修补。
**约束机制**：
1. **代码事实优先**：接手任务第一步 `git log -p` 核对代码现状 vs 文档（本周实例：路由测试在 `tests/` 下从未被 pytest.ini 收集、asset.mathjax 被 CDN.option 覆盖——都是"读代码"抓出、文档全错）。
2. **文档验证戳**：每份设计/现状文档头部标注"核实于 YYYY-MM-DD + 核实方式"；超 30 天未复核的文档引用时必须先验证。
3. **表达约束**：整改类回复禁用"可能/视情况/稳妥起见"，替换为可执行断言 + 验证命令；若真有不确定性，走 1.1 的提问机制而不是防御性措辞。

## 2. 已核实问题的处理顺序与状态

| 顺序 | 组 | 当前证据与动作 | 状态 |
|---|---|---|---|
| P0 | pytest 范围 | 根级原配置没有 `testpaths`，初次出现 34 collection errors；现已固定项目测试根，并通过根级默认回归。 | 已通过：260 passed、11 subtests passed |
| P0 | content_factory | fixtures 已 tracked；修的是与 LightGCL 内容冲突的断言，不重建 fixture。clean archive 验证通过。 | 已通过：57 passed |
| P1 | content_events + DTLE | 测试输入路径缺失；改为已跟踪队列 fixture 与受支持的 inline Markdown。 | 已通过：46 + 13 passed |
| P1 | venue alias / note 增量 | 修复缺失的显式 alias 配置及被 `*.json` 忽略的问题；note 测试基于实际迁移清单，容忍用户增加合法 note。 | 已通过：相关测试纳入默认回归 |
| 待分支 | sentinel | 当前提交树无被引用实现/测试，未复制其他工作树。 | 未验证；目标代码进入本分支后复测 |
| 待分支 | ADA | 当前提交树无被引用实现/测试，不使用 sleep 或伪造 flake 结论。 | 未验证；目标代码进入本分支后复测 |

## 3. 整改清单与提交前验收标准

**改动范围**（全部留在工作树，归属清晰的会话各自提交）：
- [ ] 主仓 `.gitignore`：`*.json` 加 fixtures 例外 + 注释
- [ ] `content_factory/tests/fixtures/`：两个 fixture 重建入库（内容源自真实 summary，不手编数字）
- [ ] 主仓根 `pytest.ini`：basetemp 指向仓库内目录（父目录预存在）
- [ ] `content_events` serve/DTLE：真实语料 fixture 入库 + 断言修复
- [ ] sentinel 测试 fixture 补 daily_draft.yaml 或 CLI E_CONFIG 化（择一并写明选择理由）
- [ ] ADA 两测试竞态修法
- [ ] 本方案文档入 `docs/`

**提交前验收标准（全过才许 commit）**：
1. `pytest <各失败组> -q --basetemp=<repo-local>` 失败数为 0；全量回归失败清单逐项标注"已修 / 已知 flake+证据"。
2. **新 clone 冒烟**：`git stash` 全部改动后（或用 `git archive HEAD` 导出临时目录）跑 content_factory 全套——验证 fixtures 真正入库，不再依赖本机残留。
3. `git check-ignore content_factory/tests/fixtures/*.json` 返回非忽略。
4. 哨兵 `run_once` 产生含 `worktree_audit` 的 run report 样本一条，落 `data/logs/runs.jsonl`。
5. 交付报告含"已验证/未验证"两栏 + 失败计数对账（与 27 的差异逐项解释）。
6. 未提交改动归属清单：哪些文件归哪个会话，逐个列名（当前主仓 4 个已跟踪改动归 XHS 会话；sab-anc-design 未提交归 logging 会话）。

**明确不做**（防 1.2 复发）：不为凑绿改动产品逻辑；不给 ADA flake 加 sleep；不为 DTLE 绕过守卫断言。
