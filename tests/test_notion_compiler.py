from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from paper_intake.models import CompilationInputs


def _inputs(tmp_path: Path, canonical_id: str, paper_url: str) -> CompilationInputs:
    parsed = tmp_path / "parsed"
    parsed.mkdir()
    markdown = parsed / "paper.md"
    markdown.write_text("Paper evidence, result 12%.\n", encoding="utf-8")
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-paper")
    image = parsed / "fig.png"
    Image.new("RGB", (1280, 720), "white").save(image)
    image_hash = hashlib.sha256(image.read_bytes()).hexdigest()
    manifest = parsed / "selected.json"
    manifest.write_text(json.dumps({"canonical_id": canonical_id, "figures": [{
        "figure_id": "Figure 1", "path": "fig.png", "caption": "Architecture",
        "source_type": "pdf_high_dpi", "sha256": image_hash,
        "width": 1280, "height": 720, "selected": True,
    }]}), encoding="utf-8")
    pack = tmp_path / "fact.json"
    pack.write_text(json.dumps({"canonical_id": canonical_id,
        "source_hash": hashlib.sha256(markdown.read_bytes()).hexdigest(),
        "platform_hints": {},
        "facts": {"paper_title": "Paper title", "problem": "Problem", "method": "Method",
                  "experiments": ["result 12%"], "authors": [{"name": "Author"}],
                  "background": "Background paragraph.",
                  "method_summary": "统一编码",
                  "method_overview": "Overview paragraph.",
                  "methods": [{"heading": "像素空间统一", "detail": "Detail paragraph."}],
                  "experiment_highlight": "跨语言一致",
                  "datasets": ["CVSS-C"],
                  "experiment_protocol": "Protocol paragraph.",
                  "metrics": ["BLEU"],
                  "hyperparameters": "lr=2e-6",
                  "results_analysis": "Analysis paragraph.",
                  "summary_highlight": "像素空间统一编码"},
        "homepage_draft": {"summary_1line": "Summary"},
        "location": {"venue_city": "Vienna", "affil_city": ["Beijing"]},
        "references": [{"title": "Prior", "paper_url": "https://example.org/prior",
                        "code_url": "https://github.com/example/prior"}],
        "formulae": [{"latex": "x^2", "display_mode": "block", "source_location": "p1"}],
        # 图注由事实包提供：站点要求图片后面跟一段可读描述，而不是 "图示解释：" 前缀。
        "figures": [{"figure_id": "Figure 1",
                     "explanation": "该图展示整体流程：输入先进入编码器，再经统一空间对齐后输出。"}],
    }), encoding="utf-8")
    return CompilationInputs(canonical_id, canonical_id, "job-1", markdown, pdf,
        fact_pack_path=pack, figure_manifest_path=manifest, paper_url=paper_url,
        pdf_url="https://example.org/paper.pdf", code_url="https://github.com/example/paper")


