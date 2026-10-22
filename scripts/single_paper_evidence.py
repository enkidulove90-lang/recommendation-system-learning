from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


class EvidenceContractError(ValueError):
    """Raised when evidence cannot be recorded without breaking the contract."""


@dataclass(frozen=True)
class EvidenceAudit:
    passed: bool
    errors: list[str]
    secret_hits: list[str]
    valid_ids: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "assertions": {"passed": self.passed},
            "errors": self.errors,
            "secret_hits": self.secret_hits,
            "valid_ids": self.valid_ids,
        }


_SECRET_PATTERN = re.compile(
    r"(?i)(?:\b(?:authorization|token|password)\b\s*[:=]\s*\S+"
    r"|\bbearer\s+\S+"
    r"|\bsk[-_][A-Za-z0-9_-]{8,}"
    r"|\b(?:ntn|ghp|gho)_[A-Za-z0-9_-]{8,}"
    r"|\bgithub_pat_[A-Za-z0-9_-]{8,})"
)
_SECRET_FLAGS = {
    "--api-key",
    "--authorization",
    "--notion-token",
    "--password",
    "--secret",
    "--token",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _redact_command(command: Sequence[str]) -> list[str]:
    redacted: list[str] = []
    hide_next = False
    for raw_argument in command:
        argument = str(raw_argument)
        if hide_next:
            redacted.append("[REDACTED]")
            hide_next = False
            continue
        lowered = argument.lower()
        if lowered in _SECRET_FLAGS:
            redacted.append(argument)
            hide_next = True
            continue
        matching_flag = next(
            (flag for flag in _SECRET_FLAGS if lowered.startswith(f"{flag}=")),
            None,
        )
        if matching_flag:
            redacted.append(f"{argument.split('=', 1)[0]}=[REDACTED]")
            continue
        if _SECRET_PATTERN.search(argument):
            redacted.append("[REDACTED]")
            continue
        redacted.append(argument)
    return redacted


class EvidenceRecorder:
    def __init__(self, root: Path, run_id: str):
        self.root = Path(root)
        self.run_id = run_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.root / "manifest.json"
        if self.manifest_path.exists():
            self._manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if self._manifest.get("run_id") != run_id:
                raise EvidenceContractError("manifest run_id mismatch")
        else:
            self._manifest = {"records": [], "run_id": run_id}
            self._save_manifest()

    def _save_manifest(self) -> None:
        self.manifest_path.write_text(_stable_json(self._manifest), encoding="utf-8")

    def record(
        self,
        test_id: str,
        command: list[str],
        exit_code: int,
        assertions: dict[str, Any],
        evidence_path: Path,
    ) -> None:
        if any(item["test_id"] == test_id for item in self._manifest["records"]):
            raise EvidenceContractError(f"duplicate test_id: {test_id}")

        path = Path(evidence_path).resolve()
        root = self.root.resolve()
        if root not in path.parents:
            raise EvidenceContractError("evidence path must be inside evidence root")
        if not path.is_file():
            raise EvidenceContractError("evidence file does not exist")

        self._manifest["records"].append(
            {
                "assertions": assertions,
                "command": _redact_command(command),
                "exit_code": int(exit_code),
                "path": path.relative_to(root).as_posix(),
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "sha256": _sha256(path),
                "test_id": test_id,
            }
        )
        self._save_manifest()

    def audit(self, required_ids: Sequence[str]) -> EvidenceAudit:
        errors: list[str] = []
        secret_hits: list[str] = []
        valid_ids: list[str] = []
        required = list(required_ids)

        if len(required) != len(set(required)):
            errors.append("required_ids contains duplicates")

        records = {item["test_id"]: item for item in self._manifest["records"]}
        for test_id in required:
            record = records.get(test_id)
            if record is None:
                errors.append(f"{test_id}: manifest record missing")
                continue

            path = self.root / record["path"]
            if not path.is_file():
                errors.append(f"{test_id}: evidence file missing")
                continue
            if _sha256(path) != record["sha256"]:
                errors.append(f"{test_id}: sha256 mismatch")
                continue
            if record["exit_code"] != 0:
                errors.append(f"{test_id}: command exit_code is not zero")
                continue

            raw = path.read_text(encoding="utf-8", errors="replace")
            if _SECRET_PATTERN.search(raw):
                secret_hits.append(test_id)
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                errors.append(f"{test_id}: evidence is not valid JSON")
                continue
            if payload.get("assertions") != record["assertions"]:
                errors.append(f"{test_id}: assertions contradict evidence")
                continue
            valid_ids.append(test_id)

        passed = not errors and not secret_hits and valid_ids == required
        return EvidenceAudit(
            passed=passed,
            errors=errors,
            secret_hits=secret_hits,
            valid_ids=valid_ids,
        )

    def write_audit(self, required_ids: Sequence[str], path: Path) -> EvidenceAudit:
        result = self.audit(required_ids)
        output = Path(path)
        if output.resolve().parent != self.root.resolve():
            raise EvidenceContractError("audit path must be directly inside evidence root")
        output.write_text(_stable_json(result.as_dict()), encoding="utf-8")
        return result
