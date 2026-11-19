# 小红书投递链路编排层开发计划 v2（M0–M5 + A5）

> 日期：2026-11-19
> 基线：主工作区 detached HEAD `0d8dd49`；前置评估见 `docs/system_design_assessment_redbook_2026-11-19.md`（"两头强、中间薄"）。
> 输入：编排层设计稿（任务模型/队列/错误码/注册表/限流/收件箱方案），本文将其落成可执行计划。
> 定位：**不重写内容端与适配器**，在其上补编排层。与既有 `xhs_delivery_backend_devplan_2026-11-19.md` 的 M0-M5 对齐（M2=错误码、M3=注册表，锚点一致；阶段名如原文有差异仅重命名，依赖关系不变）。

---

## 〇、总则

### 0.1 目标
在低运维约束下（SQLite + 本地 worker + 文件系统，无 Redis/Kafka/常驻微服务），实现：
多草稿并行生成 → 账号级串行保存 → 投递注册表对账 → 统一错误分拣 → 收件箱为事实源 + 通知只做提醒。

### 0.2 非目标
- 不改 `redbook/services/` 内容生产端（note_spec/content_spec/cards）。
- 不改两个适配器的平台交互逻辑本身（选择器/验证/回滚），只包一层领域异常映射。
- 不做 Web UI（收件箱先做目录 + CLI 视图）。

### 0.3 六条铁律（贯穿全部里程碑，验收时逐条检查）
1. **注册表始终只有一个事实源**：M3 迁移验收前，单进程投递以
   `data/workflow_state/<slug>/delivery_registry.json` 为唯一事实源；M3 迁移验收后，
   `data/state/orchestration.sqlite`（WAL）承担队列 + 投递注册表。迁移期间禁止双写；
   JSONL 仅审计。
2. **保存先登记**：保存前写 `SAVING` intent，保存成功立即写 `SAVED_UNVERIFIED`，再验证。
3. **验证不确定不删除**：新增 `E_VERIFY_UNCERTAIN` → 待对账；只有确认 `E_VERIFY_MISMATCH` 才回滚（修改现 `xiaohongshu_delivery.py` L674-681 的"不过即删"硬行为）。
4. **通知只提醒不替事实**：收件箱先于通知；成功静默。
5. **账号级串行保存、任务独立 session**：保存并发=1/账号；每任务 session 带 `job_id` 前缀，只清理自己的。
6. **未知异常默认人工**：任何未映射错误 → `E_UNKNOWN_MANUAL` 进收件箱。

### 0.4 新增代码组织

```text
redbook/orchestration/            # 新包，全部新建
  __init__.py
  models.py        # Job/Attempt/Receipt schema（dataclass）+ 状态机枚举 + 合法迁移表
  errors.py        # E_* 错误码表 + 领域异常层级 + 映射函数 + exit code 映射
  store.py         # SQLite 连接管理（WAL/事务/CAS 状态迁移）、schema DDL、lease
  queue.py         # 入队/领取(lease+心跳)/完成/失败/重试/取消
  registry.py      # 投递注册表读写 + SAVING/SAVED_UNVERIFIED intent + 唯一约束
  reconcile.py     # 对账 job：SAVING 扫描、草稿箱对照、MISSING 处理
  worker.py        # 单进程 worker 骨架（生成池 + 保存信号量）
  inbox.py         # data/inbox/manual/ 聚合 + CLI 视图
  notify.py        # outbox + 聚合/静默/去重（M5）
redbook/tests/orchestration/      # 每里程碑对应测试文件
```

**修改的既有文件**（最小侵入）：
- `redbook/cli.py`：新增 `orchestrate` 子命令组；回执 envelope 替换 stdout JSON。
- `redbook/infrastructure/xiaohongshu_delivery.py`：异常改为领域异常；"验证不过即删"改为按错误码分拣（铁律 3）；session 参数化。
- `redbook/infrastructure/wechat_delivery.py`：同上（仅异常映射层）。
- `redbook/application/paper_workflow.py`：checkpoint 增加 `run_id` 关联字段（向后兼容旧 checkpoint）。
- `redbook/infrastructure/run_log.py`：事件增加 `job_id/trace_id/step`；按日文件选项。

