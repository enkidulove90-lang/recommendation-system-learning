# 小红书投递链路系统设计现状评估（基于真实代码库填写）

> 填写日期：2026-11-19
> 基线：主工作区 detached HEAD `0d8dd49`，`redbook/` 目录为唯一投递管线载体。
> 填写原则：每条结论均附代码证据路径；不存在的模块直接标注"未实现"，不夸大、不虚构。

> **experiments 基线差异附注（2026-11-19，`9fec8b8`）**：本文主体保留
> `0d8dd49` 的历史评估结论，不能用来描述已推进的 experiments 工作树。该分支已实现
> `redbook.infrastructure.delivery_errors` 的七个基础 E_* 码、per-slug
> `delivery_registry.json`、OpenCLI preflight、`note --save-draft` 与
> `note --verify`。因此主体中"delivery_registry 不存在"、"错误码表未实现"、
> "无 save-draft"、"无验证 CLI"四项在 experiments 基线下均已过时；错误码的
> retryable/next_step/owner envelope、`E_VERIFY_UNCERTAIN` 等扩展，以及 SQLite
> registry 迁移、队列/并发/收件箱仍未完成，继续以 devplan 的 M2/M3/M1/M4/M5 为准。

---

## 一、设计哲学：项目实际遵循的核心原则

### 1.1 内容与平台解耦 —— 已落实

- 内容以声明式规格 `redbook/notes/<paper_id>.yaml`（`redbook/services/note_spec.py`）承载，自身带 draft/validated/staged/published 四态，不绑定任何平台。
- 正文规则在 `redbook/services/content_spec.py`：冻结 7 段题头、标题 20 字硬预算、禁 Markdown、禁 `#`（因平台把 `#` 解析为话题），校验失败返回具名失败码——平台约束沉淀在内容规格层而非投递脚本。
- 投递侧统一为 `Publisher` Protocol（validate / stage / publish 三段契约，`redbook/automation/publishing.py` L52-57）；`paper_to_xhs.py` 与 `paper_to_wechat.py` 各自把同一份 11 维摘要渲染为平台产物，互不依赖对方代码。

### 1.2 默认只存草稿，不自动发布 —— 已落实（硬约束）

- XHS 投递恒为草稿：`--draft true` 硬编码（`publishing.py` L355）；`redbook/cli.py save-xhs-draft` 回执 `state: "saved_draft_only"`（L119）。
- `note` 命令默认 action 是 `validate`（cli.py L72/L134，注释明确写 "the safe default"），需显式 `--publish` 才写草稿箱。
- `redbook/automation/build_xhs_draft.py --publish` 默认 False（L90-106，缺省只 stage 不投递）。
- 微信侧同样"只写入草稿箱，不群发"（`publishing.py` L95 docstring）。
- 全链路无任何"直接发布到公域"的代码路径。

### 1.3 失败必须附带原因和下一步操作 —— 部分落实

- 已有：失败统一返回 `{"ok": false, "error": ..., "method": ...}`（`publishing.py` L370-374、`xiaohongshu_delivery.py` L187）；HTML 预览兜底路径附带 `save_unverified` + note 说明（`publishing.py` L183-188）；`FilePublisher.publish` 返回 `manual_review_required`（L91）；适配器抛 `DeliveryError` 带场景描述（如未登录时 `paper_to_xhs.py` L605-608 直接拒绝投递）。
- 差距：返回体中**没有统一的 `next_step` / `retry` 字段**，也没有绑定处置策略的错误码表（E_* 系列——属开发计划 M2，尚未实现）。"下一步操作"目前靠 error 字符串隐式表达。

### 1.4 任务有状态机与幂等键，支持断点续跑 —— 部分落实

- 已有：
  - `WorkflowCheckpoint`（`redbook/application/paper_workflow.py` L23-35）：checkpoint 落盘 `data/workflow_state/<paper_id>/checkpoint.json`，**状态机禁止回退**（L29-30），重入即续跑。
  - 幂等键三层：采集层 `canonical_id`（doi/arxiv/openreview/dblp/title-hash 归一，`automation/sources.py` L77-84）+ jaccard 标题去重；stage 层 `content_hash[:32]` 作为 staged_id，同 hash 幂等返回 `already_staged`（`publishing.py` L80-86）；回执层 `draft_id`（`xiaohongshu_delivery.py` L154）。
