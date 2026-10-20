from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from redbook.automation.platform_adapters import (
    GitHubPagesAdapter,
    JikeAdapter,
    NotionAdapter,
    WeChatDraftAdapter,
    XAdapter,
    ZhihuAnswerAdapter,
)
from redbook.automation.publishing import PublicationPackage


def package(platform: str) -> PublicationPackage:
    return PublicationPackage(
        paper_id="arxiv:2607.09581", platform=platform, canonical_url="https://example.org/papers/2607.09581/",
        title="A validated paper", body_markdown="A factual statement.\n\nPaper: https://example.org/paper",
        image_paths=["cover.png"], links={"paper": "https://example.org/paper", "pdf": "https://example.org/pdf", "code": "https://example.org/code"},
    )


class PlatformAdapterTests(unittest.TestCase):
    def test_x_and_jike_never_call_public_write_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XAdapter(Path(directory)).stage(package("x"))
            jike = JikeAdapter(Path(directory)).stage(package("jike"))
        self.assertEqual(x["state"], "manual_action_required")
        self.assertEqual(jike["state"], "manual_action_required")
        self.assertTrue(Path(x["artifact_path"]).is_file() is False)  # temporary directory is gone

    @patch("redbook.automation.platform_adapters._opencli", return_value="opencli.cmd")
    def test_wechat_stage_uses_creator_draft_not_publish(self, _opencli: object) -> None:
        commands: list[list[str]] = []
        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, '{"draft_id":"wx-draft-1"}', "")
        with tempfile.TemporaryDirectory() as directory:
            result = WeChatDraftAdapter(Path(directory), runner=runner).stage(package("wechat"))
        self.assertEqual(result["state"], "staged")
        self.assertEqual(result["external_id"], "wx-draft-1")
        self.assertIn("create-draft", commands[0])
        self.assertNotIn("publish", commands[0])

    @patch("redbook.automation.platform_adapters._opencli", return_value="opencli.cmd")
    def test_zhihu_reads_question_candidates_without_answer_write(self, _opencli: object) -> None:
        commands: list[list[str]] = []
        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, json.dumps([{"id": "q1", "title": "Relevant question"}]), "")
        with tempfile.TemporaryDirectory() as directory:
            result = ZhihuAnswerAdapter(Path(directory), runner=runner).stage(package("zhihu"))
            artifact = json.loads(Path(result["artifact_path"]).read_text(encoding="utf-8"))
        self.assertEqual(result["state"], "manual_action_required")
        self.assertEqual(artifact["zhihu_question_candidates"][0]["id"], "q1")
        self.assertIn("search", commands[0])
        self.assertNotIn("answer", commands[0])

    @patch("redbook.automation.platform_adapters._gh", return_value="gh")
    def test_github_pages_commits_only_to_non_public_staging_branch(self, _gh: object) -> None:
        commands: list[list[str]] = []
        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            if command[-2:] == ["--jq", ".private"]:
                return subprocess.CompletedProcess(command, 0, "true\n", "")
            return subprocess.CompletedProcess(command, 0, json.dumps({"content": {"html_url": "https://github.com/o/r/blob/staging/a.md"}, "commit": {"sha": "abc"}}), "")
        with patch.dict("os.environ", {"REDBOOK_GITHUB_PAGES_REPO": "owner/repo", "REDBOOK_GITHUB_PAGES_BRANCH": "redbook-staging"}, clear=False):
            with tempfile.TemporaryDirectory() as directory:
                result = GitHubPagesAdapter(Path(directory), runner=runner).stage(package("github_pages"))
        self.assertEqual(result["state"], "staged")
        stage_command = next(command for command in commands if "--method" in command and "PUT" in command)
        self.assertIn("branch=redbook-staging", stage_command)
        self.assertNotIn("gh-pages", " ".join(stage_command))

    @patch("redbook.automation.platform_adapters._gh", return_value="gh")
    def test_github_pages_creates_missing_staging_branch_from_default(self, _gh: object) -> None:
        commands: list[list[str]] = []
        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            target = " ".join(command)
            if "auth status" in target:
                return subprocess.CompletedProcess(command, 0, "", "")
            if target.endswith("repos/owner/repo --jq .private"):
                return subprocess.CompletedProcess(command, 0, "true\n", "")
            if "git/ref/heads/redbook-staging" in target:
                return subprocess.CompletedProcess(command, 1, "", "not found")
            if target.endswith("repos/owner/repo --jq .default_branch"):
                return subprocess.CompletedProcess(command, 0, "main\n", "")
            if "git/ref/heads/main" in target:
                return subprocess.CompletedProcess(command, 0, json.dumps({"object": {"sha": "base"}}), "")
            return subprocess.CompletedProcess(command, 0, json.dumps({"content": {}, "commit": {"sha": "staged"}}), "")
        with patch.dict("os.environ", {"REDBOOK_GITHUB_PAGES_REPO": "owner/repo", "REDBOOK_GITHUB_PAGES_BRANCH": "redbook-staging"}, clear=False):
            with tempfile.TemporaryDirectory() as directory:
                result = GitHubPagesAdapter(Path(directory), runner=runner).stage(package("github_pages"))
        self.assertEqual(result["state"], "staged")
        self.assertTrue(any("refs/heads/redbook-staging" in " ".join(command) for command in commands))

    def test_notion_stage_creates_workspace_controlled_page(self) -> None:
        captured: dict[str, object] = {}
        def fake_http(method: str, url: str, headers: dict[str, str], payload: dict[str, object]) -> dict[str, str]:
            captured.update({"method": method, "url": url, "headers": headers, "payload": payload})
            return {"id": "notion-1", "url": "https://notion.so/notion-1"}
        with patch.dict("os.environ", {"NOTION_TOKEN": "secret", "NOTION_PARENT_PAGE_ID": "parent"}, clear=False):
            with tempfile.TemporaryDirectory() as directory:
                result = NotionAdapter(Path(directory), http_json=fake_http).stage(package("notion"))
        self.assertEqual(result["state"], "staged")
        self.assertEqual(captured["method"], "POST")
        self.assertIn("Authorization", captured["headers"])

    def test_publish_is_always_an_explicit_approval_boundary(self) -> None:
        result = XAdapter(Path(".")).publish("external-id")
        self.assertEqual(result["state"], "approval_required")


if __name__ == "__main__":
    unittest.main()
