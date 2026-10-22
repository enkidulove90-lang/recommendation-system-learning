from __future__ import annotations

from pathlib import Path

from paper_intake.article import PaperArticle, ReferenceChoice
from paper_intake.generation_cache import GenerationCache


def _article() -> PaperArticle:
    return PaperArticle.model_validate(
        {
            "schema_version": 1,
            "paper": {
                "canonical_id": "2610.05432",
                "title": "OpticalRec",
                "chinese_title": "OpticalRec",
                "authors": ["Alice"],
                "paper_url": "https://arxiv.org/abs/2610.05432",
                "code_url": "",
            },
            "classification": {
                "categories": ["推荐系统", "多模态推荐"],
                "tags": ["论文速读"],
                "year": "2026",
                "venue_type": "arXiv预印本",
                "venue_name": "arXiv",
            },
            "article": {
                "introduction": "背景",
                "method": "方法",
                "experiments": "实验",
                "conclusion": "结论",
                "references": [],
            },
            "figures": [],
        }
    )


def test_article_cache_hits_identical_dimensions_and_invalidates_each_dimension(
    tmp_path: Path,
) -> None:
    cache = GenerationCache(tmp_path)
    article = _article()
    calls = 0

    def load_or_generate(source: str, model: str, prompt: str) -> PaperArticle:
        nonlocal calls
        cached = cache.get_article(source, model, prompt)
        if cached is not None:
            return cached
        calls += 1
        cache.put_article(source, model, prompt, article)
        return article

    assert load_or_generate("source-a", "deepseek-chat", "article-v1") == article
    assert load_or_generate("source-a", "deepseek-chat", "article-v1") == article
    assert calls == 1
    load_or_generate("source-b", "deepseek-chat", "article-v1")
    load_or_generate("source-a", "deepseek-reasoner", "article-v1")
    load_or_generate("source-a", "deepseek-chat", "article-v2")
    assert calls == 4


def test_ranking_cache_is_separate_and_uses_all_ranking_dimensions(tmp_path: Path) -> None:
    cache = GenerationCache(tmp_path)
    choices = [
        ReferenceChoice(ref_id="ref_001", reason="最相关"),
        ReferenceChoice(ref_id="ref_002", reason="最新"),
    ]
    cache.put_ranking(
        "source-a", "candidates-a", "deepseek-chat", "article-v1", "ranking-v1", choices
    )

    assert cache.get_ranking(
        "source-a", "candidates-a", "deepseek-chat", "article-v1", "ranking-v1"
    ) == choices
    assert cache.get_article("source-a", "deepseek-chat", "article-v1") is None
    assert (
        cache.get_ranking(
            "source-a", "candidates-b", "deepseek-chat", "article-v1", "ranking-v1"
        )
        is None
    )
    assert (
        cache.get_ranking(
            "source-a", "candidates-a", "deepseek-chat", "article-v1", "ranking-v2"
        )
        is None
    )
