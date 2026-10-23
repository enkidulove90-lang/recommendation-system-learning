from __future__ import annotations

import unittest

from paper_intake.references import link_reference_titles


class ReferenceLinkingTests(unittest.TestCase):
    def test_arxiv_identity_from_source_becomes_a_direct_title_link(self) -> None:
        source = """## References

[17] Shashank Rajput et al. 2023. Recommender Systems with Generative Retrieval. arXiv preprint arXiv:2305.05065.
"""

        linked = link_reference_titles(
            ["Rajput et al. Recommender Systems with Generative Retrieval (TIGER)."],
            source,
        )

        self.assertEqual(
            linked,
            [
                "Rajput et al. [Recommender Systems with Generative Retrieval (TIGER)]"
                "(https://arxiv.org/abs/2305.05065)."
            ],
        )

    def test_doi_from_source_becomes_a_direct_title_link(self) -> None:
        source = """## References

[15] Jianmo Ni et al. 2022. Sentence-T5: Scalable Sentence Encoders from Pretrained Text-to-Text Models. doi:10.18653/v1/2022.findings-acl.146
"""

        linked = link_reference_titles(
            ["Ni et al. Sentence-T5: Scalable Sentence Encoders from Pre-trained Text-to-Text Models."],
            source,
        )

        self.assertIn("(https://doi.org/10.18653/v1/2022.findings-acl.146)", linked[0])

    def test_unresolved_reference_gets_a_deterministic_scholar_lookup(self) -> None:
        linked = link_reference_titles(
            ["Wang et al. Learnable Item Tokenization for Generative Recommendation."],
            "## References\n",
        )

        self.assertIn("https://scholar.google.com/scholar?q=", linked[0])
        self.assertIn("[Learnable Item Tokenization for Generative Recommendation]", linked[0])

    def test_partial_generic_overlap_cannot_steal_an_unrelated_arxiv_id(self) -> None:
        source = """## References

[9] Li et al. UniGRec: Unified Generative Recommendation with Soft Identifiers for End-to-End Optimization. arXiv preprint arXiv:2601.17438.
[13] Liu et al. Generative Recommender with End-to-End Learnable Item Tokenization.
"""

        linked = link_reference_titles(
            ["Zhou et al. ETEGRec: Alternating Optimization for Generative Recommendation."],
            source,
        )

        self.assertIn("https://scholar.google.com/scholar?q=", linked[0])
        self.assertNotIn("2601.17438", linked[0])

    def test_existing_markdown_link_is_preserved(self) -> None:
        reference = "[Paper](https://arxiv.org/abs/2608.17316)"

        self.assertEqual(link_reference_titles([reference], ""), [reference])


if __name__ == "__main__":
    unittest.main()
