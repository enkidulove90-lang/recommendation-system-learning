# XHS 投递链路下一步开发计划（基于五会话审计 + git 实测，2026-11-19）

> 输入：`data/workflow_state/session_audit/recent_five_agent_sessions_2026-11-19.md`（五会话逐命令审计）
> 实测基线：`.worktrees/sab-anc-design`（experiments 分支，HEAD `6431629`），**领先 origin/experiments 12 个提交未推送**
> 汇总会话结论引用：审计报告第 15455-15459 行——仅第 1 条为真实开发主会话，第 2-5 条为 Guardian 审核子会话（无执行动作，计划中忽略）
> 定位：本文是**执行层计划**，承接既有 `xhs_delivery_ops_dev_merged`（S0-S4/TC-01~TC-12）与 `xhs_orchestration_devplan_v2`（M0-M5+A5），按审计揭示的最新进度重新排序。

---

## 2026-11-19 晚执行更新（以此节为当前状态）

早前章节保留为历史计划；以下记录覆盖其中已过时的完成状态。

| 审计批次 | 当前状态 | 后续边界 |
|---|---|---|
| A：合格金丝雀 note | 阻塞 | `2611.17921` 仍缺官方 GitHub；须由用户选择新的合格论文，或等上游官方仓库发布。 |
| B：reconcile 接线 | 已完成 | `note --reconcile` 已接入 SAVING、VERIFIED、UNCERTAIN 对账和只读孤儿清单；定向测试通过。 |
| C：授权金丝雀 | 未开始 | 依赖 A 和用户对一次 `draft_only` 保存的明确批准；需归档截图和 verify JSON。 |
| D：既有孤儿草稿 | 未开始 | 每个草稿均须先只读 verify，再取得逐 ID 删除批准；不得批量操作。 |
| E：文档与审计工件 | 进行中 | 本次补 runbook、计划决策记录和 session audit 入库；提交前需全量回归。 |

T5（registry 路线裁定）、T7（错误码与回执）和 T8（SQLite registry 与对账核心）已由
`9fec8b8`、`2bfd6da`、`eaf0e11`、`4daf1e9`、`06b80ca`、`de3409a` 实现或固化。T3 的
历史草稿只读诊断完成，但不等同于 C 的合格金丝雀验收；T4 继续受 A 阻塞。

---

## 一、现状盘点（审计 + git 实测）

### 1.1 已完成（可视为既成事实，勿重做）

| 事项 | 证据 |
|---|---|
| 会话级修复（11-19 凌晨）：话题芯片点击绑定（每次选后重开面板）、`#` 前缀归一化、`{ok,data}` 信封解包、草稿 `s:93a910ec` 成功保存（3 话题/5 图/PDF 已验证） | 审计 fileChange #30-41；manifest stage=draft_saved |
| SDD 实施计划 Tasks 1-6 全部 complete：delivery_errors 七个 E_* 码、OpenCliClient 统一解包、preflight 门禁（E_PREFLIGHT_BLOCKED）、--save-draft 别名 + --verify 只读校验、DeliveryRegistry（record_verified/record_orphan/find_verified + 幂等复用）、32→64 hex staged 目录迁移、PF-1~PF-4 平台事实固化、venue_alias json→yaml | progress.md ledger（审计 #44/#57/#97）；commits `9bbeb69..6431629` |
| 全量测试通过：**126 passed, 1 skipped, 11 subtests** | 审计 #97 |
| 平台事实 7.1 节入 spec、`session-audit-template.md`、toolchain 配置（extension_min_version 1.0.27 / orphan_policy / 64hex 目录格式） | 审计 #49-#50 |
| 附带产出：ArxivSource 候选源、platform_adapters（Jike/X，public-only 需审批） | 审计 #77-#80，commit `7498c6c` |

### 1.2 悬置与未决（计划的直接对象）

