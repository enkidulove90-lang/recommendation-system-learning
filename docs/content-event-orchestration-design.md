# 内容事件编排层设计（Content Event Orchestration）

> 输入：既有设计 `docs/content-factory-engineering.md`（Stage 0–8 / M1–M19）、`redbook/docs/design/04-multi-platform-publishing.md`、`redbook/docs/design/05-feedback-loop.md`、已落地 `wechat_design/dtle/`（双轨渲染）
> 目标：补齐「设计有、代码缺」的事件编排核心——把 `publish_queue/` 里的静态内容包，驱动为一条可观测、可回滚、幂等的内容生命周期事件流（intake → render → stage → publish → feedback）
> 防幻觉：每项能力标注所依据的设计章节；未落地部分显式标注【待实现】

---

## 1. 优化方向总览（审计结论）

当前系统「设计完整、落地碎片化」。`content-factory-engineering.md` 给出 Stage 0–8 + M1–M19，`redbook/docs/design/` 有 7 章提案，但代码侧：

| 模块 | 设计 | 落地 | 缺口 |
|---|---|---|---|
| 双轨渲染 DTLE | — | ✅ 已落地（A 轨 HTML / B 轨 PNG，Flask+Playwright / Satori+resvg） | 未接入队列 |
| 多平台发布 skill | M12/M13 | ⚠️ 手工调用为主 | 无编排层驱动 |
| 发布状态机 | `content-factory` §5.3 `draft→title_ab→scheduled→published→archived` | ❌ 无 | 状态只在文档 |
| 内容事件埋点 M18 | 曝光/滚动/测验/CTA Schema | ❌ 无 | 生命周期事件未建模 |
| 幂等 `paper_id+platform+content_hash` | 设计 04 §风控 2 | ❌ 无 | 重试会重复发 |
| 反馈闭环 | 设计 05（SQLite+QS7+贝叶斯+UCB） | ❌ 无 | 仅设计 |
| 队列处理器 | 设计 04 `publish_queue/<id>/<platform>.json` | ❌ 无 | 静态 JSON 无人驱动 |
| 统一调度 CLI / 自动化 | 设计 04 §首批 / 内容工厂 §6.1 | ❌ 无 | 只监测 `data/parsed/` |

**优化方向菜单（按杠杆排序）：**
1. 【本轮目标】内容事件编排核心：事件总线 + 状态机 + 队列处理器 + 幂等（打通渲染→发布）
2. 反馈闭环落地（设计 05）：只读采集 + SQLite + QS7 + 贝叶斯/ UCB 自优化
3. 统一 Publisher 适配器：WeChat 草稿 / XHS 草稿 / Notion / Blog（设计 04 接口）
4. 内容事件埋点 M18：前端/发布侧生命周期事件入库（曝光/滚动深度/CTA）
5. 内容日历自动化：GitHub Action 监测 `data/parsed/` → 建卡 → 触发 Stage 1–6 → 入队
6. 图片智能合成（设计 06）、人设-证据规范（设计 07）、数据源扩展（设计 01）：均为独立优化项

---

## 2. 内容事件模型

### 2.1 事件类型（对应 M18「内容生命周期」视角）
```
CONTENT_INTAKE     论文摘要/草稿进入队列（来自 data/parsed 或 publish_queue）
RENDER_REQUEST     请求 DTLE 双轨渲染
RENDERED           DTLE 渲染完成（产出 wechat HTML / xhs PNG）
VALIDATED          Publisher.validate 通过
STAGED             平台草稿/本地待发布包创建（返回 external_id）
PUBLISHED          人工审核后 publish 成功（记录 note_id）
FEEDBACK_SAMPLED   反馈采集窗口命中（2h/24h/7d/30d）
DECISION_MADE      反馈闭环产生权重/时段决策
NEEDS_REVIEW       任意环节失败/风控触发，转人工
```

### 2.2 ContentItem 事实包（复用设计 04 §统一 Publisher 输入）
```json
{
  "paper_id": "arxiv:3806231",
  "platform": "xhs | wechat | zhihu_answer | x_thread | jike | notion | blog",
  "canonical_url": "https://<site>/papers/<id>/",
  "title": "...", "body_markdown": "...",
  "image_paths": ["..."], "links": {"paper":"","pdf":"","code":""},
  "review_status": "pending | approved | needs_review",
  "source_attribution": "图表摘自论文，仅作学术解读",
  "content_hash": "<sha256(title+body+images+links)>"
}
```

### 2.3 幂等键
`key = f"{paper_id}::{platform}::{content_hash}"`——同 key 已 `STAGED/PUBLISHED` 则跳过（设计 04 §风控 2）。

---

## 3. 状态机

