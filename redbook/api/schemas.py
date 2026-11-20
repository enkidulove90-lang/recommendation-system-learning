"""Request/response schemas for the intake API (Pydantic v2)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class IntakeRequest(BaseModel):
    paper_id: str = Field(min_length=1, max_length=128,
                          description="note slug, e.g. 2611.17921")
    run_id: str = Field(default="", max_length=128)


class IntakeAccepted(BaseModel):
    ok: bool = True
    job_id: str
    state: str = "QUEUED"
    queue: str = "intake"


class StatusResponse(BaseModel):
    ok: bool = True
    job_id: str
    state: str
    attempt: int
    cancel_requested: bool
    payload_ref: str
    last_code: str | None = None
    events: list[dict] = []
