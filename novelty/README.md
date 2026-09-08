# novelty — 论文创新性分析引擎

基于 `docs/novelty_analysis_engine_design.md` 与 `docs/innovation-tools-survey.md` 实现，
作为既有论文管线（MinerU→DeepSeek 摘要→分类→图谱）的**创新性分析扩展层**。

## 定位
增强人工对论文的深度理解（四维度拆解 + 与文献图谱对比 + 差异分析），**非全自动评判**。
工具只输出可追溯的「差异点」与证据片段，附 OpenNovelty 式三态标签
`can_refute / cannot_refute / unclear`，**不做"新颖/不新颖"终审判定**。

## 安装
```bash
pip install -r requirements.txt -r deploy/requirements-novelty.txt
# 仅需核心分析（无 REST/嵌入模型）：stdlib + pydantic + requests 即可跑 pure 后端
```

## 快速开始
```bash
# CLI：分析一篇已在 data/parsed 中的论文
python -m novelty.cli analyze --arxiv-id 2605.28175 --top-k 10
python -m novelty.cli analyze --arxiv-id 2605.28175 --embedder tfidf --no-online
python -m novelty.cli list-corpus

# REST 服务
uvicorn novelty.serve:app --host 0.0.0.0 --port 8000
#   GET  /health
#   POST /analyze  {"arxiv_id":"2605.28175","top_k":10,"embedder":"tfidf","use_online":true}

# 作为 skill 接入既有工厂
from skills.base_module import get_skill
r = get_skill("novelty-analyze").execute(arxiv_id="2605.28175")
```

## 模块
| 模块 | 职责 | 设计文档对应 |
|------|------|--------------|
| `extractor.py` | 四维度拆解 + 贡献句/声明抽取（LLM+启发式） | §2/§5 |
| `corpus.py` | 本地快照知识图谱（加载 data/parsed + summaries） | §3 |
| `embedder.py` | 表示引擎 SPECTER2/MiniLM/TF-IDF/纯Python（可降级） | §2 |
| `index.py` | 向量检索 faiss/numpy/linear 回退 | §3 |
| `graph_query.py` | 图谱查询：复用 CitationCollector(S2)+OpenAlex | §1/§3 |
| `contrast.py` | FactReview 设计轴差异矩阵 + 三态标签 | §4 |
| `report.py` | 报告生成（差异矩阵+证据+不下终审声明） | §4 |
| `engine.py` | 编排全流程 | §1 |
| `analyzer_skill.py` | 注册 `novelty-analyze` skill | — |
| `cli.py` / `serve.py` | CLI / FastAPI 服务 | §7 |

## 测试
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
测试默认用 `pure` 嵌入后端，零外部依赖即可通过。

## 运维
见 `deploy/ops.md`（Docker 编排、监控、定时同步、成本、排查）。
