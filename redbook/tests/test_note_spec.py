"""note spec → render_post 定稿分支 → PublicationPackage 的 P0 验收线。

最关键的一条是 ``test_build_note_package_matches_legacy``：用 AST 从旧
``build_xhs_draft_sage.py`` 抽常量重建 legacy package，逐字段比对，证明迁移
没有改变任何一篇已发布帖子的内容。
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
import yaml

from redbook.application.paper_workflow import PaperCreationWorkflow
from redbook.automation.publishing import PublicationPackage
from redbook.services.note_spec import NoteSpecError, list_notes, load_note
from redbook.services.render_post import render_post
from redbook.services.xhs_content_gate import ContentSpecError

REPO_ROOT = Path(__file__).resolve().parents[2]
SAGE_ID = "2601.21452"
SAGE_TOPICS = ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"]
SAGE_REVIEW = "ViewImage 逐张目检 6 张（含 1.8x 放大伪影复核）"


def _legacy_script() -> Path:
    for rel in ("build_xhs_draft_sage.py", "archive/xhs_drafts/build_xhs_draft_sage.py"):
        path = REPO_ROOT / rel
        if path.is_file():
            return path
    pytest.skip("legacy SAGE script unavailable; equivalence assertion skipped")


def _legacy_constants() -> dict:
    tree = ast.parse(_legacy_script().read_text(encoding="utf-8"))
    result = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                result[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError):
                pass
    return result


def _rel(path: str) -> str:
    """把绝对路径归一化成相对仓库根，用于跨路径写法比较。"""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except (ValueError, OSError):
        return str(path).replace("\\", "/")


def _write_spec(tmp_path: Path, **overrides) -> Path:
    spec = yaml.safe_load((REPO_ROOT / "redbook" / "notes" / f"{SAGE_ID}.yaml").read_text(encoding="utf-8"))
    spec.update(overrides)
    notes = tmp_path / "notes"
    notes.mkdir(exist_ok=True)
    (notes / f"{SAGE_ID}.yaml").write_text(
        yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, width=100000), encoding="utf-8"
    )
    return notes


def test_load_sage_spec_roundtrip():
    spec = load_note(SAGE_ID)
    assert spec.paper_id == SAGE_ID
    assert spec.title == "SAGE：只换优化器，冷启动召回翻倍"
    assert len(spec.title) <= 20
    assert len(spec.body) == 999
    assert len(spec.body) <= 1000
    assert len(spec.figures) == 6
    assert spec.figures[0].file == "images/paper-all-pic.png"
    assert spec.figures[0].type == "motivation"
    assert spec.figures[0].description.startswith("论文图 1")
    assert spec.topics == tuple(SAGE_TOPICS)
    assert spec.links["paper"] == "https://arxiv.org/abs/2601.21452"
    assert spec.pdf_path == "data/parsed/2601.21452/2601.21452_origin.pdf"
    assert spec.visual_review == SAGE_REVIEW
    assert spec.status == "staged"
    assert spec.source == "handwritten"


def test_spec_body_matches_legacy_constant():
    """定稿正文必须逐字相同，不允许为了过闸门而改写。"""
    assert load_note(SAGE_ID).body == _legacy_constants()["BODY"]


def test_image_paths_resolve_from_repo_root_not_cwd(tmp_path, monkeypatch):
    spec = load_note(SAGE_ID)
    monkeypatch.chdir(tmp_path)
    assert all(path.startswith(str(REPO_ROOT)) for path in spec.image_paths())
    assert Path(spec.image_paths()[0]).name == "paper-all-pic.png"
    assert Path(spec.image_paths()[0]).parent.name == "images"


def test_list_notes_skips_schema():
    rows = list_notes()
    assert "_schema" not in [row["slug"] for row in rows]
    assert all(not row.get("error") for row in rows)
    sage = next(row for row in rows if row["slug"] == SAGE_ID)
    assert sage["figures"] == 6
    assert sage["visual_review"] is True


def test_missing_field_and_bad_status_raise(tmp_path):
    with pytest.raises(NoteSpecError, match="missing fields"):
        load_note(SAGE_ID, _write_spec(tmp_path, body=""))
    with pytest.raises(NoteSpecError, match="invalid status"):
        load_note(SAGE_ID, _write_spec(tmp_path, status="shipped"))
    mismatch_notes = _write_spec(tmp_path)
    (mismatch_notes / "9999.99999.yaml").write_text(
        (mismatch_notes / f"{SAGE_ID}.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(NoteSpecError, match="paper_id mismatch"):
        load_note("9999.99999", mismatch_notes)
    with pytest.raises(NoteSpecError, match="paper and pdf"):
        load_note(SAGE_ID, _write_spec(tmp_path, links={"paper": "x"}))


def test_render_post_handwritten_branch_skips_composer(monkeypatch):
    spec = load_note(SAGE_ID)

    def _must_not_run(*args, **kwargs):
        pytest.fail("handwritten body must not go through PersonaPostComposer")

    monkeypatch.setattr("redbook.services.render_post.PersonaPostComposer.compose", _must_not_run)
    post = render_post("xhs", **spec.as_post_kwargs())
    assert post["body"] == spec.body
    assert post["title"] == spec.title
    assert post["generation_prompt"] == ""
    assert post["persona_id"] == "handwritten"
    assert post["metadata"]["source"] == "handwritten"
    assert len(post["images"]) == 6


def test_gate_rejects_weak_handwritten_posts():
    spec = load_note(SAGE_ID)
    kwargs = spec.as_post_kwargs()
    with pytest.raises(ContentSpecError, match="visual_review"):
        render_post("xhs", **{**kwargs, "visual_review": ""})
    with pytest.raises(ContentSpecError, match="content gate failed"):
        render_post("xhs", **{**kwargs, "body": kwargs["body"] + "\n#话题"})
    with pytest.raises(ContentSpecError, match="not in config"):
        render_post("xhs", **{**kwargs, "topics": ["AI新手村"]})


def test_compose_post_generated_path_still_works():
    """定稿分支不能破坏原有 summary → persona 模板路径。"""
    summary = "## 问题\nA\n\n## 方法\nB\n\n## 结果\nC\n\n## 局限\nD\n"
    post = render_post("xhs", summary, None, arxiv_id="9999.00001")
    assert post["generation_prompt"]
    assert post["persona_id"] != "handwritten"
    assert post["metadata"]["source"] == "render_post"


def test_build_note_package_matches_legacy():
    """P0 等价性：新旧 package 指向同一份标题/正文/图/链接/话题/附件。"""
    consts = _legacy_constants()
    legacy = PublicationPackage(
        paper_id=SAGE_ID,
        platform="xhs",
        canonical_url=consts["PAPER_URL"],
        title=consts["TITLE"],
        body_markdown=consts["BODY"],
        image_paths=[f"data/parsed/2601.21452/images/{name}" for name in consts["FIG_ORDER"]],
        links={"paper": consts["PAPER_URL"], "pdf": "https://arxiv.org/pdf/2601.21452", "code": ""},
        metadata={
            "topics": SAGE_TOPICS,
            "visual_review": SAGE_REVIEW,
            "pdf_path": "data/parsed/2601.21452/2601.21452_origin.pdf",
            "author": "",
            "source_attribution": "图表摘自论文，仅作学术解读。",
        },
        review_status="pending",
    )
    workflow = PaperCreationWorkflow(REPO_ROOT / "data")
    _, package = workflow.build_note_package(SAGE_ID)

    assert package.title == legacy.title
    assert package.body_markdown == legacy.body_markdown
    assert package.canonical_url == legacy.canonical_url
    assert package.links == legacy.links
    assert package.review_status == legacy.review_status
    assert package.source_attribution == legacy.source_attribution
    assert package.paper_id == legacy.paper_id
    assert [_rel(p) for p in package.image_paths] == [_rel(p) for p in legacy.image_paths]

    # 只排除迁移新增的两个审计标记；其余 metadata 必须逐项一致。
    new_meta = {k: v for k, v in package.metadata.items() if k not in {"source", "persona_id"}}
    old_meta = dict(legacy.metadata)
    assert set(new_meta) == set(old_meta)
    for key in old_meta:
        if key == "pdf_path":
            assert _rel(new_meta[key]) == _rel(old_meta[key])
        else:
            assert new_meta[key] == old_meta[key]
    assert package.metadata["source"] == "handwritten"


def test_validate_and_stage_note_with_tmp_assets(tmp_path):
    """另一台机器没有真实图片也能 validate；stage 才检查文件并推进断点。"""
    notes = _write_spec(tmp_path)
    assets = tmp_path / "data" / "parsed" / SAGE_ID / "images"
    assets.mkdir(parents=True)
    for figure in load_note(SAGE_ID, notes).figures:
        (assets / Path(figure.file).name).write_bytes(b"fake-png")
    pdf = tmp_path / "data" / "parsed" / SAGE_ID / "2601.21452_origin.pdf"
    pdf.write_bytes(b"fake-pdf")

    workflow = PaperCreationWorkflow(tmp_path / "queue_root")
    validated = workflow.validate_note(SAGE_ID, notes_dir=notes, repo_root=tmp_path)
    assert validated["ok"] is True, validated
    assert validated["body_chars"] == 999

    staged = workflow.stage_note(SAGE_ID, notes_dir=notes, repo_root=tmp_path)
    assert staged["ok"] is True, staged
    checkpoint = tmp_path / "queue_root" / "workflow_state" / SAGE_ID / "checkpoint.json"
    assert "packaged" in checkpoint.read_text(encoding="utf-8")
    staged_file = Path(staged["path"])
    payload = json.loads(staged_file.read_text(encoding="utf-8"))
    assert payload["body_markdown"] == load_note(SAGE_ID).body
    assert payload["content_hash"][:32] == staged_file.parent.name


def test_validate_does_not_require_image_files(tmp_path):
    notes = _write_spec(tmp_path)
    workflow = PaperCreationWorkflow(tmp_path / "queue_root")
    result = workflow.validate_note(SAGE_ID, notes_dir=notes, repo_root=tmp_path)
    assert result["ok"] is True
    blocked = workflow.stage_note(SAGE_ID, notes_dir=notes, repo_root=tmp_path)
    assert blocked["ok"] is False
    assert any("missing asset" in error for error in blocked["errors"])
