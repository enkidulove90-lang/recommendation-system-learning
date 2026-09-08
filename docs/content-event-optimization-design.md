# 内容事件编排层优化设计（Content Event Orchestration — Optimization）

> 依据：`docs/content-event-orchestration-design.md`（原设计）+ 对 `content_events/` 实际实现的调研审计
> 目标：在不破坏「人工审核优先 / 沙箱安全 / 幂等」前提下，补齐编排层的可恢复性、可观测性与真实发布通路，并接通反馈自优化死代码、接入主流程调度。
> 防幻觉：每项改动标注依据的问题编号（见 §2）与对应原设计章节。

---

## 1. 优化方向总览（回答「有哪些优化方向」）

按杠杆排序，覆盖「设计有代码缺」+「实现脆弱」两类：

| # | 方向 | 解决的核心痛点 | 依据 |
|---|---|---|---|
| O1 | **幂等跨目录强制** | 同 `idem_key` 落在不同 `publish_queue/<dir>` 会重复 stage/publish | 原设计 §2.3；问题 A5 |
| O2 | **状态/事件持久化原子化+韧性** | `state.json` 非原子写会写半截；`events.jsonl` 一行损坏中断迭代 | 问题 B2/B3 |
| O3 | **瞬时失败重试+退避+可恢复** | 无重试，瞬时抖动直接转 `needs_review`，无 resume | 问题 B1 |
| O4 | **真实发布守卫修正** | `_GuardedRedbookPublisher.stage` 无条件抛错，真实 WeChat/XHS 永远不 stage | 问题 A3 |
| O5 | **未知平台显式占位+告警** | notion/blog 静默回退 DryRun，无本地包/无告警 | 问题 A4 |
| O6 | **可观测性（日志+运行摘要+计数器）** | 仅 `print(json)`，失败静默，无结构化日志/指标 | 问题 B4 |
| O7 | **CLI 健壮性** | `status` 无 `--paper-id`；空队列/坏 JSON 直接崩 | 问题 A6/B5 |
| O8 | **反馈闭环自优化接通** | `compute_metrics/bayes/ucb` 是死代码，`DECISION_MADE/FEEDBACK_SAMPLED` 从未发 | 问题 A2 |
| O9 | **主流程集成 + 调度** | `run_batch_pipeline.py`/自动化零引用，编排层孤立 | 问题 D1 |
| O10 | **生命周期事件补齐** | `RENDER_REQUEST` 已定义从未发 | 问题 A1 |
| O11 | **测试补全** | publishers/orchestrator/cli/needs_review/自优化集成零覆盖 | 问题 C |

本轮聚焦 **O1–O8 + O10 + O11**（核心、可验证）；**O9** 做最小集成钩子 + 调度文档；**D2**（content_factory 侧车目录不一致）在 §4.8 给出容忍解析器，不破坏既有契约。

---

## 2. 问题总结（针对当前 content_events 提案/实现）

审计基于实际代码（file:line 为调研时快照，实现时将二次核对）。

### A. 与设计文档不符 / 桩 / 待实现
- **A1** `schema.py` 定义 `RENDER_REQUEST` 事件，但 `queue_processor` 全程未发出（原设计 §2.1）。
- **A2** `feedback_collector.py:65-134` 的 `compute_metrics / qs7_for_posts / bayes_group_lift / ucb_slot` 是**死代码**：`collect_once`(139-163) 与 `orchestrator.collect_feedback` 从不调用；`DECISION_MADE`/`FEEDBACK_SAMPLED` 从未发出；`decisions` 表(40-48)永不写入（原设计 §6 自优化未落地）。
- **A3** `publishers.py:114-142` `_GuardedRedbookPublisher.stage` **无条件**抛 `PublishingError`（即使真实 delivery 类导入成功）→ 真实 WeChat/XHS 永远不被 stage，无论是否登录/approved。
- **A4** `publishers.py:168` 未知平台（notion/blog）**静默**回退 `DryRunPublisher`，无占位本地包、无告警（原设计 §5 标【待实现】本地包）。
- **A5** `queue_processor.py:98-101` 幂等仅依赖 per-dir `state.json`，无原设计 §2.3 的全局「幂等表」；两个不同目录同 `idem_key` 不会去重。
- **A6** `cli.py:63-65` `status` 子命令**不支持** `--paper-id`（原设计 §7 列了 `--paper-id`，argparse 未定义）。

