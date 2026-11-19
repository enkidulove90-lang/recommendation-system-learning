# 小红书投递链路：运维与开发综合文档（合并版）

生成：2026-11-19（Asia/Shanghai）
整合来源：
- 《小红书链路报错修复运维文档》= `docs/session_audit_xhs_draft_repair_2026-11-19.md`（会话审计）+ `docs/branch_diff_analysis_xhs_delivery_2026-11-19.md`（分支差异分析）
- 《冗余修复与分支开发进度文档》= `docs/xhs_delivery_backend_devplan_2026-11-19.md`（开发计划）

定位：本文是唯一的运维+开发执行总纲；上述三份文档降级为历史索引与详细依据。结构：背景现状 → 代码改动清单 → 分支合并计划 → 验收用例 → 证据要求。

---

## 一、背景与现状汇总

### 1.1 故障背景

2026-11-19 草稿修复会话定位并修复：投递后草稿"只有 #算法、正文为空"，且历史草稿被拆分到多条记录（正文/话题/PDF 各占一条）。根因两层：

1. **直接诱因**：投递入口从 phase1 链路切换到 experiments 的 `cae019f`（11-10）中间态重构实现 × 扩展处于过期版本 1.0.25（原生输入路径断裂）。
2. **结构性根因**：phase1 与 experiments 对同一平台做了两次平行实现，平台行为硬事实（`#` 前缀/面板收起/原生输入不可用/`{ok,data}` 包装）均未固化为代码+测试；保存后验证与对账机制在两分支同时缺位。

### 1.2 当前状态（2026-11-19 13:35）

| 项 | 状态 |
|---|---|
| 11-19 修复代码 | **工作区未提交**（experiments worktree，4 M + 1 未跟踪）——最大悬置风险 |
| 草稿 `s:93a910ec…`（2611.17921） | 已保存并验证（body/topics/pdf 三项 ok），未公开发布 |
| 旧拆分草稿 | 仍在平台草稿箱，待人工清理决策（P1） |
| delivery_registry / 错误码表 / --verify 子命令 / preflight | 未实现（开发计划 M2–M4 待做） |
| 分支分叉规模 | phase1 领先 58 提交 / experiments 领先 34 提交（互不含） |

---

## 二、涉及的代码文件及修改内容

### 2.1 已完成的修改（11-19 修复，待提交）

| 文件路径 | 修改点 | 修改原因 | 状态 |
|---|---|---|---|
| `redbook/infrastructure/xiaohongshu_delivery.py`（+199/−51） | ① OpenCLI 2.x `--session` 参数位置适配；② `{ok,data}` 响应包装解包；③ 话题绑定改为"先读面板→只点真实芯片→去 `#` 前缀→每选一个重开重读"；④ 正文禁止打 `#topic` 字面量；⑤ 会话租约清理（上次中断残留租约指向无关 tab）；⑥ 新增 `_verify_saved_draft()`（IndexedDB 回读 body/topics/pdf），失败删除本次残缺稿 | 对应故障的直接修复：面板状态机缺陷（PF-1/PF-4）、响应包装错配、原生输入不可用（PF-2）、残缺稿无法检测 | ⚠️ 未提交 |
| `redbook/scripts/xhs_drafts.py`（+10） | 草稿列表兼容 OpenCLI 2.x `{ok,data}` 包装 | 与 delivery 同源错配；清点脚本报"0 条草稿"假象 | ⚠️ 未提交 |
| `redbook/tests/test_xiaohongshu_delivery.py`（+76） | 为上述行为补回归测试（13 passed 基线 + 新用例） | 修复无测试即会复发 | ⚠️ 未提交 |
| `redbook/tests/test_cards_and_mcp.py`（+2） | 适配解包后的返回结构 | 同上 | ⚠️ 未提交 |
| `redbook/notes/2611.17921.yaml`（新文件） | 候选话题收敛为页面可提供实体：论文分享/推荐系统/人工智能 | 旧候选含页面无法提供的实体 → `E_TOPIC_UNAVAILABLE` 故障源 | ⚠️ 未跟踪 |

### 2.2 开发计划将创建/修改的文件（M0–M5）

