# 第 5 章：反馈闭环

## 结论

反馈闭环采用 OpenCLI 从小红书创作中心读取数据，不接入第三方小红书 API，也不自动执行点赞、评论、关注等互动动作。反馈只影响“下一篇论文的草稿优先级、话题选择、发布时间候选”，不绕过人工发布审核。

当前环境已有三条只读入口：

- `opencli xiaohongshu creator-notes --limit 20`：单篇观看、点赞、收藏、评论、发布时间与 URL。
- `opencli xiaohongshu creator-note-detail <note-id>`：单篇互动、趋势、流量来源、观众画像。
- `opencli xiaohongshu creator-stats --period seven|thirty`：账号级观看、点赞、收藏、评论、分享、涨粉及每日趋势。

系统不依赖非官方第三方数据接口；创作中心页面或 OpenCLI 适配器不可读时，降级为人工从创作中心导出的表格导入，不影响论文发现、解析和草稿生成。

## 数据采集与观察窗口

发布成功后记录 `note_id`、论文 ID、版本 hash、发布时间、时段、主题、机构、研究方向、图片数和发布渠道。采集器仅对已发布笔记运行，在发布后的 `2h`、`24h`、`7d`、`30d` 各采样一次：

| 窗口 | 目的 | 数据 |
| --- | --- | --- |
| 2h | 发现异常或首轮分发差异 | 观看、点赞、收藏、评论 |
| 24h | 比较早期内容质量 | 核心互动、流量来源 |
| 7d | 调整发布策略的唯一主窗口 | 完整互动、涨粉、趋势 |
| 30d | 评估长尾收藏和知识价值 | 收藏、搜索流量、累计互动 |

同一笔记在同一窗口只保存一次规范化快照；再次抓取仅追加原始快照，不覆盖历史。采集器须使用 `--site-session persistent --keep-tab true`，一次批量读取完成后退出，不高频刷新页面。

## 指标定义

令 `V` 为观看/曝光，`L` 为点赞，`F` 为收藏，`C` 为评论，`R` 为评论回复数，`S` 为分享，`N` 为该笔记带来的新增关注。所有除法使用 `max(V, 100)`，防止极低曝光造成虚高比例。

| 指标 | 公式 | 含义 |
| --- | --- | --- |
| 互动率 `ER` | `(L + F + C + S) / max(V,100)` | 综合即时反应。 |
| 收藏率 `SR` | `F / max(V,100)` | 论文内容的主指标，代表日后查阅价值。 |
| 收藏/点赞比 `FLR` | `F / max(L,1)` | 区分“好看”与“值得保留”；只在 `L ≥ 20` 时参与决策。 |
| 深度讨论率 `DDR` | `(C + 0.5R) / max(V,100)` | 区分有回复链的讨论与单句评论。 |
| 关注转化 `FR` | `N / max(V,100)` | 衡量对账号长期增长的贡献。 |
| 7 日质量分 `QS7` | `0.45*z(SR)+0.25*z(ER)+0.20*z(DDR)+0.10*z(FR)` | 各指标对近 28 篇同类笔记做 winsorize 后的 z 分数；用于排序。 |

`QS7` 不以单篇绝对点赞数为依据，也不奖励诱导评论。若 `V` 不可用，系统将 `exposure_available=false`，仅保存原始计数和 `FLR`，该篇不得进入自动权重学习。

## 反馈管线

```text
Creator Center / 导出文件
          ↓（只读）
raw snapshot JSONL → 规范化 SQLite → 2h/24h/7d 指标
                                      ↓
                         论文主题、机构、图片、时段分组
                                      ↓
                 优先级增量 / 时段选择 / 生成复盘报告
                                      ↓
                       仅影响下一批草稿候选队列
```

每日任务只拉取“有到期观察窗口的已发布笔记”和最近 30 篇列表；单篇详情只在 24h、7d、30d 调用。正常执行少于 10 分钟，符合 30 分钟窗口。

## 自动调优逻辑

### 内容与论文优先级

