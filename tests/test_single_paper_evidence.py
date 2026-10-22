from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.single_paper_evidence import EvidenceContractError, EvidenceRecorder


def _write_evidence(path: Path, assertions: dict[str, object]) -> Path:
    path.write_text(
        json.dumps({"assertions": assertions}, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return path


def _record(
    recorder: EvidenceRecorder,
    test_id: str,
    *,
    assertions: dict[str, object] | None = None,
    command: list[str] | None = None,
) -> Path:
    expected = assertions or {"passed": True}
    evidence = _write_evidence(recorder.root / f"{test_id.lower()}.json", expected)
    recorder.record(
        test_id=test_id,
        command=command or ["python", "-m", "pytest", "tests"],
        exit_code=0,
        assertions=expected,
        evidence_path=evidence,
    )
    return evidence


def test_audit_rejects_duplicate_test_ids(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    _record(recorder, "TC-01")

    with pytest.raises(EvidenceContractError, match="duplicate test_id: TC-01"):
        _record(recorder, "TC-01")


def test_audit_rejects_missing_evidence_file(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    evidence = _record(recorder, "TC-01")
    evidence.unlink()

    result = recorder.audit(["TC-01"])

    assert result.passed is False
    assert result.errors == ["TC-01: evidence file missing"]


def test_audit_rejects_modified_evidence_hash(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    evidence = _record(recorder, "TC-01")
    evidence.write_text('{"assertions":{"passed":false}}', encoding="utf-8")

    result = recorder.audit(["TC-01"])

    assert result.passed is False
    assert result.errors == ["TC-01: sha256 mismatch"]


def test_audit_rejects_assertion_evidence_contradiction(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    evidence = _write_evidence(tmp_path / "tc-01.json", {"count": 1})
    recorder.record(
        test_id="TC-01",
        command=["python", "check.py"],
        exit_code=0,
        assertions={"count": 2},
        evidence_path=evidence,
    )

    result = recorder.audit(["TC-01"])

    assert result.passed is False
    assert result.errors == ["TC-01: assertions contradict evidence"]


@pytest.mark.parametrize(
    "leak",
    [
        "Authorization: Basic abc123",
        "Bearer abc123",
        "token: abc123",
        "password=abc123",
        "sk-0123456789abcdef",
        "ntn_0123456789abcdef",
        "ghp_0123456789abcdef",
        "github_pat_0123456789abcdef",
    ],
)
def test_audit_rejects_secret_patterns(tmp_path: Path, leak: str) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    evidence = tmp_path / "tc-01.json"
    evidence.write_text(
        json.dumps({"assertions": {"passed": True}, "diagnostic": leak}),
        encoding="utf-8",
    )
    recorder.record(
        test_id="TC-01",
        command=["python", "check.py"],
        exit_code=0,
        assertions={"passed": True},
        evidence_path=evidence,
    )

    result = recorder.audit(["TC-01"])

    assert result.passed is False
    assert result.secret_hits == ["TC-01"]


def test_record_redacts_secret_command_values(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    _record(
        recorder,
        "TC-01",
        command=["python", "release.py", "--token", "ghp_supersecret", "--slug", "paper-x"],
    )

    manifest = json.loads(recorder.manifest_path.read_text(encoding="utf-8"))

    assert manifest["records"][0]["command"] == [
        "python",
        "release.py",
        "--token",
        "[REDACTED]",
        "--slug",
        "paper-x",
    ]
    assert "ghp_supersecret" not in recorder.manifest_path.read_text(encoding="utf-8")


def test_two_phase_audit_adds_tc14_without_self_referential_hash(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "release-1")
    required_phase_one = [f"TC-{index:02d}" for index in range(1, 14)]
    for test_id in required_phase_one:
        _record(recorder, test_id)

    audit_path = tmp_path / "tc-14-evidence-audit.json"
    phase_one = recorder.write_audit(required_phase_one, audit_path)

    assert phase_one.passed is True
    recorder.record(
        test_id="TC-14",
        command=["python", "scripts/single_paper_evidence.py", "audit"],
        exit_code=0,
        assertions={"passed": True},
        evidence_path=audit_path,
    )
    final = recorder.audit(required_phase_one + ["TC-14"])

    assert final.passed is True
    assert final.valid_ids == required_phase_one + ["TC-14"]


def test_audit_requires_every_id_exactly_once(tmp_path: Path) -> None:
    recorder = EvidenceRecorder(tmp_path, "run-1")
    _record(recorder, "TC-01")

    result = recorder.audit(["TC-01", "TC-02"])

    assert result.passed is False
    assert result.errors == ["TC-02: manifest record missing"]
