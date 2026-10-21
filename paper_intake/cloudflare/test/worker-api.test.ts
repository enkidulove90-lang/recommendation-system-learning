import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { describe, expect, it } from "vitest";

import { IntakeRepository } from "../src/repository";
import type { AppEnv } from "../src/security";

const testEnv = env as AppEnv & { ARTIFACTS: R2Bucket };
const machineHeaders = {
  authorization: "Bearer test-worker-token",
  "content-type": "application/json",
};

async function seedJob(inputType: "url" | "pdf" = "url") {
  const repository = new IntakeRepository(testEnv.DB);
  const paper = await repository.createOrReusePaper({
    canonicalUrl: `https://papers.example/${crypto.randomUUID()}`,
  });
  const inputRef = inputType === "pdf"
    ? `originals/${paper.paperId}/paper.pdf`
    : paper.canonicalUrl;
  if (inputType === "pdf") {
    await testEnv.ARTIFACTS.put(inputRef, new TextEncoder().encode("%PDF-1.7\n%%EOF"));
  }
  return repository.createJob({
    paperId: paper.paperId,
    ownerIdentity: "owner@example.com",
    inputType,
    inputRef,
  });
}

async function claim(workerId = "worker-a", authorization = machineHeaders.authorization) {
  return SELF.fetch("https://worker.test/v1/worker/claim", {
    method: "POST",
    headers: { ...machineHeaders, authorization },
    body: JSON.stringify({ worker_id: workerId, lease_seconds: 600 }),
  });
}

