from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class StepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    INTERRUPTED = "interrupted"


class StepName(StrEnum):
    VALIDATE_INPUT = "validate_input"
    RESOLVE_METADATA = "resolve_metadata"
    DOWNLOAD_PDF = "download_pdf"
    MINERU_PARSE = "mineru_parse"
    DEEPSEEK_GENERATE = "deepseek_generate"
    CLASSIFY = "classify"
    QUALITY_CHECK = "quality_check"
    WRITE_NOTION_PUBLISHED = "write_notion_published"
    WRITE_NOTION_DRAFT = "write_notion_published"  # compatibility alias
    APPROVE = "approve"
    TRIGGER_PAGES = "trigger_pages"
    VERIFY_PUBLICATION = "verify_publication"


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: str
    source_type: str
    source_url: str = ""
    upload_path: str = ""
    source_sha256: str = ""
    canonical_id: str = ""
    title: str = ""
    status: JobStatus = JobStatus.RECEIVED
    current_step: str = ""
    notion_page_id: str = ""
    notion_url: str = ""
    github_run_id: str = ""
    published_url: str = ""
    error_code: str = ""
    error_message: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True, slots=True)
class StepRecord:
    job_id: str
    step_name: StepName
    status: StepStatus
    attempts: int = 0
    input_hash: str = ""
    output: dict[str, Any] = field(default_factory=dict)
    error_code: str = ""
    error_message: str = ""
    started_at: str = ""
    completed_at: str = ""


@dataclass(frozen=True, slots=True)
class EventRecord:
    event_id: int
    job_id: str
    event_type: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

