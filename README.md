# recommendation-system

基于 arXiv 的推荐系统论文爬取与解析工具。

## 功能概览

- 🔍 **多主题搜索**：预置四大研究方向 (Agent 推荐、多模态推荐、LLM 召回、LLM 排序)
- 📄 **元数据提取**：自动提取标题、作者、摘要、发表日期、PDF 链接、arXiv 页面链接等
- 🧠 **PDF 解析**：可选接入 MinerU API 进行论文全文结构化解析
- 🧪 **论文知识摘要**：通过 DeepSeek 提取贡献、创新点、实验条件、效果及 Agent 开发价值
- 🧭 **Summary 2.0 研究画像**：结构化标签、实验事实、证据锚点、质量等级与本地筛选
- 🕸️ **研究关系与学习路径**：引用/语义关系图、可解释阅读顺序与 Profile 重排
- 🧩 **模块化 Skill 架构**：搜索 / 元数据提取 / PDF 解析均为独立可复用技能
- 📦 **结构化输出**：按主题组织 JSON 输出，支持去重与增量更新

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 MINERU_API_KEY 和 DEEPSEEK_API_KEY

# 3. 查看可用主题
python main.py list

# 4. 爬取所有主题
python main.py crawl-all

# 5. 爬取单个主题
python main.py crawl --topic llm-ranking --max 30

# 6. 自定义搜索
python main.py search --query 'all:"graph neural network" AND all:"recommendation"' --max 20

# 7. 解析单篇论文 PDF
python main.py parse --arxiv-id 2503.21460

# 8. 生成单篇 DeepSeek 知识摘要
python main.py summarize --arxiv-id 2503.21460

# 9. 为已有摘要批量补齐实验条件
python backfill_experiment_conditions.py --source profile
# 配置 DeepSeek 后也可使用：python backfill_experiment_conditions.py --source deepseek

# 10. 构建并校验全部 Summary 2.0 画像
python main.py profile --all
python main.py validate-profile --all

# 11. 按受控标签检索
python main.py search-profile --stage reranking --problem cold_start --quality B,C

# 12. 构建关系图并生成五条默认学习路径
python main.py build-relations --max-semantic-edges 6
python main.py learning-path --all

# 13. 使用本地 Profile、关系边和多样性约束重排
python main.py recommend --seed 2606.26859 --top-k 8 --use-profiles
```

## 单篇论文入库控制台

本机控制台把一篇论文按固定状态链送入网站：

```text
论文链接 / PDF → MinerU → DeepSeek → 质量检查 → Notion Draft
                                           ↓ 人工审核
                         Notion Published → GitHub Pages → 在线检查
```

GitHub Pages 仍然是静态展示站，Notion 是发布主库。网站同步脚本只查询
`status=Published` 且 `type=Post` 的记录，因此 Draft 不会提前出现在公开网站。

### 启动

1. 安装依赖：`pip install -r requirements.txt`。
2. 将 `.env.example` 复制为 `.env`，至少配置以下四项：
   `MINERU_API_KEY`、`DEEPSEEK_API_KEY`、`NOTION_TOKEN`、
   `NOTION_DATABASE_ID`。
3. 如需审核后立即触发网站构建，再配置 `GITHUB_TOKEN`；未配置时保留既有的
   定时构建作为后备。
4. 启动仅监听本机的服务：

```powershell
python -m paper_intake serve --host 127.0.0.1 --port 8765
```

随后打开 `http://127.0.0.1:8765/`。链接提交支持 arXiv 摘要页或 PDF 链接；
直接上传 PDF 时建议同时填写论文原始链接，便于生成可核验的 References。
本地 PDF 使用 MinerU 官方的签名上传流程，不会把 `file://` 地址交给云端。

### 状态与操作

| 状态 | 含义 | 可用操作 |
| --- | --- | --- |
| `received` | 已入队，尚未开始 | 取消 |
| `processing` | 正在执行一个处理步骤 | 等待或取消 |
| `blocked` | 图片、中文图解或文章结构未通过质量门 | 修正配置后从检查点重试 |
| `failed` | 外部服务或输入步骤失败 | 从失败步骤重试 |
| `awaiting_review` | Notion Draft 已创建，等待人工审核 | 打开 Notion、批准或取消 |
| `publishing` | 已批准并触发 GitHub Pages | 仅重试部署、检查公开页面 |
| `published` | 公开 URL 已返回 HTTP 200 | 完成 |
| `cancelled` | 停止后续步骤 | 原始文件仍保留 |