---

## 一、里程碑总览与依赖

| 阶段 | 名称 | 优先级 | 预估工作量 | 依赖 |
|---|---|---|---|---|
| M0 | 基线冻结与编排契约 | P0 | 2–3 天 | 无 |
| M1 | 任务队列与可观测骨架 | P0 | 3–4 天 | M0 |
| M2 | 错误码与处置策略 | P1 | 2–3 天 | M0（可与 M1 并行） |
| M3 | 投递注册表与对账 | P1 | 3–4 天 | M0、M2 |
| M4 | 并发调度与账号级限流 | P1 | 4–5 天 | M1+M2+M3 |
| M5 | 通知与人工收件箱 | P2 | 3 天 | M2/M3/M4 |
| A5 | 版本兼容矩阵 | P2 | 与 M4/M5 并行 | M0 |

关键路径：**M0 → M2 → M3 → M4 → M5**（M1 可与 M2 并行插队）。

```text
M0 ─┬→ M1 队列/可观测
    ├→ M2 错误码 ──→ M3 注册表 ──→ M4 并发/限流 ──→ M5 通知/收件箱
    └→ A5 兼容矩阵（契约测试依赖 M0，可与 M4/M5 并行）
```

---

## 二、逐里程碑实施计划

### M0 基线冻结与编排契约（2–3 天）

**任务**：
1. `orchestration/models.py`：`Job`（job_id, run_id, staged_id, content_hash, platform, account, payload_ref）、`Attempt`（attempt_no, started_at, trace_id）、`Receipt`（job_id, state, code, retryable, next_step, evidence_ref）dataclass。
2. 状态机：`QUEUED → RUNNING → GENERATED → SAVING → SAVED_UNVERIFIED → VERIFIED / MANUAL / FAILED_RETRYABLE / FAILED_TERMINAL`；合法迁移表写成常量 `ALLOWED_TRANSITIONS`，禁止回退，人工重置走显式 `reset` API（记录审计事件）。
3. 幂等键规范冻结：唯一键 `(platform, account, staged_id)`；staged_id 复用现有 `content_hash[:32]`（`publishing.py` L80-86，不改算法）。
4. 死代码处置：`infrastructure/publishing/scheduler.py` + `strategy.py` 模块级 docstring 标注 `DEPRECATED — M4 接线或删除`；`test_automation.py` 中对应单测移入 `@pytest.mark.legacy`。
5. 现有回执 envelope 占位：`cli.py` note/save-xhs-draft 回执加 `job_id/state/code/retryable` 空字段（向后兼容，消费方按"字段存在即新格式"判断）。

**涉及文件**：新建 `models.py`；改 `cli.py`、`publishing/scheduler.py`、`publishing/strategy.py`。

**验收（TC-M0-01~04）**：
- TC-M0-01：`Job/Attempt/Receipt` 单测覆盖序列化/反序列化（`tests/orchestration/test_models.py`）。
- TC-M0-02：非法状态迁移（如 `VERIFIED → SAVING`）被拒并抛 `InvalidTransition`。
- TC-M0-03：旧 checkpoint（无 run_id 字段）加载不报错，新字段缺省补齐。
- TC-M0-04：现有 XHS/WeChat 端到端脚本（`validate_wechat_real_paper.py`、`smoke_test.py`）不回归。

---

### M1 任务队列与可观测骨架（3–4 天，可与 M2 并行）

