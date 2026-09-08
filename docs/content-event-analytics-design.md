# 内容事件回收（Stage 8）优化设计文档

> 对应代码：`content_factory/analytics.py`、`content_factory/distribution.py`、`content_factory/factory.py`
> 前置提案：`docs/content-factory-engineering.md`（M17/M18/M8）、`docs/content-strategy-research.md`（报告 15/16/23/24/27）
> 设计原则：本地离线可跑、零 API 依赖、外部服务仅留可插拔接口（与全包一致）

---

## 0. 背景与现状

Stage 8 已落地三块能力：

- **M18 事件埋点 Schema**：6 类事件（impression / scroll_depth / quiz_answer / play_run / cta_click / ab_assign）的字段 + 样例。
- **M17 GA4 + Metabase**：`ga4_events()` 注册 + `metabase_dashboard()` 卡片 + `tracking_snippet()` 注入 JS。
- **M8 标题线上 A/B**：`TitleABTest.pick_winner`（Wilson 区间 + 两比例 z-test，95% 才宣布胜者）。

**但提案存在"文档正确、工程未闭环"的问题**：事件是结构定义而非可校验合约；A/B 分配与统计两段互相不调用；事件无归因维度；前端 snippet 不去重。本文档给出闭环方案并实现。

---

## 1. 痛点总结（按优先级）

| # | 痛点 | 严重度 | 根因 |
|---|------|--------|------|
| P1 | 事件契约无运行时校验 | 高 | `EVENT_SCHEMA` 仅为类型字符串字典，发出前不校验 |
| P2 | A/B 闭环断开 | 高 | 分配固定取首变体、不发 `ab_assign`；`pick_winner` 不被调用 |
| P3 | 缺平台/内容维度 | 高 | 多数事件无 `platform`；无 `content_id/experiment_id` |
| P4 | 无会话/漏斗关联 | 高 | 无 `session_id`，漏斗不可重建 |
| P5 | JS 不去重 + 档位硬编码 | 中 | snippet 重复发 `scroll_depth`；档位写死 |
| P6 | Metabase 看板不可导入 | 中 | 伪查询结构，无 `native_query`/漏斗/时序卡 |
| P7 | 无 PII/采样合规 | 中 | `session_id` 是否哈希、采样率未定义 |
| P8 | quiz/play 载荷过薄 | 低 | 只记布尔，不知误区/错误 |
| P9 | A/B 仅两臂 | 中 | 工厂产 ≤5 标题，无多臂判定 |
| P10 | 无合约测试 | 中 | 测试只验结构，不验事件能否通过校验 |

---

## 2. 设计目标与非目标

**目标**

1. 事件成为**可校验合约**（版本化 + 公共维度 + emit-time 校验）。
2. A/B 形成**完整闭环**：发布时稳定随机分配并写 `ab_assign` → 采集 impression/cta_click → 多臂统计宣布胜者。
3. 所有事件携带 `platform / content_id / session_id / experiment_id`，支持跨平台对比与单人漏斗。
4. 前端 snippet 去重、可配置档位、注入会话与 A/B 钩子。
5. Metabase 看板给出**可导入的原生 SQL** + 漏斗卡 + 时序卡。
6. 明确 PII/采样合规策略。

**非目标**

- 不接入真实 GA4 / Metabase 后端（仅产出 Schema / SQL / 可粘贴 snippet / 离线统计）。
- 不做服务端事件接收管道（属于独立运维组件）。
- 不做实时流计算（批次上报即可）。

---

## 3. 事件契约 v1

### 3.1 版本与公共维度

- `SCHEMA_VERSION = "1.0.0"`，每个事件带 `schema_version` 字段，Schema 变更时递增，旧事件可回溯。
- **公共维度（每个事件必带）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_time` | string(ISO8601) | 事件时间（UTC） |
| `schema_version` | string | 合约版本 |
| `platform` | enum | xhs/wechat/zhihu/devto/x_thread/hn/reddit/web |
| `content_id` | string | publish_queue hash 或 paper_id |
| `session_id` | string | 客户端稳定匿名 id（必须哈希，见 §7） |
| `experiment_id` | string? | A/B 实验 id，可空 |

### 3.2 事件定义（节选）

| 事件 | 专属字段 | 必填 | 枚举/约束 |
|------|----------|------|-----------|
| impression | `component` | component + 公共 | — |
| scroll_depth | `percent` | percent + 公共 | `{25,50,75,100}`（可配置档位） |
| quiz_answer | `block_id`,`correct`,`question_id?`,`option?` | block_id,correct + 公共 | correct:bool |
| play_run | `editor`,`ran`,`,`error?`,`code_ref?` | editor,ran + 公共 | ran:bool |
| cta_click | `variant?` | platform + 公共 | — |
| ab_assign | `variant`,`algorithm` | variant + 公共 | algorithm: `hash_stable` |

### 3.3 校验（emit-time 合约强制）

新增 `InvalidEventError` 与 `validate_event(name, params)`：

- 必填字段缺失 → 拒绝。
- 类型不匹配（如 `correct` 非 bool、`percent` 非 int）→ 拒绝。
- 枚举越界（如 `percent=40`、未知 `platform`）→ 拒绝。
- 公共维度缺失 → 拒绝。
- `AnalyticsSpec.emit(events)` 对每个事件调用校验并自动补 `schema_version`/`event_time`（若缺）。

