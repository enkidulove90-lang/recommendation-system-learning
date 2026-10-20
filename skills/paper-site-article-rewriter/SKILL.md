---
name: paper-site-article-rewriter
description: Rewrite parsed academic papers into evidence-backed Chinese website articles with an editorial introduction, method-focused figure explanations, experiment tables, ablations, summary, and references. Use for the recommendation-system-learning paper site; do not use for short social-media briefs or raw paper summaries.
---

# Paper Site Article Rewriter

Turn a PDF, arXiv source, MinerU Markdown, or an existing weak draft into a readable Chinese research article. Preserve factual traceability while writing in an editor's voice rather than translating the paper paragraph by paragraph.

## Required outcome

- Put the paper, official code when verified, and local PDF links at the top.
- Open with several Chinese paragraphs covering context, current research position, the precise problem, and deployment or experimental preconditions. Do not repeat the abstract under another heading.
- Organize empirical papers as `一、方法` → `二、实验` → `三、总结` → `References`. Adapt surveys to `综述框架` and `证据与比较` rather than inventing experiments.
- Explain every retained figure in original Chinese prose. Discuss what to look at, how information flows, and which claim the figure supports. Never reproduce an English caption as a separate paragraph.
- Integrate innovations into the relevant method subsections instead of creating a generic innovation list.
- Reconstruct result and ablation tables from source evidence. Explain patterns, trade-offs, limitations, and which module causes which change; do not merely announce that the method is best.
- End with a bounded conclusion: problem, mechanism, evidence, limitations, reusable insight.

Read [references/article-contract.md](references/article-contract.md) before editing or reviewing an article. For batch rewrites, use `scripts/rewrite_articles.py`; it checkpoints API results, validates claims and assets, and only replaces a post after validation.

## Evidence rules

Prefer arXiv LaTeX and author assets, then MinerU Markdown and images, then a reliable project summary. Existing generated prose is a discovery aid, not authoritative evidence.

- Keep exact experimental values, dataset names, model versions, and venue status.
- Do not call an arXiv preprint accepted unless the source proves it.
- Do not invent a GitHub repository, ablation, benchmark, or explanation for an unreadable figure.
- Use at most four informative figures by default. Exclude screenshots of prompts, raw English tables, decorative logos, and near-duplicates unless they are central evidence.
- If no independent ablation exists, state that boundary naturally; never fabricate one to satisfy the structure.

## Validation

Build the site and inspect the rendered article. Confirm that every image loads, tables fit the content column, headings form a useful table of contents, English-caption boilerplate is absent, and all numerical claims occur in the supplied evidence. Keep changes local for review unless the user also asks to publish.