| # | 悬置项 | 证据 |
|---|---|---|
| H1 | **experiments 12 提交未推送**（931365b→6431629，含全部 Tasks 1-6） | `git log origin/experiments..experiments` = 12 |
| H2 | **验收未通过**：TC-03 既有草稿回读 body mismatch；TC-02 无独立批准的金丝雀；无草稿箱截图 | acceptance manifest（审计 #95-#96）：overall **not accepted** |
| H3 | **工作区未提交工件**：1 M（feature_source_survey.md）+ 7 个 untracked docs + `data/workflow_state/2611.17921/`（含 acceptance 证据）+ `data/papers/2611.17921_RecMem.pdf` | `git status --short` 实测 |
| H4 | **registry 技术路线冲突**：Task 4 已实现 per-slug JSON（`data/workflow_state/<slug>/delivery_registry.json`）；而 orchestration devplan v2 铁律 1 规定 SQLite 单表事实源 + 唯一索引 `(platform, account, staged_id)`。两方案并存无裁定 | 审计 #62-#67 vs devplan v2 §0.4 |
| H5 | **E_* 码表不完整**：已有 7 码（PREFLIGHT/OPENCLI_UNAVAILABLE/RESPONSE_SHAPE/TOPIC_UNAVAILABLE/SAVE_UNVERIFIED/VERIFY_MISMATCH/REGISTRY_CONFLICT），缺 `E_VERIFY_UNCERTAIN`、`E_ROLLBACK_FAILED`、`E_AUTH`、retryable/next_step/owner 字段、exit code 映射 | 审计 #46 vs devplan v2 M2 |
| H6 | **文档基线漂移**：主工作区（detached HEAD 0d8dd49）的 system_design_assessment 结论"delivery_registry 不存在、错误码表未实现"已**过时**——experiments worktree 已实现 | git 实测 vs 评估文档 §附 |
| H7 | phase1 分支 S0-S4 合并计划未核对：Tasks 1-6 直接做在 experiments 上，phase1 的 58 提交是否仍有移植价值需重判（branch_diff_analysis 结论"平行演化"可能已被部分消解） | merged 总纲 §3 |
| H8 | 每日自动化（redbook-daily-paper-draft）仍走旧口径（automation prompt 提 `save-xhs-draft`，与 --save-draft/--verify 新契约未对齐） | 审计 #13 首条用户上下文 |

---

## 二、任务清单与优先级排序

### 短期阶段（Sprint 0：本周内，目标=验收闭环 + 资产安全）

#### T1【P0】推送 experiments 分支
- **目标**：12 个未推送提交上远程，消除单点丢失风险。
- **产出**：`git push origin experiments` 成功输出；`git ls-remote` 确认 origin/experiments = 6431629。
- **操作要点**：用系统 git 直连姿势（`git -c http.proxy= -c https.proxy= push`），失败按既定姿势循环重试、代理兜底；大推送加 `http.postBuffer`。
- **依赖**：无（最先做）。

#### T2【P0】提交悬置工件（H3）
- **目标**：工作区归零，审计文档与验收证据入库可回溯。
- **产出**：三类提交——
  1. `docs(xhs): 七份审计/计划文档入库`（review / session_audit / branch_diff / devplan / merged / superpowers plan + feature_source_survey.md 修正）；
  2. `docs(xhs): next-step plan 本文档`；
  3. `chore(evidence): 2611.17921 acceptance 证据与 checkpoint`（`data/workflow_state/2611.17921/` 全量，含 acceptance 目录、manifest、registry 片段；PDF `data/papers/2611.17921_RecMem.pdf` 按仓库既有惯例一并入库）。
- **依赖**：T1 之后提交推送可一并带上；与 T1 可合并执行。

#### T3【P0】验收闭环：TC-03 body mismatch 诊断（H2）
- **目标**：搞清"既有草稿 s:93a910ec 回读 body mismatch"是**内容漂移**（草稿保存后 spec/正文被改过）还是**校验器缺陷**（回读归一化与写入不一致，如 emoji/空白/换行差异），并出结论。
- **步骤**：
  1. 用 `--verify --draft-id s:93a910ec` 只读回读，dump 实际 body 与 spec body 的逐字符 diff（禁写操作）；
  2. 判定归因：若是 spec 改动（note yaml topics 已从 5 改 3，正文若也改过则草稿为旧版）→ 结论"草稿为旧 staged 版本，预期内"，重新 stage+save 新草稿再 verify；
  3. 若是校验器归一化缺陷 → 修 `_verify_saved_draft` 的比较逻辑，补归一化单测。
