"""
novelty/serve.py — FastAPI REST 服务（运维部署）

提供:
    GET  /health       健康检查（含嵌入后端/语料规模）
    POST /analyze      {arxiv_id, top_k?, embedder?, use_online?} -> NoveltyReport(JSON)
    GET  /corpus       {limit?} 本地语料列表

运行:
    pip install fastapi uvicorn
    uvicorn novelty.serve:app --host 0.0.0.0 --port 8000
或:
    python -m novelty.serve

依赖仅在部署环境安装（requirements-novelty.txt 含 fastapi/uvicorn）。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from config import settings  # noqa: E402
from novelty.engine import NoveltyEngine  # noqa: E402
from novelty.report import ReportGenerator  # noqa: E402

app = FastAPI(title="Novelty Analysis Engine", version="0.1.0")

_engine: Optional[NoveltyEngine] = None


def get_engine(embedder: str = "tfidf", use_online: bool = True) -> NoveltyEngine:
    global _engine
    if _engine is None:
        _engine = NoveltyEngine(
            data_dir=settings.DATA_DIR,
            embedder_kind=embedder,
            use_s2=use_online,
            use_openalex=use_online,
            top_k=10,
        )
    return _engine


class AnalyzeRequest(BaseModel):
    arxiv_id: str = Field(..., description="arXiv ID，需已在本地语料 data/parsed 中")
    top_k: int = 10
    embedder: str = "tfidf"
    use_online: bool = True


class AnalyzeResponse(BaseModel):
    arxiv_id: str
    title: str
    markdown: str
    report: dict


@app.get("/health")
def health():
    eng = get_engine()
    return {
        "status": "ok",
        "engine_version": "novelty-0.1.0",
        "embedder": eng.embedder.kind,
        "corpus_size": len(eng._ensure_corpus().records),
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    eng = get_engine(req.embedder, req.use_online)
    eng.top_k = req.top_k
    report = eng.analyze(req.arxiv_id)
    if report.meta.get("error") == "target_not_in_corpus":
        raise HTTPException(status_code=404, detail=report.summary_note)
    md, _ = ReportGenerator().generate(report)
    return AnalyzeResponse(arxiv_id=req.arxiv_id, title=report.title, markdown=md, report=report.model_dump())


@app.get("/corpus")
def corpus(limit: int = 20):
    eng = get_engine()
    recs = eng._ensure_corpus().records[:limit]
    return [{"arxiv_id": r.arxiv_id, "title": r.title, "year": r.year} for r in recs]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
