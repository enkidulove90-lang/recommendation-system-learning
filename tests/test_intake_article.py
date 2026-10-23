from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pydantic import ValidationError

from paper_intake.article import (
    ArticlePayloadError,
    PaperArticle,
    normalize_classification,
    parse_article_payload,
    render_article_markdown,
    validate_article,
)


def _payload(figure_path: str = "images/figure-1.png", figure_sha256: str = "") -> dict:
    return {
        "schema_version": 1,
        "paper": {
            "canonical_id": "2608.17316",
            "title": "A Reliable Recommendation Model",
            "chinese_title": "可靠推荐模型",
            "authors": ["Alice", "Bob"],
            "paper_url": "https://arxiv.org/abs/2608.17316",
            "code_url": "https://github.com/example/reliable-rec",
        },
        "classification": {
            "categories": ["推荐系统", "多模态推荐"],
            "tags": ["论文速读", "多模态推荐"],
            "year": "2025",
            "venue_type": "arXiv预印本",
            "venue_name": "arXiv",
        },
        "article": {
            "introduction": "这篇论文研究多模态推荐中的噪声传播问题，并说明了现有融合方法的限制。",
            "method": "作者提出可靠性估计与门控融合模块，使不同模态按照样本质量动态参与表示学习。",
            "experiments": "论文在三个公开数据集上比较多种基线，并通过消融实验验证两个核心模块。",
            "conclusion": "该方法把模态可靠性显式纳入推荐流程，在准确率与鲁棒性之间取得稳定平衡。",
            "references": [
                "[A Reliable Recommendation Model](https://arxiv.org/abs/2608.17316)",
                "[Official implementation](https://github.com/example/reliable-rec)",
            ],
        },
        "figures": [
            {
                "path": figure_path,
                "sha256": figure_sha256,
                "section": "method",
                "explanation": "这张结构图展示了可靠性估计如何控制各模态进入融合层的权重，从而降低噪声模态对用户表示的干扰。",
            }
        ],
    }


class PaperArticleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        image = self.root / "images" / "figure-1.png"
        image.parent.mkdir(parents=True)
        image.write_bytes(b"real-paper-figure")
        self.figure_sha256 = hashlib.sha256(image.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def valid_article(self) -> PaperArticle:
        return PaperArticle.model_validate(_payload(figure_sha256=self.figure_sha256))

    def test_article_without_renderable_figure_is_blocked(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["figures"] = []
        article = PaperArticle.model_validate(payload)

        result = validate_article(article, artifact_root=self.root)

        self.assertFalse(result.publishable)
        self.assertIn("figure_required", result.issue_codes)

    def test_missing_or_empty_required_section_is_blocked(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["article"]["experiments"] = ""

        result = validate_article(PaperArticle.model_validate(payload), artifact_root=self.root)

        self.assertFalse(result.publishable)
        self.assertIn("experiments_required", result.issue_codes)

    def test_missing_or_hash_mismatched_figure_is_blocked(self) -> None:
        missing = PaperArticle.model_validate(
            _payload(figure_path="images/missing.png", figure_sha256="abc")
        )
        mismatch = PaperArticle.model_validate(_payload(figure_sha256="abc"))

        missing_result = validate_article(missing, artifact_root=self.root)
        mismatch_result = validate_article(mismatch, artifact_root=self.root)

        self.assertIn("figure_missing", missing_result.issue_codes)
        self.assertIn("figure_hash_mismatch", mismatch_result.issue_codes)

    def test_english_only_or_one_line_figure_explanation_is_blocked(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["figures"][0]["explanation"] = "Model overview."
        article = PaperArticle.model_validate(payload)

        result = validate_article(article, artifact_root=self.root)

        self.assertFalse(result.publishable)
        self.assertIn("figure_explanation_invalid", result.issue_codes)

    def test_formula_crop_cannot_satisfy_the_paper_figure_gate(self) -> None:
        image = self.root / "images" / "formula-crop.png"
        Image.new("RGB", (223, 31), "white").save(image)
        payload = _payload(
            figure_path="images/formula-crop.png",
            figure_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
        )

        result = validate_article(PaperArticle.model_validate(payload), artifact_root=self.root)

        self.assertFalse(result.publishable)
        self.assertIn("figure_too_small", result.issue_codes)

    def test_reference_without_clickable_title_is_blocked(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["article"]["references"] = ["Rajput et al. Recommender Systems with Generative Retrieval."]

        result = validate_article(PaperArticle.model_validate(payload), artifact_root=self.root)

        self.assertFalse(result.publishable)
        self.assertIn("reference_link_missing", result.issue_codes)

    def test_replacement_character_in_generated_article_is_blocked(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["paper"]["title"] = "�-Rec"
        payload["article"]["method"] = "方法正文包含损坏字符 �。"

        result = validate_article(PaperArticle.model_validate(payload), artifact_root=self.root)

        self.assertFalse(result.publishable)
        self.assertIn("replacement_character_forbidden", result.issue_codes)

    def test_unknown_category_falls_back_to_controlled_taxonomy(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["classification"]["categories"] = ["模型自己发明的分类"]
        article = PaperArticle.model_validate(payload)

        normalized, warnings = normalize_classification(article.classification)

        self.assertEqual(normalized.categories, ["推荐系统", "论文速递"])
        self.assertIn("classification_fallback", warnings)

    def test_verified_conference_name_overrides_inconsistent_preprint_alias(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        payload["classification"]["venue_type"] = "arxiv预印本"
        payload["classification"]["venue_name"] = "WWW'26 (The ACM Web Conference 2026)"
        article = PaperArticle.model_validate(payload)

        normalized, warnings = normalize_classification(article.classification)

        self.assertEqual(normalized.venue_type, "会议")
        self.assertIn("venue_type_corrected_from_venue", warnings)

    def test_markdown_has_stable_frontmatter_sections_links_and_figure(self) -> None:
        markdown = render_article_markdown(self.valid_article())

        self.assertIn("title: 可靠推荐模型", markdown)
        self.assertIn("year: 2025", markdown)
        self.assertIn("categories: [推荐系统, 多模态推荐]", markdown)
        self.assertIn("## 一、研究背景与问题", markdown)
        self.assertIn("## 二、方法", markdown)
        self.assertIn("![方法图 1](/images/papers/2608.17316/figure-1.png)", markdown)
        self.assertIn("## 三、实验", markdown)
        self.assertIn("## 四、总结", markdown)
        self.assertIn("## References", markdown)
        self.assertIn("[论文链接](https://arxiv.org/abs/2608.17316)", markdown)
        self.assertIn("[代码链接](https://github.com/example/reliable-rec)", markdown)

    def test_fenced_json_payload_is_parsed(self) -> None:
        raw = "```json\n" + json.dumps(_payload(figure_sha256=self.figure_sha256), ensure_ascii=False) + "\n```"

        article = parse_article_payload(raw)

        self.assertEqual(article.paper.canonical_id, "2608.17316")
        self.assertEqual(article.schema_version, 1)

    def test_invalid_json_is_not_silently_converted_to_article(self) -> None:
        with self.assertRaises((ValueError, ValidationError)):
            parse_article_payload("not json")

    def test_payload_repairs_wrapped_json_and_trailing_commas(self) -> None:
        raw = "Model output:\n" + json.dumps(
            _payload(figure_sha256=self.figure_sha256), ensure_ascii=False
        )
        raw = raw.replace("}]}", "},],}") + "\nDone"

        article = parse_article_payload(raw)

        self.assertEqual(article.paper.canonical_id, "2608.17316")

    def test_payload_reports_full_schema_locations_without_input(self) -> None:
        payload = _payload(figure_sha256=self.figure_sha256)
        del payload["paper"]["title"]
        payload["figures"][0]["section"] = "unknown"

        with self.assertRaises(ArticlePayloadError) as caught:
            parse_article_payload(json.dumps(payload, ensure_ascii=False))

        details = caught.exception.details
        self.assertEqual([item["loc"] for item in details], ["paper.title", "figures.0.section"])
        self.assertTrue(all("input" not in item for item in details))


if __name__ == "__main__":
    unittest.main()
