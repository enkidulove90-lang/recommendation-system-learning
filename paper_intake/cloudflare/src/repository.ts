import type {
  ArtifactInput,
  ArtifactRecord,
  CreateJobInput,
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
    try {
      await this.db.batch([
        this.db
          .prepare(
            `INSERT INTO jobs (
              job_id, paper_id, owner_identity, input_type, input_ref,
              stage, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'received', 'queued', ?, ?)`,
          )
          .bind(
            jobId,
            input.paperId,
            input.ownerIdentity,
            input.inputType,
            input.inputRef,
            timestamp,
            timestamp,
          ),
        this.db
          .prepare(
            `INSERT INTO job_events (job_id, event_type, details_json, created_at)
             VALUES (?, 'job.created', '{}', ?)`,
          )
          .bind(jobId, timestamp),
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

  async heartbeat(jobId: string, workerId: string, leaseSeconds: number): Promise<boolean> {
    const now = this.timestamp();
    const leaseUntil = new Date(this.now().getTime() + leaseSeconds * 1000).toISOString();
    const result = await this.db
      .prepare(
        `UPDATE jobs SET lease_until = ?, updated_at = ?
         WHERE job_id = ? AND status = 'processing' AND lease_owner = ? AND lease_until >= ?`,
      )
      .bind(leaseUntil, now, jobId, workerId, now)
      .run();
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
    return this.requireJob(jobId);
  }

  async fail(
    jobId: string,
    workerId: string,
    errorCode: string,
    errorMessage: string,
  ): Promise<JobRecord> {
    const result = await this.db
      .prepare(
        `UPDATE jobs SET status = 'failed', lease_owner = NULL, lease_until = NULL,
          error_code = ?, error_message = ?, updated_at = ?
         WHERE job_id = ? AND status = 'processing' AND lease_owner = ?`,
      )
      .bind(errorCode, errorMessage, this.timestamp(), jobId, workerId)
      .run();
    if (result.meta.changes !== 1) throw new Error("lease_lost");
    return this.requireJob(jobId);
  }

  async retry(jobId: string, ownerIdentity: string): Promise<JobRecord> {
    const result = await this.db
      .prepare(
        `UPDATE jobs SET status = 'queued', lease_owner = NULL, lease_until = NULL,
          error_code = NULL, error_message = NULL, updated_at = ?
         WHERE job_id = ? AND owner_identity = ? AND status = 'failed'`,
      )
      .bind(this.timestamp(), jobId, ownerIdentity)
      .run();
    if (result.meta.changes !== 1) throw new Error("job_not_retryable");
    return this.requireJob(jobId);
  }

  async listOwnerJobs(ownerIdentity: string, limit = 100): Promise<JobRecord[]> {
    const rows = await this.db
      .prepare("SELECT * FROM jobs WHERE owner_identity = ? ORDER BY created_at DESC LIMIT ?")
      .bind(ownerIdentity, Math.max(1, Math.min(limit, 100)))
      .all<JobRow>();
    return rows.results.map(mapJob);
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
    await this.db
      .prepare(
        `INSERT OR IGNORE INTO job_events (job_id, event_type, details_json, created_at)
         VALUES (?, ?, ?, ?)`,
      )
      .bind(jobId, eventType, JSON.stringify(details), this.timestamp())
      .run();
  }

  async finishPublication(
    jobId: string,
    success: boolean,
    gitCommit = "",
  ): Promise<JobRecord> {
    const current = await this.requireJob(jobId);
    if (success && current.status === "published") return current;
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
          .bind(jobId, JSON.stringify({ git_commit: gitCommit }), timestamp),
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
    }
    return this.requireJob(jobId);
  }
}
