"""Tests for the S4 consumption middleware (Phases 1-6).

All model calls are faked; no network, no real API keys required.
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

from paper_intake.asset_manifest import ContentAssetManifest
from paper_intake.catalog_store import CatalogRepository
from paper_intake.fact_pack import (
    FactPack,
    FACT_PACK_PROMPT_VERSION,
    build_fact_pack_prompt,
    parse_fact_pack_response,
)
from paper_intake.model_gateway import (
    ModelCallGateway,
    artifact_basename,
    sha256_file,
)


def _db(tmp_path: Path) -> Path:
    path = tmp_path / "catalog.sqlite3"
    repository = CatalogRepository(path)
    repository.close()
    return path


def test_fact_pack_preserves_site_geography_references_figures_and_formulae() -> None:
    pack = FactPack.model_validate({
        "canonical_id": "2026.findings-acl.1001", "source_hash": "hash",
        "model_id": "model", "prompt_version": "test",
        "facts": {"one_line": "summary", "paper_title": "Original title",
                  "venue_type": "conference", "published_date": "2026-01-02"},
        "platform_hints": {},
        "location": {"location_type": "affiliation", "affiliation_name": "University",
                     "affil_city": ["Beijing"], "venue_city": "Vienna",
                     "corresponding_city": "Beijing", "source": "paper p1"},
        "references": [{"title": "Prior paper", "paper_url": "https://example.org/paper",
                        "code_url": "https://github.com/example/repo", "source": "p9"}],
        "figures": [{"figure_id": "1", "path": "images/figure1.png", "caption": "Architecture",
                     "source_type": "pdf", "width": 1200, "height": 800, "sha256": "abc"}],
        "formulae": [{"latex": "x^2", "display_mode": "block", "source_location": "p3"}],
    }).model_dump()
    assert pack["facts"]["paper_title"] == "Original title"
    assert pack["facts"]["venue_type"] == "conference"
    assert pack["facts"]["published_date"] == "2026-01-02"
    assert pack["location"]["venue_city"] == "Vienna"
    assert pack["location"]["affil_city"] == ["Beijing"]
    assert pack["references"][0]["code_url"] == "https://github.com/example/repo"
    assert pack["references"][0]["verification_status"] == "unverified"
    assert pack["figures"][0]["sha256"] == "abc"
    assert pack["figures"][0]["visual_review_status"] == "pending"
    assert pack["formulae"][0]["latex"] == "x^2"
    parsed = parse_fact_pack_response(json.dumps(pack), pack["canonical_id"])
    assert parsed["references"][0]["paper_url"] == "https://example.org/paper"
    assert parsed["location"]["affil_city"] == ["Beijing"]


def test_legacy_fact_pack_keeps_new_metadata_unset() -> None:
    pack = FactPack.model_validate({
        "canonical_id": "arxiv:2601.00001", "source_hash": "hash",
        "model_id": "model", "prompt_version": "v1",
        "facts": {}, "platform_hints": {},
    }).model_dump()
    assert pack["location"] is None
    assert pack["references"] == []
    assert pack["figures"] == []
    assert pack["formulae"] == []


def test_fact_pack_parser_rejects_invalid_structured_references() -> None:
    payload = json.dumps({"facts": {}, "platform_hints": {}, "references": "not-a-list"})
    with pytest.raises(ValueError, match="references"):
        parse_fact_pack_response(payload, "arxiv:2601.00001")


def test_phase1_manifest_relative_path_and_idempotency(tmp_path) -> None:
    db = _db(tmp_path)
    manifest = ContentAssetManifest(db)
    source = tmp_path / "source.md"
    source.write_text("paper", encoding="utf-8")

    manifest.record("arxiv:2601.00001", "fact_pack", source, "h", "v1", "m1", "gateway")
    hit = manifest.lookup("arxiv:2601.00001", "fact_pack", "h", "v1", "m1")
    assert hit is not None
    assert not Path(hit["relative_path"]).is_absolute()
    assert ":" not in hit["relative_path"]  # no Windows drive prefix
    assert manifest.lookup("arxiv:2601.00001", "fact_pack", "other", "v1", "m1") is None
    assert manifest.lookup("arxiv:2601.00001", "fact_pack", "h", "v2", "m1") is None


def test_phase2_gateway_reuses_on_cache_hit(tmp_path) -> None:
    db = _db(tmp_path)
    source = tmp_path / "source.md"
    source.write_text("paper text", encoding="utf-8")
    calls = {"n": 0}

    def client(prompt: str) -> str:
        calls["n"] += 1
        return json.dumps({"facts": {"one_line": "ok"}, "platform_hints": {}})

    gateway = ModelCallGateway(ContentAssetManifest(db), client, Path(__file__).resolve().parents[1])
    kwargs = dict(
        canonical_id="arxiv:2601.00002", purpose="fact_pack", source=source,
        prompt_version="v1", model_id="m1",
        build_prompt=lambda p: p.read_text(encoding="utf-8"),
        parse_response=json.loads,
    )
    first = gateway.ensure(**kwargs)
    second = gateway.ensure(**kwargs)
    assert first == second
    assert calls["n"] == 1
    assert first.is_file()

    # Simulate a missing artifact without unlink(): the sandbox blocks deletes.
    # Rename to a unique name so repeated runs never collide with residue.
    import time
    first.rename(first.with_name(f"{first.name}.moved-{time.time_ns()}"))
    gateway.ensure(**kwargs)
    assert calls["n"] == 2  # self-healing

    gateway.ensure(**{**kwargs, "model_id": "m2"})
    assert calls["n"] == 3  # intentional invalidation


def test_phase3_fact_pack_schema_and_parse_failure(tmp_path) -> None:
    pack = FactPack(
        canonical_id="arxiv:2601.00003", source_hash="h", model_id="m",
        prompt_version="v1",
        facts={"one_line": "summary", "experiments": ["e1"], "keywords": ["k"]},
        platform_hints={"xhs": {"hook": "hook"}},
    )
    assert pack.schema_version == "fact-pack/v2"
    assert pack.facts.experiments == ["e1"]

    valid = json.dumps({"facts": {}, "platform_hints": {}})
    assert parse_fact_pack_response(valid, "arxiv:2601.00003") == json.loads(valid)

    with pytest.raises(ValueError, match="fact_pack parse failed"):
        parse_fact_pack_response("not-json", "arxiv:2601.00003")
    diagnostic = Path(__file__).resolve().parents[1] / "data" / "diagnostics" / "arxiv__2601.00003_fact_pack_error.json"
    assert diagnostic.is_file()


def test_phase4_narrative_uses_fact_pack_without_llm() -> None:
    from content_factory.narrative_engine import NarrativeEngine
    from content_factory.schemas import PaperSummary

    root = Path(__file__).resolve().parents[1]
    cid = "arxiv:2601.00004"
    artifact = root / "data" / "summaries" / f"{artifact_basename(cid, 'fact_pack')}.json"
    artifact.write_text(
        json.dumps({"platform_hints": {"xhs": {"hook": "FROM_FACT_PACK"}}}),
        encoding="utf-8")
    try:
        calls = {"n": 0}

        def llm(text: str, instruction: str) -> str:
            calls["n"] += 1
            return "FROM_LLM"

        summary = PaperSummary(raw={
            "title": "T", "methodology": "method RADAR",
            "main_contribution": "problem solved",
            "experimental_results": "16.5% gain", "limitations": "limits",
        })
        story = NarrativeEngine(polish=True, llm_callable=llm, canonical_id=cid).build(summary, cid)
        assert story.hook == "FROM_FACT_PACK"
        assert calls["n"] == 0
    finally:
        # Rename instead of unlink: the sandbox blocks deletions.  A unique
        # suffix keeps repeated runs from colliding.
        if artifact.exists():
            import time
            artifact.rename(artifact.with_name(
                f"{artifact.name}.consumed-{time.time_ns()}"))


def test_parse_event_carries_producing_job_and_catalog_identity(tmp_path) -> None:
    from scripts.daily_paper_ingest import emit_parse_completed

    db = _db(tmp_path)
    repository = CatalogRepository(db)
    emit_parse_completed(repository, "2026.findings-acl.1001", "parsed/a.md",
                         job_id="job-1", catalog_canonical_id="source:acl:1001",
                         pdf_path="papers/a.pdf", pdf_sha256="hash-a")
    repository.close()
    with sqlite3.connect(db) as connection:
        version, raw = connection.execute(
            "SELECT event_version,payload_json FROM outbox WHERE event_type='ParseCompleted'"
        ).fetchone()
    payload = json.loads(raw)
    assert version == 2
    assert payload["job_id"] == "job-1"
    assert payload["catalog_canonical_id"] == "source:acl:1001"
    assert payload["pdf_path"] == "papers/a.pdf"
    assert payload["pdf_sha256"] == "hash-a"


def test_compilation_input_resolves_event_job_not_newer_unrelated_job(tmp_path) -> None:
    from paper_intake.models import StepName
    from paper_intake.repository import JobRepository
    from scripts.content_bridge import resolve_event_inputs

    db = _db(tmp_path)
    repository = JobRepository(db)
    markdown = tmp_path / "parsed.md"
    markdown.write_text("original", encoding="utf-8")
    original_pdf = tmp_path / "original.pdf"
    original_pdf.write_bytes(b"%PDF-original")
    newer_pdf = tmp_path / "newer.pdf"
    newer_pdf.write_bytes(b"%PDF-newer")
    job = repository.create_job(source_type="url", source_url="https://example.org/a.pdf")
    repository.update_job(job.job_id, canonical_id="acl:1", upload_path=str(original_pdf))
    repository.start_step(job.job_id, StepName.MINERU_PARSE)
    repository.complete_step(job.job_id, StepName.MINERU_PARSE, output={"markdown_path": str(markdown)})
    later = repository.create_job(source_type="url", source_url="https://example.org/b.pdf")
    repository.update_job(later.job_id, canonical_id="acl:1", upload_path=str(newer_pdf))
    repository.close()
    result = resolve_event_inputs({"canonical_id": "acl:1", "job_id": job.job_id,
                                   "markdown_path": str(markdown), "pdf_path": str(original_pdf)}, db)
    assert result.job_id == job.job_id
    assert result.pdf_path == original_pdf
    assert result.markdown_path == markdown


def test_compilation_input_rejects_legacy_event_with_ambiguous_jobs(tmp_path) -> None:
    from paper_intake.models import StepName
    from paper_intake.repository import JobRepository
    from scripts.content_bridge import resolve_event_inputs

    db = _db(tmp_path)
    repository = JobRepository(db)
    markdown = tmp_path / "shared.md"
    markdown.write_text("paper", encoding="utf-8")
    for index in range(2):
        job = repository.create_job(source_type="url", source_url=f"https://example.org/{index}")
        repository.update_job(job.job_id, canonical_id="acl:1")
        repository.start_step(job.job_id, StepName.MINERU_PARSE)
        repository.complete_step(job.job_id, StepName.MINERU_PARSE, output={"markdown_path": str(markdown)})
    repository.close()
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_event_inputs({"canonical_id": "acl:1", "markdown_path": str(markdown)}, db)


def test_content_bridge_rejects_event_without_producing_job_before_model_call(tmp_path, monkeypatch) -> None:
    import scripts.content_bridge as bridge
    from paper_intake.repository import JobRepository

    db = _db(tmp_path)
    JobRepository(db).close()
    markdown = tmp_path / "paper.md"
    markdown.write_text("paper", encoding="utf-8")
    event = {"id": 1, "payload_json": json.dumps({"canonical_id": "acl:1", "markdown_path": str(markdown)})}
    def fail_if_called(*args, **kwargs):
        raise AssertionError("model gateway must not be created")
    monkeypatch.setattr(bridge, "ModelCallGatewayWithFallback", fail_if_called)
    with pytest.raises(ValueError, match="producing job"):
        bridge._consume_event(event, dry_run=True, db_path=db)


def test_phase5_emit_parse_completed_is_idempotent(tmp_path) -> None:
    from scripts.daily_paper_ingest import emit_parse_completed

    db = _db(tmp_path)
    repository = CatalogRepository(db)
    first = emit_parse_completed(repository, "arxiv:2601.00005", "data/parsed/x/x.md")
    second = emit_parse_completed(repository, "arxiv:2601.00005", "data/parsed/x/x.md")
    repository.close()
    assert first is not None
    assert second is None
    with sqlite3.connect(db) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM outbox WHERE event_type='ParseCompleted'").fetchone()[0]
    assert count == 1


def test_phase5_pool_advances_through_valid_transitions(tmp_path) -> None:
    import scripts.content_bridge as bridge

    db = _db(tmp_path)
    repository = CatalogRepository(db)
    repository._connection.execute(
        "INSERT INTO papers(canonical_id,status,title,publication_year,venue_type,created_at,updated_at) "
        "VALUES('arxiv:2601.00006','discovered','T',2026,'c','now','now')")
    repository._connection.commit()
    repository.close()

    bridge._advance_pool("arxiv:2601.00006", db_path=db)

    with sqlite3.connect(db) as connection:
        status = connection.execute(
            "SELECT status FROM paper_pool WHERE canonical_id='arxiv:2601.00006'"
        ).fetchone()[0]
    assert status == "staged"


def test_phase6_verifier_reports_missing_artifacts() -> None:
    from scripts.verify_end_to_end_pipeline import find_parsed_markdown

    assert find_parsed_markdown("arxiv:definitely-not-present-9999") is None


def test_p0_run_status_derived_from_counters() -> None:
    import scripts.content_bridge as bridge

    # Empty queue: nothing attempted -> ok (exit 0).
    assert bridge._run_status(0, 0, 0) == "ok"
    # Dry run never claims real work.
    assert bridge._run_status(0, 0, 2, dry_run=True) == "dry_run"
    # All succeeded -> ok.
    assert bridge._run_status(3, 0, 3) == "ok"
    # Mixed -> partial.
    assert bridge._run_status(1, 1, 2) == "partial"
    # Attempted but nothing succeeded -> failed.
    assert bridge._run_status(0, 1, 1) == "failed"


def test_bridge_dry_run_does_not_claim_or_modify_event(tmp_path) -> None:
    import scripts.content_bridge as bridge

    db = _db(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO outbox(event_id,event_type,event_version,producer_domain,target_domain,"
            "aggregate_id,idempotency_key,payload_json,occurred_at,available_at) "
            "VALUES('evt-dry','ParseCompleted',1,'intake','bridge','acl:1','dry-1',"
            "'{\"canonical_id\":\"acl:1\",\"markdown_path\":\"ignored.md\"}',"
            "'2000-01-01','2000-01-01')")
        before = connection.execute("SELECT * FROM outbox WHERE event_id='evt-dry'").fetchone()
    result = bridge.run_bridge_once(db, max_jobs=1, dry_run=True)
    with sqlite3.connect(db) as connection:
        after = connection.execute("SELECT * FROM outbox WHERE event_id='evt-dry'").fetchone()
    assert after == before
    assert result["status"] == "dry_run"
    assert result["scanned"] == 1
    assert result["processed"] == 0


def test_p0_main_exit_code_reflects_failures(tmp_path, monkeypatch, capsys) -> None:
    import sys

    import scripts.content_bridge as bridge

    db = _db(tmp_path)
    # One claimed event whose consumption always raises -> failed += 1.
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO outbox(event_id, event_type, event_version, producer_domain, "
            "target_domain, aggregate_id, idempotency_key, payload_json, occurred_at, available_at) "
            "VALUES('evt-1', 'ParseCompleted', 1, 'paper_intake', 'content_bridge', "
            "'arxiv:2601.00999', 'idem-p0', "
            "json_object('canonical_id','arxiv:2601.00999','markdown_path','data/parsed/none.md'), "
            "'now','2000-01-01T00:00:00')")

    def blow_up(self, event, *, dry_run, db_path):
        raise RuntimeError("simulated s5 failure")

    monkeypatch.setattr(bridge, "_consume_event", blow_up)
    monkeypatch.setattr(sys, "argv", [
        "content_bridge.py", "--db", str(db), "--max-jobs", "1"])
    exit_code = bridge.main()
    captured = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert captured["failed"] == 1
    assert captured["status"] == "failed"
    assert exit_code != 0  # the bug this pins: s5 must not look ok on failure


def test_p0_main_exit_code_zero_on_empty_queue(tmp_path, monkeypatch, capsys) -> None:
    import sys

    import scripts.content_bridge as bridge

    db = _db(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "content_bridge.py", "--db", str(db), "--max-jobs", "1"])
    exit_code = bridge.main()
    captured = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert captured == {"status": "ok", "processed": 0, "failed": 0, "scanned": 0}
    assert exit_code == 0
