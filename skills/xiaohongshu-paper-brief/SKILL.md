---
name: xiaohongshu-paper-brief
description: Draft the text portion of a factual Xiaohongshu paper post from an arXiv paper, parsed PDF, or structured evidence. Use for requests involving paper explainers, conference/company paper posts, experiment summaries, or a Xiaohongshu draft that must include accessible arXiv and official GitHub links.
---

# Xiaohongshu Paper Brief

Create the text payload only. Do not publish. Use the paper, parsed Markdown, and official links as the only source of factual claims.

## Input checklist

Collect or explicitly mark missing:

- Conference or journal, year, company or institution, and paper title.
- Paper type: empirical, benchmark, system, survey, or perspective.
- Main contributions, method, benchmark/data, experimental setup, metrics, and results.
- Official arXiv/PDF and official GitHub. Never infer a repository is official from a third-party index.
- Practical implication for the requested target system, such as a recommender or agent.

## Write the post

Use [post-template.md](references/post-template.md). Keep the title under 20 Chinese characters. Begin with a reader-facing question or surprising mechanism rather than a generic paper title.

Rules:

1. State the venue/year/company only when verified; otherwise write `原文未披露`.
2. Separate paper-reported results from the editor's interpretation. Use `论文报告` for the former.
3. For empirical papers, include task, datasets, baselines, metrics, hardware/key settings when available, and only reported numbers.
4. For surveys and perspective papers, write `不适用：本文未提出统一实验` instead of fabricating benchmarks, baselines, or gains.
5. Explain the implication as a transferable design lesson, not a deployment promise.
6. Put `arXiv 链接` and `GitHub 链接` on separate lines. Write `暂无已核验官方 GitHub` when missing.
7. Return a JSON object containing `title`, `body`, `topics`, and `comment_prompt`. Use 3–5 candidate topic names only; platform entity binding is a separate delivery gate.

## Topic candidates

Prefer concrete, searchable topics aligned with the evidence: `人工智能`, `大模型`, `智能体`, `推荐系统`, `多模态`, `论文解读`. Do not insert `#` into the generated body; let the delivery workflow resolve genuine topic entities.

