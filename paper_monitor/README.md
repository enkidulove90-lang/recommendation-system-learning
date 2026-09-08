# paper_monitor — 前沿论文自动发现·过滤·推送系统

按 `docs/openalex_paper_monitoring.md` 设计方案实现。四层架构，数据自底向上流动：

```
数据源层  OpenAlex REST(#5) · arXiv Atom(#8) · HF Daily Papers(#11) · Semantic Scholar(#9)
   ↓ 并行摄入 (ingest/)
处理层    dedup(去重) → classify(主题硬过滤) → score(打分) → rerank(重排)  (process/)
存储层    SQLite: works + 倒排 topics/authors + snapshots  (store/)
应用层    digest 渲染 + 投递 console/file/email/slack + 引用爆发检测 (notify/)
```

## 模块布局（对应设计文档§1-§6）

| 路径 | 职责 | 设计映射 |
|---|---|---|
| `paper_monitor/config.py` | 环境变量配置中心 | §6 密钥/路径/阈值走环境变量 |
| `paper_monitor/models.py` | Paper/Author/Topic + 跨源归一主键 | §3 数据模型，dedup_key=DOI>arXiv>OpenAlex |
| `paper_monitor/ingest/` | 4 个数据源 adapter + `huggingface_code.py` 代码关联富集（替换 PWC #13），统一输出 Paper | §1 数据源层 |
| `paper_monitor/process/dedup.py` | 按归一主键合并跨源记录 | §5 去重准确性 |
| `paper_monitor/process/classify.py` | OpenAlex topics 硬过滤（叶子精确+父召回） | §5 分类相关性 |
| `paper_monitor/process/score.py` | influentialCitation+upvotes+stars+cited+兴趣加权 | §1 软过滤 |
| `paper_monitor/store/sqlite_store.py` | SQLite 主表+倒排+快照；引用爆发检测 | §6 持久化/监控 |
| `paper_monitor/notify/` | digest 渲染 + 多通道投递（防静默空推） | §1 应用层 |
| `paper_monitor/orchestrator.py` | 摄入 DAG（并行拉取→去重→过滤→打分→入库→投递） | §1 数据流 |
| `paper_monitor/api.py` | 极简内部 REST（/papers, /trends/burst） | §3 内部服务 |
| `paper_monitor/cli.py` | ingest / digest / analyze / serve | — |
| `paper_monitor/deploy/` | .env.example · run_daily.sh · GitHub Action | §6 部署运维 |

## 快速开始

```bash
# 1) 准备 venv（已装 pyalex/semanticscholar/requests/pytest 的 python 即可）
PY=python   # 或指向你的 venv

# 2) 配置（复制后按需填写）
cp paper_monitor/deploy/.env.example .env
#   至少设置 OPENALEX_MAILTO 进入 polite pool

# 3) 离线自测（无需网络，验证全链路）
PM_OFFLINE_FIXTURE=1 PM_DELIVERY=file PM_DB_PATH=/tmp/pm.sqlite \
  PM_DIGEST_PATH=/tmp/pm_digest $PY -m paper_monitor.cli ingest --limit 20

# 4) 真实摄入（需网络）
$PY -m paper_monitor.cli ingest --limit 100

# 5) 查看统计 / 启动 API
$PY -m paper_monitor.cli analyze --limit 20
$PY -m paper_monitor.cli serve --port 8787   # GET /papers?topic=recsys&since=2026-08-01
```

## 测试

```bash
$PY -m pytest paper_monitor/tests -q
```

覆盖：去重（同 DOI 三 ID 表达→1）、主题分类（50 样本 100% 命中 + 父召回）、
打分（信号越高分越高 + 兴趣加分）、端到端冒烟（DAG 跑通 + digest 非空含高信号论文 + 空推防护）。

## 运维（设计文档§6）

- **调度**：`cron` 每日 09:00 调 `deploy/run_daily.sh`，或零服务器 GitHub Action（已提供 workflow）。
- **限额**：OpenAlex 走 `mailto` polite pool + `per_page=100` + cursor 分页；429 自动退避。S2 匿名易 429，建议配 key。
- **持久化**：SQLite（个人版）。团队版可换 PostgreSQL（表结构同 `works` 主表）。
- **监控**：引用爆发 = 定期重摄入 `cited_by_count` 写入 `snapshots`，`detect_bursts()` 按环比 > 均值+3σ 告警。

## 说明（诚实偏差）

- 设计文档推荐 `pyalex`(#1)/`arxiv.py`(#6) 作为客户端；本实现直接调用 OpenAlex REST(#5) 与
  arXiv Atom(#8) 端点（`requests`），与其为同一数据源，换取零依赖、可控限额/退避。
  `pyalex`/`semanticscholar` 仍按设计文档在 venv 中安装可用。
- **Papers With Code(#13) 公共 API 已于 2025-07 停用 → 已替换为 Hugging Face 代码关联 API**。
  去重后 `enrich_code_links` 对每个含 `arxiv_id` 的论文请求 `api/papers/{arxiv_id}`，
  标注 `code_count`（关联 models+datasets+spaces 数，即"有可运行代码/实现"）与官方
  `github_repo` 链接，补上 PWC 原本承担的"代码/SOTA 链接"角色（见 `ingest/huggingface_code.py`）。
- **Semantic Scholar key 已接入**：`config.s2_api_key` 兼容 `S2_API_KEY` / `SEMANTIC_SCHOLAR_API_KEY` /
  `Semantic_Scholar_API_Key` 三种命名，并支持从 `.env` 自动加载；配置后 S2 不再匿名 429。
- 运行前建议将密钥写入 `.env`（项目根或 cwd），例如：
  `OPENALEX_MAILTO=you@x.com`、`S2_API_KEY=...` 或 `Semantic_Scholar_API_Key=...`。