状态（合并内容工厂 §5.3 与发布设计 04 review_status）：
```
draft → rendered → validated → staged → published → archived
                       │           │
                       └──→ needs_review（任意校验/发布失败）
NEEDS_REVIEW → draft（人工修订后重入）
```
转移守卫：
- `draft→rendered`：DTLE 渲染成功且产物存在
- `rendered→validated`：Publisher.validate 返回空错误列表
- `validated→staged`：未达 `review_status=approved` 时仅写本地包；`approved` 才调 `stage()`
- `staged→published`：仅人工审核后显式 `publish()`
- 任意步异常 → `needs_review` + 发 `NEEDS_REVIEW` 事件（不自动重试，设计 04 §风控 3 / 设计 05 §实施 3）

状态持久化：每个 item 在 `publish_queue/<id>/state.json` 记录当前状态 + 最后事件时间；事件流追加到 `data/content_events/events.jsonl`（不可变审计日志）。

---

## 4. 队列处理器（process_queue）

```
for each publish_queue/<paper_id>/<platform>.json:
  1. 载入事实包 → 计算 content_hash → 查幂等表
  2. emit CONTENT_INTAKE
  3. if not rendered: DTLE.render(track=platform) → 写 data/publish_artifacts/<key>/(index.html|card.png)
     emit RENDERED
  4. Publisher.validate(package) → 空则 emit VALIDATED，否则 NEEDS_REVIEW
  5. if review_status==approved: Publisher.stage() → 写 data/publish_results/<platform>/<external_id>.json
     emit STAGED（external_id）
  6. 状态机推进；落 state.json + events.jsonl
```
沙箱无网络时：Publisher 降级 `DryRunPublisher`，仅写本地待发布包 + 记录事件，不触达真实平台（设计 04 §风控 1「先草稿后发布」）。

---

## 5. 统一 Publisher 接口（复用设计 04 §统一 Publisher）
```python
class Publisher(Protocol):
    platform: str
    def validate(self, package) -> list[str]: ...      # 返回阻断错误
    def stage(self, package) -> dict: ...               # 草稿/本地包，返 external_id
    def publish(self, staged_id) -> dict: ...           # 仅 approved 调用
    def metrics(self, external_id) -> dict: ...         # 读互动，不可读返 unavailable
```
实现：
- `DryRunPublisher`：永远成功，写 `data/publish_results/<platform>/dryrun_<hash>.json`（沙箱/测试用）
- `WeChatPublisher`：守卫导入 `redbook.infrastructure.wechat_delivery.WeChatDraftDelivery`，异常→needs_review
- `XhsPublisher`：守卫导入 `redbook.infrastructure.xiaohongshu_delivery.OpenCliXiaohongshuDelivery`
- `NotionPublisher` / `BlogPublisher`：【待实现】本地包占位

---

## 6. 反馈闭环接入（复用设计 05）
`feedback_collector.py` 实现：
- SQLite：`data/feedback/feedback.sqlite`，表 `posts / metric_snapshots / decisions`（DDL 同设计 05 §数据存储）
- 指标：`ER / SR / FLR / DDR / FR / QS7`（公式同设计 05 §指标定义），`max(V,100)` 防虚高
- 采集：守卫调用 `opencli xiaohongshu creator-notes/creator-note-detail`（设计 05 §只读入口）；不可读→`collection_failed`，等下一窗口
- 自优化：贝叶斯平滑分组 lift（设计 05 §内容与论文优先级）+ UCB 时段选择（§发布时间自优化）；变化 `±0.05`，7 天一次，可回滚
- 仅影响「下一批草稿候选队列」，不绕过人工审核（设计 05 §结论）

---

## 7. 调度 CLI / 自动化
`content_events/cli.py`：
```
python content_events/cli.py process-queue [--root .] [--publisher dryrun]
python content_events/cli.py collect-feedback [--window 24h]
python content_events/cli.py status [--paper-id X]
```
GitHub Action / 本仓库 `.workbuddy` 自动化可定时调用 `process-queue`（监测 `publish_queue/`）→ `collect-feedback`（监测已发布笔记观察窗口）。

---

## 8. 安全边界（继承设计 04/05）
1. 任何平台默认只 `stage`，定时任务不直接 `publish`
2. 网络/登录/审核失败 → `needs_review`，不自动重试
3. 反馈采集只读，不点赞/评论/关注/删帖
4. 幂等键防重复发；状态机不能随意跳变

---

## 9. 实施计划
- 本轮交付：`content_events/` 包（schema / state_machine / event_log / publishers / queue_processor / feedback_collector / orchestrator / cli / tests）+ 本设计文档。
- 验证：单测全绿；用现有 `publish_queue/` 一个 item 跑 `process-queue --publisher dryrun`，确认 DTLE 渲染产物（wechat HTML / xhs PNG）+ 状态机 + 事件日志 + 本地待发布包落盘。
- 后续：接真实 WeChat/XHS `stage`（设计 04 首批计划）、反馈闭环 OpenCLI 采集（设计 05）、内容日历 Action。