---

## 4. A/B 闭环设计

```
发布时 (factory/distribution)                采集时 (前端 snippet)             分析时 (离线)
┌──────────────────────────┐          ┌────────────────────────┐     ┌─────────────────────────┐
│ assign_ab_variant(        │          │ 发 ab_assign(已分配)    │     │ report_ab(events)        │
│   experiment, variants,   │ ───────▶ │ 发 impression(per var)  │ ──▶ │  按 variant 聚 impr/click │
│   session_id) → variant   │          │ 发 cta_click(variant)   │     │  multi_arm_winner(arms)  │
│ 哈希稳定：同 session 同变 │          │                         │     │  对照 control 逐臂 z-test │
│ 体，跨 session 伪随机     │          └────────────────────────┘     │  显著才宣布（95%）        │
└──────────────────────────┘                                         └─────────────────────────┘
```

- **分配算法** `assign_ab_variant`：以 `hash(session_id + experiment + salt) % len(variants)` 决定，保证同一读者回访不变体（稳定），不同读者分布均匀（伪随机）。替代原 `variants[0]` 的硬分配。
- **事件落地**：分配时产出一条 `ab_assign` 事件（`algorithm="hash_stable"`），随包写入 `analytics.json`，供前端注入。
- **统计闭环**：新增 `TitleABTest.multi_arm_winner(arms)`，以 `arms[0]` 为 control，对其余臂做两比例 z-test（复用 `_wilson`），显著且胜出者宣布，否则 `inconclusive`。原 `pick_winner`（两臂）保留作底层原语。

---

## 5. 会话 / 漏斗关联模型

- 前端在首屏生成 `session_id = sha256(匿名种子)`，全程携带。
- 通过 `session_id + content_id` 串起 `impression → scroll_depth → quiz_answer/play_run → cta_click`。
- Metabase 漏斗卡：`COUNT(DISTINCT session_id)` 按事件顺序逐步筛选。
- `experiment_id` 与 `variant`（cta_click / ab_assign）关联，支撑分变体漏斗对比。

---

## 6. Metabase 看板查询规范

`metabase_dashboard()` 输出**可导入卡片**：每张卡含 `name`、`native_query`（针对 `ga4_events` 表的 SQL）、`visualization`（line/bar/funnel/table）。至少包含：

1. **曝光量 by 组件**（`GROUP BY component`）
2. **滚动完成度分布**（`GROUP BY percent`）
3. **测验正确率**（`AVG(correct)`）
4. **A/B CTR 对比**（`GROUP BY experiment, variant`）
5. **标题漏斗**（funnel：impression→cta_click by session_id）
6. **每日曝光时序**（time-series）

SQL 用参数占位（`{{content_id}}`），便于按内容过滤。

---

## 7. 合规策略（PII / 采样）

- `PII_POLICY` 常量：
  - `session_id` **必须哈希**，禁止明文用户标识。
  - `content_id` 仅用内容 hash，不绑个人。
  - 默认 `sampling_rate = 1.0`（全采）；GA4 侧可配置降采样。
  - 开源内容不含 consent 字段；落地私有部署需补 consent 闸门（本文档不实现）。
- snippet 注释明示：注入前需确认平台隐私政策允许该埋点。

---

## 8. 实现映射（问题 → 文件 → 函数）

| 问题 | 文件 | 改动 |
|------|------|------|
| P1 | analytics.py | `SCHEMA_VERSION` + `COMMON_DIMENSIONS` + `InvalidEventError` + `validate_event` + `AnalyticsSpec.emit` |
| P2 | analytics.py / distribution.py | `assign_ab_variant`；`AppnestABAdapter.assign` 改调；`report_ab`/`multi_arm_winner` |
| P3/P4 | analytics.py | 公共维度写入所有事件；snippet 注入 `session_id/content_id` |
| P5 | analytics.py | snippet 去重（sent set）+ 可配置 `scroll_buckets` |
| P6 | analytics.py | `metabase_dashboard` 改产出 `native_query` + 漏斗/时序卡 |
| P7 | analytics.py | `PII_POLICY` 常量 + 文档 |
| P8 | analytics.py | quiz/play 增加可选字段并在校验中放行 |
| P9 | analytics.py | `TitleABTest.multi_arm_winner` |
| P10 | tests | 新增校验/分配/多臂/看板/去重测试 |

`factory.py`：新增 `experiment` 参数透传；`analytics=True` 时按包分配 variant 并写 `experiment_id`+`assigned_variant` 到包 metadata 与 `analytics.json`。

---

## 9. 测试策略

- **合约**：合法事件通过 `validate_event`；缺必填/越界枚举/错类型被拒。
- **分配**：同 `session_id` 稳定同变体；不同 `session_id` 分布覆盖全部变体。
- **多臂**：B 显著胜出 → 宣布；差异极小 → `inconclusive`。
- **看板**：断言含 `native_query` 与 funnel/时序卡。
- **snippet**：含 `session_id` 占位与 scroll 去重逻辑。
- 全部用例在受管 venv 离线运行，零 API 依赖。
