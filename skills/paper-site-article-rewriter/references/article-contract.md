# Chinese paper-site article contract

Use the rewritten FOCUS article (`paper-2608.01847`) as the tone and structure reference, not as wording to copy.

## Opening

Write 3–6 connected paragraphs without an `Introduction` heading:

1. Explain why the problem matters in its technical or application setting.
2. Locate the paper honestly: authors or organizations when known, venue status, and what makes the question timely. “Important” must be justified by the problem, evidence, adoption, or code—not hype.
3. State the exact research tension or question.
4. State important preconditions and what the method does not change.

## Method or survey framework

Use numbered Chinese subsections. Start from the baseline or missing capability, then follow the actual data flow. Define symbols only when they help understanding. Place a figure immediately after the concept it explains.

After each figure, write one or more ordinary Chinese paragraphs. A useful explanation answers:

- Which region should the reader inspect first?
- What changes from the baseline to the proposed method?
- Which information or tensor flows between modules?
- Which claimed advantage does this visual support?

Do not emit labels such as `原图说明：` or `图示解释：`. Do not paste the source caption beneath the image.

## Experiments or evidence

Begin with a compact table of datasets, tasks, splits, baselines, metrics, and implementation conditions. Then present the main comparison as Markdown tables with directional arrows in headers.

For every result table, explain:

- the strongest relevant comparator;
- absolute changes in the original metric;
- whether gains are consistent across datasets, models, or settings;
- exceptions or cases where the method is not best;
- the mechanism that the evidence supports, without claiming causality beyond the ablation.

Present module ablations and hyperparameter or efficiency experiments in separate subsections when the paper reports them. Include resource costs when they change the practical interpretation.

For surveys or position papers, replace benchmark tables with taxonomy, corpus coverage, or evidence-comparison tables. Explicitly say that a unified experiment is absent.

## Summary and references

The summary should synthesize rather than repeat. Include at least one limitation or boundary and one reusable design insight.

References must begin with the focal paper and link to arXiv or DOI plus the verified official repository. Add only the most relevant compared or foundational works; do not dump the full bibliography.

## Rejection conditions

Reject or revise a draft if it contains any of the following:

- duplicated abstract or background;
- headings named `研究问题`, generic `创新点`, or `实验：数据、基线与结果`;
- English caption paragraphs or boilerplate figure explanations;
- a figure described by the same sentence as another figure;
- results without a table when exact values are available;
- “达到 SOTA” without specifying the comparison and metric;
- unsupported numbers, venue claims, repository links, or causal explanations;
- missing image files or a broken local PDF link.
