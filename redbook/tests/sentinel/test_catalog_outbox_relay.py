"""Outbox handoff is atomic, idempotent, and platform specific."""
import json
import sys

from paper_intake.catalog_governance import CatalogGovernance, IdentityEvidence
from redbook.orchestration.catalog_relay import CatalogOutboxRelay
from redbook.cli import main as redbook_main


def _ready_store(path):
    store = CatalogGovernance(path)
    store.import_records([{
        "source": "recsys_program", "source_id": "2026:bonsai", "title": "BONSAI Paper",
        "paper_url": "https://recsys.acm.org/recsys26/session-1/",
        "venue_name": "ACM RecSys 2026", "venue_type": "conference-paper",
        "publication_year": 2026, "topics": ["Semantic IDs"],
        "topic_source": "conference_session", "authors": ["Jingzhe Liu"],
    }])
    paper_id = "recsys_program:2026:bonsai"
    store.verify_identity(paper_id, IdentityEvidence(
        title="BONSAI Paper", authors=("Jingzhe Liu",),
        paper_url="https://arxiv.org/abs/2607.16633", arxiv_id="2607.16633",
        published_at="2026-07-20", authority="arxiv",
        evidence_url="https://export.arxiv.org/api/query?id_list=2607.16633"))
    store.admit(paper_id, "homepage", topic_terms=("Semantic IDs",))
    store.admit(paper_id, "wechat", topic_terms=("Semantic IDs",))
    return store


def test_relay_creates_only_admitted_platform_jobs_and_is_idempotent(tmp_path):
    path = tmp_path / "state.sqlite"
    store = _ready_store(path)
    relay = CatalogOutboxRelay(path)
    assert relay.run_once(limit=10) == {"sent": 2, "duplicates": 0, "deferred": 0, "dead": 0}
    assert relay.run_once(limit=10)["sent"] == 0
    # Simulate an old receipt marker surviving while the consumed flag is lost.
    with store._connect() as db:
        db.execute("UPDATE catalog_outbox SET consumed_at=NULL WHERE platform='homepage'")
    assert relay.run_once(limit=10)["duplicates"] == 1
    with store._connect() as db:
        jobs = db.execute("SELECT payload_ref FROM jobs ORDER BY payload_ref").fetchall()
        assert [r[0] for r in jobs] == [
            "sentinel:homepage:arxiv:2607.16633", "sentinel:wechat:arxiv:2607.16633"]
        assert db.execute("SELECT COUNT(*) FROM catalog_event_deliveries").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM paper_pool_platform_delivery").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM catalog_outbox WHERE consumed_at IS NULL").fetchone()[0] == 0


def test_relay_cli_uses_explicit_persistent_database(tmp_path, monkeypatch, capsys):
    path = tmp_path / "state.sqlite"
    _ready_store(path)
    monkeypatch.setattr(sys, "argv", ["redbook.cli", "catalog-relay", "--database", str(path)])
    redbook_main()
    assert json.loads(capsys.readouterr().out)["sent"] == 2
    monkeypatch.setattr(sys, "argv", ["redbook.cli", "catalog-relay", "--database", str(path)])
    redbook_main()
    assert json.loads(capsys.readouterr().out)["sent"] == 0


def test_relay_rolls_back_crash_then_retries_without_duplicate(tmp_path):
    path = tmp_path / "state.sqlite"
    store = _ready_store(path)
    tripped = False

    def fail_once():
        nonlocal tripped
        if not tripped:
            tripped = True
            raise RuntimeError("simulated worker crash")

    relay = CatalogOutboxRelay(path, retry_delay_seconds=0, after_job_insert=fail_once)
    assert relay.run_once(limit=1)["deferred"] == 1
    with store._connect() as db:
        assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
    assert relay.run_once(limit=10)["sent"] == 2
    with store._connect() as db:
        assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 2


def test_poison_event_goes_to_dead_letter_without_blocking_later_event(tmp_path):
    path = tmp_path / "state.sqlite"
    store = _ready_store(path)
    with store._connect() as db:
        db.execute("UPDATE catalog_outbox SET payload_json='{}' WHERE platform='homepage'")
    report = CatalogOutboxRelay(path).run_once(limit=10)
    assert report["dead"] == 1 and report["sent"] == 1
    with store._connect() as db:
        row = db.execute("SELECT dead_letter_reason FROM catalog_outbox WHERE platform='homepage'").fetchone()
        assert row[0] == "invalid_event_payload"
        assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1


def test_retry_exhaustion_enters_dead_letter(tmp_path):
    path = tmp_path / "state.sqlite"
    store = _ready_store(path)
    relay = CatalogOutboxRelay(path, max_attempts=2, retry_delay_seconds=0,
                               after_job_insert=lambda: (_ for _ in ()).throw(RuntimeError("down")))
    assert relay.run_once(limit=1)["deferred"] == 1
    assert relay.run_once(limit=1)["dead"] == 1
    with store._connect() as db:
        event = db.execute("SELECT attempts, dead_letter_reason FROM catalog_outbox ORDER BY id LIMIT 1").fetchone()
        assert tuple(event) == (2, "RuntimeError")
        assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
