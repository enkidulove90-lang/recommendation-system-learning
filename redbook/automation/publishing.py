"""Chapter 4: platform-neutral content packages and explicit staging commands.

Supports: xhs, wechat, zhihu_answer, x_thread, jike, notion, blog.
Each platform has a render_* function that converts paper data to a
PublicationPackage with platform-specific body text and image count.
WeChatPublisher drives the WeChat editor through the OpenCLI browser bridge
(see ``redbook/infrastructure/wechat_delivery.py``); the legacy
``opencli weixin create-draft`` path was removed because its title-fill and
plain-text body caused the title to silently disappear and Markdown syntax to
show up literally in the saved draft.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Protocol

from .common import utc_now, write_json
from ..infrastructure import opencli_runtime
import subprocess


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
        # NOTE: the staged file lives under content_hash[:32] so that
        # ``publish(staged_id)`` (which reads publish_queue/<staged_id[:32]>/...)
        # finds it.  Keep this in lock-step with the publisher read paths.
        path = self.root / "publish_queue" / package.content_hash[:32] / f"{self.platform}.json"
        existing = path.exists() and json.loads(path.read_text(encoding="utf-8"))
        if existing and existing.get("content_hash") == package.content_hash:
            return {"ok": True, "status": "already_staged", "path": str(path), "staged_id": package.content_hash}
        write_json(path, {**package.as_dict(), "staged_at": utc_now()})
        return {"ok": True, "status": "staged", "path": str(path), "staged_id": package.content_hash}

    def publish(self, staged_id: str) -> dict[str, Any]:
        return {"ok": False, "status": "manual_review_required", "staged_id": staged_id}


class WeChatPublisher(FilePublisher):
    """微信公众号草稿投递器 — 只写入草稿箱，不群发。

    通过 :class:`WeChatDraftDelivery`（browser-bridge 驱动真实编辑器）创建图文草稿，
    标题/正文/封面/摘要 全部以浏览器真实事件写入。
    当 OpenCLI 不可用或编辑器未登录时，fallback 为本地 HTML 预览文件。
    """

    def __init__(self, root: Path) -> None:
        super().__init__("wechat", root)

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = super().validate(package)
        if len(package.title) > 64:
            errors.append("wechat title must be at most 64 characters")
        if len(package.body_markdown) < 200:
            errors.append("wechat body should be at least 200 characters for depth")
        if len(package.image_paths) > 9:
            errors.append("wechat supports at most 9 images per article")
        return errors

    def publish(self, staged_id: str) -> dict[str, Any]:
        """Drive a single WeChat draft to the草稿箱 through the browser bridge.

        Flow (mirrors ``redbook/infrastructure/wechat_delivery.py``):

        1. Build a :class:`WeChatDraftPayload` from the staged package.
        2. Hand it to :class:`WeChatDraftDelivery` which opens the editor in
           one persistent session, fills the title (verified), injects the
           body — the rich WeChat-safe HTML (``metadata.wechat_html``) when
           present, else the WeChat-flavored plain text — uploads + sets a
           cover image, fills the summary, and clicks 保存为草稿.
        3. If the editor was not logged in, fall back to an HTML preview so a
           usable artifact is always produced.

        Returns the delivery receipt (or HTML-preview fallback) plus a
        ``stage_error`` envelope when the editor step failed before saving.
        """
        path = self.root / "publish_queue" / staged_id[:32] / "wechat.json"
        if not path.exists():
            return {"ok": False, "error": f"staged package not found: {path}"}
        package_data = json.loads(path.read_text(encoding="utf-8"))

        # ── 公众号 HTML 合规门禁（发布前硬性校验）──
        gate = self._gzh_html_gate(package_data)
        if gate.get("block"):
            return gate

        if not opencli_runtime.is_available():
            return self._publish_html_preview(package_data)

        # Lazy import: keeps the module usable in environments without the
        # browser bridge installed (e.g. plain unit tests).
        from ..infrastructure.wechat_delivery import (
            DeliveryError as WeChatDeliveryError,
            WeChatDraftDelivery,
            WeChatDraftPayload,
        )

        metadata = package_data.get("metadata", {})
        cover = None
        images = [Path(p) for p in package_data.get("image_paths", [])]
        if images:
            cover = images[0]

        payload = WeChatDraftPayload(
            title=str(package_data["title"]),
            body_text=str(package_data["body_markdown"]),
            body_html=str(metadata.get("wechat_html", "")),
            cover_image=cover,
            summary=str(metadata.get("summary", "")),
            author=str(metadata.get("author", "")) or "推荐系统研读",
        )

        try:
            receipt = WeChatDraftDelivery().deliver(payload)
        except WeChatDeliveryError as exc:
            # Surface the editor-side error verbatim; reviewers see the same
            # message they would have seen in the browser console.
            return {
                "ok": False,
                "method": "browser-bridge",
                "error": str(exc),
                "stage_error": str(exc),
            }

        if not receipt.saved:
            # The editor accepted the inputs but the save marker never lit up.
            # Fall back to the HTML preview so the artifact isn't lost.
            preview = self._publish_html_preview(package_data)
            preview["save_unverified"] = True
            preview["note"] = (
                (preview.get("note") or "")
                + " 编辑器接受了输入但「已保存」标记未出现，已生成 HTML 预览。")
            return preview

        return {
            "ok": True,
            "method": "browser-bridge",
            "title": receipt.title,
            "cover_applied": receipt.cover_applied,
            "body_chars": receipt.body_chars,
            "status": "draft saved",
            "detail": (
                f"\"{receipt.title}\" by {payload.author}"
                + (" (with cover)" if receipt.cover_applied else "")
            ),
        }

    def _gzh_html_gate(self, data: dict[str, Any]) -> dict[str, Any]:
        """发布前硬性合规校验：正文 HTML 必须过 ``validate_gzh_html``。

        存在 ERROR（会被公众号过滤或粘贴后样式丢失）→ 阻断发布并返回原因；
        仅有 WARNING → 放行但记录，不阻断。校验器缺失（环境无 gzh-design skill）
        时不致命，仅告警放行。
        """
        html = (data.get("metadata", {}) or {}).get("wechat_html") or ""
        if not html:
            return {"block": False, "note": "no wechat_html to gate"}
        validator_dir = (
            Path(__file__).resolve().parents[2]
            / ".workbuddy" / "skills" / "gzh-design" / "scripts"
        )
        if not (validator_dir / "validate_gzh_html.py").is_file():
            return {"block": False, "warn": f"validator not found at {validator_dir}"}
        if str(validator_dir) not in sys.path:
            sys.path.insert(0, str(validator_dir))
        try:
            from validate_gzh_html import validate as _validate
        except Exception as exc:  # 校验器不可导入不致命
            return {"block": False, "warn": f"validator import failed: {exc}"}
        errors, warnings, _ = _validate(html, name=str(data.get("title", "wechat")))
        if errors:
            return {
                "ok": False, "block": True, "method": "gzh-gate",
                "error": "公众号 HTML 合规校验未通过，已阻断发布：\n"
                + "\n".join(f"  • {e}" for e in errors),
            }
        return {"block": False, "warnings": warnings}

    def _publish_html_preview(self, data: dict[str, Any]) -> dict[str, Any]:  # noqa: D401 — instance method keeps self.root
        """Fallback: write a self-contained HTML preview for manual upload.

        Renders the staged body_markdown (which is the WeChat-flavored plain
        text from :func:`paper_to_wechat.render_wechat_article`) so reviewers
        can eyeball the final shape without an mp.weixin.qq.com session.
        """
        preview_dir = self.root / "publish_preview" / "wechat"
        preview_dir.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(c for c in data["title"] if c.isalnum() or c in "._-")[:40]
        html_path = preview_dir / f"{safe_title}.html"

        body = str(data.get("body_markdown", ""))
        # Prefer the rich WeChat-safe HTML when present (render_wechat_html);
        # otherwise wrap the plain WeChat-flavored text into minimal <p>s.
        wechat_html = (data.get("metadata", {}) or {}).get("wechat_html")
        if wechat_html:
            body_html = wechat_html
        else:
            paragraphs = [p.strip() for p in re.split(r"\n{2,}", body) if p.strip()]
            body_html = "\n".join(
                f'<p style="margin:0 0 14px 0;line-height:1.85;">{p.replace(chr(10), "<br/>")}</p>'
                for p in paragraphs
            )
        images_html = ""
        for img in data.get("image_paths", [])[:7]:
            images_html += f'<img src="file:///{img}" style="max-width:100%;margin:8px 0;">\n'

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{data['title']}</title>
<style>
body {{ max-width:680px; margin:0 auto; padding:20px; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif; color:#222; }}
h1 {{ font-size:1.6em; line-height:1.4; margin:0 0 24px 0; }}
.cover {{ width:100%; border-radius:6px; margin-bottom:18px; }}
</style>
</head>
<body>
<h1>{data['title']}</h1>
{images_html}
{body_html}
<hr><p style="color:#888;font-size:0.9em;">图表摘自论文，仅作学术解读。</p>
</body></html>"""
        html_path.write_text(html_content, encoding="utf-8")
        return {
            "ok": True, "method": "html_preview", "path": str(html_path),
            "note": "browser bridge unavailable or save unverified; HTML preview generated for manual upload",
        }


