# Sentinel release and catalog handoff

## Observed dependency chain

The former scheduled action called `scripts/run_sentinel_task.ps1` in an
isolated worktree. That script derived its application root from `PSScriptRoot`;
`redbook.cli sentinel` used a relative `data` directory and a bundled YAML file.
The YAML named a machine-specific Hexo exclusion path. The discovery adapter
then read `daily_draft.yaml`, wrote JSONL under `data/discovery`, and used the
same root for the SQLite pool, queue, and logs. Removing the worktree would
therefore remove executable code and could strand the state. The old scheduled
task is disabled. The alternate untracked `redbook/sentinel/schedule.py` is
not an approved registration entry point until it enforces the same boundary.

## Installed layout

Use `scripts/install_sentinel_release.ps1` with explicit absolute
`InstallBase`, `DataRoot`, and `ExclusionsSource`. It archives a committed Git
SHA to an immutable `InstallBase/releases/<sha>` directory and copies the
exclusion snapshot to `DataRoot/exclusions.json`. The installed code contains
the same Python modules and YAML configuration as the tested commit. Keep
SQLite, discovery JSONL, logs, and credential environment outside the release.
The installer rejects paths inside worktrees. It does not register or enable a
task.

`scripts/register_sentinel_task.ps1` requires `InstallRoot`, `DataRoot`,
`ConfigPath`, and `ExclusionsPath` for a real registration. The task action
points to the installed release's runner and passes the state/config/exclusion
paths explicitly. Preview mode remains available in the source checkout.
Do not re-enable the disabled legacy task until the installed release has
passed `run_sentinel_task.ps1 -NoDispatch -WhatIf` and one real discovery-only
run with read-back of the SQLite and log paths. A new release requires a new
registration pointing to its immutable path; retain the previous release for
rollback. Re-registering must not overwrite the persistent state directory.

## Catalog and delivery boundary

The catalog snapshot is read-only input to `CatalogGovernance`. Topic matches
are computed from the saved title and topic signals, with the term, field,
value, and topic source stored in `catalog_admissions.evidence_json`.
Xiaohongshu additionally requires the result of the official GitHub verifier:
paper names repository, repository is reachable, and its text matches title
and author. An unverified document identity cannot be admitted.
`redbook.orchestration.catalog_admission.admit_candidate` is the adapter from
the normalized `PaperRecord`: it checks title and canonical landing URL against
the verified catalog row, fetches the paper and repository through the existing
official GitHub verifier, and stores the result, evidence URLs, source label,
and check time in `catalog_admissions.evidence_json`. A missing fetcher,
missing record, unreachable repository, or mismatch leaves XHS deferred.

The catalog writes only `PaperEligible` events. `CatalogOutboxRelay` consumes
those events in outbox-ID order and creates a single platform job, idempotency
marker, pool projection, and consumed receipt in one SQLite transaction.
It never invokes MinerU, a model, or a publication adapter. Homepage events
declare `publish`; Xiaohongshu and WeChat declare `save_draft`. Malformed
events go to the outbox dead-letter field; transient failures increment
attempts and defer visibility, with a bounded retry count. A relay event does
not grant another platform admission.

The legacy daily discovery/pool dispatch path remains available while this
new path is validated. Do not run both dispatchers for the same canonical
paper: a legacy pool conflict fails closed and requires reconciliation.
The new relay has an explicit opt-in command:
`python -m redbook.cli catalog-relay --database <DataRoot>/state/orchestration.sqlite`.
It does not run automatically with the legacy Sentinel command; enable its
schedule only after a catalog admission producer uses the same persistent DB
and the platform consumers' draft-only behavior has been verified.

## Regression gates

1. Import the full snapshot twice: all records present, second import adds
   zero, no delivery event is produced by import alone.
2. BONSAI's RecSys session URL and old snapshot without authors remain
   unresolved. Official arXiv metadata must match title and author.
3. Topic mismatch defers all platforms. Xiaohongshu code evidence missing or
   incomplete defers only Xiaohongshu; homepage and WeChat may proceed.
4. Duplicate relay delivery creates one job per admitted platform. A crash
   after job insertion rolls back the whole transaction; retry succeeds.
5. Malformed event goes to dead letter; retry exhaustion records attempts.
6. Registration preview points only to installed code and external state;
   missing exclusions fail closed. A source-worktree registration is rejected.
7. Run the full redbook and catalog test suites, inspect the installed task
   action, and verify a discovery-only run before enabling any scheduler.

The standalone source code is not proof of a live deployment. The scheduler
remains disabled until the installed release and its runtime state are checked.
