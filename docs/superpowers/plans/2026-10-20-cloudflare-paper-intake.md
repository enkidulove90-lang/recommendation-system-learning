# Cloudflare Paper Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Embed an owner-authenticated paper upload modal and collapsible task drawer in the existing GitHub Pages site, backed by a Cloudflare intake API and a resumable local Python worker that publishes validated articles through Notion.

**Architecture:** GitHub Pages is a static client. A TypeScript Cloudflare Worker provides GitHub/Access session exchange, D1 job state, R2 artifacts, worker leases, and GitHub dispatch. The existing Python `paper_intake` pipeline becomes a polling worker and writes Notion pages directly as `Published`; the website syncs them through the existing GitHub Actions workflow.

**Tech Stack:** Cloudflare Workers, D1, R2, TypeScript, Vitest, Python 3.12, `httpx`, existing MinerU/DeepSeek/Notion adapters, Hexo 7, Butterfly, browser JavaScript, CSS, GitHub Actions.

---

## File map

### Main repository: `D:\recommendation-system-learning`

- Create `paper_intake/cloudflare/package.json` — isolated Worker toolchain and test scripts.
- Create `paper_intake/cloudflare/tsconfig.json` — Worker and test type-checking.
- Create `paper_intake/cloudflare/vitest.config.ts` — Cloudflare Workers test pool.
- Create `paper_intake/cloudflare/wrangler.jsonc` — Worker bindings and non-secret configuration.
- Create `paper_intake/cloudflare/migrations/0001_initial.sql` — D1 paper/job/artifact/publication/session schema.
- Create `paper_intake/cloudflare/src/types.ts` — API, environment, and persistence types.
- Create `paper_intake/cloudflare/src/security.ts` — origin checks, one-time codes, HMAC sessions, machine authentication.
- Create `paper_intake/cloudflare/src/repository.ts` — D1 deduplication, leases, checkpoints, and completion transactions.
- Create `paper_intake/cloudflare/src/index.ts` — routing, R2 streaming, Worker API, GitHub dispatch, callback endpoint.
- Create `paper_intake/cloudflare/test/*.test.ts` — gateway contract tests with fake D1/R2 helpers.
- Create `paper_intake/remote.py` — typed remote gateway client.
- Create `paper_intake/remote_worker.py` — claim/heartbeat/checkpoint/run loop.
- Modify `paper_intake/models.py` — direct-publish step and public status mapping.
- Modify `paper_intake/adapters.py` — Notion upsert with `Published` status.
- Modify `paper_intake/pipeline.py` — direct publish after quality gate.
- Modify `paper_intake/__main__.py` — `remote-worker` command.
- Create `tests/test_remote_client.py` and `tests/test_remote_worker.py`.
- Modify `tests/test_intake_pipeline.py`, `tests/test_intake_service.py`, and `tests/test_intake_end_to_end.py`.

### Website repository

Repository root: `C:\Users\lkshpc\.codex\visualizations\2026\10\16\01a144bb-b59f-7333-994d-b25e734ecd1b\homepage-filter-fix`

- Create `scripts/paper_intake_config.js` — emit `/paper-intake-config.json` from a public build variable.
- Create `source/js/paper-intake.js` — login popup, upload modal, polling, retry, and drawer controller.
- Create `source/css/paper-intake.css` — modal and hover/click drawer behavior.
- Modify `_config.butterfly.yml` — inject the two assets.
- Modify `.github/workflows/publish.yml` — callback after successful deployment.
- Create `tests/paper-intake-ui.test.js` — DOM behavior and public-config tests.

## Task 1: Establish the Cloudflare API contract and durable schema

**Files:**
- Create: `paper_intake/cloudflare/package.json`
- Create: `paper_intake/cloudflare/wrangler.jsonc`
- Create: `paper_intake/cloudflare/migrations/0001_initial.sql`
- Create: `paper_intake/cloudflare/src/types.ts`
- Create: `paper_intake/cloudflare/src/repository.ts`
- Test: `paper_intake/cloudflare/test/repository.test.ts`

- [x] **Step 1: Add the isolated Worker test toolchain**

```json
{
  "name": "paper-intake-gateway",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "types": "wrangler types src/worker-configuration.d.ts",
    "typecheck": "npm run types && tsc --noEmit",
    "dev": "wrangler dev --local"
  },
  "devDependencies": {
    "@cloudflare/vitest-plugin": "^1.0.0",
    "typescript": "^5.9.0",
    "vitest": "^4.1.0",
    "wrangler": "^4.0.0"
  }
}
```

