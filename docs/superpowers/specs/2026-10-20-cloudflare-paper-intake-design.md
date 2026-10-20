# GitHub Pages 单篇论文上传链路设计

日期：2026-10-20  
状态：已完成设计评审，待实施计划  
适用仓库：`recommendation-system-learning` 与 `enkidulove90-lang.github.io`

## 1. 目标

在现有 GitHub Pages/Hexo 网站中加入“上传论文”按钮。站长使用 GitHub 账号完成身份验证后，可在当前页面的弹窗中提交论文链接或 PDF。提交任务由本机 Python Worker 异步处理，依次完成下载、去重、MinerU 解析、DeepSeek 文章生成、自动分类、质量校验、Notion 发布和 GitHub Pages 同步。

首版只解决单篇论文完整链路，不进行与链路无关的目录重构，也不提供公共投稿、多人权限或独立后台页面。

## 2. 已确认的产品约束

- 保留现有 GitHub Pages 前端，不迁移到独立管理站。
- 上传入口是网站左侧导航中的按钮，点击后在当前页面打开弹窗。
- 仅使用 GitHub 账号鉴权，且只允许站长本人提交和查看任务。
- 支持论文链接和本地 PDF 两种输入。
- 本机 Worker 主动领取任务，不开放本机公网端口。
- 本机离线时任务和 PDF 保留在 Cloudflare，重新上线后继续处理。
- Notion 页面状态默认写成 `Published`，不增加人工审核等待阶段。
- 网站任务抽屉默认收起，只露出右侧窄标签；悬浮或点击时从右向左滑出。
- 任务抽屉只有“处理中”和“已完成”两个分组。失败任务进入“已完成”，标记“未发布”并提供重试。
- 不提交 PDF、MinerU 缓存、解析中间产物、运行日志或密钥。

## 3. 系统边界

### 3.1 GitHub Pages

职责：

- 渲染上传按钮、链接/PDF 弹窗和任务抽屉。
- 发起 GitHub 身份登录。
- 上传文件、提交链接、读取任务状态和请求重试。
- 展示安全的用户提示，不展示服务器堆栈、内部路径或密钥。

GitHub Pages 不执行 MinerU、DeepSeek、Notion 或 GitHub API 调用，也不保存长期凭据。

### 3.2 Cloudflare 控制面

使用以下资源：

- Access：通过 GitHub identity provider 验证站长身份。
- Worker：提供统一接入 API、会话交换、任务领取、状态更新和发布触发。
- D1：保存论文身份、任务状态、租约、重试次数和发布关联。
- R2：保存原始 PDF、MinerU Markdown、论文图片、最终 Markdown 和必要日志摘要。

首版不强制使用 Cloudflare Queue。D1 的任务表提供可靠的待领取队列；本机 Worker 通过原子领取和租约避免重复处理。若以后需要多个并发 Worker，再引入 Queue。

### 3.3 本机 Python Worker

职责：

- 使用独立机器凭据主动轮询可领取任务。
- 下载 R2 输入并调用现有 `paper_intake` 管线。
- 定期续租，写入阶段检查点和安全日志摘要。
- 上传产物到 R2。
- 创建或更新 Notion 页面，状态直接设为 `Published`。
- 把 Notion Page ID、文章 slug 和产物地址回报给 Cloudflare。

本机 Worker 不监听公网请求。进程退出或电脑离线后，租约到期的任务可被重新领取并从最近检查点继续。

### 3.4 Notion 与 GitHub Actions

- Notion 是最终文章内容和发布状态的主库。
- R2 是 PDF、原图和解析产物的主存储；Notion 只保存文章内容、元数据及对象链接。
- Cloudflare 在任务完成后触发网站仓库的 GitHub Actions。
- 已有 `tools/notion_sync.py` 继续只同步 `Published + Post`。
- GitHub Actions 构建成功后部署 Hexo；构建失败时保留线上上一版本。

## 4. 数据模型

### 4.1 Paper

一篇论文的稳定身份：

- `paper_id`
- `doi`
- `arxiv_id`
- `canonical_url`
- `normalized_title`
- `title_fingerprint`
- `pdf_sha256`
- `created_at`
- `updated_at`

去重顺序固定为：DOI → arXiv ID → PDF SHA-256 → 规范化标题指纹。命中已有论文时返回现有 `paper_id`，不新建 Notion 页面或网站文章。

### 4.2 Job

- `job_id`
- `paper_id`
- `input_type`：`url` 或 `pdf`
- `input_ref`：规范化链接或 R2 object key
- `stage`
- `status`
- `attempt`
- `lease_owner`
- `lease_until`
- `last_error_code`
- `last_error_message`
- `created_at`
- `updated_at`

