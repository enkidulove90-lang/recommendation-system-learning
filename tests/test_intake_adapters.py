from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from paper_intake.adapters import (
    DEEPSEEK_ARTICLE_SYSTEM_PROMPT,
    DeepSeekArticleAdapter,
    GitHubPagesGateway,
    MinerUAdapter,
    NotionDraft,
    NotionGateway,
)
from paper_intake.trace_context import trace_scope


def _article_payload(figure_sha256: str) -> dict:
    return {
        "schema_version": 1,
        "paper": {
            "canonical_id": "2608.17316",
            "title": "A Paper",
            "chinese_title": "一篇论文",
            "authors": ["Alice"],
            "paper_url": "https://arxiv.org/abs/2608.17316",
            "code_url": "",
        },
        "classification": {
            "categories": ["推荐系统", "论文速递"],
            "tags": ["论文速读"],
            "venue_type": "arXiv预印本",
            "venue_name": "arXiv",
        },
        "article": {
            "introduction": "研究背景内容完整。",
            "method": "方法内容完整。",
            "experiments": "实验内容完整。",
            "conclusion": "总结内容完整。",
            "references": ["https://arxiv.org/abs/2608.17316"],
        },
        "figures": [
            {
                "path": "images/figure.png",
                "sha256": figure_sha256,
                "section": "method",
                "explanation": "这张图展示论文方法的主要信息流、核心模块与训练目标之间的连接关系。",
            }
        ],
    }


class _FakeMinerUParser:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class _FakeDeepSeekCompletions:
    def __init__(self, content: str):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class _FakeDeepSeekClient:
    def __init__(self, content: str):
        self.chat = SimpleNamespace(completions=_FakeDeepSeekCompletions(content))


class _FakeBalanceTransport:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def request(self, method: str, path: str, **kwargs):
        self.calls.append((method, path, kwargs))
        return self.payload


class _FakeNotionTransport:
    def __init__(self, property_names=None):
        self.calls = []
        self.last_properties = {}
        self.page_exists = False
        self.created_pages = 0
        self.uploads = 0
        self.blocks = []
        self.markdown = "old remote body"
        self.property_names = property_names or [
            "title", "status", "type", "slug", "summary", "arxiv_id",
            "category", "tags", "year", "venue_type", "venue_name"
        ]

    def request(self, method: str, path: str, **kwargs):
        self.calls.append((method, path, kwargs))
        if method == "GET" and path == "/databases/database":
            return {"data_sources": [{"id": "source"}]}
        if method == "GET" and path == "/data_sources/source":
            return {"properties": {name: {} for name in self.property_names}}
        if method == "POST" and path == "/data_sources/source/query":
            results = [{"id": "page", "url": "https://notion.so/page"}] if self.page_exists else []
            return {"results": results, "has_more": False}
        if method == "POST" and path == "/pages":
            self.page_exists = True
            self.created_pages += 1
            self.last_properties = kwargs["json"]["properties"]
            return {"id": "page", "url": "https://notion.so/page"}
        if method == "PATCH" and path == "/pages/page":
            self.last_properties = kwargs["json"]["properties"]
            return {}
        if method == "GET" and path == "/pages/page/markdown":
            return {"markdown": self.markdown}
        if method == "GET" and path == "/blocks/page/children":
            return {"results": [], "has_more": False}
        if method == "POST" and path == "/file_uploads":
            self.uploads += 1
            return {"id": f"upload-{self.uploads}"}
        if method == "POST" and path.startswith("/file_uploads/") and path.endswith("/send"):
            return {}
        if method == "PATCH" and path == "/blocks/page/children":
            self.blocks.extend(kwargs["json"]["children"])
            return {}
        raise AssertionError(f"Unexpected Notion request: {method} {path}")


class _FakeGitHubTransport:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls = []

    def request(self, method: str, path: str, **kwargs):
        self.calls.append((method, path, kwargs))
        if self.error:
            raise self.error
        return {}


class AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.pdf = self.root / "paper.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\nbody")
        self.markdown = self.root / "paper.md"
        self.markdown.write_text("# Parsed paper", encoding="utf-8")
        self.image = self.root / "images" / "figure.png"
        self.image.parent.mkdir()
        self.image.write_bytes(b"figure")
        self.figure_hash = hashlib.sha256(self.image.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_mineru_adapter_uses_local_pdf_and_collects_images(self) -> None:
        parser = _FakeMinerUParser(
            {"error": None, "markdown_path": str(self.markdown), "content": {"text": "parsed"}}
        )
        adapter = MinerUAdapter(parser=parser)

        result = adapter.parse(self.pdf, canonical_id="2608.17316", title="A Paper")

        self.assertEqual(parser.calls[0]["pdf_path"], str(self.pdf))
        self.assertEqual(result.markdown_path, self.markdown)
        self.assertEqual(result.image_paths, (self.image,))

    def test_trace_id_is_forwarded_to_mineru_and_deepseek(self) -> None:
        parser = _FakeMinerUParser(
            {"error": None, "markdown_path": str(self.markdown), "content": {"text": "parsed"}}
        )
        content = json.dumps(_article_payload(self.figure_hash), ensure_ascii=False)
        client = _FakeDeepSeekClient(content)
        with trace_scope("tr_test-chain"):
            MinerUAdapter(parser=parser).parse(self.pdf, canonical_id="2608.17316")
            DeepSeekArticleAdapter(api_key="secret", client=client).generate(
                markdown="# Full paper", metadata={"canonical_id": "2608.17316", "title": "A Paper"}, figures=[]
            )
        self.assertEqual(parser.calls[0]["trace_id"], "tr_test-chain")
        self.assertEqual(client.chat.completions.calls[0]["extra_headers"], {"X-Trace-Id": "tr_test-chain"})

    def test_deepseek_adapter_requests_json_and_parses_article(self) -> None:
        content = json.dumps(_article_payload(self.figure_hash), ensure_ascii=False)
        client = _FakeDeepSeekClient(content)
        adapter = DeepSeekArticleAdapter(api_key="secret", model="deepseek-chat", client=client)

        envelope = adapter.generate(
            markdown="# Full paper",
            metadata={"canonical_id": "2608.17316", "title": "A Paper"},
            figures=[{"path": "images/figure.png", "sha256": self.figure_hash}],
        )

        call = client.chat.completions.calls[0]
        self.assertEqual(call["response_format"], {"type": "json_object"})
        self.assertEqual(envelope.article.paper.canonical_id, "2608.17316")

    def test_deepseek_prompt_preserves_content_rules_and_adds_only_formula_and_selection(self) -> None:
        content = json.dumps(
            {
                "article": _article_payload(self.figure_hash),
                "reference_choices": [
                    {"ref_id": "ref_001", "reason": "与核心方法直接相关。"},
                    {"ref_id": "ref_002", "reason": "提供最新的对比方法。"},
                ],
            },
            ensure_ascii=False,
        )
        client = _FakeDeepSeekClient(content)
        adapter = DeepSeekArticleAdapter(api_key="secret", model="deepseek-chat", client=client)

        envelope = adapter.generate(
            markdown="# Full paper\n公式 $x$ 与 $$y$$",
            metadata={"canonical_id": "2608.17316", "title": "A Paper"},
            figures=[{"path": "images/figure.png", "sha256": self.figure_hash}],
            reference_candidates=[
                {"ref_id": "ref_001", "title": "First", "year": 2025},
                {"ref_id": "ref_002", "title": "Second", "year": 2026},
            ],
        )

        call = client.chat.completions.calls[0]
        self.assertEqual(
            call["messages"][0]["content"],
            "你是推荐系统论文编辑。只输出符合给定 Schema 的 JSON；不得虚构实验数字、链接或图片路径。",
        )
        self.assertEqual(call["messages"][0]["content"], DEEPSEEK_ARTICLE_SYSTEM_PROMPT)
        prompt = json.loads(call["messages"][1]["content"])
        requirements = prompt["requirements"]
        self.assertEqual(requirements["language"], "Chinese")
        self.assertEqual(
            requirements["sections"],
            ["introduction", "method", "experiments", "conclusion", "references"],
        )
        self.assertEqual(
            requirements["figure_rule"],
            "Use only available figure paths and write an original Chinese explanation.",
        )
        self.assertEqual(
            set(requirements),
            {
                "language",
                "sections",
                "figure_rule",
                "output_schema",
                "formula_format",
                "reference_selection",
            },
        )
        self.assertIn("$...$", requirements["formula_format"])
        self.assertIn("$$...$$", requirements["formula_format"])
        self.assertEqual(
            [item["ref_id"] for item in requirements["reference_selection"]["candidates"]],
            ["ref_001", "ref_002"],
        )
        self.assertNotIn(
            "http", json.dumps(requirements["reference_selection"], ensure_ascii=False).lower()
        )
        self.assertEqual(
            [choice.ref_id for choice in envelope.reference_choices or []],
            ["ref_001", "ref_002"],
        )

    def test_deepseek_invalid_output_is_redacted_and_saved_for_diagnosis(self) -> None:
        secret = "sk-super-secret-value"
        content = '{"paper":{"title":"' + secret + '"}}'
        client = _FakeDeepSeekClient(content)
        adapter = DeepSeekArticleAdapter(api_key="secret", client=client)
        failure_path = self.root / "diagnostics" / "deepseek-invalid.json"

        with self.assertRaises(Exception) as caught:
            adapter.generate(
                markdown="# Full paper",
                metadata={"canonical_id": "2608.17316", "title": "A Paper"},
                figures=[],
                failure_path=failure_path,
            )

        saved_text = failure_path.read_text(encoding="utf-8")
        saved = json.loads(saved_text)
        self.assertEqual(caught.exception.code, "deepseek_invalid_output")
        self.assertIn("paper.paper_url", str(caught.exception))
        self.assertNotIn(secret, saved_text)
        self.assertIn("[REDACTED]", saved["response"])
        self.assertTrue(saved["validation_errors"])

    def test_deepseek_preflight_rejects_unavailable_balance(self) -> None:
        balance = _FakeBalanceTransport({"is_available": False, "balance_infos": []})
        adapter = DeepSeekArticleAdapter(
            api_key="secret",
            client=_FakeDeepSeekClient("{}"),
            preflight_transport=balance,
        )

        with self.assertRaisesRegex(Exception, "balance") as caught:
            adapter.preflight()

        self.assertEqual(caught.exception.code, "deepseek_balance_low")
        self.assertEqual(balance.calls[0][0:2], ("GET", "/user/balance"))

    def test_notion_upsert_defaults_new_article_to_draft_and_uploads_figure(self) -> None:
        transport = _FakeNotionTransport()
        gateway = NotionGateway("token", "database", transport=transport)
        draft = NotionDraft(
            arxiv_id="2608.17316",
            title="一篇论文",
            slug="paper-2608.17316",
            summary="摘要",
            markdown="# 一篇论文\n\n![方法图 1](/images/papers/2608.17316/figure.png)",
            figure_paths=(self.image,),
        )

        page = gateway.upsert_draft(draft)

        self.assertEqual(transport.last_properties["status"]["select"]["name"], "Draft")
        self.assertEqual(transport.created_pages, 1)
        self.assertEqual(transport.uploads, 1)
        self.assertEqual(page.page_id, "page")
        self.assertEqual(page.before_markdown, "")

    def test_notion_metadata_refresh_updates_properties_without_touching_body(self) -> None:
        transport = _FakeNotionTransport(
            property_names=[
                "title", "status", "type", "slug", "arxiv_id", "year",
                "authors", "published", "updated",
            ]
        )
        gateway = NotionGateway("token", "database", transport=transport)

        gateway.update_metadata_properties(
            "page",
            {
                "canonical_id": "2606.17628",
                "title": "OPD-Evolver",
                "authors": ["Author One", "Author Two"],
                "published": "2026-06-18T00:00:00Z",
                "updated": "2026-06-20T09:30:00Z",
            },
        )

        mutation_calls = [call for call in transport.calls if call[0] in {"POST", "PATCH", "DELETE"}]
        self.assertEqual([(method, path) for method, path, _ in mutation_calls], [("PATCH", "/pages/page")])
        self.assertEqual(transport.last_properties["title"]["title"][0]["text"]["content"], "OPD-Evolver")
        self.assertEqual(
            transport.last_properties["authors"]["rich_text"][0]["text"]["content"],
            "Author One, Author Two",
        )
        self.assertNotIn("status", transport.last_properties)

    def test_notion_preflight_rejects_missing_required_schema(self) -> None:
        transport = _FakeNotionTransport(
            property_names=["title", "status", "type", "summary", "arxiv_id"]
        )
        gateway = NotionGateway("token", "database", transport=transport)

        with self.assertRaises(Exception) as caught:
            gateway.preflight_schema()

        self.assertEqual(caught.exception.code, "notion_schema_mismatch")
        self.assertIn("slug", str(caught.exception))

    def test_notion_preflight_allows_optional_summary_and_arxiv_id(self) -> None:
        transport = _FakeNotionTransport(
            property_names=["title", "status", "type", "slug"]
        )
        gateway = NotionGateway("token", "database", transport=transport)

        self.assertEqual(gateway.preflight_schema(), {"title", "status", "type", "slug"})

    def test_notion_existing_page_is_snapshotted_before_update(self) -> None:
        transport = _FakeNotionTransport()
        transport.page_exists = True
        gateway = NotionGateway("token", "database", transport=transport)

        page = gateway.upsert_draft(
            NotionDraft(
                arxiv_id="2608.17316",
                title="一篇论文",
                slug="paper-2608.17316",
                summary="摘要",
                markdown="# replacement",
            )
        )

        self.assertEqual(transport.created_pages, 0)
        self.assertEqual(page.before_markdown, "old remote body")
        self.assertEqual(transport.last_properties["status"]["select"]["name"], "Draft")

    def test_notion_direct_publish_sets_published_post_before_writing_blocks(self) -> None:
        transport = _FakeNotionTransport()
        gateway = NotionGateway("token", "database", transport=transport)

        page = gateway.upsert_published(
            NotionDraft(
                arxiv_id="2608.17316",
                title="一篇论文",
                slug="paper-2608.17316",
                summary="摘要",
                markdown="# published body",
                categories=("推荐系统", "生成式推荐"),
                tags=("论文速读", "Semantic ID"),
                year="2026",
                venue_type="会议",
                venue_name="RecSys 2026",
            )
        )

        self.assertEqual(transport.last_properties["status"]["select"]["name"], "Published")
        self.assertEqual(transport.last_properties["type"]["select"]["name"], "Post")
        self.assertEqual(
            transport.last_properties["category"]["select"]["name"],
            "推荐系统 / 生成式推荐",
        )
        self.assertEqual(
            [item["name"] for item in transport.last_properties["tags"]["multi_select"]],
            ["论文速读", "Semantic ID"],
        )
        self.assertEqual(transport.last_properties["venue_type"]["select"]["name"], "会议")
        self.assertEqual(transport.last_properties["year"]["select"]["name"], "2026")
        self.assertEqual(
            transport.last_properties["venue_name"]["rich_text"][0]["text"]["content"],
            "RecSys 2026",
        )
        self.assertEqual(page.status, "Published")

    def test_notion_approval_only_changes_status_to_published(self) -> None:
        transport = _FakeNotionTransport()
        transport.page_exists = True
        gateway = NotionGateway("token", "database", transport=transport)

        gateway.publish("page", title="一篇论文", slug="paper-2608.17316", arxiv_id="2608.17316")

        self.assertEqual(transport.last_properties["status"]["select"]["name"], "Published")

    def test_notion_restore_replaces_body_and_returns_page_to_draft(self) -> None:
        transport = _FakeNotionTransport()
        transport.page_exists = True
        gateway = NotionGateway("token", "database", transport=transport)

        page = gateway.restore_draft(
            "page",
            markdown="# Restored body",
            title="一篇论文",
            slug="paper-2608.17316",
            arxiv_id="2608.17316",
        )

        self.assertEqual(page.status, "Draft")
        self.assertEqual(transport.last_properties["status"]["select"]["name"], "Draft")
        self.assertTrue(any(block["type"] == "heading_1" for block in transport.blocks))

    def test_github_dispatch_is_optional_and_uses_workflow_dispatch(self) -> None:
        no_token = GitHubPagesGateway(token="", repository="owner/site")
        self.assertFalse(no_token.dispatch().triggered)

        transport = _FakeGitHubTransport()
        gateway = GitHubPagesGateway(
            token="github-token",
            repository="owner/site",
            workflow="publish.yml",
            ref="source",
            transport=transport,
        )
        result = gateway.dispatch()

        self.assertTrue(result.triggered)
        method, path, kwargs = transport.calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(path, "/repos/owner/site/actions/workflows/publish.yml/dispatches")
        self.assertEqual(kwargs["json"], {"ref": "source"})

    def test_github_error_does_not_expose_token(self) -> None:
        token = "github-super-secret-token"
        gateway = GitHubPagesGateway(
            token=token,
            repository="owner/site",
            transport=_FakeGitHubTransport(RuntimeError(f"request failed with {token}")),
        )

        with self.assertRaises(Exception) as caught:
            gateway.dispatch()

        self.assertNotIn(token, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