class XhsPublisher(FilePublisher):
    """小红书发布器 — OpenCLI 是唯一写入通道。

    ``xhs-cli`` 的逆向签名路径已停用（见 ``redbook/config/opencli.yaml``）：
    它每次风控更新都会失效，而 OpenCLI 直接驱动已登录 Chrome 的创作者后台。

    投递顺序被平台约束固定为 **topics → PDF → draft**：话题必须在编辑器打开
    时绑定为真实话题实体（而非正文里的 ``#`` 文本），PDF 只能在笔记实体存在
    后经 CDP 附件通道上传，最后才落草稿。
    """

    def __init__(self, root: Path) -> None:
        super().__init__("xhs", root)

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = super().validate(package)
        if len(package.title) > 20:
            errors.append("xhs title must be at most 20 characters")
        if not package.image_paths:
            errors.append("xhs requires at least one image")
        if len(package.image_paths) > 9:
            errors.append("xhs supports at most 9 images per note")
        return errors

    def publish(self, staged_id: str) -> dict[str, Any]:
        """通过 OpenCLI 创建小红书草稿（可选附加 PDF）。"""
        path = self.root / "publish_queue" / staged_id[:32] / "xhs.json"
        if not path.exists():
            return {"ok": False, "error": f"staged package not found: {path}"}
        data = json.loads(path.read_text(encoding="utf-8"))

        if not opencli_runtime.is_available():
            return {
                "ok": False, "method": "none",
                "error": "OpenCLI not found; set OPENCLI_NODE and OPENCLI_MAIN",
            }
        return self._publish_opencli(data)

    def _publish_opencli(self, data: dict[str, Any]) -> dict[str, Any]:
        """通过 OpenCLI 创作者后台自动化创建草稿。

        参数契约来自 ``opencli xiaohongshu publish --help`` (v1.8.6)::

            opencli xiaohongshu publish <content> --title <t> [--images a,b,c]
                                        [--topics x,y] [--draft true]

        注意 ``--images`` 只接受 jpg/png/gif/webp，**不接受 PDF**；论文附件
        走 :class:`~redbook.infrastructure.xiaohongshu_delivery.OpenCliXiaohongshuDelivery`
        的 CDP 上传通道。
        """
        metadata = data.get("metadata", {})
        topics = [str(t).lstrip("#").strip() for t in metadata.get("topics", []) if str(t).strip()]
        images = [str(img) for img in data.get("image_paths", [])][:9]
        pdf_path = metadata.get("pdf_path")

        if pdf_path:
            return self._deliver_with_pdf(data, topics, images, Path(pdf_path))

        try:
            runtime = opencli_runtime.resolve_runtime()
        except opencli_runtime.OpenCliUnavailable as exc:
            return {"ok": False, "error": str(exc), "method": "opencli"}

        parts = [
            "xiaohongshu", "publish", str(data["body_markdown"]),
            "--title", str(data["title"])[:20],
            "--draft", "true",
        ]
        if images:
            parts.extend(["--images", ",".join(images)])
        if topics:
            parts.extend(["--topics", ",".join(topics[:10])])
        parts.extend([
            "--window", "foreground", "--site-session", "ephemeral", "--keep-tab", "false",
        ])

        try:
            result = runtime.run(*parts, "-f", "json", timeout=300)
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "error": str(exc), "method": "opencli"}
        stdout = (result.stdout or "").strip()
        if result.returncode != 0 or stdout.startswith("ok: false"):
            return {
                "ok": False, "error": (stdout or result.stderr or "")[:500],
                "method": "opencli", "returncode": result.returncode,
            }
        try:
            response = json.loads(stdout)
            # OpenCLI 的 publish 有时返回 list（如 [draft]）而非 dict
            if isinstance(response, list):
                response = response[0] if response else {}
            return {
                "ok": True, "method": "opencli",
                "draft_id": response.get("id", "") if isinstance(response, dict) else "",
                "topics": topics, "data": response,
            }
        except json.JSONDecodeError:
            return {"ok": True, "method": "opencli", "topics": topics, "raw_output": stdout[:500]}

    def _deliver_with_pdf(
        self, data: dict[str, Any], topics: list[str], images: list[str], pdf_path: Path
    ) -> dict[str, Any]:
        """Full topics → PDF → draft delivery, refusing to downgrade on failure."""
        from ..infrastructure.xiaohongshu_delivery import (
            DeliveryError, DraftPayload, OpenCliXiaohongshuDelivery,
        )

        payload = DraftPayload(
            title=str(data["title"])[:20],
            body=str(data["body_markdown"]),
            image_paths=tuple(Path(img) for img in images),
            topics=tuple(topics),
            pdf_path=pdf_path,
        )
        try:
            receipt = OpenCliXiaohongshuDelivery().deliver(payload)
        except DeliveryError as exc:
            return {"ok": False, "method": "opencli-cdp", "error": str(exc)}
        return {
            "ok": True, "method": "opencli-cdp", "draft_id": receipt.draft_id,
            "topics": list(receipt.topics), "image_count": receipt.image_count,
            "pdf_name": receipt.pdf_name,
        }


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
    elif platform == "wechat":
        body, images = _render_wechat(paper, title, summary, links, canonical_url)
    elif platform == "xhs":
        body, images = _render_xhs(paper, title, summary, links, canonical_url)
    else:
        body = f"# {title}\n\n{summary}\n\n## 论文与复现\n- 论文：{links.get('paper', canonical_url)}\n- PDF：{links.get('pdf', '')}\n- 代码：{links.get('code', '暂无官方代码')}"
        images = list(paper.get("images", []))[:7]
    return PublicationPackage(str(paper["paper_id"]), platform, canonical_url, title, body, images, {"paper": links.get("paper", canonical_url), "pdf": links.get("pdf", ""), "code": links.get("code", "")})


