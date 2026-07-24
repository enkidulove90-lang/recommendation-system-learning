# recommendation-system

基于 arXiv 的推荐系统论文爬取与解析工具。

## 功能概览

- 🔍 **多主题搜索**：预置四大研究方向 (Agent 推荐、多模态推荐、LLM 召回、LLM 排序)
- 📄 **元数据提取**：自动提取标题、作者、摘要、发表日期、PDF 链接、arXiv 页面链接等
- 🧠 **PDF 解析**：可选接入 MinerU API 进行论文全文结构化解析
- 🧩 **模块化 Skill 架构**：搜索 / 元数据提取 / PDF 解析均为独立可复用技能
- 📦 **结构化输出**：按主题组织 JSON 输出，支持去重与增量更新

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 MINERU_API_KEY（PDF 解析需要；仅爬取可不填）

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
```

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