内部状态可细分，但前端只映射为两类：

- 处理中：`queued`、`claimed`、`stored`、`parsed`、`generated`、`validated`、`publishing`。
- 已完成：`published`、`failed`、`cancelled`。

### 4.3 Artifact

- `artifact_id`
- `paper_id`
- `job_id`
- `kind`：PDF、MinerU Markdown、图片、生成文章或日志摘要
- `r2_key`
- `sha256`
- `size_bytes`
- `content_type`
- `created_at`

原始输入不可被重试覆盖。生成产物按阶段和 attempt 保存，成功版本由 publication 记录引用。

### 4.4 Publication

- `paper_id`
- `notion_page_id`
- `slug`
- `site_url`
- `git_commit`
- `publish_status`
- `published_at`

发布重试复用相同 Notion Page ID 和 slug，不重新生成正文。

## 5. API 边界

### 5.1 浏览器 API

- `GET /v1/session/start`：进入 GitHub/Access 登录。
- `POST /v1/session/exchange`：交换一次性授权码，取得短期应用会话。
- `POST /v1/intake/url`：提交论文链接。
- `POST /v1/intake/pdf`：流式上传 PDF 并创建任务。
- `GET /v1/jobs`：读取站长任务列表。
- `GET /v1/jobs/{job_id}`：读取单个任务状态。
- `POST /v1/jobs/{job_id}/retry`：重试失败任务。

上传上限为 50 MB，只接受 PDF MIME、PDF 文件签名或允许的论文链接。R2 object key 由服务器生成，浏览器不能指定任意存储位置。

### 5.2 本机 Worker API

- `POST /v1/worker/jobs/claim`
- `POST /v1/worker/jobs/{job_id}/heartbeat`
- `POST /v1/worker/jobs/{job_id}/checkpoint`
- `POST /v1/worker/jobs/{job_id}/complete`
- `POST /v1/worker/jobs/{job_id}/fail`
- `GET /v1/worker/artifacts/{artifact_id}/download`
- `POST /v1/worker/artifacts/upload`

本机 Worker 使用独立机器身份，不复用浏览器会话。领取操作必须是原子的；租约初始 10 分钟，每 60 秒续租。租约过期后任务才能被其他 Worker 重新领取。

### 5.3 返回格式

所有接口使用统一 envelope：

```json
{
  "ok": true,
  "request_id": "request identifier",
  "paper_id": "paper identifier",
  "job_id": "job identifier",
  "status": "queued",
  "code": null,
  "message": "论文已进入处理队列",
  "retryable": false
}
```

错误响应不包含服务器堆栈、密钥、R2 内部签名或本地绝对路径。

## 6. 状态机与恢复

处理阶段为：

`received → stored → parsed → generated → validated → publishing → published`

规则：

- 每个阶段成功写入检查点后才能进入下一阶段。
- 同一阶段最多自动重试三次，使用指数退避。
- 本机中断后从最近成功检查点继续，不重复执行已确认的昂贵阶段。
- 下载失败、MinerU 失败、DeepSeek 失败、质量门禁失败、Notion 失败和部署触发失败使用不同错误码。
- 质量门禁失败不得创建 Published 页面。
- Notion 已成功但 GitHub Actions 触发失败时，只重试发布触发，不重新生成文章。
- 失败任务进入前端“已完成”分组，显示“未发布”和重试操作。

## 7. 身份与安全

- Access 仅允许已批准的 GitHub 身份。
- 由于 GitHub Pages 与 API 是跨站来源，登录使用顶层弹窗完成。API 将 Access 已验证身份交换为一次性授权码，再由页面取得短期 bearer session；不依赖长期第三方 cookie。
- 短期会话仅保存在页面内存或 `sessionStorage`，不得放入源码或构建产物。
- CORS 只允许 `https://enkidulove90-lang.github.io`、`http://127.0.0.1:4322` 和明确列出的本地测试源。
- PDF 上传必须校验 Content-Type、文件签名、大小和 object key。
- Notion、DeepSeek 和 MinerU 配置只在本机 `.env` 中。
- GitHub 发布凭据存入 Cloudflare secret 或 GitHub secret，不进入浏览器。
- Worker 机器凭据与浏览器会话分离，可单独吊销和轮换。
- 用户曾在对话中暴露过 Notion token；实施前应轮换该 token，但规范和日志不得记录旧值。

## 8. 网站交互

### 8.1 上传入口

