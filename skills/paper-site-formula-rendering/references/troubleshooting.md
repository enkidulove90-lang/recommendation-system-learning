# Formula troubleshooting and regression evidence

## Historical failures

The OpticalRec article exposed four different failure modes:

1. `$$` and LaTeX appeared literally because MathJax was absent or did not typeset the article.
2. `\(...\)` became ordinary `(...)` because the full Hexo post pipeline consumed the backslash delimiters.
3. `_` and `*` inside inline formulas were parsed as Markdown emphasis, producing fragments such as `\mathbf{x}*i`, `\mathcal{D}*`, `$y`, or `$\mathcal{D}`.
4. A local renderer test passed while the build remained wrong because `db.json` reused a stale rendered post. A query parameter such as `?v=math-v2` changes browser cache identity but cannot repair bad generated HTML.

## Locate the failing layer

Use the smallest observation that distinguishes the layers:

- Source: count `$...$` and `$$...$$`; scan for `�`, bare `\math...` in parentheses, unbalanced delimiters, `\_`, and corruption fragments.
- Hexo post object: initialize Hexo with a temporary database path, load locals, and inspect the target post content. This catches filters not exercised by a direct `hexo.render.render()` call.
- Built HTML: after `hexo clean && hexo generate`, parse with a DOM parser. Assert wrapper counts, delimiters, and `em .math-inline, .math-inline em == 0`.
- Browser: use the deployed page DOM. Count `.math-inline mjx-container` and `.math-display mjx-container`; both must equal their wrapper counts. Check the page has neither `paper-math-load-failed` nor `paper-math-typeset-failed`.

## Correct filter behavior

Protect formulas in `before_post_render`:

- Convert inline source math to a raw `<span class="math-inline">$...$</span>` wrapper.
- Encode Markdown-sensitive `_` and `*` inside that raw inline wrapper as numeric HTML entities before Markdown parsing. The browser decodes them back to the original LaTeX for MathJax.
- Convert display math to a block wrapper retaining `\[...\]` or another MathJax display delimiter that survives the configured renderer.
- Do not mutate the formula body beyond HTML/Markdown protection.

## Required regression cases

At minimum cover:

- `I(\mathbf{q}_i;\mathbf{x}_i)` with multiple subscripts;
- `\mathcal{D}_{\mathrm{intra}}^{\mathrm{LF}}` adjacent to Chinese prose;
- `\mathrm{erank}(\mathbf{X})=\exp(-\sum_{i=1}^{n}p_i\log p_i)`;
- multiple inline formulas on one line;
- one display formula;
- a fresh full-Hexo load using a temporary database;
- deployed DOM formula counts.

Evidence is acceptable only when it reports expected and actual counts, the exact failed layer, and absence of known corruption patterns. A green workflow alone is insufficient.
