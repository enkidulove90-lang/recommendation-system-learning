from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from redbook.automation.feedback import FeedbackStore
from redbook.automation.github_verification import (
    discover_and_verify_official_github,
    normalize_github_repository,
    verify_official_github,
)
from redbook.automation.common import append_jsonl
from redbook.automation.images import build_manifest, compose_group, group_figures, metadata_from_mineru_markdown
from redbook.automation.publishing import FilePublisher, render_package
from redbook.automation.scheduling import PublishScheduler
from redbook.automation.scoring import QualityScorerV2
from redbook.automation.sources import ArxivSource, JsonlSource, PaperRecord, SourceRunner, deduplicate_records
from redbook.automation.daily_discovery import DailyDiscoveryRunner
from redbook.sentinel.paper_pool import PaperPool


class AutomationTests(unittest.TestCase):
    def test_daily_delivery_contract_uses_note_save_and_verify(self) -> None:
        repository = Path(__file__).resolve().parents[2]
        pipeline = (repository / "redbook" / "docs" / "daily-draft-pipeline.md").read_text(encoding="utf-8")
        runner = (repository / "redbook" / "automation" / "daily_runner.py").read_text(encoding="utf-8")
        daily_skill = (repository / "skills" / "xiaohongshu-paper-daily-runner" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (repository / "skills" / "xiaohongshu-paper-daily-runner" / "references" / "workflow.md").read_text(encoding="utf-8")

        self.assertIn("python -m redbook.cli note <slug> --save-draft", pipeline)
        self.assertIn("python -m redbook.cli note <slug> --verify --draft-id <draft-id>", pipeline)
        self.assertNotIn("python -m redbook.cli save-xhs-draft", pipeline)
        self.assertIn("``note <slug> --save-draft``", runner)
        self.assertIn("``note <slug> --verify``", runner)
        self.assertIn("python -m redbook.cli note <slug> --save-draft", daily_skill)
        self.assertIn("python -m redbook.cli note <slug> --verify --draft-id <draft-id>", workflow)
        self.assertNotIn("python -m redbook.cli save-xhs-draft", daily_skill)
        self.assertNotIn("python -m redbook.cli save-xhs-draft", workflow)

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

    def test_daily_discovery_keeps_jsonl_and_writes_qualified_candidates_to_pool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "daily.yaml"
            config.write_text(
                "candidate_domains: [recommender]\n"
                "candidate_organizations: {companies: [], universities: []}\n"
                "venue_gate: {allowed: [SIGIR], allow_verified_preprint: false}\n"
                "discovery: {arxiv_max_results_per_query: 1, max_candidate_age_days: 90}\n",
                encoding="utf-8",
            )
            record = PaperRecord.from_dict({
                "record_id": "arxiv:2601.00001", "title": "A Recommender Paper",
                "identifiers": {"arxiv": "2601.00001"},
                "published_at": datetime.now(timezone.utc).isoformat(),
                "venue": {"name": "SIGIR", "status": "published"},
                "authors": [{"name": "Ada Lovelace"}],
                "urls": {"landing": "https://arxiv.org/abs/2601.00001",
                         "code": "https://github.com/example/recommender"},
                "source_records": [{"source_type": "arxiv"}],
            })

            class Source:
                def __init__(self, name: str, max_results: int) -> None:
                    self.name = name

                def discover(self, cursor, query):
                    return [record], {"seen_ids": ["2601.00001"]}

            pool = PaperPool(root / "state" / "orchestration.sqlite")
            result = DailyDiscoveryRunner(
                root / "data", config, source_factory=Source,
                code_verifier=lambda url: {"state": "verified", "url": url, "detail": "fixture"},
                text_fetcher=lambda url: (
                    "https://github.com/example/recommender"
                    if url.startswith("https://arxiv.org/")
                    else "A Recommender Paper Lovelace"
                ),
            ).run(paper_pool=pool)

            self.assertTrue(Path(result["candidate_path"]).is_file())
            self.assertEqual(result["mode"], "qualified_discovery")
            self.assertEqual(result["candidate_count"], 1)
            self.assertEqual(result["paper_pool"]["added"], 1)
            with pool._connection() as connection:
                row = connection.execute(
                    "SELECT canonical_id, arxiv_id, pending_delivery FROM paper_pool"
                ).fetchone()
            self.assertEqual(tuple(row), ("arxiv:2601.00001", "2601.00001", 1))

    def test_arxiv_source_marks_candidate_as_preprint_and_keeps_query_evidence(self) -> None:
        atom = b'''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
        <entry><id>http://arxiv.org/abs/2608.00001v2</id><title> Agentic Recommenders </title>
        <summary> A verifiable recommender experiment. </summary><published>2026-08-02T00:00:00Z</published>
        <author><name>Ada Lovelace</name></author><category term="cs.IR"/><arxiv:doi>10.1000/example</arxiv:doi></entry></feed>'''

        class Response:
            content = atom

            def raise_for_status(self) -> None:
                return None

        from unittest.mock import patch
        with patch("httpx.get", return_value=Response()):
            records, cursor = ArxivSource(max_results=3).discover(
                {}, {"search_query": 'all:"agentic recommender systems"', "scope": "domain"}
            )

        self.assertEqual(records[0].identifiers["doi"], "10.1000/example")
        self.assertEqual(records[0].venue, {"name": "", "year": "2026", "status": "preprint"})
        self.assertEqual(records[0].topics, ["cs.IR"])
        self.assertEqual(records[0].provenance["candidate_scope"], "domain")
        self.assertEqual(cursor["search_query"], 'all:"agentic recommender systems"')

    def test_official_github_verifier_requires_the_paper_to_name_same_repository(self) -> None:
        record = PaperRecord.from_dict({
            "title": "Thought-Augmented Planning for LLM-Powered Interactive Recommender Agent",
            "authors": [{"name": "Haocheng Yu"}],
            "urls": {"landing": "https://arxiv.org/abs/2506.23485"},
            "source_records": [{"source_type": "arxiv"}],
        })
        pages = {
            "https://arxiv.org/abs/2506.23485": (
                'Code is available at <a href="https://github.com/Alcein/TAIRA" '
                'rel="external noopener">this https URL</a>.'
            ),
            "https://github.com/Alcein/TAIRA": (
                "Thought-Augmented Planning for LLM-Powered Interactive Recommender Agent\n"
                "Haocheng Yu and collaborators"
            ),
        }

        verification = verify_official_github(record, "https://github.com/Alcein/TAIRA/", pages.__getitem__)

        self.assertTrue(verification.verified)
        self.assertEqual(verification.repository_url, "https://github.com/Alcein/TAIRA")
        self.assertTrue(verification.paper_names_repository)
        self.assertTrue(verification.repository_matches_title)
        self.assertTrue(verification.repository_mentions_author)
        self.assertEqual(normalize_github_repository("https://github.com/Alcein/TAIRA/issues/1"), "")

    def test_official_github_verifier_rejects_repository_not_named_by_paper(self) -> None:
        record = PaperRecord.from_dict({
            "title": "A Verifiable Recommendation Paper",
            "authors": [{"name": "Ada Lovelace"}],
            "urls": {"landing": "https://arxiv.org/abs/2601.00001"},
            "source_records": [{"source_type": "arxiv"}],
        })
        pages = {
            "https://arxiv.org/abs/2601.00001": "No implementation link is listed.",
            "https://github.com/example/repo": "A Verifiable Recommendation Paper by Ada Lovelace",
        }

        verification = verify_official_github(record, "https://github.com/example/repo", pages.__getitem__)

        self.assertFalse(verification.verified)
        self.assertFalse(verification.paper_names_repository)

    def test_resource_record_can_discover_and_verify_its_paper_declared_repository(self) -> None:
        record = PaperRecord.from_dict({
            "title": "TAIRA: A Verifiable Recommender",
            "authors": [{"name": "Ada Lovelace"}],
            "urls": {"landing": "https://arxiv.org/abs/2601.00002"},
            "source_records": [{"source_type": "arxiv"}],
        })
        pages = {
            "https://arxiv.org/abs/2601.00002": '<a href="https://github.com/example/taira">code</a>',
            "https://github.com/example/taira": "TAIRA A Verifiable Recommender — Ada Lovelace",
        }

        verification = discover_and_verify_official_github(record, pages.__getitem__)

        self.assertTrue(verification.verified)
        self.assertEqual(record.urls["github"], "https://github.com/example/taira")
        self.assertTrue(record.provenance["official_github_verification"]["verified"])

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
