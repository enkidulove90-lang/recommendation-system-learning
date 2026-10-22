import type {
  ArtifactInput,
  ArtifactRecord,
  CreateJobInput,
  FailureDescriptor,
  JobRecord,
  PaperIdentity,
  PaperRecord,
  PaperResolution,
  PublicationInput,
} from "./types";

interface PaperRow {
  paper_id: string;
  doi: string | null;
  arxiv_id: string | null;
  canonical_url: string;
  normalized_title: string;
  title_fingerprint: string;
  pdf_sha256: string | null;
  created_at: string;
  updated_at: string;
}

interface JobRow {
  job_id: string;
  paper_id: string;
  owner_identity: string;
  input_type: "url" | "pdf";
  input_ref: string;
  stage: string;
  status: JobRecord["status"];
  attempt: number;
  lease_owner: string | null;
  lease_until: string | null;
  checkpoint_json: string;
  error_code: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  trace_id: string | null;
}

interface ArtifactRow {
  artifact_id: string;
  paper_id: string;
  job_id: string;
  kind: string;
  r2_key: string;
  sha256: string;
  size_bytes: number;
  content_type: string;
  created_at: string;
}

interface RetryOperationRow {
  idempotency_key: string;
  job_id: string;
  state: "pending" | "completed";
  response_json: string;
  created_at: string;
  updated_at: string;
}

interface MetadataRefreshRow {
  idempotency_key: string;
  job_id: string;
  state: "queued" | "processing" | "completed" | "failed";
  lease_owner: string | null;
  lease_until: string | null;
  result_json: string;
  error_code: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  paper_id?: string;
  arxiv_id?: string | null;
  input_ref?: string;
  notion_page_id?: string;
  slug?: string;
}

export interface MetadataRefreshRecord {
  idempotencyKey: string;
  jobId: string;
  state: MetadataRefreshRow["state"];
  leaseOwner: string | null;
  leaseUntil: string | null;
  result: Record<string, unknown>;
  errorCode: string | null;
  errorMessage: string | null;
  paperId?: string;
  arxivId?: string | null;
  inputRef?: string;
  notionPageId?: string;
  slug?: string;
}

