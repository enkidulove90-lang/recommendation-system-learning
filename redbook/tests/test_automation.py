from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess

from PIL import Image

from redbook.automation.feedback import FeedbackStore
from redbook.automation.daily_discovery import DailyDiscoveryConfig, filter_candidates
from redbook.automation.daily_runner import DailyDraftRunner, configured_interval_minutes
from redbook.automation.one_click import QualifiedPaperDraftDelivery, OneClickEligibilityError
from redbook.automation.common import append_jsonl
from redbook.automation.content_operations import ContentOperationError, PaperCardStore, ReviewQueue, XiaohongshuPaperRenderer, card_content_hash
from redbook.automation.images import build_manifest, compose_group, group_figures, metadata_from_mineru_markdown
from redbook.automation.publishing import FilePublisher, render_package
from redbook.automation.scheduling import PublishScheduler
from redbook.automation.scoring import QualityScorerV2
from redbook.automation.sources import ArxivSource, JsonlSource, PaperRecord, SourceRunner, deduplicate_records


class AutomationTests(unittest.TestCase):
    def test_paper_card_is_the_validated_fact_source_for_xhs_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf, markdown = root / "p.pdf", root / "p.md"
            pdf.write_bytes(b"%PDF-1.7"); markdown.write_text("parsed", encoding="utf-8")
            figures = []
            for index in range(4):
                path = root / f"f{index}.png"; path.write_bytes(b"png")
                figures.append({"path": str(path), "role": "results"})
            card = {
                "schema_version": 1, "paper_id": "arxiv:2607.1",
                "identity": {"title": "A factual paper", "authors": [], "organizations": [], "venue": {"name": "arXiv", "year": 2026, "status": "preprint"}},
                "provenance": {"source_records": [{"url": "https://arxiv.org/abs/2607.1"}], "verified_at": "2026-08-02T00:00:00+00:00", "verifier": "test"},
                "links": {"landing": "https://arxiv.org/abs/2607.1", "pdf": "https://arxiv.org/pdf/2607.1", "official_github": "https://github.com/org/repo"},
                "evidence": {"problem": ["A measured problem."], "contributions": ["A verified contribution."], "method": ["A documented method."], "benchmarks": [], "experimental_conditions": [], "results": ["A reported result."], "limitations": ["A stated boundary."]},
                "assets": {"local_pdf": str(pdf), "mineru_markdown": str(markdown), "figures": figures},
                "eligibility": {"official_github_verified": True, "venue_verified": True, "mineru_verified": True, "high_resolution_figure_count": 4, "eligible": True, "reasons": []},
                "strategy": {"platform": "xiaohongshu", "angle": "research_evidence", "topics": ["人工智能"]},
                "delivery": {"mode": "draft_only", "state": "discovered"},
            }
            card["content_hash"] = card_content_hash(card)
            card_path = root / "paper_card.json"
            PaperCardStore().write(card_path, card)
            loaded = PaperCardStore.load(card_path, require_delivery_assets=True)
            rendered = XiaohongshuPaperRenderer.render(loaded)
            review = ReviewQueue(root).create(card_path, loaded)
            review = ReviewQueue(root).transition("arxiv:2607.1", "qualified")

        self.assertEqual(rendered["topics"], ["人工智能"])
        self.assertIn("A reported result.", rendered["body"])
        self.assertEqual(review["state"], "qualified")

    def test_review_queue_rejects_skipped_states(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            queue = ReviewQueue(Path(directory))
            path = queue.path_for("arxiv:1")
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"paper_id": "arxiv:1", "state": "discovered", "history": [], "content_hash": "x"}), encoding="utf-8")
            with self.assertRaises(ContentOperationError):
                queue.transition("arxiv:1", "staged")

    def test_daily_runner_writes_fail_closed_qualification_queue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "data"
            candidate_path = root / "discovery" / "today" / "candidates.jsonl"
            append_jsonl(candidate_path, [{"title": "Candidate", "identifiers": {"arxiv": "2608.1"}}])

            class Discovery:
                def __init__(self, *_: object) -> None:
                    pass

                def run(self) -> dict[str, object]:
                    return {"candidate_path": str(candidate_path), "manifest_path": "manifest.json"}

            result = DailyDraftRunner(root, Path("config.yaml"), discovery_factory=Discovery).run_once()
            queue = json.loads(Path(result.queue_path).read_text(encoding="utf-8"))

        self.assertEqual(result.state, "awaiting_qualification")
        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(queue["delivery"], "disabled_until_every_hard_gate_is_verified")

    def test_daily_runner_reads_configured_hourly_interval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "daily.yaml"
            config.write_text("continuous_runner:\n  discovery_interval_hours: 18\n", encoding="utf-8")
            self.assertEqual(configured_interval_minutes(config), 1080)

    def test_one_click_delivery_rejects_incomplete_bundle_before_executor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "selection_manifest.json"
            manifest_path.write_text(json.dumps({"paper_id": "p", "mode": "draft_only", "local_artifacts": {}, "links": {}, "selected_figures": []}), encoding="utf-8")
            with self.assertRaises(OneClickEligibilityError):
                QualifiedPaperDraftDelivery(lambda _: self.fail("executor must not run")).deliver(manifest_path)

    def test_one_click_delivery_updates_manifest_from_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf, markdown, draft = root / "p.pdf", root / "p.md", root / "draft.json"
            for path in (pdf, markdown, draft): path.write_text("x", encoding="utf-8")
            figures = [root / f"f{index}.jpg" for index in range(4)]
            for figure in figures: figure.write_bytes(b"x")
            manifest_path = root / "selection_manifest.json"
            manifest_path.write_text(json.dumps({"paper_id": "p", "mode": "draft_only", "local_artifacts": {"pdf": str(pdf), "mineru_markdown": str(markdown), "structured_draft": str(draft)}, "links": {"github": "https://github.com/org/repo"}, "selected_figures": [{"path": str(path)} for path in figures]}), encoding="utf-8")
            receipt = {"draft_id": "draft-1", "state": "saved_draft_only", "pdf_attachment": "p.pdf"}
            (root / "one_click_delivery_receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            executor = lambda command: subprocess.CompletedProcess(command, 0, json.dumps(receipt), "")
            result = QualifiedPaperDraftDelivery(executor).deliver(manifest_path)
            updated = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(result["draft_id"], "draft-1")
        self.assertTrue(updated["pdf_attachment_verified"])

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

    def test_arxiv_source_normalizes_records_and_remembers_seen_ids(self) -> None:
        atom = b'''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
        <entry><id>http://arxiv.org/abs/2608.00001v2</id><title> Agentic Recommenders </title>
        <summary> A verifiable recommender experiment. </summary><published>2026-08-02T00:00:00Z</published>
        <author><name>Ada Lovelace</name></author><category term="cs.IR"/><arxiv:doi>10.1000/example</arxiv:doi></entry></feed>'''

        class Response:
            content = atom

            def raise_for_status(self) -> None:
                return None

        with patch("httpx.get", return_value=Response()) as request:
            source = ArxivSource(max_results=3)
            records, cursor = source.discover({}, {"search_query": 'all:"agentic recommender systems"', "scope": "domain"})
            repeated, _ = source.discover(cursor, {"search_query": 'all:"agentic recommender systems"', "scope": "domain"})

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].identifiers["arxiv"], "2608.00001")
        self.assertEqual(records[0].urls["pdf"], "https://arxiv.org/pdf/2608.00001")
        self.assertEqual(repeated, [])
        self.assertEqual(request.call_args.kwargs["params"]["sortBy"], "submittedDate")

    def test_daily_filter_records_unverified_organization_hints(self) -> None:
        config = DailyDiscoveryConfig(
            companies=("OpenAI",), universities=(), domains=("agentic recommender systems",),
            allowed_venues=("KDD",), allow_verified_preprint=True,
        )
        record = PaperRecord.from_dict({
            "title": "Agentic Recommender Systems", "abstract": "Experiments from OpenAI.",
            "identifiers": {"arxiv": "2608.00001"}, "venue": {"status": "preprint"},
            "published_at": "2026-08-02T00:00:00+00:00",
            "source_records": [{"source_type": "arxiv"}],
            "provenance": {"candidate_scope": "domain", "arxiv_query": 'all:"agentic recommender systems"'},
        })
        filtered = filter_candidates([record], config)
        self.assertEqual(len(filtered), 1)
        evidence = filtered[0].provenance["daily_filter"]
        self.assertIn("agentic recommender systems", evidence["matched_domains"])
        self.assertTrue(evidence["requires_official_github_verification"])

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