```json
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "paper-intake-gateway",
  "main": "src/index.ts",
  "compatibility_date": "2026-10-20",
  "vars": {
    "ALLOWED_ORIGINS": "https://enkidulove90-lang.github.io,http://127.0.0.1:4322",
    "GITHUB_REPOSITORY": "enkidulove90-lang/enkidulove90-lang.github.io"
  },
  "d1_databases": [
    { "binding": "DB", "database_name": "paper-intake", "database_id": "local-paper-intake" }
  ],
  "r2_buckets": [
    { "binding": "ARTIFACTS", "bucket_name": "paper-intake-artifacts" }
  ]
}
```

`local-paper-intake` is the intentional local-development D1 identifier. Task 8 replaces it with the real identifier returned by `wrangler d1 create` before remote deployment.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "types": ["@cloudflare/vitest-plugin/types"]
  },
  "include": ["src/**/*.ts", "test/**/*.ts", "vitest.config.ts", "src/worker-configuration.d.ts"]
}
```

```ts
import { cloudflareTest } from "@cloudflare/vitest-plugin";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [cloudflareTest({ wrangler: { configPath: "./wrangler.jsonc" } })]
});
```

Run: `cd paper_intake/cloudflare; npm install`  
Expected: lockfile created with no runtime dependency outside the Worker package.

- [x] **Step 2: Write the failing repository tests**

```ts
type SeededJob = { jobId: string };
let now = new Date("2026-10-20T00:00:00Z");
let repo: IntakeRepository;

beforeEach(() => {
  repo = new IntakeRepository(testDb(), () => now);
});

async function seedQueuedJob(repo: IntakeRepository): Promise<SeededJob> {
  const paper = await repo.createOrReusePaper({ doi: "10.1/lease", pdfSha256: "lease-hash" });
  return repo.createJob({ paperId: paper.paperId, inputType: "pdf", inputRef: "originals/lease.pdf" });
}

it("deduplicates by DOI before PDF hash", async () => {
  const first = await repo.createOrReusePaper({ doi: "10.1/example", pdfSha256: "a" });
  const second = await repo.createOrReusePaper({ doi: "10.1/example", pdfSha256: "b" });
  expect(second.paperId).toBe(first.paperId);
  expect(second.reused).toBe(true);
});