@pytest.mark.parametrize(("canonical_id", "paper_url", "kind", "arxiv_id"), [
    ("arxiv:2601.00001", "https://arxiv.org/abs/2601.00001", "arxiv", "2601.00001"),
    ("2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/", "acl_doi", ""),
    ("doi:10.1145/3774904.3792523", "https://doi.org/10.1145/3774904.3792523", "none", ""),
    ("doi:10.18653/fake", "https://doi.org/10.18653/fake", "none", ""),
])
def test_local_review_package_preserves_identity_and_evidence(tmp_path, canonical_id, paper_url, kind, arxiv_id):
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, canonical_id, paper_url)
    result = compile_notion_package(inputs, output_dir=tmp_path / "queue")
    package = json.loads(result.path.read_text(encoding="utf-8"))
    assert result.status == "compiled"
    assert package["identity"]["kind"] == kind
    assert package["identity"]["canonical_id"] == canonical_id
    assert package["article_input"]["arxiv_id"] == arxiv_id
    assert package["article_input"]["source_pdf"] == str(inputs.pdf_path)
    assert package["article_input"]["source_text"] == "Paper evidence, result 12%.\n"
    assert package["location"]["venue_city"] == "Vienna"
    assert package["references"][0]["code_url"] == "https://github.com/example/prior"
    assert "[Prior](https://example.org/prior)" in package["article_input"]["markdown"]
    assert "[代码](https://github.com/example/paper)" in package["article_input"]["markdown"]
    assert package["formulae"][0]["latex"] == "x^2"
    assert package["figures"][0]["sha256"] == hashlib.sha256((inputs.markdown_path.parent / "fig.png").read_bytes()).hexdigest()
    assert package["review_status"] == "pending"
    assert package["provenance"]["pdf_sha256"] == hashlib.sha256(inputs.pdf_path.read_bytes()).hexdigest()
    assert package["provenance"]["fact_pack_path"] == str(inputs.fact_pack_path.resolve())
    assert package["notion_written"] is False
    assert package["blog_validation_performed"] is False
    assert package["blog_compatibility"] == ("not_validated" if kind in ("arxiv", "acl_doi") else "blocked_non_arxiv")
    assert package["identity_status"] == ("ready" if kind == "arxiv" else "ready_non_arxiv" if kind == "acl_doi" else "blocked_non_arxiv")
    assert compile_notion_package(inputs, output_dir=tmp_path / "queue").path == result.path


def test_arxiv_review_input_can_construct_and_validate_real_blog_article(tmp_path, monkeypatch):
    from paper_intake.notion_compiler import compile_notion_package

    blog_tools = Path("D:/enkidulove90-lang.github.io/tools")
    if not (blog_tools / "paper_article.py").is_file():
        pytest.skip("local blog checkout unavailable")
    monkeypatch.syspath_prepend(str(blog_tools))
    from mineru_adapter import FigureAsset
    from paper_article import ArticleDraft, validate_article, materialize_article
    from notion_publish import markdown_to_blocks

    inputs = _inputs(tmp_path, "arxiv:2601.00001", "https://arxiv.org/abs/2601.00001")
    result = compile_notion_package(inputs, output_dir=tmp_path / "queue")
    data = json.loads(result.path.read_text(encoding="utf-8"))["article_input"]
    figures = [FigureAsset(path=Path(item["path"]), caption=item["caption"],
                           dimensions=tuple(item["dimensions"]), is_hd=item["is_hd"],
                           provenance=item["provenance"]) for item in data["figures"]]
    draft = ArticleDraft(arxiv_id=data["arxiv_id"], title=data["title"], slug=data["slug"],
        markdown=data["markdown"], source_text=data["source_text"], figures=figures,
        source_pdf=Path(data["source_pdf"]), source_spans=data["source_spans"])
    assert validate_article(draft) == []
    site = tmp_path / "isolated_site"
    article = materialize_article(draft, site)
    assert article.is_file()
    assert (site / "source" / "images" / "papers" / "2601.00001" / "fig.png").is_file()
    assert "/images/papers/2601.00001/fig.png" in article.read_text(encoding="utf-8")
    blocks = markdown_to_blocks(draft.markdown, {"fig.png": "local-test-upload-id"})
    assert any(block["type"] == "image" for block in blocks)


def test_blog_markdown_renderer_renders_local_review_image_and_reference(tmp_path, monkeypatch):
    import shutil
    import subprocess
    from paper_intake.notion_compiler import compile_notion_package

    marked = Path("D:/enkidulove90-lang.github.io/node_modules/marked/lib/marked.cjs")
    if not marked.is_file() or not shutil.which("node"):
        pytest.skip("blog marked renderer or node unavailable")
    inputs = _inputs(tmp_path, "arxiv:2601.00001", "https://arxiv.org/abs/2601.00001")
    package = json.loads(compile_notion_package(inputs, output_dir=tmp_path / "out").path.read_text(encoding="utf-8"))
    script = "const m=require(process.argv[1]);let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(m.parse(s)));"
    result = subprocess.run(["node", "-e", script, str(marked)], input=package["article_input"]["markdown"],
                            text=True, encoding="utf-8", capture_output=True, check=True)
    assert 'src="/images/papers/2601.00001/fig.png"' in result.stdout
    assert 'href="https://example.org/prior"' in result.stdout


