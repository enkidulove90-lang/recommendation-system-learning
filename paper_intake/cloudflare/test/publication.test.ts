import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { afterEach, describe, expect, it, vi } from "vitest";

import { IntakeRepository } from "../src/repository";
import type { AppEnv } from "../src/security";

const testEnv = env as AppEnv;
const machineHeaders = {
  authorization: "Bearer test-worker-token",
  "content-type": "application/json",
};

async function seedClaimedJob() {
  const repository = new IntakeRepository(testEnv.DB);
  const paper = await repository.createOrReusePaper({
    canonicalUrl: `https://papers.example/${crypto.randomUUID()}`,
  });
  const job = await repository.createJob({
    paperId: paper.paperId,
    ownerIdentity: "owner@example.com",
    inputType: "url",
    inputRef: paper.canonicalUrl,
  });
  await repository.claim("worker-a", 600);
  return { repository, paper, job };
}

afterEach(() => vi.restoreAllMocks());

describe("publication dispatch", () => {
  it("dispatches once and completes only after the Pages callback", async () => {
    const { repository, job } = await seedClaimedJob();
    const github = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status: 204 }));

    const completion = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/complete`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({
          worker_id: "worker-a",
          publication: {
            notion_page_id: "notion-page-1",
            slug: "consumer-search-transformer",
            site_url: "https://enkidulove90-lang.github.io/article/consumer-search-transformer/",
          },
        }),
      },
    );
    expect(completion.status).toBe(200);
    expect(github).toHaveBeenCalledTimes(1);
    const dispatch = JSON.parse(String(github.mock.calls[0]?.[1]?.body || "{}"));
    expect(dispatch.client_payload).toMatchObject({
      job_id: job.jobId,
      paper_id: job.paperId,
      notion_page_id: "notion-page-1",
      slug: "consumer-search-transformer",
    });
    expect((await repository.getJob(job.jobId))?.status).toBe("publishing");

    const callback = await SELF.fetch("https://worker.test/v1/publications/callback", {
      method: "POST",
      headers: {
        authorization: "Bearer test-callback-token",
        "content-type": "application/json",
      },
      body: JSON.stringify({ job_id: job.jobId, ok: true, git_commit: "abc123" }),
    });
    expect(callback.status).toBe(200);
    expect((await repository.getJob(job.jobId))?.status).toBe("published");

    const repeated = await SELF.fetch("https://worker.test/v1/publications/callback", {
      method: "POST",
      headers: {
        authorization: "Bearer test-callback-token",
        "content-type": "application/json",
      },
      body: JSON.stringify({ job_id: job.jobId, ok: true, git_commit: "abc123" }),
    });
    expect(repeated.status).toBe(200);
    expect(github).toHaveBeenCalledTimes(1);
    const completedEvents = await testEnv.DB.prepare(
      "SELECT COUNT(*) AS count FROM job_events WHERE job_id = ? AND event_type = 'publication.completed'",
    ).bind(job.jobId).first<{ count: number }>();
    expect(completedEvents?.count).toBe(1);
  });

  it("keeps a failed deployment retryable in the completed UI group", async () => {
    const { repository, job } = await seedClaimedJob();
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status: 204 }));
    await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/complete`, {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({
        worker_id: "worker-a",
        publication: {
          notion_page_id: "notion-page-2",
          slug: "failed-deploy",
          site_url: "https://enkidulove90-lang.github.io/article/failed-deploy/",
        },
      }),
    });
    const callback = await SELF.fetch("https://worker.test/v1/publications/callback", {
      method: "POST",
      headers: {
        authorization: "Bearer test-callback-token",
        "content-type": "application/json",
      },
      body: JSON.stringify({ job_id: job.jobId, ok: false }),
    });
    expect(callback.status).toBe(200);
    const failed = await repository.getJob(job.jobId);
    expect(failed?.status).toBe("failed");
    expect(failed?.errorCode).toBe("deploy_failed");
    expect((await repository.retry(job.jobId, "owner@example.com")).status).toBe("queued");
  });
});
