from __future__ import annotations

import unittest

from paper_intake.references import VerifiedReferenceResolver, link_reference_titles


ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2305.05065v1</id>
    <title>Recommender Systems with Generative Retrieval</title>
  </entry>
</feed>
"""


class FakeReferenceTransport:
    def __init__(self, *, arxiv_xml: str = "", crossref: dict | None = None, openalex: dict | None = None):
        self.arxiv_xml = arxiv_xml
        self.crossref = crossref
        self.openalex = openalex
        self.calls: list[str] = []

    def get_text(self, url: str) -> str:
        self.calls.append(url)
        if not self.arxiv_xml:
            raise RuntimeError("arxiv unavailable")
        return self.arxiv_xml

    def get_json(self, url: str) -> dict:
        self.calls.append(url)
        if "crossref.org" in url:
            if self.crossref is None:
                raise RuntimeError("crossref unavailable")
            return self.crossref
        if self.openalex is None:
            raise RuntimeError("openalex unavailable")
        return self.openalex


class ReferenceLinkingTests(unittest.TestCase):
    def test_arxiv_identity_is_verified_before_linking(self) -> None:
        source = """## References

[17] Shashank Rajput et al. 2023. Recommender Systems with Generative Retrieval. arXiv preprint arXiv:2305.05065.
"""
        transport = FakeReferenceTransport(arxiv_xml=ARXIV_XML)

        linked = link_reference_titles(
            ["Rajput et al. Recommender Systems with Generative Retrieval."],
            source,
            resolver=VerifiedReferenceResolver(transport=transport),
        )

        self.assertEqual(
            linked,
            ["Rajput et al. [Recommender Systems with Generative Retrieval]"
             "(https://arxiv.org/abs/2305.05065)."],
        )
        self.assertTrue(any("export.arxiv.org/api/query" in call for call in transport.calls))

    def test_doi_is_verified_with_crossref_before_linking(self) -> None:
        source = """## References

[15] Jianmo Ni et al. Sentence-T5: Scalable Sentence Encoders from Pretrained Text-to-Text Models. doi:10.18653/v1/2022.findings-acl.146
"""
        transport = FakeReferenceTransport(
            crossref={
                "status": "ok",
                "message": {
                    "DOI": "10.18653/v1/2022.findings-acl.146",
                    "title": ["Sentence-T5: Scalable Sentence Encoders from Pretrained Text-to-Text Models"],
                    "URL": "https://doi.org/10.18653/v1/2022.findings-acl.146",
                },
            }
        )

        linked = link_reference_titles(
            ["Ni et al. Sentence-T5: Scalable Sentence Encoders from Pretrained Text-to-Text Models."],
            source,
            resolver=VerifiedReferenceResolver(transport=transport),
        )

        self.assertIn("(https://doi.org/10.18653/v1/2022.findings-acl.146)", linked[0])
        self.assertTrue(any("api.crossref.org/works/" in call for call in transport.calls))

    def test_openalex_verifies_a_doi_when_crossref_is_unavailable(self) -> None:
        source = """## References

[3] Example Author. Verified Paper Title. doi:10.5555/example.1
"""
        transport = FakeReferenceTransport(
            openalex={
                "results": [
                    {
                        "doi": "https://doi.org/10.5555/example.1",
                        "title": "Verified Paper Title",
                    }
                ]
            }
        )

        linked = link_reference_titles(
            ["Example Author. Verified Paper Title."],
            source,
            resolver=VerifiedReferenceResolver(transport=transport),
        )

        self.assertIn("(https://doi.org/10.5555/example.1)", linked[0])
        self.assertTrue(any("api.openalex.org/works" in call for call in transport.calls))

    def test_authoritative_title_mismatch_is_unresolved(self) -> None:
        transport = FakeReferenceTransport(
            arxiv_xml=ARXIV_XML.replace(
                "Recommender Systems with Generative Retrieval",
                "A Completely Different Paper",
            )
        )

        linked = link_reference_titles(
            ["Rajput et al. Recommender Systems with Generative Retrieval. arXiv:2305.05065."],
            "## References\n",
            resolver=VerifiedReferenceResolver(transport=transport),
        )

        self.assertIn("（未解析）", linked[0])
        self.assertNotIn("](http", linked[0])

    def test_missing_identity_is_unresolved_without_google_scholar(self) -> None:
        linked = link_reference_titles(
            ["Wang et al. Learnable Item Tokenization for Generative Recommendation."],
            "## References\n",
            resolver=VerifiedReferenceResolver(transport=FakeReferenceTransport()),
        )

        self.assertIn("（未解析）", linked[0])
        self.assertNotIn("scholar.google", linked[0])

    def test_partial_generic_overlap_cannot_steal_an_unrelated_arxiv_id(self) -> None:
        source = """## References

[9] Li et al. UniGRec: Unified Generative Recommendation with Soft Identifiers for End-to-End Optimization. arXiv preprint arXiv:2601.17438.
[13] Liu et al. Generative Recommender with End-to-End Learnable Item Tokenization.
"""

        linked = link_reference_titles(
            ["Zhou et al. ETEGRec: Alternating Optimization for Generative Recommendation."],
            source,
            resolver=VerifiedReferenceResolver(transport=FakeReferenceTransport()),
        )

        self.assertIn("（未解析）", linked[0])
        self.assertNotIn("2601.17438", linked[0])


if __name__ == "__main__":
    unittest.main()
