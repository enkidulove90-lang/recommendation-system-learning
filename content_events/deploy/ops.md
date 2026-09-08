# content_events 部署与运维手册

## 1. 组件边界
`content_events` 是内容生命周期编排层，把 `publish_queue/<id>/<platform>.json` 静态内容包驱动为可观测、幂等、可回滚的事件流：
`intake → render(DTLE) → validated → staged → [人工 publish] → feedback`。

- **不负责**内容生产（DTLE 渲染、配图在 `wechat_design`/`redbook` 侧完成）。
- **不自动发布**：任何定时/服务模式默认只 `stage`（写本地待发布包）或降级 `needs_review`。
- **反馈采集只读**：不点赞/评论/关注/删帖。

## 2. 三种运行形态
| 形态 | 命令 | 适用 |
|------|------|------|
| CLI | `python content_events/cli.py process-queue --root . --publisher dryrun` | 本地/CI 一次性执行 |
| REST | `uvicorn content_events.serve:app --port 8080` | 调度器/远程触发 |
| 流水线钩子 | `python run_batch_pipeline.py --step 7`（或 `all`） | 论文解析全链路尾部 |

## 3. Docker 部署
```bash
docker compose -f content_events/deploy/docker-compose.yml up --build
curl http://localhost:8080/health
```
- 镜像仅含运行 `serve.py` 所需源码 + fastapi/uvicorn，不含语料大文件。
- `publish_queue/`（ro）与 `data/`（rw）以卷挂载；事件日志/反馈库/幂等注册表落在 `data/`。
- 默认 `dry_run=True`。真实 stage 需请求体显式 `dry_run=false` 且宿主机具备登录态。

## 4. 健康检查与监控
- `GET /health` → `{"status":"ok"}`；接入 LB 探活。
- 每轮 `process-queue` 返回 `RunSummary`（`scanned/processed/skipped_idempotent/published/errors/...`），`errors>0` 时 CLI 退出码 1、REST 返回 200 但 `summary.errors>0`（调用方需自行判读）。
- 事件审计：`data/content_events/events.jsonl`（损坏行可容忍，落地 fsync）。

## 5. 安全边界（强制）
1. 禁止任何非交互通道自动 `publish`；仅 `stage`/`dryrun`。
2. 网络/登录/审核失败 → `needs_review`，不自动重试（仅瞬时错误重试，永久错误直转）。
3. 幂等键 `paper_id::platform::content_hash` 防重复 stage；全局注册表 `data/content_events/idem_registry.jsonl`。
4. 反馈采集只读；`decide_once` 仅产出自优化决策写入 `decisions` 表，不执行任何写操作类动作。

## 6. 回滚与排障
- 单条失败不影响整轮（RunSummary 记录 `errors` 与 `skipped_detail`）。
- 状态机不随意跳变；`state.json` 原子写（tmp+os.replace）。
- 重新处理：删除 `idem_registry.jsonl` 中对应 `idem_key` 行即可（慎用于已 published 项）。
- 日志：`python -m content_events.cli ...` 已 `logging.basicConfig(INFO)`；REST 服务日志在容器 stdout。
