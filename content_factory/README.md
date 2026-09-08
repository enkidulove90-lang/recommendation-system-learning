# content_factory — 科研故事化内容工厂

把「论文 11 维摘要 → 故事化草稿 → 标题工厂 → 多平台适配 → 发布审核包」做成
端到端可工程化流水线。设计来源：

- `docs/content-factory-engineering.md`（19 模块 / Stage 0–8）
- `docs/content-strategy-research.md`（27 个已验证工具）

## 已实现（本地可工程化，无需外部 API）

| Stage | 模块 | 文件 | 说明 |
|-------|------|------|------|
| 1 | M1 叙事骨架 + M2 LLM 润色 | `narrative_engine.py` | 四段式 ABT/Freytag/Six Steps 规则层 + 可选 LLM 润色 |
| 3 | M6 变体生成 + M7 评分门禁 + M8 A/B 判定 | `title_factory.py` | 本地启发式评分（0–100，<70 触发重写）；`--llm` 下用 DEEPSEEK 生成额外标题；`AnalyticsSpec.pick_winner` 做 Wilson+z-test |
| 4 | M3 交互可视化 + M4 信息图 + M5 滚动叙事 | `visualization.py` | Idyll/Observable/Vizzu/AntV/NarroViz spec + 可离线渲染内联 SVG |
| 5 | M9 代码 Playground + M10 测验投票 + M11 滑块 | `interaction.py` | Replit/Apester/Idyll 组件，fact-only，iframe/HTML 占位 |
| 6 | M12 多平台改写 | `platforms.py` + `platforms.yaml` | 长度/emoji/陈述句/话题硬约束 |
| 7 | M13 定时发布 + M14 canonical + M16 A/B | `distribution.py` | Buffer / Dev.to / @appnest 可插拔适配器，离线产出 payload + curl 占位 |
| 8 | M17 GA4+Metabase + M18 事件 Schema | `analytics.py` | 6 类事件埋点 Schema + 可校验合约 + 看板 JSON + 埋点 JS 片段 + 本地漏斗/AB 引擎 |
| 编排 | — | `factory.py` + `cli.py` + `auto_runner.py` | 串起全链，产出与 redbook `PublicationPackage` 同构的 `publish_queue/<hash[:32]>/<platform>.json`，Stage 4/5/7/8 产物写入同包侧车 `<paper_hash>/{viz,interaction,distribution,analytics}.json` |

> 外部服务（Idyll/Observable/Apester/Buffer/Dev.to/GA4/Metabase）需前端或 API key；
> 适配器均设计为**可插拔 + 离线可渲染**：无 key 时只产出结构化 payload / 内联 SVG / curl 占位，
> 拿到 key 后由运营执行 `publish()` 或贴出 curl。全部单测离线可跑。

## 防幻觉铁律

- 规则层只用摘要原文事实填空；`PaperSummary` 在「方法 / 结果 / 问题动机」任一缺失时
  抛 `InsufficientSourceError` 阻断生成（绝不编造）。
- 每段故事绑定来源字段（`StoryDraft.bound_fields`），可追溯。
- LLM 润色层（`polish=True`）仅改表达，不引入原文外数字；缺 key 时自动跳过。

## 用法

```bash
# 端到端生成（规则层，dry-run 不写队列）
python -m content_factory --paper-id 2506.07261 --platforms xhs,wechat --dry-run

# 写入发布审核包（review_status=pending，人工审核后再发）
python -m content_factory --paper-id 2506.07261

# 启用 LLM 润色 + 标题生成（需 DEEPSEEK_API_KEY）
python -m content_factory --paper-id 2506.07261 --llm

# Stage 4/5 可视化 + 交互组件
python -m content_factory --paper-id 2506.07261 --viz

# Stage 7 分发 + canonical + A/B 作业
python -m content_factory --paper-id 2506.07261 --distribute

# Stage 8 GA4/Metabase 看板 + 事件 Schema
python -m content_factory --paper-id 2506.07261 --analytics

# 一次性全链路（规则层 + 三路扩展）
python -m content_factory --paper-id 2506.07261 --llm --viz --distribute --analytics

# 自动调度：对最新、未暂存的论文生成（本地 cron / CI 共用）
python content_factory/auto_runner.py --limit 3 --llm --viz --distribute --analytics

# 接入既有批量管线
python run_batch_pipeline.py --step 6                      # 单步（默认仅规则层）
python run_batch_pipeline.py --step 6 --cf-llm --cf-viz --cf-distribute --cf-analytics
python run_batch_pipeline.py --step all                    # 1-6 全跑（Step6 失败不阻断前 5 步）
```

