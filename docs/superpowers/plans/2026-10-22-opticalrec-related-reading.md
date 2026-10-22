# OpticalRec Single-Paper Direct Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Regenerate only `paper-2610.05432` from its existing MinerU artifact, add two verified recommended references and route-scoped typography/LaTeX rendering, then update the existing live URL with test-to-evidence parity and rollback protection.

**Architecture:** Deterministic Python code extracts and verifies reference candidates, while the existing DeepSeek call remains responsible for article generation and performs only a constrained `ref_id` selection as an additional result. Article and ranking results have separate logical caches; rendering is idempotent, and a single-paper release command enforces exact job/page/slug identity before Notion or site writes. The Hexo site loads typography and MathJax only on the target route.

**Tech Stack:** Python 3, Pydantic, pytest, requests/httpx-compatible adapters, Notion API, Hexo, Butterfly, vanilla JavaScript, MathJax, GitHub Actions/Pages.

**Spec:** `docs/superpowers/specs/2026-10-22-opticalrec-related-reading-design.md`

## Global Constraints

- Scope is exactly arXiv `2610.05432`, slug `paper-2610.05432`, and its existing live URL.
- Reuse the existing MinerU Markdown; MinerU must not run during this release.
- Preserve the current article-generation prompt and content requirements; add only formula syntax and constrained reference-selection instructions.
- The model may return only candidate `ref_id` values and reasons; code owns all identifiers and URLs.
- Do not use BM25; invalid recommendation output degrades to the latest two deterministic candidates without failing valid article generation.
- Never invent a paper URL, code URL, relevance reason, author, venue, or year.
- Only a pinned, checksum-verified local Papers with Code snapshot may provide code URLs; absence degrades to `null`.
- Do not modify or commit the existing unrelated `redbook/` working-tree changes.
- Evidence is local, redacted, hash-addressed, and excluded from Git.
- No Notion or GitHub Pages mutation occurs before all local mandatory tests and evidence parity checks pass.

## Review Focus

- A References heading with wrapped/multiline entries must preserve original order and not merge two citations; Task 2 pins this case.
- DOI punctuation, `arXiv:xxxx.xxxxxvN`, and old-style arXiv identifiers must normalize without accepting unrelated numbers; Task 2 pins these cases.
- A valid article plus an invalid ranking payload must publish the article with deterministic fallback rather than fail the job; Tasks 3 and 6 pin this case.
- A missing/corrupt Papers with Code snapshot or transient arXiv/Crossref failure must never create a guessed link or block publication; Task 4 pins this case.
- Re-running the exact release after a partial Notion/site write must update the same targets and keep one recommendation block; Tasks 5, 7, and 9 pin this case.

---

## Test-to-Evidence Contract

| ID | Acceptance condition | Required evidence |
|---|---|---|
| TC-01 | Reference extraction accepts only normalized arXiv/DOI candidates with stable IDs | `tc-01-reference-extraction.json` |
| TC-02 | Source/candidate hashes are stable and exclude an existing generated block | `tc-02-hash-stability.json` |
| TC-03 | Existing prompt is byte-for-byte pinned except the two approved additions | `tc-03-prompt-diff.json` |
| TC-04 | Ranking validation is soft; malformed ranking never invalidates a valid article | `tc-04-soft-validation.json` |
| TC-05 | Latest-two fallback, partial fill, and empty-candidate behavior are deterministic; no BM25 exists | `tc-05-fallback.json` |
| TC-06 | arXiv/DOI/code URLs come only from deterministic verified resolvers | `tc-06-link-resolution.json` |
| TC-07 | Identical inputs make zero additional model calls; cache dimensions invalidate correctly | `tc-07-cache.json` |
| TC-08 | Recommendation rendering is marker-based, byte-idempotent, and labeled correctly | `tc-08-render-idempotency.json` |
| TC-09 | `$...$` and `$$...$$` survive Hexo build and MathJax is target-route-only | `tc-09-mathjax-build.json` |
| TC-10 | Target typography applies; a control article remains unchanged | `tc-10-route-isolation.json` |
| TC-11 | Single-paper dry-run reuses MinerU and selects exactly one job/page/slug | `tc-11-single-paper-dry-run.json` |
| TC-12 | No other post changes; allowed source/config assets are explicitly enumerated | `tc-12-scope-hashes.json` |
| TC-13 | Recommendation-stage failure degrades; article-generation failure retains existing hard-fail semantics | `tc-13-failure-isolation.json` |
| TC-14 | Every mandatory ID has one valid evidence file and secret scan has zero matches | `tc-14-evidence-audit.json` |
| TC-15 | Actions succeeds and the existing live URL contains one verified recommendation block | `tc-15-live-verification.json` |
| TC-16 | Notion and Git rollback inputs are complete and restorable | `tc-16-rollback-rehearsal.json` |

