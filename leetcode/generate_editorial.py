"""DeepSeek-powered editorial (题解) generation for LeetCode problems.

Follows the user's copywriting rules migrated from the XHS pipeline:
plain Chinese, no jargon stacking, all numbers from the real submission.
Output is markdown with fixed sections: 思路 / 解题过程 / 复杂度 / Code.
"""
import os
import re
import sys
import html
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """你是一位中文算法题解作者，为 LeetCode 中国站的题解区写题解。

写作铁律：
1. 全文简体中文，平实自然，面向刷题的同学；不堆砌英文术语和论文黑话，专业词首次出现时用中文解释。
2. 所有事实（题目条件、复杂度、运行数据）必须来自给定的题目和提交信息，严禁编造。
3. 不要夸大，不要营销腔，不要"这道题非常简单"之类的空话。
3.5 判断必须肯定：不要在正文里自我提问、犹豫、或写"（是这样吗？""注意：也许…"）这类自我纠正；想清楚再写结论。
4. 输出纯 Markdown，结构必须严格为以下四节（用 ## 二级标题）：

## 思路
（1-3 段：这道题在问什么，核心的观察/贪心/DP/数据结构选择是什么，为什么可行）

## 解题过程
（分步骤讲清楚怎么做，可用有序列表；关键步骤给出小例子更佳）

## 复杂度
（时间复杂度和空间复杂度，各一行，并说明为什么）

## Code
（用 ```python3 等 fence 原样嵌入给定的提交代码，一个字都不要改）

只输出 Markdown 正文，不要任何额外说明。"""


def html_to_text(html_str):
    """Very small HTML->text for problem statements (good enough for prompts)."""
    s = html_str or ""
    s = re.sub(r"<pre>.*?</pre>", lambda m: "\n" + re.sub(r"<[^>]+>", "", m.group(0)) + "\n",
               s, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|li|h[1-6]|ul|ol)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# leetcode.cn lang key -> display name / editor language key
LANG_DISPLAY = {
    "python3": "Python3", "python": "Python3", "cpp": "C++", "c++": "C++",
    "java": "Java", "c": "C", "csharp": "C#", "javascript": "JavaScript",
    "typescript": "TypeScript", "golang": "Go", "go": "Go", "rust": "Rust",
    "kotlin": "Kotlin", "swift": "Swift", "scala": "Scala", "ruby": "Ruby",
    "php": "PHP", "dart": "Dart", "elixir": "Elixir", "erlang": "Erlang",
    "racket": "Racket", "bash": "Bash", "mysql": "MySQL", "mssql": "MS SQL Server",
}

TRANSLATE_SYSTEM = """你是代码翻译助手。把给定的 LeetCode 提交代码逐行等价翻译成目标语言。

要求：
1. 保持算法逻辑、类/方法签名语义与 LeetCode 目标语言模板一致（例如 C++ 用 class Solution + public 方法）。
2. 不要改变算法，不要优化，不要加注释以外的额外内容。
3. 只输出代码本身，用 ```fence 包裹，不要任何解释文字。"""


def translate_code(code, src_lang, dst_lang, max_retries=3):
    """Translate an AC solution into another language (used for code tabs)."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY missing in .env")

    src = LANG_DISPLAY.get(src_lang, src_lang)
    dst = LANG_DISPLAY.get(dst_lang, dst_lang)
    prompt = f"""把下面这份 {src} 的 LeetCode 提交翻译成 {dst}：

```{src_lang}
{code}
```
"""
    last_err = None
    for attempt in range(max_retries):
        try:
            r = requests.post(
                DEEPSEEK_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                    "messages": [
                        {"role": "system", "content": TRANSLATE_SYSTEM},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=300,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            # strip the fence wrapper if the model kept it
            m = re.search(r"```[A-Za-z0-9_+]*\n(.*?)```", content, flags=re.S)
            if m:
                content = m.group(1)
            if not content.strip():
                raise RuntimeError("empty translation")
            return content.strip()
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[translate] attempt {attempt + 1} failed: {e}")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"translation {src_lang}->{dst_lang} failed: {last_err}")


def generate_editorial(problem, submission, max_retries=3):
    """problem: dict from LeetCodeClient.question_detail
    submission: dict from LeetCodeClient.submission_detail
    Returns markdown string of the editorial."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY missing in .env")

    code = submission.get("code") or ""
    lang = submission.get("lang") or "python3"
    q = problem or {}
    runtime, memory = submission.get("runtime"), submission.get("memory")
    # 某些提交拿不到运行数据（如每日一题的提交），此时不提，避免模型编数字
    perf = (f"，运行时间 {runtime}，内存 {memory}" if runtime and memory else "")
    user_prompt = f"""请为下面这道题写题解。

题目：{q.get('questionFrontendId')}. {q.get('translatedTitle')}（难度：{q.get('difficulty')}）

题目描述：
{html_to_text(q.get('translatedContent') or '')}

我的提交（{lang}，已 Accepted{perf}）：
```{lang}
{code}
```
"""
    last_err = None
    for attempt in range(max_retries):
        try:
            r = requests.post(
                DEEPSEEK_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=300,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            if "## 思路" not in content or "## Code" not in content:
                raise RuntimeError(f"editorial sections missing, got: {content[:200]}")
            return content.strip()
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[deepseek] attempt {attempt + 1} failed: {e}")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"editorial generation failed: {last_err}")
