from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from paper_intake.models import JobStatus, StepName
from paper_intake.repository import JobRepository
from scripts.reprocess_single_paper import (
    LiveNotionReleaseGateway,
    NotionTarget,
    ReleaseSafetyError,
    SinglePaperReprocessor,
    assemble_site_article,
    build_parser,
)
from scripts.single_paper_evidence import EvidenceRecorder
from scripts.verify_single_paper_release import restore_release, verify_allowed_changes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeNotion:
    def __init__(self, targets: list[NotionTarget]):
        self.targets = targets
        self.restore_calls: list[tuple[str, bytes]] = []

    def find_targets(self, *, canonical_id: str, slug: str) -> list[NotionTarget]:
        return list(self.targets)

    def restore(self, page_id: str, content: bytes) -> None:
        self.restore_calls.append((page_id, content))


class FakePipeline:
    PROCESSING_STEPS = (
        StepName.VALIDATE_INPUT,
        StepName.RESOLVE_METADATA,
        StepName.DOWNLOAD_PDF,
        StepName.MINERU_PARSE,
        StepName.DEEPSEEK_GENERATE,
        StepName.CLASSIFY,
        StepName.QUALITY_CHECK,
        StepName.WRITE_NOTION_PUBLISHED,
    )

    def __init__(self, repository: JobRepository, generated_path: Path):
        self.repository = repository
        self.generated_path = generated_path
        self.run_calls = 0
        self.mineru_calls = 0

    def run(self, job_id: str):
        self.run_calls += 1
        assert self.repository.get_step(job_id, StepName.MINERU_PARSE) is not None
        self.repository.start_step(job_id, StepName.QUALITY_CHECK)
        self.repository.complete_step(
            job_id,
            StepName.QUALITY_CHECK,
            output={"article_path": str(self.generated_path), "publishable": True},
        )
        return self.repository.update_job(job_id, status=JobStatus.PUBLISHING)


@pytest.fixture
def release_fixture(tmp_path: Path):
    repository = JobRepository(tmp_path / "jobs.sqlite3")
    job = repository.create_job(
        source_type="url",
        source_url="https://arxiv.org/abs/2610.05432",
        job_id="job-opticalrec",
    )
    repository.update_job(
        job.job_id,
        canonical_id="2610.05432",
        title="OpticalRec",
        notion_page_id="notion-page-1",
        status=JobStatus.PUBLISHED,
    )
    mineru_path = tmp_path / "workflow" / job.job_id / "paper.md"
    mineru_path.parent.mkdir(parents=True)
    mineru_path.write_bytes(b"# Parsed OpticalRec\n")
    repository.start_step(job.job_id, StepName.MINERU_PARSE)
    repository.complete_step(
        job.job_id,
        StepName.MINERU_PARSE,
        output={"markdown_path": str(mineru_path)},
    )
    site_root = tmp_path / "site" / "source" / "_posts"
    site_root.mkdir(parents=True)
    source_path = site_root / "paper-2610.05432.md"
    source_path.write_bytes(
        b'---\ntitle: OpticalRec\ndate: "2026-10-22"\n---\n'
        b'old body\n![method](/images/existing-method.png)\n'
    )
    notion = FakeNotion(
        [NotionTarget("notion-page-1", "paper-2610.05432", b"old notion body\n")]
    )
    generated_path = tmp_path / "workflow" / job.job_id / "generated.md"
    generated_path.write_bytes(
        b"---\nslug: paper-2610.05432\n---\nnew generated body\n"
        b"![method](/images/papers/2610.05432/new-method.jpg)\n"
    )
    pipeline = FakePipeline(repository, generated_path)
    coordinator = SinglePaperReprocessor(
        repository=repository,
        pipeline=pipeline,
        notion=notion,
        site_posts_root=site_root,
    )
    yield coordinator, repository, pipeline, notion, source_path, mineru_path
    repository.close()


def test_dry_run_selects_one_target_and_records_complete_hashes(
    release_fixture, tmp_path: Path
) -> None:
    coordinator, _repository, pipeline, _notion, source_path, mineru_path = release_fixture

    plan = coordinator.prepare(
        job_id="job-opticalrec",
        canonical_id="2610.05432",
        expected_slug="paper-2610.05432",
        reuse_mineru=True,
        evidence_dir=tmp_path / "evidence",
    )

    assert plan.job_id == "job-opticalrec"
    assert plan.notion_page_id == "notion-page-1"
    assert Path(plan.mineru_markdown_path) == mineru_path.resolve()
    assert Path(plan.site_source_path) == source_path.resolve()
    assert plan.mineru_sha256 == _sha256(mineru_path.read_bytes())
    assert plan.site_source_sha256 == _sha256(source_path.read_bytes())
    assert plan.notion_backup_sha256 == _sha256(b"old notion body\n")
    assert Path(plan.notion_backup_path).read_bytes() == b"old notion body\n"
    assert Path(plan.site_backup_path).read_bytes() == source_path.read_bytes()
    assert plan.allowed_changed_paths == [str(source_path.resolve())]
    assert pipeline.run_calls == 0
    assert pipeline.mineru_calls == 0


