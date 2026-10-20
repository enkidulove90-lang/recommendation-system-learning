#!/usr/bin/env python3
"""Rewrite weak paper-site posts with evidence-backed Chinese long-form articles."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI


TARGET_MARKERS = (
    "## 方法：核心思路与整体框架",
    "## 创新点",
    "## 实验：数据、基线与结果",
    "原图说明：",
    "**图示解释：**",
)
CORE_TEMPLATE_MARKERS = (
    "## 方法：核心思路与整体框架",
    "## 创新点",
    "## 实验：数据、基线与结果",
)
BAD_OUTPUT_MARKERS = TARGET_MARKERS + (
    "这张图用于补充论文的核心方法或实验结论",
    "具体符号与数值以原文图注为准",
)
IMAGE = re.compile(r"!\[([^\]]*)\]\((/images/papers/[^)]+)\)")
ARXIV_ID = re.compile(r"(?m)^arxiv_id:\s*[\"']?([^\"'\s]+)")
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RESOURCE_LINE = re.compile(r"(?m)^>\s+.+$")
HEADING = re.compile(r"(?m)^#{1,3}\s+(.+?)\s*$")
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?%?")
TABLE_SEPARATOR = re.compile(r"(?m)^\|(?:\s*:?-+:?\s*\|){2,}\s*$")
PRINT_LOCK = threading.Lock()


SYSTEM_PROMPT = """你是一位严谨的中文科技编辑，负责把论文材料改写为个人学术网站的长文。

输出必须是合法 JSON：
{
  "title": "有信息量、有记忆点的中文标题，保留方法简称",
  "description": "一句话说明问题、机制与最关键证据",
  "body_markdown": "完整 Markdown 正文，不含 YAML frontmatter"
}

