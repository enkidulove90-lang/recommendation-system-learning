"""14 篇 note spec 的迁移完整性回归。

证明迁移「只搬不改」：每篇 spec 的标题与正文必须与归档脚本里的常量逐字一致。
归档脚本带 DEPRECATED 注释头，但 AST 解析不受影响。
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from redbook.services.content_composer import compose_content
from redbook.services.note_spec import NOTES_DIR, list_notes, load_note

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = REPO_ROOT / "archive" / "xhs_drafts"

#: 归档脚本 -> (slug, 是否有字面 BODY 常量)
LEGACY_BUILDS = {
    "build_xhs_draft_2608_14429.py": "2608.14429",
    "build_xhs_draft_2609_05339.py": "2609.05339",
    "build_xhs_draft_2609_20804.py": "2609.20804",
    "build_xhs_draft_2609_22086.py": "2609.22086",
    "build_xhs_draft_ace_2605_29322.py": "2605.29322",
    "build_xhs_draft_ace_v2.py": "2605.29322_ace_v2",
    "build_xhs_draft_diffgrm.py": "2510.21805",
    "build_xhs_draft_diger_2601_19711.py": "2601.19711",
    "build_xhs_draft_sage.py": "2601.21452",
    "build_xhs_draft_sihg_rec.py": "10.1145_3847662",
    "build_xhs_draft_tmlr_cot_v2.py": "TiZQnKDIHq_cot_v2",
    "build_xhs_draft_tmlr_loadbearing_cot.py": "TiZQnKDIHq",
    "build_xhs_draft_unipinrec.py": "2606.00422",
}


def _constants(path: Path) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            try:
                if isinstance(target, ast.Name):
                    result[target.id] = ast.literal_eval(node.value)
                elif isinstance(target, ast.Tuple):
                    values = ast.literal_eval(node.value)
                    for item, value in zip(target.elts, values):
                        if isinstance(item, ast.Name):
                            result[item.id] = value
            except (ValueError, TypeError, SyntaxError):
                pass
    return result


def test_all_14_specs_load_and_list():
    files = sorted(path for path in NOTES_DIR.glob("*.yaml") if not path.name.startswith("_"))
    assert len(files) == 14
    rows = list_notes()
    assert len(rows) == 14
    assert all(not row.get("error") for row in rows)
    assert all(row["figures"] >= 1 for row in rows)
    for path in files:
        spec = load_note(path.stem)
        assert spec.slug == path.stem
        assert spec.title and spec.body and spec.topics and spec.links["paper"]
        assert spec.visual_review.strip()
        assert spec.parsed_dir.startswith("data/parsed")


def test_every_legacy_script_is_deprecated_and_mapped():
    for name, slug in LEGACY_BUILDS.items():
        path = ARCHIVE / name
        assert path.is_file(), path
        assert "DEPRECATED 2026-11-10" in path.read_text(encoding="utf-8")[:400]
        assert f"redbook/notes/{slug}.yaml" in path.read_text(encoding="utf-8")[:400]
    assert (ARCHIVE / "README.md").is_file()


@pytest.mark.parametrize("name,slug", sorted(LEGACY_BUILDS.items()))
def test_spec_body_and_title_match_legacy_verbatim(name, slug):
    consts = _constants(ARCHIVE / name)
    spec = load_note(slug)
    assert spec.title == consts["TITLE"], name
    assert spec.body == consts["BODY"], name
    assert len(spec.figures) >= 1


def test_gatebox_spec_matches_content_composer_output():
    """第四套路径（冻结 7 段口径）的正文必须等于 compose_content 的产出。"""
    consts = _constants(ARCHIVE / "build_xhs_draft_gateboxgcn.py")
    composed = compose_content(
        consts["SECTIONS"], venue=consts["VENUE"], year=consts["YEAR"], hook=consts["HOOK"]
    )
    spec = load_note("3773078.3831765")
    assert spec.title == composed["title"]
    assert spec.body == composed["body"]
    assert spec.source == "content_composer"


def test_two_known_legacy_gate_exceptions_are_documented():
    """2608 用「一点提醒」代替局限题头；gateboxgcn 是 1328 字冻结口径。

    两篇正文都原样保留，不因过闸门而改写；这里锁死事实，避免有人偷偷改文案。
    """
    spec_a = load_note("2608.14429")
    assert "⚠️ 一点提醒" in spec_a.body and "局限" not in spec_a.body
    assert spec_a.status == "draft"
    spec_b = load_note("3773078.3831765")
    assert len(spec_b.body) > 1000
    assert "局限" not in spec_b.body
    assert spec_b.status == "draft"


def test_archived_tools_are_deprecated():
    expected = {
        "crop_pdf_figure.py": "figure_crop",
        "fetch_acm_pdf.py": "acm_dl",
        "inspect_xhs_drafts.py": "xhs_drafts",
        "verify_xhs_drafts.py": "xhs_drafts",
    }
    for name, module in expected.items():
        path = ARCHIVE / name
        assert path.is_file(), path
        header = path.read_text(encoding="utf-8")[:400]
        assert "DEPRECATED 2026-11-10" in header
        assert module in header
