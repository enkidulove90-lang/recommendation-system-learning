"""Decoupled automation modules for the redbook paper-publication workflow."""

from .sources import PaperRecord, SourceRunner, deduplicate_records
from .scoring import QualityScorerV2
from .scheduling import PublishScheduler
from .feedback import FeedbackStore

__all__ = [
    "FeedbackStore",
    "PaperRecord",
    "PublishScheduler",
    "QualityScorerV2",
    "SourceRunner",
    "deduplicate_records",
]