- **产出**：诊断报告（进 `docs/`）+ 归因结论 + （若需）修复提交 + 重跑 verify 的 `body_ok/topics_ok/pdf_ok` JSON。
- **依赖**：T1/T2（证据可回溯后再动平台）。

#### T4【P0】金丝雀投递 + 截图证据（H2 后两项）
- **目标**：补齐 acceptance 缺口——独立批准的金丝雀投递 + 草稿箱截图。
- **步骤**：选当前 staged 包 → 用户显式批准 → 真机 T3 smoke（save-draft → --verify → 草稿箱截图）→ 按 `session-audit-template.md` 产出会话审计。
- **产出**：acceptance manifest 更新为 **accepted**；证据归档 `data/workflow_state/2611.17921/acceptance/`（截图、JSON、pytest 尾行、commit hash 清单）。
- **依赖**：T3 结论（若需重建草稿）。

#### T5【P1】registry 路线裁定（H4）
- **目标**：消除 JSON-per-slug 与 SQLite 单表两方案的并存冲突，出唯一裁定。
- **建议裁定**：**短期维持 per-slug JSON**（单进程投递下无并发写风险，Task 4 已验证、有单测；符合低运维），把"SQLite 单表 + 唯一索引"移入 M3 硬化阶段作为**迁移项**而非推翻项；devplan v2 铁律 1 措辞相应修订。
- **产出**：裁定记录（进 devplan v2 决策记录节 + MEMORY.md），M3 任务书更新。
- **依赖**：无，可与 T3/T4 并行。

#### T6【P1】文档基线修正（H6）
- **目标**：`system_design_assessment_redbook_2026-11-19.md` 补"基线差异附注"：experiments worktree 已实现 delivery_errors/registry/preflight/save-draft/verify，原文"不存在清单"中 4 项状态变更（registry、错误码表、--save-draft、验证 CLI），其余仍成立。
- **产出**：评估文档修订 + 注明两基线（0d8dd49 vs 6431629）。
- **依赖**：T2 入库后修订。

### 中期阶段（Sprint 1-2：1-2 周，目标=契约硬化与对账）

#### T7【P1】E_* 码表补全与回执 envelope（H5，= devplan v2 M2 余量）
- **目标**：新增 `E_VERIFY_UNCERTAIN`（验证不确定→待对账不删）、`E_ROLLBACK_FAILED`、`E_AUTH`（→扫码接管）；回执补 `retryable/next_step/owner` 字段；CLI exit code 映射（人工类 2 / 可重试类 3）。
- **产出**：`delivery_errors.py` 扩展 + 表驱动单测 + 每日自动化 prompt 对齐（H8 一并解决：automation 改用 `note <slug> --save-draft` + `--verify` 口径）。
- **依赖**：T5 裁定（码表归属 delivery_errors 不变）。

#### T8【P1】注册表硬化与对账 job（= devplan v2 M3 核心）
- **目标**：唯一键 `(platform, account, staged_id)`、保存前 SAVING intent、启动对账（SAVING 超时扫描 / MISSING 处理 / E_VERIFY_UNCERTAIN 读回重试）；WeChat 侧纳入同一 registry。
- **产出**：registry v2 + reconcile 模块 + 崩溃恢复用例（模拟保存后 kill）。
- **依赖**：T5（路线裁定）、T7（错误码）。

#### T9【P1】phase1 合并价值重判（H7）
- **目标**：Tasks 1-6 在 experiments 落地后，重新 diff phase1 vs experiments 的投递模块；判定 merged 总纲 S0-S4 中哪些条目已被 Tasks 1-6 等价覆盖、哪些仍需 cherry-pick（重点：phase1 独有的 daily_runner/排期类改动）。
- **产出**：S0-S4 清单勾销表；若仅剩少量独有提交，一次 cherry-pick 批次收口；若已无净增量，记录"合并计划关闭"。
- **依赖**：T1 推送后 diff 才可靠。

### 长期阶段（Sprint 3+：3-4 周，目标=编排层）

