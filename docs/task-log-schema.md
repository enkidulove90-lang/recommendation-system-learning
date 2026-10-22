# Paper task diagnostic log (schema v2)

The owner-only `GET /v1/jobs/{job_id}/log` export is a diagnostic record, not a raw process log.
It contains `trace_id`, sanitized paper identity, a deterministic `diagnosis`, `stage_metrics`, and the ordered event ledger.

## Failure events

`job.stage_failed` is the canonical processing failure event. Its details contain the stage, stable error code,
category, server-controlled retry decision, HTTP/provider identifiers when available, attempt, duration, safe
message, action hint, fingerprint, and a local log reference. It must never contain credentials, request headers,
raw model responses, URL query values, or a traceback.

Other terminal/control events are `publication.failed`, `publication.dispatch_failed`, `job.retry_scheduled`,
`job.retry_exhausted`, and `job.lease_lost`.

## Retry policy

Retry decisions are made by the gateway error policy, not by `status == failed` and not solely by the worker.
Transient network/provider errors may retry. Validation, configuration, authentication, and internal code errors
require correction. Three failed attempts produce `job.retry_exhausted` and disable further automatic retry.

## Trace propagation

One `tr_<uuid>` is created with the job and is included in gateway events, claimed worker jobs, Worker-to-gateway
requests, MinerU and DeepSeek requests, Notion/GitHub HTTP requests, repository dispatch payloads, the Actions
environment, and the publication callback.

## Verification

Run:

```text
python -m pytest tests -q
cd paper_intake/cloudflare && npm test && npm run typecheck
cd .worktrees/site-ui-fixes && npm test && npm run build
```

The export sanitization test injects credential-shaped text and URL query secrets and proves none survive in the
JSON response. Do not replace that test with a snapshot containing real secrets.
