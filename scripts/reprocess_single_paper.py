from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol, Sequence

from paper_intake.models import StepName
from scripts.single_paper_evidence import EvidenceRecorder


class ReleaseSafetyError(RuntimeError):
    """Raised before mutation when the single-paper release contract is not met."""


@dataclass(frozen=True)
class NotionTarget:
    page_id: str
    slug: str
    content: bytes


@dataclass(frozen=True)
class ReleasePlan:
    job_id: str
    canonical_id: str
    slug: str
    notion_page_id: str
    mineru_markdown_path: str
    mineru_sha256: str
    site_source_path: str
    site_source_sha256: str
    notion_backup_path: str
    notion_backup_sha256: str
    site_backup_path: str
    allowed_changed_paths: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ReleasePlan":
        return cls(**payload)


class NotionReleaseGateway(Protocol):
    def find_targets(self, *, canonical_id: str, slug: str) -> list[NotionTarget]: ...

    def restore(self, page_id: str, content: bytes) -> None: ...


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SinglePaperReprocessor:
    """Coordinates one exact paper while preserving all upstream checkpoints."""

    def __init__(self, *, repository, pipeline, notion: NotionReleaseGateway, site_posts_root: Path):
        self.repository = repository
        self.pipeline = pipeline
        self.notion = notion
        self.site_posts_root = Path(site_posts_root)

    def prepare(
        self,
        *,
        job_id: str,
        canonical_id: str,
        expected_slug: str,
        reuse_mineru: bool,
        evidence_dir: Path,
    ) -> ReleasePlan:
        job = self.repository.get_job(job_id)
        if job is None:
            raise ReleaseSafetyError("job identity mismatch: no exact job exists")
        if job.canonical_id != canonical_id:
            raise ReleaseSafetyError("canonical identity mismatch")
        canonical_slug = f"paper-{canonical_id}"
        if expected_slug != canonical_slug:
            raise ReleaseSafetyError("slug identity mismatch")
        if not reuse_mineru:
            raise ReleaseSafetyError("single-paper release requires --reuse-mineru")

        parse_step = self.repository.get_step(job_id, StepName.MINERU_PARSE)
        markdown_value = (parse_step.output if parse_step else {}).get("markdown_path")
        mineru_path = Path(markdown_value).resolve() if markdown_value else None
        if mineru_path is None or not mineru_path.is_file():
            raise ReleaseSafetyError("MinerU artifact is missing")

        targets = self.notion.find_targets(canonical_id=canonical_id, slug=expected_slug)
        if len(targets) != 1:
            raise ReleaseSafetyError("expected exactly one Notion page")
        target = targets[0]
        if target.page_id != job.notion_page_id or target.slug != expected_slug:
            raise ReleaseSafetyError("Notion page identity mismatch")

        source_matches = [path.resolve() for path in self.site_posts_root.rglob(f"{expected_slug}.md")]
        if len(source_matches) != 1:
            raise ReleaseSafetyError("expected exactly one site post")
        source_path = source_matches[0]

        evidence_root = Path(evidence_dir).resolve()
        backup_root = evidence_root / "pre-write"
        backup_root.mkdir(parents=True, exist_ok=True)
        notion_backup = backup_root / "notion-page.md"
        site_backup = backup_root / source_path.name
        notion_backup.write_bytes(target.content)
        site_backup.write_bytes(source_path.read_bytes())

        plan = ReleasePlan(
            job_id=job_id,
            canonical_id=canonical_id,
            slug=expected_slug,
            notion_page_id=target.page_id,
            mineru_markdown_path=str(mineru_path),
            mineru_sha256=_sha256(mineru_path),
            site_source_path=str(source_path),
            site_source_sha256=_sha256(source_path),
            notion_backup_path=str(notion_backup),
            notion_backup_sha256=_sha256(notion_backup),
            site_backup_path=str(site_backup),
            allowed_changed_paths=[str(source_path)],
        )
        (evidence_root / "release-plan.json").write_text(
            json.dumps(plan.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return plan

    def publish(
        self,
        plan: ReleasePlan,
        manifest_path: Path,
        required_evidence_ids: Sequence[str],
    ):
        source_path = Path(plan.site_source_path)
        mineru_path = Path(plan.mineru_markdown_path)
        if not source_path.is_file() or _sha256(source_path) != plan.site_source_sha256:
            raise ReleaseSafetyError("pre-write source hash changed")
        if not mineru_path.is_file() or _sha256(mineru_path) != plan.mineru_sha256:
            raise ReleaseSafetyError("pre-write MinerU hash changed")

        current_job = self.repository.get_job(plan.job_id)
        if current_job is None or current_job.canonical_id != plan.canonical_id:
            raise ReleaseSafetyError("job identity changed after dry-run")
        if current_job.notion_page_id != plan.notion_page_id:
            raise ReleaseSafetyError("Notion page identity changed after dry-run")

        manifest = Path(manifest_path)
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            recorder = EvidenceRecorder(manifest.parent, str(payload["run_id"]))
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            raise ReleaseSafetyError("evidence manifest is invalid") from exc
        audit = recorder.audit(required_evidence_ids)
        if not audit.passed:
            raise ReleaseSafetyError("evidence gate failed: " + "; ".join(audit.errors + audit.secret_hits))

        self.repository.reset_steps(
            plan.job_id,
            restart_from=StepName.DEEPSEEK_GENERATE,
            ordered_steps=tuple(self.pipeline.PROCESSING_STEPS),
        )
        return self.pipeline.run(plan.job_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely reprocess one exact paper")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--expected-slug", required=True)
    parser.add_argument("--reuse-mineru", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    return parser


def main() -> int:
    build_parser().parse_args()
    raise SystemExit(
        "Runtime adapters must be constructed by the intake bootstrap; no mutation was attempted."
    )


if __name__ == "__main__":
    raise SystemExit(main())
