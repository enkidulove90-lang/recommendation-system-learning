from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image

BLOG_TOOLS = Path("D:/enkidulove90-lang.github.io/tools")
sys.path.insert(0, str(BLOG_TOOLS))


@pytest.mark.parametrize(("fields", "kind", "canonical"), [
    ({"arxiv_id": "2401.00001"}, "arxiv", "2401.00001"),
    ({"arxiv_id": "arXiv:2401.00001"}, "arxiv", "2401.00001"),
    ({"paper_url": "https://arxiv.org/abs/2401.00001v2"}, "arxiv", "2401.00001"),
    ({"arxiv_id": "hep-th/9701001"}, "arxiv", "hep-th/9701001"),
    ({"doi": "10.18653/v1/2026.findings-acl.1001"}, "acl_doi", "10.18653/v1/2026.findings-acl.1001"),
    ({"paper_url": "https://doi.org/10.18653/v1/2026.findings-acl.1001"}, "acl_doi", "10.18653/v1/2026.findings-acl.1001"),
    ({"paper_url": "https://aclanthology.org/2026.findings-acl.1001/"}, "acl_doi", "10.18653/v1/2026.findings-acl.1001"),
    ({"arxiv_id": "2401.00001", "doi": "10.18653/v1/2026.findings-acl.1001"}, "both", "2401.00001"),
    ({"doi": "10.18653/fake"}, "none", ""),
    ({"paper_url": "https://evil.example/10.18653/v1/2026.findings-acl.1001"}, "none", ""),
    ({}, "none", ""),
])
def test_detect_identity_validates_identifier_forms(fields, kind, canonical):
    from paper_identity import detectIdentity
    assert detectIdentity(fields) == {"type": kind, "canonicalId": canonical}


@pytest.mark.parametrize(("arxiv_id", "doi", "expected_error"), [
    ("2401.00001", "", False),
    ("", "10.18653/v1/2026.findings-acl.1001", False),
    ("2401.00001", "10.18653/v1/2026.findings-acl.1001", False),
    ("", "10.18653/fake", True),
])
def test_validator_blocks_only_unrecognized_identity(tmp_path, arxiv_id, doi, expected_error):
    from paper_identity import detectIdentity, identityStatus
    from paper_article import ArticleDraft, REQUIRED_SECTIONS, validate_article
    from mineru_adapter import FigureAsset

    image = tmp_path / "figure.png"
    Image.new("RGB", (1280, 720)).save(image)
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-sample")
    draft = ArticleDraft(arxiv_id=arxiv_id, doi=doi, title="Paper", slug="paper",
        markdown="\n".join(REQUIRED_SECTIONS) + "\n图示解释：架构图。",
        source_text="", source_pdf=pdf, figures=[FigureAsset(path=image, caption="Figure",
        dimensions=(1280, 720), is_hd=True, provenance="fixture")])
    errors = validate_article(draft)
    assert bool(errors) is expected_error, f"identity={detectIdentity(draft)}, errors={errors}"
    expected = "blocked_non_arxiv" if expected_error else "ready" if arxiv_id else "ready_non_arxiv"
    assert identityStatus(draft) == expected, f"identity={detectIdentity(draft)}, errors={errors}"


def test_acl_identity_no_longer_blocked_by_arxiv_only_guard(tmp_path):
    """P0: ACL DOI papers pass the unified identity gate.

    The old contract asserted "non-arXiv deduplication" / "non-arXiv
    materialization" blocks. That arxiv-only guard was removed in P0;
    identityKey() now gives ACL papers a stable dedup key. A write with no
    client fails on the *client* prerequisite, not on identity, and
    materialization succeeds at an identity-derived path.
    """
    from paper_article import ArticleDraft, REQUIRED_SECTIONS, materialize_article
    from notion_publish import publish_article
    from mineru_adapter import FigureAsset
    image = tmp_path / "figure.png"
    Image.new("RGB", (1280, 720)).save(image)
    draft = ArticleDraft(arxiv_id="", doi="10.18653/v1/2026.findings-acl.1001", title="Paper", slug="paper",
        markdown="\n".join(REQUIRED_SECTIONS) + "\n图示解释：架构图。", source_text="",
        figures=[FigureAsset(path=image, caption="Figure", dimensions=(1280, 720), is_hd=True, provenance="fixture")])
    # No identity block: it reaches the client prerequisite instead.
    with pytest.raises(ValueError, match="Notion client is required"):
        publish_article(None, draft, "db", write=True)
    # ACL materialization succeeds at an identity-derived path (not paper-.md).
    post = materialize_article(draft, tmp_path / "site")
    assert post.name == "paper-acl-2026-findings-acl-1001.md"
    assert post.exists()


def test_detect_identity_all_conditional_bytecode_branches():
    """Measure both successors of every conditional jump in detectIdentity."""
    import dis
    from paper_identity import detectIdentity

    instructions = list(dis.get_instructions(detectIdentity))
    jumps = {instruction.offset: instruction for instruction in instructions
             if instruction.opname.startswith("POP_JUMP_IF_") or instruction.opname == "FOR_ITER"}
    following = {instruction.offset: instructions[index + 1].offset
                 for index, instruction in enumerate(instructions[:-1]) if instruction.offset in jumps}
    observed = set()
    previous = {}

    def tracer(frame, event, arg):
        if frame.f_code is not detectIdentity.__code__:
            return tracer
        if event == "call":
            frame.f_trace_opcodes = True
        elif event == "opcode":
            old = previous.get(id(frame))
            if old in jumps:
                observed.add((old, frame.f_lasti))
            previous[id(frame)] = frame.f_lasti
        elif event == "return":
            previous.pop(id(frame), None)
        return tracer

    samples = [
        {}, {"arxiv_id": "2401.00001"}, {"arxiv_id": "2401.00001", "paper_url": "https://arxiv.org/abs/2401.00001"},
        {"arxiv_id": "2401.00001", "doi": "10.18653/v1/2026.findings-acl.1001"},
        {"doi": "10.18653/v1/2026.findings-acl.1001", "paper_url": "https://aclanthology.org/2026.findings-acl.1001/"},
        {"doi": "10.18653/v1/fake"}, {"doi": "10.18653/fake"}, {"paper_url": "https://doi.org/10.18653/v1/2026.findings-acl.1001"},
        {"paper_url": "https://arxiv.org/abs/2401.00001"}, {"paper_url": "https://arxiv.org/other/2401.00001"},
        {"paper_url": "https://invalid.example/paper"}, {"paper_url": "ftp://arxiv.org/abs/2401.00001"},
        {"paper_url": "https://user@arxiv.org/abs/2401.00001"}, {"paper_url": "https://:secret@arxiv.org/abs/2401.00001"},
        {"paper_url": "https:///abs/2401.00001"},
    ]
    old_trace = sys.gettrace()
    try:
        sys.settrace(tracer)
        for sample in samples:
            detectIdentity(sample)
    finally:
        sys.settrace(old_trace)
    # CPython 3.13 reports the next opcode after END_FOR and POP_TOP.
    offsets = [instruction.offset for instruction in instructions]
    target = {offset: (offsets[offsets.index(inst.argval) + 2] if inst.opname == "FOR_ITER"
                       and instructions[offsets.index(inst.argval)].opname == "END_FOR" else inst.argval)
              for offset, inst in jumps.items()}
    expected = {(offset, destination) for offset, inst in jumps.items()
                for destination in (target[offset], following[offset])}
    assert expected <= observed, f"missed branches: {sorted(expected - observed)}; observed: {sorted(observed)}"
