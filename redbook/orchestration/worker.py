"""Resident worker skeleton: claim -> heartbeat -> handler -> receipt.

Three execution modes keep the low-ops contract: ``run_once`` for a single
job, ``drain`` until the queue is empty (CLI/cron friendly), ``run_forever``
for a resident daemon. A background heartbeat thread keeps the lease alive
while a long handler runs; a stale lease (crashed worker) is recovered by the
queue itself when another worker claims after expiry. The startup hook
receives the registry so a deployment can wire read-only reconciliation
(``redbook.orchestration.reconcile``) before the first claim.
"""
from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Callable

from redbook.infrastructure.delivery_errors import (
    E_UNKNOWN_MANUAL, OrchestrationError,
)
from . import models
from .models import Job, Receipt
from .queue import QueueBackend

Handler = Callable[[Job, Callable[[], None]], str]
OnStart = Callable[[Any], None]


class NoopHandler:
    """Terminal handler for queue/worker tests and smoke drains."""

    def __call__(self, job: Job, heartbeat: Callable[[], None]) -> str:
        heartbeat()
        return models.VERIFIED


class SaveDraftHandler:
    """Map a ``note:<paper_id>`` job onto the existing draft-only workflow."""

    def __init__(self, data_root, notes_dir=None) -> None:
        from redbook.application.paper_workflow import PaperCreationWorkflow
        self.workflow = PaperCreationWorkflow(data_root)
        self.notes_dir = notes_dir

    def __call__(self, job: Job, heartbeat: Callable[[], None]) -> str:
        from redbook.infrastructure.delivery_errors import DeliveryError
        paper_id = job.payload_ref.removeprefix("note:")
        heartbeat()
        result = self.workflow.publish_note(paper_id, notes_dir=self.notes_dir)
        heartbeat()
        if result.get("ok"):
            return models.SAVED_UNVERIFIED if result.get("state") == "SAVED_UNVERIFIED" \
                else models.VERIFIED
        raise DeliveryError(
            str(result.get("error", "note action failed")),
            str(result.get("error_code") or E_UNKNOWN_MANUAL),
            result.get("error_details") if isinstance(result.get("error_details"), dict) else None,
        )


HANDLERS: dict[str, Handler] = {"noop": NoopHandler()}


def register_handler(name: str, handler: Handler) -> None:
    HANDLERS[name] = handler


class Worker:
    def __init__(self, backend: QueueBackend, *, worker_id: str = "",
                 heartbeat_interval_seconds: float = 10.0,
                 lease_ttl_seconds: float = 60.0,
                 on_start: OnStart | None = None) -> None:
        self.backend = backend
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.heartbeat_interval = heartbeat_interval_seconds
        self.lease_ttl = lease_ttl_seconds
        self.on_start = on_start

    # -- heartbeat ----------------------------------------------------------
    def _start_heartbeat(self, job_id: str) -> Callable[[], None]:
        stop = threading.Event()

        def beat() -> None:
            while not stop.wait(self.heartbeat_interval):
                self.backend.heartbeat(job_id, self.worker_id,
                                       lease_ttl_seconds=self.lease_ttl)

        thread = threading.Thread(target=beat, daemon=True, name=f"hb-{job_id[:8]}")
        thread.start()

        def sync() -> None:
            self.backend.heartbeat(job_id, self.worker_id,
                                   lease_ttl_seconds=self.lease_ttl)

        sync.stop = stop  # type: ignore[attr-defined]
        return sync

    @staticmethod
    def _stop_heartbeat(sync: Callable[[], None]) -> None:
        stop = getattr(sync, "stop", None)
        if stop is not None:
            stop.set()

    # -- execution ----------------------------------------------------------
    def _execute(self, job: Job, handler: Handler) -> Receipt:
        sync = self._start_heartbeat(job.job_id)
        try:
            target_state = handler(job, sync)
            models.validate_transition(models.RUNNING, target_state)
            latest = self.backend.get_job(job.job_id)
            if latest is not None and latest.cancel_requested:
                return self.backend.complete(job.job_id, self.worker_id, models.CANCELLED)
            return self.backend.complete(job.job_id, self.worker_id, target_state)
        except OrchestrationError as error:
            return self.backend.fail(job.job_id, self.worker_id, error)
        except Exception as error:  # unknown -> manual, never silently retried
            return self.backend.fail(
                job.job_id, self.worker_id,
                OrchestrationError(f"{type(error).__name__}: {error}", E_UNKNOWN_MANUAL),
            )
        finally:
            self._stop_heartbeat(sync)

    def run_once(self, handler: Handler) -> Receipt | None:
        if self.on_start is not None:
            self.on_start(self)
        job = self.backend.claim(self.worker_id, lease_ttl_seconds=self.lease_ttl)
        if job is None:
            return None
        return self._execute(job, handler)

    def drain(self, handler: Handler, *, max_jobs: int = 0) -> list[Receipt]:
        receipts: list[Receipt] = []
        while not max_jobs or len(receipts) < max_jobs:
            receipt = self.run_once(handler)
            if receipt is None:
                break
            receipts.append(receipt)
        return receipts

    def run_forever(self, handler: Handler, *, poll_interval_seconds: float = 2.0,
                    stop_event: threading.Event | None = None) -> None:
        stop = stop_event or threading.Event()
        while not stop.is_set():
            receipt = self.run_once(handler)
            if receipt is None:
                stop.wait(poll_interval_seconds)