The release gate reads this table as data from `scripts/single_paper_evidence.py`; a pytest success without its corresponding evidence is a failure. A mismatch sends execution back to the task owning that TC, followed by a complete TC-01–TC-14 rerun before another publication attempt.

## File Structure

**Main repository**

- Create `paper_intake/reference_candidates.py`: extraction, normalization, stable IDs, hashes, deterministic fallback.
- Create `paper_intake/reference_links.py`: arXiv/Crossref/Papers-with-Code resolvers and safe partial failure.
- Create `paper_intake/generation_cache.py`: article/ranking cache records and keys.
- Modify `paper_intake/article.py`: constrained recommendation models, soft ranking parsing, marker rendering.
- Modify `paper_intake/adapters.py`: approved prompt additions and combined response parsing.
- Modify `paper_intake/pipeline.py`: cache use and recommendation enrichment without MinerU changes.
- Create `scripts/reprocess_single_paper.py`: exact-scope dry-run/publish coordinator.
- Create `scripts/single_paper_evidence.py`: evidence manifest, hashing, redaction scan, parity gate.
- Create `scripts/verify_single_paper_release.py`: live and rollback verification.
- Create `config/pwc-snapshot.json`: pinned source revision and SHA256 manifest only.
- Modify `.gitignore`: ignore snapshot payload/cache and evidence outputs.
- Create/modify tests named in the tasks below.

**Website worktree** (`.worktrees/site-ui-fixes`)

- Modify `source/_posts/paper-2610.05432.md`: regenerated single article only after the gate.
- Create `source/css/paper-2610.05432.css`: target-only typography.
- Create `source/js/paper-2610.05432.js`: target-only body class and MathJax loading.
- Modify `_config.butterfly.yml`: inject the small route guard; no global typography change.
- Create `tests/paper-2610-page.test.js`: route/build assertions.

### Task 1: Evidence Harness and Release Gate

**Files:**
- Create: `scripts/single_paper_evidence.py`
- Modify: `.gitignore`
- Test: `tests/test_single_paper_evidence.py`

**Interfaces:**
- Produces: `EvidenceRecorder(root: Path, run_id: str)`, `record(test_id: str, command: list[str], exit_code: int, assertions: dict, evidence_path: Path)`, `audit(required_ids: Sequence[str]) -> EvidenceAudit`.
- Evidence manifest fields: `test_id`, `command`, `exit_code`, `assertions`, `path`, `sha256`, `recorded_at`.

- [ ] **Step 1: Write failing evidence-contract tests**

Pin: duplicate IDs fail; missing files fail; modified SHA256 fails; assertion/evidence contradiction fails; secret regex hits fail; a two-phase audit can first validate TC-01–TC-13, record TC-14 from that immutable audit result, and then validate TC-01–TC-14 exactly once without a self-referential hash.

- [ ] **Step 2: Run the focused test and confirm RED**

Run: `python -m pytest tests/test_single_paper_evidence.py -q`
Expected: FAIL because the recorder and audit do not exist.

- [ ] **Step 3: Implement the minimal recorder and audit**

Use JSON with stable key ordering. Scan text evidence for case-insensitive `authorization`, `bearer`, `token`, `password`, and known key prefixes; store only command names/arguments after secret-value redaction.

- [ ] **Step 4: Run focused tests and emit harness evidence**

Run: `python -m pytest tests/test_single_paper_evidence.py -q`
Expected: PASS. Do not yet create release manifest entries; this validates the harness itself.

- [ ] **Step 5: Commit**

Run: `git add .gitignore scripts/single_paper_evidence.py tests/test_single_paper_evidence.py`

Run: `git commit -m "test(intake): add single-paper evidence gate"`

### Task 2: Deterministic Reference Candidates and Hashes

**Files:**
- Create: `paper_intake/reference_candidates.py`
- Test: `tests/test_reference_candidates.py`
- Test fixture: `tests/fixtures/references/2610.05432-excerpt.md`

