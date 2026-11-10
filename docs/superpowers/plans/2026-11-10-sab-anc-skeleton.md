# SAB-ANC Project Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable, data-first SAB-ANC skeleton that makes P0 feature ingestion, feature/order integrity, split auditing, and Gate-0 decisions reproducible before any SASRec or downstream training.

**Architecture:** Create a small `sab_anc` Python package under `baseline/sab_anc/src/`, with immutable data contracts as the shared boundary. A P0 CLI orchestrates only local artifacts: it validates the MMSSL bundle, rebuilds a canonical item index, writes synchronously reordered feature arrays, audits the untouched official splits, then calculates the Gate-0 V–T retrieval ratio. Training modules consume these artifacts later but are intentionally out of scope.

**Tech Stack:** Python 3.13, NumPy, scikit-learn (Ridge + KFold), pytest, JSON/YAML, existing MMSSL `.npy` and grouped split files.

**Spec:** `docs/Hi-SAM原型验证方案_v6.md`, `docs/sab_anc_design.md`, `docs/sab_anc_params.md`, `docs/sab_anc_q30_register.md`

## Global Constraints

- Use MMSSL Amazon-Baby only; do not replace its per-user chronological `train.txt` / `valid.txt` / `test.txt` splits.
- Inputs are visual/textual arrays plus a future behavioral array; their first dimension must equal the canonical item count.
- Canonical item order is ascending numeric item ID; every modality uses exactly that order.
- Feature rows, split hashes, and artifact hashes must be persisted before training is allowed.
- Split audit uses train-only frequency; valid/test never contribute to frozen statistics.
- Gate-0 runs before SASRec: V–T R@10 must be at least `3 ×` shuffled-pair baseline; V–B and T–B are informational only.
- Gate-0 failure returns a stopped status and must not trigger training.
- All data, logs, configs, and generated arrays remain on D: through this worktree; source features are never committed.

## Review Focus

- A test-only item at the maximum numeric ID must be included when validating feature row count.
- A split whose rows differ only by CRLF/LF must have identical semantic hashes, while changed item order must not.
- Missing modality rows or a duplicate canonical item ID must halt before any `.npy` output is committed.
- Gate-0 must use held-out folds and shuffled pairing, not training-set retrieval or a constant random baseline.
- A V–T result strictly below `3 ×` must return `failed_stop`, while exactly `3 ×` is a warning/pass boundary by the documented rule.

---

## File Structure

```text
baseline/sab_anc/
├── README.md
├── .gitignore
├── configs/sab_anc_baby.yaml
├── src/sab_anc/
│   ├── __init__.py
│   ├── contracts.py          # Immutable bundle, index, audit, gate result types
│   ├── bundle.py             # Feature/split discovery and validation
│   ├── index.py              # Canonical IDs and synchronous .npy reordering
│   ├── split_audit.py        # Split/negative audit and frozen train statistics
│   ├── gate0.py              # 5-fold Ridge R@10 alignability test
│   └── p0.py                 # CLI orchestration and status transitions
└── tests/
    ├── conftest.py
    ├── test_bundle.py
    ├── test_index.py
    ├── test_split_audit.py
    ├── test_gate0.py
    └── test_p0_cli.py
```

### Task 1: Contracts and feature-bundle validation

**Files:**
- Create: `baseline/sab_anc/src/sab_anc/contracts.py`
- Create: `baseline/sab_anc/src/sab_anc/bundle.py`
- Create: `baseline/sab_anc/src/sab_anc/__init__.py`
- Test: `baseline/sab_anc/tests/test_bundle.py`

**Interfaces:**
- Produces `FeatureBundle`, `ValidationError`, and `load_bundle(root: Path) -> FeatureBundle`.
- `FeatureBundle` exposes `item_count`, `modalities`, `split_paths`, `feature_paths`, and raw shapes.

- [ ] **Step 1: Write failing validation tests**

```python
def test_load_bundle_requires_rows_for_all_items_seen_across_three_splits(): ...
def test_load_bundle_rejects_missing_text_features(): ...
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest baseline/sab_anc/tests/test_bundle.py -q`

- [ ] **Step 3: Implement the immutable contract and loader**

`load_bundle` reads the grouped official split files, computes `max_item_id + 1` over all three, memory-maps arrays, and rejects non-rank-2/mismatched arrays.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest baseline/sab_anc/tests/test_bundle.py -q`

### Task 2: Canonical index and atomic feature reordering

**Files:**
- Create: `baseline/sab_anc/src/sab_anc/index.py`
- Test: `baseline/sab_anc/tests/test_index.py`

**Interfaces:**
- Consumes `FeatureBundle`.
- Produces `build_canonical_index(bundle: FeatureBundle, output: Path) -> IndexManifest` and `reorder_modalities(bundle, index, output) -> ReorderManifest`.

- [ ] **Step 1: Write failing tests for one shared permutation across image/text**

```python
def test_reorder_modalities_applies_one_canonical_permutation_to_every_modality(): ...
def test_reorder_modalities_leaves_no_outputs_after_validation_failure(): ...
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest baseline/sab_anc/tests/test_index.py -q`

- [ ] **Step 3: Implement index persistence and staging-directory promotion**

Write `item_index.json`, `.npy` outputs, shapes, and SHA-256 digests only after validating every selected modality. Preserve the original feature files unchanged.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest baseline/sab_anc/tests/test_index.py -q`

