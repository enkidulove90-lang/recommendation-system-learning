# 第 1 章：数据源扩展

## 结论

以“各届会议官网的接收名单/日程页”为最早权威信号，以正式论文集为终稿校验，以 arXiv 为最快 PDF 信号；把 OpenAlex、Crossref、DBLP 定位为元数据增强而不是发现主源。所有来源只写 JSONL 文件，后续链路不直接依赖网页实现。

## 优先级与采集方式

| 优先级 | 来源 | 覆盖与用途 | 实现方式 |
| --- | --- | --- | --- |
| P0 | arXiv API/RSS | 预印本、版本更新、最快 PDF | 保留现有分类+关键词检索，按 arXiv ID 和更新时间增量读取。 |
| P0 | 会议官网接收名单/Program | SIGIR、KDD、WWW、RecSys 最早接收状态 | 每届配置 URL、CSS/XPath、正文哈希；优先用 ETag/Last-Modified，无响应头时比较正文 hash。 |
| P0 | PMLR、NeurIPS Proceedings | ICML、NeurIPS 正式论文、BibTeX、PDF | 逐届 HTML/BibTeX 解析并保留官方 PDF。 |
| P0 | OpenReview | 采用 OpenReview 的会议公开投稿与决定 | 按 invitation 调用 Notes API；只接受公开可读的记录。 |
| P1 | ACM DL、DBLP | ACM 顶会最终书目信息 | 官网论文集抓取，DBLP 仅交叉校验 DOI/页码，不能取代官网公告。 |
| P1 | OpenAlex、Crossref | DOI、作者、机构、主题补全 | 对新增候选按 DOI/arXiv 单篇查询；批量查询使用 cursor。 |
| P1 | 实验室主页与 GitHub | 定向发现机构论文及官方代码 | 网页 hash + GitHub Events/Release 轮询。 |
| P2 | 官方博客/RSS、X 信号 | 宣发和即时线索 | RSS 自动轮询；X 仅接受人工核验后的链接 JSONL。 |

SIGIR、KDD、WWW、RecSys 没有跨年份稳定一致的公开 RSS/API，不能为它们假定一个通用接口；应使用 `ConferenceAnnouncementSource`，按“届次”维护选择器与快照测试。SIGIR 已公开过 Accepted Papers/Full Papers 页面，KDD 维护官方 proceedings；ICML 的 PMLR 每卷提供论文条目、BibTeX 与 PDF，NeurIPS 有逐届官方 proceedings 索引。

## 机构监控

| 对象 | 主源 | 补充源 | 确定性归属规则 |
| --- | --- | --- | --- |
| 清华 THUIR | THUIR 论文/新闻页 | 成员 ORCID、arXiv author query、已确认仓库的 release | 作者单位匹配规则或成员白名单命中。 |
| 人大 IIR | IIR 官网论文/新闻页 | 成员 ORCID/arXiv、经配置确认的 `RUCAIBox` 等公开组织 | GitHub 只证明代码可用，不单独证明机构归属。 |
| 香港理工 | 院系、研究中心、课题组论文页 | 成员 ORCID/arXiv、课题组 GitHub | 作者单位与配置的域名/名称规则匹配。 |
| 阿里巴巴/达摩院 | 官方研究/论文/新闻页 | `alibaba` 及确认研究组织仓库、作者 ORCID/arXiv、官方博客 RSS | 产品新闻没有论文 ID、PDF 或作者信息时不入论文库。 |

Google Scholar 没有本链路可依赖的官方公共 API。因此只接收用户建立的 Scholar Alert 邮件，从邮件抽取 DOI、arXiv 或官方 URL；不抓取 Scholar 页面。GitHub 事件接口支持 ETag/304 与轮询间隔，适合作为低成本增量信号。

## 社交媒体

监控 NeurIPS、ICML、ACM SIGIR、SIGKDD、ACM RecSys 的官方会议账号，以及已在配置中验证的 OpenAI、Google DeepMind、Meta AI、腾讯、阿里研究账号。X 记录统一为 `x_signal`：必须在 P0/P1 找到同一论文，才能进入候选池。

不接入 X API。当前 API 需要访问计划并采用按量计费，不符合“不新增付费服务”。替代方案是官网/RSS/博客自动化，X 链接由人工导出至 `data/inbox/x_signals.jsonl`，并保存核验人和核验时间。

## 统一接口与文件契约

