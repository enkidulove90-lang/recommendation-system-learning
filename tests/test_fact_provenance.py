"""P1 trusted fact source: per-field provenance and strict core-field gate.

Uses unittest so it runs under the available interpreter (pytest lacks pluggy).
No network: ACL bib and catalog snapshots are injected as plain strings/dicts.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from paper_intake.fact_pack import (  # noqa: E402
    FactField, FactProvenance, FactReference, build_fact_provenance,
    extract_references, stamp_location_verification,
)

REFERENCES_SAMPLE = """## References

Shuai Bai, Keqin Chen, Xuejing Liu, et al. 2025b. Qwen2. 5-vl technical report. arXiv preprint arXiv:2502.13923.

Aysen Degerli, Serkan Kiranyaz, Tahir Hamid, and Moncef Gabbouj. 2024. Early myocardial infarction detection over multi-view echocardiography. Biomedical Signal Processing and Control, 87:105448.

Garrett Duffy, Patrick P. Cheng, Nan Yuan, et al. 2022. High-throughput precision phenotyping of left ven-
tricular hypertrophy with cardiovascular deep learning. JAMA Cardiology, 7(4):386–395.
"""


ACL_BIB = """@inproceedings{huang-etal-2026-echomllm,
    title = "{E}cho{MLLM}: Incentivizing Echocardiographic Video Understanding with Keyframe Grounding and Report Generation",
    author = "Huang, Heyu  and  Sun, Wanran  and  Chen, Chi",
    booktitle = "Findings of the {A}ssociation for {C}omputational {L}inguistics: {ACL} 2026",
    year = "2026",
    address = "San Diego, California, United States",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.findings-acl.1001/",
    doi = "10.18653/v1/2026.findings-acl.1001"
}
"""

PDF_HEADER = (
    "# EchoMLLM: Incentivizing Echocardiographic Video Understanding\n"
    "Heyu Huang<sup>1</sup>, Wanran Sun<sup>3</sup>, Chi Chen<sup>2</sup>\n"
    "<sup>1</sup>Huazhong University of Science and Technology, Wuhan, China\n"
    "<sup>2</sup> Tsinghua University, Beijing, China\n"
)


class FactFieldTest(unittest.TestCase):
    def test_field_carries_source_status_and_evidence(self):
        field = FactField(value="ACL 2026", source="aclanthology.bib",
                          verification_status="verified", evidence="booktitle = ...ACL 2026")
        self.assertEqual(field.value, "ACL 2026")
        self.assertEqual(field.source, "aclanthology.bib")
        self.assertEqual(field.verification_status, "verified")

    def test_unverified_is_default(self):
        field = FactField(value="guess")
        self.assertEqual(field.verification_status, "unverified")


class FactProvenanceBuildTest(unittest.TestCase):
    CORE = ("paper_title", "authors", "venue_name", "year", "identity")

    def test_acl_bib_and_pdf_make_core_fields_verified(self):
        prov = build_fact_provenance(
            acl_bib=ACL_BIB, pdf_markdown=PDF_HEADER, catalog_row={},
            canonical_id="2026.findings-acl.1001")
        self.assertIsInstance(prov, FactProvenance)
        for name in self.CORE:
            field = prov.fields.get(name)
            self.assertIsNotNone(field, name)
            self.assertEqual(field.verification_status, "verified", name)

    def test_authors_are_list_and_from_bib(self):
        prov = build_fact_provenance(
            acl_bib=ACL_BIB, pdf_markdown=PDF_HEADER, catalog_row={},
            canonical_id="2026.findings-acl.1001")
        authors = prov.fields["authors"]
        self.assertIsInstance(authors.value, list)
        self.assertIn("Heyu Huang", authors.value)
        self.assertEqual(authors.source, "aclanthology.bib")

    def test_missing_all_sources_leaves_core_fields_unverified(self):
        prov = build_fact_provenance(
            acl_bib="", pdf_markdown="", catalog_row={}, canonical_id="unknown")
        for name in self.CORE:
            field = prov.fields.get(name)
            self.assertIsNotNone(field, name)
            self.assertNotEqual(field.verification_status, "verified", name)

    def test_catalog_is_used_only_when_no_authoritative_source(self):
        prov = build_fact_provenance(
            acl_bib="", pdf_markdown="",
            catalog_row={"title": "Fallback Title", "publication_year": "2026"},
            canonical_id="2401.00001")
        self.assertEqual(prov.fields["paper_title"].source, "catalog")
        self.assertEqual(prov.fields["paper_title"].verification_status, "verified")

    def test_core_status_reports_missing_names(self):
        prov = build_fact_provenance(
            acl_bib="", pdf_markdown="", catalog_row={}, canonical_id="unknown")
        missing = prov.unverified_core(self.CORE)
        self.assertEqual(set(missing), set(self.CORE))


class ExtractReferencesTest(unittest.TestCase):
    def test_arxiv_id_becomes_verified_real_url(self):
        refs = extract_references(REFERENCES_SAMPLE)
        qwen = next(r for r in refs if "Qwen2" in r.title)
        self.assertEqual(qwen.paper_url, "https://arxiv.org/abs/2502.13923")
        self.assertEqual(qwen.source, "pdf_original")
        self.assertEqual(qwen.verification_status, "verified")
        self.assertIn("arXiv:2502.13923", qwen.evidence)

    def test_reference_without_link_is_unverified_and_not_guessed(self):
        refs = extract_references(REFERENCES_SAMPLE)
        deg = next(r for r in refs if "myocardial" in r.title)
        self.assertEqual(deg.paper_url, "")
        self.assertEqual(deg.verification_status, "unverified")

    def test_hyphenated_line_break_is_joined(self):
        refs = extract_references(REFERENCES_SAMPLE)
        duffy = next(r for r in refs if "phenotyping" in r.title)
        self.assertIn("ventricular", duffy.title)
        self.assertNotIn("ven-\n", duffy.title)

    def test_no_code_url_when_source_has_none(self):
        refs = extract_references(REFERENCES_SAMPLE)
        self.assertTrue(refs)
        self.assertTrue(all(not r.code_url for r in refs))

    def test_empty_and_no_references_section(self):
        self.assertEqual(extract_references(""), [])
        self.assertEqual(extract_references("# Title\n\nbody text"), [])


PDF_HEADER = """# Paper Title