def test_acl_review_identity_passes_blog_identity_gate(tmp_path, monkeypatch):
    from paper_intake.notion_compiler import compile_notion_package
    blog_tools = Path("D:/enkidulove90-lang.github.io/tools")
    if not (blog_tools / "paper_article.py").is_file():
        pytest.skip("local blog checkout unavailable")
    monkeypatch.syspath_prepend(str(blog_tools))
    from mineru_adapter import FigureAsset
    from paper_article import ArticleDraft, validate_article

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    package = json.loads(compile_notion_package(inputs, output_dir=tmp_path / "out").path.read_text(encoding="utf-8"))
    data = package["article_input"]
    figs = [FigureAsset(path=Path(f["path"]), caption=f["caption"], dimensions=tuple(f["dimensions"]),
                        is_hd=f["is_hd"], provenance=f["provenance"]) for f in data["figures"]]
    draft = ArticleDraft(arxiv_id=data["arxiv_id"], title=data["title"], slug=data["slug"],
                         markdown=data["markdown"], source_text=data["source_text"], figures=figs,
                         source_pdf=Path(data["source_pdf"]), source_spans=data["source_spans"],
                         paper_url=data["paper_url"], doi=data["doi"])
    assert validate_article(draft) == []
    assert package["formulae"][0]["latex"] == "x^2"
    assert "x^2" not in data["markdown"]


def test_local_review_rejects_wrong_factpack_before_writing(tmp_path):
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["canonical_id"] = "another-paper"
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        compile_notion_package(inputs, output_dir=tmp_path / "queue")
    assert not (tmp_path / "queue").exists()