```python
class PaperSource(Protocol):
    name: str

    def discover(self, cursor: dict, query: dict) -> tuple[list[dict], dict]:
        """返回候选和下一游标；不直接写下游数据库。"""

    def fetch_detail(self, source_id: str) -> dict:
        """返回带来源 URL、抓取时间和原始 ID 的单篇记录。"""
```

适配器写入 `data/inbox/<YYYY-MM-DD>/<source>.jsonl`；规范化器输出 `data/normalized/papers.jsonl`；游标、ETag、网页 hash 写入 `redbook/state/sources/<source>.json`。命令统一为 `python -m redbook.sources run --source <name> --since-state`，可被定时任务调用或单独回放。

核心记录 Schema：

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["record_id", "title", "source_records", "provenance"],
  "properties": {
    "record_id": {"type": "string"},
    "identifiers": {"type": "object", "properties": {
      "doi": {"type": "string"}, "arxiv": {"type": "string"},
      "openreview": {"type": "string"}, "dblp": {"type": "string"}
    }},
    "title": {"type": "string"}, "abstract": {"type": "string"},
    "authors": {"type": "array", "items": {"type": "object", "required": ["name"]}},
    "venue": {"type": "object", "properties": {
      "name": {"type": "string"}, "year": {"type": "integer"},
      "track": {"type": "string"}, "status": {"enum": ["preprint", "accepted", "published"]}
    }},
    "urls": {"type": "object", "properties": {
      "landing": {"type": "string"}, "pdf": {"type": "string"}, "code": {"type": "string"}
    }},
    "announced_at": {"type": "string", "format": "date-time"},
    "published_at": {"type": "string", "format": "date-time"},
    "topics": {"type": "array", "items": {"type": "string"}},
    "source_records": {"type": "array", "items": {"type": "object", "required": ["source", "source_id", "url", "fetched_at"]}},
    "provenance": {"type": "object", "required": ["first_seen_at", "last_seen_at"]}
  }
}
```

## 去重与合并

1. 按 `doi` 精确合并；缺 DOI 时按 `arxiv`，再按 `openreview`。这些标识形成不可拆分论文簇。
2. 没有共同标识时，使用规范化标题指纹 + 首位作者姓氏 + 年份。标题 token Jaccard ≥ 0.92 且首位作者一致才合并；0.85–0.92 一律保持为两个候选。
3. 字段可信度固定为：会议官网接收状态 > 正式 proceedings/ACM DL/PMLR/NeurIPS > OpenReview > arXiv > 机构官网 > 社交信号。PDF 固定优先级为正式终稿 > 作者公开版 > arXiv。
4. 每一次覆盖都保留原值和来源；高可信标题、作者或 PDF 变化写入 `revision`，重新评分，不覆盖历史。

## 30 分钟窗口与实施顺序

每轮仅处理 cursor/ETag 之后的变化：P0 并发运行约 5 分钟，P1 对新增候选增强约 3 分钟，去重与入队约 1 分钟；只有通过主题初筛的新候选才进入 PDF/MinerU。失败时保留上次快照并记录，不阻塞 arXiv。

实施顺序：接口化现有 arXiv → `ConferenceAnnouncementSource`（SIGIR/KDD/WWW/RecSys）→ `PmlrSource`、`NeuripsSource`、`OpenReviewSource` → 机构/GitHub → OpenAlex/Crossref 异步增强。

## 可实施性

**5/5；首个可运行版本 3 个工作日。** 接口与六个 P0 适配器约 2 天，去重、状态和回放测试约 1 天；机构与 GitHub 扩展另需 1.5 个工作日。

## 依据

- [NeurIPS 官方 proceedings](https://proceedings.neurips.cc/)
- [PMLR proceedings 规范](https://proceedings.mlr.press/spec.html)
- [KDD 官方 proceedings](https://www.kdd.org/proceedings)
- [SIGIR Accepted Papers 示例](https://sigir.org/sigir2023/program/accepted-papers/full-papers/)
- [OpenReview Notes 批量查询](https://docs.openreview.net/how-to-guides/data-retrieval-and-modification/how-to-get-all-notes-for-submissions-reviews-rebuttals-etc)
- [OpenAlex API](https://developers.openalex.org/api-reference/introduction)
- [Crossref REST API](https://api.crossref.org/swagger-ui/index.html)
- [GitHub Events 的 ETag 轮询](https://docs.github.com/en/rest/activity/events)
- [X Developer Platform](https://developer.x.com/)