#### T10【P2】M1 队列与可观测骨架（devplan v2）
SQLite WAL jobs/leases/events 三表 + worker 骨架（--once/--drain）+ trace_id/指标 + runs.jsonl 按日文件。依赖 T7/T8。

#### T11【P2】M4 并发调度与账号级限流
生成并行/保存账号串行两阶段、独立 session（job_id 前缀，只清理自己的）、平台能力矩阵（XHS 支持强校验 / WeChat 保存灯即可）、scheduler/strategy 死代码删除（已有 Jike/X adapter 需一并纳入审批语义）。依赖 T10。

#### T12【P2】M5 收件箱与通知
`data/inbox/manual/` 聚合（待人工/可重试/待对账/回滚失败/HTML 预览/扫码）+ notify outbox（批次汇总、成功静默）。依赖 T7/T8/T11。

#### T13【P2】A5 平台契约注册表
把 PF-1~PF-4 + toolchain 配置扩展为完整 `platform_contracts.yaml`（选择器/文案/IndexedDB 版本化）+ 契约测试 + 三层试验 gate。依赖 M0 契约（现状契约已部分存在）。

---

## 三、依赖关系图

```text
T1 推送 ─→ T2 提交悬置工件 ─→ T3 TC-03 诊断 ─→ T4 金丝雀+截图 ─→ 验收 accepted
                                  │
T5 registry 裁定 ────────────────┼─→ T7 码表补全 ─→ T8 注册表硬化/对账 ─→ T10 队列 ─→ T11 并发 ─→ T12 收件箱/通知
T6 基线修正（依赖 T2）            │
T9 phase1 重判（依赖 T1）────────┘
T13 A5 契约（可与 T10-T12 并行）
```

关键路径：**T1 → T2 → T3 → T4 → T7 → T8 → T10 → T11 → T12**；T5/T6/T9/T13 可并行插入。

---

## 四、风险与应对

| 风险 | 等级 | 应对 |
|---|---|---|
| 推送失败（代理/网络，仓库 fetch 慢是已知坑） | 高 | 系统 git 直连姿势优先、代理兜底、循环重试；T1 必须最先执行 |
| TC-03 归因错误导致误删有效草稿 | 高 | 诊断阶段全程只读（--verify / drafts API 对账）；任何删除仅限"本次新建且确认 mismatch"（orphan_policy 既有约定） |
| 金丝雀投递触发平台风控/登录态失效 | 中 | 投递前 `probe_login` + preflight；一次只投一包；失败按 E_* 分拣不盲目重试 |
| registry 双方案并存期间出现状态分裂 | 中 | T5 裁定后立即在 devplan 决策记录落档；M3 迁移前 JSON 为唯一事实源，禁止双写 |
| 每日自动化与新人机契约漂移（H8） | 中 | T7 中把 automation prompt 更新为 --save-draft/--verify 口径，作为码表任务的一部分而非独立事项 |
| 文档基线混乱（主工作区 vs worktree 两套文档） | 中 | T6 补注基线；后续所有投递类开发统一在 sab-anc-design worktree（experiments）进行，主工作区仅作只读参照 |
| guardian 子会话噪音混入计划归因 | 低 | 遵循审计汇总结论：以第 1 条主会话为准（已执行） |

---

## 五、阶段划分总览（便于评审跟踪）

| 阶段 | 时间窗 | 任务 | 完成判据 |
|---|---|---|---|
| Sprint 0（短期） | 本周 | T1-T6 | origin 同步、工作区归零、acceptance manifest = accepted、裁定与基线修正落档 |
| Sprint 1-2（中期） | 1-2 周 | T7-T9 | E_* 码表 10 码 + envelope 字段齐、registry v2 + 对账 job 上线、phase1 合并清单勾销或关闭 |
| Sprint 3+（长期） | 3-4 周 | T10-T13 | 队列/并发/收件箱/契约四模块按 devplan v2 DoD 验收（含六条铁律自查） |

每任务关单证据沿用既有约定：pytest 尾行原文、命令 exit code、平台侧 JSON/截图、commit hash、registry 片段、hash 三处一致比对；统一归档 `data/workflow_state/<slug>/acceptance/`。
