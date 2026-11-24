# 统一论文抓取与 Intake 链路

`config/paper_ingest_schedule.yaml` 是论文抓取、准入和 intake 的唯一调度权威。系统计划任务只调用一次性入口 `scripts/daily_paper_ingest.py`；脚本本身不常驻。

```text
official sources
    -> refresh catalog (SQLite + papers.json snapshot)
    -> qualify catalog jobs
    -> consume outbox into intake jobs
    -> download PDF / parse / register assets
```

## 配置

- `enabled`：关闭时入口记录跳过并成功退出。
- `time`：每日触发时间，入口会校验为 `HH:MM`（`00:00`–`23:59`）。
- `timezone`：当前 Windows `schtasks` 安装方案不做时区换算；`time` 按执行机器的系统本地时区解释。跨时区部署必须在安装脚本中先换算到目标机器本地时间，再重新安装任务。
- `working_dir`、`python`、`entrypoint` 与 `log_file`：安装脚本构造任务命令时使用。相对 `working_dir` 以仓库根解析，入口会验证该目录含 `scripts/daily_paper_ingest.py`。

候选来源、缓存 TTL、准入额度与来源限速只属于 `config/paper_catalog_sources.json`，不定义系统调度时间。`--watch` 仅是 `refresh_paper_catalog.py` 的人工常驻调试模式，使用脚本内的睡眠间隔，不是生产调度机制。

## 资产与索引

目录 SQLite 与 intake SQLite 必须指向同一 `data/paper_catalog/catalog.sqlite3`。日常 S4 只消费 S3 创建的 `received` job：它下载来源 URL、运行 MinerU、把 PDF 登记到 `data/papers/`，并将 `download_pdf` 与 `mineru_parse` 的产物原子登记到该统一库。S3 每轮消费 outbox 直到为空（上限 1000 条），不再只取一条。

`scripts/backfill_paper_index.py` 是**仅用于历史存量回填**的一次性工具，不属于日常 S1–S4 链路。执行前后必须人工确认要补录的 PDF 清单；它只扫描 `data/papers/*.pdf`、从文件名提取 arXiv ID、计算 SHA-256、为缺失记录创建 intake job，并登记完成的 `download_pdf` 步骤。它不移动、删除或重写 PDF；重复运行按 canonical ID/SHA-256 跳过已有记录。无法提取 arXiv ID 的文件只输出 warning，保留给人工处理。

## 系统任务

用 `scripts/install_paper_ingest_task.ps1` 从唯一 YAML 读取运行环境并注册 `PaperDailyIngest`；先执行 `-WhatIf` 复核命令。卸载使用 `scripts/uninstall_paper_ingest_task.ps1`。安装脚本显式设置 `PAPER_INTAKE_DB_PATH` 为统一目录 SQLite，避免 outbox 与 intake 写入两份数据库。

## 回滚与数据清理

### 代码回滚

此修复序列可按提交逆序执行 `git revert`：先回滚 `[FIX-5]` 至 `[FIX-1]`，再按需要回滚原始统一 intake PR 的 `[P4]` 至 `[P0]` 提交。代码回滚**不会**自动删除运行时目录或 SQLite 文件。

### 统一索引的保留决策

保留 `data/paper_catalog/catalog.sqlite3` 作为运行时证据和统一索引。该文件当前包含历史回填生成的 `source_type=upload`、`source_url=''` job；它们不是日常链路产物，核验时必须与 `source_url` 非空的 catalog/outbox 链路 job 分开统计。若人工决定清除该索引，先在仓库外备份，再停止相关进程并删除：

```powershell
Copy-Item data/paper_catalog/catalog.sqlite3 C:\tmp\paper-ingest-backup\catalog.sqlite3
Remove-Item data/paper_catalog/catalog.sqlite3
```

### 旧索引处置

已选择“重命名为 `.deprecated`”而非自动迁移或删除：`data/paper_intake/jobs.sqlite3` 与 `data/paper_intake/remote/jobs.sqlite3` 保存的失败/发布中状态无法无损映射到统一库，保留原文件可供人工审计和恢复。实际处置命令为：

```powershell
Move-Item data/paper_intake/jobs.sqlite3 data/paper_intake/jobs.sqlite3.deprecated
Move-Item data/paper_intake/remote/jobs.sqlite3 data/paper_intake/remote/jobs.sqlite3.deprecated
```

需要恢复旧 worker 时，先停止统一入口，再把对应 `.deprecated` 文件改回 `jobs.sqlite3`；不要同时让旧 worker 与统一入口写入不同索引。
