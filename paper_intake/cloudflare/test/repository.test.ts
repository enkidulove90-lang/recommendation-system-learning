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