@pytest.mark.parametrize(
    ("job_id", "canonical_id", "expected_slug", "message"),
    [
        ("wrong-job", "2610.05432", "paper-2610.05432", "job identity mismatch"),
        ("job-opticalrec", "9999.00001", "paper-2610.05432", "canonical identity mismatch"),
        ("job-opticalrec", "2610.05432", "wrong-slug", "slug identity mismatch"),
    ],
)
def test_identity_mismatch_aborts_before_any_write(
    release_fixture,
    tmp_path: Path,
    job_id: str,
    canonical_id: str,
    expected_slug: str,
    message: str,
) -> None:
    coordinator, _repository, pipeline, notion, source_path, _mineru_path = release_fixture
    before = source_path.read_bytes()

    with pytest.raises(ReleaseSafetyError, match=message):
        coordinator.prepare(
            job_id=job_id,
            canonical_id=canonical_id,
            expected_slug=expected_slug,
            reuse_mineru=True,
            evidence_dir=tmp_path / "evidence",
        )

    assert pipeline.run_calls == 0
    assert notion.restore_calls == []
    assert source_path.read_bytes() == before


def test_missing_mineru_artifact_is_rejected(release_fixture, tmp_path: Path) -> None:
    coordinator, _repository, pipeline, _notion, _source_path, mineru_path = release_fixture
    mineru_path.unlink()

    with pytest.raises(ReleaseSafetyError, match="MinerU artifact is missing"):
        coordinator.prepare(
            job_id="job-opticalrec",
            canonical_id="2610.05432",
            expected_slug="paper-2610.05432",
            reuse_mineru=True,
            evidence_dir=tmp_path / "evidence",
        )

    assert pipeline.run_calls == 0


def test_duplicate_notion_or_site_target_is_rejected(release_fixture, tmp_path: Path) -> None:
    coordinator, _repository, pipeline, notion, source_path, _mineru_path = release_fixture
    notion.targets.append(NotionTarget("page-2", "paper-2610.05432", b"duplicate"))
    duplicate = source_path.parent / "nested" / source_path.name
    duplicate.parent.mkdir()
    duplicate.write_bytes(source_path.read_bytes())

    with pytest.raises(ReleaseSafetyError, match="exactly one Notion page"):
        coordinator.prepare(
            job_id="job-opticalrec",
            canonical_id="2610.05432",
            expected_slug="paper-2610.05432",
            reuse_mineru=True,
            evidence_dir=tmp_path / "evidence",
        )

    assert pipeline.run_calls == 0


def test_publish_requires_audited_evidence_and_reuses_mineru(
    release_fixture, tmp_path: Path
) -> None:
    coordinator, repository, pipeline, _notion, _source_path, _mineru_path = release_fixture
    evidence_root = tmp_path / "evidence"
    plan = coordinator.prepare(
        job_id="job-opticalrec",
        canonical_id="2610.05432",
        expected_slug="paper-2610.05432",
        reuse_mineru=True,
        evidence_dir=evidence_root,
    )
    recorder = EvidenceRecorder(evidence_root, "release-test")
    assertions = {"passed": True}
    evidence = evidence_root / "tc-11.json"
    evidence.write_text(json.dumps({"assertions": assertions}), encoding="utf-8")
    recorder.record("TC-11", ["pytest"], 0, assertions, evidence)

    result = coordinator.publish(
        plan,
        manifest_path=recorder.manifest_path,
        required_evidence_ids=["TC-11"],
    )

    assert result.status == JobStatus.PUBLISHING
    assert pipeline.run_calls == 1
    assert pipeline.mineru_calls == 0
    published = _source_path.read_text(encoding="utf-8")
    assert 'date: "2026-10-22"' in published
    assert "![method](/images/existing-method.png)" in published
    assert "/images/papers/2610.05432/new-method.jpg" not in published
    assert repository.get_step("job-opticalrec", StepName.MINERU_PARSE) is not None
    assert repository.get_step("job-opticalrec", StepName.DEEPSEEK_GENERATE) is None


def test_publish_rejects_tampered_prewrite_hash(release_fixture, tmp_path: Path) -> None:
    coordinator, _repository, pipeline, _notion, source_path, _mineru_path = release_fixture
    evidence_root = tmp_path / "evidence"
    plan = coordinator.prepare(
        job_id="job-opticalrec",
        canonical_id="2610.05432",
        expected_slug="paper-2610.05432",
        reuse_mineru=True,
        evidence_dir=evidence_root,
    )
    source_path.write_bytes(b"tampered")
    (evidence_root / "manifest.json").write_text(
        json.dumps({"run_id": "x", "records": []}), encoding="utf-8"
    )

    with pytest.raises(ReleaseSafetyError, match="pre-write source hash changed"):
        coordinator.publish(plan, evidence_root / "manifest.json", [])

    assert pipeline.run_calls == 0