**任务**：
1. `store.py`：SQLite 打开策略（`PRAGMA journal_mode=WAL`、`busy_timeout`）、事务上下文、状态 CAS 迁移（`UPDATE ... WHERE state=:expected`，受影响行数=0 即迁移冲突）。DDL：
```sql
CREATE TABLE jobs (
  job_id TEXT PRIMARY KEY,
  run_id TEXT, staged_id TEXT, content_hash TEXT,
  platform TEXT NOT NULL, account TEXT NOT NULL,
  payload_ref TEXT,          -- 只存引用/哈希，不存正文（脱敏铁律）
  state TEXT NOT NULL,
  attempt INTEGER DEFAULT 0,
  created_at TEXT, updated_at TEXT
);
CREATE UNIQUE INDEX uq_staged ON jobs(platform, account, staged_id);
CREATE TABLE job_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT, trace_id TEXT, step TEXT,
  level TEXT, message TEXT, created_at TEXT
);
CREATE TABLE leases (
  resource TEXT PRIMARY KEY,   -- 如 "save:xhs:account_a" / "session:<job_id>"
  owner TEXT, heartbeat_at TEXT, expires_at TEXT
);
```
2. `queue.py`：enqueue（幂等：唯一冲突返回已有 job）、claim（SQLite lease：`INSERT OR REPLACE` + 过期判定）、heartbeat、complete/fail（重试计数）、cancel（写 `cancel_requested`，worker 步骤间检查）。
3. `worker.py`：单进程 worker，`--once` / `--drain` / 常驻三种模式；启动时扫描 `SAVING/SAVED_UNVERIFIED` 触发对账（M3 完成前先空跑）。
4. 可观测：`run_log.py` 事件带 `job_id/trace_id/step`；新增 `runs.jsonl` 按日文件选项（`data/logs/runs-YYYYMMDD.jsonl`）+ 容量告警钩子；`orchestrate status` 输出队列深度/失败率/验证失败率/回滚失败率。
5. 收件箱雏形：`data/inbox/manual/` 目录 + `inbox.py` 聚合 `manual_review_required`、HTML preview（`data/publish_preview/`）、失败任务，`orchestrate inbox` 列表视图。

**验收（TC-M1-01~05）**：
- TC-M1-01：入队 → claim → 心跳 → 完成，进程重启后任务从上次状态恢复。
- TC-M1-02：两个进程同时 claim 同一任务，仅一个成功（lease 互斥）。
- TC-M1-03：心跳超时的 lease 被其他 worker 回收（僵尸任务恢复）。
- TC-M1-04：单 worker 串行跑通现有 XHS/WeChat 流程（真机 smoke）。
- TC-M1-05：`orchestrate status` 各指标非空且与实际任务数一致。

---

### M2 错误码与处置策略（2–3 天）

**任务**：
1. `errors.py` 错误码表（版本化 `ERROR_CODE_TABLE_VERSION = 1`）：

| 码 | 语义 | retryable | next_step | owner |
|---|---|---|---|---|
| `E_VALIDATION` | 内容规格校验失败 | false | 修复 note_spec 后重新 validate | author |
| `E_AUTH` | 登录态失效 | true | 运行 `scripts/login_qr.py` 扫码后重试 | human |
| `E_PLATFORM_TRANSIENT` | 平台瞬时错误（超时/网络） | true | 自动重试 ≤N 次 | system |
| `E_TOPIC_TERMINAL` | 话题无实体（终态） | false | 人工改话题后重跑 | author |
| `E_VERIFY_UNCERTAIN` | 验证不确定（读回失败/平台延迟） | true | 进对账 job，**不删除** | system |
| `E_VERIFY_MISMATCH` | 验证确认不匹配 | false | 回滚（删草稿） | system |
| `E_ROLLBACK_FAILED` | 回滚删除失败 | true | 进人工收件箱，附 draft_id | human |
| `E_REGISTRY_CONFLICT` | staged_id 已登记 | false | 返回已有回执（幂等命中） | system |
| `E_MANUAL_REQUIRED` | 兜底（HTML 预览等） | false | 人工上传后标记完成 | human |
| `E_UNKNOWN_MANUAL` | 未映射异常兜底 | false | 进收件箱附原始摘要 | human |