| 文件路径 | 修改内容 | 原因（对应问题编号） |
|---|---|---|
| `redbook/docs/xhs-content-spec.md` | 新增 Platform Facts 章节（PF-1~PF-4）+ 错误码表引用 | A1 防复发 + A6 |
| `redbook/docs/session-audit-template.md`（新） | 审计模板：分支+commit、工具链版本、每命令 exit code、期望 vs 实际 | A7 |
| `config/xhs_content_rules.yaml` | 新增 `toolchain:`（兼容矩阵/orphan_policy/staged 命名规则） | A5/A3/A8 |
| `redbook/infrastructure/delivery_errors.py`（新） | 7 项错误码表（E_PREFLIGHT_BLOCKED 等），DeliveryError 结构化 | A6 |
| `redbook/infrastructure/opencli_runtime.py` | 改造为唯一 `OpenCliClient`（会话+解包+错误码映射）；delivery 与 xhs_drafts.py 改为调用 | R1 去重双实现 |
| `redbook/infrastructure/delivery_registry.py`（新） | run_id↔draft_id↔staged_id 注册表 + reconcile 幂等对账 | A3 |
| `redbook/cli.py` | `--save-draft` 主别名；`note --verify` 子命令（L1 列表+L2 IndexedDB+checkpoint 比对） | A2/A4 |
| `redbook/scripts/stage 包迁移脚本`（新，一次性） | 旧 32hex 目录 → staged_id 全文（64hex）目录 | A8 |
| `redbook/tests/`（多个） | Golden fixtures 契约测试（T1）、PF 回归测试、幂等测试 `test_delivery_idempotent_rerun` | A1/A5 |
| `.agents/skills/xhs-paper-draft/SKILL.md` | 流程描述统一改 `--save-draft`，数值引用 YAML | R2 去重 |

---

## 三、分支开发进度与合并计划

### 3.1 进度现状

- 两分支在 merge-base `5e7590c` 后平行演化：phase1 独有 58 提交（automation 层 `8a615c4`、catalog `4be4ff0`、runbooks、intake）；experiments 独有 34 提交（内容生产统一 `900f446`、后端分层 `cae019f`、日志 JSONL `6059f5b`、ADA 平台等）。
- 投递实现在两分支均为独立版本，且 11-19 修复只存在于 experiments 工作区。

### 3.2 待合并分支与策略

**主决策：experiments 为主干（唯一演化线），不整分支合并 phase1。**
理由：58×34 提交分叉且 phase1 含大量非投递改动（intake/研究资产）；全量合并冲突面与回归风险过大。采用**按能力移植（cherry-pick/port）**：

| 顺序 | 来源 | 内容 | 方式 | 冲突风险 |
|---|---|---|---|---|
| S0 | experiments 工作区 | 11-19 修复（§2.1 五个文件） | **先提交进 experiments**（M-1） | 无 |
| S1 | phase1 `fe336cb` | paper publishing runbooks 文档 | cherry-pick | 低（纯 docs） |
| S2 | phase1 `4be4ff0` | paper_catalog 聚合 + `--skip-pdf-attachment` | cherry-pick，**只取 redbook 部分**（catalog 部分按需） | 中：`redbook/cli.py`、`redbook/services/` 与 experiments `900f446/cae019f` 同文件改动 |
| S3 | phase1 `8a615c4` | automation 层新增文件（daily_discovery/one_click/platform_adapters） | cherry-pick 后**人工裁剪**：新文件可干净落入；与 experiments automation 公共文件（publishing.py 等）冲突时以 experiments 为准，phase1 能力按 M-1.5 移植 | 高：automation 公共文件双方都改 |
| S4 | — | 废弃 phase1 native-input 路径（mjs 两脚本不移植），统一适配层宿主 = `opencli_runtime.py` | 决策项，无需代码合并 | — |

### 3.3 冲突热点清单（合并时逐一处理）

1. `redbook/cli.py`：experiments 重写 note/save-xhs-draft 编排 vs phase1 `--skip-pdf-attachment`、automation 命令注册 → 手工合并，保留 experiments 编排 + phase1 参数。
2. `redbook/infrastructure/xiaohongshu_delivery.py`：两分支完全分叉 → **冲突一律取 experiments（ours）**，phase1 修复点已由 11-19 修复覆盖，不允许合入 phase1 版本。
3. `redbook/automation/publishing.py` 等：双方都改 → 逐 hunk 审查，能力归属按 S3 裁剪规则。
4. `redbook/services/*`：experiments 新增 render_post/xhs_content_gate/note_spec；phase1 无对应改动 → 低风险。
5. `redbook/tests/*`：双方测试基线不同 → 合并后全量重跑 pytest 作为唯一判据。

### 3.4 合并完成判据

- experiments 上 pytest 全绿（含 11-19 新增用例）；`--verify` 对现存草稿 `s:93a910ec…` 回读三项 ok；
- phase1 不再接收投递代码改动（只读归档），spec/SKILL 中所有入口指向 experiments 单线。

---

## 四、验收测试用例清单

