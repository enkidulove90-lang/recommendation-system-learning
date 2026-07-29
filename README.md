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
