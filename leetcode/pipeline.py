"""LeetCode 题解自动生成管线（纯 API，无需浏览器）。

用法示例：
  # 单语言（默认，自动带题目自带话题标签）
  python leetcode/pipeline.py 754693208

  # 代码可切换：主语言 + AI 翻译出的 C++/Java 版本（编辑器里按 tab 切换）
  python leetcode/pipeline.py 754693208 --extra-lang cpp,java

  # 用自己另一份提交当第二语言（推荐，代码是真实 AC 的）
  python leetcode/pipeline.py 754693208 --extra-submission 754123456

  # 用本地文件当第二语言（可重复传）
  python leetcode/pipeline.py 754693208 --extra-code cpp=my/sol.cpp --extra-code java=my/Sol.java

  # 更新已有草稿而不是新建
  python leetcode/pipeline.py 754693208 --extra-lang cpp --slug <draftSlug>

  # 人工改完 outputs/*.md 后就地回传更新草稿（跳过 LLM，保留代码 tab）
  python leetcode/pipeline.py 754693208 --md leetcode/outputs/754693208_editorial.md --slug <draftSlug>

流程：取提交详情 -> 取题目描述+话题标签 -> DeepSeek 生成题解(markdown) ->
      组装多语言 Code tab -> 转 Slate JSON -> autoSaveSolutionArticle 存草稿（不发布）。

草稿查看：https://leetcode.cn/post-editor/solution/create/?submissionId=<submissionId>
"""
import argparse
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from leetcode_api import LeetCodeClient
from generate_editorial import (generate_editorial, translate_code,
                                LANG_DISPLAY)
from slate_builder import (markdown_to_slate, attach_code_tabs,
                           code_tabs_node, slate_to_json)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def _parse_extra_codes(items):
    """--extra-code lang=path -> [(lang_key, code)]"""
    out = []
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--extra-code 格式应为 lang=path，收到: {item}")
        lang, path = item.split("=", 1)
        with open(path, encoding="utf-8") as f:
            out.append((lang.strip(), f.read()))
    return out


