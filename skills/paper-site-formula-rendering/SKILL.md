---
name: paper-site-formula-rendering
description: Generate, diagnose, or repair LaTeX formulas in Hexo/Butterfly paper articles. Use when paper prose contains inline or display mathematics, raw LaTeX appears online, Markdown damages underscores or asterisks, or MathJax/cache behavior must be verified end to end.
---

# Paper Site Formula Rendering

Keep mathematical meaning in the article source and make the renderer—not the language model—responsible for HTML structure.

## Author formulas

- Write inline math as `$...$` and display math as `$$...$$` on separate lines with blank lines around the block.
- Inside math, use ordinary LaTeX subscripts and superscripts such as `x_i`, `D_{\mathrm{intra}}`, and `q_i^{\mathrm{LF}}`. Do not escape `_` as `\_`.
- Never imitate math with plain parentheses such as `(\mathcal{I}_i)`, Markdown emphasis, a code fence, or prebuilt MathJax HTML.
- Keep Chinese punctuation and prose outside the delimiters.
- Reject `U+FFFD` (`�`) before generation or publication. Restore titles and metadata from an authoritative source; do not ask the model to guess corrupted text.

## Render and verify

The Hexo filter must protect formulas before Markdown parses emphasis markers. Inline formulas require Markdown-sensitive `_` and `*` to be HTML-entity protected while retaining MathJax delimiters. The browser loads one self-hosted MathJax bundle, then typesets the complete article.

Do not claim success from source inspection or a unit test around one renderer call. Verify all three layers:

1. Fresh Hexo database or `hexo clean` followed by a build.
2. Generated HTML contains the expected formula wrapper counts, complete delimiters, no formula nested under `<em>`, and no known corruption fragments.
3. The deployed DOM contains one `mjx-container` per formula, no raw formula wrappers, and no loader/typeset failure class.

Read [references/troubleshooting.md](references/troubleshooting.md) when diagnosing a failure, changing the Hexo filter, or preparing regression evidence.

## Publication boundary

Formula repair must not rewrite numerical claims or mathematical semantics. Stop publication when delimiters are unbalanced, a formula is truncated, `�` is present, or the deployed MathJax count differs from the generated formula count.
