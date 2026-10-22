import { env } from "cloudflare:workers";
import { describe, expect, it } from "vitest";

import { IntakeRepository } from "../src/repository";

describe("IntakeRepository", () => {
  it("deduplicates in DOI, arXiv, PDF hash, then title fingerprint order", async () => {
    const repository = new IntakeRepository(env.DB);
    const first = await repository.createOrReusePaper({
      doi: "10.1/example",
      arxivId: "2608.17316",
      pdfSha256: "hash-a",
      titleFingerprint: "paper-title",
    });

    const byDoi = await repository.createOrReusePaper({
      doi: "10.1/example",
      pdfSha256: "different-hash",
    });
    const byArxiv = await repository.createOrReusePaper({ arxivId: "2608.17316" });
    const byHash = await repository.createOrReusePaper({ pdfSha256: "hash-a" });
    const byTitle = await repository.createOrReusePaper({ titleFingerprint: "paper-title" });

    expect(byDoi.paperId).toBe(first.paperId);
    expect(byArxiv.paperId).toBe(first.paperId);
    expect(byHash.paperId).toBe(first.paperId);
    expect(byTitle.paperId).toBe(first.paperId);
    expect([byDoi, byArxiv, byHash, byTitle].every((paper) => paper.reused)).toBe(true);
  });

  it("leases one queued job and reclaims it only after expiry", async () => {
    let now = new Date("2026-10-20T00:00:00.000Z");
    const repository = new IntakeRepository(env.DB, () => now);
    const paper = await repository.createOrReusePaper({ doi: "10.1/lease" });
    const job = await repository.createJob({
      paperId: paper.paperId,
      ownerIdentity: "owner@example.com",
      inputType: "pdf",
      inputRef: "originals/paper.pdf",
    });

    expect((await repository.claim("worker-a", 600))?.jobId).toBe(job.jobId);
    expect(await repository.claim("worker-b", 600)).toBeNull();

    now = new Date(now.getTime() + 601_000);
    const reclaimed = await repository.claim("worker-b", 600);
    expect(reclaimed?.jobId).toBe(job.jobId);
    expect(reclaimed?.leaseOwner).toBe("worker-b");
    expect(reclaimed?.attempt).toBe(2);
  });

  it("accepts heartbeats and checkpoints only from the active lease owner", async () => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({ arxivId: "2608.01847" });
    const job = await repository.createJob({
      paperId: paper.paperId,
      ownerIdentity: "owner@example.com",
      inputType: "url",
      inputRef: "https://arxiv.org/abs/2608.01847",
    });
    await repository.claim("worker-a", 600);

    expect(await repository.heartbeat(job.jobId, "worker-b", 600)).toBe(false);
    await expect(
      repository.checkpoint(job.jobId, "worker-b", "parsed", { artifactId: "a1" }),
    ).rejects.toThrow("lease_lost");

    expect(await repository.heartbeat(job.jobId, "worker-a", 600)).toBe(true);
    const checkpointed = await repository.checkpoint(
      job.jobId,
      "worker-a",
      "parsed",
      { artifactId: "a1" },
    );
    expect(checkpointed.stage).toBe("parsed");
    expect(checkpointed.checkpoints.parsed).toEqual({ artifactId: "a1" });
  });

  it("stores verified metadata from a checkpoint without rerunning any job stage", async () => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({ arxivId: "2606.17628" });
    const job = await repository.createJob({
      paperId: paper.paperId,
      ownerIdentity: "owner@example.com",
      inputType: "url",
      inputRef: "https://arxiv.org/abs/2606.17628",
    });
    await repository.claim("worker-a", 600);
    await repository.checkpoint(job.jobId, "worker-a", "resolve_metadata", {
      metadata: {
        canonical_id: "2606.17628",
        title: "OPD-Evolver",
        authors: ["Author One"],
        metadata_source: "arxiv_xml",
      },
    });

    const stored = await env.DB.prepare(
      "SELECT metadata_json, metadata_source, normalized_title FROM papers WHERE paper_id = ?",
    ).bind(paper.paperId).first<{
      metadata_json: string;
      metadata_source: string;
      normalized_title: string;
    }>();
    expect(JSON.parse(stored?.metadata_json || "{}").authors).toEqual(["Author One"]);
    expect(stored?.metadata_source).toBe("arxiv_xml");
    expect(stored?.normalized_title).toBe("OPD-Evolver");
  });

  it("moves failed jobs back to queued without losing checkpoints", async () => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({ pdfSha256: "retry-hash" });
    const job = await repository.createJob({
      paperId: paper.paperId,
      ownerIdentity: "owner@example.com",
      inputType: "pdf",
      inputRef: "originals/retry.pdf",
    });
    await repository.claim("worker-a", 600);
    await repository.checkpoint(job.jobId, "worker-a", "parsed", { artifactId: "parsed" });
    await repository.fail(job.jobId, "worker-a", "deepseek_failed", "generation failed");

    const retried = await repository.retry(job.jobId, "owner@example.com");
    expect(retried.status).toBe("queued");
    expect(retried.checkpoints.parsed).toEqual({ artifactId: "parsed" });
    expect(retried.errorCode).toBeNull();
  });

  it("records a structured stage failure and a retry event with the stable trace id", async () => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({ arxivId: "2601.00001" });
    const job = await repository.createJob({
      paperId: paper.paperId,
      ownerIdentity: "owner@example.com",
      inputType: "url",
      inputRef: "https://arxiv.org/abs/2601.00001",
      traceId: "tr_11111111-1111-4111-8111-111111111111",
    });
    await repository.claim("worker-a", 600);
    await repository.heartbeat(job.jobId, "worker-a", 600, "deepseek_generate");
    await repository.fail(job.jobId, "worker-a", {
      stage: "deepseek_generate",
      code: "deepseek_schema_invalid",
      category: "validation",
      retryable: false,
      httpStatus: 200,
      providerErrorCode: "invalid_json",
      providerRequestId: "req-safe",
      attempt: 1,
      durationMs: 27510,
      safeMessage: "模型返回内容未通过文章 Schema 校验",
      diagnosticHint: "检查缺失字段和 JSON 局部修复记录",
      errorFingerprint: "sha1-safe",
      localLogRef: "worker-a:remote-worker.log#event-12",
    });

    const failed = await repository.getJob(job.jobId);
    const events = await repository.listJobEvents(job.jobId);
    const event = events.find((item) => item.event_type === "job.stage_failed");
    expect(failed?.traceId).toBe("tr_11111111-1111-4111-8111-111111111111");
    expect(event).toMatchObject({
      event_type: "job.stage_failed",
      details: {
        trace_id: "tr_11111111-1111-4111-8111-111111111111",
        stage: "deepseek_generate",
        code: "deepseek_schema_invalid",
        category: "validation",
        retryable: false,
        http_status: 200,
        provider_request_id: "req-safe",
      },
    });

    await expect(repository.retry(job.jobId, "owner@example.com")).rejects.toThrow("job_not_retryable");
  });

  it("records lease loss and retry exhaustion as explicit events", async () => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({ arxivId: "2601.00003" });
    const job = await repository.createJob({
      paperId: paper.paperId, ownerIdentity: "owner@example.com", inputType: "url",
      inputRef: "https://arxiv.org/abs/2601.00003",
    });
    await repository.claim("worker-a", 600);
    expect(await repository.heartbeat(job.jobId, "wrong-worker", 600, "download_pdf")).toBe(false);
    await env.DB.prepare("UPDATE jobs SET attempt = 3 WHERE job_id = ?").bind(job.jobId).run();
    await repository.fail(job.jobId, "worker-a", {
      stage: "download_pdf", code: "timeout", category: "network", retryable: true,
      attempt: 3, safeMessage: "Download timed out.", diagnosticHint: "Retry later.",
      errorFingerprint: "timeout-fingerprint",
    });
    const events = await repository.listJobEvents(job.jobId);
    expect((await repository.getJob(job.jobId))?.errorCode).toBe("retry_exhausted");
    expect(events).toEqual(expect.arrayContaining([
      expect.objectContaining({ event_type: "job.lease_lost", details: expect.objectContaining({ worker_id: "wrong-worker" }) }),
      expect.objectContaining({ event_type: "job.retry_exhausted", details: expect.objectContaining({ total_attempts: 3, last_code: "timeout" }) }),
    ]));
    await expect(repository.retry(job.jobId, "owner@example.com")).rejects.toThrow("job_retry_exhausted");
  });

  it.each([
    ["pdf_url_malformed", "validation"],
    ["deepseek_schema_invalid", "validation"],
    ["notion_schema_incompatible", "config"],
    ["file_io_error", "internal"],
  ] as const)("refuses retries for %s", async (code, category) => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({ canonicalUrl: `https://papers.example/${code}` });
    const job = await repository.createJob({
      paperId: paper.paperId, ownerIdentity: "owner@example.com", inputType: "url", inputRef: paper.canonicalUrl,
    });
    await repository.claim(`worker-${code}`, 600);
    await repository.fail(job.jobId, `worker-${code}`, {
      stage: "validate_input", code, category, retryable: true, attempt: 1,
      safeMessage: "Safe failure.", diagnosticHint: "Fix the input or configuration.", errorFingerprint: `fp-${code}`,
    });
    await expect(repository.retry(job.jobId, "owner@example.com")).rejects.toThrow("job_not_retryable");
  });

  it("leases one idempotent published metadata refresh without changing publication state", async () => {
    const repository = new IntakeRepository(env.DB);
    const paper = await repository.createOrReusePaper({
      arxivId: "2606.17628",
      normalizedTitle: "2606.17628",
    });
    const job = await repository.createJob({
      paperId: paper.paperId,
      ownerIdentity: "owner@example.com",
      inputType: "url",
      inputRef: "https://arxiv.org/abs/2606.17628",
    });
    await repository.claim("publisher", 600);
    await repository.complete(job.jobId, "publisher", {
      notionPageId: "notion-page",
      slug: "paper-2606.17628",
      siteUrl: "https://example.github.io/article/paper-2606.17628/",
    });
    await repository.finishPublication(job.jobId, true, "commit-1");

    const first = await repository.enqueueMetadataRefresh(job.jobId, "11111111-1111-4111-8111-111111111111");
    const replay = await repository.enqueueMetadataRefresh(job.jobId, "11111111-1111-4111-8111-111111111111");
    const claimed = await repository.claimMetadataRefresh("metadata-worker", 600);

    expect(first.replayed).toBe(false);
    expect(replay.replayed).toBe(true);
    expect(claimed?.jobId).toBe(job.jobId);
    expect(claimed?.notionPageId).toBe("notion-page");
    expect(await repository.claimMetadataRefresh("second-worker", 600)).toBeNull();
    expect((await repository.getJob(job.jobId))?.status).toBe("published");

    await repository.completeMetadataRefresh(
      "11111111-1111-4111-8111-111111111111",
      "metadata-worker",
      {
        changed: true,
        metadata: {
          canonical_id: "2606.17628",
          title: "OPD-Evolver",
          authors: ["Author One"],
          metadata_source: "arxiv_api_refresh",
        },
      },
    );
    const completed = await repository.getMetadataRefresh("11111111-1111-4111-8111-111111111111");
    expect(completed?.state).toBe("completed");
    expect((await repository.getJob(job.jobId))?.status).toBe("published");
    const stored = await env.DB.prepare("SELECT metadata_source, normalized_title FROM papers WHERE paper_id = ?")
      .bind(paper.paperId).first<{ metadata_source: string; normalized_title: string }>();
    expect(stored?.metadata_source).toBe("arxiv_api_refresh");
    expect(stored?.normalized_title).toBe("OPD-Evolver");
  });
});
