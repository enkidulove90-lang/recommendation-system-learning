from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paper_intake.metadata import ArxivMetadataResolver


ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2606.17628v1</id>
    <published>2026-06-19T12:00:00Z</published>
    <updated>2026-06-20T09:30:00Z</updated>
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


class _FailingTransport:
    def get_text(self, url: str) -> str:
        raise TimeoutError("arXiv API timed out")


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
        self.assertEqual(metadata["updated"], "2026-06-20T09:30:00Z")
        self.assertIn("id_list=2606.17628", transport.calls[0])

    def test_non_arxiv_id_uses_safe_fallback_without_network(self) -> None:
        transport = _Transport(ATOM)
        resolver = ArxivMetadataResolver(transport=transport)

        metadata = resolver("pdf-deadbeef", "https://example.org/paper.pdf")

        self.assertEqual(metadata["title"], "pdf-deadbeef")
        self.assertEqual(metadata["authors"], [])
        self.assertEqual(metadata["paper_url"], "https://example.org/paper.pdf")
        self.assertEqual(transport.calls, [])

    def test_arxiv_timeout_uses_local_authoritative_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "2606.10156" / "arxiv_source"
            source.mkdir(parents=True)
            (source / "main_arxiv.tex").write_text(
                "\\title{$\\tau$-Rec: A Verifiable Benchmark}\\n"
                "\\author{Bharath Sivaram Narasimhan}\\n"
                "\\author{Karthik R Narasimhan}\\n",
                encoding="utf-8",
            )
            resolver = ArxivMetadataResolver(
                transport=_FailingTransport(), local_source_root=root
            )

            metadata = resolver("2606.10156", "https://arxiv.org/abs/2606.10156")

            self.assertEqual(metadata["title"], "τ-Rec: A Verifiable Benchmark")
            self.assertEqual(
                metadata["authors"],
                ["Bharath Sivaram Narasimhan", "Karthik R Narasimhan"],
            )
            self.assertEqual(metadata["metadata_source"], "local_arxiv_source")
            self.assertEqual(metadata["year"], "2026")


if __name__ == "__main__":
    unittest.main()