| 用例 ID | 覆盖修复点 | 前置条件 | 操作步骤 | 预期结果 |
|---|---|---|---|---|
| TC-01 | PF-3 `{ok,data}` 解包 | experiments worktree，pytest 可用 | 运行 `python -m pytest redbook/tests/test_xiaohongshu_delivery.py -q` | 全部 passed（≥13+新增），无 {ok,data} 相关断言失败 |
| TC-02 | PF-1/PF-4 面板状态机 | 金丝雀 note（`[canary]` 前缀）+ 登录态正常 | 对 canary note 执行 `note <slug> --save-draft`，观察话题绑定阶段日志 | 3 个话题逐一绑定成功；日志显示每次点选后重开面板；无 `E_TOPIC_UNAVAILABLE` |
| TC-03 | 保存后验证（_verify_saved_draft） | TC-02 刚完成，持 draft_id | 执行 `note <slug> --verify --draft-id <id>`（M2 后）/ 现阶段回读命令 | 输出 JSON：`body_ok=true, topics_ok=true, pdf_ok=true, status="passed"`，退出码 0 |
| TC-04 | verify 失败删残缺稿 | 构造失败注入（mock 回读不匹配） | 触发 verify-mismatch 场景 | 本次新建残缺稿被删除；registry 记 orphan；状态 `verify_failed` |
| TC-05 | 幂等对账（A3，M3 后） | registry 已有该 slug 的 `verify_passed` 记录 | 同一 slug 再次 `--save-draft` | 返回**同一 draft_id**，平台草稿箱数量不变（`test_delivery_idempotent_rerun` 绿） |
| TC-06 | `--save-draft` 语义（A2） | — | `--help` 查看；分别执行两别名 | 两别名输出相同结果；help 明示"只存草稿，never publishes" |
| TC-07 | staged 目录命名（A8） | 旧 32hex 暂存包存在 | 跑迁移脚本 → 校验 `data/publish_queue/` | 目录名 = staged_id 64hex 全文；脚本重复执行无差异（幂等） |
| TC-08 | preflight 版本门禁（A5） | 模拟过期扩展（doctor 输出 extensionOutdated=true） | 执行投递入口 | 状态 `blocked`（E_PREFLIGHT_BLOCKED），**无浏览器进程启动** |
| TC-09 | 错误码结构化（A6） | 注入 E_TOPIC_UNAVAILABLE 场景 | 投递中途失败 | 事件/回执含 `error.code` 字段而非仅自由文本 |
| TC-10 | T3 金丝雀全链路（A5） | 版本升级后（如扩展 1.0.27→新版本） | 跑 canary 流程：save-draft → verify → 按 orphan_policy 清理 | 全链路绿；草稿已清理；无残留 |
| TC-11 | 合并回归（§3.4） | S1–S3 合并完成 | experiments 全量 `pytest redbook/tests -q` | 全绿；`--verify` 对现存草稿回读三项 ok |
| TC-12 | PF 回归防线（A1） | Golden fixtures 就位 | 修改适配层模拟"点选后不重开面板" | 对应 PF 回归测试变红，阻止合并 |

执行环境统一约定：experiments worktree；环境变量 `KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1`（如涉 torch 依赖）；测试不触碰公开发布路径。

---

## 五、证据要求（验收通过的依据）

每个 TC 关单时必须附齐以下证据，缺任一项视为未验收：

| 类别 | 具体要求 |
|---|---|
| **测试输出** | pytest 完整尾行（如 `36 passed in 24s`），禁止只报"通过"；TC-09/TC-04 附失败场景的完整回执 JSON |
| **命令日志** | 每条投递/验证命令的 exit code + 关键输出行；JSONL 事件流片段（含 `seq` 单调号与 `p0/verify` 事件） |
| **平台侧证据** | 草稿箱截图（显示正文完整、话题芯片、5 图、PDF 附件）；`--verify` 输出 JSON 原文（body_ok/topics_ok/pdf_ok） |
| **代码提交记录** | 每个修复/合并项的 commit hash（40 hex）+ 涉及文件清单；S1–S3 合并需附 cherry-pick 冲突解决说明（哪些文件取了谁） |
| **registry/审计工件** | `delivery_registry.json` 片段（run_id↔draft_id↔staged_id 对应关系）；按 `session-audit-template.md` 产出的会话审计（含分支+commit、工具链版本、期望 vs 实际） |
| **哈希一致性** | config_hash / split_hash / staged_id 在 parent 验证、快照、manifest 三处一致的比对输出（沿用 ADA 平台口径） |

证据存放约定：验收证据统一归档至 `data/workflow_state/<slug>/acceptance/`（截图、JSON 输出、pytest 日志），并在 registry 对应 run 记录 `evidence_paths`；会话审计文档进 `docs/`，commit hash 必须可回溯。

---

## 六、执行顺序速查（运维/开发人员）

1. **今天**：M-1 提交工作区修复（S0）→ TC-01/TC-03 回归确认；
2. **本周**：M0 契约冻结（spec PF 章节 + 错误码表 + 审计模板 + YAML toolchain）→ M1 OpenCliClient 统一适配层（S1–S3 同步推进 cherry-pick）；
3. **下周**：M2 CLI 固化（--save-draft/--verify/目录迁移）→ M3 registry 幂等（TC-05 为关键验收）；
4. **随后**：M4 preflight 门禁 → M5 端到端 + canary 脚本化；
5. **人工决策项**（非代码）：平台旧拆分草稿的删除/留档（P1），建议在 TC-05 幂等防线就位后执行清理。