it("only leases one queued job and reclaims expired leases", async () => {
  const job = await seedQueuedJob(repo);
  expect((await repo.claim("worker-a", 600)).jobId).toBe(job.jobId);
  expect(await repo.claim("worker-b", 600)).toBeNull();
  now = new Date(now.getTime() + 601_000);
  expect((await repo.claim("worker-b", 600)).jobId).toBe(job.jobId);
});
```

Run: `npm test -- repository.test.ts`  
Expected: FAIL because the schema and repository do not exist.

- [x] **Step 3: Add the D1 schema**

```sql
CREATE TABLE papers (
  paper_id TEXT PRIMARY KEY,
  doi TEXT UNIQUE,
  arxiv_id TEXT UNIQUE,
  canonical_url TEXT NOT NULL DEFAULT '',
  normalized_title TEXT NOT NULL DEFAULT '',
  title_fingerprint TEXT NOT NULL DEFAULT '',
  pdf_sha256 TEXT UNIQUE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE jobs (
  job_id TEXT PRIMARY KEY,
  paper_id TEXT NOT NULL REFERENCES papers(paper_id),
  input_type TEXT NOT NULL CHECK(input_type IN ('url','pdf')),
  input_ref TEXT NOT NULL,
  stage TEXT NOT NULL DEFAULT 'received',
  status TEXT NOT NULL DEFAULT 'queued',
  attempt INTEGER NOT NULL DEFAULT 0,
  lease_owner TEXT,
  lease_until TEXT,
  error_code TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE artifacts (
  artifact_id TEXT PRIMARY KEY,
  paper_id TEXT NOT NULL REFERENCES papers(paper_id),
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  kind TEXT NOT NULL,
  r2_key TEXT NOT NULL UNIQUE,
  sha256 TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  content_type TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE publications (
  paper_id TEXT PRIMARY KEY REFERENCES papers(paper_id),
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  notion_page_id TEXT NOT NULL,
  slug TEXT NOT NULL,
  site_url TEXT NOT NULL,
  git_commit TEXT NOT NULL DEFAULT '',
  publish_status TEXT NOT NULL,
  published_at TEXT
);

CREATE TABLE login_codes (
  code_hash TEXT PRIMARY KEY,
  owner_identity TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  consumed_at TEXT
);

CREATE INDEX jobs_claim_idx ON jobs(status, lease_until, created_at);
CREATE INDEX papers_title_fingerprint_idx ON papers(title_fingerprint);
```

- [x] **Step 4: Implement atomic deduplication and leasing**

```ts
export interface JobDbRow {
  job_id: string;
  paper_id: string;
  input_type: "url" | "pdf";
  input_ref: string;
  stage: string;
  status: "queued" | "processing" | "publishing" | "published" | "failed" | "cancelled";
  attempt: number;
  lease_owner: string | null;
  lease_until: string | null;
}

export interface JobRecord {
  jobId: string;
  paperId: string;
  inputType: "url" | "pdf";
  inputRef: string;
  stage: string;
  status: "queued" | "processing" | "publishing" | "published" | "failed" | "cancelled";
  attempt: number;
  leaseOwner: string | null;
  leaseUntil: string | null;
}

function rowToJob(row: JobDbRow): JobRecord {
  return {
    jobId: row.job_id, paperId: row.paper_id, inputType: row.input_type,
    inputRef: row.input_ref, stage: row.stage, status: row.status,
    attempt: row.attempt, leaseOwner: row.lease_owner, leaseUntil: row.lease_until
  };
}

export class IntakeRepository {
  constructor(private readonly db: D1Database, private readonly now = () => new Date()) {}

  async claim(workerId: string, leaseSeconds: number): Promise<JobRecord | null> {
    const until = new Date(this.now().getTime() + leaseSeconds * 1000).toISOString();
    const row = await this.db.prepare(`
      UPDATE jobs SET status='processing', lease_owner=?1, lease_until=?2,
        attempt=attempt+1, updated_at=?3
      WHERE job_id=(
        SELECT job_id FROM jobs
        WHERE status='queued' OR (status='processing' AND lease_until < ?3)
        ORDER BY created_at LIMIT 1
      )
      RETURNING *
    `).bind(workerId, until, this.now().toISOString()).first<JobDbRow>();
    return row ? rowToJob(row) : null;
  }
}
```

Implement `createOrReusePaper`, `createJob`, `heartbeat`, `checkpoint`, `complete`, `fail`, `listOwnerJobs`, and `retry` using bound statements and transactions.

- [x] **Step 5: Run repository tests and commit**

Run: `npm test -- repository.test.ts; npm run typecheck`  
Expected: all repository tests pass and TypeScript reports zero errors.

```bash
git add paper_intake/cloudflare
git commit -m "feat(intake): add durable cloudflare job ledger"
```

## Task 2: Add owner login, strict CORS, and URL/PDF intake

**Files:**
- Create: `paper_intake/cloudflare/src/security.ts`
- Modify: `paper_intake/cloudflare/src/index.ts`
- Test: `paper_intake/cloudflare/test/security.test.ts`
- Test: `paper_intake/cloudflare/test/intake.test.ts`

- [x] **Step 1: Write failing security and intake tests**

```ts
it("accepts only configured GitHub Pages and local origins", () => {
  expect(assertOrigin("https://enkidulove90-lang.github.io", env)).toBeTruthy();
  expect(assertOrigin("http://127.0.0.1:4322", env)).toBeTruthy();
  expect(() => assertOrigin("https://attacker.example", env)).toThrow("origin_denied");
});

it("rejects non-PDF bodies before writing R2", async () => {
  const response = await request("/v1/intake/pdf", {
    method: "POST",
    headers: { "content-type": "application/pdf" },
    body: new TextEncoder().encode("not a pdf")
  });
  expect(response.status).toBe(415);
  expect(await r2.list()).toHaveLength(0);
});

it("returns an existing identity for a duplicate DOI", async () => {
  const first = await submitUrl("https://doi.org/10.1287/mnsc.2024.04540");
  const second = await submitUrl("https://doi.org/10.1287/mnsc.2024.04540");
  expect(second.paper_id).toBe(first.paper_id);
  expect(second.code).toBe("duplicate_paper");
});
```

Run: `npm test -- security.test.ts intake.test.ts`  
Expected: FAIL because the router and security functions are absent.

- [x] **Step 2: Implement short-lived sessions and one-time login codes**

```ts
export async function signSession(identity: string, key: string, now: number): Promise<string> {
  const payload = base64url(JSON.stringify({ sub: identity, exp: now + 1800 }));
  const signature = await hmac(payload, key);
  return `${payload}.${signature}`;
}

export async function requireOwner(request: Request, env: Env): Promise<Owner> {
  const token = request.headers.get("authorization")?.replace(/^Bearer\s+/i, "");
  const claims = token && await verifySession(token, env.SESSION_SIGNING_KEY);
  if (!claims || !env.OWNER_IDENTITIES.split(",").includes(claims.sub)) {
    throw new ApiError(401, "auth_required", "请使用已授权的 GitHub 账号登录。", false);
  }
  return { identity: claims.sub };
}
```

`/v1/session/start` reads the Access-authenticated identity, creates a two-minute single-use code, and returns a tiny `postMessage` page. `/v1/session/exchange` consumes the code and returns a 30-minute bearer session.

- [x] **Step 3: Implement URL and PDF ingestion**

```ts
async function ingestPdf(request: Request, env: Env, owner: Owner): Promise<Response> {
  const length = Number(request.headers.get("content-length") || 0);
  if (length <= 0 || length > 50 * 1024 * 1024) {
    throw new ApiError(413, "pdf_too_large", "PDF 必须小于 50 MB。", false);
  }
  const bytes = new Uint8Array(await request.arrayBuffer());
  if (new TextDecoder().decode(bytes.slice(0, 5)) !== "%PDF-") {
    throw new ApiError(415, "invalid_pdf", "上传内容不是有效 PDF。", false);
  }
  const sha256 = await digestHex(bytes);
  const result = await repository(env).createPdfJob({ sha256, owner: owner.identity });
  if (!result.reused) await env.ARTIFACTS.put(result.inputRef, bytes, {
    httpMetadata: { contentType: "application/pdf" }
  });
  return jsonEnvelope(result.reused ? 200 : 202, result);
}
```

URL ingestion accepts only `https`, normalizes DOI/arXiv links, rejects private/local hosts, and creates an R2 input only after the local worker legally downloads the paper.

- [x] **Step 4: Add exact CORS and safe envelopes**

All successful and failed responses use `{ok, request_id, paper_id, job_id, status, code, message, retryable}`. Preflight responses echo only a matched origin and allow `authorization, content-type`.

```ts
function corsHeaders(origin: string, env: Env): Headers {
  assertOrigin(origin, env);
  return new Headers({
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "authorization,content-type",
    "access-control-max-age": "600",
    vary: "Origin"
  });
}
```

- [x] **Step 5: Run tests and commit**

Run: `npm test -- security.test.ts intake.test.ts; npm run typecheck`  
Expected: all tests pass; no response snapshot contains a secret, stack, R2 key, or local path.

```bash
git add paper_intake/cloudflare
git commit -m "feat(intake): secure owner URL and PDF submissions"
```

## Task 3: Add remote-worker leases, artifacts, publication dispatch, and callback

**Files:**
- Modify: `paper_intake/cloudflare/src/index.ts`
- Modify: `paper_intake/cloudflare/src/repository.ts`
- Test: `paper_intake/cloudflare/test/worker-api.test.ts`
- Test: `paper_intake/cloudflare/test/publication.test.ts`

- [x] **Step 1: Write failing worker contract tests**

```ts
it("requires the machine token and renews only the current lease", async () => {
  expect((await claim({ authorization: "Bearer wrong" })).status).toBe(401);
  const claimed = await claim(machineHeaders);
  expect((await heartbeat(claimed.job_id, "other-worker")).status).toBe(409);
  expect((await heartbeat(claimed.job_id, claimed.lease_owner)).status).toBe(200);
});

it("dispatches once and completes only after the Pages callback", async () => {
  await completeJob(jobId, notionPublication);
  expect(github.calls).toHaveLength(1);
  expect((await repo.getJob(jobId)).status).toBe("publishing");
  await pagesCallback(jobId, "abc123");
  expect((await repo.getJob(jobId)).status).toBe("published");
});
```

Run: `npm test -- worker-api.test.ts publication.test.ts`  
Expected: FAIL because worker and callback routes do not exist.

- [x] **Step 2: Implement machine-authenticated claim and heartbeat**

```ts
function requireMachine(request: Request, env: Env): void {
  const provided = request.headers.get("authorization") || "";
  if (!timingSafeEqual(provided, `Bearer ${env.WORKER_TOKEN}`)) {
    throw new ApiError(401, "worker_auth_required", "Worker authentication failed.", false);
  }
}
```

Claim returns the job plus a short-lived artifact download URL. Heartbeat and checkpoint require matching `lease_owner`; a stale worker receives HTTP 409 and must stop processing.

- [x] **Step 3: Implement artifact upload and completion**

Artifact upload verifies lease ownership, kind, declared SHA-256, actual SHA-256, MIME and size. Completion transaction records the Notion Page ID, slug, public URL and final artifact references before changing the job to `publishing`.

```ts
async function completeClaimedJob(request: Request, env: Env, jobId: string): Promise<Response> {
  requireMachine(request, env);
  const payload = await request.json<CompletionPayload>();
  const job = await repository(env).complete(jobId, payload.leaseOwner, payload.publication);
  await dispatchPublication(env, job);
  return jsonEnvelope(200, { job_id: job.jobId, paper_id: job.paperId, status: "publishing" });
}
```

- [x] **Step 4: Dispatch and accept the Pages callback**

```ts
await fetch(`https://api.github.com/repos/${env.GITHUB_REPOSITORY}/dispatches`, {
  method: "POST",
  headers: {
    authorization: `Bearer ${env.GITHUB_TOKEN}`,
    accept: "application/vnd.github+json",
    "content-type": "application/json",
    "x-github-api-version": "2022-11-28"
  },
  body: JSON.stringify({
    event_type: "notion-updated",
    client_payload: { job_id: job.jobId, paper_id: job.paperId }
  })
});
```

`POST /v1/publications/callback` requires `PUBLISH_CALLBACK_TOKEN`. Success stores the commit and marks `published`; failure stores `deploy_failed` and remains retryable in the completed UI group.

- [x] **Step 5: Run tests and commit**

Run: `npm test; npm run typecheck`  
Expected: all gateway tests pass.

```bash
git add paper_intake/cloudflare
git commit -m "feat(intake): add leased workers and publication callback"
```

## Task 4: Convert the Python pipeline to direct Published output

**Files:**
- Modify: `paper_intake/models.py`
- Modify: `paper_intake/adapters.py`
- Modify: `paper_intake/pipeline.py`
- Modify: `paper_intake/service.py`
- Modify: `tests/test_intake_pipeline.py`
- Modify: `tests/test_intake_service.py`
- Modify: `tests/test_intake_end_to_end.py`

- [x] **Step 1: Replace review expectations with direct-publish failing tests**

```python
PDF_BYTES = b"%PDF-1.7\nvalidated test document"

def test_successful_pipeline_writes_published_notion_page(self):
    job = self.service.submit_upload("paper.pdf", PDF_BYTES)
    self.assertTrue(self.service.run_pending_once())
    completed = self.repository.get_job(job.job_id)
    self.assertEqual(self.notion.status, "Published")
    self.assertEqual(completed.status, JobStatus.PUBLISHING)

def test_quality_failure_never_writes_notion(self):
    self.quality.publishable = False
    job = self.service.submit_upload("paper.pdf", PDF_BYTES)
    self.service.run_pending_once()
    self.assertEqual(self.repository.get_job(job.job_id).status, JobStatus.FAILED)
    self.assertEqual(self.notion.calls, [])
```

Run: `python -m unittest tests.test_intake_pipeline tests.test_intake_service tests.test_intake_end_to_end`  
Expected: FAIL because the pipeline still stops at `AWAITING_REVIEW`.

- [x] **Step 2: Replace the draft step with a published-page step**

```python
class StepName(StrEnum):
    # existing processing steps remain unchanged
    WRITE_NOTION_PUBLISHED = "write_notion_published"
    TRIGGER_PAGES = "trigger_pages"
    VERIFY_PUBLICATION = "verify_publication"
```

Change `NotionGateway.upsert_draft` into `upsert_published`, setting Notion properties `status=Published` and `type=Post` in the create/update request.

- [x] **Step 3: Make the service auto-publish only after quality success**

```python
result = self.pipeline.run(job.job_id)
if result.status is JobStatus.FAILED:
    return result
return self.repository.update_job(
    job.job_id,
    status=JobStatus.PUBLISHING,
)
```

The local service does not call GitHub in this path. The remote worker reports the Notion result to Cloudflare, and Task 3's gateway performs the single repository dispatch. Keep `approve()` temporarily as a compatibility method that returns an already publishing/published job and rejects every other state; remove its HTTP button and review wording.

- [x] **Step 4: Run the focused and regression tests**

Run: `python -m unittest tests.test_intake_pipeline tests.test_intake_service tests.test_intake_end_to_end`  
Expected: direct-publish tests pass.

Run: `python -m unittest discover -s tests -p "test_*.py"`  
Expected: all existing intake and unrelated tests pass.

- [x] **Step 5: Commit**

```bash
git add paper_intake tests
git commit -m "feat(intake): publish validated papers without review wait"
```

## Task 5: Add the remote gateway client and polling local worker

**Files:**
- Create: `paper_intake/remote.py`
- Create: `paper_intake/remote_worker.py`
- Modify: `paper_intake/__main__.py`
- Test: `tests/test_remote_client.py`
- Test: `tests/test_remote_worker.py`

- [x] **Step 1: Write failing remote client and recovery tests**

```python
class FakeGateway:
    def __init__(self, *, heartbeat_result=True, checkpoints=None):
        self.heartbeat_result = heartbeat_result
        self.checkpoints = checkpoints or {}
        self.completed = []
        self.failed = []

    def claim(self, _worker_id="test-worker"):
        return type("Claim", (), {"job_id": "job-1", "checkpoints": self.checkpoints})()

    def heartbeat(self, _job_id, _worker_id):
        return self.heartbeat_result

def test_worker_stops_when_heartbeat_loses_lease(self):
    gateway = FakeGateway(heartbeat_result=False)
    runner = RemoteWorker(gateway=gateway, processor=self.processor, poll_seconds=0)
    with self.assertRaises(LeaseLost):
        runner.run_claimed(gateway.claim())

def test_retry_reuses_parsed_checkpoint(self):
    gateway = FakeGateway(checkpoints={"parsed": self.parsed_artifact})
    runner = RemoteWorker(gateway=gateway, processor=self.processor, poll_seconds=0)
    runner.run_once()
    self.assertEqual(self.processor.mineru_calls, 0)
    self.assertEqual(self.processor.deepseek_calls, 1)
```

Run: `python -m unittest tests.test_remote_client tests.test_remote_worker`  
Expected: FAIL because the client and worker are absent.

- [x] **Step 2: Implement the typed gateway client**

```python
class RemoteJob(BaseModel):
    job_id: str
    paper_id: str
    input_type: Literal["url", "pdf"]
    input_ref: str
    stage: str
    checkpoints: dict[str, dict] = Field(default_factory=dict)
    lease_owner: str
    lease_until: datetime

class RemoteGatewayClient:
    def __init__(self, base_url: str, token: str, *, client: httpx.Client | None = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=120,
        )

    def claim(self, worker_id: str) -> RemoteJob | None:
        response = self.client.post("/v1/worker/jobs/claim", json={"worker_id": worker_id})
        if response.status_code == 204:
            return None
        response.raise_for_status()
        return RemoteJob.model_validate(response.json()["job"])
```

Implement heartbeat, download, checkpoint, artifact upload, complete and fail with bounded retries only for network errors and HTTP 429/5xx.

- [x] **Step 3: Implement the local polling loop with a heartbeat thread**

```python
def run_once(self) -> bool:
    job = self.gateway.claim(self.worker_id)
    if job is None:
        return False
    with self.heartbeat(job.job_id):
        try:
            result = self.processor.process(job, self.gateway)
            self.gateway.complete(job.job_id, result)
        except LeaseLost:
            raise
        except Exception as exc:
            self.gateway.fail(job.job_id, error_from_exception(exc))
    return True
```

The processor mirrors the remote `job_id` into the local SQLite repository, downloads artifacts into `data/paper_intake/remote/<job_id>/`, and skips stages represented by verified remote checkpoints.

- [x] **Step 4: Add the CLI entry**

```python
def remote_worker_command() -> int:
    client = RemoteGatewayClient(
        os.environ["PAPER_INTAKE_API_BASE"],
        os.environ["PAPER_INTAKE_WORKER_TOKEN"],
    )
    build_remote_worker(client).run_forever()
    return 0
```

Command: `python -m paper_intake remote-worker`  
Missing variables must produce a concise configuration error without printing values.

- [x] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_remote_client tests.test_remote_worker`  
Expected: all remote tests pass.

Run: `python -m unittest discover -s tests -p "test_*.py"`  
Expected: full Python suite passes.

```bash
git add paper_intake tests
git commit -m "feat(intake): add resumable local cloud worker"
```

## Task 6: Embed the upload modal and collapsible task drawer in Hexo

**Files:**
- Create: `scripts/paper_intake_config.js`
- Create: `source/js/paper-intake.js`
- Create: `source/css/paper-intake.css`
- Modify: `_config.butterfly.yml`
- Modify: `package.json`
- Test: `tests/paper-intake-ui.test.js`

- [ ] **Step 1: Add jsdom and write failing UI tests**

Run: `npm install --save-dev jsdom`  
Expected: `package.json` and `package-lock.json` record jsdom only as a development dependency.

```js
const { JSDOM } = require('jsdom');
const { mountPaperIntake } = require('../source/js/paper-intake.js');

let dom;
beforeEach(() => {
  dom = new JSDOM('<!doctype html><body><nav id="sidebar-menus"></nav></body>', {
    url: 'http://127.0.0.1:4322/'
  });
});

const fakeApi = {
  exchange: async () => ({ token: 'session-token' }),
  listJobs: async () => [],
  retry: async () => ({ ok: true })
};

test("drawer stays closed until hover or click", async () => {
  const app = mountPaperIntake(dom.window.document, fakeApi);
  assert.equal(app.drawer.dataset.state, "closed");
  app.tab.dispatchEvent(new dom.window.MouseEvent("mouseenter"));
  assert.equal(app.drawer.dataset.state, "peek");
  app.tab.click();
  assert.equal(app.drawer.dataset.state, "locked");
});

test("failed jobs appear under completed with retry", () => {
  const app = mountPaperIntake(dom.window.document, fakeApi);
  app.renderJobs([{ status: "failed", error_message: "PDF 下载失败", retryable: true }]);
  assert.match(app.completed.textContent, /未发布/);
  assert.ok(app.completed.querySelector("[data-action=retry]"));
});
```

Run: `npm test -- paper-intake-ui.test.js`  
Expected: FAIL because the component is absent.

- [ ] **Step 2: Emit a public runtime config**

```js
hexo.extend.generator.register('paper-intake-config', function () {
  return {
    path: 'paper-intake-config.json',
    data: JSON.stringify({
      apiBase: process.env.PAPER_INTAKE_API_BASE || 'http://127.0.0.1:8787'
    })
  };
});
```

Only the API URL is emitted. Tests assert that token-like environment variables cannot appear in the JSON.

- [ ] **Step 3: Implement the modal and owner login flow**

`paper-intake.js` injects one button into both desktop and mobile Butterfly menus, mounts one modal, opens the Access login popup, validates `postMessage.origin`, exchanges the one-time code, and keeps the bearer only in `sessionStorage`.

```js
window.addEventListener('message', async (event) => {
  if (event.origin !== apiOrigin || event.data?.type !== 'paper-intake-code') return;
  session = await api.exchange(event.data.code);
  sessionStorage.setItem('paper-intake-session', session.token);
  openModal();
});

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { mountPaperIntake, mapJobGroup };
}
```

- [ ] **Step 4: Implement drawer states and two UI groups**

```css
.paper-task-drawer { transform: translateX(calc(100% - 42px)); transition: transform .24s ease; }
.paper-task-drawer[data-state="peek"],
.paper-task-drawer[data-state="locked"] { transform: translateX(0); }
@media (hover: none) { .paper-task-drawer[data-state="peek"] { transform: translateX(calc(100% - 42px)); } }
```

Mouse entry opens `peek`; leaving the combined tab/drawer hot zone starts a short close timer. Click sets `locked`; close and outside-click restore `closed`. Status mapping is `published/failed/cancelled → completed`, all others → processing.

- [ ] **Step 5: Inject, test, build, and commit in the website repository**

Add to `_config.butterfly.yml`:

```yaml
inject:
  head:
    - <link rel="stylesheet" href="/css/paper-intake.css">
  bottom:
    - <script defer src="/js/paper-intake.js"></script>
```

Run: `npm test; npm run test:python; npm run build`  
Expected: Node and Python suites pass; Hexo generates the homepage and `paper-intake-config.json`.

```bash
git add _config.butterfly.yml package.json package-lock.json scripts source tests
git commit -m "feat(site): embed owner paper upload workflow"
```

## Task 7: Connect GitHub Actions publication callbacks

**Files:**
- Modify: website `.github/workflows/publish.yml`
- Test: website `tests/publish-workflow.test.js`
- Modify: `paper_intake/cloudflare/test/publication.test.ts`

- [ ] **Step 1: Write a failing workflow contract test**

```js
test('publish workflow reports repository-dispatch completion', () => {
  const yaml = fs.readFileSync('.github/workflows/publish.yml', 'utf8');
  assert.match(yaml, /PAPER_INTAKE_CALLBACK_URL/);
  assert.match(yaml, /PAPER_INTAKE_CALLBACK_TOKEN/);
  assert.match(yaml, /github\.event\.client_payload\.job_id/);
});
```

Run: `node --test tests/publish-workflow.test.js`  
Expected: FAIL because callback variables are absent.

- [ ] **Step 2: Add the post-deploy callback**

```yaml
      - name: Report paper intake deployment
        if: ${{ success() && github.event_name == 'repository_dispatch' && github.event.client_payload.job_id != '' }}
        env:
          CALLBACK_URL: ${{ secrets.PAPER_INTAKE_CALLBACK_URL }}
          CALLBACK_TOKEN: ${{ secrets.PAPER_INTAKE_CALLBACK_TOKEN }}
          JOB_ID: ${{ github.event.client_payload.job_id }}
        run: |
          curl --fail --retry 3 --request POST "$CALLBACK_URL/v1/publications/callback" \
            --header "Authorization: Bearer $CALLBACK_TOKEN" \
            --header "Content-Type: application/json" \
            --data "{\"job_id\":\"$JOB_ID\",\"git_commit\":\"${GITHUB_SHA}\"}"
```

- [ ] **Step 3: Verify callback idempotency**

Extend the Worker test so two identical callbacks both return 200 and create only one publication event.

```ts
const first = await pagesCallback(jobId, "abc123");
const second = await pagesCallback(jobId, "abc123");
expect(first.status).toBe(200);
expect(second.status).toBe(200);
expect(await repo.countEvents(jobId, "publication.completed")).toBe(1);
```

- [ ] **Step 4: Run both repository test suites**

Website: `npm test; npm run test:python; npm run build`  
Gateway: `cd D:\recommendation-system-learning\paper_intake\cloudflare; npm test; npm run typecheck`  
Expected: all pass.

- [ ] **Step 5: Commit website and gateway changes separately**

```bash
git add .github/workflows/publish.yml tests/publish-workflow.test.js
git commit -m "feat(site): report completed paper deployments"
```

```bash
git add paper_intake/cloudflare/test/publication.test.ts
git commit -m "test(intake): lock publication callback idempotency"
```

## Task 8: Provision safely and perform one-paper end-to-end verification

**Files:**
- Create: `docs/paper-intake-operations.md`
- Modify: `.gitignore`
- Modify after successful verification: `paper_intake/web.py`
- Delete after successful verification: `paper_intake/templates/index.html`
- Delete after successful verification: `paper_intake/static/app.js`
- Delete after successful verification: `paper_intake/static/style.css`
- Modify: `tests/test_intake_web.py`

- [ ] **Step 1: Protect all local and Cloudflare artifacts**

Add exact ignore rules:

```gitignore
.dev.vars
.wrangler/
data/paper_intake/
data/workflow_state/paper_intake/
*.sqlite3
```

Run: `git check-ignore -v paper_intake/cloudflare/.dev.vars data/paper_intake/jobs.sqlite3`  
Expected: both paths are ignored.

- [ ] **Step 2: Create Cloudflare resources and secrets**

Run from `paper_intake/cloudflare`:

```powershell
npx wrangler login
npx wrangler d1 create paper-intake
npx wrangler r2 bucket create paper-intake-artifacts
npx wrangler secret put SESSION_SIGNING_KEY
npx wrangler secret put WORKER_TOKEN
npx wrangler secret put GITHUB_TOKEN
npx wrangler secret put PUBLISH_CALLBACK_TOKEN
npx wrangler d1 migrations apply paper-intake --remote
npx wrangler deploy
```

Use the D1 identifier returned by `wrangler d1 create` in `wrangler.jsonc`. Configure Access only for `/v1/session/start*` with GitHub identity and the owner allow policy. Configure Worker variables with the exact production and local origins; do not store secret values in Git.

- [ ] **Step 3: Configure website and local worker secrets**

GitHub repository secrets:

- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`
- `PAPER_INTAKE_API_BASE`
- `PAPER_INTAKE_CALLBACK_URL`
- `PAPER_INTAKE_CALLBACK_TOKEN`

Local `.env` adds `PAPER_INTAKE_API_BASE` and `PAPER_INTAKE_WORKER_TOKEN`. Before using Notion, rotate the token previously exposed in chat and update local/GitHub values.

- [ ] **Step 4: Run the single-PDF acceptance scenario**

1. Start the site at `127.0.0.1:4322`.
2. Submit a legally available PDF from the embedded modal.
3. Start `python -m paper_intake remote-worker`.
4. Stop the process after MinerU checkpoint, restart it, and verify MinerU is not repeated.
5. Confirm Notion contains one `Published + Post` page with images and references.
6. Confirm repository dispatch builds the website and the callback moves the task into completed.
7. Re-upload the same PDF and confirm the existing `paper_id` is returned.
8. Confirm no PDF, image cache, `.dev.vars`, SQLite database, or token appears in `git status`.

- [ ] **Step 5: Remove the standalone 8765 UI only after acceptance passes**

Keep `create_app()` only if API-level regression tests still require it; remove the `/` HTML route, static mounts, review/approve UI endpoints and template/static files. Change the web test to assert `/` returns 404 while safe JSON endpoints remain testable.

Run: `python -m unittest discover -s tests -p "test_*.py"`  
Expected: full Python suite passes without the standalone control desk.

- [ ] **Step 6: Write operations documentation and final commits**

Document startup, token rotation, retry, lease recovery, Cloudflare deployment, GitHub secret names, rollback, and how to disable the injected website component.

```bash
git add .gitignore docs/paper-intake-operations.md paper_intake tests
git commit -m "docs(intake): document operations and retire local control desk"
```

Website final verification:

```bash
npm test
npm run test:python
npm run build
```

Main repository final verification:

```bash
python -m unittest discover -s tests -p "test_*.py"
cd paper_intake/cloudflare
npm test
npm run typecheck
```

Expected: every command passes and both worktrees contain only intentional source changes.
