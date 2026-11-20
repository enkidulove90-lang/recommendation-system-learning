"""Intake API: receive fast, deliver slow.

``POST /intake`` answers in milliseconds with a job id (or HTTP 429 with the
structured ``E_QUEUE_FULL`` envelope when the bounded queue is saturated);
the real pipeline runs asynchronously through the queue. ``GET /status`` and
``GET /events`` expose the job lifecycle; the SSE stream ends when the job
reaches a terminal state.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from redbook.infrastructure.delivery_errors import (
    E_QUEUE_FULL, policy_for,
)
from redbook.orchestration import models
from redbook.orchestration.queue import QueueBackend, QueueFullError, SqliteQueueBackend
from .schemas import IntakeAccepted, IntakeRequest, StatusResponse


def create_app(queue: QueueBackend | None = None, *,
               data_root: Path = Path("data")) -> FastAPI:
    backend = queue or SqliteQueueBackend(
        data_root / "state" / "orchestration.sqlite",
        max_depths={"intake": 2},
    )
    app = FastAPI(title="redbook intake", version="0.1.0")

    @app.post("/intake", response_model=IntakeAccepted)
    def intake(request: IntakeRequest) -> IntakeAccepted:
        try:
            job = backend.enqueue(
                "intake", f"note:{request.paper_id}", run_id=request.run_id,
                enqueue_step="intake",
            )
        except QueueFullError as error:
            policy = policy_for(error.code)
            raise HTTPException(
                status_code=429,
                detail={
                    "ok": False, "code": policy["code"],
                    "message": error.message, "retryable": policy["retryable"],
                    "next_step": policy["next_step"],
                },
            ) from error
        return IntakeAccepted(job_id=job.job_id, state=job.state, queue=job.queue)

    @app.get("/status/{job_id}", response_model=StatusResponse)
    def status(job_id: str) -> StatusResponse:
        job = backend.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail={"ok": False, "code": "E_NOT_FOUND"})
        return StatusResponse(
            job_id=job.job_id, state=job.state, attempt=job.attempt,
            cancel_requested=job.cancel_requested, payload_ref=job.payload_ref,
            last_code=job.last_code, events=backend.events(job_id),
        )

    @app.post("/status/{job_id}/cancel")
    def cancel(job_id: str) -> dict:
        job = backend.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail={"ok": False, "code": "E_NOT_FOUND"})
        return {"ok": backend.cancel(job_id), "job_id": job_id}

    @app.get("/events/{job_id}")
    async def events(job_id: str) -> StreamingResponse:
        async def stream():
            last_seq = 0
            while True:
                job = backend.get_job(job_id)
                if job is None:
                    yield _sse(0, {"ok": False, "code": "E_NOT_FOUND"})
                    return
                for event in backend.events(job_id):
                    if event["seq"] > last_seq:
                        last_seq = event["seq"]
                        yield _sse(event["seq"], event)
                if models.is_terminal(job.state):
                    return
                await asyncio.sleep(0.2)

        return StreamingResponse(stream(), media_type="text/event-stream")

    return app


def _sse(seq: int, payload: dict) -> str:
    return f"id: {seq}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


app = None  # created via create_app() in tests / uvicorn factory mode