### B. 运维弱点（重试/幂等/可观测/错误）
- **B1** 无任何重试/退避；瞬时失败仅转 `needs_review` 返回（`queue_processor.py:110-116`），无 resume，无 backoff。
- **B2** `queue_processor.py:79-81` `_save_state` 直接 `json.dump` 写 `state.json`，**非原子**（无 temp+rename）；崩溃可写半截。解析失败在 `:74` 被 `except Exception: return None` 吞掉 → 下次重跑可能重复处理。
- **B3** `event_log.py:32-35` 追加不 `fsync`；`iter()`(44-45) 只捕获 `OSError` 不捕获 `JSONDecodeError` → 一行损坏的 JSON 会让迭代器抛异常中断。
- **B4** `cli.py:26` 可观测性仅 `print(json.dumps(...))`：无结构化日志、无计数器、无 run-summary、无 metrics。
- **B5** 宽异常吞掉：`publishers.py:107`（import 失败→静默 `None`）、`queue_processor.py:74`、`event_log.py:29/49`、`feedback_collector.py:162`（采集失败仅返回 dict）。
- **正向**：DryRun 默认（`cli.py:55`、`queue_processor.py:134`）确保沙箱不会误触真实平台（保留）。

### C. 测试覆盖缺口
- 已覆盖：schema、state_machine、event_log、queue_processor(渲染+stage+幂等)、feedback_collector(指标+sqlite)。
- 缺：`publishers.py`（DryRun/stage/守卫回退/make_publisher 回退）、`orchestrator.py`、`cli.py`（空队列/坏 json/参数）、`queue_processor` 的 `needs_review` 分支、反馈自优化与 `collect_once` 的集成（自优化函数从未被调用）。

### D. 集成/编排缺口
- **D1** `run_batch_pipeline.py`、`main.py` 及全仓对 `content_events`/`process_queue`/`orchestrator` 零引用（grep 确认）；无任何自动化驱动 `process-queue`。
- **D2** `content_factory/factory.py:46` 写 `publish_queue/<content_hash[:32]>/<platform>.json`(`review_status=pending`)，而 `factory.py:194` 把 viz/interaction 等侧车写到 `publish_queue/<paper_id_hash[:32]>/`（**不同目录**）→ 侧车不与平台包同目录，编排层取不到。
- **D3** 真实 delivery 类签名不匹配：`wechat_delivery.py:134`/`xiaohongshu_delivery.py:110` 的 `validate(self)` 无 `package` 参数，与 `Publisher.validate(package)` 协议不符（当前因 A3 先抛错而未触发，属隐患）。
- **D4** `publishers.py:101-108` 延迟 import redbook delivery 用裸 `except Exception: return None` → 导入失败静默降级，难排查。
- **正向**：`__init__.py` 完整、无循环导入、cli 自加 `ROOT` 到 `sys.path`（保留）。

---

## 3. 目标与原则

1. **人工审核优先**：默认只 `stage`（或 DryRun 本地包），定时任务绝不自动 `publish`（继承原设计 §8）。
2. **幂等 + 可恢复**：同 `idem_key` 跨目录只处理一次；中途崩溃可安全重跑。
3. **韧性**：持久化原子写、损坏事件跳过不中断、瞬时失败可重试。
4. **沙箱安全**：`dry_run=True` 默认；真实 stage 仅在 `dry_run=False` 且 delivery 类可用且 `review_status=approved` 时触发。
5. **可观测**：结构化日志 + 每次运行摘要（scanned/processed/skipped/needs_review/published/errors）。
6. **增量兼容**：不改 `content_factory` 的 `PublicationPackage` 契约；编排层仅增强。

