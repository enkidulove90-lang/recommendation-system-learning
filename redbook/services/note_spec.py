"""小红书论文帖的声明式 note spec（``redbook/notes/<paper_id>.yaml``）。

每篇论文只新增一个 YAML，不再新增根目录脚本。spec 只声明「这一篇不同的东西」：
标题、人工定稿正文、图序与图注、话题、链接、PDF 与目检记录；执行骨架统一由
``PaperCreationWorkflow`` + ``render_post`` + ``XhsPublisher`` 提供。

路径约定（跨机器关键）
--------------------
- ``parsed_dir`` / ``pdf_path`` 相对**仓库根**，绝不由 cwd 解析（旧脚本用
  ``ROOT = Path(".")``，换机器或换工作目录就会断）。
- ``figures[].file`` 相对 ``parsed_dir``。
- 图片文件存在性只在 stage 检查；validate 只跑内容闸门。原因是
  ``data/parsed/**/*.png`` 被 .gitignore 挡掉，另一台机器 clone 后天然没有图，
  若 validate 强制检查会全红，闸门就失去意义。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

#: redbook/services/note_spec.py -> parents[2] 是仓库根。
REPO_ROOT = Path(__file__).resolve().parents[2]
NOTES_DIR = Path(__file__).resolve().parents[1] / "notes"

STATUSES = frozenset({"draft", "validated", "staged", "published"})
REQUIRED_FIELDS = ("paper_id", "title", "body", "parsed_dir", "figures", "topics", "links")


class NoteSpecError(ValueError):
    """spec 缺字段、类型不对或状态非法；不静默降级成半合规草稿。"""


@dataclass(frozen=True)
class NoteFigure:
    file: str
    type: str = ""
    description: str = ""


@dataclass(frozen=True)
class NoteSpec:
    paper_id: str
    title: str
    body: str
    parsed_dir: str
    figures: tuple[NoteFigure, ...]
    topics: tuple[str, ...]
    links: dict[str, str]
    pdf_path: str = ""
    visual_review: str = ""
    status: str = "draft"
    source: str = "handwritten"
    review_status: str = "pending"
    slug: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    @property
    def canonical_url(self) -> str:
        return str(self.links.get("paper", ""))

    def image_paths(self, root: Path | None = None) -> list[str]:
        base = (root or REPO_ROOT) / self.parsed_dir
        return [str(base / figure.file) for figure in self.figures]

    def resolved_pdf_path(self, root: Path | None = None) -> str | None:
        if not self.pdf_path:
            return None
        return str((root or REPO_ROOT) / self.pdf_path)

    def as_post_kwargs(self, root: Path | None = None) -> dict[str, Any]:
        """交给 ``render_post`` 的参数；定稿正文走 body 分支，不过 persona 模板。"""
        return {
            "body": self.body,
            "title": self.title,
            "arxiv_id": self.paper_id,
            "topics": list(self.topics),
            "figures": self.image_paths(root),
            "visual_review": self.visual_review,
            "metadata": dict(self.metadata),
            "source": self.source,
        }


def note_path(paper_id: str, notes_dir: Path | None = None) -> Path:
    return (notes_dir or NOTES_DIR) / f"{paper_id}.yaml"


def load_note(paper_id: str, notes_dir: Path | None = None) -> NoteSpec:
    """加载并校验一篇 note spec；字段缺失直接报错，避免静默产出半合规草稿。"""
    path = note_path(paper_id, notes_dir)
    if not path.is_file():
        raise NoteSpecError(f"note spec not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
        raise NoteSpecError(f"note spec must be a YAML mapping: {path}")
    missing = [key for key in REQUIRED_FIELDS if not data.get(key)]
    if missing:
        raise NoteSpecError(f"note spec {path.name} missing fields: {', '.join(missing)}")
    # 同一篇论文可能有多个版本（ACE 原稿/v2、TMLR CoT 原稿/v2）。
    # 文件名 stem 即 slug；声明了 slug 时用它匹配，否则回退到 paper_id。
    declared = str(data.get("slug") or data.get("paper_id"))
    if declared != str(paper_id):
        raise NoteSpecError(f"paper_id mismatch: {declared!r} != {paper_id!r} ({path.name})")
    if data.get("status", "draft") not in STATUSES:
        raise NoteSpecError(f"invalid status {data.get('status')!r}; allowed: {sorted(STATUSES)}")
    if not isinstance(data["links"], Mapping) or not data["links"].get("paper") or not data["links"].get("pdf"):
        raise NoteSpecError(f"links must provide non-empty paper and pdf URLs: {path.name}")

    raw_figures = data["figures"]
    if not isinstance(raw_figures, Sequence) or isinstance(raw_figures, (str, bytes)) or not raw_figures:
        raise NoteSpecError(f"figures must be a non-empty list: {path.name}")
    figures: list[NoteFigure] = []
    for index, item in enumerate(raw_figures):
        if not isinstance(item, Mapping) or not item.get("file"):
            raise NoteSpecError(f"figures[{index}] needs a 'file': {path.name}")
        figures.append(NoteFigure(
            file=str(item["file"]),
            type=str(item.get("type", "")),
            description=str(item.get("description", "")),
        ))

    topics = data["topics"]
    if not isinstance(topics, Sequence) or isinstance(topics, (str, bytes)):
        raise NoteSpecError(f"topics must be a list: {path.name}")
    return NoteSpec(
        # 真实论文 id 来自 spec 字段；参数 paper_id 只是文件名 stem（slug）。
        paper_id=str(data["paper_id"]),
        title=str(data["title"]),
        body=str(data["body"]),
        parsed_dir=str(data["parsed_dir"]),
        figures=tuple(figures),
        topics=tuple(str(item) for item in topics),
        links={str(key): str(value) for key, value in data["links"].items()},
        pdf_path=str(data.get("pdf_path", "")),
        visual_review=str(data.get("visual_review", "")),
        status=str(data.get("status", "draft")),
        source=str(data.get("source", "handwritten")),
        review_status=str(data.get("review_status", "pending")),
        slug=str(paper_id),
        metadata=dict(data.get("metadata") or {}),
        path=path,
    )


def list_notes(notes_dir: Path | None = None) -> list[dict[str, Any]]:
    """按 paper_id 排序列出全部 spec，供 ``redbook.cli note --list`` 使用。"""
    directory = notes_dir or NOTES_DIR
    if not directory.is_dir():
        return []
    result: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        try:
            spec = load_note(path.stem, directory)
        except NoteSpecError as error:
            result.append({"paper_id": path.stem, "status": "invalid", "error": str(error), "path": str(path)})
            continue
        result.append({
            "paper_id": spec.paper_id,
            "slug": path.stem,
            "title": spec.title,
            "status": spec.status,
            "figures": len(spec.figures),
            "visual_review": bool(spec.visual_review.strip()),
            "path": str(path),
        })
    return result