def _read_md(path):
    """Read a locally edited markdown copy back for re-upload.

    Strips the header lines written by `run()` (# title / 话题标签), and splits
    off the trailing extra-language appendix as code tabs.
    Returns (markdown_body, [(lang_key, code)]).
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    for _ in range(2):
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines and lines[0].startswith("话题标签:"):
            lines = lines[1:]
    md = "\n".join(lines).lstrip("\n")

    extra = []
    marker = "\n## Code（其他语言版本"
    i = md.find(marker)
    if i != -1:
        appendix = md[i + len(marker):]
        md = md[:i].rstrip() + "\n"
        for m in re.finditer(r"###\s+[^\n]+\n+```([A-Za-z0-9+#]+)\n(.*?)\n```",
                             appendix, re.S):
            extra.append((_norm_lang(m.group(1)), m.group(2)))
    return md, extra


def _norm_lang(lang):
    """leetcode lang value -> editor language key."""
    key = (lang or "").strip().lower()
    return {"c++": "cpp", "go": "golang", "python": "python3"}.get(key, key)


def build_code_tabs(cli, submission, args):
    """Assemble [(lang_key, code)] with the submitted language first."""
    main_lang = _norm_lang(submission.get("lang"))
    tabs = [(main_lang, submission.get("code") or "")]

    # 1) another real submission of the same account (best quality: real AC)
    for sid in args.extra_submission or []:
        sub = cli.submission_detail(sid)
        if not sub:
            print(f"  警告: 提交 {sid} 拉取失败，跳过")
            continue
        lang = _norm_lang(sub.get("lang"))
        if lang == main_lang:
            print(f"  警告: 提交 {sid} 也是 {lang}，跳过")
            continue
        tabs.append((lang, sub.get("code") or ""))
        print(f"  附加语言 ({lang}，来自提交 {sid})")

    # 2) local files
    for lang, code in _parse_extra_codes(args.extra_code):
        lang = _norm_lang(lang)
        tabs.append((lang, code))
        print(f"  附加语言 ({lang}，来自本地文件)")

    # 3) AI translation
    for lang in args.extra_lang or []:
        lang = _norm_lang(lang)
        if any(l == lang for l, _ in tabs):
            continue
        print(f"  正在翻译 {main_lang} -> {lang} ...")
        tabs.append((lang, translate_code(tabs[0][1], main_lang, lang)))
        print(f"  附加语言 ({lang}，AI 翻译)")

    return tabs


def _resolve_submission_id(cli, raw):
    """Accept a numeric submission id, a problem slug, or a leetcode.cn URL.

    Non-numeric input is treated as a problem: pick the newest Accepted
    submission of the current account on that problem.
    """
    raw = (raw or "").strip()
    m = re.search(r"/problems/([a-z0-9\-]+)", raw)
    if m:
        raw = m.group(1)
    if raw.isdigit():
        return raw
    subs = cli.submission_list(raw, limit=20)
    ok = [s for s in subs if s.get("statusDisplay") == "Accepted"]
    if not ok:
        raise SystemExit(f"题目 {raw} 下没找到 Accepted 提交（共 {len(subs)} 条）")
    print(f"  题目 {raw} -> 取最新 Accepted 提交 {ok[0].get('id')} "
          f"({ok[0].get('lang')})")
    return ok[0].get("id")


def run(submission_id, args, save_markdown=True):
    cli = LeetCodeClient()
    me = cli.whoami()
    if not me.get("isSignedIn"):
        raise RuntimeError("LEETCODE_SESSION 已失效，请从浏览器重新复制 cookie 更新 .env")
    print(f"[1/6] 登录账号: {me.get('username')}")

    submission_id = _resolve_submission_id(cli, submission_id)
    sub = cli.submission_detail(submission_id)
    if not sub:
        raise RuntimeError(f"提交 {submission_id} 不存在或不属于当前账号")
    if sub.get("statusDisplay") != "Accepted":
        print(f"  警告: 该提交状态为 {sub.get('statusDisplay')}（非 Accepted）")
    q_meta = sub.get("question") or {}
    title_slug = q_meta.get("titleSlug")
    print(f"[2/6] 提交详情: {q_meta.get('questionFrontendId')}. "
          f"{q_meta.get('translatedTitle')} ({q_meta.get('difficulty')}) "
          f"{sub.get('lang')} {sub.get('runtime')}/{sub.get('memory')}")

    problem = cli.question_detail(title_slug) or {}
    topic_tags = problem.get("topicTags") or []
    if args.tags == "auto":
        tags = [t.get("slug") for t in topic_tags if t.get("slug")]
        print(f"[3/6] 话题标签(自动取题目自带): {tags} "
              f"({'/'.join(t.get('translatedName') or t.get('name') or '' for t in topic_tags)})")
    elif args.tags in ("none", "", None):
        tags = []
        print("[3/6] 话题标签: 不填")
    else:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        print(f"[3/6] 话题标签(手动): {tags}")

    local_tabs = []
    if getattr(args, "md", None):
        md, local_tabs = _read_md(args.md)
        print(f"[4/6] 使用本地 markdown 回传（{len(md)} 字符）: {args.md}")
    else:
        md = generate_editorial(problem, sub)
        print(f"[4/6] 题解已生成（{len(md)} 字符 markdown）")

    tabs = build_code_tabs(cli, sub, args)
    for lang, code in local_tabs:
        if not any(l == lang for l, _ in tabs):
            tabs.append((lang, code))
            print(f"  附加语言 ({lang}，来自本地 markdown)")
    blocks = markdown_to_slate(md)
    if len(tabs) > 1 and not args.no_multitab:
        blocks = attach_code_tabs(blocks, tabs, active_index=0)
        print(f"[5/6] 代码块: {len(tabs)} 个可切换 tab "
              f"({', '.join(LANG_DISPLAY.get(l, l) for l, _ in tabs)})，默认显示 "
              f"{LANG_DISPLAY.get(tabs[0][0], tabs[0][0])}")
    else:
        print(f"[5/6] 代码块: 单语言 {LANG_DISPLAY.get(tabs[0][0], tabs[0][0])}")

    title = f"{q_meta.get('questionFrontendId')}. {q_meta.get('translatedTitle')}"
    if args.title_suffix:
        title = f"{title}{args.title_suffix}"
    article = cli.auto_save_draft(
        title=title,
        slate_value=json.dumps(blocks, ensure_ascii=False),
        question_slug=title_slug,
        tags=tags,
        slug=args.slug,
    )
    print(f"[6/6] 草稿已保存: slug={article.get('slug')} status={article.get('status')}")

    if save_markdown:
        os.makedirs(OUT_DIR, exist_ok=True)
        out_path = os.path.join(OUT_DIR, f"{submission_id}_editorial.md")
        if (getattr(args, "md", None)
                and os.path.abspath(args.md) == os.path.abspath(out_path)):
            print(f"  markdown 副本: {out_path}（就地回传，未覆盖）")
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"话题标签: {', '.join(tags) or '（无）'}\n\n")
                f.write(md)
                if len(tabs) > 1:
                    f.write("\n## Code（其他语言版本，编辑器中为可切换 tab）\n")
                    for lang, code in tabs[1:]:
                        f.write(f"\n### {LANG_DISPLAY.get(lang, lang)}\n\n"
                                f"```{lang}\n{code}\n```\n")
            print(f"  markdown 副本: {out_path}")

    editor_url = (f"https://leetcode.cn/post-editor/solution/create/"
                  f"?submissionId={submission_id}")
    return {"title": title, "tags": tags, "slug": article.get("slug"),
            "languages": [l for l, _ in tabs], "editor_url": editor_url}


def main():
    ap = argparse.ArgumentParser(description="LeetCode 题解自动生成（存草稿）")
    ap.add_argument("submission_id",
                    help="提交 id，也可直接给题目 slug 或 leetcode.cn 题目链接"
                         "（自动取该题最新 Accepted 提交）")
    ap.add_argument("--tags", default="auto",
                    help="话题标签: auto(取题目自带，默认) | none | slug1,slug2")
    ap.add_argument("--extra-lang", default=None,
                    help="附加语言(AI 翻译)，逗号分隔，如 cpp,java")
    ap.add_argument("--extra-code", action="append", default=None,
                    help="附加语言(本地文件)，格式 lang=path，可重复")
    ap.add_argument("--extra-submission", action="append", default=None,
                    help="附加语言(自己的其他提交 id)，可重复")
    ap.add_argument("--slug", default=None, help="更新已有草稿的 slug（不传=新建）")
    ap.add_argument("--title-suffix", default=None)
    ap.add_argument("--no-multitab", action="store_true", help="只保留主语言，不做多 tab")
    ap.add_argument("--md", default=None,
                    help="用本地改好的 markdown 回传草稿（跳过 LLM 生成）")
    args = ap.parse_args()
    args.extra_lang = ([l.strip() for l in args.extra_lang.split(",") if l.strip()]
                       if args.extra_lang else [])
    result = run(args.submission_id, args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n下一步: 打开下面地址复核草稿，确认后手动点「发布题解」：")
    print(result["editor_url"])


if __name__ == "__main__":
    main()
