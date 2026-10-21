# 论文收录链路凭据运行规范

## 信任域与最小权限

| 凭据 | 只允许的用途 | 建议轮换 | 吊销后验证 |
|---|---|---:|---|
| Intake machine token | Worker 领取、心跳、checkpoint、完成任务 | 90 天；泄露立即 | 旧 token 返回 401，新 token 的 `/v1/worker/health` 返回 200 |
| DeepSeek API key | 余额查询与文章生成 | 90 天；余额异常或泄露立即 | `/user/balance` 可用，旧 key 返回 401 |
| Notion integration token | 目标数据库读写 | 180 天；泄露立即 | 目标 data source schema 可读，旧 integration 不再能访问数据库 |
| GitHub 发布凭据 | 仅目标仓库触发 `repository_dispatch` | GitHub App installation token 自动约 1 小时；App 私钥 90 天 | 目标仓库权限为 Contents: write，旧私钥/令牌失效 |
| Pages callback token | Actions 回写指定发布任务 | 90 天；泄露立即 | 新 token 回调成功，旧 token 返回 401 |
| GitHub OAuth client secret | 仅站点所有者登录 | 180 天；泄露立即 | 新登录成功，旧 secret 不能兑换 access token |
| Session signing key | 浏览器会话签名 | 90 天；泄露立即 | 新会话有效，旧会话按计划失效 |

轮换周期是本项目的运维上限，不代表供应商凭据的自然过期时间。负责人默认为仓库所有者；任何自动化不得打印或回传明文。

## 双钥轮换步骤

1. 在供应商创建新凭据，不删除旧凭据。
2. 将新值写入对应 Secret 存储；本地 Worker 使用服务管理器或受保护的进程环境，Cloudflare 使用 `wrangler secret put`，GitHub 使用 Actions Secrets。
3. 运行只读预检：DeepSeek 余额、Notion schema、Cloudflare machine health、GitHub 目标仓库与发布权限。
4. 让 Worker 受控停止领取新任务，等待当前租约结束，再重启加载新凭据。不要对运行中的 Python 进程使用 `importlib.reload`。
5. 完成一条不产生重复内容的冒烟任务并核对 D1、Notion、Pages 状态。
6. 吊销旧凭据，再确认旧凭据返回 401/403。
7. 审计日志只记录凭据类型、版本标识或末四位，绝不记录完整值。

## 结构化失败码

- `deepseek_balance_low`：余额不可用，不领取新任务。
- `deepseek_auth_rejected`：401/403，轮换 Key。
- `deepseek_rate_limited`：429，可退避重试。
- `deepseek_unreachable`：DNS、代理、TLS 或 5xx，可重试并告警。
- `notion_schema_mismatch`：数据库缺少 `title/status/type/slug`，禁止写入。
- `lease_lost`：当前执行者失去所有权；这是 warning，不是任务失败终态。
- `github_dispatch_failed`：发布触发失败，任务保持可对账/可重试，不得假报 published。

## 当前迁移约束

- 业务幂等键依次使用 arXiv ID、稳定 slug；标题只用于人工候选匹配，不能自动合并。
- D1 是任务状态唯一事实源，本地 SQLite 仅是执行缓存，Notion 是文章内容事实源，Pages 是公开可达性的事实源。
- 当前长期 `GITHUB_TOKEN` 应迁移到 GitHub App installation token。完成 App 安装与私钥托管前，不得声称短期凭据方案已经上线。
- 下一阶段必须增加 `lease_id/lease_epoch` fencing、发布 outbox 和 `publish_attempt_id`；在此之前固定 Worker ID 的并发重启不安全。