def _render_wechat(paper: dict[str, Any], title: str, summary: str, links: dict[str, str], canonical_url: str) -> tuple[str, list[str]]:
    """微信公众号：1,200-2,000 字深度图文。"""
    sections = []
    sections.append(f"# {title}\n")
    sections.append(f"## 背景\n{paper.get('background', summary[:300])}\n")
    sections.append(f"## 方法\n{paper.get('method_details', summary[:500])}\n")
    experiments = paper.get("experiments", "")
    if isinstance(experiments, list):
        experiments = "\n".join(f"- {e}" for e in experiments[:5])
    sections.append(f"## 实验\n{experiments or summary[:200]}\n")
    sections.append(f"## 局限性\n{paper.get('limitations', '详见原文。')}\n")
    sections.append(f"## 实践启发\n{paper.get('practical_insights', '本文方法可为推荐系统设计提供参考。')}\n")
    sections.append("## 参考文献\n")
    sections.append(f"- 论文：{links.get('paper', canonical_url)}")
    sections.append(f"- PDF：{links.get('pdf', '')}")
    code = links.get("code", "")
    sections.append(f"- 代码：{code if code else '暂无官方代码'}")
    sections.append(f"\n> 图表摘自论文，仅作学术解读。")
    body = "\n".join(sections)
    images = list(paper.get("images", []))[:7]
    return body, images