**Interfaces:**
- Produces: `ReferenceCandidate(ref_id, raw_text, title, year, arxiv_id, doi, original_index)`.
- Produces: `extract_reference_candidates(markdown: str) -> list[ReferenceCandidate]`.
- Produces: `strip_generated_related_reading(markdown: str) -> str`, `source_hash(markdown: str) -> str`, `candidate_hash(candidates: Sequence[ReferenceCandidate]) -> str`.
- Produces: `select_latest(candidates, count=2, excluded_ids=frozenset()) -> list[ReferenceCandidate]`.

- [ ] **Step 1: Write failing TC-01 and TC-02 tests**

Assert stable `ref_001...`, multiline parsing, DOI punctuation removal, arXiv version removal, modern and old-style IDs, unrelated numeric text exclusion, deterministic original order, and identical source hashes before/after replacing a generated block.

- [ ] **Step 2: Run and confirm RED**

Run: `python -m pytest tests/test_reference_candidates.py -q`
Expected: FAIL because the module is missing.

- [ ] **Step 3: Implement extraction, normalization, hashing, and latest ordering**

The fallback sort key is `(year desc, normalized arXiv YYMM desc, original_index asc)`. Unknown years sort last. No lexical relevance function or BM25 dependency is permitted.

- [ ] **Step 4: Run and record TC-01/TC-02**

Run: `python -m pytest tests/test_reference_candidates.py -q`
Expected: PASS. Write normalized candidate samples and repeat hashes to the two evidence files, then register them.

- [ ] **Step 5: Commit**

Run: `git add paper_intake/reference_candidates.py tests/test_reference_candidates.py tests/fixtures/references/2610.05432-excerpt.md`

Run: `git commit -m "feat(intake): extract deterministic reference candidates"`

### Task 3: Prompt Extension, Soft Ranking Validation, and Logical Cache

**Files:**
- Modify: `paper_intake/article.py:88-340`
- Modify: `paper_intake/adapters.py:113-230`
- Create: `paper_intake/generation_cache.py`
- Test: `tests/test_intake_article.py`
- Test: `tests/test_intake_adapters.py`
- Test: `tests/test_generation_cache.py`

**Interfaces:**
- Produces: `ReferenceChoice(ref_id: str, reason: str)` and `GenerationEnvelope(article: PaperArticle, reference_choices: list[ReferenceChoice] | None)`.
- Produces: `parse_generation_envelope(raw: str, eligible_ids: set[str]) -> GenerationEnvelope`; article schema violations raise, ranking violations return `reference_choices=None` plus a safe diagnostic.
- Produces: `GenerationCache.get_article/put_article` and `get_ranking/put_ranking` using the five cache dimensions in the spec.

- [ ] **Step 1: Pin the current prompt before modification**

Write TC-03 asserting the exact current system string and existing requirements remain present. Assert the only new requirement keys are `formula_format` and `reference_selection`, and the latter lists eligible IDs without URLs.

- [ ] **Step 2: Write TC-04 and TC-07 failing tests**

Cover valid choices, duplicate IDs, unknown IDs, missing reasons, malformed ranking JSON with a valid article, identical-input zero-call cache hit, and invalidation by source/candidate/model/prompt/rule changes.

- [ ] **Step 3: Run focused tests and confirm RED**

Run: `python -m pytest tests/test_intake_article.py tests/test_intake_adapters.py tests/test_generation_cache.py -q`
Expected: FAIL on the new envelope/cache behavior.

- [ ] **Step 4: Implement the approved prompt delta and separate logical caches**

Keep the existing system prompt exactly: `你是推荐系统论文编辑。只输出符合给定 Schema 的 JSON；不得虚构实验数字、链接或图片路径。` Do not add content constraints. Formula text must specify `$...$`/`$$...$$`; selection asks for exactly two `ref_id` values with short reasons.

- [ ] **Step 5: Run and record TC-03/TC-04/TC-07**

Run the same pytest command; expected PASS. Evidence stores prompt key diff, validation cases, cache keys, and model-call counts—never the full model response.

- [ ] **Step 6: Commit**

Run: `git add paper_intake/article.py paper_intake/adapters.py paper_intake/generation_cache.py tests/test_intake_article.py tests/test_intake_adapters.py tests/test_generation_cache.py`

Run: `git commit -m "feat(intake): add constrained reference ranking to generation"`

### Task 4: Verified Link Resolution and Safe Fallback

