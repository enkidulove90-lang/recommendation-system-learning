# content_events · 内容事件编排层

把 `publish_queue/<id>/<platform>.json` 内容包驱动为**可观测、幂等、可回滚**的内容生命周期事件流：
`intake → render(DTLE) → validated → staged → [人工 publish] → feedback`。

- 设计文档：`docs/content-event-orchestration-design.md`（原始提案）+ `docs/content-event-optimization-design.md`（优化方案 O1–O11 / 问题 A–D / 安全边界）
- 部署运维：`deploy/ops.md`

---

## 1. 为什么需要它
原 `publish_queue` 只是静态 JSON 包，缺：跨目录幂等、原子持久化、重试、真实发布守卫、可观测性、反馈自优化闭环。本层补齐这些（详见优化设计文档）。

## 2. 快速开始
```bash
# 1) 处理发布队列（默认 dryrun，沙箱安全）
python content_events/cli.py process-queue --root . --publisher dryrun

# 2) 查看队列状态
python content_events/cli.py status --root . --paper-id <arxiv:xxxx>

# 3) 采集反馈观察窗口 + 自优化决策
python content_events/cli.py collect-feedback --root .
```

## 3. CLI 参考
| 子命令 | 关键参数 | 说明 |
|--------|----------|------|
| `process-queue` | `--publisher dryrun\|wechat\|xhs`、`--theme`、`--no-dry-run`、`--retry`、`--retry-attempts` | 处理队列；默认 dryrun 只写本地包。`--no-dry-run` 仅对 approved 真实项尝试 stage（沙箱无会话→needs_review） |
| `status` | `--paper-id` | 扫描 `publish_queue/*/state.json`，支持按 paper_id 过滤 |
| `collect-feedback` | — | 跑反馈采集窗口（守卫 OpenCLI）+ `decide_once` 自优化决策 |

退出码：`errors>0 → 1`，便于自动化识别部分失败。

## 4. REST 服务
```bash
pip install fastapi uvicorn
uvicorn content_events.serve:app --host 0.0.0.0 --port 8080
```
| 方法 | 路径 | 请求体 | 返回 |
|------|------|--------|------|
| GET | `/health` | — | `{"status":"ok"}` |
| POST | `/process-queue` | `{root?, publisher?, theme?, dry_run=true, retry?, retry_attempts?}` | `{processed, summary, summary_text, results, dry_run}` |
| POST | `/collect-feedback` | `{root?}` | 反馈采集 + 自优化决策 |
| GET | `/status?root=&paper_id=` | query | `state.json` 列表 |

**安全默认值**：`/process-queue` 的 `dry_run` 默认为 `true`。仅显式传 `false` 才允许 approved 项真实 stage，沙箱无登录态仍降级 `needs_review`，绝不会自动 publish。

测试（TestClient）：
```bash
python -m unittest content_events.tests.test_serve -v
```

## 5. 部署（Docker）
```bash
docker compose -f content_events/deploy/docker-compose.yml up --build
curl http://localhost:8080/health
```
镜像仅含 `serve.py` 运行所需源码 + fastapi/uvicorn，语料经卷挂载（见 `deploy/ops.md`）。

## 6. 安全边界（强制）
1. 非交互通道**禁止自动 publish**，仅 `stage`/`dryrun`。
2. 网络/登录/审核失败 → `needs_review`，不自动重试（仅瞬时错误重试，永久错误直转）。
3. 幂等键 `paper_id::platform::content_hash` 防重复；全局注册表 `data/content_events/idem_registry.jsonl`。
4. 反馈采集只读；`decide_once` 只写 `decisions` 表，不执行任何写操作类动作。

## 7. 测试与验证
```bash
# 全部用例（40+）
python -m unittest content_events.tests

# 真实语料冒烟：复制 publish_queue 到临时根，dryrun 实跑
python content_events/cli.py process-queue --root <copy> --publisher dryrun
```
已实现：幂等跨目录去重（O1）、原子写（O2）、重试（O3）、RunSummary 可观测（O6）、侧车聚合（D2）、守卫/未知平台修复（A3/A4/D3/D4）、反馈自优化接通（O8）。

## 8. 模块索引
| 文件 | 职责 |
|------|------|
| `schema.py` | `ContentItem`/`ContentEvent`/`RunSummary`/`content_hash` |
| `state_machine.py` | 状态机（不随意跳变） |
| `event_log.py` | 事件审计（fsync + 损坏行容忍） |
| `publishers.py` | `make_publisher` 守卫/占位/签名适配 |
| `queue_processor.py` | `IdempotencyRegistry` + `process_queue`（O1–O3/O6/O7/O10/D2） |
| `feedback_collector.py` | 反馈采集 + `decide_once`（O8） |
| `orchestrator.py` | 组合 `run_once` / `collect_feedback` |
| `retry.py` | `RetryPolicy` / `retry_call` |
| `cli.py` / `serve.py` | CLI / REST 入口 |