def test_missing_figures_block_compilation(tmp_path):
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    inputs.figure_manifest_path.write_text(json.dumps({"canonical_id": inputs.canonical_id, "figures": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="no usable selected figures"):
        compile_notion_package(inputs, output_dir=tmp_path / "queue")
    assert not (tmp_path / "queue").exists()


def test_mismatched_arxiv_url_does_not_claim_blog_compatibility(tmp_path):
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, "arxiv:2601.00001", "https://arxiv.org/abs/2601.00002")
    with pytest.raises(ValueError, match="arXiv URL"):
        compile_notion_package(inputs, output_dir=tmp_path / "queue")


def test_review_package_with_both_identities_is_identity_ready(tmp_path):
    from paper_intake.notion_compiler import compile_notion_package
    inputs = _inputs(tmp_path, "arxiv:2601.00001", "https://aclanthology.org/2026.findings-acl.1001/")
    package = json.loads(compile_notion_package(inputs, output_dir=tmp_path / "queue").path.read_text(encoding="utf-8"))
    assert package["identity"]["kind"] == "both"
    assert package["identity_status"] == "ready"
    assert package["article_input"]["doi"] == "10.18653/v1/2026.findings-acl.1001"
    assert package["blog_validation_performed"] is False


def test_three_compilers_independently_compile_same_isolated_inputs(tmp_path, monkeypatch):
    import yaml
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["xhs_draft"] = {"title_literary": "Paper", "opening": "Intro", "sections": {"result": "Result"}}
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    # The isolated paper assets are intentionally outside the simulated checkout.
    monkeypatch.setattr(notes, "ROOT", tmp_path / "repo")
    monkeypatch.setattr(wechat, "ROOT", tmp_path / "repo")
    common = dict(canonical_id=inputs.canonical_id, parsed_dir=inputs.markdown_path.parent,
        pdf_path=inputs.pdf_path, figure_manifest_path=inputs.figure_manifest_path,
        paper_url=inputs.paper_url, pdf_url=inputs.pdf_url, code_url=inputs.code_url)
    xhs = notes.compile_note(inputs.fact_pack_path, notes_dir=tmp_path / "xhs", **common)
    wechat_path, _ = wechat.compile_wechat_package(inputs.fact_pack_path, queue_dir=tmp_path / "wechat", **common)
    notion = compile_notion_package(inputs, output_dir=tmp_path / "notion")
    xhs_data = yaml.safe_load(xhs.read_text(encoding="utf-8"))
    wechat_data = json.loads(wechat_path.read_text(encoding="utf-8"))
    notion_data = json.loads(notion.path.read_text(encoding="utf-8"))
    image = inputs.markdown_path.parent / "fig.png"
    assert Path(xhs_data["parsed_dir"]) == image.parent
    assert Path(xhs_data["pdf_path"]) == inputs.pdf_path
    assert Path(wechat_data["image_paths"][0]) == image
    assert image.as_posix() in wechat_data["metadata"]["wechat_html"]
    assert Path(notion_data["figures"][0]["path"]) == image
    assert xhs_data["body"] == wechat_data["body_markdown"]
    assert xhs_data["visual_review"] == wechat_data["review_status"] == notion_data["review_status"] == "pending"
    assert notion_data["notion_written"] is False


@pytest.mark.parametrize("platform", ["xhs", "wechat", "notion"])
def test_each_compiler_writes_without_other_platform_outputs(tmp_path, monkeypatch, platform):
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["xhs_draft"] = {"title_literary": "Paper", "sections": {"result": "Result"}}
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    monkeypatch.setattr(notes, "ROOT", tmp_path / "repo")
    monkeypatch.setattr(wechat, "ROOT", tmp_path / "repo")
    output = tmp_path / "output"
    if platform == "notion":
        path = compile_notion_package(inputs, output_dir=output).path
    else:
        common = dict(canonical_id=inputs.canonical_id, parsed_dir=inputs.markdown_path.parent,
            pdf_path=inputs.pdf_path, figure_manifest_path=inputs.figure_manifest_path,
            paper_url=inputs.paper_url, pdf_url=inputs.pdf_url, code_url=inputs.code_url)
        if platform == "xhs":
            path = notes.compile_note(inputs.fact_pack_path, notes_dir=output, **common)
        else:
            path, _ = wechat.compile_wechat_package(inputs.fact_pack_path, queue_dir=output, **common)
    assert path.is_file()
    assert list(output.rglob("*.yaml" if platform == "xhs" else "*.json")) == [path]


def test_factory_compiles_notion_from_shared_inputs_without_delivery(tmp_path, monkeypatch):
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    from content_factory.factory import ContentFactory

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["xhs_draft"] = {"title_literary": "Paper", "sections": {"result": "Result"}}
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    results = ContentFactory(tmp_path, tmp_path, tmp_path).compile_shared(inputs)
    assert results["notion"]["status"] == "compiled", results["notion"]
    package = json.loads(Path(results["notion"]["path"]).read_text(encoding="utf-8"))
    assert package["canonical_id"] == inputs.canonical_id
    assert package["notion_written"] is False
    assert results["notion"]["drafted"] is False


def test_notion_failure_does_not_erase_other_local_packages(tmp_path, monkeypatch):
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    import paper_intake.notion_compiler as notion
    from content_factory.factory import ContentFactory

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["xhs_draft"] = {"title_literary": "Paper", "sections": {"result": "Result"}}
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    def fail(*args, **kwargs):
        raise ValueError("notion compilation test failure")
    monkeypatch.setattr(notion, "compile_notion_package", fail)
    result = ContentFactory(tmp_path, tmp_path, tmp_path).compile_shared(inputs)
    assert result["notion"]["status"] == "failed"
    assert "notion compilation test failure" in result["notion"]["reason"]
    assert all(result[p]["status"] == "compiled" and Path(result[p]["path"]).is_file()
               for p in ("xhs", "wechat"))


def test_s5_stages_three_compilers_from_same_resolved_inputs(tmp_path, monkeypatch):
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    import scripts.content_bridge as bridge

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["xhs_draft"] = {"title_literary": "Paper", "sections": {"result": "Result"}}
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    monkeypatch.setattr(bridge, "ROOT", tmp_path)
    result = bridge._stage_platform_packages(inputs)
    assert set(result) == {"xhs", "wechat", "notion"}
    assert all(result[name]["status"] == "compiled" for name in result), result
    assert Path(result["notion"]["path"]).is_file()
    assert all(result[name]["drafted"] is False for name in result)


def test_s5_populates_common_input_from_exact_catalog_identity(tmp_path, monkeypatch):
    import sqlite3
    import scripts.content_bridge as bridge

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    db = tmp_path / "catalog.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE papers (canonical_id TEXT, paper_url TEXT, pdf_url TEXT)")
        connection.execute("INSERT INTO papers VALUES (?, ?, ?)",
            (inputs.catalog_canonical_id, inputs.paper_url, inputs.pdf_url))
    monkeypatch.setattr(bridge, "ROOT", tmp_path)
    result = bridge._prepare_compilation_inputs(inputs, inputs.fact_pack_path,
        {"figure_manifest_path": str(inputs.figure_manifest_path)}, db)
    assert result.fact_pack_path == inputs.fact_pack_path
    assert result.figure_manifest_path == inputs.figure_manifest_path
    assert result.paper_url == inputs.paper_url
    assert result.pdf_url == inputs.pdf_url