---

## 4. 详细设计（分模块解决方案）

### 4.1 幂等注册表（O1 / A5）
- 新增全局幂等表 `data/content_events/idem_registry.jsonl`（追加写，每行 `{idem_key, state, ts, paper_id, platform}`）。
- `process_item`：算 `idem_key = schema.idem_key(item)`；若注册表中该 key 已处于 `STAGED/PUBLISHED` 终态 → 跳过并计 `skipped_idempotent`；本运行内用 `set` 去重。
- 进入 `STAGED/PUBLISHED` 时追加一行（与 state 落盘同事务语义：先写注册表再推进）。

### 4.2 原子 + 韧性持久化（O2 / B2 / B3）
- `queue_processor._save_state`：写 `state.json.tmp` → `os.replace` 原子替换。
- `event_log.append`：`flush()` + `os.fsync(fileno())`（至少 flush；fsync 可配置）。
- `event_log.iter`：逐行 `json.loads` 包 `try/except (JSONDecodeError, ValueError)` → 损坏行 `logger.warning` 后 `continue`，不中断。

### 4.3 重试 / 退避（O3 / B1）
- 新增 `content_events/retry.py`：`RetryPolicy(max_attempts, backoff_base=1.0, backoff_cap=30.0, transient=(ConnectionError, Timeout, OSError...))` + `retry_call(fn, policy)`。
- `queue_processor` 对 **render** 与 **stage** 调用套重试；校验类（VALIDATED 失败）属永久错误，直接 `needs_review` 不重试。
- `state.json` 记录 `attempts`，重跑时续跑（已达上限则跳过重试直接 `needs_review`）。

### 4.4 发布守卫修正（O4 / A3 / D3 / D4）
- `_GuardedRedbookPublisher.__init__(platform, real_cls=None, dry_run=True)`。
- `stage(package)`：
  - 若 `dry_run` 或 `real_cls is None` → 走 DryRun 本地包（保持沙箱安全）。
  - 否则调用 `real_cls().stage(package)`（真实草稿创建），异常 → `PublishingError` → `needs_review`。
- `validate(package)` 调整：若真实类 `validate` 签名无 `package`（D3），用 `inspect` 适配（无参则 `real.validate()`，有参则 `real.validate(package)`）。
- 延迟 import 改为捕获**具体**异常（`ImportError`/`AttributeError`）并 `logger.warning`，非裸 `except Exception`。
- 真实 delivery 调用统一走 `make_publisher(platform, dry_run=<flag>)`。

### 4.5 未知平台显式占位（O5 / A4）
- `make_publisher` 对未知平台返回 `PlaceholderPublisher`：写 `data/publish_results/<platform>/placeholder_<hash>.json` 本地占位包 + `logger.warning("unknown platform → placeholder")`，不再静默 DryRun。

### 4.6 可观测性（O6 / B4）
- 各模块统一 `logger = logging.getLogger(__name__)`（替代 `print`）。
- `orchestrator.run_once` 累积 `RunSummary`（dataclass：`scanned, processed, skipped_idempotent, skipped_other, needs_review, published, errors`）。
- `cli` 结束打印 `RunSummary` 的 JSON + 人类可读摘要；非 0 错误计 `errors>0` 时退出码 1（部分失败），全空队列退出码 0。

### 4.7 生命周期事件补齐（O10 / A1）
- `process_item` 在 render 前显式 `emit(RENDER_REQUEST)`，render 后 `emit(RENDERED)`；保持 `VALIDATED/STAGED/NEEDS_REVIEW` 既有发射。

