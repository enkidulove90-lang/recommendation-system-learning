from __future__ import annotations

from paper_intake.article import (
    render_article_markdown,
    render_related_reading,
    replace_related_reading,
)
from paper_intake.reference_candidates import ReferenceCandidate
from paper_intake.reference_links import ResolvedReference, ResolutionResult
from tests.test_generation_cache import _article


def _resolved(
    ref_id: str,
    *,
    title: str,
    year: int,
    paper_url: str,
    code_url: str | None,
    reason: str | None,
) -> ResolvedReference:
    return ResolvedReference(
        candidate=ReferenceCandidate(
            ref_id=ref_id,
            raw_text=title,
            title=title,
            year=year,
            arxiv_id=paper_url.rsplit("/", 1)[-1] if "arxiv.org" in paper_url else None,
            doi=None,
            original_index=int(ref_id.rsplit("_", 1)[-1]),
        ),
        paper_url=paper_url,
        code_url=code_url,
        link_source="arxiv",
        verification_status="verified",
        reason=reason,
    )


def test_recommended_block_is_last_and_contains_one_marker_pair() -> None:
    result = ResolutionResult(
        mode="recommended",
        references=[
            _resolved(
                "ref_001",
                title="First paper",
                year=2025,
                paper_url="https://arxiv.org/abs/2511.21631",
                code_url="https://github.com/example/first",
                reason="与核心视觉语言表示直接相关。",
            ),
            _resolved(
                "ref_002",
                title="Second paper",
                year=2026,
                paper_url="https://arxiv.org/abs/2604.20937",
                code_url=None,
                reason="提供最新的模型剪枝视角。",
            ),
        ],
    )

    markdown = render_article_markdown(_article(), result)

    assert markdown.count("<!-- related-reading:start -->") == 1
    assert markdown.count("<!-- related-reading:end -->") == 1
    assert "## 延伸阅读" in markdown
    assert "## 补充阅读" not in markdown
    assert "[代码链接](https://github.com/example/first)" in markdown
    second_section = markdown.split("### 2. Second paper", 1)[1]
    assert "代码链接" not in second_section
    assert markdown.rstrip().endswith("<!-- related-reading:end -->")


def test_supplemental_block_omits_fake_reason_for_fallback_item() -> None:
    result = ResolutionResult(
        mode="supplemental",
        references=[
            _resolved(
                "ref_003",
                title="Latest fallback",
                year=2026,
                paper_url="https://arxiv.org/abs/2604.20937",
                code_url=None,
                reason=None,
            )
        ],
    )

    block = render_related_reading(result)

    assert "## 补充阅读" in block
    assert "## 延伸阅读" not in block
    assert "推荐理由" not in block
    assert "相关" not in block


def test_replacing_generated_block_twice_is_byte_idempotent() -> None:
    result = ResolutionResult(
        mode="supplemental",
        references=[
            _resolved(
                "ref_003",
                title="Latest fallback",
                year=2026,
                paper_url="https://arxiv.org/abs/2604.20937",
                code_url=None,
                reason=None,
            )
        ],
    )
    original = "# Article\n\n## References\n\n- Author reference\n"
    block = render_related_reading(result)

    first = replace_related_reading(original, block)
    second = replace_related_reading(first, block)

    assert first == second
    assert second.count("<!-- related-reading:start -->") == 1
    assert "- Author reference" in second


def test_omitted_result_removes_only_generated_block() -> None:
    original = (
        "# Article\n\n## References\n\n- Author reference\n\n"
        "<!-- related-reading:start -->\n## 补充阅读\nold\n"
        "<!-- related-reading:end -->\n"
    )

    cleaned = replace_related_reading(
        original, render_related_reading(ResolutionResult(mode="omitted", references=[]))
    )

    assert "related-reading" not in cleaned
    assert "## References" in cleaned
    assert "- Author reference" in cleaned
