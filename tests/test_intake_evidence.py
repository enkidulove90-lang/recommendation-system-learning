from __future__ import annotations

import hashlib

import pytest

from paper_intake.evidence import (
    ContentIntegrityError,
    build_fact_pack,
    ensure_clean_text,
)


def test_replacement_character_is_rejected_with_stage() -> None:
    with pytest.raises(ContentIntegrityError, match="mineru_output"):
        ensure_clean_text("broken \ufffd text", stage="mineru_output")


def test_fact_pack_has_stable_sources_numbers_figures_and_anchors() -> None:
    markdown = """# Method

The model improves NDCG@20 by 2.12% on Amazon Baby.

![Figure 3: unified optical encoder](images/figure-3.png)
"""
    digest = hashlib.sha256(b"figure").hexdigest()

    pack = build_fact_pack(
        markdown=markdown,
        metadata={
            "canonical_id": "2610.05432",
            "title": "OpticalRec",
            "paper_url": "https://arxiv.org/abs/2610.05432",
        },
        figures=[{"path": "images/figure-3.png", "sha256": digest}],
    )

    assert pack.metadata["title"] == "OpticalRec"
    assert pack.metadata_source == "authoritative_metadata"
    assert any(fact.value == "2.12%" and fact.source_id.startswith("mineru:") for fact in pack.key_numbers)
    assert pack.figures[0].figure_label == "Figure 3"
    assert pack.figures[0].original_caption == "Figure 3: unified optical encoder"
    assert pack.figures[0].sha256 == digest
    assert "method.overview" in pack.anchor_ids
    assert pack.evidence_blocks[0].source_id.startswith("mineru:")