**Files:**
- Create: `paper_intake/reference_links.py`
- Create: `config/pwc-snapshot.json`
- Create: `scripts/bootstrap_pwc_snapshot.py`
- Test: `tests/test_reference_links.py`
- Test fixtures: `tests/fixtures/pwc/minimal-links.json`, `tests/fixtures/http/reference-responses.json`

**Interfaces:**
- Produces: `ResolvedReference(candidate, paper_url, code_url, link_source, verification_status)`.
- Produces: `resolve_selected_references(candidates, choices, clients, pwc_snapshot) -> ResolutionResult` with `mode: "recommended" | "supplemental" | "omitted"`.
- The snapshot loader requires manifest revision and SHA256 equality; any mismatch disables code links.

- [ ] **Step 1: Write TC-05/TC-06 failing tests**

Cover arXiv and DOI success, 404/429/TLS failure, valid/corrupt/missing PWC fixture, GitHub URL acceptance only from snapshot, partial model selection fill, latest-two ordering, no candidates, and repository scan asserting no `BM25`/`rank_bm25` reference in production modules.

- [ ] **Step 2: Run and confirm RED**

Run: `python -m pytest tests/test_reference_links.py -q`
Expected: FAIL because resolvers are absent.

- [ ] **Step 3: Implement deterministic resolvers**

Batch arXiv requests where possible; normalize DOI URLs to `https://doi.org/<doi>`. Retry only safe reads under the shared network policy. Never synthesize a URL when verification fails.

- [ ] **Step 4: Implement snapshot bootstrap without committing the payload**

`bootstrap_pwc_snapshot.py` downloads only the manifest-pinned revision, verifies SHA256, and writes under ignored `.paper-work/cache/pwc/`. Failure exits nonzero but does not block article publishing; the runtime then emits `code_url=null`.

- [ ] **Step 5: Run and record TC-05/TC-06**

Run the focused test; expected PASS. Evidence records identifiers, statuses, and safe URL origins, not response bodies.

- [ ] **Step 6: Commit**

Run: `git add paper_intake/reference_links.py config/pwc-snapshot.json scripts/bootstrap_pwc_snapshot.py tests/test_reference_links.py tests/fixtures/pwc/minimal-links.json tests/fixtures/http/reference-responses.json`

Run: `git commit -m "feat(intake): resolve verified reading links"`

### Task 5: Idempotent Markdown Rendering

**Files:**
- Modify: `paper_intake/article.py:295-340`
- Test: `tests/test_related_reading_render.py`

**Interfaces:**
- Produces: `render_related_reading(result: ResolutionResult) -> str`.
- Produces: `replace_related_reading(markdown: str, block: str | None) -> str`.
- `render_article_markdown` consumes optional resolved references but preserves its current output when none are supplied.

- [ ] **Step 1: Write TC-08 failing tests**

Assert exactly one marker pair, second rendering is byte-identical, recommended/fallback headings differ, missing code link is omitted, no valid candidates removes the entire block, and the block is the final article section.

- [ ] **Step 2: Run and confirm RED**

Run: `python -m pytest tests/test_related_reading_render.py -q`
Expected: FAIL on missing marker renderer.

- [ ] **Step 3: Implement marker replacement**

Strip any previous generated block before appending. Never modify author-provided References text outside the markers.

- [ ] **Step 4: Run and record TC-08**

Expected: PASS. Evidence contains first/second hashes and marker counts.

- [ ] **Step 5: Commit**

Run: `git add paper_intake/article.py tests/test_related_reading_render.py`

Run: `git commit -m "feat(intake): render idempotent related reading"`

### Task 6: Pipeline Integration and Failure Isolation

**Files:**
- Modify: `paper_intake/pipeline.py:266-350`
- Test: `tests/test_intake_pipeline.py`

**Interfaces:**
- `_step_deepseek_generate(job_id)` extracts candidates before the existing model call, applies caches, and writes separate safe ranking diagnostics.
- `_step_quality_check(job_id)` resolves links and renders the final marker block.
- Recommendation exceptions become supplemental/omitted results; article-generation exceptions retain the current failed-stage semantics.

- [ ] **Step 1: Write TC-13 and pipeline cache tests**

Use fakes to prove recommendation parsing/resolution failure still reaches quality check, DeepSeek article failure still fails, and a cache hit makes zero adapter calls.

- [ ] **Step 2: Run and confirm RED**

Run: `python -m pytest tests/test_intake_pipeline.py -q`
Expected: FAIL on missing integration.

- [ ] **Step 3: Integrate without changing MinerU or Notion behavior**

