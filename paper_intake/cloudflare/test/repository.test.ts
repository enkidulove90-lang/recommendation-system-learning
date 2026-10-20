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
});
