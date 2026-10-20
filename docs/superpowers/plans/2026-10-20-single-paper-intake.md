# Single Paper Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a localhost management page that accepts one paper URL or PDF, resumes a checkpointed MinerU/DeepSeek pipeline, creates a Notion draft, requires approval, and then triggers the existing GitHub Pages deployment.

**Architecture:** The processing repository owns a small FastAPI control plane, a SQLite job ledger, deterministic artifact manifests, and adapters around the existing MinerU and DeepSeek code. Notion remains the publication source of truth; the website repository continues to read only `Published` posts. Every external step is idempotent and independently retryable, while local PDFs and parser output remain ignored runtime assets.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, SQLite, Pydantic, httpx, existing MinerU/DeepSeek skills, Notion REST API, GitHub Actions workflow dispatch, unittest.

---

## File structure

- Create `paper_intake/models.py`: job/step enums and API/domain models.
- Create `paper_intake/repository.py`: SQLite schema, transactions, checkpoints, and event log.
- Create `paper_intake/inputs.py`: URL/PDF validation, canonical IDs, hashes, and duplicate keys.
- Create `paper_intake/article.py`: DeepSeek article schema, classification normalization, rendering, and quality gate.
- Create `paper_intake/adapters.py`: MinerU, DeepSeek, Notion, and GitHub interfaces plus production adapters.
- Create `paper_intake/pipeline.py`: resumable single-job orchestration.
- Create `paper_intake/service.py`: application service and one-at-a-time background worker.
- Create `paper_intake/web.py`: FastAPI endpoints and localhost application factory.
- Create `paper_intake/templates/index.html`: upload, progress, retry, approve, and publication UI.
- Create `paper_intake/static/app.js`: polling and button actions.
- Create `paper_intake/static/style.css`: compact management-page styling.
- Create `paper_intake/__main__.py`: `python -m paper_intake serve` entry point.
- Create `tests/test_intake_*.py`: unit and integration tests with fake external adapters.
- Modify `requirements.txt`: add FastAPI/Uvicorn/multipart dependencies.
- Modify `.env.example`: document Notion/GitHub/site variables without secrets.
- Modify `.gitignore`: ignore inbox, SQLite, task bundles, and generated intake state.
- Modify `README.md`: startup, recovery, and approval instructions.
- Modify website `tools/notion_sync.py`: preserve the explicit `Published` filter and add test coverage that drafts never render.

### Task 1: Persistent job and checkpoint ledger

**Files:**
- Create: `paper_intake/__init__.py`
- Create: `paper_intake/models.py`
- Create: `paper_intake/repository.py`
- Test: `tests/test_intake_repository.py`

- [ ] **Step 1: Write failing repository tests**

Cover creation, step transitions, event persistence, restart recovery (`running` to `interrupted`), and one job retaining its `notion_page_id` and publication URL.

```python
def test_running_step_becomes_interrupted_after_restart(tmp_path):
    repo = JobRepository(tmp_path / "jobs.sqlite3")
    job = repo.create_job(source_type="url", source_url="https://arxiv.org/pdf/2608.17316")
    repo.start_step(job.job_id, StepName.MINERU_PARSE)
    repo.close()

    reopened = JobRepository(tmp_path / "jobs.sqlite3")
    reopened.recover_interrupted_jobs()

    assert reopened.get_step(job.job_id, StepName.MINERU_PARSE).status == StepStatus.INTERRUPTED
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_repository -v`

Expected: FAIL because `paper_intake.repository` does not exist.

- [ ] **Step 3: Implement the SQLite schema and typed models**

Create `jobs`, `job_steps`, and `job_events` tables. Use transactions for every state change and a unique constraint on `(job_id, step_name)`.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_repository -v`

Expected: all repository tests pass.

- [ ] **Step 5: Commit**

```powershell
git add paper_intake tests/test_intake_repository.py
git commit -m "feat(intake): add persistent paper job ledger"
```

### Task 2: Safe URL/PDF intake and duplicate identity

**Files:**
- Create: `paper_intake/inputs.py`
- Test: `tests/test_intake_inputs.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write failing input tests**

Test arXiv abs/PDF normalization, generic PDF URLs, `%PDF-` validation, maximum size, SHA-256 generation, upload filename sanitization, and duplicate lookup by canonical ID/hash/URL.

```python
def test_arxiv_abs_and_pdf_urls_share_canonical_identity():
    assert canonicalize_url("https://arxiv.org/abs/2608.17316").canonical_id == "2608.17316"
    assert canonicalize_url("https://arxiv.org/pdf/2608.17316.pdf").canonical_id == "2608.17316"
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_inputs -v`

Expected: FAIL because intake helpers are missing.

- [ ] **Step 3: Implement validation and artifact storage**