def test_s5_builds_pending_figure_manifest_from_parse_assets(tmp_path, monkeypatch):
    import sqlite3
    import scripts.content_bridge as bridge

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    images = inputs.markdown_path.parent / "images"
    images.mkdir()
    (inputs.markdown_path.parent / "fig.png").replace(images / "fig.png")
    db = tmp_path / "catalog.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE papers (canonical_id TEXT, paper_url TEXT, pdf_url TEXT)")
        connection.execute("INSERT INTO papers VALUES (?, ?, ?)",
            (inputs.catalog_canonical_id, inputs.paper_url, inputs.pdf_url))
    monkeypatch.setattr(bridge, "ROOT", tmp_path)
    result = bridge._prepare_compilation_inputs(inputs, inputs.fact_pack_path, {}, db)
    manifest = json.loads(result.figure_manifest_path.read_text(encoding="utf-8"))
    assert manifest["canonical_id"] == inputs.canonical_id
    assert manifest["figures"][0]["path"] == "images/fig.png"
    assert manifest["figures"][0]["visual_review"]["status"] == "pending"


def test_s5_consume_event_creates_notion_review_package(tmp_path, monkeypatch):
    import paper_intake.note_compiler as notes
    import paper_intake.wechat_compiler as wechat
    import scripts.content_bridge as bridge
    from paper_intake.catalog_store import CatalogRepository
    from paper_intake.repository import JobRepository
    from paper_intake.models import StepName

    inputs = _inputs(tmp_path, "2026.findings-acl.1001", "https://aclanthology.org/2026.findings-acl.1001/")
    pack = json.loads(inputs.fact_pack_path.read_text(encoding="utf-8"))
    pack["xhs_draft"] = {"title_literary": "Paper", "sections": {"result": "Result"}}
    inputs.fact_pack_path.write_text(json.dumps(pack), encoding="utf-8")
    db = tmp_path / "catalog.sqlite3"
    catalog = CatalogRepository(db)
    catalog._connection.execute(
        "INSERT INTO papers(canonical_id,status,title,paper_url,pdf_url,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
        (inputs.catalog_canonical_id, "discovered", "Paper", inputs.paper_url, inputs.pdf_url, "now", "now"))
    catalog._connection.commit()
    catalog.close()
    jobs = JobRepository(db)
    job = jobs.create_job(source_type="url", source_url=inputs.pdf_url)
    jobs.update_job(job.job_id, canonical_id=inputs.canonical_id, upload_path=str(inputs.pdf_path))
    jobs._connection.execute("UPDATE jobs SET catalog_canonical_id=? WHERE job_id=?",
                             (inputs.catalog_canonical_id, job.job_id))
    jobs._connection.commit()
    jobs.start_step(job.job_id, StepName.MINERU_PARSE)
    jobs.complete_step(job.job_id, StepName.MINERU_PARSE, output={"markdown_path": str(inputs.markdown_path)})
    jobs.close()
    monkeypatch.setattr(bridge, "ROOT", tmp_path)
    monkeypatch.setattr(bridge, "RUN_LOG", tmp_path / "logs" / "runs.jsonl")
    monkeypatch.setattr(notes, "ROOT", tmp_path)
    monkeypatch.setattr(wechat, "ROOT", tmp_path)
    monkeypatch.setattr(bridge, "ContentAssetManifest", lambda db: type("Manifest", (), {
        "lookup": lambda self, *args: {"relative_path": "fact.json"}})())
    monkeypatch.setattr(bridge, "ModelCallGatewayWithFallback", lambda *args, **kwargs: object())
    monkeypatch.setattr(bridge, "_advance_pool", lambda canonical_id, db: None)
    event = {"id": "evt-1", "payload_json": json.dumps({"canonical_id": inputs.canonical_id, "job_id": job.job_id,
        "markdown_path": str(inputs.markdown_path), "figure_manifest_path": str(inputs.figure_manifest_path)})}
    assert bridge._consume_event(event, dry_run=False, db_path=db) is True
    packages = list((tmp_path / "publish_queue" / "notion").glob("*/notion.json"))
    assert len(packages) == 1
    package = json.loads(packages[0].read_text(encoding="utf-8"))
    assert package["canonical_id"] == inputs.canonical_id
    assert package["job_id"] == job.job_id
    logs = (tmp_path / "logs" / "runs.jsonl").read_text(encoding="utf-8")
    assert "platform_compilation" in logs and "compiled" in logs



