from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from paper_intake.adapters import ExternalServiceError, NotionPage, ParseResult
from paper_intake.article import PaperArticle
from paper_intake.inputs import PaperInputStore
from paper_intake.models import JobStatus, StepName, StepStatus
from paper_intake.pipeline import PaperPipeline
from paper_intake.remote import LeaseLost
from paper_intake.repository import JobRepository


class _FakeMinerU:
    def __init__(self, root: Path, *, with_figure: bool = True):
        self.calls = 0
        self.markdown = root / "parsed" / "paper.md"
        self.markdown.parent.mkdir(parents=True)
        self.markdown.write_text("# Full paper\n\nMethod and experiments", encoding="utf-8")
        self.images: tuple[Path, ...] = ()
        if with_figure:
            image = self.markdown.parent / "images" / "figure.png"
            image.parent.mkdir()
            image.write_bytes(b"figure-content")
            self.images = (image,)

    def parse(self, _pdf_path, *, canonical_id: str, title: str = "") -> ParseResult:
        self.calls += 1
        return ParseResult(self.markdown, self.images, self.markdown.read_text(encoding="utf-8"))


class _FakeDeepSeek:
    def __init__(self, *, fail_once: bool = False):
        self.calls = 0
        self.fail_once = fail_once
        self.metadata_history = []

    def generate(self, *, markdown: str, metadata: dict, figures: list[dict], failure_path=None) -> PaperArticle:
        self.calls += 1
        self.metadata_history.append(dict(metadata))
        if self.fail_once and self.calls == 1:
            raise ExternalServiceError("deepseek_timeout", "DeepSeek request timed out.")
        article_figures = []
        if figures:
            article_figures.append(
                {
                    "path": figures[0]["path"],
                    "sha256": figures[0]["sha256"],
                    "section": "method",
                    "explanation": "这张图展示了论文方法的核心模块、信息流向以及各组成部分之间的协作关系。",
                }
            )
        return PaperArticle.model_validate(
            {
                "schema_version": 1,
                "paper": {
                    "canonical_id": metadata["canonical_id"],
                    "title": metadata["title"],
                    "chinese_title": "测试论文",
                    "authors": metadata.get("authors", []),
                    "paper_url": metadata["paper_url"],
                    "code_url": "",
                },
                "classification": {
                    "categories": ["推荐系统", "论文速递"],
                    "tags": ["论文速读"],
                    "venue_type": "arXiv预印本",
                    "venue_name": "arXiv",
                },
                "article": {
                    "introduction": "论文研究推荐系统中的表示学习问题，并分析现有方法在噪声环境下的局限。",
                    "method": "作者提出新的表示学习模块，并通过可靠性权重控制不同信息来源的贡献。",
                    "experiments": "实验比较多个公开基线，并通过消融实验验证核心模块的实际作用。",
                    "conclusion": "结果表明该方法能够稳定改善性能，并为后续研究提供清晰的模块化方向。",
                    "references": [metadata["paper_url"]],
                },
                "figures": article_figures,
            }
        )


class _FakeNotion:
    def __init__(self):
        self.calls = 0
        self.pages = []

    def upsert_published(self, draft):
        self.calls += 1
        self.pages.append(draft)
        return NotionPage("page-id", "https://notion.so/page-id", "Published", "old body")


class PipelineHarness:
    def __init__(self, root: Path, *, fail_once: bool = False, with_figure: bool = True):
        self.root = root
        self.repo = JobRepository(root / "jobs.sqlite3")
        self.input_store = PaperInputStore(root / "inbox")
        saved = self.input_store.store_upload("seed", "paper.pdf", b"%PDF-1.7\nbody")
        self.job = self.repo.create_job(source_type="upload", upload_path=str(saved.path))
        self.mineru = _FakeMinerU(root, with_figure=with_figure)
        self.deepseek = _FakeDeepSeek(fail_once=fail_once)
        self.notion = _FakeNotion()
        self.pipeline = PaperPipeline(
            repository=self.repo,
            input_store=self.input_store,
            mineru=self.mineru,
            deepseek=self.deepseek,
            notion=self.notion,
            workflow_root=root / "workflow",
            metadata_resolver=lambda canonical_id, _url: {
                "canonical_id": canonical_id,
                "title": "A Test Paper",
                "authors": ["Alice"],
                "paper_url": f"https://arxiv.org/abs/{canonical_id}",
            },
        )

    def close(self):
        self.repo.close()


