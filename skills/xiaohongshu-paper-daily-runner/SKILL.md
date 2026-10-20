---
name: xiaohongshu-paper-daily-runner
description: Run or repair the strict Xiaohongshu paper-daily workflow in this repository. Use when discovering experimental papers, qualifying PDF/GitHub/MinerU/figures, creating a factual paper brief, saving a Xiaohongshu draft with real topic entities and a same-editor PDF attachment, configuring the 18-hour qualification queue, or diagnosing a hard-gate failure. Never use it to publicly publish a note.
---

# Xiaohongshu Paper Daily Runner

Create only verified `draft_only` Xiaohongshu paper posts. Treat every missing
hard gate as a terminal skip; never substitute a plain hashtag, third-party
repository, URL-only PDF, or public publish action.

## Run the workflow

1. Read [workflow.md](references/workflow.md) before acting; it contains the
   exact sequence, commands, acceptance checks, and recovery matrix.
2. Use `academic-search` and `arxiv` for discovery and verification. Use
   `xiaohongshu-paper-brief` for evidence-bound post text.
3. Use `python -m redbook.cli save-xhs-draft` as the only platform delivery
   entry point. Its only allowed terminal state is `saved_draft_only`.
4. Start or change the discovery cadence with:

   ```powershell
   python -m redbook.automation.cli --data-root data run-daily --interval-hours N
   ```

   The configured default is 18 hours. This command only discovers and queues
   candidates; it does not make Xiaohongshu drafts.
5. Store every candidate, skip, receipt, and recovery decision in
   `data/workflow_state/<arxiv-id>/`. Never delete an existing user draft to
   make a run pass.

## Invariants

- Require official public PDF, verified venue/trusted preprint, official
  GitHub, local MinerU parse, and at least four qualified figures.
- Bind actual topic entities and verify `a.tiptap-topic[data-topic]` before
  saving. A literal `#topic` fails.
- Upload and verify the local PDF filename in the same creator editor before
  saving.
- Use a unique title in readiness testing; resume an auto-saved draft only by
  explicit draft ID.
- Never call legacy `publish*.py`, direct API publishers, or public publish.
