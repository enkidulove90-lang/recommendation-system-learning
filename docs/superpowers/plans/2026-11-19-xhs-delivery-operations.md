# XHS Delivery Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the XHS draft delivery path single-sourced, verifiable, idempotent, and operable on the `experiments` mainline without ever publishing a note.

**Architecture:** Preserve `OpenCliXiaohongshuDelivery` as the only platform writer, but move OpenCLI response normalization and structured errors into reusable infrastructure. Persist every attempted delivery in a registry keyed by slug/content hash, then let CLI preflight, save-draft, and verify operate against the same staged payload and record.

**Tech Stack:** Python 3.11, pytest, YAML, JSONL, OpenCLI Browser Bridge, Git cherry-pick.

**Spec:** `docs/xhs_delivery_ops_dev_merged_2026-11-19.md`

## Global Constraints

- `experiments` is the only integration mainline; never merge all of `phase1`.
- Delivery implementation conflicts always keep the `experiments` side.
- All XHS writes remain draft-only; `--save-draft` must state this explicitly.
- PDF, body, real topic entities, and images must be validated as one saved draft.
- Evidence belongs under `data/workflow_state/<slug>/acceptance/`; no root stdout logs.
- S0 must contain only the five 11-19 repair files; S1–S3 are independently committed and traceable.

## Review Focus

- An OpenCLI 2.x `{ok,data}` envelope must normalize identically for list, eval, and doctor responses (Task 2 tests).
- A stale or outdated extension must fail preflight before any browser command (Task 5 tests).
- A verify mismatch must remove only the just-created draft and record an orphan, never an older draft (Task 3 tests).
- Repeating a verified slug must return the same draft ID without increasing platform draft count (Task 4 tests).
- Migration must be idempotent for both legacy 32-hex and already-migrated 64-hex queue directories (Task 5 tests).

---

### Task 1: Freeze S0 and port the safe phase1 documentation

**Files:**
- Modify: Git history on `experiments`
- Add: `redbook/docs/design/08-unified-content-operations-roadmap.md`
- Add: `redbook/docs/design/09-real-platform-adapters.md`

**Interfaces:**
- Produces: S0 repair commit and S1 cherry-pick commit, both with 40-hex IDs.
- Consumed by: all later tasks and final acceptance evidence.

- [x] **Step 1:** Run the S0 delivery/unit suite before staging.
- [x] **Step 2:** Commit only the five S0 delivery files.
- [x] **Step 3:** Cherry-pick `phase1:fe336cb` as S1 and retain `experiments` as mainline.

### Task 2: Establish platform facts, structured errors, and the OpenCLI client

**Files:**
- Create: `redbook/infrastructure/delivery_errors.py`
- Modify: `redbook/infrastructure/opencli_runtime.py`
- Modify: `redbook/infrastructure/xiaohongshu_delivery.py`
- Modify: `redbook/scripts/xhs_drafts.py`
- Modify: `redbook/docs/xhs-content-spec.md`
- Modify: `config/xhs_content_rules.yaml`
- Create: `redbook/docs/session-audit-template.md`
- Test: `redbook/tests/test_opencli_runtime.py`
- Test: `redbook/tests/test_xiaohongshu_delivery.py`

**Interfaces:**
- Produces: `DeliveryFailure(code, message, details)` and `OpenCliClient.run_json()/doctor()`.
- Consumes: current `OpenCliRuntime`, `OpenCliXiaohongshuDelivery`, OpenCLI 1.x/2.x JSON envelopes.

- [x] **Step 1: Write failing tests** for `{ok,data}` unwrapping, doctor version parsing, and a topic-unavailable structured error.
- [x] **Step 2: Verify RED** with `python -m pytest redbook/tests/test_opencli_runtime.py redbook/tests/test_xiaohongshu_delivery.py -q`.
- [x] **Step 3: Implement** seven stable codes: `E_PREFLIGHT_BLOCKED`, `E_OPENCLI_UNAVAILABLE`, `E_RESPONSE_SHAPE`, `E_TOPIC_UNAVAILABLE`, `E_SAVE_UNVERIFIED`, `E_VERIFY_MISMATCH`, `E_REGISTRY_CONFLICT`; expose `OpenCliClient` as the sole JSON/doctor adapter.
- [x] **Step 4: Replace** duplicate parsing in delivery and draft inventory with `OpenCliClient` while preserving the S0 real-chip state machine.
- [x] **Step 5: Freeze PF-1..PF-4** and toolchain compatibility/orphan policy in docs/config, then run the focused suite.
- [x] **Step 6: Commit** `feat(xhs): centralize platform facts and OpenCLI errors`.

### Task 3: Add `--save-draft` and read-only verification

**Files:**
- Modify: `redbook/cli.py`
- Modify: `redbook/application/paper_workflow.py`
- Modify: `redbook/infrastructure/xiaohongshu_delivery.py`
- Test: `redbook/tests/test_cli_xhs_delivery.py`
- Test: `redbook/tests/test_note_spec.py`

