# 小红书投递后端服务开发计划（A1–A8 落地方案 + 分阶段实施）

日期：2026-11-19（Asia/Shanghai）
依据：`docs/review_xhs_draft_repair_audit_2026-11-19.md`（审查报告）+ 本轮决策
目标：构建完整、可一次性交付的小红书投递后端服务；**命令语义唯一、平台事实进规范、失败行为确定、验证可复现、外部依赖兼容受控**。
代码摸底结论（计划已按实际文件落地）：`redbook/cli.py`（note 子命令 --validate/--stage/--publish）、`redbook/infrastructure/xiaohongshu_delivery.py`（633 行，含 DeliveryError/TopicEntityUnavailable/_verify_saved_draft）、`redbook/infrastructure/opencli_runtime.py`（242 行，**已存在，作为统一适配层的宿主**）、`redbook/scripts/xhs_drafts.py`（170 行）。

---

## 〇、已确认的决策基线

| 决策项 | 拍板 |
|---|---|
| `--publish` 语义 | 就是"保存草稿"；新增 `--save-draft` 主别名，`--publish` 保留为兼容别名 |
| 失败恢复 | 本地维护 run_id ↔ draft_id 映射表，重跑先对账 |
| 验证步骤 | 固化为 CLI 子命令，禁内联 `python -c` |
| 外部工具链 | 兼容旧版本（走 §三 兼容性试验计划，不做硬升级） |
| 错误处理 | 结构化错误码表 |
| staged 目录命名 | 目录名 = staged_id 全文（64 hex），不截断 |
| 内容重复 | 按 §二 去重合并 |

---

## 一、A1–A8 逐项解决方案

### A1 平台事实固化（解决"再次复发"的根本手段）

复发的原因：修复知识只存在于会话记忆/审计文档，**没有任何机器可执行的载体**。固化必须同时落到三个层面，缺一即失效：

1. **规范层**：`redbook/docs/xhs-content-spec.md` 新增"平台行为约束（Platform Facts）"章节，逐条登记：
   - PF-1 Creator Center 话题展示带 `#` 前缀，点选后面板收起；每绑定一个实体后必须重读面板
   - PF-2 原生键盘输入路径不可用（`Native input requires a visible browser page`）；正文写入必须走 CDP eval
   - PF-3 OpenCLI 2.x `--session` 参数位置与 `{ok,data}` 响应包装（引用适配层为唯一实现）
   - PF-4 推荐面板的 `.tag` 芯片随机轮换，唯一稳定锚点是真实话题芯片
   每条 PF 必须带"首次发现会话 + 修复提交"引用（与 A7 审计模板联动）。
2. **代码层**：`xiaohongshu_delivery.py` 顶部模块级常量 `PLATFORM_FACTS = {...}`（结构化字典，含事实编号与约束），实现中的关键分支（去 `#` 前缀、面板重读、CDP 输入）必须引用对应 PF 编号——review 时可机器检查"每个平台事实是否有实现覆盖"。
3. **测试层（最关键，防复发的牙齿）**：把 PF 编码为回归测试夹具——用录制的页面/响应样本（ Golden files）做适配层契约测试，测试名直接叫 `test_pf1_topic_panel_reread_after_selection`。**规范会被人忘掉，CI 不会**。

验收：新增内容闸门测试 `test_content_spec.py` 断言 spec 含 PF 章节；适配层契约测试覆盖 PF-1~PF-4。

### A2 `--publish` 语义去歧义

- `cli.py` note 子命令新增 `--save-draft`（主别名，与 `--publish` 互斥使用，同 group）；`--publish` help 改为「deprecated alias of --save-draft; saves to draft box, never publishes」。
- SKILL.md / spec 中所有流程描述统一改用 `--save-draft`。
- 加一条测试：两个别名走同一 handler（防未来分叉）。

### A3 失败恢复：run_id ↔ draft_id 对账注册表

新增 `redbook/infrastructure/delivery_registry.py`：

```json
// data/workflow_state/<slug>/delivery_registry.json
{
  "runs": [
    {"run_id": "r-20261119-001", "slug": "2611.17921",
     "staged_id": "<64hex>", "draft_id": "s:...",
     "status": "draft_saved|verify_passed|verify_failed|orphan",
     "verify": {"body_ok": true, "topics_ok": true, "pdf_ok": true},
     "created_at": "<iso8601>"}
  ],
  "orphan_policy": "keep_audit | delete"   // 显式配置，默认 keep_audit
}
```

- `deliver()` 前先 `reconcile(slug)`：存在 `verify_passed` 的记录 → 直接返回该 draft_id（幂等，不新建）；存在 `verify_failed`/`orphan` → 按 orphan_policy 处置并记录处置动作。
- 投递成功立刻写注册表（先写本地再信任平台），verify 结果异步回填。
- 现有 `checkpoint.json` 的 draft_saved 状态改为引用 registry（P8）。

### A4 验证固化为 CLI 子命令

