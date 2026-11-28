from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from paper_intake.fact_pack import FactFormula, parse_fact_pack_response

ROOT = Path(__file__).resolve().parents[1]
ECHO = ROOT / "data/parsed/2026.findings-acl.1001_2026.findings-acl.1001/2026.findings-acl.1001.md"
GLASS = ROOT / "data/parsed/2602.05663_glass/2602.05663.md"


def render(source, formulae=()):
    from paper_intake.notion_compiler import _review_markdown
    return _review_markdown("Title", "https://example.org/paper", "", "paper", {}, {}, [], [],
                            formulae=list(formulae), source_markdown=source)


@pytest.mark.parametrize(("path", "heading"), [
    (ECHO, "3.4 Stage 2: Cycle-Aware Reinforcement Learning"),
    (GLASS, "3 PRELIMINARY"),
])
def test_real_mineru_formula_locates_exact_source_and_is_rendered(path, heading):
    from paper_intake.fact_pack import locate_formula
    if not path.is_file():
        pytest.skip("optional local MinerU source unavailable")
    source = path.read_text(encoding="utf-8")
    start = source.index("## " + heading)
    match = re.search(r"(?m)^\$\$\s*\n(.*?)\n\$\$\s*$", source[start:], re.S)
    assert match is not None
    latex = match.group(1)
    expected = (start + match.start(1), start + match.end(1))
    formula = FactFormula(latex=latex, display_mode="block", source_location=heading + "::1")
    actual = locate_formula(source, formula)
    assert actual == expected, f"actual={actual}, expected={expected}, source={latex!r}"
    output, unplaced = render(source, [formula])
    assert "\n$$\n" + latex + "\n$$\n" in output
    assert not unplaced


def test_inline_and_missing_source_are_handled_without_guessing():
    from paper_intake.fact_pack import locate_formula
    source = "## Method\nBefore $x+1$ after.\n"
    formula = FactFormula(latex="x+1", display_mode="inline", source_location="Method::1")
    bounds = locate_formula(source, formula)
    assert source[slice(*bounds)] == "x+1"
    output, unplaced = render(source, [formula])
    assert "$x+1$" in output and not unplaced
    baseline, _ = render(source)
    for location in ("", "p1", "Method::0", "Method::2", "Method::" + "1" * 5000):
        unknown = formula.model_copy(update={"source_location": location})
        assert locate_formula(source, unknown) is None
        result, unplaced = render(source, [unknown])
        assert result == baseline
        assert len(unplaced) == 1 and unplaced[0]["status"] == "pending_review"


def test_duplicate_headings_and_wrong_formula_do_not_resolve():
    from paper_intake.fact_pack import locate_formula
    formula = FactFormula(latex="x", display_mode="block", source_location="Method::1")
    duplicate = "## Method\n$$\nx\n$$\n## Method\n$$\nx\n$$\n"
    assert locate_formula(duplicate, formula) is None
    result, unplaced = render(duplicate, [formula])
    assert result == render(duplicate)[0] and len(unplaced) == 1
    assert locate_formula("## Method\n$$\ny\n$$\n", formula) is None


def test_formula_delimiters_inside_code_fences_are_not_paper_math():
    from paper_intake.fact_pack import locate_formula
    source = "## Method\n```text\n$$\nwrong\n$$\n$x$\n```\n$$\nright\n$$\n$x$\n"
    block = FactFormula(latex="right", display_mode="block", source_location="Method::1")
    inline = FactFormula(latex="x", display_mode="inline", source_location="Method::1")
    assert source[slice(*locate_formula(source, block))] == "right"
    assert source[slice(*locate_formula(source, inline))] == "x"


def test_empty_formulae_preserves_legacy_markdown_exactly():
    expected = ("# Title\n\n原文或 FactPack 未提供，待核验。\n\n## 研究问题\n\n原文或 FactPack 未提供，待核验。\n\n"
                "## 方法：核心思路与整体框架\n\n原文或 FactPack 未提供，待核验。\n\n## 创新点\n\n原文或 FactPack 未提供，待核验。\n\n"
                "## 实验：数据、基线与结果\n\n### 数据集与设置\n\n原文或 FactPack 未提供，待核验。\n\n"
                "### Benchmark 与结果\n\n原文或 FactPack 未提供，待核验。\n\n### 消融实验\n\n原文或 FactPack 未提供，待核验。\n\n"
                "## 总结\n\n原文或 FactPack 未提供，待核验。\n\n## References\n\n- [论文](https://example.org/paper)\n")
    # Empty homepage summary was omitted by the pre-existing renderer.
    expected = expected.replace("# Title\n\n原文或 FactPack 未提供，待核验。\n\n## 研究问题", "# Title\n\n## 研究问题", 1)
    assert render("# Original\n")[0] == expected


def test_old_formula_without_verification_remains_compatible():
    source = {"facts": {}, "platform_hints": {}, "formulae": [
        {"latex": "x", "display_mode": "block", "source_location": "p1"}]}
    parsed = parse_fact_pack_response(json.dumps(source), "legacy")
    assert FactFormula.model_validate(parsed["formulae"][0]).verification_status == "unverified"