export interface RetryOperationRecord {
  idempotencyKey: string;
  jobId: string;
  state: "pending" | "completed";
  response: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

function optional(value: string | undefined): string | null {
  const normalized = value?.trim();
  return normalized ? normalized : null;
}

function mapPaper(row: PaperRow): PaperRecord {
  return {
    paperId: row.paper_id,
    doi: row.doi,
    arxivId: row.arxiv_id,
    canonicalUrl: row.canonical_url,
    normalizedTitle: row.normalized_title,
    titleFingerprint: row.title_fingerprint,
    pdfSha256: row.pdf_sha256,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function parseCheckpoints(value: string): Record<string, unknown> {
  try {
    const parsed: unknown = JSON.parse(value || "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? (parsed as Record<string, unknown>)
      : {};
  } catch {
    return {};
  }
}

function mapJob(row: JobRow): JobRecord {
  return {
    jobId: row.job_id,
    paperId: row.paper_id,
    ownerIdentity: row.owner_identity,
    inputType: row.input_type,
    inputRef: row.input_ref,
    stage: row.stage,
    status: row.status,
    attempt: row.attempt,
    leaseOwner: row.lease_owner,
    leaseUntil: row.lease_until,
    checkpoints: parseCheckpoints(row.checkpoint_json),
    errorCode: row.error_code,
    errorMessage: row.error_message,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    traceId: row.trace_id || `tr_${row.job_id}`,
  };
}

function mapRetryOperation(row: RetryOperationRow): RetryOperationRecord {
  return {
    idempotencyKey: row.idempotency_key,
    jobId: row.job_id,
    state: row.state,
    response: parseCheckpoints(row.response_json),
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function mapMetadataRefresh(row: MetadataRefreshRow): MetadataRefreshRecord {
  return {
    idempotencyKey: row.idempotency_key,
    jobId: row.job_id,
    state: row.state,
    leaseOwner: row.lease_owner,
    leaseUntil: row.lease_until,
    result: parseCheckpoints(row.result_json),
    errorCode: row.error_code,
    errorMessage: row.error_message,
    paperId: row.paper_id,
    arxivId: row.arxiv_id,
    inputRef: row.input_ref,
    notionPageId: row.notion_page_id,
    slug: row.slug,
  };
}

export class IntakeRepository {
  constructor(
    private readonly db: D1Database,
    private readonly now: () => Date = () => new Date(),
  ) {}

  private timestamp(): string {
    return this.now().toISOString();
  }

  private async findPaper(identity: PaperIdentity): Promise<PaperRow | null> {
    const selectors: Array<[string, string | null]> = [
      ["doi", optional(identity.doi)],
      ["arxiv_id", optional(identity.arxivId)],
      ["pdf_sha256", optional(identity.pdfSha256)],
      ["canonical_url", optional(identity.canonicalUrl)],
      ["title_fingerprint", optional(identity.titleFingerprint)],
    ];
    for (const [column, value] of selectors) {
      if (!value) continue;
      const row = await this.db
        .prepare(`SELECT * FROM papers WHERE ${column} = ? LIMIT 1`)
        .bind(value)
        .first<PaperRow>();
      if (row) return row;
    }
    return null;
  }

  async createOrReusePaper(identity: PaperIdentity): Promise<PaperResolution> {
    const existing = await this.findPaper(identity);
    if (existing) {
      const updatedAt = this.timestamp();
      try {
        await this.db
          .prepare(
            `UPDATE papers SET
              doi = COALESCE(doi, ?), arxiv_id = COALESCE(arxiv_id, ?),
              canonical_url = CASE WHEN canonical_url = '' THEN COALESCE(?, '') ELSE canonical_url END,
              normalized_title = CASE WHEN normalized_title = '' THEN COALESCE(?, '') ELSE normalized_title END,
              title_fingerprint = CASE WHEN title_fingerprint = '' THEN COALESCE(?, '') ELSE title_fingerprint END,
              pdf_sha256 = COALESCE(pdf_sha256, ?), updated_at = ?
             WHERE paper_id = ?`,
          )
          .bind(
            optional(identity.doi),
            optional(identity.arxivId),
            optional(identity.canonicalUrl),
            optional(identity.normalizedTitle),
            optional(identity.titleFingerprint),
            optional(identity.pdfSha256),
            updatedAt,
            existing.paper_id,
          )
          .run();
      } catch (error) {
        throw new Error(`identity_conflict: ${String(error)}`);
      }
      const refreshed = await this.requirePaper(existing.paper_id);
      return { ...refreshed, reused: true };
    }

    const paperId = crypto.randomUUID();
    const timestamp = this.timestamp();
    try {
      await this.db
        .prepare(
          `INSERT INTO papers (
            paper_id, doi, arxiv_id, canonical_url, normalized_title,
            title_fingerprint, pdf_sha256, created_at, updated_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        )
        .bind(
          paperId,
          optional(identity.doi),
          optional(identity.arxivId),
          optional(identity.canonicalUrl) ?? "",
          optional(identity.normalizedTitle) ?? "",
          optional(identity.titleFingerprint) ?? "",
          optional(identity.pdfSha256),
          timestamp,
          timestamp,
        )
        .run();
    } catch (error) {
      const raced = await this.findPaper(identity);
      if (raced) return { ...mapPaper(raced), reused: true };
      throw error;
    }
    return { ...(await this.requirePaper(paperId)), reused: false };
  }

  private async requirePaper(paperId: string): Promise<PaperRecord> {
    const row = await this.db
      .prepare("SELECT * FROM papers WHERE paper_id = ?")
      .bind(paperId)
      .first<PaperRow>();
    if (!row) throw new Error("paper_not_found");
    return mapPaper(row);
  }

  async createJob(input: CreateJobInput): Promise<JobRecord> {
    await this.requirePaper(input.paperId);
    const jobId = crypto.randomUUID();
    const timestamp = this.timestamp();
    const traceId = input.traceId?.trim() || `tr_${crypto.randomUUID()}`;
    try {
      await this.db.batch([
        this.db
          .prepare(
            `INSERT INTO jobs (
              job_id, paper_id, owner_identity, input_type, input_ref,
              stage, status, created_at, updated_at, trace_id
            ) VALUES (?, ?, ?, ?, ?, 'received', 'queued', ?, ?, ?)`,
          )
          .bind(
            jobId,
            input.paperId,
            input.ownerIdentity,
            input.inputType,
            input.inputRef,
            timestamp,
            timestamp,
            traceId,
          ),
        this.db
          .prepare(
            `INSERT INTO job_events (job_id, event_type, details_json, created_at)
             VALUES (?, 'job.created', ?, ?)`,
          )
          .bind(jobId, JSON.stringify({ trace_id: traceId }), timestamp),
      ]);
    } catch (error) {
      const raced = await this.getLatestJobForPaper(input.paperId);
      if (raced) return raced;
      throw error;
    }
    return this.requireJob(jobId);
  }

  async getJob(jobId: string): Promise<JobRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM jobs WHERE job_id = ?")
      .bind(jobId)
      .first<JobRow>();
    return row ? mapJob(row) : null;
  }

  async getPaperIdentity(paperId: string): Promise<Record<string, unknown>> {
    const row = await this.db.prepare(
      `SELECT p.normalized_title, p.arxiv_id, p.doi, p.metadata_source, p.metadata_json,
              u.slug, u.site_url
       FROM papers p LEFT JOIN publications u ON u.paper_id = p.paper_id
       WHERE p.paper_id = ? LIMIT 1`,
    ).bind(paperId).first<{
      normalized_title: string; arxiv_id: string | null; doi: string | null;
      metadata_source: string | null; metadata_json: string | null;
      slug: string | null; site_url: string | null;
    }>();
    if (!row) return {};
    const metadata = parseCheckpoints(row.metadata_json || "{}");
    return {
      title: row.normalized_title || metadata.title || null,
      arxiv_id: row.arxiv_id,
      doi: row.doi,
      slug: row.slug,
      metadata_source: row.metadata_source,
      final_url: row.site_url,
    };
  }

  async getLatestJobForPaper(paperId: string): Promise<JobRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM jobs WHERE paper_id = ? ORDER BY created_at DESC LIMIT 1")
      .bind(paperId)
      .first<JobRow>();
    return row ? mapJob(row) : null;
  }

  async getActiveLease(jobId: string, workerId: string): Promise<JobRecord | null> {
    const job = await this.getJob(jobId);
    if (
      !job ||
      job.status !== "processing" ||
      job.leaseOwner !== workerId ||
      !job.leaseUntil ||
      job.leaseUntil < this.timestamp()
    ) {
      return null;
    }
    return job;
  }

  private async requireJob(jobId: string): Promise<JobRecord> {
    const job = await this.getJob(jobId);
    if (!job) throw new Error("job_not_found");
    return job;
  }

  async claim(workerId: string, leaseSeconds: number): Promise<JobRecord | null> {
    const now = this.timestamp();
    const leaseUntil = new Date(this.now().getTime() + leaseSeconds * 1000).toISOString();
    const row = await this.db
      .prepare(
        `UPDATE jobs SET
          status = 'processing', lease_owner = ?, lease_until = ?,
          attempt = attempt + 1, error_code = NULL, error_message = NULL, updated_at = ?
         WHERE job_id = (
           SELECT job_id FROM jobs
           WHERE status = 'queued'
              OR (status = 'processing' AND lease_until IS NOT NULL AND lease_until < ?)
           ORDER BY created_at LIMIT 1
         )
         RETURNING *`,
      )
      .bind(workerId, leaseUntil, now, now)
      .first<JobRow>();
    return row ? mapJob(row) : null;
  }

  async heartbeat(jobId: string, workerId: string, leaseSeconds: number, stage = ""): Promise<boolean> {
    const now = this.timestamp();
    const leaseUntil = new Date(this.now().getTime() + leaseSeconds * 1000).toISOString();
    const result = await this.db
      .prepare(
        `UPDATE jobs SET lease_until = ?, stage = CASE WHEN ? <> '' THEN ? ELSE stage END, updated_at = ?
         WHERE job_id = ? AND status = 'processing' AND lease_owner = ? AND lease_until >= ?`,
      )
      .bind(leaseUntil, stage, stage, now, jobId, workerId, now)
      .run();
    if (result.meta.changes === 1 && stage) {
      await this.recordJobEvent(jobId, "job.stage_started", { stage });
    } else if (result.meta.changes !== 1) {
      if (await this.getJob(jobId)) {
        await this.recordJobEvent(jobId, "job.lease_lost", {
          worker_id: workerId,
          stage: stage || null,
          elapsed_since_heartbeat_ms: null,
        });
      }
    }
    return result.meta.changes === 1;
  }

  async checkpoint(
    jobId: string,
    workerId: string,
    stage: string,
    output: unknown,
  ): Promise<JobRecord> {
    const current = await this.requireJob(jobId);
    if (
      current.status !== "processing" ||
      current.leaseOwner !== workerId ||
      !current.leaseUntil ||
      current.leaseUntil < this.timestamp()
    ) {
      throw new Error("lease_lost");
    }
    const checkpoints = { ...current.checkpoints, [stage]: output };
    const result = await this.db
      .prepare(
        `UPDATE jobs SET stage = ?, checkpoint_json = ?, updated_at = ?
         WHERE job_id = ? AND status = 'processing' AND lease_owner = ?`,
      )
      .bind(stage, JSON.stringify(checkpoints), this.timestamp(), jobId, workerId)
      .run();
    if (result.meta.changes !== 1) throw new Error("lease_lost");
    const envelope = output && typeof output === "object" && !Array.isArray(output)
      ? output as Record<string, unknown>
      : {};
    const metadata = envelope.metadata && typeof envelope.metadata === "object" && !Array.isArray(envelope.metadata)
      ? envelope.metadata as Record<string, unknown>
      : null;
    const title = typeof metadata?.title === "string" ? metadata.title.trim() : "";
    const authors = Array.isArray(metadata?.authors)
      ? metadata.authors.filter((author) => typeof author === "string" && author.trim())
      : [];
    if (metadata && title && authors.length > 0) {
      const source = typeof metadata.metadata_source === "string" ? metadata.metadata_source.trim() : "";
      await this.db.prepare(
        `UPDATE papers SET metadata_json = ?, metadata_source = ?, normalized_title = ?, updated_at = ?
         WHERE paper_id = ?`,
      ).bind(JSON.stringify(metadata), source || null, title, this.timestamp(), current.paperId).run();
    }
    const metrics: Record<string, unknown> = { stage };
    for (const key of ["duration_ms", "http_status", "file_size_bytes", "sha256", "task_id", "page_count", "poll_count", "model", "input_tokens", "output_tokens", "json_repair_count", "domain", "year", "venue", "rule_version", "operation", "page_id_suffix", "workflow_run_id", "run_url", "commit", "final_url"]) {
      if (key in envelope) metrics[key] = envelope[key];
    }
    await this.recordJobEvent(jobId, "job.stage_completed", metrics);
    return this.requireJob(jobId);
  }

  async fail(
    jobId: string,
    workerId: string,
    failureOrCode: FailureDescriptor | string,
    legacyMessage = "Processing failed.",
  ): Promise<JobRecord> {
    const current = await this.requireJob(jobId);
    const failure: FailureDescriptor = typeof failureOrCode === "string" ? {
      stage: current.stage, code: failureOrCode, category: "internal", retryable: false,
      attempt: current.attempt, safeMessage: legacyMessage,
      diagnosticHint: "Inspect the local worker log reference.", errorFingerprint: `legacy:${failureOrCode}`,
    } : failureOrCode;
    const errorCode = failure.code.slice(0, 100);
    const errorMessage = failure.safeMessage.slice(0, 1000);
    const { retryPolicy } = await import("./diagnostics");
    const policy = retryPolicy(errorCode, failure.retryable);
    const exhausted = current.attempt >= 3 && policy.retryable;
    const storedErrorCode = exhausted ? "retry_exhausted" : errorCode;
    const result = await this.db
      .prepare(
        `UPDATE jobs SET status = 'failed', lease_owner = NULL, lease_until = NULL,
          error_code = ?, error_message = ?, updated_at = ?
         WHERE job_id = ? AND status = 'processing' AND lease_owner = ?`,
      )
      .bind(storedErrorCode, errorMessage, this.timestamp(), jobId, workerId)
      .run();
    if (result.meta.changes !== 1) throw new Error("lease_lost");
    await this.recordJobEvent(jobId, "job.stage_failed", {
      trace_id: current.traceId, stage: failure.stage || current.stage, code: errorCode,
      category: policy.category, retryable: policy.retryable,
      http_status: failure.httpStatus ?? null, provider_error_code: failure.providerErrorCode ?? null,
      provider_request_id: failure.providerRequestId ?? null, attempt: failure.attempt,
      duration_ms: failure.durationMs ?? null, safe_message: errorMessage,
      diagnostic_hint: failure.diagnosticHint, error_fingerprint: failure.errorFingerprint,
      local_log_ref: failure.localLogRef ?? null, exception_type: failure.exceptionType ?? null,
      module: failure.module ?? null, function: failure.functionName ?? null,
    });
    if (exhausted) {
      await this.recordJobEvent(jobId, "job.retry_exhausted", {
        trace_id: current.traceId,
        total_attempts: current.attempt,
        last_code: errorCode,
      });
    }
    return this.requireJob(jobId);
  }

  async retry(jobId: string, ownerIdentity: string): Promise<JobRecord> {
    const current = await this.requireJob(jobId);
    if (await this.hasJobEvent(jobId, "job.retry_exhausted")) throw new Error("job_retry_exhausted");
    const { retryPolicy } = await import("./diagnostics");
    if (!retryPolicy(current.errorCode).retryable) throw new Error("job_not_retryable");
    const result = await this.db
      .prepare(
        `UPDATE jobs SET status = 'queued', lease_owner = NULL, lease_until = NULL,
          error_code = NULL, error_message = NULL, updated_at = ?
         WHERE job_id = ? AND owner_identity = ? AND status = 'failed'`,
      )
      .bind(this.timestamp(), jobId, ownerIdentity)
      .run();
    if (result.meta.changes !== 1) throw new Error("job_not_retryable");
    await this.recordJobEvent(jobId, "job.retry_scheduled", {
      trace_id: current.traceId, attempt: current.attempt + 1,
      reason: current.errorCode, next_at: this.timestamp(),
    });
    return this.requireJob(jobId);
  }

  async getRetryOperation(idempotencyKey: string): Promise<RetryOperationRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM retry_operations WHERE idempotency_key = ? LIMIT 1")
      .bind(idempotencyKey)
      .first<RetryOperationRow>();
    return row ? mapRetryOperation(row) : null;
  }

  async retryIdempotent(
    jobId: string,
    ownerIdentity: string,
    idempotencyKey: string,
  ): Promise<{ job: JobRecord; replayed: boolean }> {
    const existing = await this.getRetryOperation(idempotencyKey);
    if (existing && existing.jobId !== jobId) throw new Error("idempotency_conflict");
    if (existing) {
      const current = await this.requireJob(jobId);
      const cachedStatus = String(existing.response.status ?? "");
      const replay = cachedStatus
        ? { ...current, status: cachedStatus as JobRecord["status"] }
        : current;
      return { job: replay, replayed: true };
    }
    const current = await this.requireJob(jobId);
    if (current.ownerIdentity !== ownerIdentity || current.status !== "failed") {
      throw new Error("job_not_retryable");
    }
    if (await this.hasJobEvent(jobId, "job.retry_exhausted")) throw new Error("job_retry_exhausted");
    const { retryPolicy } = await import("./diagnostics");
    if (!retryPolicy(current.errorCode).retryable) throw new Error("job_not_retryable");
    const timestamp = this.timestamp();
    const results = await this.db.batch([
      this.db.prepare(
        `INSERT OR IGNORE INTO retry_operations (
          idempotency_key, job_id, operation, state, response_json, created_at, updated_at
        ) VALUES (?, ?, 'retry', 'pending', '{}', ?, ?)`,
      ).bind(idempotencyKey, jobId, timestamp, timestamp),
      this.db.prepare(
        `UPDATE jobs SET status = 'queued', lease_owner = NULL, lease_until = NULL,
          error_code = NULL, error_message = NULL, updated_at = ?
         WHERE job_id = ? AND owner_identity = ? AND status = 'failed'`,
      ).bind(timestamp, jobId, ownerIdentity),
    ]);
    const operation = await this.getRetryOperation(idempotencyKey);
    if (!operation || operation.jobId !== jobId) throw new Error("idempotency_conflict");
    const job = await this.requireJob(jobId);
    const changed = Number(results[1].meta.changes) === 1;
    if (!changed && job.status !== "queued" && job.status !== "processing") {
      throw new Error("job_not_retryable");
    }
    const response = {
      job_id: job.jobId,
      paper_id: job.paperId,
      status: job.status,
      code: "retry_accepted",
    };
    await this.db.prepare(
      `UPDATE retry_operations SET state = 'completed', response_json = ?, updated_at = ?
       WHERE idempotency_key = ?`,
    ).bind(JSON.stringify(response), this.timestamp(), idempotencyKey).run();
    if (changed) {
      await this.recordJobEvent(jobId, "job.retry_scheduled", {
        trace_id: current.traceId,
        attempt: current.attempt + 1,
        reason: current.errorCode,
        next_at: timestamp,
      });
    }
    return { job, replayed: !changed };
  }

  async getMetadataRefresh(idempotencyKey: string): Promise<MetadataRefreshRecord | null> {
    const row = await this.db.prepare(
      `SELECT o.*, j.paper_id, j.input_ref, p.arxiv_id, u.notion_page_id, u.slug
       FROM metadata_refresh_operations o
       JOIN jobs j ON j.job_id = o.job_id
       JOIN papers p ON p.paper_id = j.paper_id
       LEFT JOIN publications u ON u.job_id = j.job_id
       WHERE o.idempotency_key = ? LIMIT 1`,
    ).bind(idempotencyKey).first<MetadataRefreshRow>();
    return row ? mapMetadataRefresh(row) : null;
  }

  async enqueueMetadataRefresh(
    jobId: string,
    idempotencyKey: string,
  ): Promise<{ operation: MetadataRefreshRecord; replayed: boolean }> {
    const existing = await this.getMetadataRefresh(idempotencyKey);
    if (existing && existing.jobId !== jobId) throw new Error("idempotency_conflict");
    if (existing) return { operation: existing, replayed: true };
    const job = await this.requireJob(jobId);
    if (job.status !== "published") throw new Error("metadata_refresh_not_allowed");
    const publication = await this.db.prepare(
      "SELECT notion_page_id FROM publications WHERE job_id = ? AND publish_status = 'published' LIMIT 1",
    ).bind(jobId).first<{ notion_page_id: string }>();
    if (!publication) throw new Error("publication_not_found");
    const timestamp = this.timestamp();
    await this.db.prepare(
      `INSERT OR IGNORE INTO metadata_refresh_operations (
        idempotency_key, job_id, state, created_at, updated_at
      ) VALUES (?, ?, 'queued', ?, ?)`,
    ).bind(idempotencyKey, jobId, timestamp, timestamp).run();
    const operation = await this.getMetadataRefresh(idempotencyKey);
    if (!operation || operation.jobId !== jobId) throw new Error("idempotency_conflict");
    return { operation, replayed: false };
  }

  async claimMetadataRefresh(workerId: string, leaseSeconds: number): Promise<MetadataRefreshRecord | null> {
    const now = this.timestamp();
    const leaseUntil = new Date(this.now().getTime() + leaseSeconds * 1000).toISOString();
    const row = await this.db.prepare(
      `UPDATE metadata_refresh_operations SET
        state = 'processing', lease_owner = ?, lease_until = ?,
        error_code = NULL, error_message = NULL, updated_at = ?
       WHERE idempotency_key = (
         SELECT idempotency_key FROM metadata_refresh_operations
         WHERE state = 'queued'
            OR (state = 'processing' AND lease_until IS NOT NULL AND lease_until < ?)
         ORDER BY created_at LIMIT 1
       )
       RETURNING *`,
    ).bind(workerId, leaseUntil, now, now).first<MetadataRefreshRow>();
    if (!row) return null;
    const details = await this.db.prepare(
      `SELECT o.*, j.paper_id, j.input_ref, p.arxiv_id, u.notion_page_id, u.slug
       FROM metadata_refresh_operations o
       JOIN jobs j ON j.job_id = o.job_id
       JOIN papers p ON p.paper_id = j.paper_id
       JOIN publications u ON u.job_id = j.job_id
       WHERE o.idempotency_key = ?`,
    ).bind(row.idempotency_key).first<MetadataRefreshRow>();
    return details ? mapMetadataRefresh(details) : null;
  }

  async completeMetadataRefresh(
    idempotencyKey: string,
    workerId: string,
    result: Record<string, unknown>,
  ): Promise<MetadataRefreshRecord> {
    const current = await this.getMetadataRefresh(idempotencyKey);
    if (
      !current || current.state !== "processing" || current.leaseOwner !== workerId ||
      !current.leaseUntil || current.leaseUntil < this.timestamp()
    ) throw new Error("lease_lost");
    const metadata = result.metadata && typeof result.metadata === "object" && !Array.isArray(result.metadata)
      ? result.metadata as Record<string, unknown>
      : {};
    const title = typeof metadata.title === "string" ? metadata.title.trim() : "";
    const source = typeof metadata.metadata_source === "string" ? metadata.metadata_source.trim() : "";
    const timestamp = this.timestamp();
    await this.db.batch([
      this.db.prepare(
        `UPDATE metadata_refresh_operations SET state = 'completed', lease_owner = NULL,
          lease_until = NULL, result_json = ?, updated_at = ?
         WHERE idempotency_key = ? AND state = 'processing' AND lease_owner = ?`,
      ).bind(JSON.stringify(result), timestamp, idempotencyKey, workerId),
      this.db.prepare(
        `UPDATE papers SET metadata_json = ?, metadata_source = ?,
          normalized_title = CASE WHEN ? <> '' THEN ? ELSE normalized_title END, updated_at = ?
         WHERE paper_id = (SELECT paper_id FROM jobs WHERE job_id = ?)`,
      ).bind(JSON.stringify(metadata), source || null, title, title, timestamp, current.jobId),
    ]);
    const completed = await this.getMetadataRefresh(idempotencyKey);
    if (!completed || completed.state !== "completed") throw new Error("lease_lost");
    return completed;
  }

  async failMetadataRefresh(
    idempotencyKey: string,
    workerId: string,
    errorCode: string,
    errorMessage: string,
  ): Promise<MetadataRefreshRecord> {
    const changed = await this.db.prepare(
      `UPDATE metadata_refresh_operations SET state = 'failed', lease_owner = NULL,
        lease_until = NULL, error_code = ?, error_message = ?, updated_at = ?
       WHERE idempotency_key = ? AND state = 'processing' AND lease_owner = ?`,
    ).bind(errorCode, errorMessage, this.timestamp(), idempotencyKey, workerId).run();
    if (changed.meta.changes !== 1) throw new Error("lease_lost");
    const failed = await this.getMetadataRefresh(idempotencyKey);
    if (!failed) throw new Error("operation_not_found");
    return failed;
  }

  async listOwnerJobs(ownerIdentity: string, limit = 100): Promise<JobRecord[]> {
    const rows = await this.db
      .prepare("SELECT * FROM jobs WHERE owner_identity = ? ORDER BY created_at DESC LIMIT ?")
      .bind(ownerIdentity, Math.max(1, Math.min(limit, 100)))
      .all<JobRow>();
    return rows.results.map(mapJob);
  }

  async getOwnerJob(jobId: string, ownerIdentity: string): Promise<JobRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM jobs WHERE job_id = ? AND owner_identity = ? LIMIT 1")
      .bind(jobId, ownerIdentity)
      .first<JobRow>();
    return row ? mapJob(row) : null;
  }

  async listJobEvents(jobId: string): Promise<Array<Record<string, unknown>>> {
    const rows = await this.db
      .prepare(
        `SELECT event_type, details_json, created_at FROM job_events
         WHERE job_id = ? ORDER BY event_id`,
      )
      .bind(jobId)
      .all<{ event_type: string; details_json: string; created_at: string }>();
    return rows.results.map((row) => ({
      event_type: row.event_type,
      details: parseCheckpoints(row.details_json),
      created_at: row.created_at,
    }));
  }

  async complete(
    jobId: string,
    workerId: string,
    publication: PublicationInput,
  ): Promise<JobRecord> {
    const current = await this.requireJob(jobId);
    if (
      current.status !== "processing" ||
      current.leaseOwner !== workerId ||
      !current.leaseUntil ||
      current.leaseUntil < this.timestamp()
    ) {
      throw new Error("lease_lost");
    }
    const timestamp = this.timestamp();
    await this.db.batch([
      this.db
        .prepare(
          `INSERT INTO publications (
            paper_id, job_id, notion_page_id, slug, site_url, publish_status
          ) VALUES (?, ?, ?, ?, ?, 'publishing')
          ON CONFLICT(paper_id) DO UPDATE SET
            job_id = excluded.job_id,
            notion_page_id = excluded.notion_page_id,
            slug = excluded.slug,
            site_url = excluded.site_url,
            publish_status = 'publishing'`,
        )
        .bind(
          current.paperId,
          jobId,
          publication.notionPageId,
          publication.slug,
          publication.siteUrl,
        ),
      this.db
        .prepare(
          `UPDATE jobs SET status = 'publishing', stage = 'publishing',
            lease_owner = NULL, lease_until = NULL, updated_at = ?
           WHERE job_id = ? AND status = 'processing' AND lease_owner = ?`,
        )
        .bind(timestamp, jobId, workerId),
    ]);
    return this.requireJob(jobId);
  }

  async recordArtifact(
    jobId: string,
    workerId: string,
    artifact: ArtifactInput,
  ): Promise<ArtifactRecord> {
    const job = await this.getActiveLease(jobId, workerId);
    if (!job) throw new Error("lease_lost");
    const artifactId = crypto.randomUUID();
    const createdAt = this.timestamp();
    await this.db
      .prepare(
        `INSERT INTO artifacts (
          artifact_id, paper_id, job_id, kind, r2_key, sha256,
          size_bytes, content_type, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        artifactId,
        job.paperId,
        jobId,
        artifact.kind,
        artifact.r2Key,
        artifact.sha256,
        artifact.sizeBytes,
        artifact.contentType,
        createdAt,
      )
      .run();
    return {
      artifactId,
      paperId: job.paperId,
      jobId,
      createdAt,
      ...artifact,
    };
  }

  async getArtifactForJob(jobId: string, artifactId: string): Promise<ArtifactRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM artifacts WHERE job_id = ? AND artifact_id = ?")
      .bind(jobId, artifactId)
      .first<ArtifactRow>();
    if (!row) return null;
    return {
      artifactId: row.artifact_id,
      paperId: row.paper_id,
      jobId: row.job_id,
      kind: row.kind,
      r2Key: row.r2_key,
      sha256: row.sha256,
      sizeBytes: row.size_bytes,
      contentType: row.content_type,
      createdAt: row.created_at,
    };
  }

  async hasJobEvent(jobId: string, eventType: string): Promise<boolean> {
    const row = await this.db
      .prepare("SELECT event_id FROM job_events WHERE job_id = ? AND event_type = ? LIMIT 1")
      .bind(jobId, eventType)
      .first<{ event_id: number }>();
    return Boolean(row);
  }

  async recordJobEvent(
    jobId: string,
    eventType: string,
    details: Record<string, unknown> = {},
  ): Promise<void> {
    const traceId = typeof details.trace_id === "string"
      ? details.trace_id
      : (await this.getJob(jobId))?.traceId ?? null;
    const safeDetails = { ...details, trace_id: traceId };
    await this.db
      .prepare(
        `INSERT OR IGNORE INTO job_events (job_id, event_type, details_json, created_at)
         VALUES (?, ?, ?, ?)`,
      )
      .bind(jobId, eventType, JSON.stringify(safeDetails), this.timestamp())
      .run();
  }

  async finishPublication(
    jobId: string,
    success: boolean,
    gitCommit = "",
    metrics: { workflowRunId?: string; runUrl?: string } = {},
  ): Promise<JobRecord> {
    const current = await this.requireJob(jobId);
    if (current.status !== "publishing") {
      await this.recordJobEvent(jobId, "publication.stale_callback_ignored", {
        observed_status: current.status,
        callback_success: success,
        git_commit: gitCommit,
      });
      return current;
    }
    const timestamp = this.timestamp();
    if (success) {
      await this.db.batch([
        this.db
          .prepare(
            `UPDATE publications SET publish_status = 'published', git_commit = ?, published_at = ?
             WHERE job_id = ?`,
          )
          .bind(gitCommit, timestamp, jobId),
        this.db
          .prepare(
            `UPDATE jobs SET status = 'published', stage = 'published', error_code = NULL,
              error_message = NULL, updated_at = ? WHERE job_id = ? AND status = 'publishing'`,
          )
          .bind(timestamp, jobId),
        this.db
          .prepare(
            `INSERT OR IGNORE INTO job_events (job_id, event_type, details_json, created_at)
             VALUES (?, 'publication.completed', ?, ?)`,
          )
          .bind(jobId, JSON.stringify({
            git_commit: gitCommit,
            trace_id: current.traceId,
            workflow_run_id: metrics.workflowRunId || null,
            run_url: metrics.runUrl || null,
          }), timestamp),
      ]);
    } else {
      await this.db.batch([
        this.db
          .prepare("UPDATE publications SET publish_status = 'deploy_failed' WHERE job_id = ?")
          .bind(jobId),
        this.db
          .prepare(
            `UPDATE jobs SET status = 'failed', error_code = 'deploy_failed',
              error_message = 'GitHub Pages deployment failed.', updated_at = ?
             WHERE job_id = ? AND status = 'publishing'`,
          )
          .bind(timestamp, jobId),
      ]);
      await this.recordJobEvent(jobId, "publication.failed", {
        trace_id: current.traceId,
        stage: "github_pages_deploy",
        code: "deploy_failed",
        category: "publication",
        retryable: true,
        diagnostic_hint: "Open the GitHub Actions run and inspect the failed deployment step.",
        workflow_run_id: metrics.workflowRunId || null,
        run_url: metrics.runUrl || null,
      });
    }
    return this.requireJob(jobId);
  }

  async failPublicationDispatch(jobId: string, githubStatus: number): Promise<JobRecord> {
    const timestamp = this.timestamp();
    await this.db.batch([
      this.db
        .prepare("UPDATE publications SET publish_status = 'dispatch_failed' WHERE job_id = ?")
        .bind(jobId),
      this.db
        .prepare(
          `UPDATE jobs SET status = 'failed', error_code = 'github_dispatch_failed',
            error_message = 'GitHub 构建触发失败，请检查 Cloudflare GITHUB_TOKEN 的仓库权限。',
            updated_at = ? WHERE job_id = ? AND status = 'publishing'`,
        )
        .bind(timestamp, jobId),
      this.db
        .prepare(
          `INSERT INTO job_events (job_id, event_type, details_json, created_at)
           VALUES (?, 'publication.dispatch_failed', ?, ?)`,
        )
        .bind(jobId, JSON.stringify({ github_status: githubStatus }), timestamp),
    ]);
    return this.requireJob(jobId);
  }
}