- 差距：`draft_id` 与 staged_id 之间**没有对账注册表**——`delivery_registry.json` 全仓不存在（属开发计划 M3，未实现）；`draft_id` 只出现在回执日志，不参与重跑判断。

### 1.5 生成可并行、保存需限流 —— 以"串行单会话"隐式实现，未代码化

- "生成可并行"事实成立但未主动并行：各论文的状态隔离在 `data/workflow_state/<paper_id>/`，理论上可多进程并行跑 CLI；当前代码为顺序执行，无并发调度器。
- "保存需限流"**没有显式限流代码**：全仓无 QPS/节流；现存 `time.sleep` 均为等待而非限流（PDF 上传轮询 0.5s `xiaohongshu_delivery.py` L465、登录轮询 `scripts/login_qr.py` L161）。实际防线是**单持久会话 + 固定平台操作顺序**（topics → PDF → draft，`publishing.py` L290-293 docstring 明言为平台约束）+ 三级保存 fallback（L545-566）+ 300s/270s 超时预算（`opencli_runtime.py` L66-75 经 `OPENCLI_BROWSER_COMMAND_TIMEOUT` 上调）。串行本身就是当前对平台的唯一"限流"。

### 1.6 低运维、少组件、自愈 —— 基本落实（自愈靠人工）

- 纯 CLI + 文件系统状态：`data/workflow_state/`（checkpoint）、`data/publish_queue/<content_hash>/`（stage 产物）、`data/state/sources/`（采集 cursor）、`data/inbox/`（原始记录）、`data/publish_preview/`（HTML 兜底）。唯一数据库是本地 SQLite（`data/feedback/feedback.sqlite`，无服务端）。
- 日志：`redbook/infrastructure/run_log.py` 结构化 JSONL 追加 `data/logs/runs.jsonl`，线程锁 + 幂等 handler + 自带查看器子命令（L153），**明言不做日志轮转**——刻意少组件。
- 无后台常驻服务；唯一外部进程依赖是 OpenCLI daemon（复用已登录 Chrome）。
- "自愈"现状：登录态探针 `probe_login` 用真实鉴权读操作（`xiaohongshu drafts`）代替易误判的 whoami（`opencli_runtime.py` L219-242）、`scripts/login_qr.py` 扫码重登、HTML 预览兜底人工上传——均为**人工触发**，无自动重试/自动恢复。

### 1.7 平台适配器隔离平台差异 —— 已落实（隔离方式是"契约 + 镜像"，非继承）

- `infrastructure/xiaohongshu_delivery.py`（`OpenCliXiaohongshuDelivery`）与 `infrastructure/wechat_delivery.py`（`WeChatDraftDelivery`）结构镜像，共享 `Publisher` Protocol 契约与 `DeliveryError`/回执模式，但**无公共基类**，各自独立实现。
- 平台特有事实内聚在各自适配器内：XHS 侧——话题必须绑真实实体、无实体抛 `TopicEntityUnavailable` 终态（L297-341）、CDP fetch/XHR hook 探测 PDF 上传（L439-465）、保存三级 fallback（L545-566）；WeChat 侧——弃用 `opencli weixin create-draft`（标题丢失/Markdown 直出，docstring 有留档）、以 `#js_save_success` 保存灯判定成功（L68）。
- 统一驱动方式：两者都走 `opencli_runtime.py` 定位并直调 `@jackwener/opencli` 的 browser-bridge（CDP），复用已登录 Chrome，不逆向 API、不依赖 playwright。

### 1.8 平台事实显式化、验证不过即回滚 —— 已落实

