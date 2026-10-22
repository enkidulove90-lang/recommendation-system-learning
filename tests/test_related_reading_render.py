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
            original_index=int(ref_id.rsplit("_", 1)[-1]) - 1,
        ),
        paper_url=paper_url,
        code_url=code_url,
        link_source="arxiv",
        verification_status="verified",
        reason=reason,
    )


def test_selected_links_are_appended_to_their_existing_reference_entries() -> None:
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

    article = _article()
    article.article.references = ["First paper citation", "Second paper citation"]
    markdown = render_article_markdown(article, result)

    assert "补充阅读" not in markdown
    assert "延伸阅读" not in markdown
    references = markdown.split("## References", 1)[1]
    first_line = references.splitlines()[2]
    second_line = references.splitlines()[3]
    assert first_line.endswith(
        "[论文链接](https://arxiv.org/abs/2511.21631) · "
        "[代码链接](https://github.com/example/first)"
    )
    assert second_line.endswith("[论文链接](https://arxiv.org/abs/2604.20937)")
    assert "代码链接" not in second_line


def test_supplemental_selection_does_not_create_a_separate_section() -> None:
    result = ResolutionResult(
        mode="supplemental",
        references=[
            _resolved(
                "ref_001",
                title="Latest fallback",
                year=2026,
                paper_url="https://arxiv.org/abs/2604.20937",
                code_url=None,
                reason=None,
            )
        ],
    )

    article = _article()
    article.article.references = ["Latest fallback citation"]
    markdown = render_article_markdown(article, result)

    assert "## 补充阅读" not in markdown
    assert "## 延伸阅读" not in markdown
    assert "推荐理由" not in markdown
    assert "[论文链接](https://arxiv.org/abs/2604.20937)" in markdown


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
