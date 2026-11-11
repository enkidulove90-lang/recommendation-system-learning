# 论文解析资产接入 Notion 数据仓库 / 个人主页（设计，未实施）

> 状态：**仅设计文档**，2026-11-11。本轮不改任何代码、不改 `enkidu-blog/repo`、
> 不写 Notion、不引入凭据。目标是先回答「能不能接、接在哪、有哪些断点」，再决定要不要动手。

## 0. 结论先行

**能接，而且链路已经存在**，不是从零建设：论文仓的 `data/papers|summaries|parsed`
→ 博客仓 `tools/publish_paper_library.py` → `paper_article.build_article`
→ `notion_publish.publish_article` → Notion 数据库 → `notion_sync.py`（GitHub Actions）
→ `source/_posts/*.md` → Hexo → 个人主页。

上一轮只读 dry-run（2026-11-10，显式传 `--library-root`）已经跑通前半段：
manifest `total=60, published=51, needs_parse=7, needs_summary=1, ready=1`；
`selected=1, publishable=1, blocked=0`，唯一 ready 论文是 `2608.14429`。

**但不能「现在直接跑」**，有四个断点：默认路径硬编码在另一块盘、本机没有
Notion 凭据、Actions 只做「Notion → 站点」不做「论文仓 → Notion」、
以及现有管线吃的是解析稿与 11 维摘要，**完全不吃 `redbook/notes/*.yaml`**。
另外 `publish_article` 写模式会 `clear_children()` 覆盖已有页面正文，属于破坏性动作。

**推荐先做方案 A（只读盘点 + 本文定稿）**，不写 Notion、不做自动同步。
是否升级到 B / C、是否动博客仓，需要用户单独拍板。

## 1. 两端仓库与职责

| 仓库 | 分支 | 职责 |
|---|---|---|
| `C:/Users/xu.yan1/papers/recommendation-system-learning` | `experiments` | 论文资产生产：PDF、MinerU 解析、摘要、分类、小红书 note spec、发布闸门 |
| `C:/Users/xu.yan1/enkidu-blog/repo` | `source` | 文章组装与投递：`tools/*.py` → Notion DB；Actions `publish.yml` → Notion 同步到 Hexo 站点 |

个人主页（GitHub Pages）的数据来源是 **Notion 数据库**；Notion 是「已发布文章」的权威存储，
站点是它的镜像。`notion_sync.py` 每 30 分钟把 Notion 中 `status: Published` 的页面
拉成 `source/_posts/*.md` 并提交到 `source` 分支。地图视图另有
`tools/build_places.py` → `source/_data/places.json`，与本文链路并行、不要混淆。

## 2. 现有链路（逐段代码事实）

```
论文仓 data/
  ├── papers/*.pdf            论文原文
  ├── summaries/*.md          11 维摘要（含「英文标题」）
  └── parsed/<id>/*.md        MinerU 解析稿 + 图注 + 高清图
        │
        ▼  paper_inventory.build_manifest()      tools/paper_inventory.py:108
      PaperRecord（arxiv_id / quality_state / on_site / 标题一致性指纹）
        │
        ▼  publish_paper_library.run_pipeline() tools/publish_paper_library.py:49
      mineru_adapter.prepare_assets() → paper_article.build_article() (:158)
        │                              → validate_article() (:305)  ← 硬闸门
        ▼
      notion_publish.publish_article()          tools/notion_publish.py:331
        ├─ find_page_by_arxiv() 幂等：存在则 update_page，否则 create_page
        ├─ properties: title / slug / summary / arxiv_id / status
        ├─ upload_file() 逐图 + 源 PDF → markdown_to_blocks()
        └─ clear_children() + append_children()（覆盖式写正文）
        │
        ▼  Notion Database
        │
        ▼  .github/workflows/publish.yml（cron 每 30 分钟 / repository_dispatch）
      tools/notion_sync.py → source/_posts/*.md → hexo generate → Pages
```

`materialize_article()`（`paper_article.py:334`）是另一条**绕开 Notion** 的本地兜底：
直接把文章与图写进 `source/_posts` / `source/images/papers` / `source/papers`。
它只应在明确不走 Notion 时使用，否则会与 `notion_sync.py` 抢同一批文件。

## 3. 数据资产盘点（2026-11-11，本机只读）

| 资产 | 位置 | 数量 | 是否被现有管线消费 |
|---|---|---|---|
| 论文 PDF | `data/papers/` | 66 个顶层文件 | ✅ `build_manifest` 按文件名 arXiv id 索引 |
| 摘要 md | `data/summaries/` | 283 个顶层文件 | ✅ 取「最大文件」作该 id 的摘要 |
| 解析目录 | `data/parsed/` | 187 个子目录、432 个 md | ✅ 递归索引 `*.md` |
| 注册表 | `data/registry/papers.jsonl` | 113+ 行 | ❌ 博客仓不读 |
| 小红书定稿 | `redbook/notes/*.yaml` | 14 篇 spec | ❌ 博客仓完全不读 |
| 运行记录 | `data/logs/runs.jsonl` | 结构化 JSONL | ❌ 与 Notion 无关 |

