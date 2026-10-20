# 论文自动收录：部署与运维手册

这套链路保留 GitHub Pages/Hexo 作为公开网站，以 Cloudflare Worker、D1 和 R2 作为统一接入层，本机 Worker 执行 MinerU、DeepSeek 与 Notion 发布。公开网页只得到 API 地址；所有令牌均留在 Cloudflare、GitHub Secrets 或本机 `.env` 中。

## 数据流

```text
GitHub.io「收录论文」按钮
  → Cloudflare Access（只允许站点所有者的 GitHub 身份）
  → Worker 接收 URL/PDF，D1 去重并记录任务，R2 暂存原始 PDF
  → 本机 remote-worker 领取带租约任务
  → MinerU 解析与提图 → DeepSeek 生成 → 质量门禁
  → Notion 直接写入 Published + Post
  → Worker 触发 repository_dispatch
  → GitHub Actions 同步 Notion、构建并发布 Pages
  → Actions 回调 Worker，任务进入「处理完成」
```

失败任务显示为“未发布”，可在网站任务抽屉中重新处理。重复 DOI、arXiv ID、规范化 URL 或 PDF SHA-256 会复用已有论文/任务，不会生成第二篇在线文章。

## 首次部署

### 1. 先轮换暴露过的凭据

曾在聊天、日志或截图中出现过的 Notion token 必须先在 Notion 后台撤销并重新生成。更新本机和 GitHub Secrets 后再运行真实论文。不要把 token 粘贴到命令历史、Markdown、截图或 Git 提交中。

### 2. 创建 Cloudflare 资源

在 `paper_intake/cloudflare` 目录执行：

```powershell
npx wrangler login
npx wrangler d1 create paper-intake
npx wrangler r2 bucket create paper-intake-artifacts
```

把 D1 创建命令返回的 `database_id` 写入 `wrangler.jsonc`，不要修改绑定名 `DB`。R2 绑定名必须保持 `ARTIFACTS`。

通过交互式输入设置四个 Worker secret；不要把值写入仓库：

```powershell
npx wrangler secret put SESSION_SIGNING_KEY
npx wrangler secret put WORKER_TOKEN
npx wrangler secret put GITHUB_TOKEN
npx wrangler secret put PUBLISH_CALLBACK_TOKEN
npx wrangler d1 migrations apply paper-intake --remote
npx wrangler deploy
```

建议使用相互独立的高熵随机值作为会话签名、机器 Worker 和发布回调令牌。`GITHUB_TOKEN` 使用仅能向目标仓库发送 `repository_dispatch` 的细粒度 PAT。

在 Cloudflare Zero Trust 中只保护 `/v1/session/start*`：身份源选 GitHub，策略仅允许站点所有者账号。不要把机器接口放在浏览器 Access 跳转之后；机器接口已经使用单独 Bearer token。

生产变量 `ALLOWED_ORIGINS` 只保留：

```text
https://enkidulove90-lang.github.io,http://127.0.0.1:4322
```

域名必须精确匹配，不使用 `*`。

### 3. 配置 GitHub Secrets

网站仓库需要：

- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`
- `PAPER_INTAKE_API_BASE`：部署后的 Worker HTTPS 根地址，不含末尾 `/`
- `PAPER_INTAKE_CALLBACK_URL`：通常与 API 根地址相同
- `PAPER_INTAKE_CALLBACK_TOKEN`：与 Worker 的同名回调 secret 完全一致
- `CARTO_API_KEY`：现有地图构建所需

网站构建脚本只把 `PAPER_INTAKE_API_BASE` 输出到 `/paper-intake-config.json`；测试会阻止 token/secret 被写入该文件。

### 4. 配置本机 Worker

项目根目录 `.env` 至少包括：

```dotenv
PAPER_INTAKE_API_BASE=https://<worker-domain>
PAPER_INTAKE_WORKER_TOKEN=<与 Cloudflare WORKER_TOKEN 相同>
MINERU_API_KEY=<local-only>
DEEPSEEK_API_KEY=<local-only>
NOTION_TOKEN=<rotated-token>
NOTION_DATABASE_ID=<database-id>
```

启动：

```powershell
python -m paper_intake remote-worker
```

进程可以安全重启。任务租约会阻止两台机器同时处理同一任务，阶段 checkpoint 会避免已经成功的 MinerU 等步骤被重复执行。

## 日常使用

1. 打开站点导航栏的“收录论文”。
2. 选择公开 HTTPS 链接或不超过 50 MB 的 PDF。
3. 使用 GitHub 所有者身份登录；浏览器凭据只存于 `sessionStorage`，关闭会话后不会长期保留。
4. 提交后从右侧“任务”抽屉观察“处理中/处理完成”。
5. 失败卡片显示“未发布”和脱敏错误，可点击“重新处理”。

状态含义：

- `queued/processing/publishing` → 处理中
- `published` → 处理完成
- `failed/cancelled` → 处理完成（其中 failed 明确标记未发布）

## 恢复与排错

### 本机 Worker 中断

直接重启 `python -m paper_intake remote-worker`。旧租约最长 15 分钟到期；不要手工删除 D1 行或清空 checkpoint。若日志报告 `lease_lost`，停止该次本地处理，让当前租约持有者继续。

### MinerU 或 DeepSeek 失败

保留任务和 R2 原始输入，在网站点击“重新处理”。只清除确实损坏的对应 checkpoint，禁止通过新建重复任务绕过去重约束。

### Notion 已发布但 Pages 失败

任务会收到 Actions 失败回调并显示“未发布”。修复 Actions 或 Secrets 后点击重新处理。Notion 写入具有幂等标识，不应新建第二页。

### Pages 已发布但回调丢失

重新运行对应的 `repository_dispatch` workflow，或以相同 `job_id` 再次发送带鉴权的回调。回调是幂等的，重复成功回调只保留一个 `publication.completed` 事件。

### 回滚 Cloudflare Worker

使用 Wrangler 的部署版本回滚能力恢复上一版本；D1 migration 只做向前兼容变更，不直接删除表或列。回滚期间可以停止本机 Worker，已提交任务仍保留在 D1/R2。

### 临时关闭网页入口

从 `_config.butterfly.yml` 的 `inject` 中移除 `/css/paper-intake.css` 与 `/js/paper-intake.js`，重新构建网站即可。此操作不会删除 D1、R2、Notion 内容或正在处理的任务。

## 单篇验收清单

上线前只使用一篇可合法下载的测试论文：

- 从网页 PDF 模式提交，确认得到一个 `paper_id/job_id`。
- 启动 Worker，在 MinerU checkpoint 完成后中断并重启，确认不重复解析。
- 确认生成内容通过图片、引用与文章结构门禁。
- 确认 Notion 仅有一个 `Published + Post` 页面。
- 确认 `repository_dispatch` 完成 Pages 构建，任务进入“处理完成”。
- 再次上传相同 PDF，确认返回原 `paper_id`，且线上没有重复文章。
- 执行 `git status --short`，确认没有 PDF、解析图片、SQLite、`.dev.vars` 或 token。

验收成功之前保留旧的 8765 本机控制台作为回退入口；只有完整链路通过后才删除其 HTML、静态资源和人工审核接口。