- 验证强约束：XHS 保存后做"before/after 草稿箱 API 对账，必须恰好一条新草稿"（`xiaohongshu_delivery.py` L231-237）；再重开草稿做 indexedDB+DOM 核对 body/topics/PDF（L467-543）；**不通过即删除该草稿并抛错**（L674-681）。
- 显式豁免：`--skip-pdf-attachment` 与 `--pdf` 互斥、必须显式声明（L53-56），不留隐式默认。
- "不猜"原则：话题无实体不猜名字直接终态失败；`cards.py` 明确"不在 stage 时偷偷写文件"。

---

## 二、理想系统形态：各环节实际实现程度对照

理想链路：内容源 → 内容工作台 → 投递编排器 → 平台适配器 → 平台草稿箱 → 草稿验证与结果收件箱 → 通知与人工接管

| 环节 | 实现程度 | 对应模块 | 现状与差距 |
|---|---|---|---|
| 内容源 | **已实现** | `main.py`（arXiv 爬取→PDF→MinerU→DeepSeek 摘要，11 维 JSON）、`redbook/automation/sources.py`（多源 Protocol + canonical_id 去重 + cursor 增量）、`redbook/application/paper_workflow.py prepare_figures`（三级图片来源：arXiv LaTeX 源码原图 → PDF 高 DPI 重渲染 → MinerU 目录兜底，L37-76） | 成熟度最高；采集侧已有增量与去重 |
| 内容工作台 | **已实现** | `note_spec.py`（声明式 YAML）、`content_spec.py`（7 段/字数/禁 Markdown 校验门，25+ 测试用例）、`cards.py`（PIL 数字卡）、`persona_composer.py`（人设 YAML → PostDraft，无发布副作用） | 工作台即"spec + 校验 + 渲染"三件套，规格冻结；缺的是可视化界面（本就以 CLI 为形态） |
| 投递编排器 | **部分实现** | `redbook/cli.py`（自称"唯一受支持入口"）、`PaperCreationWorkflow`（checkpoint 状态机）、`automation/cli.py`（六章统一 CLI） | 单论文单平台**顺序**执行；无任务队列、无多草稿并发、无统一投递注册表（delivery_registry 未实现）。编排能力停留在"工作流续跑"而非"任务编排" |
| 平台适配器 | **部分实现** | `xiaohongshu_delivery.py`、`wechat_delivery.py`、`opencli_runtime.py` | 两个适配器均可端到端跑通；共享契约但无基类（镜像重复）；无版本兼容矩阵与三层试验（A5，属 devplan 未实现） |
| 平台草稿箱 | **已实现（作为投递目标）** | 同上 | XHS 恒草稿 + WeChat 只写草稿箱，是全链路硬边界 |
| 草稿验证与结果收件箱 | **部分实现** | XHS：草稿箱 before/after 对账 + 重开 DOM 核对 + 不过即删（`xiaohongshu_delivery.py` L231-237/L467-543/L674-681）；WeChat：保存灯校验，未亮灯回退 HTML 预览（`publishing.py` L180-188） | 验证本身很强（XHS 侧），但验证结果只进 `data/logs/runs.jsonl` 与 stdout——**没有"收件箱"式结果汇总**；WeChat 校验强度明显低于 XHS |
| 通知与人工接管 | **通知未实现 / 人工接管部分实现** | 兜底：HTML 预览文件（`publishing.py` L234-281）+ `login_qr.py` 扫码 + `manual_review_required` 回执 | 全仓无 notify/webhook/邮件/桌面通知代码；结果暴露仅 stdout + runs.jsonl。人工接管路径存在但**不会主动唤起**——需人工翻日志才发现失败 |

**总体判断**：链路"两头强、中间薄"——内容生产端与平台投递/验证端已达到可日常使用的工程强度；编排层（并发、注册表、错误码、通知）是当前与理想形态的主要差距，与《xhs_delivery_backend_devplan》M0-M5 的规划一致。

---

## 三、功能清单：逐项核对真实状态