## 测试

```bash
python -m pytest content_factory/tests -q        # 51 用例：抽取/叙事/标题/平台/可视化/交互/分发/分析（含合约校验/A/B 分配/多臂/看板）
```
测试用受管 venv（`~/.workbuddy/binaries/python/envs/default`，已装 pytest + pyyaml）；
规则层与全部单测均不依赖任何 API key。

## 运维

- `.github/workflows/content-calendar.yml`：每小时巡检 `data/summaries/`，对最新未暂存
  论文跑工厂并暂存，产物作为 artifact 上传供人工审核。
- 与既有 redbook 发布体系兼容：本包写入的 `publish_queue/<hash[:32]>/<platform>.json`
  与 `redbook.automation.publishing.PublicationPackage` 同构，`XhsPublisher` /
  `WeChatPublisher` 可直接读取并走真实发布流程。

## 外部服务接入（拿到 key 后启用真实发布）

本包产出的是**结构化 spec / 离线占位**，真实触网需在对应适配器注入 key 后调用 `publish()`
（或按 `offline_stub` 的 curl 手动执行）：

- **可视化/交互挂载**：把 `viz.json` / `interaction.json` 的 HTML 片段注入平台（Idyll/Observable
  iframe、Apester unit、Replit 分享链接）。
- **Stage 7 分发**：`BufferAdapter(api_key=...)` / `DevToAdapter(api_key=...)` 调用 Buffer /
  Dev.to API；`@appnest/ab-test` 组件注入页面，A/B 选择事件自动上报 GA4。
- **Stage 8 回收**：把 `analytics.json` 的 GA4 事件注册到 GA4，把 `metabase_dashboard` 导入
  Metabase；埋点 JS 片段注入各平台页脚。

### Stage 8 v1 合约升级（docs/content-event-analytics-design.md）

事件从「结构定义」升级为「可校验合约」：

- **版本化 + 公共维度**：`SCHEMA_VERSION=1.0.0`；每事件必带 `event_time/schema_version/
  platform/content_id/session_id/experiment_id`，支持跨平台对比与单人漏斗。
- **emit-time 校验**：`validate_event()` / `AnalyticsSpec.emit()` 在发出前校验必填、类型、枚举，
  非法事件抛 `InvalidEventError`，脏数据无法进入看板。
- **A/B 闭环**：`AnalyticsSpec.assign_ab_variant()` 以 `hash(session|experiment)` 做稳定随机分配
  （同读者不变体、跨读者均匀），产出合法 `ab_assign` 事件；`TitleABTest.multi_arm_winner()` 支持
  ≤N 标题多臂判定（对照 control 逐臂 z-test，95% 才宣布胜者）。`distribution.assign` 已改用此分配。
- **Metabase 看板**：`metabase_dashboard()` 输出 6 张可导入卡片，含**原生 SQL**（`native_query`）、
  **漏斗卡**（impression→cta_click by session_id）与**时序卡**。
- **埋点 snippet**：注入 `session_id`（localStorage 匿名）、`scroll_depth` **去重**（sent set）、
  A/B 分配钩子（`ab_assign`），并携带 `content_id/experiment/variants`。
- **合规**：`PII_POLICY` 明确 session_id 必须哈希、采样率、consent 职责。
- **Phase 2 本地-first 分析引擎**（无需 GA4/Metabase）：`EventCollector` 采集+JSONL 落盘/回放；
  `FunnelAnalyzer` 对一批事件直接算 `funnel/conversion/engagement/ab_lift`；`report_ab(events)` 按
  `ab_assign` 的 session→variant 归因后聚合调 `multi_arm_winner`。设计见 `docs/content-event-optimization-design.md`。
- **quiz/play 富集**：新增 `question_id/option`、`error/code_ref` 可选字段（校验放行）。
- **标题外部评分器**：`TitleFactory(external_scorer=...)` 已支持 Sharethrough / CoSchedule
  / Headline Goat 客户端接入。
