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
- `time` 与 `timezone`：Windows 计划任务的每日触发时间。
- `working_dir`、`python`、`entrypoint` 与 `log_file`：安装脚本构造任务命令时使用的绝对运行环境。

候选来源、缓存 TTL、准入额度与来源限速只属于 `config/paper_catalog_sources.json`，不定义系统调度时间。`--watch` 仅是 `refresh_paper_catalog.py` 的人工常驻调试模式，使用脚本内的睡眠间隔，不是生产调度机制。

## 资产与索引

目录 SQLite 与 intake SQLite 必须指向同一 `data/paper_catalog/catalog.sqlite3`。此前 `data/papers/` 可由手工流程直接落盘，而 `data/paper_intake/jobs.sqlite3` 是另一份旧索引，因此两者会出现孤立资产；统一入口与回填脚本会以相同仓储记录 PDF 的 SHA-256 与 `download_pdf` 步骤。

`scripts/backfill_paper_index.py` 只扫描 `data/papers/*.pdf`：从文件名提取 arXiv ID、计算 SHA-256、为缺失记录创建 intake job，并登记完成的 `download_pdf` 步骤。它不移动、删除或重写 PDF；重复运行按 canonical ID/SHA-256 跳过已有记录。无法提取 arXiv ID 的文件只输出 warning，保留给人工处理。

## 系统任务

用 `scripts/install_paper_ingest_task.ps1` 从唯一 YAML 读取运行环境并注册 `PaperDailyIngest`；先执行 `-WhatIf` 复核命令。卸载使用 `scripts/uninstall_paper_ingest_task.ps1`。安装脚本显式设置 `PAPER_INTAKE_DB_PATH` 为统一目录 SQLite，避免 outbox 与 intake 写入两份数据库。
