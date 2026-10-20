"""Real, approval-safe platform adapters built around ``validate -> stage -> receipt``.

Only a platform operation that has a non-public staging primitive is allowed to
write remotely.  This makes the distinction explicit: WeChat can create a
creator draft and Notion/GitHub can create a canonical staging artifact, while
Zhihu, X and Jike expose only public-write commands and are deliberately kept
at a candidate/composer package until a separate approval workflow exists.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .common import utc_now, write_json
from .content_operations import PaperCardStore
from .publishing import PublicationPackage


class PlatformAdapterError(RuntimeError):
    """A platform operation cannot safely be staged."""


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]
HttpJson = Callable[[str, str, dict[str, str], dict[str, Any]], dict[str, Any]]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def _http_json(method: str, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(url, data=json.dumps(payload).encode("utf-8"), method=method)
    for name, value in headers.items():
        request.add_header(name, value)
    try:
        with urlopen(request, timeout=30) as response:  # nosec B310: configured official API endpoint
            return dict(json.loads(response.read().decode("utf-8")))
    except (HTTPError, URLError, json.JSONDecodeError) as error:
        raise PlatformAdapterError(f"platform HTTP request failed: {error}") from error


def _opencli() -> str | None:
    return shutil.which("opencli.cmd") or shutil.which("opencli")


def _gh() -> str | None:
    """Resolve a freshly winget-installed GitHub CLI before PATH refreshes."""
    configured = os.getenv("REDBOOK_GH_PATH")
    candidates = (configured, shutil.which("gh"), shutil.which("gh.exe"), r"C:\Program Files\GitHub CLI\gh.exe")
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


def _safe_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in value)


def _evidence(card: dict[str, Any], key: str) -> list[str]:
    return [str(value).strip() for value in dict(card.get("evidence", {})).get(key, []) if str(value).strip()]


def _markdown_page(card: dict[str, Any], canonical_url: str) -> str:
    identity, links = dict(card["identity"]), dict(card["links"])
    venue = dict(identity.get("venue", {}))
    blocks = [
        f"# {identity['title']}",
        "",
        f"Canonical URL: {canonical_url}",
        f"Venue: {venue.get('name', '')} {venue.get('year', '')} ({venue.get('status', '')})",
        "",
    ]
    for label, key in (("What problem does it address?", "problem"), ("Contributions", "contributions"),
                       ("Method", "method"), ("Evidence and results", "results"), ("Limitations", "limitations")):
        values = _evidence(card, key)
        if values:
            blocks.extend([f"## {label}", *(f"- {value}" for value in values), ""])
    blocks.extend((
        "## Sources and reproduction",
        f"- Paper: {links['landing']}",
        f"- PDF: {links['pdf']}",
        f"- Official GitHub: {links['official_github']}",
        "",
        "Figures are reproduced from the linked paper for research communication.",
    ))
    return "\n".join(blocks)


def package_from_paper_card(card_path: Path, platform: str, canonical_url: str) -> PublicationPackage:
    """Render a platform package only from the validated canonical fact card."""
    card = PaperCardStore.load(card_path, require_delivery_assets=False)
    identity, links, assets = dict(card["identity"]), dict(card["links"]), dict(card["assets"])
    title = str(identity["title"])
    problem, contributions, results, limitations = (_evidence(card, name) for name in
                                                      ("problem", "contributions", "results", "limitations"))
    claim = (results or contributions or problem or [title])[0]
    if platform == "wechat":
        body = _markdown_page(card, canonical_url)
        images = [str(row["path"]) for row in assets.get("figures", [])[:7]]
    elif platform == "zhihu":
        body = "\n\n".join((claim, *contributions, *results, "Sources", f"Paper: {links['landing']}",
                               f"PDF: {links['pdf']}", f"Official GitHub: {links['official_github']}",
                               *(f"Boundary: {item}" for item in limitations)))
        images = [str(row["path"]) for row in assets.get("figures", [])[:3]]
    elif platform == "x":
        body = f"{claim}\n\nPaper: {links['landing']}\nCode: {links['official_github']}"
        images = [str(row["path"]) for row in assets.get("figures", [])[:1]]
    elif platform == "jike":
        body = f"{claim}\n\n{links['landing']}\n{links['official_github']}"
        images = []
    elif platform == "bilibili":
        body = "\n".join((f"Topic: {title}", f"Hook: {claim}", "Script outline:",
                            "1. Explain the problem with one paper figure.",
                            "2. Explain the method with the architecture figure.",
                            "3. Present only author-reported results and limitations.",
                            f"Sources: {links['landing']} | {links['official_github']}"))
        images = [str(row["path"]) for row in assets.get("figures", [])[:3]]
    else:  # notion and github_pages
        body = _markdown_page(card, canonical_url)
        images = [str(row["path"]) for row in assets.get("figures", [])]
    return PublicationPackage(
        paper_id=str(card["paper_id"]), platform=platform, canonical_url=canonical_url,
        title=title[:64] if platform == "wechat" else title,
        body_markdown=body, image_paths=images,
        links={"paper": str(links["landing"]), "pdf": str(links["pdf"]), "code": str(links["official_github"])},
        metadata={"paper_card": str(card_path), "paper_card_hash": card["content_hash"], "mode": "stage_only"},
    )


@dataclass(frozen=True)
class PlatformReceipt:
    platform: str
    paper_id: str
    content_hash: str
    state: str
    external_id: str | None
    external_url: str | None
    detail: str
    created_at: str
    artifact_path: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class PlatformAdapter:
    """Base adapter. ``publish`` is intentionally incapable of public writes."""

    platform: str

    def __init__(self, root: Path, *, runner: Runner = _run) -> None:
        self.root, self.runner = root, runner

    def validate(self, package: PublicationPackage) -> list[str]:
        errors: list[str] = []
        if package.platform != self.platform:
            errors.append("package platform does not match adapter")
        if not package.paper_id or not package.title or not package.body_markdown:
            errors.append("paper_id, title, and body_markdown are required")
        if not package.canonical_url.startswith(("https://", "http://")):
            errors.append("canonical_url must be an http(s) URL")
        for name in ("paper", "pdf", "code"):
            if not package.links.get(name):
                errors.append(f"links.{name} is required")
        return errors

    def _receipt_path(self, package: PublicationPackage) -> Path:
        return self.root / "publish_results" / self.platform / f"{package.content_hash}.json"

    def _saved(self, package: PublicationPackage) -> dict[str, Any] | None:
        path = self._receipt_path(package)
        if not path.is_file():
            return None
        receipt = json.loads(path.read_text(encoding="utf-8"))
        # A failed attempt has no external stage to protect.  Retrying it must
        # be possible after a transient browser, encoding, or login repair.
        return receipt if receipt.get("state") in {"staged", "manual_action_required"} else None

    def _receipt(self, package: PublicationPackage, state: str, detail: str, *, external_id: str | None = None,
                 external_url: str | None = None, artifact_path: Path | None = None) -> dict[str, Any]:
        receipt = PlatformReceipt(self.platform, package.paper_id, package.content_hash, state, external_id,
                                  external_url, detail, utc_now(), str(artifact_path) if artifact_path else None)
        path = self._receipt_path(package)
        write_json(path, receipt.as_dict())
        return receipt.as_dict() | {"ok": state in {"staged", "manual_action_required"}, "receipt": str(path)}

    def _artifact(self, package: PublicationPackage, extension: str = "json") -> Path:
        path = self.root / "publish_queue" / _safe_name(package.paper_id) / f"{self.platform}.{extension}"
        if extension == "md":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(package.body_markdown, encoding="utf-8")
        else:
            write_json(path, package.as_dict())
        return path

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "state": "invalid", "errors": errors}
        if existing := self._saved(package):
            return {"ok": True, "state": "already_staged", **existing, "receipt": str(self._receipt_path(package))}
        artifact = self._artifact(package)
        return self._receipt(package, "manual_action_required", "platform has no safe draft primitive", artifact_path=artifact)

    def publish(self, staged_id: str, *, approval_id: str | None = None) -> dict[str, Any]:
        return {"ok": False, "state": "approval_required", "staged_id": staged_id,
                "detail": "Public publishing is intentionally implemented in a separate approved operation."}


class GitHubPagesAdapter(PlatformAdapter):
    platform = "github_pages"

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = super().validate(package)
        repo, branch = os.getenv("REDBOOK_GITHUB_PAGES_REPO"), os.getenv("REDBOOK_GITHUB_PAGES_BRANCH", "redbook-staging")
        if not repo or "/" not in repo:
            errors.append("REDBOOK_GITHUB_PAGES_REPO=owner/repo is required")
        if branch in {"main", "master", "gh-pages"}:
            errors.append("REDBOOK_GITHUB_PAGES_BRANCH must be a non-public staging branch")
        executable = _gh()
        if not executable:
            errors.append("GitHub CLI gh is required and must be authenticated")
        elif self.runner([executable, "auth", "status"]).returncode:
            errors.append("GitHub CLI is not authenticated; run gh auth login manually")
        elif repo:
            private = self.runner([executable, "api", f"repos/{repo}", "--jq", ".private"])
            if private.returncode or private.stdout.strip().casefold() != "true":
                errors.append("REDBOOK_GITHUB_PAGES_REPO must point to a private staging repository")
        return errors

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "state": "invalid", "errors": errors}
        if existing := self._saved(package):
            return {"ok": True, "state": "already_staged", **existing, "receipt": str(self._receipt_path(package))}
        repo, branch = os.environ["REDBOOK_GITHUB_PAGES_REPO"], os.getenv("REDBOOK_GITHUB_PAGES_BRANCH", "redbook-staging")
        branch_error = self._ensure_staging_branch(repo, branch)
        if branch_error:
            return self._receipt(package, "failed", branch_error)
        relative = f"{os.getenv('REDBOOK_GITHUB_PAGES_PATH', 'content/papers').strip('/')}/{_safe_name(package.paper_id)}.md"
        encoded = base64.b64encode(package.body_markdown.encode("utf-8")).decode("ascii")
        command = [_gh() or "gh", "api", f"repos/{repo}/contents/{relative}", "--method", "PUT", "-f", f"message=stage canonical paper {package.paper_id}",
                   "-f", f"content={encoded}", "-f", f"branch={branch}"]
        result = self.runner(command)
        if result.returncode:
            return self._receipt(package, "failed", result.stderr or result.stdout or "GitHub staging failed")
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            response = {}
        content = dict(response.get("content", {})); commit = dict(response.get("commit", {}))
        return self._receipt(package, "staged", "canonical Markdown committed to a non-public staging branch",
                             external_id=str(commit.get("sha", "")) or None, external_url=str(content.get("html_url", "")) or None)

    def _ensure_staging_branch(self, repo: str, branch: str) -> str | None:
        """Create a staging branch from the repository default branch when needed."""
        executable = _gh() or "gh"
        exists = self.runner([executable, "api", f"repos/{repo}/git/ref/heads/{branch}"])
        if not exists.returncode:
            return None
        default = self.runner([executable, "api", f"repos/{repo}", "--jq", ".default_branch"])
        if default.returncode or not default.stdout.strip():
            # A newly created private repository has no refs at all.  Seed a
            # harmless marker on its private default branch, then build the
            # actual content branch from that commit.  This never targets a
            # public repository or a Pages source branch.
            if "repository is empty" in (default.stderr + default.stdout).casefold():
                marker = base64.b64encode(b"private redbook canonical staging repository\n").decode("ascii")
                bootstrap = self.runner([
                    executable, "api", f"repos/{repo}/contents/.redbook-staging", "--method", "PUT",
                    "-f", "message=initialize private redbook staging repository", "-f", f"content={marker}",
                ])
                if bootstrap.returncode:
                    return bootstrap.stderr or bootstrap.stdout or "could not initialize the private GitHub staging repository"
                return self._ensure_staging_branch(repo, branch)
            return default.stderr or default.stdout or "could not discover the GitHub repository default branch"
        source_branch = default.stdout.strip()
        source = self.runner([executable, "api", f"repos/{repo}/git/ref/heads/{source_branch}"])
        if source.returncode:
            if "repository is empty" in (source.stderr + source.stdout).casefold():
                marker = base64.b64encode(b"private redbook canonical staging repository\n").decode("ascii")
                bootstrap = self.runner([
                    executable, "api", f"repos/{repo}/contents/.redbook-staging", "--method", "PUT",
                    "-f", "message=initialize private redbook staging repository", "-f", f"content={marker}",
                ])
                if bootstrap.returncode:
                    return bootstrap.stderr or bootstrap.stdout or "could not initialize the private GitHub staging repository"
                return self._ensure_staging_branch(repo, branch)
            return source.stderr or source.stdout or "could not read the GitHub default branch reference"
        try:
            sha = str(json.loads(source.stdout)["object"]["sha"])
        except (KeyError, TypeError, json.JSONDecodeError):
            return "GitHub default branch reference did not return a commit SHA"
        created = self.runner([executable, "api", f"repos/{repo}/git/refs", "--method", "POST", "-f", f"ref=refs/heads/{branch}", "-f", f"sha={sha}"])
        if created.returncode:
            return created.stderr or created.stdout or "could not create the non-public GitHub staging branch"
        return None


class NotionAdapter(PlatformAdapter):
    platform = "notion"

    def __init__(self, root: Path, *, http_json: HttpJson = _http_json, runner: Runner = _run) -> None:
        super().__init__(root, runner=runner); self.http_json = http_json

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = super().validate(package)
        if not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_PARENT_PAGE_ID"):
            errors.append("NOTION_TOKEN and NOTION_PARENT_PAGE_ID are required")
        return errors

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "state": "invalid", "errors": errors}
        if existing := self._saved(package):
            return {"ok": True, "state": "already_staged", **existing, "receipt": str(self._receipt_path(package))}
        paragraphs = [line for line in package.body_markdown.splitlines() if line.strip()]
        blocks = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": line[:1900]}}]}}
                  for line in paragraphs]
        payload = {"parent": {"page_id": os.environ["NOTION_PARENT_PAGE_ID"]},
                   "properties": {"title": {"title": [{"type": "text", "text": {"content": package.title[:200]}}]}},
                   "children": blocks[:100]}
        response = self.http_json("POST", "https://api.notion.com/v1/pages",
                                  {"Authorization": f"Bearer {os.environ['NOTION_TOKEN']}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}, payload)
        if response.get("object") == "error":
            return self._receipt(package, "failed", str(response.get("message", "Notion stage failed")))
        return self._receipt(package, "staged", "Notion canonical page created; sharing remains workspace-controlled",
                             external_id=str(response.get("id", "")) or None, external_url=str(response.get("url", "")) or None)


class WeChatDraftAdapter(PlatformAdapter):
    platform = "wechat"

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = super().validate(package)
        if len(package.title) > 64:
            errors.append("WeChat title exceeds 64 characters")
        if not package.image_paths:
            errors.append("WeChat draft requires at least one local cover image")
        if not _opencli():
            errors.append("OpenCLI weixin create-draft is not installed")
        return errors

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "state": "invalid", "errors": errors}
        if existing := self._saved(package):
            return {"ok": True, "state": "already_staged", **existing, "receipt": str(self._receipt_path(package))}
        # Windows ``.cmd`` launchers can split a multiline positional argument
        # before parsing later flags.  Put all required flags first and the
        # article body last so the title/cover are received before rich text.
        command = [_opencli() or "opencli", "weixin", "create-draft", "--title", package.title,
                   "--cover-image", package.image_paths[0], "--summary", package.body_markdown.replace("\n", " ")[:120],
                   "-f", "json", "--window", "foreground", "--site-session", "persistent", "--keep-tab", "true", package.body_markdown]
        result = self.runner(command)
        if result.returncode:
            return self._receipt(package, "failed", result.stderr or result.stdout or "WeChat draft creation failed")
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            response = {"raw": result.stdout.strip()}
        return self._receipt(package, "staged", "WeChat creator draft saved; it was not published",
                             external_id=str(response.get("draft_id") or response.get("id") or "") or None)


class ZhihuAnswerAdapter(PlatformAdapter):
    platform = "zhihu"

    def validate(self, package: PublicationPackage) -> list[str]:
        errors = super().validate(package)
        if not _opencli():
            errors.append("OpenCLI zhihu search is not installed")
        return errors

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "state": "invalid", "errors": errors}
        if existing := self._saved(package):
            return {"ok": True, "state": "already_staged", **existing, "receipt": str(self._receipt_path(package))}
        query = str(package.metadata.get("zhihu_query") or package.title)
        result = self.runner([_opencli() or "opencli", "zhihu", "search", query, "--type", "question", "--limit", "10", "-f", "json", "--window", "background", "--site-session", "persistent", "--keep-tab", "true"])
        artifact = self._artifact(package)
        if result.returncode:
            return self._receipt(package, "failed", result.stderr or result.stdout or "Zhihu question search failed", artifact_path=artifact)
        try:
            candidates = json.loads(result.stdout)
        except json.JSONDecodeError:
            candidates = []
        package_data = package.as_dict() | {"zhihu_question_candidates": candidates, "publication_guard": "OpenCLI answer is a public write; no answer was sent."}
        write_json(artifact, package_data)
        return self._receipt(package, "manual_action_required", "question candidates fetched; select one and approve a separate public-answer operation", artifact_path=artifact)


class ComposerOnlyAdapter(PlatformAdapter):
    """X, Jike and Bilibili lack a safe remote draft primitive in the configured toolchain."""

    instruction: str

    def stage(self, package: PublicationPackage) -> dict[str, Any]:
        errors = self.validate(package)
        if errors:
            return {"ok": False, "state": "invalid", "errors": errors}
        if existing := self._saved(package):
            return {"ok": True, "state": "already_staged", **existing, "receipt": str(self._receipt_path(package))}
        artifact = self._artifact(package)
        return self._receipt(package, "manual_action_required", self.instruction, artifact_path=artifact)


class XAdapter(ComposerOnlyAdapter):
    platform = "x"
    instruction = "X provides only direct public post commands in this toolchain; review the thread package before any separately approved publish."


class JikeAdapter(ComposerOnlyAdapter):
    platform = "jike"
    instruction = "Jike provides only a direct public create command in this toolchain; review the short-post package before any separately approved publish."


class BilibiliAdapter(ComposerOnlyAdapter):
    platform = "bilibili"
    instruction = "Bilibili receives a topic and video-script package only; no automated publishing adapter is enabled."


ADAPTERS: dict[str, type[PlatformAdapter]] = {
    "github_pages": GitHubPagesAdapter, "notion": NotionAdapter, "wechat": WeChatDraftAdapter,
    "zhihu": ZhihuAnswerAdapter, "x": XAdapter, "jike": JikeAdapter, "bilibili": BilibiliAdapter,
}


def adapter_for(platform: str, root: Path) -> PlatformAdapter:
    try:
        return ADAPTERS[platform](root)
    except KeyError as error:
        raise PlatformAdapterError(f"unsupported platform adapter: {platform}") from error


def platform_doctor(root: Path) -> dict[str, Any]:
    """Report real backend prerequisites without sending any platform write."""
    output: dict[str, Any] = {"generated_at": utc_now(), "opencli": _opencli(), "platforms": {}}
    placeholder = PublicationPackage("diagnostic", "", "https://example.invalid/canonical", "diagnostic", "body", ["cover.png"],
                                     {"paper": "https://example.invalid/paper", "pdf": "https://example.invalid/pdf", "code": "https://example.invalid/code"})
    for name, adapter_type in ADAPTERS.items():
        package = PublicationPackage(**(placeholder.__dict__ | {"platform": name}))
        adapter = adapter_type(root)
        errors = adapter.validate(package)
        output["platforms"][name] = {"ready_for_stage": not errors, "missing_or_blocked": errors,
                                     "public_publish": "separate manual approval required"}
    return output