**关键限制**：`paper_inventory.py:14` 的 `ARXIV_ID = \d{4}\.\d{4,5}` 只认 arXiv 风格 id。
`redbook/notes/` 里的 `10.1145_3847662`（DOI）、`3773078.3831765`、`TiZQnKDIHq`（TMLR）
这类论文**天然进不了 manifest**，必须先建 id 映射（或改索引规则）才能谈接入。
`tools/paper_exclusions.json` 还永久排除了 `2504.00678` / `2505.00556`，
注释明确写着「未显式复核不得重新导入」。

## 4. 四个断点

| # | 断点 | 证据 | 影响 |
|---|---|---|---|
| 1 | 默认库路径指向另一台机器 | `publish_paper_library.py:149`、`paper_inventory.py:175` 默认 `D:/recommendation-system-learning` | 本机不显式传 `--library-root` 就得到空 manifest；CI 上更不可能对 |
| 2 | 本机无 Notion 凭据 | 当前 shell 无 `NOTION_TOKEN` / `NOTION_DATABASE_ID`；`run_pipeline` 在 `--write-notion` 且无 DB id 时直接 `ValueError` | 只能 dry-run；写模式的密钥只存在于 GitHub Actions secrets |
| 3 | 触发方向只有一半 | `.github/workflows/publish.yml` 的 job 是 `Sync Notion -> Markdown`（`python tools/notion_sync.py`），没有「论文仓 → Notion」步骤 | 论文解析结果必须人工在本机推一次，或新增跨仓 workflow |
| 4 | 内容源错配 | `build_article(record, parsed, summary)` 吃 `PaperRecord` + 解析资产 + 摘要；`redbook/notes/<slug>.yaml` 是 ≤1000 字的小红书定稿正文 | note spec 不能「顺手」变成 Notion 长文；两者口径、闸门、目检流程都不同 |

### 4.1 质量闸门（`validate_article`，会被硬拒绝）

`REQUIRED_SECTIONS` 全部出现；正文中不得出现 `LEAK_MARKERS`
（`本课题 / 我们的实验 / 我们的方法 / MMEACR / E14 / E15 / MIG / syn 专家`）；
**所有百分数必须能在源文本里找到**（`unsupported numeric claim`）；
必须有 `https://arxiv.org/abs/<id>`；必须有至少一张高清图且每张有图注；
必须有「图示解释：」；源 PDF 存在。任何一条不过即 `blocked`，不会写 Notion。

这条闸门意味着「文章解析内容」不能原样倒进 Notion：内部实验结论、未在原文出现的
百分比、无图注的裁图都会被拦。这是**保护性设计，不应为接入而放宽**。

### 4.2 写入语义的三个风险

- `publish_article` 默认 `status = "Invisible"`，只有 `--promote` 才写 `Published`；
  未授权不得带 `--promote`。
- 幂等靠 `find_page_by_arxiv`，但命中后仍执行 `clear_children()` + 重新 append，
  即对已存在页面是**覆盖式重写**；`--refresh-existing` 还要求显式 `--ids`。
- `clear_children()` 会清掉页面上人工添加的内容。若 Notion 里已有人工编辑，
  应先导出备份（Notion 自带页面历史）再写。

## 5. 字段映射（现状，不是新增设计）

| 来源 | 目标 | 说明 |
|---|---|---|
| `PaperRecord.arxiv_id` | Notion `arxiv_id` (rich_text) | 幂等键，`find_page_by_arxiv` 用它查重 |
| `ArticleDraft.title` / `.slug` | Notion `title` / `slug` | `slug` 也被 `notion_sync.py` 的站点路由使用，需全库唯一 |
| 固定空串 | Notion `summary` | 当前实现写空，摘要正文在 page blocks 里 |
| `"Invisible"` / `"Published"` | Notion `status` | `notion_sync.py` 只同步 Published 页面 |
| `draft.markdown` | page blocks（heading_1 / paragraph / image / file） | `markdown_to_blocks` 逐段转换，每批最多 100 块 |
| `draft.figures[*]` | Notion 上传文件 + 图片块 | 走 `upload_file`，不依赖外链 |
| `draft.source_pdf` | Notion `file` 块 | 仅新建页或已有页带 PDF 时附加 |

注意 `notion_publish.py:120` 会按远端 data source 的实际 properties 过滤字段：
数据库缺列时字段被静默丢弃，**不会报错**。接入前应先读一次目标 DB schema 核对列名。

## 6. 三个接入深度

### 方案 A：只读盘点（推荐，本轮只做文档）