`note <slug> --verify [--draft-id <id>]`：
- 无 `--draft-id` 时从 delivery_registry 取最新 `draft_saved` 记录；
- 内部执行两级断言：L1 `fetch_drafts` 列表在册（R4 合并后的单一实现）→ L2 `_verify_saved_draft` IndexedDB 深校验；
- 输出统一 JSON schema：`{"slug","draft_id","l1_registered":bool,"l2":{"body_ok","topics_ok","pdf_ok"},"checkpoint_consistent":bool,"status":"passed|failed"}`；
- 同步比对 checkpoint.json 的 draft_id（P8 一并解决）；
- 退出码：passed=0，failed=3（可脚本判断）。

### A5 外部工具链兼容：前置门禁 + 兼容层（试验计划见 §三）

- 预检函数 `preflight(config)`：解析 `opencli doctor --json` 输出，断言 connectivity.ok=true；版本按 §三 的兼容矩阵判定 `supported | degraded | unsupported`，unsupported → blocked（不启动浏览器进程）。
- 期望版本写入 `config/xhs_content_rules.yaml` 的 `toolchain:` 段（含 min/max 支持区间），而非硬编码。

### A6 结构化错误码表

新增 `redbook/infrastructure/delivery_errors.py`（错误码唯一权威，供 spec/SKILL 引用）：

| 错误码 | 触发条件 | 处置 | 可重试 |
|---|---|---|---|
| `E_PREFLIGHT_BLOCKED` | doctor/版本断言不过 | blocked，不启动 | 否 |
| `E_NATIVE_INPUT` | 原生键盘输入路径失败（PF-2） | 切 CDP eval 重试一次 | 是(1) |
| `E_TOPIC_UNAVAILABLE` | 面板无候选/点选失败（PF-1/PF-4） | fail-fast，保留现场快照 | 否 |
| `E_VERIFY_MISMATCH` | 回读 body/topics/pdf 不一致 | 删本次残缺稿 + registry 记 orphan | 否 |
| `E_OPENCLI_WRAP` | 响应包装不符合预期 | fail-fast，落原始响应样本 | 否 |
| `E_SESSION_LEASE` | 会话被上次中断占用 | 清理租约后重试一次 | 是(1) |
| `E_DRAFT_LIST_UNREACHABLE` | L1 清点不可达 | 重试 3 次（退避） | 是(3) |

`DeliveryError` 增加结构化字段：`code, message, pf_refs, retry_policy, raw_snapshot`。事件流/回执 JSON 统一落 `error.code`。

### A7 审计元数据模板（会话审计 schema）

新增 `redbook/docs/session-audit-template.md`，强制结构：

```markdown
# <标题>会话审计
## 0. 元数据（必填）
- 分支 + HEAD commit：experiments @ <40hex>（dirty: yes/no）
- 相关改动提交：<commit 列表>
- 工具链版本：OpenCLI <ver> / 扩展 <ver> / Chrome <ver>
- 会话起止时间：<iso8601>
## N. 阶段（每阶段一张表）
| seq | 时间 | 命令 | exit code | 关键断言（期望 vs 实际） |
## 结论
- 状态机终态 / 未决项 / 引用的 PF 编号
```

要点：无 exit code 的命令视为"未验证"；所有断言必须写实际值（本审计已做到）+ 期望值（本轮补）。

### A8 staged 目录名 = staged_id 全文

- `--stage` 写包路径改为 `data/publish_queue/<staged_id_64hex>/xhs.json`；
- 提供一次性迁移脚本（读旧 32hex 目录 → 按包内 staged_id 改名/重链 → 打迁移报告）；旧目录保留只读归档；
- spec 中明文：**目录名 = staged_id 全文，禁止截断**；registry（A3）以 staged_id 全文为主键。

---

## 二、去重合并方案（R1–R5）

| 项 | 动作 | 落点 |
|---|---|---|
| R1 `{ok,data}` 解包双实现 | 合并进 `opencli_runtime.py` 改造为唯一 `OpenCliClient`（会话管理 + 参数位置 + 解包 + 错误码映射）；`xiaohongshu_delivery.py`、`scripts/xhs_drafts.py` 只调用 | `opencli_runtime.py` |
| R2 硬门槛四处复述 | YAML 为唯一机读权威；SKILL.md/spec 只引用路径+PF 编号；加 `test_content_spec.py` 断言数值只出现在 YAML | `config/xhs_content_rules.yaml` |
| R3 话题处理分散 | delivery 内独立 `TopicBinder` 类（输入候选列表 → 输出已点选清单+面板快照），独立测试 | `xiaohongshu_delivery.py` |
| R4 回读双通道 | 合并为 `--verify` 内部 L1+L2 两级断言（见 A4） | `cli.py` |
| R5 审计重复叙事 | 采用 §A7 模板重写后续审计 | `docs/session-audit-template.md` |

---

## 三、外部工具链兼容性试验计划（A5 展开）

原则：**兼容靠契约测试 + 特性协商，不靠"只支持最新版"**。