def test_manuscript_follows_the_five_section_site_spec(tmp_path):
    """No H1, five numbered sections, no stub text, references in ACL style."""
    from paper_intake.notion_compiler import compile_notion_package

    inputs = _inputs(tmp_path, "arxiv:2601.00001", "https://arxiv.org/abs/2601.00001")
    result = compile_notion_package(inputs, output_dir=tmp_path / "queue")
    package = json.loads(result.path.read_text(encoding="utf-8"))
    md = package["article_input"]["markdown"]

    assert not md.lstrip().startswith("# "), "正文不应重复标题"
    for heading in ("## 1 研究背景与问题", "## 2 方法：", "## 3 实验：",
                    "## 4 论文总结：", "## 5 References"):
        assert heading in md, heading
    assert "待核验" not in md
    assert "图示解释" not in md
    assert "## 论文总结" not in md.replace("## 4 论文总结", "")
    # 图后必须跟一段可读说明，而不是 caption 原文
    assert "该图展示整体流程" in md


def test_reference_line_matches_the_requested_academic_format():
    from paper_intake.notion_compiler import _render_reference

    line = _render_reference({
        "authors": ["Yueqi Wang", "Julian McAuley"],
        "year": "2026",
        "title": "OpticalRec: Unified Optical Vision-Language Representation",
        "paper_url": "https://arxiv.org/abs/2610.05432",
        "venue": "arXiv preprint arXiv:2610.05432",
        "code_url": "https://github.com/rlqja1107/SToP",
    })
    assert line == (
        "Yueqi Wang, and Julian McAuley. 2026. "
        "**[OpticalRec: Unified Optical Vision-Language Representation]"
        "(https://arxiv.org/abs/2610.05432)**. arXiv preprint arXiv:2610.05432. "
        "（代码：https://github.com/rlqja1107/SToP）"
    )


def test_reference_without_a_link_keeps_the_title_bold_but_plain():
    from paper_intake.notion_compiler import _render_reference

    line = _render_reference({"authors": ["OpenAI"], "year": "2026",
                              "title": "OpenAI gpt-5 system card",
                              "venue": "Preprint, arXiv:2601.03267"})
    assert line == "OpenAI. 2026. **OpenAI gpt-5 system card**. Preprint, arXiv:2601.03267."
