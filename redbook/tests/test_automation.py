from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from redbook.automation.feedback import FeedbackStore
from redbook.automation.common import append_jsonl
from redbook.automation.images import build_manifest, compose_group, group_figures, metadata_from_mineru_markdown
from redbook.automation.publishing import FilePublisher, render_package
from redbook.automation.scheduling import PublishScheduler
from redbook.automation.scoring import QualityScorerV2
from redbook.automation.sources import JsonlSource, PaperRecord, SourceRunner, deduplicate_records


class AutomationTests(unittest.TestCase):
    def test_deduplicate_merges_identifier_records(self) -> None:
        left = PaperRecord.from_dict({"title": "A Paper", "identifiers": {"arxiv": "2607.00001"}, "source_records": [{"source_type": "arxiv"}]})
        right = PaperRecord.from_dict({"title": "A Paper Final", "identifiers": {"doi": "10.1/example", "arxiv": "2607.00001"}, "urls": {"pdf": "https://example/pdf"}, "source_records": [{"source_type": "proceedings"}]})
        merged = deduplicate_records([left, right])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].identifiers["doi"], "10.1/example")
        self.assertEqual(merged[0].urls["pdf"], "https://example/pdf")

    def test_quality_score_v2_uses_new_dimensions(self) -> None:
        result = QualityScorerV2().score({
            "citing_q1_ratio": 0.8, "citation_count": 30, "age_months": 6,
            "citing_focal_only": 8, "citing_prior_only": 2, "citing_both": 1,
            "problem_method_frequency": 1, "method_improvement": 0.9,
            "application_improvement": 0.8, "dataset_improvement": 0.6,
            "institution_count": 3, "region_count": 2, "author_count": 6,
            "content_completeness": 0.9, "official_code": True,
        })
        self.assertIn("disruption", result.dimensions)
        self.assertGreater(result.score, 0.72)
        self.assertEqual(result.decision, "full_analysis")

    def test_scheduler_prefers_balanced_exploration_then_event_gate(self) -> None:
        scheduler = PublishScheduler()
        now = datetime(2026, 7, 29, 9, tzinfo=timezone.utc)
        ordinary = scheduler.choose([], now)
        self.assertEqual(ordinary.strategy, "balanced_explore")
        event = {"first_seen_at": "2026-07-29T08:00:00+00:00", "quality_score": 0.9, "verified": True}
        triggered = scheduler.choose([], now, event)
        self.assertTrue(triggered.event_triggered)

    def test_file_publisher_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paper = {"paper_id": "arxiv:1", "title": "Paper", "summary": "A factual summary.", "links": {"paper": "https://paper", "pdf": "https://pdf"}}
            package = render_package(paper, "wechat", "https://canonical")
            publisher = FilePublisher("wechat", Path(directory))
            self.assertEqual(publisher.stage(package)["status"], "staged")
            self.assertEqual(publisher.stage(package)["status"], "already_staged")

    def test_feedback_metrics_are_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = FeedbackStore(Path(directory))
            store.register_post({"note_id": "n1", "paper_id": "arxiv:1", "published_at": "2026-07-01T08:15:00+00:00", "time_slot": "08:15", "content_hash": "abc"})
            result = store.record_snapshot("n1", 168, {"views": 1000, "likes": 20, "collects": 30, "comments": 4, "replies": 2, "shares": 3, "follows": 5})
            self.assertTrue(result["available"])
            self.assertAlmostEqual(result["sr"], 0.03)

    def test_source_runner_writes_replayable_jsonl_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixture.jsonl"
            append_jsonl(fixture, [{"title": "Paper", "identifiers": {"arxiv": "2607.1"}, "source_records": [{"source": "fixture", "source_type": "arxiv", "source_id": "1", "url": "https://example", "fetched_at": "2026-07-01T00:00:00+00:00"}]}])
            result = SourceRunner(root / "data").run(JsonlSource("fixture", fixture))
            self.assertEqual(result["count"], 1)
            self.assertTrue(Path(result["raw_path"]).exists())
            self.assertTrue(Path(result["state_path"]).exists())

    def test_composer_preserves_uncropped_panels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, colour in enumerate(("red", "blue"), 1):
                path = root / f"fig-{index}.jpg"
                Image.new("RGB", (1800, 900), colour).save(path)
                paths.append(path)
            manifest = root / "manifest.jsonl"
            assets = build_manifest(paths, manifest, {path.name: {"figure_id": "Figure 1", "caption": "Shared evaluation", "page": 1} for path in paths})
            groups = group_figures(assets)
            self.assertEqual(len(groups[0]), 2)
            result = compose_group(groups[0], root / "combined.jpg")
            self.assertTrue(result["composed"])
            with Image.open(root / "combined.jpg") as output:
                self.assertEqual(output.size, (1440, 1920))

    def test_mineru_metadata_uses_nearest_figure_caption(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "figure.jpg"
            Image.new("RGB", (1600, 900), "white").save(image)
            markdown = root / "paper.md"
            markdown.write_text("## Method\n![](images/figure.jpg)\nFigure 1: The model architecture.\n", encoding="utf-8")
            result = metadata_from_mineru_markdown(markdown, [image])
            self.assertEqual(result["figure.jpg"]["figure_id"], "Figure 1")


if __name__ == "__main__":
    unittest.main()
