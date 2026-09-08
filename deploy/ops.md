# 创新性分析引擎 · 运维手册（Operations）

> 对应设计文档 `docs/novelty_analysis_engine_design.md` §7 与 `docs/innovation-tools-survey.md` 运维层。
> 系统定位：**辅助人工理解**，只输出可追溯差异点与证据，**不做新颖性终审判定**。

## 1. 架构与数据流

```
PDF/解析(md) → Extractor(四维度拆解) → GraphQuery(S2/OpenAlex 邻域)
            → VectorIndex(嵌入近邻, 本地语料) → ContrastEngine(设计轴差异矩阵)
            → ReportGenerator(Markdown+JSON, 三态标签) → 人工终判
```

- **解析/语料**：复用既有 `data/parsed/*`（MinerU）与 `data/summaries/*`；本地快照即"知识图谱"。
- **嵌入后端**：`tfidf`（默认，零下载）/ `minilm` / `specter2` / `pure`（纯 Python 兜底）。
- **在线源**：Semantic Scholar Graph API（免费无需 Key）、OpenAlex（CC0）。均可独立关闭。
- **模型服务**：SPECTER2 经 `sentence-transformers` 本地推理；DeepSeek 仅用于抽取增强（可选）。

## 2. 部署

### 2.1 容器编排（推荐）
```bash
cd deploy
cp ../.env.example .env   # 按需填 DEEPSEEK_API_KEY
docker compose up -d --build
# 校验
curl http://localhost:8000/health
```
- `grobid` 容器常驻（PDF 解析）；`novelty` 容器暴露 `:8000`。
- `data/` 以只读卷挂载；索引缓存挂到 `./index_cache`。

### 2.2 本地 / venv 运行
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r deploy/requirements-novelty.txt
# CLI
python -m novelty.cli analyze --arxiv-id 2605.28175 --top-k 10
# 或 REST
uvicorn novelty.serve:app --host 0.0.0.0 --port 8000
```

## 3. 监控（Monitoring）

| 项 | 方式 | 说明 |
|----|------|------|
| 存活 | `GET /health` | 返回 `status=ok`、嵌入后端、语料规模 |
| 容器 | `docker ps` / compose `healthcheck` | GROBID `:8070/api/isalive`、novelty `/health` |
| 日志 | `docker logs novelty-engine` 或 uvicorn stdout | 关注 `GraphQuery` 失败、`VectorIndex` 构建耗时 |
| 指标（建议） | Prometheus 拉 `/health` 或加 `/metrics` | corpus_size、last_analyze_elapsed、online_source 可用性 |

简易存活巡检（可放进 crontab / 自动化）：
```bash
curl -fsS http://localhost:8000/health >/dev/null || echo "novelty DOWN $(date)" | mail -s alert you@example.com
```

## 4. 定时同步与索引版本化（设计文档 §3/§7）

- **OpenAlex** 每日更新、**S2** 批量夜间刷新：用定时任务（cron / GitHub Action）拉增量、重算受影响子图嵌入、重建 FAISS 索引。
- **快照版本化**：`VectorIndex.save()` 落盘到带日期的目录（如 `data/novelty_index_cache/2026-08-12/`），支持回滚。
- **重建触发**：新增/更新 `data/parsed` 后调用一次 `python -m novelty.cli list-corpus` 确认规模，再重启服务以便引擎重建内存索引（或加 `/reindex` 管理端点）。

示例 nightly cron：
```cron
# 每日 03:10 重建索引快照
10 3 * * *  cd /path/recommendation-system-learning && python -m novelty.cli analyze --arxiv-id 2605.28175 --no-online >/dev/null 2>&1
```

## 5. 成本与限额

- **免费**：S2 API、OpenAlex、本地 FAISS/嵌入推理。
- **付费/受限**：DeepSeek（抽取增强，批处理优先、限流）、Scite/Elicit（本期未接入，按需）。
- **限流**：`CitationCollector` 已对 S2 做 1s 间隔；OpenAlex 适配器带 `User-Agent`。

## 6. 故障排查

| 现象 | 可能原因 | 处置 |
|------|----------|------|
| `/health` 404 | 服务未起 | `docker logs novelty-engine` 看启动错误 |
| 报告 `target_not_in_corpus` | arXiv ID 不在 `data/parsed` | 先跑解析管线把目标论文纳入语料 |
| 邻域为空 | 离线模式 / 网络被挡 | 确认 `--no-online` 未误开；检查 S2/OpenAlex 连通 |
| 嵌入慢/首次卡 | 正在下载 MiniLM/SPECTER2 | 改用 `--embedder tfidf` 或预拉模型 |
| 差异矩阵空 | 邻域论文无全文 | 正常：外部(S2/OpenAlex)论文仅有元数据，深度轴对比需本地语料近邻 |

## 7. 扩展点

- **新嵌入后端**：在 `embedder.py` 增加 `kind` 分支（已实现 auto/tfidf/minilm/specter2/pure）。
- **新图谱源**：在 `graph_query.py` 增加适配器（如 Connected Papers / Inciteful 导出）。
- **新设计轴**：在 `contrast.py` 的 `_AXES` 增加轴与关键词。
- **接入既有 skill 工厂**：`analyzer_skill.py` 已注册 `novelty-analyze`，可被主流程统一调度。
