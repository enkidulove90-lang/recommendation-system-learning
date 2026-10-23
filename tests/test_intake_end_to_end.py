from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paper_intake.adapters import DispatchResult, NotionPage, ParseResult
from paper_intake.article import PaperArticle
from paper_intake.inputs import PaperInputStore
from paper_intake.models import JobStatus
from paper_intake.pipeline import PaperPipeline
from paper_intake.repository import JobRepository
from paper_intake.service import PaperIntakeService


class _MinerU:
    def __init__(self, root: Path):
        parsed = root / "fake-mineru"
        parsed.mkdir()
        self.markdown = parsed / "paper.md"
        self.markdown.write_text("# Paper\n\nMethod and experiment evidence.", encoding="utf-8")
        image_dir = parsed / "images"
        image_dir.mkdir()
        self.image = image_dir / "architecture.png"
        self.image.write_bytes(b"real-image-bytes")

    def parse(self, _pdf_path, *, canonical_id: str, title: str = ""):
        return ParseResult(self.markdown, (self.image,), self.markdown.read_text(encoding="utf-8"))


class _DeepSeek:
    def generate(self, *, markdown: str, metadata: dict, figures: list[dict], failure_path=None):
        return PaperArticle.model_validate(
            {
                "paper": {
                    "canonical_id": metadata["canonical_id"],
                    "title": metadata["title"],
                    "chinese_title": "端到端测试论文",
                    "authors": ["Alice"],
                    "paper_url": metadata["paper_url"],
                },
                "classification": {
                    "categories": ["推荐系统", "论文速递"],
                    "tags": ["论文速读"],
                    "venue_type": "arXiv预印本",
                    "venue_name": "arXiv",
                },
                "article": {
                    "introduction": "论文研究推荐系统中的信息融合问题，并说明现有方法面对噪声时的主要局限。",
                    "method": "作者提出带可靠性控制的表示模块，使不同信息来源能够按可信程度参与最终预测。",
                    "experiments": "实验覆盖多个公开数据集、主要基线和消融设置，并分析各模块带来的性能变化。",
                    "conclusion": "结果支持核心方法的有效性，也揭示了该方案在可扩展性方面仍可继续研究。",
                    "references": [metadata["paper_url"]],
                },
                "figures": [
                    {
                        "path": figures[0]["path"],
                        "sha256": figures[0]["sha256"],
                        "section": "method",
                        "explanation": "这张结构图用信息流展示了核心模块如何接收多源输入、估计可靠性并生成最终推荐表示。",
                    }
                ],
            }
        )


class _Notion:
    def __init__(self):
        self.status = ""
        self.draft_markdown = ""

    def upsert_published(self, draft):
        self.status = "Published"
        self.draft_markdown = draft.markdown
        return NotionPage("page-e2e", "https://notion.so/page-e2e", "Published", "")

    def publish(self, page_id: str, *, title: str, slug: str, arxiv_id: str):
        self.status = "Published"
        return NotionPage(page_id, "https://notion.so/page-e2e", "Published")


class _GitHub:
    def __init__(self):
        self.calls = 0

    def dispatch(self):
        self.calls += 1
        return DispatchResult(True, run_id="run-e2e")


class IntakeEndToEndTests(unittest.TestCase):
    def test_pdf_survives_direct_publish_and_repository_restart(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = root / "jobs.sqlite3"
            repository = JobRepository(database)
            store = PaperInputStore(root / "inbox")
            notion = _Notion()
            github = _GitHub()
            pipeline = PaperPipeline(
                repository=repository,
                input_store=store,
                mineru=_MinerU(root),
                deepseek=_DeepSeek(),
                notion=notion,
                workflow_root=root / "workflow",
                metadata_resolver=lambda canonical_id, source_url: {
                    "canonical_id": canonical_id,
                    "title": "An End-to-End Paper",
                    "authors": ["Alice"],
                    "paper_url": source_url,
                },
            )
            service = PaperIntakeService(
                repository=repository,
                input_store=store,
                pipeline=pipeline,
                notion=notion,
                github=github,
                workflow_root=root / "workflow",
                site_url="https://example.github.io",
                start_worker=False,
            )

            job = service.submit_upload(
                "paper.pdf",
                b"%PDF-1.7\nbody",
                paper_url="https://arxiv.org/abs/2608.17316",
            )
            original_pdf = Path(repository.get_job(job.job_id).upload_path)
            self.assertTrue(service.run_pending_once())
            publishing = repository.get_job(job.job_id)

            self.assertEqual(publishing.status, JobStatus.PUBLISHING)
            self.assertEqual(notion.status, "Published")
            self.assertIn("## 方法", notion.draft_markdown)
            self.assertTrue(original_pdf.is_file())
            self.assertEqual(github.calls, 0)
            published = service.verify_publication(job.job_id, checker=lambda _url: True)
            self.assertEqual(published.status, JobStatus.PUBLISHED)

            service.close()
            repository.close()
            reopened = JobRepository(database)
            try:
                persisted = reopened.get_job(job.job_id)
                self.assertEqual(persisted.status, JobStatus.PUBLISHED)
                self.assertEqual(persisted.github_run_id, "")
                self.assertTrue(original_pdf.is_file())
                self.assertGreaterEqual(len(reopened.list_events(job.job_id)), 19)
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