<sup>1</sup>Wuhan University, Wuhan, China

<sup>2</sup>Beijing Academy, Beijing, China

## 1 Introduction

body
"""


class LocationProvenanceTest(unittest.TestCase):
    """The map needs a city; only the affiliation header may back one."""

    def test_location_is_derived_from_the_pdf_header(self):
        provenance = build_fact_provenance(pdf_markdown=PDF_HEADER)
        field = provenance.fields["location"]
        self.assertEqual(field.verification_status, "verified")
        self.assertEqual(field.source, "pdf_original")
        self.assertEqual(field.value["affil_city"], ["Wuhan", "Beijing"])
        self.assertEqual(field.value["corresponding_city"], "Wuhan")
        self.assertEqual(field.value["affiliation_name"], "Wuhan University；Beijing Academy")

    def test_location_stays_unverified_without_a_header(self):
        provenance = build_fact_provenance(pdf_markdown="# Title\n\nbody without header")
        field = provenance.fields["location"]
        self.assertEqual(field.verification_status, "unverified")
        self.assertIsNone(field.value)

    def test_stamp_marks_a_header_city_as_verified(self):
        pack = {"location": {"location_type": "affiliation", "affil_city": ["Wuhan"],
                             "venue_city": "", "corresponding_city": "Wuhan",
                             "affiliation_name": "Wuhan University"}}
        stamped = stamp_location_verification(pack, pdf_markdown=PDF_HEADER)
        self.assertEqual(stamped["location"]["verification_status"], "verified")
        self.assertEqual(stamped["location"]["source"], "pdf_original")

    def test_stamp_downgrades_a_city_the_header_never_mentions_to_inferred(self):
        # A model-derived city is publishable but must never masquerade as
        # header-verified: the site labels it as inference.
        pack = {"location": {"affil_city": ["Springfield"],
                             "corresponding_city": "Springfield"}}
        stamped = stamp_location_verification(pack, pdf_markdown=PDF_HEADER)
        self.assertEqual(stamped["location"]["verification_status"], "inferred")
        self.assertEqual(stamped["location"]["source"], "model_inference")

    def test_stamp_leaves_a_cityless_location_unverified(self):
        pack = {"location": {"affiliation_name": "Some University", "affil_city": []}}
        stamped = stamp_location_verification(pack, pdf_markdown="# Title\n\nno header")
        self.assertEqual(stamped["location"]["verification_status"], "unverified")

    def test_stamp_fills_a_missing_location_from_the_header(self):
        stamped = stamp_location_verification({}, pdf_markdown=PDF_HEADER)
        self.assertEqual(stamped["location"]["affil_city"], ["Wuhan", "Beijing"])
        self.assertEqual(stamped["location"]["verification_status"], "verified")


if __name__ == "__main__":
    unittest.main()