2. 领域异常层级：`OrchestrationError` 基类；`DeliveryError`、`TopicEntityUnavailable` 收编为子类；适配器 `except Exception` 末层统一 `to_error_code()` 映射，未知 → `E_UNKNOWN_MANUAL`（保留原始异常摘要，脱敏后存 evidence）。
3. 统一回执 envelope：`{ok, job_id, state, code, message, retryable, next_step, owner, evidence_ref}`；message 脱敏（剥路径/正文/账号名）。
4. CLI exit code 映射：0=成功，2=人工类（manual/terminal），3=可重试类（与现有"失败 `SystemExit(2)`"兼容：人工类维持 2）。
5. 行为变更（唯一一处改适配器语义）：`xiaohongshu_delivery.py` 验证失败路径——读回重试 3 次（间隔递增）→ 仍失败抛 `E_VERIFY_UNCERTAIN`（不删）→ 对账确认 mismatch 后才删 → 删除失败抛 `E_ROLLBACK_FAILED`。

**验收（TC-M2-01~04）**：
- TC-M2-01：`tests/orchestration/test_errors.py` — 每个已知异常类型映射到正确码/策略（表驱动）。
- TC-M2-02：模拟"验证读回失败"：草稿**不被删除**，状态 `E_VERIFY_UNCERTAIN` 进对账。
- TC-M2-03：模拟"确认 mismatch + 删除失败"：`E_ROLLBACK_FAILED` 进收件箱，附 draft_id。
- TC-M2-04：抽查 20 个失败场景（人工构造），分拣正确率 100%。

---

### M3 投递注册表与对账（3–4 天）

**任务**：
1. 迁移边界：M3 开始时以每 slug JSON registry 为唯一在线事实源；迁移程序在单一
   SQLite 事务中导入其 `verified` / `orphan` 记录并写迁移标记。只有
   TC-M3-01~06 全部通过后，SQLite 才接管在线事实源；旧 JSON 保留只读审计，禁止双写。
2. `registry.py` DDL：
```sql
CREATE TABLE deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  staged_id TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  platform TEXT NOT NULL, account TEXT NOT NULL,
  draft_id TEXT,
  state TEXT NOT NULL,          -- SAVING/SAVED_UNVERIFIED/VERIFIED/MISSING/ROLLED_BACK/MANUAL
  attempt INTEGER NOT NULL DEFAULT 1,
  last_code TEXT,               -- 最后一次错误码（可空）
  evidence TEXT,                -- JSON：对账证据引用（快照路径/哈希），不存正文
  created_at TEXT, updated_at TEXT
);
CREATE UNIQUE INDEX uq_delivery ON deliveries(platform, account, staged_id);
```
3. 投递协议改造（`xiaohongshu_delivery.py` / `wechat_delivery.py` 的调用方，即 `paper_to_xhs.py` / `paper_to_wechat.py`）：
   - 保存前 `INSERT state=SAVING`（intent，含 attempt）；
   - 保存成功立即 `UPDATE state=SAVED_UNVERIFIED, draft_id=...`；
   - 验证通过 → `VERIFIED`；`E_VERIFY_UNCERTAIN` → 保持 SAVED_UNVERIFIED 等对账；回滚成功 → `ROLLED_BACK`。
4. 幂等重跑：任何投递动作前查注册表，`SAVED_UNVERIFIED/VERIFIED` 直接返回已有回执（`E_REGISTRY_CONFLICT` 语义=幂等命中，非错误）。
5. `reconcile.py` 对账 job：
   - 启动扫描：`SAVING` 超时未更新 → 查草稿箱 API 找同内容草稿 → 找到补 draft_id / 找不到标 `MANUAL`；
   - 周期对账：注册表 VERIFIED 项与草稿箱 API 对照，平台侧消失 → `MISSING` → 进收件箱（可重跑）；
   - `E_VERIFY_UNCERTAIN` 队列：重试读回 → 确认 mismatch 才删。
6. checkpoint 关联：`paper_workflow.py` checkpoint 增加 `run_id` 引用（注册表为事实源，checkpoint 只挂引用）。

