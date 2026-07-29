"""Chapter 4: platform-neutral content packages and explicit staging commands."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Protocol

from .common import utc_now, write_json


@dataclass
class PublicationPackage:
    paper_id: str
    platform: str
    canonical_url: str
    title: str
    body_markdown: str
    image_paths: list[str]
    links: dict[str, str]
    review_status: str = "pending"
    source_attribution: str = "图表摘自论文，仅作学术解读。"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        payload = json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["content_hash"] = self.content_hash
        return value


class Publisher(Protocol):
    platform: str

    def validate(self, package: PublicationPackage) -> list[str]: ...
    def stage(self, package: PublicationPackage) -> dict[str, Any]: ...
    def publish(self, staged_id: str) -> dict[str, Any]: ...


class FilePublisher:
    """Safe default: write an immutable review package, never contacts platforms."""

    def __init__(self, platform: str, root: Path) -> None:
        self.platform, self.root = platform, root

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = []
        if package.platform != self.platform:
            errors.append("package platform does not match publisher")
        if not package.paper_id or not package.title or not package.body_markdown:
            errors.append("paper_id, title, and body_markdown are required")
        if not package.links.get("paper") or not package.links.get("pdf"):
            errors.append("paper and pdf links are required")
        return errors

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "errors": errors}
        path = self.root / "publish_queue" / package.paper_id.replace(":", "_") / f"{self.platform}.json"
        existing = path.exists() and json.loads(path.read_text(encoding="utf-8"))
        if existing and existing.get("content_hash") == package.content_hash:
            return {"ok": True, "status": "already_staged", "path": str(path), "staged_id": package.content_hash}
        write_json(path, {**package.as_dict(), "staged_at": utc_now()})
        return {"ok": True, "status": "staged", "path": str(path), "staged_id": package.content_hash}

    def publish(self, staged_id: str) -> dict[str, Any]:
        return {"ok": False, "status": "manual_review_required", "staged_id": staged_id}


def render_package(paper: dict[str, Any], platform: str, canonical_url: str) -> PublicationPackage:
    title = str(paper["title"])
    links = dict(paper.get("links", {}))
    summary = str(paper.get("summary", "")).strip()
    if platform == "x_thread":
        body = f"{title}\n\n{summary[:220]}\n\nPaper: {links.get('paper', canonical_url)}"
        images = list(paper.get("images", []))[:4]
    elif platform == "jike":
        body = f"{title}\n{summary[:180]}\n{canonical_url}"
        images = []
    elif platform == "zhihu_answer":
        body = f"先说结论：{summary}\n\n论文：{links.get('paper', canonical_url)}\nPDF：{links.get('pdf', '')}\n代码：{links.get('code', '暂无官方代码')}"
        images = list(paper.get("images", []))[:3]
    else:
        body = f"# {title}\n\n{summary}\n\n## 论文与复现\n- 论文：{links.get('paper', canonical_url)}\n- PDF：{links.get('pdf', '')}\n- 代码：{links.get('code', '暂无官方代码')}"
        images = list(paper.get("images", []))[:7]
    return PublicationPackage(str(paper["paper_id"]), platform, canonical_url, title, body, images, {"paper": links.get("paper", canonical_url), "pdf": links.get("pdf", ""), "code": links.get("code", "")})