写作契约：
1. 正文开头直接写 3—6 段中文导语，依次交代背景、论文的真实地位、研究矛盾和前置/部署条件。不要复制摘要，不要加“研究问题”标题。
2. 实证论文使用“## 一、方法：具体标题”“## 二、实验：具体标题”“## 三、总结”“## References”。综述可改为“综述框架”和“证据与比较”，不得虚构实验。
3. 创新点必须融进方法的小节与数据流，不要设置泛化的“创新点”章节。
4. 图片只能使用候选列表中给出的站内 URL，默认选 1—4 张真正帮助理解方法或关键结果的图。不要选择纯 prompt 截图、英文表格截图、logo 或近重复图片，除非它是论文核心证据。
5. 图片之后直接用自然中文解释阅读顺序、区域含义、数据流和它支撑的主张。禁止输出“原图说明：”“图示解释：”，禁止逐字翻译英文 caption，也不要让多张图共用同一句解释。
6. 实验部分先用 Markdown 表格交代数据集、模型、划分、基线、指标和实现条件，再用表格呈现主结果。论文有消融、效率、超参数或案例实验时必须分别列表并分析；没有时明确边界，不得补造。
7. 表格只使用证据中明确出现的数值。分析要指出最强相关基线、绝对变化、一致性、例外和代价；不要只写“达到 SOTA”。不要擅自计算或创造证据中未直接给出的新数字。
8. 总结必须包含方法机制、实验证据、至少一个限制或边界，以及一个可迁移的设计启示。
9. References 首项是目标论文，附 arXiv/DOI 与已验证的官方代码链接；只保留少量直接相关工作。
10. 只根据提供的证据写作。不得捏造作者单位、会议录用、GitHub、数据集、实验、数值或因果结论。
11. 不要在正文里说“根据提供材料”“原文显示”“作为 AI”。
12. 实验表格和分析只能复述证据中原样出现的数值；不要自行补算百分点、相对提升、均值或图轴读数。
"""


@dataclass(frozen=True)
class RewriteResult:
    paper_id: str
    status: str
    draft_path: str = ""
    output_path: str = ""
    title: str = ""
    errors: tuple[str, ...] = ()
    attempts: int = 0


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER.search(text)
    if not match:
        raise ValueError("missing YAML frontmatter")
    return match.group(1), text[match.end() :].lstrip()


def yaml_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
    return match.group(1).strip().strip("\"'") if match else ""


def replace_yaml(frontmatter: str, key: str, value: str) -> str:
    rendered = json.dumps(value, ensure_ascii=False)
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    if pattern.search(frontmatter):
        return pattern.sub(f"{key}: {rendered}", frontmatter)
    return frontmatter.rstrip() + f"\n{key}: {rendered}"


def priority_excerpt(text: str, max_chars: int = 52000) -> str:
    if len(text) <= max_chars:
        return text
    matches = list(HEADING.finditer(text))
    if not matches:
        return text[:max_chars]
    sections: list[tuple[int, int, str]] = []
    preamble = text[: matches[0].start()]
    if preamble.strip():
        sections.append((0, 0, preamble))
    high = (
        "abstract", "introduction", "background", "prelim", "method", "approach",
        "framework", "architecture", "experiment", "evaluation", "result", "ablation",
        "analysis", "dataset", "implementation", "efficiency", "conclusion", "discussion",
        "摘要", "引言", "背景", "方法", "框架", "实验", "结果", "消融", "数据", "结论",
    )
    low = ("related work", "reference", "bibliography", "acknowledg", "appendix")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        heading = match.group(1).lower()
        rank = 20
        if any(word in heading for word in high):
            rank = 1
        if any(word in heading for word in low):
            rank = 80
        sections.append((rank, index + 1, text[match.start() : end]))
    chosen: list[tuple[int, str]] = []
    total = 0
    for _rank, order, section in sorted(sections, key=lambda item: (item[0], item[1])):
        if total >= max_chars:
            break
        chunk = section[: max_chars - total]
        chosen.append((order, chunk))
        total += len(chunk)
    return "\n\n".join(chunk for _order, chunk in sorted(chosen))


def find_source(library_root: Path, paper_id: str, kind: str) -> Path | None:
    data = library_root / "data"
    if kind == "summary":
        candidates = list((data / "summaries").glob(f"{paper_id}*.md"))
    elif kind == "parsed":
        candidates = [
            path for path in (data / "parsed").rglob(f"{paper_id}.md")
            if "arxiv_source" not in {part.lower() for part in path.parts}
        ]
    else:
        candidates = list((data / "parsed").rglob("arxiv.tex"))
        candidates = [path for path in candidates if paper_id in str(path)]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: (-path.stat().st_size, len(path.parts)))[0]


def figure_candidates(body: str, site_root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in IMAGE.finditer(body):
        alt, url = match.groups()
        if url in seen:
            continue
        seen.add(url)
        tail = body[match.end() : match.end() + 700]
        caption_match = re.search(r"原图说明：(.+?)(?:\*\s*$|\n)", tail)
        local = site_root / "source" / url.lstrip("/")
        candidates.append(
            {
                "url": url,
                "alt": alt,
                "caption": caption_match.group(1).strip() if caption_match else alt,
                "exists": local.exists(),
                "bytes": local.stat().st_size if local.exists() else 0,
            }
        )
    return candidates


def site_figure_candidates(
    paper_id: str, parsed: str, site_root: Path, existing: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Include every staged paper image, not only images used by the legacy post."""
    candidates = list(existing)
    seen = {item["url"] for item in candidates}
    captions: dict[str, str] = {}
    for match in re.finditer(r"!\[[^\]]*\]\((?:\./)?images/([^)]+)\)", parsed):
        filename = Path(match.group(1)).name
        tail = parsed[match.end() : match.end() + 900]
        caption = next((line.strip() for line in tail.splitlines() if line.strip()), filename)
        captions[filename] = re.sub(r"<[^>]+>", "", caption)
    image_dir = site_root / "source" / "images" / "papers" / paper_id
    if not image_dir.exists():
        return candidates
    for local in sorted(image_dir.iterdir()):
        if not local.is_file() or local.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        url = f"/images/papers/{paper_id}/{local.name}"
        if url in seen:
            continue
        seen.add(url)
        candidates.append(
            {
                "url": url,
                "alt": f"{paper_id} 论文图",
                "caption": captions.get(local.name, local.name),
                "exists": True,
                "bytes": local.stat().st_size,
            }
        )
    return candidates