### 4.8 反馈自优化接通（O8 / A2）
- `feedback_collector.collect_once` 在写入 `metric_snapshots` 后：
  1. 调 `compute_metrics` 算 ER/SR/FLR/DDR/FR/QS7（按 post）；
  2. 调 `bayes_group_lift` + `ucb_slot` 产出自优化决策（变化 `±0.05`，7 天一次，可回滚，继承原设计 §6）；
  3. 写 `decisions` 表一行；
  4. `emit(FEEDBACK_SAMPLED)` + `emit(DECISION_MADE)`（事件流）。
- 保持**只读**（不点赞/评论/关注/删帖），仅影响「下一批草稿候选队列」（不绕过人工审核）。

### 4.9 集成与调度（O9 / D1 / D2）
- **最小集成钩子**：`run_batch_pipeline.py` 新增可选 `--step content-events`（try/except 包裹，`content_events.orchestrator.run_once(root, publisher="dryrun")`），失败不阻断前序步骤。
- **调度文档**：`content_events/scheduler.md` + 示例 `.github/workflows/content-events.yml`（每小时 `process-queue` + 每日 `collect-feedback`），与 `paper_monitor` 同范式。
- **D2 容忍解析**：`queue_processor` 增加 `resolve_sidecars(paper_id)` —— 在 `publish_queue/` 下按 `paper_id` 扫描兄弟目录，聚合 viz/interaction 侧车路径，避免目录命名不一致导致取不到。

### 4.10 测试补全（O11 / C）
- 新增 `tests/test_publishers.py`：DryRun/stage/守卫回退/make_publisher 回退/未知平台占位。
- 新增 `tests/test_orchestrator.py`：run_once 聚合 RunSummary、dryrun 端到端。
- 扩展 `tests/test_content_events.py` 或新增 `test_cli.py`：空队列、坏 JSON、参数、`--paper-id`、`needs_review` 分支、幂等跨目录、事件日志损坏跳过。
- 新增 `tests/test_feedback_opt.py`：collect_once 接通后发 FEEDBACK_SAMPLED/DECISION_MADE、写 decisions。

---

## 5. 实施计划

### Phase 1（本轮交付，可验证）
1. `retry.py` 新增 RetryPolicy + retry_call。
2. `event_log.py`：fsync + 损坏行容忍迭代。
3. `queue_processor.py`：幂等注册表(O1) + 原子 state(O2) + 重试(O3) + RENDER_REQUEST(O10) + 坏 JSON/空队列处理 + RunSummary 累积。
4. `publishers.py`：守卫修正(O4) + 未知平台占位(O5) + 具体异常日志(D4) + validate 签名适配(D3)。
5. `schema.py`：必要时补 `RunSummary`（或放 orchestrator）。
6. `orchestrator.py`：RunSummary 聚合 + 传 dry_run + 接通反馈自优化(O8)。
7. `feedback_collector.py`：collect_once 接通 compute_metrics/bayes/ucb + 事件(O8)。
8. `cli.py`：`--paper-id`(A6) + 健壮性(O7) + 结构化输出。
9. `run_batch_pipeline.py`：`--step content-events` 钩子。
10. 测试：publishers/orchestrator/cli/feedback_opt/idempotency/event_log。
11. 验证：`python -m unittest content_events.tests` 全绿；用现有 `publish_queue/` 一个 item 跑 `process-queue --publisher dryrun` 确认无回归 + RunSummary 打印。

### Phase 2（后续，本文档标注）
- `scheduler.md` + GitHub Action 实际接入（O9 深化）。
- D2 侧车目录命名在 `content_factory` 侧对齐（消除容忍解析器的必要性）。
- 真实 WeChat/XHS `stage` 端到端验证（需登录态，沙箱外）。

---

## 6. 安全边界（继承并强化原设计 §8）
1. 任何平台默认只 `stage`/DryRun，定时任务不 `publish`。
2. 网络/登录/审核失败 → `needs_review`，不自动重试（仅瞬时错误重试，永久错误直转）。
3. 反馈采集只读，不点赞/评论/关注/删帖。
4. 幂等键防重复发；状态机不随意跳变；注册表与 state 同语义落盘。
