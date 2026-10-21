# 论文收录与发布排障

## 最短定位路径

1. 运行 `python scripts/paper_intake_diagnose.py`，只看状态码与错误码；脚本不会输出凭据。
2. 运行 `powershell -ExecutionPolicy Bypass -File scripts/paper_worker_control.ps1 status`。
3. 查看 `.paper-work/remote-worker.err.log` 与 `.paper-work/remote-worker.out.log` 的末尾。
4. 在论文任务卡右上角 `•••` 导出该任务事件日志。

## 错误与处置

- `401/auth_required`：浏览器会清理过期会话并提示重新 GitHub 登录；不要反复提交论文。
- `deepseek_balance_low` / HTTP 402：充值或轮换 DeepSeek Key，预检恢复前不领取新任务。
- `notion_schema_mismatch`：恢复 `title/status/type/slug` 字段，预检通过后再重试。
- `TLS EOF`、429、502：公共请求层按 1/2/4 秒退避；连续失败后保留任务检查点。
- `lease_lost`：它是分布式所有权变化，不是论文处理失败；由新租约持有者继续。
- `deploy_failed`：查看 GitHub Actions 的 Build/Publish/Smoke 阶段；Notion 页面不会重复创建。
- 地图白屏：先检查 CARTO；连续三次瓦片错误后自动切换 OpenTopoMap。

## 恢复原则

- 任务、Notion 与发布均以 `slug`/arXiv ID 幂等；恢复时使用“重新处理”，不要新建同一论文。
- MinerU 成果和步骤检查点存在时会复用，不进行全库重跑。
- GitHub Pages 的公开冒烟仅检查站点、地图 JSON 和网关 `/health`；本机 MinerU、DeepSeek、Notion 凭据由本机诊断负责。