def evidence_for(post: Path, library_root: Path, site_root: Path) -> dict[str, Any]:
    text = post.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = split_frontmatter(text)
    paper_id = yaml_value(frontmatter, "arxiv_id") or post.stem.removeprefix("paper-")
    summary_path = find_source(library_root, paper_id, "summary")
    parsed_path = find_source(library_root, paper_id, "parsed")
    tex_path = find_source(library_root, paper_id, "tex")
    summary = summary_path.read_text(encoding="utf-8", errors="replace") if summary_path else ""
    parsed = parsed_path.read_text(encoding="utf-8", errors="replace") if parsed_path else ""
    tex = tex_path.read_text(encoding="utf-8", errors="replace") if tex_path else ""
    figures = site_figure_candidates(
        paper_id, parsed, site_root, figure_candidates(body, site_root)
    )
    resource = RESOURCE_LINE.search(body)
    return {
        "paper_id": paper_id,
        "post": post,
        "frontmatter": frontmatter,
        "legacy_body": body,
        "resource_line": resource.group(0) if resource else f"> 论文：[arXiv {paper_id}](https://arxiv.org/abs/{paper_id})",
        "figures": figures,
        "summary": summary,
        "parsed": priority_excerpt(parsed),
        "tex": priority_excerpt(tex, 18000),
        # Keep the complete local text for validation only. It is not added to
        # the API prompt, but prevents valid table/axis values outside the
        # excerpt from being rejected as hallucinations.
        "numeric_source": "\n".join([summary, parsed, tex, body, frontmatter]),
        "source_paths": {
            "summary": str(summary_path or ""),
            "parsed": str(parsed_path or ""),
            "tex": str(tex_path or ""),
        },
    }


def build_user_prompt(evidence: dict[str, Any], feedback: list[str]) -> str:
    figures = json.dumps(evidence["figures"], ensure_ascii=False, indent=2)
    correction = ""
    if feedback:
        correction = "\n\n上一次草稿未通过以下检查，请全部修正：\n- " + "\n- ".join(feedback)
    return f"""请改写 arXiv {evidence['paper_id']} 的网站文章。

正文第一行必须原样保留这个资源链接：
{evidence['resource_line']}

候选图片（只能使用其中 exists=true 的 URL；caption 仅用于理解，不要照抄）：
{figures}

正文必须使用至少一张 exists=true 的候选图片，并逐字符复制候选 URL；不得猜测、改写目录或文件名。

可靠项目摘要：
{evidence['summary']}

论文解析正文（关键章节）：
{evidence['parsed']}

可用的 LaTeX 源码片段：
{evidence['tex']}

旧稿（只用于发现已有链接和待修正问题，若与论文证据冲突以论文证据为准）：
{evidence['legacy_body']}
{correction}
"""


def parse_json_response(raw: str) -> dict[str, str]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    return {
        "title": str(data.get("title", "")).strip(),
        "description": str(data.get("description", "")).strip(),
        "body_markdown": str(data.get("body_markdown", "")).strip(),
    }


def numeric_support(evidence_text: str) -> set[str]:
    values = set(NUMBER.findall(evidence_text))
    # Dataset/model identifiers can embed evidence-bearing numbers, such as
    # NQ100K or LLaMA2. Accept those embedded tokens on the evidence side.
    values.update(re.findall(r"\d+(?:\.\d+)?%?", evidence_text))
    values.update(value.rstrip("%") for value in tuple(values))
    raw_numbers: list[float] = []
    for value in values:
        try:
            raw_numbers.append(float(value.rstrip("%")))
        except ValueError:
            pass
    if len(raw_numbers) <= 350:
        for left in raw_numbers:
            for right in raw_numbers:
                difference = abs(left - right)
                values.add(f"{difference:.1f}")
                values.add(f"{difference:.2f}")
    return values


def remove_unsupported_numeric_sentences(
    payload: dict[str, str], errors: list[str]
) -> dict[str, str] | None:
    """Conservatively drop prose sentences containing unsupported numbers.

    Tables and headings are never modified: if an unsupported value occurs
    there, the draft remains blocked for manual evidence review.
    """
    if not errors or any(not error.startswith("出现证据中无法核对的数值：") for error in errors):
        return None
    tokens = {
        token.strip()
        for error in errors
        for token in error.split("：", 1)[-1].split(",")
        if token.strip()
    }
    token_patterns = [
        re.compile(rf"(?<![\d.]){re.escape(token)}(?![\d.])") for token in tokens
    ]

    def contains_unsupported(text: str) -> bool:
        return any(pattern.search(text) for pattern in token_patterns)

    lines: list[str] = []
    changed = False
    for line in payload["body_markdown"].splitlines():
        if contains_unsupported(line) and (line.startswith("|") or line.startswith("#")):
            return None
        if contains_unsupported(line):
            sentences = re.split(r"(?<=[。；])", line)
            kept = [sentence for sentence in sentences if not contains_unsupported(sentence)]
            replacement = "".join(kept).strip()
            changed = changed or replacement != line.strip()
            if replacement:
                lines.append(replacement)
            continue
        lines.append(line)
    if not changed:
        return None
    return {**payload, "body_markdown": "\n".join(lines).strip()}