**Interfaces:**
- Produces: `note <slug> --save-draft` (alias of legacy `--publish`) and `note <slug> --verify --draft-id <id>`.
- Consumes: `verify_saved_draft(draft_id, payload) -> dict` and a staged package.

- [x] **Step 1: Write failing CLI tests** for help copy, alias equivalence, JSON `status="passed"`, and nonzero verify failure.
- [x] **Step 2: Verify RED** with the new CLI test module.
- [x] **Step 3: Implement** alias parsing without changing `--publish` compatibility; verify must compare staged body/topics/PDF with one draft ID and update checkpoint only on passed verification.
- [x] **Step 4: Run** CLI and note-spec tests; archive exit code and JSON result in the acceptance directory.
- [x] **Step 5: Commit** `feat(xhs): add save-draft and verify commands`.

### Task 4: Registry, reconciliation, and idempotency

**Files:**
- Create: `redbook/infrastructure/delivery_registry.py`
- Modify: `redbook/automation/publishing.py`
- Modify: `redbook/application/paper_workflow.py`
- Modify: `redbook/infrastructure/run_log.py`
- Test: `redbook/tests/test_delivery_registry.py`
- Test: `redbook/tests/test_xiaohongshu_delivery.py`

**Interfaces:**
- Produces: `DeliveryRegistry.start()`, `.record_verified()`, `.record_orphan()`, `.find_verified(slug, staged_id)`.
- Consumes: slug, staged ID, run ID, draft ID, verify JSON, evidence paths.

- [x] **Step 1: Write failing tests** for registry round-trip, mismatch/orphan state, and `test_delivery_idempotent_rerun` returning the same draft ID without invoking a second save.
- [x] **Step 2: Verify RED** with registry/delivery tests.
- [x] **Step 3: Implement** an atomic JSON registry under `data/workflow_state/<slug>/delivery_registry.json`; use a lock-safe write/replace and record JSONL phase events.
- [x] **Step 4: Gate publish/save** on an existing `verify_passed` `(slug, staged_id)` record; otherwise create one run, verify, and persist evidence paths.
- [x] **Step 5: Run** TC-04/TC-05 focused tests and commit `feat(xhs): reconcile draft delivery idempotently`.

### Task 5: Preflight, queue migration, and S2/S3 capability port

**Files:**
- Modify: `redbook/cli.py`
- Modify: `redbook/infrastructure/opencli_runtime.py`
- Create: `redbook/scripts/migrate_staged_packages.py`
- Modify: `redbook/automation/publishing.py`
- Add selectively from phase1 `8a615c4`: `redbook/automation/daily_discovery.py`, `daily_runner.py`, `one_click.py`, `platform_adapters.py`, `sources.py`
- Test: `redbook/tests/test_opencli_runtime.py`
- Test: `redbook/tests/test_migrate_staged_packages.py`
- Test: `redbook/tests/test_platform_adapters.py`

**Interfaces:**
- Produces: preflight result with error code; idempotent 32→64 hex migration CLI.
- Consumes: toolchain config and registry/staged package metadata.

- [x] **Step 1: Write failing tests** for an outdated extension blocking before browser invocation, and repeatable directory migration.
- [x] **Step 2: Verify RED** on preflight/migration tests.
- [x] **Step 3: Implement** preflight from parsed `opencli doctor` data and make all XHS write entries invoke it before `browser open`.
- [x] **Step 4: Implement** migration dry-run/apply behavior; update stage/publish readers to prefer the full 64-hex directory and support legacy reads only during migration.
- [x] **Step 5: Port S2 only as needed:** retain the already-present explicit `--skip-pdf-attachment` payload contract; do not import phase1 native-input delivery code.
- [x] **Step 6: Port S3 selectively:** add new automation files; reject phase1 changes to delivery/public automation files when they conflict with experiments.
- [x] **Step 7: Run** targeted adapter suite and commit separate S2/S3 commits with conflict resolution notes.

### Task 6: Remove obsolete native-input path and perform acceptance

**Files:**
- Modify: `.agents/skills/xhs-paper-draft/SKILL.md`
- Modify: `redbook/docs/xhs-content-spec.md`
- Modify: delivery tests/docs as required
- Create: `data/workflow_state/2611.17921/acceptance/*`

**Interfaces:**
- Produces: S4 decision record; TC-01..TC-12 evidence manifest.

- [x] **Step 1: Write a regression test** proving XHS topic binding makes no native `browser type` call.
- [x] **Step 2: Verify RED** by temporarily exercising the obsolete path through a test double.
- [x] **Step 3: Remove/deprecate** phase1 `.mjs` native-input imports from all active paths; document `--save-draft` as draft-only.
- [x] **Step 4: Run** the full `python -m pytest redbook/tests -q` suite and each safe TC; use mocks for TC-02/TC-10 to avoid creating platform drafts unless a separately approved canary is supplied.
- [x] **Step 5: Archive** pytest tail, exit codes, JSONL excerpts, verify JSON, registry excerpt, hashes, and only an already-available screenshot to `acceptance/`; do not fabricate a screenshot or run a public post.
- [x] **Step 6: Commit** docs/tests and record S0–S4 40-hex hashes.
