# arXiv 推荐系统论文爬取与解析工具 — 技术文档

> **版本**: 1.0  
> **最后更新**: 2026-07-22  
> **适用环境**: Python 3.10+ / Windows / macOS / Linux

---

## 目录

1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [目录结构与文件说明](#3-目录结构与文件说明)
4. [核心模块设计](#4-核心模块设计)
   - [4.1 配置模块 (config/)](#41-配置模块-config)
   - [4.2 Skill 技能框架 (skills/)](#42-skill-技能框架-skills)
   - [4.3 爬取编排器 (crawler/)](#43-爬取编排器-crawler)
   - [4.4 存储模块 (storage/)](#44-存储模块-storage)
   - [4.5 工具模块 (utils/)](#45-工具模块-utils)
   - [4.6 CLI 入口 (main.py)](#46-cli-入口-mainpy)
5. [Skill 接口规范与扩展指南](#5-skill-接口规范与扩展指南)
6. [数据流与处理流水线](#6-数据流与处理流水线)
7. [配置说明](#7-配置说明)
8. [运行指南](#8-运行指南)
9. [输出格式规范](#9-输出格式规范)

---

## 1. 项目概述

### 1.1 项目目标

构建一个模块化、可扩展的 arXiv 论文爬取与解析工具，聚焦**推荐系统**领域的学术前沿。系统围绕四大研究方向预设搜索策略，覆盖 2024 年及以后发表的最新论文，提供从检索到全文解析的端到端流水线。

### 1.2 四大研究主题

| 主题标识符 | 研究方向 | arXiv 查询策略 |
|---|---|---|
| `agent-recommendation` | Agent 与推荐系统 | Agent 技术在推荐场景中的建模与应用 |
| `multimodal-recommendation` | 多模态推荐 | 融合图像、文本、视频等多模态信号的推荐方法 |
| `llm-recall` | 大模型参与召回 | LLM 在候选生成 (candidate generation) 与召回阶段的角色 |
| `llm-ranking` | 大模型参与排序 | LLM 在预排序、排序、重排序等精排阶段的介入方式 |

### 1.3 核心能力

1. **论文搜索**：基于 arXiv 官方 API，支持结构化查询与年份过滤
2. **元数据提取**：对原始搜索结果进行清洗、标准化和完整性校验，补全 PDF/页面链接
3. **PDF 全文解析**：可选接入 MinerU API，提取论文的结构化文本、表格、公式与图片
4. **结构化存储**：按主题与时间组织 JSON 输出，内置去重与增量合并逻辑
5. **模块化架构**：所有功能封装为独立 Skill，遵循统一接口，支持热插拔与第三方扩展

### 1.4 参考论文

以 [arXiv:2503.21460](https://arxiv.org/abs/2503.21460) 为输出字段参考样例，确保每篇论文至少包含以下元数据：

- `title` — 论文标题
- `authors` — 作者列表
- `abstract` — 摘要全文
- `published` — 发表日期 (YYYY-MM-DD)
- `pdf_url` — PDF 下载链接
- `arxiv_url` — arXiv 页面链接
- `arxiv_id` — arXiv 标识符
- `categories` — 分类标签

---

## 2. 系统架构

### 2.1 分层架构图

```
┌──────────────────────────────────────────────────┐
│                    CLI (main.py)                  │
│        crawl-all | crawl | search | parse         │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│               Crawler 编排层 (crawler/)            │
│   ArxivCrawler: 协调各 Skill 完成端到端流水线      │
│   Search → Extract → Store → (Parse PDF)          │
└──────────────────────┬───────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Searcher  │ │  Extractor  │ │  PDF Parser │
│  (搜索技能)  │ │ (清洗技能)   │ │ (解析技能)   │
└─────────────┘ └─────────────┘ └─────────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│           Skill 抽象层 (skills/base_module.py)     │
│   BaseSkill + register_skill + get_skill          │
│   统一接口，动态注册，工厂创建                       │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│              基础设施层                             │
│   config/ (配置)  │  storage/ (持久化)  │  utils/ │
└──────────────────────────────────────────────────┘
```

### 2.2 设计原则

- **关注点分离**：搜索、清洗、解析、存储各司其职，通过编排层串联
- **面向接口编程**：所有 Skill 继承 `BaseSkill`，通过注册表实现依赖反转
- **配置外部化**：所有可变参数集中管理在 `.env` 中，代码不硬编码
- **可扩展性优先**：新增一个搜索源（如 Semantic Scholar）只需编写新的 Skill 类并注册
- **优雅降级**：MinerU 不可用时，爬取流程正常执行，PDF 解析步骤静默跳过

### 2.3 Seed-Driven 推荐扩展

针对“围绕关键论文补齐相关研究”的使用场景，系统新增 `related-paper-recommend` Skill，
在原有主题爬取之外增加一条种子论文驱动链路：

```
Seed arXiv ID
    ↓
获取种子论文元数据
    ↓
扩展相关查询（Agent / LLM / 工业评估 / 自动迭代）
    ↓
候选论文去重
    ↓
可解释评分（主题命中 + 种子关键词重叠 + 年份 + 分类 + 查询命中）
    ↓
Top-K 推荐报告
    ↓
可选 PDF 下载
    ↓
MinerU 可用时再进入全文解析与 DeepSeek 摘要
```

该扩展的目的不是替代 `crawl-all`，而是补强推荐系统学习过程中的“重点论文追踪”能力。
固定主题爬取适合周期性扩库，Seed-Driven 推荐适合从一篇核心论文出发快速定位上下游工作，
并将推荐结果保存到 `data/metadata/recommendations/`，作为后续解析与摘要的任务清单。
`data/summaries/` 仅保存 DeepSeek 生成的单篇论文知识摘要。
解析层采用 MinerU 优先、本地兜底策略：当 `.env` 未配置 `MINERU_API_KEY` 时，
CLI 会自动调用 `pdf-parse-local` 将已下载 PDF 提取为纯文本 Markdown，保证摘要和合并链路不中断。

---

## 3. 目录结构与文件说明

### 3.1 数据存储约定

| 路径 | 内容 |
|---|---|
| `data/parsed/{arXiv ID}_{中文标题}/` | 单篇论文资产包：MinerU Markdown、原始 PDF、图片及结构化产物 |
| `data/summaries/{arXiv ID}_summary.md` | DeepSeek 单篇知识摘要：贡献、创新点、方法、数据集、实验条件、实验效果、Agent 借鉴 |
| `data/metadata/recommendations/` | 种子论文扩展查询、候选排序和下载记录 |
| `data/papers/` | PDF 下载缓存；进入解析流程后同时归档至论文资产包 |

`storage/paper_assets.py` 统一处理 `{id}` 与 `{id}_{中文标题}` 两种目录名，CLI、批处理和合并流程不得自行拼接解析文件路径。

### 3.2 Summary 2.0 知识层

Summary 2.0 在既有 Markdown 摘要之外增加四类机器可读产物：

| 产物 | 路径 | 作用 |
|---|---|---|
| Research Profile | `data/profiles/{id}.json` | 分类、研究主张、实验事实、Agent 设计价值 |
| Evidence Bundle | `data/evidence/{id}.json` | 原文章节、字符范围、摘录和源文件哈希 |
| Review Record | `data/reviews/{id}.json` | Schema、受控标签、证据覆盖和跨文件一致性问题 |
| Paper Registry | `data/registry/papers.jsonl` | 以 arXiv ID 为主键的增量资产与质量索引 |

受控标签维护在 `data/registry/taxonomies.yaml`，数据集规范名和官方来源维护在 `data/registry/datasets.yaml`。未知标签不能直接进入正式索引。

完整命令：

```bash
python main.py profile --arxiv-id 2606.09595
python main.py profile --all --force
python main.py validate-profile --all
python main.py search-profile --paradigm llm --quality B,C
```

`profile` 会优先复用现有 DeepSeek Markdown；摘要缺失时可从解析原文降级构建，但质量等级会下降。`validate-profile` 不调用 LLM，可重复检查证据引用、源哈希、数值证据、受控词表和资产身份冲突，并生成 `data/reviews/quality_report.md`。

### 3.3 关系图、学习路径与 Profile 重排

关系图只读取通过质量门禁且未被隔离的 Profile。引用边来自解析原文中可定位的 arXiv 引用；语义边来自受控研究方向、链路阶段、问题、技术范式、模态、数据集和指标交集，并限制每篇论文保留的语义邻居数量。

```bash
python main.py build-relations --arxiv-id 2606.26859
python main.py learning-path --topic multimodal --level intermediate
python main.py learning-path --all
python main.py recommend --seed 2606.26859 --top-k 8 --use-profiles
```

Profile 重排按 `config/recommendation_weights.yaml` 计算主题与问题、链路阶段、范式与模态、共享数据集、关系图、时效性和质量分。输出包含 `why_this_paper`、`comparison_role`、`evidence_refs`、分项得分及质量等级，并在最终候选集合上执行方法族多样性约束。

错配论文不会被删除。`data/registry/quarantined_assets.yaml` 保存原始 ID、隔离原因和有效替代论文；全量校验、检索、关系构建、学习路径和重排默认只使用活跃资产。

```
recommendation-system/
│
├── .env                          # 用户私有配置（API Key 等，不提交到 Git）
├── .env.example                  # 配置模板，含所有可配置项的说明
├── .gitignore                    # Git 忽略规则
├── README.md                     # 快速上手文档
├── requirements.txt              # Python 依赖清单
├── main.py                       # CLI 命令行入口
│
├── config/                       # ────── 全局配置模块 ──────
│   ├── __init__.py               # 模块入口，导出 settings 单例
│   └── settings.py               # Settings 类，从 .env 读取所有配置项
│
├── skills/                       # ────── 可复用技能模块 ──────
│   ├── __init__.py               # 模块入口，导出 BaseSkill 及注册函数
│   ├── base_module.py            # 抽象基类 + Skill 注册表 + 工厂函数
│   ├── arxiv_searcher.py         # Skill A: arXiv 论文搜索
│   ├── metadata_extractor.py     # Skill B: 论文元数据清洗与校验
│   └── pdf_parser.py             # Skill C: MinerU PDF 全文解析
│
├── crawler/                      # ────── 爬取编排层 ──────
│   ├── __init__.py               # 模块入口，导出 ArxivCrawler
│   └── arxiv_crawler.py          # 爬取编排器，串联各 Skill 完成流水线
│
├── storage/                      # ────── 数据持久化层 ──────
│   ├── __init__.py               # 模块入口，导出 PaperStore
│   └── paper_store.py            # JSON 文件存储、去重、增量合并
│
├── utils/                        # ────── 通用工具模块 ──────
│   ├── __init__.py               # 模块入口，导出工具函数
│   └── helpers.py                # 日志配置、文本清理、重试装饰器
│
└── docs/                         # ────── 项目文档 ──────
    └── TECHNICAL_DOC.md          # 本文件
```

### 各文件核心职责速览

| 文件 | 职责 | 关键类/函数 |
|---|---|---|
| `config/settings.py` | 环境变量读取与默认值管理 | `Settings` (单例) |
| `skills/base_module.py` | Skill 抽象接口定义与注册机制 | `BaseSkill`, `register_skill`, `get_skill` |
| `skills/arxiv_searcher.py` | arXiv API 搜索封装 | `ArxivSearcher.execute(query, max_results, start_year)` |
| `skills/metadata_extractor.py` | 论文元数据清洗、格式化与完整性校验 | `MetadataExtractor.execute(mode, papers)` |
| `skills/pdf_parser.py` | MinerU API 调用、PDF 结构化解析 | `PDFParser.execute(pdf_url, pdf_path)` |
| `crawler/arxiv_crawler.py` | 端到端爬取流水线编排 | `ArxivCrawler.run_all_topics()`, `run_topic()` |
| `storage/paper_store.py` | JSON 持久化、去重与增量合并 | `PaperStore.save_topic()`, `deduplicate()` |
| `utils/helpers.py` | 日志初始化、文本清洗、重试装饰器 | `setup_logging()`, `clean_text()`, `@retry` |
| `main.py` | CLI 入口，argparse 命令路由 | `main()` |

---

## 4. 核心模块设计

### 4.1 配置模块 (config/)

#### 设计思路

所有可变参数 — 从 API 密钥到搜索策略 — 均通过 `.env` 文件注入，由 `Settings` 类统一管理。代码中任何模块只需 `from config import settings` 即可获取配置，无需自行解析环境变量。

#### Settings 类结构

```python
class Settings:
    # -- MinerU --
    MINERU_API_KEY: str         # MinerU API 密钥

    # -- arXiv --
    ARXIV_API_BASE: str         # arXiv API 端点（默认 export.arxiv.org）

    # -- 爬取控制 --
    REQUEST_INTERVAL: float     # 请求间隔（秒），防止限流
    MAX_RESULTS_PER_QUERY: int  # 单次搜索最大返回数
    START_YEAR: int             # 论文发表年份下限

    # -- 输出 --
    OUTPUT_DIR: Path            # 结果输出目录
    LOG_LEVEL: str              # 日志级别

    # -- 搜索主题 --
    SEARCH_TOPICS: dict[str, str]  # {主题名: arXiv 查询字符串}
```

#### 扩展方式

新增配置项只需在 `Settings` 类中添加一个 `@property`，无需修改任何调用方代码。例如：

```python
@property
def ENABLE_PDF_PARSE(self) -> bool:
    return os.getenv("ENABLE_PDF_PARSE", "false").lower() == "true"
```

---

### 4.2 Skill 技能框架 (skills/)

#### 4.2.1 抽象基类

`BaseSkill` 是系统中最核心的抽象。所有技能 — 无论是内置的 arXiv 搜索、元数据提取，还是将来接入的 Semantic Scholar 搜索、Sci-Hub 下载 — 都必须实现 `execute(**kwargs) -> dict[str, Any]` 方法。

```python
class BaseSkill(ABC):
    skill_type: str = "base"

    @abstractmethod
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """执行技能逻辑，返回 {'results': [...], ...}"""
        ...
```

统一返回 `dict` 的设计使得下游调用方无需关心具体实现，编排层完全与 Skill 实现解耦。

#### 4.2.2 注册机制

通过装饰器 `@register_skill("skill-name")` 将技能注册到全局注册表，工厂函数 `get_skill("skill-name")` 按名称动态获取实例：

```python
@register_skill("arxiv-search")
class ArxivSearcher(BaseSkill):
    ...

# 使用
searcher = get_skill("arxiv-search")
result = searcher.execute(query="...", max_results=30)
```

这种"注册-查找"模式使得系统可以在**不修改编排层代码**的情况下接入新技能：只需编写新类并加上装饰器即可。

#### 4.2.3 已注册技能一览

| 注册名 | 实现类 | 功能 |
|---|---|---|
| `arxiv-search` | `ArxivSearcher` | arXiv API 论文搜索，支持年份过滤与速率控制 |
| `metadata-extract` | `MetadataExtractor` | 元数据清洗、作者格式统一、字段完整性校验 |
| `pdf-parse` | `PDFParser` | 接入 MinerU API，解析论文 PDF 为结构化文本 |

#### 4.2.4 ArxivSearcher 详解

**核心逻辑**：
1. 接收 arXiv 查询字符串（支持 `all:`, `ti:`, `au:`, `cat:` 等 arXiv 搜索语法）
2. 通过 `arxiv.Client` 发起分页请求，内置速率控制
3. 将 `arxiv.Result` 对象转换为标准化字典
4. 按 `start_year` 在应用层过滤（arXiv API 本身不支持年份范围过滤）

**关键设计决策**：
- 使用官方 `arxiv` Python 包而非直接 HTTP 请求，保证与 arXiv API 的兼容性
- 将 `Result.get_short_id()` 解析为纯净的 `arxiv_id`（去除版本号后缀），确保后续去重和链接生成的准确性
- 年份过滤放在客户端进行，因为 arXiv API 的 `submittedDate` 排序不保证精确的年份范围

#### 4.2.5 MetadataExtractor 详解

**两种操作模式**：

| 模式 | 用途 | 行为 |
|---|---|---|
| `refine` | 数据清洗 | 格式化标题/摘要/作者、补全 PDF 和 arXiv 链接、生成短摘要 |
| `validate` | 完整性校验 | 逐字段检查，返回 valid/invalid 统计 |

**数据增强项**：
- `short_abstract`：自动生成的 200 字符短摘要，用于表格展示
- `pdf_url` / `arxiv_url`：当原始数据缺失时，根据 `arxiv_id` 补全链接

#### 4.2.6 PDFParser 详解

**设计要点**：
- `is_ready` 属性：用于优雅降级——如果用户未配置 `MINERU_API_KEY`，系统不会报错，而是静默跳过 PDF 解析步骤
- 双输入模式：支持传入 PDF URL（由 MinerU 服务端拉取）或本地文件路径（base64 上传）
- 指数退避重试：默认最多重试 3 次，退避间隔为 2^attempt 秒
- `_normalize_response()`：将 MinerU 的原始响应转换为统一结构，屏蔽 API 变更对上游的影响

---

### 4.3 爬取编排器 (crawler/)

`ArxivCrawler` 是系统的"指挥中心"，负责按序调用各 Skill 并处理异常。

#### 核心流水线

```
run_topic(topic_name)
  │
  ├── Step 1: ArxivSearcher.execute(query, max_results, start_year)
  │     └── 返回 {"results": [<paper dict>], "total": N}
  │
  ├── Step 2: MetadataExtractor.execute(mode="refine", papers=papers)
  │     └── 返回 {"results": [<cleaned dict>], "valid": N, "invalid": M}
  │
  ├── Step 3: PaperStore.save_topic(topic_name, cleaned_papers)
  │     └── 写入 output/<topic>/papers_YYYY-MM-DD.json
  │
  └── Step 4 (可选): PDFParser.execute(pdf_url, arxiv_id)
        └── 仅在 parse_pdf=True 且 MinerU 可用时执行
```

#### run_all_topics() 的容错设计

每个主题独立执行，单个主题失败不会中止其他主题。最终无论成功或失败，都会生成汇总报告，确保部分成功的结果不会丢失。

---

### 4.4 存储模块 (storage/)

#### 输出文件组织

```
output/
├── agent-recommendation/
│   └── papers_2026-07-22.json      # 主题级论文列表
├── multimodal-recommendation/
│   └── papers_2026-07-22.json
├── llm-recall/
│   └── papers_2026-07-22.json
├── llm-ranking/
│   └── papers_2026-07-22.json
└── summary_2026-07-22.json          # 跨主题汇总
```

#### 去重策略

- 以 `arxiv_id` 为唯一键
- `deduplicate()` 保留首次出现、丢弃后续重复
- `merge_results()` 则是新覆盖旧，适用于增量更新场景

---

### 4.5 工具模块 (utils/)

| 函数 | 功能 |
|---|---|
| `setup_logging(level)` | 统一日志初始化，DEBUG 模式输出时间戳和模块名 |
| `clean_text(text)` | 去除多余空白与换行，输出单行干净文本 |
| `@retry(max_attempts, backoff, exceptions)` | 通用重试装饰器，支持指数退避和可配置异常类型 |

---

### 4.6 CLI 入口 (main.py)

基于 `argparse` 的子命令模式，提供 5 个命令：

| 命令 | 功能 | 示例 |
|---|---|---|
| `crawl-all` | 爬取所有预设主题 | `python main.py crawl-all` |
| `crawl` | 爬取单个主题 | `python main.py crawl -t llm-ranking --max 30 --pdf` |
| `search` | 自定义 arXiv 搜索 | `python main.py search -q 'all:"graph neural network" AND all:"recommendation"' --max 20` |
| `parse` | 解析单篇论文 PDF | `python main.py parse --arxiv-id 2503.21460` |
| `list` | 列出可用技能与主题 | `python main.py list` |

---

## 5. Skill 接口规范与扩展指南

### 5.1 接口契约

系统中所有 Skill 必须遵守以下契约：

```python
class MySkill(BaseSkill):
    skill_type: str = "my-skill"  # 唯一标识符

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        参数:
            **kwargs: 技能特定的运行时参数

        返回:
            {
                "results": [...],    # 核心输出（列表或单值）
                "total": int,        # 结果数量
                "error": str | None, # 错误信息（成功时为 None）
                ...                  # 其他技能特定字段
            }
        """
        ...
```

### 5.2 新增 Skill 的四步流程

以接入 Semantic Scholar 搜索为例：

**Step 1 — 创建技能文件** `skills/semantic_scholar_searcher.py`：

```python
from skills.base_module import BaseSkill, register_skill

@register_skill("semantic-scholar-search")
class SemanticScholarSearcher(BaseSkill):
    def execute(self, **kwargs):
        query = kwargs["query"]
        # ... 调用 Semantic Scholar API ...
        return {"results": papers, "total": len(papers)}
```

**Step 2 — (可选) 在配置中添加相关参数**：

在 `config/settings.py` 的 `Settings` 类中添加 `SEMANTIC_SCHOLAR_API_KEY` 等属性。

**Step 3 — 在编排器中接入**：

在 `crawler/arxiv_crawler.py` 中按需调用：

```python
ss_searcher = get_skill("semantic-scholar-search")
results = ss_searcher.execute(query="...")
```

**Step 4 — 在 `skills/__init__.py` 中导入模块**（触发装饰器注册）：

```python
from skills import semantic_scholar_searcher  # noqa: F401
```

无需修改 `ArxivCrawler` 核心逻辑——只需在调用处通过 `get_skill()` 按名查找即可。

### 5.3 设计意图

采用注册表 + 工厂模式而非传统的类继承硬编码，是为了实现**运行时动态组装**的能力：未来可以通过配置文件指定使用哪一组 Skill（例如在生产环境使用 MinerU 云 API，在开发环境使用本地 PyMuPDF），而无需改动任何业务代码。

---

## 6. 数据流与处理流水线

### 6.1 端到端数据流

```
用户执行命令
    │
    ▼
main.py (CLI 解析)
    │
    ▼
ArxivCrawler.run_all_topics() / run_topic()
    │
    ├─[1]─► ArxivSearcher.execute(query)
    │         │ arxiv.Search → arxiv.Client.results → [Result]
    │         │ 每个 Result 转换为统一字典:
    │         │ {title, authors, abstract, published, pdf_url, arxiv_url, ...}
    │         ▼
    │       [raw papers list]
    │
    ├─[2]─► MetadataExtractor.execute(mode="refine", papers=[...])
    │         │ 标题清洗、作者格式化、摘要压缩
    │         │ 补全链接、添加 short_abstract
    │         │ 按 REQUIRED_FIELDS 校验完整性
    │         ▼
    │       [cleaned papers list]
    │
    ├─[3]─► PaperStore.save_topic(topic, papers)
    │         │ JSON 序列化
    │         │ 写入 output/<topic>/papers_YYYY-MM-DD.json
    │
    ├─[4]─► (可选) PDFParser.execute(pdf_url, arxiv_id)
    │         │ 调用 MinerU API
    │         │ 提取 text, sections, tables, figures, formulas
    │         │ 写入 paper["pdf_content"]
    │
    ▼
汇总报告 → output/summary_YYYY-MM-DD.json
```

### 6.2 单篇论文的数据结构

以参考论文 `2503.21460` 为样例，经过完整流水线后的数据结构如下：

```json
{
  "title": "A Survey on Large Language Model powered Recommendation Systems",
  "authors": ["Author One", "Author Two", "Author Three"],
  "abstract": "This survey provides a comprehensive review of ...",
  "short_abstract": "This survey provides a comprehensive review of ... (截断至200字符)",
  "published": "2025-03-27",
  "year": 2025,
  "pdf_url": "https://arxiv.org/pdf/2503.21460",
  "arxiv_url": "https://arxiv.org/abs/2503.21460",
  "arxiv_id": "2503.21460",
  "categories": ["cs.IR", "cs.AI"],
  "comment": "Submitted to ACM Computing Surveys",
  "primary_category": "cs.IR",
  "pdf_content": {                       // 仅 parse_pdf=True 时存在
    "text": "Full text of the paper...",
    "sections": [...],
    "tables": [...],
    "figures": [...],
    "formulas": [...]
  }
}
```

---

## 7. 配置说明

### 7.1 .env 文件模板

```ini
# MinerU API Key — PDF 解析功能所需
# 从 https://mineru.net 获取
MINERU_API_KEY=sk-your-key-here

# arXiv API 基础地址（一般无需修改）
ARXIV_API_BASE=https://export.arxiv.org/api/query

# 请求间隔（秒）— 建议 ≥3.0 以免触发 arXiv 限流
REQUEST_INTERVAL=3.0

# 单次搜索的最大返回结果数
MAX_RESULTS_PER_QUERY=50

# 论文发表年份下限（仅爬取该年及以后的论文）
START_YEAR=2024

# 输出目录（相对于项目根目录或绝对路径）
OUTPUT_DIR=./output

# 日志级别: DEBUG | INFO | WARNING | ERROR
LOG_LEVEL=INFO
```

### 7.2 配置优先级

1. `.env` 文件中的值
2. 若 `.env` 中未设置，回退到 `Settings` 类中定义的默认值
3. 运行时可通过 Skill 构造函数的 `kwargs` 临时覆盖（如 `ArxivSearcher(api_key="...")`）

---

## 8. 运行指南

### 8.1 环境准备

```bash
# 1. 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env：至少需要填写 MINERU_API_KEY（若需 PDF 解析）

# 4. 验证安装
python main.py list
```

### 8.2 典型使用场景

**场景 A：全量批量爬取（首次使用）**

```bash
python main.py crawl-all
```

执行后将在 `output/` 下生成四个主题的 JSON 文件和一份汇总报告。

**场景 B：增量跟踪最新论文（定时任务）**

配合 cron / task scheduler 定期执行：

```bash
# 每周一早上 9 点爬取最新论文
0 9 * * 1 cd /path/to/recommendation-system && python main.py crawl-all
```

结合 `PaperStore.merge_results()` 可实现增量更新而不重复。

**场景 C：单篇论文深度阅读**

```bash
python main.py parse --arxiv-id 2503.21460
```

输出论文的结构化全文解析结果（需 MinerU API Key）。

**场景 D：自定义研究方向探索**

```bash
python main.py search \
  --query 'all:"contrastive learning" AND all:"recommendation" AND cat:cs.IR' \
  --max 30
```

### 8.3 在中国大陆网络环境下的注意事项

arXiv API 在某些网络环境下可能访问受限。解决方案：

1. **配置代理**：在运行前设置 `HTTPS_PROXY` 环境变量
2. **使用镜像站**：修改 `.env` 中 `ARXIV_API_BASE` 为可用镜像地址
3. **增大请求间隔**：将 `REQUEST_INTERVAL` 设为 5.0 或更大以提升稳定性

---

## 9. 输出格式规范

### 9.1 主题论文文件

文件名: `output/<topic>/papers_<YYYY-MM-DD>.json`

```json
{
  "topic": "llm-ranking",
  "crawled_at": "2026-07-22T10:30:00.000000",
  "total": 42,
  "papers": [
    {
      "title": "...",
      "authors": ["..."],
      "abstract": "...",
      "short_abstract": "...",
      "published": "2025-03-27",
      "year": 2025,
      "pdf_url": "https://arxiv.org/pdf/...",
      "arxiv_url": "https://arxiv.org/abs/...",
      "arxiv_id": "...",
      "categories": ["cs.IR"],
      "comment": "...",
      "primary_category": "cs.IR"
    }
  ]
}
```

### 9.2 汇总报告

文件名: `output/summary_<YYYY-MM-DD>.json`

```json
{
  "generated_at": "2026-07-22T10:35:00.000000",
  "total_topics": 4,
  "total_papers": 156,
  "topics": {
    "agent-recommendation":     {"total": 28, "error": null},
    "multimodal-recommendation": {"total": 45, "error": null},
    "llm-recall":               {"total": 37, "error": null},
    "llm-ranking":              {"total": 46, "error": null}
  }
}
```

---

## 附录 A: 依赖说明

| 包名 | 版本 | 用途 |
|---|---|---|
| `arxiv` | ≥2.1.0 | arXiv 官方 Python API 客户端 |
| `httpx` | ≥0.27.0 | 异步 HTTP 客户端（MinerU API 调用） |
| `beautifulsoup4` | ≥4.12.0 | HTML 解析（备用方案） |
| `lxml` | ≥5.2.0 | 高性能 XML/HTML 解析器 |
| `python-dotenv` | ≥1.0.0 | .env 环境变量加载 |
| `pandas` | ≥2.2.0 | 数据表处理（预留） |
| `tqdm` | ≥4.66.0 | CLI 进度条 |
| `loguru` | ≥0.7.0 | 结构化日志（预留升级） |

## 附录 B: 后续规划

1. **多源聚合**：接入 Semantic Scholar、DBLP、OpenAlex 等学术数据库
2. **论文去重**：跨源去重，使用标题 + DOI 等组合键
3. **Web UI**：基于 Streamlit 提供可视化检索界面
4. **自动摘要**：接入 LLM 对论文生成中文摘要
5. **趋势分析**：对爬取结果按时间进行统计和趋势可视化
6. **论文关系图谱**：基于引用关系和主题相似度构建知识图谱