只做：把 `--library-root` 的正确路径与 dry-run 命令固化进本文；重跑一次 manifest；
产出「哪些论文可入 Notion、哪些被闸门拦、为什么」的清单；`redbook/notes` 与 Notion
的关系只在文档里写清。**不改任何仓库代码、不写 Notion。**

成本 ≈ 0，风险 ≈ 0，产出是后续所有方案的决策依据。

### 方案 B：人工单向补录

在博客仓加一个薄配置（环境变量或 `--library-root` 默认值）消除断点 1，
由人显式执行 `python tools/publish_paper_library.py --library-root ... --write-notion --ids <id>`，
默认 `Invisible`，人工在 Notion 核对后再决定是否 `--promote`。
需要：`NOTION_TOKEN` / `NOTION_DATABASE_ID`、目标 DB schema、以及用户明确授权。
不新增 workflow，不自动触发。

### 方案 C：自动同步（暂不建议）

新增跨仓 workflow：论文仓有新的 ready 解析 → 触发博客仓生成文章 → 写 Notion →
Actions 同步到站点。需要跨仓密钥、防重复发布、以及把 `validate_article` 的
失败回传到论文仓。在 A 的清单和人工目检流程稳定前做 C，等于把未经审核的长文
自动推上个人主页，风险最高。

### 独立决策 D：`redbook/notes/*.yaml` 要不要进 Notion

**建议不混流。** note spec 是小红书定稿（≤1000 字、纯文本、局限段、逐张目检、
话题白名单），Notion 文章是长文解析（多段章节、高清原图、PDF 附件、百分比溯源）。
若确实要关联，最多在 Notion 加一个 `xhs_note_slug` (rich_text) 指向 spec 文件名，
**不要**把 `body` 当成文章摘要或塞进 `summary`。

## 7. 实施清单（记录，本轮不执行）

| 阶段 | 动作 | 前置 |
|---|---|---|
| P0 | 重跑 dry-run 并核对 `total / ready / blocked` 与本文数字；列非 arXiv id 映射清单 | 无（只读） |
| P1 | 读目标 Notion DB 的 properties，核对 §5 五列是否齐备 | 用户提供凭据 / 或由 Actions 环境只读探测 |
| P2 | 选定 A / B / C 与 D；明确 `--promote` 的授权人 | 用户拍板 |
| P3 | 若选 B：改博客仓默认路径为环境变量 + 加幂等/备份检查；若选 C：再设计 workflow | 允许改 `enkidu-blog/repo` |
| P4 | 人工在 Notion 核对首篇（建议 `2608.14429`）后再批量 | 逐篇目检 |

## 8. 红线

1. 本轮不写 Notion，不执行 `--write-notion` / `--promote` / `--materialize`。
2. 不把 `NOTION_TOKEN` / `NOTION_DATABASE_ID` 写进任何仓库、文档或 `.env` 副本。
3. 不放宽 `validate_article` 的任何一条（尤其 `LEAK_MARKERS` 与百分比溯源）。
4. `paper_exclusions.json` 里两个 id 未经显式复核不得重导。
5. 博客仓当前 `source` 分支有 3 个未跟踪文件；Actions 每次运行会提交
   `content: sync Notion incrementally`，本地极易落后 —— 动手前先 `git fetch` 看分歧，
   且**判断远程分支一律用 `git ls-remote`**（该仓 refspec 曾只配 `main`）。
6. 不新建框架：复用 `tools/` 现有 5 个模块；默认远程分支是 `source` 不是 `main`。
7. `.workbuddy/` 已被 `.gitignore` 忽略，项目级 skill 拉不到；跨 IDE 规则只放 `AGENTS.md` / `.agents/skills/`。

## 9. 验收命令（只读，供 P0 使用）

在博客仓 `tools/` 下、Python 3.11+ 且装有 `requests / Pillow / pyyaml / PyMuPDF` 时：

```bash
python tools/publish_paper_library.py \
  --library-root "C:/Users/xu.yan1/papers/recommendation-system-learning" \
  --batch ready \
  --report "<临时目录>/notion_dryrun_report.json"

python tools/paper_inventory.py \
  --library-root "C:/Users/xu.yan1/papers/recommendation-system-learning" \
  --output "<临时目录>/paper_publication_manifest.json"
```

`--report` / `--output` 一律写临时目录，不要写进任一仓库（根 `.gitignore` 含 `*.json`）。
返回值 `1` 表示存在 blocked 条目，属预期，不代表链路故障。

## 10. 待用户拍板

1. 是否允许改 `enkidu-blog/repo`（本轮完全未动，含 3 个未跟踪文件）。
2. 是否提供 Notion 凭据 / 目标 DB schema，或仅接受只读盘点。
3. 选 A / B / C；以及 D 是否需要 `xhs_note_slug` 关联字段。
4. 非 arXiv id（`10.1145/3847662` 等）是否要建映射进入 Notion。
5. 谁负责长文的人工目检与 `--promote` 授权。
