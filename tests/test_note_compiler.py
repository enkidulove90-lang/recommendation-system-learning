"""Tests for deterministic JSON -> note YAML compilation (agent-free)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from paper_intake.note_compiler import (
    SECTION_HEADINGS,
    SECTION_ORDER,
    _fit_title,
    _probe_review,
    build_body,
    compile_note,
    select_figures,
)
from redbook.services.xhs_content_gate import validate_xhs_content

ROOT = Path(__file__).resolve().parents[1]


def test_fit_title_keeps_literary_style_and_fits_gate() -> None:
    assert _fit_title("WWW 2026 | RecCLIP：协同过滤的视觉显影") == "RecCLIP：协同过滤的视觉显影"
    assert len(_fit_title("WWW 2026 | RecCLIP：协同过滤的视觉显影")) <= 20
    assert _fit_title("一个很短的标题") == "一个很短的标题"
    assert len(_fit_title("序" * 60)) <= 20


def test_select_figures_natural_order_without_manifest(tmp_path) -> None:
    images = tmp_path / "images"
    images.mkdir()
    for name in ("fig10.png", "fig2.png", "fig1.png"):
        (images / name).write_bytes(b"\x89PNG\r\n\x1a\n")
    figures = select_figures(tmp_path)
    assert [figure["file"] for figure in figures] == [
        "images/fig1.png", "images/fig2.png", "images/fig10.png"]


def test_select_figures_reads_selected_entries_in_versioned_manifest(tmp_path) -> None:
    images = tmp_path / "images_hd"
    images.mkdir()
    (images / "a.png").write_bytes(b"image-a")
    (images / "b.png").write_bytes(b"image-b")
    manifest = tmp_path / "reviewed_figures.json"
    manifest.write_text(json.dumps({"schema_version": "figure-manifest/v1", "canonical_id": "acl:1",
        "figures": [{"figure_id": "2", "path": "images_hd/b.png", "caption": "Results", "selected": True},
                    {"figure_id": "1", "path": "images_hd/a.png", "caption": "Other", "selected": False}]}), encoding="utf-8")
    figures = select_figures(tmp_path, manifest_path=manifest,
                             figure_intents=[{"description": "Unverified model caption"}])
    assert len(figures) == 1
    assert figures[0]["file"] == "images_hd/b.png"
    assert figures[0]["figure_id"] == "2"
    assert figures[0]["caption"] == "Results"
    assert figures[0]["description"] == "Results"


def test_default_manifest_reader_accepts_versioned_object(tmp_path) -> None:
    (tmp_path / "a.png").write_bytes(b"image")
    (tmp_path / "figure_manifest.json").write_text(json.dumps({
        "schema_version": "figure-manifest/v1", "canonical_id": "acl:1",
        "figures": [{"path": "a.png", "caption": "Architecture", "selected": True}]}), encoding="utf-8")
    assert select_figures(tmp_path)[0]["file"] == "a.png"
    assert select_figures(tmp_path)[0]["caption"] == "Architecture"
    with pytest.raises(ValueError, match="identity"):
        select_figures(tmp_path, canonical_id="other-paper")


def test_existing_manifest_without_selected_figures_does_not_scan_other_files(tmp_path) -> None:
    (tmp_path / "a.png").write_bytes(b"image")
    (tmp_path / "figure_manifest.json").write_text(json.dumps({"canonical_id": "acl:1", "figures": [
        {"path": "a.png", "selected": False}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="no usable selected figures"):
        select_figures(tmp_path, canonical_id="acl:1")


def test_compilers_use_same_manifest_links_and_wechat_root_relative_paths(tmp_path, monkeypatch) -> None:
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat

    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "QUEUE_DIR", tmp_path / "queue")
    parsed = tmp_path / "parsed"
    (parsed / "images").mkdir(parents=True)
    (parsed / "images" / "a.png").write_bytes(b"image-a")
    manifest = parsed / "selected.json"
    manifest.write_text(json.dumps({"canonical_id": "acl:1", "figures": [
        {"figure_id": "1", "path": "images/a.png", "caption": "Real caption", "selected": True,
         "sha256": "figure-hash", "source_type": "latex"}]}), encoding="utf-8")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"facts": {"method": "Method"}, "xhs_draft": {
        "title_literary": "Test", "opening": "Intro", "sections": {"result": "Result"}, "topics": ["科研"]},
        "wechat_draft": {"body": "Body"}}), encoding="utf-8")
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-paper")
    links = {"paper_url": "https://aclanthology.org/acl1", "pdf_url": "https://aclanthology.org/acl1.pdf",
             "code_url": "https://github.com/example/repo"}
    note = notes.compile_note(pack, canonical_id="acl:1", parsed_dir=parsed, pdf_path=pdf,
                              notes_dir=tmp_path / "notes", figure_manifest_path=manifest, **links)
    wechat_path, _ = wechat.compile_wechat_package(pack, canonical_id="acl:1", parsed_dir=parsed,
                                                    pdf_path=pdf, figure_manifest_path=manifest, **links)
    spec = yaml.safe_load(note.read_text(encoding="utf-8"))
    package = json.loads(wechat_path.read_text(encoding="utf-8"))
    assert spec["figures"][0]["file"] == "images/a.png"
    assert package["metadata"]["figure_manifest"][0]["figure_id"] == "1"
    assert spec["figures"][0]["sha256"] == package["metadata"]["figure_manifest"][0]["sha256"] == "figure-hash"
    assert spec["figures"][0]["source_type"] == "latex"
    assert 'src="parsed/images/a.png"' in package["metadata"]["wechat_html"]
    assert "Real caption" in package["metadata"]["wechat_html"]
    assert spec["links"]["paper"] == package["links"]["paper"] == links["paper_url"]
    assert spec["links"]["pdf"] == package["links"]["pdf"] == links["pdf_url"]
    assert spec["links"]["code"] == package["links"]["code"] == links["code_url"]
    assert spec["visual_review"] == package["review_status"] == "pending"
    assert package["body_markdown"] == spec["body"]
    assert "Intro" in package["metadata"]["wechat_html"]
    assert "Result" in package["metadata"]["wechat_html"]


def test_content_factory_compiles_shared_inputs_without_claiming_delivery(tmp_path, monkeypatch) -> None:
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    from content_factory.factory import ContentFactory
    from paper_intake.models import CompilationInputs

    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    parsed = tmp_path / "parsed"
    parsed.mkdir()
    (parsed / "a.png").write_bytes(b"figure")
    manifest = parsed / "selected.json"
    manifest.write_text(json.dumps({"canonical_id": "acl:1", "figures": [
        {"path": "a.png", "caption": "Figure", "selected": True}]}), encoding="utf-8")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"canonical_id": "acl:1", "facts": {}, "xhs_draft": {"title_literary": "Paper",
        "sections": {"result": "Result"}}}), encoding="utf-8")
    markdown = parsed / "paper.md"
    markdown.write_text("paper", encoding="utf-8")
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-paper")
    inputs = CompilationInputs("acl:1", "acl:1", "job-1", markdown, pdf,
        fact_pack_path=pack, figure_manifest_path=manifest,
        paper_url="https://example.org/paper", pdf_url="https://example.org/paper.pdf")
    factory = ContentFactory(tmp_path, tmp_path, parsed)
    result = factory.compile_shared(inputs)
    assert result["xhs"]["status"] == "compiled"
    assert result["wechat"]["status"] == "compiled"
    # The fixture deliberately uses fake image bytes and omits FactPack provenance.
    assert result["notion"]["status"] == "failed"
    assert result["xhs"]["drafted"] is False
    assert result["wechat"]["drafted"] is False
    package = json.loads(Path(result["wechat"]["path"]).read_text(encoding="utf-8"))
    assert '<span leaf="">' in package["metadata"]["wechat_html"]
    assert 'src="parsed/a.png"' in package["metadata"]["wechat_html"]


def test_real_echomllm_assets_compile_same_selected_figures_offline(tmp_path) -> None:
    import hashlib
    from content_factory.factory import ContentFactory
    from paper_intake.models import CompilationInputs
    from redbook.services.figure_retrieval import FigureRetrievalService, build_selected_figure_manifest

    canonical_id = "2026.findings-acl.1001"
    parsed = ROOT / "data" / "parsed" / "2026.findings-acl.1001_2026.findings-acl.1001"
    markdown = parsed / f"{canonical_id}.md"
    pdf = ROOT / "data" / "papers" / f"{canonical_id}.pdf"
    pack = ROOT / "data" / "summaries" / f"{canonical_id}_fact_pack.json"
    if not (markdown.is_file() and pdf.is_file() and pack.is_file() and (parsed / "images").is_dir()):
        pytest.skip("optional local EchoMLLM assets are not present")
    selected, _, _ = FigureRetrievalService().select(markdown, parsed / "images", limit=9)
    assert selected, "the real parsed paper needs at least one structurally eligible figure"
    manifest = build_selected_figure_manifest(canonical_id, parsed, selected)
    manifest_path = tmp_path / "selected.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    inputs = CompilationInputs(canonical_id, "source:acl_anthology:" + canonical_id,
        "local-regression", markdown, pdf, fact_pack_path=pack, figure_manifest_path=manifest_path,
        paper_url=f"https://aclanthology.org/{canonical_id}/",
        pdf_url=f"https://aclanthology.org/{canonical_id}.pdf")
    result = ContentFactory(tmp_path, tmp_path, parsed).compile_shared(inputs)
    assert result["xhs"]["status"] == "compiled", result["xhs"]
    assert result["wechat"]["status"] == "compiled", result["wechat"]
    assert result["notion"]["status"] == "compiled", result["notion"]
    spec = yaml.safe_load(Path(result["xhs"]["path"]).read_text(encoding="utf-8"))
    package = json.loads(Path(result["wechat"]["path"]).read_text(encoding="utf-8"))
    notion_package = json.loads(Path(result["notion"]["path"]).read_text(encoding="utf-8"))
    assert spec["visual_review"] == package["review_status"] == "pending"
    assert spec["body"] == package["body_markdown"]
    assert spec["links"]["paper"] == package["links"]["paper"] == inputs.paper_url
    assert len(spec["figures"]) == len(package["metadata"]["figure_manifest"]) == len(selected)
    assert len(notion_package["figures"]) == len(selected)
    assert notion_package["identity_status"] == "ready_non_arxiv"
    assert notion_package["blog_compatibility"] == "not_validated"
    for a, b in zip(spec["figures"], package["metadata"]["figure_manifest"]):
        assert a["file"] == b["file"]
        assert a["sha256"] == b["sha256"] == hashlib.sha256((parsed / a["file"]).read_bytes()).hexdigest()
        assert a["caption"] == b["caption"]
    assert result["xhs"]["drafted"] is False and result["wechat"]["drafted"] is False


def test_content_factory_rejects_fact_pack_from_another_paper(tmp_path, monkeypatch) -> None:
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    from content_factory.factory import ContentFactory
    from paper_intake.models import CompilationInputs

    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    (tmp_path / "a.png").write_bytes(b"figure")
    manifest = tmp_path / "selected.json"
    manifest.write_text(json.dumps({"canonical_id": "acl:1", "figures": [{"path": "a.png"}]}), encoding="utf-8")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"canonical_id": "wrong", "facts": {}, "xhs_draft": {
        "title_literary": "Paper", "sections": {"result": "Result"}}}), encoding="utf-8")
    markdown = tmp_path / "paper.md"
    markdown.write_text("paper", encoding="utf-8")
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-paper")
    inputs = CompilationInputs("acl:1", "acl:1", "job-1", markdown, pdf,
        fact_pack_path=pack, figure_manifest_path=manifest,
        paper_url="https://example.org/paper", pdf_url="https://example.org/paper.pdf")
    result = ContentFactory(tmp_path, tmp_path, tmp_path).compile_shared(inputs)
    assert result["xhs"]["status"] == "blocked"
    assert result["wechat"]["status"] == "blocked"
    assert not (tmp_path / "redbook" / "notes").exists()
    changed = json.loads(pack.read_text(encoding="utf-8"))
    changed.update(canonical_id="acl:1", source_hash="wrong-hash")
    pack.write_text(json.dumps(changed), encoding="utf-8")
    result = ContentFactory(tmp_path, tmp_path, tmp_path).compile_shared(inputs)
    assert result["xhs"]["status"] == "blocked"
    assert "source hash" in result["xhs"]["reason"]


def test_content_factory_rejects_missing_source_pdf_before_compiling(tmp_path) -> None:
    from content_factory.factory import ContentFactory
    from paper_intake.models import CompilationInputs

    markdown = tmp_path / "paper.md"
    markdown.write_text("paper", encoding="utf-8")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"canonical_id": "acl:1", "facts": {}, "xhs_draft": {
        "title_literary": "Paper", "sections": {"result": "Result"}}}), encoding="utf-8")
    manifest = tmp_path / "selected.json"
    manifest.write_text(json.dumps({"canonical_id": "acl:1", "figures": []}), encoding="utf-8")
    inputs = CompilationInputs("acl:1", "acl:1", "job-1", markdown, tmp_path / "missing.pdf",
        fact_pack_path=pack, figure_manifest_path=manifest,
        paper_url="https://example.org/paper", pdf_url="https://example.org/paper.pdf")
    result = ContentFactory(tmp_path, tmp_path, tmp_path).compile_shared(inputs)
    assert result["xhs"]["status"] == "blocked"
    assert result["wechat"]["status"] == "blocked"
    assert not (tmp_path / "redbook" / "notes").exists()


def test_compiler_rejects_manifest_for_different_paper(tmp_path) -> None:
    parsed = tmp_path / "parsed"
    parsed.mkdir()
    (parsed / "a.png").write_bytes(b"image")
    manifest = parsed / "selected.json"
    manifest.write_text(json.dumps({"canonical_id": "wrong-paper", "figures": [
        {"path": "a.png", "selected": True}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        select_figures(parsed, manifest_path=manifest, canonical_id="acl:1")


def test_wechat_html_includes_all_selected_figures() -> None:
    from paper_intake.wechat_compiler import build_wechat_html_with_captions

    figures = [{"file": f"data/fig{n}.png", "caption": f"Caption {n}"} for n in range(1, 7)]
    html = build_wechat_html_with_captions({}, figures, paper_url="https://example.org/paper",
                                           code_url="", title="Paper")
    for figure in figures:
        assert f'src="{figure["file"]}"' in html
        assert figure["caption"] in html


def test_build_body_new_template_rules() -> None:
    draft = {
        "opening": "跨域新范式：协同过滤视觉语言模型——RecCLIP论文导读",
        "pain_point": "核心痛点：不同数据集ID互不通用，跨域迁移困难",
        "seed": 2,
        "sections": {
            "contribution": "① 把交互矩阵变成图像。\n② 文本提示表达候选。\n③ 视觉语言模型重排。",
            "method": "① 压缩交互矩阵。\n② 映射黑白像素。\n③ 对比微调。",
            "experiment": "数据集：A、B、C\n算力：4 GPU\n指标：Recall@K",
            "result": "跨域 Recall@1 达 57.62%，优于基线 38.77%。",
        },
    }
    paper_url = "https://arxiv.org/abs/2601.00001"
    code_url = "https://github.com/example/recclip"
    body = build_body(draft, paper_url=paper_url, code_url=code_url)
    assert len(body) <= 980
    assert body.startswith("🌐 ")
    assert "论文导读\n核心痛点：" in body  # newline after 🌐 hook
    assert "🎓 主要贡献与创新\n①" in body  # heading, ONE newline, content next line
    assert "🎓 主要贡献与创新 ①" not in body  # no longer heading+content same line
    assert "② 文本提示表达候选。" in body  # bullet newlines preserved
    assert "💡 借鉴" not in body  # template omits these sections
    assert "⚠️ 局限" not in body  # gate no longer requires it
    # Reference tail: result paragraph → 📎 paper → 💻 code, single newlines.
    assert "\n📎 论文链接：" + paper_url in body
    assert body.endswith("\n💻 代码链接：" + code_url)
    tail_at = body.index("📎 论文链接")
    assert body[tail_at - 1] == "\n"  # single newline after the result paragraph
    # Topics are NEVER literal text in the body: typing '#' on the platform
    # opens the topic picker and the draft keeps real entities instead.
    assert "#" not in body
    assert validate_xhs_content(body, ["论文分享", "人工智能"]) == []
    for key in SECTION_ORDER:
        assert SECTION_HEADINGS[key] in body


def test_build_body_without_code_link_keeps_tail_shape() -> None:
    draft = {
        "opening": "开篇",
        "sections": {"result": "结果一段。"},
    }
    body = build_body(draft, paper_url="https://doi.org/10.1000/x")
    assert body.endswith("\n📎 论文链接：https://doi.org/10.1000/x")
    assert "💻 代码链接" not in body  # no code link -> no line
    assert "#" not in body


def test_compile_note_end_to_end(tmp_path) -> None:
    parsed = tmp_path / "parsed"
    (parsed / "images").mkdir(parents=True)
    (parsed / "images" / "fig1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    fact_pack = {
        "schema_version": "fact-pack/v2",
        "canonical_id": "arxiv:2601.00001",
        "source_hash": "h", "model_id": "m", "prompt_version": "v2",
        "facts": {"limitations": "仅离线验证，线上收益待确认。"},
        "platform_hints": {},
        "xhs_draft": {
            "title_literary": "WWW 2026 | FooBar：一个诗意的标题",
            "title_question": "推荐也能这样？",
            "opening": "一句话新意——FooBar论文导读",
            "pain_point": "核心痛点：老方法迁移难",
            "seed": 3,
            "sections": {
                "contribution": "贡献一段。", "method": "方法一。",
                "experiment": "数据集：A\n算力：1 GPU\n指标：R@K",
                "result": "结果一段。",
            },
            "topics": ["论文分享", "不在白名单的话题"],
            "figure_intents": [{"order": 1, "intent": "architecture", "description": "架构图"}],
        },
        "wechat_draft": {"lead": "lead", "body": "long body"},
        "homepage_draft": {"summary_1line": "one line", "summary_para": "para"},
    }
    pack_path = tmp_path / "fact_pack.json"
    pack_path.write_text(json.dumps(fact_pack, ensure_ascii=False), encoding="utf-8")

    notes_dir = tmp_path / "notes"
    target = compile_note(
        pack_path, canonical_id="arxiv:2601.00001", parsed_dir=parsed,
        pdf_path=pdf, notes_dir=notes_dir)
    spec = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert spec["title"] == "FooBar：一个诗意的标题"
    assert spec["paper_id"] == "2601.00001"
    assert spec["figures"][0]["type"] == "architecture"
    assert "论文分享" in spec["topics"]
    assert "不在白名单的话题" not in spec["topics"]
    assert spec["visual_review"]
    assert spec["source"] == "handwritten"
    # Template v3 tail closes with the reference links; topics stay in the
    # topics list and are bound as platform entities at delivery time.
    assert "📎 论文链接：https://arxiv.org/abs/2601.00001" in spec["body"]
    assert spec["body"].endswith("https://arxiv.org/abs/2601.00001")
    assert "#" not in spec["body"]
    assert validate_xhs_content(spec["body"], spec["topics"]) == []


def test_doi_note_uses_safe_slug_and_preserves_existing_revision(tmp_path) -> None:
    parsed = tmp_path / "parsed"
    parsed.mkdir()
    (parsed / "fig.png").write_bytes(b"image")
    pack = tmp_path / "pack.json"
    payload = {"facts": {}, "xhs_draft": {"title_literary": "Version one", "sections": {"result": "First"}}}
    pack.write_text(json.dumps(payload), encoding="utf-8")
    kwargs = {"canonical_id": "doi:10.1145/3774904.3792523", "parsed_dir": parsed,
              "pdf_path": None, "notes_dir": tmp_path / "notes"}
    first = compile_note(pack, **kwargs)
    original = first.read_bytes()
    assert first.parent == tmp_path / "notes"
    assert "/" not in first.stem and "\\" not in first.stem
    assert yaml.safe_load(original)["paper_id"] == "10.1145/3774904.3792523"
    assert compile_note(pack, **kwargs) == first
    payload["xhs_draft"]["title_literary"] = "Version two"
    pack.write_text(json.dumps(payload), encoding="utf-8")
    second = compile_note(pack, **kwargs)
    assert second != first and first.read_bytes() == original
    assert yaml.safe_load(second.read_bytes())["slug"] == second.stem


def test_retired_json_to_xhs_entrypoint_does_not_generate_or_publish(tmp_path, monkeypatch) -> None:
    import scripts.generate_fact_pack as generation
    from scripts.json_to_xhs_draft import run

    def fail_if_called(*args, **kwargs):
        raise AssertionError("retired entrypoint must not generate content")
    monkeypatch.setattr(generation, "generate", fail_if_called)
    with pytest.raises(RuntimeError, match="retired"):
        run("arxiv:1", tmp_path / "paper.md", tmp_path, None, publish=True)


def test_compile_rejects_v1_pack(tmp_path) -> None:
    pack_path = tmp_path / "v1.json"
    pack_path.write_text(json.dumps({"facts": {}, "platform_hints": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="xhs_draft"):
        compile_note(pack_path, canonical_id="arxiv:x", parsed_dir=tmp_path,
                     pdf_path=None, notes_dir=tmp_path / "notes")