class PaperPipelineTests(unittest.TestCase):
    def test_lease_lost_from_checkpoint_callback_is_not_swallowed(self):
        pipeline = object.__new__(PaperPipeline)
        pipeline.PROCESSING_STEPS = (StepName.VALIDATE_INPUT,)
        job = type("Job", (), {"status": JobStatus.RECEIVED})()
        pipeline._job = lambda _job_id: job
        pipeline._run_step = lambda _job_id, _step: {}
        pipeline.repository = type("Repository", (), {"get_job": lambda _self, _job_id: job})()

        with self.assertRaises(LeaseLost):
            pipeline.run(
                "job-1",
                on_step_completed=lambda _step, _output: (_ for _ in ()).throw(LeaseLost("lost")),
            )

    def test_lease_guard_stops_before_the_next_external_step(self):
        pipeline = object.__new__(PaperPipeline)
        pipeline.PROCESSING_STEPS = (StepName.VALIDATE_INPUT, StepName.RESOLVE_METADATA)
        job = type("Job", (), {"status": JobStatus.RECEIVED})()
        executed = []
        pipeline._job = lambda _job_id: job
        pipeline._run_step = lambda _job_id, step: executed.append(step) or {}
        pipeline.repository = type("Repository", (), {"get_job": lambda _self, _job_id: job})()
        guards = iter((None, LeaseLost("lost")))

        with self.assertRaises(LeaseLost):
            pipeline.run(
                "job-1",
                before_step=lambda _step: (_ for _ in ()).throw(error)
                if (error := next(guards))
                else None,
            )

        self.assertEqual(executed, [StepName.VALIDATE_INPUT])
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_successful_run_writes_published_notion_page(self) -> None:
        harness = PipelineHarness(self.root)
        try:
            result = harness.pipeline.run(harness.job.job_id)

            self.assertEqual(result.status, JobStatus.PUBLISHING)
            self.assertEqual(result.notion_page_id, "page-id")
            self.assertEqual(harness.notion.calls, 1)
            self.assertEqual(harness.mineru.calls, 1)
            step_names = [step.step_name for step in harness.repo.list_steps(harness.job.job_id)]
            self.assertEqual(
                step_names,
                [
                    StepName.VALIDATE_INPUT,
                    StepName.RESOLVE_METADATA,
                    StepName.DOWNLOAD_PDF,
                    StepName.MINERU_PARSE,
                    StepName.DEEPSEEK_GENERATE,
                    StepName.CLASSIFY,
                    StepName.QUALITY_CHECK,
                    StepName.WRITE_NOTION_PUBLISHED,
                ],
            )
            self.assertTrue(all(step.status == StepStatus.SUCCEEDED for step in harness.repo.list_steps(harness.job.job_id)))
        finally:
            harness.close()

    def test_retry_after_deepseek_failure_does_not_repeat_mineru(self) -> None:
        harness = PipelineHarness(self.root, fail_once=True)
        try:
            failed = harness.pipeline.run(harness.job.job_id)
            retried = harness.pipeline.retry(harness.job.job_id)

            self.assertEqual(failed.status, JobStatus.FAILED)
            self.assertEqual(retried.status, JobStatus.PUBLISHING)
            self.assertEqual(harness.mineru.calls, 1)
            self.assertEqual(harness.deepseek.calls, 2)
            deepseek_step = harness.repo.get_step(harness.job.job_id, StepName.DEEPSEEK_GENERATE)
            self.assertEqual(deepseek_step.attempts, 2)
        finally:
            harness.close()

    def test_retry_refreshes_fallback_metadata_without_repeating_mineru(self) -> None:
        harness = PipelineHarness(self.root, fail_once=True)
        try:
            metadata_path = harness.pipeline._bundle(harness.job.job_id) / "metadata.json"
            refreshed_calls = []

            def resolver(canonical_id, source_url):
                refreshed_calls.append((canonical_id, source_url))
                return {
                    "canonical_id": canonical_id,
                    "title": "OPD-Evolver: Cultivating Holistic Agent Evolver via On-Policy Distillation",
                    "authors": ["ByteDance Seed"],
                    "paper_url": f"https://arxiv.org/abs/{canonical_id}",
                    "metadata_source": "arxiv",
                }

            failed = harness.pipeline.run(harness.job.job_id)
            stale = __import__("json").loads(metadata_path.read_text(encoding="utf-8"))
            canonical_id = harness.repo.get_job(harness.job.job_id).canonical_id
            stale.update({"title": canonical_id, "authors": []})
            stale.pop("metadata_source", None)
            metadata_path.write_text(
                __import__("json").dumps(stale, ensure_ascii=False), encoding="utf-8"
            )
            harness.pipeline.metadata_resolver = resolver

            retried = harness.pipeline.retry(harness.job.job_id)

            self.assertEqual(failed.status, JobStatus.FAILED)
            self.assertEqual(retried.status, JobStatus.PUBLISHING)
            self.assertEqual(harness.mineru.calls, 1)
            self.assertEqual(len(refreshed_calls), 1)
            self.assertEqual(
                harness.deepseek.metadata_history[-1]["title"],
                "OPD-Evolver: Cultivating Holistic Agent Evolver via On-Policy Distillation",
            )
            refreshed = __import__("json").loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(refreshed["metadata_source"], "arxiv")
        finally:
            harness.close()

    def test_missing_figure_blocks_publication_before_notion(self) -> None:
        harness = PipelineHarness(self.root, with_figure=False)
        try:
            result = harness.pipeline.run(harness.job.job_id)

            self.assertEqual(result.status, JobStatus.FAILED)
            self.assertEqual(harness.notion.calls, 0)
            quality = harness.repo.get_step(harness.job.job_id, StepName.QUALITY_CHECK)
            self.assertEqual(quality.status, StepStatus.SUCCEEDED)
            self.assertIn("figure_required", quality.output["issue_codes"])
            self.assertIsNone(harness.repo.get_step(harness.job.job_id, StepName.WRITE_NOTION_PUBLISHED))
        finally:
            harness.close()

    def test_duplicate_pdf_hash_fails_before_mineru(self) -> None:
        harness = PipelineHarness(self.root)
        try:
            existing = harness.repo.create_job(source_type="upload", upload_path="other.pdf")
            digest = hashlib.sha256(Path(harness.job.upload_path).read_bytes()).hexdigest()
            harness.repo.update_job(existing.job_id, source_sha256=digest)

            result = harness.pipeline.run(harness.job.job_id)

            self.assertEqual(result.status, JobStatus.FAILED)
            self.assertEqual(result.error_code, "duplicate_paper")
            self.assertEqual(harness.mineru.calls, 0)
        finally:
            harness.close()


if __name__ == "__main__":
    unittest.main()
