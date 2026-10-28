# 论文发现目录

`scripts/refresh_paper_catalog.py` 把论文发现与现有单篇投递解耦：它只维护候选目录，不触发 MinerU、DeepSeek、Notion 或 GitHub Pages 发布。

## 项目现有获取途径盘点

- `paper_intake/metadata.py`：按 arXiv ID 获取单篇权威 metadata。
- `paper_intake/references.py`：按 citation 中的 arXiv ID 或 DOI，使用 arXiv、Crossref、OpenAlex 做引用身份验证；它不是批量发现器。
- `redbook/automation/sources.py`：已有 arXiv、OpenReview、官方会议公告页、proceedings、离线 JSONL 适配器与确定性去重。
- `redbook/infrastructure/paper_sources/`：小红书链路的 arXiv 与 OpenReview 发现器。
- `config/settings.py`：Semantic Scholar 只用于引用/分析增强，不是当前论文列表的主身份源。
- URL/PDF 手工投递：进入 `paper_intake` 后解析，但不会自动形成会议论文列表。

本目录层复用同一权威来源原则，但输出一个前端和投递器都容易消费的稳定 JSON；它不调用 LLM 生成标题、venue 或 topic。

## 当前接入源与字段语义

| 来源 | 列表方式 | 年份 | 类型/刊会 | topic 的真实含义 | 论文链接 |
|---|---|---|---|---|---|
| arXiv Atom API | `search_query=cat:cs.IR` 等分类查询 | `published` | 固定为 `preprint`；`journal_ref` 不能作为可靠会议归属 | `category` / `primary_category` 学科分类码 | 规范化 `arxiv.org/abs/{id}` |
| ACL Anthology | ACL 2026 event 页面和官方 XML/Python API | Anthology ID/volume 年份 | `conference-paper` + ACL 2026 | 卷/track（Long、Short、Industry、Findings 等），不是逐篇语义主题 | Anthology canonical URL |
| ACM RecSys 官网 | 2026 session、poster、demo 页面 | 会议年 | 页面前缀映射 research/industry/demo 等 track | Session 标题；这是官方议程主题 | 若页面有 DOI 就用 DOI，否则保留官方 session 页面 |
| OpenAlex（可选补全） | 标题精确匹配后读取 Work | `publication_year/date` | `type` 与 primary location/source | OpenAlex `topics` | DOI 优先 |
| Crossref（现有参考文献链） | DOI 或 works 查询 | issued/published | `type` + `container-title` | `subject` 可能缺失，不应强行推断 | DOI |
| Semantic Scholar（暂不默认启用） | paper search/bulk，支持 year/venue/fieldsOfStudy 过滤 | `year/publicationDate` | `publicationTypes`/`venue` | `s2FieldsOfStudy` 是宽学科标签 | paper URL/DOI/arXiv ID |

目录统一字段为 `publication_year`、`venue_type`、`venue_name`、`track`、`topics`、`topic_source`、`title`、`paper_url`，并保留 `source/source_id/doi/arxiv_id` 供去重和溯源。`topic_source` 必须随字段输出，禁止把 arXiv 分类、会议 track、议程 session 和语义 topic 混成同一含义。

## 运行

单次刷新：

```powershell
python scripts/refresh_paper_catalog.py
```

持续每 30 分钟刷新：

```powershell
python scripts/refresh_paper_catalog.py --watch --interval 1800
```

默认输出为 `data/paper_catalog/papers.json`。文件通过同目录临时文件原子替换；若全部来源返回零篇或刷新异常，旧文件不会被覆盖。需要本机代理时只对本进程设置 `PAPER_CATALOG_HTTP_PROXY`。

主循环每 30 分钟运行，但 arXiv 官方说明同一查询的结果按日更新并要求缓存，因此 arXiv 原始 feed 默认缓存 24 小时；ACL/RecSys 页面缓存 30 分钟。上游超时会读取最近一次缓存，避免把已有目录清空。

OpenAlex 按标题逐条补全会增加请求量，因此默认关闭。确认 `mailto` 和速率预算后，在 `config/paper_catalog_sources.json` 中启用；只有标题规范化后完全一致的记录才会覆盖 venue/topic/DOI。

ACL 默认仅保留主会六卷和 Findings。若要同时收录 ACL 2026 event 下的全部联合 workshop，删除 `include_id_prefixes` 即可。