**验收（TC-M3-01~06）**：
- TC-M3-01：重跑同一 `(platform, account, staged_id)` 返回已有回执，平台草稿数不变（幂等命中）。
- TC-M3-02：模拟"保存成功后进程崩溃"→ 启动对账找回 draft_id 或标 MANUAL，不重复保存。
- TC-M3-03：模拟平台清理草稿 → 对账标 `MISSING` 进收件箱。
- TC-M3-04：双进程并发写注册表（WAL + 唯一索引），无丢更新/重复行。
- TC-M3-05：`E_VERIFY_UNCERTAIN` → 对账确认 mismatch → 删除 → `ROLLED_BACK` 全链路。
- TC-M3-06：注册表无正文/路径字段（脱敏审计）。

---

### M4 并发调度与账号级限流（4–5 天）

**任务**：
1. 两阶段调度：`GENERATED`（生成，可 N 并行）与 `SAVING`（保存，账号级信号量=1）分离；保存 lease 资源名 `save:<platform>:<account>`。
2. 独立 session：适配器打开会话时 session 标识带 `job_id` 前缀；结束只清理自己的 session（修改现适配器"打开前 `browser close`"的固定行为——改为"关闭自己的 session"）。
3. worker 池：生成 worker N（默认 2，可配）；保存 worker 按账号=1、跨平台可并行；配置集中 `redbook/config/orchestration.yaml`（含每平台能力矩阵：`max_save_concurrency`、`supports_verify`、`supports_pdf`）。
4. 平台能力矩阵驱动调度：WeChat `supports_verify=false` → 保存后只做保存灯检查（现状），不排对账强校验。
5. 取消/超时/僵尸：步骤间检查 `cancel_requested`；步骤级超时复用现有 `OPENCLI_BROWSER_COMMAND_TIMEOUT` 预算；lease 过期即回收；失败任务标记后立即释放资源不阻塞队列。
6. scheduler/strategy 死代码二选一收口：M4 接线（作为"固定时段保存"策略）或正式删除——**默认删除**（YAGNI，接线收益不明确）。

**验收（TC-M4-01~06）**：
- TC-M4-01：同一账号并发提交 10 任务 → 保存严格串行（注册表时间戳单调），无 session 互关。
- TC-M4-02：不同账号任务可并行，互不等待。
- TC-M4-03：每任务 session 独立创建/清理，任务结束后无残留 session。
- TC-M4-04：kill 保存中 worker → lease 过期 → 其他 worker 接管，不重复保存（依赖 M3 intent）。
- TC-M4-05：取消任务在步骤间生效；失败任务不阻塞后续队列。
- TC-M4-06：平台能力矩阵变更（如 XHS `max_save_concurrency=2`）无需改代码即生效。

---

### M5 通知与人工收件箱（3 天）

**任务**：
1. 收件箱为事实源：`data/inbox/manual/` 统一聚合待人工/可重试/待对账/回滚失败/HTML 预览/扫码重登六类，条目含 `job_id/code/next_step/evidence 链接`；`orchestrate inbox --json` 机读视图。
2. 通知 outbox 表（复用 M1 store）：
```sql
CREATE TABLE notify_outbox (
  event_id TEXT PRIMARY KEY,       -- 幂等去重
  kind TEXT,                       -- manual_needed / batch_summary / consecutive_failures
  payload TEXT,                    -- 只含 job_id/平台/错误码/计数/收件箱链接
  created_at TEXT, sent_at TEXT, status TEXT
);
```
3. 聚合策略：成功静默；批次结束发 ≤1 条汇总 + 需人工项；连续失败 ≥3 才升级；静默时段可配。
4. 渠道（自用低运维优先级）：本地收件箱视图（默认）→ 桌面通知（可选）→ webhook（可选）；邮件不做。
5. 人工接管：收件箱条目附一键命令（`orchestrate retry <job_id>` / `orchestrate open <job_id>` 打开草稿或 HTML 预览 / `orchestrate resolve <job_id> --done`）；人工处理后状态闭环。
6. 内容脱敏红线：通知 payload 只含 job_id/平台/错误码/计数/链接，**不含标题/正文/路径**。

