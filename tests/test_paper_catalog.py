from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from paper_intake.catalog import (
    CatalogCache,
    PaperCatalog,
    parse_acl_event,
    parse_arxiv_feed,
    parse_recsys_program_page,
)


ARXIV_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>https://arxiv.org/abs/2606.17628v2</id>
    <published>2026-06-19T12:00:00Z</published>
    <updated>2026-06-20T09:30:00Z</updated>
    <title>OPD-Evolver: Cultivating Holistic Agent Evolver</title>
    <author><name>Guibin Zhang</name></author>
    <category term="cs.AI" />
    <category term="cs.LG" />
    <arxiv:primary_category term="cs.AI" />
    <arxiv:journal_ref>arXiv preprint</arxiv:journal_ref>
    <link rel="alternate" href="https://arxiv.org/abs/2606.17628v2" />
  </entry>
</feed>
"""


ACL_EVENT = """
<main>
  <h2>Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics</h2>
  <h3>bib (full) Volume 1: Long Papers</h3>
  <p><a href="/2026.acl-long.1/">A Traceable ACL Paper</a></p>
  <h3>Volume 2: Short Papers</h3>
  <p><a href="/2026.acl-short.7/">A Short ACL Paper</a></p>
</main>
"""


RECSYS_PAGE = """
<main>
  <h1>Session 1</h1>
  <h3>1A: Semantic IDs &amp; Generative Interfaces</h3>
  <ul>
    <li><strong>RES Beyond Fixed Depths and Widths by Jingzhe Liu and Hanbing Wang</strong></li>
    <li><a href="https://doi.org/10.1145/example">IND Production Recommendation at Scale</a><br/>by Ada Lovelace</li>
  </ul>
</main>
"""


class PaperCatalogParsingTests(unittest.TestCase):
    def test_arxiv_exposes_categories_as_topics_and_keeps_preprint_type(self) -> None:
        records = parse_arxiv_feed(ARXIV_FEED)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.publication_year, 2026)
        self.assertEqual(record.venue_type, "preprint")
        self.assertEqual(record.venue_name, "arXiv")
        self.assertEqual(record.topics, ["cs.AI", "cs.LG"])
        self.assertEqual(record.topic_source, "arxiv_category")
        self.assertEqual(record.arxiv_id, "2606.17628")
        self.assertEqual(record.paper_url, "https://arxiv.org/abs/2606.17628")

    def test_acl_event_uses_volume_as_track_not_semantic_topic(self) -> None:
        records = parse_acl_event(
            ACL_EVENT,
            event_url="https://aclanthology.org/events/acl-2026/",
            venue_name="ACL 2026",
        )

        self.assertEqual([item.title for item in records], ["A Traceable ACL Paper", "A Short ACL Paper"])
        self.assertEqual(records[0].track, "Volume 1: Long Papers")
        self.assertEqual(records[0].topics, ["Volume 1: Long Papers"])
        self.assertEqual(records[0].topic_source, "conference_track")
        self.assertEqual(records[0].paper_url, "https://aclanthology.org/2026.acl-long.1/")

    def test_recsys_session_heading_is_topic_and_prefix_is_track(self) -> None:
        records = parse_recsys_program_page(
            RECSYS_PAGE,
            page_url="https://recsys.acm.org/recsys26/session-1/",
            publication_year=2026,
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].title, "Beyond Fixed Depths and Widths")
        self.assertEqual(records[0].track, "research")
        self.assertEqual(records[0].topics, ["Semantic IDs & Generative Interfaces"])
        self.assertEqual(records[0].paper_url, "https://recsys.acm.org/recsys26/session-1/")
        self.assertEqual(records[1].track, "industry")
        self.assertEqual(records[1].doi, "10.1145/example")

    def test_catalog_deduplicates_by_normalized_title_and_writes_atomic_json(self) -> None:
        arxiv = parse_arxiv_feed(ARXIV_FEED)[0]
        duplicate = parse_arxiv_feed(ARXIV_FEED.replace("v2", "v3"))[0]
        catalog = PaperCatalog([arxiv, duplicate])

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "paper_catalog.json"
            catalog.write_json(output, refresh_interval_seconds=1800)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["refresh_interval_seconds"], 1800)
        self.assertEqual(payload["paper_count"], 1)
        self.assertEqual(payload["papers"][0]["publication_year"], 2026)
        self.assertEqual(payload["papers"][0]["title"], "OPD-Evolver: Cultivating Holistic Agent Evolver")

    def test_expired_cache_falls_back_to_stale_copy_when_provider_fails(self) -> None:
        class FailingTransport:
            def get_text(self, url: str) -> str:
                raise TimeoutError(url)

        with tempfile.TemporaryDirectory() as temporary:
            cache = CatalogCache(Path(temporary))
            cache.store("arxiv:test", "cached-feed")

            text = cache.get_text(
                FailingTransport(),
                "https://example.invalid/feed",
                key="arxiv:test",
                ttl_seconds=0,
            )

        self.assertEqual(text, "cached-feed")


if __name__ == "__main__":
    unittest.main()
