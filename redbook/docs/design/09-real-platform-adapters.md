# Real platform adapters

All adapters consume a validated `paper_card.json`, render their own content,
then follow exactly one contract:

```text
validate -> stage -> receipt
```

`stage` never means public publishing. There is deliberately no CLI command
that can publish a social post. The `publish()` method is an approval boundary
which always returns `approval_required` until a separately audited approval
system is introduced.

## Run the capability check

```powershell
python -m redbook.automation.cli --data-root data platform-doctor
```

The command is read-only. It reports missing local credentials and backend
tools; it does not attempt login, create content, or inspect browser cookies.

## Stage from the canonical fact card

```powershell
python -m redbook.automation.cli --data-root data stage-platform `
  --platform wechat `
  --paper-card data/workflow_state/<paper-id>/paper_card.json `
  --canonical-url https://example.org/papers/<paper-id>/
```

Every result is stored at:

```text
data/publish_results/<platform>/<content-hash>.json
```

The receipt contains the fact-card-derived content hash, platform state,
external draft/page ID when one exists, and the local artifact path otherwise.
Repeating the same content hash returns `already_staged` instead of writing a
second external draft.

## Supported adapters and safety boundary

| Priority | Adapter | Real stage operation | Public write |
| --- | --- | --- | --- |
| P0 | `github_pages` | Commit canonical Markdown through `gh api` to a private staging repository and `REDBOOK_GITHUB_PAGES_BRANCH` | Never; a separate approved deployment moves content to a public Pages source |
| P0 | `notion` | Create a page through the official Notion API | Sharing remains controlled in the Notion workspace |
| P0 | `wechat` | `opencli weixin create-draft` creates a creator draft | Never |
| P1 | `zhihu` | `opencli zhihu search` retrieves question candidates | Never; `answer` is a direct public write and is blocked from stage |
| P1 | `x` | Generate an English thread/composer package | Never; `twitter post` is direct public write |
| P1 | `jike` | Generate a short-post/composer package | Never; `jike create` is direct public write |
| P2 | `bilibili` | Generate a topic, figure selection, and video-script package | Never |

This follows Agent-Reach's useful separation of a capability-routing layer from
the underlying platform tools: a platform can expose a healthy read backend
without being authorized for a write backend. The adapter therefore reports
the actual backend and its missing prerequisites rather than silently falling
back to an unrelated command. See [Agent-Reach's capability routing design](https://github.com/Panniantong/Agent-Reach).

## Required configuration

GitHub canonical staging requires an authenticated `gh` CLI plus:

```text
REDBOOK_GITHUB_PAGES_REPO=owner/repository
REDBOOK_GITHUB_PAGES_BRANCH=redbook-staging
REDBOOK_GITHUB_PAGES_PATH=content/papers
```

The repository itself must be private, and the adapter also rejects `main`,
`master`, and `gh-pages` as staging branches. A repository owner must
separately review and move content into whatever public repository, branch, or
Action is configured to publish the site.

Notion canonical staging requires:

```text
NOTION_TOKEN=<integration token>
NOTION_PARENT_PAGE_ID=<parent page id>
```

The integration only creates a workspace page. It does not change the page's
sharing state or enable a public Notion site.

WeChat uses the existing, user-controlled browser session through OpenCLI.
Before staging, log in manually to the intended official-account creator
workspace. `stage-platform --platform wechat` then creates a draft with a
cover taken from the first qualified paper figure. If login, cover upload, or
creator validation fails, it returns a failed receipt and does not retry with
a publish command.

## Zhihu question selection

```powershell
python -m redbook.automation.cli --data-root data stage-platform `
  --platform zhihu `
  --paper-card data/workflow_state/<paper-id>/paper_card.json `
  --canonical-url https://example.org/papers/<paper-id>/ `
  --zhihu-query "your research question"
```

The receipt is `manual_action_required` and its local artifact contains the
returned question candidates and the answer package. A reviewer must choose a
question and explicitly invoke a future, separately approved public-answer
workflow. This prevents a relevance match from being mistaken for permission
to post.