**验收（TC-M5-01~04）**：
- TC-M5-01：模拟 50 任务批次（48 成功 2 失败）→ 通知 ≤1 条汇总 + 2 条需人工，无风暴。
- TC-M5-02：outbox 幂等：同 event 重投不重复发送；通知渠道失败不阻塞主流程。
- TC-M5-03：收件箱与注册表状态一致（以收件箱条目抽查注册表，100% 对得上）。
- TC-M5-04：`orchestrate retry/open/resolve` 三命令闭环人工处理。

---

### A5 版本兼容矩阵（与 M4/M5 并行）

**任务**：选择器/文案/IndexedDB schema 版本化注册表（`redbook/config/platform_contracts.yaml`）；适配器读注册表而非硬编码；契约测试（`test_platform_contracts.py`）覆盖 XHS/WeChat；三层试验（T1 fixture / T2 只读探针 / T3 真机 smoke）作为手动 gate 脚本；灰度开关 + 回退路径。

**验收**：平台改版模拟（改注册表中关键选择器）→ 契约测试失败并给出降级提示；T1/T2 在无登录环境下可跑，T3 显式确认后才执行。

---

## 三、总体排期与风险

### 3.1 排期建议（按关键路径，约 3 周）
- 第 1 周：M0 → M2（M2 与 M1 前半并行）
- 第 2 周：M1 收尾 → M3
- 第 3 周：M4 → M5；A5 穿插推进

### 3.2 主要风险与对策

| 风险 | 对策 |
|---|---|
| 改"验证不过即删"引入新风险（废草稿堆积） | `E_VERIFY_UNCERTAIN` 由对账 job 定期清理 + 收件箱可手动处理；删除动作只收窄不放开 |
| SQLite 并发写锁竞争（多 worker） | WAL + busy_timeout + 短事务；保存本就账号级串行，竞争面小 |
| 适配器侵入过深导致回归 | M2/M3 只改异常边界与调用方协议，平台交互逻辑不动；每里程碑跑真机 smoke 作为回归门 |
| 旧 checkpoint / 旧回执格式兼容 | 字段缺省补齐 + "字段存在即新格式"判定；`test_note_migration.py` 同款思路加 `test_checkpoint_compat.py` |
| 真机验收依赖登录态 | 验收用例分层：T1 纯单测（沙箱可跑）→ T2 只读探针 → T3 显式确认真机；pytest basetemp 沿用 `.pytest_tmp/` 约定 |

### 3.3 决策记录
- 注册表事实源分阶段切换：当前单进程交付阶段维持 per-slug
  `delivery_registry.json`；M3 通过迁移验收后切换为 SQLite。两者不得双写，JSON
  在切换后只作只读审计。
- scheduler/strategy 死代码默认**删除**（M4 时执行），不留 deprecated 长尾。
- exit code：人工类维持 2（兼容现状），可重试类新增 3。
- 错误码表版本从 1 起，映射漂移靠契约测试拦截。
- 注册表路线裁定已由 `9fec8b8` 落档并在 `eaf0e11`、`4daf1e9`、`06b80ca` 执行：在线
  事实源已从 per-slug JSON 切换为 SQLite，JSON 仅保留为一次性迁移输入和只读审计。M3
  余项是平台/账号维度的对账策略扩展与 WeChat 校验增强；不得恢复双写。

---

## 四、里程碑完成定义（统一 DoD）

每个里程碑合并前必须满足：
1. 对应 TC-* 用例全部通过；T1 单测在沙箱环境可跑（无需登录）。
2. 真机 smoke（XHS 存草稿 + WeChat 存草稿）不回归。
3. 铁律六条逐条自查（代码评审 checklist）。
4. 注册表/日志无正文、路径、账号明文（脱敏审计）。
5. `orchestrate status` 指标覆盖该里程碑新增状态。
