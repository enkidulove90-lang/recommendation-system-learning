"""Task 1 intake API acceptance: instant answer, backpressure, status, SSE."""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from redbook.api.main import create_app
from redbook.orchestration import models
from redbook.orchestration.queue import SqliteQueueBackend
from redbook.orchestration.worker import NoopHandler, Worker


@pytest.fixture()
def client(tmp_path):
    backend = SqliteQueueBackend(tmp_path / "state" / "orchestration.sqlite",
                                 max_depths={"intake": 2}, backoff_seconds=0.0)
    app = create_app(backend)
    return TestClient(app), backend


def test_intake_answers_immediately_with_job_id(client):  # TC7 intake half
    client, _ = client
    response = client.post("/intake", json={"paper_id": "2611.17921"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True and body["state"] == "QUEUED" and body["queue"] == "intake"


def test_intake_backpressure_returns_429_with_structured_code(client):  # TC8
    client, _ = client
    client.post("/intake", json={"paper_id": "a"})
    client.post("/intake", json={"paper_id": "b"})
    third = client.post("/intake", json={"paper_id": "c"})
    assert third.status_code == 429
    detail = third.json()["detail"]
    assert detail["ok"] is False and detail["code"] == "E_QUEUE_FULL"
    assert detail["retryable"] is True and detail["next_step"]


def test_status_reports_state_and_events(client):
    client, _ = client
    job_id = client.post("/intake", json={"paper_id": "x"}).json()["job_id"]
    status = client.get(f"/status/{job_id}")
    assert status.status_code == 200
    body = status.json()
    assert body["state"] == "QUEUED" and body["payload_ref"] == "note:x"
    assert [event["step"] for event in body["events"]] == ["intake"]


def test_unknown_job_returns_404(client):
    client, _ = client
    assert client.get("/status/missing").status_code == 404


def test_worker_drain_completes_intake_job_end_to_end(client):  # TC7
    client, backend = client
    job_id = client.post("/intake", json={"paper_id": "2611.17921"}).json()["job_id"]
    Worker(backend).drain(NoopHandler())
    body = client.get(f"/status/{job_id}").json()
    assert body["state"] == models.VERIFIED
    assert [event["step"] for event in body["events"]] == ["intake", "claim", "complete"]


def test_sse_stream_emits_events_and_closes_on_terminal(client):
    client, backend = client
    job_id = client.post("/intake", json={"paper_id": "sse"}).json()["job_id"]
    Worker(backend).drain(NoopHandler())
    with client.stream("GET", f"/events/{job_id}") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        payload = b"".join(response.iter_bytes()).decode("utf-8")
    lines = [line for line in payload.splitlines() if line.startswith("data: ")]
    states = [json.loads(line[6:])["state"] for line in lines]
    assert states == ["QUEUED", "RUNNING", "VERIFIED"]


def test_cancel_endpoint_requests_cancellation(client):
    client, _ = client
    job_id = client.post("/intake", json={"paper_id": "cancel"}).json()["job_id"]
    assert client.post(f"/status/{job_id}/cancel").json()["ok"] is True
    assert client.get(f"/status/{job_id}").json()["cancel_requested"] is True
