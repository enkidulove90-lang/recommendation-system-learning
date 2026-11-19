from __future__ import annotations

from pathlib import Path
import tempfile

from redbook.automation.platform_adapters import JikeAdapter, XAdapter
from redbook.automation.publishing import PublicationPackage


def _package(platform: str) -> PublicationPackage:
    return PublicationPackage(
        paper_id="arxiv:2608.00001",
        platform=platform,
        canonical_url="https://example.org/papers/2608.00001",
        title="A validated paper",
        body_markdown="A factual, reviewable statement.",
        image_paths=[],
        links={"paper": "https://example.org/paper", "pdf": "https://example.org/pdf", "code": "https://github.com/example/repo"},
    )


def test_public_only_platforms_stage_local_artifacts_and_require_approval() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        staged_x = XAdapter(root).stage(_package("x"))
        staged_jike = JikeAdapter(root).stage(_package("jike"))

        assert staged_x["state"] == "manual_action_required"
        assert staged_jike["state"] == "manual_action_required"
        assert Path(staged_x["artifact_path"]).is_file()
        assert XAdapter(root).publish("unused")["state"] == "approval_required"

