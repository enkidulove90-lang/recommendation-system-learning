"""FastAPI application: REST + SSE for the ADA experiment console."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncIterator, Optional

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from .repository import Repository
from .runner import Runner
from .schemas import ConfigIn
from .service import Service, ServiceError

TERMINAL_RUN_STATES = {"succeeded", "failed", "cancelled", "blocked"}


def create_app(
    db_path: str,
    artifact_root: str,
    ada_root: Optional[str] = None,
    python_executable: Optional[str] = None,
) -> FastAPI:
    ada_root = ada_root or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    repo = Repository(db_path)
    runner = Runner(ada_root=ada_root, python_executable=python_executable)
    service = Service(repo=repo, runner=runner, artifact_root=artifact_root)

    app = FastAPI(title="ADA Experiment Platform")
    app.state.repo = repo
    app.state.service = service

    # -- REST ----------------------------------------------------------------

    @app.post("/api/configs/validate")
    def validate_config(body: ConfigIn):
        return service.validate(body)

    @app.post("/api/runs")
    def create_run(body: ConfigIn):
        try:
            return service.create_run(body)
        except ServiceError as exc:
            return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.get("/api/runs")
    def list_runs():
        return {"runs": service.list_runs()}

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str):
        try:
            return service.run_detail(run_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown run '{run_id}'")

    @app.post("/api/runs/{run_id}/start")
    def start_run(run_id: str):
        try:
            return service.start_run(run_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown run '{run_id}'")
        except ServiceError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @app.post("/api/runs/{run_id}/cancel")
    def cancel_run(run_id: str):
        try:
            return service.cancel_run(run_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown run '{run_id}'")
        except ServiceError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @app.get("/api/runs/{run_id}/artifacts")
    def run_artifacts(run_id: str):
        try:
            return {"artifacts": service.run_artifacts(run_id)}
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown run '{run_id}'")

    # -- SSE -----------------------------------------------------------------

    @app.get("/api/runs/{run_id}/events")
    async def run_events(
        run_id: str,
        last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
        last_seq: int = Query(default=0),
    ):
        try:
            service.run_detail(run_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown run '{run_id}'")

        resume_from = last_seq
        if last_event_id:
            try:
                resume_from = max(resume_from, int(last_event_id))
            except ValueError:
                pass

        async def stream() -> AsyncIterator[str]:
            seq = resume_from
            # Replay persisted events from the last event ID (no duplicates:
            # terminal events are deduped at write time).
            while True:
                events = service.run_events(run_id, seq)
                for ev in events:
                    seq = ev["seq"]
                    data = f"event: {ev['event']}\nid: {ev['seq']}\ndata: " \
                           f"{__import__('json').dumps(ev['payload'], default=str)}\n\n"
                    yield data
                    if ev["is_terminal"]:
                        return
                run = service.run_detail(run_id)
                if run["status"] in TERMINAL_RUN_STATES:
                    return
                await asyncio.sleep(0.2)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app