“审核通过并发布”会先把 Notion 状态改为 `Published`，再触发 GitHub workflow。
页面不会自动批准文章。发布后点击“检查公开页面”，只有目标 URL 实际返回成功，
本地任务才会进入 `published`。

### 故障恢复

- 每个步骤记录在 `data/paper_intake/jobs.sqlite3`，服务重启时会把正在运行的步骤
  标为中断，已成功的 MinerU 等步骤不会重复付费执行。
- 原始 PDF 保存在 `data/paper_intake/inbox/`，文章 JSON、Markdown、图片和 Notion
  前后快照保存在 `data/workflow_state/paper_intake/`。这些目录均被 Git 忽略。
- DeepSeek 或质量检查失败时，可从对应检查点重试；选择较晚步骤不会重跑 MinerU。
- GitHub 触发失败时使用“仅重试部署”，不会再次发布 Notion。
- Notion 内容需要回退时，使用保存的 `notion-before.md` 快照恢复为 Draft。
- 取消、失败和发布都不会自动删除 PDF、MinerU 产物或审计记录；确认备份和内容一致
  后再由维护者手动清理。
- 控制台 API 只返回审核字段，不返回 Token、本地文件路径、SHA-256 或全文解析内容。

## 数据存储约定

- `data/parsed/{arXiv ID}_{中文标题}/`：单篇论文资产包，包含 Markdown、原始 PDF 和 MinerU 图片。
- `data/summaries/{arXiv ID}_summary.md`：DeepSeek 论文知识摘要，统一包含实验条件。
- `data/metadata/recommendations/`：种子论文扩展产生的候选排序与推荐过程元数据。
- `data/profiles/{arXiv ID}.json`：Summary 2.0 机器可读研究画像。
- `data/evidence/{arXiv ID}.json`：画像结论对应的原文章节、字符范围与摘录。
- `data/reviews/{arXiv ID}.json`：Schema、标签、证据、哈希和一致性校验结果。
- `data/registry/`：论文登记、受控词表、数据集登记和 JSON Schema。
- `data/registry/quarantined_assets.yaml`：错配资产、修复方式和有效替代论文的审计记录。
- `data/relations/`：活跃论文之间的引用边和高置信语义边。
- `data/learning_paths/`：面向主题和难度生成的 JSON/Markdown 阅读路径。
- `data/metadata/papers/`：经核验的 arXiv 标题、作者和发布日期侧车数据。
- `data/papers/`：下载缓存；解析后 PDF 会同时归档到对应论文资产包。

`data/summaries/` 是人类阅读入口，`data/profiles/` 是筛选和后续关系构建的事实源。质量等级为 D 的论文不会进入可信实验事实检索。

## 项目结构

```
recommendation-system/
├── .env                  # 用户配置文件（含 MINERU_API_KEY）
├── .env.example          # 配置模板
├── .gitignore
├── README.md
├── requirements.txt
├── main.py               # CLI 入口
├── config/               # 全局配置（读取 .env）
│   ├── __init__.py
│   └── settings.py
├── skills/               # 可复用 Skill 模块
│   ├── __init__.py
│   ├── base_module.py    # BaseSkill 抽象基类 + 注册表
│   ├── arxiv_searcher.py # arXiv 论文搜索
│   ├── metadata_extractor.py # 元数据提取与清洗
│   └── pdf_parser.py     # MinerU PDF 解析
├── crawler/              # 爬取编排
│   ├── __init__.py
│   └── arxiv_crawler.py  # 主爬虫类
├── storage/              # 数据持久化
│   ├── __init__.py
│   └── paper_store.py    # JSON 存储与去重
├── utils/                # 通用工具
│   ├── __init__.py
│   └── helpers.py        # 日志、文本清理、重试
└── docs/                 # 文档
    └── TECHNICAL_DOC.md  # 详细技术文档
```

## 搜索主题

| 主题 | 描述 |
|------|------|
| `agent-recommendation` | Agent 技术与推荐系统交叉研究 |
| `multimodal-recommendation` | 多模态推荐系统研究 |
| `llm-recall` | LLM 参与推荐系统召回/候选生成阶段 |
| `llm-ranking` | LLM 参与预排序、排序、重排序阶段 |

爬取范围默认从 2024 年开始，可通过 `.env` 中的 `START_YEAR` 调整。