def validate_payload(payload: dict[str, str], evidence: dict[str, Any], site_root: Path) -> list[str]:
    errors: list[str] = []
    title = payload["title"]
    description = payload["description"]
    body = payload["body_markdown"]
    if not title or len(title) < 8:
        errors.append("标题过短或缺失")
    if len(description) < 35:
        errors.append("description 未概括问题、机制和证据")
    if len(body) < 1800:
        errors.append(f"正文过短（{len(body)} 字符）")
    if not body.startswith(evidence["resource_line"]):
        errors.append("正文没有原样保留顶部资源链接")
    required = ("## 一、", "## 二、", "## 三、总结", "## References")
    for marker in required:
        if marker not in body:
            errors.append(f"缺少章节：{marker}")
    for marker in BAD_OUTPUT_MARKERS:
        if marker in body:
            errors.append(f"仍含旧模板标记：{marker}")
    image_urls = [url for _alt, url in IMAGE.findall(body)]
    allowed = {item["url"] for item in evidence["figures"] if item["exists"]}
    if not image_urls:
        errors.append("正文没有保留任何可解释的论文图片")
    if len(image_urls) > 4:
        errors.append(f"图片过多（{len(image_urls)}，上限 4）")
    for url in image_urls:
        if url not in allowed:
            errors.append(f"使用了候选列表之外的图片：{url}")
        if not (site_root / "source" / url.lstrip("/")).exists():
            errors.append(f"图片文件不存在：{url}")
    if not TABLE_SEPARATOR.search(body):
        errors.append("正文没有 Markdown 表格")
    if f"https://arxiv.org/abs/{evidence['paper_id']}" not in body:
        errors.append("References 缺少目标论文 arXiv 链接")
    source_text = evidence["numeric_source"]
    supported = numeric_support(source_text)
    unsupported: list[str] = []
    # References contain publication years and paper identifiers rather than
    # empirical claims. Validate only the editorial title/description/body.
    body_without_references = body.split("## References", 1)[0]
    # Decimal subsection labels such as “### 1.1” are structure, not claims.
    body_without_references = re.sub(r"(?m)^#{3,6}\s+.*$", "", body_without_references)
    for token in NUMBER.findall("\n".join([title, description, body_without_references])):
        bare = token.rstrip("%")
        try:
            number = float(bare)
        except ValueError:
            continue
        if number <= 3 and "." not in token and not token.endswith("%"):
            continue
        if token not in supported and bare not in supported:
            unsupported.append(token)
    if unsupported:
        errors.append("出现证据中无法核对的数值：" + ", ".join(sorted(set(unsupported))[:12]))
    return errors


def render_post(payload: dict[str, str], evidence: dict[str, Any]) -> str:
    frontmatter = replace_yaml(evidence["frontmatter"], "title", payload["title"])
    frontmatter = replace_yaml(frontmatter, "description", payload["description"])
    return f"---\n{frontmatter.rstrip()}\n---\n\n{payload['body_markdown'].rstrip()}\n"


