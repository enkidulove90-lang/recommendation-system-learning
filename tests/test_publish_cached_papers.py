from __future__ import annotations

from pathlib import Path

from paper_intake.article import PaperArticle, validate_article
from scripts.publish_cached_papers import TAU_BUNDLE, TAU_SOURCE, repair_tau_article


def test_tau_repair_links_references_removes_small_images_and_normalizes_math() -> None:
    article = PaperArticle.model_validate_json((TAU_BUNDLE / "article.json").read_text(encoding="utf-8"))

    repaired = repair_tau_article(
        article,
        TAU_SOURCE.read_text(encoding="utf-8"),
        TAU_BUNDLE,
    )
    result = validate_article(repaired, artifact_root=TAU_BUNDLE)
    serialized = repaired.model_dump_json()

    assert result.publishable, result.issue_codes
    assert len(repaired.figures) == 4
    assert len(repaired.article.references) == 26
    assert all("](" in reference for reference in repaired.article.references)
    assert r"\passhat" not in serialized
    assert r"\mathrm{pass}" in serialized
    assert r"\texttt" not in serialized