Store inputs under `data/inbox/{job_id}/source.pdf`, stream downloads with a byte limit, reject non-PDF content, and register all three duplicate keys before paid API calls.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_inputs -v`

Expected: all input tests pass.

- [ ] **Step 5: Commit**

```powershell
git add .gitignore paper_intake/inputs.py tests/test_intake_inputs.py
git commit -m "feat(intake): validate and deduplicate paper inputs"
```

### Task 3: Structured article contract and quality gate

**Files:**
- Create: `paper_intake/article.py`
- Test: `tests/test_intake_article.py`

- [ ] **Step 1: Write failing schema and rendering tests**

Require introduction, method, experiments, conclusion, references, controlled categories, paper URL, and at least one existing figure with a non-empty Chinese explanation. Verify Markdown contains stable front matter and no one-line/English-only figure caption.

```python
def test_article_without_renderable_figure_is_blocked(tmp_path):
    article = valid_article(figures=[])
    result = validate_article(article, artifact_root=tmp_path)
    assert result.publishable is False
    assert "figure_required" in result.issue_codes
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_article -v`

Expected: FAIL because the article contract is missing.

- [ ] **Step 3: Implement Pydantic schema, controlled classification, renderer, and gates**

Keep the generated JSON as the canonical artifact and produce Markdown deterministically. Unknown model categories fall back to `推荐系统 / 论文速递` and are recorded as review warnings.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_article -v`

Expected: all article tests pass.

- [ ] **Step 5: Commit**

```powershell
git add paper_intake/article.py tests/test_intake_article.py
git commit -m "feat(intake): define publishable paper article contract"
```

### Task 4: External adapters with retry-safe boundaries

**Files:**
- Create: `paper_intake/adapters.py`
- Test: `tests/test_intake_adapters.py`
- Modify: `.env.example`

- [ ] **Step 1: Write failing adapter tests**

Use fake transports to verify MinerU calls the existing parser with a local PDF, DeepSeek returns schema-valid JSON, Notion upserts by arXiv ID, Notion writes `Draft`, approval writes `Published`, and GitHub dispatch never logs its token.

```python
def test_notion_upsert_defaults_new_article_to_draft():
    transport = FakeNotionTransport()
    gateway = NotionGateway("token", "database", transport=transport)
    page = gateway.upsert_draft(valid_manifest())
    assert transport.last_properties["status"]["select"]["name"] == "Draft"
    assert page.page_id
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_adapters -v`

Expected: FAIL because adapter interfaces do not exist.

- [ ] **Step 3: Implement dependency-injected adapters**

Wrap existing `PDFParser`; use the configured OpenAI-compatible DeepSeek client; implement Notion idempotent lookup/update and image upload; implement GitHub `workflow_dispatch` with optional token and a scheduled-build fallback.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_adapters -v`

Expected: all adapter tests pass without network access.

- [ ] **Step 5: Commit**

```powershell
git add .env.example paper_intake/adapters.py tests/test_intake_adapters.py
git commit -m "feat(intake): add MinerU DeepSeek Notion and GitHub adapters"
```

### Task 5: Resumable orchestration

**Files:**
- Create: `paper_intake/pipeline.py`
- Test: `tests/test_intake_pipeline.py`

- [ ] **Step 1: Write failing orchestration tests**

Verify the exact step order, stop-on-failure behavior, retry from the failed step, no repeated MinerU call after DeepSeek failure, blocked quality state, Notion draft creation, and no GitHub call before approval.

```python
def test_retry_after_deepseek_failure_does_not_repeat_mineru(harness):
    harness.deepseek.fail_once = True
    harness.pipeline.run(harness.job_id)
    harness.pipeline.retry(harness.job_id)
    assert harness.mineru.calls == 1
    assert harness.deepseek.calls == 2
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_pipeline -v`

Expected: FAIL because the orchestrator is missing.

- [ ] **Step 3: Implement checkpoint-aware orchestration**

Successful steps are skipped when their input hash and output manifest still match. Transient failures receive bounded retries; validation/auth failures stop immediately; cancellation is checked between steps.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_pipeline -v`

Expected: all pipeline tests pass.

- [ ] **Step 5: Commit**

```powershell
git add paper_intake/pipeline.py tests/test_intake_pipeline.py
git commit -m "feat(intake): orchestrate resumable single paper processing"
```

### Task 6: Approval, deployment, and recovery operations

**Files:**
- Create: `paper_intake/service.py`
- Test: `tests/test_intake_service.py`

- [ ] **Step 1: Write failing service tests**

Test one active job at a time, approval forbidden before quality success, remote Notion snapshot saved before overwrite, approval changing Notion to `Published`, deployment-only retry, cancellation without artifact deletion, and publication verification.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_service -v`

Expected: FAIL because the application service is missing.

- [ ] **Step 3: Implement worker and recovery commands**

The service owns one background worker thread, startup interruption recovery, `retry`, `approve`, `cancel`, `restore_notion`, and `retry_deployment` operations.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_service -v`

Expected: all service tests pass.

- [ ] **Step 5: Commit**

```powershell
git add paper_intake/service.py tests/test_intake_service.py
git commit -m "feat(intake): add approval and recovery service"
```