Do not change `_step_mineru_parse`. Persist cache metadata and safe diagnostics under the job artifact root; exclude full raw model output from evidence/export.

- [ ] **Step 4: Run and record TC-13**

Run focused test; expected PASS. Evidence lists final job result per injected failure and contains no traceback/provider body.

- [ ] **Step 5: Commit**

Run: `git add paper_intake/pipeline.py tests/test_intake_pipeline.py`

Run: `git commit -m "feat(intake): isolate recommendation failures"`

### Task 7: Exact-Scope Single-Paper Coordinator and Rollback Inputs

**Files:**
- Create: `scripts/reprocess_single_paper.py`
- Create: `scripts/verify_single_paper_release.py`
- Test: `tests/test_single_paper_reprocess.py`

**Interfaces:**
- CLI: `reprocess_single_paper.py --job-id UUID --canonical-id 2610.05432 --expected-slug paper-2610.05432 --reuse-mineru --dry-run|--publish --evidence-dir PATH`.
- Dry-run returns a `ReleasePlan` containing exact artifact, Notion page, site source, pre-write hashes, and allowed changed paths.
- Publish refuses if any identity differs, MinerU artifact is missing, evidence gate fails, or more than one Notion page/site post matches.

- [ ] **Step 1: Write TC-11/TC-12/TC-16 failing tests**

Assert MinerU fake call count is zero; wrong job/arXiv/slug/page aborts before writes; dry-run selects one target; backup hashes are complete; only enumerated site paths may differ; mocked rollback restores byte-identical Notion/source content.

- [ ] **Step 2: Run and confirm RED**

Run: `python -m pytest tests/test_single_paper_reprocess.py -q`
Expected: FAIL because the coordinator does not exist.

- [ ] **Step 3: Implement dry-run first**

Use `JobRepository.reset_steps` only from `deepseek_generate` onward and only after exact identity assertions. Snapshot Notion/source before mutation. Dry-run must perform no network write.

- [ ] **Step 4: Implement gated publish and rollback command**

Require the audited manifest path and expected pre-write hashes. Make publish idempotent: existing page/post is updated, never duplicated.

- [ ] **Step 5: Run and record TC-11/TC-12/TC-16**

Run focused tests; expected PASS. Evidence contains safe paths, IDs suffixes, hashes, and mocked restore hashes.

- [ ] **Step 6: Commit**

Run: `git add scripts/reprocess_single_paper.py scripts/verify_single_paper_release.py tests/test_single_paper_reprocess.py`

Run: `git commit -m "feat(intake): gate exact single-paper release"`

### Task 8: Target-Only Typography and MathJax

**Files (website worktree):**
- Create: `.worktrees/site-ui-fixes/source/css/paper-2610.05432.css`
- Create: `.worktrees/site-ui-fixes/source/js/paper-2610.05432.js`
- Modify: `.worktrees/site-ui-fixes/_config.butterfly.yml:114-125`
- Create: `.worktrees/site-ui-fixes/tests/paper-2610-page.test.js`

**Interfaces:**
- Route guard matches exactly `/article/paper-2610.05432/` with optional query/hash/trailing slash normalization.
- Guard adds `paper-2610-05432` to `<body>`, then loads MathJax once.
- CSS scopes every rule under `body.paper-2610-05432`.

- [ ] **Step 1: Write TC-09/TC-10 failing tests**

Assert target class, heading/body/Latin font stacks, preserved inline/block delimiters, one MathJax load on target, zero on a control article, and no global `.post-content` rule outside the target prefix.

- [ ] **Step 2: Run site tests and confirm RED**

Run from the worktree: `npm test -- paper-2610-page.test.js`
Expected: FAIL because assets/injection are missing.

- [ ] **Step 3: Implement route-scoped assets**

Use local CSS with `SimHei, Heiti SC` for titles/headings; `SimSun, Songti SC` for Chinese body; apply `Times New Roman` to explicit Latin/math selectors without forcing Chinese glyphs into Times.

- [ ] **Step 4: Build and record TC-09/TC-10**

Run: `npm test -- paper-2610-page.test.js` then `npm run build`.
Expected: PASS and successful Hexo build. Evidence records generated target/control HTML assertions and asset hashes.

- [ ] **Step 5: Commit website assets only**

Run in site worktree: `git add _config.butterfly.yml source/css/paper-2610.05432.css source/js/paper-2610.05432.js tests/paper-2610-page.test.js`

