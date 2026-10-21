from __future__ import annotations

import unittest

from paper_intake.metadata import ArxivMetadataResolver


ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2606.17628v1</id>
    <updated>2026-06-19T12:00:00Z</updated>
    <published>2026-06-19T12:00:00Z</published>
    <title> OPD-Evolver: Cultivating Holistic Agent Evolver via On-Policy Distillation </title>
    <summary> A slow-fast co-evolution framework. </summary>
    <author><name>Guibin Zhang</name></author>
    <author><name>Xun Xu</name></author>
    <link title="pdf" href="https://arxiv.org/pdf/2606.17628v1" />
  </entry>
</feed>
"""


class _Transport:
    def __init__(self, text: str):
        self.text = text
        self.calls = []

    def get_text(self, url: str) -> str:
        self.calls.append(url)
        return self.text


class ArxivMetadataResolverTests(unittest.TestCase):
    def test_resolves_title_authors_and_canonical_links(self) -> None:
        transport = _Transport(ATOM)
        resolver = ArxivMetadataResolver(transport=transport)

        metadata = resolver("2606.17628", "https://arxiv.org/pdf/2606.17628.pdf")

        self.assertEqual(metadata["title"], "OPD-Evolver: Cultivating Holistic Agent Evolver via On-Policy Distillation")
        self.assertEqual(metadata["authors"], ["Guibin Zhang", "Xun Xu"])
        self.assertEqual(metadata["paper_url"], "https://arxiv.org/abs/2606.17628")
        self.assertEqual(metadata["pdf_url"], "https://arxiv.org/pdf/2606.17628.pdf")
        self.assertEqual(metadata["year"], "2026")
        self.assertIn("id_list=2606.17628", transport.calls[0])

    def test_non_arxiv_id_uses_safe_fallback_without_network(self) -> None:
        transport = _Transport(ATOM)
        resolver = ArxivMetadataResolver(transport=transport)

        metadata = resolver("pdf-deadbeef", "https://example.org/paper.pdf")

        self.assertEqual(metadata["title"], "pdf-deadbeef")
        self.assertEqual(metadata["authors"], [])
        self.assertEqual(metadata["paper_url"], "https://example.org/paper.pdf")
        self.assertEqual(transport.calls, [])


if __name__ == "__main__":
    unittest.main()