def rewrite_one(
    post: Path,
    library_root: Path,
    site_root: Path,
    cache_dir: Path,
    api_key: str,
    model: str,
    apply: bool,
    force: bool,
    max_attempts: int,
) -> RewriteResult:
    evidence = evidence_for(post, library_root, site_root)
    paper_id = evidence["paper_id"]
    cache_path = cache_dir / f"{paper_id}.json"
    rejected_path = cache_dir / "rejected" / f"{paper_id}.json"
    feedback: list[str] = []
    payload: dict[str, str] | None = None
    last_payload: dict[str, str] | None = None
    if cache_path.exists() and not force:
        try:
            payload = parse_json_response(cache_path.read_text(encoding="utf-8"))
            feedback = validate_payload(payload, evidence, site_root)
            if feedback:
                payload = None
        except Exception:
            payload = None
    if payload is None and rejected_path.exists() and not force:
        try:
            rejected = parse_json_response(rejected_path.read_text(encoding="utf-8"))
            rejected_errors = validate_payload(rejected, evidence, site_root)
            sanitized = remove_unsupported_numeric_sentences(rejected, rejected_errors)
            if sanitized is not None and not validate_payload(sanitized, evidence, site_root):
                payload = sanitized
                cache_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
        except Exception:
            payload = None
    attempts = 0
    while payload is None and attempts < max_attempts:
        attempts += 1
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(evidence, feedback)},
                ],
                temperature=0.2,
                max_tokens=8000,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or ""
            payload = parse_json_response(raw)
            last_payload = payload
            feedback = validate_payload(payload, evidence, site_root)
            if feedback:
                payload = None
                time.sleep(min(2 ** attempts, 8))
                continue
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except Exception as exc:
            feedback = [f"API 或 JSON 错误：{type(exc).__name__}: {exc}"]
            payload = None
            time.sleep(min(2 ** attempts, 8))
    if payload is None:
        if last_payload is not None:
            rejected_dir = cache_dir / "rejected"
            rejected_dir.mkdir(parents=True, exist_ok=True)
            (rejected_dir / f"{paper_id}.json").write_text(
                json.dumps(last_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        return RewriteResult(paper_id, "blocked", errors=tuple(feedback), attempts=attempts)
    rendered = render_post(payload, evidence)
    draft_path = cache_dir / f"{paper_id}.md"
    draft_path.write_text(rendered, encoding="utf-8", newline="\n")
    output_path = ""
    if apply:
        post.write_text(rendered, encoding="utf-8", newline="\n")
        output_path = str(post)
    return RewriteResult(
        paper_id,
        "rewritten" if apply else "validated_draft",
        draft_path=str(draft_path),
        output_path=output_path,
        title=payload["title"],
        attempts=attempts,
    )


def target_posts(site_root: Path, ids: set[str]) -> list[Path]:
    posts = site_root / "source" / "_posts"
    selected: list[Path] = []
    for post in sorted(posts.glob("*.md")):
        text = post.read_text(encoding="utf-8", errors="replace")
        match = ARXIV_ID.search(text)
        paper_id = match.group(1) if match else ""
        if ids and paper_id not in ids:
            continue
        # Select only posts generated from the complete legacy template.  A
        # single phrase such as “图示解释” can also occur in an intentionally
        # edited article and is not sufficient evidence for a batch rewrite.
        if all(marker in text for marker in CORE_TEMPLATE_MARKERS):
            selected.append(post)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path, required=True)
    parser.add_argument("--library-root", type=Path, required=True)
    parser.add_argument("--ids", default="", help="comma-separated arXiv IDs")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    site_root = args.site_root.resolve()
    library_root = args.library_root.resolve()
    env = {**load_env(library_root / ".env"), **os.environ}
    api_key = env.get("DEEPSEEK_API_KEY", "")
    model = env.get("DEEPSEEK_MODEL", "deepseek-chat") or "deepseek-chat"
    if not api_key:
        print("DEEPSEEK_API_KEY is not configured", file=sys.stderr)
        return 2
    ids = {value.strip() for value in args.ids.split(",") if value.strip()}
    posts = target_posts(site_root, ids)
    cache_dir = (args.cache_dir or site_root / ".paper-rewrite" / "drafts").resolve()
    report_path = (args.report or site_root / ".paper-rewrite" / "report.json").resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"selected={len(posts)} model={model} workers={args.workers} apply={args.apply}", flush=True)

    results: list[RewriteResult] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                rewrite_one,
                post,
                library_root,
                site_root,
                cache_dir,
                api_key,
                model,
                args.apply,
                args.force,
                args.max_attempts,
            ): post
            for post in posts
        }
        for future in as_completed(futures):
            post = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                paper_id = post.stem.removeprefix("paper-")
                result = RewriteResult(paper_id, "blocked", errors=(f"Unhandled: {exc}",))
            results.append(result)
            with PRINT_LOCK:
                detail = result.title if result.status != "blocked" else "; ".join(result.errors)
                print(f"[{result.paper_id}] {result.status} attempts={result.attempts} {detail}", flush=True)
            report_path.write_text(
                json.dumps(
                    {
                        "selected": len(posts),
                        "completed": len(results),
                        "apply": args.apply,
                        "items": [item.__dict__ for item in sorted(results, key=lambda value: value.paper_id)],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
    blocked = [result for result in results if result.status == "blocked"]
    print(f"completed={len(results)} blocked={len(blocked)} report={report_path}", flush=True)
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