- 左侧导航增加“＋ 上传论文”。
- 按钮可公开看见，但只有站长能通过 GitHub 身份验证。
- 验证成功后在当前页面打开弹窗，不跳转 `/admin/` 或独立端口。
- 弹窗提供“论文链接”和“上传 PDF”两个页签。

### 8.2 任务抽屉

- 默认收起，仅在页面右侧显示窄标签和未完成数量。
- 鼠标进入标签后向左展开；鼠标从标签进入抽屉时保持展开。
- 离开整个热区后短延迟收起，避免移动过程闪退。
- 点击标签后锁定展开，点击关闭按钮或页面空白处收起。
- 移动端没有 hover，只使用点击开关。
- 抽屉只含“处理中”和“已完成”两个分组。
- 成功卡片显示文章链接；失败卡片显示“未发布”、简洁原因和重试按钮。
- 完成事件不弹出阻塞阅读的大遮罩。

## 9. 仓库改造边界

### 9.1 `recommendation-system-learning`

首版围绕现有 `paper_intake/` 增量扩展：

- 增加 Cloudflare gateway 工程、D1 migration 和资源配置。
- 增加远程任务客户端及本机 Worker 入口。
- 复用现有 inputs、repository、pipeline、article 和 adapters。
- 现有本机 FastAPI 页面在端到端验收前保留，作为回滚路径。
- 验收后再以独立提交删除 8765 管理界面；不在本阶段先移动所有目录。

### 9.2 `enkidulove90-lang.github.io`

- `_config.butterfly.yml` 注入上传组件资源。
- `source/js/paper-intake.js` 负责登录、弹窗、上传和任务抽屉。
- `source/css/paper-intake.css` 负责响应式界面和抽屉动画。
- 构建期只输出公开 API base URL，不输出密钥。
- 不创建独立 `/admin/` 页面。
- 继续使用现有 `tools/notion_sync.py` 和 `.github/workflows/publish.yml`。

两个仓库只通过 `job_id`、`paper_id`、Notion Page ID、R2 object URL 和 GitHub dispatch event 连接，不使用本机绝对路径互相引用。

## 10. 测试与验收

### 10.1 自动测试

- D1 repository：原子领取、租约、续租、过期回收和幂等去重。
- Gateway：身份检查、CORS、链接校验、PDF 校验、50 MB 上限和统一错误格式。
- Worker：断点恢复、三次重试、阶段不重复和产物哈希校验。
- 网站：弹窗、上传页签、抽屉 hover/click、移动端点击、两分组映射和错误重试。
- 发布：Notion 直接 Published、重复发布复用页面、dispatch 失败只重试发布。
- 回归：现有 53 个 intake 测试、51 个 redbook 测试、网站 Python/Node 测试和 Hexo build 均通过。

### 10.2 单篇端到端验收

使用一篇合法可下载或用户直接上传的 PDF：

1. 从 `127.0.0.1:4322` 弹窗提交。
2. 未授权 GitHub 账号被拒绝。
3. PDF 进入 R2，D1 中出现唯一 paper/job。
4. 本机 Worker 领取并完成 MinerU、DeepSeek 和质量门禁。
5. Notion 创建 `Published + Post` 页面。
6. GitHub Actions 构建成功。
7. 新文章出现在首页、分类和搜索中；若论文已解析出可靠机构或会议地点，也进入相应地图数据。
8. 重复上传返回同一论文身份，不生成第二篇。
9. 中途停止 Worker，再启动后从检查点继续。

## 11. 上线与回滚

实施使用 `codex/cloudflare-paper-intake` 分支，并按以下边界提交：

1. 设计规范。
2. Cloudflare gateway、D1、R2 和测试。
3. 网站弹窗与任务抽屉。
4. 本机 Worker 远程任务适配。
5. Notion Published 与 GitHub Actions 发布链路。
6. 端到端验收和独立旧 UI 清理。

回滚策略：

- 网站组件可通过移除注入配置完全关闭，不影响已有文章。
- Cloudflare API 可暂停新任务，D1/R2 数据保留。
- 本机 Worker 可停止而不丢任务。
- 发布失败不覆盖上一版 GitHub Pages。
- 旧 8765 页面在新链路验收前保留。

## 12. 非目标

首版不实现：

- 公共投稿和邀请制多用户。
- 云端 MinerU/GPU Worker。
- 批量论文上传。
- 定时抓取不同论文网站。
- 多 Worker 调度和 Cloudflare Queue。
- 论文内容的人工审核工作流。
- 全仓库目录重构。

这些能力必须在单篇论文链路稳定后分别设计和实施。