| 功能 | 状态 | 实现方式与证据 |
|---|---|---|
| 内容工作台 | **已实现** | `note_spec.py` 声明式内容规格（四态）；`content_spec.py` 校验门（7 段冻结/标题 20 字/禁 Markdown/禁 `#`）；`cards.py` 数字卡由 spec 的 `card:` 配方声明绘制；`persona_composer.py` 人设合成。测试：`test_note_spec.py`、`test_content_spec.py`、`test_note_migration.py`（14 篇旧脚本迁移一致性） |
| 任务编排（多草稿并发） | **未实现** | 全仓无 ThreadPool/asyncio/任务队列；投递为单会话顺序执行。唯一线程锁在 `run_log.py` L39，仅保护日志写入。`infrastructure/publishing/` 下有 scheduler/strategy（三阶段发布时机策略），但**未被任何投递入口调用**，属死代码（仅 `test_automation.py` 有单测） |
| 多草稿生成 | **部分实现** | "生成"侧天然支持多论文：各论文独立 `data/workflow_state/<paper_id>/checkpoint.json`，`persona_composer.py` 可产出多个 PostDraft，可手动并行起多个 CLI 进程互不干扰；但**无编排器统一管理**并发、进度汇总或失败重试 |
| 人工兜底收件箱 | **部分实现** | 兜底路径存在：OpenCLI/登录不可用 → 本地 HTML 预览文件供人工手动上传（`publishing.py` L234-281，产物在 `data/publish_preview/wechat/`）；`FilePublisher.publish` 返回 `manual_review_required`；`scripts/login_qr.py` 扫码重登。差距：无统一"收件箱"目录或界面聚合所有待人工项，预览文件与失败原因散落在不同目录/日志中 |
| 平台适配器——小红书 | **已实现** | `OpenCliXiaohongshuDelivery`：OpenCLI browser-bridge 驱动已登录 Chrome（CDP）；固定顺序 open composer → 上传图 → 填标题 → execCommand 写正文 → 绑真实话题实体（无实体抛 `TopicEntityUnavailable` 终态）→ CDP 探针传 PDF → 三级 fallback 存草稿；保存后草稿箱对账 + 重开核对，不过即删。测试 `test_xiaohongshu_delivery.py` |
| 平台适配器——微信公众号 | **部分实现** | `WeChatDraftDelivery`：同一 browser-bridge 驱动 mp.weixin.qq.com 真实编辑器；以 `#js_save_success` 保存灯判定，未亮灯回退 HTML 预览。校验强度低于 XHS（无草稿箱对账）；`opencli weixin create-draft` 路线已弃用并留档原因。端到端验证脚本 `validate_wechat_real_paper.py`（2302.08191）/`validate_wechat_template.py` |
| 低运维设计 | **已实现** | 纯 CLI + 文件系统状态（workflow_state/publish_queue/state/sources/inbox）；无后台服务、无服务端数据库（仅本地 SQLite）；`run_log.py` JSONL 自带查看器、明言不做轮转；唯一外部依赖 OpenCLI daemon。代价：恢复类动作（重登、重跑、人工上传）全部人工触发 |
| 省时省力功能 | **部分实现** | 已有：checkpoint 断点续跑、content_hash 幂等 stage（`already_staged`）、采集 cursor 增量（ETag/内容 hash，`sources.py` L173-181）、`probe_login` 真实读操作探针、MCP server 把 note 工具暴露为 MCP（`redbook/mcp/server.py`，不存 cookie）、`multi-platform-publishing` skill（`.agents/skills/`，提交 946e6ea）。未实现：投递结果通知、多草稿并发、定时自动投递（scheduler 未接线）、draft_id↔staged_id 对账注册表 |

---

## 附：本次核对确认"不存在"的模块（防虚构清单）

- `delivery_registry.json` / run_id↔draft_id 对账注册表 —— 未实现（devplan M3）
- 任务队列 / 多草稿并发投递 —— 未实现
- 投递结果通知（notify/webhook/邮件/桌面通知）—— 未实现
- QPS/保存限流代码 —— 未实现（以串行单会话隐式替代）
- 平台适配器公共基类 —— 未实现（契约共享 + 结构镜像）
- 后台常驻服务 —— 无（刻意设计）
- 统一错误码表（E_* 绑定处置/重试策略）—— 未实现（devplan M2）