### 3.1 兼容矩阵（写入 config/xhs_content_rules.yaml `toolchain:`）

```yaml
toolchain:
  opencli:
    supported: ["2.x"]           # 主支持线
    wrappers: {"2.x": "ok_data"} # 响应包装协商键
  extension:
    min: "1.0.25"                # 1.0.25 可 degraded 运行（禁原生输入路径）
    recommended: "1.0.27"        # 1.0.25 升级动机正是 PF-2
  degrade_rules:
    "1.0.25": ["--use-native-input off", "topic-probe 频率减半"]
```

### 3.2 三层试验设计

**T1 离线契约测试（每次 CI）**：为 OpenCLI 各版本的典型响应录 Golden fixtures（`tests/fixtures/opencli/`）：`{ok,data}` 包装、`--session` 参数位置、drafts 列表结构、错误响应。`OpenCliClient` 针对 fixtures 跑全量行为测试——**不依赖真实浏览器即可回归**。

**T2 只读探针（每次投递前自动执行，分钟级）**：`preflight` 依次跑
1. `opencli doctor --json` → 版本/connectivity 判 supported|degraded|unsupported；
2. `opencli xiaohongshu drafts -f json`（只读）→ 实际响应包装与协商键比对；
3. 特性协商结果写进 run 事件（`toolchain_profile` 字段），全程只读、零副作用。

**T3 金丝雀投递（版本变更/周检，一次性草稿验证）**：用固定测试 note（内容恒定、标题带 `[canary]` 前缀）走完整链路存草稿 → `--verify` → 按 orphan_policy=delete 清理。任何版本升级（OpenCLI 2.x→3.x、扩展新版本）后先跑 canary 再允许正式投递。

### 3.3 升级触发与回退

- 响应包装比对失败（E_OPENCLI_WRAP）→ blocked + 落原始响应样本 → 人工更新 fixtures/适配层 → T1/T3 重绿才放行；
- degraded 档位运行时事件流标注 `degraded: true`，UI/审计可见。

---

## 四、分阶段开发计划

每阶段有独立验收，按序执行；M1 是其他阶段的地基。

### M0 契约冻结（纯文档 + 配置，先于一切代码）
- [ ] spec 增加 Platform Facts 章节（PF-1~PF-4）+ 审计模板落盘
- [ ] 错误码表进 spec（引用 `delivery_errors.py` 为实现权威）
- [ ] YAML `toolchain:` 段 + `orphan_policy` + staged 目录命名规则
- 验收：`test_content_spec.py` 新增断言全绿

### M1 适配层统一（R1）
- [ ] `opencli_runtime.py` → `OpenCliClient`（解包/会话/错误码映射）
- [ ] delivery 与 `xhs_drafts.py` 改为调用；Golden fixtures + 契约测试
- [ ] `delivery_errors.py` 落地，`DeliveryError` 结构化
- 验收：现有 13 个测试不回归 + 新增契约测试；全链路 canary 通过

### M2 CLI 固化（A2/A4/A8）
- [ ] `--save-draft` 主别名；`--verify` 子命令（L1+L2+checkpoint 比对）
- [ ] `--stage` 目录名改 staged_id 全文 + 一次性迁移脚本
- 验收：`--verify` 输出 schema 稳定；迁移脚本对现有暂存包幂等重跑无差异

### M3 幂等与治理（A3 + P1/P8）
- [ ] `delivery_registry.py` + reconcile 进 `deliver()` 入口
- [ ] checkpoint 引用 registry；孤儿稿按 orphan_policy 处置
- 验收：**同一 note 连续投递两遍，第二遍返回同一 draft_id 且平台草稿数不变**（幂等测试具名：`test_delivery_idempotent_rerun`）

### M4 预检门禁（A5 + P2/P3/P6）
- [ ] `preflight`：doctor 断言 + 只读探针 + 特性协商（T2）
- [ ] 话题候选可用性前置校验进 `--validate`；登录态探针；unsupported → blocked
- 验收：手动构造过期版本 → 状态 blocked 且无浏览器进程启动

### M5 端到端集成验收
- [ ] canary T3 流程脚本化（版本变更即跑）
- [ ] 全链路：validate → stage → preflight → save-draft → verify → registry/checkpoint 一致
- [ ] 按 A7 模板产出本轮开发自己的会话审计（自举验证模板可用）
- 验收总门禁：pytest 全绿（含 PF 回归 + 契约 + 幂等）+ canary 绿 + 审计模板实例化完成

---

## 五、明确不做（防 scope 蔓延）

- 不做公开发布路径（铁律不变，`--save-draft` 语义即边界）
- 不做多账号/并发投递（P5 留待批量需求出现再立项）
- 不做平台端草稿自动批量清理（P1 仅单条人工决策 + registry 防再生成）
- 不复刻 ADA 平台的全套 REST/SSE——本轮只做 CLI + registry 的确定性后端；若后续需要 UI 再复用 ADA 模式
