"""内容事件编排 REST 服务（content_events/serve.py）。

把 CLI 能力暴露为 HTTP 接口，便于自动化/调度器/CI 远程触发内容生命周期编排。

安全边界（继承设计 §8 + 优化 §6）：
  - /process-queue 默认 dry_run=True（沙箱安全：只写本地待发布包，不触达真实平台）。
  - 仅在请求体显式传 dry_run=false 时，才允许 approved 真实平台项尝试 stage；
    沙箱无登录会话时仍降级 needs_review，绝不会自动 publish。
  - /collect-feedback 只读采集反馈观察窗口，不点赞/评论/关注/删帖。

运行：
  uvicorn content_events.serve:app --host 0.0.0.0 --port 8080
或（Docker）：docker compose -f content_events/deploy/docker-compose.yml up
"""
from __future__ import annotations

import logging
import os
import sys

import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from content_events import orchestrator  # noqa: E402
from content_events.retry import RetryPolicy  # noqa: E402

logger = logging.getLogger("content_events.serve")
app = FastAPI(title="Content Events Orchestrator", version="1.0.0")


# --------------------------------------------------------------------------- #
# 请求模型
# --------------------------------------------------------------------------- #
class ProcessQueueReq(BaseModel):
    root: str = Field(default=ROOT, description="项目根目录（含 publish_queue/）")
    publisher: str = Field(default="dryrun", description="dryrun | wechat | xhs")
    theme: str = Field(default="recsys-blue", description="DTLE 主题")
    dry_run: bool = Field(
        default=True,
        description="True=只写本地待发布包(安全)；False=允许 approved 项真实 stage(沙箱仍降级 needs_review)",
    )
    retry: bool = Field(default=False, description="对 stage 瞬时失败启用重试+退避")
    retry_attempts: int = Field(default=3, ge=1, le=10, description="最大重试次数")


class CollectFeedbackReq(BaseModel):
    root: str = Field(default=ROOT, description="项目根目录")


class StatusReq(BaseModel):
    root: str = Field(default=ROOT, description="项目根目录")
    paper_id: str | None = Field(default=None, description="仅返回该 paper_id 的状态")


# --------------------------------------------------------------------------- #
# 路由
# --------------------------------------------------------------------------- #
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "content_events"}


@app.post("/process-queue")
def process_queue(req: ProcessQueueReq) -> dict:
    if not os.path.isdir(os.path.join(req.root, "publish_queue")):
        raise HTTPException(status_code=400, detail=f"root 下无 publish_queue 目录: {req.root}")
    try:
        retry_policy = RetryPolicy(max_attempts=req.retry_attempts) if req.retry else None
        results, summary = orchestrator.run_once(
            req.root, publisher=req.publisher, theme=req.theme,
            dry_run=req.dry_run, retry_policy=retry_policy,
        )
    except Exception as exc:  # 整轮异常转为 500，便于自动化识别
        logger.exception("process-queue failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"process-queue error: {exc}")
    return {
        "processed": len(results),
        "summary": summary.as_dict(),
        "summary_text": summary.render(),
        "results": results,
        "dry_run": req.dry_run,
    }


@app.post("/collect-feedback")
def collect_feedback(req: CollectFeedbackReq) -> dict:
    try:
        return orchestrator.collect_feedback(req.root)
    except Exception as exc:
        logger.exception("collect-feedback failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"collect-feedback error: {exc}")


@app.get("/status")
def status(root: str = ROOT, paper_id: str | None = None) -> list:
    qroot = os.path.join(root, "publish_queue")
    out: list = []
    if not os.path.isdir(qroot):
        return out
    for name in sorted(os.listdir(qroot)):
        sp = os.path.join(qroot, name, "state.json")
        if not os.path.exists(sp):
            continue
        try:
            with open(sp, encoding="utf-8") as _sf:
                d = json.load(_sf)
        except (json.JSONDecodeError, OSError):
            continue
        if paper_id and d.get("paper_id") != paper_id:
            continue
        out.append(d)
    return out


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
