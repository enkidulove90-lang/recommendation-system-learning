from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paper_intake.models import JobStatus, StepName
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


def _notion_property_text(properties: dict, name: str) -> str:
    value = properties.get(name) or {}
    fragments = value.get("title") or value.get("rich_text") or []
    return "".join(
        str(fragment.get("plain_text") or (fragment.get("text") or {}).get("content") or "")
        for fragment in fragments
    ).strip()


class LiveNotionReleaseGateway:
    """Narrow adapter exposing only exact read/restore operations for release safety."""

    def __init__(self, gateway):
        self.gateway = gateway
        self._identities: dict[str, tuple[str, str, str]] = {}

    def find_targets(self, *, canonical_id: str, slug: str) -> list[NotionTarget]:
        source_id = self.gateway._data_source()
        property_names = self.gateway._property_names or set()
        if "arxiv_id" in property_names:
            property_name, property_value = "arxiv_id", canonical_id
        elif "slug" in property_names:
            property_name, property_value = "slug", slug
        else:
            raise ReleaseSafetyError("Notion identity properties are missing")
        response = self.gateway._request(
            "POST",
            f"/data_sources/{source_id}/query",
            json={
                "filter": {
                    "property": property_name,
                    "rich_text": {"equals": property_value},
                },
                "page_size": 3,
            },
        )
        targets: list[NotionTarget] = []
        for page in response.get("results") or []:
            properties = page.get("properties") or {}
            actual_slug = _notion_property_text(properties, "slug") or slug
            title = _notion_property_text(properties, "title") or canonical_id
            page_id = str(page.get("id") or "")
            content = self.gateway._snapshot_markdown(page_id).encode("utf-8")
            self._identities[page_id] = (canonical_id, actual_slug, title)
            targets.append(NotionTarget(page_id, actual_slug, content))
        return targets

    def restore(self, page_id: str, content: bytes) -> None:
        try:
            canonical_id, slug, title = self._identities[page_id]
        except KeyError as exc:
            raise ReleaseSafetyError("Notion restore identity was not frozen") from exc
        from paper_intake.adapters import NotionDraft

        self.gateway.upsert_published(
            NotionDraft(
                arxiv_id=canonical_id,
                title=title,
                slug=slug,
                summary="",
                markdown=content.decode("utf-8"),
                figure_paths=(),
                categories=(),
                tags=(),
                year="",
                venue_type="",
                venue_name="",
            )
        )


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
        result = self.pipeline.run(plan.job_id)
        if result.status != JobStatus.PUBLISHING:
            raise ReleaseSafetyError(
                f"single-paper pipeline did not reach publishing: {result.status.value}"
            )
        quality = self.repository.get_step(plan.job_id, StepName.QUALITY_CHECK)
        article_value = (quality.output if quality else {}).get("article_path")
        article_path = Path(article_value).resolve() if article_value else None
        if article_path is None or not article_path.is_file():
            raise ReleaseSafetyError("generated target article is missing")
        generated = article_path.read_bytes()
        slug_line = f"slug: {plan.slug}".encode()
        quoted_slug_line = f'slug: "{plan.slug}"'.encode()
        if slug_line not in generated and quoted_slug_line not in generated:
            raise ReleaseSafetyError("generated article slug identity mismatch")
        try:
            source_path.write_bytes(generated)
        except Exception:
            source_path.write_bytes(Path(plan.site_backup_path).read_bytes())
            self.notion.restore(
                plan.notion_page_id,
                Path(plan.notion_backup_path).read_bytes(),
            )
            raise
        return result


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
    parser.add_argument("--manifest-path", type=Path)
    parser.add_argument("--require-evidence", default="TC-01,TC-02,TC-03,TC-04,TC-05,TC-06,TC-07,TC-08,TC-09,TC-10,TC-11,TC-12,TC-13,TC-14")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--site-posts-root", type=Path)
    return parser


def build_runtime(*, project_root: Path, site_posts_root: Path | None):
    from dotenv import load_dotenv

    from paper_intake.adapters import DeepSeekArticleAdapter, MinerUAdapter, NotionGateway
    from paper_intake.inputs import PaperInputStore
    from paper_intake.metadata import ArxivMetadataResolver
    from paper_intake.pipeline import PaperPipeline
    from paper_intake.repository import JobRepository

    root = Path(project_root).resolve()
    load_dotenv(root / ".env", override=False)
    required = {
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN", ""),
        "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID", ""),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ReleaseSafetyError("missing release configuration: " + ", ".join(missing))
    runtime_root = root / "data" / "paper_intake" / "remote"
    workflow_root = root / "data" / "workflow_state" / "paper_intake" / "remote"
    repository = JobRepository(runtime_root / "jobs.sqlite3")
    notion_gateway = NotionGateway(required["NOTION_TOKEN"], required["NOTION_DATABASE_ID"])
    pipeline = PaperPipeline(
        repository=repository,
        input_store=PaperInputStore(runtime_root / "inbox"),
        mineru=MinerUAdapter(),
        deepseek=DeepSeekArticleAdapter(
            api_key=required["DEEPSEEK_API_KEY"],
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        ),
        notion=notion_gateway,
        workflow_root=workflow_root,
        metadata_resolver=ArxivMetadataResolver(),
    )
    posts_root = site_posts_root or root / ".worktrees" / "site-ui-fixes" / "source" / "_posts"
    return (
        SinglePaperReprocessor(
            repository=repository,
            pipeline=pipeline,
            notion=LiveNotionReleaseGateway(notion_gateway),
            site_posts_root=posts_root,
        ),
        repository,
    )


def main() -> int:
    arguments = build_parser().parse_args()
    coordinator, repository = build_runtime(
        project_root=arguments.project_root,
        site_posts_root=arguments.site_posts_root,
    )
    try:
        plan = coordinator.prepare(
            job_id=arguments.job_id,
            canonical_id=arguments.canonical_id,
            expected_slug=arguments.expected_slug,
            reuse_mineru=arguments.reuse_mineru,
            evidence_dir=arguments.evidence_dir,
        )
        if arguments.dry_run:
            print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if arguments.manifest_path is None:
            raise ReleaseSafetyError("--manifest-path is required with --publish")
        result = coordinator.publish(
            plan,
            manifest_path=arguments.manifest_path,
            required_evidence_ids=[
                item.strip() for item in arguments.require_evidence.split(",") if item.strip()
            ],
        )
        print(
            json.dumps(
                {
                    "canonical_id": result.canonical_id,
                    "job_id": result.job_id,
                    "notion_page_suffix": result.notion_page_id[-6:],
                    "slug": plan.slug,
                    "status": result.status.value,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    finally:
        repository.close()


if __name__ == "__main__":
    raise SystemExit(main())