### Task 7: Local management page and API

**Files:**
- Create: `paper_intake/web.py`
- Create: `paper_intake/templates/index.html`
- Create: `paper_intake/static/app.js`
- Create: `paper_intake/static/style.css`
- Create: `paper_intake/__main__.py`
- Test: `tests/test_intake_web.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Write failing API tests**

Test URL submission, multipart PDF upload, list/detail polling, duplicate response, retry, cancel, approval, blocked approval, upload size error, and sanitized JSON errors.

```python
def test_upload_returns_job_without_exposing_local_secrets(client):
    response = client.post(
        "/api/jobs/upload",
        files={"file": ("paper.pdf", b"%PDF-1.7\nbody", "application/pdf")},
    )
    assert response.status_code == 202
    assert "token" not in response.text.lower()
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_web -v`

Expected: FAIL because the web app is missing.

- [ ] **Step 3: Implement the localhost UI and endpoints**

Bind to `127.0.0.1` by default, poll job status every two seconds, show per-step progress and safe errors, and only render approval when the quality gate succeeds.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_intake_web -v`

Expected: all web tests pass.

- [ ] **Step 5: Commit**

```powershell
git add requirements.txt paper_intake tests/test_intake_web.py
git commit -m "feat(intake): add localhost paper management page"
```

### Task 8: Website draft isolation

**Files:**
- Modify in website repository: `tests/test_notion_map_fields.py` or create `tests/test_notion_sync_status.py`
- Modify in website repository only if required: `tools/notion_sync.py`

- [ ] **Step 1: Write a failing website test**

Prove that the Notion query includes `status=Published` and `type=Post`, and that `Draft`, `Review`, `Rejected`, or `Invisible` records cannot generate Markdown.

- [ ] **Step 2: Verify RED or confirm existing behavior**

Run: `python -m unittest tests/test_notion_sync_status.py -v`

Expected: FAIL until the status-query behavior is exposed for testing. If production behavior already matches, the new test must still first fail because the testable query builder is absent.

- [ ] **Step 3: Extract a pure query builder without changing behavior**

Return the existing `Published` + `Post` filter from a function used by `main()`.

- [ ] **Step 4: Verify GREEN and full website build**

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
npm test
npm run build
```

Expected: Python and Node suites pass and Hexo generates the site.

- [ ] **Step 5: Commit in the website repository**

```powershell
git add tools/notion_sync.py tests/test_notion_sync_status.py
git commit -m "test(notion): enforce published-only website sync"
```

### Task 9: End-to-end fake pipeline and operator documentation

**Files:**
- Create: `tests/test_intake_end_to_end.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing end-to-end test**

Use a real temporary SQLite database and filesystem with fake external transports. Submit one PDF, run through Notion Draft, approve, dispatch, verify publication, restart the service, and verify all state remains readable.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_intake_end_to_end -v`

Expected: FAIL until all integration wiring is complete.

- [ ] **Step 3: Wire the production factory and document operation**

Document installation, `python -m paper_intake serve --host 127.0.0.1 --port 8765`, environment variables, status meanings, retry behavior, Notion restoration, deployment-only retry, and the rule that local artifacts are never auto-deleted.

- [ ] **Step 4: Run full verification**

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m unittest redbook.tests.test_automation redbook.tests.test_xiaohongshu_delivery redbook.tests.test_platform_adapters
python -m paper_intake --help
git diff --check
```

Expected: all tests pass, help exits 0, and diff check reports no errors.

- [ ] **Step 5: Commit**

```powershell
git add README.md tests/test_intake_end_to_end.py
git commit -m "docs(intake): document single paper publication workflow"
```

### Task 10: One-paper controlled live validation

**Files:**
- Runtime only under ignored `data/inbox/`, `data/workflow_state/`, `data/parsed/`, and `data/summaries/`

- [ ] **Step 1: Confirm credentials without printing them**

Check presence only for `MINERU_API_KEY`, `DEEPSEEK_API_KEY`, `NOTION_TOKEN`, and `NOTION_DATABASE_ID`. Treat `GITHUB_TOKEN` as optional because the scheduled website build remains a fallback.

- [ ] **Step 2: Start the server and submit one user-selected unpublished paper**

Do not reuse an existing online paper because duplicate protection must remain enabled.

- [ ] **Step 3: Verify each persisted checkpoint and Notion Draft**

Compare PDF hash, MinerU Markdown, selected images, article JSON, rendered Markdown, Notion read-back, and task event log.

- [ ] **Step 4: Stop before publication for human review**

The user reviews the Notion Draft or localhost preview and explicitly approves it.

- [ ] **Step 5: Approve, deploy, and verify the public URL**

Confirm Notion is `Published`, GitHub Actions succeeds (or scheduled build completes), the public article returns HTTP 200, and all local site images render.

- [ ] **Step 6: Preserve the audit record**

Keep the ignored task manifest and hashes. Do not delete the PDF or MinerU output during this implementation.
