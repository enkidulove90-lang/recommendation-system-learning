"""LeetCode (leetcode.cn) GraphQL API client for the editorial pipeline.

Auth: LEETCODE_SESSION + csrftoken from .env (browser cookies, route B).
Read-only queries here; draft creation is handled separately (browser or API).
"""
import os
import sys
import json
import time
import requests

# stdout utf-8 to avoid GBK crashes on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

GRAPHQL = "https://leetcode.cn/graphql/"

SUBMISSION_DETAIL_QUERY = """
query submissionDetail($submissionId: ID!) {
  submissionDetail(submissionId: $submissionId) {
    id
    code
    runtime
    memory
    lang
    timestamp
    statusDisplay
    question {
      questionFrontendId
      translatedTitle
      title
      titleSlug
      difficulty
    }
  }
}
"""

WHOAMI_QUERY = """
query {
  userStatus {
    isSignedIn
    username
    userSlug
  }
}
"""

QUESTION_DETAIL_QUERY = """
query questionDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    translatedTitle
    translatedContent
    difficulty
    topicTags { name slug translatedName }
  }
}
"""

SUBMISSION_LIST_QUERY = """
query submissionList($offset: Int!, $limit: Int!, $questionSlug: String!) {
  submissionList(offset: $offset, limit: $limit, questionSlug: $questionSlug) {
    lastKey
    hasNext
    submissions { id statusDisplay lang runtime memory }
  }
}
"""

AUTOSAVE_MUTATION = """
mutation autoSaveSolutionArticle($data: AutoSaveSolutionArticleInput!) {
  autoSaveSolutionArticle(data: $data) {
    ok
    error
    article { slug status }
  }
}
"""

DRAFTS_QUERY = """
query solutionDrafts($questionSlug: String!, $first: Int!, $skip: Int!) {
  solutionDrafts(questionSlug: $questionSlug, first: $first, skip: $skip) {
    edges { node { slug title status } }
  }
}
"""


class LeetCodeClient:
    def __init__(self, session_cookie=None, csrftoken=None, verbose=True):
        self.verbose = verbose
        self.session_cookie = session_cookie or os.getenv("LEETCODE_SESSION", "")
        self.csrftoken = csrftoken or os.getenv("LEETCODE_CSRFTOKEN", "")
        if not self.session_cookie or not self.csrftoken:
            raise RuntimeError("LEETCODE_SESSION / LEETCODE_CSRFTOKEN missing in .env")
        self.http = requests.Session()
        self.http.headers.update({
            "Cookie": f"LEETCODE_SESSION={self.session_cookie}; csrftoken={self.csrftoken}",
            "x-csrftoken": self.csrftoken,
            "Content-Type": "application/json",
            "Referer": "https://leetcode.cn/",
            "Origin": "https://leetcode.cn",
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/130.0.0.0 Safari/537.36"),
        })

    def gql(self, query, variables=None, retries=3):
        body = {"query": query, "variables": variables or {}}
        last_err = None
        for attempt in range(retries):
            try:
                r = self.http.post(GRAPHQL, json=body, timeout=30)
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
                data = r.json()
                if data.get("errors"):
                    raise RuntimeError(f"GraphQL errors: {data['errors']}")
                return data.get("data", {})
            except Exception as e:  # noqa: BLE001
                last_err = e
                if self.verbose:
                    print(f"[gql] attempt {attempt + 1} failed: {e}")
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"GraphQL query failed after {retries} retries: {last_err}")

    def whoami(self):
        return self.gql(WHOAMI_QUERY).get("userStatus", {})

    def submission_detail(self, submission_id):
        """Fetch one submission's code + question meta. Returns dict or None."""
        data = self.gql(SUBMISSION_DETAIL_QUERY, {"submissionId": str(submission_id)})
        return data.get("submissionDetail")

    def question_detail(self, title_slug):
        """Fetch problem statement (HTML) by slug."""
        data = self.gql(QUESTION_DETAIL_QUERY, {"titleSlug": title_slug})
        return data.get("question")

    def auto_save_draft(self, title, slate_value, question_slug, tags=None, slug=None):
        """Create/update a solution DRAFT via autoSaveSolutionArticle.

        Returns article dict {slug, status} on success, raises otherwise.
        """
        data = {
            "title": title,
            "content": "",
            "tags": tags or [],
            "questionSlug": question_slug,
            "slateValue": slate_value,
            "slug": slug,
        }
        result = self.gql(AUTOSAVE_MUTATION, {"data": data})
        res = result.get("autoSaveSolutionArticle") or {}
        if not res.get("ok"):
            raise RuntimeError(f"autoSaveSolutionArticle failed: {res.get('error')}")
        return res.get("article")

    def submission_list(self, question_slug, limit=30):
        """List this account's submissions for a question (for multi-language code)."""
        data = self.gql(SUBMISSION_LIST_QUERY,
                        {"offset": 0, "limit": limit, "questionSlug": question_slug})
        conn = data.get("submissionList") or {}
        return conn.get("submissions") or []

    def list_drafts(self, question_slug, first=10):
        data = self.gql(DRAFTS_QUERY, {"questionSlug": question_slug,
                                       "first": first, "skip": 0})
        conn = data.get("solutionDrafts") or {}
        return [e.get("node") for e in conn.get("edges", []) if e.get("node")]


if __name__ == "__main__":
    cli = LeetCodeClient()
    print("[whoami]", json.dumps(cli.whoami(), ensure_ascii=False))
    sid = sys.argv[1] if len(sys.argv) > 1 else "754693208"
    detail = cli.submission_detail(sid)
    if not detail:
        print(f"[submission {sid}] NOT FOUND (可能不属于当前账号或已过期)")
        sys.exit(1)
    q = detail.get("question") or {}
    print(f"[submission {sid}]")
    print(f"  question : {q.get('questionFrontendId')}. {q.get('translatedTitle')} ({q.get('difficulty')})")
    print(f"  slug     : {q.get('titleSlug')}")
    print(f"  lang     : {detail.get('lang')}  runtime={detail.get('runtimeDisplay')}  memory={detail.get('memoryDisplay')}")
    print(f"  code({len(detail.get('code') or '')} chars):")
    print(detail.get("code", ""))