def _render_xhs(paper: dict[str, Any], title: str, summary: str, links: dict[str, str], canonical_url: str) -> tuple[str, list[str]]:
    """小红书：300-700 字 + emoji 分段。"""
    short_title = title[:20] if len(title) > 20 else title
    lines = []
    lines.append(f"{short_title}")
    lines.append("")
    lines.append(f"🎓 {summary[:150]}")
    lines.append("")
    innovation = paper.get("core_innovation", "")
    lines.append(f"✨ {innovation[:120] if innovation else summary[:120]}")
    lines.append("")
    method = paper.get("method_details", "")
    if method:
        for bullet in method.split("\n")[:3]:
            bullet = bullet.strip()
            if bullet:
                lines.append(f"🧠 {bullet[:80]}")
        lines.append("")
    experiments = paper.get("experiments", "")
    if isinstance(experiments, list):
        exp_str = " ".join(str(e)[:60] for e in experiments[:3])
    else:
        exp_str = str(experiments)[:150]
    lines.append(f"📊 {exp_str}")
    lines.append("")
    insights = paper.get("practical_insights", "")
    if insights:
        lines.append(f"💡 {insights[:100]}")
        lines.append("")
    lines.append(f"arxiv 🔗：{links.get('paper', canonical_url)}")
    pdf_link = links.get("pdf", "")
    if pdf_link:
        lines.append(f"📎 原文 PDF：{pdf_link}")
    code = links.get("code", "")
    if code:
        lines.append(f"github 🔗：{code}")
    images = list(paper.get("images", []))[:5]
    return "\n".join(lines), images
