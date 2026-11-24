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

目录 SQLite 与 intake SQLite 必须指向同一 `data/paper_catalog/catalog.sqlite3`。日常 S4 只消费 S3 创建的 `received` job：它下载来源 URL、运行 MinerU、把 PDF 登记到 `data/papers/`，并将 `download_pdf` 与 `mineru_parse` 的产物原子登记到该统一库。S3 每轮消费 outbox 直到为空（上限 1000 条），不再只取一条。

`scripts/backfill_paper_index.py` 是**仅用于历史存量回填**的一次性工具，不属于日常 S1–S4 链路。执行前后必须人工确认要补录的 PDF 清单；它只扫描 `data/papers/*.pdf`、从文件名提取 arXiv ID、计算 SHA-256、为缺失记录创建 intake job，并登记完成的 `download_pdf` 步骤。它不移动、删除或重写 PDF；重复运行按 canonical ID/SHA-256 跳过已有记录。无法提取 arXiv ID 的文件只输出 warning，保留给人工处理。

## 系统任务

用 `scripts/install_paper_ingest_task.ps1` 从唯一 YAML 读取运行环境并注册 `PaperDailyIngest`；先执行 `-WhatIf` 复核命令。卸载使用 `scripts/uninstall_paper_ingest_task.ps1`。安装脚本显式设置 `PAPER_INTAKE_DB_PATH` 为统一目录 SQLite，避免 outbox 与 intake 写入两份数据库。