describe("remote worker API", () => {
  it("accepts an operator URL through the same normalized intake path", async () => {
    const response = await SELF.fetch("https://worker.test/v1/worker/intake/url", {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({ url: "https://arxiv.org/pdf/2509.06002v1.pdf" }),
    });
    expect(response.status).toBe(202);
    expect(await response.json()).toMatchObject({
      status: "queued",
      code: "intake_accepted",
    });
  });

  it("exposes a non-mutating authenticated health check", async () => {
    const denied = await SELF.fetch("https://worker.test/v1/worker/health", {
      headers: { authorization: "Bearer wrong" },
    });
    expect(denied.status).toBe(401);

    const response = await SELF.fetch("https://worker.test/v1/worker/health", {
      headers: { authorization: machineHeaders.authorization },
    });
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({
      status: "ok",
      code: "worker_authenticated",
    });
  });

  it("returns 204 when no work is queued", async () => {
    const response = await SELF.fetch("https://worker.test/v1/worker/jobs/claim", {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({ worker_id: "worker-a" }),
    });
    expect(response.status).toBe(204);
  });

  it("requires the machine token and renews only the current lease", async () => {
    const job = await seedJob();
    expect((await claim("worker-a", "Bearer wrong")).status).toBe(401);
    const claimedResponse = await claim();
    expect(claimedResponse.status).toBe(200);
    const claimed = await claimedResponse.json<{ job_id: string; lease_owner: string }>();
    expect(claimed.job_id).toBe(job.jobId);

    const heartbeat = (workerId: string) => SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/heartbeat`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({ worker_id: workerId, lease_seconds: 600 }),
      },
    );
    expect((await heartbeat("other-worker")).status).toBe(409);
    expect((await heartbeat(claimed.lease_owner)).status).toBe(200);
  });

  it("serves the claimed PDF without exposing its R2 key", async () => {
    const job = await seedJob("pdf");
    await claim();
    const response = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/input?worker_id=worker-a`,
      { headers: { authorization: machineHeaders.authorization } },
    );
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/pdf");
    expect(new TextDecoder().decode(await response.arrayBuffer())).toContain("%PDF-");
    expect(response.headers.get("x-r2-key")).toBeNull();
  });

  it("verifies artifact hashes before writing R2 and records checkpoints", async () => {
    const job = await seedJob();
    await claim();
    const bytes = new TextEncoder().encode("# parsed paper");
    const upload = (sha256: string) => SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/artifacts/parsed_markdown?worker_id=worker-a`,
      {
        method: "PUT",
        headers: {
          authorization: machineHeaders.authorization,
          "content-type": "text/markdown; charset=utf-8",
          "x-content-sha256": sha256,
          "x-artifact-name": "paper.md",
        },
        body: bytes,
      },
    );
    expect((await upload("wrong")).status).toBe(422);
    expect((await testEnv.ARTIFACTS.list({ prefix: "derived/" })).objects).toHaveLength(0);

    const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
    const sha256 = [...digest].map((value) => value.toString(16).padStart(2, "0")).join("");
    const accepted = await upload(sha256);
    expect(accepted.status).toBe(201);
    expect((await testEnv.ARTIFACTS.list({ prefix: "derived/" })).objects).toHaveLength(1);
    const artifact = await accepted.json<{ artifact_id: string }>();

    const downloaded = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/artifacts/${artifact.artifact_id}?worker_id=worker-a`,
      { headers: { authorization: machineHeaders.authorization } },
    );
    expect(downloaded.status).toBe(200);
    expect(new Uint8Array(await downloaded.arrayBuffer())).toEqual(bytes);
    expect(downloaded.headers.get("x-content-sha256")).toBe(sha256);

    const checkpoint = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/checkpoint`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({
          worker_id: "worker-a",
          stage: "parsed",
          output: { artifact_id: artifact.artifact_id },
        }),
      },
    );
    expect(checkpoint.status).toBe(200);
  });

  it("records processing failures without losing completed checkpoints", async () => {
    const job = await seedJob();
    await claim();
    const checkpoint = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/checkpoint`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({ worker_id: "worker-a", stage: "parsed", output: { ok: true } }),
      },
    );
    expect(checkpoint.status).toBe(200);
    const failed = await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/fail`, {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({
        worker_id: "worker-a",
        error_code: "deepseek_failed",
        error_message: "generation failed",
      }),
    });
    expect(failed.status).toBe(200);
    const stored = await new IntakeRepository(testEnv.DB).getJob(job.jobId);
    expect(stored?.status).toBe("failed");
    expect(stored?.checkpoints.parsed).toEqual({ ok: true });

    const retry = await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, {
      method: "POST",
      headers: { ...machineHeaders, "idempotency-key": "11111111-1111-4111-8111-111111111111" },
    });
    expect(retry.status).toBe(202);
    expect(await retry.json()).toMatchObject({ status: "queued", code: "retry_accepted" });
  });

  it("replays one retry result for the same idempotency key", async () => {
    const job = await seedJob();
    await claim();
    await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/fail`, {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({ worker_id: "worker-a", error_code: "failed", error_message: "failed" }),
    });
    const key = "22222222-2222-4222-8222-222222222222";
    const retry = () => SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, {
      method: "POST",
      headers: { ...machineHeaders, "idempotency-key": key },
    });

    const first = await retry();
    const second = await retry();
    const queried = await SELF.fetch(`https://worker.test/v1/worker/operations/${key}`, {
      headers: { authorization: machineHeaders.authorization },
    });

    expect(first.status).toBe(202);
    expect(second.status).toBe(202);
    expect(second.headers.get("idempotency-replayed")).toBe("true");
    expect(await queried.json()).toMatchObject({
      job_id: job.jobId,
      status: "queued",
      code: "retry_accepted",
    });
  });

  it("never starts a later retry when an old idempotency key is replayed", async () => {
    const job = await seedJob();
    await claim();
    await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/fail`, {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({ worker_id: "worker-a", error_code: "failed", error_message: "failed" }),
    });
    const key = "77777777-7777-4777-8777-777777777777";
    const headers = { ...machineHeaders, "idempotency-key": key };
    await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, { method: "POST", headers });
    await testEnv.DB.prepare(
      "UPDATE jobs SET status = 'failed', error_code = 'later_failure' WHERE job_id = ?",
    ).bind(job.jobId).run();

    const replay = await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, {
      method: "POST", headers,
    });

    expect(replay.status).toBe(202);
    expect(replay.headers.get("idempotency-replayed")).toBe("true");
    expect((await new IntakeRepository(testEnv.DB).getJob(job.jobId))?.status).toBe("failed");
  });

  it("serializes concurrent retries with one idempotency key", async () => {
    const job = await seedJob();
    await claim();
    await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/fail`, {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({ worker_id: "worker-a", error_code: "failed", error_message: "failed" }),
    });
    const headers = {
      ...machineHeaders,
      "idempotency-key": "66666666-6666-4666-8666-666666666666",
    };
    const [first, second] = await Promise.all([
      SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, { method: "POST", headers }),
      SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, { method: "POST", headers }),
    ]);
    expect([first.status, second.status]).toEqual([202, 202]);
    expect(
      [first, second].filter((response) => response.headers.get("idempotency-replayed") === "true"),
    ).toHaveLength(1);
    const stored = await new IntakeRepository(testEnv.DB).getJob(job.jobId);
    expect(stored?.status).toBe("queued");
  });

  it("rejects reuse of an idempotency key for another job", async () => {
    const firstJob = await seedJob();
    const secondJob = await seedJob();
    for (const [index, job] of [firstJob, secondJob].entries()) {
      const workerId = `worker-${index}`;
      await claim(workerId);
      await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/fail`, {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({ worker_id: workerId, error_code: "failed", error_message: "failed" }),
      });
    }
    const key = "33333333-3333-4333-8333-333333333333";
    const headers = { ...machineHeaders, "idempotency-key": key };
    expect((await SELF.fetch(`https://worker.test/v1/worker/jobs/${firstJob.jobId}/retry`, {
      method: "POST", headers,
    })).status).toBe(202);
    expect((await SELF.fetch(`https://worker.test/v1/worker/jobs/${secondJob.jobId}/retry`, {
      method: "POST", headers,
    })).status).toBe(409);
  });

  it("requires a valid idempotency key and reports missing operations", async () => {
    const job = await seedJob();
    const missingKey = await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/retry`, {
      method: "POST",
      headers: machineHeaders,
    });
    expect(missingKey.status).toBe(400);
    const missing = await SELF.fetch(
      "https://worker.test/v1/worker/operations/44444444-4444-4444-8444-444444444444",
      { headers: { authorization: machineHeaders.authorization } },
    );
    expect(missing.status).toBe(404);
  });
});