def test_real_legacy_echomllm_fact_pack_remains_readable():
    path = ROOT / "data/summaries/2026.findings-acl.1001_fact_pack.json"
    if not path.is_file():
        pytest.skip("optional legacy EchoMLLM FactPack unavailable")
    parsed = parse_fact_pack_response(path.read_text(encoding="utf-8"), "2026.findings-acl.1001")
    assert parsed["prompt_version"] == "fact-pack-2.1"
    assert not parsed.get("formulae")


def test_compiler_preserves_unplaced_and_injects_located_formula(tmp_path):
    import hashlib
    from PIL import Image
    from paper_intake.models import CompilationInputs
    from paper_intake.notion_compiler import compile_notion_package

    parsed = tmp_path / "parsed"
    parsed.mkdir()
    markdown = parsed / "paper.md"
    source = "## Method\n$$\nx^2\n$$\n"
    markdown.write_text(source, encoding="utf-8")
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-sample")
    figure = parsed / "fig.png"
    Image.new("RGB", (1280, 720)).save(figure)
    manifest = parsed / "manifest.json"
    manifest.write_text(json.dumps({"canonical_id": "arxiv:2401.00001", "figures": [
        {"path": "fig.png", "caption": "Figure", "selected": True}]}), encoding="utf-8")
    fact = tmp_path / "fact.json"
    fact.write_text(json.dumps({"canonical_id": "arxiv:2401.00001", "facts": {}, "platform_hints": {},
        "source_hash": hashlib.sha256(markdown.read_bytes()).hexdigest(), "formulae": [
            {"latex": "x^2", "display_mode": "block", "source_location": "Method::1"},
            {"latex": "y", "display_mode": "inline", "source_location": "p1"}]}), encoding="utf-8")
    inputs = CompilationInputs("arxiv:2401.00001", "arxiv:2401.00001", "job-1", markdown, pdf,
        fact_pack_path=fact, figure_manifest_path=manifest,
        paper_url="https://arxiv.org/abs/2401.00001", pdf_url="https://arxiv.org/pdf/2401.00001")
    package = json.loads(compile_notion_package(inputs, output_dir=tmp_path / "out").path.read_text(encoding="utf-8"))
    assert "\n$$\nx^2\n$$\n" in package["article_input"]["markdown"]
    assert package["unplaced_formulae"][0]["source_location"] == "p1"
    assert package["unplaced_formulae"][0]["status"] == "pending_review"
    assert package["unplaced_formulae"][0]["verification_status"] == "unverified"
    assert package["review_status"] == "pending"


def test_locate_formula_all_conditional_branch_edges():
    import dis
    import sys
    from paper_intake.fact_pack import locate_formula

    if not hasattr(sys, "monitoring"):
        pytest.skip("branch monitoring requires Python 3.12+")
    instructions = list(dis.get_instructions(locate_formula))
    offsets = [item.offset for item in instructions]
    expected, observed = set(), set()
    for index, item in enumerate(instructions[:-1]):
        if not (item.opname.startswith("POP_JUMP") or item.opname == "FOR_ITER"):
            continue
        target = item.argval
        if item.opname == "FOR_ITER" and instructions[offsets.index(target)].opname == "END_FOR":
            pos = offsets.index(target) + 1
            if instructions[pos].opname == "POP_TOP":
                pos += 1
            target = offsets[pos]
        expected.update({(item.offset, target), (item.offset, instructions[index + 1].offset)})
    def hit(code, source, target):
        if code is locate_formula.__code__:
            observed.add((source, target))
    cases = [
        ("", FactFormula()),
        ("## A\n$$\nx\n$$\n", FactFormula(latex="x", display_mode="bad", source_location="A::1")),
        ("## A\n$$\nx\n$$\n", FactFormula(latex="", display_mode="block", source_location="A::1")),
        ("## B\n$$\nx\n$$\n", FactFormula(latex="x", display_mode="block", source_location="A::1")),
        ("## A\n$$\nx\n$$\n## A\n$$\nx\n$$\n", FactFormula(latex="x", display_mode="block", source_location="A::1")),
        ("## A\n### B\n$$\nx\n$$\n## C\n", FactFormula(latex="x", display_mode="block", source_location="A::1")),
        ("## A\n$$\nx\n$$\n", FactFormula(latex="x", display_mode="block", source_location="A::2")),
        ("## A\n$$\ny\n$$\n", FactFormula(latex="x", display_mode="block", source_location="A::1")),
        ("## A\n$$\ny\n$$\n$x$\n", FactFormula(latex="x", display_mode="inline", source_location="A::1")),
        ("## A\n$inside$\n$$\n$blocked$\n$$\n$after$\n", FactFormula(latex="after", display_mode="inline", source_location="A::2")),
    ]
    sys.monitoring.use_tool_id(5, "formula-location-test")
    sys.monitoring.register_callback(5, sys.monitoring.events.BRANCH, hit)
    sys.monitoring.set_local_events(5, locate_formula.__code__, sys.monitoring.events.BRANCH)
    try:
        for source, formula in cases:
            locate_formula(source, formula)
    finally:
        sys.monitoring.set_local_events(5, locate_formula.__code__, 0)
        sys.monitoring.register_callback(5, sys.monitoring.events.BRANCH, None)
        sys.monitoring.free_tool_id(5)
    assert not (expected - observed), f"uncovered edges: {sorted(expected - observed)}"