Run in site worktree: `git commit -m "style(article): scope OpticalRec typography and math"`

### Task 9: Full Local Gate, Single-Paper Publish, Live Verification

**Files:**
- Evidence only: `.paper-work/evidence/paper-2610.05432/<run_id>/`
- On successful generation only: `.worktrees/site-ui-fixes/source/_posts/paper-2610.05432.md`

**Interfaces:**
- Consumes every interface above.
- Produces final TC-14/TC-15 evidence and a release/rollback record.

- [ ] **Step 1: Discover and freeze the exact job identity read-only**

Run the coordinator in identity-only mode. Record job ID, arXiv ID, slug, Notion page suffix, MinerU artifact path/hash, source post hash, and current main/site commits. Abort if any target is ambiguous.

- [ ] **Step 2: Run the complete local test suites**

Main: `python -m pytest tests -q`.

Site: `npm test` and `npm run build` from `.worktrees/site-ui-fixes`.

Expected: all PASS. Store raw command logs with secret redaction.

- [ ] **Step 3: Run exact-scope dry-run using the frozen job ID**

Run: `python scripts/reprocess_single_paper.py --job-id <UUID> --canonical-id 2610.05432 --expected-slug paper-2610.05432 --reuse-mineru --dry-run --evidence-dir .paper-work/evidence/paper-2610.05432/<run_id>`.

Expected: one target, zero MinerU calls, no writes, all hashes stable.

- [ ] **Step 4: Run the two-phase TC-01–TC-14 evidence audit**

First run: `python scripts/single_paper_evidence.py audit --root <evidence-dir> --require TC-01,TC-02,TC-03,TC-04,TC-05,TC-06,TC-07,TC-08,TC-09,TC-10,TC-11,TC-12,TC-13 --write-audit tc-14-evidence-audit.json`.

Register the immutable `tc-14-evidence-audit.json` as TC-14, then run: `python scripts/single_paper_evidence.py audit --root <evidence-dir> --require TC-01,TC-02,TC-03,TC-04,TC-05,TC-06,TC-07,TC-08,TC-09,TC-10,TC-11,TC-12,TC-13,TC-14`.

Expected: `PASS`, 14 unique IDs, zero secret hits, every SHA256 valid. Any discrepancy returns to its owning task; after correction rerun the entire local gate.

- [ ] **Step 5: Publish the exact paper**

Run the same coordinator with `--publish` and the audited manifest. It updates the existing Notion page, writes only the target post, and emits Notion-before/after plus source-before/after hashes.

- [ ] **Step 6: Review and commit only the generated target post**

Run `git diff -- source/_posts/paper-2610.05432.md` in the site worktree. Confirm marker count is one, formulas use approved delimiters, and no other post hash changed. Commit with `git commit -m "content(article): refresh OpticalRec with related reading"`.

- [ ] **Step 7: Push the site branch and wait for GitHub Pages**

Push only after the user-approved branch integration path is confirmed. Capture workflow run ID, commit SHA, conclusion, and Pages deployment URL.

- [ ] **Step 8: Run TC-15 live verification**

Run: `python scripts/verify_single_paper_release.py --url https://enkidulove90-lang.github.io/article/paper-2610.05432/ --expected-commit <SHA> --control-url <unchanged-article-url> --evidence-dir <dir>`.

Expected: HTTP 200; exactly one recommendation block; two verified paper links when at least two valid candidates exist; target stylesheet and MathJax active; control article has neither target class nor target-only asset; GitHub Actions conclusion `success`.

- [ ] **Step 9: Final evidence audit including TC-15/TC-16**

Require TC-01–TC-16 exactly once. If the live result or evidence is abnormal, stop, execute the recorded rollback, attach rollback hashes, revise the owning task, rerun TC-01–TC-14, and only then attempt release again.

- [ ] **Step 10: Commit main-repository implementation after final green gate**

Exclude `.paper-work`, cached snapshots, credentials, Notion backups, and unrelated `redbook/` changes. Run `git status --short` and review every staged path before committing.

## Release Decision Rule

“Tests pass” alone is insufficient. Publication is approved only when all local commands pass, TC-01–TC-14 have exactly one matching valid evidence record, the evidence audit reports zero secret hits, and the change-scope hash permits only the target post and declared route assets. Completion is approved only after TC-15 live verification and TC-16 rollback evidence also match. Any mismatch resets the release decision to **not approved** and routes work back to the owning task rather than weakening the test.

