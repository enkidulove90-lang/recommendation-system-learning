"""Unified job model and state machine for the orchestration layer (M0 contract).

The states mirror the delivery lifecycle that already exists in the SQLite
registry (SAVING -> SAVED_UNVERIFIED -> VERIFIED) so a queue job and a
registry row can be reconciled through ``run_id``/``staged_id`` without a
second vocabulary. Transitions are forward-only; only a human reset may move
a job back to QUEUED (via ``cancel`` + re-enqueue).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from redbook.infrastructure.delivery_errors import OrchestrationError


# ---- canonical state vocabulary -------------------------------------------
QUEUED = "QUEUED"
RUNNING = "RUNNING"
GENERATED = "GENERATED"
SAVING = "SAVING"
SAVED_UNVERIFIED = "SAVED_UNVERIFIED"
VERIFIED = "VERIFIED"
PUBLISHED = "PUBLISHED"
MISSING = "MISSING"
MANUAL = "MANUAL"
FAILED_RETRYABLE = "FAILED_RETRYABLE"
FAILED_TERMINAL = "FAILED_TERMINAL"
CANCELLED = "CANCELLED"

TERMINAL_STATES = frozenset({VERIFIED, PUBLISHED, MISSING, MANUAL, FAILED_TERMINAL, CANCELLED})

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    QUEUED: frozenset({RUNNING, CANCELLED}),
    # QUEUED is reachable from RUNNING only via lease-expiry recovery (a dead
    # worker's job is taken over by another worker), never by business logic.
    RUNNING: frozenset({GENERATED, SAVING, SAVED_UNVERIFIED, VERIFIED, PUBLISHED,
                        MANUAL, FAILED_RETRYABLE, FAILED_TERMINAL, CANCELLED, QUEUED}),
    GENERATED: frozenset({SAVING, CANCELLED}),
    SAVING: frozenset({SAVED_UNVERIFIED, MANUAL, FAILED_RETRYABLE, FAILED_TERMINAL}),
    SAVED_UNVERIFIED: frozenset({VERIFIED, MANUAL, FAILED_RETRYABLE, FAILED_TERMINAL}),
    VERIFIED: frozenset({PUBLISHED, MISSING}),
    PUBLISHED: frozenset(),
    MISSING: frozenset({SAVING}),
    MANUAL: frozenset({QUEUED}),
    FAILED_RETRYABLE: frozenset({QUEUED}),
    FAILED_TERMINAL: frozenset({QUEUED}),
    CANCELLED: frozenset({QUEUED}),
}


class InvalidTransition(OrchestrationError):
    """Raised when a job state change violates the forward-only state machine."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            f"illegal transition {current} -> {target}",
            code="E_UNKNOWN_MANUAL",
            details={"current": current, "target": target},
        )


def validate_transition(current: str, target: str) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise InvalidTransition(current, target)


def is_terminal(state: str) -> bool:
    return state in TERMINAL_STATES


# ---- task model ------------------------------------------------------------
@dataclass
class Job:
    """A queueable unit of delivery work.

    ``payload_ref`` carries only an addressing reference (e.g. ``note:<slug>``
    or ``sha256:<hex>``) -- never body text or local paths, per the redaction
    rule of the receipt contract.
    """

    job_id: str
    queue: str
    payload_ref: str
    payload_digest: str
    state: str = QUEUED
    attempt: int = 0
    max_attempts: int = 3
    cancel_requested: bool = False
    lease_owner: str = ""
    lease_expires_at: str = ""
    last_code: str | None = None
    run_id: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id, "queue": self.queue,
            "payload_ref": self.payload_ref, "payload_digest": self.payload_digest,
            "state": self.state, "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "cancel_requested": self.cancel_requested,
            "lease_owner": self.lease_owner, "last_code": self.last_code,
            "run_id": self.run_id,
            "created_at": self.created_at, "updated_at": self.updated_at,
        }


@dataclass
class Attempt:
    """One claim-try of a job; failures accumulate without erasing history."""

    job_id: str
    attempt: int
    worker_id: str
    started_at: str
    finished_at: str = ""
    code: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id, "attempt": self.attempt,
            "worker_id": self.worker_id, "started_at": self.started_at,
            "finished_at": self.finished_at, "code": self.code,
            "message": self.message,
        }


@dataclass
class Receipt:
    """Stable terminal receipt; the dict form matches ``receipt_envelope``."""

    job_id: str
    state: str
    code: str = ""
    retryable: bool = False
    next_step: str = ""
    owner: str = ""
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.state in ({VERIFIED, PUBLISHED}),
            "job_id": self.job_id, "state": self.state, "code": self.code,
            "retryable": self.retryable, "next_step": self.next_step,
            "owner": self.owner, "evidence_ref": self.evidence_ref,
        }
