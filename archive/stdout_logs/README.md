# 归档：根目录 stdout 日志（2026-11-10）

这里共 34 个 `.txt`（29 个已入库 + 5 个此前未入库的会话产物），**只作历史溯源，不再新增**。
它们的共同问题是：每跑一次链路就把 stdout 重定向到仓库根目录一个 `logs_*.txt`，
文件名带机器时间戳、内容与命令不对应，换机器 / 换 IDE 后完全无法比对。

| 类别 | 数量 | 例子 |
|---|---|---|
| 小红书草稿 / 发布 stdout | ~20 | `logs_xhs_publish_sage.txt`、`logs_publish_diffgrm.txt` |
| 构建 / 取图 / 核验 stdout | ~9 | `logs_build_sihg_dryrun.txt`、`logs_verify_diffgrm.txt` |
| 审计与会话转储 | 5 | `e15_numbers_audit.txt`、`xhs_drafts_dump.txt`、`_calls_readable.txt` |

`requirements.txt` **没有**移动：它是依赖清单，必须留在仓库根。

## 现在的落点

* 正式入口（`main.py`、`run_batch_pipeline.py`、`redbook.cli note`）一律写
  `data/logs/runs.jsonl`，一行一个 JSON 事件，实现见
  `redbook/infrastructure/run_log.py`；`data/logs/*.jsonl` 已加入 `.gitignore`。
* `run_batch_pipeline.py` 原有的 `data/logs/batch_step*.json` 逐步结果文件保持不变，
  只是额外追加一条 `batch_step` 事件指针。
* 查看运行记录：

```bash
python -m redbook.infrastructure.run_log --summary --tail 20
python -m redbook.infrastructure.run_log --json --event note
```

* 查看 WorkBuddy 会话转储（替代 `_dump_calls.py` 等一次性脚本）：

```bash
python -m redbook.scripts.session_inspect <session.jsonl> --output <readable.txt>
```

根目录新增 `logs_*.txt` / `_*.txt` 会被 `.gitignore` 拦下；需要留痕就走上面两个入口，
不要把 stdout 再重定向到仓库根。