### Task 3: Official-split and train-only statistics audit

**Files:**
- Create: `baseline/sab_anc/src/sab_anc/split_audit.py`
- Test: `baseline/sab_anc/tests/test_split_audit.py`

**Interfaces:**
- Consumes `FeatureBundle`, `IndexManifest`.
- Produces `audit_splits(bundle, index, output: Path) -> SplitAudit` and `freeze_train_statistics(train_path, output: Path) -> AuxStats`.

- [ ] **Step 1: Write failing tests for positive and negative audits**

```python
def test_audit_persists_semantic_split_hashes_without_repartitioning(): ...
def test_audit_marks_identical_train_and_full_frequency_tables_for_manual_review(): ...
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest baseline/sab_anc/tests/test_split_audit.py -q`

- [ ] **Step 3: Implement audit JSON and frozen train-only table**

Compute raw/semantic `split_hash`, train-only item frequency, full-data comparison, `status` (`passed` or `warn_review_required`), and a blank `review_note`/signature field. Do not write a new split.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest baseline/sab_anc/tests/test_split_audit.py -q`

### Task 4: Gate-0 held-out cross-modal alignability

**Files:**
- Create: `baseline/sab_anc/src/sab_anc/gate0.py`
- Test: `baseline/sab_anc/tests/test_gate0.py`

**Interfaces:**
- Consumes reordered visual/textual arrays and optional behavioral array.
- Produces `run_gate0(features: Mapping[str, Path], output: Path, folds: int = 5, k: int = 10) -> Gate0Result`.

- [ ] **Step 1: Write failing gate tests**

```python
def test_gate0_reports_held_out_vt_ratio_against_shuffled_pairing(): ...
def test_gate0_returns_failed_stop_when_vt_ratio_is_below_three(): ...
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest baseline/sab_anc/tests/test_gate0.py -q`

- [ ] **Step 3: Implement deterministic KFold Ridge retrieval**

Fit source-to-target Ridge only on each fold's training rows, calculate held-out R@10 by cosine ranking, repeat against deterministic shuffled pairs, and emit V–T/V–B/T–B measurements. Gate only V–T at `3.0`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest baseline/sab_anc/tests/test_gate0.py -q`

### Task 5: P0 CLI, configuration, and operator documentation

**Files:**
- Create: `baseline/sab_anc/src/sab_anc/p0.py`
- Create: `baseline/sab_anc/configs/sab_anc_baby.yaml`
- Create: `baseline/sab_anc/README.md`
- Create: `baseline/sab_anc/.gitignore`
- Test: `baseline/sab_anc/tests/test_p0_cli.py`

**Interfaces:**
- Consumes Task 1–4 APIs.
- Produces `python -m sab_anc.p0 --data-root ... --output-root ...` with a single `p0_status.json` and non-zero exit on Gate-0 stop.

- [ ] **Step 1: Write the failing CLI state-transition test**

```python
def test_p0_cli_stops_before_training_when_gate0_fails(tmp_path): ...
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest baseline/sab_anc/tests/test_p0_cli.py -q`

- [ ] **Step 3: Implement CLI and checked-in operator assets**

The CLI performs only P0: bundle validation → canonical reorder → split audit → Gate-0. The README documents the Drive manifest boundary, artifact tree, gate semantics, and the required manual review on `warn_review_required`.

- [ ] **Step 4: Run focused and full tests**

Run: `python -m pytest baseline/sab_anc/tests -q`

- [ ] **Step 5: Commit the skeleton**

```bash
git add baseline/sab_anc baseline/LightGCNpp/code/fetch_mm_data.py baseline/LightGCNpp/code/test_fetch_mm_data.py docs/superpowers/plans/2026-11-10-sab-anc-skeleton.md
git commit -m "feat: scaffold SAB-ANC P0 data pipeline"
```

## Self-Review

- Spec coverage: P0 steps 1–6 map to Tasks 1–5; SASRec/baseline/model training remain intentionally downstream of Gate-0.
- Type consistency: each later task consumes the contract or manifest emitted by its predecessor.
- Review focus: all five high-risk conditions have a named test in Tasks 1–4.
- Proportion: the plan fixes names, interfaces, thresholds, and validation ownership without prescribing implementation bodies.