对 `topic`、`institution`、`venue`、`paper_type`、`image_pattern` 建立分组后验，采用贝叶斯平滑：

`group_lift = (group_QS7_mean * n + account_QS7_mean * 12) / (n + 12) - account_QS7_mean`

- 分组样本 `< 6`：不调整，只显示“样本不足”。
- 样本 `≥ 6` 且 90% 置信下界 `> +0.15`：在候选论文基础分上加 `+0.05`。
- 样本 `≥ 6` 且 90% 置信上界 `< -0.15`：基础分减 `-0.05`。
- 每次权重变化最多 `±0.05`，每 7 天更新一次，总上限 `±0.15`。

这样，例如“推荐系统 + 原始架构图”的收藏率持续更高时会获得小幅优先级提升，但不会因 1–2 篇爆款改变整个选题方向。

### 负反馈与降级

以下任一条件触发“降低该组合的发布频率”，不是删除历史或屏蔽方向：

1. 分组至少 6 篇，连续两个 7 日窗口的 `QS7` 后验上界低于账号中位数 15%。
2. `SR` 连续 6 篇低于账号 25 分位，而论文核验、封面和链接均无错误。
3. 同一方向 14 天内发布至少 4 篇且其 `FLR` 明显下降，触发 14 天冷却期。
4. 评论中出现事实错误纠正并经人工确认：该论文卡片标记 `needs_correction`，暂停同类自动候选，先修订事实抽取规则。

任何降级只影响未来草稿排序；不自动删除或修改已发布笔记。

### 发布时间自优化

按第 3 章的三个时段保留 `QS7` 后验。总样本至少 28 篇、每个时段至少 7 篇后，采用 UCB：

`slot_score = posterior_mean(QS7) + 0.20 * posterior_uncertainty`

选择得分最高时段，同时强制 30% 探索概率。连续两周某时段的后验下界低于最佳时段 15% 时，将其降为每周一次探索；账号总体 `QS7` 连续两周下降 25% 时回退到均衡探索。

## 数据存储设计

使用 SQLite 保存可查询数据，JSONL 保存不可变原始证据：

```sql
CREATE TABLE posts (
  note_id TEXT PRIMARY KEY,
  paper_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  published_at TEXT NOT NULL,
  time_slot TEXT NOT NULL,
  topics_json TEXT NOT NULL,
  features_json TEXT NOT NULL,
  content_hash TEXT NOT NULL
);

CREATE TABLE metric_snapshots (
  note_id TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  age_hours INTEGER NOT NULL,
  views INTEGER, likes INTEGER, collects INTEGER,
  comments INTEGER, replies INTEGER, shares INTEGER, follows INTEGER,
  traffic_json TEXT, audience_json TEXT,
  raw_path TEXT NOT NULL,
  PRIMARY KEY (note_id, age_hours)
);

CREATE TABLE decisions (
  decision_id TEXT PRIMARY KEY,
  made_at TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  previous_value REAL, next_value REAL,
  evidence_json TEXT NOT NULL,
  rollback_at TEXT
);
```

原始文件位于 `data/feedback/raw/<date>.jsonl`，规范化库位于 `data/feedback/feedback.sqlite`，每次调优决策另存 `data/feedback/decisions/<date>.json`。因此任何一次权重变化都能回放到原始指标。

## 实施与安全边界

1. 先实现只读采集、JSONL/SQLite 和周报，不改变任何论文筛选权重。
2. 观察 28 篇发布笔记后启用小幅、可回滚的优先级调整。
3. 只读任务不发送评论、不点赞、不关注、不删除笔记；发布任务仍需现有审核闸门。
4. 页面结构变化、登录失败、字段缺失或采集限流时，记录 `collection_failed` 并等待下一窗口，不循环重试。

## 可实施性

**5/5；预计 2.5 个工作日。** 第 1 天完成 OpenCLI 采集和原始快照；第 2 天完成 SQLite、指标与周报；第 3 天半天实现平滑权重、回滚记录与时段选择。无需新增付费服务。