def test_scope_verifier_and_rollback_restore_byte_identical_content(
    release_fixture, tmp_path: Path
) -> None:
    coordinator, _repository, _pipeline, notion, source_path, _mineru_path = release_fixture
    plan = coordinator.prepare(
        job_id="job-opticalrec",
        canonical_id="2610.05432",
        expected_slug="paper-2610.05432",
        reuse_mineru=True,
        evidence_dir=tmp_path / "evidence",
    )
    before = {str(source_path.resolve()): plan.site_source_sha256, "unrelated.txt": _sha256(b"same")}
    allowed_after = {str(source_path.resolve()): _sha256(b"new"), "unrelated.txt": _sha256(b"same")}
    assert verify_allowed_changes(before, allowed_after, plan.allowed_changed_paths) == []
    unexpected_after = dict(allowed_after, **{"unrelated.txt": _sha256(b"changed")})
    assert verify_allowed_changes(before, unexpected_after, plan.allowed_changed_paths) == [
        "unrelated.txt"
    ]

    source_path.write_bytes(b"new site body")
    restore_release(plan, notion=notion)

    assert source_path.read_bytes() == Path(plan.site_backup_path).read_bytes()
    assert _sha256(source_path.read_bytes()) == plan.site_source_sha256
    assert notion.restore_calls == [("notion-page-1", b"old notion body\n")]
    assert _sha256(notion.restore_calls[0][1]) == plan.notion_backup_sha256


class FakeRawNotion:
    def __init__(self):
        self.database_id = "database"
        self._property_names = {"arxiv_id", "slug", "title"}
        self.upserts = []

    def _data_source(self):
        return "source"

    def _request(self, method, path, **kwargs):
        assert method == "POST"
        assert path == "/data_sources/source/query"
        return {
            "results": [
                {
                    "id": "page-1",
                    "properties": {
                        "slug": {"rich_text": [{"plain_text": "paper-2610.05432"}]},
                        "title": {"title": [{"plain_text": "OpticalRec"}]},
                    },
                }
            ]
        }

    def _snapshot_markdown(self, page_id):
        assert page_id == "page-1"
        return "notion body"

    def upsert_published(self, draft):
        self.upserts.append(draft)


def test_live_notion_gateway_queries_exact_identity_and_can_restore() -> None:
    raw = FakeRawNotion()
    gateway = LiveNotionReleaseGateway(raw)

    targets = gateway.find_targets(
        canonical_id="2610.05432", slug="paper-2610.05432"
    )
    gateway.restore("page-1", b"old notion body")

    assert targets == [
        NotionTarget("page-1", "paper-2610.05432", b"notion body")
    ]
    assert len(raw.upserts) == 1
    assert raw.upserts[0].arxiv_id == "2610.05432"
    assert raw.upserts[0].slug == "paper-2610.05432"
    assert raw.upserts[0].markdown == "old notion body"


def test_cli_exposes_exact_dry_run_contract(tmp_path: Path) -> None:
    arguments = build_parser().parse_args(
        [
            "--job-id",
            "job-1",
            "--canonical-id",
            "2610.05432",
            "--expected-slug",
            "paper-2610.05432",
            "--reuse-mineru",
            "--dry-run",
            "--evidence-dir",
            str(tmp_path),
        ]
    )

    assert arguments.dry_run is True
    assert arguments.publish is False
    assert arguments.reuse_mineru is True


def test_cli_script_can_be_executed_directly() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/reprocess_single_paper.py", "--help"],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "--reuse-mineru" in completed.stdout


def test_site_assembly_rejects_a_new_image_without_existing_alt_mapping() -> None:
    existing = b"---\ndate: 2026-10-22\n---\nold\n"
    generated = (
        b"---\nslug: paper-2610.05432\n---\n"
        b"![unknown](/images/papers/2610.05432/new.jpg)\n"
    )

    with pytest.raises(ReleaseSafetyError, match="unmapped generated site image"):
        assemble_site_article(existing, generated)


def test_site_assembly_accepts_windows_newlines() -> None:
    existing = (
        b'---\r\ntitle: OpticalRec\r\ndate: "2026-10-22"\r\n---\r\n'
        b'![method](/images/existing-method.png)\r\n'
    )
    generated = (
        b'---\r\nslug: paper-2610.05432\r\n---\r\n'
        b'![method](/images/papers/2610.05432/new-method.jpg)\r\n'
    )

    assembled = assemble_site_article(existing, generated).decode("utf-8")

    assert 'date: "2026-10-22"' in assembled
    assert "/images/existing-method.png" in assembled
    assert "/images/papers/2610.05432/" not in assembled
